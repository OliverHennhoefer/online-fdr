from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class SequentialTest(Protocol):
    """Protocol for one-at-a-time multiple-testing procedures."""

    target_fdr: float
    current_threshold: float | None
    num_tests: int

    def test_one(self, value: float) -> bool:
        """Test one input value and return whether it is rejected."""
        ...


class BatchTest(Protocol):
    """Protocol for batch multiple-testing procedures."""

    target_fdr: float
    current_threshold: float | None
    num_tests: int

    def test_batch(self, values: Sequence[float]) -> list[bool]:
        """Test a batch of input values and return rejection decisions."""
        ...
