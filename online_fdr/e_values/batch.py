from __future__ import annotations

import math
from collections.abc import Sequence

from online_fdr.core.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.core.results import BatchDecision
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


class EBH(AbstractBatchingTest):
    """Batch FDR control with e-values via e-Benjamini-Hochberg.

    References:
        Wang, R. and Ramdas, A. (2022). False discovery rate control with
        e-values. Journal of the Royal Statistical Society: Series B.
        Author code: https://github.com/ruoduwang/e-BH
    """

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self._last_num_rejections = 0

    @property
    def current_k(self) -> int:
        return self._last_num_rejections

    def test_batch(self, e_values: Sequence[float]) -> list[bool]:
        """Test one batch of e-values and return rejection decisions."""
        raw_values = list(e_values)
        if not raw_values:
            return []
        decisions = e_bh(raw_values, self.target_level)
        self._last_num_rejections = sum(decisions)
        threshold = (
            len(raw_values) / (self.target_level * self._last_num_rejections)
            if self._last_num_rejections
            else math.inf
        )
        self._set_test_level(self.target_level, rejection_threshold=threshold)
        self._advance_batch(len(raw_values))
        return decisions

    def test_batch_detail(self, e_values: Sequence[float]) -> BatchDecision:
        """Return details using the same validation and state as ``test_batch``."""
        return super().test_batch_detail(e_values)
