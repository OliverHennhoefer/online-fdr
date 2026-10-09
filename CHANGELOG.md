# Changelog

All notable changes to this project are documented in this file.
Release entries describe PyPI publications; the previously unpublished
repository milestones are consolidated into the first stable release below.

## [Unreleased]

## [1.0.0] - 2026-10-09

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
- BatchStoreyBH computes `R+` with same-size replacement semantics.
- JSON snapshots preserve NumPy scalar state and helper identity; existing
  schema-1 e-LOND snapshots remain restorable.
- Invalid synchronous calls to asynchronous methods no longer allocate tests;
  failed starts preserve automatic IDs, which skip explicit IDs already in use.
- Weighted GAI++ validates finite positive weights before state changes, permits
  every test through its configured horizon, and raises before changing state
  when the horizon is exhausted. Earlier schema-1 snapshots remain restorable.
- Likelihood-ratio mixtures commit component capitals together after successful
  evaluation. E-value means and mixtures share overflow-safe log-weight
  normalization; zero-weight infinite evidence is ignored, while positive
  weights remain active even when ordinary-scale normalization would underflow.
- Typed snapshot restoration preserves concrete method types, and weighted
  detailed calls expose explicit weight arguments instead of arbitrary `Any`
  arguments.

### Performance

- Asynchronous SAFFRON and ADDIS use incremental prefix counts instead of
  repeated history scans, preserving assigned levels, decisions, and schema-1
  snapshots. Records still require linear memory, and threshold calculations
  still sum contributions from past discoveries.

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
