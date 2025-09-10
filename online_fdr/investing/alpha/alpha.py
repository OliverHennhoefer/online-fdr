from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultSaffronGammaSequence


class Gai(AbstractSequentialTest):
    """GAI: Generalized Alpha-Investing for online FDR control with SAFFRON updates.
    
    Generalized Alpha-Investing (GAI) extends the original alpha-investing procedure 
    of Foster and Stine (2008) for sequential control of expected false discoveries.
    This implementation uses SAFFRON-style update rules for improved power while 
    maintaining the core alpha-investing philosophy.
    
    Alpha-investing resembles alpha-spending but with a key difference: when a test 
    rejects a null hypothesis, the procedure earns additional probability toward 
    subsequent tests. This allows incorporation of domain knowledge and improved power 
    over non-adaptive methods.
    
    The GAI framework has become fundamental for online hypothesis testing, providing 
    a robust, computationally efficient approach that requires no parametric assumptions 
    about underlying null and alternative distributions.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).
        wealth: Initial alpha-wealth for purchasing rejection thresholds.
                Must satisfy 0 ≤ wealth ≤ alpha.

    Attributes:
        alpha0: Original target FDR level.
        wealth0: Initial wealth allocation.
        num_test: Number of hypotheses tested so far.
        candidates: Boolean list indicating which tests were candidates.
        reject_idx: Indices of rejected hypotheses.

    Examples:
        >>> # Basic usage
        >>> gai = Gai(alpha=0.05, wealth=0.025)
        >>> decision = gai.test_one(0.01)  # Test a small p-value
        >>> print(f"Rejected: {decision}")
        
        >>> # Sequential testing with wealth dynamics
        >>> p_values = [0.001, 0.3, 0.02, 0.8, 0.005]
        >>> decisions = [gai.test_one(p) for p in p_values]
        >>> discoveries = sum(decisions)

    References:
        Foster, D., and R. Stine (2008). "α-investing: a procedure for sequential 
        control of expected false discoveries." Journal of the Royal Statistical 
        Society (Series B), 70(2):429-444.
        
        Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan (2018). 
        "SAFFRON: an adaptive algorithm for online control of the FDR." 
        Proceedings of the 35th International Conference on Machine Learning (ICML), 
        Proceedings of Machine Learning Research, vol. 80, pp. 4286-4294, PMLR.
    """

    def __init__(self, alpha: float, wealth: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth

        validity.check_initial_wealth(wealth, alpha)
        validity.check_candidate_threshold(alpha)

        self.num_test: int = 0
        self.candidates: list[bool] = []
        self.reject_idx: list[int] = []

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1
        self.alpha = self.calc_alpha_t()

        is_candidate = p_val <= self.alpha  # candidate
        self.candidates.append(is_candidate)

        is_rejected = p_val <= self.alpha  # rejection
        self.reject_idx.append(self.num_test) if is_rejected else None
        return is_rejected

    def calc_alpha_t(self):

        if self.num_test == 1:
            alpha_t = (
                self.seq.calc_gamma(1, None)  # fmt: skip
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
        return alpha_t / (1 + alpha_t)
