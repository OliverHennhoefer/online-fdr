# Online Fallback Procedure

::: online_fdr.p_values.OnlineFallback

## Overview

The Online Fallback procedure provides strong familywise error rate (FWER) control for testing an a priori unbounded sequence of hypotheses one by one over time. Unlike FDR procedures, it ensures that with high probability there are no false discoveries in the entire sequence.

## Key Features

- **FWER control**: Strong control under arbitrary dependence
- **Fallback mechanism**: Increased power after making discoveries  
- **Unbounded sequences**: No need to specify total number of tests
- **Adaptive power**: Testing power increases with discoveries
- **General dependence**: Valid under arbitrary p-value dependence

## Mathematical Framework

The online fallback procedure maintains an alpha wealth process $\{W_t\}$ where:

1. **Initial wealth**: $W_0 = \alpha$
2. **Alpha allocation**: $\alpha_t = \gamma_t \cdot W_{t-1}$ (if no recent discovery)
3. **Fallback mechanism**: $\alpha_t = W_{t-1}$ (if previous test was rejected)
4. **Wealth update**: $W_t = W_{t-1} - \alpha_t$ (spend alpha)
5. **Discovery reward**: $W_t = W_t + \alpha_t$ (earn back on rejection)

## Algorithm Details

For test $t = 1, 2, \ldots$:

1. **Calculate alpha level**:
   - If previous test rejected: $\alpha_t = W_{t-1}$ (full wealth)
   - Otherwise: $\alpha_t = \gamma_t \cdot \alpha_0$ (gamma sequence)

2. **Make decision**: Reject $H_t$ if $P_t \leq \alpha_t$

3. **Update wealth**:
   - Spend: $W_t = W_{t-1} - \alpha_t$
   - If rejected: $W_t = W_t + \alpha_t$ (earn back)

## Fallback Mechanism

The key innovation is the "fallback" property:
- **After discovery**: Next test uses all remaining wealth
- **High power**: Discoveries enable aggressive follow-up testing  
- **FWER preservation**: Wealth accounting ensures error control
- **Momentum**: Recent discoveries create testing momentum

## Implementation

The `OnlineFallback` class uses:
- LORD gamma sequence for baseline alpha allocation
- Boolean flag to track recent discoveries
- Wealth-based alpha calculation with fallback

## Examples

### Basic FWER Control

```python
from online_fdr.p_values import OnlineFallback

# Initialize online fallback procedure
fallback = OnlineFallback(alpha=0.05)

# Test p-values sequentially
p_values = [0.3, 0.01, 0.02, 0.4, 0.003]
decisions = []

for i, p_val in enumerate(p_values, 1):
    decision = fallback.test_one(p_val)
    decisions.append(decision)
    print(f"Test {i}: p={p_val:.3f}, alpha={fallback.last_rejection_threshold:.4f}, reject={decision}")

print(f"Total discoveries: {sum(decisions)}")
print(f"FWER controlled at level {fallback.target_level}")
```

### Demonstrating Fallback Effect

```python
# Show how alpha increases after discovery
fallback = OnlineFallback(alpha=0.05)

print("Without discovery:")
fallback.test_one(0.8)  # No rejection
print(f"Next alpha: {fallback.last_rejection_threshold:.4f}")

print("\\nWith discovery:")
fallback_2 = OnlineFallback(alpha=0.05)
fallback_2.test_one(0.01)  # Rejection
print(f"Next alpha after discovery: {fallback_2.last_rejection_threshold:.4f}")
```

### Sequential Testing Scenario

```python
# Simulate drug development pipeline
fallback = OnlineFallback(alpha=0.05)

# Stage 1: Screening compounds
screening_p = [0.6, 0.4, 0.02, 0.7, 0.1]  # One promising compound
decisions = [fallback.test_one(p) for p in screening_p]
print(f"Screening phase: {sum(decisions)} compounds selected")

# Stage 2: Detailed testing (higher power due to fallback)
detailed_p = [0.03, 0.008, 0.15]  # Follow-up on promising leads
for p in detailed_p:
    decision = fallback.test_one(p)
    print(f"Detailed test: p={p}, alpha={fallback.last_rejection_threshold:.4f}, reject={decision}")
```

## Comparison with Other Methods

| Method | Error Type | Power After Discovery | Dependence Handling |
|--------|------------|----------------------|-------------------|
| Online Fallback | FWER | High (fallback) | Arbitrary |
| Alpha Spending | FWER | Fixed | Limited |  
| Bonferroni | FWER | Low | Arbitrary |
| Online FDR | FDR | Variable | Algorithm-specific |

## Applications

The online fallback procedure is particularly suitable for:

- **Drug discovery**: Sequential compound testing
- **Clinical monitoring**: Safety signal detection
- **Quality control**: Manufacturing process monitoring  
- **A/B testing**: Sequential feature testing with strict error control
- **Genomic screening**: Gene discovery with strong error control

## Theoretical Properties

**Theorem (FWER Control)**: Under arbitrary dependence among p-values, the online fallback procedure controls FWER at level $\alpha$.

**Key insight**: The wealth process $\{W_t\}$ forms a supermartingale under the global null hypothesis, ensuring $\mathbb{E}[V_\infty] \leq \alpha$ where $V_\infty$ is the total number of false discoveries.

## Advantages and Limitations

### Advantages
- Strong FWER control under arbitrary dependence
- Increased power after discoveries (fallback mechanism)
- No need to pre-specify number of tests
- Intuitive wealth-based interpretation

### Limitations
- More conservative than FDR methods when many discoveries expected
- Requires careful wealth management
- May exhaust alpha budget quickly without discoveries
- Less suitable when false discoveries are acceptable

## Best Practices

1. **Use when strict error control is required** (no false discoveries acceptable)
2. **Monitor wealth levels** to avoid early exhaustion
3. **Consider prior information** about expected discovery rates
4. **Plan sequential testing strategy** to maximize fallback benefits
5. **Document decision process** for regulatory compliance

## References

Tian, J., and A. Ramdas (2021). "Online control of the familywise error rate." *Statistical Methods in Medical Research*, 30(4):976-993.

Ramdas, A., T. Zrnic, M. Wainwright, and M. Jordan (2018). "SAFFRON: an adaptive algorithm for online control of the false discovery rate." *Proceedings of the 35th International Conference on Machine Learning*, 80:4286-4294.

Foster, D. P., and R. A. Stine (2008). "-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society: Series B*, 70(2):429-444.
