from __future__ import annotations

from dataclasses import dataclass

import pytest

from tests.parity_cases import (
    BatchParityCase,
    SequentialParityCase,
    batch_cases,
    sequential_cases,
)
from tests.parity_oracle import (
    PARITY_METHOD_SPECS,
    MethodSpec,
    ParityResult,
    require_r_onlinefdr,
)


@dataclass(frozen=True)
class ParityScenario:
    spec: MethodSpec
    case_name: str
    case: SequentialParityCase | BatchParityCase


def _build_scenarios() -> list[ParityScenario]:
    seq = sequential_cases()
    batches = batch_cases()
    scenarios: list[ParityScenario] = []

    for spec in PARITY_METHOD_SPECS:
        selected = seq if spec.kind == "sequential" else batches
        for case_name, case in selected.items():
            scenarios.append(ParityScenario(spec=spec, case_name=case_name, case=case))

    return scenarios


def _assert_alpha_close(
    alpha_py: list[float | None],
    alpha_r: list[float | None],
    tolerance: float = 1e-12,
) -> None:
    assert len(alpha_py) == len(alpha_r)
    for py_value, r_value in zip(alpha_py, alpha_r):
        if py_value is None or r_value is None:
            assert py_value is None and r_value is None
            continue
        assert py_value == pytest.approx(r_value, abs=tolerance, rel=0.0)


@pytest.fixture(scope="session")
def r_env():
    try:
        return require_r_onlinefdr()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=1)


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param(
            scenario,
            id=f"{scenario.spec.id}__{scenario.case_name}",
        )
        for scenario in _build_scenarios()
    ],
)
def test_onlinefdr_parity_against_live_r(scenario: ParityScenario, r_env) -> None:
    ro, onlinefdr = r_env

    result_py: ParityResult = scenario.spec.run_python(scenario.case)
    result_r: ParityResult = scenario.spec.run_r(ro, onlinefdr, scenario.case)

    assert result_py.decisions == result_r.decisions
    _assert_alpha_close(result_py.alpha, result_r.alpha)
