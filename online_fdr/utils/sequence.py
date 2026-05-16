import math

from online_fdr.abstract.abstract_gamma_seq import AbstractGammaSequence


class DefaultLondGammaSequence(AbstractGammaSequence):
    """Default gamma sequence for LOND (Levels based On Number of Discoveries).

    This gamma sequence is specifically designed for LOND procedures and provides
    the recommended decay rate for optimal power-stability trade-offs. The sequence
    incorporates both logarithmic and exponential decay components to balance
    early power with long-term FDR control.

    The sequence is defined as:
    γⱼ = c × α × log(max(j,2)) / (j × exp(√log(j)))

    Args:
        c: Normalization constant controlling the overall scale of the sequence.

    Attributes:
        c: The normalization constant.

    Examples:
        >>> # Standard LOND gamma sequence
        >>> gamma_seq = DefaultLondGammaSequence(c=0.07720838)
        >>> gamma_1 = gamma_seq.calc_gamma(1, alpha=0.05)
        >>> gamma_10 = gamma_seq.calc_gamma(10, alpha=0.05)
        >>> print(f"γ₁ = {gamma_1:.6f}, γ₁₀ = {gamma_10:.6f}")

    References:
        Javanmard, A., and A. Montanari (2018). "Online rules for control of false
        discovery rate and false discovery exceedance." Annals of Statistics,
        46(2):526-554.
    """

    def __init__(self, c: float):
        """Initialize the LOND gamma sequence.

        Args:
            c: Normalization constant. Recommended value: c ≈ 0.07720838.
        """
        super().__init__(c)

    def calc_gamma(self, j: int, **kwargs: object) -> float:
        """Calculate the gamma value for the j-th test.

        Args:
            j: Test index (1-based).
            **kwargs: Must contain 'alpha' - the target FDR level.

        Returns:
            The gamma value for test j.

        Examples:
            >>> seq = DefaultLondGammaSequence(c=0.07720838)
            >>> gamma_5 = seq.calc_gamma(5, alpha=0.05)
        """
        alpha = kwargs.get("alpha")
        if not isinstance(alpha, int | float):
            raise ValueError(
                "alpha must be provided as a numeric value for LOND gamma sequence."
            )
        return (
            self.c
            * float(alpha)
            * (math.log(max(j, 2)) / (j * math.exp(math.sqrt(math.log(j)))))
        )


class DefaultLordGammaSequence(AbstractGammaSequence):
    """Default gamma sequence for LORD (Levels based On Recent Discovery) procedures.

    This gamma sequence is optimized for LORD algorithms and provides the balance
    between early power and long-term FDR control. Unlike LOND sequences, LORD
    sequences don't require the alpha parameter since they work with alpha wealth
    dynamics.

    The sequence is defined as:
    γⱼ = c × log(max(j,2)) / (j × exp(√log(j)))

    Args:
        c: Normalization constant controlling sequence scale.

    Examples:
        >>> # Standard LORD gamma sequence
        >>> gamma_seq = DefaultLordGammaSequence(c=0.07720838)
        >>> gamma_values = [gamma_seq.calc_gamma(j) for j in range(1, 6)]
        >>> print(f"First 5 gamma values: {gamma_values}")

    References:
        Javanmard, A., and A. Montanari (2018). "Online rules for control of false
        discovery rate and false discovery exceedance." Annals of Statistics,
        46(2):526-554.
    """

    def __init__(self, c: float):
        """Initialize the LORD gamma sequence.

        Args:
            c: Normalization constant. Recommended value: c ≈ 0.07720838.
        """
        super().__init__(c)

    def calc_gamma(self, j: int, **kwargs: object) -> float:
        """Calculate the gamma value for position j in the sequence.

        Args:
            j: Position index (1-based).
            **kwargs: Additional arguments (unused for LORD sequences).

        Returns:
            The gamma value for position j.
        """
        return (
            self.c  # fmt: skip
            * math.log(max(j, 2))
            / (j * math.exp(math.sqrt(math.log(j))))
        )


class DefaultSaffronGammaSequence(AbstractGammaSequence):
    """Default gamma sequence for SAFFRON (Spectral Approach for FDR with Online N-tests).

    SAFFRON uses a power-law gamma sequence that provides excellent performance
    for adaptive online FDR control. The sequence can operate in two modes:
    with or without a normalization constant c.

    The sequence is defined as:
    - With c: γⱼ = c / j^(gamma_exp)
    - Without c: γⱼ = j^(gamma_exp)

    Args:
        gamma_exp: Exponent controlling the decay rate. Recommended: 1.6.
        c: Normalization constant. If None, uses pure power law.

    Examples:
        >>> # Standard SAFFRON sequence with recommended parameters
        >>> gamma_seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
        >>> gamma_values = [gamma_seq.calc_gamma(j) for j in range(1, 6)]
        >>> print(f"SAFFRON γ values: {gamma_values}")

    References:
        Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan (2018).
        "SAFFRON: an adaptive algorithm for online control of the false discovery rate."
        Proceedings of the 35th International Conference on Machine Learning (ICML),
        PMLR, 80:4286-4294.
    """

    def __init__(self, gamma_exp: float, c: float | None):
        """Initialize the SAFFRON gamma sequence.

        Args:
            gamma_exp: Decay exponent. Recommended value: 1.6.
            c: Normalization constant. Recommended value: 0.4374901658.
               If None, uses pure power law without normalization.
        """
        if c is None:
            raise ValueError(
                "DefaultSaffronGammaSequence requires a finite normalization constant c."
            )
        if gamma_exp <= 1:
            raise ValueError("gamma_exp must be > 1 for a summable gamma sequence.")
        super().__init__(gamma_exp=gamma_exp, c=c)

    def calc_gamma(self, j: int, *args: object) -> float:
        """Calculate gamma value for position j.

        Args:
            j: Position index (1-based).
            *args: Additional arguments (unused).

        Returns:
            Gamma value for position j.
        """
        return float(self.c / math.pow(float(j), self.gamma_exp))


