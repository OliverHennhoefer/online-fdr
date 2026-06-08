# Contributing to online-fdr

Thanks for contributing. This repository accepts improvements to algorithms,
tests, documentation, and examples.

## Start Here

Use the full contributor guide:

- [Developer contribution guide](docs/contributing.md)

That guide includes:

- local environment setup with `uv`
- testing, linting, and typing commands
- method implementation and documentation standards

## Quick Commands

```bash
uv sync --group dev
uv run python -m pytest -q --ignore=tests/test_onlinefdr_parity.py --ignore=tests/test_async_methods.py
uv run python -m ruff check .
uv run python -m ruff format --check online_fdr tests
uv run python -m mypy online_fdr
```

## Project Policies

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

## Pull Requests

- Keep changes scoped and well-tested.
- Update docs for user-visible behavior changes.
- Add or update tests for bug fixes and features.
- Document public-facing changes in `CHANGELOG.md`.
