import math

from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DefaultLondGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for LOND variants as
    proposed by [1]_.

    References
    ----------
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


class DefaultLordGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for LORD variants as
    proposed by [1]_.

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


class DefaultSaffronGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for SAFFRON[1]_.

    [1] Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan.
    SAFFRON: an adaptive algorithm for online control of the FDR.
    In Proceedings of the Internat. Conference on Machine Learning, 2018."""

    def __init__(self, gamma_exp, c):
        super().__init__(gamma_exp=gamma_exp, c=c)

    def calc_gamma(self, j: int, alpha: None = None):
        return j**self.gamma_exp if self.c is None \
            else self.c / j**self.gamma_exp  # fmt: skip


class DependentLordGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for the 'dependent' LORD [1]_ variant.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(self, c: float, b0: float):
        super().__init__(c=c, b0=b0)

    def calc_gamma(self, j: int, alpha: None = None) -> float:
        return self.c / (j * (math.log(max(j, 2)) ** 3))
