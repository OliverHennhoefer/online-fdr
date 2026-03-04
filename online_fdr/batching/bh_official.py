"""
BatchBH Official: Official Implementation of Online Batch FDR Control
Implementation based on the official code from "The Power of Batching in Multiple Hypothesis Testing"
by Zrnic, Jiang, Ramdas, and Jordan (2020) - https://arxiv.org/pdf/1910.04968

This implementation matches the exact algorithm and data structures used by the paper authors
in their official implementation, including:
- Dynamic array resizing with doubling strategy
- Cumulative rejection tracking with R_sums array updates
- Adaptive gamma sequence selection based on batch size
- Extended return values including FDH (False Discovery Hat) estimates

NOTE: This differs from the simplified BatchBH implementation in bh.py which follows
the R reference implementation. Both are mathematically valid implementations of the
same core algorithm, but this version provides the exact behavior of the authors' code.
"""

from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import (
    BatchBHHalfGammaSequence,
    BatchBHPolynomialGammaSequence,
)
from online_fdr.utils.static import bh


class BatchBHOfficial(AbstractBatchingTest):
    """Official BatchBH algorithm implementation matching the paper authors' code.

    This implementation exactly replicates the behavior of the official BatchBH
    implementation from the paper authors, including all data structure management,
    array resizing, and calculation specifics.

    Key differences from the simplified BatchBH implementation:
    1. Dynamic array resizing with doubling strategy
    2. Cumulative rejection tracking (R_sums stores cumulative values)
    3. Adaptive gamma sequences based on batch size (<100 vs â‰¥100)
    4. Extended return values including FDH estimates
    5. Exact replication of official beta calculation logic

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2020).
        The Power of Batching in Multiple Hypothesis Testing.
        International Conference on Artificial Intelligence and Statistics.
    [2] Official implementation: https://arxiv.org/pdf/1910.04968
    """

    def __init__(self, alpha: float):
        """Initialize BatchBHOfficial with FDR control level alpha.

        Args:
            alpha: Target FDR control level (between 0 and 1)
        """
        super().__init__(alpha)
        self.alpha0 = alpha
        self.num_test = 0

        # Initialize gamma sequences for adaptive selection
        self.poly_seq = BatchBHPolynomialGammaSequence()
        self.half_seq = BatchBHHalfGammaSequence()

        # Initialize lists for online processing (no pre-allocation)
        self.r_s_plus: list[int] = []  # R^+ values for each batch
        self.r_total_sum = 0  # Total rejections across all batches
        self.r_s_cumulative: list[int] = []  # Cumulative rejection tracking
        self.alpha_s: list[float] = []  # Alpha values used for each batch

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values using the official BatchBH procedure.

        Args:
            p_vals: List of p-values for the current batch

        Returns:
            List of boolean values indicating which hypotheses are rejected
        """
        rejections, _, _, _ = self.test_batch_extended(p_vals)
        return rejections

    def test_batch_extended(
        self, p_vals: list[float]
    ) -> tuple[list[bool], float, float, float]:
        """Test a batch of p-values using the official BatchBH procedure with extended output.

        Args:
            p_vals: List of p-values for the current batch

        Returns:
            Tuple containing:
            - rejections: List of boolean values indicating which hypotheses are rejected
            - fdh: False Discovery Hat (FDH) estimate
            - alpha_t: Alpha threshold used for this batch
            - additional_rejections: R_plus - num_rejects (additional possible rejections)
        """
        p_vals = list(p_vals)
        batch_size = len(p_vals)
        if batch_size == 0:
            return [], 0.0, 0.0, 0.0
        validity.check_p_vals_batch(p_vals)
        t = self.num_test

        # Calculate alpha_t
        if t == 0:
            # First batch: Î±â‚ = Î± Ã— Î³â‚
            gamma_1 = self._get_gamma(j=1, batch_size=batch_size)
            alpha_t = self.alpha0 * gamma_1
        else:
            # Calculate gamma sum for batches 1 to t+1
            gamma_sum = sum(
                self._get_gamma(j=i, batch_size=batch_size) for i in range(1, t + 2)
            )

            # Calculate beta_t using official formula
            beta_t = 0.0
            for s in range(t):
                denominator = self.r_s_plus[s] + self.r_s_cumulative[s]
                if denominator > 0:
                    beta_t += self.alpha_s[s] * self.r_s_plus[s] / denominator

            # Î±_t = (Î± Ã— Î£Î³_s - Î²_t) Ã— (n_t + R_total) / n_t
            alpha_t = (
                (self.alpha0 * gamma_sum - beta_t)
                * (batch_size + self.r_total_sum)
                / batch_size
            )

        # Run BH procedure on current batch
        num_rejections, threshold = bh(p_vals, alpha_t)

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

        # Calculate R^+ (maximum rejections with one p-value set to 0)
        r_plus = num_rejections
        for i in range(len(p_vals)):
            original_p = p_vals[i]
            p_vals[i] = 0
            temp_rejections, _ = bh(p_vals, alpha_t)
            r_plus = max(r_plus, temp_rejections)
            p_vals[i] = original_p

        self.r_s_plus.append(r_plus)

        # Move to next batch
        self.num_test += 1

        # Calculate FDH (False Discovery Hat) estimate
        fdh = 0.0
        for s in range(t + 1):
            denominator = self.r_s_plus[s] + self.r_s_cumulative[s]
            if denominator > 0:
                fdh += self.alpha_s[s] * self.r_s_plus[s] / denominator

        # Generate rejection decisions
        rejections = [p_val <= threshold for p_val in p_vals]

        return rejections, fdh, alpha_t, r_plus - num_rejections

    def _get_gamma(self, j: int, batch_size: int) -> float:
        """Get gamma value using adaptive sequence selection based on batch size."""
        if batch_size < 100:
            return self.poly_seq.calc_gamma(j)
        else:
            return self.half_seq.calc_gamma(j)
