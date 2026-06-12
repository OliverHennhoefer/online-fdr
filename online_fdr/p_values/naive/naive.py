from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils.validity import check_p_val


class NaiveTest(AbstractSequentialTest):
    """Reference procedure without accounting for multiplicity."""

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        self._advance_hypotheses()
        alpha_t = self.target_level
        self._set_test_level(alpha_t)
        return p_val <= alpha_t
