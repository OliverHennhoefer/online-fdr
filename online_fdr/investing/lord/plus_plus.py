from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence.default_lord import DefaultLordGammaSequence


class LordPlusPlus(AbstractSequentialTest):
    """Implements LORD++[1]_ that superseded LORD1 and
    LORD2, so neither variant is implemented.

    References
    ----------
    """

    def __init__(self, alpha: float, wealth: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.first_reject: int | None = None  # first rejection index
        self.last_reject: list = []  # rejection indices without first

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = self.wealth0 * self.seq.calc_gamma(self.num_test)
        self.alpha += (
            (self.alpha0 - self.wealth0)
            * self.seq.calc_gamma(self.num_test - self.first_reject)
            if self.first_reject is not None else 0  # fmt: skip
        )
        self.alpha += (
            self.alpha0
            * sum(self.seq.calc_gamma(self.num_test - reject_idx)
                  for reject_idx in self.last_reject)
            if self.last_reject else 0  # fmt: skip
        )

        is_rejected = p_val <= self.alpha

        (
            self.last_reject.append(self.num_test)
            if is_rejected and self.first_reject is not None
            else None
        )

        self.first_reject = (
            self.num_test if self.first_reject is None else self.first_reject
        )

        return is_rejected
