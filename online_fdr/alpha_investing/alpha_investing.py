from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class AlphaInvesting(AbstractOnlineTest):
    """Implements Alpha Investing."""

    def __init__(
        self,
        alpha: float,
        initial_wealth: float | None = None,
        payout: float | None = None,
    ):
        super().__init__(alpha)
        self.payout: float = payout or alpha
        self.wealth: float = initial_wealth or alpha

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        alpha = self.wealth / 2  # alpha allocation
        is_rejected = p_val <= alpha
        self.wealth += (self.payout - alpha) if is_rejected else -alpha
        return is_rejected

    def transform_one(self, p_val: float) -> float:
        check_p_val(p_val)
        return p_val  # method only adapts the significance threshold
