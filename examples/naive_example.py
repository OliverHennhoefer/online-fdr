from online_fdr.naive.naive import NaiveTest

from online_fdr.utils.format import format_result
from online_fdr.utils.evaluation import calculate_sfdr, calculate_power
from online_fdr.utils.generation import DataGenerator, StandardGaussianProcess

N = 100
generator = DataGenerator(n=N, contamination=0.1, dgp=StandardGaussianProcess())
naive = NaiveTest(alpha=0.05)

false_positive = 0
true_positive = 0
false_negatives = 0

for i in range(0, N):

    p_value, label = generator.sample_one()  # sample generation
    result = naive.test_one(p_value)  # naive test

    true_positive += label and result
    false_positive += not label and result
    false_negatives += label and not result
    format_result(i, result, p_value, naive.alpha)

print(f"Empirical sFDR: {calculate_sfdr(tp=true_positive, fp=false_positive)}")
print(f"Empirical Power: {calculate_power(tp=true_positive, fn=false_negatives)}")
