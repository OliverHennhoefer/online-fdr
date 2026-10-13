import abc

from online_fdr.core.abstract.abstract_test import AbstractTest
from online_fdr.core.results import TestDecision


class AbstractSequentialTest(AbstractTest):
    """Shared state and detailed results for sequential hypothesis testing."""

    @property
    def num_test(self) -> int:
        """Read-only legacy alias for the internal hypothesis counter."""
        return self.num_hypotheses

    @abc.abstractmethod
    def test_one(self, p_val: float, /) -> bool:
        """
        Make a decision for a single hypothesis.

        :param p_val: evidence value to be tested
        :return: whether to reject the hypothesis or not
        """
        raise NotImplementedError

    def test_one_detail(self, p_val: float) -> TestDecision:
        """Test one hypothesis and return an immutable decision record."""
        return self._decision(p_val, self.test_one(p_val))

    def _decision(self, value: float, rejected: bool) -> TestDecision:
        """Capture the shared observations after a completed test."""
        return TestDecision(
            rejected=bool(rejected),
            value=float(value),
            rejection_threshold=self.last_rejection_threshold,
            index=self.num_hypotheses,
            test_level=self.last_test_level,
            error_rate=self.error_rate,
        )
