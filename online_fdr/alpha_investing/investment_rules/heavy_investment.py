from online_fdr.abstract.abstract_investment_rule import AbstractInvestmentRule


class HeavyInvestment(AbstractInvestmentRule):
    """Implements the 'heavy' investment rule as presented in the
    original paper [1]_.

    References
    ----------
    [1] Foster, D., and R. Stine. α-investing: a procedure for
    sequential control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B),
    29(4):429-444, 2008."""

    @staticmethod
    def update_wealth(wealth: float, alpha: float, omega: float) -> float:
        return wealth / 2
