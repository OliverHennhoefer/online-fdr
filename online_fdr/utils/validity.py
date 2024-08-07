def check_p_val(p_val: float) -> None:
    """Raise a ValueError for invalid p-values."""
    if not 0 <= p_val <= 1:
        raise ValueError(
            """
            Given p-value must be between [0,1].
            """
        )


def check_alpha(p_val: float) -> None:
    """Raise a ValueError for invalid significance levels."""
    if not 0 < p_val < 1:
        raise ValueError(
            """
            Given alpha value must be between (0,1).
            """
        )


def check_initial_wealth(initial_wealth: float, alpha: float) -> None:
    """Raise a warning for unusual initial wealth values."""
    if not 0 < initial_wealth < alpha:
        raise ValueError(
            """
            The initial wealth should be between (0, alpha).
            """
        )


def check_wealth(wealth: float) -> None:
    """Raise a ValueError when alpha wealth is depleted."""
    if wealth <= 0:
        raise ValueError(
            """
            Alpha wealth depleted. Test execution stopped.
            """
        )
