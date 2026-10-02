"""Frozen scan-based async oracle captured before the history-index optimization.

Keep these formulas and gamma-call order independent of production changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Hashable

from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence


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


class ReferenceAsyncTest(AbstractSequentialTest):
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

    def _snapshot_state(self) -> dict[str, Any]:
        state = dict(self.__dict__)
        state["_records"] = [dict(record.__dict__) for record in self._records]
        state.pop("_records_by_id", None)
        return state

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        records = [_AsyncRecord(**record) for record in state.get("_records", [])]
        state["_records"] = records
        state["_records_by_id"] = {record.test_id: record for record in records}
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

        stage = len(self._records) + 1
        alpha_t = self._calc_alpha_for_stage(stage)
        record = _AsyncRecord(test_id=test_id, start_stage=stage, test_level=alpha_t)
        self._records.append(record)
        self._records_by_id[test_id] = record
        self._advance_hypotheses()
        self._set_test_level(alpha_t)
        self.alpha_history.append(alpha_t)
        self._decisions.append(None)
        return AsyncTestLevel(test_id=test_id, test_level=alpha_t)

    def finish_test(self, test_id: Hashable, p_val: float) -> bool:
        validity.check_p_val(p_val)
        record = self._records_by_id.get(test_id)
        if record is None:
            raise ValueError(f"Unknown test_id {test_id!r}.")
        if record.finish_stage is not None:
            raise ValueError(f"test_id {test_id!r} has already been finished.")

        record.p_val = float(p_val)
        record.finish_stage = len(self._records)
        record.rejected = p_val <= record.test_level
        self._decisions[record.start_stage - 1] = record.rejected
        return bool(record.rejected)

    def test_one(self, p_val: float) -> bool:
        level = self.start_test()
        return self.finish_test(level.test_id, p_val)

    def _is_available(self, record: _AsyncRecord, stage: int) -> bool:
        return record.finish_stage is not None and record.finish_stage <= stage - 1

    def _is_active_at(self, record: _AsyncRecord, stage: int) -> bool:
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
                    for record in self._records[: observed_stage - 1]
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


class ReferenceSaffronAsync(ReferenceAsyncTest):
    """Asynchronous SAFFRONstar lifecycle for overlapping online tests.

    This implements the async SAFFRONstar accounting used by the Bioconductor
    onlineFDR package for Zrnic, Ramdas, and Jordan's asynchronous online testing
    framework. It assigns a test level at ``start_test`` time and only uses
    completed prior tests for candidate and rejection accounting.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        wealth: float | None = None,
        lambda_: float = 0.5,
        gamma_seq: DefaultSaffronGammaSequence | None = None,
    ):
        super().__init__(alpha)
        self.wealth0 = alpha / 2 if wealth is None else wealth
        self.lambda_ = lambda_
        validity.check_initial_wealth(self.wealth0, alpha)
        validity.check_candidate_threshold(lambda_)
        self.seq = gamma_seq or DefaultSaffronGammaSequence(
            gamma_exp=1.6, c=0.4374901658
        )

    def _gamma_at_zero_based(self, idx: int) -> float:
        if idx < 0:
            raise ValueError("SAFFRONstar gamma index became negative.")
        return float(self.seq.calc_gamma(idx + 1))

    def _is_candidate_available(self, idx: int, stage: int) -> bool:
        record = self._records[idx]
        return (
            self._is_available(record, stage)
            and record.p_val is not None
            and record.p_val <= self.lambda_
        )

    def _candidate_count_between_available(
        self, start_idx: int, end_idx: int, stage: int
    ) -> int:
        if end_idx < start_idx:
            return 0
        return sum(
            self._is_candidate_available(idx, stage)
            for idx in range(start_idx, end_idx + 1)
            if idx < len(self._records)
        )

    def _calc_alpha_for_stage(self, stage: int) -> float:
        i = stage - 1
        if stage == 1:
            return min(
                self.lambda_,
                (1 - self.lambda_) * self._gamma_at_zero_based(0) * self.wealth0,
            )

        candsum = sum(
            self._is_candidate_available(idx, stage) for idx in range(stage - 1)
        )
        rejection_positions = self._available_rejection_positions(stage)
        num_rejections = len(rejection_positions)

        if num_rejections == 0:
            alpha_tilde = (
                (1 - self.lambda_)
                * self.wealth0
                * self._gamma_at_zero_based(i - candsum)
            )
            return min(self.lambda_, alpha_tilde)

        c_plus: list[int] = []
        for position in rejection_positions:
            c_plus.append(
                self._candidate_count_between_available(
                    position + 1,
                    max(i - 1, position + 1),
                    stage,
                )
            )

        first_gamma = self._gamma_at_zero_based(
            i - rejection_positions[0] - c_plus[0] - 1
        )
        alpha_tilde = (1 - self.lambda_) * (
            self.wealth0 * self._gamma_at_zero_based(i - candsum)
            + (self.alpha0 - self.wealth0) * first_gamma
        )

        if num_rejections > 1:
            tail_sum = (
                sum(
                    self._gamma_at_zero_based(i - position - c_val - 1)
                    for position, c_val in zip(rejection_positions, c_plus)
                )
                - first_gamma
            )
            alpha_tilde += (1 - self.lambda_) * self.alpha0 * tail_sum

        return min(self.lambda_, alpha_tilde)


