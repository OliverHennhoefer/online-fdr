import math

import numpy as np
import pytest

from online_fdr.e_values import EBH, GaussianEValueGenerator, p_to_e_power


def test_power_calibrator_recovers_finite_result_from_overflowing_power():
    # A high-precision evaluation of .001 * (1e-310 ** -.999) is finite.
    value = p_to_e_power(1e-310, exponent=0.001)
    assert math.isfinite(value)
    assert value == pytest.approx(4.89778819368445e306, rel=1e-12)


def test_power_calibrator_returns_infinity_for_unrepresentable_result():
    assert p_to_e_power(math.ulp(0.0), exponent=0.001) == math.inf


@pytest.mark.parametrize(
    ("p_value", "exponent", "expected"),
    [(0.25, 0.5, 1.0), (0.0625, 0.5, 2.0), (1.0, 0.25, 0.25), (0.0, 0.5, math.inf)],
)
def test_power_calibrator_preserves_ordinary_values(p_value, exponent, expected):
    assert p_to_e_power(p_value, exponent) == expected


def test_power_calibrator_preserves_exact_ebh_rejection_boundary():
    value = p_to_e_power(0.0625, exponent=0.5)
    assert EBH(alpha=0.5).test_batch([value]) == [True]


@pytest.mark.parametrize("bad_size", [0, -1, True, False, 0.5, 1.5, math.inf, math.nan])
@pytest.mark.parametrize("parameter", ["n", "batch_size"])
def test_gaussian_generator_rejects_invalid_constructor_sizes(parameter, bad_size):
    arguments = {"n": 5, "pi0": 0.5, parameter: bad_size}
    with pytest.raises(ValueError, match=f"{parameter} must be a positive integer"):
        GaussianEValueGenerator(**arguments)


@pytest.mark.parametrize("bad_size", [0, -1, True, False, 0.5, 1.5, math.inf, math.nan])
def test_gaussian_generator_invalid_batch_size_preserves_stream(bad_size):
    generator = GaussianEValueGenerator(5, 0.5, seed=7)
    control = GaussianEValueGenerator(5, 0.5, seed=7)
    assert generator.sample_one() == control.sample_one()

    with pytest.raises(ValueError, match="size must be a positive integer"):
        generator.sample_batch(bad_size)

    assert generator.current_idx == 1
    assert generator.remaining == 4
    actual_values, actual_labels = generator.sample_batch(2)
    expected_values, expected_labels = control.sample_batch(2)
    np.testing.assert_array_equal(actual_values, expected_values)
    np.testing.assert_array_equal(actual_labels, expected_labels)


def test_gaussian_generator_default_batch_size_consumes_short_final_batch():
    generator = GaussianEValueGenerator(5, 0.5, batch_size=2)
    assert [len(generator.sample_batch()[0]) for _ in range(3)] == [2, 2, 1]
    assert generator.remaining == 0
    with pytest.raises(StopIteration):
        generator.sample_batch()
