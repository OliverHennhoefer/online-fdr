from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils.sequence.dependent_lord import (
    DependentLordGammaSequence,
)
from online_fdr.utils import validity


class LordDependent(AbstractSequentialTest):
    """Implements a variant of LORD for dependent p-values[1]_.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(
        self,  # fmt: skip
        alpha: float,  # fmt: skip
        wealth: float,  # fmt: skip
        reward: float,  # fmt: skip
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth: float = alpha / 2 if wealth is None else wealth
        self.reward: float = alpha / 2 if reward is None else reward
        validity.check_initial_wealth(wealth, alpha)

        self.seq = DependentLordGammaSequence(c=0.139307, b0=self.reward)

        self.last_reject: int = 0  # tau
        self.wealth_reject: float = self.wealth  # wealth at tau

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = (  # fmt: skip
            self.seq.calc_gamma(self.num_test)  # fmt: skip
            * self.wealth_reject
        )

        is_rejected = p_val <= self.alpha

        self.wealth -= self.alpha
        self.wealth += self.reward if is_rejected else 0
        self.last_reject = self.num_test if is_rejected else self.last_reject
        self.wealth_reject = self.wealth if is_rejected else self.wealth_reject

        return is_rejected
