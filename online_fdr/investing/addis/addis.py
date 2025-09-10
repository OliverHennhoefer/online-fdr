from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultSaffronGammaSequence


class Addis(AbstractSequentialTest):
    """ADDIS: Adaptive Discarding algorithm for online FDR control with conservative nulls.

    ADDIS addresses the critical limitation of existing online FDR methods: power loss when
    null p-values are conservative (stochastically larger than uniform). This frequently
    occurs in practice, especially in industrial A/B testing scenarios with tens of thousands
    of tests.

    The algorithm combines three key innovations:
    1. Adaptive estimation of the fraction of null hypotheses (like SAFFRON)
    2. Adaptive discarding of conservative null hypotheses (unique to ADDIS)
    3. Conservative null compensation through candidate selection

    ADDIS provably controls the FDR and achieves substantial power gains with conservative
    nulls while rarely losing power when nulls are uniform.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).
        wealth: Initial alpha-wealth for purchasing rejection thresholds.
                Must satisfy 0 ≤ wealth ≤ alpha.
        lambda_: Candidate threshold for identifying promising hypotheses.
                 P-values ≤ lambda_ (after scaling) become candidates. Must be in (0, 1).
        tau: Discarding threshold for conservative nulls. P-values > tau are discarded
             (not tested). Must be in (0, 1) with tau > lambda_.

    Attributes:
        alpha0: Original target FDR level.
        wealth0: Initial wealth allocation.
        lambda_: Candidate threshold parameter.
        tau: Discarding threshold parameter.
        num_test: Number of hypotheses tested so far (excluding discarded).
        candidates: Boolean list indicating which tests were candidates.
        reject_idx: Indices of rejected hypotheses.

    Examples:
        >>> # Basic usage with recommended parameters
        >>> addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
        >>> decision = addis.test_one(0.01)  # Test a small p-value
        >>> print(f"Rejected: {decision}")

        >>> # Sequential testing
        >>> p_values = [0.001, 0.3, 0.02, 0.8, 0.005]
        >>> decisions = [addis.test_one(p) for p in p_values]
        >>> discoveries = sum(decisions)

    References:
        Tian, J., and A. Ramdas (2019). "ADDIS: an adaptive discarding algorithm for
        online FDR control with conservative nulls." Advances in Neural Information
        Processing Systems (NeurIPS), 32. Curran Associates, Inc.

        ArXiv: https://arxiv.org/abs/1905.11465
        NeurIPS: https://proceedings.neurips.cc/paper/2019/hash/1d6408264d31d453d556c60fe7d0459e-Abstract.html
    """

    def __init__(
        self,
        alpha: float,
        wealth: float,
        lambda_: float,
        tau: float,
    ):  # fmt: skip
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.lambda_: float = lambda_
        self.tau: float = tau

        validity.check_initial_wealth(wealth, alpha)
        validity.check_candidate_threshold(lambda_)

        self.num_test: int = 0
        self.candidates: list[bool] = []
        self.reject_idx: list[int] = []

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the ADDIS procedure.

        The ADDIS algorithm processes p-values sequentially with three-step logic:
        1. Discard: If p_val > tau, discard the hypothesis (don't test)
        2. Candidate selection: Scale remaining p-value and check if ≤ lambda_
        3. Rejection: Test scaled p-value against adaptive threshold

        Args:
            p_val: P-value to test. Must be in [0, 1].

        Returns:
            True if the null hypothesis is rejected (discovery), False otherwise.

        Raises:
            ValueError: If p_val is not in [0, 1].

        Examples:
            >>> addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
            >>> addis.test_one(0.01)  # Small p-value, likely rejected
            True
            >>> addis.test_one(0.8)   # Large p-value, discarded
            False
            >>> addis.test_one(0.3)   # Medium p-value, tested but not rejected
            False
        """
        validity.check_p_val(p_val)

        if p_val > self.tau:  # discard
            self.alpha = None
            return False

        self.num_test += 1
        self.alpha = self.calc_alpha_t()

        p_val *= 1 / self.tau
        is_candidate = p_val <= self.lambda_  # candidate
        self.candidates.append(is_candidate)

        is_rejected = p_val <= self.alpha  # rejection
        self.reject_idx.append(self.num_test) if is_rejected else None
        return is_rejected

    def calc_alpha_t(self):
        """Calculate the adaptive rejection threshold for the current test.

        The ADDIS threshold adapts based on:
        1. Initial wealth allocation
        2. Number of candidates discovered so far
        3. Wealth earned back from previous discoveries
        4. Conservative null compensation factor (tau - lambda_)

        Returns:
            The adaptive rejection threshold alpha_t, bounded by tau * lambda_.

        Note:
            This is an internal method called by test_one(). The threshold formula
            follows Equation (7) in Tian and Ramdas (2019).
        """
        alpha_t = self.wealth0 * self.seq.calc_gamma(
            self.num_test - sum(self.candidates), None
        )
        if len(self.reject_idx) >= 1:
            tau_1 = self.reject_idx[0]
            c_1_plus = sum(self.candidates[tau_1:])
            alpha_t += (self.alpha0 - self.wealth0) * self.seq.calc_gamma(
                (self.num_test - tau_1 - c_1_plus), None
            )
        if len(self.reject_idx) >= 2:
            alpha_t += self.alpha0 * sum(
                self.seq.calc_gamma(
                    (self.num_test - idx - sum(self.candidates[idx:])),
                    None,
                )
                for idx in self.reject_idx[1:]
            )
        alpha_t *= self.tau - self.lambda_
        return min(self.tau * self.lambda_, alpha_t)
