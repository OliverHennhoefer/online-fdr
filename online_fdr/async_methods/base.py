from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity


@dataclass(frozen=True)
class AsyncTestLevel:
    """Assigned test level for an asynchronous hypothesis test."""

    test_id: Hashable
    alpha: float


@dataclass
class AsyncRecord:
    """Internal state for one asynchronous test."""

    test_id: Hashable
    start_stage: int
    alpha: float
    p_val: float | None = None
    finish_stage: int | None = None
    rejected: bool | None = None

    @property
    def is_finished(self) -> bool:
        return self.finish_stage is not None


class AbstractAsyncTest(AbstractSequentialTest):
    """Base lifecycle for asynchronous online procedures."""

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self.alpha0 = alpha
        self.records: list[AsyncRecord] = []
        self._records_by_id: dict[Hashable, AsyncRecord] = {}
        self._next_auto_id = 1
        self.alpha_history: list[float] = []
        self.decisions: list[bool | None] = []

    @property
    def active(self) -> dict[Hashable, AsyncRecord]:
        return {
            record.test_id: record
            for record in self.records
            if record.finish_stage is None
        }

    @property
    def completed(self) -> dict[Hashable, AsyncRecord]:
        return {
            record.test_id: record
            for record in self.records
            if record.finish_stage is not None
        }

    def start_test(self, test_id: Hashable | None = None) -> AsyncTestLevel:
        if test_id is None:
            test_id = self._next_auto_id
            self._next_auto_id += 1
        if test_id in self._records_by_id:
            raise ValueError(f"test_id {test_id!r} has already been started.")

        stage = len(self.records) + 1
        alpha_t = self._calc_alpha_for_stage(stage)
        record = AsyncRecord(test_id=test_id, start_stage=stage, alpha=alpha_t)
        self.records.append(record)
        self._records_by_id[test_id] = record
        self.num_test = stage
        self.alpha = alpha_t
        self.alpha_history.append(alpha_t)
        self.decisions.append(None)
        return AsyncTestLevel(test_id=test_id, alpha=alpha_t)

    def finish_test(self, test_id: Hashable, p_val: float) -> bool:
        validity.check_p_val(p_val)
        record = self._records_by_id.get(test_id)
        if record is None:
            raise ValueError(f"Unknown test_id {test_id!r}.")
        if record.finish_stage is not None:
            raise ValueError(f"test_id {test_id!r} has already been finished.")

        record.p_val = float(p_val)
        record.finish_stage = len(self.records)
        record.rejected = p_val <= record.alpha
        self.decisions[record.start_stage - 1] = record.rejected
        return bool(record.rejected)

    def test_one(self, p_val: float) -> bool:
        level = self.start_test()
        return self.finish_test(level.test_id, p_val)

    def _is_available(self, record: AsyncRecord, stage: int) -> bool:
        return record.finish_stage is not None and record.finish_stage <= stage - 1

    def _is_active_at(self, record: AsyncRecord, stage: int) -> bool:
        return record.finish_stage is None or record.finish_stage >= stage

    def _available_rejection_positions(self, stage: int) -> list[int]:
        """Return zero-based conflict-adjusted discovery positions for STAR rules."""
        r_dec: list[int] = []
        for observed_stage in range(2, stage + 1):
            r_dec.append(
                sum(
                    bool(record.rejected)
                    and record.finish_stage is not None
                    and record.finish_stage <= observed_stage - 1
                    for record in self.records[: observed_stage - 1]
                )
            )

        if not r_dec:
            return []

        positions: list[int] = []
        for target in range(max(r_dec)):
            for idx, value in enumerate(r_dec):
                if value > target:
                    positions.append(idx)
                    break
        return positions

    def _calc_alpha_for_stage(self, stage: int) -> float:
        raise NotImplementedError
