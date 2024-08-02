import random

from online_fdr.lond.lond import LOND

random.seed(1)
x = [random.random() for _ in range(1_000)]

lond = LOND(alpha=0.05, initial_wealth=0.025, gamma=0)

for p_val in x:
    result = lond.test_one(p_val)
    print(f"[{lond.i}] {result} ({p_val:.3f}; threshold {lond.alpha:.6f})")
