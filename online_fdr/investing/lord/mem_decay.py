from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class LORDMemoryDecay(AbstractOnlineTest):
    """Implements a variant of LORD."""

    def __init__(self, alpha: float, delta: float):
        super().__init__(alpha)
        self.delta: float = delta

        validity.check_decay_factor(delta)

    def test_one(self, p_val: float) -> bool:
        self.num_test += 1
        return True
