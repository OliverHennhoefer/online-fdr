from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any, Protocol

from online_fdr.core.utils.validity import check_nonnegative_weights

__all__ = [
    "BettingEProcess",
    "EProcess",
    "LikelihoodRatioEProcess",
    "MixtureLikelihoodRatioEProcess",
    "stop",
    "value_at_stop",
]


class EProcess(Protocol):
    """Protocol for anytime-valid e-processes."""

    @property
    def current(self) -> float:
        """Current e-value."""
        ...

    def update(self, observation: Any) -> float:
        """Update with one observation and return the current e-value."""
        ...

    def reset(self) -> None:
        """Reset the process to its initial e-value."""
        ...


def _exp_or_inf(log_value: float) -> float:
    if log_value == -math.inf:
        return 0.0
    if log_value == math.inf:
        return math.inf
    try:
        return float(math.exp(log_value))
    except OverflowError:
        return math.inf


def _logsumexp(log_terms: Sequence[float]) -> float:
    if not log_terms:
        raise ValueError("at least one log term is required.")
    max_log = max(log_terms)
    if max_log == -math.inf:
        return -math.inf
    if max_log == math.inf:
        return math.inf
    return float(max_log + math.log(sum(math.exp(term - max_log) for term in log_terms)))


class LikelihoodRatioEProcess:
    """Log-space likelihood-ratio e-process.

    ``log_likelihood_ratio`` must return log ``f_alt(x) / f_null(x)`` for each
    observation. The caller is responsible for the model assumptions that make
    this an e-process under the null.
    """

    def __init__(self, log_likelihood_ratio: Callable[[Any], float]):
        self.log_likelihood_ratio = log_likelihood_ratio
        self.log_current = 0.0

    @property
    def current(self) -> float:
        return _exp_or_inf(self.log_current)

    def update(self, observation: Any) -> float:
        increment = float(self.log_likelihood_ratio(observation))
        if math.isnan(increment):
            raise ValueError("log likelihood ratio must not be NaN.")
        self.log_current += increment
        return self.current

    def reset(self) -> None:
        self.log_current = 0.0


class MixtureLikelihoodRatioEProcess:
    """Fixed-prior mixture of likelihood-ratio e-processes.

    Each component accumulates its own likelihood-ratio process over time. The
    reported value is the weighted arithmetic mixture of those cumulative
    component processes, not a product of per-observation mixture likelihoods.
    The caller is responsible for the null and alternative model assumptions.
    """

    def __init__(
        self,
        log_likelihood_ratios: Sequence[Callable[[Any], float]],
        weights: Sequence[float] | None = None,
    ):
        if not log_likelihood_ratios:
            raise ValueError("at least one likelihood-ratio component is required.")
        self.log_likelihood_ratios = list(log_likelihood_ratios)
        if weights is None:
            self.weights = [1.0 / len(self.log_likelihood_ratios)] * len(
                self.log_likelihood_ratios
            )
        else:
            if len(weights) != len(self.log_likelihood_ratios):
                raise ValueError("weights must match likelihood-ratio components.")
            check_nonnegative_weights(weights)
            total = float(sum(weights))
            self.weights = [float(weight) / total for weight in weights]
        self.component_log_currents = [0.0] * len(self.log_likelihood_ratios)

    @property
    def current(self) -> float:
        return _exp_or_inf(self.log_current)

    @property
    def log_current(self) -> float:
        terms = []
        for weight, component_log_current in zip(
            self.weights, self.component_log_currents
        ):
            if weight == 0:
                terms.append(-math.inf)
            else:
                terms.append(math.log(weight) + component_log_current)
        return _logsumexp(terms)

    def update(self, observation: Any) -> float:
        for idx, (weight, log_lr) in enumerate(
            zip(self.weights, self.log_likelihood_ratios)
        ):
            if weight == 0:
                continue
            value = float(log_lr(observation))
            if math.isnan(value):
                raise ValueError("log likelihood ratio must not be NaN.")
            self.component_log_currents[idx] += value
            if math.isnan(self.component_log_currents[idx]):
                raise ValueError("cumulative log likelihood ratio must not be NaN.")
        return _exp_or_inf(self.log_current)

    def reset(self) -> None:
        self.component_log_currents = [0.0] * len(self.log_likelihood_ratios)


class BettingEProcess:
    """Simple betting e-process from multiplicative betting factors.

    For each score, the factor is ``1 + stake * score``. The caller is
    responsible for using scores and predictable stakes that make the factor
    conditionally expectation-bounded by one under the null.
    """

    def __init__(self, stake: float | Callable[[float], float]):
        self.stake = stake
        self.log_current = 0.0

    @property
    def current(self) -> float:
        return _exp_or_inf(self.log_current)

    def update(self, score: float) -> float:
        stake = self.stake(score) if callable(self.stake) else self.stake
        stake = float(stake)
        score = float(score)
        factor = 1.0 + stake * score
        if not math.isfinite(factor) or factor < 0:
            raise ValueError("betting factor must be finite and nonnegative.")
        if factor == 0:
            self.log_current = -math.inf
        elif self.log_current != -math.inf:
            self.log_current += math.log(factor)
        return self.current

    def reset(self) -> None:
        self.log_current = 0.0


def value_at_stop(process: EProcess) -> float:
    """Return the stopped value of an e-process."""
    return float(process.current)


def stop(process: EProcess) -> float:
    """Alias for ``value_at_stop``."""
    return value_at_stop(process)
