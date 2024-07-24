import warnings


def check_p_val(p_val: float) -> None:
    if not 0 <= p_val <= 1:
        raise ValueError(
            """
            Given p-value must be between [0,1].
            """
        )


def check_alpha(p_val: float) -> None:
    if not 0 < p_val < 1:
        raise ValueError(
            """
            Given alpha value must be between (0,1).
            """
        )


def check_initial_wealth(initial_wealth: float, alpha: float) -> None:
    if not 0 < initial_wealth < alpha:
        warnings.warn(
            """
            By convention, initial wealth should be between (0, alpha].
            """
        )
