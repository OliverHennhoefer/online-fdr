# Changelog

All notable changes to this project are documented in this file.

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
