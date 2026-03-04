def calculate_sfdr(tp: int, fp: int, eta: float = 0.0001) -> float:
    """Calculate smoothed FDR."""
    return fp / (fp + tp + eta)


def calculate_power(tp: int, fn: int) -> float:
    """Calculate statistical power."""
    return 0.0 if tp + fn == 0 else tp / (tp + fn)


class MemoryDecayFDR:
    def __init__(self, delta: float = 0.99, offset: float = 0):
        self.delta: float = delta
        self.offset: float = offset

        self.labels: list[bool] = []
        self.ground_truth: list[bool] = []
        self.cumulative: bool = False

    def score_one(self, label: bool, ground_truth: bool) -> float | list[float]:
        self.labels.append(label)
        self.ground_truth.append(ground_truth)

        fp = [lb and not gt for lb, gt in zip(self.labels, self.ground_truth)]
        deltas = [self.delta ** float(i) for i in range(len(self.labels))]

        v_t = [
            sum(
                fp[i] * deltas[j - i]
                for i in range(max(0, j - len(deltas) + 1), min(j + 1, len(fp)))
            )
            for j in range(len(fp) + len(deltas) - 1)
        ][: len(self.labels)]

        r_t = [
            sum(
                self.labels[i] * deltas[j - i]
                for i in range(
                    max(0, j - len(deltas) + 1), min(j + 1, len(self.labels))
                )
            )
            for j in range(len(self.labels) + len(deltas) - 1)
        ][: len(self.labels)]

        if not self.cumulative:
            v_scalar = float(v_t[-1])
            r_scalar = float(max(r_t[-1], 1))
            return float(v_scalar / (r_scalar + self.offset))

        r_t = [max(r, 1) for r in r_t]
        return [float(v / (r + self.offset)) for v, r in zip(v_t, r_t)]
