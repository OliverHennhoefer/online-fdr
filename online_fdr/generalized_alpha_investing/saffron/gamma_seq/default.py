import math

from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DefaultSaffronGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for SAFFRON[1]_.

    [1] Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan.
    SAFFRON: an adaptive algorithm for online control of the FDR.
    In Proceedings of the Internat. Conference on Machine Learning, 2018."""

    def __init__(self, gamma_exp):
        super().__init__(gamma_exp)

    def calc_gamma(self, j: int, alpha: float | None):
        return math.pow(j, self.gamma_exponent)
