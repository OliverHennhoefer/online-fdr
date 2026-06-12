# Online FDR: Online False Discovery Rate Control Algorithms

[![python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![CI](https://github.com/OliverHennhoefer/online-fdr/actions/workflows/ci.yml/badge.svg)](https://github.com/OliverHennhoefer/online-fdr/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/online-fdr.svg)](https://pypi.org/project/online-fdr/)

`online-fdr` is a Python package for multiple testing when hypotheses arrive
over time or in batches. It provides p-value and e-value procedures for false
discovery rate (FDR) and family-wise error rate (FWER) control.

The package focuses on small stateful objects:

- sequential methods use `test_one(...)`
- batch methods use `test_batch(...)`
- method state exposes the target level, current threshold, and number of
  processed tests where applicable

## Install

```bash
pip install online-fdr
```

For development:

```bash
git clone https://github.com/OliverHennhoefer/online-fdr.git
cd online-fdr
uv sync --group dev
```

Live parity tests additionally require R `4.5.x`, Bioconductor
`onlineFDR==2.18.0`, and `uv sync --group dev --group parity`.

## Minimal Example

```python
from online_fdr.p_values import Addis

p_values = [0.20, 0.004, 0.32, 0.018, 0.60, 0.0007]
method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

decisions = [method.test_one(p_value) for p_value in p_values]

print(f"Tests processed: {method.num_hypotheses}")
print(f"Discoveries: {sum(decisions)}")
print(f"Decisions: {decisions}")
```

## Methods

P-value procedures:

- sequential: ADDIS, SAFFRON, GAI, weighted GAI++, LOND, LORD variants,
  alpha-spending, online fallback, and a naive baseline
- asynchronous: ADDIS and SAFFRON lifecycle APIs
- batch: BatchBH, BatchStoreyBH, BatchPRDS, BatchBY, BatchBHOfficial, and TOAD

E-value procedures and tools:

- e-BH and e-LOND
- p-to-e calibration, e-to-p conversion, e-value merging
- likelihood-ratio and betting e-process helpers

## Project Guarantees

Statistical guarantees are method-specific and depend on the assumptions of the
underlying procedure. The [guarantee matrix](theory/guarantee_matrix.md)
summarizes which methods are proven, parity-tested against Bioconductor
`onlineFDR`, or implemented as package extensions.

The live parity suite compares overlapping p-value methods against
Bioconductor `onlineFDR==2.18.0` through `rpy2`.

## Next Steps

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [User Guide](user_guide/index.md)
- [API Reference](api/index.md)
- [Theory and Guarantees](theory/index.md)
- [Release Process](release.md)
