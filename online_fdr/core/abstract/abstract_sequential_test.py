import abc
from typing import Any

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

    def test_one_detail(self, p_val: float, *args: Any, **kwargs: Any) -> TestDecision:
        """Test one hypothesis and return an immutable decision record."""
        rejected = self.test_one(p_val, *args, **kwargs)
        return TestDecision(
            rejected=bool(rejected),
            value=float(p_val),
            rejection_threshold=self.last_rejection_threshold,
            index=self.num_hypotheses,
            test_level=self.last_test_level,
            error_rate=self.error_rate,
        )
