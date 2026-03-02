# Utility Functions

The utils module provides essential supporting functions for online FDR control algorithms, including static procedures, gamma sequences, validation functions, and data generation utilities.

## Static Procedures

Core implementations of classical multiple testing procedures:

::: online_fdr.utils.static.bh
::: online_fdr.utils.static.storey_bh
::: online_fdr.utils.static.by

## Gamma Sequences  

Specialized sequences for alpha allocation in online procedures:

::: online_fdr.utils.sequence.DefaultSaffronGammaSequence
::: online_fdr.utils.sequence.DefaultLordGammaSequence
::: online_fdr.utils.sequence.DefaultLondGammaSequence

## Validation Functions

Input validation and error checking:

::: online_fdr.utils.validity.check_p_val
::: online_fdr.utils.validity.check_alpha
::: online_fdr.utils.validity.check_initial_wealth
::: online_fdr.utils.validity.check_candidate_threshold
::: online_fdr.utils.validity.check_wealth
::: online_fdr.utils.validity.check_decay_factor

## Overview

### Static Procedures

The static module contains implementations of classical FDR control procedures that form the building blocks for online and batch methods:

- **Benjamini-Hochberg (BH)**: The foundational FDR procedure
- **Storey-BH**: Enhanced power through  estimation  
- **Benjamini-Yekutieli (BY)**: FDR control under arbitrary dependence

These functions are used internally by batch testing methods and can also be used directly for offline multiple testing.

### Gamma Sequences

Gamma sequences determine how alpha budget is allocated over time in online procedures. Different algorithms require different sequence properties:

- **SAFFRON sequences**: Power-law decay optimized for adaptive procedures
- **LORD sequences**: Logarithmic decay for wealth-based procedures  
- **LOND sequences**: Complex decay balancing early/late power

### Validation Framework

The validation module ensures input correctness and provides informative error messages:

- **Range validation**: P-values in [0,1], alpha in (0,1)
- **Relationship validation**: Initial wealth < alpha
- **State validation**: Wealth depletion detection

## Usage Examples

### Static Procedures

```python
from online_fdr.utils.static import bh, storey_bh, by

# Sample p-values  
p_values = [0.001, 0.02, 0.15, 0.8, 0.9]
alpha = 0.05

# Standard Benjamini-Hochberg
num_rej_bh, threshold_bh = bh(p_values, alpha)
print(f"BH: {num_rej_bh} rejections at threshold {threshold_bh:.4f}")

# Storey-BH with  estimation
num_rej_storey, threshold_storey = storey_bh(p_values, alpha, lambda_=0.5)
print(f"Storey-BH: {num_rej_storey} rejections at threshold {threshold_storey:.4f}")

# Benjamini-Yekutieli (under dependence)
num_rej_by, threshold_by = by(p_values, alpha)  
print(f"BY: {num_rej_by} rejections at threshold {threshold_by:.4f}")
```

### Gamma Sequences

```python
from online_fdr.utils.sequence import DefaultSaffronGammaSequence

# Create SAFFRON gamma sequence
gamma_seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)

# Generate first 10 gamma values
gamma_values = [gamma_seq.calc_gamma(j) for j in range(1, 11)]
print("SAFFRON gamma sequence:", gamma_values)

# Show decay behavior
import matplotlib.pyplot as plt
j_values = range(1, 101)
gamma_values = [gamma_seq.calc_gamma(j) for j in j_values]
plt.loglog(j_values, gamma_values)
plt.xlabel("Position j")
plt.ylabel("Gamma value")
plt.title("SAFFRON Gamma Sequence Decay")
```

### Validation Functions

```python
from online_fdr.utils.validity import check_p_val, check_alpha, check_initial_wealth

# Validate inputs
try:
    check_p_val(0.05)           # Valid p-value
    check_alpha(0.05)           # Valid alpha  
    check_initial_wealth(0.025, 0.05)  # Valid wealth < alpha
    print("All validations passed")
except ValueError as e:
    print(f"Validation error: {e}")

# Example of validation failure
try:
    check_p_val(1.5)            # Invalid p-value > 1
except ValueError as e:
    print(f"P-value validation failed: {e}")
```

## Algorithm Support

### How Utilities Support Online Algorithms

1. **Static procedures** provide the core multiple testing logic
2. **Gamma sequences** control alpha allocation strategies  
3. **Validation functions** ensure algorithmic correctness
4. **Data utilities** support testing and evaluation

### Customization and Extension

The utility framework supports customization:

- **Custom gamma sequences**: Inherit from `AbstractGammaSequence`
- **Custom spending functions**: Implement `AbstractSpendFunc`  
- **Custom static procedures**: Follow the standard interface
- **Additional validation**: Extend existing validation functions

## Best Practices

### Static Procedure Usage

1. **Choose appropriate procedure** based on dependence assumptions
2. **Handle edge cases** (empty input, all p-values = 1)
3. **Validate inputs** before calling procedures
4. **Understand threshold interpretation** for downstream usage

### Gamma Sequence Selection

1. **Use algorithm-specific defaults** when available
2. **Consider decay rate** for your application timeline
3. **Validate convergence properties** for custom sequences
4. **Test empirical performance** versus theoretical optimal

### Validation Integration

1. **Validate early and often** in computational pipelines
2. **Provide informative error messages** to users
3. **Handle validation gracefully** in production code
4. **Document validation requirements** for API users

## Performance Considerations

### Computational Complexity

- **Static procedures**: O(n log n) due to sorting
- **Gamma sequences**: O(1) per value computation
- **Validation**: O(1) per check

### Memory Usage

- **Static procedures**: O(n) for input storage
- **Gamma sequences**: O(1) stateless computation
- **Validation**: Minimal memory footprint

### Optimization Tips

1. **Pre-sort p-values** when calling static procedures repeatedly
2. **Cache gamma values** for frequently accessed positions
3. **Batch validation** when checking many values
4. **Use numpy arrays** for vectorized operations when possible

## References

**Static Procedures:**
- Benjamini, Y., and Y. Hochberg (1995). "Controlling the False Discovery Rate"
- Storey, J. D. (2002). "A direct approach to false discovery rates"  
- Benjamini, Y., and D. Yekutieli (2001). "Control under dependency"

**Gamma Sequences:**
- Ramdas, A., et al. (2018). "SAFFRON: adaptive algorithm for online FDR control"
- Javanmard, A., and A. Montanari (2018). "Online rules for FDR control"

**Validation Theory:**
- Wassmer, G., and W. Brannath (2016). "Group Sequential and Confirmatory Adaptive Designs"