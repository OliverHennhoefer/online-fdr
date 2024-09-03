from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.functions.bonferroni import Bonferroni

from online_fdr.utils.format import format_result
from online_fdr.utils.evaluation import calculate_sfdr, calculate_power
from online_fdr.utils.generation import DataGenerator, StandardGaussianProcess

N = 100
generator = DataGenerator(n=N, contamination=0.1, dgp=StandardGaussianProcess())
alpha_spending = AlphaSpending(alpha=0.1, spend_func=Bonferroni(1_000))

false_positive = 0
true_positive = 0
false_negatives = 0

for i in range(0, N):

    p_value, label = generator.sample_one()  # sample generation
    result = alpha_spending.test_one(p_value)  # generalized alpha spending

    true_positive += label and result
    false_positive += not label and result
    false_negatives += label and not result
    format_result(i, result, p_value, alpha_spending.alpha)

print(f"Empirical sFDR: {calculate_sfdr(tp=true_positive, fp=false_positive)}")
print(f"Empirical Power: {calculate_power(tp=true_positive, fn=false_positive)}")
