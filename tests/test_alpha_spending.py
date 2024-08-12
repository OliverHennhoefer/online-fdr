import unittest

from online_fdr.alpha_spending.alpha_spending import AlphaSpending
from online_fdr.alpha_spending.functions.bonferroni import Bonferroni
from online_fdr.alpha_spending.functions.lord_three import LordThree
from tests.utils import get_test_data


class TestCaseAlphaSpending(unittest.TestCase):
    data = get_test_data()  # test data
    k = len(data["p_value"])  # number of tests to be performed
    alpha = 0.05  # significance level

    def test_alpha_spending_bonferroni(self):
        alpha_spending = AlphaSpending(
            alpha=self.alpha, spend_func=Bonferroni(k=self.k)
        )

        alpha_j = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.threshold, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha_j,
            [round((self.alpha / self.k), 6)] * 15,  # Bonferroni
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

    def test_alpha_spending_lord_three(self):
        alpha_spending = AlphaSpending(alpha=self.alpha, spend_func=LordThree(k=self.k))

        alpha_j = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.threshold, ndigits=6))
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
