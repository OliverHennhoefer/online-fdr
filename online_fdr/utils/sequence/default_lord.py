import math

from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DefaultLordGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for LORD variants as
    proposed by [1]_ in equation 31.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate and false discovery
    exceedance. Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(self, c: float):
        super().__init__(c)

    def calc_gamma(self, j: int, alpha: None = None):
        return (
            self.c  # fmt: skip
            * math.log(max(j, 2))
            / (j * math.exp(math.sqrt(math.log(j))))
        )
