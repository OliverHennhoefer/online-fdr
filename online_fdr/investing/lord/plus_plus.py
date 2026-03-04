import math

from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLordGammaSequence


class LordPlusPlus(AbstractSequentialTest):
    """Implements LORD++, an improved variant that superseded LORD1 and LORD2.

    LORD++ uses a wealth-based approach where alpha levels are determined by
    accumulated wealth and the gamma sequence. The method tracks rejections
    and spends wealth accordingly.

    References
    ----------
    [1] Ramdas, A., Zrnic, T., Wainwright, M.J. and Jordan, M.I. (2017).
    "SAFFRON: an adaptive algorithm for online control of the false discovery rate."
    arXiv preprint arXiv:1802.09098.

    [2] Javanmard, A., and Montanari, A. (2018).
    "Online Rules for Control of False Discovery Rate and False Discovery Exceedance."
    Annals of Statistics, 46(2):526-554.
    """

    def __init__(self, alpha: float, wealth: float, reward: float | None = None):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.wealth: float = wealth

        validity.check_initial_wealth(wealth, alpha)
        if reward is not None and not math.isclose(reward, alpha):
            raise ValueError("LordPlusPlus guarantee regime requires reward == alpha.")
        self.reward: float = alpha

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.first_reject: int | None = None  # first rejection index
        self.last_reject: list = []  # rejection indices without first
        self.wealth_at_first_reject: float | None = None

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        # Calculate alpha based on LORD++ formula
        self.alpha = self.wealth0 * self.seq.calc_gamma(self.num_test)

        if self.first_reject is not None:
            # Add contribution from first rejection
            self.alpha += (self.alpha0 - self.wealth0) * self.seq.calc_gamma(
                self.num_test - self.first_reject
            )

            # Add contributions from subsequent rejections
            self.alpha += self.alpha0 * sum(
                self.seq.calc_gamma(self.num_test - reject_idx)
                for reject_idx in self.last_reject
            )

        # Ensure we don't spend more than available wealth
        self.alpha = min(self.alpha, self.wealth)

        is_rejected = p_val <= self.alpha

        # Update wealth: spend alpha, gain reward if rejected
        self.wealth -= self.alpha
        if is_rejected:
            self.wealth += self.reward

            if self.first_reject is None:
                # First rejection
                self.first_reject = self.num_test
                self.wealth_at_first_reject = self.wealth
            else:
                # Subsequent rejection
                self.last_reject.append(self.num_test)

        return is_rejected
