import abc

from online_fdr.core.utils.validity import check_alpha


class AbstractSequentialTest(abc.ABC):
    """Abstract class for sequential hypothesis testing."""

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
        """Number of hypotheses processed so far."""
        return self.num_test

    @num_tests.setter
    def num_tests(self, value: int) -> None:
        self.num_test = value

    @abc.abstractmethod
    def test_one(self, p_val: float) -> bool:
        """
        Make a decision for a single hypothesis.

        :param p_val: p-value to be tested
        :return: whether to reject the hypothesis or not
        """
        raise NotImplementedError
