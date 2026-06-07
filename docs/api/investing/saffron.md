# SAFFRON: Adaptive Online FDR Control

**SAFFRON** (Serial estimate of the Alpha Fraction that is Futilely Rationed On true Nulls) is an adaptive algorithm for online FDR control that estimates the proportion of true null hypotheses to set more powerful rejection thresholds.

!!! quote "Original Paper"
    **Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan.** "SAFFRON: an adaptive algorithm for online control of the false discovery rate." *Proceedings of the 35th International Conference on Machine Learning (ICML)*, Proceedings of Machine Learning Research, vol. 80, pp. 4286-4294, PMLR, 2018. [[ArXiv]](https://arxiv.org/abs/1802.09098) [[ICML]](https://proceedings.mlr.press/v80/ramdas18a.html)

## Overview

### The Innovation

SAFFRON can be seen as an online analogue of the famous offline Storey-BH adaptive procedure. Just as Storey-BH typically achieves higher power than Benjamini-Hochberg by estimating the proportion of true nulls, SAFFRON typically achieves higher power than non-adaptive online methods like LORD.

### Key Features

1. **Adaptive null proportion estimation** - Uses candidate fraction to estimate alpha-wealth allocated to true nulls
2. **Alpha-wealth dynamics** - Intelligently allocates wealth to different tests over time
3. **Proven FDR control** - Provably controls FDR for independent p-values
4. **Superior power** - Typically more powerful than non-adaptive counterparts

## Algorithm Details

### Core Mechanism

SAFFRON starts with alpha-wealth that it allocates to tests over time, earning back wealth on discoveries. Unlike older alpha-investing methods, SAFFRON's thresholds are based on estimating the alpha fraction allocated to true null hypotheses using the **candidate threshold (`lambda`)**.

### Wealth Dynamics

The algorithm maintains wealth that:
- Starts at initial value `W0`  
- Is spent to purchase rejection thresholds
- Is earned back from discoveries
- Adapts based on estimated proportion of true nulls via candidates

## Class Reference

::: online_fdr.p_values.investing.saffron.saffron.Saffron

## Usage Examples

### Basic Usage

```python
from online_fdr.p_values.investing.saffron.saffron import Saffron

# Create SAFFRON instance with recommended parameters
saffron = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)

# Test individual p-values
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45, 0.006]

print("SAFFRON Online Testing:")
discoveries = []

for i, p_value in enumerate(p_values):
    decision = saffron.test_one(p_value)
    
    if decision:
        discoveries.append(i + 1)
        print(f" Test {i+1}: p={p_value:.3f}  discovery")
    else:
        print(f"  Test {i+1}: p={p_value:.3f}  no rejection")

print(f"\nTotal discoveries: {len(discoveries)}")
print(f"Discovery indices: {discoveries}")
```

### Parameter Selection

```python
# Conservative: Lower lambda for more selective candidate identification
conservative = Saffron(alpha=0.05, wealth=0.01, lambda_=0.25)

# Moderate: Balanced parameters (recommended starting point)  
moderate = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)

# Aggressive: Higher lambda for more candidates
aggressive = Saffron(alpha=0.05, wealth=0.05, lambda_=0.75)

# Test on same data for comparison
test_p_values = [0.001, 0.02, 0.15, 0.03, 0.8, 0.01]

for name, method in [("Conservative", conservative), 
                     ("Moderate", moderate), 
                     ("Aggressive", aggressive)]:
    decisions = [method.test_one(p) for p in test_p_values]
    print(f"{name}: {sum(decisions)} discoveries")
```

### Working with Real Data Patterns

```python
from online_fdr.core.utils.generation import DataGenerator, BetaMixtureModel

# Simulate realistic genomics-style data with conservative nulls
dgp = BetaMixtureModel(alt_alpha=0.3, alt_beta=5.0)  # Alternatives skewed toward 0
generator = DataGenerator(n=200, pi0=0.9, dgp=dgp)   # 90% true nulls

# Create SAFFRON instance
saffron = Saffron(alpha=0.1, wealth=0.05, lambda_=0.5)

print("SAFFRON on Realistic Data:")
print("=" * 35)

true_discoveries = 0
false_discoveries = 0

# Test first 50 hypotheses
for i in range(50):
    p_value, is_alternative = generator.sample_one()
    decision = saffron.test_one(p_value)
    
    if decision:
        if is_alternative:
            true_discoveries += 1
            result = "true discovery"
        else:
            false_discoveries += 1
            result = "false discovery"
        
        truth = "ALT" if is_alternative else "NULL"
        print(f"Test {i+1:2d}: p={p_value:.3f} ({truth})  REJECT ({result})")

total_discoveries = true_discoveries + false_discoveries
empirical_fdr = false_discoveries / max(total_discoveries, 1)

print(f"\nSummary:")
print(f"True discoveries: {true_discoveries}")
print(f"False discoveries: {false_discoveries}")
print(f"Empirical FDR: {empirical_fdr:.3f}")
print(f"Target FDR: {saffron.alpha0}")
```

### Comparison with Non-Adaptive Methods

```python
from online_fdr.p_values.investing.lord.three import LordThree

def compare_adaptive_vs_nonadaptive(p_values):
    """Compare SAFFRON (adaptive) with LORD 3 (non-adaptive)."""
    
    print("Adaptive vs Non-Adaptive Comparison:")
    print("=" * 40)
    
    # Create methods
    saffron = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)
    lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)
    
    # Test both methods
    saffron_decisions = [saffron.test_one(p) for p in p_values]
    lord3_decisions = [lord3.test_one(p) for p in p_values]
    
    saffron_discoveries = sum(saffron_decisions)
    lord3_discoveries = sum(lord3_decisions)
    
    print(f"SAFFRON (adaptive): {saffron_discoveries} discoveries")
    print(f"LORD 3 (non-adaptive): {lord3_discoveries} discoveries")
    print(f"Power advantage: {saffron_discoveries - lord3_discoveries}")
    
    # Show which additional discoveries SAFFRON made
    additional = []
    for i, (s_dec, l_dec) in enumerate(zip(saffron_decisions, lord3_decisions)):
        if s_dec and not l_dec:
            additional.append(f"p={p_values[i]:.3f}")
    
    if additional:
        print(f"Additional SAFFRON discoveries: {additional}")
    
    return saffron_discoveries, lord3_discoveries

# Test with mixed p-value scenario
mixed_p_values = [0.001, 0.25, 0.02, 0.7, 0.005, 0.9, 0.04, 0.3, 0.008, 0.6]
compare_adaptive_vs_nonadaptive(mixed_p_values)
```

## Mathematical Foundation

### Candidate-Based Estimation

SAFFRON estimates the proportion of alpha-wealth allocated to true nulls using:

$$\hat{\pi}_0^{(\text{SAFFRON})}(t) = \frac{\text{Number of non-candidates up to time } t}{\text{Total tests up to time } t}$$

where candidates are p-values <= lambda.

### Threshold Formula

The adaptive rejection threshold at time t is:

$$\alpha_t = \min\left(\lambda, \text{wealth-based threshold} \times (1-\lambda)\right)$$

The wealth-based component adapts based on:
- Initial wealth allocation
- Discoveries and candidate history  
- Gamma sequence for proper spending

### FDR Guarantee

**Theorem (SAFFRON FDR Control)**: Under independence of p-values, SAFFRON controls FDR at level alpha.

## Best Practices

### Parameter Selection Guidelines

!!! tip "Lambda (lambda) Selection"
    - **lambda = 0.25**: Conservative, fewer candidates, more selective
    - **lambda = 0.5**: Moderate, balanced (recommended default)
    - **lambda = 0.75**: Aggressive, more candidates, higher power potential

!!! tip "Wealth (W) Selection"  
    - Start with W = alpha/2 (e.g., 0.025 for alpha = 0.05)
    - Increase for more initial power, decrease for more conservative start
    - Must satisfy `0 < W < alpha`

### When to Use SAFFRON

- **Recommended for**: Independent p-values with unknown pi0
- **Advantages**: Higher power than non-adaptive methods, robust performance
- **Considerations**: Requires tuning the lambda parameter, assumes independence

### Troubleshooting

!!! warning "Common Issues"
    - **Low power**: Try increasing lambda or W
    - **Too aggressive**: Decrease lambda or W  
    - **No early discoveries**: SAFFRON needs some candidates to build momentum

## References

1. **Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan** (2018). "SAFFRON: an adaptive algorithm for online control of the false discovery rate." *Proceedings of the 35th International Conference on Machine Learning (ICML)*, PMLR, 80:4286-4294.

2. **Storey, J. D.** (2002). "A direct approach to false discovery rates." *Journal of the Royal Statistical Society: Series B*, 64(3):479-498.

3. **Foster, D. P., and R. A. Stine** (2008). "Alpha-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society: Series B*, 70(2):429-444.

## See Also

- **[ADDIS](addis.md)**: Handles conservative nulls better than SAFFRON
- **[LORD variants](lord.md)**: Non-adaptive alternatives  
- **[Theory](../../theory/algorithms.md)**: Mathematical foundations of online FDR control
