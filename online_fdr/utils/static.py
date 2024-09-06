def bh(p_vals: [float], alpha: float) -> (int, float):
    """(Static) Benjamini-Hochberg Procedure."""
    n = len(p_vals)
    sorted_p_vals = sorted(p_vals)

    def condition(i):
        return sorted_p_vals[i] <= alpha * (i + 1) / n

    left, right = 0, n
    while left < right:
        mid = (left + right) // 2
        if condition(mid):
            left = mid + 1
        else:
            right = mid

    return left, alpha * left / n if left else 0


def storey_bh(p_vals: [float], alpha: float, lambda_: float) -> (int, float):
    """(Static) Storey Benjamini-Hochberg Procedure"""
    n = len(p_vals)
    pi0 = (1 + sum(p > lambda_ for p in p_vals)) / (n * (1 - lambda_))
    sorted_p_vals = sorted(p_vals)

    i = 0
    for i, p in enumerate(sorted_p_vals, 1):
        if n * pi0 * p / i > alpha:
            break
        else:
            i += 1

    return i - 1, sorted_p_vals[i - 2] if i > 1 else 0
