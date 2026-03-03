# LORD: Levels based On Recent Discovery

**LORD** (significance Levels based On Recent Discovery) is a family of procedures for online FDR control that use alpha-investing principles, where test levels depend on the timing and wealth from previous discoveries.

!!! quote "Original Paper"
    **Javanmard, A., and A. Montanari.** "Online rules for control of false discovery rate and false discovery exceedance." *Annals of Statistics*, 46(2):526-554, 2018. [[Project Euclid]](https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.full)

## Overview

### The Alpha-Investing Philosophy

LORD procedures have an intuitive interpretation: they start with an **error budget** (alpha-wealth), pay a price each time a hypothesis is tested, and earn back wealth when discoveries are made. The adjusted significance thresholds depend on:

1. **Alpha-wealth dynamics** - Spending and earning back wealth
2. **Discovery timing** - When previous discoveries were made  
3. **Gamma sequences** - Proper spending schedules for FDR control

### Key Innovation

Unlike LOND which depends only on the number of discoveries, LORD takes advantage of the **timing** of discoveries. This allows for higher power by allocating more wealth when discoveries are recent.

## Available LORD Variants

The package implements **LORD 3**, which depends on the past only through the time of the last discovery and the wealth at that time.

!!! note "Historical Context"
    LORD 3 was superseded by LORD++ in later work, but remains implemented for comparison studies and educational purposes. For practical applications, consider more recent methods like SAFFRON or ADDIS.

## Class Reference

### LORD3

::: online_fdr.investing.lord.three.LordThree

### LORD++

::: online_fdr.investing.lord.plus_plus.LordPlusPlus

### LORD Dependent

::: online_fdr.investing.lord.dependent.LordDependent

### LORD Discard

::: online_fdr.investing.lord.discard.LordDiscard

### LORD Memory Decay

::: online_fdr.investing.lord.mem_decay.LORDMemoryDecay

## Usage Examples

### Basic Usage

```python
from online_fdr.investing.lord.three import LordThree

# Create LORD 3 instance with recommended parameters
lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)

# Test individual p-values
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45, 0.006]

print("LORD 3 Online Testing:")
discoveries = []

for i, p_value in enumerate(p_values):
    decision = lord3.test_one(p_value)
    
    if decision:
        discoveries.append(i + 1)
        print(f" Test {i+1}: p={p_value:.3f}  discovery (wealth: {lord3.wealth:.4f})")
    else:
        print(f"  Test {i+1}: p={p_value:.3f}  no rejection (wealth: {lord3.wealth:.4f})")

print(f"\nTotal discoveries: {len(discoveries)}")
print(f"Final wealth: {lord3.wealth:.4f}")
```

### Understanding Wealth Dynamics

```python
def demonstrate_wealth_dynamics():
    """Show how LORD 3 manages alpha-wealth over time."""
    
    lord3 = LordThree(alpha=0.1, wealth=0.05, reward=0.05)
    
    print("LORD 3 Wealth Dynamics:")
    print("=" * 30)
    print(f"Initial wealth: {lord3.wealth:.4f}")
    
    test_scenarios = [
        (0.001, "Very small p-value"),
        (0.8, "Large p-value"),  
        (0.02, "Small p-value after discovery"),
        (0.5, "Medium p-value"),
        (0.005, "Another small p-value")
    ]
    
    for i, (p_value, description) in enumerate(test_scenarios, 1):
        wealth_before = lord3.wealth
        decision = lord3.test_one(p_value)
        wealth_after = lord3.wealth
        
        status = "REJECT" if decision else "ACCEPT"
        wealth_change = wealth_after - wealth_before
        
        print(f"Test {i}: p={p_value:.3f} ({description})")
        print(f"  Decision: {status}")
        print(f"  Wealth: {wealth_before:.4f}  {wealth_after:.4f} (change: {wealth_change:+.4f})")
        print()

demonstrate_wealth_dynamics()
```

### Parameter Selection and Tuning

```python
def compare_lord_parameters():
    """Compare LORD 3 performance with different parameters."""
    
    # Test different parameter combinations
    configs = [
        {"name": "Conservative", "wealth": 0.01, "reward": 0.04},
        {"name": "Moderate", "wealth": 0.025, "reward": 0.025},  
        {"name": "Aggressive", "wealth": 0.04, "reward": 0.01},
    ]
    
    test_p_values = [0.001, 0.02, 0.15, 0.003, 0.8, 0.01, 0.4, 0.005]
    
    print("LORD 3 Parameter Comparison:")
    print("=" * 40)
    
    for config in configs:
        lord3 = LordThree(alpha=0.05, 
                         wealth=config["wealth"], 
                         reward=config["reward"])
        
        decisions = [lord3.test_one(p) for p in test_p_values]
        discoveries = sum(decisions)
        
        print(f"{config['name']:>12} (W={config['wealth']:.3f}, R={config['reward']:.3f}): "
              f"{discoveries} discoveries")

compare_lord_parameters()
```

### Comparison with Other Methods

