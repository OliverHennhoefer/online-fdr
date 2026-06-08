from __future__ import annotations

import math

import pytest

from online_fdr.p_values.investing.alpha.weighted_gai_plus_plus import (
    WeightedGaiPlusPlus,
)


def _author_gamma_values(horizon: int) -> list[float]:
    raw = [
        math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j))))
        for j in range(1, horizon + 1)
    ]
    total = sum(raw)
    return [value / total for value in raw]


def _author_weighted_reference(
    p_values: list[float],
    prior_weights: list[float],
    penalty_weights: list[float],
    *,
    alpha: float,
    wealth: float,
    decay: float,
    horizon: int,
) -> tuple[list[bool], list[float], list[float]]:
    gamma = _author_gamma_values(horizon)
    current_wealth = wealth
    next_alpha = gamma[0] * wealth
    first = False
    rejections: list[int] = []
    psi_rejections: list[float] = []
    decisions: list[bool] = []
    thresholds: list[float] = []
    used_prior_weights: list[float] = []

    for idx, (p_val, prior_weight, penalty_weight) in enumerate(
        zip(p_values, prior_weights, penalty_weights), start=1
    ):
        base_alpha = next_alpha
        first_flag = 0 if first else 1
        b_t = alpha - first_flag * wealth / penalty_weight
        phi = min(
            base_alpha, decay * current_wealth + (1 - decay) * first_flag * wealth
        )
        max_weight = phi * penalty_weight / ((1 - b_t) * base_alpha)
        prior_used = min(prior_weight, max_weight)
        ratio = penalty_weight / prior_used
        threshold = base_alpha / ratio
        psi = max(
            min(
                phi + penalty_weight * b_t,
                (phi / base_alpha) * ratio - penalty_weight + penalty_weight * b_t,
            ),
            0.0,
        )
        rejected = p_val < threshold
        if rejected:
            first = True
            rejections.append(idx)
            psi_rejections.append(psi)

        current_wealth = (
            decay * current_wealth
            + (1 - decay) * first_flag * wealth
            - phi
            + int(rejected) * psi
        )
        next_alpha = gamma[idx] * wealth
        for reject_idx, reject_psi in zip(rejections, psi_rejections):
            zero_distance = idx - reject_idx
            next_alpha += reject_psi * (decay**zero_distance) * gamma[zero_distance]

        decisions.append(rejected)
        thresholds.append(threshold)
        used_prior_weights.append(prior_used)

    return decisions, thresholds, used_prior_weights


def test_weighted_gai_plus_plus_matches_author_weighted_reference() -> None:
    p_values = [0.0005, 0.2, 0.001, 0.04, 0.0001, 0.8, 0.002]
    prior_weights = [1.0, 1.7, 0.8, 1.2, 2.0, 0.9, 1.4]
    penalty_weights = [1.0, 1.1, 0.95, 1.3, 1.0, 1.2, 0.9]
    method = WeightedGaiPlusPlus(
        alpha=0.05,
        wealth=0.025,
        decay=0.92,
        gamma_horizon=100,
    )

    decisions = [
        method.test_one(p_val, prior_weight=prior, penalty_weight=penalty)
        for p_val, prior, penalty in zip(p_values, prior_weights, penalty_weights)
    ]
    expected_decisions, expected_alpha, expected_prior = _author_weighted_reference(
        p_values,
        prior_weights,
        penalty_weights,
        alpha=0.05,
        wealth=0.025,
        decay=0.92,
        horizon=100,
    )

    assert decisions == expected_decisions
    assert method.alpha_history == pytest.approx(expected_alpha, rel=0.0, abs=1e-15)
    assert method.prior_weights_used == pytest.approx(
        expected_prior, rel=0.0, abs=1e-15
    )


def test_weighted_gai_plus_plus_defaults_match_explicit_unit_weights() -> None:
    p_values = [0.001, 0.2, 0.003, 0.8, 0.0004]
    implicit = WeightedGaiPlusPlus(alpha=0.05, wealth=0.025, gamma_horizon=100)
    explicit = WeightedGaiPlusPlus(alpha=0.05, wealth=0.025, gamma_horizon=100)

    assert [implicit.test_one(p_val) for p_val in p_values] == [
        explicit.test_one(p_val, prior_weight=1.0, penalty_weight=1.0)
        for p_val in p_values
    ]
    assert implicit.alpha_history == pytest.approx(explicit.alpha_history)


def test_higher_useful_prior_weight_increases_effective_threshold() -> None:
    baseline = WeightedGaiPlusPlus(alpha=0.05, wealth=0.025, gamma_horizon=100)
    weighted = WeightedGaiPlusPlus(alpha=0.05, wealth=0.025, gamma_horizon=100)

    baseline.test_one(0.5, prior_weight=1.0)
    weighted.test_one(0.5, prior_weight=2.0)

    assert weighted.prior_weights_used[0] > baseline.prior_weights_used[0]
    assert weighted.alpha_history[0] > baseline.alpha_history[0]
