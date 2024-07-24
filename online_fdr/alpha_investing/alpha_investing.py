from online_fdr.abstract.abstract_invest_rule import AbstractInvestRule
from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.invest_rules.original_function import (
    OriginalInvestRule,
)
from online_fdr.utils.validity import check_p_val, check_initial_wealth


class AlphaInvesting(AbstractOnlineTest):
    """Implements Alpha Investing."""

    def __init__(
        self,
        alpha: float,
        initial_wealth: float | None = None,
        payout: float | None = None,
        rule: AbstractInvestRule | None = None,
    ):
        super().__init__(alpha)
        self.payout: float = payout or alpha
        self.wealth: float = initial_wealth or alpha
        self.rule = rule or OriginalInvestRule()
        check_initial_wealth(self.wealth, self.alpha)

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        self.alpha = self.rule.allocate_wealth(self.wealth, self.alpha, self.payout)
        is_rejected = p_val <= self.alpha
        self.wealth += (
            self.payout
            if is_rejected
            else self.rule.decrease_wealth(self.wealth, self.alpha)
        )
        return is_rejected
