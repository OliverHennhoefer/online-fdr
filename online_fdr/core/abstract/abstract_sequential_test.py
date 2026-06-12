import abc
from typing import Any

from online_fdr.core.results import TestDecision
from online_fdr.core.state import StatefulMethodMixin
from online_fdr.core.utils.validity import check_alpha


class AbstractSequentialTest(StatefulMethodMixin, abc.ABC):
    """Abstract class for sequential hypothesis testing."""

    error_rate = "FDR"

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.target_level: float = float(alpha)
        self._last_test_level: float | None = None
        self._last_rejection_threshold: float | None = None
        self._num_hypotheses: int = 0

    @property
    def last_test_level(self) -> float | None:
        """Last method-specific test level."""
        return self._last_test_level

    @property
    def last_rejection_threshold(self) -> float | None:
        """Last input-scale rejection threshold."""
        return self._last_rejection_threshold

    @property
    def current_threshold(self) -> float | None:
        """Alias for the last input-scale rejection threshold."""
        return self.last_rejection_threshold

    @property
    def alpha(self) -> float | None:
        """Read-only alias for the last method-specific test level."""
        return self.last_test_level

    @property
    def num_hypotheses(self) -> int:
        """Number of hypotheses processed so far."""
        return self._num_hypotheses

    @property
    def num_tests(self) -> int:
        """Number of hypotheses processed so far."""
        return self.num_hypotheses

    @property
    def num_test(self) -> int:
        """Read-only legacy alias for the internal hypothesis counter."""
        return self.num_hypotheses

    def _advance_hypotheses(self, count: int = 1) -> None:
        self._num_hypotheses += count

    def _set_test_level(
        self,
        level: float | None,
        rejection_threshold: float | None = None,
    ) -> None:
        self._last_test_level = None if level is None else float(level)
        if rejection_threshold is None:
            rejection_threshold = level
        self._last_rejection_threshold = (
            None if rejection_threshold is None else float(rejection_threshold)
        )

    @abc.abstractmethod
    def test_one(self, p_val: float) -> bool:
        """
        Make a decision for a single hypothesis.

        :param p_val: p-value to be tested
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
