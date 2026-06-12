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


def test_pytest_excludes_live_parity_by_default() -> None:
    pytest_config = tomllib.loads(_read("pyproject.toml"))["tool"]["pytest"][
        "ini_options"
    ]

    assert "-m 'not live_r_parity'" in pytest_config["addopts"]
    assert any(
        marker.startswith("live_r_parity:") for marker in pytest_config["markers"]
    )


def test_release_workflow_uses_trusted_publishing() -> None:
    workflow = _read(".github/workflows/release.yml")
    parity_command = (
        "-m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py"
    )

    assert "tags:" in workflow
    assert '"v*.*.*"' in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert "uv run python -m ruff check ." in workflow
    assert "uv run python -m mypy online_fdr" in workflow
    assert "uv run python -m pytest -q" in workflow
    assert parity_command in workflow
    assert "uv run mkdocs build --strict" in workflow
    assert "Run live parity tests" in workflow
    assert "needs: [build, parity]" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "actions/download-artifact@v8" in workflow


def test_ci_keeps_live_parity_separate_from_python_matrix() -> None:
    workflow = _read(".github/workflows/ci.yml")
    parity_command = (
        "-m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py"
    )

    assert 'python-version: ["3.10", "3.11", "3.12", "3.13"]' in workflow
    assert "uv sync --locked --group dev --python" in workflow
    assert "uv sync --locked --group dev --group parity --python 3.12" in workflow
    assert "uv run python -m pytest -q" in workflow
    assert parity_command in workflow
    assert "--ignore=tests/test_onlinefdr_parity.py" not in workflow
    assert "--ignore=tests/test_async_methods.py" not in workflow


def test_release_support_files_exist() -> None:
    assert Path("docs/release.md").is_file()
    assert Path("CITATION.cff").is_file()
    assert Path(".github/dependabot.yml").is_file()

    dependabot = _read(".github/dependabot.yml")
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert 'package-ecosystem: "uv"' in dependabot
