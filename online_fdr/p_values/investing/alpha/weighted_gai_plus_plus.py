from __future__ import annotations

import math
from functools import cache
from typing import Any

from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.results import TestDecision
from online_fdr.core.utils import validity


@cache
def _finite_lord_gamma_normalizer(horizon: int) -> float:
    return sum(
        math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j))))
        for j in range(1, horizon + 1)
    )


def _finite_lord_gamma(j: int, horizon: int) -> float:
    if j < 1:
        raise ValueError("gamma index must be positive.")
    if j > horizon:
        raise ValueError("gamma horizon exceeded; initialize with a larger horizon.")
    raw = math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j))))
    return raw / _finite_lord_gamma_normalizer(horizon)


class WeightedGaiPlusPlus(AbstractSequentialTest):
    """Prior/penalty-weighted GAI++ with optional memory decay.

    Controls penalty-weighted FDR under independent p-values and predictable,
    monotone weights. With ``decay < 1``, the target is penalty-weighted
    decaying-memory FDR. Ordinary FDR is the special case of unit penalty
    weights and no decay. Choose weights before observing the current p-value.

    This follows Ramdas, Yang, Wainwright, and Jordan's memory-and-weights
    GAI++ reward constraints. It corrects the prior-weight cap in the authors'
    ``GAI2_MW_proc_batch`` example so that nonnegative rewards are feasible.
    """

    error_rate = "weighted FDR"

    def __init__(
        self,
        alpha: float = 0.05,
        wealth: float | None = None,
        decay: float = 1.0,
        gamma_horizon: int = 9_999,
    ):
        super().__init__(alpha)
        self.alpha0 = alpha
        self.wealth0 = alpha / 2 if wealth is None else wealth
        validity.check_initial_wealth(self.wealth0, alpha)
        validity.check_finite_number(decay, "decay")
        if not 0 < decay <= 1:
            raise ValueError("decay must be in (0, 1].")
        validity.check_positive_integer(gamma_horizon, "gamma_horizon")

        self.decay = decay
        self.error_rate = "weighted mem-FDR" if decay < 1 else "weighted FDR"
        self.gamma_horizon = gamma_horizon
        self.wealth = self.wealth0
        self.wealth_history = [self.wealth]
        self.base_alpha: float = self._gamma(1) * self.wealth0
        self.reject_idx: list[int] = []
        self.decisions: list[bool] = []
        self.base_alpha_history: list[float] = []
        self.alpha_history: list[float] = []
        self.prior_weights_used: list[float] = []
        self.penalty_weights: list[float] = []
        self.phi_history: list[float] = []
        self.psi_history: list[float] = []
        self._psi_rejections: list[float] = []
        self._first_rejection_seen = False

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        # Older schema-1 snapshots prefetched a redundant next test level.
        state.pop("_next_base_alpha", None)
        state["error_rate"] = (
            "weighted mem-FDR" if state["decay"] < 1 else "weighted FDR"
        )
        return state

    def _gamma(self, j: int) -> float:
        return _finite_lord_gamma(j, self.gamma_horizon)

    def test_one(
        self, p_val: float, prior_weight: float = 1.0, penalty_weight: float = 1.0
    ) -> bool:
        validity.check_p_val(p_val)
        for name, weight in (
            ("prior_weight", prior_weight),
            ("penalty_weight", penalty_weight),
        ):
            validity.check_finite_number(weight, name)
            if weight <= 0:
                raise ValueError(f"{name} must be finite and positive.")

        idx = self.num_hypotheses + 1
        base_alpha = self._calc_base_alpha(idx)
        first_flag = 0 if self._first_rejection_seen else 1
        b_t = self.alpha0 - first_flag * self.wealth0 / penalty_weight
        if not math.isfinite(b_t):
            raise ValueError("penalty_weight produces a nonfinite reward budget.")
        phi = min(
            base_alpha,
            self.decay * self.wealth + (1 - self.decay) * first_flag * self.wealth0,
        )
        max_weight = (phi / base_alpha) / (1 - b_t) if base_alpha > 0 else 0.0
        if max_weight <= 0:
            used_prior_weight = 0.0
            threshold = 0.0
            psi = 0.0
        else:
            used_prior_weight = min(prior_weight, max_weight)
            ratio = penalty_weight / used_prior_weight
            threshold = base_alpha / ratio
            # Both upper bounds must admit a nonnegative reward (paper Eq. 10a).
            reward_bound = min(
                phi + penalty_weight * b_t,
                (phi / base_alpha) * ratio - penalty_weight + penalty_weight * b_t,
            )
            tolerance = 8 * math.ulp(
                max(abs(phi), abs(penalty_weight * b_t), penalty_weight)
            )
            if not math.isfinite(reward_bound) or reward_bound < -tolerance:
                raise ValueError(
                    "penalty_weight is incompatible with the remaining wealth: "
                    "no nonnegative reward satisfies the GAI++ bounds."
                )
            psi = max(reward_bound, 0.0)

        rejected = p_val < threshold
        next_wealth = (
            self.decay * self.wealth
            + (1 - self.decay) * first_flag * self.wealth0
            - phi
            + int(rejected) * psi
        )
        if not math.isfinite(next_wealth) or next_wealth < 0:
            raise ValueError("weights produce nonfinite or negative wealth.")
        self._advance_hypotheses()
        if rejected:
            self._first_rejection_seen = True
            self.reject_idx.append(idx)
            self._psi_rejections.append(psi)

        self.wealth = next_wealth
        self.base_alpha = base_alpha
        self._set_test_level(base_alpha, rejection_threshold=threshold)
        self.decisions.append(rejected)
        self.base_alpha_history.append(base_alpha)
        self.alpha_history.append(threshold)
        self.prior_weights_used.append(used_prior_weight)
        self.penalty_weights.append(penalty_weight)
        self.phi_history.append(phi)
        self.psi_history.append(psi)
        self.wealth_history.append(self.wealth)
        return bool(rejected)

    def test_one_detail(
        self, p_val: float, prior_weight: float = 1.0, penalty_weight: float = 1.0
    ) -> TestDecision:
        """Test with explicit weights and return an immutable decision record."""
        return self._decision(p_val, self.test_one(p_val, prior_weight, penalty_weight))

    def _calc_base_alpha(self, idx: int) -> float:
        alpha_t = self._gamma(idx) * self.wealth0
        for reject_idx, psi in zip(self.reject_idx, self._psi_rejections):
            zero_distance = idx - reject_idx - 1
            alpha_t += (
                psi * (self.decay**zero_distance) * self._gamma(zero_distance + 1)
            )
        return alpha_t
