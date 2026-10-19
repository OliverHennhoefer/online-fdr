from __future__ import annotations

import json
import math
from fractions import Fraction

import pytest

from online_fdr.p_values import BatchBHOfficial, LordDependent, LordDiscard, Toad

_AUTHOR_POLY_COEFFICIENT = 0.6079271388115668


def _restart(method):
    return type(method).from_snapshot(json.loads(json.dumps(method.snapshot())))


@pytest.mark.parametrize("wealth,reward", [(0.049, 0.001), (0.025, 0.005)])
def test_dependent_lord_rejects_wealth_above_reward(
    wealth: float, reward: float
) -> None:
    # Both pairs satisfy the general LORD budget but violate LORDdep's w0 <= b0.
    with pytest.raises(ValueError, match="wealth <= reward"):
        LordDependent(alpha=0.05, wealth=wealth, reward=reward)


def test_dependent_lord_allows_the_reference_boundary() -> None:
    method = LordDependent(alpha=0.05, wealth=0.025, reward=0.025)
    expected = 0.139307 * 0.05 / math.log(2) ** 3
    assert method.test_one(1.0) is False
    assert method.last_test_level == pytest.approx(expected)
    assert method.wealth >= 0


@pytest.mark.parametrize("wealth,tau", [(0.049, 0.01), (0.03, 0.5)])
def test_discarding_lord_rejects_wealth_above_selected_budget(
    wealth: float, tau: float
) -> None:
    with pytest.raises(ValueError, match=r"wealth <= tau \* alpha"):
        LordDiscard(alpha=0.05, wealth=wealth, tau=tau)


def test_discarding_lord_allows_zero_first_discovery_reward() -> None:
    method = LordDiscard(alpha=0.05, wealth=0.025, tau=0.5)
    assert method.test_one(0.0) is True
    assert method.test_one(0.1) is False
    expected = 0.025 * 0.07720838 * math.log(2) / (2 * math.exp(math.sqrt(math.log(2))))
    assert method.last_test_level == pytest.approx(expected)
    assert method.last_test_level >= 0


def test_toad_arrival_after_advance_cannot_change_a_final_decision() -> None:
    method = Toad(alpha=0.05)
    assert method.add_test(0.03, deadline=2, test_id="a", weight=0.5) is False
    assert method.advance_to(3) == {"a": False}

    assert method.add_test(0.001, deadline=4, test_id="b", weight=0.5) is True
    assert method.current_stage == 4
    assert method.num_hypotheses == 2
    assert method.records[1].stage == 4
    assert method.current_decisions == {"a": False, "b": True}
    assert method.final_decisions == {"a": False}
    assert method.records[0].finalized is True
    assert method.records[0].rejected is False


def test_toad_arrivals_also_finalize_expired_decisions() -> None:
    method = Toad(alpha=0.05)
    method.add_test(0.03, deadline=1, test_id="a", weight=0.5)
    method.add_test(0.001, deadline=2, test_id="b", weight=0.5)
    assert method.final_decisions == {"a": False}
    assert method.records[0].finalized is True
    assert method.advance_to(3) == {"b": True}


def test_toad_clock_and_arrival_weights_survive_restart() -> None:
    method = Toad()
    method.add_test(0.9, deadline=1)
    method.advance_to(100)
    restored = _restart(method)

    for current in (method, restored):
        current.add_test(0.001, deadline=101)
        assert current.current_stage == 101
        assert current.records[-1].stage == 101
        # Advancing time does not skip the second hypothesis's default weight.
        expected_weight = (
            0.07720838 * math.log(2) / (2 * math.exp(math.sqrt(math.log(2))))
        )
        assert current.records[-1].weight == pytest.approx(expected_weight)
    assert method.snapshot() == restored.snapshot()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"deadline": 0},
        {"deadline": 1.5},
        {"deadline": math.nan},
        {"deadline": True},
        {"deadline": 1, "weight": math.nan},
        {"deadline": 1, "weight": math.inf},
        {"deadline": 1, "weight": 0.0},
        {"deadline": 1, "weight": -0.1},
        {"deadline": 1, "weight": True},
        {"deadline": 1, "weight": 1.1},
    ],
)
def test_toad_invalid_arrival_does_not_consume_an_id_or_change_state(kwargs) -> None:
    method = Toad()
    before = method.snapshot()
    with pytest.raises(ValueError):
        method.add_test(0.01, **kwargs)
    assert method.snapshot() == before
    method.add_test(0.01, deadline=1)
    assert method.records[0].test_id == 1


