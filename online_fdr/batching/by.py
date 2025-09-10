from online_fdr.abstract.abstract_batching_test import AbstractBatchingTest
from online_fdr.utils.sequence import (
    DefaultSaffronGammaSequence,
)
from online_fdr.utils.static import by


class BatchBY(AbstractBatchingTest):
    """Benjamini-Yekutieli procedure for online batch FDR control under dependence.

    BatchBY extends the online batching framework to use the Benjamini-Yekutieli (BY)
    procedure, which provides FDR control even under arbitrary dependence among
    p-values. This makes it particularly suitable for situations where the
    independence assumption may be violated, such as in spatial statistics,
    time series analysis, or genomics with linkage disequilibrium.

    The BY procedure is a modification of the Benjamini-Hochberg (BH) procedure
    that uses harmonic weights to maintain FDR control under arbitrary dependence.
    While this comes at the cost of reduced power compared to BH, it provides
    robust FDR control in challenging dependence scenarios.

    The algorithm follows the online batching framework, allocating alpha budget
    across batches using a gamma sequence and adjusting for inter-batch dependencies
    through the β_t correction mechanism.

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
        >>> from online_fdr.batching import BatchBH
        >>> bh_test = BatchBH(alpha=0.05)
        >>> by_test = BatchBY(alpha=0.05)
        >>> # BY provides guaranteed FDR control, BH may not under dependence

    Notes:
        The BY procedure is particularly recommended when:
        - P-values exhibit positive dependence
        - Spatial or temporal correlation is present
        - Conservative FDR control is required
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
        self.r_s_plus: [float] = []
        self.r_s: [bool] = []
        self.r_total: int = 0
        self.r_sums: [float] = [0]
        self.alpha_s: [float] = []

    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """Test a batch of p-values using the Benjamini-Yekutieli procedure.

        The BY procedure provides FDR control under arbitrary dependence among
        p-values by using harmonic weights in the rejection threshold calculation.
        This method adapts the static BY procedure to the online batching framework.

        The algorithm:
        1. Calculates adaptive alpha level for the current batch
        2. Applies the BY procedure with harmonic correction
        3. Updates statistics for future batch calculations
        4. Computes R⁺ for inter-batch dependency handling

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
            The BY procedure is more conservative than BH but maintains FDR
            control even when p-values are positively dependent.
        """
        n_batch = len(p_vals)
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

        num_reject, threshold = by(p_vals, self.alpha)

        self.r_sums.append(self.r_total)
        self.r_sums[1:self.num_test] = \
            [x + num_reject for x in self.r_sums[1:self.num_test]]  # fmt: skip
        self.r_total += num_reject
        self.alpha_s.append(self.alpha)

        r_plus = 0
        for i, p_val in enumerate(p_vals):
            p_vals[i] = 0
            r_plus = max(r_plus, by(p_vals, self.alpha)[0])
            p_vals[i] = p_val
        self.r_s_plus.append(r_plus)

        self.num_test += 1
        return [p_val <= threshold for p_val in p_vals]
