from __future__ import annotations

from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.p_values.async_methods.base import AbstractAsyncTest


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

    def _is_candidate_available(self, idx: int, stage: int) -> bool:
        record = self.records[idx]
        return (
            self._is_available(record, stage)
            and record.p_val is not None
            and record.p_val <= self.lambda_
        )

    def _candidate_count_between_available(
        self, start_idx: int, end_idx: int, stage: int
    ) -> int:
        if end_idx < start_idx:
            return 0
        return sum(
            self._is_candidate_available(idx, stage)
            for idx in range(start_idx, end_idx + 1)
            if idx < len(self.records)
        )

    def _calc_alpha_for_stage(self, stage: int) -> float:
        i = stage - 1
        if stage == 1:
            return min(
                self.lambda_,
                (1 - self.lambda_) * self._gamma_at_zero_based(0) * self.wealth0,
            )

        candsum = sum(
            self._is_candidate_available(idx, stage) for idx in range(stage - 1)
        )
        rejection_positions = self._available_rejection_positions(stage)
        num_rejections = len(rejection_positions)

        if num_rejections == 0:
            alpha_tilde = (
                (1 - self.lambda_)
                * self.wealth0
                * self._gamma_at_zero_based(i - candsum)
            )
            return min(self.lambda_, alpha_tilde)

        c_plus: list[int] = []
        for position in rejection_positions:
            c_plus.append(
                self._candidate_count_between_available(
                    position + 1,
                    max(i - 1, position + 1),
                    stage,
                )
            )

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
