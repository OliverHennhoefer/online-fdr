import abc

from online_fdr.utils.validity import check_alpha


class AbstractOnlineTest(abc.ABC):
    """Abstract class for online hypothesis testing."""

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.alpha: float = alpha
        self.num_test: int = 0

    @abc.abstractmethod
    def test_one(self, p_val: float) -> bool:
        """
        Make a rejection decision for a single hypothesis.

        Args:
            p_val (float): The p-value to be tested.

        Returns:
            bool: True if the null hypothesis is rejected, False otherwise.
        """
        raise NotImplementedError
