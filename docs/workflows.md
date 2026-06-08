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

Run parity tests directly:

```bash
uv run python -m pytest tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
```

If parity setup is not available yet, run a local non-parity subset:

```bash
uv run python -m pytest -q --ignore=tests/test_onlinefdr_parity.py --ignore=tests/test_async_methods.py
```

## Packaging Smoke

Build artifacts and verify package metadata locally:

```bash
uv run python -m build
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
