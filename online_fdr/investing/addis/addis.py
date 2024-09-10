from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultSaffronGammaSequence


class Addis(AbstractSequentialTest):
    """Implements ADDIS[1]_.

    References
    ----------
    [1] Tian, J., and A. Ramdas.
    ADDIS: an adaptive discarding algorithm for
    online FDR control with conservative nulls.
    In Advances in Neural Information Processing Systems
    (NeurIPS 2019), vol. 32. Curran Associates, Inc., 2019."""

    def __init__(
        self,
        alpha: float,
        wealth: float,
        lambda_: float,
        tau: float,
    ):  # fmt: skip
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.lambda_: float = lambda_
        self.tau: float = tau

        validity.check_initial_wealth(wealth, alpha)
        validity.check_candidate_threshold(lambda_)

        self.num_test: int = 0
        self.candidates: list[bool] = []
        self.reject_idx: list[int] = []

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)

        if p_val > self.tau:  # discard
            self.alpha = None
            return False

        self.num_test += 1
        self.alpha = self.calc_alpha_t()

        p_val *= 1 / self.tau
        is_candidate = p_val <= self.lambda_  # candidate
        self.candidates.append(is_candidate)

        is_rejected = p_val <= self.alpha  # rejection
        self.reject_idx.append(self.num_test) if is_rejected else None
        return is_rejected

    def calc_alpha_t(self):
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
        alpha_t *= self.tau - self.lambda_
        return min(self.tau * self.lambda_, alpha_t)
