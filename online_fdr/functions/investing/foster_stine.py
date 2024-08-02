from online_fdr.abstract.abstract_invest_func import AbstractInvestFunc


class FosterStine(AbstractInvestFunc):
    """Implements the original investment rule as mentioned in the
    original paper. [1]_.

    References
    ----------
    [1] Foster, D., and R. Stine. α-investing: a procedure for
    sequential control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B),
    29(4):429-444, 2008."""

    def invest(
        self, k: int, wealth: float, alpha: float, phi: float, last_reject: int
    ) -> float:
        if k == 1:
            return wealth / 2
        else:
            return min(
                wealth / (1 + k + 2 - last_reject),
                ((1 - phi) * wealth) / ((1 - phi) * wealth + 1),
            )

    def reduce(self, wealth: float, alpha: float) -> float:
        return -alpha / (1 - alpha)
