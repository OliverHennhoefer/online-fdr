import random

from online_fdr.naive.naive import NaiveTest
from online_fdr.utils.format import format_result

random.seed(1)
x = [random.random() for _ in range(1_000)]

# Instantiate 'naive' object for sequential hypothesis testing
naive = NaiveTest(alpha=0.05)

for i, p_val in enumerate(x):
    result = naive.test_one(p_val)  # subsequently test
    format_result(i, result, p_val, naive.alpha)
