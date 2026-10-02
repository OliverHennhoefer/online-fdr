from __future__ import annotations

import json
import math
import random
from dataclasses import asdict

import pytest

from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.p_values.async_methods import AddisAsync, SaffronAsync
from online_fdr.p_values.async_methods._history import _FenwickCounter
from tests.async_reference import ReferenceAddisAsync, ReferenceSaffronAsync

METHOD_PAIRS = [
    pytest.param(SaffronAsync, ReferenceSaffronAsync, id="saffron"),
    pytest.param(AddisAsync, ReferenceAddisAsync, id="addis"),
]


def _assert_equivalent(method, reference, *, snapshot: bool = True) -> None:
    assert method.alpha_history == reference.alpha_history
    assert method.decisions == reference.decisions
    assert method.num_hypotheses == reference.num_hypotheses
    assert method.last_test_level == reference.last_test_level
    assert method.last_rejection_threshold == reference.last_rejection_threshold
    assert [asdict(record) for record in method.records] == [
        asdict(record) for record in reference.records
    ]
    for name in ("active", "completed"):
        assert {
            key: asdict(record) for key, record in getattr(method, name).items()
        } == {key: asdict(record) for key, record in getattr(reference, name).items()}
    if snapshot:
        payload = method.snapshot()
        assert "_history_index" not in payload["state"]
        assert payload["schema_version"] == 1
        assert payload["state"] == reference.snapshot()["state"]


def _start_pair(method, reference, test_id=None, *, snapshot: bool = True):
    actual = method.start_test(test_id)
    expected = reference.start_test(test_id)
    assert actual.test_id == expected.test_id
    assert actual.test_level == expected.test_level
    _assert_equivalent(method, reference, snapshot=snapshot)
    return actual


def _finish_pair(method, reference, test_id, value, *, snapshot: bool = True):
    assert method.finish_test(test_id, value) is reference.finish_test(test_id, value)
    _assert_equivalent(method, reference, snapshot=snapshot)


def _boundary_values(method):
    thresholds = [0.0, 1.0, method.lambda_]
    if isinstance(method, AddisAsync):
        thresholds.extend([method.tau, method.tau * method.lambda_])
    for value in thresholds:
        yield value
        if value > 0:
            yield math.nextafter(value, -math.inf)
        if value < 1:
            yield math.nextafter(value, math.inf)


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
def test_delayed_reverse_and_tied_completions_match_frozen_scan(
    method_type, reference_type
) -> None:
    method, reference = method_type(), reference_type()
    pending = []
    values = list(_boundary_values(method)) + [0.1, 0.3, 0.8, 0.0]
    for block in range(8):
        ids = [("block", block, offset) for offset in range(7)]
        for test_id in ids:
            _start_pair(method, reference, test_id)
        # Same-stage completions intentionally retain duplicate SAFFRON positions.
        for offset, test_id in reversed(list(enumerate(ids))):
            if offset % 3 == 0:
                pending.append(test_id)
            else:
                value = values[(block * 7 + offset) % len(values)]
                _finish_pair(method, reference, test_id, value)
        if block % 2 == 1:
            _finish_pair(method, reference, pending.pop(0), 0.0)
            _finish_pair(method, reference, pending.pop(), 0.8)
    for test_id in reversed(pending):
        _finish_pair(method, reference, test_id, 0.0)
    _start_pair(method, reference, "after-all-ties")


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
@pytest.mark.parametrize("seed", [7, 41, 2026])
def test_seeded_interleavings_match_exact_levels_and_boundaries(
    method_type, reference_type, seed
) -> None:
    method, reference = method_type(), reference_type()
    rng = random.Random(seed)
    pending = []
    values = list(_boundary_values(method)) + [0.0, 0.0, 0.1, 0.8]
    for event in range(110):
        if not pending or (len(pending) < 13 and rng.random() < 0.6):
            test_id = f"h-{event}"
            _start_pair(method, reference, test_id)
            pending.append(test_id)
        else:
            test_id = pending.pop(rng.randrange(len(pending)))
            if event % 5 == 0:
                threshold = reference.active[test_id].test_level
                value = rng.choice(
                    [
                        threshold,
                        math.nextafter(threshold, 0.0),
                        math.nextafter(threshold, 1.0),
                    ]
                )
            else:
                value = rng.choice(values)
            _finish_pair(method, reference, test_id, value)
    for test_id in reversed(pending):
        _finish_pair(method, reference, test_id, rng.choice(values))
    _start_pair(method, reference, "final")


