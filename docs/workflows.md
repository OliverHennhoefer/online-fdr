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

If parity setup is not available yet, run the standard suite:

```bash
uv run python -m pytest -q
```

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
