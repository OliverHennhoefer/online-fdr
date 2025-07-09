from online_fdr.investing.lord.mem_decay import LORDMemoryDecay

from online_fdr.utils.format import format_result
from online_fdr.utils.evaluation import calculate_sfdr, calculate_power, MemoryDecayFDR
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

N = 500
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(
    n=N, pi0=0.98, dgp=dgp
)  # pi0 = 1 - contamination = 1 - 0.02 = 0.98
# Create LORD Memory Decay instance
# eta=0.5 is the new default (moderate detection threshold)
# For more aggressive detection, use eta=1.0
# For more conservative detection, use eta=0.1
mem_decay_lord = LORDMemoryDecay(alpha=0.1, delta=0.99, eta=0.5)

false_positive = 0
true_positive = 0
false_negatives = 0

mem_fdr = MemoryDecayFDR(delta=0.99, offset=0)
for i in range(0, N):

    p_value, label = generator.sample_one()  # sample generation
    result = mem_decay_lord.test_one(p_value)  # mem-decay LORD

    fdr = mem_fdr.score_one(result, label)  # Fixed: (prediction, ground_truth)
    # print(f"Memory-Decay FDR: {fdr}")  # Comment out for performance

    true_positive += label and result
    false_positive += not label and result
    false_negatives += label and not result
    format_result(i, result, p_value, mem_decay_lord.alpha)

print(f"Empirical sFDR: {calculate_sfdr(tp=true_positive, fp=false_positive)}")
print(f"Empirical Power: {calculate_power(tp=true_positive, fn=false_negatives)}")
