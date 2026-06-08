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

## Installation

```bash
pip install online-fdr
```

For development:

```bash
git clone https://github.com/OliverHennhoefer/online-fdr.git
cd online-fdr
uv sync --group dev
```

Live parity tests also need R `4.5.x`, Bioconductor `onlineFDR==2.18.0`, and
the `parity` dependency group; see `docs/installation.md` and
`tests/reference/README.md`.

## P-values

Sequential p-value methods make one decision per incoming p-value.

```python
from online_fdr.p_values import Addis

p_values = [0.20, 0.004, 0.32, 0.018, 0.60, 0.0007]
method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

decisions = [method.test_one(p_value) for p_value in p_values]

print("ADDIS sequential p-value test")
print(f"Tests processed: {method.num_tests}")
print(f"Discoveries: {sum(decisions)}")
print(f"Decisions: {decisions}")
```

Batch methods test a group of p-values at once.

```python
from online_fdr.p_values import BatchStoreyBH

p_values = [0.001, 0.012, 0.20, 0.40, 0.006, 0.70]
method = BatchStoreyBH(alpha=0.10, lambda_=0.5)

decisions = method.test_batch(p_values)

print("Batch Storey-BH p-value test")
print(f"Batch threshold: {method.current_threshold:.6f}")
print(f"Discoveries: {sum(decisions)} of {len(decisions)}")
print(f"Decisions: {decisions}")
```

## E-values

E-value methods use evidence values where larger values are stronger evidence
against the null.

```python
from online_fdr.e_values import EBH, ELond

batch = EBH(alpha=0.10)
e_values = [1.0, 4.0, 80.0, 12.0, 0.5, 25.0]
batch_decisions = batch.test_batch(e_values)

stream = ELond(alpha=0.10)
stream_decisions = [stream.test_one(e_value) for e_value in [250.0, 40.0, 500.0]]

print("e-BH batch test")
print(f"Discoveries: {sum(batch_decisions)} of {len(batch_decisions)}")
print(f"Decisions: {batch_decisions}")
print("")
print("e-LOND sequential test")
print(f"Tests processed: {stream.num_tests}")
print(f"Discoveries: {sum(stream_decisions)}")
print(f"Decisions: {stream_decisions}")
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

## Examples

The `examples/` notebooks are short demonstrations of individual procedures:

- `examples/addis.ipynb`
- `examples/alpha_spend.ipynb`
- `examples/batch_storey_bh.ipynb`
- `examples/e_value.ipynb`
- `examples/lord_mem_decay.ipynb`
- `examples/naive.ipynb`
- `examples/weight_decay.ipynb`

## Guarantees and parity

Statistical guarantees are method-specific and depend on the assumptions of the
underlying procedure. The guarantee matrix in `docs/theory/guarantee_matrix.md`
summarizes which methods are proven, parity-tested against Bioconductor
`onlineFDR`, or implemented as package extensions.

The live parity suite compares overlapping p-value methods against
Bioconductor `onlineFDR==2.18.0` through `rpy2`. CI runs this suite with the
pinned R package; local setup instructions are in `tests/reference/README.md`.

## Documentation

- Installation: `docs/installation.md`
- User guide: `docs/user_guide/index.md`
- API reference: `docs/api/index.md`
- Theory and guarantees: `docs/theory/index.md`
- Release process: `docs/release.md`

## License

This project is licensed under the BSD 3-Clause License. See `LICENSE` for
details.
