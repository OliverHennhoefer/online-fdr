import math

from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DependentLordGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for the 'dependent' LORD [1]_ variant
    as implemented in [2]_[3]_.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018.
    [2] Robertson, D. S., Liou, L., Ramdas, A., and Karp, N. A.
    onlineFDR: Online error control. R package, 2.12.0, 2022.
    [3] Robertson, D. S., Wildenhain, J., Javanmard, A., and Karp, N. A.
    onlineFDR: an R package to control the false discovery rate for
    growing data repositories. Bioinformatics, 35:4196-4199, 2019."""

    def __init__(self, c: float, b0: float):
        super().__init__(c=c, b0=b0)

    def calc_gamma(self, j: int, alpha: float) -> float:
        # return (self.c * alpha) / (self.b0 * j * (math.log(max(j, 2)) ** 3))
        return self.c / (j * (math.log(max(j, 2)) ** 3))
