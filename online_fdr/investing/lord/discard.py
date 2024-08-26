from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.investing.gamma_seq.default_lord import (
    DefaultLordGammaSequence,
)
from online_fdr.utils import validity


class LordDiscard(AbstractOnlineTest):
    """Implements LORD++ with discarding as
    described in [1]_.

    References
    ----------
    [1] Tian, J., and A. Ramdas.
    ADDIS: an adaptive discarding algorithm for
    online FDR control with conservative nulls.
    In Advances in Neural Information Processing Systems
    (NeurIPS 2019), vol. 32. Curran Associates, Inc., 2019."""

    def __init__(self, alpha: float, wealth: float, tau: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.tau: float = tau

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.first_reject: int | None = None  # first rejection index
        self.last_reject: list = []  # without first rejection

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)

        if p_val > self.tau:
            self.alpha = None
            return False  # discard

        self.num_test += 1

        self.alpha = self.wealth0 * self.seq.calc_gamma(self.num_test)
        self.alpha += (
            (self.tau * self.alpha0 - self.wealth0)
            * self.seq.calc_gamma(self.num_test - self.first_reject)
            if self.first_reject is not None else 0  # fmt: skip
        )
        self.alpha += (
            self.tau * self.alpha0
            * sum(self.seq.calc_gamma(self.num_test - reject_idx)
                  for reject_idx in self.last_reject)
            if self.last_reject else 0  # fmt: skip
        )

        is_rejected = p_val <= min(self.tau, self.alpha)

        (
            self.last_reject.append(self.num_test)
            if is_rejected and self.first_reject is not None
            else None
        )

        self.first_reject = (
            self.num_test if self.first_reject is None else self.first_reject
        )

        return is_rejected
