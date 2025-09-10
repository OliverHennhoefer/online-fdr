# Batch Testing Methods

Batch testing methods process all p-values simultaneously, applying multiple testing correction after collecting the complete set of hypotheses. These methods are optimal when all data is available upfront and provide the highest statistical power for a given FDR level.

## Overview

Batch methods differ from sequential methods in their **information advantage**:

!!! success "Batch Methods"
    - See all p-values before making decisions
    - Can sort and optimize rejection thresholds
    - Achieve optimal power for given FDR level
    - Best for post-hoc analysis

!!! warning "Sequential Methods"  
    - Must decide immediately on each p-value
    - Cannot use future information
    - Slightly lower power but work in real-time
    - Best for streaming applications

## Mathematical Foundation

The **False Discovery Rate (FDR)** is defined as:

$$\text{FDR} = \mathbb{E}\left[\frac{V}{R \vee 1}\right]$$

where:
- $V$ = number of false discoveries (Type I errors)
- $R$ = total number of discoveries
- $R \vee 1 = \max(R, 1)$ to avoid division by zero

Batch methods aim to control $\text{FDR} \leq \alpha$ while maximizing power.

## Available Methods

### Benjamini-Hochberg (BH) Procedure
**The gold standard for FDR control under independence**

```python
from online_fdr.batching.bh import BatchBH

# Create Benjamini-Hochberg instance
bh = BatchBH(alpha=0.05)

# Test a batch of p-values
p_values = [0.001, 0.02, 0.15, 0.03, 0.8, 0.005, 0.4]
decisions = bh.test_batch(p_values)

# Show results
for i, (p_val, decision) in enumerate(zip(p_values, decisions)):
    print(f"Test {i+1}: p={p_val:.3f} → {'REJECT' if decision else 'ACCEPT'}")

print(f"Total discoveries: {sum(decisions)}")
```

#### Mathematical Algorithm

The BH procedure works by:

1. **Sort p-values**: $p_{(1)} \leq p_{(2)} \leq \ldots \leq p_{(m)}$
2. **Find threshold**: $k = \max\{i : p_{(i)} \leq \frac{i \alpha}{m}\}$  
3. **Reject hypotheses**: $H_{(1)}, \ldots, H_{(k)}$

```python
# Demonstrate the BH algorithm step-by-step
import numpy as np

def demonstrate_bh_algorithm(p_values, alpha=0.05):
    """Show step-by-step Benjamini-Hochberg procedure."""
    
    m = len(p_values)
    
    # Step 1: Sort p-values and keep track of original indices
    sorted_indices = np.argsort(p_values)
    sorted_p_values = np.array(p_values)[sorted_indices]
    
    print("Step 1: Sorted p-values")
    for i, (idx, p_val) in enumerate(zip(sorted_indices, sorted_p_values)):
        print(f"  Rank {i+1}: p_{{{idx+1}}} = {p_val:.4f}")
    
    # Step 2: Calculate BH thresholds
    print(f"\nStep 2: BH thresholds (α={alpha})")
    bh_thresholds = [(i+1) * alpha / m for i in range(m)]
    
    significant_up_to = -1
    for i, (p_val, threshold) in enumerate(zip(sorted_p_values, bh_thresholds)):
        is_significant = p_val <= threshold
        print(f"  Rank {i+1}: p={p_val:.4f} vs {threshold:.4f} → {'✓' if is_significant else '✗'}")
        
        if is_significant:
            significant_up_to = i
    
    # Step 3: Determine rejections
    print(f"\nStep 3: Rejections")
    if significant_up_to >= 0:
        print(f"Reject first {significant_up_to + 1} sorted hypotheses")
        rejected_indices = sorted_indices[:significant_up_to + 1]
        print(f"Original indices rejected: {sorted(rejected_indices + 1)}")
    else:
        print("No rejections")
        rejected_indices = []
    
    return rejected_indices

# Example usage
p_vals = [0.001, 0.02, 0.15, 0.03, 0.8, 0.005]
demonstrate_bh_algorithm(p_vals, alpha=0.1)
```

### Storey's Adaptive Benjamini-Hochberg
**Adaptive FDR control when null proportion is unknown**

The Storey procedure estimates the proportion of true null hypotheses ($\hat{\pi}_0$) and uses this for more powerful FDR control.

