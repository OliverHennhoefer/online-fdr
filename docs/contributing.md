# Contributing

Contributions are welcome for algorithms, tests, documentation, examples, and
release maintenance. Keep changes scoped, cite method references, and update
tests and docs when behavior changes.

## Development Setup

Install the routine development tools:

```bash
git clone https://github.com/OliverHennhoefer/online-fdr.git
cd online-fdr
uv sync --group dev
```

This installs Python test, lint, type-check, and package-build tooling. It does
not install the R bridge used by live parity tests.

## Routine Checks

Run these before opening a pull request:

```bash
uv run python -m ruff check .
uv run python -m ruff format --check online_fdr tests
uv run python -m mypy online_fdr
uv run python -m pytest -q
```

Run focused tests while developing:

```bash
uv run python -m pytest tests/test_public_api_surface.py tests/test_import_smoke.py -q
uv run python -m pytest tests/test_static.py -q
```

## Live R Parity

The live parity suite compares overlapping p-value methods against
Bioconductor `onlineFDR` (`2.18.0`, Bioconductor `3.22`) through `rpy2`.
Use it for changes to parity-covered methods, async lifecycles, validation, or
state accounting.

Install R `4.5.x`, then install the parity Python group and pinned R package:

```bash
uv sync --group dev --group parity
Rscript -e "options(repos = c(CRAN = 'https://cloud.r-project.org')); if (!requireNamespace('BiocManager', quietly = TRUE)) install.packages('BiocManager')"
Rscript -e "BiocManager::install(version = '3.22', ask = FALSE, update = FALSE)"
Rscript -e "BiocManager::install('onlineFDR', version = '3.22', ask = FALSE, update = FALSE)"
Rscript -e "stopifnot(as.character(utils::packageVersion('onlineFDR')) == '2.18.0')"
```

Run the parity tests:

```bash
uv run python -m pytest -m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
```

If Bioconductor reports that version `3.22` requires R `4.5`, upgrade R and
rerun the `Rscript` commands.

## Implementation Standards

- Prefer existing public interfaces and helper functions over new abstractions.
- Validate p-values, e-values, alphas, horizons, and method-specific parameters
  at the boundary.
- Keep state names consistent with the package interface: `target_level`,
  `error_rate`, `last_test_level`, `last_rejection_threshold`,
  `num_hypotheses`, and `num_batches` where available.
- For new methods, cite the paper and inspect an author or reputable reference
  implementation before coding.
- Add focused tests for input validation, boundary behavior, state accounting,
  and any parity claim.
- Update API docs, the guarantee matrix, and the changelog for user-visible
  behavior changes.

## Documentation

Build docs locally with:

```bash
uv sync --group docs
uv run mkdocs build --strict
uv run mkdocs serve
```

Documentation examples should use public imports, avoid path manipulation, and
keep output concise enough to render well on GitHub and the docs site.

## Pull Requests

- Describe what changed and why.
- Include the commands you ran.
- Keep statistical claims tied to documented assumptions.
- Mention whether live R parity was run or why it was not needed.
- Add a `CHANGELOG.md` entry for public-facing changes.

## Releases

Release mechanics are documented in [Release Process](release.md). In short,
the release tag should match the package version, CI must be green, and PyPI
publishing uses the `pypi` GitHub environment with trusted publishing.
