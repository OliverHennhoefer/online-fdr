import unittest

from tests.utils import get_test_data


class MyTestCase(unittest.TestCase):

    data = get_test_data()

    def test_alpha_investing(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == "__main__":
    unittest.main()
