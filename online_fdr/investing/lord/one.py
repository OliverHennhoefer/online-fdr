from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.investing.gamma_seq.default_lord import (
    DefaultLordGammaSequence,
)
from online_fdr.utils import validity


class LordOne(AbstractOnlineTest):
    """Implements the variant LORD 1[1]_. Here, the test levels
    are set solely based on the time of the last discovery.

    This method was superseded by LORD++[2]_ and is implemented
    for demonstrative purposes only.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018.
    [2] Ramdas, A., Yang, F., Wainwright, M. J., and Jordan, M. I.
    Online control of the false discovery rate with decaying memory.
    Advances in Neural Information Processing Systems, 30, 2017."""

    def __init__(
        self,  # fmt: skip
        alpha: float,  # fmt: skip
        wealth: float = None,  # fmt: skip
        reward: float = None,  # fmt: skip
    ):
        super().__init__(alpha)
        self.wealth0: float = alpha / 2 if wealth is None else wealth
        self.reward: float = alpha / 2 if reward is None else reward

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.num_test: int = 1
        self.num_reject: int = 0
        self.last_reject: int | None = None

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)

        self.alpha = (
            self.seq.calc_gamma(self.num_test, self.alpha) * self.wealth0
            if self.last_reject is None
            else (
                self.seq.calc_gamma(  # fmt: skip
                    self.num_test - self.last_reject, self.alpha
                )
                * self.reward
            )
        )

        is_rejected = p_val <= self.alpha
        self.num_reject += 1 if is_rejected else 0

        self.last_reject = self.num_test if is_rejected else None
        self.num_test += 1

        return is_rejected
