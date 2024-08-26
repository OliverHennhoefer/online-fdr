import unittest

from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.functions.bonferroni import Bonferroni
from online_fdr.spending.functions.lord_three import LordThree
from online_fdr.utils.testing import get_test_data


class TestSuiteAlphaSpending(unittest.TestCase):

    DATA: dict = get_test_data()

    def test_alpha_spending_bonferroni(self):

        k = len(self.DATA["p_value"])
        alpha_spending = AlphaSpending(alpha=0.05, spend_func=Bonferroni(k=k))

        alpha_j, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha_j,
            [round((0.05 / k), 6)] * 15,
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
        k = len(self.DATA["p_value"])
        alpha_spending = AlphaSpending(alpha=0.05, spend_func=LordThree(k=k))

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
