import unittest

from online_fdr.spending.online_fallback import OnlineFallback
from online_fdr.utils.testing import get_test_data


class TestSuiteOnlineFallback(unittest.TestCase):

    DATA: dict = get_test_data()

    def test_online_fallback(self):
        alpha_spending = OnlineFallback(alpha=0.05)

        alpha_j, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = alpha_spending.test_one(p_value)
            alpha_j.append(round(alpha_spending.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha_j,
            [
                0.002676,
                0.003258,
                0.003753,
                0.000412,
                0.000349,
                0.000302,
                0.000568,
                0.000237,
                0.000214,
                0.000195,
                0.000374,
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
                True,
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
