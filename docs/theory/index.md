# Mathematical Theory

This section provides the mathematical foundations underlying online false discovery rate (FDR) control methods. Understanding the theory helps in choosing appropriate methods, setting parameters correctly, and interpreting results.

## Overview

Online FDR control addresses the fundamental challenge of multiple hypothesis testing in sequential settings where:

1. **Hypotheses arrive over time**: $H_1, H_2, H_3, \ldots$
2. **Decisions must be immediate**: Can't wait for future p-values
3. **Statistical guarantees must hold**: FDR ≤ α at all stopping times

This creates a fundamentally different problem from traditional batch multiple testing correction.

## Core Mathematical Framework

### Problem Setup

Let $(H_i, p_i)$ be the sequence of null hypotheses and corresponding p-values arriving at times $i = 1, 2, 3, \ldots$.

**Online Testing Rule**: A sequence of (possibly random) thresholds $(\alpha_i)_{i \geq 1}$ where:
- $\alpha_i$ depends only on $(p_1, R_1), \ldots, (p_{i-1}, R_{i-1})$
- $R_i = \mathbf{1}(p_i \leq \alpha_i)$ is the rejection indicator

### False Discovery Rate

For any stopping time $T$, define:

$$\text{FDR}(T) = \mathbb{E}\left[\frac{V(T)}{\max(R(T), 1)}\right]$$

where:
- $V(T) = \sum_{i=1}^T (1-H_i) R_i$ (false discoveries)
- $R(T) = \sum_{i=1}^T R_i$ (total discoveries)
- $H_i = 1$ if $H_i$ is false (alternative), 0 if true (null)

**Goal**: Design $(\alpha_i)$ such that $\text{FDR}(T) \leq \alpha$ for all $T$.

## Theoretical Foundations

### [FDR Control Theory](fdr_control.md)
**Mathematical principles of FDR control**

- Benjamini-Hochberg procedure and extensions
- Online vs batch FDR control differences  
- Stopping time considerations
- Dependence structures and their impact

### [Algorithm Design](algorithms.md)
**Core algorithmic approaches and their analysis**

- Alpha investing framework
- Wealth dynamics and martingale theory
- Sequential testing with discarding
- Adaptive estimation techniques

### [Statistical Guarantees](guarantees.md)
**Theoretical guarantees and their assumptions**

- Independence and dependence assumptions
- Uniform and conservative null hypotheses
- Finite-sample vs asymptotic results
- Robustness to model misspecification

## Key Theoretical Results

### Alpha Investing Martingale

The foundation of alpha investing methods relies on a wealth martingale:

**Theorem (Foster & Stine, 2008)**: Define wealth process $W_i$ where:
- $W_0 = w_0 \geq 0$ (initial wealth)  
- $W_i = W_{i-1} + \psi_i$ where $\psi_i$ is the wealth change from test $i$

If $\mathbb{E}[\psi_i | \mathcal{F}_{i-1}] \leq 0$ for all $i$, then $(W_i)$ is a supermartingale, and:

$$\mathbb{E}[V(T)] \leq w_0 \text{ for any stopping time } T$$

This leads to FDR control when wealth is properly allocated.

### SAFFRON Adaptive Estimation

**Theorem (Ramdas et al., 2018)**: The SAFFRON procedure with adaptive null proportion estimation $\hat{\pi}_0(t)$ satisfies:

$$\text{FDR}(T) \leq \alpha \cdot \frac{\pi_0}{\mathbb{E}[\hat{\pi}_0(T)]}$$

Under suitable conditions on the estimator, this yields $\text{FDR}(T) \leq \alpha$.

### ADDIS Discarding Analysis  

**Theorem (Tian & Ramdas, 2019)**: For conservative nulls with $F_0(p) \leq p$, ADDIS with discarding threshold $\tau$ satisfies:

$$\text{mFDR}(T) \leq \alpha$$

where mFDR is the modified FDR among non-discarded tests.

## Common Mathematical Constructions

### 1. **Gamma Sequences**

Many methods use probability sequences $(\gamma_i)$ with:
- $\gamma_i \geq 0$ and $\sum_{i=1}^{\infty} \gamma_i = 1$
- Often $\gamma_i = C \log(\max(i,2))/(i \exp(\sqrt{\log i}))$

These control the allocation of alpha-wealth across tests.

### 2. **Candidate Selection**

Methods like SAFFRON and ADDIS use candidate sets:
- $C_i = \{j \leq i : p_j \leq \lambda\}$ (candidates by time $i$)
- Rejection thresholds apply only to candidates
- Allows adaptive focusing on promising hypotheses

