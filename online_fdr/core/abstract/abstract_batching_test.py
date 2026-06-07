import abc

from online_fdr.core.utils.validity import check_alpha


class AbstractBatchingTest(abc.ABC):
    """Abstract class for batch hypothesis testing."""

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.target_fdr: float = alpha
        self.alpha: float | None = alpha
        self.num_test: int = 0

    @property
    def current_threshold(self) -> float | None:
        """Current rejection boundary in the method's native evidence scale."""
        return self.alpha

    @current_threshold.setter
    def current_threshold(self, value: float | None) -> None:
        self.alpha = value

    @property
    def num_tests(self) -> int:
        """Number of batches processed so far."""
        return self.num_test

    @num_tests.setter
    def num_tests(self, value: int) -> None:
        self.num_test = value

    @abc.abstractmethod
    def test_batch(self, p_vals: list[float]) -> list[bool]:
        """
        Make a decision for a batch of hypotheses.

        :param p_vals: p-value to be tested
        :return: whether to reject which of the hypotheses
        """
        raise NotImplementedError
