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
                Must satisfy 0 < wealth < alpha.
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
        validity.check_tau(tau)
        if not 0 <= lambda_ < tau:
            raise ValueError("lambda_ must satisfy 0 <= lambda_ < tau.")

        self.num_test: int = 0
        self.candidates: list[bool] = []
        self.selected: list[bool] = []
        self._candidate_prefix: list[int] = [0]
        self._selected_prefix: list[int] = [0]
        self.reject_idx: list[int] = []

        self.seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the ADDIS procedure.

        The ADDIS algorithm processes p-values sequentially with:
        1. Selected-set tracking via tau (p-values <= tau)
        2. Candidate tracking via lambda_ (p-values <= lambda_)
        3. Rejection against the adaptive alpha threshold

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
            >>> addis.test_one(0.8)   # Large p-value, not selected
            False
            >>> addis.test_one(0.3)   # Medium p-value, typically not rejected
            False
        """
        validity.check_p_val(p_val)

        self.alpha = self.calc_alpha_t()
        is_rejected = p_val <= self.alpha  # rejection uses unscaled p-values

        is_selected = p_val <= self.tau
        is_candidate = p_val <= self.lambda_
        self.selected.append(is_selected)
        self.candidates.append(is_candidate)
        self._selected_prefix.append(self._selected_prefix[-1] + int(is_selected))
        self._candidate_prefix.append(self._candidate_prefix[-1] + int(is_candidate))

        self.num_test += 1
        if is_rejected:
            self.reject_idx.append(self.num_test)
        return is_rejected

    def calc_alpha_t(self) -> float:
        """Calculate the adaptive rejection threshold for the current test.

        The ADDIS threshold adapts based on:
        1. Initial wealth allocation
        2. Number of candidates discovered so far
        3. Wealth earned back from previous discoveries
        4. Conservative null compensation factor (tau - lambda_)

        Returns:
            The adaptive rejection threshold alpha_t, bounded by lambda_.

        Note:
            This is an internal method called by test_one(). The threshold formula
            follows Equation (7) in Tian and Ramdas (2019).
        """
        selected_so_far = self._selected_prefix[-1]
        candidates_so_far = self._candidate_prefix[-1]

        base_idx = selected_so_far - candidates_so_far
        alpha_t = (self.tau - self.lambda_) * self.wealth0 * self._gamma_from_offset(
            base_idx
        )

        if not self.reject_idx:
            return min(self.lambda_, alpha_t)

        first_reject = self.reject_idx[0]
        first_term = self._gamma_from_offset(
            selected_so_far
            - self._selected_prefix[first_reject]
            - (candidates_so_far - self._candidate_prefix[first_reject])
        )
        alpha_t += (self.tau - self.lambda_) * (self.alpha0 - self.wealth0) * first_term

        if len(self.reject_idx) > 1:
            tail_terms = sum(
                self._gamma_from_offset(
                    selected_so_far
                    - self._selected_prefix[reject_idx]
                    - (candidates_so_far - self._candidate_prefix[reject_idx])
                )
                for reject_idx in self.reject_idx[1:]
            )
            alpha_t += (self.tau - self.lambda_) * self.alpha0 * tail_terms

        return min(self.lambda_, alpha_t)

    def _gamma_from_offset(self, offset: int) -> float:
        """Map zero-based ADDIS gamma offsets to the one-based gamma sequence API."""
        if offset < 0:
            raise ValueError("ADDIS gamma offset must be non-negative.")
        return float(self.seq.calc_gamma(offset + 1, None))
