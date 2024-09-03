from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.abstract.abstract_spend_func import AbstractSpendFunc
from online_fdr.utils import validity


class AlphaSpending(AbstractSequentialTest):
    """Implements Alpha Spending[1]_[2]_.

    References
    ----------
    [1] Lan, K. K. Gordon, and D. L. DeMets.
    "Discrete Sequential Boundaries for Clinical Trials."
    Biometrika, 70(3):659, 1983.
    [2] DeMets, D. L., and K. K. Gordon Lan.
    "Interim Analysis: The Alpha Spending Function Approach."
    Statistics in Medicine, 13(13–14):1341–1352, 1994."""

    def __init__(
        self,
        alpha: float,
        spend_func: AbstractSpendFunc,
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.rule: AbstractSpendFunc = spend_func

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)

        self.alpha = self.rule.spend(index=self.num_test, alpha=self.alpha0)
        self.num_test += 1
        return p_val < self.alpha
