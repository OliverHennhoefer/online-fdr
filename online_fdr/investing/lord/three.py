from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLordGammaSequence


class LordThree(AbstractSequentialTest):
    """LORD 3: Online FDR control based on recent discovery with wealth dynamics.

    LORD 3 is a variant of the LORD (significance Levels based On Recent Discovery)
    procedure for online FDR control. The test levels depend on the past only through
    the time of the last discovery and the wealth accumulated at that time.

    LORD procedures have an intuitive interpretation: they start with an error budget
    (alpha-wealth), pay a price each time a hypothesis is tested, and earn back wealth
    when discoveries are made. LORD 3 sets thresholds based on the time since the last
    discovery and the wealth at that time.

    Note:
        This method was superseded by LORD++ and is implemented for demonstrative
        purposes and comparison studies. For practical applications, consider using
        LORD++ or more recent methods like ADDIS or SAFFRON.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).
        wealth: Initial alpha-wealth for purchasing rejection thresholds.
                Must satisfy 0 ≤ wealth ≤ alpha.
        reward: Reward earned back for each discovery. Must be positive.
                Typical choice is reward = alpha - wealth.

    Attributes:
        wealth: Current alpha-wealth available for testing.
        reward: Fixed reward earned per discovery.
        last_reject: Index of the most recent rejection (0 if none).
        wealth_reject: Alpha-wealth at the time of the last rejection.

    Examples:
        >>> # Basic usage with recommended parameters
        >>> lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)
        >>> decision = lord3.test_one(0.01)  # Test a small p-value
        >>> print(f"Rejected: {decision}")

        >>> # Sequential testing
        >>> p_values = [0.001, 0.3, 0.02, 0.8, 0.005]
        >>> decisions = [lord3.test_one(p) for p in p_values]
        >>> discoveries = sum(decisions)

    References:
        Javanmard, A., and A. Montanari (2018). "Online rules for control of false
        discovery rate and false discovery exceedance." Annals of Statistics,
        46(2):526-554.

        Project Euclid: https://projecteuclid.org/journals/annals-of-statistics/volume-46/issue-2/Online-rules-for-control-of-false-discovery-rate-and-false/10.1214/17-AOS1559.full
    """

    def __init__(
        self,
        alpha: float,
        wealth: float,
        reward: float,
    ):  # fmt: skip
        super().__init__(alpha)
        self.wealth: float = wealth
        self.reward: float = reward
        validity.check_initial_wealth(wealth, alpha)
        validity.check_reward_budget(wealth=wealth, reward=reward, alpha=alpha)

        self.seq = DefaultLordGammaSequence(c=0.07720838)

        self.last_reject: int = 0  # reject index
        self.wealth_reject: float = wealth  # reject wealth
        # Matches onlineFDR's LORD(version = "3") state recursion sentinel.
        self._decision_history: list[bool] = [True]

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the LORD 3 procedure.

        The LORD 3 algorithm processes p-values sequentially:
        1. Calculate threshold based on time since last discovery and wealth at that time
        2. Spend alpha-wealth equal to the threshold
        3. Earn back reward if discovery is made
        4. Update last rejection time and wealth if discovery is made

        Args:
            p_val: P-value to test. Must be in [0, 1].

        Returns:
            True if the null hypothesis is rejected (discovery), False otherwise.

        Raises:
            ValueError: If p_val is not in [0, 1].

        Examples:
            >>> lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)
            >>> lord3.test_one(0.01)  # Small p-value, likely rejected
            True
            >>> lord3.test_one(0.8)   # Large p-value, not rejected
            False
        """
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = (
            self.seq.calc_gamma(self.num_test - self.last_reject)  # fmt: skip
            * self.wealth_reject
        )

        is_rejected = p_val <= self.alpha

        # onlineFDR applies the spend as min(alpha_t, W_{t-1}).
        spend = min(self.alpha, self.wealth)

        # onlineFDR LORD-3 recursion credits reward with one-step lag and
        # sentinel R_0 = TRUE on t=2.
        reward_credited = (
            is_rejected
            if self.num_test == 1
            else self._decision_history[self.num_test - 2]
        )

        self.wealth -= spend
        self.wealth += self.reward if reward_credited else 0.0
        self._decision_history.append(is_rejected)

        self.last_reject = self.num_test if is_rejected else self.last_reject
        self.wealth_reject = self.wealth if is_rejected else self.wealth_reject

        return is_rejected
