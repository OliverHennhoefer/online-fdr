from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Literal

from online_fdr.batching.bh import BatchBH
from online_fdr.batching.prds import BatchPRDS
from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.alpha.alpha import Gai
from online_fdr.investing.lond.lond import Lond
from online_fdr.investing.lord.dependent import LordDependent
from online_fdr.investing.lord.discard import LordDiscard
from online_fdr.investing.lord.plus_plus import LordPlusPlus
from online_fdr.investing.lord.three import LordThree as InvestingLordThree
from online_fdr.investing.saffron.saffron import Saffron
from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.functions.lord_three import LordThree as SpendingLordThree
from online_fdr.spending.online_fallback import OnlineFallback
from tests.parity_cases import BatchParityCase, SequentialParityCase

PINNED_ONLINEFDR_VERSION = "2.18.0"


@dataclass(frozen=True)
class ParityResult:
    alpha: list[float | None]
    decisions: list[bool]


@dataclass(frozen=True)
class MethodSpec:
    id: str
    profile_name: str
    kind: Literal["sequential", "batch"]
    run_python: Callable[[SequentialParityCase | BatchParityCase], ParityResult]
    run_r: Callable[[Any, Any, SequentialParityCase | BatchParityCase], ParityResult]


def require_r_onlinefdr() -> tuple[Any, Any]:
    try:
        import rpy2.robjects as ro
        from rpy2.robjects.packages import importr
    except Exception as exc:
        raise RuntimeError(
            "rpy2 is mandatory for this test suite. Install dev dependencies with "
            "`uv sync --group dev` and ensure R is available on PATH. "
            f"Original error: {exc}"
        ) from exc

    try:
        onlinefdr = importr("onlineFDR")
    except Exception as exc:
        raise RuntimeError(
            "R package `onlineFDR` is required for parity tests. "
            "Install the pinned Bioconductor release (expected 2.18.0). "
            f"Original error: {exc}"
        ) from exc

    version = str(ro.r("as.character(utils::packageVersion('onlineFDR'))")[0])
    if version != PINNED_ONLINEFDR_VERSION:
        raise RuntimeError(
            "onlineFDR version mismatch for parity tests. "
            f"Expected {PINNED_ONLINEFDR_VERSION}, found {version}. "
            "Install the pinned version before running tests."
        )

    return ro, onlinefdr


def _to_float_or_none(value: Any) -> float | None:
    as_float = float(value)
    if math.isnan(as_float):
        return None
    return as_float


def _extract_r_result(result: Any) -> ParityResult:
    alpha = [_to_float_or_none(value) for value in result.rx2("alphai")]
    decisions = [bool(value) for value in result.rx2("R")]
    return ParityResult(alpha=alpha, decisions=decisions)


def _run_python_sequential(
    method: Any,
    case: SequentialParityCase,
) -> ParityResult:
    alpha: list[float | None] = []
    decisions: list[bool] = []
    for p_value in case.p_values:
        decisions.append(bool(method.test_one(p_value)))
        alpha.append(None if method.alpha is None else float(method.alpha))
    return ParityResult(alpha=alpha, decisions=decisions)


def _run_python_batch(method: Any, case: BatchParityCase) -> ParityResult:
    alpha: list[float | None] = []
    decisions: list[bool] = []

    start = 0
    for batch_size in case.batch_sizes:
        end = start + batch_size
        batch = case.p_values[start:end]
        start = end

        batch_decisions = method.test_batch(batch)
        decisions.extend(bool(value) for value in batch_decisions)

        alpha_s = getattr(method, "alpha_s", None)
        if alpha_s:
            batch_alpha = float(alpha_s[-1])
        else:
            raw_alpha = method.alpha
            batch_alpha = None if raw_alpha is None else float(raw_alpha)
        alpha.extend([batch_alpha] * batch_size)

    return ParityResult(alpha=alpha, decisions=decisions)


def _to_r_batch_frame(ro: Any, case: BatchParityCase) -> Any:
    size = len(case.p_values)
    return ro.DataFrame(
        {
            "id": ro.StrVector([f"id_{i + 1}" for i in range(size)]),
            "pval": ro.FloatVector(case.p_values),
            "batch": ro.IntVector(case.batch_ids),
        }
    )


