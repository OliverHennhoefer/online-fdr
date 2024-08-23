import unittest

from online_fdr.investing.lord.dependent import LordDependent
from online_fdr.investing.lord.discard import LordDiscard
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.investing.lord.one import LordOne
from online_fdr.investing.lord.plus_plus import LordPlusPlus
from online_fdr.investing.lord.three import LordThree
from online_fdr.investing.lord.two import LordTwo
from online_fdr.utils.testing import get_test_data


class TestSuiteLord(unittest.TestCase):

    DATA: dict = get_test_data()

    def test_lord_one(self):
        """Disclaimer: No reference solution available!"""
        lord = LordOne(alpha=0.05, wealth=0.025, reward=0.025)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
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
        lord = LordTwo(alpha=0.05, wealth=0.025, reward=0.025)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
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
        lord = LordThree(alpha=0.05, wealth=0.025, reward=0.025)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
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
        lord = LordPlusPlus(alpha=0.05, wealth=0.025)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
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

    def test_lord_discard(self):
        lord = LordDiscard(alpha=0.05, wealth=0.025, tau=0.5)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, 6) if lord.alpha is not None\
        else None)  # fmt: skip
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.001338,
                0.000291,
                0.000248,
                0.000206,
                0.000175,
                0.000151,
                None,  # Discarded
                0.001471,
                0.00041,
                0.000355,
                None,
                0.001641,
                0.000555,
                None,  # Discarded
                None,  # Discarded
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
                False,  # Discarded
                False,
                False,
                True,
                False,  # Discarded
                False,
                True,
                False,  # Discarded
                False,  # Discarded
            ],
        )

    def test_lord_dependent(self):
        lord = LordDependent(alpha=0.05, wealth=0.025, reward=0.025)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
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

    def test_lord_memory_decay(self):
        """Disclaimer: No reference solution available!"""
        lord = LORDMemoryDecay(alpha=0.05, wealth=0.025, delta=0.99, eta=0.001)

        alpha, decision = [], []
        for i, p_value in enumerate(self.DATA["p_value"]):
            result = lord.test_one(p_value)
            alpha.append(round(lord.alpha, ndigits=6))
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                3e-06,
                1e-06,
                1e-06,
                1e-06,
                1e-06,
                1e-06,
                1e-06,
                1e-06,
                1e-06,
                1e-06,
                0.00265,
                0.000571,
                0.000481,
                0.000396,
                0.000333,
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
                False,
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
