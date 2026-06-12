from __future__ import annotations

import math

from online_fdr.core.utils.evaluation import MemoryDecayFDR
from online_fdr.core.utils.sequence import DefaultLordGammaSequence
from online_fdr.p_values.investing.lord.mem_decay import LORDMemoryDecay
from tests.parity_cases import sequential_cases


def _paper_lord_memory_decay_threshold(
    *,
    t: int,
    rejections: list[int],
    alpha: float,
    delta: float,
    eta: float,
    lag: int,
    seq: DefaultLordGammaSequence,
) -> float:
    threshold = alpha * eta * max(seq.calc_gamma(t), 1 - delta)
    for rejection_time in rejections:
        time_diff = t - rejection_time - lag
        if time_diff > 0:
            threshold += alpha * (delta**time_diff) * seq.calc_gamma(time_diff)
    return threshold


def _author_decay_lord_stream(
    *,
    p_values: list[float],
    alpha: float,
    delta: float,
    eta: float,
    gamma_size: int,
    c: float = 0.07720838,
) -> tuple[list[bool], list[float]]:
    base_gamma = [
        c * math.log(max(t, 2)) / (t * math.exp(math.sqrt(math.log(t))))
        for t in range(1, gamma_size + 1)
    ]
    gamma_sum = sum(base_gamma)
    gamma = [value / gamma_sum for value in base_gamma]

    def gamma_at(t: int) -> float:
        return gamma[t - 1] if 1 <= t <= gamma_size else 0.0

    decisions: list[bool] = []
    thresholds: list[float] = []
    rejections: list[int] = []
    for t, p_value in enumerate(p_values, start=1):
        threshold = alpha * eta * max(gamma_at(t), 1 - delta)
        for rejection_time in rejections:
            time_diff = t - rejection_time
            if time_diff > 0:
                threshold += alpha * (delta**time_diff) * gamma_at(time_diff)

        # Matches reference repository policy (`p < alpha_t`).
        decision = p_value < threshold
        if decision:
            rejections.append(t)

        decisions.append(decision)
        thresholds.append(threshold)
    return decisions, thresholds


def _author_score_mfdr(
    *,
    labels: list[bool],
    ground_truth: list[bool],
    delta: float,
    offset: float,
    cumulative: bool,
) -> float | list[float]:
    fp = [label and (not truth) for label, truth in zip(labels, ground_truth)]
    deltas = [delta ** float(i) for i in range(len(labels))]

    v_t = [
        sum(
            fp[i] * deltas[j - i]
            for i in range(max(0, j - len(deltas) + 1), min(j + 1, len(fp)))
        )
        for j in range(len(fp) + len(deltas) - 1)
    ][: len(labels)]
    r_t = [
        sum(
            labels[i] * deltas[j - i]
            for i in range(max(0, j - len(deltas) + 1), min(j + 1, len(labels)))
        )
        for j in range(len(labels) + len(deltas) - 1)
    ][: len(labels)]

    if not cumulative:
        return float(v_t[-1] / (max(r_t[-1], 1) + offset))

    return [float(v / (max(r, 1) + offset)) for v, r in zip(v_t, r_t)]


def test_lord_memory_decay_matches_paper_equation_no_lag() -> None:
    method = LORDMemoryDecay(alpha=0.05, delta=0.99, eta=0.3, l=0)
    seq = DefaultLordGammaSequence(c=0.07720838)
    p_values = [0.8, 0.6, 1e-12, 0.7, 0.9, 1e-12, 0.5, 0.02, 0.4, 0.9]

    rejections: list[int] = []
    for t, p_value in enumerate(p_values, start=1):
        expected_alpha = _paper_lord_memory_decay_threshold(
            t=t,
            rejections=rejections,
            alpha=0.05,
            delta=0.99,
            eta=0.3,
            lag=0,
            seq=seq,
        )
        decision = method.test_one(p_value)

        assert method.last_rejection_threshold is not None
        assert math.isclose(
            method.last_rejection_threshold, expected_alpha, rel_tol=0.0, abs_tol=1e-15
        )

        if decision:
            rejections.append(t)

    assert rejections == [3, 6]


