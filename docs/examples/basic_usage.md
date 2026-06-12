# Basic Usage Examples

This page provides practical examples of using **online-fdr** for common multiple testing scenarios.

## Getting Started

### Simple Sequential Testing

The most basic use case: test p-values one at a time as they arrive.

```python
from online_fdr.p_values import Addis

# Create an ADDIS instance for online FDR control
method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Your p-values from experiments
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45, 0.006]

print("Sequential Online Testing:")
discoveries = []

for i, p_value in enumerate(p_values):
    decision = method.test_one(p_value)
    
    if decision:
        discoveries.append(i + 1)
        print(f" Test {i+1}: p={p_value:.3f}  discovery")
    else:
        print(f"  Test {i+1}: p={p_value:.3f}  no rejection")

print(f"\nTotal discoveries: {len(discoveries)}")
print(f"Discovery indices: {discoveries}")
```

### Batch Testing

When you have all p-values upfront, batch methods are optimal:

```python
from online_fdr.p_values import BatchBH

# Create Benjamini-Hochberg instance
bh = BatchBH(alpha=0.05)

# Test all p-values simultaneously
p_values = [0.001, 0.15, 0.03, 0.8, 0.02, 0.45, 0.006]
decisions = bh.test_batch(p_values)

print("Batch Testing Results:")
discoveries = []

for i, (p_value, decision) in enumerate(zip(p_values, decisions)):
    if decision:
        discoveries.append(i + 1)
        print(f" Test {i+1}: p={p_value:.3f}  discovery")
    else:
        print(f"  Test {i+1}: p={p_value:.3f}  no rejection")

print(f"\nBatch discoveries: {len(discoveries)}")
```

## Working with Simulated Data

### Basic Simulation Setup

Use the built-in data generation utilities for testing:

```python
from online_fdr.core.utils import DataGenerator, GaussianLocationModel
from online_fdr.p_values import Addis

# Set up data generation
dgp = GaussianLocationModel(
    alt_mean=2.0,    # Effect size under alternatives
    alt_std=1.0,     # Standard deviation
    one_sided=True   # One-sided test (more powerful)
)

generator = DataGenerator(
    n=100,     # Total number of tests
    pi0=0.9,   # 90% true nulls, 10% alternatives
    dgp=dgp    # Data generating process
)

# Create method
addis = Addis(alpha=0.1, wealth=0.05, lambda_=0.5, tau=0.7)

print("Simulation with Known Truth:")
print("=" * 35)

true_discoveries = 0
false_discoveries = 0

for i in range(20):  # Test first 20 hypotheses
    p_value, is_alternative = generator.sample_one()
    decision = addis.test_one(p_value)
    
    result_type = ""
    if decision and is_alternative:
        true_discoveries += 1
        result_type = "true discovery"
    elif decision and not is_alternative:
        false_discoveries += 1
        result_type = "false discovery"
    elif not decision and is_alternative:
        result_type = "missed alternative"
    else:
        result_type = "correct null"
    
    truth = "ALT" if is_alternative else "NULL"
    decision_str = "REJECT" if decision else "ACCEPT"
    
    print(f"Test {i+1:2d}: p={p_value:.3f} ({truth:>4})  {decision_str:>6} ({result_type})")

print(f"\nSummary:")
print(f"True discoveries: {true_discoveries}")
print(f"False discoveries: {false_discoveries}")
total_discoveries = true_discoveries + false_discoveries
empirical_fdr = false_discoveries / max(total_discoveries, 1)
print(f"Empirical FDR: {empirical_fdr:.3f}")
print(f"Target FDR: {addis.target_level}")
```

### Performance Evaluation

Compare your method's performance systematically:

```python
from online_fdr.core.utils import calculate_sfdr, calculate_power

def evaluate_method_on_simulation(method, generator, n_tests=100):
    """Evaluate method performance on simulated data."""
    
    # Counters for performance metrics
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    # Store results
    all_p_values = []
    all_decisions = []
    all_truth = []
    
    print(f"Evaluating {method.__class__.__name__} on {n_tests} tests...")
    
    for i in range(n_tests):
        p_value, is_alternative = generator.sample_one()
        decision = method.test_one(p_value)
        
        # Store for analysis
        all_p_values.append(p_value)
        all_decisions.append(decision)
        all_truth.append(is_alternative)
        
        # Update counters
        if decision and is_alternative:
            true_positives += 1
        elif decision and not is_alternative:
            false_positives += 1
        elif not decision and is_alternative:
            false_negatives += 1
    
    # Calculate performance metrics
    total_discoveries = true_positives + false_positives
    total_alternatives = true_positives + false_negatives
    
    fdr = calculate_sfdr(true_positives, false_positives)
    power = calculate_power(true_positives, false_negatives) if total_alternatives > 0 else 0
    
    # Print results
    print(f"\nResults:")
    print(f"  Total tests: {n_tests}")
    print(f"  Total discoveries: {total_discoveries}")
    print(f"  True alternatives: {total_alternatives}")
    print(f"  True positives: {true_positives}")
    print(f"  False positives: {false_positives}")
    print(f"  False negatives: {false_negatives}")
    print(f"  Empirical FDR: {fdr:.3f}")
    print(f"  Statistical power: {power:.3f}")
    print(f"  Discovery rate: {total_discoveries/n_tests:.3f}")
    
    return {
        'fdr': fdr,
        'power': power,
        'discoveries': total_discoveries,
        'tp': true_positives,
        'fp': false_positives,
        'fn': false_negatives
    }

# Run evaluation
dgp = GaussianLocationModel(alt_mean=2.5, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=500, pi0=0.85, dgp=dgp)
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

results = evaluate_method_on_simulation(addis, generator, n_tests=200)
```

