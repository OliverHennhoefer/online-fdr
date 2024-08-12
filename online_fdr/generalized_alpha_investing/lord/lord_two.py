from math import log, exp, sqrt
from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class LORDOne(AbstractOnlineTest):
    """Implements '(Significance) Levels-based On Recent Discoveries'[1]_[2]_.

    Specific implementation based on:
    https://github.com/fanny-yang/OnlineFDRCode and
    https://github.com/tijana-zrnic/SAFFRONcode and
    https://github.com/JINJINT/ADDIS, respectively.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018.
    [2] Ramdas, A., F. Yang, M. J. Wainwright, and M. I. Jordan.
    Online control of the false discovery rate with decaying memory.
    Advances in Neural Info. Processing Systems, 30:5650-5659, 2017."""

    def __init__(self, alpha: float, initial_wealth: float, gamma: float):
        super().__init__(alpha)
        self.alpha0 = alpha
        self.wealth: float = initial_wealth or alpha / 2
        validity.check_initial_wealth(self.wealth, self.alpha)

        self.num_test: int = 0
        self.num_reject: int = 0
        self.last_reject: list = []

        tmp = range(1, 10000)
        self.gamma = (
            [log(max(x, 2)) / (x * exp(sqrt(log(max(1, x))))) for x in tmp]
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
        self.last_reject.append(self.num_test) if is_rejected else None

        num_last_reject = len(self.last_reject)
        if num_last_reject > 0:
            if self.last_reject[0] <= self.num_test:
                first_gamma = self.gamma[self.num_test - self.last_reject[0]]
            else:
                first_gamma = 0
            if num_last_reject >= 2:
                idx = [self.num_test] * (self.num_reject - 1)
                gamma_idx = [g - i for g, i in zip(idx, self.last_reject[1:])]
                sum_gamma = [self.gamma[i] for i in gamma_idx]
                idx = [i <= self.num_test for i in self.last_reject]
                sum_gamma = sum([g * i for g, i in zip(sum_gamma, idx)])
            else:
                sum_gamma = 0

            self.alpha = (
                self.gamma[self.num_test] * self.wealth
                + (self.alpha0 - self.wealth) * first_gamma
                + self.alpha0 * sum_gamma
            )
        else:
            self.alpha = self.gamma[self.num_test] * self.wealth

        return is_rejected
