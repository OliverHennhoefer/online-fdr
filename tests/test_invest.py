import unittest

from online_fdr.investing.alpha.alpha import Gai
from online_fdr.utils.testing import get_test_data


class TestSuiteAlphaInvesting(unittest.TestCase):

    DATA: dict = get_test_data()

    def test_generalized_alpha_investing(self):

        gai = Gai(alpha=0.05, wealth=0.025)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = gai.test_one(p_value)
            alpha.append(round(gai.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.010819,
                0.021406,
                0.041915,
                0.014226,
                0.035034,
                0.054982,
                0.074121,
                0.028363,
                0.015822,
                0.010364,
                0.031333,
                0.014488,
                0.009360,
                0.030372,
                0.013888,
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
