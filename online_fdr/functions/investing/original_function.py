from online_fdr.abstract.abstract_invest_func import AbstractInvestFunc


class OriginalInvestRule(AbstractInvestFunc):
    """Implements the original investment rule as mentioned in the
    original paper. [1]_.

    References
    ----------
    [1] Foster, D., and R. Stine. α-investing: a procedure for
    sequential control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B),
    29(4):429-444, 2008."""

    @staticmethod
    def allocate_wealth(wealth: float, alpha: float, omega: float) -> float:
        # TODO Implement the original formula
        return wealth / 2

    @staticmethod
    def decrease_wealth(wealth: float, alpha: float) -> float:
        return -alpha / (1 - alpha)
