import math

from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DefaultLondGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for LOND variants as
    proposed by [1]_ in equation 31.

    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate and false discovery
    exceedance. Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(self, c: float):
        super().__init__(c)

    def calc_gamma(self, j: int, alpha: float):
        return (
            self.c
            * alpha
            * (math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j)))))
        )
