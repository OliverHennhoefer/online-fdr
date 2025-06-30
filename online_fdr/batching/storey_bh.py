from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import storey_bh


class BatchStoreyBH(AbstractBatchingTest):
    """Batch Storey-BH procedure for online FDR control.
    
    Extends the batching framework to incorporate Storey's π₀ estimation.
    This adapts the BatchBH algorithm to use Storey's modified BH procedure.
    
    Reference:
    - Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M. (2020). "The Power of 
      Batching in Multiple Hypothesis Testing." AISTATS.
    - Storey, J.D. (2002). "A direct approach to false discovery rates."
      Journal of the Royal Statistical Society: Series B, 64(3), 479-498.
    """

    def __init__(self, alpha: float, lambda_: float):
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
        """Test a batch of p-values using Storey-BH with adaptive alpha."""
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
            gamma_sum = sum(
                self.seq.calc_gamma(i) for i in range(1, self.num_test + 1)
            )
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
        self.r_sums[1:self.num_test] = [
            x + num_reject for x in self.r_sums[1:self.num_test]
        ]
        self.r_total += num_reject
        self.alpha_s.append(self.alpha)

        # Calculate R+ efficiently
        r_plus = self._calculate_r_plus(p_vals)
        self.r_s_plus.append(r_plus)

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals]
    
    def _calculate_r_plus(self, p_vals: list[float]) -> int:
        """Calculate R+ (maximum rejections if one p-value is set to 0).
        
        This is computed efficiently by checking what happens when we add
        a p-value of 0 to the batch.
        """
        if not p_vals:
            return 0
        
        # Create a copy with an additional p-value of 0
        augmented_p_vals = p_vals + [0.0]
        r_plus, _ = storey_bh(augmented_p_vals, self.alpha, self.lambda_)
        
        # Since we added one p-value (0), and it will definitely be rejected,
        # R+ is the total rejections minus 1
        return max(0, r_plus - 1)