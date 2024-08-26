# Online Control of the False Discovery Rate
This introduction touches on the historical developments and seminal publications up to modern state-of-the-art methods for controlling the
_false discovery rate_ (FDR) in an online-manner during any kind of sequential hypothesis testing.

## Multiplicity, Interim Analysis and Knowledge Exploitation
The _multiple testing problem_ is a "core problem in statistical inference and arises in almost every scientific field" [[1]](#1).
It gained wider attention with publications of John W. Tuckey  (e.g. [[2]](#2), [[3]](#3), [[4]](#4)) and Henry Scheffé.

Typically, claims of a scientific discoveries are supported by a statistical _p_-value to quantify their statistical significance.
For a single hypothesis test, a _significance threshold_ of $\alpha=0.05$ controls the probability of a _Type I Error_ at $5\%$, as valid
statistical _p_-values under the $\mathcal{H}_{0}$ are [super-]uniformly distributed. With that, there is a probability of $5\%$ to
observe a _p_-value $\leq 0.05$ by pure chance, leading to a _false discovery_ (_Type I Error_) by falsely rejecting $\mathcal{H}_{0}$ and accepting $\mathcal{H}_{1}$.
This probability is measured by the _Family-wise Error Rate_ (FWER) [[2]](#2) that defines the probability of committing _at least_ one _Type I Error_:

$$\mathbb{P}(FWER)=1-(1-\alpha)^{n}$$

In practice, rarely only a single hypothesis is tested. With the advent of large-scale data analysis, the number of hypothesis that are getting
tested simultaneously quickly tend towards hundreds or thousands. This not only applies to sophisticated _clinical trials_ but also e.g.
when measuring the _feature importance_ for a simple [linear] regression model trained on 20 different features by the means of different _t-tests_.</br>
Expanding upon the last example in regard to a single hypothesis, testing **20** simultaneous hypothesis inflates to probability of committing a
_Type I Error_ to $\approx 64\%$:

| Number: hypothesis tests | Probability: at least one _Type I Error_ |
|:------------------------:|:----------------------------------------:|
|            10            |                  0.401                   |
|          **20**          |                **0.642**                 |
|            40            |                  0.871                   |
|            80            |                  0.983                   |
|           160            |                  0.999                   |

Without adjustments to the process of determining _statistical significance_ among test results, the number of _false discoveries_
tends to quickly "over-run true ones over time"[[1]](#1).

## Multiple Testing vs. Online Multiple Testing

### Interim Analysis
One of the earliest use-cases of accounting for the _multiple testing problem_ were clinical trials and corresponding interim analyses.
This involves the (interim) analysis of data that is still accumulating, e.g. as part of an ongoing clinical trial. Methods for adjusting
for the _multiple testing problem_ account for this repeated (sequential) look into accumulating data sets that can help to determine, whether
a study should be continued (or stopped early). With that, statistical rigor is maintained, regardless of the specific study design.

### Knowledge Exploitation
A more recent motivation for adjusting for _multiplicity_ in an _online-manner_ was to incorporate specific _domain knowledge_ [[5]](#5)
into the process of sequential hypothesis testing by determining an specific _order_ in which the hypothesis should be tested. Typically, more
promising hypothesis would be tested first to increase statistical power (...).

**_to be continued_**

## References
<a id="1">[1]</a> 
Tian J, Ramdas A. Online control of the familywise  error rate. Statistical Methods in Medical Research. 2021;30(4):976-993.</br>
<a id="1">[2]</a> 
Tukey, J. W. (1953). The problem of multiple comparisons. Unpublished manuscript. In The  Collected Works of John W. Tukey VIII. Multiple Comparisons: 1948–1983 1–300.  Chapman and Hall, New York.</br>
<a id="1">[3]</a> 
Tukey, J. W. (1977a). Some thoughts on clinical trials, especially problems of multiplicity. Science 198 679–684.</br>
<a id="1">[4]</a> 
Tukey, J. W. (1991). The philosophy of multiple comparisons. Statist. Sci. 6 100–116.</br>
<a id="1">[5]</a> 
Foster, D., and R. Stine. α-investing: a procedure for seq. control of expected false discoveries. Journal of the Royal Statistical Society (Series B), 70(2):429-444, 2008.

