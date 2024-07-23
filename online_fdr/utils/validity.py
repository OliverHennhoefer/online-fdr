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


def check_initial_wealth(initial_wealth: float) -> None:
    if not 0 < initial_wealth < 1:
        raise ValueError(
            """
            Defined initial wealth value must be between (0,1).
            """
        )
    if not 0.05 <= initial_wealth <= 0.1:
        warnings.warn(
            """
            By convention, initial wealth is usually either 0.05 or 0.1.
            """
        )
