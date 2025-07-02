# Online FDR: Online False Discovery Rate Control Algorithms

[![python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
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

# For independent p-values
lond_indep = Lond(alpha=0.05)

# For dependent p-values  
lond_dep = Lond(alpha=0.05, dependent=True)

# Both use the same API
for p_value, _ in zip([0.01, 0.8, 0.003, 0.9], [True, False, True, False]):
    result = lond_indep.test_one(p_value)
    print(f"Independent LOND: p={p_value}, discovery={result}")
```

### 3. **LORD with Memory Decay for Time Series**

```python
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.utils.evaluation import MemoryDecayFDR

# For non-stationary time series with decay
lord_decay = LORDMemoryDecay(alpha=0.1, delta=0.99, eta=0.5)

# Track memory-decay FDR  
mem_fdr = MemoryDecayFDR(delta=0.99, offset=0)

dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=500, pi0=0.98, dgp=dgp)

for i in range(100):
    p_value, true_label = generator.sample_one()
    is_discovery = lord_decay.test_one(p_value)
    fdr = mem_fdr.score_one(is_discovery, true_label)
    print(f"Memory-decay FDR: {fdr:.4f}")
```

### 4. **Batch Testing**

```python
from online_fdr.batching.storey_bh import BatchStoreyBH

batch_proc = BatchStoreyBH(alpha=0.1, lambda_=0.5)

# Generate a batch of p-values
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=250, pi0=0.95, dgp=dgp)

# Process in batches of 50
batch_size = 50
p_values, labels = [], []
for _ in range(batch_size):
    p_value, label = generator.sample_one()
    p_values.append(p_value)
    labels.append(label)

# Test entire batch at once
results = batch_proc.test_batch(p_values)
discoveries = sum(results)
print(f"Batch discoveries: {discoveries}/{batch_size}")
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
    ChiSquaredModel
)

# Gaussian location model
dgp1 = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)

# Beta mixture model  
dgp2 = BetaMixtureModel(alpha_alt=0.5, beta_alt=1.0)

# Chi-squared model
dgp3 = ChiSquaredModel(df_alt=5)

# Use with any data generator
generator = DataGenerator(n=1000, pi0=0.9, dgp=dgp1)
```

## Advanced Usage

### Alpha Spending with Custom Functions

```python
from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.functions.bonferroni import Bonferroni

# Use Bonferroni spending function
alpha_spending = AlphaSpending(alpha=0.1, spend_func=Bonferroni(1000))

# Test sequentially
for p_value, _ in zip([0.01, 0.8, 0.003], [True, False, True]):
    result = alpha_spending.test_one(p_value)
    print(f"Alpha spending result: {result}")
```

## Requirements

The library requires:
- Python 3.8+
- numpy >= 1.20.0
- scipy >= 1.9.0

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/online-fdr.git
cd online-fdr

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest

# Format code
black online_fdr tests
```

## Key Features

- **True Online API**: Make decisions sequentially as p-values arrive
- **Unified Interface**: All methods use `test_one()` for sequential testing
- **Batch Support**: Batch methods use `test_batch()` for multiple p-values
- **Rich Data Generation**: Multiple data generation models for testing
- **Performance Evaluation**: Built-in utilities for calculating sFDR and power

## Mathematical Guarantees

Each implemented method provides rigorous theoretical guarantees:
- **FDR Control**: Expected FDR ≤ α for all FDR control methods
- **FWER Control**: Probability of any false rejection ≤ α for alpha spending methods

## Acknowledgements

This library is inspired by and validated against the R package [onlineFDR](https://dsrobertson.github.io/onlineFDR/). 

**Key differentiator**: This implementation provides a truly online API with `test_one()` method calls, enabling real-time sequential applications (the R onlineFDR package requires pre-collected data).

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.