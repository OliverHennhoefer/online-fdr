from abc import ABC, abstractmethod


class AbstractInvestmentRule(ABC):
    """Abstract class of an alpha investment function."""

    @staticmethod
    @abstractmethod
    def update_wealth(wealth: float, alpha: float, omega: float) -> float:
        pass
