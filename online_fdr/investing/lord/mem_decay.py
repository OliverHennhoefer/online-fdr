from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLordGammaSequence


class LORDMemoryDecay(AbstractSequentialTest):
    """Implements the LORD variant with memory decay for time series applications.
    
    This variant introduces a decay factor δ that down-weights the contribution
    of older rejections, making it suitable for non-stationary time series where
    recent discoveries are more relevant than older ones.
    
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
        wealth: float,
        delta: float = 0.99,
        eta: float = 0.0001,
        l: float = 0,
        reward: float = None
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.wealth0: float = wealth
        self.wealth: float = wealth
        self.delta: float = delta  # decay factor
        self.eta: float = eta  # smoothing factor
        self.l: float = l  # dependency window
        self.reward: float = reward if reward is not None else alpha
        
        validity.check_initial_wealth(wealth, alpha)
        validity.check_decay_factor(delta)
        
        self.seq = DefaultLordGammaSequence(c=0.07720838)
        
        self.rejection_times: list[int] = []  # all rejection times

    def test_one(self, p_val: float) -> bool:
        validity.check_p_val(p_val)
        self.num_test += 1
        
        # Calculate alpha based on memory-decayed LORD formula
        # Base component with smoothing
        self.alpha = (
            self.wealth0
            * self.eta
            * max(self.seq.calc_gamma(self.num_test), 1 - self.delta)
        )
        
        # Add decayed contributions from past rejections
        for reject_idx in self.rejection_times:
            time_diff = self.num_test - reject_idx - self.l
            if time_diff > 0:
                decay_weight = self.delta ** time_diff
                gamma_val = self.seq.calc_gamma(time_diff)
                self.alpha += self.reward * decay_weight * gamma_val
        
        # Ensure we don't spend more than available wealth
        self.alpha = min(self.alpha, self.wealth)
        
        is_rejected = p_val <= self.alpha
        
        # Update wealth: spend alpha, gain reward if rejected
        self.wealth -= self.alpha
        if is_rejected:
            self.wealth += self.reward
            self.rejection_times.append(self.num_test)
        
        return is_rejected