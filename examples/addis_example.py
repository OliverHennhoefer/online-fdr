from online_fdr.investing.addis.addis import Addis

from online_fdr.utils.format import format_result
from online_fdr.utils.evaluation import calculate_sfdr
from online_fdr.utils.generation import DataGenerator, StandardGaussianProcess

N = 100
generator = DataGenerator(n=N, contamination=0.1, dgp=StandardGaussianProcess())
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

false_positive = 0
true_positive = 0

for i in range(0, N):

    p_value, label = generator.sample_one()  # sample generation
    result = addis.test_one(p_value)  # addis

    true_positive += 1 if label and result else 0
    false_positive += 1 if not label and result else 0
    format_result(i, result, p_value, addis.alpha)

print(f"Empirical sFDR: {calculate_sfdr(tp=true_positive, fp=false_positive)}")
