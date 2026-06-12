from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DependentLordGammaSequence


class LordDependent(AbstractSequentialTest):
    """Implements a variant of LORD for dependent p-values[1]_.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(
        self,
        alpha: float,
        wealth: float,
        reward: float,
    ):  # fmt: skip
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth: float = wealth
        self.reward: float = reward
        validity.check_initial_wealth(wealth, alpha)
        validity.check_reward_budget(wealth=wealth, reward=reward, alpha=alpha)

        # onlineFDR LORDdep default xi_i:
        # xi_i = 0.139307 * alpha / (b0 * i * log(max(i,2))^3)
        self.seq = DependentLordGammaSequence(
            c=0.139307 * self.alpha0 / self.reward,
            b0=self.reward,
        )

        self.last_reject: int = 0  # tau
        self.wealth_reject: float = self.wealth  # wealth at tau

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        index = self.num_hypotheses + 1

        alpha_t = (  # fmt: skip
            self.seq.calc_gamma(index)  # fmt: skip
            * self.wealth_reject
        )
        self._set_test_level(alpha_t)
        self._advance_hypotheses()

        is_rejected = p_val <= alpha_t

        self.wealth -= alpha_t
        self.wealth += self.reward if is_rejected else 0
        self.last_reject = index if is_rejected else self.last_reject
        self.wealth_reject = self.wealth if is_rejected else self.wealth_reject

        return is_rejected
