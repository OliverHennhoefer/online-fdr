from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultLordGammaSequence


class LordDiscard(AbstractSequentialTest):
    """Implements LORD++ with discarding as
    described in [1]_.

    References
    ----------
    [1] Tian, J., and A. Ramdas.
    ADDIS: an adaptive discarding algorithm for
    online FDR control with conservative nulls.
    In Advances in Neural Information Processing Systems
    (NeurIPS 2019), vol. 32. Curran Associates, Inc., 2019."""

    def __init__(self, alpha: float, wealth: float, tau: float):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.tau: float = tau
        validity.check_initial_wealth(wealth, alpha)
        validity.check_tau(tau)

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self._num_selected: int = 0
        self.first_reject: int | None = None  # first rejection index
        self.last_reject: list = []  # without first rejection

    @property
    def num_selected(self) -> int:
        """Number of hypotheses not discarded by the tau rule."""
        return self._num_selected

    def _compute_alpha(self, tested_index: int) -> float:
        alpha = self.wealth0 * self.seq.calc_gamma(tested_index)

        if self.first_reject is not None:
            alpha += (self.tau * self.alpha0 - self.wealth0) * self.seq.calc_gamma(
                tested_index - self.first_reject
            )

        if self.last_reject:
            alpha += (
                self.tau
                * self.alpha0
                * sum(
                    self.seq.calc_gamma(tested_index - reject_idx)
                    for reject_idx in self.last_reject
                )
            )

        return float(alpha)

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self._advance_hypotheses()
        next_tested_index = self.num_selected + 1
        # Expose the same per-step threshold semantics as onlineFDR,
        # including discarded p-values.
        alpha_t = self._compute_alpha(next_tested_index)
        threshold = min(self.tau, alpha_t)
        self._set_test_level(alpha_t, rejection_threshold=threshold)

        if p_val > self.tau:
            return False  # discard

        self._num_selected = next_tested_index

        is_rejected = p_val <= threshold

        if is_rejected:
            if self.first_reject is None:
                self.first_reject = self.num_selected
            else:
                self.last_reject.append(self.num_selected)

        return is_rejected