```python
from online_fdr.batching.storey_bh import BatchStoreyBH

# Create Storey-BH instance
storey_bh = BatchStoreyBH(
    alpha=0.05,      # Target FDR level
    lambda_=0.5      # Threshold for π₀ estimation
)

# Compare with regular BH
regular_bh = BatchBH(alpha=0.05)

# Test both methods
p_values = [0.001, 0.02, 0.15, 0.03, 0.8, 0.005, 0.4, 0.9, 0.7, 0.6]

storey_decisions = storey_bh.test_batch(p_values)
regular_decisions = regular_bh.test_batch(p_values)

print("Storey-BH vs Regular BH:")
print(f"Storey-BH discoveries: {sum(storey_decisions)}")  
print(f"Regular BH discoveries: {sum(regular_decisions)}")
print(f"Storey advantage: {sum(storey_decisions) - sum(regular_decisions)} more discoveries")
```

#### Mathematical Details

Storey's method estimates:
$$\hat{\pi}_0(\lambda) = \frac{\#\{i : p_i > \lambda\}}{(1-\lambda) \cdot m}$$

Then uses adjusted BH threshold:
$$\text{Reject } H_i \text{ if } p_i \leq \frac{i \alpha}{m \hat{\pi}_0}$$

### Benjamini-Yekutieli (BY) Procedure  
**FDR control under arbitrary dependence**

```python
from online_fdr.batching.by import BatchBY

# Create BY instance
by = BatchBY(alpha=0.05)

# BY is more conservative than BH for dependent tests
p_values = [0.01, 0.03, 0.05, 0.08, 0.12]

# Compare BH vs BY
bh = BatchBH(alpha=0.05)

bh_decisions = bh.test_batch(p_values)
by_decisions = by.test_batch(p_values)

print("BH vs BY comparison (dependent case):")
print(f"BH discoveries: {sum(bh_decisions)}")
print(f"BY discoveries: {sum(by_decisions)}")
print("BY is more conservative for dependent tests")
```

#### Mathematical Formula

BY uses the harmonic series correction:
$$c(m) = \sum_{i=1}^m \frac{1}{i} \approx \log(m) + \gamma$$

Reject $H_i$ if $p_i \leq \frac{i \alpha}{m \cdot c(m)}$

### PRDS: Positive Regression Dependency on Subsets
**Optimized for positively dependent test statistics**

```python
from online_fdr.batching.prds import BatchPRDS

# Create PRDS instance
prds = BatchPRDS(alpha=0.05)

# PRDS works well when test statistics are positively correlated
# (e.g., overlapping genomic regions, related biomarkers)
p_values = [0.002, 0.01, 0.04, 0.06, 0.3, 0.7]

prds_decisions = prds.test_batch(p_values)
bh_decisions = BatchBH(alpha=0.05).test_batch(p_values)

print("PRDS vs BH (positive dependence case):")
print(f"PRDS discoveries: {sum(prds_decisions)}")
print(f"BH discoveries: {sum(bh_decisions)}")
```

## Method Comparison

### When to Use Each Method

| Method | Best For | Assumptions | Power | Conservatism |
|--------|----------|-------------|-------|-------------|
| **BH** | Independent tests | Independence | High | Moderate |
| **Storey-BH** | Unknown π₀ | Independence | Highest | Low |
| **BY** | Arbitrary dependence | Any dependence | Low | High |
| **PRDS** | Positive dependence | PRDS condition | High | Moderate |

### Performance Simulation

```python
import numpy as np
from online_fdr.batching.bh import BatchBH
from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.batching.by import BatchBY

def compare_batch_methods(n_tests=1000, n_alternatives=100, alpha=0.05):
    """Compare batch methods on simulated data."""
    
    # Simulate p-values
    np.random.seed(42)
    
    # Null p-values (uniform)
    null_p_values = np.random.uniform(0, 1, n_tests - n_alternatives)
    
    # Alternative p-values (beta distribution, skewed toward 0)
    alt_p_values = np.random.beta(0.5, 10, n_alternatives)
    
    # Combine and shuffle
    all_p_values = np.concatenate([null_p_values, alt_p_values])
    true_alternatives = np.concatenate([
        np.zeros(n_tests - n_alternatives, dtype=bool),
        np.ones(n_alternatives, dtype=bool)
    ])
    
    # Shuffle to mix nulls and alternatives
    shuffle_idx = np.random.permutation(n_tests)
    all_p_values = all_p_values[shuffle_idx]
    true_alternatives = true_alternatives[shuffle_idx]
    
    # Test all methods
    methods = {
        'BH': BatchBH(alpha=alpha),
        'Storey-BH': BatchStoreyBH(alpha=alpha, lambda_=0.5),
        'BY': BatchBY(alpha=alpha)
    }
    
    results = {}
    
    for name, method in methods.items():
        decisions = method.test_batch(all_p_values.tolist())
        
        # Calculate metrics
        true_positives = np.sum(decisions & true_alternatives)
        false_positives = np.sum(decisions & ~true_alternatives)
        total_discoveries = true_positives + false_positives
        
        empirical_fdr = false_positives / max(total_discoveries, 1)
        power = true_positives / n_alternatives
        
        results[name] = {
            'discoveries': total_discoveries,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'empirical_fdr': empirical_fdr,
            'power': power
        }
    
    return results

# Run comparison
comparison_results = compare_batch_methods()

print("Batch Method Comparison Results:")
print("=" * 50)
for method, metrics in comparison_results.items():
    print(f"{method:>10}: {metrics['discoveries']:3d} discoveries, "
          f"FDR={metrics['empirical_fdr']:.3f}, "
          f"Power={metrics['power']:.3f}")
```

## Advanced Usage

### Custom Threshold Calculations

```python
def custom_bh_analysis(p_values, alpha=0.05):
    """Perform detailed BH analysis with visualization."""
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    m = len(p_values)
    sorted_p = np.sort(p_values)
    
    # Calculate BH line
    ranks = np.arange(1, m + 1)
    bh_line = ranks * alpha / m
    
    # Find rejections
    rejections = sorted_p <= bh_line
    if np.any(rejections):
        last_rejection = np.max(np.where(rejections)[0])
        n_rejections = last_rejection + 1
    else:
        n_rejections = 0
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.plot(ranks, sorted_p, 'bo-', label='Sorted p-values', markersize=4)
    plt.plot(ranks, bh_line, 'r--', label=f'BH line (slope = α/m = {alpha/m:.4f})')
    
    if n_rejections > 0:
        plt.fill_between(ranks[:n_rejections], 0, sorted_p[:n_rejections], 
                        alpha=0.3, color='green', label=f'Rejections ({n_rejections})')
    
    plt.xlabel('Rank (i)')
    plt.ylabel('p-value')
    plt.title('Benjamini-Hochberg Procedure Visualization')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    return n_rejections

# Example usage (requires matplotlib)
# p_vals = [0.001, 0.01, 0.03, 0.05, 0.08, 0.15, 0.3, 0.6]
# rejections = custom_bh_analysis(p_vals, alpha=0.1)
```

### Batch Processing Pipeline

```python
def batch_testing_pipeline(data, test_function, method='BH', alpha=0.05):
    """Complete pipeline for batch hypothesis testing."""
    
    # Step 1: Calculate p-values
    print("Step 1: Calculating p-values...")
    p_values = []
    for i, sample in enumerate(data):
        p_val = test_function(sample)
        p_values.append(p_val)
        if i < 5:  # Show first few
            print(f"  Sample {i+1}: p = {p_val:.4f}")
    
    print(f"  ... calculated {len(p_values)} p-values total")
    
    # Step 2: Apply FDR correction
    print(f"\nStep 2: Applying {method} correction (α={alpha})...")
    
    if method == 'BH':
        correction_method = BatchBH(alpha=alpha)
    elif method == 'Storey-BH':
        correction_method = BatchStoreyBH(alpha=alpha, lambda_=0.5)
    elif method == 'BY':
        correction_method = BatchBY(alpha=alpha)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    decisions = correction_method.test_batch(p_values)
    
    # Step 3: Summary statistics
    total_tests = len(p_values)
    discoveries = sum(decisions)
    discovery_rate = discoveries / total_tests
    
    print(f"  Total tests: {total_tests}")
    print(f"  Discoveries: {discoveries}")
    print(f"  Discovery rate: {discovery_rate:.3f}")
    
    # Step 4: Return results
    results = {
        'p_values': p_values,
        'decisions': decisions,
        'method': method,
        'alpha': alpha,
        'discoveries': discoveries,
        'discovery_rate': discovery_rate
    }
    
    return results

# Example usage
def dummy_test_function(sample):
    """Dummy test function returning random p-value."""
    import random
    return random.uniform(0, 1)

# Simulate some data
dummy_data = [f"sample_{i}" for i in range(100)]

# Run pipeline
results = batch_testing_pipeline(
    dummy_data, 
    dummy_test_function, 
    method='BH', 
    alpha=0.1
)
```

## Handling Special Cases

### Empty Results

```python
def safe_batch_testing(p_values, alpha=0.05):
    """Safely handle edge cases in batch testing."""
    
    if not p_values:
        print("Warning: No p-values provided")
        return []
    
    if any(p < 0 or p > 1 for p in p_values):
        print("Error: Invalid p-values detected")
        return None
    
    # Proceed with testing
    bh = BatchBH(alpha=alpha)
    decisions = bh.test_batch(p_values)
    
    if not any(decisions):
        print(f"No discoveries at α={alpha} level")
    
    return decisions

# Test edge cases
print("Testing edge cases:")
print("Empty list:", safe_batch_testing([]))
print("All large p-values:", safe_batch_testing([0.9, 0.8, 0.7]))
print("All small p-values:", safe_batch_testing([0.001, 0.002, 0.003]))
```

### Multiple Testing Correction with Covariates

```python
def stratified_fdr_control(p_values, groups, alpha=0.05):
    """Apply FDR control within groups/strata."""
    
    unique_groups = list(set(groups))
    all_decisions = [False] * len(p_values)
    
    print(f"Applying stratified FDR control across {len(unique_groups)} groups:")
    
    for group in unique_groups:
        # Get indices for this group
        group_indices = [i for i, g in enumerate(groups) if g == group]
        group_p_values = [p_values[i] for i in group_indices]
        
        # Apply BH within group
        bh = BatchBH(alpha=alpha)
        group_decisions = bh.test_batch(group_p_values)
        
        # Map back to full results
        for i, decision in zip(group_indices, group_decisions):
            all_decisions[i] = decision
        
        print(f"  Group {group}: {len(group_p_values)} tests, "
              f"{sum(group_decisions)} discoveries")
    
    return all_decisions

# Example usage
p_vals = [0.01, 0.3, 0.02, 0.8, 0.005, 0.4, 0.001, 0.9]
groups = ['A', 'A', 'B', 'B', 'A', 'B', 'A', 'B']

stratified_results = stratified_fdr_control(p_vals, groups, alpha=0.1)
print(f"\nOverall discoveries: {sum(stratified_results)}")
```

## Integration with Statistical Tests

### Example: Multiple t-tests with FDR Control

```python
import numpy as np
from scipy import stats
from online_fdr.batching.bh import BatchBH

def multiple_t_tests_with_fdr(data_groups, control_group, alpha=0.05):
    """Perform multiple t-tests with FDR correction."""
    
    # Calculate p-values for all comparisons
    p_values = []
    group_names = []
    
    print("Performing t-tests against control:")
    for group_name, group_data in data_groups.items():
        statistic, p_value = stats.ttest_ind(group_data, control_group)
        p_values.append(p_value)
        group_names.append(group_name)
        
        print(f"  {group_name} vs Control: t={statistic:.3f}, p={p_value:.4f}")
    
    # Apply FDR correction
    bh = BatchBH(alpha=alpha)
    decisions = bh.test_batch(p_values)
    
    # Report results
    print(f"\nFDR-corrected results (α={alpha}):")
    significant_groups = []
    
    for group_name, p_val, decision in zip(group_names, p_values, decisions):
        status = "SIGNIFICANT" if decision else "NOT SIGNIFICANT"
        print(f"  {group_name}: {status} (p={p_val:.4f})")
        
        if decision:
            significant_groups.append(group_name)
    
    return significant_groups, p_values, decisions

# Example with simulated data
np.random.seed(123)

# Control group
control = np.random.normal(0, 1, 100)

# Treatment groups with different effect sizes
groups = {
    'Treatment_A': np.random.normal(0.5, 1, 100),    # Small effect
    'Treatment_B': np.random.normal(1.0, 1, 100),    # Medium effect  
    'Treatment_C': np.random.normal(0.1, 1, 100),    # Very small effect
    'Treatment_D': np.random.normal(1.5, 1, 100),    # Large effect
}

significant, p_vals, decisions = multiple_t_tests_with_fdr(
    groups, control, alpha=0.05
)

print(f"\nSignificant treatments: {significant}")
```

## References

1. **Benjamini, Y., and Y. Hochberg** (1995). "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." *Journal of the Royal Statistical Society*, Series B, 57(1):289-300.

2. **Storey, J. D.** (2002). "A direct approach to false discovery rates." *Journal of the Royal Statistical Society*, Series B, 64(3):479-498.

3. **Benjamini, Y., and D. Yekutieli** (2001). "The control of the false discovery rate in multiple testing under dependency." *Annals of Statistics*, 29(4):1165-1188.

4. **Benjamini, Y., and D. Yekutieli** (1999). "Resampling-based false discovery rate controlling multiple test procedures for correlated test statistics." *Journal of Statistical Planning and Inference*, 82(1-2):171-196.

## Next Steps

- **Compare with [sequential methods](sequential.md)** for online scenarios
- **See [examples](../examples/comparison.md)** for detailed method comparisons  
- **Study [theory](../theory/fdr_control.md)** for mathematical foundations