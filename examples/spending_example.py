import random

from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.functions.bonferroni import Bonferroni
from online_fdr.utils.format import format_result

random.seed(1)
x = [random.random() for _ in range(1_000)]

# Instantiate 'alpha spending' object for sequential hypothesis testing
alpha_spend = AlphaSpending(alpha=0.05, spend_func=Bonferroni(1_000))

for i, p_val in enumerate(x):
    result = alpha_spend.test_one(p_val)  # subsequently test
    format_result(i, result, p_val, alpha_spend.alpha)
