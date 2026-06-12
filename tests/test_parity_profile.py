import importlib
import json
from pathlib import Path

import pytest

from tests import parity_oracle
from tests.parity_oracle import PARITY_PROFILE_COVERAGE, _parse_r_version


def test_parity_profile_is_well_formed_and_importable() -> None:
    profile_path = Path("tests/reference/parity_profile.json")
    entries = json.loads(profile_path.read_text(encoding="utf-8"))

    assert isinstance(entries, list)
    assert entries

    valid_statuses = {"Parity", "IntentionalDivergence", "Extension"}
    names = set()

    for entry in entries:
        assert "name" in entry
        assert "status" in entry
        assert "note" in entry

        assert entry["status"] in valid_statuses
        assert entry["name"] not in names
        names.add(entry["name"])

        import_path = entry.get("import_path")
        if import_path:
            module_path, symbol = import_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            assert hasattr(module, symbol)


def test_intentional_divergences_are_explicit() -> None:
    profile_path = Path("tests/reference/parity_profile.json")
    entries = json.loads(profile_path.read_text(encoding="utf-8"))
    divergences = [
        entry for entry in entries if entry["status"] == "IntentionalDivergence"
    ]

    assert divergences
    assert any("true-online" in entry["note"].lower() for entry in divergences)


def test_all_parity_profile_methods_are_covered_by_live_parity_suite() -> None:
    profile_path = Path("tests/reference/parity_profile.json")
    entries = json.loads(profile_path.read_text(encoding="utf-8"))
    parity_entries = {entry["name"] for entry in entries if entry["status"] == "Parity"}

    assert parity_entries
    assert parity_entries == PARITY_PROFILE_COVERAGE


def test_r_version_parser_accepts_r_semver_output() -> None:
    assert _parse_r_version("4.5.1") == (4, 5, 1)
    assert _parse_r_version("4.5") == (4, 5, 0)


def test_r_runtime_preflight_requires_rscript_on_path(monkeypatch) -> None:
    monkeypatch.setattr(parity_oracle.shutil, "which", lambda name: None)

    with pytest.raises(RuntimeError, match="Rscript.*PATH"):
        parity_oracle._require_supported_r_runtime()