def test_toad_auto_ids_skip_explicit_ids_and_expired_deadlines_are_atomic() -> None:
    method = Toad()
    method.add_test(0.9, deadline=1, test_id=1)
    method.advance_to(10)
    before = method.snapshot()
    with pytest.raises(ValueError, match="deadline"):
        method.add_test(0.01, deadline=2)
    assert method.snapshot() == before
    method.add_test(0.01, deadline=11)
    assert method.records[-1].test_id == 2


@pytest.mark.parametrize("stage", [-1, 1.5, math.nan, math.inf, True])
def test_toad_invalid_advance_is_atomic(stage) -> None:
    method = Toad()
    method.add_test(0.01, deadline=2)
    before = method.snapshot()
    with pytest.raises(ValueError, match="stage"):
        method.advance_to(stage)
    assert method.snapshot() == before


@pytest.mark.parametrize("deadline", [0, 1.5, math.nan, True])
def test_toad_finite_deadlines_use_the_same_integer_boundary(deadline) -> None:
    with pytest.raises(ValueError, match="deadline"):
        Toad.run_finite([0.01], [deadline])


@pytest.mark.parametrize("weight", [0.0, math.nan, math.inf, True])
def test_toad_finite_weights_must_be_finite_and_positive(weight) -> None:
    with pytest.raises(ValueError, match="weight"):
        Toad.run_finite([0.01], [1], weights=[weight])


def test_toad_rejects_weight_underflow_before_changing_stream_state() -> None:
    method, control = Toad(), Toad()
    before = method.snapshot()
    with pytest.raises(ValueError, match="weight"):
        method.add_test(0.01, deadline=1, weight=Fraction(1, 10**400))
    assert method.snapshot() == before

    assert method.add_test(0.01, deadline=1, weight=Fraction(1, 4)) == (
        control.add_test(0.01, deadline=1, weight=0.25)
    )
    assert method.snapshot() == control.snapshot()
    assert method.records[0].test_id == 1
    assert method.records[0].weight == 0.25


def test_toad_finite_rejects_weight_underflow_without_mutating_inputs() -> None:
    values, deadlines = [0.01], [1]
    weights = [Fraction(1, 10**400)]
    with pytest.raises(ValueError, match="weight"):
        Toad.run_finite(values, deadlines, weights=weights)
    assert values == [0.01]
    assert deadlines == [1]
    assert weights == [Fraction(1, 10**400)]
    assert Toad.run_finite(values, deadlines, weights=[Fraction(1, 4)]) == (
        Toad.run_finite(values, deadlines, weights=[0.25])
    )


@pytest.mark.parametrize("sizes", [[1, 100, 1, 101], [100, 100, 1, 101]])
def test_batch_official_preserves_its_first_gamma_budget_across_sizes(sizes) -> None:
    method = BatchBHOfficial(alpha=0.05)
    for stage, size in enumerate(sizes, start=1):
        detail = method.test_batch_detail([0.9] * size)
        # With no discoveries, the next level is exactly the next allocation.
        # This expectation comes from one fixed summable sequence, independent
        # of the implementation's retrospective beta calculation.
        gamma = (
            _AUTHOR_POLY_COEFFICIENT / stage**2
            if sizes[0] < 100
            else (0.5 if stage <= 2 else 0.0)
        )
        assert detail.test_level == pytest.approx(0.05 * gamma, abs=1e-15)
        assert detail.test_level >= 0
        assert not any(detail.rejected)
        assert detail.metadata["fdh"] <= 0.05 + 1e-15
    assert method.gamma_profile == ("poly" if sizes[0] < 100 else "half")


@pytest.mark.parametrize("profile", ["poly", "half"])
def test_batch_official_configured_profile_survives_empty_batches_and_restart(
    profile,
) -> None:
    method = BatchBHOfficial(alpha=0.05, gamma_profile=profile)
    before = method.snapshot()
    assert method.test_batch([]) == []
    assert method.snapshot() == before
    method.test_batch([0.001] * 101)
    restored = _restart(method)
    for values in ([0.9], [0.001, 0.02, 0.9], [0.1] * 100):
        assert method.test_batch_detail(values) == restored.test_batch_detail(values)
        assert method.gamma_profile == profile
    assert method.snapshot() == restored.snapshot()


def test_batch_official_auto_profile_waits_for_a_valid_nonempty_batch() -> None:
    method = BatchBHOfficial(alpha=0.05)
    before = method.snapshot()
    method.test_batch([])
    with pytest.raises(ValueError):
        method.test_batch([math.nan] * 100)
    assert method.snapshot() == before
    assert method.gamma_profile is None
    method.test_batch([0.9])
    assert method.gamma_profile == "poly"


