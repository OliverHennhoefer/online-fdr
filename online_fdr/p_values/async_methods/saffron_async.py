from __future__ import annotations

from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.p_values.async_methods._history import (
    _AsyncHistoryIndex,
    _FenwickCounter,
)
from online_fdr.p_values.async_methods.base import AbstractAsyncTest, _AsyncRecord


class SaffronAsync(AbstractAsyncTest):
    """Asynchronous SAFFRONstar lifecycle for overlapping online tests.

    This implements the async SAFFRONstar accounting used by the Bioconductor
    onlineFDR package for Zrnic, Ramdas, and Jordan's asynchronous online testing
    framework. It assigns a test level at ``start_test`` time and only uses
    completed prior tests for candidate and rejection accounting.
    """

    def __init__(
        self,
        alpha: float = 0.05,
        wealth: float | None = None,
        lambda_: float = 0.5,
        gamma_seq: DefaultSaffronGammaSequence | None = None,
    ):
        super().__init__(alpha)
        self.wealth0 = alpha / 2 if wealth is None else wealth
        self.lambda_ = lambda_
        validity.check_initial_wealth(self.wealth0, alpha)
        validity.check_candidate_threshold(lambda_)
        self.seq = gamma_seq or DefaultSaffronGammaSequence(
            gamma_exp=1.6, c=0.4374901658
        )

    def _gamma_at_zero_based(self, idx: int) -> float:
        if idx < 0:
            raise ValueError("SAFFRONstar gamma index became negative.")
        return float(self.seq.calc_gamma(idx + 1))

    def _prepare_history_index(self) -> None:
        signature = (self.lambda_,)
        if (
            self._history_index is not None
            and self._history_index.signature == signature
        ):
            return

        candidates: list[int] = []
        finish_counts = [0] * len(self._records)
        for record in self._records:
            candidates.append(
                int(
                    record.finish_stage is not None
                    and record.p_val is not None
                    and record.p_val <= self.lambda_
                )
            )
            if record.rejected and record.finish_stage is not None:
                finish_counts[record.finish_stage - 1] += 1
        positions = [
            position
            for position, count in enumerate(finish_counts)
            for _ in range(count)
        ]
        self._history_index = _AsyncHistoryIndex(
            signature, _FenwickCounter(candidates), positions
        )

    def _on_test_started(self, record: _AsyncRecord) -> None:
        assert self._history_index is not None
        self._history_index.counts.append(0)

    def _on_test_finished(self, record: _AsyncRecord) -> None:
        assert self._history_index is not None
        assert record.p_val is not None and record.finish_stage is not None
        if record.p_val <= self.lambda_:
            self._history_index.counts.add(record.start_stage - 1, 1)
        if record.rejected:
            # Discoveries sharing a completion stage have identical positions.
            self._history_index.rejections.append(record.finish_stage - 1)

    def _calc_alpha_for_stage(self, stage: int) -> float:
        self._prepare_history_index()
        assert self._history_index is not None
        counts = self._history_index.counts
        i = stage - 1
        if stage == 1:
            return min(
                self.lambda_,
                (1 - self.lambda_) * self._gamma_at_zero_based(0) * self.wealth0,
            )

        candsum = counts.prefix(i)
        rejection_positions = self._history_index.rejections
        num_rejections = len(rejection_positions)

        if num_rejections == 0:
            alpha_tilde = (
                (1 - self.lambda_)
                * self.wealth0
                * self._gamma_at_zero_based(i - candsum)
            )
            return min(self.lambda_, alpha_tilde)

        c_plus = [
            candsum - counts.prefix(position + 1) for position in rejection_positions
        ]

        first_gamma = self._gamma_at_zero_based(
            i - rejection_positions[0] - c_plus[0] - 1
        )
        alpha_tilde = (1 - self.lambda_) * (
            self.wealth0 * self._gamma_at_zero_based(i - candsum)
            + (self.alpha0 - self.wealth0) * first_gamma
        )

        if num_rejections > 1:
            tail_sum = (
                sum(
                    self._gamma_at_zero_based(i - position - c_val - 1)
                    for position, c_val in zip(rejection_positions, c_plus)
                )
                - first_gamma
            )
            alpha_tilde += (1 - self.lambda_) * self.alpha0 * tail_sum

        return min(self.lambda_, alpha_tilde)
