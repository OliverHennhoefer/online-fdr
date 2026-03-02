from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.utils.evaluation import calculate_power, calculate_sfdr
from online_fdr.utils.format import format_result
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

N = 250
B = 50
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(
    n=N, pi0=0.95, dgp=dgp
)  # pi0 = 1 - contamination = 1 - 0.05 = 0.95
batch_stbh = BatchStoreyBH(alpha=0.1, lambda_=0.5)

false_positive = 0
true_positive = 0
false_negatives = 0

for i in range(0, N // B):
    p_values, labels = [], []
    for _ in range(B):  # batch generation
        p_value, label = generator.sample_one()
        p_values.append(p_value)
        labels.append(label)

    results = batch_stbh.test_batch(p_values)  # generalized alpha spending

    for j in range(len(p_values)):
        p_value = p_values[j]
        label = labels[j]
        result = results[j]
        test_idx = i * B + j

        # Update counters based on the conditions
        true_positive += label and result
        false_positive += not label and result
        false_negatives += label and not result

        # Call format_result to handle the formatted output
        format_result(test_idx, result, p_value, batch_stbh.alpha)

print(f"Empirical sFDR: {calculate_sfdr(tp=true_positive, fp=false_positive)}")
print(f"Empirical Power: {calculate_power(tp=true_positive, fn=false_negatives)}")
