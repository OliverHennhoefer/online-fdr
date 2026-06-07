# API Reference

This section provides comprehensive documentation for all classes and functions in the **online-fdr** library. The API is organized by functionality, with consistent interfaces across all methods.

## Package Structure

```
online_fdr/
 p_values/           # P-value based methods
   async_methods/    # Asynchronous online FDR lifecycle methods
   investing/        # Alpha investing methods
    addis/         # ADDIS algorithm
    alpha/         # Generalized and weighted Alpha Investing
    lond/          # LOND family methods
    lord/          # LORD family methods
    saffron/       # SAFFRON algorithm
   spending/        # Alpha spending methods
    alpha_spending.py
    functions/     # Spending functions
    online_fallback.py
   batching/        # Batch testing methods
    bh.py          # Benjamini-Hochberg variants
    storey_bh.py   # Storey adaptive BH
    prds.py        # Positive regression dependency
    by.py          # Benjamini-Yekutieli
    toad.py        # Decision-deadline TOAD
 e_values/           # E-value based methods and tooling
   batch.py          # e-BH
   sequential.py     # e-LOND
   toolbox.py        # Calibration, conversion, and merging
   processes.py      # E-process helpers
   generation.py     # E-value generators
 core/               # Shared infrastructure
   utils/            # Utilities and helpers
    generation.py  # Data generation
    evaluation.py  # Performance metrics
    format.py      # Output formatting
    validity.py    # Input validation
   abstract/        # Base classes and interfaces
```

## Common Interface

All online FDR methods implement a consistent interface:

### Sequential Testing Methods

```python
class SequentialMethod:
    def __init__(self, alpha: float, **kwargs):
        """Initialize with FDR level and method-specific parameters."""
        
    def test_one(self, p_value: float) -> bool:
        """Test a single p-value. Returns True if rejected."""
        
    @property 
    def alpha(self) -> float:
        """Current significance threshold."""
```

### Batch Testing Methods

```python
class BatchMethod:
    def __init__(self, alpha: float, **kwargs):
        """Initialize with FDR level and method-specific parameters."""
        
    def test_batch(self, p_values: list[float]) -> list[bool]:
        """Test a batch of p-values. Returns rejection decisions."""
```

### E-Value Methods

```python
class EValueSequentialMethod:
    def __init__(self, alpha: float, **kwargs):
        """Initialize with target FDR level and method-specific parameters."""

    def test_one(self, e_value: float) -> bool:
        """Test a single e-value. Returns True if rejected."""
```

```python
class EValueBatchMethod:
    def __init__(self, alpha: float, **kwargs):
        """Initialize with target FDR level and method-specific parameters."""

    def test_batch(self, e_values: list[float]) -> list[bool]:
        """Test a batch of e-values. Returns rejection decisions."""
```

### Asynchronous Lifecycle Methods

```python
class AsyncMethod:
    def start_test(self, test_id=None):
        """Reserve and return a test level before the p-value is known."""

    def finish_test(self, test_id, p_value: float) -> bool:
        """Record the p-value and return the final rejection decision."""
```

## Quick Reference

### Most Common Methods

| **Method** | **Import Path** | **Best For** |
|------------|-----------------|--------------|
| e-BH | `online_fdr.e_values.EBH` | Batch FDR with e-values under arbitrary dependence |
| e-LOND | `online_fdr.e_values.ELond` | Online FDR with e-values under arbitrary dependence |
| ADDIS | `online_fdr.p_values.investing.addis.addis.Addis` | General-purpose online FDR |
| Async ADDIS | `online_fdr.p_values.async_methods.AddisAsync` | Overlapping tests with delayed p-values |
| Async SAFFRON | `online_fdr.p_values.async_methods.SaffronAsync` | Asynchronous high-throughput screening |
| Weighted GAI++ | `online_fdr.p_values.investing.alpha.weighted_gai_plus_plus.WeightedGaiPlusPlus` | Side-information weighted streams |
| LORD3 | `online_fdr.p_values.investing.lord.three.LordThree` | Sequential with temporal structure |
| SAFFRON | `online_fdr.p_values.investing.saffron.saffron.Saffron` | High-throughput screening |
| Batch BH | `online_fdr.p_values.batching.bh.BatchBH` | Traditional batch FDR control |
| TOAD | `online_fdr.p_values.batching.toad.Toad` | Tests with decision deadlines |

### Parameter Quick Start

Most common parameter combinations for getting started:

=== "ADDIS (Recommended Default)"
    ```python
    from online_fdr.p_values.investing.addis.addis import Addis
    
    # Conservative
    addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    
    # Moderate  
    addis = Addis(alpha=0.1, wealth=0.05, lambda_=0.5, tau=0.6)
    
    # Aggressive
    addis = Addis(alpha=0.1, wealth=0.075, lambda_=0.75, tau=0.8)
    ```

