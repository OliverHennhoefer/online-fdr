from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestDecision:
    """Decision details for a single hypothesis test."""

    rejected: bool
    value: float
    threshold: float | None
    index: int


@dataclass(frozen=True)
class BatchDecision:
    """Decision details for a batch of hypotheses."""

    rejected: list[bool]
    values: list[float]
    threshold: float | None
