# GAI: Generalized Alpha-Investing

**GAI** (Generalized Alpha-Investing) extends the original alpha-investing procedure of Foster and Stine (2008) for sequential control of expected false discoveries, using SAFFRON-style update rules for improved power.

!!! quote "Original Papers"
    **Foster, D., and R. Stine.** "Alpha-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society (Series B)*, 70(2):429-444, 2008.
    
    **Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan.** "SAFFRON: an adaptive algorithm for online control of the FDR." *Proceedings of the 35th International Conference on Machine Learning (ICML)*, 2018.

## Overview

### The Alpha-Investing Revolution

Alpha-investing introduced a paradigm shift in sequential hypothesis testing: instead of fixed significance levels, the procedure **earns back probability** when discoveries are made. This creates a dynamic system where successful discoveries enable more powerful future testing.

### Key Innovation

The fundamental insight is that when you reject a null hypothesis, you gain evidence that not all hypotheses are null, justifying spending more alpha-wealth on future tests. This creates a **virtuous cycle** where discoveries beget more discoveries.

### GAI Enhancement

This implementation combines the original alpha-investing philosophy with SAFFRON's gamma sequence and update rules, providing a more principled approach to wealth allocation while maintaining the core alpha-investing benefits.

## Class Reference

::: online_fdr.p_values.Gai

## Usage Examples

### Basic Alpha-Investing

```python
from online_fdr.p_values import Gai

# Create GAI instance
gai = Gai(alpha=0.05, wealth=0.025)

# Test individual p-values
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45, 0.006]

print("Generalized Alpha-Investing:")
discoveries = []

for i, p_value in enumerate(p_values):
    decision = gai.test_one(p_value)
    
    if decision:
        discoveries.append(i + 1)
        print(f" Test {i+1}: p={p_value:.3f}  discovery")
    else:
        print(f"  Test {i+1}: p={p_value:.3f}  no rejection")

print(f"\nTotal discoveries: {len(discoveries)}")
print(f"Discovery indices: {discoveries}")
```

### Understanding Wealth Dynamics

```python
def demonstrate_gai_mechanism():
    """Show how GAI differs from fixed-level testing."""
    
    print("GAI vs Fixed-Level Testing:")
    print("=" * 35)
    
    test_sequence = [0.001, 0.8, 0.02, 0.9, 0.005, 0.7, 0.015]
    
    # GAI with dynamic thresholds
    gai = Gai(alpha=0.1, wealth=0.05)  # Higher values for visibility
    
    print("GAI (Dynamic Thresholds):")
    gai_discoveries = 0
    
    for i, p_val in enumerate(test_sequence, 1):
        detail = gai.test_one_detail(p_val)
        threshold = detail.rejection_threshold or 0.0
        decision = detail.rejected
        
        if decision:
            gai_discoveries += 1
            
        print(f"Test {i}: p={p_val:.3f}, threshold={threshold:.6f}  {'REJECT' if decision else 'ACCEPT'}")
    
    # Fixed-level testing for comparison
    print(f"\nFixed-Level (alpha=0.05):")
    fixed_discoveries = 0
    
    for i, p_val in enumerate(test_sequence, 1):
        decision = p_val <= 0.05
        if decision:
            fixed_discoveries += 1
        print(f"Test {i}: p={p_val:.3f}, threshold=0.050000  {'REJECT' if decision else 'ACCEPT'}")
    
    print(f"\nComparison:")
    print(f"GAI discoveries: {gai_discoveries}")
    print(f"Fixed-level discoveries: {fixed_discoveries}")
    print(f"Power advantage: {gai_discoveries - fixed_discoveries}")

demonstrate_gai_mechanism()
```

### Incorporating Prior Knowledge

