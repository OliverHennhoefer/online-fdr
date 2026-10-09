# Migration to 1.0.0

This guide covers migration from the last published PyPI version, 0.0.3, to
the first stable release, 1.0.0.

## Python Requirement

Version 1.0.0 requires Python 3.10 or higher. Version 0.0.3 supported Python
3.8 and higher; upgrade the interpreter before installing 1.0.0.

## Package Surfaces

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

## Validation Changes

Constructors reject invalid parameter tuples that older versions accepted.
`LordPlusPlus` requires `reward == alpha`, and SAFFRON gamma sequences require
finite `c` and `gamma_exp > 1`. Batch p-values receive shared strict validation.
An empty batch is a no-op, and exceeding a finite spending horizon raises a
user-facing `ValueError`.

Weighted GAI++ requires finite positive `prior_weight` and `penalty_weight`
values and a positive integer `gamma_horizon`. It processes exactly that many
tests; the next call raises before changing wealth, counters, or history.
Invalid p-values passed to an asynchronous method's synchronous `test_one`
convenience call leave the testing state unchanged.

Likelihood-ratio mixtures own a fixed prior. The `weights` property returns a
copy; construct a new process to choose a different prior. Products containing
both zero and infinity raise `ValueError` instead of depending on input order.
Likelihood-ratio updates also reject undefined cumulative log capital without
committing a partial component update. This protects the process's internal
capital; caller-supplied functions remain responsible for their own side effects.

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

Detailed calls execute the same validation and state updates as boolean calls.
Requesting a record does not make numeric strings valid input. E-value methods
continue to accept `e_value=` and `e_values=` keyword arguments.

## Persisting Method State

Use `snapshot()` to obtain an opaque JSON-compatible payload, then restore it
with the same method's `from_snapshot(...)` class method. Snapshot state is
detached from the running method and supports NumPy scalar values produced by
array-based streams. Existing schema-1 e-LOND and weighted GAI++ snapshots remain
restorable, including snapshots containing a prefetched next test level.

The built-in gamma sequences and spending functions have explicit snapshot
codecs. Custom helpers, including subclasses of those built-ins, raise
`TypeError` when taking a snapshot; they are never silently restored as a
different helper implementation.
