def calculate_sfdr(tp: int, fp: int, eta: float = 0.0001) -> float:
    """Calculates the smoothed FDR (sFDR)."""
    return fp / (fp + tp + eta)
