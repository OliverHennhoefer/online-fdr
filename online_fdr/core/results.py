from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any


class _FrozenMapping(Mapping[str, Any]):
    """Small immutable mapping used by public result records."""

    def __init__(self, values: Mapping[str, Any]):
        self._data = {key: _freeze_value(value) for key, value in values.items()}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            return dict(self.items()) == dict(other.items())
        return NotImplemented


def _freeze_value(value: Any) -> Any:
    if isinstance(value, _FrozenMapping):
        return value
    if isinstance(value, Mapping):
        return _FrozenMapping(value)
    if isinstance(value, list | tuple):
        return tuple(_freeze_value(item) for item in value)
    return value


@dataclass(frozen=True)
class TestDecision:
    """Decision details for a single hypothesis test."""

    __test__ = False

    rejected: bool
    value: float
    rejection_threshold: float | None
    index: int
    test_level: float | None = None
    error_rate: str | None = None


@dataclass(frozen=True)
class BatchDecision:
    """Decision details for a batch of hypotheses."""

    rejected: tuple[bool, ...]
    values: tuple[float, ...]
    rejection_threshold: float | None
    batch_index: int
    test_level: float | None = None
    error_rate: str | None = None
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "rejected", tuple(self.rejected))
        object.__setattr__(self, "values", tuple(self.values))
        if self.metadata is not None:
            object.__setattr__(self, "metadata", _FrozenMapping(self.metadata))