```python
def gai_with_prior_knowledge():
    """Demonstrate how GAI can incorporate domain knowledge."""
    
    print("GAI with Prior Knowledge:")
    print("=" * 30)
    
    # Simulate a scenario where you expect more promising tests later
    # (e.g., genomics where genes are ordered by biological relevance)
    
    # Early tests: mostly null
    early_tests = [0.8, 0.7, 0.9, 0.6, 0.75]
    
    # Later tests: mix of null and alternative  
    later_tests = [0.001, 0.02, 0.8, 0.005, 0.03, 0.9, 0.007]
    
    # Conservative start to preserve wealth for later promising tests
    gai = Gai(alpha=0.05, wealth=0.01)  # Lower initial wealth
    
    print("Early phase (expected mostly nulls):")
    early_discoveries = 0
    
    for i, p_val in enumerate(early_tests, 1):
        decision = gai.test_one(p_val)
        if decision:
            early_discoveries += 1
            print(f" Test {i}: p={p_val:.3f}  discovery")
        else:
            print(f"  Test {i}: p={p_val:.3f}  no rejection (conservative)")
    
    print(f"\nTransition to promising region...")
    print("Later phase (expected more alternatives):")
    
    later_discoveries = 0
    for i, p_val in enumerate(later_tests, len(early_tests) + 1):
        decision = gai.test_one(p_val)
        if decision:
            later_discoveries += 1
            print(f" Test {i}: p={p_val:.3f}  discovery")
        else:
            print(f"  Test {i}: p={p_val:.3f}  no rejection")
    
    print(f"\nResults:")
    print(f"Early discoveries: {early_discoveries}")
    print(f"Later discoveries: {later_discoveries}")
    print(f"Total discoveries: {early_discoveries + later_discoveries}")
    print("GAI preserved wealth for the promising region!")

gai_with_prior_knowledge()
```

### Comparison with Other Alpha-Investing Methods

```python
from online_fdr.p_values import Saffron
from online_fdr.p_values import LordThree

def compare_alpha_investing_family():
    """Compare different alpha-investing approaches."""
    
    print("Alpha-Investing Family Comparison:")
    print("=" * 40)
    
    # Test sequence with varied difficulty
    p_values = [0.002, 0.8, 0.01, 0.9, 0.005, 0.7, 0.03, 0.6, 0.008]
    
    # Different alpha-investing approaches
    methods = {
        'GAI': Gai(alpha=0.05, wealth=0.025),
        'SAFFRON': Saffron(alpha=0.05, wealth=0.025, lambda_=0.5),
        'LORD 3': LordThree(alpha=0.05, wealth=0.025, reward=0.025)
    }
    
    results = {}
    
    for method_name, method in methods.items():
        decisions = [method.test_one(p) for p in p_values]
        discoveries = sum(decisions)
        discovery_indices = [i+1 for i, d in enumerate(decisions) if d]
        
        results[method_name] = {
            'discoveries': discoveries,
            'indices': discovery_indices
        }
        
        print(f"{method_name:>8}: {discoveries} discoveries at positions {discovery_indices}")
    
    return results

compare_alpha_investing_family()
```

### Simulating Industrial A/B Testing

```python
from online_fdr.core.utils import DataGenerator, GaussianLocationModel

def simulate_ab_testing_with_gai():
    """Simulate GAI in an industrial A/B testing environment."""
    
    print("Industrial A/B Testing with GAI:")
    print("=" * 36)
    
    # Simulate A/B testing scenario:
    # - Many tests run simultaneously
    # - Most are null (no real effect)
    # - Some have real but small effects
    # - Occasional large effects
    
    dgp = GaussianLocationModel(alt_mean=1.5, alt_std=1.0, one_sided=True)
    generator = DataGenerator(n=200, pi0=0.95, dgp=dgp)  # 95% nulls (realistic)
    
    gai = Gai(alpha=0.05, wealth=0.025)
    
    true_positives = 0
    false_positives = 0
    test_count = 0
    
    print("Running A/B tests sequentially...")
    
    # Simulate first 100 tests
    for i in range(100):
        p_value, is_alternative = generator.sample_one()
        decision = gai.test_one(p_value)
        test_count += 1
        
        if decision:
            if is_alternative:
                true_positives += 1
                result_type = "true effect"
            else:
                false_positives += 1
                result_type = "false alarm"
                
            # Show significant results
            effect_type = "REAL" if is_alternative else "NULL"
            print(f"Test {i+1:3d}: p={p_value:.4f} ({effect_type})  significant ({result_type})")
    
    # Calculate business metrics
    total_discoveries = true_positives + false_positives
    empirical_fdr = false_positives / max(total_discoveries, 1)
    power = true_positives / max(sum(generator.sample_one()[1] for _ in range(100)), 1)  # Approximate
    
    print(f"\nA/B Testing Campaign Results:")
    print(f"Total tests run: {test_count}")
    print(f"Significant effects found: {total_discoveries}")
    print(f"True discoveries (real effects): {true_positives}")
    print(f"False alarms: {false_positives}")
    print(f"False Discovery Rate: {empirical_fdr:.3f}")
    print(f"Target FDR: {gai.alpha0}")
    print(f"FDR controlled: {'yes' if empirical_fdr <= gai.alpha0 else 'no'}")
    
    # Business interpretation
    print(f"\nBusiness Impact:")
    if true_positives > 0:
        print(f"Found {true_positives} real improvements to implement")
    if false_positives > 0:
        print(f"{false_positives} false alarms avoided implementing bad changes")
    
    efficiency = true_positives / max(total_discoveries, 1)
    print(f"Discovery efficiency: {efficiency:.1%}")

simulate_ab_testing_with_gai()
```

