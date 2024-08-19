import unittest

from online_fdr.generalized_alpha_investing.lord.dependent import LordDependent
from online_fdr.generalized_alpha_investing.lord.lord import LORD
from online_fdr.generalized_alpha_investing.lord.one import LordOne
from online_fdr.generalized_alpha_investing.lord.plus_plus import LordPlusPlus
from online_fdr.generalized_alpha_investing.lord.three import LordThree
from online_fdr.generalized_alpha_investing.lord.two import LordTwo
from online_fdr.utils.testing import get_test_data


class TestCaseLORD(unittest.TestCase):
    data = get_test_data()

    alpha = 0.05
    wealth = 0.025
    gamma = 0.0
    reward = 0.025

    def test_lord(self):
        lord = LORD(self.alpha, self.wealth, self.gamma)

        alpha, decision = [round(lord.alpha, 6)], []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
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
                0.004196,
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

    def test_lord_one(self):
        """Disclaimer: No reference solution available!"""
        lord = LordOne(self.alpha, self.wealth, self.reward)

        alpha = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.001338,
                0.001338,
                0.000248,
                0.000206,
                0.000175,
                0.000151,
                0.001338,
                0.000119,
                0.000107,
                9.7e-05,
                0.001338,
                8.3e-05,
                7.7e-05,
                7.2e-05,
                6.7e-05,
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

    def test_lord_two(self):
        """Disclaimer: No reference solution available!"""
        lord = LordTwo(self.alpha, self.wealth, self.reward)

        alpha = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.001338,
                0.001629,
                0.000539,
                0.000454,
                0.000381,
                0.000326,
                0.001622,
                0.000543,
                0.000473,
                0.000411,
                0.0017,
                0.000614,
                0.00054,
                0.000473,
                0.000421,
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

    def test_lord_three(self):
        """Disclaimer: No reference solution available!"""
        lord = LordThree(self.alpha, self.wealth, self.reward)

        alpha = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.001338,
                0.002604,
                0.003803,
                0.000827,
                0.000704,
                0.000586,
                0.004824,
                0.001049,
                0.000893,
                0.000743,
                0.00576,
                0.001253,
                0.001067,
                0.006665,
                0.00145,
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
                True,
                False,
                False,
            ],
        )

    def test_lord_plus_plus(self):
        lord = LordPlusPlus(self.alpha, self.wealth)

        alpha = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.001338,
                0.001629,
                0.003215,
                0.001036,
                0.000876,
                0.000738,
                0.003309,
                0.001136,
                0.000987,
                0.000854,
                0.003426,
                0.001251,
                0.0011,
                0.003639,
                0.001438,
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
                True,
                False,
                False,
            ],
        )

    def test_lord_dependent(self):
        lord = LordDependent(self.alpha, self.wealth, self.reward)

        alpha = []
        decision = []
        for i, p_value in enumerate(self.data["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.010458,
                0.008270,
                0.001971,
                0.000736,
                0.000376,
                0.000227,
                0.000211,
                0.000151,
                0.000114,
                0.000089,
                0.000094,
                0.000077,
                0.000065,
                0.000055,
                0.000048,
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
