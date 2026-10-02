from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Hashable

from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity
from online_fdr.p_values.async_methods._history import _AsyncHistoryIndex


@dataclass(frozen=True)
class AsyncTestLevel:
    """Assigned test level for an asynchronous hypothesis test."""

    test_id: Hashable
    test_level: float


@dataclass(frozen=True)
class AsyncRecord:
    """Immutable public state for one asynchronous test."""

    test_id: Hashable
    start_stage: int
    test_level: float
    p_val: float | None = None
    finish_stage: int | None = None
    rejected: bool | None = None

    @property
    def is_finished(self) -> bool:
        return self.finish_stage is not None


@dataclass
class _AsyncRecord:
    """Internal mutable state for one asynchronous test."""

    test_id: Hashable
    start_stage: int
    test_level: float
    p_val: float | None = None
    finish_stage: int | None = None
    rejected: bool | None = None

    def to_snapshot(self) -> AsyncRecord:
        return AsyncRecord(
            test_id=self.test_id,
            start_stage=self.start_stage,
            test_level=self.test_level,
            p_val=self.p_val,
            finish_stage=self.finish_stage,
            rejected=self.rejected,
        )

    @property
    def is_finished(self) -> bool:
        return self.finish_stage is not None


class AbstractAsyncTest(AbstractSequentialTest):
    """Base lifecycle for asynchronous online procedures."""

    error_rate = "mFDR"

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self.alpha0 = alpha
        self._records: list[_AsyncRecord] = []
        self._records_by_id: dict[Hashable, _AsyncRecord] = {}
        self._next_auto_id = 1
        self.alpha_history: list[float] = []
        self._decisions: list[bool | None] = []
        self._history_index: _AsyncHistoryIndex | None = None

    def _snapshot_state(self) -> dict[str, Any]:
        state = dict(self.__dict__)
        state["_records"] = [dict(record.__dict__) for record in self._records]
        state.pop("_records_by_id", None)
        state.pop("_history_index", None)
        return state

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        records = [_AsyncRecord(**record) for record in state.get("_records", [])]
        state["_records"] = records
        state["_records_by_id"] = {record.test_id: record for record in records}
        state["_history_index"] = None
        return state

    @property
    def records(self) -> tuple[AsyncRecord, ...]:
        return tuple(record.to_snapshot() for record in self._records)

    @property
    def decisions(self) -> tuple[bool | None, ...]:
        return tuple(self._decisions)

    @property
    def active(self) -> dict[Hashable, AsyncRecord]:
        return {
            record.test_id: record.to_snapshot()
            for record in self._records
            if record.finish_stage is None
        }

    @property
    def completed(self) -> dict[Hashable, AsyncRecord]:
        return {
            record.test_id: record.to_snapshot()
            for record in self._records
            if record.finish_stage is not None
        }

    def start_test(self, test_id: Hashable | None = None) -> AsyncTestLevel:
        if test_id is None:
            test_id = self._next_auto_id
            self._next_auto_id += 1
        if test_id in self._records_by_id:
            raise ValueError(f"test_id {test_id!r} has already been started.")

        self._prepare_history_index()
        stage = len(self._records) + 1
        alpha_t = self._calc_alpha_for_stage(stage)
        record = _AsyncRecord(test_id=test_id, start_stage=stage, test_level=alpha_t)
        self._records.append(record)
        self._records_by_id[test_id] = record
        self._advance_hypotheses()
        self._set_test_level(alpha_t)
        self.alpha_history.append(alpha_t)
        self._decisions.append(None)
        self._on_test_started(record)
        return AsyncTestLevel(test_id=test_id, test_level=alpha_t)

    def finish_test(self, test_id: Hashable, p_val: float) -> bool:
        validity.check_p_val(p_val)
        record = self._records_by_id.get(test_id)
        if record is None:
            raise ValueError(f"Unknown test_id {test_id!r}.")
        if record.finish_stage is not None:
            raise ValueError(f"test_id {test_id!r} has already been finished.")

        self._prepare_history_index()
        record.p_val = float(p_val)
        record.finish_stage = len(self._records)
        record.rejected = p_val <= record.test_level
        self._decisions[record.start_stage - 1] = record.rejected
        self._on_test_finished(record)
        return bool(record.rejected)

    def test_one(self, p_val: float) -> bool:
        level = self.start_test()
        return self.finish_test(level.test_id, p_val)

    def _is_available(self, record: _AsyncRecord, stage: int) -> bool:
        return record.finish_stage is not None and record.finish_stage <= stage - 1

    def _is_active_at(self, record: _AsyncRecord, stage: int) -> bool:
        return record.finish_stage is None or record.finish_stage >= stage

    def _prepare_history_index(self) -> None:
        """Prepare derived accounting before a lifecycle operation."""

    def _on_test_started(self, record: _AsyncRecord) -> None:
        """Update derived accounting after a successful start."""

    def _on_test_finished(self, record: _AsyncRecord) -> None:
        """Update derived accounting after a successful completion."""

    def _calc_alpha_for_stage(self, stage: int) -> float:
        raise NotImplementedError
