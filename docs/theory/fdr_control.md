# Mathematical Foundations of FDR Control

False Discovery Rate (FDR) control is the cornerstone of modern multiple testing correction. This page provides the mathematical foundations underlying both batch and online FDR control methods.

!!! quote "Foundational Work"
    **Benjamini, Y., and Y. Hochberg** (1995). "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." *Journal of the Royal Statistical Society: Series B*, 57(1):289-300.

## The Multiple Testing Problem

### Basic Setup

Consider testing $m$ null hypotheses $H_1, H_2, \ldots, H_m$ simultaneously. Each test produces a p-value $P_i$ and a decision:

$$D_i = \mathbf{1}_{P_i \leq \alpha_i}$$

where $\alpha_i$ is the significance threshold for test $i$.

### The Decision Matrix

The outcomes can be summarized in a $2 \times 2$ decision matrix:

|                    | $H_0$ True | $H_0$ False | Total |
|--------------------|------------|-------------|-------|
| **Reject $H_0$**   | $V$        | $S$         | $R$   |
| **Accept $H_0$**   | $U$        | $T$         | $m-R$ |
| **Total**          | $m_0$      | $m_1$       | $m$   |

Where:
- $V$ = False discoveries (Type I errors)
- $S$ = True discoveries (correct rejections)  
- $R = V + S$ = Total discoveries
- $m_0$ = Number of true nulls
- $m_1 = m - m_0$ = Number of false nulls (alternatives)

## False Discovery Rate Definition

### Standard FDR

The **False Discovery Rate** is defined as:

$$\text{FDR} = \mathbb{E}\left[\frac{V}{R \vee 1}\right]$$

where $R \vee 1 = \max(R, 1)$ avoids division by zero when no discoveries are made.

### Alternative Formulations

Several related error measures exist:

**Marginal FDR (mFDR)**:
$$\text{mFDR} = \frac{\mathbb{E}[V]}{\mathbb{E}[R \vee 1]}$$

**Positive FDR (pFDR)**:
$$\text{pFDR} = \mathbb{E}\left[\frac{V}{R} \bigg| R > 0\right]$$

**False Discovery Proportion (FDP)**:
$$\text{FDP} = \frac{V}{R \vee 1}$$

Note that $\text{FDR} = \mathbb{E}[\text{FDP}]$.

## Classical Batch FDR Control

### Benjamini-Hochberg Procedure

The **Benjamini-Hochberg (BH) procedure** works as follows:

1. **Order p-values**: $P_{(1)} \leq P_{(2)} \leq \cdots \leq P_{(m)}$
2. **Find cutoff**: $k = \max\{i : P_{(i)} \leq \frac{i\alpha}{m}\}$
3. **Reject hypotheses**: $H_{(1)}, \ldots, H_{(k)}$

**Theorem (BH FDR Control)**: Under independence or positive dependence (PRDS), the BH procedure controls FDR at level $\alpha$.

### Mathematical Proof Sketch

The proof relies on showing that under the null hypothesis:

$$\mathbb{E}\left[\frac{V}{R \vee 1}\right] \leq \frac{m_0}{m} \alpha \leq \alpha$$

The key insight is that the BH threshold $\frac{i\alpha}{m}$ creates a proper **spending schedule** that allocates the total error budget optimally.

### Adaptive Extensions

**Storey-BH Procedure**: Estimates the proportion of true nulls $\pi_0$ and uses:

$$\text{Reject } H_i \text{ if } P_i \leq \frac{i\alpha}{m\hat{\pi}_0}$$

