import random

from online_fdr.naive.naive import NaiveTest

random.seed(1)
x = [random.random() for _ in range(1_000)]

naive = NaiveTest(alpha=0.05)

for p_val in x:
    result = naive.test_one(p_val)
    print(f"{result} ({p_val:.3f})")
