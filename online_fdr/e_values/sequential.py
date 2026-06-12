from __future__ import annotations

import math

from online_fdr.core.abstract.abstract_gamma_seq import AbstractGammaSequence
from online_fdr.core.results import TestDecision
from online_fdr.core.state import StatefulMethodMixin
from online_fdr.core.utils.sequence import DefaultLondGammaSequence
from online_fdr.core.utils.validity import check_alpha
from online_fdr.e_values.toolbox import check_e_value

__all__ = ["ELond"]


class ELond(StatefulMethodMixin):
    """Online FDR control for e-values with e-LOND.

    e-LOND uses the same test levels as p-value LOND but rejects when the
    incoming e-value exceeds the reciprocal test level. Valid e-values give FDR
    control under arbitrary dependence.

    References:
        Xu, Z. and Ramdas, A. (2024). Online multiple testing with e-values.
        Proceedings of AISTATS 2024.
        Author code: https://github.com/neilzxu/evalue-omt
    """

    error_rate = "FDR"

    def __init__(
        self,
        alpha: float,
        gamma_seq: AbstractGammaSequence | None = None,
    ):
        check_alpha(alpha)
        self.target_level = float(alpha)
        self._num_hypotheses = 0
        self.num_reject = 0
        self._current_level: float | None = None
        self._last_rejection_threshold: float | None = None
        self.seq = gamma_seq or DefaultLondGammaSequence(c=0.07720838)

    @property
    def num_hypotheses(self) -> int:
        return self._num_hypotheses

    @property
    def num_tests(self) -> int:
        return self.num_hypotheses

    @property
    def last_test_level(self) -> float | None:
        return self._current_level

    @property
    def current_level(self) -> float | None:
        return self.last_test_level

    @property
    def last_rejection_threshold(self) -> float | None:
        return self._last_rejection_threshold

    @property
    def current_threshold(self) -> float | None:
        return self.last_rejection_threshold

    def test_one(self, e_value: float) -> bool:
        """Test a single e-value and return whether it is rejected."""
        return self.test_one_detail(e_value).rejected

    def test_one_detail(self, e_value: float) -> TestDecision:
        """Test a single e-value and return immutable decision details."""
        check_e_value(e_value)
        self._num_hypotheses += 1

        gamma_t = self._calc_gamma(self.num_hypotheses)
        self._current_level = self.target_level * gamma_t * (self.num_reject + 1)
        self._last_rejection_threshold = (
            math.inf if self._current_level <= 0 else 1.0 / self._current_level
        )

        rejected = float(e_value) >= self._last_rejection_threshold
        if rejected:
            self.num_reject += 1
        return TestDecision(
            rejected=bool(rejected),
            value=float(e_value),
            rejection_threshold=self.last_rejection_threshold,
            index=self.num_hypotheses,
            test_level=self.last_test_level,
            error_rate=self.error_rate,
        )

    def _calc_gamma(self, index: int) -> float:
        try:
            return float(self.seq.calc_gamma(index, alpha=1.0))
        except TypeError:
            return float(self.seq.calc_gamma(index))
