from __future__ import annotations

import pytest

from online_fdr.core.utils.static import bh
from online_fdr.p_values.batching.bh_official import BatchBHOfficial
from online_fdr.p_values.batching.by import BatchBY
from online_fdr.p_values.investing.lord.mem_decay import LORDMemoryDecay
from tests.parity_cases import batch_cases, sequential_cases

_AUTHOR_BATCH_BH_POLY_COEFFICIENT = 0.6079271388115668


def _author_batch_bh_gamma(j: int, batch_size: int) -> float:
    if batch_size < 100:
        return _AUTHOR_BATCH_BH_POLY_COEFFICIENT / (j**2)
    return 0.5 if j < 3 else 0.0


def _author_batch_bh_reference(
    batches: list[list[float]], alpha: float
) -> tuple[list[bool], list[float]]:
    r_pluses: list[int] = []
    r_sums: list[int] = []
    alpha_s: list[float] = []
    r_total = 0
    decisions: list[bool] = []

    for t, p_vals in enumerate(batches, start=1):
        batch_size = len(p_vals)
        if t == 1:
            alpha_t = alpha * _author_batch_bh_gamma(t, batch_size)
        else:
            beta_t = 0.0
            for s in range(t - 1):
                denominator = r_pluses[s] + r_sums[s]
                if denominator > 0:
                    beta_t += alpha_s[s] * r_pluses[s] / denominator
            gamma_sum = sum(
                _author_batch_bh_gamma(j, batch_size) for j in range(1, t + 1)
            )
            alpha_t = (alpha * gamma_sum - beta_t) * (
                (batch_size + r_total) / batch_size
            )

        num_reject, threshold = bh(p_vals, alpha_t)

        r_sums.append(r_total)
        for idx in range(t - 1):
            r_sums[idx] += num_reject
        r_total += num_reject
        alpha_s.append(alpha_t)

        r_plus = 0
        adjusted = list(p_vals)
        for idx, p_val in enumerate(adjusted):
            adjusted[idx] = 0.0
            r_plus = max(r_plus, bh(adjusted, alpha_t)[0])
            adjusted[idx] = p_val
        r_pluses.append(r_plus)

        decisions.extend(p_val <= threshold for p_val in p_vals)

    return decisions, alpha_s


def test_lord_memory_decay_long_sequence_regression() -> None:
    case = sequential_cases()["seq_long_mixed_v1"]
    method = LORDMemoryDecay(alpha=0.05, delta=0.99, eta=0.001)

    decisions: list[bool] = []
    alpha: list[float] = []
    for p_value in case.p_values:
        decisions.append(method.test_one(p_value))
        assert method.last_rejection_threshold is not None
        alpha.append(round(method.last_rejection_threshold, 12))

    assert sum(decisions) == 87
    assert alpha[:12] == [
        2.675839e-06,
        5.8191e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
        5e-07,
    ]
    assert alpha[-12:] == [
        1.890817e-06,
        1.87359e-06,
        1.856585e-06,
        1.839798e-06,
        1.823226e-06,
        1.806867e-06,
        1.790718e-06,
        1.774776e-06,
        1.759037e-06,
        1.7435e-06,
        1.728162e-06,
        1.71302e-06,
    ]


def test_batch_bh_official_long_sequence_regression() -> None:
    case = batch_cases()["batch_long_mixed_v1"]
    method = BatchBHOfficial(alpha=0.05)

    decisions: list[bool] = []
    start = 0
    for batch_size in case.batch_sizes:
        end = start + batch_size
        decisions.extend(method.test_batch(case.p_values[start:end]))
        start = end

    assert sum(decisions) == 203
    assert len(method.alpha_s) == 141
    assert round(sum(method.alpha_s), 12) == 4.599351707459


def test_batch_bh_official_matches_author_supplement_reference() -> None:
    batches = [
        [0.001, 0.02, 0.11, 0.7],
        [0.0005, 0.018, 0.3],
        [0.0001 if i in {0, 50} else 0.2 + i / 500 for i in range(101)],
        [0.002, 0.5, 0.9],
    ]
    method = BatchBHOfficial(alpha=0.05)

    decisions: list[bool] = []
    for batch in batches:
        decisions.extend(method.test_batch(batch))

    expected_decisions, expected_alpha = _author_batch_bh_reference(batches, 0.05)

    assert decisions == expected_decisions
    assert method.alpha_s == pytest.approx(expected_alpha, rel=0.0, abs=1e-15)


def test_batch_by_long_sequence_regression() -> None:
    case = batch_cases()["batch_long_mixed_v1"]
    method = BatchBY(alpha=0.05)

    decisions: list[bool] = []
    start = 0
    for batch_size in case.batch_sizes:
        end = start + batch_size
        decisions.extend(method.test_batch(case.p_values[start:end]))
        start = end

    assert sum(decisions) == 91
    assert len(method.alpha_s) == 141
    assert round(sum(method.alpha_s), 12) == 2.344898140949
