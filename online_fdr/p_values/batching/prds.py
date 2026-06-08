from online_fdr.core.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultSaffronGammaSequence
from online_fdr.core.utils.static import bh


class BatchPRDS(AbstractBatchingTest):
    """Batch FDR control under Positive Regression Dependency on a Subset (PRDS).

    BatchPRDS provides FDR control when p-values within each batch satisfy the
    PRDS condition - a form of positive dependence that is less restrictive than
    independence but more structured than arbitrary dependence. This makes it
    suitable for applications where there is positive correlation between test
    statistics, such as in genomics or neuroimaging.

    The algorithm extends the classical Benjamini-Hochberg procedure to the online
    batching setting under PRDS conditions. It allocates alpha budget across batches
    using a gamma sequence and adjusts the significance level based on the number
    of previous discoveries and current batch size.

    PRDS (Positive Regression Dependency on a Subset) means that for any subset
    of true null hypotheses, the joint distribution of corresponding p-values is
    stochastically smaller when conditioned on smaller values of other p-values.
    This includes many practically relevant dependence structures.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).

    Attributes:
        alpha0: Original target FDR level.
        seq: Gamma sequence for alpha allocation across batches.
        num_test: Number of batches tested so far.
        r_total: Total number of rejections across all batches.
        alpha_s: Alpha levels used for each batch (stored for testing).

    Examples:
        >>> # Basic usage under PRDS conditions
        >>> prds_test = BatchPRDS(alpha=0.05)
        >>> # Test batch with positive correlation (e.g., genetic data)
        >>> batch1 = [0.001, 0.005, 0.15, 0.8]  # Positively correlated
        >>> decisions1 = prds_test.test_batch(batch1)
        >>> print(f"PRDS discoveries: {sum(decisions1)}")

        >>> # Subsequent batch - alpha adjusted for previous discoveries
        >>> batch2 = [0.02, 0.03, 0.4, 0.9]
        >>> decisions2 = prds_test.test_batch(batch2)
        >>> print(f"Total discoveries: {prds_test.r_total}")

        >>> # PRDS vs standard BH under positive dependence
        >>> # PRDS maintains FDR control while BH may be conservative

    Notes:
        PRDS conditions are satisfied in many practical scenarios:
        - Genomic association studies with linkage disequilibrium
        - Neuroimaging with spatial smoothing
        - Financial time series with positive correlation
        - Social network analysis with homophily

        The algorithm provides exact FDR control under PRDS while maintaining
        good power compared to more conservative methods like BY.

    References:
        Zrnic, T., A. Ramdas, and M. I. Jordan (2018). "Asynchronous Online
        Testing of Multiple Hypotheses." arXiv preprint arXiv:1812.05068.

        Benjamini, Y., and D. Yekutieli (2001). "The control of the false discovery
        rate in multiple testing under dependency." Annals of Statistics, 29(4):1165-1188.

        Benjamini, Y., and D. Yekutieli (2001). "On the Adaptive Control of the
        False Discovery Rate in Multiple Testing With Independent Statistics."
        Journal of Educational and Behavioral Statistics, 25(1):60-83.
    """

    def __init__(self, alpha: float):
        """Initialize BatchPRDS with FDR control level.

        Args:
            alpha: Target FDR control level. Must be in (0, 1).

        Raises:
            ValueError: If alpha is not in (0, 1).
        """
        super().__init__(alpha)
        self.alpha0 = alpha

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.num_test: int = 1
        self.r_total: int = 0

        self.alpha_s: list[float] = []  # only for test

    @property
    def num_tests(self) -> int:
        """Number of batches processed so far."""
        return self.num_test - 1

    @num_tests.setter
    def num_tests(self, value: int) -> None:
        self.num_test = value + 1

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values under PRDS conditions.

        The algorithm calculates an adaptive significance level based on the
        gamma sequence, current batch size, and total previous discoveries.
        It then applies the standard Benjamini-Hochberg procedure with this
        adapted alpha level.

        The alpha calculation incorporates:
        - Gamma sequence value for the current batch number
        - Batch size normalization
        - Adjustment for accumulated discoveries

        Args:
            p_vals: List of p-values for the current batch. Must satisfy
                   PRDS conditions within the batch.

        Returns:
            List of boolean values indicating which hypotheses are rejected.

        Examples:
            >>> prds_test = BatchPRDS(alpha=0.05)
            >>> # Test positively dependent p-values
            >>> decisions = prds_test.test_batch([0.001, 0.002, 0.15, 0.8])
            >>> print(f"PRDS rejections: {sum(decisions)}")

        Note:
            This method assumes that p-values within the batch satisfy PRDS
            conditions. If this assumption is violated, FDR control may not
            be maintained.
        """
        p_vals_local = list(p_vals)
        batch_size = len(p_vals_local)
        if batch_size == 0:
            return []
        validity.check_p_vals_batch(p_vals_local)
        self.alpha = (
            self.alpha0
            * self.seq.calc_gamma(self.num_test)
            / batch_size
            * (batch_size + self.r_total)
        )
        self.alpha_s.append(self.alpha)
        num_reject, threshold = bh(p_vals_local, self.alpha)

        self.r_total += num_reject

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals_local]
