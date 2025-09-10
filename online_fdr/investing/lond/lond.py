from online_fdr.abstract.abstract_sequential_test import AbstractSequentialTest
from online_fdr.utils import validity
from online_fdr.utils.sequence import DefaultLondGammaSequence


class Lond(AbstractSequentialTest):
    """LOND: Levels based On Number of Discoveries for online FDR control.
    
    LOND is one of the first procedures for online false discovery rate (FDR) control,
    where significance levels are adjusted based on the number of discoveries made so far.
    It is a relatively simple algorithm where test levels are multiplied by the number 
    of rejections up to the current time.
    
    While LOND provably controls the FDR, it has a significant limitation: unless many 
    discoveries are made early, the adjusted significance levels quickly approach zero,
    leading to very low power. This motivated the development of LORD procedures that 
    use "alpha investing" to maintain better power over time.

    Args:
        alpha: Target FDR level (e.g., 0.05 for 5% FDR). Must be in (0, 1).
        original: If True, use original LOND formulation (num_reject + 1).
                 If False, use modified version max(num_reject, 1). Default is True.
        dependent: If True, apply correction for arbitrary dependence using harmonic
                  series. If False, assume independence/positive dependence. Default is False.

    Attributes:
        alpha0: Original target FDR level.
        num_test: Number of hypotheses tested so far.
        num_reject: Number of hypotheses rejected so far.
        original: Whether to use original LOND formulation.
        dependent: Whether to apply dependence correction.

    Examples:
        >>> # Basic usage
        >>> lond = Lond(alpha=0.05)
        >>> decision = lond.test_one(0.01)  # Test a small p-value
        >>> print(f"Rejected: {decision}")
        
        >>> # For dependent p-values
        >>> lond_dep = Lond(alpha=0.05, dependent=True)
        >>> decisions = [lond_dep.test_one(p) for p in [0.001, 0.3, 0.02]]

    Note:
        LOND is primarily of historical importance as one of the first online FDR 
        methods. For practical applications, consider using LORD, SAFFRON, or ADDIS 
        which typically achieve higher power.

    References:
        Javanmard, A., and Montanari, A. (2015). "On online control of false discovery 
        rate." arXiv preprint arXiv:1502.06197.
        
        Javanmard, A., and A. Montanari (2018). "Online rules for control of false 
        discovery rate and false discovery exceedance." Annals of Statistics, 
        46(2):526-554.
    """

    def __init__(
        self,
            alpha: float,
            original: bool = True,
            dependent: bool = False
    ):  # fmt: skip
        super().__init__(alpha)
        self.alpha0: float = alpha

        self.num_test: int = 0
        self.num_reject: int = 0

        self.seq = DefaultLondGammaSequence(c=0.07720838)

        self.original: bool = original
        self.dependent: bool = dependent

    def test_one(self, p_val: float) -> bool:
        """Test a single p-value using the LOND procedure.
        
        The LOND algorithm processes p-values sequentially:
        1. Calculate base significance level using gamma sequence
        2. Apply dependence correction if enabled (harmonic series)
        3. Multiply by number of discoveries (+ 1 for original version)
        4. Reject if p-value ≤ threshold and update discovery count
        
        Args:
            p_val: P-value to test. Must be in [0, 1].
            
        Returns:
            True if the null hypothesis is rejected (discovery), False otherwise.
            
        Raises:
            ValueError: If p_val is not in [0, 1].
            
        Examples:
            >>> lond = Lond(alpha=0.05)
            >>> lond.test_one(0.001)  # First test, small p-value
            True
            >>> lond.test_one(0.04)   # Second test, higher threshold after discovery
            True
            >>> lond.test_one(0.04)   # Third test, threshold increased again
            False
            
        Note:
            The threshold increases with each discovery, but decreases rapidly
            if no discoveries are made early on, leading to low power.
        """
        validity.check_p_val(p_val)
        self.num_test += 1

        self.alpha = self.seq.calc_gamma(self.num_test, alpha=self.alpha0)
        self.alpha /= (
            sum(1 / i for i in range(1, self.num_test + 1))
            if self.dependent
            else 1  # fmt: split
        )
        self.alpha *= (
            self.num_reject + 1 if self.original else max(self.num_reject, 1)
        )  # fmt: split

        is_rejected = p_val <= self.alpha
        self.num_reject += 1 if is_rejected else 0

        return is_rejected
