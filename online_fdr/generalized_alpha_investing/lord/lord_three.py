from online_fdr.abstract.abstract_online_test import AbstractOnlineTest


class LordThree(AbstractOnlineTest):

    def __init__(self, alpha: float):
        super().__init__(alpha)

    def test_one(self, p_val: float) -> bool:
        return True