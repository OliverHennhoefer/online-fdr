from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils import validity


class LORDMemoryDecay(AbstractOnlineTest):
    """Implements a variant of LORD."""

    def __init__(self, decay_fac: float, alpha: float):
        super().__init__(alpha)
        self.decay_fac: float = decay_fac

        validity.check_decay_factor(decay_fac)

    def test_one(self, p_val: float) -> bool:
        self.num_test += 1
        return True
