from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils.validity import check_p_val


class NaiveTest(AbstractSequentialTest):
    """Reference procedure without accounting for multiplicity."""

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        self.num_test += 1
        alpha_t = self.alpha if self.alpha is not None else 0.0
        return p_val < alpha_t