## Method Comparison

### Compare Sequential Methods

```python
from online_fdr.p_values import Addis
from online_fdr.p_values import LordThree
from online_fdr.p_values import Saffron

def compare_sequential_methods(p_values, methods_config):
    """Compare multiple sequential methods on same data."""
    
    print("Sequential Method Comparison")
    print("=" * 40)
    
    results = {}
    
    for method_name, method_params in methods_config.items():
        print(f"\nTesting {method_name}:")
        
        # Create method instance
        if method_name == 'ADDIS':
            method = Addis(**method_params)
        elif method_name == 'LORD3':
            method = LordThree(**method_params)
        elif method_name == 'SAFFRON':
            method = Saffron(**method_params)
        
        # Test on the same p-values
        decisions = []
        for p_val in p_values:
            decision = method.test_one(p_val)
            decisions.append(decision)
        
        discoveries = sum(decisions)
        discovery_indices = [i+1 for i, d in enumerate(decisions) if d]
        
        results[method_name] = {
            'decisions': decisions,
            'discoveries': discoveries,
            'indices': discovery_indices
        }
        
        print(f"  Discoveries: {discoveries}")
        print(f"  Discovery indices: {discovery_indices[:10]}{'...' if len(discovery_indices) > 10 else ''}")
    
    return results

# Set up comparison
test_p_values = [0.001, 0.02, 0.15, 0.003, 0.8, 0.01, 0.4, 0.005, 0.9, 0.03]

methods_config = {
    'ADDIS': {'alpha': 0.1, 'wealth': 0.05, 'lambda_': 0.25, 'tau': 0.5},
    'LORD3': {'alpha': 0.1, 'wealth': 0.05, 'reward': 0.05},
    'SAFFRON': {'alpha': 0.1, 'wealth': 0.05, 'lambda_': 0.5}
}

comparison_results = compare_sequential_methods(test_p_values, methods_config)

# Analyze results
print(f"\nSummary:")
for method_name, results in comparison_results.items():
    print(f"{method_name:>8}: {results['discoveries']} discoveries")
```

### Compare with Batch Methods

```python
from online_fdr.p_values import BatchBH
from online_fdr.p_values import BatchStoreyBH

def compare_online_vs_batch(p_values):
    """Compare online methods with batch methods."""
    
    print("Online vs Batch Comparison")
    print("=" * 35)
    
    # Online method
    addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    online_decisions = [addis.test_one(p) for p in p_values]
    online_discoveries = sum(online_decisions)
    
    # Batch methods
    bh = BatchBH(alpha=0.05)
    batch_decisions = bh.test_batch(p_values)
    batch_discoveries = sum(batch_decisions)
    
    storey_bh = BatchStoreyBH(alpha=0.05, lambda_=0.5)
    storey_decisions = storey_bh.test_batch(p_values)
    storey_discoveries = sum(storey_decisions)
    
    print(f"Online ADDIS discoveries: {online_discoveries}")
    print(f"Batch BH discoveries: {batch_discoveries}")
    print(f"Batch Storey-BH discoveries: {storey_discoveries}")
    
    # Show which p-values were rejected by each method
    print(f"\nRejected p-values:")
    
    online_rejected = [p for p, d in zip(p_values, online_decisions) if d]
    batch_rejected = [p for p, d in zip(p_values, batch_decisions) if d]
    storey_rejected = [p for p, d in zip(p_values, storey_decisions) if d]
    
    print(f"ADDIS rejected: {[f'{p:.3f}' for p in online_rejected]}")
    print(f"BH rejected: {[f'{p:.3f}' for p in batch_rejected]}")  
    print(f"Storey-BH rejected: {[f'{p:.3f}' for p in storey_rejected]}")
    
    return {
        'online': online_discoveries,
        'batch_bh': batch_discoveries,
        'batch_storey': storey_discoveries
    }

# Test comparison
test_p_vals = [0.001, 0.02, 0.15, 0.003, 0.8, 0.01, 0.4, 0.005, 0.9, 0.03, 0.25, 0.007]
comparison = compare_online_vs_batch(test_p_vals)

print(f"\nBatch methods typically have higher power due to information advantage")
```

