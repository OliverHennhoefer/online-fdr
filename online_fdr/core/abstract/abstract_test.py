import abc

from online_fdr.core.state import StatefulMethodMixin
from online_fdr.core.utils.validity import check_alpha


class AbstractTest(StatefulMethodMixin, abc.ABC):
    """Shared execution state for p-value and e-value testing methods."""

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
