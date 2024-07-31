import unittest

from online_fdr.alpha_spending.alpha_spending import AlphaSpending
from online_fdr.functions.spending.bonferroni import Bonferroni
from online_fdr.functions.spending.lord_three import LordThree


class TestCaseOnlineFDR(unittest.TestCase):
    data = {
        "id": [
            "A15432",
            "B90969",
            "C18705",
            "B49731",
            "E99902",
            "C38292",
            "A30619",
            "D46627",
            "E29198",
            "A41418",
            "D51456",
            "C88669",
            "E03673",
            "A63155",
            "B66033",
        ],
        "date": [
            "2014-12-01",
            "2014-12-01",
            "2014-12-01",
            "2015-09-21",
            "2015-09-21",
            "2015-09-21",
            "2015-09-21",
            "2015-09-21",
            "2016-05-19",
            "2016-05-19",
            "2016-11-12",
            "2017-03-27",
            "2017-03-27",
            "2017-03-27",
            "2017-03-27",
        ],
        "p_value": [
            2.90e-14,
            0.00143,
            0.06514,
            0.00174,
            0.00171,
            3.61e-05,
            0.79149,
            0.27201,
            0.28295,
            7.59e-08,
            0.69274,
            0.30443,
            0.000487,
            0.72342,
            0.54757,
        ],
        "decision_times": list(range(2, 17)),
        "lags": [1] * 15,
    }

    def test_alpha_spending_bonferroni(self):

        alpha = 0.05
        k = len(self.data["p_value"])
        alpha_spending = AlphaSpending(alpha=alpha, spend_func=Bonferroni(k=k))

        alpha_j = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.threshold, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha_j,
            [round((alpha / k), 6)] * 15,  # (Non-Adaptive) Bonferroni
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

        alpha = 0.05
        k = len(self.data["p_value"])
        alpha_spending = AlphaSpending(alpha=alpha, spend_func=LordThree(k=k))

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
