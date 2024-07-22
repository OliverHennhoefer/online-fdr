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
