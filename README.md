# Online FDR: Online False Discovery Rate Control Algorithms

[![python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code_style-black-black)](https://github.com/psf/black)

## Overview

**online-fdr** is a Python library for controlling False Discovery Rate (FDR) and Family-Wise Error Rate (FWER) in online multiple hypothesis testing scenarios. Unlike traditional methods that require all p-values upfront, this library provides truly online algorithms that make decisions sequentially as data arrives.

### Why Online FDR Control?

In many applications, hypotheses arrive sequentially:
- **Clinical Trials**: Interim analyses as patient data accumulates
- **A/B Testing**: Continuous experimentation in tech companies  
- **Genomics**: Sequential gene discovery studies
- **Finance**: Real-time anomaly detection in trading
- **Web Analytics**: Ongoing feature testing and optimization

This library implements state-of-the-art online algorithms that:
- Make immediate decisions without waiting for future data
- Maintain rigorous statistical guarantees
- Support both independent and dependent p-values
- Provide a unified API for sequential and batch testing

## Installation

```bash
pip install online-fdr
```

## Quick Start

```python
from online_fdr.investing.addis.addis import Addis
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

# Initialize a data generator for demonstration
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=1000, pi0=0.9, dgp=dgp)  # 10% alternatives

# Create an online FDR procedure  
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Test hypotheses sequentially
discoveries = []
for i in range(100):
    p_value, label = generator.sample_one()
    is_discovery = addis.test_one(p_value)
    
    if is_discovery:
        discoveries.append(i)
        print(f"Discovery at test {i}: p-value = {p_value:.4f}")

print(f"Made {len(discoveries)} discoveries")
```

## Implemented Methods

### Sequential Testing Methods

Methods that test one hypothesis at a time:

#### **Alpha Investing Family**
- **Generalized Alpha Investing (GAI)**: `from online_fdr.investing.alpha.alpha import Gai`
- **SAFFRON**: `from online_fdr.investing.saffron.saffron import Saffron`  
- **ADDIS**: `from online_fdr.investing.addis.addis import Addis`

#### **LORD Family**
- **LORD3**: `from online_fdr.investing.lord.three import LordThree`
- **LORD++**: `from online_fdr.investing.lord.plus_plus import LordPlusPlus`
- **D-LORD**: `from online_fdr.investing.lord.dependent import LordDependent`
- **LORD with Discard**: `from online_fdr.investing.lord.discard import LordDiscard`
- **LORD with Memory Decay**: `from online_fdr.investing.lord.mem_decay import LORDMemoryDecay`

#### **LOND Family**
- **LOND**: `from online_fdr.investing.lond.lond import Lond`

#### **Alpha Spending**
- **Alpha Spending**: `from online_fdr.spending.alpha_spending import AlphaSpending`
- **Online Fallback**: `from online_fdr.spending.online_fallback import OnlineFallback`

### Batch Testing Methods

Methods that test hypotheses in batches:

- **BatchBH**: `from online_fdr.batching.bh import BatchBH`
- **BatchStoreyBH**: `from online_fdr.batching.storey_bh import BatchStoreyBH`
- **BatchPRDS**: `from online_fdr.batching.prds import BatchPRDS`
- **BatchBY**: `from online_fdr.batching.by import BatchBY`

## Usage Examples

### 1. **Alpha Investing (GAI)**

```python
from online_fdr.investing.alpha.alpha import Gai
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

# Note: GAI requires a wealth parameter
gai = Gai(alpha=0.05, wealth=0.025)

# Generate test data
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)

# Test sequentially
for i in range(100):
    p_value, true_label = generator.sample_one()
    is_discovery = gai.test_one(p_value)
    print(f"Test {i}: p={p_value:.4f}, Discovery={is_discovery}")
```

### 2. **LOND for Independent and Dependent P-values**

```python
from online_fdr.investing.lond.lond import Lond
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

# For independent p-values
lond_indep = Lond(alpha=0.05)

# For dependent p-values  
lond_dep = Lond(alpha=0.05, dependent=True)

# Generate test data
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=100, pi0=0.85, dgp=dgp)

print("LOND Independent:")
discoveries_indep = []
for i in range(50):
    p_value, true_label = generator.sample_one()
    result = lond_indep.test_one(p_value)
    if result:
        discoveries_indep.append(i)
        print(f"  Discovery at test {i}: p={p_value:.4f}")

print(f"\nIndependent LOND made {len(discoveries_indep)} discoveries")

# Reset generator for dependent test
generator = DataGenerator(n=100, pi0=0.85, dgp=dgp)
print("\nLOND Dependent:")
discoveries_dep = []
for i in range(50):
    p_value, true_label = generator.sample_one()
    result = lond_dep.test_one(p_value)
    if result:
        discoveries_dep.append(i)
        print(f"  Discovery at test {i}: p={p_value:.4f}")

print(f"\nDependent LOND made {len(discoveries_dep)} discoveries")
```

### 3. **LORD with Memory Decay for Time Series**

```python
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.utils.evaluation import MemoryDecayFDR
from online_fdr.utils.generation import GaussianLocationModel, DataGenerator

# For non-stationary time series with decay
lord_decay = LORDMemoryDecay(alpha=0.1, delta=0.99, eta=0.5)

# Track memory-decay FDR  
mem_fdr = MemoryDecayFDR(delta=0.99, offset=0)

# Generate test data with higher alternative proportion for more discoveries
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=200, pi0=0.90, dgp=dgp)

discoveries = []
fdr_values = []

print("LORD Memory Decay Testing:")
for i in range(100):
    p_value, true_label = generator.sample_one()
    is_discovery = lord_decay.test_one(p_value)
    fdr = mem_fdr.score_one(is_discovery, true_label)
    
    if is_discovery:
        discoveries.append(i)
        print(f"  Discovery at test {i}: p={p_value:.4f}, FDR={fdr:.4f}")
    
    fdr_values.append(fdr)

print(f"\nTotal discoveries: {len(discoveries)}")
print(f"Final memory-decay FDR: {fdr_values[-1]:.4f}")
print(f"Average FDR over sequence: {sum(fdr_values)/len(fdr_values):.4f}")
```

### 4. **Batch Testing**

```python
from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.utils.generation import GaussianLocationModel, DataGenerator

batch_proc = BatchStoreyBH(alpha=0.1, lambda_=0.5)

# Generate test data with higher alternative proportion for more discoveries
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=200, pi0=0.85, dgp=dgp)

# Process multiple batches to demonstrate batch testing
batch_size = 25
total_discoveries = 0
total_false_discoveries = 0

print("Batch Storey-BH Testing:")
for batch_num in range(3):
    p_values, labels = [], []
    
    # Generate one batch
    for _ in range(batch_size):
        p_value, label = generator.sample_one()
        p_values.append(p_value)
        labels.append(label)
    
    # Test entire batch at once
    results = batch_proc.test_batch(p_values)
    discoveries = sum(results)
    
    # Calculate false discoveries
    false_discoveries = sum(1 for r, l in zip(results, labels) if r and not l)
    batch_fdr = false_discoveries / discoveries if discoveries > 0 else 0.0
    
    print(f"  Batch {batch_num + 1}: {discoveries} discoveries, FDR = {batch_fdr:.4f}")
    print(f"    Significant p-values: {[f'{p:.4f}' for p, r in zip(p_values, results) if r]}")
    
    total_discoveries += discoveries
    total_false_discoveries += false_discoveries

overall_fdr = total_false_discoveries / total_discoveries if total_discoveries > 0 else 0.0
print(f"\nOverall: {total_discoveries} discoveries, FDR = {overall_fdr:.4f}")
```

## Evaluation and Utilities

The library provides evaluation utilities to assess performance:

```python
from online_fdr.utils.evaluation import calculate_sfdr, calculate_power
from online_fdr.utils.format import format_result

# Example: Evaluate ADDIS performance
from online_fdr.investing.addis.addis import Addis
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

true_positive = 0
false_positive = 0
false_negatives = 0

for i in range(100):
    p_value, true_label = generator.sample_one()
    result = addis.test_one(p_value)
    
    # Update counters
    true_positive += true_label and result
    false_positive += not true_label and result
    false_negatives += true_label and not result
    
    # Optional: Format output
    format_result(i, result, p_value, addis.alpha)

# Calculate performance metrics
sfdr = calculate_sfdr(tp=true_positive, fp=false_positive)
power = calculate_power(tp=true_positive, fn=false_negatives)

print(f"Empirical sFDR: {sfdr:.4f}")
print(f"Empirical Power: {power:.4f}")
```

## Available Data Generation Models

The library includes several data generation models for testing:

```python
from online_fdr.utils.generation import (
    DataGenerator, 
    GaussianLocationModel,
    BetaMixtureModel, 
    ChiSquaredModel,
    SparseGaussianModel
)

# Gaussian location model (most common for power analysis)
dgp1 = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)

# Beta mixture model (common in genomics)
dgp2 = BetaMixtureModel(alt_alpha=0.5, alt_beta=10.0)

# Chi-squared model (for variance/goodness-of-fit testing)
dgp3 = ChiSquaredModel(df=1, alt_scale=3.0)

# Sparse Gaussian model (for screening applications)
dgp4 = SparseGaussianModel(effect_dist="uniform", min_effect=2.0, max_effect=5.0)

# Example usage with different models
print("Testing different data generation models:")

for i, (name, dgp) in enumerate([
    ("Gaussian Location", dgp1),
    ("Beta Mixture", dgp2), 
    ("Chi-squared", dgp3),
    ("Sparse Gaussian", dgp4)
]):
    generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)
    # Sample a few p-values to demonstrate
    sample_p_values = [generator.sample_one()[0] for _ in range(5)]
    print(f"  {name}: {[f'{p:.4f}' for p in sample_p_values]}")
```

## Advanced Usage

### Alpha Spending with Custom Functions

```python
from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.functions.bonferroni import Bonferroni
from online_fdr.investing.lord.three import LordThree
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

# Generate test data
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)

# Compare Bonferroni spending vs. adaptive LORD3
k = 50  # Expected number of tests
alpha = 0.05

# Bonferroni spending: equal alpha allocation
bonf_spending = AlphaSpending(alpha=alpha, spend_func=Bonferroni(k))

# LORD3 investing: adaptive thresholds (this is the proper LORD3)
lord3_adaptive = LordThree(alpha=alpha, wealth=0.025, reward=0.025)

print("Alpha Spending vs. Adaptive LORD3 Comparison:")
print(f"Overall alpha level: {alpha}")
print(f"Expected tests: {k}")

bonf_discoveries = []
lord3_discoveries = []

# Reset generator for fair comparison
generator = DataGenerator(n=100, pi0=0.9, dgp=dgp)

for i in range(20):
    p_value, true_label = generator.sample_one()
    
    # Test with both methods
    bonf_result = bonf_spending.test_one(p_value)
    lord3_result = lord3_adaptive.test_one(p_value)
    
    if bonf_result:
        bonf_discoveries.append(i)
    if lord3_result:
        lord3_discoveries.append(i)
    
    # Show alpha thresholds for first few tests
    if i < 5:
        bonf_threshold = alpha / k
        lord3_threshold = lord3_adaptive.alpha
        print(f"  Test {i+1}: p={p_value:.4f}")
        print(f"    Bonferroni ={bonf_threshold:.6f}, reject={bonf_result}")
        print(f"    LORD3 ={lord3_threshold:.6f}, reject={lord3_result}")

print(f"\nBonferroni discoveries: {bonf_discoveries}")
print(f"LORD3 adaptive discoveries: {lord3_discoveries}")
print(f"LORD3 typically shows higher power, especially early in the sequence")
```

## Key Features

- **True Online API**: Make decisions sequentially as p-values arrive
- **Unified Interface**: All methods use `test_one()` for sequential testing
- **Batch Support**: Batch methods use `test_batch()` for multiple p-values
- **Rich Data Generation**: Multiple data generation models for testing
- **Performance Evaluation**: Built-in utilities for calculating sFDR and power
- **Light-weight**: Minimal external dependencies

## Mathematical Guarantees

Guarantees are method-specific and assumption-specific.

- **Proven FDR/FWER guarantees** are provided where the algorithm and parameter regime match published theory.
- **Parity methods** align behavior with the `onlineFDR` reference implementation for overlapping scope.
- **Extension/experimental methods** are documented explicitly and should not be interpreted as universally guaranteed.

See the full matrix: `docs/theory/guarantee_matrix.md`.

## onlineFDR Parity and Differences

This package is grounded against Bioconductor `onlineFDR` release semantics for
overlapping procedures (see `docs/user_guide/onlinefdr_parity.md`).

- **Parity**: ADDIS, SAFFRON, LORD family variants, LOND, Alpha-investing,
  Alpha-spending, online-fallback, BatchBH, BatchPRDS, BatchStoreyBH.
- **Intentional API divergence**: true stateful `test_one`/`test_batch`
  interface instead of wrapper-style dataset reprocessing.
- **Not currently mirrored**: internal same-date randomization and
  asynchronous `*star` wrappers from the R ecosystem.

### Mandatory Live R Parity Checks

The parity suite compares Python outputs directly against the live R
`onlineFDR` package via `rpy2` (`tests/test_onlinefdr_parity.py`).

Development and CI require all of the following:

- `rpy2` (installed through `uv sync --group dev`)
- A system R installation on PATH
- Bioconductor `onlineFDR` pinned to `2.18.0`
- R `4.5.x` (required for Bioconductor `3.22`)

If any requirement is missing, parity tests fail with setup instructions.
On Ubuntu/WSL, if `rpy2` build fails with `cannot find -ltirpc`, install
`libtirpc-dev`.

In CI, the full suite can run in a containerized R+Python environment through
`.github/workflows/tests-container.yml`, which installs pinned `onlineFDR`
automatically before running `pytest`.
## Acknowledgements

This library is inspired by and validated against the R package [onlineFDR](https://dsrobertson.github.io/onlineFDR/). 

**Key differentiator**: This implementation provides a truly online API with `test_one()` method calls, enabling real-time sequential applications (the R onlineFDR package requires pre-collected data).

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.


