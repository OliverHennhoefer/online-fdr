from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class NaiveTest(AbstractOnlineTest):
    """Reference procedure without accounting for multiplicity."""

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        return p_val < self.alpha