## Real-World Scenarios

### A/B Testing Example

```python
def ab_testing_example():
    """Realistic A/B testing scenario with multiple variants."""
    
    import random
    from scipy.stats import norm
    
    print("A/B Testing Example")
    print("=" * 25)
    
    # Simulate A/B test results
    # Control: conversion rate = 10%
    # Variants: different conversion rates
    variants = {
        'Variant_A': {'conversion_rate': 0.12, 'sample_size': 1000},  # +2%
        'Variant_B': {'conversion_rate': 0.10, 'sample_size': 1000},  # No change
        'Variant_C': {'conversion_rate': 0.15, 'sample_size': 1000},  # +5%
        'Variant_D': {'conversion_rate': 0.11, 'sample_size': 1000},  # +1%
    }
    
    control_rate = 0.10
    control_size = 1000
    
    # Calculate p-values using normal approximation
    p_values = []
    variant_names = []
    true_effects = []
    
    print("Variant test results:")
    
    for variant_name, params in variants.items():
        rate = params['conversion_rate']
        n = params['sample_size']
        
        # Normal approximation for difference in proportions
        se_diff = ((rate * (1 - rate) / n) + (control_rate * (1 - control_rate) / control_size)) ** 0.5
        z_stat = (rate - control_rate) / se_diff
        p_value = 2 * (1 - norm.cdf(abs(z_stat)))  # Two-sided test
        
        p_values.append(p_value)
        variant_names.append(variant_name)
        true_effects.append(rate > control_rate)
        
        print(f"  {variant_name}: {rate:.1%} vs {control_rate:.1%}  p={p_value:.4f}")
    
    # Apply online FDR control
    addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    
    print(f"\nOnline FDR control (=0.05):")
    
    significant_variants = []
    for variant_name, p_value, true_effect in zip(variant_names, p_values, true_effects):
        decision = addis.test_one(p_value)
        
        if decision:
            significant_variants.append(variant_name)
            result_type = " correct" if true_effect else " false positive"
            print(f"  {variant_name}: significant ({result_type})")
        else:
            result_type = " correct" if not true_effect else " false negative"  
            print(f"  {variant_name}: not significant ({result_type})")
    
    print(f"\nRecommendation: Deploy {significant_variants if significant_variants else 'none of the variants'}")
    
    return significant_variants

# Run A/B testing example
ab_results = ab_testing_example()
```

### Genomics Example

```python
def genomics_example():
    """Simplified genomics differential expression example."""
    
    from online_fdr.core.utils import DataGenerator, BetaMixtureModel
    from online_fdr.p_values import Addis
    from online_fdr.p_values import BatchBH
    
    print("Genomics Example: Differential Gene Expression")
    print("=" * 50)
    
    # Simulate genomics data with conservative nulls
    # (common in real genomics due to correlation structure)
    dgp = BetaMixtureModel(alt_alpha=0.3, alt_beta=5.0)  # Alternatives skewed toward 0
    generator = DataGenerator(n=1000, pi0=0.95, dgp=dgp)  # 5% truly differentially expressed
    
    # Generate gene expression data
    genes = []
    p_values = []
    true_status = []
    
    print("Analyzing gene expression...")
    
    for i in range(100):  # Analyze first 100 genes
        p_value, is_alternative = generator.sample_one()
        gene_id = f"GENE_{i+1:03d}"
        
        genes.append(gene_id)
        p_values.append(p_value)
        true_status.append(is_alternative)
    
    print(f"Generated p-values for {len(genes)} genes")
    print(f"True alternatives: {sum(true_status)}")
    
    # Compare online vs batch FDR control
    print(f"\nFDR control comparison:")
    
    # Online method (ADDIS)
    addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    online_decisions = [addis.test_one(p) for p in p_values]
    online_discoveries = sum(online_decisions)
    
    # Batch method (BH)  
    bh = BatchBH(alpha=0.05)
    batch_decisions = bh.test_batch(p_values)
    batch_discoveries = sum(batch_decisions)
    
    print(f"Online ADDIS: {online_discoveries} genes called significant")
    print(f"Batch BH: {batch_discoveries} genes called significant")
    
    # Evaluate accuracy
    online_tp = sum(d and t for d, t in zip(online_decisions, true_status))
    online_fp = sum(d and not t for d, t in zip(online_decisions, true_status))
    
    batch_tp = sum(d and t for d, t in zip(batch_decisions, true_status))
    batch_fp = sum(d and not t for d, t in zip(batch_decisions, true_status))
    
    print(f"\nAccuracy assessment:")
    print(f"Online - True positives: {online_tp}, False positives: {online_fp}")
    print(f"Batch  - True positives: {batch_tp}, False positives: {batch_fp}")
    
    # Show some significant genes
    online_significant = [gene for gene, decision in zip(genes, online_decisions) if decision]
    batch_significant = [gene for gene, decision in zip(genes, batch_decisions) if decision]
    
    print(f"\nSignificant genes (showing first 5):")
    print(f"Online: {online_significant[:5]}")
    print(f"Batch:  {batch_significant[:5]}")
    
    return online_significant, batch_significant

# Run genomics example
online_genes, batch_genes = genomics_example()
```

