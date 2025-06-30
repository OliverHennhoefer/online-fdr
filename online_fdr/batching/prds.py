from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.utils.static import bh


class BatchPRDS(AbstractBatchingTest):
    """Batch FDR control under Positive Regression Dependency on a Subset (PRDS).
    
    This algorithm controls the FDR when p-values within each batch satisfy the
    PRDS condition (positive regression dependency on a subset), with independence
    across batches. It applies a modified Benjamini-Hochberg procedure to each batch
    with adaptively calculated significance levels.
    
    References
    ----------
    [1] Zrnic, T., Ramdas, A., and Jordan, M.I. (2018).
    "Asynchronous Online Testing of Multiple Hypotheses."
    arXiv preprint arXiv:1812.05068.
    
    [2] Benjamini, Y., and Yekutieli, D. (2001).
    "The control of the false discovery rate in multiple testing under dependency."
    Annals of Statistics, 29(4):1165-1188.
    """

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self.alpha0 = alpha

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.num_test: int = 1
        self.r_total: int = 0

        self.alpha_s = []  # only for test

    def test_batch(self, p_vals: list[float]) -> list[bool]:

        batch_size = len(p_vals)
        self.alpha = (
            self.alpha0
            * self.seq.calc_gamma(self.num_test)
            / batch_size
            * (batch_size + self.r_total)
        )
        self.alpha_s.append(self.alpha)
        num_reject, threshold = bh(p_vals, self.alpha)

        self.r_total += num_reject

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals]
