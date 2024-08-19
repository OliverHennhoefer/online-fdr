from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.generalized_alpha_investing.lord.gamma_seq.default import (
    DefaultLordGammaSequence,
)
from online_fdr.utils import validity


class LordThree(AbstractOnlineTest):
    """Implements the variant LORD 3[1]_. Here, the test levels
    depend on the past only through the time of the last discovery,
    and the wealth accumulated at that time.

    This method was superseded by LORD++[2]_ and is implemented
    for demonstrative purposes only.

    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(
        self,  # fmt: skip
        alpha: float,  # fmt: skip
        wealth: float = None,  # fmt: skip
        reward: float = None,  # fmt: skip
    ):
        super().__init__(alpha)
        self.wealth: float = alpha / 2 if wealth is None else wealth
        self.reward: float = alpha / 2 if reward is None else reward
        validity.check_initial_wealth(wealth, alpha)

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.num_test: int = 1
        self.last_reject: int = 0  # tau
        self.wealth_reject: float = self.wealth  # wealth at tau

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)

        self.alpha = (
            self.seq.calc_gamma(self.num_test - self.last_reject)  # fmt: skip
            * self.wealth_reject
        )

        is_rejected = p_val <= self.alpha

        self.wealth -= self.alpha
        self.wealth += self.reward if is_rejected else 0
        self.last_reject = self.num_test if is_rejected else self.last_reject
        self.wealth_reject = self.wealth if is_rejected else self.wealth_reject

        self.num_test += 1
        return is_rejected