## Best Practices

### Parameter Selection

```python
def demonstrate_parameter_effects():
    """Show how parameter choices affect performance."""
    
    from online_fdr.p_values import Addis
    from online_fdr.core.utils import DataGenerator, GaussianLocationModel
    
    print("Parameter Effects Demonstration")
    print("=" * 35)
    
    # Fixed test scenario
    dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)
    generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)
    
    # Generate fixed p-values for consistent comparison
    p_values = [generator.sample_one()[0] for _ in range(50)]
    
    # Test different parameter settings
    parameter_sets = [
        {'name': 'Conservative', 'wealth': 0.01, 'lambda_': 0.1, 'tau': 0.3},
        {'name': 'Moderate', 'wealth': 0.025, 'lambda_': 0.25, 'tau': 0.5},
        {'name': 'Aggressive', 'wealth': 0.04, 'lambda_': 0.5, 'tau': 0.7},
    ]
    
    for params in parameter_sets:
        addis = Addis(alpha=0.05, 
                     wealth=params['wealth'],
                     lambda_=params['lambda_'], 
                     tau=params['tau'])
        
        decisions = [addis.test_one(p) for p in p_values]
        discoveries = sum(decisions)
        
        print(f"{params['name']:>12}: {discoveries:2d} discoveries "
              f"(wealth={params['wealth']:.3f}, ={params['lambda_']:.2f}, ={params['tau']:.1f})")
    
    print(f"\nGuideline: Start with moderate parameters and adjust based on performance")

# Run parameter demonstration
demonstrate_parameter_effects()
```

### Error Handling

```python
def robust_fdr_testing(p_values, alpha=0.05):
    """Demonstrate robust FDR testing with error handling."""
    
    from online_fdr.p_values import Addis
    
    print("Robust FDR Testing with Error Handling")
    print("=" * 42)
    
    # Input validation
    if not p_values:
        print("Error: Empty p-value list")
        return []
    
    # Check for invalid p-values
    invalid_p_values = [p for p in p_values if not (0 <= p <= 1)]
    if invalid_p_values:
        print(f"Warning: Found {len(invalid_p_values)} invalid p-values")
        print(f"Invalid values: {invalid_p_values}")
        # Filter out invalid p-values
        p_values = [p for p in p_values if 0 <= p <= 1]
        print(f"Proceeding with {len(p_values)} valid p-values")
    
    # Create method with error handling
    try:
        addis = Addis(alpha=alpha, wealth=alpha/2, lambda_=0.25, tau=0.5)
    except ValueError as e:
        print(f"Error creating ADDIS instance: {e}")
        return []
    
    # Test p-values with error handling
    decisions = []
    errors = 0
    
    for i, p_value in enumerate(p_values):
        try:
            decision = addis.test_one(p_value)
            decisions.append(decision)
            
            if decision:
                print(f" Test {i+1}: p={p_value:.4f}  Discovery")
                
        except Exception as e:
            print(f"Error testing p-value {p_value}: {e}")
            decisions.append(False)
            errors += 1
    
    # Summary
    total_discoveries = sum(decisions)
    print(f"\nResults:")
    print(f"  Valid tests: {len(p_values)}")
    print(f"  Discoveries: {total_discoveries}")
    print(f"  Errors: {errors}")
    print(f"  Success rate: {(len(p_values) - errors) / len(p_values):.1%}")
    
    return decisions

# Test with problematic data
test_data = [0.01, -0.1, 0.03, 1.5, 0.8, 0.02, float('nan'), 0.005]
robust_results = robust_fdr_testing(test_data)
```

## Summary

These basic examples cover:

1. **Simple Usage**: Sequential and batch testing fundamentals
2. **Simulation**: Working with generated data for validation
3. **Comparison**: Evaluating different methods systematically  
4. **Real-World**: Practical applications in A/B testing and genomics
5. **Best Practices**: Parameter selection and robust implementation

## Next Steps

- **Explore [advanced scenarios](advanced.md)** for complex use cases
- **See [method comparisons](comparison.md)** for detailed benchmarking
- **Learn about [theory](../theory/fdr_control.md)** for mathematical foundations
- **Check [API documentation](../api/index.md)** for complete method details
