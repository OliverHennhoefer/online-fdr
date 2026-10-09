from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from online_fdr.p_values import AddisAsync, SaffronAsync, WeightedGaiPlusPlus


@pytest.mark.parametrize("factory", [AddisAsync, SaffronAsync])
@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -0.1, 1.1, "bad"])
def test_invalid_synchronous_async_input_preserves_snapshot(factory, bad_value):
    method = factory()
    before = method.snapshot()
    with pytest.raises(ValueError):
        method.test_one(bad_value)
    assert method.snapshot() == before
    control = factory()
    assert method.test_one(0.001) == control.test_one(0.001)
    assert method.snapshot() == control.snapshot()


@pytest.mark.parametrize("factory", [AddisAsync, SaffronAsync])
def test_failed_async_start_does_not_consume_automatic_identifier(factory, monkeypatch):
    method = factory()
    before = method.snapshot()

    def fail_level(self, stage):
        raise ValueError("gamma horizon exceeded")

    with monkeypatch.context() as patch:
        patch.setattr(factory, "_calc_alpha_for_stage", fail_level)
        with pytest.raises(ValueError, match="horizon"):
            method.start_test()
    assert method.snapshot() == before
    assert method.start_test().test_id == 1


@pytest.mark.parametrize("factory", [AddisAsync, SaffronAsync])
def test_automatic_async_identifiers_skip_existing_explicit_identifiers(factory):
    method = factory()
    method.start_test(test_id=1)
    assert method.start_test().test_id == 2
    assert method.start_test().test_id == 3


@pytest.mark.parametrize("horizon", [1, 2, 3])
def test_weighted_gai_allows_last_test_and_preserves_state_at_exhaustion(horizon):
    method = WeightedGaiPlusPlus(gamma_horizon=horizon)
    for index in range(1, horizon + 1):
        detail = method.test_one_detail(0.0 if index % 2 else 0.9)
        assert detail.index == index
        assert len(method.decisions) == index
        assert len(method.wealth_history) == index + 1
    before = method.snapshot()
    with pytest.raises(ValueError, match="horizon"):
        method.test_one(0.1)
    assert method.snapshot() == before
    restored = WeightedGaiPlusPlus.from_snapshot(before)
    with pytest.raises(ValueError, match="horizon"):
        restored.test_one(0.1)
    assert restored.snapshot() == before


@pytest.mark.parametrize("name", ["prior_weight", "penalty_weight"])
@pytest.mark.parametrize(
    "bad_weight", [math.nan, math.inf, -math.inf, 0.0, -1.0, "bad"]
)
def test_weighted_gai_rejects_invalid_weights_before_any_transition(name, bad_weight):
    method = WeightedGaiPlusPlus()
    before = method.snapshot()
    with pytest.raises(ValueError, match=name):
        method.test_one_detail(0.001, **{name: bad_weight})
    assert method.snapshot() == before


@pytest.mark.parametrize("horizon", [True, 1.5, math.inf, math.nan, 0])
def test_weighted_gai_requires_a_positive_integer_horizon(horizon):
    with pytest.raises(ValueError, match="positive integer"):
        WeightedGaiPlusPlus(gamma_horizon=horizon)


def test_pre_refactor_schema_one_snapshot_preserves_weighted_continuation():
    snapshot = json.loads(
        (Path(__file__).parent / "fixtures/weighted_gai_schema1.json").read_text()
    )
    restored = WeightedGaiPlusPlus.from_snapshot(snapshot)
    control = WeightedGaiPlusPlus(
        alpha=0.05, wealth=0.025, decay=0.92, gamma_horizon=100
    )
    for value, prior, penalty in [
        (0.0005, 1.0, 1.0),
        (0.2, 1.7, 1.1),
        (0.001, 0.8, 0.95),
    ]:
        control.test_one(value, prior_weight=prior, penalty_weight=penalty)
    for value, prior, penalty in [
        (0.04, 1.2, 1.3),
        (0.0001, 2.0, 1.0),
        (0.8, 0.9, 1.2),
    ]:
        assert restored.test_one_detail(
            value, prior, penalty
        ) == control.test_one_detail(value, prior, penalty)
        assert restored.snapshot() == control.snapshot()
