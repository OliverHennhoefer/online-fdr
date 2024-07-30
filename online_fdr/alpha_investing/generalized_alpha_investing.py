from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class GeneralizedAlphaInvesting(AbstractOnlineTest):
    """Implements the Generalized Alpha Investing.[1]_ which
    encompasses the original Alpha Investing as well as other
    cases like LORD[2]_ and LOND[3]_.

    The original implementation AlphaInvesting() can be

    References
    ----------
    [1] Foster, D., and R. Stine. α-investing: a procedure for
    sequential control of expected false discoveries.
    Journal of the Royal Statistical Society (Series B),
    29(4):429-444, 2008.
    [2] Javanmard, A., and A. Montanari. Online rules for control
    of false discovery rate and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018.
    [3] Javanmard, A., and A. Montanari.
    On Online Control of False Discovery Rate.
    arXiv preprint arXiv:1502.06197, 2015"""

    def __init__(self, alpha: float, initial_wealth: float):
        super().__init__(alpha)
        self.wealth: float = initial_wealth or alpha


    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        return True
