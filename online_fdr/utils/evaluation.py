def calculate_sfdr(tp: int, fp: int, eta: float = 0.0001) -> float:
    """Calculates the smoothed FDR (sFDR)."""
    return fp / (fp + tp + eta)


def calculate_power(tp: int, fn: int) -> float:
    """Calculates the statistical power."""
    return 0 if tp + fn == 0 else tp / (tp + fn)
