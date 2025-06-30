# Online FDR: Online False Discovery Rate Control Algorithms

[![python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![pypi](https://img.shields.io/pypi/v/online-fdr.svg)](https://pypi.org/project/online-fdr/)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/yourusername/online-fdr/issues)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code_style-black-black)](https://github.com/psf/black)
[![tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/yourusername/online-fdr/actions)

## 🎯 Overview

**online-fdr** is a comprehensive Python library for controlling False Discovery Rate (FDR) and Family-Wise Error Rate (FWER) in online multiple hypothesis testing scenarios. Unlike traditional methods that require all p-values upfront, our library provides truly online algorithms that make decisions sequentially as data arrives.

### Why Online FDR Control?

In modern data science and scientific research, hypotheses often arrive sequentially:
- 🔬 **Clinical Trials**: Interim analyses as patient data accumulates
- 📊 **A/B Testing**: Continuous experimentation in tech companies
- 🧬 **Genomics**: Sequential gene discovery studies
- 📈 **Finance**: Real-time anomaly detection in trading
- 🌐 **Web Analytics**: Ongoing feature testing and optimization

Traditional FDR control methods require batch processing of all hypotheses simultaneously. This library implements state-of-the-art online algorithms that:
- ✅ Make immediate decisions without waiting for future data
- ✅ Maintain rigorous statistical guarantees
- ✅ Adapt to the sequential nature of modern data collection
- ✅ Support both independent and dependent p-values

## 🚀 Quick Start

### Installation

```bash
pip install online-fdr
```

### Basic Usage

```python
from online_fdr.investing.alpha.alpha import Gai
from online_fdr.utils.generation import ImprovedDataGenerator, GaussianLocationModel

# Initialize a data generator for demonstration
dgp = GaussianLocationModel(alt_mean=3.0, alt_std=1.0, one_sided=True)
generator = ImprovedDataGenerator(n=1000, pi0=0.9, dgp=dgp)  # 10% alternatives

# Create an online FDR procedure
alpha_investing = Gai(alpha=0.05)

# Test hypotheses sequentially
discoveries = []
for i in range(100):
    p_value, label = generator.sample_one()
    is_discovery = alpha_investing.test_one(p_value)
    
    if is_discovery:
        discoveries.append(i)
        print(f"Discovery at test {i}: p-value = {p_value:.4f}")
```

## 📚 Implemented Methods

### Sequential Testing Methods

Methods that test one hypothesis at a time:

#### **Alpha Investing Family**
- **[Generalized Alpha Investing (GAI)](https://www.jstor.org/stable/24774568)**: The classic alpha investing framework by Foster & Stine
- **[SAFFRON](https://proceedings.mlr.press/v80/ramdas18a/ramdas18a.pdf)**: Adaptive algorithm with improved power
- **[ADDIS](https://proceedings.neurips.cc/paper_files/paper/2019/file/1d6408264d31d453d556c60fe7d0459e-Paper.pdf)**: Adaptive algorithm that discards conservative nulls

#### **LORD Family**
- **[LORD3](https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.full)**: Wealth-based testing with rewards
- **LORD++**: Improved variant with better power
- **D-LORD**: Version for dependent p-values
- **[LORD with Memory Decay](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf)**: For non-stationary time series

#### **LOND Family**
- **[LOND](https://proceedings.neurips.cc/paper/2017/file/7f018eb7b301a66658931cb8a93fd6e8-Paper.pdf)**: Levels based on Number of Discoveries
- **Modified LOND**: Improved variant with max(R_t, 1)
- **LOND for Dependent p-values**: Handles arbitrary dependence

#### **Alpha Spending**
- **Bonferroni-like procedures**: Classic FWER control adapted for sequential testing
- **[Online Fallback](https://journals.sagepub.com/doi/abs/10.1177/0962280220983381)**: Guarantees FWER control in sequential settings

### Batch Testing Methods

Methods that test hypotheses in batches:

- **[BatchBH](https://proceedings.mlr.press/v108/zrnic20a/zrnic20a.pdf)**: Online version of Benjamini-Hochberg
- **[BatchStBH](https://proceedings.mlr.press/v108/zrnic20a/zrnic20a.pdf)**: Storey's improvement to BH for batches
- **BatchPRDS**: For positive regression dependency
- **BatchBY**: Benjamini-Yekutieli for arbitrary dependence

## 💡 Key Features

### 1. **True Online API**
Unlike other implementations that require pre-collected data, our library offers genuinely sequential testing:

```python
# Real-world scenario: testing as data arrives
procedure = Addis(alpha=0.05, wealth=0.025, tau=0.5)

# In production, p-values arrive one by one
while data_stream.is_active():
    p_value = compute_p_value(data_stream.get_next())
    decision = procedure.test_one(p_value)
    
    if decision:
        trigger_alert()
```

### 2. **Unified Interface**
All procedures follow the same simple interface:

```python
# Sequential testing
result = procedure.test_one(p_value)

# Batch testing
results = batch_procedure.test_batch(p_values_list)
```

### 3. **Flexible Configuration**
Each method supports various configurations for different scenarios:

```python
# For independent p-values
lond_indep = Lond(alpha=0.05)

# For dependent p-values  
lond_dep = Lond(alpha=0.05, dependent=True)

# With decay for time series
lord_decay = LORDMemoryDecay(alpha=0.05, wealth=0.025, delta=0.95)
```

### 4. **Rich Utilities**
Built-in tools for evaluation and testing:

```python
from online_fdr.utils.evaluation import evaluate_procedures
from online_fdr.utils.visualization import plot_wealth_trajectory

# Compare different procedures
results = evaluate_procedures(
    procedures=[lord3, lond, saffron],
    data_generator=generator,
    n_runs=100
)
```

## 📊 Performance Comparison

The library includes comprehensive benchmarking tools:

```python
from online_fdr.benchmarks import compare_methods

# Compare methods on your data
comparison = compare_methods(
    p_values=your_p_values,
    methods=['lord3', 'saffron', 'addis'],
    alpha=0.05
)
comparison.plot_power_curves()
```

## 🔬 Mathematical Foundations

Each implemented method provides rigorous theoretical guarantees:

- **FDR Control**: $\mathbb{E}[\text{FDR}] \leq \alpha$ for all methods
- **FWER Control**: $\mathbb{P}(\text{Any false rejection}) \leq \alpha$ for alpha spending methods
- **Power**: Optimized algorithms that maximize discovery rate while maintaining control

## 🛠️ Advanced Usage

### Custom Gamma Sequences

```python
from online_fdr.utils.sequence import AbstractGammaSequence

class MyGammaSequence(AbstractGammaSequence):
    def calc_gamma(self, j: int) -> float:
        return self.c / (j * np.log(j + 1))

# Use with any compatible method
lord_custom = LordThree(alpha=0.05, wealth=0.025, gamma_sequence=MyGammaSequence(c=0.07))
```

### Handling Dependent P-values

```python
# For arbitrary dependence
lond_dep = Lond(alpha=0.05, dependent=True)

# For positive dependence (PRDS)
batch_prds = BatchPRDS(alpha=0.05)
```

## 📖 Documentation

For detailed documentation, tutorials, and API reference, visit our [documentation site](https://online-fdr.readthedocs.io).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

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

## 📝 Citation

If you use this library in your research, please cite:

```bibtex
@software{online_fdr,
  title = {online-fdr: Online False Discovery Rate Control Algorithms},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/online-fdr}
}
```

## 🙏 Acknowledgements

This library is inspired by and validated against the R package [onlineFDR](https://dsrobertson.github.io/onlineFDR/). We extend our gratitude to the authors of the original papers and the onlineFDR package maintainers.

## 📄 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

---

## Original Content

The vast majority of implementations of online method for FDR control are either part of an experimental setup, that does
not straight-forwardly generalize towards applications outside this setup, or are geared towards tests for which all test
results are already available (i.e. they do not have an actual _online_ API).

For that reason, this repository implements a wide range of methods for FDR/FWER control for _actual_ online multiple
hypothesis testing with an intuitive `test_one()` method:

- **Alpha Spending** (Bonferroni, ...)
- [**Online Fallback**](https://journals.sagepub.com/doi/abs/10.1177/0962280220983381)
- **[[Generalized] Alpha Investing](https://www.jstor.org/stable/24774568)** ([Foster/Stine](http://deanfoster.net/research/edc.pdf), ...)
- [**LOND**](https://proceedings.neurips.cc/paper/2017/file/7f018eb7b301a66658931cb8a93fd6e8-Paper.pdf) (Original, Modified, Dependent)
- [**LORD**](https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.full) (LORD3, LOND++, D-LORD, Dependent, [DecayLORD](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf))
- [**SAFFRON**](https://proceedings.mlr.press/v80/ramdas18a/ramdas18a.pdf) (Standard, [DecaySAFFRON](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf))
- [**ADDIS**](https://proceedings.neurips.cc/paper_files/paper/2019/file/1d6408264d31d453d556c60fe7d0459e-Paper.pdf) (Standard, [DecayADDIS](https://papers.nips.cc/paper_files/paper/2021/file/def130d0b67eb38b7a8f4e7121ed432c-Paper.pdf))
- [**Batch-BH**](https://proceedings.mlr.press/v108/zrnic20a/zrnic20a.pdf) and [**Batch-StBH**](https://proceedings.mlr.press/v108/zrnic20a/zrnic20a.pdf)

Instantiate an online testing procedure (e.g. `Addis()`) and simply test _p_-values sequentially with `.test_one()`:
```python
from online_fdr.investing.addis.addis import Addis
from online_fdr.utils.generation import ImprovedDataGenerator, GaussianLocationModel

N = 100
dgp = GaussianLocationModel(alt_mean=3.0)
generator = ImprovedDataGenerator(n=N, pi0=0.9, dgp=dgp)  # 10% alternatives

addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)  # procedure

for i in range(0, N):
    p_value, label = generator.sample_one()
    result = addis.test_one(p_value)  # sequential testing
```

### 5. **Advanced Data Generation**

```python
from online_fdr.utils.generation import (
    BetaMixtureModel, DependentGaussianModel, SparseGaussianModel,
    create_genomics_generator, create_screening_generator
)

# Genomics-style data (many nulls, beta-distributed alternatives)
gen_genomics = create_genomics_generator(n=10000, pi0=0.95)

# Screening study with sparse signals
gen_screening = create_screening_generator(n=1000, pi0=0.9, 
                                         min_effect=2.0, max_effect=5.0)

# Dependent p-values with block correlation
dgp_dep = DependentGaussianModel(alt_mean=3.0, correlation=0.5, 
                                structure="block", block_size=20)
gen_dependent = ImprovedDataGenerator(n=500, pi0=0.8, dgp=dgp_dep)

# Batch generation for batch methods
p_vals_batch, labels_batch = gen_genomics.sample_batch(size=100)
```

_This work is inspired by the R package '[onlineFDR](https://dsrobertson.github.io/onlineFDR/)'. 
This package, and most of its methods, are largely validated by the [implementations](https://github.com/dsrobertson/onlineFDR) of said package.
**Key differentiator is the design choice in regard to method calls for sequential testing, as this implementation allows for truly temporal applications** ('onlineFDR' requires a [static] data.frame for testing)._

# Getting started

The library requires numpy and scipy for advanced data generation features. It's recommended to use with Python 3.8+, with testing performed on Python 3.12.