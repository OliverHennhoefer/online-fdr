import unittest

from online_fdr.generalized_alpha_investing.alpha_investing.alpha_investing import (
    AlphaInvestingPhi,
)
from online_fdr.generalized_alpha_investing.alpha_investing.foster_stine import (
    AlphaInvestingFosterStine,
)
from tests.utils import get_test_data


class TestCaseAlphaInvesting(unittest.TestCase):

    data: dict = get_test_data()

    alpha: float = 0.05
    initial_wealth: float = 0.025
    reward: float = 0.025
    phi: float = 0.25

    def test_alpha_investing_foster_stine(self):
        """Test case for the original 'Alpha Investing' (non-generalized)."""
        alpha_investing = AlphaInvestingFosterStine(
            alpha=self.alpha,
            wealth=self.initial_wealth,
            reward=self.reward,
            generalized_version=False,
        )

        wealth = []  # test sequence: wealth
        alpha = []  # test sequence: alpha
        decision = []  # test sequence: decision
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_investing.test_one(p_value)
            wealth.append(round(alpha_investing.wealth, ndigits=6))
            alpha.append(round(alpha_investing.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.0125,
                0.025,
                0.0375,
                0.018019,
                0.030519,
                0.043019,
                0.055519,
                0.026128,
                0.012713,
                0.006275,
                0.018775,
                0.009208,
                0.004561,
                0.017061,
                0.008382,
            ],
        )

        self.assertEqual(
            wealth,
            [
                0.05,
                0.075,
                0.036039,
                0.061039,
                0.086039,
                0.111039,
                0.052256,
                0.025427,
                0.01255,
                0.03755,
                0.018416,
                0.009122,
                0.034122,
                0.016765,
                0.008312,
            ],
        )

        self.assertEqual(
            decision,
            [
                True,
                True,
                False,
                True,
                True,
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                True,
                False,
                False,
            ],
        )

    def test_alpha_investing_foster_stine_generalized(self):
        """Test case for the original 'Alpha Investing' (generalized)."""
        alpha_investing = AlphaInvestingFosterStine(
            alpha=self.alpha,
            wealth=self.initial_wealth,
            reward=self.reward,
            generalized_version=True,
        )

        wealth = []  # test sequence: wealth
        alpha = []  # test sequence: alpha
        decision = []  # test sequence: decision
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_investing.test_one(p_value)
            wealth.append(round(alpha_investing.wealth, ndigits=6))
            alpha.append(round(alpha_investing.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.0125,
                0.018671,
                0.021658,
                0.010589,
                0.017738,
                0.021209,
                0.022875,
                0.01117,
                0.005522,
                0.002746,
                0.013869,
                0.006837,
                0.003395,
                0.014192,
                0.006994,
            ],
        )

        self.assertEqual(
            wealth,
            [
                0.037342,
                0.043316,
                0.021178,
                0.035476,
                0.042418,
                0.045749,
                0.022339,
                0.011043,
                0.005491,
                0.027738,
                0.013674,
                0.00679,
                0.028383,
                0.013987,
                0.006944,
            ],
        )

        self.assertEqual(
            decision,
            [
                True,
                True,
                False,
                True,
                True,
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                True,
                False,
                False,
            ],
        )

    def test_alpha_investing_phi(self):
        alpha_investing = AlphaInvestingPhi(
            self.alpha, self.initial_wealth, self.reward, self.phi
        )

        wealth = []
        alpha = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_investing.test_one(p_value)
            wealth.append(round(alpha_investing.wealth, ndigits=6))
            alpha.append(round(alpha_investing.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
            [
                0.025,
                0.0375,
                0.012013,
                0.030519,
                0.043019,
                0.055519,
                0.017419,
                0.008632,
                0.005164,
                0.025411,
                0.008249,
                0.004108,
                0.020715,
                0.006759,
            ],
        )

        self.assertEqual(
            wealth[:-1],
            [
                0.05,
                0.075,
                0.036039,
                0.061039,
                0.086039,
                0.111039,
                0.052256,
                0.034528,
                0.025821,
                0.050821,
                0.024748,
                0.01643,
                0.04143,
                0.020277,
            ],
        )

        self.assertEqual(
            decision,
            [
                True,
                True,
                False,
                True,
                True,
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                True,
                False,
                False,
            ],
        )


if __name__ == "__main__":
    unittest.main()
