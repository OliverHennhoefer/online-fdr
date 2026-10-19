from __future__ import annotations

import math

import numpy as np
import pytest

from online_fdr.core.utils import DefaultSaffronGammaSequence, MemoryDecayFDR
from online_fdr.p_values import AlphaSpending, Bonferroni, LordDependent, LordThree
from online_fdr.p_values.async_methods import SaffronAsync
from online_fdr.p_values.spending.functions.lord_three import (
    LordThree as LordThreeSpendFunc,
)


@pytest.mark.parametrize("factory", [Bonferroni, LordThreeSpendFunc])
@pytest.mark.parametrize(
    "horizon",
    [True, False, np.bool_(True), 0, -1, 0.5, 1.5, math.inf, math.nan, "2", None],
)
def test_spending_horizon_requires_a_positive_integer(factory, horizon):
    with pytest.raises(ValueError, match="k must be a positive integer"):
        factory(k=horizon)


@pytest.mark.parametrize("factory", [Bonferroni, LordThreeSpendFunc])
@pytest.mark.parametrize("horizon", [1, 3])
def test_spending_stays_within_budget_and_stops_without_changing_state(
    factory, horizon
):
    method = AlphaSpending(alpha=0.05, spend_func=factory(k=horizon))
    levels = [method.test_one_detail(0.5).test_level for _ in range(horizon)]
    assert all(level is not None and level >= 0 for level in levels)
    assert sum(levels) <= 0.05
    assert method.num_hypotheses == horizon

    before = method.snapshot()
    with pytest.raises(ValueError, match="horizon"):
        method.test_one(0.0)
    assert method.snapshot() == before


@pytest.mark.parametrize("factory", [Bonferroni, LordThreeSpendFunc])
@pytest.mark.parametrize("integer_type", [np.int32, np.int64, np.uint64])
def test_spending_numpy_integer_horizons_match_builtin_counts(factory, integer_type):
    spending = factory(k=integer_type(3))
    method = AlphaSpending(alpha=0.05, spend_func=spending)
    control = AlphaSpending(alpha=0.05, spend_func=factory(k=3))

    assert type(spending.k) is int
    for p_val in (0.0, 0.9, 0.01):
        assert method.test_one_detail(p_val) == control.test_one_detail(p_val)
    assert method.snapshot() == control.snapshot()


@pytest.mark.parametrize("real_type", [np.float32, np.float64])
def test_numpy_real_configuration_matches_builtin_scalars(real_type):
    delta, offset = real_type(0.9), real_type(0.2)
    tracker = MemoryDecayFDR(delta=delta, offset=offset)
    control = MemoryDecayFDR(delta=float(delta), offset=float(offset))
    assert type(tracker.delta) is float
    assert type(tracker.offset) is float
    for rejected, alternative in ((True, False), (False, False), (True, True)):
        assert tracker.score_one(rejected, alternative) == control.score_one(
            rejected, alternative
        )

    exponent, constant = real_type(1.6), real_type(0.4)
    sequence = DefaultSaffronGammaSequence(gamma_exp=exponent, c=constant)
    reference = DefaultSaffronGammaSequence(
        gamma_exp=float(exponent), c=float(constant)
    )
    assert [sequence.calc_gamma(j) for j in range(1, 5)] == [
        reference.calc_gamma(j) for j in range(1, 5)
    ]


@pytest.mark.parametrize("factory", [LordThree, LordDependent])
@pytest.mark.parametrize("real_type", [np.float32, np.float64])
def test_lord_numpy_rewards_match_builtin_configuration(factory, real_type):
    reward = real_type(0.025)
    method = factory(alpha=0.05, wealth=0.02, reward=reward)
    control = factory(alpha=0.05, wealth=0.02, reward=float(reward))
    assert type(method.reward) is float
    for p_val in (0.0, 0.1, 0.001, 0.9):
        assert method.test_one_detail(p_val) == control.test_one_detail(p_val)
    assert method.snapshot() == control.snapshot()


@pytest.mark.parametrize("constant", [math.nan, math.inf, -math.inf, -0.4, "0.4", True])
def test_saffron_gamma_rejects_invalid_constants(constant):
    with pytest.raises(ValueError, match="c.*finite|c.*nonnegative"):
        DefaultSaffronGammaSequence(gamma_exp=1.6, c=constant)


@pytest.mark.parametrize(
    "exponent", [math.nan, math.inf, -math.inf, 0.0, 1.0, "1.6", True]
)
def test_saffron_gamma_rejects_invalid_exponents(exponent):
    with pytest.raises(ValueError, match="gamma_exp"):
        DefaultSaffronGammaSequence(gamma_exp=exponent, c=0.4)


