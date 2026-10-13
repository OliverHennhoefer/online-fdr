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

The release workflow uses PyPI Trusted Publishing with short-lived credentials.
In PyPI, open **online-fdr → Manage → Publishing**, select **GitHub Actions**,
and enter these exact values:

| PyPI field | Value |
| --- | --- |
| Owner | `OliverHennhoefer` |
| Repository name | `online-fdr` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

Enter the workflow filename alone, without `.github/workflows/`. No PyPI API
token or GitHub secret is needed. The workflow uses the GitHub environment
`pypi`; configure required reviewers there if you want an additional approval
step before publishing.

## Tagging

Release tags use `vMAJOR.MINOR.PATCH`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Pushing a version tag runs `.github/workflows/release.yml`, which first checks
that the tag matches both the distribution and package version, then reruns lint,
format, type-check, non-parity tests, strict docs build, live R parity, package
build, and wheel smoke install. It uploads the distributions as a workflow
artifact and publishes to PyPI only after the validation jobs and the `pypi`
environment gate pass.

Use **Actions → Release → Run workflow** on a branch to validate the process
before tagging. Manual `workflow_dispatch` runs on branches validate and build
the distributions. Publishing requires a matching version tag.

## After Release

- Confirm the PyPI project page shows the new version.
- Confirm the GitHub Pages workflow is green.
- Add a GitHub release entry summarizing the `CHANGELOG.md` notes.
