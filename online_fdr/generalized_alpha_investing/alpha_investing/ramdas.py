from online_fdr.abstract.abstract_online_test import AbstractOnlineTest


class AlphaInvestingRamdas(AbstractOnlineTest):
    """Implements a modified version of Alpha Investing[1]_.

    The R package 'onlineFDR' [2]_[3]_ implements this variant
    for 'alpha investing'.

    [1] Ramdas, A., Zrnic, T., Wainwright, M., and Jordan, M. SAFFRON:
    an adaptive algorithm for online control of the false discovery rate.
    Proceedings of the 35th International Conference on Machine Learning,
    80:4286-4294, 2018.
    [2] Robertson, D. S., Liou, L., Ramdas, A., and Karp, N. A.
    onlineFDR: Online error control. R package, 2.12.0, 2022.
    [3] Robertson, D. S., Wildenhain, J., Javanmard, A., and Karp, N. A.
    onlineFDR: an R package to control the false discovery rate for
    growing data repositories. Bioinformatics, 35:4196-4199, 2019."""

    def __init__(self, alpha: float):
        self.alpha = alpha

    def test_one(self, p_val: float) -> bool:
        pass
