def check_p_val(p_val: float) -> None:
    """Validate that a p-value is in the valid range [0, 1].

    Args:
        p_val: The p-value to validate.

    Raises:
        ValueError: If p_val is not in [0, 1].

    Examples:
        >>> check_p_val(0.05)  # Valid - no exception
        >>> check_p_val(1.5)   # Raises ValueError
        Traceback (most recent call last):
        ValueError: Given p-value must be between [0,1].
    """
    if not 0 <= p_val <= 1:
        raise ValueError(
            """
            Given p-value must be between [0,1].
            """
        )


def check_alpha(p_val: float) -> None:
    """Validate that an alpha value is in the valid range (0, 1).

    Args:
        p_val: The alpha/significance level to validate.

    Raises:
        ValueError: If p_val is not in (0, 1).

    Examples:
        >>> check_alpha(0.05)  # Valid - no exception
        >>> check_alpha(0.0)   # Raises ValueError (not > 0)
        >>> check_alpha(1.0)   # Raises ValueError (not < 1)
    """
    if not 0 < p_val < 1:
        raise ValueError(
            """
            Given alpha value must be between (0,1).
            """
        )


def check_initial_wealth(initial_wealth: float, alpha: float) -> None:
    """Validate that initial wealth is properly bounded relative to alpha.

    In alpha-wealth procedures (LORD, SAFFRON, etc.), the initial wealth
    must be positive but less than the target FDR level to ensure proper
    wealth dynamics and FDR control.

    Args:
        initial_wealth: The initial alpha wealth.
        alpha: The target FDR level.

    Raises:
        ValueError: If initial_wealth is not in (0, alpha).

    Examples:
        >>> check_initial_wealth(0.025, 0.05)  # Valid - no exception
        >>> check_initial_wealth(0.1, 0.05)    # Raises ValueError (> alpha)
        >>> check_initial_wealth(0.0, 0.05)    # Raises ValueError (not > 0)
    """
    if not 0 < initial_wealth < alpha:
        raise ValueError(
            """
            The initial wealth should be between (0, alpha).
            """
        )


def check_candidate_threshold(lambda_: float) -> None:
    """Validate that a candidate threshold λ is in the valid range (0, 1).

    The candidate threshold λ is used in SAFFRON and ADDIS algorithms to
    determine which p-values are considered "candidates" for rejection.
    It must be strictly between 0 and 1.

    Args:
        lambda_: The candidate threshold to validate.

    Raises:
        ValueError: If lambda_ is not in (0, 1).

    Examples:
        >>> check_candidate_threshold(0.5)  # Valid - no exception
        >>> check_candidate_threshold(0.0)  # Raises ValueError
        >>> check_candidate_threshold(1.0)  # Raises ValueError
    """
    if not 0 < lambda_ < 1:
        raise ValueError(
            """
            The candidate threshold (lambda) should be between (0, 1).
            """
        )


def check_wealth(wealth: float) -> None:
    """Validate that alpha wealth is positive (not depleted).

    In alpha-wealth procedures, when wealth reaches zero or below,
    no more tests can be performed while maintaining FDR control.
    This function checks for wealth depletion.

    Args:
        wealth: Current alpha wealth level.

    Raises:
        ValueError: If wealth <= 0.

    Examples:
        >>> check_wealth(0.01)  # Valid - no exception
        >>> check_wealth(0.0)   # Raises ValueError (wealth depleted)
        >>> check_wealth(-0.1)  # Raises ValueError (negative wealth)
    """
    if wealth <= 0:
        raise ValueError(
            """
            Alpha wealth depleted. Test execution stopped.
            """
        )


def check_decay_factor(decay_factor: float) -> None:
    """Validate that a decay factor is in the valid range (0, 1).

    Decay factors are used in various algorithms to control the rate
    at which parameters decrease over time. They must be strictly
    between 0 and 1 for proper convergence behavior.

    Args:
        decay_factor: The decay factor to validate.

    Raises:
        ValueError: If decay_factor is not in (0, 1).

    Examples:
        >>> check_decay_factor(0.9)   # Valid - no exception
        >>> check_decay_factor(0.0)   # Raises ValueError (not > 0)
        >>> check_decay_factor(1.0)   # Raises ValueError (not < 1)
        >>> check_decay_factor(1.5)   # Raises ValueError (not < 1)
    """
    if not 0 < decay_factor < 1:
        raise ValueError(
            """
            Decay factor must be between (0,1).
            """
        )
