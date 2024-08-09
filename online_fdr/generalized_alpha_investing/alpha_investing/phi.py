from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class AlphaInvestingPhi(AbstractOnlineTest):
    """Implements the Alpha Investing[1]_ as found in
    https://github.com/JINJINT/ADDIS. The rule for updating
    the wealth implements an additional parameter 'phi'.

    The penalty is parameterized by 'phi' as proposed[2]_ to
    have additional control over the significance level.

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
        reward: float | None = None,
        phi: float = 0.25,
    ):
        super().__init__(alpha)
        self.wealth: float = initial_wealth or (alpha / 2)
        self.reward: float = reward or (alpha / 2)
        self.phi: float = 1 - phi
        validity.check_initial_wealth(self.wealth, self.alpha)

        self.num_test: int = 0
        self.last_reject: int = 0

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        validity.check_wealth(self.wealth)
        self.num_test += 1

        self.alpha = self.wealth / 2 if (self.num_test == 1) else self.alpha
        is_rejected = p_val <= self.alpha
        self.last_reject = self.num_test if is_rejected else self.last_reject
        self.wealth = (
            self.wealth
            - (1 - is_rejected) * self.alpha / (1 - self.alpha)
            + is_rejected * self.reward
        )

        self.alpha = min(
            self.wealth / (self.num_test + 2 - self.last_reject),
            (self.phi * self.wealth) / (self.phi * self.wealth + 1),
        )

        return is_rejected
