import unittest

from online_fdr.alpha_investing.alpha_investing import AlphaInvesting
from online_fdr.functions.investing.foster_stine import FosterStine
from tests.utils import get_test_data


class MyTestCase(unittest.TestCase):

    data = get_test_data()
    alpha = 0.05
    initial_wealth = 0.025
    payout = 0.025
    phi = 0.25
    rule = FosterStine()

    def test_alpha_investing_foster_stine(self):
        alpha_investing = AlphaInvesting(
            self.alpha, self.initial_wealth, self.payout, self.phi
        )

        wealth_j = [self.initial_wealth]
        alpha_j = [self.initial_wealth / 2]
        num_rej = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_investing.test_one(p_value)
            wealth_j.append(round(alpha_investing.wealth, ndigits=6))
            alpha_j.append(round(alpha_investing.alpha, ndigits=6))
            num_rej.append(alpha_investing.num_reject)
            decision.append(result)

        self.assertEqual(
            alpha_j[:-1],
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
            wealth_j[:-1],
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
            num_rej[:-1],
            [
                1,
                2,
                2,
                4,
                5,
                6,
                6,
                6,
                6,
                10,
                10,
                10,
                13,
                13,
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