where $\hat{\pi}_0(\lambda) = \frac{\#\{i : P_i > \lambda\}}{(1-\lambda)m}$.

## Online FDR Control Framework

### The Online Setting

In **online multiple testing**, p-values arrive sequentially: $P_1, P_2, P_3, \ldots$

At time $t$, we must decide whether to reject $H_t$ based only on:
- The current p-value $P_t$
- Previous p-values $P_1, \ldots, P_{t-1}$  
- Previous decisions $D_1, \ldots, D_{t-1}$

**Constraint**: We cannot use future information $P_{t+1}, P_{t+2}, \ldots$

### Online FDR Definition

For any stopping time $T$ (possibly infinite), we require:

$$\mathbb{E}\left[\frac{V(T)}{R(T) \vee 1}\right] \leq \alpha$$

where $V(T)$ and $R(T)$ are the number of false discoveries and total discoveries up to time $T$.

### The Alpha-Wealth Paradigm

**Key Insight**: Most online FDR procedures use an **alpha-wealth** framework:

1. **Start with wealth** $W_0 \leq \alpha$
2. **Spend wealth** to purchase rejection thresholds: $W_t \leftarrow W_t - \alpha_t$
3. **Earn wealth** from discoveries: $W_t \leftarrow W_t + \text{payout}$

**Theorem (Alpha-Wealth FDR Control)**: If wealth remains non-negative and payouts are properly calibrated, then FDR ≤ α.

## Key Theoretical Results

### Independence Assumption

**Theorem**: Under independence of p-values, most online FDR procedures (LORD, SAFFRON, ADDIS) control FDR at level α.

**Proof technique**: The procedures are designed so that the wealth process $\{W_t\}$ forms a **supermartingale** under the null hypothesis.

### Dependence Handling

**Positive Regression Dependency on Subsets (PRDS)**:
Many procedures maintain FDR control under positive dependence, extending the classical BH result.

**Arbitrary Dependence**:
Requires more conservative procedures (e.g., Benjamini-Yekutieli correction with harmonic series).

### Conservative Nulls

**Problem**: When null p-values are stochastically larger than Uniform(0,1), power decreases dramatically.

**Solution**: ADDIS introduces **discarding** to handle conservative nulls while maintaining FDR control.

## Gamma Sequences and Spending Functions

### Definition

A **gamma sequence** $\{\gamma_t\}_{t=1}^{\infty}$ satisfies:
- $\gamma_t \geq 0$ for all $t$
- $\sum_{t=1}^{\infty} \gamma_t \leq 1$

### Role in Online Testing

Gamma sequences determine how alpha-wealth is spent over time:

$$\alpha_t = \gamma_t \cdot (\text{available wealth})$$

**Common choices**:
- **LORD**: $\gamma_t = \frac{c}{t(t+1)}$ for constant $c$
- **SAFFRON**: $\gamma_t = \frac{c}{(t+1)^{1.6}}$ for power decay

### Optimality Considerations

The choice of gamma sequence affects:
- **Power**: Faster spending → higher early power, lower late power
- **Robustness**: Slower spending → more conservative, sustained power
- **Adaptivity**: Some sequences adapt to discovery history

## Advanced Topics

### Asynchronous Testing

**Setting**: Tests complete at random times, not in submission order.

**Challenges**: 
- Decision order differs from submission order
- Requires careful wealth accounting
- May need modified procedures

**Solutions**: LORDstar and other asynchronous-compatible procedures.

### Multiple Endpoints

**Problem**: Each experiment may test multiple outcomes simultaneously.

**Approaches**:
- **Hierarchical testing**: Primary → secondary endpoints
- **Composite hypotheses**: Joint null vs. any alternative
- **Closed testing**: Maintains familywise error rate

### Non-parametric Guarantees

Most FDR procedures make **no assumptions** about:
- The distribution of test statistics under alternatives
- The effect sizes
- The proportion of true nulls (except adaptive procedures)

This **distribution-free** property is crucial for practical applications.

## Practical Implications

### Power Considerations

**Trade-off**: FDR control inherently trades power for error control.

**Factors affecting power**:
- **Proportion of nulls** ($\pi_0$): Lower $\pi_0$ → higher power
- **Effect sizes**: Larger effects → higher power  
- **Dependence structure**: Positive dependence can help
- **Procedure choice**: Adaptive procedures often more powerful

### Choosing FDR Level

**Guidelines**:
- **α = 0.05**: Standard for most applications
- **α = 0.10**: More liberal for exploratory studies
- **α = 0.01**: Conservative for high-stakes decisions

**Context matters**: Biological discovery vs. financial decisions require different error tolerances.

### Interpretation

**FDR = 0.05** means:
- Among all discoveries made, expect ≤ 5% to be false on average
- **Not** that each individual discovery has ≤ 5% chance of being false
- The guarantee is **average case**, not worst case

## Connections to Other Fields

### Bayesian Multiple Testing

**Connection**: FDR procedures can be viewed through Bayesian lens with specific prior assumptions.

**Local FDR**: $\text{fdr}(p) = \mathbb{P}(H_0 | P = p)$ provides test-specific error rates.

### Machine Learning

**Feature Selection**: FDR control used in high-dimensional regression for selecting relevant features.

**A/B Testing**: Online FDR crucial for continuous experimentation platforms.

### Signal Processing

**Change Point Detection**: Online testing applied to detect structural breaks in time series.

## References

### Foundational Papers

1. **Benjamini, Y., and Y. Hochberg** (1995). "Controlling the false discovery rate: A practical and powerful approach to multiple testing." *Journal of the Royal Statistical Society: Series B*, 57(1):289-300.

2. **Benjamini, Y., and D. Yekutieli** (2001). "The control of the false discovery rate in multiple testing under dependency." *Annals of Statistics*, 29(4):1165-1188.

3. **Storey, J. D.** (2002). "A direct approach to false discovery rates." *Journal of the Royal Statistical Society: Series B*, 64(3):479-498.

### Online FDR Literature

4. **Foster, D. P., and R. A. Stine** (2008). "α-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society: Series B*, 70(2):429-444.

5. **Javanmard, A., and A. Montanari** (2018). "Online rules for control of false discovery rate and false discovery exceedance." *Annals of Statistics*, 46(2):526-554.

6. **Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan** (2018). "SAFFRON: an adaptive algorithm for online control of the false discovery rate." *Proceedings of the 35th International Conference on Machine Learning (ICML)*, PMLR, 80:4286-4294.

### Survey and Tutorial Papers

7. **Goeman, J. J., and A. Solari** (2014). "Multiple hypothesis testing in genomics." *Statistics in Medicine*, 33(11):1946-1978.

8. **Ramdas, A., R. F. Barber, M. J. Wainwright, and M. I. Jordan** (2019). "A unified treatment of multiple testing with prior knowledge using the p-filter." *Annals of Statistics*, 47(5):2790-2821.

## See Also

- **[Algorithm Details](algorithms.md)**: Specific implementations and proofs
- **[Theoretical Guarantees](guarantees.md)**: Detailed analysis of FDR control properties
- **[User Guide](../user_guide/concepts.md)**: Practical introduction to FDR concepts