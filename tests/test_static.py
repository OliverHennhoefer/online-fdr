import random
import unittest

from online_fdr.utils.static import bh, storey_bh


class TestSuiteAlphaSpending(unittest.TestCase):

    random.seed(1)
    p_values = [random.uniform(0, 1) for _ in range(20)] + [
        random.uniform(0, 0.05) for _ in range(3)
    ]

    def test_bh(self):

        rejections, threshold = bh(self.p_values, alpha=0.05)

        self.assertEqual(rejections, 2)
        self.assertEqual(threshold, 0.004347826086956522)

    def test_storey_bh(self):

        rejections, threshold = storey_bh(self.p_values, alpha=0.05, lambda_=0.5)

        self.assertEqual(rejections, 2)
        self.assertEqual(threshold, 0.0021060533511106927)


if __name__ == "__main__":
    unittest.main()
