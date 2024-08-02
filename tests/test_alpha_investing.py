import unittest

from online_fdr.alpha_investing.alpha_investing import AlphaInvesting
from tests.utils import get_test_data


class MyTestCase(unittest.TestCase):

    data = get_test_data()

    alpha = 0.05
    initial_wealth = 0.025
    reward = 0.025
    phi = 0.25

    def test_alpha_investing(self):
        alpha_investing = AlphaInvesting(
            self.alpha, self.initial_wealth, self.reward, self.phi
        )

        wealth = [self.initial_wealth]
        alpha = [self.initial_wealth / 2]
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_investing.test_one(p_value)
            wealth.append(round(alpha_investing.wealth, ndigits=6))
            alpha.append(round(alpha_investing.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
            [
                0.0125,
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
                0.025,
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
