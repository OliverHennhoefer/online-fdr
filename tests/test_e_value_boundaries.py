from __future__ import annotations

import math

import pytest

from online_fdr.e_values import (
    EBH,
    LikelihoodRatioEProcess,
    MixtureLikelihoodRatioEProcess,
    log_product_e_values,
    product_e_values,
    weighted_arithmetic_mean,
)


@pytest.mark.parametrize("weights", [[1.0, 1.0], [1e308, 1e308]])
def test_large_finite_weights_preserve_the_same_arithmetic_mixture(weights):
    assert weighted_arithmetic_mean([2.0, 4.0], weights) == pytest.approx(3.0)
    process = MixtureLikelihoodRatioEProcess(
        [lambda x: math.log(2.0), lambda x: math.log(4.0)], weights
    )
    assert process.current == pytest.approx(1.0)
    assert process.update(None) == pytest.approx(3.0)


def test_zero_weight_infinity_is_ignored_and_tiny_positive_weight_is_retained():
    assert weighted_arithmetic_mean([math.inf, 2.0], [0.0, 1.0]) == pytest.approx(2.0)
    assert weighted_arithmetic_mean([math.inf, 2.0], [1e-308, 1e308]) == math.inf
    process = MixtureLikelihoodRatioEProcess(
        [lambda x: math.inf, lambda x: 0.0], [1e-308, 1e308]
    )
    assert process.current == pytest.approx(1.0)
    assert process.update(None) == math.inf


def test_small_positive_weights_can_still_contribute_finite_evidence():
    assert weighted_arithmetic_mean([1e308, 0.0], [1e-308, 1e308]) == pytest.approx(
        1e-308, rel=1e-12, abs=0.0
    )


def test_ordinary_weighted_mean_preserves_exact_rejection_boundary():
    merged = weighted_arithmetic_mean([2.0, 4.0], [1.0, 3.0])
    assert merged == 3.5
    assert EBH(alpha=2.0 / 7.0).test_batch([merged]) == [True]


@pytest.mark.parametrize("values", [[0.0, math.inf], [math.inf, 0.0]])
@pytest.mark.parametrize("merge", [log_product_e_values, product_e_values])
def test_undefined_zero_infinity_products_are_order_independent(values, merge):
    with pytest.raises(ValueError, match="zero and infinity"):
        merge(values)


@pytest.mark.parametrize("bad_value", [math.nan, -math.inf])
def test_likelihood_ratio_rejects_undefined_update_without_changing_capital(bad_value):
    process = LikelihoodRatioEProcess(lambda x: x)
    process.update(math.inf)
    with pytest.raises(ValueError, match="NaN"):
        process.update(bad_value)
    assert process.current == math.inf


@pytest.mark.parametrize("failure", ["nan", "exception", "opposing_infinity"])
def test_mixture_commits_all_component_capitals_together(failure):
    def second_component(value):
        if value == "bad":
            if failure == "exception":
                raise RuntimeError("component failed")
            return math.nan if failure == "nan" else -math.inf
        return math.inf if failure == "opposing_infinity" else 0.5

    process = MixtureLikelihoodRatioEProcess([lambda x: 1.0, second_component])
    control = MixtureLikelihoodRatioEProcess([lambda x: 1.0, second_component])
    process.update("good")
    control.update("good")
    before = process.component_log_currents.copy()
    with pytest.raises((ValueError, RuntimeError)):
        process.update("bad")
    assert process.component_log_currents == before
    assert process.update("good") == control.update("good")


def test_mixture_prior_cannot_be_changed_by_mutating_returned_weights():
    process = MixtureLikelihoodRatioEProcess([lambda x: 0.0, lambda x: 1.0], [1.0, 3.0])
    observed_weights = process.weights
    observed_weights[0] = 1.0
    assert process.weights == pytest.approx([0.25, 0.75])