### 3. **Wealth Dynamics**

General wealth update formula:
$$W_i = W_{i-1} - \text{cost}_i + \text{reward}_i \cdot R_i$$

where:
- $\text{cost}_i$: alpha spent on test $i$
- $\text{reward}_i$: alpha earned from discovery $i$

## Dependency Structures

### Independent P-values

**Assumption**: $p_1, p_2, \ldots$ are mutually independent

**Methods**: All methods work, optimal power achievable

**Theory**: Classical martingale arguments apply directly

### Positive Dependence

**Assumption**: Test statistics exhibit positive correlation

**Examples**: 
- Genomic data from nearby regions
- Related biomarkers  
- Overlapping populations

**Theory**: FDR control often preserved under positive dependence

### Arbitrary Dependence

**Assumption**: No restrictions on dependence structure  

**Methods**: Conservative variants (Benjamini-Yekutieli, dependent LOND)

**Theory**: Requires more sophisticated analysis, often less powerful

### Temporal Dependence

**Special case**: Sequential correlation in online settings

$$\text{Cov}(p_i, p_j) = \rho(|i-j|)$$

**Methods**: LORD with memory decay, time-aware procedures

## Key Theoretical Insights

### 1. **Online vs Batch Trade-offs**

**Batch optimal**: Benjamini-Hochberg achieves minimum FDR for given power

**Online constraint**: Cannot achieve same optimality due to limited information

**Gap**: Online methods typically have 5-15% power loss vs batch

### 2. **Conservative Nulls Advantage**

When null p-values satisfy $F_0(p) \leq p$ (conservative):
- Traditional methods lose power significantly
- ADDIS-type discarding methods maintain or gain power
- Real applications often have conservative nulls

### 3. **Wealth Management Principle**

Optimal alpha-wealth allocation follows:
- **Spend cautiously early**: Build up discoveries for momentum
- **Spend aggressively after success**: Leverage discovery clusters  
- **Save for dry periods**: Maintain ability to detect sparse signals

## Advanced Topics

### Asynchronous Testing

Tests that start and finish at random times:
- Martingale theory extends with random stopping  
- Requires careful handling of information flow
- Applications: Clinical trials, A/B testing platforms

### Group Sequential Methods  

Testing families of related hypotheses:
- Hierarchical testing structures
- Closed testing procedures
- Applications: Clinical trials with multiple endpoints

### Nonparametric Methods

FDR control without distributional assumptions:
- Rank-based procedures
- Permutation methods  
- Bootstrap approaches

## Computational Considerations

### Algorithm Complexity

Most online FDR methods have:
- **Time per test**: $O(1)$ to $O(\log i)$
- **Memory**: $O(1)$ to $O(i)$ for history-dependent methods
- **Numerical stability**: Well-behaved for reasonable parameters

### Implementation Challenges

- **Floating point precision**: Wealth can become very small
- **Parameter selection**: Often requires domain knowledge
- **Monitoring**: Need real-time performance tracking

## Open Research Questions

### Theoretical Gaps

1. **Optimal online procedures**: What's the fundamental limit of online FDR control?
2. **Dependence modeling**: Better handling of complex correlation structures
3. **Adaptive parameter selection**: Theory-guided parameter tuning

### Practical Extensions

1. **Multi-objective control**: Simultaneous FDR and power optimization
2. **Contextual information**: Using covariate information in decisions  
3. **Distributed testing**: FDR control across multiple data centers

## Mathematical Notation Reference

| Symbol | Meaning |
|--------|---------|
| $H_i$ | $i$-th null hypothesis |
| $p_i$ | $i$-th p-value |
| $\alpha_i$ | $i$-th significance threshold |
| $R_i$ | $i$-th rejection indicator |
| $V(T)$ | False discoveries by time $T$ |
| $R(T)$ | Total discoveries by time $T$ |
| $W_i$ | Alpha-wealth at time $i$ |
| $\gamma_i$ | $i$-th element of gamma sequence |
| $\mathcal{F}_i$ | Filtration (information) up to time $i$ |
| $\pi_0$ | Proportion of true null hypotheses |
| $\lambda$ | Candidate threshold |
| $\tau$ | Discarding threshold |

## Further Reading

Each subsection provides detailed mathematical development:

- **[FDR Control Theory](fdr_control.md)**: Fundamental principles and classical results
- **[Algorithm Design](algorithms.md)**: Mathematical construction of online methods
- **[Statistical Guarantees](guarantees.md)**: Formal theorems and their proofs

For implementation details, see the [API Reference](../api/index.md).  
For practical applications, explore [Examples](../examples/index.md).