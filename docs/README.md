# Documentation

The documentation site is built with Material for MkDocs from the repository
root.

## Local Build

```bash
uv sync --group docs
uv run mkdocs build --strict
uv run mkdocs serve
```

The generated site is written to `site/`, which is intentionally ignored by
Git.

## Structure

- `index.md`: documentation home page
- `installation.md`: installation and optional parity setup
- `quickstart.md`: first package walkthrough
- `workflows.md`: local validation commands
- `release.md`: release checklist and PyPI publishing notes
- `user_guide/`: user-facing concepts and workflows
- `examples/`: narrative examples
- `api/`: API reference pages
- `theory/`: assumptions, algorithms, and guarantees

## Deployment

`.github/workflows/docs.yml` builds the site with `mkdocs build --strict` and
deploys it to GitHub Pages on documentation changes to `main`.
