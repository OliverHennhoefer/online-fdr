from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.investing.gamma_seq.default_lord import (
    DefaultLordGammaSequence,
)
from online_fdr.utils import validity


class LORDMemoryDecay(AbstractOnlineTest):
    """Implements the LORD variant with memory decay[1]_.

    References
    ----------
    [1] Rebjock, Q., B. Kurt, T. Januschowski, and L. Callot.
    Online false discovery rate control for anomaly detection in time series.
    In Advances in Neural Information Processing Systems (NeurIPS 2021),
    vol. 34, pp. 26487-26498. Curran Associates, Inc., 2021."""

    def __init__(
        self,  # fmt: skip
        alpha: float,  # fmt: skip
        wealth: float,  # fmt: skip
        delta: float = 0.99,  # fmt: skip
        eta: float = 0.0001,  # fmt: skip
        l: float = None  # fmt: skip
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.delta: float = delta  # decay factor
        self.eta: float = eta  # smoothing factor
        self.l: float = 0 if l is None else l  # dependency window

        validity.check_decay_factor(delta)

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.first_reject: int | None = None  # first rejection index
        self.last_reject: list = []  # rejection indices without first

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = (
            self.alpha0
            * self.eta
            * max(self.seq.calc_gamma(self.num_test), 1 - self.delta)
        )
        self.alpha += self.alpha0 * sum(
            [
                (self.delta ** (self.num_test - reject_idx - self.l))
                * self.seq.calc_gamma(self.num_test - reject_idx - self.l)
                for reject_idx in self.last_reject
            ]
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