class DependentLordGammaSequence(AbstractGammaSequence):
    """Proposed default gamma sequence for the 'dependent' LORD [1]_ variant.

    References
    ----------
    [1] Javanmard, A., and A. Montanari.
    Online rules for control of false discovery rate
    and false discovery exceedance.
    Annals of Statistics, 46(2):526-554, 2018."""

    def __init__(self, c: float, b0: float):
        super().__init__(c=c, b0=b0)

    def calc_gamma(self, j: int, **kwargs) -> float:
        return self.c / (j * (math.log(max(j, 2)) ** 3))


class BatchGammaSequenceSmall(AbstractGammaSequence):
    """Proposed default gamma sequence for Batch-BH and Batch-StBH [1]_
    with batche sizes up to 100.

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2019).
    The Power of Batching in Multiple Hypothesis Testing.
    International Conference on Artificial Intelligence and Statistics."""

    def __init__(self, gamma_exp: float):
        super().__init__(gamma_exp=gamma_exp)

    def calc_gamma(self, j: int, **kwargs) -> float:
        batch_size = kwargs.get("batch_size")
        if batch_size is None:
            raise ValueError("batch_size must be provided in kwargs.")
        batch_size = int(batch_size)
        if self.gamma_exp <= 1:
            raise ValueError("gamma_exp must be > 1 for a summable gamma sequence.")
        sum_gamma = sum(s ** (-self.gamma_exp) for s in range(1, batch_size + 1))
        normalization_factor = 1.0 / sum_gamma
        return float(normalization_factor * math.pow(float(j), -self.gamma_exp))


class BatchGammaSequenceLarge(AbstractGammaSequence):
    """Proposed default gamma sequence for Batch-BH and Batch-StBH [1]_
    with batch sizes of more than 100.

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2019).
    The Power of Batching in Multiple Hypothesis Testing.
    International Conference on Artificial Intelligence and Statistics."""

    def __init__(self):
        super().__init__()

    def calc_gamma(self, j: int, **kwargs) -> float:
        return 0.5 if j < 3 else 0.0


class BatchBHPolynomialGammaSequence(AbstractGammaSequence):
    """Polynomial gamma sequence for BatchBH with small batch sizes (< 100).

    This is the 'poly' gamma sequence from the official BatchBH implementation
    corresponding to the paper by Zrnic et al. (2020). In the authors'
    supplementary code, the unnormalized sequence is j^-2 and the normalizing
    coefficient is computed over np.arange(1, 1e7).

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2020).
    The Power of Batching in Multiple Hypothesis Testing.
    International Conference on Artificial Intelligence and Statistics.
    [2] Official implementation: https://proceedings.mlr.press/v108/zrnic20a.html
    """

    _COEFFICIENT = 0.6079271388115668

    def __init__(self):
        super().__init__()

    def calc_gamma(self, j: int, **kwargs) -> float:
        """Calculate polynomial gamma sequence.

        This implements the polynomial decay gamma sequence used in the
        official BatchBH implementation for small batch sizes.
        """
        return float(self._COEFFICIENT / math.pow(float(j), 2.0))


class BatchBHHalfGammaSequence(AbstractGammaSequence):
    """Half gamma sequence for BatchBH with large batch sizes (>= 100).

    This is the 'half' gamma sequence from the official BatchBH implementation
    corresponding to the paper by Zrnic et al. (2020).

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2020).
    The Power of Batching in Multiple Hypothesis Testing.
    International Conference on Artificial Intelligence and Statistics.
    [2] Official implementation: https://proceedings.mlr.press/v108/zrnic20a.html
    """

    def __init__(self):
        super().__init__()

    def calc_gamma(self, j: int, **kwargs) -> float:
        """Calculate half gamma sequence.

        This implements the 'half' gamma sequence used in the
        official BatchBH implementation for large batch sizes.
        """
        # Based on the official implementation pattern
        # Returns 1/2 for the first two batches, 0 thereafter
        return 0.5 if j <= 2 else 0.0


class BatchBHAdaptiveGammaSequence(AbstractGammaSequence):
    """Adaptive gamma sequence that switches based on batch size.

    This mimics the official BatchBH implementation that uses different
    gamma sequences based on batch size: 'poly' for small batches (< 100)
    and 'half' for large batches (>= 100).

    References
    ----------
    [1] Zrnic, T., Jiang, D., Ramdas, A., & Jordan, M.I. (2020).
    The Power of Batching in Multiple Hypothesis Testing.
    International Conference on Artificial Intelligence and Statistics.
    [2] Official implementation: https://proceedings.mlr.press/v108/zrnic20a.html
    """

    def __init__(self):
        super().__init__()
        self.poly_seq: BatchBHPolynomialGammaSequence = BatchBHPolynomialGammaSequence()
        self.half_seq: BatchBHHalfGammaSequence = BatchBHHalfGammaSequence()

    def calc_gamma(self, j: int, **kwargs) -> float:
        """Calculate gamma using adaptive sequence selection.

        Args:
            j: Batch number (1-indexed)
            **kwargs: Must include 'batch_size' parameter

        Returns:
            Gamma value for batch j
        """
        batch_size = kwargs.get("batch_size")
        if batch_size is None:
            raise ValueError("batch_size must be provided in kwargs")

        if batch_size < 100:
            return self.poly_seq.calc_gamma(j, **kwargs)
        else:
            return self.half_seq.calc_gamma(j, **kwargs)
