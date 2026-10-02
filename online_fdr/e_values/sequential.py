from __future__ import annotations

import math
from typing import Any

from online_fdr.core.abstract.abstract_gamma_seq import AbstractGammaSequence
from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.results import TestDecision
from online_fdr.core.utils.sequence import DefaultLondGammaSequence
from online_fdr.e_values.toolbox import check_e_value

__all__ = ["ELond"]


class ELond(AbstractSequentialTest):
    """Online FDR control for e-values with e-LOND.

    e-LOND uses the same test levels as p-value LOND but rejects when the
    incoming e-value exceeds the reciprocal test level. Valid e-values give FDR
    control under arbitrary dependence.

    References:
        Xu, Z. and Ramdas, A. (2024). Online multiple testing with e-values.
        Proceedings of AISTATS 2024.
        Author code: https://github.com/neilzxu/evalue-omt
    """

    def __init__(
        self,
        alpha: float,
        gamma_seq: AbstractGammaSequence | None = None,
    ):
        super().__init__(alpha)
        self.num_reject = 0
        self.seq = gamma_seq or DefaultLondGammaSequence(c=0.07720838)

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        # Schema-1 snapshots before the shared state used this private name.
        if "_current_level" in state:
            state["_last_test_level"] = state.pop("_current_level")
        return state

    @property
    def current_level(self) -> float | None:
        return self.last_test_level

    def test_one(self, e_value: float) -> bool:
        """Test a single e-value and return whether it is rejected."""
        check_e_value(e_value)
        gamma_t = self._calc_gamma(self.num_hypotheses + 1)
        level = self.target_level * gamma_t * (self.num_reject + 1)
        threshold = math.inf if level <= 0 else 1.0 / level
        self._set_test_level(level, rejection_threshold=threshold)
        self._advance_hypotheses()

        rejected = float(e_value) >= threshold
        if rejected:
            self.num_reject += 1
        return rejected

    def test_one_detail(self, e_value: float) -> TestDecision:
        """Return details using the same validation and state as ``test_one``."""
        return super().test_one_detail(e_value)

    def _calc_gamma(self, index: int) -> float:
        try:
            return float(self.seq.calc_gamma(index, alpha=1.0))
        except TypeError:
            return float(self.seq.calc_gamma(index))
