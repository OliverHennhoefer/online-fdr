# Quick Start Guide

This guide will get you up and running with **online-fdr** in just a few minutes. We'll walk through the core concepts and show you how to perform online FDR control with real examples.

## Basic Concepts

Before diving into code, let's understand the key concepts:

!!! info "Online vs Batch Testing"
    - **Batch Testing**: Collect all p-values first, then apply multiple testing correction
    - **Online Testing**: Make decisions immediately as each p-value arrives

!!! info "FDR Control"
    False Discovery Rate (FDR) is the expected proportion of false discoveries among all discoveries:
    $$\text{FDR} = \mathbb{E}\left[\frac{\text{False Positives}}{\max(\text{Total Discoveries}, 1)}\right]$$

## Your First Online Test

Let's start with the simplest possible example using ADDIS:

```python
from online_fdr.p_values.investing.addis.addis import Addis

# Create an ADDIS procedure with 5% FDR control
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Test individual p-values as they arrive
p_values = [0.001, 0.1, 0.03, 0.8, 0.02]

for i, p_val in enumerate(p_values):
    decision = addis.test_one(p_val)
    print(f"Test {i+1}: p={p_val:5.3f}  {'REJECT' if decision else 'ACCEPT'}")
```

Output:
```
Test 1: p=0.001  REJECT
Test 2: p=0.100  ACCEPT  
Test 3: p=0.030  REJECT
Test 4: p=0.800  ACCEPT
Test 5: p=0.020  ACCEPT
```

## Realistic Simulation

Let's create a more realistic scenario with simulated data:

```python
from online_fdr.p_values.investing.addis.addis import Addis
from online_fdr.core.utils.generation import DataGenerator, GaussianLocationModel

# Set up data generation
# 90% null hypotheses, 10% alternatives with effect size 3
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=200, pi0=0.9, dgp=dgp)

# Initialize ADDIS
addis = Addis(alpha=0.1, wealth=0.05, lambda_=0.25, tau=0.5)

# Simulate sequential testing
discoveries = []
true_discoveries = []
false_discoveries = []

print("Sequential Online Testing with ADDIS")
print("=" * 50)

for i in range(50):  # Test first 50 hypotheses
    p_value, is_alternative = generator.sample_one()
    decision = addis.test_one(p_value)
    
    if decision:  # We made a discovery
        discoveries.append(i + 1)
        if is_alternative:
            true_discoveries.append(i + 1)
            result = "true discovery"
        else:
            false_discoveries.append(i + 1)
            result = "false discovery"
        
        print(f"Test {i+1:2d}: p={p_value:.4f}  discovery ({result})")

# Calculate performance metrics
n_discoveries = len(discoveries)
n_false = len(false_discoveries)
empirical_fdr = n_false / max(n_discoveries, 1)

print(f"\nResults after 50 tests:")
print(f"Total discoveries: {n_discoveries}")
print(f"False discoveries: {n_false}")
print(f"Empirical FDR: {empirical_fdr:.3f}")
print(f"Target FDR: {addis.alpha0}")
```

## Comparing Different Methods

Let's compare several online FDR methods on the same data:

```python
from online_fdr.p_values.investing.addis.addis import Addis
from online_fdr.p_values.investing.lord.three import LordThree
from online_fdr.p_values.investing.saffron.saffron import Saffron
from online_fdr.core.utils.generation import DataGenerator, GaussianLocationModel

# Setup
dgp = GaussianLocationModel(alt_mean=2.5, alt_std=1.0, one_sided=True)
alpha = 0.1

# Initialize different methods
methods = {
    'ADDIS': Addis(alpha=alpha, wealth=0.05, lambda_=0.25, tau=0.5),
    'LORD3': LordThree(alpha=alpha, wealth=0.05, reward=0.05),
    'SAFFRON': Saffron(alpha=alpha, wealth=0.05, lambda_=0.5)
}

# Test all methods on the same sequence
generator = DataGenerator(n=100, pi0=0.8, dgp=dgp)
p_values = [generator.sample_one()[0] for _ in range(30)]

print("Method Comparison")
print("=" * 60)

for name, method in methods.items():
    discoveries = 0
    for i, p_val in enumerate(p_values):
        if method.test_one(p_val):
            discoveries += 1
    
    print(f"{name:>8}: {discoveries:2d} discoveries")
```

