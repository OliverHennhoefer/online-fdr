from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from online_fdr.core.utils.validity import (
    check_calibrator,
    check_e_value,
    check_e_values,
    check_nonnegative_weights,
    check_p_val,
)

__all__ = [
    "check_calibrator",
    "check_e_value",
    "check_e_values",
    "check_nonnegative_weights",
    "e_to_p",
    "log_product_e_values",
    "make_power_calibrator",
    "max_e_value",
    "mixture_e_value",
    "p_to_e_power",
    "product_e_values",
    "weighted_arithmetic_mean",
]


def e_to_p(e_value: float) -> float:
    """Convert an e-value to the conservative p-value ``min(1, 1 / e)``."""
    check_e_value(e_value)
    value = float(e_value)
    if value == 0:
        return 1.0
    if math.isinf(value):
        return 0.0
    return min(1.0, 1.0 / value)


def p_to_e_power(p_value: float, exponent: float) -> float:
    """Calibrate a p-value into an e-value with ``k * p ** (k - 1)``.

    The exponent must be in ``(0, 1)``. The calibrator integrates to one on
    ``[0, 1]`` and is decreasing, so applying it to a valid p-value yields an
    e-value. This is the power calibrator from Vovk and Wang (2021).
    """
    check_p_val(p_value)
    if not 0 < exponent < 1:
        raise ValueError("exponent must be in (0, 1).")
    if p_value == 0:
        return math.inf
    try:
        return float(exponent * math.pow(float(p_value), exponent - 1.0))
    except OverflowError:
        # The power may overflow even when multiplication by k brings the
        # complete calibrated value back into the representable range.
        log_value = math.log(exponent) + (exponent - 1.0) * math.log(float(p_value))
        try:
            return float(math.exp(log_value))
        except OverflowError:
            return math.inf


def _prepare_weights(
    length: int,
    weights: Sequence[float] | None,
    mismatch_message: str = "weights must have the same length as e_values.",
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if length == 0:
        raise ValueError("at least one e-value is required.")
    if weights is None:
        normalized = (1.0 / length,) * length
        return normalized, (math.log(normalized[0]),) * length
    if len(weights) != length:
        raise ValueError(mismatch_message)
    check_nonnegative_weights(weights)
    # Sum Python floats so an overflowing NumPy total does not emit a warning.
    total = sum(float(weight) for weight in weights)
    # Preserve ordinary arithmetic when representable; scale only an overflowing
    # total. Retain a log representation for positive weights that underflow.
    scale = 1.0 if math.isfinite(total) else float(max(weights))
    if not math.isfinite(total):
        total = math.fsum(float(weight) / scale for weight in weights)
    normalized = tuple(float(weight) / scale / total for weight in weights)
    log_scale, log_total = math.log(scale), math.log(total)
    logs = tuple(
        math.log(value)
        if value > 0
        else (math.log(weight) - log_scale - log_total if weight > 0 else -math.inf)
        for weight, value in zip(weights, normalized)
    )
    return normalized, logs


def weighted_arithmetic_mean(
    e_values: Sequence[float],
    weights: Sequence[float] | None = None,
) -> float:
    """Merge e-values by weighted arithmetic mean.

    This is valid for arbitrary dependence when all inputs are valid e-values
    and weights are fixed independently of the null evidence, as in the
    averaging rule of Vovk and Wang (2021).
    """
    check_e_values(e_values)
    normalized, log_weights = _prepare_weights(len(e_values), weights)
    if any(
        math.isinf(float(e)) and log_weight != -math.inf
        for e, log_weight in zip(e_values, log_weights)
    ):
        return math.inf
    return float(
        sum(
            float(e) * weight
            if weight > 0
            else math.exp(math.log(float(e)) + log_weight)
            for e, weight, log_weight in zip(e_values, normalized, log_weights)
            if log_weight != -math.inf and e > 0
        )
    )


def mixture_e_value(
    e_values: Sequence[float],
    weights: Sequence[float] | None = None,
) -> float:
    """Alias for weighted arithmetic e-value merging."""
    return weighted_arithmetic_mean(e_values, weights)


def log_product_e_values(e_values: Sequence[float]) -> float:
    """Return the log product of e-values.

    Products are valid under independence or suitable conditional/sequential
    validity assumptions supplied by the caller.
    A product containing both zero and infinity is undefined and raises
    ``ValueError``, independently of input order.
    """
    check_e_values(e_values)
    values = [float(value) for value in e_values]
    has_zero = 0.0 in values
    has_infinity = math.inf in values
    if has_zero and has_infinity:
        raise ValueError("a product containing both zero and infinity is undefined.")
    if has_zero:
        return -math.inf
    if has_infinity:
        return math.inf
    total = sum(math.log(value) for value in values)
    return float(total)


def product_e_values(e_values: Sequence[float]) -> float:
    """Return the product of e-values in ordinary scale."""
    log_value = log_product_e_values(e_values)
    if log_value == -math.inf:
        return 0.0
    if log_value == math.inf:
        return math.inf
    try:
        return float(math.exp(log_value))
    except OverflowError:
        return math.inf


def max_e_value(e_values: Sequence[float]) -> float:
    """Conservative max merge, ``max(e_values) / len(e_values)``.

    The scaling is deliberate: the raw maximum is not generally an e-value under
    arbitrary dependence.
    """
    check_e_values(e_values)
    if not e_values:
        raise ValueError("at least one e-value is required.")
    max_value = max(float(value) for value in e_values)
    return math.inf if math.isinf(max_value) else float(max_value / len(e_values))


def make_power_calibrator(exponent: float) -> Callable[[float], float]:
    """Return the power p-to-e calibrator for a fixed exponent."""
    if not 0 < exponent < 1:
        raise ValueError("exponent must be in (0, 1).")
    return lambda p_value: p_to_e_power(p_value, exponent)
