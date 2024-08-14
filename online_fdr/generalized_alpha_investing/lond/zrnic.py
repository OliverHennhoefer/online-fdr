from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.generalized_alpha_investing.lond.gamma_seq.default import (
    DefaultLondGammaSequence,
)
from online_fdr.utils import validity


class LONDZrnic(AbstractOnlineTest):
    """Implements a modified variant of '[Significance] Levels based
    On Number of Discoveries', short LOND[1]_.

    The R package 'onlineFDR' [2]_[3]_ implements this variant for 'LOND'
    (original=FALSE). The dependent modification also controls the FDR
    under positive dependence (PRDS condition)[1]_.

    [1] Zrnic, T., A. Ramdas, and M. I. Jordan.
    Asynchronous online testing of multiple hypotheses.
    Journal of Machine Learning Research, (to appear), 2021.
    [2] Robertson, D. S., Liou, L., Ramdas, A., and Karp, N. A.
    onlineFDR: Online error control. R package, 2.12.0, 2022.
    [3] Robertson, D. S., Wildenhain, J., Javanmard, A., and Karp, N. A.
    onlineFDR: an R package to control the false discovery rate for
    growing data repositories. Bioinformatics, 35:4196-4199, 2019."""

    def __init__(self, alpha: float, dependent: bool = False):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.dependent: bool = dependent

        self.num_test: int = 1
        self.seq = DefaultLondGammaSequence(c=0.07720838)
        self.alpha = self.seq.calc_gamma(self.num_test, self.alpha0)
        self.num_reject: int = 0

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        is_rejected = p_val <= self.alpha
        self.num_reject += 1 if is_rejected else 0

        self.alpha = self.calc_gamma_j()
        self.alpha *= max(self.num_reject, 1)

        return is_rejected

    def calc_gamma_j(self) -> float:
        gamma_j = self.seq.calc_gamma(self.num_test, self.alpha0)
        return (
            gamma_j
            if not self.dependent
            else gamma_j / sum(1 / i for i in range(1, self.num_test + 1))
        )
