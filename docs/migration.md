# Migration To Package Surfaces

`online-fdr` exposes p-value and e-value methods through separate package
surfaces:

- `online_fdr.p_values` for p-value procedures
- `online_fdr.e_values` for e-value procedures

The root package no longer re-exports every method.

## Import Changes

```python
# Before:
# from online_fdr.investing.addis.addis import Addis
# from online_fdr.batching.bh import BatchBH
# from online_fdr.utils.generation import DataGenerator

# Now
from online_fdr.p_values import Addis
from online_fdr.p_values import BatchBH
from online_fdr.core.utils import DataGenerator
```

For common p-value methods, prefer package-level imports:

```python
from online_fdr.p_values import Addis, BatchBH, Saffron
```

For e-value methods:

```python
from online_fdr.e_values import EBH, ELond
```

## State Names

New code should use:

- `target_level` for the configured error-control level
- `error_rate` for the controlled error-rate family (`FDR`, `mFDR`, or `FWER`)
- `last_test_level` for the last method-specific test level
- `last_rejection_threshold` for the last input-scale rejection boundary
- `num_hypotheses` for processed hypotheses
- `num_batches` for processed non-empty batches where applicable

Use `test_one_detail(...)` and `test_batch_detail(...)` when downstream audit
logs need thresholds, indices, or metadata in addition to boolean decisions.
