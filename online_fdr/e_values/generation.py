from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from online_fdr.e_values.toolbox import p_to_e_power

__all__ = [
    "GaussianEValueGenerator",
    "calibrated_p_value_stream",
    "gaussian_likelihood_ratio_e_value",
    "gaussian_likelihood_ratio_e_values",
]


def gaussian_likelihood_ratio_e_value(
    sample: float,
    alt_mean: float,
    *,
    null_mean: float = 0.0,
    std: float = 1.0,
) -> float:
    """Likelihood-ratio e-value for normal means with known common variance."""
    if std <= 0:
        raise ValueError("std must be positive.")
    sample = float(sample)
    variance = std * std
    log_lr = ((sample - null_mean) ** 2 - (sample - alt_mean) ** 2) / (2 * variance)
    return float(np.exp(log_lr))


def gaussian_likelihood_ratio_e_values(
    samples: np.ndarray | list[float],
    alt_mean: float,
    *,
    null_mean: float = 0.0,
    std: float = 1.0,
) -> np.ndarray:
    """Vectorized Gaussian likelihood-ratio e-values."""
    if std <= 0:
        raise ValueError("std must be positive.")
    values = np.asarray(samples, dtype=float)
    variance = std * std
    log_lr = ((values - null_mean) ** 2 - (values - alt_mean) ** 2) / (2 * variance)
    return np.exp(log_lr)


def calibrated_p_value_stream(
    p_values: np.ndarray | list[float],
    exponent: float,
) -> np.ndarray:
    """Convert p-values to e-values with the power calibrator."""
    return np.asarray([p_to_e_power(float(p_value), exponent) for p_value in p_values])


class GaussianEValueGenerator:
    """Generate labeled Gaussian likelihood-ratio e-values."""

    def __init__(
        self,
        n: int,
        pi0: float,
        alt_mean: float = 3.0,
        null_mean: float = 0.0,
        std: float = 1.0,
        batch_size: Optional[int] = None,
        seed: int = 1,
    ):
        if n <= 0:
            raise ValueError("n must be positive.")
        if not 0 <= pi0 <= 1:
            raise ValueError("pi0 must be in [0, 1].")
        if std <= 0:
            raise ValueError("std must be positive.")
        self.n = int(n)
        self.pi0 = float(pi0)
        self.alt_mean = float(alt_mean)
        self.null_mean = float(null_mean)
        self.std = float(std)
        self.batch_size = batch_size
        self.rng = np.random.RandomState(seed)
        self.current_idx = 0

        n_null = int(self.n * self.pi0)
        n_alt = self.n - n_null
        null_samples = self.rng.normal(self.null_mean, self.std, n_null)
        alt_samples = self.rng.normal(self.alt_mean, self.std, n_alt)
        samples = np.concatenate([null_samples, alt_samples])
        labels = np.concatenate([np.zeros(n_null), np.ones(n_alt)]).astype(bool)
        order = self.rng.permutation(self.n)

        self.samples = samples[order]
        self.labels = labels[order]
        self.e_values = gaussian_likelihood_ratio_e_values(
            self.samples,
            self.alt_mean,
            null_mean=self.null_mean,
            std=self.std,
        )

    def sample_one(self) -> Tuple[float, bool]:
        """Sample one ``(e_value, is_alternative)`` pair."""
        if self.current_idx >= self.n:
            raise StopIteration("All samples have been generated.")
        e_value = self.e_values[self.current_idx]
        label = self.labels[self.current_idx]
        self.current_idx += 1
        return float(e_value), bool(label)

    def sample_batch(
        self, size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample a batch of e-values and labels."""
        if size is None:
            size = self.batch_size or self.n
        if self.current_idx >= self.n:
            raise StopIteration("All samples have been generated.")
        end_idx = min(self.current_idx + size, self.n)
        e_values = self.e_values[self.current_idx : end_idx]
        labels = self.labels[self.current_idx : end_idx]
        self.current_idx = end_idx
        return e_values, labels

    def reset(self) -> None:
        """Reset the generator to the beginning."""
        self.current_idx = 0

    @property
    def remaining(self) -> int:
        """Number of samples remaining."""
        return self.n - self.current_idx
