import ast
import importlib
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
