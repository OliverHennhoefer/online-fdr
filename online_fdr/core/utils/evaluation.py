from online_fdr.core.utils.validity import check_finite_number


def calculate_sfdr(tp: int, fp: int, eta: float = 0.0001) -> float:
    """Calculate smoothed FDR."""
    return fp / (fp + tp + eta)


def calculate_power(tp: int, fn: int) -> float:
    """Calculate statistical power."""
    return 0.0 if tp + fn == 0 else tp / (tp + fn)


class MemoryDecayFDR:
    """Track empirical memory-decay FDR with fixed configuration.

    ``delta`` is in [0, 1], and ``offset`` is nonnegative. Both are read-only;
    construct a new tracker to evaluate a different configuration. ``labels``
    and ``ground_truth`` return detached copies of the recorded boolean history.

    Set ``cumulative`` to return all scores instead of the latest score. This
    option can change between calls without losing earlier scores. Returned
    lists are detached from the tracker. A scalar update costs O(1); cumulative
    output costs O(n) to copy the requested history.
    """

    def __init__(self, delta: float = 0.99, offset: float = 0):
        check_finite_number(delta, "delta")
        check_finite_number(offset, "offset")
        if not 0 <= delta <= 1:
            raise ValueError("delta must be in [0, 1].")
        if offset < 0:
            raise ValueError("offset must be nonnegative.")

        self._delta = float(delta)
        self._offset = float(offset)
        self._labels: list[bool] = []
        self._ground_truth: list[bool] = []
        self._scores: list[float] = []
        self._decayed_false_positives = 0.0
        self._decayed_rejections = 0.0
        self.cumulative: bool = False

    @property
    def delta(self) -> float:
        """Fixed forgetting factor; zero keeps only the current event."""
        return self._delta

    @property
    def offset(self) -> float:
        """Fixed nonnegative denominator offset."""
        return self._offset

    @property
    def labels(self) -> list[bool]:
        """Detached history of rejection decisions."""
        return list(self._labels)

    @property
    def ground_truth(self) -> list[bool]:
        """Detached history; true marks an alternative hypothesis."""
        return list(self._ground_truth)

    def score_one(self, label: bool, ground_truth: bool) -> float | list[float]:
        """Record one decision and return its score or all scores so far."""
        rejected, alternative = bool(label), bool(ground_truth)
        false_positives = self._delta * self._decayed_false_positives + int(
            rejected and not alternative
        )
        rejections = self._delta * self._decayed_rejections + int(rejected)
        score = false_positives / (max(rejections, 1.0) + self._offset)

        self._decayed_false_positives = false_positives
        self._decayed_rejections = rejections
        self._labels.append(rejected)
        self._ground_truth.append(alternative)
        self._scores.append(score)

        return list(self._scores) if self.cumulative else score
