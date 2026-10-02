from __future__ import annotations

from collections.abc import Callable

import pytest

from online_fdr.p_values.async_methods import AddisAsync, SaffronAsync
from tests.async_reference import ReferenceAddisAsync
from tests.parity_oracle import _extract_r_result, require_r_onlinefdr

_P_VALUES = [0.2, 1e-8, 0.04, 0.3, 0.01, 0.3]
_FINISH_STAGES = [3, 2, 4, 6, 5, 6]


def _run_lifecycle(
    method: SaffronAsync | AddisAsync | ReferenceAddisAsync,
    blocks: int = 1,
    p_values: list[float] | None = None,
) -> tuple[list[float], list[bool]]:
    p_values = _P_VALUES * blocks if p_values is None else p_values
    for block in range(blocks):
        values = p_values[block * len(_P_VALUES) : (block + 1) * len(_P_VALUES)]
        ids = [f"h{block * len(_P_VALUES) + i}" for i in range(1, 7)]
        method.start_test(ids[0])
        method.start_test(ids[1])
        method.finish_test(ids[1], values[1])
        method.start_test(ids[2])
        method.finish_test(ids[0], values[0])
        method.start_test(ids[3])
        method.finish_test(ids[2], values[2])
        method.start_test(ids[4])
        method.finish_test(ids[4], values[4])
        method.start_test(ids[5])
        method.finish_test(ids[3], values[3])
        method.finish_test(ids[5], values[5])
    return method.alpha_history, [bool(value) for value in method.decisions]


def _r_async_frame(ro, blocks: int = 1, p_values: list[float] | None = None):
    return ro.DataFrame(
        {
            "id": ro.StrVector(
                [f"h{i}" for i in range(1, blocks * len(_P_VALUES) + 1)]
            ),
            "pval": ro.FloatVector(
                _P_VALUES * blocks if p_values is None else p_values
            ),
            "decision.times": ro.IntVector(
                [
                    stage + block * len(_P_VALUES)
                    for block in range(blocks)
                    for stage in _FINISH_STAGES
                ]
            ),
        }
    )


@pytest.fixture(scope="session")
def r_env():
    try:
        return require_r_onlinefdr()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=1)


@pytest.mark.live_r_parity
@pytest.mark.parametrize("blocks", [1, 20])
def test_saffron_async_matches_onlinefdr_async(r_env, blocks: int) -> None:
    ro, onlinefdr = r_env
    alpha_py, decisions_py = _run_lifecycle(
        SaffronAsync(alpha=0.05, wealth=0.025, lambda_=0.5), blocks
    )

    result_r = onlinefdr.SAFFRONstar(
        _r_async_frame(ro, blocks),
        alpha=0.05,
        version="async",
        w0=0.025,
        display_progress=False,
        **{"lambda": 0.5},
    )
    parity_r = _extract_r_result(result_r)

    assert decisions_py == parity_r.decisions
    assert alpha_py == pytest.approx(parity_r.alpha, rel=0.0, abs=1e-12)


@pytest.mark.live_r_parity
@pytest.mark.parametrize("blocks", [1, 20])
def test_addis_async_onlinefdr_lifecycle_accounting(r_env, blocks: int) -> None:
    ro, onlinefdr = r_env
    alpha_py, decisions_py = _run_lifecycle(
        AddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5), blocks
    )

    result_r = onlinefdr.ADDIS(
        _r_async_frame(ro, blocks),
        alpha=0.05,
        w0=0.025,
        tau=0.5,
        **{"lambda": 0.25, "async": True},
    )
    parity_r = _extract_r_result(result_r)

    assert decisions_py == parity_r.decisions
    # R collapses the second discovery's position at stage 9 in the repeated case.
    assert alpha_py[:8] == pytest.approx(parity_r.alpha[:8], rel=0.0, abs=1e-12)
    if blocks == 20:
        assert alpha_py[8] != pytest.approx(parity_r.alpha[8], rel=0.0, abs=1e-12)


@pytest.mark.live_r_parity
@pytest.mark.parametrize("discoveries", [1, 2])
def test_addis_async_matches_onlinefdr_for_supported_repeated_discoveries(
    r_env, discoveries: int
) -> None:
    """Keep pending tests selected and discovery positions representable as bools."""
    ro, onlinefdr = r_env
    blocks = 20
    p_values = _P_VALUES * blocks
    for block in range(1, blocks):
        p_values[block * len(_P_VALUES) + 1] = 0.2
    if discoveries == 2:
        p_values[0] = 1e-8
        p_values[4] = 0.2
    alpha_py, decisions_py = _run_lifecycle(
        AddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
        blocks,
        p_values,
    )

    result_r = onlinefdr.ADDIS(
        _r_async_frame(ro, blocks, p_values),
        alpha=0.05,
        w0=0.025,
        tau=0.5,
        **{"lambda": 0.25, "async": True},
    )
    parity_r = _extract_r_result(result_r)

    assert sum(decisions_py) == discoveries
    assert [idx for idx, rejected in enumerate(decisions_py) if rejected] == (
        [1] if discoveries == 1 else [0, 1]
    )
    assert decisions_py == parity_r.decisions
    assert alpha_py == pytest.approx(parity_r.alpha, rel=0.0, abs=1e-12)


def test_addis_async_preserves_frozen_multi_discovery_accounting() -> None:
    """Independently protect Python accounting for the known R parity difference."""
    alpha_py, decisions_py = _run_lifecycle(
        AddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5), 20
    )
    alpha_reference, decisions_reference = _run_lifecycle(
        ReferenceAddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5), 20
    )

    assert sum(decisions_py) == 20
    assert decisions_py == decisions_reference
    assert alpha_py == alpha_reference


def test_async_lifecycle_rejects_invalid_operation_order() -> None:
    method = SaffronAsync(alpha=0.05)
    level = method.start_test("dup")

    with pytest.raises(ValueError, match="already been started"):
        method.start_test("dup")
    with pytest.raises(ValueError, match="Unknown test_id"):
        method.finish_test("missing", 0.01)
    with pytest.raises(ValueError, match="p-value"):
        method.finish_test(level.test_id, 1.2)

    method.finish_test(level.test_id, 0.01)
    with pytest.raises(ValueError, match="already been finished"):
        method.finish_test(level.test_id, 0.02)


@pytest.mark.parametrize(
    "method_factory",
    [
        lambda: SaffronAsync(alpha=0.05, wealth=0.025, lambda_=0.5),
        lambda: AddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
    ],
)
def test_async_test_one_matches_immediate_start_finish(
    method_factory: Callable[[], SaffronAsync | AddisAsync],
) -> None:
    direct = method_factory()
    lifecycle = method_factory()

    direct_decisions = [direct.test_one(p_val) for p_val in [0.001, 0.2, 0.01]]
    lifecycle_decisions = []
    for idx, p_val in enumerate([0.001, 0.2, 0.01], start=1):
        level = lifecycle.start_test(f"h{idx}")
        lifecycle_decisions.append(lifecycle.finish_test(level.test_id, p_val))

    assert direct_decisions == lifecycle_decisions
    assert direct.alpha_history == pytest.approx(lifecycle.alpha_history)
