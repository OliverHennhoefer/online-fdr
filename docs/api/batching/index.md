# Batch Testing Methods

Batch testing methods extend classical multiple testing procedures to the online setting, where hypotheses arrive in batches over time and must be tested sequentially while maintaining overall FDR control across all batches.

## Overview

The batching framework, developed by Zrnic et al. (2020), addresses scenarios where:
- Tests naturally arrive in groups (batches)
- Each batch can be processed using classical procedures
- Overall FDR control is required across all batches
- Adaptive alpha allocation improves power over time

## Available Methods

### Benjamini-Hochberg Batch Testing
::: online_fdr.batching.bh.BatchBH

### Storey-BH Batch Testing  
::: online_fdr.batching.storey_bh.BatchStoreyBH

### Benjamini-Yekutieli Batch Testing
::: online_fdr.batching.by.BatchBY

### PRDS Batch Testing
::: online_fdr.batching.prds.BatchPRDS

## Key Concepts

### Alpha Allocation

The batching framework uses a gamma sequence $\{_t\}$ to allocate alpha budget across batches:
- **Batch 1**: $_1 = _1  $  
- **Batch t**: $_t$ calculated using inter-batch dependency corrections

### R Calculation

For each batch, the algorithm computes $R^+$ (maximum possible rejections if one p-value were 0):
- Used to determine optimal alpha allocation for future batches
- Balances current discoveries with future testing power
- Key innovation enabling adaptive power allocation

### _t Correction

The inter-batch dependency correction $_t$ accounts for:
- Previous batch results affecting current alpha allocation
- Preventing "double spending" of alpha across batches
- Maintaining valid FDR control despite dependencies

## Batch Size Considerations

| Batch Size | Recommended Method | Gamma Sequence | Notes |
|------------|-------------------|----------------|-------|
| < 10 | BatchBH | Polynomial decay | Small batch penalty |
| 10-100 | BatchBH/BatchStoreyBH | Polynomial decay | Good balance |
|  100 | BatchStoreyBH | Half sequence |  estimation effective |
| Variable | BatchBH | Adaptive | Handles size variation |

## Method Comparison

### Power Under Different Conditions

| Method | Independent | PRDS | Arbitrary Dependence |  < 1 |
|--------|------------|------|-------------------|--------|
| BatchBH | Excellent | Good | May not control | Good |
| BatchStoreyBH | Excellent | Good | May not control | Excellent |
| BatchBY | Good | Good | Conservative extension | Fair |
| BatchPRDS | Excellent | Excellent | May not control | Good |

### Computational Complexity

| Method | Per-batch Time | Per-batch Space | Cumulative Storage |
|--------|----------------|-----------------|-------------------|
| BatchBH | O(n log n) | O(n) | O(T) |
| BatchStoreyBH | O(n log n) | O(n) | O(T) |  
| BatchBY | O(n log n) | O(n) | O(T) |
| BatchPRDS | O(n log n) | O(n) | O(1) |

where n = batch size, T = number of batches.

## Usage Guidelines

### Method Selection

1. **BatchBH**: Default choice for most applications
2. **BatchStoreyBH**: When  < 1 and batches are reasonably large
3. **BatchBY**: When a conservative BY-style within-batch correction is desired
4. **BatchPRDS**: When positive dependence structure is known

### Parameter Tuning

- **Alpha**: Set based on desired FDR level (typically 0.05 or 0.1)
- **Gamma sequence**: Use defaults unless specific decay patterns needed
- ** (Storey)**: 0.5 is standard, higher values more conservative

### Practical Implementation

```python
from online_fdr.batching import BatchBH

# Initialize batch testing procedure
batch_test = BatchBH(alpha=0.05)

# Process batches sequentially  
batches = [
    [0.001, 0.02, 0.15, 0.8],      # Batch 1
    [0.03, 0.9, 0.006, 0.4],       # Batch 2  
    [0.12, 0.005, 0.7, 0.25]       # Batch 3
]

all_decisions = []
for i, batch in enumerate(batches, 1):
    decisions = batch_test.test_batch(batch)
    discoveries = sum(decisions)
    all_decisions.extend(decisions)
    print(f"Batch {i}: {discoveries}/{len(batch)} discoveries")

total_discoveries = sum(all_decisions)
print(f"Total: {total_discoveries} discoveries with FDR  0.05")
```

## Advanced Topics

### Asynchronous Batching

When batches complete out of order:
- Maintain batch ordering for FDR calculations
- Buffer results until dependencies resolved  
- Use timestamps or sequence numbers

### Variable Batch Sizes

The framework naturally handles:
- Different batch sizes across time
- Empty batches (no effect on FDR control)
- Very large batches (may need memory management)

### Online-to-Batch Adaptation

Converting online methods to batch setting:
- Group individual tests into batches
- Apply batch framework with chosen internal procedure
- May improve power over pure online methods

## Applications

### Genomics
- **GWAS studies**: SNPs tested in chromosomal batches
- **RNA-seq**: Genes tested by biological pathway
- **Meta-analysis**: Studies combined in batches

### A/B Testing
- **Feature releases**: Tests grouped by release cycle
- **Market segments**: Tests batched by user demographic  
- **Time periods**: Daily/weekly testing batches

### Clinical Trials
- **Interim analyses**: Endpoints tested in groups
- **Safety monitoring**: Adverse events by system
- **Biomarker discovery**: Markers tested by assay batch

## Implementation Notes

### Memory Management
- Store only essential statistics between batches
- Use efficient R calculation algorithms
- Consider streaming for very large batch sequences

### Numerical Stability  
- Handle very small p-values carefully
- Avoid numerical overflow in cumulative calculations
- Use log-space computations when appropriate

### Validation
- Verify FDR control through simulation
- Test edge cases (empty batches, extreme p-values)
- Benchmark against known implementations

## References

Zrnic, T., D. Jiang, A. Ramdas, and M. I. Jordan (2020). "The Power of Batching in Multiple Hypothesis Testing." *Proceedings of the 37th International Conference on Machine Learning (ICML)*, PMLR, 119:11504-11515.

Benjamini, Y., and Y. Hochberg (1995). "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." *Journal of the Royal Statistical Society: Series B*, 57(1):289-300.

Storey, J. D. (2002). "A direct approach to false discovery rates." *Journal of the Royal Statistical Society: Series B*, 64(3):479-498.