def test_valid_gamma_parameters_remain_usable_in_async_methods():
    sequence = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
    method = SaffronAsync(gamma_seq=sequence)
    assert method.start_test().test_level == pytest.approx(
        (1 - 0.5) * 0.025 * sequence.calc_gamma(1)
    )
    assert DefaultSaffronGammaSequence(gamma_exp=2, c=0).calc_gamma(1) == 0.0


@pytest.mark.parametrize("constant", [0.0, 0.4])
def test_large_finite_gamma_exponent_remains_usable_for_async_starts(constant):
    sequence = DefaultSaffronGammaSequence(gamma_exp=1e308, c=constant)
    method = SaffronAsync(gamma_seq=sequence)
    assert method.start_test().test_level == pytest.approx(0.0125 * constant)
    assert method.start_test().test_level == 0.0
    assert method.num_hypotheses == 2


def test_gamma_recovers_finite_value_from_overflowing_denominator():
    sequence = DefaultSaffronGammaSequence(gamma_exp=1024, c=1e308)
    assert sequence.calc_gamma(2) == pytest.approx(0.5562684646268004, rel=1e-12)


@pytest.mark.parametrize("factory", [LordThree, LordDependent])
@pytest.mark.parametrize(
    "reward", [math.nan, math.inf, -math.inf, 0, -0.01, "0.025", True]
)
def test_lord_rewards_require_finite_positive_numbers(factory, reward):
    with pytest.raises(ValueError, match="reward"):
        factory(alpha=0.05, wealth=0.025, reward=reward)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("delta", math.nan),
        ("delta", math.inf),
        ("delta", -0.1),
        ("delta", 1.1),
        ("delta", "0.9"),
        ("delta", True),
        ("offset", math.nan),
        ("offset", math.inf),
        ("offset", -0.1),
        ("offset", "0.1"),
        ("offset", True),
    ],
)
def test_memory_decay_rejects_invalid_configuration(name, value):
    with pytest.raises(ValueError, match=name):
        MemoryDecayFDR(**{name: value})


@pytest.mark.parametrize("delta", [0.0, 0.4, 0.95, 1.0])
@pytest.mark.parametrize("offset", [0.0, 0.2])
@pytest.mark.parametrize("cumulative", [False, True])
def test_memory_decay_scores_match_independent_weighted_history(
    delta, offset, cumulative
):
    events = [(i % 3 == 0, i % 5 == 0) for i in range(30)]
    tracker = MemoryDecayFDR(delta=delta, offset=offset)
    tracker.cumulative = cumulative
    expected = []
    for end, (rejected, alternative) in enumerate(events, start=1):
        weights = [delta ** (end - i - 1) for i in range(end)]
        false_positives = sum(
            weight * (decision and not truth)
            for weight, (decision, truth) in zip(weights, events[:end])
        )
        rejections = sum(
            weight * decision for weight, (decision, _) in zip(weights, events[:end])
        )
        expected.append(false_positives / (max(rejections, 1) + offset))
        observed = tracker.score_one(rejected, alternative)
        assert observed == pytest.approx(expected if cumulative else expected[-1])
    assert all(0 <= score <= 1 for score in expected)


def test_memory_decay_owns_configuration_and_history_when_switching_output():
    tracker = MemoryDecayFDR(delta=0.5, offset=0.2)
    first = tracker.score_one(True, False)
    tracker.labels.append(False)
    tracker.ground_truth[0] = True
    assert tracker.labels == [True]
    assert tracker.ground_truth == [False]

    with pytest.raises(AttributeError):
        tracker.delta = 0.1
    with pytest.raises(AttributeError):
        tracker.offset = 0.1
    with pytest.raises(AttributeError):
        tracker.labels = []
    with pytest.raises(AttributeError):
        tracker.ground_truth = []

    tracker.cumulative = True
    history = tracker.score_one(False, False)
    assert isinstance(history, list)
    assert history == pytest.approx([first, 0.5 / 1.2])
    history[0] = -1.0
    tracker.cumulative = False
    third = tracker.score_one(True, True)
    tracker.cumulative = True
    fourth = tracker.score_one(False, False)
    assert isinstance(fourth, list)
    assert fourth == pytest.approx([first, 0.5 / 1.2, third, 0.125 / 1.2])
    assert tracker.labels == [True, False, True, False]
    assert tracker.ground_truth == [False, False, True, False]
