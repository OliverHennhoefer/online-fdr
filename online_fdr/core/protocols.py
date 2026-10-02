from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from online_fdr.core.results import BatchDecision, TestDecision


class _TestState(Protocol):
    """Read-only observations shared by testing procedures."""

    @property
    def target_level(self) -> float: ...

    @property
    def error_rate(self) -> str: ...

    @property
    def last_test_level(self) -> float | None: ...

    @property
    def last_rejection_threshold(self) -> float | None: ...

    @property
    def num_hypotheses(self) -> int: ...


class SequentialTest(_TestState, Protocol):
    """Protocol for one-at-a-time multiple-testing procedures."""

    def test_one(self, value: float, /) -> bool:
        """Test one input value and return whether it is rejected."""
        ...

    def test_one_detail(self, value: float, /) -> TestDecision:
        """Test one input value and return an immutable decision record."""
        ...


class BatchTest(_TestState, Protocol):
    """Protocol for batch multiple-testing procedures."""

    @property
    def num_batches(self) -> int: ...

    def test_batch(self, values: Sequence[float], /) -> list[bool]:
        """Test a batch of input values and return rejection decisions."""
        ...

    def test_batch_detail(self, values: Sequence[float], /) -> BatchDecision:
        """Test a batch of input values and return an immutable decision record."""
        ...
