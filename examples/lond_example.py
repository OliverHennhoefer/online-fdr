import random

from online_fdr.generalized_alpha_investing.lond.javanmard import LONDJavanmard

random.seed(1)
x = [random.random() for _ in range(1_000)]

lond = LONDJavanmard(alpha=0.05)

for p_val in x:
    result = lond.test_one(p_val)
    print(f"[{lond.i}] {result} ({p_val:.3f}; threshold {lond.alpha:.6f})")
