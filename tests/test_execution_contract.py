from collections.abc import Callable

import pytest

from online_fdr.core.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.e_values import EBH, ELond
from online_fdr.p_values import (
    Addis,
    BatchBH,
    BatchBHOfficial,
    BatchBY,
    BatchPRDS,
    BatchStoreyBH,
    NaiveTest,
    WeightedGaiPlusPlus,
)

BATCH_FACTORIES: list[Callable[[], AbstractBatchingTest]] = [
    lambda: BatchBH(alpha=0.05),
    lambda: BatchBHOfficial(alpha=0.05),
    lambda: BatchBY(alpha=0.05),
    lambda: BatchPRDS(alpha=0.05),
    lambda: BatchStoreyBH(alpha=0.05, lambda_=0.5),
    lambda: EBH(alpha=0.05),
]


@pytest.mark.parametrize("factory", BATCH_FACTORIES)
def test_batch_boolean_and_detail_apis_have_identical_state(factory) -> None:
    plain, detailed = factory(), factory()
    for values in [[], [0.001, 0.2, 0.8], [], [0.01, 0.9]]:
        decisions = plain.test_batch(values)
        detail = detailed.test_batch_detail(values)
        assert detail.rejected == tuple(decisions)
        assert detail.values == tuple(values)
        assert detail.batch_index == plain.num_batches == detailed.num_batches
        assert plain.num_hypotheses == detailed.num_hypotheses
        assert detail.test_level == plain.last_test_level
        assert detail.rejection_threshold == plain.last_rejection_threshold
        assert plain.snapshot() == detailed.snapshot()


@pytest.mark.parametrize("factory", BATCH_FACTORIES)
@pytest.mark.parametrize("bad_value", ["0.001", "x", None, float("nan")])
@pytest.mark.parametrize("detailed", [False, True])
def test_invalid_batch_does_not_change_state(factory, bad_value, detailed) -> None:
    method = factory()
    method.test_batch([0.001, 0.2])
    before = method.snapshot()
    test_batch = method.test_batch_detail if detailed else method.test_batch
    with pytest.raises(ValueError):
        test_batch([0.001, bad_value])
    assert method.snapshot() == before


@pytest.mark.parametrize(
    ("factory", "values"),
    [
        (lambda: Addis(0.05, 0.025, 0.25, 0.5), [0.001, 0.2, 0.8]),
        (lambda: NaiveTest(0.05), [0.001, 0.2, 0.05]),
        (lambda: WeightedGaiPlusPlus(), [0.001, 0.2, 0.8]),
        (lambda: ELond(0.05), [1000.0, 1.0, 5000.0]),
    ],
)
def test_sequential_boolean_and_detail_apis_have_identical_state(
    factory: Callable[[], AbstractSequentialTest], values: list[float]
) -> None:
    plain, detailed = factory(), factory()
    for value in values:
        decision = plain.test_one(value)
        detail = detailed.test_one_detail(value)
        assert detail.rejected is decision
        assert detail.value == value
        assert detail.index == plain.num_hypotheses == detailed.num_hypotheses
        assert detail.test_level == plain.last_test_level
        assert detail.rejection_threshold == plain.last_rejection_threshold
        assert plain.snapshot() == detailed.snapshot()


def test_e_value_keyword_arguments_remain_supported() -> None:
    sequential = ELond(alpha=0.05)
    assert sequential.test_one(e_value=1000.0) is True
    assert sequential.test_one_detail(e_value=1.0).index == 2

    batch = EBH(alpha=0.05)
    assert batch.test_batch(e_values=[1000.0]) == [True]
    assert batch.test_batch_detail(e_values=[1.0]).batch_index == 2


def test_elond_restores_original_schema_one_level_field() -> None:
    snapshot = {
        "schema_version": 1,
        "method": "ELond",
        "state": {
            "target_level": 0.05,
            "_num_hypotheses": 1,
            "num_reject": 1,
            "_current_level": 0.002675838545630043,
            "_last_rejection_threshold": 373.7146255079989,
            "seq": {
                "__online_fdr_type__": "helper",
                "kind": "DefaultLondGammaSequence",
                "params": {"c": 0.07720838},
            },
        },
    }
    restored = ELond.from_snapshot(snapshot)
    original = ELond(alpha=0.05)
    original.test_one(1000.0)
    assert restored.current_level == snapshot["state"]["_current_level"]
    assert (
        restored.last_rejection_threshold
        == snapshot["state"]["_last_rejection_threshold"]
    )
    assert restored.test_one_detail(1.0) == original.test_one_detail(1.0)
