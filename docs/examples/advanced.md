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

## Where to Start

- [Basic Usage](basic_usage.md)
- [Method Comparisons](comparison.md)
- [User Guide](../user_guide/index.md)