@pytest.mark.parametrize("profile", ["poly", "half"])
def test_batch_official_mixed_discoveries_stay_within_one_gamma_budget(profile) -> None:
    method = BatchBHOfficial(alpha=0.05, gamma_profile=profile)
    gamma_budget = 0.0
    for stage, size in enumerate((4, 101, 1, 100, 3), start=1):
        gamma_budget += (
            _AUTHOR_POLY_COEFFICIENT / stage**2
            if profile == "poly"
            else (0.5 if stage <= 2 else 0.0)
        )
        values = [0.00001] + [0.9] * (size - 1)
        detail = method.test_batch_detail(values)
        assert detail.test_level >= 0
        assert 0 <= detail.metadata["fdh"] <= 0.05 * gamma_budget + 1e-15


def test_batch_official_rejects_an_unknown_profile() -> None:
    with pytest.raises(ValueError, match="gamma_profile"):
        BatchBHOfficial(alpha=0.05, gamma_profile="unknown")


def test_batch_official_exhausted_budget_does_not_create_negative_levels() -> None:
    method = BatchBHOfficial(alpha=0.19550964730548234, gamma_profile="half")
    batches = [
        [0.0, 0.99],
        [0.0001, 0.99, 0.99, 0.0001, 0.0],
        [0.0001, 0.0, 0.99],
        [0.0001, 0.0, 0.0001, 0.99, 0.99],
        [0.0001],
        [0.99],
        [0.99, 0.99, 0.99],
    ]
    for values in batches:
        detail = method.test_batch_detail(values)
        assert detail.test_level >= 0
        assert detail.metadata["fdh"] <= method.target_level + 1e-15
    assert detail.test_level == 0.0
    assert not any(detail.rejected)
    restored = _restart(method)
    assert method.test_batch_detail([0.99]) == restored.test_batch_detail([0.99])
    assert method.last_test_level == 0.0


@pytest.mark.parametrize("size", [4, 101])
def test_batch_official_legacy_snapshot_recovers_first_profile(size: int) -> None:
    method = BatchBHOfficial(alpha=0.05)
    method.test_batch([0.001] * size)
    method.test_batch([0.9] * size)
    legacy = json.loads(json.dumps(method.snapshot()))
    del legacy["state"]["_gamma_profile"]
    restored = BatchBHOfficial.from_snapshot(legacy)
    assert restored.gamma_profile == ("poly" if size < 100 else "half")
    assert method.test_batch_detail([0.002]) == restored.test_batch_detail([0.002])


def test_batch_official_empty_legacy_snapshot_defers_automatic_selection() -> None:
    legacy = BatchBHOfficial(alpha=0.05).snapshot()
    del legacy["state"]["_gamma_profile"]
    restored = BatchBHOfficial.from_snapshot(legacy)
    assert restored.gamma_profile is None
    restored.test_batch([0.9] * 100)
    assert restored.gamma_profile == "half"


def test_batch_official_legacy_snapshot_rejects_invalid_past_levels() -> None:
    method = BatchBHOfficial(alpha=0.05)
    for size in (100, 100, 1):
        method.test_batch([0.9] * size)
    legacy = json.loads(json.dumps(method.snapshot()))
    del legacy["state"]["_gamma_profile"]
    # The old implementation produced this third level after switching profile.
    legacy["state"]["alpha_s"][2] = -0.008627180830879481
    with pytest.raises(ValueError, match="prior decisions cannot be repaired"):
        BatchBHOfficial.from_snapshot(legacy)


def test_batch_official_legacy_snapshot_rejects_positive_but_overspent_history() -> (
    None
):
    method = BatchBHOfficial(alpha=0.05)
    for size in (1, 100):
        method.test_batch([0.9] * size)
    legacy = json.loads(json.dumps(method.snapshot()))
    del legacy["state"]["_gamma_profile"]
    # The old size-dependent rule switched to the half profile at batch two,
    # spending its full cumulative budget minus the first allocation. Both
    # levels are positive, but their sum exceeds the inferred polynomial
    # budget and would produce a negative level on the next batch.
    legacy["state"]["alpha_s"][1] = 0.05 - legacy["state"]["alpha_s"][0]
    assert all(level > 0 for level in legacy["state"]["alpha_s"])
    with pytest.raises(ValueError, match="exceed the fixed gamma budget"):
        BatchBHOfficial.from_snapshot(legacy)
