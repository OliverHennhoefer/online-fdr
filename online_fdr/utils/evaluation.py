def calculate_sfdr(tp: int, fp: int, eta: float = 0.0001) -> float:
    """Calculates the smoothed FDR (sFDR)."""
    return fp / (fp + tp + eta)


def calculate_power(tp: int, fn: int) -> float:
    """Calculates the statistical power."""
    return 0 if tp + fn == 0 else tp / (tp + fn)


class MemoryDecayFDR:

    def __init__(self, delta: float = 0.99, offset: float = 0):
        self.delta: float = delta
        self.offset: float = offset

        self.labels: [bool] = []
        self.ground_truth: [bool] = []

        self.cumulative: bool = False

    def score_one(self, label: bool, ground_truth: bool):

        self.labels.append(label)
        self.ground_truth.append(ground_truth)

        fp = [lb and not g for lb, g in zip(self.labels, self.ground_truth)]
        deltas = [pow(self.delta, float(i)) for i in range(len(self.labels))]

        v_t = [
            sum(
                fp[i] * deltas[j - i]
                for i in range(  # fmt: skip
                    max(0, j - len(deltas) + 1), min(j + 1, len(fp))
                )
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
            v_t = v_t[-1]
            r_t = r_t[-1]

        if isinstance(r_t, list):
            r_t = [max(r, 1) for r in r_t]
        else:
            r_t = max(r_t, 1)

        if isinstance(v_t, list) and isinstance(r_t, list):
            return [v / (r + self.offset) for v, r in zip(v_t, r_t)]
        else:
            return v_t / (r_t + self.offset)
