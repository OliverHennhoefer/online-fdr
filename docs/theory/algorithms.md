# Algorithm Descriptions and Analysis

This page provides detailed mathematical descriptions of the online FDR control algorithms implemented in the package, including their theoretical properties and algorithmic details.

## Algorithm Classification

Online FDR control algorithms can be classified along several dimensions:

### By Adaptation Strategy
- **Non-adaptive**: Fixed spending schedules (LOND, LORD)
- **Adaptive**: Adapt to estimated null proportion (SAFFRON, ADDIS)
- **Semi-adaptive**: Adapt to discovery patterns (GAI)

### By Wealth Management
- **Alpha-investing**: Earn back wealth from discoveries (LORD, GAI, SAFFRON, ADDIS)
- **Fixed spending**: Predetermined spending schedule (LOND)

### By Null Handling
- **Standard**: Assume uniform nulls (LOND, LORD, SAFFRON)
- **Conservative**: Handle non-uniform nulls (ADDIS)

## LOND: Levels based On Number of Discoveries

### Algorithm Description

LOND is the simplest online FDR procedure, where thresholds depend only on the number of discoveries made so far.

**Input**: Target FDR level $\alpha$, gamma sequence $\{\gamma_t\}$

**For test $t = 1, 2, \ldots$**:
1. Observe p-value $P_t$
2. Set threshold: $\alpha_t = \gamma_t \cdot (R_{t-1} + 1) \cdot \alpha$
3. Reject if $P_t \leq \alpha_t$
4. Update: $R_t = R_{t-1} + \mathbf{1}_{P_t \leq \alpha_t}$

where $R_t$ is the number of rejections up to time $t$.

### Theoretical Analysis

**Theorem (LOND FDR Control)**: For independent p-values and $\sum_{t=1}^{\infty} \gamma_t \leq 1$, LOND controls FDR at level $\alpha$.

**Proof Sketch**: The key insight is that under the null hypothesis:
$$\mathbb{E}[V_t | \mathcal{F}_{t-1}] = \mathbb{E}[V_{t-1} | \mathcal{F}_{t-1}] + \alpha_t \cdot \mathbf{1}_{H_t \text{ is null}}$$

Since $\sum_t \alpha_t = \alpha \sum_t \gamma_t (R_{t-1} + 1) \leq \alpha m_0$, the FDR is controlled.

### Limitations

1. **Power decay**: Without early discoveries, thresholds become very small
2. **Non-adaptive**: Doesn't adapt to unknown proportion of nulls
3. **Ordering sensitivity**: Performance heavily depends on test ordering

## LORD: Levels based On Recent Discovery

### Algorithm Description

LORD improves upon LOND by using alpha-wealth dynamics and considering the timing of discoveries.

**LORD 3 Algorithm**:

**Input**: Target FDR $\alpha$, initial wealth $W_0$, reward $R$, gamma sequence $\{\gamma_t\}$

**Initialize**: $W_0 \leq \alpha$, $\tau_0 = 0$ (time of last discovery)

**For test $t = 1, 2, \ldots$**:
1. Set threshold: $\alpha_t = \gamma(t - \tau_{\text{last}}) \cdot W_{\tau_{\text{last}}}$
2. Spend wealth: $W_t = W_{t-1} - \alpha_t$
3. Test: Reject if $P_t \leq \alpha_t$
4. If rejected:
   - Update discovery time: $\tau_{\text{last}} = t$
   - Earn reward: $W_t = W_t + R$
   - Record wealth at discovery: $W_{\tau_{\text{last}}} = W_t$

### Key Innovation

LORD uses **recent discovery information**: the threshold depends on:
- Time since last discovery: $t - \tau_{\text{last}}$
- Wealth accumulated at last discovery: $W_{\tau_{\text{last}}}$

This creates **momentum** where recent discoveries enable higher thresholds.

### Theoretical Guarantees

**Theorem (LORD FDR Control)**: Under independence, with proper wealth initialization and gamma sequence, LORD controls FDR at level $\alpha$.

**Proof Strategy**: The wealth process $\{W_t\}$ is designed to be a supermartingale under the null hypothesis, ensuring $\mathbb{E}[W_t] \leq W_0 \leq \alpha$.

## SAFFRON: Adaptive Online FDR Control

### Algorithm Description

SAFFRON introduces **adaptivity** by estimating the proportion of wealth allocated to true nulls.

**Input**: $\alpha$, initial wealth $W_0$, candidate threshold $\lambda$, gamma sequence $\{\gamma_t\}$

**Initialize**: Candidates list $C = []$, rejection list $R = []$

