import unittest

from online_fdr.batching.bh import BatchBH
from online_fdr.batching.prds import BatchPRDS
from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.utils.testing import get_test_data


class TestSuiteBatching(unittest.TestCase):

    data: dict = get_test_data()

    def test_batch_bh(self):

        batch_bh = BatchBH(alpha=0.05)
        batch_no = [5, 11, 15]

        decision = []
        for start, end in zip([0] + batch_no[:-1], batch_no):
            batch = self.data["p_value"][start:end]

            result = batch_bh.test_batch(batch)
            decision += result

        alpha = [round(i, 6) for i in batch_bh.alpha_s]

        self.assertEqual(
            alpha,
            [
                0.021875,
                0.012026,
                0.030208,
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

    def test_batch_storey_bh(self):

        batch_st_bh = BatchStoreyBH(alpha=0.05, lambda_=0.5)
        batch_no = [5, 11, 15]

        decision = []
        for start, end in zip([0] + batch_no[:-1], batch_no):
            batch = self.data["p_value"][start:end]

            result = batch_st_bh.test_batch(batch)
            decision += result

        alpha = [round(i, 6) for i in batch_st_bh.alpha_s]

        self.assertEqual(
            alpha,
            [
                0.021875,
                0.048484,
                0.030208,
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

    def test_batch_prds(self):

        batch_prds = BatchPRDS(alpha=0.05)
        batch_no = [5, 11, 15]

        decision = []
        alpha = []
        for start, end in zip([0] + batch_no[:-1], batch_no):
            batch = self.data["p_value"][start:end]

            result = batch_prds.test_batch(batch)
            decision += result
            alpha.append(round(batch_prds.alpha, 6))

        self.assertEqual(
            alpha,
            [
                0.021875,
                0.012026,
                0.009429,
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


if __name__ == "__main__":
    unittest.main()
