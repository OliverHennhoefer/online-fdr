import math
import random

import numpy as np
import pytest

from online_fdr.e_values import EBH, ELond, e_bh
from online_fdr.e_values.generation import (
    GaussianEValueGenerator,
    calibrated_p_value_stream,
    gaussian_likelihood_ratio_e_value,
)
from online_fdr.e_values.processes import (
    BettingEProcess,
    LikelihoodRatioEProcess,
    MixtureLikelihoodRatioEProcess,
    value_at_stop,
)
from online_fdr.e_values.toolbox import (
    check_calibrator,
    e_to_p,
    log_product_e_values,
    make_power_calibrator,
    max_e_value,
    p_to_e_power,
    product_e_values,
    weighted_arithmetic_mean,
)


class FixedGamma:
    def __init__(self, values: list[float]):
        self.values = values

    def calc_gamma(self, j: int, **kwargs: object) -> float:
        return self.values[j - 1]


def test_e_bh_rejects_top_k_in_input_order() -> None:
    assert e_bh([1.0, 100.0, 1.0, 100.0], alpha=0.5) == [
        False,
        True,
        False,
        True,
    ]


def test_e_bh_handles_boundaries_ties_and_no_discoveries() -> None:
    assert e_bh([2.0, 2.0], alpha=0.5) == [True, True]
    assert e_bh([3.0, 3.0, 1.0], alpha=0.5) == [True, True, False]
    assert e_bh([1.0, 2.0, 3.0], alpha=0.05) == [False, False, False]


def test_e_bh_can_reject_all_and_support_infinite_values() -> None:
    assert e_bh([10.0, 4.0, 3.0], alpha=0.5) == [True, True, True]
    assert e_bh([0.0, math.inf], alpha=0.5) == [False, True]


@pytest.mark.parametrize("bad_values", [[-1.0], [math.nan], ["x"]])
def test_e_bh_rejects_invalid_e_values(bad_values: list[float]) -> None:
    with pytest.raises(ValueError):
        e_bh(bad_values, alpha=0.05)


def test_ebh_rejects_invalid_e_values_before_state_updates() -> None:
    method = EBH(alpha=0.05)
    with pytest.raises(ValueError, match="index 0"):
        method.test_batch(["x"])  # type: ignore[list-item]
    assert method.num_tests == 0
    assert method.num_batches == 0


def test_ebh_empty_batch_is_noop() -> None:
    method = EBH(alpha=0.05)
    assert method.test_batch([]) == []
    assert method.num_tests == 0
    assert method.num_batches == 0
    assert method.current_threshold is None


def test_ebh_updates_state_after_nonempty_batch() -> None:
    method = EBH(alpha=0.5)
    assert method.test_batch([1.0, 100.0, 1.0, 100.0]) == [
        False,
        True,
        False,
        True,
    ]
    assert method.num_tests == 4
    assert method.num_batches == 1
    assert method.current_k == 2
    assert method.current_threshold == pytest.approx(4.0)


def test_elond_level_threshold_and_rejections() -> None:
    method = ELond(alpha=0.5, gamma_seq=FixedGamma([1.0, 0.5, 0.25]))

    assert method.test_one(2.0) is True
    assert method.current_level == pytest.approx(0.5)
    assert method.current_threshold == pytest.approx(2.0)
    assert method.num_tests == 1
    assert method.num_reject == 1

    assert method.test_one(1.0) is False
    assert method.current_level == pytest.approx(0.5)
    assert method.current_threshold == pytest.approx(2.0)
    assert method.num_tests == 2
    assert method.num_reject == 1


def test_elond_rejects_invalid_e_value() -> None:
    method = ELond(alpha=0.05, gamma_seq=FixedGamma([1.0]))
    with pytest.raises(ValueError):
        method.test_one(-0.1)


def test_e_to_p_and_power_calibrator() -> None:
    assert e_to_p(0.0) == 1.0
    assert e_to_p(math.inf) == 0.0
    assert e_to_p(2.0) == 0.5
    assert e_to_p(0.25) == 1.0
    assert p_to_e_power(0.25, exponent=0.5) == pytest.approx(1.0)
    assert math.isinf(p_to_e_power(0.0, exponent=0.5))
    calibrator = make_power_calibrator(0.5)
    assert calibrator(0.25) == pytest.approx(1.0)