class _RecordingGamma(DefaultSaffronGammaSequence):
    def __init__(self):
        super().__init__(gamma_exp=1.6, c=0.4374901658)
        self.calls: list[int] = []

    def calc_gamma(self, j: int, *args: object) -> float:
        self.calls.append(j)
        # A call-dependent return value catches removed or reordered gamma calls.
        return super().calc_gamma(j, *args) * (1 + len(self.calls) * 1e-10)


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
def test_custom_gamma_evaluation_order_and_float_arithmetic_are_preserved(
    method_type, reference_type
) -> None:
    actual_gamma, expected_gamma = _RecordingGamma(), _RecordingGamma()
    method = method_type(gamma_seq=actual_gamma)
    reference = reference_type(gamma_seq=expected_gamma)
    for block in range(5):
        for offset in range(4):
            _start_pair(method, reference, (block, offset), snapshot=False)
            assert actual_gamma.calls == expected_gamma.calls
        for offset in (2, 0, 3, 1):
            value = 0.0 if offset != 1 else 0.8
            _finish_pair(method, reference, (block, offset), value, snapshot=False)
        _start_pair(method, reference, (block, "pending"), snapshot=False)
        assert actual_gamma.calls == expected_gamma.calls


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
def test_parameter_changes_reclassify_history_before_start_and_finish(
    method_type, reference_type
) -> None:
    method, reference = method_type(), reference_type()
    for offset, value in enumerate([0.0, 0.1, 0.2, 0.3, 0.5, 0.8]):
        _start_pair(method, reference, offset)
        _finish_pair(method, reference, offset, value)
    _start_pair(method, reference, "old-pending")
    for index, lambda_ in enumerate([0.2, 0.4, 0.1, 0.3]):
        method.lambda_ = reference.lambda_ = lambda_
        if isinstance(method, AddisAsync):
            method.tau = reference.tau = 0.7 if index % 2 == 0 else 0.6
        if index == 0:
            # Rebuilding must happen before the pending record becomes completed.
            _finish_pair(method, reference, "old-pending", 0.15)
        _start_pair(method, reference, ("changed", index))
        _finish_pair(method, reference, ("changed", index), 0.0)


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
def test_legacy_schema_one_and_new_snapshots_resume_pending_and_tied_tests(
    method_type, reference_type
) -> None:
    reference = reference_type()
    for test_id in range(6):
        reference.start_test(test_id)
    reference.finish_test(3, 0.0)
    reference.finish_test(0, 0.0)
    reference.finish_test(1, 0.8)
    # This is the actual pre-index schema, rather than a new payload with a key removed.
    legacy = json.loads(json.dumps(reference.snapshot(), allow_nan=False))
    legacy["method"] = method_type.__name__
    assert "_history_index" not in legacy["state"]
    method = method_type.from_snapshot(legacy)
    _assert_equivalent(method, reference)
    _finish_pair(method, reference, 5, 0.1)
    _start_pair(method, reference, "after-legacy-restore")
    _finish_pair(method, reference, 2, 0.0)
    _finish_pair(method, reference, 4, 0.8)
    restored = method_type.from_snapshot(
        json.loads(json.dumps(method.snapshot(), allow_nan=False))
    )
    restored_reference = reference_type.from_snapshot(reference.snapshot())
    for subject, oracle in ((method, reference), (restored, restored_reference)):
        _start_pair(subject, oracle, "after-new-restore")
        _finish_pair(subject, oracle, "after-legacy-restore", 0.0)
        _start_pair(subject, oracle, "last")
    assert method.snapshot() == restored.snapshot()


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
@pytest.mark.parametrize("payload_source", ["legacy", "current"])
def test_parameter_changes_after_restore_rebuild_before_finish_and_next_start(
    method_type, reference_type, payload_source
) -> None:
    method, reference = method_type(), reference_type()
    for test_id in range(5):
        _start_pair(method, reference, test_id)
    for test_id, value in ((1, 0.0), (3, 0.0), (0, 0.3)):
        _finish_pair(method, reference, test_id, value)
    source = reference if payload_source == "legacy" else method
    payload = json.loads(json.dumps(source.snapshot(), allow_nan=False))
    payload["method"] = method_type.__name__
    method = method_type.from_snapshot(payload)
    reference = reference_type.from_snapshot(reference.snapshot())

    method.lambda_ = reference.lambda_ = 0.2
    if isinstance(method, AddisAsync):
        method.tau = reference.tau = 0.75
    _finish_pair(method, reference, 2, 0.2)

    method.lambda_ = reference.lambda_ = 0.35
    if isinstance(method, AddisAsync):
        method.tau = reference.tau = 0.8
    _start_pair(method, reference, "after-restored-parameter-change")
    _finish_pair(method, reference, 4, 0.0)
    _start_pair(method, reference, "after-restored-late-rejection")


