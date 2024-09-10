from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import storey_bh


class BatchStoreyBH(AbstractBatchingTest):

    def __init__(self, alpha: float, lambda_: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.num_test: int = 1
        self.lambda_: float = lambda_

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.candidate: [int] = []
        self.r_s_plus: [float] = []
        self.r_s: [bool] = []
        self.r_total: int = 0
        self.r_sums: [float] = [0]
        self.alpha_s: [float] = []

    def test_batch(self, p_vals: list[float]) -> list[bool]:

        cand_sum = sum([i > self.lambda_ for i in p_vals])
        self.candidate.append(
            cand_sum / (cand_sum + (max(p_vals) <= self.lambda_))
        )  # fmt: skip

        n_batch = len(p_vals)
        if self.num_test == 1:
            self.alpha = (
                self.alpha0  # fmt: skip
                * self.seq.calc_gamma(j=1)
            )
        else:
            self.alpha = (
                sum(
                    self.seq.calc_gamma(i) for i in range(1, self.num_test + 1)
                )
                * self.alpha0  # fmt: skip
            )
            self.alpha -= sum(
                [
                    self.alpha_s[i]
                    * self.candidate[i]
                    * self.r_s_plus[i]
                    / (self.r_s_plus[i] + self.r_sums[i + 1])
                    for i in range(0, self.num_test - 1)
                ]
            )
            self.alpha *= (n_batch + self.r_total) / n_batch

        num_reject, threshold = storey_bh(p_vals, self.alpha, self.lambda_)

        self.r_sums.append(self.r_total)
        self.r_sums[1:self.num_test] = \
            [x + num_reject for x in self.r_sums[1:self.num_test]]  # fmt: skip
        self.r_total += num_reject
        self.alpha_s.append(self.alpha)

        r_plus = 0
        for i, p_val in enumerate(p_vals):
            p_vals[i] = 0
            r_plus = max(r_plus, storey_bh(p_vals, self.alpha, self.lambda_)[0])
            p_vals[i] = p_val
        self.r_s_plus.append(r_plus)

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals]
