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
from online_fdr.p_values.investing.addis.addis import Addis
from online_fdr.p_values.batching.bh import BatchBH
from online_fdr.core.utils.generation import DataGenerator
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

- `target_fdr` for the configured FDR level
- `current_threshold` for the current rejection boundary
- `num_tests` for processed tests

Moved p-value methods still expose `alpha` and `num_test` internally for
algorithm compatibility, but new code should not rely on those names.
