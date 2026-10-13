"""BatchBH using the gamma profiles and accounting from the authors' code.

The AISTATS supplementary experiments use a fixed batch size per stream.
This implementation selects one gamma profile for the entire stream so that
varying batch sizes cannot retrospectively change past budget allocations.
"""

import math
from collections.abc import Sequence
from typing import Any, Literal

from online_fdr.core.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.core.results import BatchDecision
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import (
    BatchBHHalfGammaSequence,
    BatchBHPolynomialGammaSequence,
)
from online_fdr.core.utils.static import _bh_r_plus, bh


def _estimate_fdp(
    levels: Sequence[float],
    augmented_rejections: Sequence[int],
    other_rejections: Sequence[int],
) -> float:
    """Compute the authors' FDP estimate from recorded batch allocations."""
    return float(
        sum(
            level * r_plus / (r_plus + r_other)
            for level, r_plus, r_other in zip(
                levels, augmented_rejections, other_rejections
            )
            if r_plus + r_other > 0
        )
    )


class BatchBHOfficial(AbstractBatchingTest):
    """BatchBH with the paper authors' gamma profiles and FDH estimate.

    ``gamma_profile="auto"`` chooses the polynomial profile for a first
    nonempty batch smaller than 100, or the half profile otherwise. The choice
    is then fixed, including when subsequent batch sizes cross that boundary.
    Callers can instead choose ``"poly"`` or ``"half"`` explicitly.

    The half profile allocates its initial budget to the first two batches;
    later levels depend on discoveries that release budget. The polynomial
    profile allocates positive initial budget throughout the stream.

    FDR control requires independent null p-values and a monotone testing
    procedure (the paper's Theorem 1). This uses the authors' experimental
    update; its fixed allocation budget does not certify monotonicity for
    every possible p-value sequence.

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2020).
        The Power of Batching in Multiple Hypothesis Testing.
        International Conference on Artificial Intelligence and Statistics.
    [2] Official implementation: https://proceedings.mlr.press/v108/zrnic20a.html
    """

    def __init__(
        self, alpha: float, gamma_profile: Literal["auto", "poly", "half"] = "auto"
    ):
        """Initialize BatchBHOfficial with FDR control level alpha.

        Args:
            alpha: Target FDR control level (between 0 and 1)
            gamma_profile: Gamma policy, fixed for the entire stream. ``"auto"``
                selects from the first valid nonempty batch.
        """
        super().__init__(alpha)
        self.alpha0 = alpha
        if gamma_profile not in {"auto", "poly", "half"}:
            raise ValueError("gamma_profile must be 'auto', 'poly', or 'half'.")
        self._gamma_profile: Literal["poly", "half"] | None = (
            None if gamma_profile == "auto" else gamma_profile
        )

        # Retain the built-in sequences for the stream's fixed selection.
        self.poly_seq = BatchBHPolynomialGammaSequence()
        self.half_seq = BatchBHHalfGammaSequence()

        # Initialize lists for online processing (no pre-allocation)
        self.r_s_plus: list[int] = []  # R^+ values for each batch
        self.r_total_sum = 0  # Total rejections across all batches
        self.r_s_cumulative: list[int] = []  # Cumulative rejection tracking
        self.alpha_s: list[float] = []  # Alpha values used for each batch

    @property
    def gamma_profile(self) -> Literal["poly", "half"] | None:
        """Selected policy; ``None`` until automatic selection takes place."""
        return self._gamma_profile

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        if "_gamma_profile" not in state:
            # Earlier schema-1 snapshots did not retain the first batch size.
            # Its level still identifies the profile used on that first batch.
            levels = state["alpha_s"]
            if not levels:
                state["_gamma_profile"] = None
            else:
                if any(not math.isfinite(level) or level < 0 for level in levels):
                    raise ValueError(
                        "cannot restore a legacy BatchBHOfficial snapshot with "
                        "invalid past test levels; prior decisions cannot be repaired."
                    )
                first_gamma = levels[0] / state["alpha0"]
                if math.isclose(first_gamma, 0.5, rel_tol=1e-12, abs_tol=0.0):
                    state["_gamma_profile"] = "half"
                elif math.isclose(
                    first_gamma,
                    state["poly_seq"].calc_gamma(1),
                    rel_tol=1e-12,
                    abs_tol=0.0,
                ):
                    state["_gamma_profile"] = "poly"
                else:
                    raise ValueError(
                        "cannot identify the gamma profile of this legacy "
                        "BatchBHOfficial snapshot."
                    )
                sequence = (
                    state["half_seq"]
                    if state["_gamma_profile"] == "half"
                    else state["poly_seq"]
                )
                budget = state["alpha0"] * sum(
                    sequence.calc_gamma(j) for j in range(1, len(levels) + 1)
                )
                spent = _estimate_fdp(
                    levels, state["r_s_plus"], state["r_s_cumulative"]
                )
                if spent > budget and not math.isclose(
                    spent, budget, rel_tol=1e-12, abs_tol=0.0
                ):
                    raise ValueError(
                        "cannot restore a legacy BatchBHOfficial snapshot whose "
                        "past allocations exceed the fixed gamma budget; "
                        "prior decisions cannot be repaired."
                    )
        return state

    def test_batch(self, p_vals: Sequence[float]) -> list[bool]:
        """Test a batch of p-values using the official BatchBH procedure.

        Args:
            p_vals: List of p-values for the current batch

        Returns:
            List of boolean values indicating which hypotheses are rejected
        """
        return list(self.test_batch_detail(p_vals).rejected)

    def test_batch_detail(self, p_vals: Sequence[float]) -> BatchDecision:
        """Test a batch of p-values and return a stable detailed result.

        Args:
            p_vals: List of p-values for the current batch

        Returns:
            Immutable decision details, with FDH and additional-rejection
            metadata available in ``metadata``.
        """
        p_vals = list(p_vals)
        batch_size = len(p_vals)
        if batch_size == 0:
            return BatchDecision(
                rejected=(),
                values=(),
                rejection_threshold=self.last_rejection_threshold,
                batch_index=self.num_batches,
                test_level=self.last_test_level,
                error_rate=self.error_rate,
                metadata={"fdh": 0.0, "additional_rejections": 0.0},
            )
        validity.check_p_vals_batch(p_vals)
        t = self.num_batches
        profile = self._gamma_profile
        if profile is None:
            profile = "poly" if batch_size < 100 else "half"

        # Calculate alpha_t
        if t == 0:
            # First batch: alpha_1 = alpha * gamma_1
            gamma_1 = self._get_gamma(j=1, profile=profile)
            alpha_t = self.alpha0 * gamma_1
        else:
            # Calculate gamma sum for batches 1 to t+1
            gamma_sum = sum(
                self._get_gamma(j=i, profile=profile) for i in range(1, t + 2)
            )

            # Calculate beta_t using official formula
            beta_t = _estimate_fdp(self.alpha_s, self.r_s_plus, self.r_s_cumulative)

            # alpha_t = (alpha * sum(gamma_s) - beta_t) * (n_t + R_total) / n_t
            # The remainder is nonnegative in exact arithmetic; cancellation
            # at an exhausted budget can leave a tiny negative float.
            remaining = max(self.alpha0 * gamma_sum - beta_t, 0.0)
            alpha_t = remaining * (batch_size + self.r_total_sum) / batch_size

        # Run BH procedure on current batch
        num_rejections, threshold = bh(p_vals, alpha_t)
        r_plus = _bh_r_plus(p_vals, alpha_t)

        self._gamma_profile = profile
        # Update cumulative tracking (matches official implementation)
        self.r_s_cumulative.append(
            self.r_total_sum
        )  # Store total rejections before this batch
        for i in range(
            len(self.r_s_cumulative) - 1
        ):  # Add current rejections to all previous batches
            self.r_s_cumulative[i] += num_rejections
        self.r_total_sum += num_rejections  # Update total
        self.alpha_s.append(alpha_t)  # Store alpha used

        self.r_s_plus.append(r_plus)

        # Move to next batch
        self._set_test_level(alpha_t, rejection_threshold=threshold)
        self._advance_batch(batch_size)

        # Calculate FDH (False Discovery Hat) estimate
        fdh = _estimate_fdp(self.alpha_s, self.r_s_plus, self.r_s_cumulative)

        # Generate rejection decisions
        rejections = [p_val <= threshold for p_val in p_vals]

        return BatchDecision(
            rejected=tuple(rejections),
            values=tuple(float(p_val) for p_val in p_vals),
            rejection_threshold=threshold,
            batch_index=self.num_batches,
            test_level=alpha_t,
            error_rate=self.error_rate,
            metadata={
                "fdh": fdh,
                "additional_rejections": r_plus - num_rejections,
                "num_rejections": num_rejections,
            },
        )

    def _get_gamma(self, j: int, profile: Literal["poly", "half"]) -> float:
        """Evaluate the stream's fixed gamma policy."""
        if profile == "poly":
            return self.poly_seq.calc_gamma(j)
        else:
            return self.half_seq.calc_gamma(j)
