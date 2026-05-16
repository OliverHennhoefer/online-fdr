# Online FDR: Online False Discovery Rate Control Algorithms

[![python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code_style-black-black)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/online-fdr.svg)](https://badge.fury.io/py/online-fdr)

**online-fdr** is a comprehensive Python library for controlling False Discovery Rate (FDR) and Family-Wise Error Rate (FWER) in online multiple hypothesis testing scenarios. Unlike traditional methods that require all p-values upfront, this library provides truly online algorithms that make decisions sequentially as data arrives.

## Why Online FDR Control?

In many modern applications, hypotheses arrive sequentially and decisions must be made in real-time:

=== "Clinical Trials"
    Interim analyses as patient data accumulates, allowing for early stopping or protocol modifications while maintaining statistical validity.

=== "A/B Testing" 
    Continuous experimentation in tech companies where new variants are tested as they're developed, requiring immediate go/no-go decisions.

=== "Genomics"
    Sequential gene discovery studies where new candidates are evaluated as they're identified through various screening methods.

=== "Finance"
    Real-time anomaly detection in trading systems where suspicious patterns must be flagged immediately as they occur.

=== "Web Analytics"
    Ongoing feature testing and optimization where user behavior changes need rapid assessment for business decisions.

## Key Features

-  **True Online Processing**: Make immediate decisions without waiting for future data
-  **Explicit Guarantee Scope**: Method-by-method assumptions and guarantee status are documented  
-  **Unified API**: Consistent interface across all methods with `test_one()` for sequential testing
-  **Comprehensive Method Coverage**: State-of-the-art algorithms from recent literature
-  **Performance Optimized**: Efficient implementations suitable for high-throughput applications
-  **Rich Documentation**: Detailed mathematical explanations and practical examples

## Quick Installation

```bash
pip install online-fdr
```

## Quick Start Example

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

## Available Methods

### Sequential Testing (One-by-One)

| **Method Family** | **Methods** | **Best For** |
|------------------|-------------|--------------|
| **Alpha Investing** | GAI, Weighted GAI++, SAFFRON, ADDIS | High-throughput screening |
| **Asynchronous** | SAFFRON Async, ADDIS Async | Overlapping tests with delayed p-values |
| **LORD** | LORD3, LORD++, D-LORD, Discard, Memory Decay | Time series with trends |
| **LOND** | LOND | Independent/weakly dependent p-values |
| **Alpha Spending** | Bonferroni, LORD3 spending | Conservative control |

### Batch Testing

| **Method** | **Description** | **Best For** |
|------------|-----------------|--------------|
| **BatchBH** | Classic Benjamini-Hochberg | Independent p-values |
| **BatchStoreyBH** | Adaptive Storey-BH procedure | Unknown null proportion |
| **BatchPRDS** | Positive regression dependency | Positively correlated tests |
| **BatchBY** | Benjamini-Yekutieli extension | Stronger within-batch dependence correction |
| **TOAD** | Decision-deadline online FDR | Tests that can be revised until deadlines |

## Mathematical Guarantees

Guarantees are method-specific and assumption-specific:

!!! theorem "FDR Control"
    For methods in the proven regime, $\mathbb{E}[\text{FDR}] \leq \alpha$ under the documented assumptions.

!!! theorem "FWER Control"  
    For methods in the proven regime, $\mathbb{P}(\text{FWER} > 0) \leq \alpha$ under the documented assumptions.

See [Theory Guarantee Matrix](theory/guarantee_matrix.md) for the exact per-method status.

## Getting Started

=== "New Users"
    Start with our [Quick Start Guide](quickstart.md) for a hands-on introduction to the library.

=== "Researchers"
    Explore the [Theory Section](theory/index.md) for mathematical foundations and algorithm details.

=== "Practitioners" 
    Jump to [Examples](examples/index.md) for real-world use cases and method comparisons.

=== "Developers"
    Check the [API Reference](api/index.md) for detailed class and method documentation.

## Acknowledgements

This library is inspired by and validated against the R package [onlineFDR](https://dsrobertson.github.io/onlineFDR/).

**Key differentiator**: Our implementation provides a truly online API with `test_one()` method calls, enabling real-time sequential applications. The R package requires pre-collected data arrays.

## Support

-  **Documentation**: Comprehensive guides and API reference
-  **Issues**: Report bugs on [GitHub Issues](https://github.com/OliverHennhoefer/online-fdr/issues)  
-  **Discussions**: Ask questions in [GitHub Discussions](https://github.com/OliverHennhoefer/online-fdr/discussions)
-  **Contact**: Reach out to the maintainers for collaboration opportunities

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](https://github.com/OliverHennhoefer/online-fdr/blob/main/LICENSE) file for details.
