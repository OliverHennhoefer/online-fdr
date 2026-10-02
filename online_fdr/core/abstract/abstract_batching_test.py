import abc
from collections.abc import Sequence

from online_fdr.core.abstract.abstract_test import AbstractTest
from online_fdr.core.results import BatchDecision


class AbstractBatchingTest(AbstractTest):
    """Shared state and detailed results for batch hypothesis testing."""

    def __init__(self, alpha: float):
        super().__init__(alpha)
        self._num_batches: int = 0

    @property
    def num_batches(self) -> int:
        """Number of non-empty batches processed so far."""
        return self._num_batches

    @property
    def num_test(self) -> int:
        """Read-only legacy alias for the internal batch counter."""
        return self.num_batches

    def _advance_batch(self, num_hypotheses: int) -> None:
        self._num_batches += 1
        self._advance_hypotheses(num_hypotheses)

    @abc.abstractmethod
    def test_batch(self, p_vals: Sequence[float], /) -> list[bool]:
        """
        Make a decision for a batch of hypotheses.

        :param p_vals: evidence values to be tested
        :return: whether to reject which of the hypotheses
        """
        raise NotImplementedError

    def test_batch_detail(self, p_vals: Sequence[float]) -> BatchDecision:
        """Test one batch and return an immutable decision record."""
        values = list(p_vals)
        rejected = self.test_batch(values)
        return BatchDecision(
            rejected=tuple(rejected),
            values=tuple(float(value) for value in values),
            rejection_threshold=self.last_rejection_threshold,
            batch_index=self.num_batches,
            test_level=self.last_test_level,
            error_rate=self.error_rate,
            metadata={"num_rejections": sum(rejected)},
        )
