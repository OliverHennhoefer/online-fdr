import unittest

from online_fdr.alpha_spending.alpha_spending import AlphaSpending
from online_fdr.alpha_spending.functions.bonferroni import Bonferroni
from online_fdr.alpha_spending.functions.lord_three import LordThree
from online_fdr.utils.testing import get_test_data


class TestCaseAlphaSpending(unittest.TestCase):
    DATA = get_test_data()
    K = len(DATA["p_value"])
    ALPHA = 0.05

    # Test Case 1: Alpha Spending (Bonferroni)
    def test_alpha_spending_bonferroni(self):
        alpha_spending = AlphaSpending(alpha=self.ALPHA, spend_func=Bonferroni(self.K))

        alpha_j, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha_j,
            [round((self.ALPHA / self.K), 6)] * 15,
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

    # Test Case 2: Alpha Spending (Default; LORD3)
    def test_alpha_spending_lord_three(self):
        alpha_spending = AlphaSpending(alpha=self.ALPHA, spend_func=LordThree(k=self.K))

        alpha_j, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha_j,
            [
                0.002676,
                0.000582,
                0.000496,
                0.000412,
                0.000349,
                0.000302,
                0.000266,
                0.000237,
                0.000214,
                0.000195,
                0.000179,
                0.000165,
                0.000154,
                0.000143,
                0.000134,
            ],
        )
        self.assertEqual(
            decision,
            [
                True,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
                False,
                False,
            ],
        )


if __name__ == "__main__":
    unittest.main()
