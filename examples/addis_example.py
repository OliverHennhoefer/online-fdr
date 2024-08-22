import random

from online_fdr.investing.addis.addis import Addis
from online_fdr.utils.format import format_result

random.seed(1)
x = [random.random() for _ in range(1_000)]

# Instantiate 'ADDIS' object for sequential hypothesis testing
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

for i, p_val in enumerate(x):
    result = addis.test_one(p_val)  # subsequently test
    format_result(i, result, p_val, addis.alpha)
