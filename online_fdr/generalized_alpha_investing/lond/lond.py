from math import log, exp, sqrt
from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class LOND(AbstractOnlineTest):
    """Implements '(Significance) Levels-based On Recent Discoveries'[1]_[2]_.

    Specific implementation is based on https://github.com/JINJINT/ADDIS.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018.
    [2] Ramdas, A., F. Yang, M. J. Wainwright, and M. I. Jordan.
    Online control of the false discovery rate with decaying memory.
    Advances in Neural Info. Processing Systems, 30:5650-5659, 2017"""

    def __init__(self, alpha: float, initial_wealth: float, gamma: float):
        super().__init__(alpha)
        self.alpha0 = alpha
        self.wealth: float = initial_wealth or alpha / 2
        validity.check_initial_wealth(self.wealth, self.alpha)

        self.num_test: int = 0
        self.num_reject: int = 0

        tmp = range(1, 10000)
        self.gamma = (
            [log(max(x, 2)) / (x * exp(sqrt(log(x)))) for x in tmp]
            if gamma == 0
            else [1 / (x**gamma) for x in tmp]
        )
        self.gamma = [x / sum(self.gamma) for x in self.gamma]
        self.alpha: float = self.gamma[0] * self.wealth

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        validity.check_wealth(self.wealth)

        self.num_test += 1

        is_rejected = True if p_val < self.alpha else False
        self.num_reject += is_rejected

        self.alpha = float(
            self.alpha0 * self.gamma[self.num_test] * max(1, self.num_reject)
        )
        return is_rejected
