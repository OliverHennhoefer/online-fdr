# Method Comparisons

This page is a hub for practical comparisons between procedures.

## Comparison Checklist

1. Fix random seeds for reproducibility.
2. Evaluate both error control and power.
3. Run enough replications to reduce Monte Carlo noise.
4. Compare methods under both null-heavy and signal-heavy regimes.

## Suggested Baseline Set

- `Addis`
- `Saffron`
- `LordThree`
- `BatchBH`

## Minimal Experiment Skeleton

```python
import random

from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.saffron.saffron import Saffron

rng = random.Random(42)
p_values = [rng.random() for _ in range(500)]

methods = {
    "addis": Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
    "saffron": Saffron(alpha=0.05, wealth=0.025, lambda_=0.5),
}

discoveries = {name: sum(method.test_one(p) for p in p_values) for name, method in methods.items()}
print(discoveries)
```

## Next Links

- [Performance Evaluation](../user_guide/evaluation.md)
- [Guarantee Matrix](../theory/guarantee_matrix.md)
