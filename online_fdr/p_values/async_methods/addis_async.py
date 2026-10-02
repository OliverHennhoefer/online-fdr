from __future__ import annotations

from bisect import insort

from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.p_values.async_methods._history import (
    _AsyncHistoryIndex,
    _FenwickCounter,
)
from online_fdr.p_values.async_methods.base import AbstractAsyncTest, _AsyncRecord


class AddisAsync(AbstractAsyncTest):
    """Asynchronous ADDIS lifecycle with conservative-null discarding.

    Completed tests use ADDIS asynchronous accounting. Tests
    still in progress are treated pessimistically as selected in the ADDIS
    conflict accounting, which is the information available to a true lifecycle
    API before their p-values are known.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        wealth: float | None = None,
        lambda_: float = 0.25,
        tau: float = 0.5,
        gamma_seq: DefaultSaffronGammaSequence | None = None,
    ):
        super().__init__(alpha)
        self.lambda_ = lambda_
        self.tau = tau
        self.wealth0 = alpha / 2 if wealth is None else wealth
        validity.check_tau(tau)
        if not 0 < lambda_ < tau:
            raise ValueError("lambda_ must be in (0, tau).")
        if self.wealth0 < 0 or self.wealth0 > alpha:
            raise ValueError("wealth must satisfy 0 <= wealth <= alpha.")
        self.seq = gamma_seq or DefaultSaffronGammaSequence(
            gamma_exp=1.6, c=0.4374901658
        )

    @property
    def candidate_threshold(self) -> float:
        return self.tau * self.lambda_

    @property
    def rejection_cap(self) -> float:
        return self.lambda_

    def _gamma_at_zero_based(self, idx: int) -> float:
        if idx < 0:
            raise ValueError("ADDIS async gamma index became negative.")
        return float(self.seq.calc_gamma(idx + 1))

    def _record_contribution(self, record: _AsyncRecord) -> int:
        if record.finish_stage is None:
            return 1
        if record.p_val is None:
            return 0
        return int(record.p_val <= self.tau) - int(
            record.p_val <= self.candidate_threshold
        )

    def _prepare_history_index(self) -> None:
        signature = (self.tau, self.lambda_)
        if (
            self._history_index is not None
            and self._history_index.signature == signature
        ):
            return

        contributions: list[int] = []
        positions: list[int] = []
        for position, record in enumerate(self._records):
            contributions.append(self._record_contribution(record))
            if record.rejected and record.finish_stage is not None:
                positions.append(position)
        self._history_index = _AsyncHistoryIndex(
            signature, _FenwickCounter(contributions), positions
        )

    def _on_test_started(self, record: _AsyncRecord) -> None:
        assert self._history_index is not None
        self._history_index.counts.append(1)

    def _on_test_finished(self, record: _AsyncRecord) -> None:
        assert self._history_index is not None
        self._history_index.counts.add(
            record.start_stage - 1, self._record_contribution(record) - 1
        )
        if record.rejected:
            # ADDIS gives its first reward to the earliest-started discovery.
            insort(self._history_index.rejections, record.start_stage - 1)

    def _calc_alpha_for_stage(self, stage: int) -> float:
        self._prepare_history_index()
        assert self._history_index is not None
        counts = self._history_index.counts
        if stage == 1:
            return min(
                self.rejection_cap,
                (self.tau - self.lambda_) * self.wealth0 * self._gamma_at_zero_based(0),
            )

        # This counter combines selected/active counts minus candidate counts.
        total = counts.prefix(stage - 1)
        rejection_positions = self._history_index.rejections

        if not rejection_positions:
            alpha_hat = (
                (self.tau - self.lambda_)
                * self.wealth0
                * self._gamma_at_zero_based(total)
            )
            return min(self.rejection_cap, alpha_hat)

        offsets = [
            total - counts.prefix(position + 1) for position in rejection_positions
        ]

        first_gamma = self._gamma_at_zero_based(offsets[0])
        alpha_hat = (
            self.tau - self.lambda_
        ) * self.wealth0 * self._gamma_at_zero_based(total) + (
            self.tau - self.lambda_
        ) * (self.alpha0 - self.wealth0) * first_gamma

        if len(rejection_positions) > 1:
            tail_sum = (
                sum(self._gamma_at_zero_based(offset) for offset in offsets)
                - first_gamma
            )
            alpha_hat += (self.tau - self.lambda_) * self.alpha0 * tail_sum

        return min(self.rejection_cap, alpha_hat)
