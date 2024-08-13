import math

from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class LordPlusPlus(AbstractOnlineTest):
    """Implements LORD++. This method superseded LORD1 and
    LORD 2, so neither variant is implemented."""

    def __init__(self, alpha: float, wealth: float = None):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = alpha / 2 if wealth is None else wealth
        validity.check_initial_wealth(self.alpha0, self.wealth0)

        self.num_test: int = 1
        self.num_reject: int = 0
        self.last_reject: list = []

        self.alpha = self.calc_gamma_at_j(self.num_test) * self.wealth0

        validity.check_alpha(alpha)

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        return True

    @staticmethod
    def calc_gamma_at_j(j: int) -> float:
        return 0.07720838 * (  # compare Javanmard2018, Equation (31)
            math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j))))
        )
