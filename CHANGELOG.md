# Changelog

All notable changes to this project are documented in this file.
Release entries describe PyPI publications; the previously unpublished
repository milestones are consolidated into the first stable release below.

## [Unreleased]

### Changed

- `BatchBY` computes its augmented rejection count with one step-up pass
  instead of one pass per p-value, and `Gai` no longer rescans its candidate
  history on every test. Decisions and test levels are unchanged.
- Validation errors for p-values, alpha, wealth, the candidate threshold, and
  the decay factor are single-line messages without padding whitespace.
- P-values, e-values, weights, and the LOND `alpha` accept any real scalar,
  including NumPy scalars such as `np.float32`, and refuse booleans.
- `BatchStoreyBH` computes its augmented rejection count from two candidate
  replacements instead of one per p-value, and dependent `Lond` extends a
  running harmonic sum instead of recomputing it on every test. Decisions
  and test levels are unchanged.
- `LORDMemoryDecay` stops visiting rejections whose decay weight has reached
  exactly zero, keeps its gamma cache bounded and out of snapshots, and
  validates `l`. Test levels are unchanged.
- The Gaussian and chi-squared data generators compute p-values with the
  survival function, so very strong signals no longer round to exactly zero.
  Generated p-values differ from earlier versions in their last digits.
- `DependentGaussianModel` builds its autoregressive correlation matrix
  without a Python loop over all pairs.
- `BatchGammaSequenceSmall` validates `gamma_exp` when it is created and
  reuses its normalizer per batch size.
- `ELond` no longer swallows a `TypeError` raised inside a gamma sequence.
  `DefaultSaffronGammaSequence.calc_gamma` accepts keyword arguments like the
  other sequences.
- Docstring examples run as part of the test suite.

### Removed

- `BatchGammaSequenceLarge`, which duplicated `BatchBHHalfGammaSequence`.
- `LordPlusPlus.wealth_at_first_reject` and `LordDependent.last_reject`,
  which were written and never read. Snapshots no longer contain them.
- `online_fdr.core.utils.testing` and `online_fdr.core.utils.format`. Their
  helpers were unused by the package; the one a test needed now lives with
  that test.
- The `docs` extra. The documentation toolchain is the `docs` dependency
  group, which is what the workflows install.

### Fixed

- The "block" structure of `DependentGaussianModel` left a trailing partial
  block uncorrelated.
- Docstring examples for `Addis`, `Saffron`, `LordThree`, `Lond`, and
  `OnlineFallback` now state the decisions the methods actually return.
- The ADDIS parameter-sensitivity example in the evaluation guide no longer
  sweeps `lambda_` values at or above `tau`.

## [1.0.0] - 2026-10-19

### Added

- Separate `online_fdr.p_values` and `online_fdr.e_values` package surfaces,
  with common protocols, results, and utilities under `online_fdr.core`.
- First-class e-value support: e-BH, e-LOND, p-to-e calibration, e-to-p
  conversion, e-value merging, and likelihood-ratio and betting e-processes.
- Asynchronous SAFFRON and ADDIS lifecycle APIs, weighted GAI++, TOAD, and
  the original Batch-BH implementation.
- Public method state, detailed decision records through `test_one_detail`
  and `test_batch_detail`, JSON-compatible snapshots, and a typed package
  marker for consumers.

### Changed

- Require Python 3.10 or higher, compared with Python 3.8 in 0.0.3.
- Move legacy p-value imports to `online_fdr.p_values` and common helpers to
  `online_fdr.core`; the root package no longer re-exports every method.
- Reject invalid constructor parameters and batch inputs consistently.
  LORD++ requires `reward == alpha`; SAFFRON gamma sequences require finite
  `c` and `gamma_exp > 1`. Empty batches are a no-op, and exceeding a finite
  spending horizon raises `ValueError`.
- Unify execution state across p-value and e-value methods. Detailed calls
  preserve the same validation and state updates as boolean calls, including
  the existing e-value keyword arguments.
- Keep snapshot payloads detached from running state. Unsupported custom
  helpers and helper subclasses raise `TypeError` instead of restoring a
  different algorithm.
- Keep runtime dependencies limited to NumPy and SciPy; documentation and
  live R parity tooling have separate dependency groups.
- Likelihood-ratio mixture priors are fixed and returned as detached weight
  lists. Undefined zero-times-infinity products raise `ValueError` regardless
  of input order, and undefined cumulative likelihood ratios leave capital
  unchanged.

