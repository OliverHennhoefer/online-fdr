from typing import Iterable, Sequence


def _step_up_k(sorted_p_vals: Sequence[float], thresholds: Iterable[float]) -> int:
    """Return k = max{i: p_(i) <= threshold_i} using a full step-up scan."""
    k = 0
    for i, (p_val, threshold) in enumerate(zip(sorted_p_vals, thresholds), start=1):
        if p_val <= threshold:
            k = i
    return k


def bh(p_vals: list[float], alpha: float) -> tuple[int, float]:
    """Benjamini-Hochberg step-up procedure."""
    n = len(p_vals)
    if n == 0:
        return 0, 0.0

    sorted_p_vals = sorted(p_vals)
    k = _step_up_k(sorted_p_vals, (alpha * i / n for i in range(1, n + 1)))
    return k, (alpha * k / n if k else 0.0)


def _zero_replaced(p_vals: list[float]) -> list[float]:
    """Sorted batch after replacing its largest p-value with zero.

    Replacing the largest value minimizes every order statistic among all
    one-zero replacements, which maximizes the rejection count of any step-up
    procedure whose critical values depend only on the batch size.
    """
    return [0.0, *sorted(p_vals)[:-1]]


def _bh_r_plus(p_vals: list[float], alpha: float) -> int:
    """Maximum BH rejections after replacing one p-value with zero."""
    if not p_vals:
        return 0
    return bh(_zero_replaced(p_vals), alpha)[0]


def storey_bh(p_vals: list[float], alpha: float, lambda_: float) -> tuple[int, float]:
    """Storey-BH step-up procedure with pi0 estimation."""
    if not p_vals:
        return 0, 0.0
    if not 0 <= lambda_ < 1:
        raise ValueError("lambda_ must be in [0, 1).")

    n = len(p_vals)
    num_above_lambda = sum(1 for p in p_vals if p > lambda_)
    pi0 = min(1.0, (1 + num_above_lambda) / (n * (1 - lambda_)))

    sorted_p_vals = sorted(p_vals)
    k = _step_up_k(sorted_p_vals, ((i * alpha) / (n * pi0) for i in range(1, n + 1)))
    return k, (sorted_p_vals[k - 1] if k else 0.0)


def by(p_vals: list[float], alpha: float) -> tuple[int, float]:
    """Benjamini-Yekutieli step-up procedure."""
    n = len(p_vals)
    if n == 0:
        return 0, 0.0

    sorted_p_vals = sorted(p_vals)
    harmonic_sum = sum(1 / i for i in range(1, n + 1))
    k = _step_up_k(
        sorted_p_vals, (alpha * i / (n * harmonic_sum) for i in range(1, n + 1))
    )
    return k, (alpha * k / (n * harmonic_sum) if k else 0.0)


def _by_r_plus(p_vals: list[float], alpha: float) -> int:
    """Maximum BY rejections after replacing one p-value with zero."""
    if not p_vals:
        return 0
    return by(_zero_replaced(p_vals), alpha)[0]
