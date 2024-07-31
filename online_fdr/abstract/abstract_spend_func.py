from abc import ABC, abstractmethod


class AbstractSpendFunc(ABC):
    """Abstract class of an alpha spending function."""

    def __init__(self, k: int | None):
        self.k: int | None = k  # None for 'adaptive' functions

    @abstractmethod
    def spend(self, index: int, alpha: float) -> float:
        pass
