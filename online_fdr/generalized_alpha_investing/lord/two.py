from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.generalized_alpha_investing.lord.gamma_seq.default import (
    DefaultLordGammaSequence,
)
from online_fdr.utils import validity


class LordTwo(AbstractOnlineTest):
    """Implements the variant LORD 2[1]_. Here, the test levels
    are set based on previous discovery times.

    This method was superseded by LORD++[2]_ and is implemented
    for demonstrative purposes only.

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
        self.last_reject: list = []

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.alpha = self.seq.calc_gamma(self.num_test) * self.wealth0

        is_rejected = p_val <= self.alpha
        self.num_reject += 1 if is_rejected else 0

        if self.last_reject:
            self.alpha += (
                sum(
                    self.seq.calc_gamma(self.num_test - last_reject)
                    for last_reject in self.last_reject
                )
                * self.reward
            )

        self.last_reject.append(self.num_test) if is_rejected else None
        self.num_test += 1

        return is_rejected
