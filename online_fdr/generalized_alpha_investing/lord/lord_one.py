from online_fdr.abstract.abstract_online_test import AbstractOnlineTest


class LordOne(AbstractOnlineTest):
    def __init__(
        self,
        alpha: float,
        gamma: float,
        wealth: float,
        kappa: float,
        reward: float,
    ):
        super().__init__(alpha)
        self.gamma: float = gamma
        self.wealth: float = wealth
        self.kappa: float = kappa  # proportionality constant
        self.reward: float = reward

        self.num_test: int = 0

    def test_one(self, p_val: float) -> bool:
        return True
