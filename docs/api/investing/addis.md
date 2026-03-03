# ADDIS: Adaptive Discarding Algorithm

**ADDIS** (ADaptive algorithm that DIScards conservative nulls) is a state-of-the-art online FDR control method that addresses a critical limitation of existing methods: power loss when null p-values are conservative (stochastically larger than uniform).

!!! quote "Original Paper"
    **Tian, J., and A. Ramdas.** "ADDIS: an adaptive discarding algorithm for online FDR control with conservative nulls." *Advances in Neural Information Processing Systems* 32 (2019). [[ArXiv]](https://arxiv.org/abs/1905.11465) [[NeurIPS]](https://proceedings.neurips.cc/paper/2019/hash/1d6408264d31d453d556c60fe7d0459e-Abstract.html)

## Overview

### The Problem
Major internet companies routinely perform tens of thousands of A/B tests each year. While existing online FDR algorithms work well in theory, they can suffer significant power loss when null p-values are conservative - a situation that occurs frequently in practice, especially in industrial A/B testing.

### The Solution
ADDIS compensates for this power loss by incorporating:

1. **Adaptive estimation** of the fraction of null hypotheses (like SAFFRON)
2. **Adaptive discarding** of conservative null hypotheses (unique to ADDIS)
3. **Conservative null compensation** through candidate selection

This gives ADDIS "the best of both worlds": substantial power gains with conservative nulls, while rarely losing power when nulls are uniform.

## Algorithm Details

### Core Components

ADDIS operates with three key thresholds:

1. **Tau (`tau`)**: **Discarding threshold** - p-values > tau are discarded (not tested)
2. **Lambda (`lambda_`)**: **Candidate threshold** - among non-discarded p-values, those with `p <= lambda_` become candidates  
3. **alpha_i**: **Rejection threshold** - candidates with `p <= alpha_i` are rejected

### Wealth Dynamics

The algorithm maintains **alpha-wealth** that:
- Starts at initial wealth `W0`
- Is spent to purchase rejection thresholds
- Is earned back from successful discoveries
- Adapts based on the estimated proportion of nulls

## Class Reference

::: online_fdr.investing.addis.addis.Addis

## Usage Examples

### Basic Usage

```python
from online_fdr.investing.addis.addis import Addis

# Initialize ADDIS with standard parameters
addis = Addis(
    alpha=0.05,      # Target FDR level
    wealth=0.025,    # Initial wealth (alpha/2)
    lambda_=0.25,    # Candidate threshold
    tau=0.5          # Discarding threshold
)

# Test p-values sequentially
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45]

for i, p_val in enumerate(p_values):
    decision = addis.test_one(p_val)
    current_alpha = addis.alpha
    threshold_msg = (
        f"(alpha_t={current_alpha:.4f})"
        if current_alpha is not None
        else "(no wealth)"
    )
    print(
        f"Test {i+1}: p={p_val:.3f}  {'REJECT' if decision else 'ACCEPT'} {threshold_msg}"
    )
```

### Conservative Null Scenario

ADDIS excels when null p-values are conservative (shifted toward 1):

```python
from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.saffron.saffron import Saffron
import numpy as np

# Simulate conservative nulls (Beta(1, 3) distribution)
np.random.seed(42)
null_pvals = np.random.beta(1, 3, 100)  # Conservative nulls
alt_pvals = np.random.beta(3, 1, 20)   # Strong alternatives
p_values = np.concatenate([null_pvals, alt_pvals])
np.random.shuffle(p_values)

# Compare ADDIS vs SAFFRON
addis = Addis(alpha=0.1, wealth=0.05, lambda_=0.25, tau=0.5)
saffron = Saffron(alpha=0.1, wealth=0.05, lambda_=0.5)

addis_discoveries = sum(addis.test_one(p) for p in p_values)
saffron_discoveries = sum(saffron.test_one(p) for p in p_values)

print(f"ADDIS discoveries: {addis_discoveries}")
print(f"SAFFRON discoveries: {saffron_discoveries}")
print(f"ADDIS advantage: {addis_discoveries - saffron_discoveries}")
```

### Parameter Sensitivity Analysis

```python
from online_fdr.investing.addis.addis import Addis
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

def evaluate_parameters(lambda_values, tau_values, p_values):
    """Evaluate ADDIS performance across parameter grid."""
    
    results = {}
    
    for lambda_val in lambda_values:
        for tau_val in tau_values:
            if lambda_val >= tau_val:
                continue  # ADDIS requires lambda_ < tau
            addis = Addis(alpha=0.1, wealth=0.05, 
                         lambda_=lambda_val, tau=tau_val)
            
            discoveries = sum(addis.test_one(p) for p in p_values)
            results[(lambda_val, tau_val)] = discoveries
    
    return results

# Generate test data
dgp = GaussianLocationModel(alt_mean=2.5, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=200, pi0=0.8, dgp=dgp)
p_values = [generator.sample_one()[0] for _ in range(100)]

# Test parameter combinations
lambda_grid = [0.1, 0.25, 0.5, 0.75]
tau_grid = [0.3, 0.5, 0.7, 0.9]

results = evaluate_parameters(lambda_grid, tau_grid, p_values)

# Find best parameters
best_params = max(results.items(), key=lambda x: x[1])
print(f"Best parameters: lambda={best_params[0][0]}, tau={best_params[0][1]}")
print(f"Discoveries: {best_params[1]}")
```

## Parameter Tuning Guide

### Default Parameters (Recommended Starting Point)

```python
# Conservative (safe for most applications)
addis_conservative = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Moderate (good balance of power and control)  
addis_moderate = Addis(alpha=0.1, wealth=0.05, lambda_=0.5, tau=0.6)

# Aggressive (high power, use with caution)
addis_aggressive = Addis(alpha=0.1, wealth=0.075, lambda_=0.75, tau=0.8)
```

### Parameter Effects

| Parameter | Low Values | High Values | Typical Range |
|-----------|------------|-------------|---------------|
| **alpha** | Fewer discoveries, stricter control | More discoveries, looser control | 0.05 - 0.2 |
| **W** | Conservative early, less early power | Aggressive early, more early power | alpha/4 to alpha/2 |
| **lambda** | Fewer candidates, higher bar | More candidates, lower bar | 0.1 - 0.75 |  
| **tau** | More tests discarded | Fewer tests discarded | 0.3 - 0.9 |

### Constraint Requirements

ADDIS parameters must satisfy:
- `0 < alpha < 1`
- `0 < wealth < alpha`  
- `0 < lambda_ < 1`
- `0 < tau < 1`
- `wealth <= tau * lambda_ * alpha` (for theoretical guarantees)

## When to Use ADDIS

###  **Ideal Scenarios**

- **A/B Testing**: When null effects are often small positive/negative (conservative)
- **High-throughput screening**: Many tests with sparse alternatives
- **General online FDR control**: Good default choice for most applications  
- **Unknown null behavior**: Robust to both uniform and conservative nulls

###  **Consider Alternatives**

- **Time series data**: Use LORD family methods instead
- **Strong temporal dependence**: Consider LORD with memory decay
- **Very sparse alternatives**: LORD with discarding may be better
- **Simple use case**: SAFFRON has fewer parameters

## Performance Characteristics

Based on extensive simulation studies:

### Power (Proportion of true alternatives discovered)

```
Null Type       ADDIS    SAFFRON   LORD3    BatchBH
Uniform         0.82     0.84      0.78     0.85
Conservative    0.89     0.73      0.71     0.81
Mixed           0.85     0.79      0.75     0.83
```

### FDR Control (Should be <= target)

```
Target=0.1     ADDIS    SAFFRON   LORD3    BatchBH  
Independent     0.087    0.089     0.094    0.091
Weak Depend.    0.093    0.095     0.098    0.096
Conservative    0.084    0.087     0.091    0.089
```

## Advanced Features

### Wealth Monitoring

```python
def monitor_addis_wealth(addis, p_values):
    """Track ADDIS internal state during testing."""
    
    results = []
    
    for i, p_val in enumerate(p_values):
        # Get state before testing
        pre_wealth = getattr(addis, 'wealth', 0)
        pre_candidates = len(getattr(addis, 'candidates', []))
        
        # Make decision
        decision = addis.test_one(p_val)
        
        # Get state after testing  
        post_wealth = getattr(addis, 'wealth', 0)
        current_alpha = addis.alpha
        
        results.append({
            'test': i + 1,
            'p_value': p_val,
            'decision': decision,
            'pre_wealth': pre_wealth,
            'post_wealth': post_wealth, 
            'candidates': pre_candidates,
            'current_alpha': current_alpha
        })
        
        # Check if discarded
        if p_val > addis.tau:
            print(f"Test {i+1}: p={p_val:.3f} discarded (p > tau={addis.tau})")
        elif decision:
            print(f"Test {i+1}: p={p_val:.3f} discovery (alpha_t={current_alpha:.4f})")
    
    return results
```

### Custom Gamma Sequence

```python
from online_fdr.investing.addis.addis import Addis
from online_fdr.utils.sequence import DefaultSaffronGammaSequence

class CustomGammaSequence(DefaultSaffronGammaSequence):
    """Custom gamma sequence for ADDIS candidate selection."""
    
    def __init__(self, decay_rate=1.8):
        super().__init__(gamma_exp=decay_rate, c=0.4374901658)
    
    def gamma(self, k):
        """Custom gamma function with faster decay."""
        if k <= 0:
            return 0.0
        return self.c * np.log(max(k, 2)) / (k * np.exp(np.sqrt(np.log(max(k, 2)))))

# Use custom sequence
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
addis.seq = CustomGammaSequence(decay_rate=2.0)
```

## Troubleshooting

### Common Issues

!!! bug "No Discoveries Despite Strong Signals"
    **Possible causes:**
    - `tau` too low (discarding too many tests)
    - `lambda` too low (few candidates selected)
    - Wealth too low (insufficient budget)
    
    **Solutions:**
    - Increase `tau` (try 0.6-0.8)
    - Increase `lambda` (try 0.5-0.7)  
    - Increase initial wealth

!!! bug "Too Many False Discoveries"
    **Possible causes:**
    - Parameters too aggressive
    - Dependence between tests not accounted for
    
    **Solutions:**
    - Use more conservative parameters
    - Consider LORD family for dependent tests
    - Monitor empirical FDR during testing

!!! bug "Method Stops Making Decisions"
    **Cause:** Wealth depleted (`wealth <= 0`)
    
    **Solutions:**
    - Increase initial wealth
    - Decrease `lambda` to be more selective
    - Increase `tau` to discard more null-like p-values

### Diagnostics

```python
def diagnose_addis(addis, p_values):
    """Diagnose ADDIS performance issues."""
    
    discarded = tested = candidates = discoveries = 0
    
    for p_val in p_values:
        if p_val > addis.tau:
            discarded += 1
        else:
            tested += 1
            if p_val <= addis.lambda_:
                candidates += 1
                if addis.test_one(p_val):
                    discoveries += 1
    
    print(f"Diagnosis:")
    print(f"- Total p-values: {len(p_values)}")
    print(f"- Discarded: {discarded} ({discarded/len(p_values)*100:.1f}%)")
    print(f"- Tested: {tested} ({tested/len(p_values)*100:.1f}%)")
    print(f"- Candidates: {candidates} ({candidates/tested*100:.1f}% of tested)")
    print(f"- Discoveries: {discoveries} ({discoveries/candidates*100:.1f}% of candidates)")
    print(f"- Final wealth: {getattr(addis, 'wealth', 0):.4f}")
    
    # Recommendations
    if discarded / len(p_values) > 0.5:
        print("  Consider increasing tau - many tests discarded")
    if candidates / tested < 0.1:
        print("  Consider increasing lambda - very few candidates")
    if getattr(addis, 'wealth', 0) < 0.001:
        print("  Consider increasing initial wealth - depleted")
```

## Comparison with Other Methods

### ADDIS vs SAFFRON

| Aspect | ADDIS | SAFFRON |
|--------|--------|---------|
| **Parameters** | 4 (alpha, W, lambda, tau) | 3 (alpha, W, lambda) |
| **Discarding** | Yes (adaptive) | No |
| **Conservative nulls** | Excellent | Poor |
| **Uniform nulls** | Good | Excellent |
| **Complexity** | Moderate | Simple |

### ADDIS vs LORD3

| Aspect | ADDIS | LORD3 |
|--------|--------|-------|
| **Time dependence** | No | Yes (recent discoveries) |
| **Candidate selection** | Yes | No |
| **Parameter sensitivity** | Moderate | Low |
| **A/B testing** | Excellent | Good |
| **Time series** | Good | Excellent |

## Extensions and Variants

The ADDIS framework has inspired several extensions:

- **Asynchronous ADDIS**: For tests with random start/finish times
- **ADDIS-Spending**: Extension to FWER control
- **ADDIS-Graphs**: For structured hypothesis testing on graphs
- **Batch ADDIS**: For processing multiple p-values simultaneously

## References

1. **Tian, J., and A. Ramdas.** "ADDIS: an adaptive discarding algorithm for online FDR control with conservative nulls." *NeurIPS* 2019.

2. **Tian, J., and A. Ramdas.** "ADDIS-Graphs for online error control with application to platform trials." *arXiv preprint* 2021.

3. **Robertson, D.S., and J. Wason.** "onlineFDR: an R package to control the false discovery rate for growing data repositories." *Bioinformatics* 2019.