def _run_addis_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(
        Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
        case,
    )


def _run_addis_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.ADDIS(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        w0=0.025,
        tau=0.5,
        **{"lambda": 0.25},
    )
    return _extract_r_result(result)


def _run_saffron_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(
        Saffron(alpha=0.05, wealth=0.025, lambda_=0.5),
        case,
    )


def _run_saffron_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.SAFFRON(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        w0=0.025,
        **{"lambda": 0.5},
    )
    return _extract_r_result(result)


def _run_lord3_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(
        InvestingLordThree(alpha=0.05, wealth=0.025, reward=0.025),
        case,
    )


def _run_lord3_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.LORD(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        version="3",
        w0=0.025,
        b0=0.025,
    )
    return _extract_r_result(result)


def _run_lordpp_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(LordPlusPlus(alpha=0.05, wealth=0.025), case)


def _run_lordpp_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.LORD(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        version="++",
        w0=0.025,
        b0=0.025,
        tau_discard=0.5,
    )
    return _extract_r_result(result)


def _run_lord_discard_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(
        LordDiscard(alpha=0.05, wealth=0.025, tau=0.5),
        case,
    )


def _run_lord_discard_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.LORD(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        version="discard",
        w0=0.025,
        b0=0.025,
        tau_discard=0.5,
    )
    return _extract_r_result(result)


def _run_lord_dep_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(
        LordDependent(alpha=0.05, wealth=0.025, reward=0.025),
        case,
    )


def _run_lord_dep_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    if not hasattr(onlinefdr, "LORDdep"):
        raise RuntimeError(
            "The installed onlineFDR package does not expose LORDdep. "
            "Install the pinned release with LORDdep support."
        )

    result = onlinefdr.LORDdep(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        w0=0.025,
        b0=0.025,
    )
    return _extract_r_result(result)


def _make_lond_python_runner(original: bool, dependent: bool) -> Callable[[SequentialParityCase | BatchParityCase], ParityResult]:
    def _runner(case: SequentialParityCase | BatchParityCase) -> ParityResult:
        assert isinstance(case, SequentialParityCase)
        return _run_python_sequential(
            Lond(alpha=0.05, original=original, dependent=dependent),
            case,
        )

    return _runner


def _make_lond_r_runner(original: bool, dependent: bool) -> Callable[[Any, Any, SequentialParityCase | BatchParityCase], ParityResult]:
    def _runner(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
        assert isinstance(case, SequentialParityCase)
        result = onlinefdr.LOND(
            ro.FloatVector(case.p_values),
            alpha=0.05,
            original=original,
            dep=dependent,
        )
        return _extract_r_result(result)

    return _runner


def _run_gai_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(Gai(alpha=0.05, wealth=0.025), case)


def _run_gai_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.Alpha_investing(
        ro.FloatVector(case.p_values),
        alpha=0.05,
        w0=0.025,
    )
    return _extract_r_result(result)


def _run_alpha_spending_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    spend_func = SpendingLordThree(k=len(case.p_values))
    method = AlphaSpending(alpha=0.05, spend_func=spend_func)
    return _run_python_sequential(method, case)


def _run_alpha_spending_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.Alpha_spending(ro.FloatVector(case.p_values), alpha=0.05)
    return _extract_r_result(result)


def _run_fallback_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    return _run_python_sequential(OnlineFallback(alpha=0.05), case)


def _run_fallback_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, SequentialParityCase)
    result = onlinefdr.online_fallback(ro.FloatVector(case.p_values), alpha=0.05)
    return _extract_r_result(result)


def _run_batch_bh_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, BatchParityCase)
    return _run_python_batch(BatchBH(alpha=0.05), case)


def _run_batch_bh_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, BatchParityCase)
    result = onlinefdr.BatchBH(_to_r_batch_frame(ro, case), alpha=0.05)
    return _extract_r_result(result)


def _run_batch_prds_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, BatchParityCase)
    return _run_python_batch(BatchPRDS(alpha=0.05), case)


def _run_batch_prds_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, BatchParityCase)
    result = onlinefdr.BatchPRDS(_to_r_batch_frame(ro, case), alpha=0.05)
    return _extract_r_result(result)


