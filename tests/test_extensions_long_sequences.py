from __future__ import annotations

from online_fdr.batching.bh_official import BatchBHOfficial
from online_fdr.batching.by import BatchBY
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay

from tests.parity_cases import batch_cases, sequential_cases


def test_lord_memory_decay_long_sequence_regression() -> None:
    case = sequential_cases()["seq_long_mixed_v1"]
    method = LORDMemoryDecay(alpha=0.05, delta=0.99, eta=0.001)

    decisions: list[bool] = []
    alpha: list[float] = []
    for p_value in case.p_values:
        decisions.append(method.test_one(p_value))
        assert method.alpha is not None
        alpha.append(round(method.alpha, 12))

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

    assert sum(decisions) == 261
    assert len(method.alpha_s) == 141
    assert round(sum(method.alpha_s), 12) == 12.570189427201


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
