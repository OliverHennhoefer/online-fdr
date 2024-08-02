import unittest

from online_fdr.lond.lond import LOND
from tests.utils import get_test_data


class MyTestCase(unittest.TestCase):

    data = get_test_data()

    alpha = 0.05
    initial_wealth = 0.025
    gamma = 0

    def test_lond(self):
        lond = LOND(self.alpha, self.initial_wealth, self.gamma)

        alpha = [round(lond.alpha, 6)]
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
            [
                0.003485,
                0.001516,
                0.002582,
                0.002147,
                0.002731,
                0.00315,
                0.003464,
                0.00309,
                0.002788,
                0.002539,
                0.002796,
                0.002583,
                0.0024,
                0.002614,
                0.002451,
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