### Fixed

- Static BH, BY, and Storey-BH step-up logic now uses full scan semantics.
- Alpha-spending and online-fallback rejection boundaries use `<=`.
- ADDIS validates `0 < tau < 1` and `0 <= lambda_ < tau`.
- Correct dependent LORD sequence scaling and its first-rejection state
  transition to the supported `onlineFDR` reference regime.
- Enforce `wealth <= reward` for dependent LORD and `wealth <= tau * alpha`
  for discarding LORD. Reject nonfinite LORD rewards, nonfinite SAFFRON gamma
  parameters, and noninteger finite spending horizons.
- Evaluate SAFFRON gamma values in log space when a finite exponent overflows
  the power denominator, preserving finite results and valid zero limits.
- BatchStoreyBH computes `R+` with same-size replacement semantics.
- JSON snapshots preserve NumPy scalar state and helper identity; existing
  schema-1 e-LOND snapshots remain restorable.
- Invalid synchronous calls to asynchronous methods no longer allocate tests;
  failed starts preserve automatic IDs, which skip explicit IDs already in use.
- Weighted GAI++ validates finite positive weights before state changes, permits
  every test through its configured horizon, and raises before changing state
  when the horizon is exhausted. Earlier schema-1 snapshots remain restorable.
- Correct weighted GAI++'s prior cap to satisfy both nonnegative reward bounds;
  infeasible penalty weights fail before a state transition. Public metadata
  and documentation describe penalty-weighted FDR and decaying-memory FDR.
- TOAD arrivals preserve a monotone stage clock and finalized decisions after
  explicit advancement. Document conditional positive dependence for its
  implemented identity shape. Streaming deadlines and stages must be integers
  (NumPy integers included), and weights must lie in `(0, 1]`.
- Keep BatchBHOfficial's gamma profile fixed across changing batch sizes,
  preventing retrospective allocations. Clamp floating-point cancellation at
  an exhausted budget to zero instead of emitting negative test levels.
- Gaussian e-value generators reject invalid dimensions and batch sizes before
  changing their cursor. Power calibration handles an overflowing intermediate
  even when the complete e-value remains finite.
- Execute representative SAFFRON documentation examples during tests and fix
  the parameter-selection example's invalid initial wealth.
- Likelihood-ratio mixtures commit component capitals together after successful
  evaluation. E-value means and mixtures share overflow-safe log-weight
  normalization; zero-weight infinite evidence is ignored, while positive
  weights remain active even when ordinary-scale normalization would underflow.
- Typed snapshot restoration preserves concrete method types, and weighted
  detailed calls expose explicit weight arguments instead of arbitrary `Any`
  arguments.
- Accept NumPy integer horizons and generator sizes, and NumPy real scalar
  configuration values, while continuing to reject booleans. Normalize these
  inputs to Python numbers before storing execution state.
- The p-value `DataGenerator.sample_batch` rejects nonpositive or fractional
  sizes before moving its cursor.

### Performance

- Asynchronous SAFFRON and ADDIS use incremental prefix counts instead of
  repeated history scans, preserving assigned levels, decisions, and schema-1
  snapshots. Records still require linear memory, and threshold calculations
  still sum contributions from past discoveries.
- Memory-decay FDR evaluation maintains discounted counts incrementally instead
  of recomputing full convolutions. Scalar updates take constant time; tracker
  configuration is fixed and observation histories are returned as detached lists.
- BatchBH and BatchBHOfficial compute `R+` with one largest-value replacement
  instead of rerunning BH for every hypothesis. Decisions and snapshots are
  preserved, while per-batch sorting work drops from quadratic to `O(n log n)`.

### Migration

See the [1.0 migration guide](docs/migration.md) for Python requirements,
replacement imports, stricter validation, public state, and snapshot support.
Method-specific assumptions and live R parity coverage remain documented in
the [guarantee matrix](docs/theory/guarantee_matrix.md).

## [0.0.3] - 2025-07-03

- Last published legacy p-value release before the stable 1.0 line.
- Supported Python 3.8 and higher with NumPy and SciPy runtime dependencies.

[Unreleased]: https://github.com/OliverHennhoefer/online-fdr/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/OliverHennhoefer/online-fdr/compare/ce4308958088d0061ccafdc42a15ac91231c5b64...v1.0.0
[0.0.3]: https://pypi.org/project/online-fdr/0.0.3/
