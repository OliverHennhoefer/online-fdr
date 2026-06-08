# E-Value Methods

E-values are evidence measures where larger values are stronger evidence
against a null hypothesis. A valid null e-value is nonnegative and has null
expectation at most one. This expectation bound, rather than a small-tail
probability bound, is what gives e-value procedures their dependence-robust
multiple-testing guarantees.

The e-value API is a first-class package surface:

```python
from online_fdr.e_values import EBH, ELond
```

Use this API when your evidence is naturally expressed as likelihood ratios,
betting scores, stopped e-processes, or calibrated p-values with explicitly
documented construction assumptions.

## P-Values vs E-Values

| Evidence type | Strong evidence | Null validity condition | Typical decision rule |
|---|---:|---|---|
| p-value | small | `P(P <= u) <= u` under the null | reject when `p <= alpha_t` |
| e-value | large | `E[E] <= 1` under the null | reject when `e >= 1 / alpha_t` |

The conversion `e_to_p(e) = min(1, 1 / e)` is conservative. It is useful for
interoperability, but converting p-values to e-values and back is not
evidence-preserving.

## Procedure Selection

| Situation | Procedure | Import | Guarantee scope |
|---|---|---|---|
| Fixed batch of valid e-values | e-BH | `from online_fdr.e_values import EBH` | FDR under arbitrary dependence |
| Online stream of valid e-values | e-LOND | `from online_fdr.e_values import ELond` | Online FDR under arbitrary dependence |
| Need to construct e-values | Toolbox, generation, processes | `online_fdr.e_values.*` | Construction-level validity only |

Toolbox utilities do not provide FDR control by themselves. They construct,
combine, or transform evidence; FDR control comes from feeding valid e-values
into a valid e-value multiple-testing procedure under its stated assumptions.

## Batch E-BH

`EBH` implements the base e-Benjamini-Hochberg procedure of Wang and Ramdas
(2022). Given `m` e-values sorted descending as `e_(1) >= ... >= e_(m)`, it
chooses the largest `k` satisfying:

$$
e_{(k)} \geq \frac{m}{\alpha k}.
$$

It rejects exactly the hypotheses belonging to the top `k` e-values and returns
decisions in the original input order.

```python
from online_fdr.e_values import EBH, e_bh

e_values = [1.0, 3.0, 100.0, 8.0, 0.5]

decisions = e_bh(e_values, alpha=0.1)

method = EBH(alpha=0.1)
same_decisions = method.test_batch(e_values)

assert decisions == same_decisions
```

`test_batch([])` returns `[]` without mutating state.

## Online E-LOND

`ELond` implements e-LOND from Xu and Ramdas (2024). At time `t`, it computes:

$$
\alpha_t = \alpha \gamma_t (R_{t-1} + 1),
$$

where `R_{t-1}` is the number of previous rejections. It rejects when:

$$
E_t \geq 1 / \alpha_t.
$$

The class exposes the configured target as `target_fdr`, the current e-value
test level as `current_level`, the reciprocal rejection boundary as
`current_threshold`, and the stream length as `num_tests`.

```python
from online_fdr.e_values import ELond

method = ELond(alpha=0.05)

for e_value in [1.0, 20.0, 3.0, 500.0]:
    rejected = method.test_one(e_value)
    print(method.num_tests, method.current_level, method.current_threshold, rejected)
```

You may inject a custom gamma sequence by passing an object with
`calc_gamma(index)` or `calc_gamma(index, alpha=...)`.

## Construction Toolbox

### Validation

```python
from online_fdr.e_values import check_e_value, check_e_values

check_e_value(2.5)
check_e_values([0.0, 1.0, float("inf")])
```

E-values must be numeric, nonnegative, and not NaN. Infinite e-values are
allowed because exact-zero calibrated p-values and zero null-density likelihood
ratios can produce them.

### Conversion

```python
from online_fdr.e_values import e_to_p, make_power_calibrator, p_to_e_power

p_value = e_to_p(20.0)
e_value = p_to_e_power(0.01, exponent=0.5)
calibrator = make_power_calibrator(0.5)
same_e_value = calibrator(0.01)
```

The power calibrator is valid for `0 < exponent < 1`. Its validity depends on
the input being a valid p-value.

### Merging

```python
from online_fdr.e_values import product_e_values, weighted_arithmetic_mean

robust_merge = weighted_arithmetic_mean([2.0, 5.0, 1.0])
sequential_product = product_e_values([1.2, 0.8, 3.0])
```

Weighted arithmetic means are valid under arbitrary dependence when the weights
are fixed independently of the null evidence. Product helpers are intended for
independent or conditionally valid sequential e-values; that assumption is
supplied by the user.

## E-Processes

An e-process is an anytime-valid process whose value at a valid stopping time is
an e-value. The process helpers are deliberately low-level because the package
cannot infer your filtration, model, or stopping assumptions.

```python
from online_fdr.e_values import LikelihoodRatioEProcess, value_at_stop

process = LikelihoodRatioEProcess(lambda observation: observation)
process.update(0.2)
process.update(1.1)

stopped_e_value = value_at_stop(process)
```

For stopped local e-processes used in multiple testing, the global filtration
condition matters. The stopped e-BH literature shows that local stopping-time
validity alone is not enough under arbitrary cross-stream information flow.

## Generators

The e-value generation helpers mirror the p-value simulation tools for examples
and sanity checks.

```python
from online_fdr.e_values import GaussianEValueGenerator

generator = GaussianEValueGenerator(n=100, pi0=0.9, alt_mean=3.0, seed=1)
e_value, is_alternative = generator.sample_one()
batch, labels = generator.sample_batch(10)
```

## Roadmap

The stable first wave is `EBH`, `ELond`, and general e-value tooling. Newer
procedures such as e-GAI, e-LORD, e-SAFFRON, online ARC e-BH, and stopped e-BH
are roadmap items unless they later appear under an explicit experimental
namespace.

## References And Author Code

- Wang, R. and Ramdas, A. (2022). False discovery rate control with e-values.
  Journal of the Royal Statistical Society: Series B.
  Paper: https://academic.oup.com/jrsssb/article/84/3/822/7056146
  Author code: https://github.com/ruoduwang/e-BH
- Xu, Z. and Ramdas, A. (2024). Online multiple testing with e-values.
  Proceedings of AISTATS 2024.
  Paper: https://proceedings.mlr.press/v238/xu24a.html
  Author code: https://github.com/neilzxu/evalue-omt
- Vovk, V. and Wang, R. (2021). E-values: Calibration, combination, and
  applications. Annals of Statistics.
  DOI: https://doi.org/10.1214/20-AOS2020
- Wang, H., Dandapanthula, S. and Ramdas, A. (2025). Anytime-valid FDR control
  with the stopped e-BH procedure.
  Preprint: https://arxiv.org/abs/2502.08539
