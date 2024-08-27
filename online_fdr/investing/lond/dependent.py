from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.investing.gamma_seq.default_lond import (
    DefaultLondGammaSequence,
)
from online_fdr.utils import validity


class LondDependent(AbstractOnlineTest):
    """Implements the a variant of '[Significance] Levels based
    On Number of Discoveries', short LOND[1]_, for arbitrarily
    dependent p-values.

    References
    ----------
    [1] Javanmard, A., and Montanari, A.
    On online control of false discovery rate. arXiv preprint, 2015.
    """

    def __init__(
        self,  # fmt: skip
            alpha: float,  # fmt: skip
            original: bool = True,  # fmt: skip
            dependent: bool = False  # fmt: skip
    ):
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

        self.alpha = self.seq.calc_gamma(self.num_test, self.alpha0)
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