def test_power_calibrator_integrates_to_one_numerically() -> None:
    exponent = 0.5
    grid_size = 20_000
    midpoint_values = [
        p_to_e_power((idx + 0.5) / grid_size, exponent) for idx in range(grid_size)
    ]
    assert sum(midpoint_values) / grid_size == pytest.approx(1.0, rel=5e-3)
    check_calibrator(lambda p_value: p_to_e_power(p_value, exponent))


def test_e_value_merging_helpers() -> None:
    assert weighted_arithmetic_mean([2.0, 4.0], weights=[1.0, 3.0]) == pytest.approx(
        3.5
    )
    assert product_e_values([2.0, 3.0]) == pytest.approx(6.0)
    assert log_product_e_values([2.0, 3.0]) == pytest.approx(math.log(6.0))
    assert product_e_values([0.0, 3.0]) == 0.0
    assert max_e_value([2.0, 5.0, 1.0]) == pytest.approx(5.0 / 3.0)


def test_likelihood_ratio_processes_and_betting_process() -> None:
    process = LikelihoodRatioEProcess(lambda x: float(x))
    assert process.update(1.0) == pytest.approx(math.e)
    assert value_at_stop(process) == pytest.approx(math.e)
    process.reset()
    assert process.current == pytest.approx(1.0)

    mixture = MixtureLikelihoodRatioEProcess(
        [lambda x: float(x), lambda x: 2.0 * float(x)],
        weights=[0.25, 0.75],
    )
    assert mixture.update(0.0) == pytest.approx(1.0)
    assert mixture.update(1.0) == pytest.approx(0.25 * math.e + 0.75 * math.e**2)
    assert mixture.update(1.0) == pytest.approx(0.25 * math.e**2 + 0.75 * math.e**4)
    mixture.reset()
    assert mixture.current == pytest.approx(1.0)

    betting = BettingEProcess(stake=0.5)
    assert betting.update(1.0) == pytest.approx(1.5)
    assert betting.update(-1.0) == pytest.approx(0.75)


def test_e_value_generation_helpers_are_stream_compatible() -> None:
    assert gaussian_likelihood_ratio_e_value(0.0, alt_mean=1.0) == pytest.approx(
        math.exp(-0.5)
    )
    assert calibrated_p_value_stream(
        [0.25, 1.0], exponent=0.5
    ).tolist() == pytest.approx([1.0, 0.5])

    generator = GaussianEValueGenerator(n=10, pi0=0.5, seed=1)
    e_value, label = generator.sample_one()
    assert e_value >= 0
    assert isinstance(label, bool)
    batch, labels = generator.sample_batch(3)
    assert len(batch) == 3
    assert labels.dtype == np.bool_
    assert generator.remaining == 6


def test_ebh_null_stream_statistical_sanity() -> None:
    alpha = 0.1
    n_runs = 500
    n_tests = 100
    rng = random.Random(1)
    any_reject = 0

    for _ in range(n_runs):
        spike = n_tests / alpha
        e_values = [
            spike if rng.random() <= alpha / n_tests else 0.0 for _ in range(n_tests)
        ]
        any_reject += int(any(e_bh(e_values, alpha=alpha)))

    assert any_reject / n_runs <= alpha * 1.5


def test_elond_null_stream_statistical_sanity() -> None:
    alpha = 0.1
    n_runs = 250
    n_tests = 250
    any_reject = 0

    for seed in range(n_runs):
        generator = GaussianEValueGenerator(
            n=n_tests,
            pi0=1.0,
            alt_mean=3.0,
            seed=10_000 + seed,
        )
        method = ELond(alpha=alpha)
        decisions = [method.test_one(generator.sample_one()[0]) for _ in range(n_tests)]
        any_reject += int(any(decisions))

    assert any_reject / n_runs <= alpha * 1.7
