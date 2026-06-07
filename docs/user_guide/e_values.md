# E-Value Methods

E-values are evidence measures where larger values are stronger evidence against
the null. A valid null e-value has expectation at most one. This is the key
difference from p-values: p-values reject when they are small, e-values reject
when they are large.

## Quick Start

```python
from online_fdr.e_values import EBH, ELond

batch = EBH(alpha=0.05)
batch_decisions = batch.test_batch([1.0, 5.0, 100.0, 2.0])

online = ELond(alpha=0.05)
stream_decisions = [online.test_one(e) for e in [1.0, 20.0, 3.0, 500.0]]
```

## Core Procedures

`EBH` applies the e-Benjamini-Hochberg procedure to a batch of e-values. It
controls FDR under arbitrary dependence when the inputs are valid e-values.

`ELond` is the online e-value analogue of LOND. It uses levels
`alpha_t = alpha * gamma_t * (R_{t-1} + 1)` and rejects when
`e_t >= 1 / alpha_t`. It controls online FDR under arbitrary dependence for
valid e-values.

## Toolbox

```python
from online_fdr.e_values import (
    e_to_p,
    p_to_e_power,
    weighted_arithmetic_mean,
    product_e_values,
)

p_value = e_to_p(20.0)
e_value = p_to_e_power(0.01, exponent=0.5)
merged = weighted_arithmetic_mean([2.0, 5.0, 1.0])
product = product_e_values([2.0, 3.0])
```

`e_to_p(e)` returns `min(1, 1 / e)`, which is conservative. Converting from
p-values to e-values and back is not evidence-preserving.

Weighted arithmetic means are valid under arbitrary dependence when weights are
fixed independently of the null evidence. Products require independence or a
valid conditional/sequential construction supplied by the caller.

## E-Processes

```python
from online_fdr.e_values import LikelihoodRatioEProcess

process = LikelihoodRatioEProcess(lambda x: x)
process.update(0.2)
process.update(1.1)
stopped_e_value = process.current
```

Stopped e-process values are e-values under their stated filtration and stopping
assumptions. Be careful when applying multiple-testing procedures to stopped
local e-processes: the required global filtration assumptions are part of the
statistical design, not something the package can infer automatically.

## Roadmap

The first e-value lane intentionally stabilizes `EBH`, `ELond`, and general
tooling. Newer procedures such as e-GAI, e-LORD, e-SAFFRON, online ARC e-BH,
and stopped e-BH are planned as explicit future or experimental additions.
