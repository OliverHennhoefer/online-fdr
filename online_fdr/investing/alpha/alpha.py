from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultSaffronGammaSequence


class Gai(AbstractSequentialTest):
    """Implements a variant of the original Alpha-Investing[1]_
    as categorized by Generalized Alpha-Investing[2]_ that
    is based on the update rule SAFFRON[2]_

    References
    ----------
    [1] Foster, D., and R. Stine.
    α-investing: a procedure for seq. control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B), 70(2):429-444, 2008.
    [2] Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan.
    SAFFRON: an adaptive algorithm for online control of the FDR.
    In Proceedings of the 35th Internat. Conference on ML (ICML 2018),
    Proceedings of ML Research, vol. 80, pp. 4283-4291, PMLR, 2018."""

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
