from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.abstract.abstract_spend_func import AbstractSpendFunc
from online_fdr.utils import validity


class AlphaSpending(AbstractSequentialTest):
    """Alpha Spending Function for sequential hypothesis testing with flexible interim analyses.

    The alpha spending function approach, developed by Lan and DeMets (1983), provides
    flexible group sequential boundaries that control Type I error rate while allowing
    the number and timing of interim analyses to be determined adaptively during the trial.

    This method overcomes key limitations of traditional group sequential methods by not
    requiring the total number of analyses or their exact timing to be specified in advance.
    It's particularly valuable in clinical trials where interim analyses may be needed
    at unplanned times for ethical or scientific reasons.

    The approach works by "spending" portions of the overall alpha budget at each interim
    analysis according to a pre-specified spending function, ensuring that the cumulative
    Type I error rate never exceeds the target level.

    Args:
        alpha: Target Type I error rate (e.g., 0.05 for 5% error rate). Must be in (0, 1).
        spend_func: Alpha spending function that determines how to allocate alpha
                   across interim analyses. Must inherit from AbstractSpendFunc.

    Attributes:
        alpha0: Original target Type I error rate.
        rule: The spending function used to determine alpha allocation.
        num_test: Number of tests/analyses conducted so far.
        alpha: Current alpha level for the next test.

    Examples:
        >>> from online_fdr.spending.functions.bonferroni import BonferroniSpendFunc
        >>> # Create Bonferroni spending function for 5 planned analyses
        >>> spend_func = BonferroniSpendFunc(max_analyses=5)
        >>> alpha_spending = AlphaSpending(alpha=0.05, spend_func=spend_func)
        >>> # Test p-values sequentially
        >>> decision1 = alpha_spending.test_one(0.01)  # First interim analysis
        >>> decision2 = alpha_spending.test_one(0.03)  # Second interim analysis

    References:
        Lan, K. K. Gordon, and D. L. DeMets (1983). "Discrete Sequential Boundaries
        for Clinical Trials." Biometrika, 70(3):659-663.

        DeMets, D. L., and K. K. Gordon Lan (1994). "Interim Analysis: The Alpha
        Spending Function Approach." Statistics in Medicine, 13(13-14):1341-1352.

        Jennison, C., and B. W. Turnbull (1999). "Group Sequential Methods with
        Applications to Clinical Trials." Chapman and Hall/CRC.
    """

    def __init__(
        self,
        alpha: float,
        spend_func: AbstractSpendFunc,
    ):
        super().__init__(alpha)
        self.alpha0: float = alpha
        self.rule: AbstractSpendFunc = spend_func

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the alpha spending approach.

        Determines the alpha level for the current analysis based on the spending function
        and the analysis number, then tests whether the p-value meets the significance
        threshold.

        Args:
            p_val: P-value to test. Must be in [0, 1].

        Returns:
            True if the null hypothesis is rejected (p_val < alpha), False otherwise.

        Raises:
            ValueError: If p_val is not in [0, 1].

        Examples:
            >>> alpha_spending = AlphaSpending(alpha=0.05, spend_func=my_spend_func)
            >>> alpha_spending.test_one(0.01)  # First analysis
            True
            >>> alpha_spending.test_one(0.04)  # Second analysis, stricter threshold
            False
        """
        validity.check_p_val(p_val)

        self.alpha = self.rule.spend(index=self.num_test, alpha=self.alpha0)
        self.num_test += 1
        return p_val < self.alpha