**For test $t = 1, 2, \ldots$**:
1. **Candidate check**: $\text{is\_candidate} = (P_t \leq \lambda)$
2. **Update candidates**: $C_t = C_{t-1} + \text{is\_candidate}$
3. **Calculate threshold**:
   - If $t = 1$: $\alpha_t = (1-\lambda) \gamma_1 W_0$
   - Else: $\alpha_t = f(W_0, C_t, R_t, \lambda, \gamma_t)$ (complex formula)
4. **Test**: Reject if $P_t \leq \alpha_t$
5. **Update rejections**: If rejected, add $t$ to rejection list

### Adaptivity Mechanism

SAFFRON estimates the **alpha-wealth fraction** going to true nulls:

$$\hat{\pi}_0^{(\text{SAFFRON})}(t) \approx \frac{\text{Non-candidates up to } t}{t}$$

This estimate is used to **reallocate wealth** more efficiently than non-adaptive methods.

### Theoretical Properties

**Theorem (SAFFRON FDR Control)**: Under independence, SAFFRON controls FDR at level $\alpha$.

**Key Insight**: The candidate-based estimation provides a **conservative estimate** of the null proportion, ensuring FDR control while improving power.

### Power Advantage

**Theorem (SAFFRON Power)**: Under mild conditions, SAFFRON achieves higher power than LORD when the true proportion of nulls is less than the candidate threshold $\lambda$.

## ADDIS: Adaptive Discarding for Conservative Nulls

### The Conservative Null Problem

**Problem**: When null p-values are **stochastically larger** than Uniform(0,1), existing methods lose substantial power.

**Examples**:
- A/B testing with conservative statistical tests  
- Genomics with correlation-induced conservatism
- Meta-analysis with heterogeneous studies

### Algorithm Description

ADDIS introduces **three thresholds**:
- $\tau$ (discarding): P-values $> \tau$ are discarded (not tested)
- $\lambda$ (candidate): Among non-discarded, those $\leq \lambda$ (after scaling) are candidates
- $\alpha_t$ (rejection): Candidates $\leq \alpha_t$ are rejected

**Input**: $\alpha$, $W_0$, $\lambda$, $\tau$, gamma sequence

