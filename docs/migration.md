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
`LordPlusPlus` requires `reward == alpha`. `LordDependent` also requires
`wealth <= reward`, and `LordDiscard` requires `wealth <= tau * alpha`.
LORD rewards must be finite and positive. SAFFRON gamma sequences require
finite nonnegative `c` and finite `gamma_exp > 1`; normalization of a custom
sequence remains the caller's responsibility. Batch p-values receive shared strict validation.
An empty batch is a no-op, and exceeding a finite spending horizon raises a
user-facing `ValueError`.

Weighted GAI++ requires finite positive numeric `prior_weight` and `penalty_weight`
values (excluding booleans) and a positive integer `gamma_horizon`. It processes
exactly that many tests; the next call raises before changing wealth, counters,
or history.
The prior-weight cap now enforces the paper's nonnegative reward bounds.
Penalty weights that cannot support a nonnegative reward raise `ValueError`
before changing state. `error_rate` now reports `"weighted FDR"` or
`"weighted mem-FDR"` according to the configured decay. These describe
penalty-weighted error ratios; ordinary FDR requires unit penalty weights
and no decay, under the documented independence assumptions.
Invalid p-values passed to an asynchronous method's synchronous `test_one`
convenience call leave the testing state unchanged.

Finite spending horizons and Gaussian e-value generator dimensions/batch sizes
must be positive integers; booleans and fractional values are rejected.
An invalid requested batch size leaves the generator's cursor unchanged.

TOAD arrivals advance from the current stage, including after `advance_to`;
finalized decisions remain final. Its identity-shape guarantee requires
conditional positive dependence and appropriately prespecified or predictable
weights, as detailed in the guarantee matrix.

`BatchBHOfficial` retains one gamma profile for the whole stream. Automatic
selection uses the first nonempty batch. Later changes in batch size do not
recalculate historical allocations. Pass `gamma_profile="poly"` or
`gamma_profile="half"` to choose explicitly; the read-only `gamma_profile`
property reports the selected profile, or `None` before automatic selection.

Likelihood-ratio mixtures own a fixed prior. The `weights` property returns a
copy; construct a new process to choose a different prior. Products containing
both zero and infinity raise `ValueError` instead of depending on input order.
Likelihood-ratio updates also reject undefined cumulative log capital without
committing a partial component update. This protects the process's internal
capital; caller-supplied functions remain responsible for their own side effects.

## State Names

New code should use:

- `target_level` for the configured error-control level
- `error_rate` for the controlled error-rate family (`FDR`, `mFDR`, `FWER`,
  `weighted FDR`, or `weighted mem-FDR`)
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
Weighted GAI++ restores historical levels and weights as recorded, while future
calls use the corrected prior cap and updated error-target metadata. Restoring
a snapshot cannot repair invalid past statistical decisions.

Legacy `BatchBHOfficial` snapshots infer their fixed profile from the first
recorded allocation. Snapshots with negative or nonfinite past levels, or
accounting that exceeds the inferred fixed gamma budget, are rejected.
Older snapshots do not store historical batch sizes, so restoration
cannot establish the validity of past mixed-profile allocations; it preserves
those decisions and fixes the profile for future batches.

The built-in gamma sequences and spending functions have explicit snapshot
codecs. Custom helpers, including subclasses of those built-ins, raise
`TypeError` when taking a snapshot; they are never silently restored as a
different helper implementation.

## Memory-Decay Evaluation

`MemoryDecayFDR` uses running discounted counts, so a scalar `score_one` call
takes constant time. Requesting cumulative output copies the full score history.
`delta` and `offset` are fixed after construction; `labels` and `ground_truth`
return detached lists. Construct a new tracker to change its configuration.
The writable `cumulative` flag can still switch between scalar and historical
outputs at any point. Configuration requires finite `delta` in `[0, 1]` and
finite nonnegative `offset`. Floating-point summation order can differ from
the previous convolution implementation by roundoff.
