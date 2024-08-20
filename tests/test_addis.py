import unittest

from online_fdr.generalized_alpha_investing.addis.addis import Addis
from online_fdr.utils.testing import get_test_data


class MyTestCase(unittest.TestCase):

    data = get_test_data()

    def test_addis(self):

        addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

        alpha, decision = [], []
        for i, p_value in enumerate(self.data["p_value"]):
            result = addis.test_one(p_value)
            alpha.append(
                round(addis.alpha, ndigits=6) if addis.alpha is not None else None
            )
            decision.append(result)

        self.assertEqual(
            alpha,
            [
                0.002734,
                0.005469,
                0.010937,
                0.010937,
                0.016406,
                0.021875,
                None,  # Discarded
                0.027343,
                0.00902,
                0.004715,
                None,  # Discarded
                0.010183,
                0.004779,
                None,  # Discarded
                None,  # Discarded
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


if __name__ == "__main__":
    unittest.main()
