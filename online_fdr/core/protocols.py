from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from online_fdr.core.results import BatchDecision, TestDecision


class SequentialTest(Protocol):
    """Protocol for one-at-a-time multiple-testing procedures."""

    target_level: float
    error_rate: str
    last_test_level: float | None
    last_rejection_threshold: float | None
    num_hypotheses: int

    def test_one(self, value: float) -> bool:
        """Test one input value and return whether it is rejected."""
        ...

    def test_one_detail(self, value: float) -> TestDecision:
        """Test one input value and return an immutable decision record."""
        ...


class BatchTest(Protocol):
    """Protocol for batch multiple-testing procedures."""

    target_level: float
    error_rate: str
    last_test_level: float | None
    last_rejection_threshold: float | None
    num_batches: int
    num_hypotheses: int

    def test_batch(self, values: Sequence[float]) -> list[bool]:
        """Test a batch of input values and return rejection decisions."""
        ...

    def test_batch_detail(self, values: Sequence[float]) -> BatchDecision:
        """Test a batch of input values and return an immutable decision record."""
        ...
