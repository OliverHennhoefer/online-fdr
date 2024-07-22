import abc

from online_fdr.utils.validity import check_alpha


class AbstractOnlineTest(abc.ABC):

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.alpha: float = alpha
        self.i: int = 0  # number of tests conducted

    @abc.abstractmethod
    def test_one(self, p_val: float) -> bool:
        """
        Make a rejection decision for a single hypothesis.

        Args:
            p_val (float): The p-value to be tested.

        Returns:
            bool: True if the null hypothesis is rejected, False otherwise.
        """
        pass

    @abc.abstractmethod
    def transform_one(self, p_val: float) -> float:
        """
        Transform a p-value based on the specific method.

        Args:
            p_val (float): The p-value to be transformed.

        Returns:
            float: The transformed p-value.
        """
        pass
