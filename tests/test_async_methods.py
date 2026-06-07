from __future__ import annotations

from collections.abc import Callable

import pytest

from online_fdr.p_values.async_methods import AddisAsync, SaffronAsync
from tests.parity_oracle import _extract_r_result, require_r_onlinefdr

_P_VALUES = [0.2, 1e-8, 0.04, 0.3, 0.01, 0.3]
_FINISH_STAGES = [3, 2, 4, 6, 5, 6]


def _run_lifecycle(method: SaffronAsync | AddisAsync) -> tuple[list[float], list[bool]]:
    method.start_test("h1")
    method.start_test("h2")
    method.finish_test("h2", _P_VALUES[1])
    method.start_test("h3")
    method.finish_test("h1", _P_VALUES[0])
    method.start_test("h4")
    method.finish_test("h3", _P_VALUES[2])
    method.start_test("h5")
    method.finish_test("h5", _P_VALUES[4])
    method.start_test("h6")
    method.finish_test("h4", _P_VALUES[3])
    method.finish_test("h6", _P_VALUES[5])
    return method.alpha_history, [bool(value) for value in method.decisions]


def _r_async_frame(ro):
    return ro.DataFrame(
        {
            "id": ro.StrVector([f"h{i}" for i in range(1, len(_P_VALUES) + 1)]),
            "pval": ro.FloatVector(_P_VALUES),
            "decision.times": ro.IntVector(_FINISH_STAGES),
        }
    )


@pytest.fixture(scope="session")
def r_env():
    try:
        return require_r_onlinefdr()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=1)


def test_saffron_async_matches_onlinefdr_async(r_env) -> None:
    ro, onlinefdr = r_env
    alpha_py, decisions_py = _run_lifecycle(
        SaffronAsync(alpha=0.05, wealth=0.025, lambda_=0.5)
    )

    result_r = onlinefdr.SAFFRONstar(
        _r_async_frame(ro),
        alpha=0.05,
        version="async",
        w0=0.025,
        display_progress=False,
        **{"lambda": 0.5},
    )
    parity_r = _extract_r_result(result_r)

    assert decisions_py == parity_r.decisions
    assert alpha_py == pytest.approx(parity_r.alpha, rel=0.0, abs=1e-12)


def test_addis_async_matches_onlinefdr_async_for_lifecycle_safe_order(r_env) -> None:
    ro, onlinefdr = r_env
    alpha_py, decisions_py = _run_lifecycle(
        AddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
    )

    result_r = onlinefdr.ADDIS(
        _r_async_frame(ro),
        alpha=0.05,
        w0=0.025,
        tau=0.5,
        **{"lambda": 0.25, "async": True},
    )
    parity_r = _extract_r_result(result_r)

    assert decisions_py == parity_r.decisions
    assert alpha_py == pytest.approx(parity_r.alpha, rel=0.0, abs=1e-12)


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
