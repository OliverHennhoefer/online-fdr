# LOND: Levels based On Number of Discoveries

**LOND** (significance Levels based On Number of Discoveries) is one of the first procedures for online false discovery rate (FDR) control, where significance levels are multiplied by the number of discoveries made so far.

!!! quote "Original Papers"
    **Javanmard, A., and Montanari, A.** "On online control of false discovery rate." arXiv preprint arXiv:1502.06197, 2015.
    
    **Javanmard, A., and A. Montanari.** "Online rules for control of false discovery rate and false discovery exceedance." *Annals of Statistics*, 46(2):526-554, 2018.

## Overview

### Historical Importance

LOND represents one of the first successful attempts to control FDR in the online setting. Javanmard and Montanari (2015) were among the first to tackle the challenge of sequential hypothesis testing with FDR guarantees.

### Algorithm Principle

LOND is conceptually simple: **test levels are multiplied by the number of rejections made thus far**. The more discoveries you make, the higher your future rejection thresholds become, creating a self-reinforcing discovery process.

### Key Limitation

While LOND provably controls FDR, it has a significant drawback: unless many discoveries are made early, the adjusted significance levels quickly approach zero, leading to very low power. This motivated the development of LORD and other alpha-investing procedures.

## Class Reference

::: online_fdr.investing.lond.lond.Lond

## Usage Examples

### Basic Usage

```python
from online_fdr.investing.lond.lond import Lond

# Create LOND instance
lond = Lond(alpha=0.05)

# Test individual p-values
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45, 0.006]

print("LOND Online Testing:")
discoveries = []

for i, p_value in enumerate(p_values):
    decision = lond.test_one(p_value)
    
    if decision:
        discoveries.append(i + 1)
        print(f" Test {i+1}: p={p_value:.3f}  discovery (total: {lond.num_reject})")
    else:
        print(f"  Test {i+1}: p={p_value:.3f}  no rejection (threshold: {lond.alpha:.6f})")

print(f"\nTotal discoveries: {len(discoveries)}")
print(f"Discovery indices: {discoveries}")
```

### Understanding the Discovery Momentum

```python
def demonstrate_discovery_momentum():
    """Show how LOND's power depends on early discoveries."""
    
    # Scenario 1: Early discoveries
    print("Scenario 1: Early Discoveries")
    print("=" * 35)
    
    lond1 = Lond(alpha=0.1)  # Higher alpha for better visibility
    early_discoveries = [0.001, 0.005, 0.02, 0.8, 0.3, 0.04, 0.2]
    
    for i, p_val in enumerate(early_discoveries, 1):
        decision = lond1.test_one(p_val)
        print(f"Test {i}: p={p_val:.3f}  {'REJECT' if decision else 'ACCEPT'} "
              f"(threshold: {lond1.alpha:.6f}, discoveries: {lond1.num_reject})")
    
    print(f"Final discoveries: {lond1.num_reject}\n")
    
    # Scenario 2: No early discoveries  
    print("Scenario 2: No Early Discoveries")
    print("=" * 37)
    
    lond2 = Lond(alpha=0.1)
    no_early = [0.8, 0.9, 0.7, 0.001, 0.005, 0.02, 0.04]  # Same p-values, reordered
    
    for i, p_val in enumerate(no_early, 1):
        decision = lond2.test_one(p_val)
        print(f"Test {i}: p={p_val:.3f}  {'REJECT' if decision else 'ACCEPT'} "
              f"(threshold: {lond2.alpha:.6f}, discoveries: {lond2.num_reject})")
    
    print(f"Final discoveries: {lond2.num_reject}")
    print(f"\nPower difference due to ordering: {lond1.num_reject - lond2.num_reject} discoveries")

demonstrate_discovery_momentum()
```

### Handling Dependent Data

```python
def lond_with_dependence():
    """Compare LOND variants for different dependence assumptions."""
    
    print("LOND Dependence Handling:")
    print("=" * 30)
    
    # Test p-values with some correlation structure
    p_values = [0.01, 0.02, 0.015, 0.8, 0.03, 0.9, 0.025, 0.7]
    
    # Independent version
    lond_indep = Lond(alpha=0.05, dependent=False)
    indep_decisions = [lond_indep.test_one(p) for p in p_values]
    
    # Dependent version (with harmonic correction)
    lond_dep = Lond(alpha=0.05, dependent=True)
    dep_decisions = [lond_dep.test_one(p) for p in p_values]
    
    print("Results:")
    print(f"Independent assumption: {sum(indep_decisions)} discoveries")
    print(f"Dependent correction: {sum(dep_decisions)} discoveries")
    print(f"Dependent version is more conservative as expected")
    
    # Show threshold differences
    print(f"\nFinal thresholds:")
    print(f"Independent: {lond_indep.alpha:.6f}")  
    print(f"Dependent: {lond_dep.alpha:.6f}")

lond_with_dependence()
```

### Original vs Modified Formulation

```python
def compare_lond_variants():
    """Compare original and modified LOND formulations."""
    
    print("LOND Formulation Comparison:")
    print("=" * 32)
    
    p_values = [0.002, 0.8, 0.01, 0.9, 0.005, 0.7, 0.015]
    
    # Original: uses (num_reject + 1) in threshold
    lond_orig = Lond(alpha=0.05, original=True)
    
    # Modified: uses max(num_reject, 1) in threshold
    lond_mod = Lond(alpha=0.05, original=False)
    
    print("Test | P-value | Original | Modified")
    print("-" * 35)
    
    for i, p_val in enumerate(p_values, 1):
        orig_decision = lond_orig.test_one(p_val)
        mod_decision = lond_mod.test_one(p_val)
        
        print(f"{i:4d} | {p_val:7.3f} | {'REJECT' if orig_decision else 'ACCEPT':>8} | "
              f"{'REJECT' if mod_decision else 'ACCEPT':>8}")
    
    print(f"\nOriginal formulation: {lond_orig.num_reject} discoveries")
    print(f"Modified formulation: {lond_mod.num_reject} discoveries")

compare_lond_variants()
```

