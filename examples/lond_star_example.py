import random

from online_fdr.lond.lond_star import LONDstar

random.seed(1)
x = [random.random() for _ in range(1_000)]

lond = LONDstar(alpha=0.05)

for p_val in x:
    result = lond.test_one(p_val)
    print(f"[{lond.i}] {result} ({p_val:.3f}; threshold {lond.threshold:.6f})")