def test_lord_memory_decay_matches_paper_equation_with_lag() -> None:
    method = LORDMemoryDecay(alpha=0.05, delta=0.99, eta=0.2, l=2)
    seq = DefaultLordGammaSequence(c=0.07720838)
    p_values = [0.9, 0.0, 1.0, 1.0, 1.0, 1.0]

    rejections: list[int] = []
    for t, p_value in enumerate(p_values, start=1):
        expected_alpha = _paper_lord_memory_decay_threshold(
            t=t,
            rejections=rejections,
            alpha=0.05,
            delta=0.99,
            eta=0.2,
            lag=2,
            seq=seq,
        )
        decision = method.test_one(p_value)

        assert method.last_rejection_threshold is not None
        assert math.isclose(
            method.last_rejection_threshold, expected_alpha, rel_tol=0.0, abs_tol=1e-15
        )

        if t in (3, 4):
            base_only = 0.05 * 0.2 * max(seq.calc_gamma(t), 1 - 0.99)
            assert math.isclose(
                method.last_rejection_threshold, base_only, rel_tol=0.0, abs_tol=1e-15
            )
        if t == 5:
            base_only = 0.05 * 0.2 * max(seq.calc_gamma(t), 1 - 0.99)
            first_contribution = 0.05 * (0.99**1) * seq.calc_gamma(1)
            assert math.isclose(
                method.last_rejection_threshold,
                base_only + first_contribution,
                rel_tol=0.0,
                abs_tol=1e-15,
            )

        if decision:
            rejections.append(t)

    assert rejections == [2]


def test_lord_memory_decay_boundary_policy_is_less_or_equal() -> None:
    method = LORDMemoryDecay(alpha=0.05, delta=0.99, eta=0.001, l=0)

    first_threshold = 0.05 * 0.001 * max(method.seq.calc_gamma(1), 1 - 0.99)
    decision = method.test_one(first_threshold)

    assert method.last_rejection_threshold is not None
    assert math.isclose(
        method.last_rejection_threshold, first_threshold, rel_tol=0.0, abs_tol=1e-15
    )
    assert decision is True

    # The author implementation uses strict inequality (`p < alpha_t`).
    assert (first_threshold < first_threshold) is False


def test_lord_memory_decay_diverges_from_author_default_gamma_policy() -> None:
    p_values = sequential_cases()["seq_long_mixed_v1"].p_values

    local_method = LORDMemoryDecay(alpha=0.05, delta=0.99, eta=0.001, l=0)
    local_decisions: list[bool] = []
    local_thresholds: list[float] = []
    for p_value in p_values:
        local_decisions.append(local_method.test_one(p_value))
        assert local_method.last_rejection_threshold is not None
        local_thresholds.append(local_method.last_rejection_threshold)

    author_decisions, author_thresholds = _author_decay_lord_stream(
        p_values=p_values,
        alpha=0.05,
        delta=0.99,
        eta=0.001,
        gamma_size=100,
    )

    decision_matches = sum(
        int(local_decision == author_decision)
        for local_decision, author_decision in zip(local_decisions, author_decisions)
    )
    max_abs_threshold_diff = max(
        abs(local_threshold - author_threshold)
        for local_threshold, author_threshold in zip(
            local_thresholds, author_thresholds
        )
    )

    assert sum(local_decisions) == 87
    assert sum(author_decisions) == 130
    assert decision_matches == 1157
    assert math.isclose(
        max_abs_threshold_diff,
        0.018539034568175242,
        rel_tol=0.0,
        abs_tol=1e-15,
    )
    assert (
        next(
            i
            for i, (local_decision, author_decision) in enumerate(
                zip(local_decisions, author_decisions),
                start=1,
            )
            if local_decision != author_decision
        )
        == 187
    )


def test_memory_decay_fdr_matches_author_score_non_cumulative() -> None:
    labels = [False, False, True, False, True, True]
    ground_truth = [False, True, False, False, True, False]

    tracker = MemoryDecayFDR(delta=0.95, offset=0.2)
    observed: list[float] = []
    expected: list[float] = []
    for idx, (label, truth) in enumerate(zip(labels, ground_truth), start=1):
        observed_value = tracker.score_one(label, truth)
        expected_value = _author_score_mfdr(
            labels=labels[:idx],
            ground_truth=ground_truth[:idx],
            delta=0.95,
            offset=0.2,
            cumulative=False,
        )
        assert isinstance(observed_value, float)
        assert isinstance(expected_value, float)
        observed.append(observed_value)
        expected.append(expected_value)

    assert observed == expected
    # At t=1 denominator floor uses max(r_t, 1), so value is exactly 0.
    assert observed[0] == 0.0


def test_memory_decay_fdr_matches_author_score_cumulative() -> None:
    labels = [True, False, True, True]
    ground_truth = [True, False, False, True]

    tracker = MemoryDecayFDR(delta=0.9, offset=0.1)
    tracker.cumulative = True

    for idx, (label, truth) in enumerate(zip(labels, ground_truth), start=1):
        observed = tracker.score_one(label, truth)
        expected = _author_score_mfdr(
            labels=labels[:idx],
            ground_truth=ground_truth[:idx],
            delta=0.9,
            offset=0.1,
            cumulative=True,
        )
        assert isinstance(observed, list)
        assert isinstance(expected, list)
        assert observed == expected
