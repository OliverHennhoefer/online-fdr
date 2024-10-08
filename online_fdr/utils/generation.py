import abc
import math
import random


class DataGeneratingProcess(abc.ABC):

    def __init__(self, seed: int = 1):
        self.seed: int = seed

    @abc.abstractmethod
    def generate_normal(self) -> float:
        """Generate a p-value under H0."""
        raise NotImplementedError

    @abc.abstractmethod
    def generate_anomaly(self) -> float:
        """Generate a p-value under H1."""
        raise NotImplementedError


class StandardGaussianProcess(DataGeneratingProcess):

    def __init__(
        self,
        alt_mean: float = 3,
        alt_sd: float = 1,
        seed: int = 1,
    ):
        super().__init__(seed)
        random.seed(seed)

        self.alt_mean: float = alt_mean
        self.alt_sd: float = alt_sd

    def generate_normal(self) -> float:
        return random.uniform(0, 1)

    def generate_anomaly(self) -> float:
        sample = random.gauss(self.alt_mean, self.alt_sd)
        return self.gaussian_cdf(sample)

    @staticmethod
    def gaussian_cdf(x) -> float:
        """Approximation of the standard Gaussian CDF."""
        return 1 - (0.5 * (1 + math.erf(x / math.sqrt(2))))


class DataGenerator:
    """Generates data according to the given data generating process."""

    def __init__(
        self,  # fmt: skip
        n: int,  # fmt: skip
        contamination: float,  # fmt: skip
        dgp: DataGeneratingProcess  # fmt: skip
    ):
        self.n: int = n
        self.contamination: float = contamination
        self.dgp: DataGeneratingProcess = dgp

        self.n_samples = n
        self.n_anomalies = int(contamination * n)
        self.current_sample = 0
        self.current_anomalies = 0

        random.seed(self.dgp.seed)

    def sample_one(self) -> (float, bool):
        if self.current_sample >= self.n_samples:
            raise StopIteration("All samples have been generated.")

        remaining_samples = self.n_samples - self.current_sample
        remaining_anomalies = self.n_anomalies - self.current_anomalies

        remaining_ratio = remaining_anomalies / remaining_samples
        p_anomaly = remaining_ratio if remaining_samples > 0 else 0

        is_anomaly = random.random() < p_anomaly
        if is_anomaly:
            sample = self.dgp.generate_anomaly()
            self.current_anomalies += 1
        else:
            sample = self.dgp.generate_normal()

        self.current_sample += 1

        return sample, is_anomaly
