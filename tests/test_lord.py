import unittest

from online_fdr.lord.lord import LORD
from tests.utils import get_test_data


class TestCaseLORD(unittest.TestCase):

    data = get_test_data()

    alpha = 0.05
    initial_wealth = 0.025
    gamma = 0

    def test_lond(self):
        lord = LORD(self.alpha, self.initial_wealth, self.gamma)

        alpha = [round(lord.alpha, 6)]
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
            [
                0.003485,
                0.004243,
                0.008374,
                0.002698,
                0.009254,
                0.010409,
                0.011428,
                0.005324,
                0.004556,
                0.003922,
                0.010406,
                0.00457,
                0.004041,
                0.010545,
                0.004719,
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
