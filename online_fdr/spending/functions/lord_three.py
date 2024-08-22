from math import log, exp, sqrt

from online_fdr.abstract.abstract_spend_func import AbstractSpendFunc


class LordThree(AbstractSpendFunc):
    """Alpha Spending Function based on LORD3[1_] equation (31).

    [1] Javanmard, A., and A. Montanari.
    "Online Rules for Control of False Discovery Rate
    and False Discovery Exceedance."
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(self, k):
        super().__init__(k)
        self.threshold = [
            0.07720838 * log(max(i, 2)) / (i * exp(sqrt(log(i))))
            for i in range(1, self.k + 1)
        ]

    def spend(self, index: int, alpha: float) -> float:
        return alpha * self.threshold[index]
