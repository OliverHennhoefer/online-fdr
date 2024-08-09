import math

from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class LONDJavanmard(AbstractOnlineTest):
    """Implements the original variant of '[Significance] Levels based
    On Number of Discoveries', short LOND[1]_. For beta(i), the equation
    proposed in [2]_ (equation 31) is implemented.

    The R package 'onlineFDR' [3]_[4]_ implements this variant for 'LOND'.

    [1] Javanmard, A., and Montanari, A.
    On online control of false discovery rate. arXiv preprint, 2015.
    [2] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate and false discovery
    exceedance. Annals of Statistics, 46(2):526-554, 2018.
    [3] Robertson, D. S., Liou, L., Ramdas, A., and Karp, N. A.
    onlineFDR: Online error control. R package, 2.12.0, 2022.
    [4] Robertson, D. S., Wildenhain, J., Javanmard, A., and Karp, N. A.
    onlineFDR: an R package to control the false discovery rate for
    growing data repositories. Bioinformatics, 35:4196-4199, 2019."""

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self.alpha0: float = alpha

        self.num_test: int = 1
        self.num_reject: int = 0

        self.alpha = self.calc_gamma_at_j(j=self.num_test)

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        is_rejected = p_val <= self.alpha
        self.num_reject += 1 if is_rejected else 0

        self.alpha = self.calc_gamma_at_j(self.num_test)
        self.alpha *= self.num_reject + 1

        return is_rejected

    def calc_gamma_at_j(self, j: int) -> float:
        return (
            0.07720838  # compare Javanmard2018, Equation (31)
            * self.alpha0
            * (math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j)))))
        )
