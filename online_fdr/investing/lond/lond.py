from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLondGammaSequence


class Lond(AbstractSequentialTest):
    """Implements the original variant of '[Significance] Levels based
    On Number of Discoveries', short LOND[1]_. As gamma sequence, the
    equation proposed in [2]_ (Equation 31) is implemented.

    References
    ----------
    [1] Javanmard, A., and Montanari, A.
    On online control of false discovery rate. arXiv preprint, 2015.
    [2] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate and false discovery
    exceedance. Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(
        self,
            alpha: float,
            original: bool = True,
            dependent: bool = False
    ):  # fmt: skip
        super().__init__(alpha)
        self.alpha0: float = alpha

        self.num_test: int = 0
        self.num_reject: int = 0

        self.seq = DefaultLondGammaSequence(c=0.07720838)

        self.original: bool = original
        self.dependent: bool = dependent

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = self.seq.calc_gamma(self.num_test, alpha=self.alpha0)
        self.alpha /= (
            sum(1 / i for i in range(1, self.num_test + 1))
            if self.dependent
            else 1  # fmt: split
        )
        self.alpha *= (
            self.num_reject + 1 if self.original else max(self.num_reject, 1)
        )  # fmt: split

        is_rejected = p_val <= self.alpha
        self.num_reject += 1 if is_rejected else 0

        return is_rejected
