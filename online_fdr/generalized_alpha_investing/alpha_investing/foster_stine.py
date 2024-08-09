from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class AlphaInvestingFosterStine(AbstractOnlineTest):
    """Implements the original version of Alpha Investing[1]_.

    The original (non-generalized) method only controls the mFDR.

    Strictly spoken, this version does not conform to the overall
    framework of 'Generalized Alpha Investing' as the alpha wealth
    does not get depleted by rejections. For 'Generalized Alpha
    Investing' the alpha wealth gets reduced iteratively, regardless
    of whether a rejection was made (a reward was granted) or not.

    Setting the parameter 'gen[eralized]' to True makes the online
    test conform to the framework of 'Generalized Alpha Investing'.
    This variant controls provably controls FDR for independent p-values.

    The alpha levels a(j) can be chosen arbitrarily, as long as they
    satisfy: a(j)/(a(j) - 1) <= W(j-1) (see validity.check_wealth())
    This guarantees that the available wealth does not turn negative.
    Here, the implementation is based on [1]_.

    Implemented default fallbacks in the constructor are based on [1]_.

    References
    ----------
    [1] Foster, D., and R. Stine. α-investing: a procedure for
    sequential control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B),
    29(4):429-444, 2008."""

    def __init__(
        self,
        alpha: float,
        wealth: float,
        reward: float,
        generalized_version: bool = True,
    ):
        super().__init__(alpha)
        self.wealth: float = wealth or alpha
        self.reward: float = reward or alpha
        self.generalized: bool = generalized_version

        validity.check_initial_wealth(wealth, alpha)

        self.num_test: int = 0
        self.last_reject: int = 0

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        validity.check_wealth(self.wealth)

        self.num_test += 1

        self.alpha = self.wealth / 2
        is_rejected = p_val <= self.alpha
        self.last_reject = self.num_test if is_rejected else 0

        self.wealth += is_rejected * self.reward
        self.wealth -= (
            (self.alpha / (1 - self.alpha))
            if self.generalized
            else (1 - is_rejected) * (self.alpha / (1 - self.alpha))
        )

        return is_rejected
