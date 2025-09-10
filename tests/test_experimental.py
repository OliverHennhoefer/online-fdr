import unittest

from online_fdr.batching.by import BatchBY
from online_fdr.utils.testing import generate_test_data


class TestSuiteExperimental(unittest.TestCase):
    """
    Methods in the Experimental Test Suite are derivations and
    do not have a reference implementation yet.
    Use with care.
    """

    def test_batch_bh_large(self):
        batch_bh = BatchBY(alpha=0.05)

        p_vals, batch_sizes = generate_test_data(
            n=1_000, h0_prop=0.025, max_batch_size=15, seed=1
        )

        decision = []
        start_index = 0
        for batch_size in batch_sizes:
            end_index = start_index + batch_size
            batch = p_vals[start_index:end_index]
            start_index = end_index

            result = batch_bh.test_batch(batch)
            decision += result

        self.assertEqual(sum(decision), 9)

        alpha = [round(i, 6) for i in batch_bh.alpha_s]

        n, d = float.as_integer_ratio(sum(alpha))
        self.assertEqual(
            n,
            7487468567684073,
        )

        self.assertEqual(
            d,
            18014398509481984,
        )


if __name__ == "__main__":
    unittest.main()
