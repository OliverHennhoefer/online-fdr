from abc import ABC, abstractmethod


class AbstractInvestFunc(ABC):
    """Abstract class of an alpha investing function."""

    @abstractmethod
    def invest(
        self, k: int, wealth: float, alpha: float, phi: float, last_reject: int
    ) -> float:
        pass

    @abstractmethod
    def reduce(self, wealth: float, alpha: float) -> float:
        pass
