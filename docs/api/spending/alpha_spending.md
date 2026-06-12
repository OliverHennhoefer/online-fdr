# Alpha Spending Function

::: online_fdr.p_values.AlphaSpending

## Overview

The Alpha Spending Function approach provides a flexible framework for sequential hypothesis testing that allows the number and timing of interim analyses to be determined adaptively during the trial. Unlike traditional group sequential methods, it does not require advance specification of when analyses will be conducted.

## Key Features

- **Adaptive timing**: Interim analyses can be conducted at any time
- **Flexible boundaries**: Spending function determines significance boundaries
- **Type I error control**: Maintains strict control regardless of analysis timing
- **Clinical applicability**: Designed for real-world trial scenarios

## Mathematical Framework

The alpha spending function $\alpha(t)$ satisfies:

1. $\alpha(0) = 0$ (no spending at the start)
2. $\alpha(1) = \alpha$ (complete budget spent at the end)  
3. $\alpha(t)$ is non-decreasing in $t$

At analysis $k$, the incremental alpha spent is:
$$\Delta_k = \alpha(t_k) - \alpha(t_{k-1})$$

## Implementation Details

The `AlphaSpending` class requires:
- Target Type I error rate ($\alpha$)
- A spending function implementing `AbstractSpendFunc`

Common spending functions include:
- O'Brien-Fleming boundaries
- Pocock boundaries  
- Linear spending
- Custom user-defined functions

## Examples

### Basic Usage

```python
from online_fdr.p_values import AlphaSpending
from online_fdr.p_values import Bonferroni

# Create Bonferroni spending function
spend_func = Bonferroni(k=5)

# Initialize alpha spending procedure
alpha_spending = AlphaSpending(alpha=0.05, spend_func=spend_func)

# Test p-values sequentially
p_values = [0.02, 0.15, 0.01, 0.8, 0.003]
decisions = []

for p_val in p_values:
    decision = alpha_spending.test_one(p_val)
    decisions.append(decision)
    print(f"P-value: {p_val}, Decision: {decision}")
```

### Unplanned Interim Analysis

```python
# Alpha spending allows unplanned analyses
# No need to pre-specify analysis times

analysis_times = [0.2, 0.35, 0.6, 0.9, 1.0]  # Can be determined adaptively
p_values = [0.03, 0.12, 0.008, 0.45, 0.002]

# Reinitialize for a new scenario when using finite-horizon spend functions.
alpha_spending = AlphaSpending(alpha=0.05, spend_func=Bonferroni(k=5))

for time, p_val in zip(analysis_times, p_values):
    decision = alpha_spending.test_one(p_val)
    print(f"Analysis at t={time}: p={p_val}, reject={decision}")
```

## Clinical Trial Application

Alpha spending is particularly useful in:

- **Adaptive trials**: Where analysis timing depends on enrollment or events
- **Safety monitoring**: Unscheduled safety analyses may be required
- **Futility assessment**: Early stopping for lack of efficacy
- **Regulatory compliance**: FDA guidance supports alpha spending approaches

## Comparison with Group Sequential Methods

| Aspect | Alpha Spending | Group Sequential |
|--------|----------------|------------------|
| Analysis timing | Flexible | Fixed |
| Number of analyses | Adaptive | Pre-specified |
| Boundary calculation | Via spending function | Via recursive formula |
| Implementation | More complex | Simpler |
| Regulatory acceptance | High | High |

## Best Practices

1. **Choose spending function carefully** based on trial objectives
2. **Monitor cumulative spending** to avoid early exhaustion
3. **Document analysis timing** for regulatory submissions
4. **Consider practical constraints** in spending function selection
5. **Plan for emergency analyses** that may be required

## References

Lan, K. K. Gordon, and D. L. DeMets (1983). "Discrete Sequential Boundaries for Clinical Trials." *Biometrika*, 70(3):659-663.

DeMets, D. L., and K. K. Gordon Lan (1994). "Interim Analysis: The Alpha Spending Function Approach." *Statistics in Medicine*, 13(13-14):1341-1352.

Wassmer, G., and W. Brannath (2016). *Group Sequential and Confirmatory Adaptive Designs in Clinical Trials*. Springer.
