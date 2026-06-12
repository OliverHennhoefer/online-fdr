import abc
from collections.abc import Sequence

from online_fdr.core.results import BatchDecision
from online_fdr.core.state import StatefulMethodMixin
from online_fdr.core.utils.validity import check_alpha


class AbstractBatchingTest(StatefulMethodMixin, abc.ABC):
    """Abstract class for batch hypothesis testing."""

    error_rate = "FDR"

    def __init__(self, alpha: float):
        check_alpha(alpha)

        self.target_level: float = float(alpha)
        self._last_test_level: float | None = None
        self._last_rejection_threshold: float | None = None
        self._num_batches: int = 0
        self._num_hypotheses: int = 0

    @property
    def last_test_level(self) -> float | None:
        """Last batch-level alpha allocation."""
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
        """Read-only alias for the last batch-level alpha allocation."""
        return self.last_test_level

    @property
    def num_batches(self) -> int:
        """Number of non-empty batches processed so far."""
        return self._num_batches

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
        """Read-only legacy alias for the internal batch counter."""
        return self.num_batches

    def _advance_batch(self, num_hypotheses: int) -> None:
        self._num_batches += 1
        self._num_hypotheses += num_hypotheses

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
    def test_batch(self, p_vals: Sequence[float]) -> list[bool]:
        """
        Make a decision for a batch of hypotheses.

        :param p_vals: p-value to be tested
        :return: whether to reject which of the hypotheses
        """
        raise NotImplementedError

    def test_batch_detail(self, p_vals: Sequence[float]) -> BatchDecision:
        """Test one batch and return an immutable decision record."""
        values = [float(value) for value in p_vals]
        rejected = self.test_batch(values)
        return BatchDecision(
            rejected=tuple(rejected),
            values=tuple(values),
            rejection_threshold=self.last_rejection_threshold,
            batch_index=self.num_batches,
            test_level=self.last_test_level,
            error_rate=self.error_rate,
            metadata={"num_rejections": sum(rejected)},
        )
