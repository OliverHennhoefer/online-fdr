from __future__ import annotations

import math
from typing import Any

from online_fdr.core.abstract.abstract_gamma_seq import AbstractGammaSequence
from online_fdr.core.utils.sequence import DefaultLondGammaSequence
from online_fdr.core.utils.validity import check_alpha
from online_fdr.e_values.toolbox import check_e_value

__all__ = ["ELond"]


class ELond:
    """Online FDR control for e-values with e-LOND.

    e-LOND uses the same test levels as p-value LOND but rejects when the
    incoming e-value exceeds the reciprocal test level. Valid e-values give FDR
    control under arbitrary dependence.
    """

    def __init__(
        self,
        alpha: float,
        gamma_seq: AbstractGammaSequence | None = None,
    ):
        check_alpha(alpha)
        self.target_fdr = float(alpha)
        self.num_tests = 0
        self.num_reject = 0
        self.current_level: float | None = None
        self.current_threshold: float | None = None
        self.seq = gamma_seq or DefaultLondGammaSequence(c=0.07720838)

    def test_one(self, e_value: float) -> bool:
        """Test a single e-value and return whether it is rejected."""
        check_e_value(e_value)
        self.num_tests += 1

        gamma_t = self._calc_gamma(self.num_tests)
        self.current_level = self.target_fdr * gamma_t * (self.num_reject + 1)
        self.current_threshold = (
            math.inf if self.current_level <= 0 else 1.0 / self.current_level
        )

        rejected = float(e_value) >= self.current_threshold
        if rejected:
            self.num_reject += 1
        return bool(rejected)

    def _calc_gamma(self, index: int) -> float:
        try:
            return float(self.seq.calc_gamma(index, alpha=1.0))
        except TypeError:
            return float(self.seq.calc_gamma(index))

    @property
    def alpha(self) -> float | None:
        """Current e-LOND test level, retained as a compatibility alias."""
        return self.current_level

    @property
    def num_test(self) -> int:
        """Compatibility alias for the old singular state name."""
        return self.num_tests

    @num_test.setter
    def num_test(self, value: int) -> None:
        self.num_tests = value

    def __getstate__(self) -> dict[str, Any]:
        return self.__dict__.copy()
