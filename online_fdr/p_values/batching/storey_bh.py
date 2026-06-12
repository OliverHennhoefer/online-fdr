from collections.abc import Sequence

from online_fdr.core.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence


class BatchStoreyBH(AbstractBatchingTest):
    """Storey-BH batch procedure for online batch-level FDR control."""

    def __init__(self, alpha: float, lambda_: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.lambda_: float = lambda_

        if not 0 < lambda_ < 1:
            raise ValueError("lambda_ must be between 0 and 1.")

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.k_s: list[int] = []
        self.pi0_estimates: list[float] = []
        self.r_s_plus: list[int] = []
        self.r_sums: list[int] = []
        self.alpha_s: list[float] = []

    def test_batch(self, p_vals: Sequence[float]) -> list[bool]:
        p_vals_local = list(p_vals)
        n_batch = len(p_vals_local)
        if n_batch == 0:
            return []
        validity.check_p_vals_batch(p_vals_local)

        batch_number = self.num_batches + 1
        if batch_number == 1:
            alpha_batch = self.alpha0 * self.seq.calc_gamma(j=1)
        else:
            gamma_sum = self.alpha0 * sum(
                self.seq.calc_gamma(i) for i in range(1, batch_number + 1)
            )
            total_rejections = sum(self.r_sums)
            penalty = 0.0
            for idx in range(batch_number - 1):
                denom = self.r_s_plus[idx] + (total_rejections - self.r_sums[idx])
                if denom > 0:
                    penalty += (
                        self.k_s[idx] * self.alpha_s[idx] * (self.r_s_plus[idx] / denom)
                    )
            alpha_batch = (gamma_sum - penalty) * (
                (n_batch + total_rejections) / n_batch
            )

        batch_decisions, pi0_batch = self._storey_batch_decisions(
            p_vals_local, alpha_batch
        )
        num_reject = sum(batch_decisions)

        self.k_s.append(int(max(p_vals_local) > self.lambda_))
        self.pi0_estimates.append(pi0_batch)
        self.r_sums.append(num_reject)
        self.alpha_s.append(alpha_batch)
        r_plus = self._calculate_r_plus(p_vals_local, alpha_batch)
        self.r_s_plus.append(r_plus)

        threshold = max(
            (
                p_val
                for p_val, rejected in zip(p_vals_local, batch_decisions)
                if rejected
            ),
            default=0.0,
        )
        self._set_test_level(alpha_batch, rejection_threshold=threshold)
        self._advance_batch(n_batch)
        return batch_decisions

    def _calculate_r_plus(
        self, p_vals: list[float], alpha_batch: float | None = None
    ) -> int:
        """Compute R+ via one-coordinate replacement p_i <- 0 on same batch size."""
        if not p_vals:
            return 0
        if alpha_batch is None:
            if self.last_test_level is None:
                raise AssertionError(
                    "BatchStoreyBH alpha threshold was not initialized."
                )
            alpha_batch = float(self.last_test_level)

        r_plus = 0
        n = len(p_vals)
        for i in range(n):
            pseudo_pvals = p_vals[:i] + p_vals[i + 1 :] + [0.0]
            pseudo_rejections, _ = self._storey_batch_decisions(
                pseudo_pvals, alpha_batch
            )
            r_plus = max(r_plus, sum(pseudo_rejections))
        return r_plus

    def _storey_batch_decisions(
        self, p_vals: list[float], alpha_batch: float
    ) -> tuple[list[bool], float]:
        """Replicate onlineFDR's BatchStBH inner Storey-BH rejection rule."""
        n_batch = len(p_vals)
        if n_batch == 0:
            return [], 0.0

        num_above_lambda = sum(1 for p in p_vals if p > self.lambda_)
        pi0_batch = (num_above_lambda + 1.0) / ((1.0 - self.lambda_) * n_batch)

        order_desc = sorted(range(n_batch), key=p_vals.__getitem__, reverse=True)
        inv_order = [0] * n_batch
        for rank, idx in enumerate(order_desc):
            inv_order[idx] = rank

        adjusted_desc: list[float] = []
        running_min = 1.0
        for rank, idx in enumerate(order_desc):
            j_val = n_batch - rank
            candidate = (n_batch / j_val) * pi0_batch * p_vals[idx]
            running_min = min(running_min, candidate)
            adjusted_desc.append(min(1.0, running_min))

        return (
            [adjusted_desc[inv_order[i]] <= alpha_batch for i in range(n_batch)],
            pi0_batch,
        )
