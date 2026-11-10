from numbers import Integral
from typing import Any

from online_fdr.core.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.core.utils import validity
from online_fdr.core.utils.sequence import DefaultLordGammaSequence


class LORDMemoryDecay(AbstractSequentialTest):
    """LORD variant with memory decay for time series anomaly detection.

    This variant is designed for non-stationary time series where recent
    discoveries are more relevant than older ones. Unlike standard LORD
    variants, it does NOT track wealth. Instead, it uses a decay factor
    to down-weight older rejections and a smoothing parameter to control
    the base detection threshold.

    The algorithm spends:
        alpha_t = alpha * eta * max(gamma(t), 1-delta)
                  + alpha * sum_r decay(t,r) * gamma(t-r-l)

    where the sum is over past rejections r, and decay(t,r) = delta^(t-r-l).

    Key differences from standard LORD:
    - No wealth tracking or accumulation
    - Uses decay to forget old discoveries
    - Ensures minimum spending via max(gamma(t), 1-delta)

    References
    ----------
    [1] Rebjock, Q., B. Kurt, T. Januschowski, and L. Callot.
    Online false discovery rate control for anomaly detection in time series.
    In Advances in Neural Information Processing Systems (NeurIPS 2021),
    vol. 34, pp. 26487-26498. Curran Associates, Inc., 2021.
    """

    def __init__(self, alpha: float, delta: float = 0.99, eta: float = 0.5, l: int = 0):
        """
        Parameters
        ----------
        alpha : float
            Overall significance level in (0, 1). This is the target FDR level.
        delta : float, optional
            Decay factor in (0, 1) for down-weighting older rejections.
            Default is 0.99 (1% decay per time step). Lower values mean
            faster forgetting of old discoveries.
        eta : float, optional
            Smoothing/scaling factor that controls the base detection threshold.
            - eta * alpha * max(gamma(t), 1-delta) is spent at each step
            - eta=0.1: Conservative (10% of budget)
            - eta=0.5: Moderate (50% of budget) [default]
            - eta=1.0: Aggressive (full budget)
        l : int, optional
            Dependency lag parameter. Set l>0 if p-values have serial dependence.
            Default is 0 (assumes independence).
        """
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.delta: float = delta
        self.eta: float = eta
        self.l: int = l

        validity.check_decay_factor(delta)
        if not 0 < eta <= 1:
            raise ValueError(f"eta must be in (0, 1], got {eta}")
        if isinstance(l, bool) or not isinstance(l, Integral) or l < 0:
            raise ValueError(f"l must be a non-negative integer, got {l}")

        self.seq: DefaultLordGammaSequence = DefaultLordGammaSequence(c=0.07720838)

        self.rejection_times: list[int] = []  # all rejection times
        # Rejections before this position have decayed to a weight of exactly
        # zero, so they can no longer change a test level.
        self._first_active: int = 0
        # Gamma by time since a rejection. Only active rejections are looked up,
        # which bounds it by the time a weight takes to reach zero.
        self._gamma_cache: dict[int, float] = {}

    def _snapshot_state(self) -> dict[str, Any]:
        state = super()._snapshot_state()
        del state["_gamma_cache"]  # derived, and rebuilt on demand
        return state

    @classmethod
    def _restore_snapshot_state(cls, state: dict[str, Any]) -> dict[str, Any]:
        state["_gamma_cache"] = {}
        return state

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        index = self.num_hypotheses + 1

        # Base component with smoothing and minimum threshold
        gamma_t = self.seq.calc_gamma(index)
        alpha_t = self.alpha0 * self.eta * max(gamma_t, 1 - self.delta)

        # Add decayed contributions from past rejections, oldest first
        cache = self._gamma_cache
        for position in range(self._first_active, len(self.rejection_times)):
            time_diff = index - self.rejection_times[position] - self.l
            if time_diff <= 0:
                break  # later rejections are more recent still

            decay_weight = self.delta**time_diff
            if decay_weight == 0.0:
                self._first_active = position + 1
                continue

            gamma_val = cache.get(time_diff)
            if gamma_val is None:
                gamma_val = cache[time_diff] = self.seq.calc_gamma(time_diff)
            alpha_t += self.alpha0 * decay_weight * gamma_val

        self._set_test_level(alpha_t)
        self._advance_hypotheses()
        is_rejected = p_val <= alpha_t

        if is_rejected:
            self.rejection_times.append(index)

        return is_rejected