class ReferenceAddisAsync(ReferenceAsyncTest):
    """Asynchronous ADDIS lifecycle with conservative-null discarding.

    Completed tests follow the onlineFDR ADDIS ``async=TRUE`` accounting. Tests
    still in progress are treated pessimistically as selected in the ADDIS
    conflict accounting, which is the information available to a true lifecycle
    API before their p-values are known.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        wealth: float | None = None,
        lambda_: float = 0.25,
        tau: float = 0.5,
        gamma_seq: DefaultSaffronGammaSequence | None = None,
    ):
        super().__init__(alpha)
        self.lambda_ = lambda_
        self.tau = tau
        self.wealth0 = alpha / 2 if wealth is None else wealth
        validity.check_tau(tau)
        if not 0 < lambda_ < tau:
            raise ValueError("lambda_ must be in (0, tau).")
        if self.wealth0 < 0 or self.wealth0 > alpha:
            raise ValueError("wealth must satisfy 0 <= wealth <= alpha.")
        self.seq = gamma_seq or DefaultSaffronGammaSequence(
            gamma_exp=1.6, c=0.4374901658
        )

    @property
    def candidate_threshold(self) -> float:
        return self.tau * self.lambda_

    @property
    def rejection_cap(self) -> float:
        return self.lambda_

    def _gamma_at_zero_based(self, idx: int) -> float:
        if idx < 0:
            raise ValueError("ADDIS async gamma index became negative.")
        return float(self.seq.calc_gamma(idx + 1))

    def _is_selected(self, record: _AsyncRecord) -> bool:
        return record.p_val is not None and record.p_val <= self.tau

    def _is_candidate_available(self, idx: int, stage: int) -> bool:
        record = self._records[idx]
        return (
            self._is_available(record, stage)
            and record.p_val is not None
            and record.p_val <= self.candidate_threshold
        )

    def _selected_prefix_count(self, end_exclusive: int) -> int:
        count = 0
        for record in self._records[:end_exclusive]:
            if record.finish_stage is None:
                count += 1
            else:
                count += int(self._is_selected(record))
        return count

    def _candidate_count_between_available(
        self, start_idx: int, end_idx: int, stage: int
    ) -> int:
        if end_idx < start_idx:
            return 0
        return sum(
            self._is_candidate_available(idx, stage)
            for idx in range(start_idx, end_idx + 1)
            if idx < len(self._records)
        )

    def _calc_alpha_for_stage(self, stage: int) -> float:
        if stage == 1:
            return min(
                self.rejection_cap,
                (self.tau - self.lambda_) * self.wealth0 * self._gamma_at_zero_based(0),
            )

        previous = self._records[: stage - 1]
        selected_or_active = sum(
            (
                self._is_selected(record)
                if self._is_available(record, stage)
                else self._is_active_at(record, stage)
            )
            for record in previous
        )
        candidate_count = sum(
            self._is_candidate_available(idx, stage) for idx in range(stage - 1)
        )
        rejection_positions = [
            idx
            for idx, record in enumerate(previous)
            if bool(record.rejected) and self._is_available(record, stage)
        ]

        if not rejection_positions:
            alpha_hat = (
                (self.tau - self.lambda_)
                * self.wealth0
                * self._gamma_at_zero_based(selected_or_active - candidate_count)
            )
            return min(self.rejection_cap, alpha_hat)

        c_plus: list[int] = []
        kappa_star: list[int] = []
        for position in rejection_positions:
            kappa_star.append(self._selected_prefix_count(position + 1))
            c_plus.append(
                self._candidate_count_between_available(
                    position + 1,
                    max(stage - 2, position + 1),
                    stage,
                )
            )

        first_gamma = self._gamma_at_zero_based(
            selected_or_active - kappa_star[0] - c_plus[0]
        )
        alpha_hat = (
            self.tau - self.lambda_
        ) * self.wealth0 * self._gamma_at_zero_based(
            selected_or_active - candidate_count
        ) + (self.tau - self.lambda_) * (self.alpha0 - self.wealth0) * first_gamma

        if len(rejection_positions) > 1:
            tail_sum = (
                sum(
                    self._gamma_at_zero_based(selected_or_active - k_star - c_val)
                    for k_star, c_val in zip(kappa_star, c_plus)
                )
                - first_gamma
            )
            alpha_hat += (self.tau - self.lambda_) * self.alpha0 * tail_sum

        return min(self.rejection_cap, alpha_hat)
