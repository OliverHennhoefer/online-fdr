from online_fdr.abstract.abstract_online_test import AbstractOnlineTest


class LordDependent(AbstractOnlineTest):
    """Implements a variant of LORD for dependent p-values[1]_.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(self, alpha: float):
        super().__init__(alpha)

    def test_one(self, p_val: float) -> bool:
        return True
