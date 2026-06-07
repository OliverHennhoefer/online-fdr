# E-Value Examples

These examples mirror the p-value examples but use the e-value lane. E-values
are large-is-strong evidence, so the decision boundaries are reciprocal levels.

## Batch E-BH

Use `EBH` when all e-values are available at once.

```python
from online_fdr.e_values import EBH

e_values = [1.0, 4.0, 80.0, 12.0, 0.5, 25.0]

method = EBH(alpha=0.1)
decisions = method.test_batch(e_values)

discoveries = [
    {"index": idx, "e_value": e_value}
    for idx, (e_value, rejected) in enumerate(zip(e_values, decisions))
    if rejected
]

print(discoveries)
print(method.current_threshold)
```

`EBH` sorts internally and returns decisions in the original input order.

## Online E-LOND Stream

Use `ELond` when e-values arrive sequentially and each decision must be made
before seeing future evidence.

```python
from online_fdr.e_values import ELond

method = ELond(alpha=0.1)
stream = [1.0, 4.0, 80.0, 2.0, 500.0]

for idx, e_value in enumerate(stream, start=1):
    rejected = method.test_one(e_value)
    print(
        idx,
        e_value,
        method.current_level,
        method.current_threshold,
        rejected,
    )
```

`current_level` is the e-LOND level `alpha_t`; `current_threshold` is
`1 / alpha_t`.

## Calibrating P-Values To E-Values

The power calibrator can turn valid p-values into valid e-values. This is useful
when a pipeline still produces p-values but you want to use an e-value
procedure. The round trip is not evidence-preserving.

```python
from online_fdr.e_values import EBH, e_to_p, make_power_calibrator

p_values = [0.001, 0.2, 0.03, 0.8, 0.01]
calibrator = make_power_calibrator(exponent=0.5)
e_values = [calibrator(p_value) for p_value in p_values]

decisions = EBH(alpha=0.1).test_batch(e_values)
conservative_p_values = [e_to_p(e_value) for e_value in e_values]

print(e_values)
print(conservative_p_values)
print(decisions)
```

## Merging Multiple E-Values

Weighted arithmetic means are valid under arbitrary dependence when weights are
fixed independently of the null evidence.

```python
from online_fdr.e_values import weighted_arithmetic_mean

replicate_e_values = [2.0, 0.8, 5.0]
merged = weighted_arithmetic_mean(replicate_e_values, weights=[1.0, 1.0, 2.0])

print(merged)
```

Products are only appropriate when the input e-values are independent or
conditionally valid in the sequential sense supplied by your statistical design.

```python
from online_fdr.e_values import product_e_values

sequential_e_value = product_e_values([1.1, 0.9, 4.0])
print(sequential_e_value)
```

## Gaussian Likelihood-Ratio Simulation

The e-value generator is useful for examples and statistical sanity checks. It
produces labeled Gaussian likelihood-ratio e-values.

```python
from online_fdr.e_values import ELond, GaussianEValueGenerator

generator = GaussianEValueGenerator(n=100, pi0=0.9, alt_mean=3.0, seed=7)
method = ELond(alpha=0.1)

true_discoveries = 0
false_discoveries = 0

for _ in range(100):
    e_value, is_alternative = generator.sample_one()
    rejected = method.test_one(e_value)

    if rejected and is_alternative:
        true_discoveries += 1
    elif rejected:
        false_discoveries += 1

discoveries = true_discoveries + false_discoveries
empirical_fdr = false_discoveries / max(discoveries, 1)

print(true_discoveries, false_discoveries, empirical_fdr)
```

## Stopped E-Process Value

Stopped e-process values are e-values under the process and stopping-time
assumptions of the design.

```python
from online_fdr.e_values import LikelihoodRatioEProcess, value_at_stop

process = LikelihoodRatioEProcess(lambda observation: observation)

for observation in [0.1, -0.2, 0.8]:
    process.update(observation)

stopped_e_value = value_at_stop(process)
print(stopped_e_value)
```

When stopped local e-processes are used in multiple testing, verify the global
filtration assumptions before relying on stopped e-BH-style guarantees.
