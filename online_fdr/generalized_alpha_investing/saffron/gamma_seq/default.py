from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DefaultSaffronGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for SAFFRON[1]_, parameterizable
    to conform to the implementation in the R package 'onlineFDR'[2]_[3]_..

    [1] Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan.
    SAFFRON: an adaptive algorithm for online control of the FDR.
    In Proceedings of the Internat. Conference on Machine Learning, 2018.
    [2] Robertson, D. S., Liou, L., Ramdas, A., and Karp, N. A.
    onlineFDR: Online error control. R package, 2.12.0, 2022.
    [3] Robertson, D. S., Wildenhain, J., Javanmard, A., and Karp, N. A.
    onlineFDR: an R package to control the false discovery rate for
    growing data repositories. Bioinformatics, 35:4196-4199, 2019."""

    def __init__(self, gamma_exp, c):
        super().__init__(gamma_exp=gamma_exp, c=c)

    def calc_gamma(self, j: int, alpha: float | None):
        return j**self.gamma_exp if self.c is None \
            else self.c / j**self.gamma_exp  # fmt: skip
