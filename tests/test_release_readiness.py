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

    assert "tags:" in workflow
    assert '"v*.*.*"' in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert "uv run python -m ruff check ." in workflow
    assert "uv run python -m mypy online_fdr tests/typing" in workflow
    assert "uv run python -m pytest -q" in workflow
    assert "uses: ./.github/workflows/live-r-parity.yml" in workflow
    assert "uv run mkdocs build --strict" in workflow
    assert "needs: [build, parity]" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "actions/download-artifact@v8" in workflow


def test_ci_keeps_live_parity_separate_from_python_matrix() -> None:
    workflow = _read(".github/workflows/ci.yml")
    parity = _read(".github/workflows/live-r-parity.yml")

    assert 'python-version: ["3.10", "3.11", "3.12", "3.13"]' in workflow
    assert "uv sync --locked --group dev --python" in workflow
    assert "uv run python -m mypy online_fdr tests/typing" in workflow
    assert "uses: ./.github/workflows/live-r-parity.yml" in workflow
    assert "uv sync --locked --group dev --group parity --python 3.12" in parity
    assert "uv run python -m pytest -q" in workflow
    assert (
        "-m live_r_parity tests/test_onlinefdr_parity.py tests/test_async_methods.py"
        in parity
    )
    assert "--ignore=tests/test_onlinefdr_parity.py" not in workflow
    assert "--ignore=tests/test_async_methods.py" not in workflow


def test_parity_installation_uses_one_stabilized_recipe() -> None:
    parity = _read(".github/workflows/live-r-parity.yml")
    container = _read(".github/workflows/tests-container.yml")
    install = _read(".github/actions/install-onlinefdr/action.yml")

    assert "workflow_call:" in parity
    assert 'r-version: "4.5.1"' in parity
    assert "use-public-rspm: false" in parity
    assert "image: rocker/r-ver:4.5.1" in container
    for workflow in (parity, container):
        assert "uses: ./.github/actions/install-onlinefdr" in workflow
        assert "timeout-minutes: 30" in workflow
        assert "BiocManager::install" not in workflow

    assert "using: composite" in install
    assert "shell: bash" in install
    assert "timeout=600, repos=c(CRAN='https://cloud.r-project.org')" in install
    assert "repos=BiocManager::repositories(version='3.22')" in install
    assert "BiocManager::install(version='3.22', ask=FALSE, update=FALSE)" in install
    assert "BiocManager::install('onlineFDR', version='3.22'" in install
    assert "packageVersion('onlineFDR')) == '2.18.0'" in install


def test_ci_covers_shared_workflow_and_action_changes() -> None:
    workflow = _read(".github/workflows/ci.yml")

    assert '".github/workflows/**"' in workflow
    assert '".github/actions/**"' in workflow


def test_release_support_files_exist() -> None:
    assert Path("docs/release.md").is_file()
    assert Path("CITATION.cff").is_file()
    assert Path(".github/dependabot.yml").is_file()

    dependabot = _read(".github/dependabot.yml")
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert 'package-ecosystem: "uv"' in dependabot
