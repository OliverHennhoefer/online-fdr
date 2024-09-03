import abc

from online_fdr.utils.validity import check_alpha


class AbstractSequentialTest(abc.ABC):
    """Abstract class for sequential hypothesis testing."""

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.alpha: float = alpha
        self.num_test: int = 0

    @abc.abstractmethod
    def test_one(self, p_val: float) -> bool:
        """
        Make a decision for a single hypothesis.

        :param p_val: p-value to be tested
        :return: whether to reject the hypothesis or not
        """
        raise NotImplementedError
