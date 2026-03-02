"""
BatchBH: Online Batch FDR Control via Benjamini-Hochberg
Implementation based on "The Power of Batching in Multiple Hypothesis Testing"
by Zrnic, Jiang, Ramdas, and Jordan (2020)
"""

from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import bh


class BatchBH(AbstractBatchingTest):
    """Benjamini-Hochberg procedure for online batch FDR control.

    BatchBH extends the classical Benjamini-Hochberg (BH) procedure to the online
    batching setting, where hypotheses arrive in batches over time and must be
    tested sequentially while maintaining overall FDR control across all batches.

    This implements Algorithm 1 from "The Power of Batching in Multiple Hypothesis
    Testing" by Zrnic, Jiang, Ramdas, and Jordan (2020). The key innovation is
    the calculation of adaptive alpha levels that account for the interdependence
    between batches while preserving the BH optimality within each batch.

    The algorithm maintains FDR control by:
    1. Allocating alpha budget using a gamma sequence
    2. Adjusting for dependencies between batches via Î²_t correction
    3. Computing R^+ (maximum possible rejections) for power optimization
    4. Applying standard BH procedure within each batch

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).

    Attributes:
        alpha0: Original target FDR level.
        num_test: Number of batches tested so far.
        seq: Gamma sequence for alpha allocation across batches.
        r_s: Number of rejections in each batch.
        r_s_plus: Maximum possible rejections for each batch (R^+ values).
        alpha_s: Alpha level used for each batch.

    Examples:
        >>> # Basic batch testing
        >>> bh = BatchBH(alpha=0.05)
        >>> batch1 = [0.001, 0.02, 0.15, 0.8]
        >>> decisions1 = bh.test_batch(batch1)
        >>> print(f"Batch 1 discoveries: {sum(decisions1)}")

        >>> # Sequential batches with adaptive alpha
        >>> batch2 = [0.03, 0.9, 0.006, 0.4]
        >>> decisions2 = bh.test_batch(batch2)  # Alpha adjusted based on batch1
        >>> print(f"Batch 2 discoveries: {sum(decisions2)}")

        >>> # Multiple batches
        >>> batches = [[0.001, 0.8], [0.02, 0.3], [0.005, 0.9]]
        >>> all_decisions = []
        >>> for i, batch in enumerate(batches):
        ...     decisions = bh.test_batch(batch)
        ...     all_decisions.append(decisions)
        ...     print(f"Batch {i+1}: {sum(decisions)} discoveries")

    References:
        Zrnic, T., D. Jiang, A. Ramdas, and M. I. Jordan (2020). "The Power of
        Batching in Multiple Hypothesis Testing." Proceedings of the 37th
        International Conference on Machine Learning (ICML), PMLR, 119:11504-11515.

        Benjamini, Y., and Y. Hochberg (1995). "Controlling the False Discovery Rate:
        A Practical and Powerful Approach to Multiple Testing." Journal of the Royal
        Statistical Society: Series B, 57(1):289-300.
    """

    def __init__(self, alpha: float):
        """Initialize BatchBH with FDR control level alpha.

        Args:
            alpha: Target FDR control level. Must be in (0, 1).

        Raises:
            ValueError: If alpha is not in (0, 1).
        """
        super().__init__(alpha)
        self.alpha0 = alpha
        self.num_test = 0  # Number of batches tested so far
        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.r_s_plus: list[int] = []  # R^+ values for each batch
        self.r_s: list[int] = []  # R values (number of rejections) for each batch
        self.alpha_s: list[float] = []  # Alpha values used for each batch

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values using the BatchBH procedure.

        Args:
            p_vals: List of p-values for the current batch

        Returns:
            List of boolean values indicating which hypotheses are rejected
        """
        p_vals_local = list(p_vals)
        n_batch = len(p_vals_local)
        if n_batch == 0:
            return []
        validity.check_p_vals_batch(p_vals_local)
        t = self.num_test  # Current batch index (0-based)

        if t == 0:
            # First batch: Î±â‚ = Î³â‚Î±
            alpha_t = self.alpha0 * self.seq.calc_gamma(j=1)
        else:
            # Calculate Î²_t
            beta_t = 0.0
            total_rejections_except_s = sum(self.r_s)  # Total rejections so far

            for s in range(t):
                # For each previous batch s, calculate its contribution to Î²_t
                # Denominator is R^+_s + sum of all other rejections up to t-1
                rejections_from_other_batches = total_rejections_except_s - self.r_s[s]
                denominator = self.r_s_plus[s] + rejections_from_other_batches
                if denominator > 0:
                    beta_t += self.alpha_s[s] * self.r_s_plus[s] / denominator

            # Calculate Î±_t = (Î£_{sâ‰¤t} Î³_s Î± - Î²_t) Ã— (n_t + Î£_{s<t} R_s) / n_t
            gamma_sum = sum(self.seq.calc_gamma(j=i + 1) for i in range(t + 1))
            numerator = gamma_sum * self.alpha0 - beta_t
            total_prev_rejections = sum(self.r_s)
            alpha_t = numerator * (n_batch + total_prev_rejections) / n_batch

            # Ensure alpha_t is non-negative
            alpha_t = max(0, alpha_t)

        # Run BH on current batch
        num_reject, threshold = bh(p_vals_local, alpha_t)

        # Calculate R^+_t (maximum rejections if one p-value is set to 0)
        r_plus = num_reject  # Start with current rejections
        adjusted = list(p_vals_local)
        for i in range(len(adjusted)):
            # Temporarily set p-value to 0
            original_p = adjusted[i]
            adjusted[i] = 0.0
            temp_reject, _ = bh(adjusted, alpha_t)
            r_plus = max(r_plus, temp_reject)
            # Restore original p-value
            adjusted[i] = original_p

        # Store results
        self.r_s.append(num_reject)
        self.r_s_plus.append(r_plus)
        self.alpha_s.append(alpha_t)
        self.num_test += 1

        # Return rejection decisions
        return [p_val <= threshold for p_val in p_vals_local]

