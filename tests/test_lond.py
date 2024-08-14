import unittest

from online_fdr.generalized_alpha_investing.lond.javanmard import LONDJavanmard
from online_fdr.generalized_alpha_investing.lond.zrnic import LONDZrnic
from online_fdr.utils.testing import get_test_data


class TestCaseLOND(unittest.TestCase):
    data = get_test_data()

    alpha = 0.05
    gamma = 0

    def test_lond_javanmard(self):
        lond = LONDJavanmard(self.alpha)

        alpha = [round(lond.alpha, 6)]
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
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

    def test_lond_zrnic(self):
        lond = LONDZrnic(self.alpha, dependent=False)

        alpha = [round(lond.alpha, 6)]
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
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

    def test_lond_zrnic_dependent(self):
        lond = LONDZrnic(self.alpha, dependent=True)

        alpha = [round(lond.alpha, 6)]
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lond.test_one(p_value)
            alpha.append(round(lond.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha[:-1],
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
