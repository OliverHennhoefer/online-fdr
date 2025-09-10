import unittest

from online_fdr.investing.saffron.saffron import Saffron
from online_fdr.utils.testing import get_test_data


class TestSuiteSaffron(unittest.TestCase):
    DATA: dict = get_test_data()

    def test_saffron(self):
        saffron = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = saffron.test_one(p_value)
            alpha.append(round(saffron.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.005469,
                0.010937,
                0.021875,
                0.021875,
                0.032812,
                0.043749,
                0.054686,
                0.01804,
                0.01804,
                0.01804,
                0.028977,
                0.013037,
                0.013037,
                0.023975,
                0.011445,
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