### Performance Evaluation

```python
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

def evaluate_lond_performance():
    """Evaluate LOND on simulated data."""
    
    print("LOND Performance Evaluation:")
    print("=" * 32)
    
    # Generate realistic test scenario
    dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)
    generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)  # 90% nulls
    
    # Create LOND instance
    lond = Lond(alpha=0.05)
    
    # Simulate testing
    true_positives = 0
    false_positives = 0
    total_tests = 50
    
    print(f"Testing {total_tests} hypotheses (10% alternatives expected):")
    print()
    
    for i in range(total_tests):
        p_value, is_alternative = generator.sample_one()
        decision = lond.test_one(p_value)
        
        if decision:
            if is_alternative:
                true_positives += 1
                result = "true discovery"
            else:
                false_positives += 1
                result = "false discovery"
            
            truth = "ALT" if is_alternative else "NULL"
            print(f"Test {i+1:2d}: p={p_value:.3f} ({truth})  REJECT ({result})")
    
    # Calculate metrics
    total_discoveries = true_positives + false_positives
    empirical_fdr = false_positives / max(total_discoveries, 1)
    
    print(f"\nPerformance Summary:")
    print(f"Total discoveries: {total_discoveries}")
    print(f"True positives: {true_positives}")
    print(f"False positives: {false_positives}")
    print(f"Empirical FDR: {empirical_fdr:.3f}")
    print(f"Target FDR: {lond.alpha0}")
    print(f"FDR controlled: {'yes' if empirical_fdr <= lond.alpha0 else 'no'}")

evaluate_lond_performance()
```

## Mathematical Foundation

### Threshold Formula

For test t, LOND sets the rejection threshold as:

$$\alpha_t = \gamma_t \cdot \begin{cases}
R_t + 1 & \text{(original formulation)} \\
\max(R_t, 1) & \text{(modified formulation)}
\end{cases}$$

where:
- gamma_t is from a gamma sequence with sum_t gamma_t <= 1
- R_t is the number of rejections up to time t

### Dependence Correction

For arbitrarily dependent p-values, LOND applies the correction:

$$\alpha_t^{\text{dep}} = \frac{\alpha_t}{\sum_{i=1}^t \frac{1}{i}} = \frac{\alpha_t}{H_t}$$

where H_t is the t-th harmonic number.

### FDR Guarantee

**Theorem (LOND FDR Control)**: 
- For independent p-values: LOND controls FDR at level alpha
- For positively dependent (PRDS) p-values: LOND controls FDR at level alpha
- For arbitrary dependence: LOND with harmonic correction controls FDR at level alpha

## Comparison with Other Methods

### LOND vs LORD vs SAFFRON

| Method | Adaptation | Power | Complexity | FDR Control |
|--------|------------|--------|------------|-------------|
| **LOND** | None | Low (without early discoveries) | Simple |  |
| **LORD** | Timing-based | Medium | Moderate |  |
| **SAFFRON** | Null proportion | High | Moderate |  |

### When to Use LOND

!!! info "Appropriate Use Cases"
    - **Historical studies**: Understanding the evolution of online FDR methods
    - **Educational purposes**: Learning basic online testing concepts
    - **Baseline comparisons**: Simple benchmark for other methods
    - **Very sparse alternatives**: When few discoveries are expected

!!! warning "Not Recommended For"
    - **Practical applications**: Better methods are available (SAFFRON, ADDIS)
    - **Unknown discovery patterns**: Non-adaptive nature is limiting
    - **High-power requirements**: Performance degrades without early discoveries

## Best Practices

### Parameter Selection

!!! tip "Alpha Selection"
    - Use standard values (0.05, 0.1) for comparability
    - Higher  may be needed to see any discoveries with LOND

!!! tip "Dependence Setting"
    - `dependent=False`: For independent or positively dependent tests
    - `dependent=True`: Conservative choice for unknown dependence
    - The harmonic correction is quite conservative

### Improving LOND Performance

1. **Ensure early discoveries**: LOND works best when early tests are promising
2. **Consider pre-filtering**: Remove obviously null hypotheses
3. **Use as baseline**: Compare against more powerful methods
4. **Understand limitations**: Expect lower power than adaptive methods

## References

1. **Javanmard, A., and Montanari, A.** (2015). "On online control of false discovery rate." arXiv preprint arXiv:1502.06197.

2. **Javanmard, A., and A. Montanari** (2018). "Online rules for control of false discovery rate and false discovery exceedance." *Annals of Statistics*, 46(2):526-554.

3. **Benjamini, Y., and Y. Hochberg** (1995). "Controlling the false discovery rate: A practical and powerful approach to multiple testing." *Journal of the Royal Statistical Society: Series B*, 57(1):289-300.

## See Also

- **[LORD](lord.md)**: Improved successor to LOND
- **[SAFFRON](saffron.md)**: Adaptive online FDR control
- **[ADDIS](addis.md)**: Handles conservative nulls
- **[Theory](../../theory/algorithms.md)**: Mathematical foundations of online FDR
