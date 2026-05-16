from __future__ import annotations

import math
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from online_fdr.utils import validity


@dataclass
class ToadRecord:
    test_id: Hashable
    p_val: float
    deadline: int
    weight: float
    stage: int
    rejected: bool = False
    finalized: bool = False


def _default_stream_weight(j: int) -> float:
    return 0.07720838 * math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j))))


def _toad_step(
    ratios: Sequence[float],
    alpha: float,
    past_rejections: set[int],
    candidates: Sequence[int],
) -> set[int]:
    old_rejections = past_rejections.difference(candidates)
    if not candidates:
        return set(old_rejections)

    sorted_ratios = sorted(ratios[idx] for idx in candidates)
    len_old = len(old_rejections)
    step_up = 0
    for rank, ratio in enumerate(sorted_ratios, start=1):
        if ratio < (rank + len_old) * alpha:
            step_up = rank

    if step_up == 0:
        return set(old_rejections)

    threshold = sorted_ratios[step_up - 1]
    return set(old_rejections).union(
        idx for idx in candidates if ratios[idx] <= threshold
    )


def run_finite(
    p_values: Sequence[float],
    deadlines: Sequence[int],
    alpha: float = 0.05,
    weights: Sequence[float] | None = None,
) -> list[bool]:
    """Run Fisher's finite TOAD loop from the AISTATS supplementary code."""
    validity.check_alpha(alpha)
    if len(p_values) != len(deadlines):
        raise ValueError("p_values and deadlines must have the same length.")
    if not p_values:
        return []
    validity.check_p_vals_batch(p_values)

    n_tests = len(p_values)
    if weights is None:
        weights = [1.0 / n_tests] * n_tests
    if len(weights) != n_tests:
        raise ValueError("weights must have the same length as p_values.")
    if any(weight <= 0 for weight in weights):
        raise ValueError("weights must be positive.")
    if sum(weights) > 1 + 1e-10:
        raise ValueError("weights must sum to at most 1.")
    if any(deadline < idx for idx, deadline in enumerate(deadlines, start=1)):
        raise ValueError("each deadline must be at least its test index.")

    ratios = [float(p_val) / float(weight) for p_val, weight in zip(p_values, weights)]
    stages = sorted(set(deadlines))
    rejections: set[int] = set()
    candidates = set(range(min(stages[0], n_tests)))
    previous_stage = 1

    for idx, stage in enumerate(stages):
        if idx > 0:
            previous_stage = stages[idx - 1]
        candidates.update(range(max(previous_stage - 1, 0), min(stage, n_tests)))
        candidates = {cand for cand in candidates if deadlines[cand] >= stage}
        rejections = _toad_step(ratios, alpha, rejections, sorted(candidates))

    return [idx in rejections for idx in range(n_tests)]


class Toad:
    """Thresholds based on active discoveries for decision-deadline online FDR."""

    def __init__(self, alpha: float = 0.05):
        validity.check_alpha(alpha)
        self.alpha = alpha
        self.records: list[ToadRecord] = []
        self._records_by_id: dict[Hashable, ToadRecord] = {}
        self._next_auto_id = 1
        self._current_rejections: set[int] = set()
        self.current_stage = 0
        self.current_decisions: dict[Hashable, bool] = {}
        self.final_decisions: dict[Hashable, bool] = {}

    def add_test(
        self,
        p_val: float,
        deadline: int,
        test_id: Hashable | None = None,
        weight: float | None = None,
    ) -> bool:
        validity.check_p_val(p_val)
        if test_id is None:
            test_id = self._next_auto_id
            self._next_auto_id += 1
        if test_id in self._records_by_id:
            raise ValueError(f"test_id {test_id!r} has already been added.")

        stage = len(self.records) + 1
        if deadline < stage:
            raise ValueError("deadline must be at least the test's arrival stage.")
        if weight is None:
            weight = _default_stream_weight(stage)
        if weight <= 0:
            raise ValueError("weight must be positive.")
        if sum(record.weight for record in self.records) + weight > 1 + 1e-10:
            raise ValueError("streaming TOAD weights must sum to at most 1.")

        record = ToadRecord(
            test_id=test_id,
            p_val=float(p_val),
            deadline=deadline,
            weight=float(weight),
            stage=stage,
        )
        self.records.append(record)
        self._records_by_id[test_id] = record
        self.current_stage = stage
        self._recompute_at(stage)
        return self.current_decisions[test_id]

    def advance_to(self, stage: int) -> dict[Hashable, bool]:
        if stage < self.current_stage:
            raise ValueError("stage cannot move backwards.")
        self.current_stage = stage
        self._recompute_at(stage)
        finalized: dict[Hashable, bool] = {}
        for record in self.records:
            if not record.finalized and record.deadline < stage:
                record.finalized = True
                decision = self.current_decisions[record.test_id]
                self.final_decisions[record.test_id] = decision
                finalized[record.test_id] = decision
        return finalized

    @staticmethod
    def run_finite(
        p_values: Sequence[float],
        deadlines: Sequence[int],
        alpha: float = 0.05,
        weights: Sequence[float] | None = None,
    ) -> list[bool]:
        return run_finite(p_values, deadlines, alpha=alpha, weights=weights)

    def _recompute_at(self, stage: int) -> None:
        ratios = [record.p_val / record.weight for record in self.records]
        candidates = [
            idx
            for idx, record in enumerate(self.records)
            if record.stage <= stage and record.deadline >= stage
        ]
        self._current_rejections = _toad_step(
            ratios, self.alpha, self._current_rejections, candidates
        )
        for idx, record in enumerate(self.records):
            record.rejected = idx in self._current_rejections
            self.current_decisions[record.test_id] = record.rejected
