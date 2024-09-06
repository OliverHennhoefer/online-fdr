from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLordGammaSequence


class OnlineFallback(AbstractSequentialTest):
    """Implements Online Fallback[1].

    References
    ----------
    [1] Tian J, Ramdas A. Online control of the familywise  error rate.
    Statistical Methods in Medical Research. 2021;30(4):976-993."""

    def __init__(
        self,
        alpha: float,
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.last_rejected: bool = False
        self.seq = DefaultLordGammaSequence(c=0.07720838)

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = self.last_rejected * self.alpha
        self.alpha += self.alpha0 * self.seq.calc_gamma(self.num_test)

        is_rejected = p_val < self.alpha
        self.last_rejected = True if is_rejected else False

        return is_rejected