## Mathematical Foundation

### Core Alpha-Investing Principle

The fundamental equation of alpha-investing is the **wealth update rule**:

$$W_{t+1} = W_t - \alpha_t + \text{payout} \cdot \mathbf{1}_{\text{discovery at } t}$$

where the payout compensates for the discovery, enabling future testing.

### GAI Threshold Formula

GAI uses SAFFRON-style gamma sequences to set thresholds:

$$\alpha_t = \text{wealth-based allocation} \times \gamma_t$$

The wealth allocation adapts based on candidate history and discovery patterns.

### Theoretical Guarantees

**Theorem (Alpha-Investing FDR Control)**: Under independence, GAI controls the False Discovery Rate (FDR) at level alpha.

The proof relies on the **martingale property** of the wealth process under the null hypothesis.

## Historical Context and Evolution

### Original Alpha-Investing (Foster & Stine, 2008)

- Introduced the wealth-based paradigm
- Controlled mFDR (marginal FDR) rather than FDR
- Simple payout rules

### Generalized Alpha-Investing

- Extended to various payout schemes
- Incorporated prior weights and penalties
- Better theoretical understanding

### Modern Variants (GAI)

- SAFFRON-style update rules
- Improved power characteristics  
- Maintains original philosophy with better performance

## Best Practices

### Parameter Selection

!!! tip "Wealth Selection Guidelines"
    - **Conservative**: W = alpha/4 (preserves wealth for later)
    - **Moderate**: W = alpha/2 (balanced approach)
    - **Aggressive**: W = 3*alpha/4 (spends wealth early)

!!! tip "Domain Knowledge Integration"
    - Start conservatively if expecting null-heavy early tests
    - Higher initial wealth if early alternatives are expected
    - Consider test ordering when possible

### When to Use GAI

!!! success "Good Use Cases"
    - **Industrial A/B testing**: Many tests, mostly null, need efficiency
    - **Sequential screening**: Tests arrive over time, immediate decisions needed
    - **Prior knowledge**: Can order tests by expected promise
    - **Computational constraints**: Simpler than adaptive methods

!!! warning "Consider Alternatives"
    - **Unknown pi0**: SAFFRON adapts better to null proportion
    - **Conservative nulls**: ADDIS handles better
    - **Batch setting**: Standard BH procedures are optimal

### Common Pitfalls

1. **Over-aggressive early spending**: Leaves no wealth for later discoveries
2. **Under-conservative start**: Misses early opportunities  
3. **Ignoring test ordering**: Random order wastes the alpha-investing advantage
4. **Wrong wealth initialization**: Mismatch with discovery expectations

## References

1. **Foster, D. P., and R. A. Stine** (2008). "Alpha-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society: Series B*, 70(2):429-444.

2. **Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan** (2018). "SAFFRON: an adaptive algorithm for online control of the FDR." *Proceedings of the 35th International Conference on Machine Learning (ICML)*, PMLR, 80:4286-4294.

3. **Aharoni, E., and D. Rosset** (2014). "Generalized alpha-investing: definitions, optimality results and application to public databases." *Journal of the Royal Statistical Society: Series B*, 76(4):771-794.

4. **Li, L., and J. G. Canner** (2007). "Modified alpha-investing: a procedure for multiple testing with prior knowledge." *Computational Statistics & Data Analysis*, 51(7):3598-3607.

## See Also

- **[SAFFRON](saffron.md)**: Modern adaptive alternative to alpha-investing
- **[LORD](lord.md)**: Timing-based alpha-investing variant
- **[ADDIS](addis.md)**: Handles conservative nulls with alpha-investing principles
- **[Theory](../../theory/algorithms.md)**: Mathematical foundations of alpha-investing
