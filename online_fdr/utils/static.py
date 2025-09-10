def bh(p_vals: [float], alpha: float) -> (int, float):
    """Static Benjamini-Hochberg (BH) procedure for FDR control.

    The Benjamini-Hochberg procedure is the fundamental method for controlling
    the False Discovery Rate in multiple testing. It provides FDR control at
    level α under independence of p-values or positive dependence (PRDS).

    The algorithm sorts p-values and finds the largest index i such that
    P(i) ≤ (i/n) × α, where P(i) is the i-th smallest p-value and n is the
    total number of tests.

    Args:
        p_vals: List of p-values to test. Should be in [0,1].
        alpha: Target FDR level. Must be in (0,1).

    Returns:
        Tuple of (number_of_rejections, rejection_threshold).
        - number_of_rejections: Number of hypotheses rejected
        - rejection_threshold: The p-value threshold used for rejection

    Examples:
        >>> # Basic usage
        >>> p_values = [0.01, 0.02, 0.5, 0.8]
        >>> num_rej, threshold = bh(p_values, alpha=0.05)
        >>> print(f"Rejected {num_rej} hypotheses at threshold {threshold:.4f}")

        >>> # Check which p-values are rejected
        >>> rejected = [p <= threshold for p in p_values]
        >>> print(f"Rejected p-values: {[p for p, r in zip(p_values, rejected) if r]}")

    References:
        Benjamini, Y., and Y. Hochberg (1995). "Controlling the False Discovery Rate:
        A Practical and Powerful Approach to Multiple Testing." Journal of the Royal
        Statistical Society: Series B, 57(1):289-300.
    """
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
    """Static Storey-Benjamini-Hochberg procedure with π₀ estimation.

    The Storey-BH procedure extends the classical Benjamini-Hochberg method by
    estimating π₀ (the proportion of true null hypotheses) and incorporating
    this estimate into the rejection threshold. This typically provides higher
    power when π₀ < 1, which is common in genomic and other high-dimensional
    applications.

    The algorithm estimates π₀ using Storey's method:
    π̂₀ = min(1, (1 + #{p > λ}) / (n × (1 - λ)))

    Then applies the BH procedure with adjusted significance level α/π̂₀.

    Args:
        p_vals: List of p-values to test. Should be in [0,1].
        alpha: Target FDR level. Must be in (0,1).
        lambda_: Threshold parameter for π₀ estimation. Must be in [0,1).
                Common choice: λ = 0.5. Higher values give more conservative
                π₀ estimates.

    Returns:
        Tuple of (number_of_rejections, rejection_threshold).
        - number_of_rejections: Number of hypotheses rejected
        - rejection_threshold: The p-value threshold used for rejection

    Raises:
        ValueError: If lambda_ >= 1.0.

    Examples:
        >>> # Standard usage with λ = 0.5
        >>> p_values = [0.001, 0.02, 0.5, 0.8, 0.9]
        >>> num_rej, threshold = storey_bh(p_values, alpha=0.05, lambda_=0.5)
        >>> print(f"Storey-BH rejected {num_rej} at threshold {threshold:.4f}")

        >>> # Compare with standard BH
        >>> num_rej_bh, threshold_bh = bh(p_values, alpha=0.05)
        >>> print(f"Standard BH rejected {num_rej_bh} at threshold {threshold_bh:.4f}")
        >>> # Storey-BH typically has higher power when π₀ < 1

    References:
        Storey, J. D. (2002). "A direct approach to false discovery rates."
        Journal of the Royal Statistical Society: Series B, 64(3):479-498.

        Storey, J. D. (2003). "The positive false discovery rate: a Bayesian
        interpretation and the q-value." Annals of Statistics, 31(6):2013-2035.
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
    """Static Benjamini-Yekutieli (BY) procedure for FDR control under dependence.

    The Benjamini-Yekutieli procedure extends the Benjamini-Hochberg method to
    provide FDR control even under arbitrary dependence among p-values. It uses
    harmonic weights to maintain FDR control at the cost of reduced power
    compared to the standard BH procedure.

    The algorithm finds the largest index i such that:
    P(i) ≤ (i/n) × α / H_n

    where H_n = Σ(1/j) for j=1 to n is the n-th harmonic number.

    Args:
        p_vals: List of p-values to test. Should be in [0,1].
        alpha: Target FDR level. Must be in (0,1).

    Returns:
        Tuple of (number_of_rejections, rejection_threshold).
        - number_of_rejections: Number of hypotheses rejected
        - rejection_threshold: The p-value threshold used for rejection

    Examples:
        >>> # Usage under arbitrary dependence
        >>> p_values = [0.01, 0.02, 0.5, 0.8]  # May be dependent
        >>> num_rej, threshold = by(p_values, alpha=0.05)
        >>> print(f"BY rejected {num_rej} at threshold {threshold:.4f}")

        >>> # Compare with BH (more conservative under dependence)
        >>> num_rej_bh, threshold_bh = bh(p_values, alpha=0.05)
        >>> print(f"BH rejected {num_rej_bh} (may not control FDR under dependence)")

    Notes:
        The BY procedure is recommended when:
        - P-values may be arbitrarily dependent
        - Conservative FDR control is required
        - The exact dependence structure is unknown

        It maintains valid FDR control under any dependence structure but
        typically has lower power than BH under independence.

    References:
        Benjamini, Y., and D. Yekutieli (2001). "The control of the false discovery
        rate in multiple testing under dependency." Annals of Statistics, 29(4):1165-1188.
    """
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
