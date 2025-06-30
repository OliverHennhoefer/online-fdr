from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLordGammaSequence


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

    def __init__(
        self,
        alpha: float,
        delta: float = 0.99,
        eta: float = 0.5,
        l: int = 0
    ):
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

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.rejection_times: list[int] = []  # all rejection times
        self._gamma_cache: dict[int, float] = {}  # Cache for efficiency

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1

        # Base component with smoothing and minimum threshold
        if self.num_test not in self._gamma_cache:
            self._gamma_cache[self.num_test] = self.seq.calc_gamma(self.num_test)
        
        gamma_t = self._gamma_cache[self.num_test]
        self.alpha = (
            self.alpha0
            * self.eta
            * max(gamma_t, 1 - self.delta)
        )
        
        # Add decayed contributions from past rejections
        for reject_idx in self.rejection_times:
            time_diff = self.num_test - reject_idx - self.l
            if time_diff > 0:
                # Cache gamma values for efficiency
                if time_diff not in self._gamma_cache:
                    self._gamma_cache[time_diff] = self.seq.calc_gamma(time_diff)
                
                decay_weight = self.delta ** time_diff
                gamma_val = self._gamma_cache[time_diff]
                self.alpha += self.alpha0 * decay_weight * gamma_val

        is_rejected = p_val <= self.alpha
        
        if is_rejected:
            self.rejection_times.append(self.num_test)
        
        return is_rejected
