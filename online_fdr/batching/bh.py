"""
BatchBH: Online Batch FDR Control via Benjamini-Hochberg
Implementation based on "The Power of Batching in Multiple Hypothesis Testing"
by Zrnic, Jiang, Ramdas, and Jordan (2020)
"""

from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import bh


class BatchBH(AbstractBatchingTest):
    """BatchBH algorithm for online batch FDR control.

    This implements Algorithm 1 from "The Power of Batching in Multiple 
    Hypothesis Testing" by Zrnic et al. (2020).

    The algorithm tests batches of hypotheses sequentially while maintaining
    FDR control at level alpha across all batches.
    """

    def __init__(self, alpha: float):
        """Initialize BatchBH with FDR control level alpha.

        Args:
            alpha: Target FDR control level (between 0 and 1)
        """
        super().__init__(alpha)
        self.alpha0 = alpha
        self.num_test = 0  # Number of batches tested so far
        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.r_s_plus = []  # R^+ values for each batch
        self.r_s = []  # R values (number of rejections) for each batch
        self.alpha_s = []  # Alpha values used for each batch

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values using the BatchBH procedure.

        Args:
            p_vals: List of p-values for the current batch

        Returns:
            List of boolean values indicating which hypotheses are rejected
        """
        n_batch = len(p_vals)
        t = self.num_test  # Current batch index (0-based)

        if t == 0:
            # First batch: α₁ = γ₁α
            alpha_t = self.alpha0 * self.seq.calc_gamma(j=1)
        else:
            # Calculate β_t
            beta_t = 0
            total_rejections_except_s = sum(self.r_s)  # Total rejections so far

            for s in range(t):
                # For each previous batch s, calculate its contribution to β_t
                # Denominator is R^+_s + sum of all other rejections up to t-1
                rejections_except_s = total_rejections_except_s - self.r_s[s]
                denominator = self.r_s_plus[s] + rejections_except_s
                if denominator > 0:
                    beta_t += self.alpha_s[s] * self.r_s_plus[s] / denominator

            # Calculate α_t = (Σ_{s≤t} γ_s α - β_t) × (n_t + Σ_{s<t} R_s) / n_t
            gamma_sum = sum(self.seq.calc_gamma(j=i + 1) for i in range(t + 1))
            numerator = gamma_sum * self.alpha0 - beta_t
            total_prev_rejections = sum(self.r_s)
            alpha_t = numerator * (n_batch + total_prev_rejections) / n_batch

            # Ensure alpha_t is non-negative
            alpha_t = max(0, alpha_t)

        # Run BH on current batch
        num_reject, threshold = bh(p_vals, alpha_t)

        # Calculate R^+_t (maximum rejections if one p-value is set to 0)
        r_plus = num_reject  # Start with current rejections
        for i in range(len(p_vals)):
            # Temporarily set p-value to 0
            original_p = p_vals[i]
            p_vals[i] = 0
            temp_reject, _ = bh(p_vals, alpha_t)
            r_plus = max(r_plus, temp_reject)
            # Restore original p-value
            p_vals[i] = original_p

        # Store results
        self.r_s.append(num_reject)
        self.r_s_plus.append(r_plus)
        self.alpha_s.append(alpha_t)
        self.num_test += 1

        # Return rejection decisions
        return [p_val <= threshold for p_val in p_vals]
