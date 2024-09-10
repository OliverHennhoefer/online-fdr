from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import bh


class BatchPRDS(AbstractBatchingTest):

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self.alpha0 = alpha

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.num_test: int = 1
        self.r_total: int = 0

    def test_batch(self, p_vals: list[float]) -> list[bool]:

        batch_size = len(p_vals)
        self.alpha = (
            self.alpha0
            * self.seq.calc_gamma(self.num_test)
            / batch_size
            * (batch_size + self.r_total)
        )
        num_reject, threshold = bh(p_vals, self.alpha)

        self.r_total += num_reject

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals]
