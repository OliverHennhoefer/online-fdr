import unittest

from online_fdr.investing.lond.lond import Lond
from online_fdr.utils.testing import get_test_data


class TestSuiteLond(unittest.TestCase):

    DATA: dict = get_test_data()

    def test_lond_original(self):

        lond = Lond(alpha=0.05, original=True, dependent=False)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.002676,
                0.001164,
                0.000991,
                0.000824,
                0.000699,
                0.000605,
                0.000798,
                0.000712,
                0.000642,
                0.000585,
                0.000716,
                0.000661,
                0.000614,
                0.000717,
                0.000672,
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
                True,
                False,
                False,
            ],
        )

    def test_lond_original_dependent(self):

        lond = Lond(alpha=0.05, original=True, dependent=True)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.002676,
                0.000776,
                0.000541,
                0.000396,
                0.000306,
                0.000247,
                0.000308,
                0.000262,
                0.000227,
                0.000200,
                0.000237,
                0.000213,
                0.000193,
                0.000176,
                0.000162,
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

    def test_lond_modified(self):
        lond = Lond(alpha=0.05, original=False, dependent=False)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.002676,
                0.000582,
                0.000496,
                0.000412,
                0.000349,
                0.000302,
                0.000532,
                0.000475,
                0.000428,
                0.000390,
                0.000537,
                0.000496,
                0.000461,
                0.000430,
                0.000403,
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

    def test_lond_modified_dependent(self):
        lond = Lond(alpha=0.05, original=False, dependent=True)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.002676,
                0.000388,
                0.000270,
                0.000198,
                0.000153,
                0.000123,
                0.000205,
                0.000175,
                0.000151,
                0.000133,
                0.000178,
                0.000160,
                0.000145,
                0.000132,
                0.000122,
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
