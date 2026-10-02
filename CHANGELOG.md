# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

- Replaced repeated history scans in asynchronous SAFFRON and ADDIS with
  incremental prefix counts, preserving assigned levels, decisions, and
  schema-1 snapshots. Records still require linear memory, and threshold
  calculations still sum contributions from past discoveries.
- Added exact async reference regressions, deterministic scalability checks,
  and a standalone comparison benchmark in `benchmarks/async_scaling.py`.
- Unified execution state and detailed decision records across p-value and
  e-value methods while retaining existing evidence keyword arguments.
- Made detailed batch calls preserve the same input validation and state
  updates as boolean batch calls.
- Fixed JSON snapshots for NumPy scalar state and rejected unsupported helper
  subclasses instead of silently restoring a different algorithm.
- Preserved restoration of existing schema-1 e-LOND snapshots.
- Aligned public protocols with read-only method state and added consumer
  type-check regressions.
- Shared the stabilized live R parity setup between CI and release, including
  the pinned Bioconductor installation used by container parity checks.

## [1.0.0] - 2026-06-08

- Promoted package metadata to the stable `1.0.0` release line.
- Added a focused release workflow for building distributions and publishing
  tagged releases to PyPI through trusted publishing.
- Split R-backed parity tooling into an explicit dependency group so routine
  Python checks can run without a local R installation.
- Added release-process documentation, citation metadata, and dependency update
  automation for GitHub Actions and `uv`.
- Updated contributor, installation, and documentation pages to match the Ruff
  based toolchain and the dedicated Bioconductor parity workflow.

## [0.1.0] - 2026-03-02

- Introduced strict shared validation for batch p-values and LORD-family preconditions.
- Standardized empty-batch semantics to a documented no-op (`test_batch([]) -> []`) with no state mutation.
- Enforced finite-horizon errors in alpha spending rules instead of leaking index errors.
- Hardened gamma-sequence invariants (`DefaultSaffronGammaSequence` now requires finite `c` and `gamma_exp > 1`).
- Aligned dependent LORD sequence scaling with the supported `onlineFDR`-compatible regime.
- Refactored SAFFRON/ADDIS candidate accounting with prefix counts to remove repeated suffix scans.
- Added high-value test coverage for input validation, no-op behavior, sequence invariants, and statistical sanity checks.
- Added optional R parity check for dependent LORD and cleaned parity skip behavior.
- Added guarantee matrix docs and replaced stale guarantees links.
- CI now includes strict docs build and package build + wheel smoke import checks.
- Packaging now exposes optional extras for docs/parity and no longer includes `tests/**/*.py` in build includes.

### Migration Notes

- Constructors now fail fast for invalid parameter tuples that were previously accepted.
- `LordPlusPlus` now enforces the guaranteed payout regime (`reward == alpha`) in strict mode.
- Finite-horizon spending functions now raise a user-facing `ValueError` when the configured horizon is exceeded.

## [0.0.3] - 2026-03-02

- Fixed static BH/BY/Storey-BH step-up logic with full scan semantics.
- Aligned Alpha-spending and online-fallback rejection boundary to `<=`.
- Added ADDIS parameter validation (`0 < tau < 1`, `0 <= lambda_ < tau`).
- Corrected D-LORD first-rejection state transition.
- Corrected BatchStoreyBH `R+` computation to same-size replacement semantics.
- Added parity regression tests, parity profile artifacts, docs import smoke tests.
- Added CI workflow for `ruff`, `mypy`, and `pytest`.
