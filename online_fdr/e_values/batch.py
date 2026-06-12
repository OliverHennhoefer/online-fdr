from __future__ import annotations

import math
from collections.abc import Sequence

from online_fdr.core.results import BatchDecision
from online_fdr.core.state import StatefulMethodMixin
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


class EBH(StatefulMethodMixin):
    """Batch FDR control with e-values via e-Benjamini-Hochberg.

    References:
        Wang, R. and Ramdas, A. (2022). False discovery rate control with
        e-values. Journal of the Royal Statistical Society: Series B.
        Author code: https://github.com/ruoduwang/e-BH
    """

    error_rate = "FDR"

    def __init__(self, alpha: float):
        check_alpha(alpha)
        self.target_level = float(alpha)
        self._num_hypotheses = 0
        self._num_batches = 0
        self._last_test_level: float | None = None
        self._last_rejection_threshold: float | None = None
        self._last_num_rejections = 0

    @property
    def num_hypotheses(self) -> int:
        return self._num_hypotheses

    @property
    def num_tests(self) -> int:
        return self.num_hypotheses

    @property
    def num_batches(self) -> int:
        return self._num_batches

    @property
    def last_test_level(self) -> float | None:
        return self._last_test_level

    @property
    def last_rejection_threshold(self) -> float | None:
        return self._last_rejection_threshold

    @property
    def current_threshold(self) -> float | None:
        return self.last_rejection_threshold

    @property
    def current_k(self) -> int:
        return self._last_num_rejections

    def test_batch(self, e_values: Sequence[float]) -> list[bool]:
        """Test one batch of e-values and return rejection decisions."""
        return list(self.test_batch_detail(e_values).rejected)

    def test_batch_detail(self, e_values: Sequence[float]) -> BatchDecision:
        """Test one batch of e-values and return immutable decision details."""
        raw_values = list(e_values)
        if not raw_values:
            return BatchDecision(
                rejected=(),
                values=(),
                rejection_threshold=self.last_rejection_threshold,
                batch_index=self.num_batches,
                test_level=self.last_test_level,
                error_rate=self.error_rate,
                metadata={"num_rejections": 0},
            )
        check_e_values(raw_values)
        values = [float(value) for value in raw_values]
        decisions = e_bh(values, self.target_level)
        self._last_num_rejections = sum(decisions)
        self._last_test_level = self.target_level
        self._last_rejection_threshold = (
            len(values) / (self.target_level * self._last_num_rejections)
            if self._last_num_rejections
            else math.inf
        )
        self._num_batches += 1
        self._num_hypotheses += len(values)
        return BatchDecision(
            rejected=tuple(decisions),
            values=tuple(values),
            rejection_threshold=self.last_rejection_threshold,
            batch_index=self.num_batches,
            test_level=self.last_test_level,
            error_rate=self.error_rate,
            metadata={"num_rejections": self._last_num_rejections},
        )