def _run_batch_storey_python(case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, BatchParityCase)
    return _run_python_batch(BatchStoreyBH(alpha=0.05, lambda_=0.5), case)


def _run_batch_storey_r(ro: Any, onlinefdr: Any, case: SequentialParityCase | BatchParityCase) -> ParityResult:
    assert isinstance(case, BatchParityCase)
    result = onlinefdr.BatchStBH(_to_r_batch_frame(ro, case), alpha=0.05, **{"lambda": 0.5})
    return _extract_r_result(result)


PARITY_METHOD_SPECS: tuple[MethodSpec, ...] = (
    MethodSpec(
        id="addis",
        profile_name="Addis",
        kind="sequential",
        run_python=_run_addis_python,
        run_r=_run_addis_r,
    ),
    MethodSpec(
        id="saffron",
        profile_name="Saffron",
        kind="sequential",
        run_python=_run_saffron_python,
        run_r=_run_saffron_r,
    ),
    MethodSpec(
        id="lord_three",
        profile_name="LordThree",
        kind="sequential",
        run_python=_run_lord3_python,
        run_r=_run_lord3_r,
    ),
    MethodSpec(
        id="lord_plus_plus",
        profile_name="LordPlusPlus",
        kind="sequential",
        run_python=_run_lordpp_python,
        run_r=_run_lordpp_r,
    ),
    MethodSpec(
        id="lord_discard",
        profile_name="LordDiscard",
        kind="sequential",
        run_python=_run_lord_discard_python,
        run_r=_run_lord_discard_r,
    ),
    MethodSpec(
        id="lord_dependent",
        profile_name="LordDependent",
        kind="sequential",
        run_python=_run_lord_dep_python,
        run_r=_run_lord_dep_r,
    ),
    MethodSpec(
        id="lond_original_independent",
        profile_name="Lond",
        kind="sequential",
        run_python=_make_lond_python_runner(original=True, dependent=False),
        run_r=_make_lond_r_runner(original=True, dependent=False),
    ),
    MethodSpec(
        id="lond_original_dependent",
        profile_name="Lond",
        kind="sequential",
        run_python=_make_lond_python_runner(original=True, dependent=True),
        run_r=_make_lond_r_runner(original=True, dependent=True),
    ),
    MethodSpec(
        id="lond_modified_independent",
        profile_name="Lond",
        kind="sequential",
        run_python=_make_lond_python_runner(original=False, dependent=False),
        run_r=_make_lond_r_runner(original=False, dependent=False),
    ),
    MethodSpec(
        id="lond_modified_dependent",
        profile_name="Lond",
        kind="sequential",
        run_python=_make_lond_python_runner(original=False, dependent=True),
        run_r=_make_lond_r_runner(original=False, dependent=True),
    ),
    MethodSpec(
        id="gai",
        profile_name="Gai",
        kind="sequential",
        run_python=_run_gai_python,
        run_r=_run_gai_r,
    ),
    MethodSpec(
        id="alpha_spending",
        profile_name="AlphaSpending",
        kind="sequential",
        run_python=_run_alpha_spending_python,
        run_r=_run_alpha_spending_r,
    ),
    MethodSpec(
        id="online_fallback",
        profile_name="OnlineFallback",
        kind="sequential",
        run_python=_run_fallback_python,
        run_r=_run_fallback_r,
    ),
    MethodSpec(
        id="batch_bh",
        profile_name="BatchBH",
        kind="batch",
        run_python=_run_batch_bh_python,
        run_r=_run_batch_bh_r,
    ),
    MethodSpec(
        id="batch_prds",
        profile_name="BatchPRDS",
        kind="batch",
        run_python=_run_batch_prds_python,
        run_r=_run_batch_prds_r,
    ),
    MethodSpec(
        id="batch_storey_bh",
        profile_name="BatchStoreyBH",
        kind="batch",
        run_python=_run_batch_storey_python,
        run_r=_run_batch_storey_r,
    ),
)


PARITY_PROFILE_COVERAGE = {spec.profile_name for spec in PARITY_METHOD_SPECS}
