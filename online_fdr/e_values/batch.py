from __future__ import annotations

import math
from collections.abc import Sequence

from online_fdr.core.utils.validity import check_alpha
from online_fdr.e_values.toolbox import check_e_values

__all__ = ["EBH", "e_bh"]


def e_bh(e_values: Sequence[float], alpha: float) -> list[bool]:
    """Apply the base e-BH procedure to a fixed batch of e-values.

    The procedure rejects the largest ``k`` e-values, where ``k`` is the largest
    index satisfying ``e_(k) >= m / (alpha * k)`` after sorting descending.
    Ties are broken stably by original input order.

    This is the base e-BH procedure of Wang and Ramdas (2022), which controls
    FDR under arbitrary dependence for valid e-values.
    """
    check_alpha(alpha)
    raw_values = list(e_values)
    if not raw_values:
        return []
    check_e_values(raw_values)
    values = [float(value) for value in raw_values]

    m = len(values)
    ordered = sorted(enumerate(values), key=lambda item: (-item[1], item[0]))
    k_star = 0
    for rank, (_, value) in enumerate(ordered, start=1):
        threshold = m / (alpha * rank)
        if value >= threshold:
            k_star = rank

    rejected = [False] * m
    for original_idx, _ in ordered[:k_star]:
        rejected[original_idx] = True
    return rejected


class EBH:
    """Batch FDR control with e-values via e-Benjamini-Hochberg.

    References:
        Wang, R. and Ramdas, A. (2022). False discovery rate control with
        e-values. Journal of the Royal Statistical Society: Series B.
        Author code: https://github.com/ruoduwang/e-BH
    """

    def __init__(self, alpha: float):
        check_alpha(alpha)
        self.target_fdr = float(alpha)
        self.num_tests = 0
        self.num_batches = 0
        self.current_threshold: float | None = None
        self.current_k = 0

    def test_batch(self, e_values: Sequence[float]) -> list[bool]:
        """Test one batch of e-values and return rejection decisions."""
        raw_values = list(e_values)
        if not raw_values:
            return []
        check_e_values(raw_values)
        values = [float(value) for value in raw_values]
        decisions = e_bh(values, self.target_fdr)
        self.current_k = sum(decisions)
        self.current_threshold = (
            len(values) / (self.target_fdr * self.current_k)
            if self.current_k
            else math.inf
        )
        self.num_batches += 1
        self.num_tests += len(values)
        return decisions
