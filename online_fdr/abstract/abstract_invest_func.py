from abc import ABC, abstractmethod


class AbstractInvestFunc(ABC):
    """Abstract class of an alpha investing function."""

    @staticmethod
    @abstractmethod
    def invest(wealth: float, alpha: float, omega: float) -> float:
        pass

    @staticmethod
    @abstractmethod
    def decrease_wealth(wealth: float, alpha: float) -> float:
        pass
