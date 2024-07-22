from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class LORD(AbstractOnlineTest):
    """Implements '(Significance) Levels-based On Recent Discoveries'."""

    def test_one(self, p_val: float) -> bool:
        pass

    def transform_one(self, p_val: float) -> float:
        check_p_val(p_val)
        return p_val  # LORD adapts the significance threshold
