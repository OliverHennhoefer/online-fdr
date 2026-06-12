## Summary

Describe the change and why it is needed.

## Changes

- ...

## Validation

Commands run locally:

```bash
uv run python -m pytest -q
uv run python -m ruff check .
uv run python -m ruff format --check online_fdr tests
uv run python -m mypy online_fdr
```

If your change touches parity behavior, include:

```bash
uv run python -m pytest -m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
```

## Checklist

- [ ] Tests added or updated for behavior changes
- [ ] Docs updated for user-visible changes
- [ ] Public API changes reflected in docs/changelog
- [ ] Workflow or release-process changes are intentional and documented