=== "LORD3 (Time Series)"
    ```python
    from online_fdr.p_values.investing.lord.three import LordThree
    
    # Conservative
    lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)
    
    # Moderate
    lord3 = LordThree(alpha=0.1, wealth=0.05, reward=0.05) 
    
    # Aggressive (must satisfy wealth + reward <= alpha)
    lord3 = LordThree(alpha=0.1, wealth=0.06, reward=0.04)
    ```

=== "Batch BH (Traditional)"
    ```python
    from online_fdr.p_values.batching.bh import BatchBH
    
    # Standard usage
    bh = BatchBH(alpha=0.05)
    results = bh.test_batch(p_values)
    ```

## Method Categories

### [Investing Methods](investing/index.md)
Alpha investing algorithms that adapt thresholds based on past discoveries.

- **[Alpha Investing](investing/gai.md)**: Generalized Alpha Investing (GAI)
- **Weighted GAI++**: Prior/penalty-weighted GAI++ with optional memory decay
- **[ADDIS](investing/addis.md)**: Adaptive discarding algorithm
- **[SAFFRON](investing/saffron.md)**: Serial estimate of the false discovery proportion  
- **[LORD Family](investing/lord.md)**: Levels based on recent observations and discoveries
- **[LOND](investing/lond.md)**: Levels based on number of discoveries

### [Spending Methods](spending/index.md)  
Alpha spending approaches that pre-allocate significance budget.

- **[Alpha Spending](spending/alpha_spending.md)**: General alpha spending framework
- **[Online Fallback](spending/online_fallback.md)**: Online fallback procedures

### [Batch Methods](batching/index.md)
Traditional batch multiple testing correction methods.

- **[Batch Methods Overview](batching/index.md)**: Benjamini-Hochberg, Storey-BH, PRDS, BY, and TOAD procedures

### [Utilities](utils/index.md)
Helper functions and utilities for simulation and evaluation.

- **[Utilities Overview](utils/index.md)**: Data generation, evaluation, formatting, and validation helpers

## Usage Examples

### Basic Sequential Testing

```python
from online_fdr.p_values.investing.addis.addis import Addis

# Initialize method
method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Test p-values sequentially
p_values = [0.01, 0.1, 0.03, 0.8, 0.02]
for i, p in enumerate(p_values):
    decision = method.test_one(p)
    print(f"Test {i+1}: p={p:.3f}  {'REJECT' if decision else 'ACCEPT'}")
```

### Batch Testing

```python
from online_fdr.p_values.batching.bh import BatchBH

# Initialize method  
method = BatchBH(alpha=0.05)

# Test all p-values at once
p_values = [0.01, 0.1, 0.03, 0.8, 0.02]
decisions = method.test_batch(p_values)

for i, (p, decision) in enumerate(zip(p_values, decisions)):
    print(f"Test {i+1}: p={p:.3f}  {'REJECT' if decision else 'ACCEPT'}")
```

### With Data Generation

```python
from online_fdr.p_values.investing.addis.addis import Addis
from online_fdr.core.utils.generation import DataGenerator, GaussianLocationModel

# Set up simulation
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)  
method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Run simulation
discoveries = 0
for i in range(50):
    p_value, is_alternative = generator.sample_one()
    if method.test_one(p_value):
        discoveries += 1
        
print(f"Made {discoveries} discoveries")
```

### Performance Evaluation

```python
from online_fdr.core.utils.evaluation import calculate_sfdr, calculate_power

# Track results during testing
true_positives = false_positives = false_negatives = 0

for p_value, is_alternative in labeled_data:
    decision = method.test_one(p_value)
    
    if decision and is_alternative:
        true_positives += 1
    elif decision and not is_alternative:
        false_positives += 1  
    elif not decision and is_alternative:
        false_negatives += 1

# Calculate metrics
sfdr = calculate_sfdr(true_positives, false_positives)
power = calculate_power(true_positives, false_negatives)

print(f"Empirical sFDR: {sfdr:.3f}")
print(f"Empirical Power: {power:.3f}")
```

## Error Handling

The library includes comprehensive input validation:

```python
from online_fdr.p_values.investing.addis.addis import Addis

try:
    # Invalid parameters will raise ValueError
    addis = Addis(alpha=1.5, wealth=0.1, lambda_=0.5, tau=0.5)
except ValueError as e:
    print(f"Parameter error: {e}")

try: 
    # Invalid p-values will raise ValueError
    addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    result = addis.test_one(-0.1)  # Invalid p-value
except ValueError as e:
    print(f"P-value error: {e}")
```

## Type Hints and IDE Support

All methods include comprehensive type hints for better IDE support:

```python
from typing import List
from online_fdr.p_values.investing.addis.addis import Addis

def run_online_fdr(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """Run ADDIS on a sequence of p-values."""
    method = Addis(alpha=alpha, wealth=alpha/2, lambda_=0.25, tau=0.5)
    return [method.test_one(p) for p in p_values]
```

## Next Steps

- **Browse specific method documentation** in the sections above
- **See real-world applications** in [Examples](../examples/index.md)  
- **Learn the theory** behind methods in [Theory](../theory/index.md)
- **Understand concepts** in [User Guide](../user_guide/index.md)
