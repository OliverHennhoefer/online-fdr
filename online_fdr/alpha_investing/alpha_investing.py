from online_fdr.abstract.abstract_invest_rule import AbstractInvestRule
from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.rules.investing.original_function import (
    OriginalInvestRule,
)
from online_fdr.utils.validity import check_p_val, check_initial_wealth


class AlphaInvesting(AbstractOnlineTest):
    """Implements the original Alpha Investing[1]_.

    References
    ----------
    [1] Foster, D., and R. Stine. α-investing: a procedure for
    sequential control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B),
    29(4):429-444, 2008."""

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
        # in contrast to GAI, the original AI invests only on acceptance of H0
        self.wealth += (
            self.payout
            if is_rejected
            else self.rule.decrease_wealth(self.wealth, self.alpha)
        )
        return is_rejected
