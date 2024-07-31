import random

from online_fdr.alpha_investing.alpha_investing import AlphaInvesting
from online_fdr.functions.investing.original_function import OriginalInvestRule

random.seed(1)
x = [random.random() for _ in range(1_000)]

investing_rule = OriginalInvestRule()
alpha_investing = AlphaInvesting(alpha=0.05, rule=investing_rule)

for i, p_val in enumerate(x):
    result = alpha_investing.test_one(p_val)
    print(f"[{i+1}] {result} ({p_val:.3f}; threshold {alpha_investing.wealth:.6f})")
