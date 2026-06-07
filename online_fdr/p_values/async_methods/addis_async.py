from __future__ import annotations

from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.p_values.async_methods.base import AbstractAsyncTest, AsyncRecord


class AddisAsync(AbstractAsyncTest):
    """Asynchronous ADDIS lifecycle with conservative-null discarding.

    Completed tests follow the onlineFDR ADDIS ``async=TRUE`` accounting. Tests
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

    def _is_selected(self, record: AsyncRecord) -> bool:
        return record.p_val is not None and record.p_val <= self.tau

    def _is_candidate_available(self, idx: int, stage: int) -> bool:
        record = self.records[idx]
        return (
            self._is_available(record, stage)
            and record.p_val is not None
            and record.p_val <= self.candidate_threshold
        )

    def _selected_prefix_count(self, end_exclusive: int) -> int:
        count = 0
        for record in self.records[:end_exclusive]:
            if record.finish_stage is None:
                count += 1
            else:
                count += int(self._is_selected(record))
        return count

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
        if stage == 1:
            return min(
                self.rejection_cap,
                (self.tau - self.lambda_) * self.wealth0 * self._gamma_at_zero_based(0),
            )

        previous = self.records[: stage - 1]
        selected_or_active = sum(
            (
                self._is_selected(record)
                if self._is_available(record, stage)
                else self._is_active_at(record, stage)
            )
            for record in previous
        )
        candidate_count = sum(
            self._is_candidate_available(idx, stage) for idx in range(stage - 1)
        )
        rejection_positions = [
            idx
            for idx, record in enumerate(previous)
            if bool(record.rejected) and self._is_available(record, stage)
        ]

        if not rejection_positions:
            alpha_hat = (self.tau - self.lambda_) * self.wealth0 * self._gamma_at_zero_based(
                selected_or_active - candidate_count
            )
            return min(self.rejection_cap, alpha_hat)

        c_plus: list[int] = []
        kappa_star: list[int] = []
        for position in rejection_positions:
            kappa_star.append(self._selected_prefix_count(position + 1))
            c_plus.append(
                self._candidate_count_between_available(
                    position + 1,
                    max(stage - 2, position + 1),
                    stage,
                )
            )

        first_gamma = self._gamma_at_zero_based(
            selected_or_active - kappa_star[0] - c_plus[0]
        )
        alpha_hat = (
            (self.tau - self.lambda_)
            * self.wealth0
            * self._gamma_at_zero_based(selected_or_active - candidate_count)
            + (self.tau - self.lambda_)
            * (self.alpha0 - self.wealth0)
            * first_gamma
        )

        if len(rejection_positions) > 1:
            tail_sum = sum(
                self._gamma_at_zero_based(selected_or_active - k_star - c_val)
                for k_star, c_val in zip(kappa_star, c_plus)
            ) - first_gamma
            alpha_hat += (self.tau - self.lambda_) * self.alpha0 * tail_sum

        return min(self.rejection_cap, alpha_hat)