@pytest.mark.parametrize(("method_type", "reference_type"), METHOD_PAIRS)
def test_invalid_calls_preserve_existing_auto_id_and_test_one_continuation(
    method_type, reference_type
) -> None:
    method, reference = method_type(), reference_type()
    _start_pair(method, reference, 1)
    _start_pair(method, reference, "done")
    _finish_pair(method, reference, "done", 0.0)
    actions = [
        lambda subject: subject.finish_test(1, math.nan),
        lambda subject: subject.finish_test("unknown", 0.1),
        lambda subject: subject.finish_test("done", 0.1),
        lambda subject: subject.start_test(1),
        # Existing behavior consumes auto-ID 1 before discovering its collision.
        lambda subject: subject.start_test(),
        # Existing test_one starts a test before its p-value validation fails.
        lambda subject: subject.test_one(math.nan),
    ]
    for index, action in enumerate(actions):
        before = method.snapshot()
        with pytest.raises(ValueError) as actual:
            action(method)
        with pytest.raises(ValueError) as expected:
            action(reference)
        assert str(actual.value) == str(expected.value)
        _assert_equivalent(method, reference)
        if index < 4:
            assert method.snapshot() == before
        # Excluded caches could be corrupted without changing persistent snapshots.
        _start_pair(method, reference, ("after-invalid", index))
        _finish_pair(method, reference, ("after-invalid", index), 0.8)
    assert set(method.active) == {1, 2}
    _finish_pair(method, reference, 2, 0.8)
    assert _start_pair(method, reference).test_id == 3
    _finish_pair(method, reference, 1, 0.0)
    _finish_pair(method, reference, 3, 0.1)
    assert method.test_one(0.0) is reference.test_one(0.0)
    _assert_equivalent(method, reference)


class _CountingRecords(list):
    def __init__(self, values):
        super().__init__(values)
        self.inspections = 0

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.inspections += len(value) if isinstance(key, slice) else 1
        return value

    def __iter__(self):
        for value in super().__iter__():
            self.inspections += 1
            yield value


@pytest.mark.parametrize("method_type", [SaffronAsync, AddisAsync])
@pytest.mark.parametrize("value", [0.8, 0.1], ids=["noncandidate", "candidate"])
@pytest.mark.parametrize("lag", [0, 63], ids=["immediate", "delayed"])
def test_long_stream_inspects_records_at_most_linearly(method_type, value, lag) -> None:
    method = method_type()
    records = _CountingRecords(method._records)
    method._records = records
    n_tests = 2_000
    for test_id in range(n_tests):
        method.start_test(test_id)
        if test_id >= lag:
            assert method.finish_test(test_id - lag, value) is False
    # Reverse and tied completions also exercise late historical point updates.
    for test_id in reversed(range(n_tests - lag, n_tests)):
        assert method.finish_test(test_id, value) is False
    assert records.inspections <= 8 * n_tests
    assert method.num_hypotheses == n_tests
    assert method.decisions == (False,) * n_tests
    assert not method.active


@pytest.mark.parametrize("size", [0, 1, 2, 3, 7, 8, 9, 17, 256])
def test_fenwick_bulk_construction_preserves_signed_prefixes(size) -> None:
    values = [(index % 7) - 3 for index in range(size)]
    counter = _FenwickCounter(value for value in values)
    assert len(counter) == size
    assert [counter.prefix(end) for end in range(size + 1)] == [
        sum(values[:end]) for end in range(size + 1)
    ]


def test_fenwick_growth_preserves_late_updates_across_power_of_two_nodes() -> None:
    counter = _FenwickCounter()
    values = []
    for index in range(257):
        value = (index % 5) - 2
        values.append(value)
        counter.append(value)
        for target, delta in ((0, -1), (index // 2, 2), (index, -3)):
            counter.add(target, delta)
            values[target] += delta
        assert len(counter) == len(values)
        assert [counter.prefix(end) for end in range(len(values) + 1)] == [
            sum(values[:end]) for end in range(len(values) + 1)
        ]


def test_fenwick_bulk_index_accepts_arbitrary_signed_point_updates() -> None:
    rng = random.Random(2026)
    values = [rng.randrange(-4, 5) for _ in range(1_025)]
    counter = _FenwickCounter(values)
    for _ in range(250):
        index, delta = rng.randrange(len(values)), rng.randrange(-20, 21)
        counter.add(index, delta)
        values[index] += delta
    for end in range(len(values) + 1):
        assert counter.prefix(end) == sum(values[:end])


@pytest.mark.parametrize("values", [[], [1, -2, 3]], ids=["empty", "populated"])
def test_fenwick_invalid_bounds_raise_without_corrupting_continuation(values) -> None:
    counter = _FenwickCounter(values)
    invalid_calls = [
        lambda: counter.add(-1, 2),
        lambda: counter.add(len(counter), 2),
        lambda: counter.prefix(-1),
        lambda: counter.prefix(len(counter) + 1),
    ]
    for invalid_call in invalid_calls:
        with pytest.raises(IndexError):
            invalid_call()
        assert [counter.prefix(end) for end in range(len(values) + 1)] == [
            sum(values[:end]) for end in range(len(values) + 1)
        ]
    counter.append(-5)
    assert counter.prefix(len(counter)) == sum(values) - 5