**For test $t = 1, 2, \ldots$**:
1. **Discard check**: If $P_t > \tau$, discard (return no rejection)
2. **Scale p-value**: $P_t' = P_t / \tau$ (compensate for discarding)
3. **Candidate check**: $\text{is\_candidate} = (P_t' \leq \lambda)$
4. **Calculate adaptive threshold** (similar to SAFFRON but with scaling)
5. **Test**: Reject if $P_t' \leq \alpha_t$

### Key Innovation

**Discarding mechanism**: By discarding large p-values, ADDIS:
- Focuses testing power on promising hypotheses
- Compensates for conservative null distribution
- Maintains FDR control through proper scaling

### Theoretical Guarantees

**Theorem (ADDIS FDR Control)**: Under uniform or conservative null distributions, ADDIS controls FDR at level $\alpha$.

**Power Theorem**: ADDIS achieves the "best of both worlds":
- **Conservative nulls**: Substantial power gain over SAFFRON/LORD
- **Uniform nulls**: Rarely loses power compared to SAFFRON

## GAI: Generalized Alpha-Investing

### Algorithm Philosophy

GAI extends the original alpha-investing framework with modern gamma sequences and wealth management.

**Core Principle**: When you make a discovery, you gain **evidence** that not all hypotheses are null, justifying increased future spending.

### Algorithm Description

**Input**: $\alpha$, initial wealth $W_0 \leq \alpha$, gamma sequence

**For test $t = 1, 2, \ldots$**:
1. **Calculate threshold**: $\alpha_t = \gamma_t \cdot (\text{available wealth})$
2. **Test**: Reject if $P_t \leq \alpha_t$  
3. **Update wealth**: 
   - Spend: $W_t = W_{t-1} - \alpha_t$
   - Earn (if discovery): $W_t = W_t + \text{payout}$

### Wealth Dynamics

The **payout mechanism** is crucial:
- **Too conservative**: Miss opportunities for future discoveries
- **Too aggressive**: Exhaust wealth quickly

**Optimal payout** depends on:
- Expected proportion of alternatives
- Temporal distribution of alternatives  
- Risk tolerance

### Theoretical Foundation

**Theorem (GAI FDR Control)**: If wealth remains non-negative and payouts are calibrated properly, GAI controls FDR at level $\alpha$.

**Proof**: The wealth process forms a **supermartingale** under the null hypothesis, with $\mathbb{E}[W_t] \leq W_0 \leq \alpha$.

## Comparative Analysis

### Power Comparison

Under typical conditions:

$$\text{Power}_{\text{ADDIS}} \geq \text{Power}_{\text{SAFFRON}} \geq \text{Power}_{\text{LORD}} \geq \text{Power}_{\text{LOND}}$$

**Caveats**:
- ADDIS advantage depends on null conservatism
- SAFFRON advantage depends on unknown $\pi_0$
- LORD advantage depends on discovery timing
- All depend on proper parameter tuning

### Computational Complexity

| Method | Time per test | Space | Comments |
|--------|---------------|--------|----------|
| LOND | $O(1)$ | $O(1)$ | Simplest |
| LORD | $O(1)$ | $O(1)$ | Lightweight |  
| SAFFRON | $O(t)$ | $O(t)$ | Tracks candidate history |
| ADDIS | $O(t)$ | $O(t)$ | Most complex |
| GAI | $O(1)$ | $O(1)$ | Simple wealth dynamics |

### Parameter Sensitivity

**Most sensitive**: ADDIS (`lambda_`, `tau`, and `W` all matter)
**Moderately sensitive**: SAFFRON (`lambda_` and `W`)
**Least sensitive**: LOND (primarily `alpha`)

## Advanced Theoretical Topics

### Gamma Sequences

**Optimal choice** of $\{\gamma_t\}$ balances:
- **Front-loading**: Higher early power, lower late power
- **Uniform spreading**: Consistent power over time
- **Back-loading**: Lower early power, higher late power

**Common choices**:
- LORD: $\gamma_t \propto t^{-2}$
- SAFFRON: $\gamma_t \propto t^{-1.6}$  
- Optimal rates depend on alternative distribution

### Asynchronous Extensions

**Challenge**: Tests may complete out of order.

**Solution**: Modify wealth accounting to handle asynchronous completions while maintaining FDR guarantees.

**LORDstar**: Asynchronous version of LORD with proper wealth management.

### Non-parametric Optimality

**Question**: What is the optimal online FDR procedure?

**Results**: 
- No uniformly optimal procedure exists
- Optimality depends on alternative distribution
- Adaptive procedures achieve better worst-case performance

### Dependence Handling

**Positive dependence** (PRDS): Most procedures maintain FDR control.

**Arbitrary dependence**: Requires modifications:
- Harmonic corrections (Benjamini-Yekutieli style)
- Conservative gamma sequences
- Reduced power but maintained control

## Implementation Considerations

### Numerical Stability

**Wealth tracking**: Avoid negative wealth due to floating-point errors.

**Threshold calculation**: Handle very small thresholds carefully.

**Candidate tracking**: Efficient data structures for long sequences.

### Parameter Selection

**Default recommendations**:
- **LOND**: $\alpha = 0.05$ (no other parameters)
- **LORD**: $W_0 = \alpha/2$, $R = \alpha/2$
- **SAFFRON**: $W_0 = \alpha/2$, $\lambda = 0.5$  
- **ADDIS**: $W_0 = \alpha/2$, $\lambda = 0.25$, $\tau = 0.5$
- **GAI**: $W_0 = \alpha/2$

### Practical Guidelines

1. **Start with SAFFRON** for most applications
2. **Use ADDIS** if conservative nulls are suspected  
3. **Use LORD** for baseline comparisons
4. **Use LOND** for educational purposes only
5. **Use GAI** when simple alpha-investing is preferred

## References

### Algorithm Papers

1. **Javanmard, A., and Montanari, A.** (2015). "On online control of false discovery rate." arXiv preprint arXiv:1502.06197.

2. **Javanmard, A., and A. Montanari** (2018). "Online rules for control of false discovery rate and false discovery exceedance." *Annals of Statistics*, 46(2):526-554.

3. **Ramdas, A., T. Zrnic, M. J. Wainwright, and M. I. Jordan** (2018). "SAFFRON: an adaptive algorithm for online control of the false discovery rate." *Proceedings of the 35th International Conference on Machine Learning (ICML)*, PMLR, 80:4286-4294.

4. **Tian, J., and A. Ramdas** (2019). "ADDIS: an adaptive discarding algorithm for online FDR control with conservative nulls." *Advances in Neural Information Processing Systems (NeurIPS)*, 32.

5. **Foster, D. P., and R. A. Stine** (2008). "-investing: a procedure for sequential control of expected false discoveries." *Journal of the Royal Statistical Society: Series B*, 70(2):429-444.

### Theoretical Analysis

6. **Aharoni, E., and D. Rosset** (2014). "Generalized -investing: definitions, optimality results and application to public databases." *Journal of the Royal Statistical Society: Series B*, 76(4):771-794.

7. **Ramdas, A., R. F. Barber, M. J. Wainwright, and M. I. Jordan** (2019). "A unified treatment of multiple testing with prior knowledge using the p-filter." *Annals of Statistics*, 47(5):2790-2821.

## See Also

- **[Mathematical Foundations](fdr_control.md)**: Basic FDR theory and definitions
- **[Guarantee Matrix](guarantee_matrix.md)**: Method-by-method assumptions and guarantee status
- **[API Reference](../api/investing/index.md)**: Implementation details for each algorithm
