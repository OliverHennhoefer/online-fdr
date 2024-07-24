from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class NaiveTest(AbstractOnlineTest):
    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        return p_val < self.alpha

    def update(self, rejected):
        """Naive online testing implements no internal update procedure."""
        pass
