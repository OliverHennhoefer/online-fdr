from __future__ import annotations

from pathlib import Path

import online_fdr

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_release_version_metadata_is_consistent() -> None:
    project = tomllib.loads(_read("pyproject.toml"))["project"]
    version = project["version"]

    assert version == "1.0.0"
    assert online_fdr.__version__ == version
    assert 'version = "1.0.0"' in _read("uv.lock")
    assert f"version: {version}" in _read("CITATION.cff")
    assert f"## [{version}]" in _read("CHANGELOG.md")
    assert "Development Status :: 5 - Production/Stable" in project["classifiers"]
    assert "Typing :: Typed" in project["classifiers"]


def test_parity_dependency_group_is_explicit() -> None:
    dependency_groups = tomllib.loads(_read("pyproject.toml"))["dependency-groups"]

    assert "rpy2>=3.5" not in dependency_groups["dev"]
    assert dependency_groups["parity"] == ["rpy2>=3.5"]


def test_release_workflow_uses_trusted_publishing() -> None:
    workflow = _read(".github/workflows/release.yml")

    assert "tags:" in workflow
    assert '"v*.*.*"' in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "actions/download-artifact@v8" in workflow


def test_ci_keeps_live_parity_separate_from_python_matrix() -> None:
    workflow = _read(".github/workflows/ci.yml")

    assert 'python-version: ["3.10", "3.11", "3.12", "3.13"]' in workflow
    assert "uv sync --locked --group dev --python" in workflow
    assert "uv sync --locked --group dev --group parity --python 3.12" in workflow
    assert "--ignore=tests/test_onlinefdr_parity.py" in workflow
    assert "--ignore=tests/test_async_methods.py" in workflow


def test_release_support_files_exist() -> None:
    assert Path("docs/release.md").is_file()
    assert Path("CITATION.cff").is_file()
    assert Path(".github/dependabot.yml").is_file()
    assert Path(".github/CODEOWNERS").is_file()

    dependabot = _read(".github/dependabot.yml")
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert 'package-ecosystem: "uv"' in dependabot