## Batch vs Online Comparison

See the difference between batch and online approaches:

```python
from online_fdr.p_values.batching.bh import BatchBH
from online_fdr.p_values.investing.lord.three import LordThree
from online_fdr.core.utils.generation import DataGenerator, GaussianLocationModel

# Generate a fixed set of p-values
dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)  
generator = DataGenerator(n=100, pi0=0.85, dgp=dgp)
p_values = [generator.sample_one()[0] for _ in range(20)]

print("Batch vs Online Comparison")
print("=" * 40)
print("P-values:", [f"{p:.3f}" for p in p_values[:10]], "...")

# Batch method: sees all p-values at once
batch_bh = BatchBH(alpha=0.1)
batch_results = batch_bh.test_batch(p_values)
batch_discoveries = sum(batch_results)

print(f"\nBatch BH discoveries: {batch_discoveries}")
print("Rejected p-values:", [f"{p:.3f}" for p, r in zip(p_values, batch_results) if r])

# Online method: sees p-values one by one
lord3 = LordThree(alpha=0.1, wealth=0.05, reward=0.05)
online_discoveries = 0
online_rejected = []

for p_val in p_values:
    if lord3.test_one(p_val):
        online_discoveries += 1
        online_rejected.append(p_val)

print(f"\nOnline LORD3 discoveries: {online_discoveries}")
print("Rejected p-values:", [f"{p:.3f}" for p in online_rejected])
```

## Working with Real Data

Here's how to use your own p-values:

```python
from online_fdr.p_values.investing.addis.addis import Addis

# Your p-values from real experiments
my_p_values = [0.032, 0.001, 0.145, 0.003, 0.234, 0.089, 0.012]

# Initialize method
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Test sequentially
significant_tests = []
for i, p_val in enumerate(my_p_values):
    if addis.test_one(p_val):
        significant_tests.append((i, p_val))
        print(f"Significant: Test {i} with p-value {p_val}")

print(f"\nFound {len(significant_tests)} significant results")
```

## Key Takeaways

!!! success "What You've Learned"
    1. **Online testing** makes decisions immediately without waiting for future p-values
    2. **All methods use** the same `test_one(p_value)` interface  
    3. **Different methods** have different power characteristics
    4. **ADDIS** is a good default choice for most applications
    5. **Method parameters** affect the power/conservatism trade-off

## Next Steps

Now that you understand the basics:

=== "Learn More About Methods"
    Read about [Sequential Testing Methods](user_guide/sequential.md) and [Batch Testing Methods](user_guide/batch.md)

=== "Explore Advanced Examples"  
    Check out [Real-world Examples](examples/index.md) for domain-specific applications

=== "Understand the Theory"
    Dive into [Mathematical Theory](theory/index.md) behind the algorithms

=== "Browse API Documentation"
    Explore the full [API Reference](api/index.md) for all available methods

## Common Patterns

Here are some common usage patterns to get you started:

### Pattern 1: Simple Online Testing
```python
from online_fdr.p_values.investing.addis.addis import Addis

method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
for p_value in your_p_values:
    if method.test_one(p_value):
        print(f"Significant result: p = {p_value}")
```

### Pattern 2: Performance Evaluation
```python
from online_fdr.core.utils.evaluation import calculate_sfdr, calculate_power

true_positives = false_positives = false_negatives = 0
for p_value, is_true_alternative in your_labeled_data:
    decision = method.test_one(p_value)
    # Update counters based on decision and true_alternative
    
sfdr = calculate_sfdr(true_positives, false_positives)
power = calculate_power(true_positives, false_negatives)
```

### Pattern 3: Method Comparison
```python
methods = [Addis(...), LordThree(...), Saffron(...)]
for method in methods:
    discoveries = sum(method.test_one(p) for p in p_values)
    print(f"{method.__class__.__name__}: {discoveries} discoveries")
```

Ready to explore more advanced features? Check out our detailed [User Guide](user_guide/index.md)!
