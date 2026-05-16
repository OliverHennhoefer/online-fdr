from __future__ import annotations

from online_fdr.batching.toad import Toad, run_finite
from online_fdr.utils.static import bh


def _reference_toad_loop(
    p_values: list[float], deadlines: list[int], alpha: float, weights: list[float]
) -> list[bool]:
    ratios = [p_val / weight for p_val, weight in zip(p_values, weights)]
    stages = sorted(set(deadlines))
    rejected: set[int] = set()
    candidates = set(range(stages[0]))

    for stage_idx, stage in enumerate(stages):
        previous_stage = 1 if stage_idx == 0 else stages[stage_idx - 1]
        candidates.update(range(previous_stage - 1, stage))
        candidates = {idx for idx in candidates if deadlines[idx] >= stage}
        old_rejected = rejected.difference(candidates)
        sorted_ratios = sorted(ratios[idx] for idx in candidates)
        step_up = 0
        for rank, ratio in enumerate(sorted_ratios, start=1):
            if ratio < (rank + len(old_rejected)) * alpha:
                step_up = rank
        if step_up:
            threshold = sorted_ratios[step_up - 1]
            rejected = old_rejected.union(
                idx for idx in candidates if ratios[idx] <= threshold
            )
        else:
            rejected = set(old_rejected)

    return [idx in rejected for idx in range(len(p_values))]


def test_toad_run_finite_reduces_to_bh_for_single_deadline_group() -> None:
    p_values = [0.001, 0.01, 0.04, 0.2, 0.9]
    _, threshold = bh(p_values, 0.05)

    assert Toad.run_finite(p_values, [5, 5, 5, 5, 5], alpha=0.05) == [
        p_val <= threshold for p_val in p_values
    ]


def test_toad_run_finite_matches_supplement_loop_reference() -> None:
    p_values = [0.001, 0.2, 0.01, 0.8, 0.003, 0.04]
    deadlines = [3, 3, 5, 5, 6, 6]
    weights = [1 / len(p_values)] * len(p_values)

    assert run_finite(p_values, deadlines, alpha=0.05, weights=weights) == (
        _reference_toad_loop(p_values, deadlines, 0.05, weights)
    )


def test_toad_streaming_finalizes_after_deadline_passes() -> None:
    method = Toad(alpha=0.05)
    method.add_test(0.001, deadline=2, test_id="a", weight=0.25)
    method.add_test(0.5, deadline=3, test_id="b", weight=0.25)

    assert method.advance_to(2) == {}
    finalized = method.advance_to(3)

    assert finalized == {"a": method.current_decisions["a"]}
    assert "a" in method.final_decisions
    assert "b" not in method.final_decisions
