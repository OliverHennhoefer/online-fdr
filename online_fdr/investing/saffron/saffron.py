from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultSaffronGammaSequence


class Saffron(AbstractSequentialTest):
    """SAFFRON: Serial estimate of the Alpha Fraction that is Futilely Rationed On true Nulls.
    
    SAFFRON is an adaptive algorithm for online FDR control that estimates the proportion 
    of true null hypotheses and uses this estimate to set more powerful rejection thresholds. 
    It can be seen as an online analogue of the famous offline Storey-BH adaptive procedure.
    
    Like alpha-investing algorithms, SAFFRON starts with alpha-wealth that it intelligently 
    allocates to different tests over time, earning back wealth on discoveries. However, 
    unlike older methods, SAFFRON's threshold sequence is based on a novel estimate of the 
    alpha fraction allocated to true null hypotheses.
    
    SAFFRON typically achieves higher power than non-adaptive methods like LORD under 
    independence, similar to how Storey-BH typically outperforms Benjamini-Hochberg.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).
        wealth: Initial alpha-wealth for purchasing rejection thresholds.
                Must satisfy 0 ≤ wealth ≤ alpha.  
        lambda_: Candidate threshold for estimating the proportion of nulls.
                 P-values ≤ lambda_ are considered "candidates". Must be in (0, 1).

    Attributes:
        alpha0: Original target FDR level.
        wealth0: Initial wealth allocation.
        lambda_: Candidate threshold parameter.
        num_test: Number of hypotheses tested so far.
        candidates: Boolean list indicating which tests were candidates.
        reject_idx: Indices of rejected hypotheses.

    Examples:
        >>> # Basic usage with recommended parameters
        >>> saffron = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)
        >>> decision = saffron.test_one(0.01)  # Test a small p-value
        >>> print(f"Rejected: {decision}")
        
        >>> # Sequential testing
        >>> p_values = [0.001, 0.3, 0.02, 0.8, 0.005]
        >>> decisions = [saffron.test_one(p) for p in p_values]
        >>> discoveries = sum(decisions)

    References:
        Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan (2018). 
        "SAFFRON: an adaptive algorithm for online control of the FDR." 
        Proceedings of the 35th International Conference on Machine Learning (ICML), 
        Proceedings of Machine Learning Research, vol. 80, pp. 4286-4294, PMLR.
        
        ArXiv: https://arxiv.org/abs/1802.09098
        ICML: https://proceedings.mlr.press/v80/ramdas18a.html
    """

    def __init__(self, alpha: float, wealth: float, lambda_: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.lambda_: float = lambda_

        validity.check_initial_wealth(wealth, alpha)
        validity.check_candidate_threshold(lambda_)

        self.num_test: int = 0
        self.candidates: list[bool] = []
        self.reject_idx: list[int] = []

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the SAFFRON procedure.
        
        The SAFFRON algorithm processes p-values sequentially:
        1. Calculate adaptive rejection threshold based on candidate estimate
        2. Determine if p-value is a candidate (≤ lambda_) 
        3. Reject if p-value ≤ adaptive threshold
        
        Args:
            p_val: P-value to test. Must be in [0, 1].
            
        Returns:
            True if the null hypothesis is rejected (discovery), False otherwise.
            
        Raises:
            ValueError: If p_val is not in [0, 1].
            
        Examples:
            >>> saffron = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)
            >>> saffron.test_one(0.01)  # Small p-value, likely rejected
            True
            >>> saffron.test_one(0.8)   # Large p-value, not rejected
            False
        """
        validity.check_p_val(p_val)
        self.num_test += 1
        self.alpha = self.calc_alpha_t()

        is_candidate = p_val <= self.lambda_  # candidate
        self.candidates.append(is_candidate)

        is_rejected = p_val <= self.alpha  # rejection
        self.reject_idx.append(self.num_test) if is_rejected else None
        return is_rejected

    def calc_alpha_t(self):
        """Calculate the adaptive rejection threshold for the current test.
        
        The SAFFRON threshold is based on estimating the alpha-wealth allocated to 
        true null hypotheses using the candidate fraction. The threshold adapts based on:
        1. Initial wealth allocation and candidate estimate (first test)
        2. Updated wealth based on discoveries and candidate history (subsequent tests)
        3. Compensation factor (1 - lambda_) for candidate selection
        
        Returns:
            The adaptive rejection threshold alpha_t, bounded by lambda_.
            
        Note:
            This is an internal method called by test_one(). The threshold formula
            follows the SAFFRON procedure in Ramdas et al. (2018).
        """

        if self.num_test == 1:
            alpha_t = (
                (1 - self.lambda_)
                * self.seq.calc_gamma(1, None)  # fmt: skip
                * self.wealth0
            )
        else:
            alpha_t = self.wealth0 * self.seq.calc_gamma(
                self.num_test - sum(self.candidates), None
            )
            if len(self.reject_idx) >= 1:
                tau_1 = self.reject_idx[0]
                c_1_plus = sum(self.candidates[tau_1:])
                alpha_t += (self.alpha0 - self.wealth0) * self.seq.calc_gamma(
                    (self.num_test - tau_1 - c_1_plus), None
                )
            if len(self.reject_idx) >= 2:
                alpha_t += self.alpha0 * sum(
                    self.seq.calc_gamma(
                        (self.num_test - idx - sum(self.candidates[idx:])),
                        None,
                    )
                    for idx in self.reject_idx[1:]
                )
            alpha_t *= 1 - self.lambda_
        return min(self.lambda_, alpha_t)
