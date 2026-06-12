# Release Process

This project uses semantic versioning and publishes Python distributions from
tagged releases.

## Release Readiness

Before tagging a release:

1. Update `pyproject.toml`, `online_fdr/__init__.py`, `uv.lock`,
   `CHANGELOG.md`, and `CITATION.cff` to the release version.
2. Run the routine local checks:

   ```bash
   uv run python -m ruff check .
   uv run python -m ruff format --check online_fdr tests
   uv run python -m mypy online_fdr
   uv run python -m pytest -q
   uv run python -m build
   ```

3. Run live parity for changes that touch parity-covered behavior:

   ```bash
   uv sync --group dev --group parity
   uv run python -m pytest -m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py -q
   ```

4. Build documentation strictly:

   ```bash
   uv run mkdocs build --strict
   ```

## PyPI Trusted Publishing

The release workflow expects a PyPI trusted publisher instead of an API token.
Configure PyPI with:

- repository: `OliverHennhoefer/online-fdr`
- workflow: `release.yml`
- environment: `pypi`

In GitHub, create the `pypi` environment and require reviewer approval if you
want a manual approval gate before publishing.

## Tagging

Release tags use `vMAJOR.MINOR.PATCH`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Pushing a version tag runs `.github/workflows/release.yml`, which reruns lint,
format, type-check, non-parity tests, strict docs build, live R parity, package
build, and wheel smoke install. It uploads the distributions as a workflow
artifact and publishes to PyPI only after the validation jobs and the `pypi`
environment gate pass.

Manual `workflow_dispatch` runs build the distributions but do not publish to
PyPI unless the run is associated with a version tag.

## After Release

- Confirm the PyPI project page shows the new version.
- Confirm the GitHub Pages workflow is green.
- Add a GitHub release entry summarizing the `CHANGELOG.md` notes.
