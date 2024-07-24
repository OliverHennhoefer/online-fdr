from abc import ABC, abstractmethod


class AbstractInvestRule(ABC):
    """Abstract class of an alpha investment rule."""

    @staticmethod
    @abstractmethod
    def allocate_wealth(wealth: float, alpha: float, omega: float) -> float:
        pass

    @staticmethod
    @abstractmethod
    def decrease_wealth(wealth: float, alpha: float) -> float:
        pass
