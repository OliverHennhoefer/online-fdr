from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pytest

from online_fdr.p_values import WeightedGaiPlusPlus


@pytest.mark.parametrize("name", ["prior_weight", "penalty_weight"])
@pytest.mark.parametrize("value", [True, 10**400])
def test_weighted_validation_preserves_state_for_bool_and_overflowing_integer(
    name, value
):
    method = WeightedGaiPlusPlus(gamma_horizon=2)
    before = method.snapshot()
    with pytest.raises(ValueError, match=name):
        method.test_one_detail(0.001, **{name: value})
    assert method.snapshot() == before


@pytest.mark.parametrize("decay", [True, "0.95", 10**400, math.nan, math.inf])
def test_weighted_decay_uses_finite_numeric_validation(decay):
    with pytest.raises(ValueError, match="decay"):
        WeightedGaiPlusPlus(decay=decay)


@pytest.mark.parametrize("alpha,wealth", [(0.05, 0.049), (0.5, 0.49)])
@pytest.mark.parametrize("penalty", [0.1, 0.5, 1.0, 10.0, 100.0])
def test_one_null_weighted_fdr_stays_within_budget(alpha, wealth, penalty):
    method = WeightedGaiPlusPlus(alpha=alpha, wealth=wealth, gamma_horizon=1)
    detail = method.test_one_detail(1.0, prior_weight=1000.0, penalty_weight=penalty)

    threshold = detail.rejection_threshold
    assert threshold is not None
    # For one Uniform null, weighted FDP on rejection is min(penalty, 1).
    exact_weighted_fdr = min(penalty, 1.0) * min(threshold, 1.0)
    assert exact_weighted_fdr <= alpha
    assert threshold == pytest.approx(wealth / (penalty * (1 - alpha) + wealth))
    assert not detail.rejected


@pytest.mark.parametrize("decay", [1.0, 0.95])
def test_every_weighted_reward_satisfies_both_paper_bounds(decay):
    rng = random.Random(194)
    method = WeightedGaiPlusPlus(decay=decay, gamma_horizon=200)
    for index in range(100):
        first = not method.reject_idx
        penalty = 1.0 if first else 10 ** rng.uniform(-2, 2)
        prior = 10 ** rng.uniform(-2, 3)
        detail = method.test_one_detail(
            0.0 if index % 3 == 0 else rng.random(), prior, penalty
        )
        phi = method.phi_history[-1]
        psi = method.psi_history[-1]
        reward_budget = method.target_level * penalty - first * method.wealth0
        threshold = detail.rejection_threshold
        assert threshold is not None
        assert psi >= 0
        assert psi <= phi + reward_budget + 1e-12
        if threshold > 0:
            assert psi <= phi / threshold - penalty + reward_budget + 1e-12
        assert method.wealth >= 0


def test_infeasible_penalty_weight_rejects_before_state_changes():
    method = WeightedGaiPlusPlus()
    before = method.snapshot()
    with pytest.raises(ValueError, match="nonnegative reward"):
        method.test_one_detail(0.0, penalty_weight=0.1)
    assert method.snapshot() == before
    control = WeightedGaiPlusPlus()
    assert method.test_one_detail(0.0) == control.test_one_detail(0.0)
    assert method.snapshot() == control.snapshot()


@pytest.mark.parametrize(
    "decay,error_rate", [(1.0, "weighted FDR"), (0.95, "weighted mem-FDR")]
)
def test_weighted_error_target_is_preserved_in_details_and_snapshots(decay, error_rate):
    method = WeightedGaiPlusPlus(decay=decay)
    assert method.error_rate == error_rate
    assert method.test_one_detail(0.0, penalty_weight=100.0).error_rate == error_rate
    restored = WeightedGaiPlusPlus.from_snapshot(
        json.loads(json.dumps(method.snapshot()))
    )
    assert restored.error_rate == error_rate
    assert restored.test_one_detail(0.5).error_rate == error_rate


def test_legacy_weighted_snapshot_reports_its_actual_memory_target():
    snapshot = json.loads(
        (Path(__file__).parent / "fixtures/weighted_gai_schema1.json").read_text()
    )
    assert WeightedGaiPlusPlus.from_snapshot(snapshot).error_rate == "weighted mem-FDR"


def test_penalty_weighted_guarantee_does_not_claim_ordinary_fdr():
    method = WeightedGaiPlusPlus()
    assert method.test_one(0.0, penalty_weight=100.0)
    detail = method.test_one_detail(1.0)
    assert detail.rejection_threshold is not None
    ordinary_fdr = detail.rejection_threshold / 2
    weighted_fdr = detail.rejection_threshold / 101
    assert ordinary_fdr > method.target_level
    assert weighted_fdr <= method.target_level
    assert detail.error_rate == "weighted FDR"
