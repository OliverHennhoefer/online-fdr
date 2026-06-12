from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from online_fdr.core import BatchDecision, TestDecision
from online_fdr.core.abstract.abstract_gamma_seq import AbstractGammaSequence
from online_fdr.e_values import EBH, ELond
from online_fdr.p_values import (
    Addis,
    AlphaSpending,
    BatchBH,
    Bonferroni,
    SaffronAsync,
    Toad,
)

ROOT = Path(__file__).resolve().parents[1]


def test_sequential_detail_result_uses_explicit_state_names() -> None:
    method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

    detail = method.test_one_detail(0.001)

    assert isinstance(detail, TestDecision)
    assert detail.rejected is True
    assert detail.index == 1
    assert detail.test_level == method.last_test_level
    assert detail.rejection_threshold == method.last_rejection_threshold
    assert method.target_level == 0.05
    assert method.error_rate == "FDR"
    assert method.num_hypotheses == 1


def test_batch_detail_result_separates_batches_from_hypotheses() -> None:
    method = BatchBH(alpha=0.05)

    detail = method.test_batch_detail([0.001, 0.2, 0.8])

    assert isinstance(detail, BatchDecision)
    assert detail.rejected == (True, False, False)
    assert detail.values == (0.001, 0.2, 0.8)
    assert detail.batch_index == 1
    assert method.num_batches == 1
    assert method.num_hypotheses == 3
    assert detail.test_level == method.last_test_level
    assert detail.rejection_threshold == method.last_rejection_threshold
    assert detail.metadata == {"num_rejections": 1}
    with pytest.raises(TypeError):
        detail.metadata["num_rejections"] = 2  # type: ignore[index]


def test_snapshot_restore_is_detached_from_mutable_runtime_state() -> None:
    method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    assert method.test_one(0.001) is True

    snapshot = method.snapshot()
    restored = Addis.from_snapshot(snapshot)

    assert restored.num_hypotheses == method.num_hypotheses
    assert restored.reject_idx == method.reject_idx
    snapshot["state"]["reject_idx"].append(999)
    assert restored.reject_idx == method.reject_idx


def test_async_public_records_are_immutable_snapshots() -> None:
    method = SaffronAsync(alpha=0.05)
    level = method.start_test("h1")

    assert level.test_level == pytest.approx(method.last_test_level)
    record = method.active["h1"]
    assert record.test_level == pytest.approx(level.test_level)
    with pytest.raises(FrozenInstanceError):
        record.rejected = True  # type: ignore[misc]


def test_toad_public_records_and_decisions_are_copied() -> None:
    method = Toad(alpha=0.05)
    method.add_test(0.001, deadline=2, test_id="a")

    record = method.records[0]
    with pytest.raises(FrozenInstanceError):
        record.rejected = False  # type: ignore[misc]

    decisions = method.current_decisions
    decisions["a"] = False
    assert method.current_decisions["a"] is True


class _UnsupportedGammaSequence(AbstractGammaSequence):
    def calc_gamma(self, j: int, *args: Any, **kwargs: Any) -> float:
        return 1.0 / j


def _json_round_trip(method):
    payload = method.snapshot()
    encoded = json.dumps(payload, allow_nan=False)
    return method.__class__.from_snapshot(json.loads(encoded))


def test_snapshot_round_trips_through_json_for_representative_methods() -> None:
    addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    assert addis.test_one(0.001) is True
    addis_restored = _json_round_trip(addis)
    assert addis.test_one(0.2) == addis_restored.test_one(0.2)

    batch = BatchBH(alpha=0.05)
    assert batch.test_batch([0.001, 0.2])
    batch_restored = _json_round_trip(batch)
    assert batch.test_batch([0.01, 0.9]) == batch_restored.test_batch([0.01, 0.9])

    ebh = EBH(alpha=0.05)
    assert ebh.test_batch([1.0, 2.0]) == [False, False]
    ebh_restored = _json_round_trip(ebh)
    assert ebh.test_batch([100.0, 2.0]) == ebh_restored.test_batch([100.0, 2.0])

    elond = ELond(alpha=0.05)
    assert elond.test_one(1000.0) is True
    elond_restored = _json_round_trip(elond)
    assert elond.test_one(10.0) == elond_restored.test_one(10.0)

    async_method = SaffronAsync(alpha=0.05)
    async_method.start_test("h1")
    assert async_method.finish_test("h1", 0.001) is True
    async_restored = _json_round_trip(async_method)
    original_level = async_method.start_test("h2")
    restored_level = async_restored.start_test("h2")
    assert restored_level.test_level == pytest.approx(original_level.test_level)
    assert async_method.finish_test("h2", 0.8) == async_restored.finish_test("h2", 0.8)

    toad = Toad(alpha=0.05)
    assert toad.add_test(0.001, deadline=2, test_id="a") is True
    toad_restored = _json_round_trip(toad)
    assert toad.add_test(0.2, deadline=3, test_id="b") == toad_restored.add_test(
        0.2, deadline=3, test_id="b"
    )
    assert toad.advance_to(3) == toad_restored.advance_to(3)

    spending = AlphaSpending(alpha=0.05, spend_func=Bonferroni(k=3))
    assert spending.test_one(0.001) is True
    spending_restored = _json_round_trip(spending)
    assert spending.test_one(0.2) == spending_restored.test_one(0.2)


def test_snapshot_rejects_schema_method_mismatches_and_unsupported_helpers() -> None:
    snapshot = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5).snapshot()

    wrong_schema = dict(snapshot)
    wrong_schema["schema_version"] = 999
    with pytest.raises(ValueError, match="schema_version"):
        Addis.from_snapshot(wrong_schema)

    wrong_method = dict(snapshot)
    wrong_method["method"] = "Saffron"
    with pytest.raises(ValueError, match="class"):
        Addis.from_snapshot(wrong_method)

    unsupported = ELond(alpha=0.05, gamma_seq=_UnsupportedGammaSequence())
    with pytest.raises(TypeError, match="seq"):
        unsupported.snapshot()


def test_docs_do_not_reference_removed_target_level_alias() -> None:
    paths = [ROOT / "README.md", ROOT / "docs", ROOT / "examples"]
    offenders: list[Path] = []
    for path in paths:
        candidates = [path] if path.is_file() else path.rglob("*")
        for candidate in candidates:
            if candidate.suffix not in {".md", ".ipynb"}:
                continue
            if "last_rejection_threshold0" in candidate.read_text(encoding="utf-8"):
                offenders.append(candidate.relative_to(ROOT))

    assert offenders == []
