# Local Workflows

This page provides practical local workflows for development and validation.

## Setup

Install dependencies:

```bash
uv sync --group dev
```

## Standard Quality Workflow

Run the same core checks used during development:

```bash
uv run python -m ruff check .
uv run python -m ruff format --check online_fdr tests
uv run python -m mypy online_fdr
uv run python -m pytest -q
```

## Focused Test Runs

Run only the new API contract checks:

```bash
uv run python -m pytest tests/test_public_api_surface.py tests/test_import_smoke.py -q
```

Run a single module:

```bash
uv run python -m pytest tests/test_static.py -q
```

## Working with R Parity Tests

Parity tests depend on a working R + `rpy2` setup and pinned Bioconductor
`onlineFDR` package.

Install parity dependencies:

```bash
uv sync --group dev --group parity
```

Run parity tests directly:

```bash
uv run python -m pytest -m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
```

The pinned `onlineFDR==2.18.0` implementation [stores async ADDIS discovery
positions as booleans](https://github.com/bioconductor-source/onlineFDR/blob/RELEASE_3_22/src/addis.cpp#L154),
collapsing start indices above 1. The repeated 20-block case directly checks
decision equality, the matching threshold prefix, and the known stage-9
difference. An independent frozen-reference regression requires exact
preservation of prior Python behavior. Supported 20-block live R comparisons
keep pending tests selected and discoveries at positions 0 and/or 1, covering
both single and multiple discoveries. The scalability optimization preserves
the prior Python accounting.

If parity setup is not available yet, run the standard suite:

```bash
uv run python -m pytest -q
```

## Async Scalability Benchmark

Compare asynchronous SAFFRON and ADDIS with the frozen scan-based reference:

```bash
uv run python benchmarks/async_scaling.py
```

The benchmark reports median times over five fresh instances for no-discovery,
candidate-heavy, mixed, and discovery-heavy streams. Reference runs stop at 800
tests; optimized no-discovery runs extend through 10,000 tests. The default run
takes several minutes because the reference implementation repeatedly scans
history. For a shorter check of the original SAFFRON bottleneck:

```bash
uv run python benchmarks/async_scaling.py --methods saffron --scenarios no-discovery --sizes 800
```

Timing results are descriptive. CI uses deterministic record-inspection tests
to detect repeated history scans without imposing machine-specific time limits.
The optimized methods retain all records and still sum past discovery
contributions when assigning a new level, so memory grows with the number of
tests and discovery-heavy streams require more work.

## Packaging Smoke

Build artifacts and verify package metadata locally:

```bash
uv run python -m build
```

## Release Smoke

Run the package build, wheel install, and import smoke check used by release CI:

```bash
uv run python -m build
uv venv .smoke --python 3.12
uv pip install --python .smoke/bin/python dist/*.whl
.smoke/bin/python -c "import online_fdr; print(online_fdr.__version__)"
```

## Documentation Workflow

Serve docs locally:

```bash
uv run mkdocs serve
```

Build strict docs:

```bash
uv run mkdocs build --strict
```
