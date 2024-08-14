import math

from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
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

        self.num_test: int = 1
        self.last_reject: int = 0  # tau
        self.wealth_reject: float = self.wealth  # wealth at tau

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)

        self.alpha = (
            self.calc_gamma_at(self.num_test - self.last_reject)  # fmt: skip
            * self.wealth_reject
        )

        is_rejected = p_val <= self.alpha

        # TODO Order correct?
        self.wealth -= self.alpha
        self.wealth += self.reward if is_rejected else 0
        self.last_reject = self.num_test if is_rejected else self.last_reject
        self.wealth_reject = self.wealth if is_rejected else self.wealth_reject

        self.num_test += 1
        return is_rejected

    @staticmethod
    def calc_gamma_at(j: int) -> float:
        return 0.07720838 * (  # compare Javanmard2018, Equation (31)
            math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j))))
        )