```python
from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.saffron.saffron import Saffron

def compare_online_methods(p_values):
    """Compare LORD 3 with adaptive methods."""
    
    print("Online FDR Method Comparison:")
    print("=" * 35)
    
    # Create method instances
    methods = {
        'LORD 3': LordThree(alpha=0.05, wealth=0.025, reward=0.025),
        'SAFFRON': Saffron(alpha=0.05, wealth=0.025, lambda_=0.5),
        'ADDIS': Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    }
    
    results = {}
    
    for method_name, method in methods.items():
        decisions = [method.test_one(p) for p in p_values]
        discoveries = sum(decisions)
        discovery_indices = [i+1 for i, d in enumerate(decisions) if d]
        
        results[method_name] = {
            'decisions': decisions,
            'discoveries': discoveries,
            'indices': discovery_indices
        }
        
        print(f"{method_name:>8}: {discoveries} discoveries at positions {discovery_indices}")
    
    return results

# Test with a realistic p-value sequence
realistic_p_values = [0.001, 0.25, 0.02, 0.7, 0.005, 0.9, 0.04, 0.3, 0.008, 0.6]
results = compare_online_methods(realistic_p_values)
```

### Working with Dependent Data

```python
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel
import numpy as np

def lord_with_correlation():
    """Test LORD 3 with correlated data."""
    
    print("LORD 3 with Correlated Test Statistics:")
    print("=" * 42)
    
    # Generate correlated test statistics (AR(1) process)
    n_tests = 100
    rho = 0.3  # Correlation parameter
    
    # Start with independent standard normals
    z = np.random.normal(0, 1, n_tests)
    
    # Apply AR(1) structure: z_t = rho * z_{t-1} + sqrt(1-rho^2) * epsilon_t
    for t in range(1, n_tests):
        z[t] = rho * z[t-1] + np.sqrt(1 - rho**2) * z[t]
    
    # Add signal to first 20% of tests
    n_alternatives = int(0.2 * n_tests)
    z[:n_alternatives] += 2.0  # Add signal
    
    # Convert to p-values (two-sided)
    from scipy.stats import norm
    p_values = 2 * (1 - norm.cdf(np.abs(z)))
    true_alternatives = np.zeros(n_tests, dtype=bool)
    true_alternatives[:n_alternatives] = True
    
    # Apply LORD 3
    lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)
    
    decisions = [lord3.test_one(p) for p in p_values]
    
    # Evaluate performance
    true_positives = sum(d and t for d, t in zip(decisions, true_alternatives))
    false_positives = sum(d and not t for d, t in zip(decisions, true_alternatives))
    total_discoveries = true_positives + false_positives
    
    empirical_fdr = false_positives / max(total_discoveries, 1)
    power = true_positives / n_alternatives
    
    print(f"Correlation (rho): {rho}")
    print(f"True alternatives: {n_alternatives}")
    print(f"Total discoveries: {total_discoveries}")
    print(f"True positives: {true_positives}")
    print(f"False positives: {false_positives}")
    print(f"Empirical FDR: {empirical_fdr:.3f}")
    print(f"Power: {power:.3f}")
    
    return empirical_fdr, power

# Run correlation test
fdr, power = lord_with_correlation()
```

## Mathematical Foundation

### Wealth Dynamics

LORD 3 maintains wealth W_t that evolves as:

$$W_{t+1} = W_t - \alpha_t + R \cdot \mathbf{1}_{\text{reject at time } t}$$

where:
- alpha_t is the rejection threshold at time t
- R is the fixed reward earned per discovery
- W0 is the initial wealth

### Threshold Formula

The rejection threshold at time t is:

$$\alpha_t = \gamma(t - \tau_{\text{last}}) \cdot W_{\tau_{\text{last}}}$$

where:
- tau_last is the time of the last discovery (0 if no discoveries)
- W_{tau_last} is the wealth at the time of the last discovery
- gamma(.) is a gamma sequence (typically declining)

### FDR Guarantee

**Theorem (LORD FDR Control)**: For independent p-values, LORD procedures control FDR at level alpha.

## Best Practices

### Parameter Selection Guidelines

!!! tip "Wealth vs Reward Trade-off"
    - **High initial wealth, low reward**: Strong early power, slower wealth recovery
    - **Low initial wealth, high reward**: Conservative start, builds momentum with discoveries  
    - **Balanced**: W = R = alpha/2 is often a good starting point

!!! tip "Practical Recommendations"
    - For alpha = 0.05: Start with W = 0.025, R = 0.025
    - Adjust based on expected discovery pattern
    - Higher W for expected early discoveries
    - Higher R for sparse discovery scenarios

### When to Use LORD 3

- **Good for**: Educational purposes, method comparisons, historical studies
- **Consider alternatives**: SAFFRON (adaptive), ADDIS (conservative nulls), LORD++ (improved version)
- **Strengths**: Simple, interpretable, proven FDR control
- **Limitations**: Non-adaptive, superseded by newer methods

### Common Issues

!!! warning "Potential Problems"
    - **Wealth depletion**: Too aggressive parameters can exhaust wealth quickly
    - **Poor parameter choice**: Mismatched W and R can hurt performance
    - **Non-adaptive**: Doesn't adapt to unknown proportion of nulls

## References

1. **Javanmard, A., and A. Montanari** (2018). "Online rules for control of false discovery rate and false discovery exceedance." *Annals of Statistics*, 46(2):526-554.

2. **Foster, D. P., and R. A. Stine** (2008). "Alpha-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society: Series B*, 70(2):429-444.

3. **Ramdas, A., F. Ruf, M. Reeb, and A. Ramdas** (2017). "A unified treatment of multiple testing with prior knowledge using the p-filter." *Annals of Statistics*, 47(5):2790-2821.

## See Also

- **[LOND](lond.md)**: Simpler predecessor to LORD
- **[SAFFRON](saffron.md)**: Adaptive online FDR control  
- **[ADDIS](addis.md)**: Handles conservative nulls
- **[Theory](../../theory/algorithms.md)**: Mathematical foundations
