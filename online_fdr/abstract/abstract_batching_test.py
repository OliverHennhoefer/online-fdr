import abc

from online_fdr.utils.validity import check_alpha


class AbstractBatchingTest(abc.ABC):
    """Abstract class for batch hypothesis testing."""

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.alpha: float = alpha
        self.num_test: int = 0

    @abc.abstractmethod
    def test_batch(self, p_vals: list[float]) -> bool:
        """
        Make a decision for a batch of hypotheses.

        :param p_vals: p-value to be tested
        :return: whether to reject which of the hypotheses
        """
        raise NotImplementedError
