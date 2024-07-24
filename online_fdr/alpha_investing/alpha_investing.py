from online_fdr.abstract.abstract_investment_rule import AbstractInvestmentRule
from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.alpha_investing.investment_rules.base_investment import (
    BaseInvestment,
)
from online_fdr.utils.validity import check_p_val, check_initial_wealth


class AlphaInvesting(AbstractOnlineTest):
    """Implements Alpha Investing."""

    def __init__(
        self,
        alpha: float,
        initial_wealth: float | None = None,
        payout: float | None = None,
        rule: AbstractInvestmentRule | None = None,
    ):
        super().__init__(alpha)
        check_initial_wealth(initial_wealth, alpha)
        self.payout: float = payout or alpha
        self.wealth: float = initial_wealth or alpha
        self.rule = rule or BaseInvestment()

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        alpha = self.rule.update_wealth(self.wealth, self.alpha, self.payout)
        is_rejected = p_val <= alpha
        self.wealth += (self.payout - alpha) if is_rejected else -alpha
        return is_rejected
