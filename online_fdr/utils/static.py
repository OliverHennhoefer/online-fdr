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
    """(Static) Storey Benjamini-Hochberg Procedure
    
    Implements Storey's modification of the Benjamini-Hochberg procedure with π₀ estimation.
    Reference: Storey, J.D. (2002). "A direct approach to false discovery rates."
    Journal of the Royal Statistical Society: Series B, 64(3), 479-498.
    
    Args:
        p_vals: List of p-values
        alpha: Significance level
        lambda_: Tuning parameter for π₀ estimation (typically 0.5)
        
    Returns:
        Tuple of (number of rejections, rejection threshold)
    """
    if not p_vals:
        return 0, 0.0
    
    n = len(p_vals)
    
    # Estimate π₀ using Storey's method
    # π₀ = (1 + #{p_i > λ}) / (n(1-λ))
    if lambda_ >= 1.0:
        raise ValueError("lambda_ must be less than 1.0")
    
    num_above_lambda = sum(1 for p in p_vals if p > lambda_)
    pi0 = min(1.0, (1 + num_above_lambda) / (n * (1 - lambda_)))
    
    # Apply BH procedure with adjusted alpha
    sorted_p_vals = sorted(p_vals)
    
    # Find the largest i such that P(i) ≤ (i/n) * (alpha/π₀)
    num_reject = 0
    threshold = 0.0
    
    for i in range(n):
        if sorted_p_vals[i] <= (i + 1) * alpha / (n * pi0):
            num_reject = i + 1
            threshold = sorted_p_vals[i]
        else:
            break
    
    return num_reject, threshold


def by(p_vals: [float], alpha: float) -> (int, float):
    """(Static) Benjamini-Yekutieli Procedure."""
    n = len(p_vals)
    sorted_p_vals = sorted(p_vals)
    harmonic_sum = sum(1 / (i + 1) for i in range(n))

    def condition(i):
        return sorted_p_vals[i] <= alpha * (i + 1) / (n * harmonic_sum)

    left, right = 0, n
    while left < right:
        mid = (left + right) // 2
        if condition(mid):
            left = mid + 1
        else:
            right = mid

    return left, alpha * left / (n * harmonic_sum) if left else 0
