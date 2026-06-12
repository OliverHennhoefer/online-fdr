# Alpha Spending Methods

Alpha spending functions provide flexible control of Type I error rate in sequential hypothesis testing, allowing the number and timing of interim analyses to be determined adaptively during the trial.

## Overview

The alpha spending approach, developed by Lan and DeMets (1983), overcomes key limitations of traditional group sequential methods by not requiring the total number of analyses or their exact timing to be specified in advance. This flexibility is particularly valuable in clinical trials where interim analyses may be needed at unplanned times.

## Available Methods

### Alpha Spending Function
::: online_fdr.p_values.AlphaSpending

### Online Fallback Procedure  
::: online_fdr.p_values.OnlineFallback

## Spending Function Types

The alpha spending framework supports various spending functions that determine how to allocate the alpha budget across interim analyses:

- **O'Brien-Fleming type**: Conservative early spending, allowing larger effects to be detected later
- **Pocock type**: Equal spending at each analysis
- **Linear spending**: Proportional to analysis timing
- **Custom functions**: User-defined spending patterns

## Key Concepts

### Alpha Budget Allocation

The fundamental principle is to "spend" portions of the overall alpha budget at each interim analysis according to a pre-specified spending function, ensuring cumulative Type I error never exceeds the target level.

### Flexibility vs. Control

Alpha spending provides:
- **Flexibility**: Adapt timing and number of analyses during the trial
- **Control**: Maintain strict Type I error rate control
- **Efficiency**: Stop early for efficacy or futility

### Comparison with Other Methods

| Method | Flexibility | Power | Complexity |
|--------|-------------|-------|------------|
| Alpha Spending | High | Good | Medium |
| Group Sequential | Low | High | Low |
| Online FDR | High | Variable | High |

## Usage Guidelines

1. **Choose appropriate spending function** based on trial characteristics
2. **Monitor spending carefully** to avoid early alpha exhaustion  
3. **Plan for unscheduled analyses** that may be required
4. **Consider futility bounds** in addition to efficacy boundaries

## References

Lan, K. K. Gordon, and D. L. DeMets (1983). "Discrete Sequential Boundaries for Clinical Trials." *Biometrika*, 70(3):659-663.

DeMets, D. L., and K. K. Gordon Lan (1994). "Interim Analysis: The Alpha Spending Function Approach." *Statistics in Medicine*, 13(13-14):1341-1352.

Jennison, C., and B. W. Turnbull (1999). *Group Sequential Methods with Applications to Clinical Trials*. Chapman and Hall/CRC.