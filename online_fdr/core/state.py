from __future__ import annotations

import json
import math
from collections.abc import Mapping
from functools import cache
from typing import Any

import numpy as np

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

_TYPE_KEY = "__online_fdr_type__"
_HELPER_KEY = "helper"


class StatefulMethodMixin:
    """Versioned snapshot support for stateful testing methods."""

    _snapshot_schema_version = 1

    def snapshot(self) -> dict[str, Any]:
        """Return an opaque, versioned snapshot for persistence."""
        payload = {
            "schema_version": self._snapshot_schema_version,
            "method": self.__class__.__name__,
            "state": _serialize_state(self._snapshot_state()),
        }
        json.dumps(payload, allow_nan=False)
        return payload

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]):
        """Restore an instance from :meth:`snapshot` output."""
        if snapshot.get("schema_version") != cls._snapshot_schema_version:
            raise ValueError("unsupported snapshot schema_version")
        if snapshot.get("method") != cls.__name__:
            raise ValueError("snapshot class does not match this method")
        state = snapshot.get("state")
        if not isinstance(state, dict):
            raise ValueError("snapshot state must be a dictionary")

        instance = cls.__new__(cls)
        instance.__dict__.update(cls._restore_snapshot_state(_deserialize_state(state)))
        return instance

    def _snapshot_state(self) -> dict[str, Any]:
        return dict(self.__dict__)

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        return state


def _serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    return {key: _serialize_value(value, key) for key, value in state.items()}


def _deserialize_state(state: dict[str, Any]) -> dict[str, Any]:
    return {key: _deserialize_value(value) for key, value in state.items()}


def _serialize_value(value: Any, path: str) -> Any:
    helper = _serialize_helper(value, path)
    if helper is not None:
        return helper
    if isinstance(value, np.bool_):
        value = bool(value)
    elif isinstance(value, np.integer):
        value = int(value)
    elif isinstance(value, np.floating):
        value = float(value)
    if value is None or isinstance(value, bool | int | str):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        if math.isnan(value):
            label = "nan"
        elif value > 0:
            label = "inf"
        else:
            label = "-inf"
        return {_TYPE_KEY: "float", "value": label}
    if isinstance(value, list):
        return [_serialize_value(item, f"{path}[]") for item in value]
    if isinstance(value, tuple):
        return {
            _TYPE_KEY: "tuple",
            "items": [_serialize_value(item, f"{path}[]") for item in value],
        }
    if isinstance(value, set):
        return {
            _TYPE_KEY: "set",
            "items": [
                _serialize_value(item, f"{path}[]") for item in sorted(value, key=repr)
            ],
        }
    if isinstance(value, Mapping):
        if all(isinstance(key, str) for key in value) and _TYPE_KEY not in value:
            return {
                key: _serialize_value(item, f"{path}.{key}")
                for key, item in value.items()
            }
        return {
            _TYPE_KEY: "dict",
            "items": [
                [
                    _serialize_value(key, f"{path}.<key>"),
                    _serialize_value(item, f"{path}[{key!r}]"),
                ]
                for key, item in value.items()
            ],
        }
    raise TypeError(
        f"snapshot field {path!r} contains unsupported object "
        f"of type {type(value).__name__}"
    )


def _deserialize_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_deserialize_value(item) for item in value]
    if isinstance(value, dict):
        value_type = value.get(_TYPE_KEY)
        if value_type is None:
            return {key: _deserialize_value(item) for key, item in value.items()}
        if value_type == "tuple":
            return tuple(_deserialize_value(item) for item in value["items"])
        if value_type == "set":
            return {_deserialize_value(item) for item in value["items"]}
        if value_type == "dict":
            return {
                _deserialize_value(key): _deserialize_value(item)
                for key, item in value["items"]
            }
        if value_type == "float":
            label = value["value"]
            if label == "inf":
                return math.inf
            if label == "-inf":
                return -math.inf
            if label == "nan":
                return math.nan
            raise ValueError(f"unsupported encoded float value: {label!r}")
        if value_type == _HELPER_KEY:
            return _deserialize_helper(value)
        raise ValueError(f"unsupported snapshot value type: {value_type!r}")
    return value


@cache
def _helper_codecs() -> dict[type[Any], tuple[str, tuple[str, ...]]]:
    # Spending methods import this module through their base class, so load their
    # helper types only when a snapshot actually contains a helper.
    from online_fdr.p_values.spending.functions.bonferroni import Bonferroni
    from online_fdr.p_values.spending.functions.lord_three import LordThree

    return {
        DefaultLondGammaSequence: ("DefaultLondGammaSequence", ("c",)),
        DefaultLordGammaSequence: ("DefaultLordGammaSequence", ("c",)),
        DefaultSaffronGammaSequence: (
            "DefaultSaffronGammaSequence",
            ("gamma_exp", "c"),
        ),
        DependentLordGammaSequence: ("DependentLordGammaSequence", ("c", "b0")),
        BatchGammaSequenceSmall: ("BatchGammaSequenceSmall", ("gamma_exp",)),
        BatchGammaSequenceLarge: ("BatchGammaSequenceLarge", ()),
        BatchBHPolynomialGammaSequence: ("BatchBHPolynomialGammaSequence", ()),
        BatchBHHalfGammaSequence: ("BatchBHHalfGammaSequence", ()),
        BatchBHAdaptiveGammaSequence: ("BatchBHAdaptiveGammaSequence", ()),
        Bonferroni: ("Bonferroni", ("k",)),
        LordThree: ("LordThreeSpend", ("k",)),
    }


def _serialize_helper(value: Any, path: str) -> dict[str, Any] | None:
    codecs = _helper_codecs()
    codec = codecs.get(type(value))
    if codec is None:
        if isinstance(value, tuple(codecs)):
            raise TypeError(
                f"snapshot field {path!r} contains unsupported helper subclass "
                f"{type(value).__name__}; only registered exact helper types "
                "can be restored without changing behavior"
            )
        return None
    kind, fields = codec
    return _helper_payload(kind, {field: getattr(value, field) for field in fields})


def _helper_payload(kind: str, params: dict[str, Any]) -> dict[str, Any]:
    return {
        _TYPE_KEY: _HELPER_KEY,
        "kind": kind,
        "params": _serialize_value(params, f"{kind}.params"),
    }


def _deserialize_helper(value: dict[str, Any]) -> Any:
    kind = value["kind"]
    params = _deserialize_value(value["params"])
    if not isinstance(params, dict):
        raise ValueError("helper params must be a dictionary")

    for helper_class, (known_kind, _) in _helper_codecs().items():
        if kind == known_kind:
            return helper_class(**params)
    raise ValueError(f"unsupported helper kind: {kind!r}")
