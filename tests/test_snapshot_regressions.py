from __future__ import annotations

import json
import math
from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from online_fdr.core.abstract.abstract_gamma_seq import AbstractGammaSequence
from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.abstract.abstract_spend_func import AbstractSpendFunc
from online_fdr.core.state import StatefulMethodMixin
from online_fdr.core.utils.sequence import (
    BatchBHAdaptiveGammaSequence,
    BatchBHHalfGammaSequence,
    BatchBHPolynomialGammaSequence,
    BatchGammaSequenceLarge,
    BatchGammaSequenceSmall,
    DefaultLondGammaSequence,
    DefaultLordGammaSequence,
    DefaultSaffronGammaSequence,
    DependentLordGammaSequence,
)
from online_fdr.e_values import ELond
from online_fdr.p_values import (
    Addis,
    AlphaSpending,
    Bonferroni,
    Saffron,
    WeightedGaiPlusPlus,
)
from online_fdr.p_values.spending.functions.lord_three import LordThree


class _SnapshotState(StatefulMethodMixin):
    def __init__(self, value: Any):
        self.value = value


def _json_round_trip(method):
    payload = json.loads(json.dumps(method.snapshot(), allow_nan=False))
    return type(method).from_snapshot(payload)


def _helper_value(
    helper: AbstractGammaSequence | AbstractSpendFunc, index: int
) -> float:
    if isinstance(helper, AbstractSpendFunc):
        return helper.spend(index - 1, alpha=0.05)
    if isinstance(helper, DefaultSaffronGammaSequence):
        return helper.calc_gamma(index)
    return helper.calc_gamma(index, alpha=0.05, batch_size=10)


@pytest.mark.parametrize(
    ("helper", "kind", "params"),
    [
        (
            DefaultLondGammaSequence(c=0.07720838),
            "DefaultLondGammaSequence",
            {"c": 0.07720838},
        ),
        (
            DefaultLordGammaSequence(c=0.07720838),
            "DefaultLordGammaSequence",
            {"c": 0.07720838},
        ),
        (
            DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658),
            "DefaultSaffronGammaSequence",
            {"gamma_exp": 1.6, "c": 0.4374901658},
        ),
        (
            DependentLordGammaSequence(c=0.07720838, b0=0.025),
            "DependentLordGammaSequence",
            {"c": 0.07720838, "b0": 0.025},
        ),
        (
            BatchGammaSequenceSmall(gamma_exp=1.6),
            "BatchGammaSequenceSmall",
            {"gamma_exp": 1.6},
        ),
        (BatchGammaSequenceLarge(), "BatchGammaSequenceLarge", {}),
        (BatchBHPolynomialGammaSequence(), "BatchBHPolynomialGammaSequence", {}),
        (BatchBHHalfGammaSequence(), "BatchBHHalfGammaSequence", {}),
        (BatchBHAdaptiveGammaSequence(), "BatchBHAdaptiveGammaSequence", {}),
        (Bonferroni(k=4), "Bonferroni", {"k": 4}),
        (LordThree(k=4), "LordThreeSpend", {"k": 4}),
    ],
)
def test_builtin_helpers_keep_schema_one_encoding_and_behavior(
    helper: AbstractGammaSequence | AbstractSpendFunc,
    kind: str,
    params: dict[str, float | int],
) -> None:
    method = _SnapshotState(helper)
    snapshot = method.snapshot()
    assert snapshot["schema_version"] == 1
    assert snapshot["state"]["value"] == {
        "__online_fdr_type__": "helper",
        "kind": kind,
        "params": params,
    }

    restored = _json_round_trip(method).value
    assert type(restored) is type(helper)
    for index in range(1, 4):
        assert _helper_value(restored, index) == _helper_value(helper, index)


class _CustomLondGamma(DefaultLondGammaSequence):
    def calc_gamma(self, j: int, **kwargs: object) -> float:
        return 1.0


class _CustomBonferroni(Bonferroni):
    def spend(self, index: int, alpha: float) -> float:
        return alpha / 10


def test_snapshot_rejects_gamma_subclass_instead_of_changing_next_decision() -> None:
    method = ELond(alpha=0.05, gamma_seq=_CustomLondGamma(c=0.07720838))
    assert method.test_one(25.0) is True

    with pytest.raises(TypeError, match="'seq'.*helper subclass _CustomLondGamma"):
        method.snapshot()


def test_snapshot_rejects_spending_subclass_with_field_path() -> None:
    method = AlphaSpending(alpha=0.05, spend_func=_CustomBonferroni(k=4))
    with pytest.raises(TypeError, match="'rule'.*helper subclass _CustomBonferroni"):
        method.snapshot()


@pytest.mark.parametrize(
    ("value", "expected", "scalar_type"),
    [
        (np.bool_(True), True, bool),
        (np.int32(-3), -3, int),
        (np.int64(7), 7, int),
        (np.uint64(2**64 - 1), 2**64 - 1, int),
        (np.float32(0.25), 0.25, float),
        (np.float64(0.125), 0.125, float),
    ],
)
def test_numpy_scalar_state_normalizes_to_json_scalars(
    value: Any, expected: bool | int | float, scalar_type: type
) -> None:
    method = _SnapshotState({"scalars": [value], "keys": {np.int64(3): value}})
    restored = _json_round_trip(method)

    assert restored.value == {"scalars": [expected], "keys": {3: expected}}
    assert type(restored.value["scalars"][0]) is scalar_type
    assert type(next(iter(restored.value["keys"]))) is int


@pytest.mark.parametrize("value", [np.float64(math.inf), np.float64(-math.inf)])
def test_numpy_infinities_keep_existing_tagged_float_encoding(value: Any) -> None:
    method = _SnapshotState(value)
    assert method.snapshot()["state"]["value"] == {
        "__online_fdr_type__": "float",
        "value": "inf" if value > 0 else "-inf",
    }
    assert _json_round_trip(method).value == value


def test_numpy_nan_keeps_existing_tagged_float_encoding() -> None:
    method = _SnapshotState(np.float64(math.nan))
    assert method.snapshot()["state"]["value"] == {
        "__online_fdr_type__": "float",
        "value": "nan",
    }
    assert math.isnan(_json_round_trip(method).value)


@pytest.mark.parametrize("value", [np.array([0.1]), np.complex64(1 + 2j)])
def test_snapshot_does_not_generalize_scalar_support_to_arrays_or_objects(
    value: Any,
) -> None:
    with pytest.raises(TypeError, match="snapshot field 'value'.*unsupported object"):
        _SnapshotState(value).snapshot()


@pytest.mark.parametrize(
    "method_factory",
    [
        lambda: Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
        lambda: Saffron(alpha=0.05, wealth=0.025, lambda_=0.5),
        WeightedGaiPlusPlus,
    ],
    ids=["Addis", "Saffron", "WeightedGaiPlusPlus"],
)
def test_ndarray_stream_restart_preserves_future_levels_and_decisions(
    method_factory: Callable[[], AbstractSequentialTest],
) -> None:
    values = np.array([0.001, 0.5, 0.01, 0.9, 0.0005, 0.25, 0.0001, 0.7])
    method = method_factory()
    for value in values[:3]:
        method.test_one(value)
    restored = _json_round_trip(method)

    for value in values[3:]:
        assert method.test_one(value) == restored.test_one(value)
        assert method.last_test_level == pytest.approx(restored.last_test_level)
        assert method.last_rejection_threshold == pytest.approx(
            restored.last_rejection_threshold
        )
        assert method.num_hypotheses == restored.num_hypotheses

    assert method.snapshot() == restored.snapshot()
