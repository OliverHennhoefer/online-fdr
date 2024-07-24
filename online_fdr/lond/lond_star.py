import math

from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class LONDstar(AbstractOnlineTest):
    """Implements '(Significance) Levels-based On Number of Discoveries'."""

    def __init__(self, alpha: float, epsilon: float = 0.01):
        super().__init__(alpha)
        self.epsilon = epsilon
        self.beta: float = 0.0  # Sum of beta(i)
        self.C: float | None = None  # Normalizing constant

        self.threshold: float | None = None  # Significance threshold
        self.threshold_sum: int = 0

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        beta = self._compute_beta()
        self.threshold = self.alpha * beta / (1 + self.threshold_sum)
        if p_val <= self.threshold:
            self.threshold_sum += self.threshold
            return True
        return False

    def _compute_beta(self):
        self.i += 1
        if self.i == 1:
            if self.C is None:
                self.C = 1  # Initialize normalizing constant C
            beta = self.C
        else:
            beta = self.C / (self.i * (math.log(self.i)) ** (1 + self.epsilon))
        self.beta += beta
        self.C = 1 / self.beta  # Update C to ensure convergence of beta to 1
        return beta
