import ast
import importlib
import re
from pathlib import Path


def _iter_online_fdr_imports(text: str) -> list[str]:
    statements: list[str] = []
    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("from online_fdr") or line.startswith("import online_fdr"):
            statement_lines = [line]
            open_parens = line.count("(") - line.count(")")

            while line.endswith("\\") or open_parens > 0:
                i += 1
                if i >= len(lines):
                    break
                line = lines[i].strip()
                statement_lines.append(line)
                open_parens += line.count("(") - line.count(")")

            statements.append("\n".join(statement_lines))

        i += 1

    return statements


def _assert_import_statement_works(statement: str) -> None:
    tree = ast.parse(statement)

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("online_fdr"):
                    importlib.import_module(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("online_fdr"):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    if alias.name != "*":
                        assert hasattr(module, alias.name)


def test_online_fdr_imports_in_docs_are_valid() -> None:
    paths = [Path("README.md"), *sorted(Path("docs").rglob("*.md"))]
    statements: list[str] = []

    for path in paths:
        statements.extend(_iter_online_fdr_imports(path.read_text(encoding="utf-8")))

    assert statements
    for statement in statements:
        _assert_import_statement_works(statement)


def test_live_r_parity_setup_docs_include_pinned_install_commands() -> None:
    required_snippets = [
        "uv sync --group dev --group parity",
        "BiocManager::install(version = '3.22'",
        "BiocManager::install('onlineFDR', version = '3.22'",
        "packageVersion('onlineFDR')) == '2.18.0'",
        "-m live_r_parity",
        "tests/test_onlinefdr_parity.py tests/test_async_methods.py",
    ]
    paths = [
        Path("docs/installation.md"),
        Path("docs/contributing.md"),
        Path("tests/reference/README.md"),
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for snippet in required_snippets:
            assert snippet in text, f"{path} is missing {snippet!r}"


def test_non_parity_workflow_docs_use_default_marker_exclusion() -> None:
    paths = [Path("docs/troubleshooting.md"), Path("docs/workflows.md")]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "uv run python -m pytest -q" in text
        assert "--ignore=tests/test_onlinefdr_parity.py" not in text
        assert "--ignore=tests/test_async_methods.py" not in text
        assert '-k "not onlinefdr_parity"' not in text


def _python_example_under_heading(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    marker = f"\n{heading}\n"
    assert text.count(marker) == 1, f"{path} must contain one {heading!r} heading"
    section = text.split(marker, 1)[1].split("\n### ", 1)[0]
    examples = re.findall(r"```python\n(.*?)\n```", section, flags=re.DOTALL)
    assert len(examples) == 1, f"{path}: {heading} must contain one Python example"
    return examples[0]


def test_saffron_basic_and_parameter_selection_examples_run() -> None:
    path = Path("docs/api/investing/saffron.md")
    namespace: dict[str, object] = {}
    # These two adjacent examples intentionally share their Saffron import.
    for heading in ("### Basic Usage", "### Parameter Selection"):
        example = _python_example_under_heading(path, heading)
        exec(compile(example, str(path), "exec"), namespace)

    assert namespace["saffron"].num_hypotheses == len(namespace["p_values"])
    for name in ("conservative", "moderate", "aggressive"):
        assert namespace[name].num_hypotheses == len(namespace["test_p_values"])
