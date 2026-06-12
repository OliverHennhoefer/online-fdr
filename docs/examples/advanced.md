# Advanced Scenarios

This page collects higher-complexity examples for production-like workflows.

## Recommended Pattern

1. Use one method instance per independent stream.
2. Persist method state between events if processing is distributed.
3. Track empirical FDR/power in a monitoring loop.
4. Keep method parameters fixed for a given experiment protocol.

## Example Topics

- Multi-variant experiment pipelines with online control.
- Rolling-window analysis for non-stationary streams.
- Hybrid workflows that compare online and batch procedures.

## Asynchronous Tests

```python
from online_fdr.p_values import AddisAsync

method = AddisAsync(alpha=0.05, lambda_=0.25, tau=0.5)

level_a = method.start_test("experiment-a")
level_b = method.start_test("experiment-b")

print(level_a.test_level, level_b.test_level)

decision_b = method.finish_test("experiment-b", 0.0001)
decision_a = method.finish_test("experiment-a", 0.2)
print(decision_a, decision_b)
```

## Weighted Side Information

```python
from online_fdr.p_values import WeightedGaiPlusPlus

method = WeightedGaiPlusPlus(alpha=0.05, decay=0.95)

events = [
    (0.002, 1.5, 1.0),
    (0.03, 0.8, 1.2),
    (0.001, 2.0, 0.9),
]

for p_value, prior_weight, penalty_weight in events:
    rejected = method.test_one(
        p_value,
        prior_weight=prior_weight,
        penalty_weight=penalty_weight,
    )
    print(rejected, method.last_rejection_threshold)
```

## Decision Deadlines

```python
from online_fdr.p_values import Toad

method = Toad(alpha=0.05)

method.add_test(0.001, deadline=3, test_id="gene-a")
method.add_test(0.4, deadline=4, test_id="gene-b")
method.add_test(0.006, deadline=4, test_id="gene-c")

finalized = method.advance_to(4)
print(finalized)
```

## Where to Start

- [Basic Usage](basic_usage.md)
- [Method Comparisons](comparison.md)
- [User Guide](../user_guide/index.md)
