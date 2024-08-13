import random

from online_fdr.generalized_alpha_investing.lord.lord import LORD

random.seed(1)
x = [random.random() for _ in range(1_000)]

lord = LORD(alpha=0.05, wealth=0.025, gamma=0)

for p_val in x:
    result = lord.test_one(p_val)
    print(f"[{lord.num_test}] {result} ({p_val:.3f}; threshold {lord.alpha:.6f})")
