from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultLordGammaSequence


class OnlineFallback(AbstractSequentialTest):
    """Online Fallback procedure for controlling the familywise error rate (FWER) online.

    The online fallback procedure, developed by Tian and Ramdas (2021), provides strong
    FWER control for testing an a priori unbounded sequence of hypotheses one by one
    over time without knowing the future. It ensures that with high probability there
    are no false discoveries in the entire sequence.

    This procedure is uniformly more powerful than traditional Alpha-spending methods
    and strongly controls the FWER even under arbitrary dependence among p-values.
    It uses a gamma sequence to allocate alpha budget over time and includes a "fallback"
    mechanism that increases future testing power after making discoveries.

    The method unifies algorithm design concepts from offline FWER control and online
    false discovery rate control, providing a powerful adaptive approach for sequential
    hypothesis testing scenarios.

    Args:
        alpha: Target familywise error rate (e.g., 0.05 for 5% FWER). Must be in (0, 1).

    Attributes:
        alpha0: Original target FWER level.
        last_rejected: Whether the previous hypothesis was rejected.
        seq: Gamma sequence for alpha allocation over time.
        num_test: Number of hypotheses tested so far.
        alpha: Current alpha level for the next test.

    Examples:
        >>> # Create online fallback instance
        >>> fallback = OnlineFallback(alpha=0.05)
        >>> # Test p-values sequentially
        >>> decision1 = fallback.test_one(0.01)  # First test
        >>> decision2 = fallback.test_one(0.03)  # Higher power if previous rejected
        >>> print(f"Decisions: {decision1}, {decision2}")

        >>> # Sequential testing with FWER guarantee
        >>> p_values = [0.001, 0.8, 0.02, 0.9, 0.005]
        >>> decisions = [fallback.test_one(p) for p in p_values]
        >>> print(f"FWER-controlled decisions: {decisions}")

    References:
        Tian, J., and A. Ramdas (2021). "Online control of the familywise error rate."
        Statistical Methods in Medical Research, 30(4):976-993.

        ArXiv preprint: https://arxiv.org/abs/1910.04900
    """

    def __init__(
        self,
        alpha: float,
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.last_rejected: bool = False
        self.seq = DefaultLordGammaSequence(c=0.07720838)

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the online fallback procedure.

        The online fallback procedure adjusts the alpha level based on whether the
        previous test was rejected (fallback mechanism) and allocates additional
        alpha using a gamma sequence. This creates higher power for future tests
        when discoveries are made.

        Args:
            p_val: P-value to test. Must be in [0, 1].

        Returns:
            True if the null hypothesis is rejected (discovery), False otherwise.

        Raises:
            ValueError: If p_val is not in [0, 1].

        Examples:
            >>> fallback = OnlineFallback(alpha=0.05)
            >>> fallback.test_one(0.01)  # First test, uses base alpha
            True
            >>> fallback.test_one(0.03)  # Second test, higher power after discovery
            True
            >>> fallback.test_one(0.04)  # Third test, even higher power
            False

        Note:
            The alpha level increases when the previous test was rejected, implementing
            the "fallback" mechanism that provides additional testing power.
        """
        validity.check_p_val(p_val)
        self.num_test += 1

        prev_alpha = self.alpha if self.alpha is not None else 0.0
        self.alpha = prev_alpha if self.last_rejected else 0.0
        self.alpha += self.alpha0 * self.seq.calc_gamma(self.num_test)

        is_rejected = p_val <= self.alpha
        self.last_rejected = bool(
            is_rejected
        )  # Fix SIM210: Use bool() instead of True if else False

        return is_rejected
