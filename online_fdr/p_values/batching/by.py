from online_fdr.core.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import (
    DefaultSaffronGammaSequence,
)
from online_fdr.core.utils.static import by


class BatchBY(AbstractBatchingTest):
    """Benjamini-Yekutieli extension for online batch testing.

    BatchBY extends the online batching framework to use the Benjamini-Yekutieli (BY)
    procedure within each batch. This is a conservative extension for settings where
    the within-batch independence assumption may be violated, such as spatial
    statistics, time series analysis, or genomics with linkage disequilibrium.

    The BY procedure is a modification of the Benjamini-Hochberg (BH) procedure
    that uses harmonic weights for arbitrary dependence in a fixed batch. While
    this comes at the cost of reduced power compared to BH, it provides a more
    conservative within-batch correction.

    The algorithm follows the online batching framework, allocating alpha budget
    across batches using a gamma sequence and adjusting for inter-batch accounting
    through the beta_t correction mechanism. It is not a direct onlineFDR parity
    method or a separately published BatchBY author implementation.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).

    Attributes:
        alpha0: Original target FDR level.
        num_test: Number of batches tested so far.
        seq: Gamma sequence for alpha allocation across batches.
        r_s_plus: Maximum possible rejections for each batch.
        r_s: Rejection indicators for each batch.
        r_total: Total number of rejections across all batches.
        r_sums: Cumulative rejection counts for dependency tracking.
        alpha_s: Alpha levels used for each batch.

    Examples:
        >>> # Basic usage for dependent p-values
        >>> by_test = BatchBY(alpha=0.05)
        >>> # Test correlated p-values (e.g., from spatial data)
        >>> batch1 = [0.001, 0.002, 0.15, 0.8]  # May be dependent
        >>> decisions1 = by_test.test_batch(batch1)
        >>> print(f"BY discoveries in batch 1: {sum(decisions1)}")

        >>> # Sequential dependent batches
        >>> batch2 = [0.03, 0.04, 0.006, 0.4]   # Also potentially dependent
        >>> decisions2 = by_test.test_batch(batch2)
        >>> print(f"BY discoveries in batch 2: {sum(decisions2)}")

        >>> # Comparing with standard BH under dependence
        >>> from online_fdr.p_values.batching import BatchBH
        >>> bh_test = BatchBH(alpha=0.05)
        >>> by_test = BatchBY(alpha=0.05)
        >>> # BY is more conservative than BH under within-batch dependence

    Notes:
        The BY procedure is particularly recommended when:
        - P-values exhibit positive dependence
        - Spatial or temporal correlation is present
        - A conservative BY-style within-batch correction is required
        - The exact dependence structure is unknown

        Trade-off: Enhanced robustness comes at the cost of reduced power
        compared to the standard Benjamini-Hochberg procedure.

    References:
        Benjamini, Y., and D. Yekutieli (2001). "The control of the false discovery
        rate in multiple testing under dependency." Annals of Statistics, 29(4):1165-1188.

        Zrnic, T., D. Jiang, A. Ramdas, and M. I. Jordan (2020). "The Power of
        Batching in Multiple Hypothesis Testing." Proceedings of the 37th
        International Conference on Machine Learning (ICML), PMLR, 119:11504-11515.
    """

    def __init__(self, alpha: float):
        """Initialize BatchBY with FDR control level.

        Args:
            alpha: Target FDR control level. Must be in (0, 1).

        Raises:
            ValueError: If alpha is not in (0, 1).
        """
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.num_test: int = 1

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        self.r_s_plus: list[int] = []
        self.r_s: list[int] = []
        self.r_total: int = 0
        self.r_sums: list[int] = [0]
        self.alpha_s: list[float] = []

    @property
    def num_tests(self) -> int:
        """Number of batches processed so far."""
        return self.num_test - 1

    @num_tests.setter
    def num_tests(self, value: int) -> None:
        self.num_test = value + 1

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values using the Benjamini-Yekutieli procedure.

        The BY procedure uses harmonic weights in the rejection threshold calculation.
        This method adapts the static BY procedure to the online batching framework
        as a conservative extension.

        The algorithm:
        1. Calculates adaptive alpha level for the current batch
        2. Applies the BY procedure with harmonic correction
        3. Updates statistics for future batch calculations
        4. Computes R+ for inter-batch accounting

        Args:
            p_vals: List of p-values for the current batch.

        Returns:
            List of boolean values indicating which hypotheses are rejected.

        Examples:
            >>> by_test = BatchBY(alpha=0.05)
            >>> # Test potentially dependent p-values
            >>> decisions = by_test.test_batch([0.001, 0.002, 0.15, 0.8])
            >>> print(f"Rejections with BY: {sum(decisions)}")

        Note:
            The BY procedure is more conservative than BH within a batch.
        """
        p_vals_local = list(p_vals)
        n_batch = len(p_vals_local)
        if n_batch == 0:
            return []
        validity.check_p_vals_batch(p_vals_local)
        if self.num_test == 1:
            self.alpha = (
                self.alpha0  # fmt: skip
                * self.seq.calc_gamma(j=1)
            )
        else:
            self.alpha = (
                sum(self.seq.calc_gamma(i) for i in range(1, self.num_test + 1))
                * self.alpha0  # fmt: skip
            )
            self.alpha -= sum(
                [
                    self.alpha_s[i]
                    * self.r_s_plus[i]
                    / (self.r_s_plus[i] + self.r_sums[i + 1])
                    for i in range(0, self.num_test - 1)
                ]
            )
            self.alpha *= (n_batch + self.r_total) / n_batch

        num_reject, threshold = by(p_vals_local, self.alpha)

        self.r_sums.append(self.r_total)
        self.r_sums[1:self.num_test] = \
            [x + num_reject for x in self.r_sums[1:self.num_test]]  # fmt: skip
        self.r_total += num_reject
        self.alpha_s.append(self.alpha)

        r_plus = 0
        adjusted = list(p_vals_local)
        for i, p_val in enumerate(adjusted):
            adjusted[i] = 0.0
            r_plus = max(r_plus, by(adjusted, self.alpha)[0])
            adjusted[i] = p_val
        self.r_s_plus.append(r_plus)

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals_local]
