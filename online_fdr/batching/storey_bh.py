from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import storey_bh


class BatchStoreyBH(AbstractBatchingTest):
    """Storey-Benjamini-Hochberg procedure for online batch FDR control.

    BatchStoreyBH extends the online batching framework to incorporate Storey's
    π₀ estimation method, which estimates the proportion of true null hypotheses
    within each batch. This provides enhanced power when the true null proportion
    is less than 1, particularly in genomics and other high-dimensional settings.

    The algorithm combines the adaptive alpha allocation strategy from BatchBH
    with Storey's modification of the Benjamini-Hochberg procedure, which adjusts
    the rejection threshold based on the estimated proportion of true nulls (π₀).

    Key innovations:
    1. Per-batch π₀ estimation using Storey's method
    2. Adaptive alpha allocation across batches
    3. Integration with the online batching framework
    4. Enhanced power when π₀ < 1

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).
        lambda_: Threshold parameter for π₀ estimation. Must be in (0, 1).
                Typically set to 0.5. Higher values give more conservative
                estimates of π₀ but may reduce power.

    Attributes:
        alpha0: Original target FDR level.
        num_test: Number of batches tested so far.
        lambda_: Threshold parameter for π₀ estimation.
        seq: Gamma sequence for alpha allocation across batches.
        pi0_estimates: π₀ estimates for each batch.
        r_s_plus: Maximum possible rejections for each batch.
        r_s: Rejection indicators for each batch.
        r_total: Total number of rejections across all batches.
        alpha_s: Alpha levels used for each batch.

    Examples:
        >>> # Basic usage with π₀ estimation
        >>> storey_bh = BatchStoreyBH(alpha=0.05, lambda_=0.5)
        >>> batch1 = [0.001, 0.02, 0.15, 0.8, 0.9]
        >>> decisions1 = storey_bh.test_batch(batch1)
        >>> print(f"π₀ estimate for batch 1: {storey_bh.pi0_estimates[-1]:.3f}")

        >>> # Sequential batches with adaptive power
        >>> batch2 = [0.03, 0.7, 0.006, 0.4, 0.85]
        >>> decisions2 = storey_bh.test_batch(batch2)
        >>> print(f"Batch 1 discoveries: {sum(decisions1)}")
        >>> print(f"Batch 2 discoveries: {sum(decisions2)}")

        >>> # Comparing different lambda values
        >>> storey_conservative = BatchStoreyBH(alpha=0.05, lambda_=0.8)
        >>> storey_liberal = BatchStoreyBH(alpha=0.05, lambda_=0.3)
        >>> # Conservative λ gives higher π₀ estimates, liberal λ gives lower

    References:
        Zrnic, T., D. Jiang, A. Ramdas, and M. I. Jordan (2020). "The Power of
        Batching in Multiple Hypothesis Testing." Proceedings of the 37th
        International Conference on Machine Learning (ICML), PMLR, 119:11504-11515.

        Storey, J. D. (2002). "A direct approach to false discovery rates."
        Journal of the Royal Statistical Society: Series B, 64(3):479-498.

        Storey, J. D. (2003). "The positive false discovery rate: a Bayesian
        interpretation and the q-value." Annals of Statistics, 31(6):2013-2035.
    """

    def __init__(self, alpha: float, lambda_: float):
        """Initialize BatchStoreyBH with FDR control level and π₀ estimation parameter.

        Args:
            alpha: Target FDR control level. Must be in (0, 1).
            lambda_: Threshold parameter for π₀ estimation. Must be in (0, 1).
                    P-values above λ are used to estimate the proportion of
                    true nulls. Common choice: λ = 0.5.

        Raises:
            ValueError: If alpha or lambda_ are not in (0, 1).
        """
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.num_test: int = 1
        self.lambda_: float = lambda_

        if not 0 < lambda_ < 1:
            raise ValueError("lambda_ must be between 0 and 1")

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.pi0_estimates: list[float] = []  # Store π₀ estimates per batch
        self.r_s_plus: list[float] = []
        self.r_s: list[bool] = []
        self.r_total: int = 0
        self.r_sums: list[float] = [0]
        self.alpha_s: list[float] = []

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values using the Storey-BH procedure with adaptive alpha.

        For each batch, this method:
        1. Estimates π₀ (proportion of true nulls) using Storey's method
        2. Calculates an adaptive alpha level based on previous batches
        3. Applies the Storey-BH procedure with the calculated alpha
        4. Updates internal statistics for future batches

        The Storey π₀ estimation uses the formula:
        π̂₀ = min(1, (1 + #{p > λ}) / (n × (1 - λ)))

        Args:
            p_vals: List of p-values for the current batch.

        Returns:
            List of boolean values indicating which hypotheses are rejected.

        Examples:
            >>> storey_bh = BatchStoreyBH(alpha=0.05, lambda_=0.5)
            >>> decisions = storey_bh.test_batch([0.001, 0.02, 0.8, 0.9])
            >>> print(f"π₀ estimate: {storey_bh.pi0_estimates[-1]:.3f}")
            >>> print(f"Rejections: {sum(decisions)}")
        """
        n_batch = len(p_vals)
        if n_batch == 0:
            return []

        # Estimate π₀ for this batch using Storey's method
        num_above_lambda = sum(1 for p in p_vals if p > self.lambda_)
        pi0_batch = min(1.0, (1 + num_above_lambda) / (n_batch * (1 - self.lambda_)))
        self.pi0_estimates.append(pi0_batch)

        # Calculate adaptive alpha for this batch
        if self.num_test == 1:
            # First batch
            self.alpha = self.alpha0 * self.seq.calc_gamma(j=1)
        else:
            # Subsequent batches: follow BatchBH framework
            gamma_sum = sum(self.seq.calc_gamma(i) for i in range(1, self.num_test + 1))
            self.alpha = gamma_sum * self.alpha0

            # Subtract previously spent alpha (adjusted by π₀ estimates)
            beta_t = sum(
                self.alpha_s[i]
                * self.pi0_estimates[i]
                * self.r_s_plus[i]
                / (self.r_s_plus[i] + self.r_sums[i + 1])
                for i in range(0, self.num_test - 1)
                if self.r_s_plus[i] + self.r_sums[i + 1] > 0
            )

            self.alpha = max(0, self.alpha - beta_t)

            # Adjust for batch size
            if n_batch > 0:
                self.alpha *= (n_batch + self.r_total) / n_batch

        # Apply Storey-BH procedure with current alpha
        num_reject, threshold = storey_bh(p_vals, self.alpha, self.lambda_)

        # Update running statistics
        self.r_sums.append(self.r_total)
        self.r_sums[1 : self.num_test] = [
            x + num_reject for x in self.r_sums[1 : self.num_test]
        ]
        self.r_total += num_reject
        self.alpha_s.append(self.alpha)

        # Calculate R+ efficiently
        r_plus = self._calculate_r_plus(p_vals)
        self.r_s_plus.append(r_plus)

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals]

    def _calculate_r_plus(self, p_vals: list[float]) -> int:
        """Calculate R⁺ (maximum rejections if one p-value is set to 0).

        R⁺ represents the maximum number of rejections possible in the current
        batch if we were allowed to set one p-value to 0 (perfect signal).
        This quantity is used in the BatchBH framework to determine how much
        alpha to allocate for future batches.

        The calculation is done efficiently by augmenting the batch with a
        p-value of 0 and running the Storey-BH procedure to see how many
        rejections would result.

        Args:
            p_vals: List of p-values for the current batch.

        Returns:
            Maximum number of additional rejections possible with one perfect signal.

        Note:
            This is a key component of the online batching framework that helps
            determine the adaptive alpha allocation for subsequent batches.
        """
        if not p_vals:
            return 0

        # Create a copy with an additional p-value of 0
        augmented_p_vals = p_vals + [0.0]
        r_plus, _ = storey_bh(augmented_p_vals, self.alpha, self.lambda_)

        # Since we added one p-value (0), and it will definitely be rejected,
        # R+ is the total rejections minus 1
        return max(0, r_plus - 1)
