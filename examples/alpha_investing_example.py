import random

from online_fdr.alpha_investing.alpha_investing import AlphaInvesting

random.seed(1)
x = [random.random() for _ in range(1_000)]

alpha_investing = AlphaInvesting(
    alpha=0.05, initial_wealth=0.025, reward=0.025, phi=0.25
)

for i, p_val in enumerate(x):
    result = alpha_investing.test_one(p_val)
    print(f"[{i+1}] {result} ({p_val:.3f}; threshold {alpha_investing.wealth:.6f})")
