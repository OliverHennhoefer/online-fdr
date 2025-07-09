"""
Improved data generation utilities for online FDR control simulations.

This module provides various data generating processes commonly used in the
FDR control literature, including support for dependent p-values and 
different alternative distributions.
"""

import abc
import math
import random
import numpy as np
from typing import Tuple, List, Optional, Union
from scipy import stats


class DataGeneratingProcess(abc.ABC):
    """Abstract base class for data generating processes."""

    def __init__(self, seed: int = 1):
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    @abc.abstractmethod
    def generate_pvalues(
        self, n_null: int, n_alt: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate p-values under null and alternative hypotheses.

        Returns:
            Tuple of (null_pvalues, alt_pvalues)
        """
        raise NotImplementedError

    def generate_mixed(self, n: int, pi0: float) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a mixture of null and alternative p-values.

        Args:
            n: Total number of p-values
            pi0: Proportion of true nulls

        Returns:
            Tuple of (p_values, labels) where labels are True for alternatives
        """
        n_null = int(n * pi0)
        n_alt = n - n_null

        null_pvals, alt_pvals = self.generate_pvalues(n_null, n_alt)

        # Combine and shuffle
        pvals = np.concatenate([null_pvals, alt_pvals])
        labels = np.concatenate([np.zeros(n_null), np.ones(n_alt)]).astype(bool)

        # Shuffle together
        indices = self.rng.permutation(n)
        return pvals[indices], labels[indices]


class GaussianLocationModel(DataGeneratingProcess):
    """
    Gaussian location model: Z ~ N(0,1) under null, Z ~ N(μ,σ²) under alternative.

    This is the most common model in power analysis studies.
    """

    def __init__(
        self,
        alt_mean: float = 3.0,
        alt_std: float = 1.0,
        one_sided: bool = True,
        seed: int = 1,
    ):
        super().__init__(seed)
        self.alt_mean = alt_mean
        self.alt_std = alt_std
        self.one_sided = one_sided

    def generate_pvalues(
        self, n_null: int, n_alt: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        # Null: standard normal
        z_null = self.rng.randn(n_null)

        # Alternative: shifted normal
        z_alt = self.rng.randn(n_alt) * self.alt_std + self.alt_mean

        # Convert to p-values
        if self.one_sided:
            p_null = 1 - stats.norm.cdf(z_null)  # Upper tail
            p_alt = 1 - stats.norm.cdf(z_alt)
        else:
            p_null = 2 * (1 - stats.norm.cdf(np.abs(z_null)))
            p_alt = 2 * (1 - stats.norm.cdf(np.abs(z_alt)))

        return p_null, p_alt


class BetaMixtureModel(DataGeneratingProcess):
    """
    Beta mixture model commonly used in genomics applications.

    Under null: p ~ Uniform(0,1) = Beta(1,1)
    Under alternative: p ~ Beta(α, β) with α < 1 to concentrate near 0
    """

    def __init__(self, alt_alpha: float = 0.5, alt_beta: float = 10.0, seed: int = 1):
        super().__init__(seed)
        self.alt_alpha = alt_alpha
        self.alt_beta = alt_beta

    def generate_pvalues(
        self, n_null: int, n_alt: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        # Null: uniform
        p_null = self.rng.uniform(0, 1, n_null)

        # Alternative: beta distributed
        p_alt = self.rng.beta(self.alt_alpha, self.alt_beta, n_alt)

        return p_null, p_alt


class ChiSquaredModel(DataGeneratingProcess):
    """
    Chi-squared model for testing variance or goodness-of-fit.

    Under null: test statistic ~ χ²(df)
    Under alternative: test statistic ~ λ·χ²(df) (scaled chi-squared)
    """

    def __init__(self, df: int = 1, alt_scale: float = 3.0, seed: int = 1):
        super().__init__(seed)
        self.df = df
        self.alt_scale = alt_scale

    def generate_pvalues(
        self, n_null: int, n_alt: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        # Null: standard chi-squared
        chi2_null = self.rng.chisquare(self.df, n_null)
        p_null = 1 - stats.chi2.cdf(chi2_null, self.df)

        # Alternative: scaled chi-squared
        chi2_alt = self.alt_scale * self.rng.chisquare(self.df, n_alt)
        p_alt = 1 - stats.chi2.cdf(chi2_alt, self.df)

        return p_null, p_alt


class DependentGaussianModel(DataGeneratingProcess):
    """
    Gaussian model with dependence structure.

    Supports various correlation structures commonly used in FDR literature.
    """

    def __init__(
        self,
        alt_mean: float = 3.0,
        correlation: float = 0.5,
        structure: str = "equicorrelated",
        block_size: int = 10,
        one_sided: bool = True,
        seed: int = 1,
    ):
        super().__init__(seed)
        self.alt_mean = alt_mean
        self.correlation = correlation
        self.structure = structure
        self.block_size = block_size
        self.one_sided = one_sided

    def _create_correlation_matrix(self, n: int) -> np.ndarray:
        """Create correlation matrix based on specified structure."""
        if self.structure == "equicorrelated":
            # All pairs have same correlation
            Sigma = np.full((n, n), self.correlation)
            np.fill_diagonal(Sigma, 1.0)

        elif self.structure == "block":
            # Block diagonal structure
            Sigma = np.eye(n)
            n_blocks = n // self.block_size
            for i in range(n_blocks):
                start = i * self.block_size
                end = min((i + 1) * self.block_size, n)
                Sigma[start:end, start:end] = self.correlation
                np.fill_diagonal(Sigma[start:end, start:end], 1.0)

        elif self.structure == "autoregressive":
            # AR(1) structure: corr(i,j) = ρ^|i-j|
            Sigma = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    Sigma[i, j] = self.correlation ** abs(i - j)

        else:
            raise ValueError(f"Unknown correlation structure: {self.structure}")

        return Sigma

    def generate_pvalues(
        self, n_null: int, n_alt: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        # Generate correlated null statistics
        if n_null > 0:
            Sigma_null = self._create_correlation_matrix(n_null)
            z_null = self.rng.multivariate_normal(np.zeros(n_null), Sigma_null)
            p_null = (
                1 - stats.norm.cdf(z_null)
                if self.one_sided
                else 2 * (1 - stats.norm.cdf(np.abs(z_null)))
            )
        else:
            p_null = np.array([])

        # Generate correlated alternative statistics
        if n_alt > 0:
            Sigma_alt = self._create_correlation_matrix(n_alt)
            mean_alt = np.full(n_alt, self.alt_mean)
            z_alt = self.rng.multivariate_normal(mean_alt, Sigma_alt)
            p_alt = (
                1 - stats.norm.cdf(z_alt)
                if self.one_sided
                else 2 * (1 - stats.norm.cdf(np.abs(z_alt)))
            )
        else:
            p_alt = np.array([])

        return p_null, p_alt


class SparseGaussianModel(DataGeneratingProcess):
    """
    Sparse signal model where only a few alternatives have large effects.

    Common in screening applications and high-dimensional statistics.
    """

    def __init__(
        self,
        effect_dist: str = "constant",
        min_effect: float = 2.0,
        max_effect: float = 5.0,
        one_sided: bool = True,
        seed: int = 1,
    ):
        super().__init__(seed)
        self.effect_dist = effect_dist
        self.min_effect = min_effect
        self.max_effect = max_effect
        self.one_sided = one_sided

    def generate_pvalues(
        self, n_null: int, n_alt: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        # Null: standard normal
        z_null = self.rng.randn(n_null)
        p_null = (
            1 - stats.norm.cdf(z_null)
            if self.one_sided
            else 2 * (1 - stats.norm.cdf(np.abs(z_null)))
        )

        # Alternative: varying effect sizes
        if self.effect_dist == "constant":
            effects = np.full(n_alt, self.min_effect)
        elif self.effect_dist == "uniform":
            effects = self.rng.uniform(self.min_effect, self.max_effect, n_alt)
        elif self.effect_dist == "exponential":
            # Exponentially decaying effect sizes
            effects = (
                self.min_effect
                + (self.max_effect - self.min_effect)
                * self.rng.exponential(1.0, n_alt)
                / 3.0
            )
            effects = np.clip(effects, self.min_effect, self.max_effect)
        else:
            raise ValueError(f"Unknown effect distribution: {self.effect_dist}")

        z_alt = self.rng.randn(n_alt) + effects
        p_alt = (
            1 - stats.norm.cdf(z_alt)
            if self.one_sided
            else 2 * (1 - stats.norm.cdf(np.abs(z_alt)))
        )

        return p_null, p_alt


class DataGenerator:
    """
    Improved data generator with support for batch generation and various models.
    """

    def __init__(
        self,
        n: int,
        pi0: float,
        dgp: DataGeneratingProcess,
        batch_size: Optional[int] = None,
    ):
        """
        Args:
            n: Total number of hypotheses
            pi0: Proportion of true null hypotheses
            dgp: Data generating process
            batch_size: If specified, generate in batches
        """
        self.n = n
        self.pi0 = pi0
        self.dgp = dgp
        self.batch_size = batch_size

        # Pre-generate all data for consistency
        self.pvalues, self.labels = dgp.generate_mixed(n, pi0)
        self.current_idx = 0

    def sample_one(self) -> Tuple[float, bool]:
        """Sample one p-value (backward compatibility)."""
        if self.current_idx >= self.n:
            raise StopIteration("All samples have been generated.")

        p_val = self.pvalues[self.current_idx]
        label = self.labels[self.current_idx]
        self.current_idx += 1

        return p_val, label

    def sample_batch(self, size: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Sample a batch of p-values."""
        if size is None:
            size = self.batch_size or self.n

        if self.current_idx >= self.n:
            raise StopIteration("All samples have been generated.")

        end_idx = min(self.current_idx + size, self.n)
        p_vals = self.pvalues[self.current_idx : end_idx]
        labels = self.labels[self.current_idx : end_idx]
        self.current_idx = end_idx

        return p_vals, labels

    def reset(self):
        """Reset the generator to start from beginning."""
        self.current_idx = 0

    @property
    def remaining(self) -> int:
        """Number of samples remaining."""
        return self.n - self.current_idx


# Convenience functions for common scenarios
def create_genomics_generator(
    n: int = 10000, pi0: float = 0.9, seed: int = 1
) -> DataGenerator:
    """Create generator mimicking genomics data (many nulls, beta alternatives)."""
    dgp = BetaMixtureModel(alt_alpha=0.5, alt_beta=10.0, seed=seed)
    return DataGenerator(n, pi0, dgp)


def create_screening_generator(
    n: int = 1000,
    pi0: float = 0.95,
    min_effect: float = 2.0,
    max_effect: float = 5.0,
    seed: int = 1,
) -> DataGenerator:
    """Create generator for screening studies (sparse signals)."""
    dgp = SparseGaussianModel(
        effect_dist="exponential",
        min_effect=min_effect,
        max_effect=max_effect,
        seed=seed,
    )
    return DataGenerator(n, pi0, dgp)


def create_dependent_generator(
    n: int = 500,
    pi0: float = 0.8,
    correlation: float = 0.5,
    structure: str = "block",
    seed: int = 1,
) -> DataGenerator:
    """Create generator with dependent p-values."""
    dgp = DependentGaussianModel(
        alt_mean=3.0, correlation=correlation, structure=structure, seed=seed
    )
    return DataGenerator(n, pi0, dgp)
