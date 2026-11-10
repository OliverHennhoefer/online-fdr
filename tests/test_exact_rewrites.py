"""Faster code paths must give the results of the plain definitions they replace."""

import json
import math
import random

import numpy as np
import pytest

from online_fdr.core.utils.generation import (
    ChiSquaredModel,
    DependentGaussianModel,
    GaussianLocationModel,
    SparseGaussianModel,
)
from online_fdr.core.utils.sequence import (
    BatchGammaSequenceSmall,
    DefaultLordGammaSequence,
    DefaultSaffronGammaSequence,
)
from online_fdr.e_values.sequential import ELond
from online_fdr.p_values.batching.storey_bh import BatchStoreyBH
from online_fdr.p_values.investing.lond.lond import Lond
from online_fdr.p_values.investing.lord.mem_decay import LORDMemoryDecay


def _stream(seed: int, n: int) -> list[float]:
    rng = random.Random(seed)
    return [rng.random() ** rng.choice([1, 4, 12]) for _ in range(n)]


def test_storey_r_plus_matches_exhaustive_coordinate_replacement() -> None:
    rng = random.Random(11)
    for _ in range(1500):
        lambda_ = rng.choice([0.05, 0.25, 0.5, 0.9])
        method = BatchStoreyBH(alpha=0.05, lambda_=lambda_)
        grid = [0.0, 0.001, 0.01, lambda_ / 2, lambda_, 0.5, 1.0]
        p_vals = [
            rng.choice(grid) if rng.random() < 0.4 else rng.random() ** 3
            for _ in range(rng.randint(1, 12))
        ]
        level = rng.choice([1e-4, 0.003, 0.02, 0.05, 0.2, 0.7])

        exhaustive = max(
            sum(
                method._storey_batch_decisions(
                    p_vals[:i] + p_vals[i + 1 :] + [0.0], level
                )[0]
            )
            for i in range(len(p_vals))
        )

        assert method._calculate_r_plus(p_vals, level) == exhaustive


@pytest.mark.parametrize("original", [True, False])
def test_dependent_lond_divides_by_the_harmonic_number(original: bool) -> None:
    method = Lond(alpha=0.05, original=original, dependent=True)
    plain = Lond(alpha=0.05, original=original)

    for index, p_val in enumerate(_stream(seed=5, n=400), start=1):
        # Keep both on the same rejection count, which scales the level.
        plain.num_reject = method.num_reject
        plain.test_one(p_val)
        method.test_one(p_val)
        harmonic = math.fsum(1 / i for i in range(1, index + 1))

        assert method.last_test_level == pytest.approx(
            plain.last_test_level / harmonic, rel=1e-14
        )


def test_dependent_lond_resumes_its_harmonic_sum_from_a_snapshot() -> None:
    method = Lond(alpha=0.05, dependent=True)
    stream = _stream(seed=6, n=120)
    for p_val in stream[:60]:
        method.test_one(p_val)

    restored = Lond.from_snapshot(json.loads(json.dumps(method.snapshot())))

    for p_val in stream[60:]:
        assert restored.test_one(p_val) == method.test_one(p_val)
        assert restored.last_test_level == method.last_test_level


def _memory_decay_levels(
    alpha: float, delta: float, eta: float, lag: int, p_vals: list[float]
) -> list[float]:
    """The published rule, summed over every past rejection."""
    seq = DefaultLordGammaSequence(c=0.07720838)
    rejections: list[int] = []
    levels = []
    for index, p_val in enumerate(p_vals, start=1):
        level = alpha * eta * max(seq.calc_gamma(index), 1 - delta)
        for rejected_at in rejections:
            since = index - rejected_at - lag
            if since > 0:
                level += alpha * delta**since * seq.calc_gamma(since)
        levels.append(level)
        if p_val <= level:
            rejections.append(index)
    return levels


@pytest.mark.parametrize(
    ("delta", "eta", "lag"), [(0.99, 0.5, 0), (0.9, 1.0, 3), (0.2, 0.5, 0)]
)
def test_memory_decay_matches_the_sum_over_all_rejections(
    delta: float, eta: float, lag: int
) -> None:
    p_vals = _stream(seed=8, n=1500)
    method = LORDMemoryDecay(alpha=0.1, delta=delta, eta=eta, l=lag)

    levels = []
    for p_val in p_vals:
        method.test_one(p_val)
        levels.append(method.last_test_level)

    assert levels == _memory_decay_levels(0.1, delta, eta, lag, p_vals)


def test_memory_decay_stops_visiting_rejections_whose_weight_is_zero() -> None:
    # 0.2 ** 463 is the first power that underflows to exactly zero.
    method = LORDMemoryDecay(alpha=0.1, delta=0.2)
    for p_val in [0.0] * 5 + [1.0] * 600:
        method.test_one(p_val)

    assert method.rejection_times == [1, 2, 3, 4, 5]
    assert method._first_active == 5
    assert max(method._gamma_cache) < 463


def test_memory_decay_snapshot_leaves_out_the_gamma_cache() -> None:
    p_vals = _stream(seed=9, n=300)
    method = LORDMemoryDecay(alpha=0.1)
    for p_val in p_vals[:200]:
        method.test_one(p_val)

    snapshot = method.snapshot()
    assert "_gamma_cache" not in snapshot["state"]

    restored = LORDMemoryDecay.from_snapshot(json.loads(json.dumps(snapshot)))
    for p_val in p_vals[200:]:
        assert restored.test_one(p_val) == method.test_one(p_val)
        assert restored.last_test_level == method.last_test_level


def test_autoregressive_correlation_matches_the_elementwise_definition() -> None:
    model = DependentGaussianModel(correlation=0.37, structure="autoregressive")

    matrix = model._create_correlation_matrix(41)

    expected = [[0.37 ** abs(i - j) for j in range(41)] for i in range(41)]
    assert matrix.tolist() == expected
    assert model._create_correlation_matrix(0).shape == (0, 0)


def test_block_correlation_covers_a_trailing_partial_block() -> None:
    model = DependentGaussianModel(correlation=0.4, structure="block", block_size=3)

    matrix = model._create_correlation_matrix(8)

    block_of = [0, 0, 0, 1, 1, 1, 2, 2]
    expected = [
        [
            1.0 if i == j else (0.4 if block_of[i] == block_of[j] else 0.0)
            for j in range(8)
        ]
        for i in range(8)
    ]
    assert matrix.tolist() == expected


@pytest.mark.parametrize(
    "model",
    [
        GaussianLocationModel(alt_mean=12.0, seed=2),
        GaussianLocationModel(alt_mean=12.0, one_sided=False, seed=2),
        SparseGaussianModel(min_effect=12.0, max_effect=12.0, seed=2),
        DependentGaussianModel(alt_mean=12.0, correlation=0.0, seed=2),
        ChiSquaredModel(df=1, alt_scale=60.0, seed=2),
    ],
    ids=["gaussian", "two-sided", "sparse", "dependent", "chi-squared"],
)
def test_generators_keep_extreme_p_values_above_zero(model) -> None:
    null, alternative = model.generate_pvalues(50, 200)

    assert np.all(alternative > 0)
    assert np.min(alternative) < 1e-17  # below what 1 - cdf can represent
    assert np.all((null >= 0) & (null <= 1))


def test_batch_small_gamma_reuses_its_normalizer_per_batch_size() -> None:
    seq = BatchGammaSequenceSmall(gamma_exp=1.6)

    for batch_size in (1, 7, 50, 7):
        normalizer = 1.0 / sum(s**-1.6 for s in range(1, batch_size + 1))
        for j in (1, 2, 9):
            assert seq.calc_gamma(j, batch_size=batch_size) == normalizer * j**-1.6


def test_elond_accepts_a_sequence_that_ignores_alpha() -> None:
    seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
    method = ELond(alpha=0.1, gamma_seq=seq)

    assert method.test_one(1000.0) is True
    assert method.last_test_level == 0.1 * seq.calc_gamma(1)


def test_elond_does_not_hide_a_type_error_raised_by_the_sequence() -> None:
    class Broken(DefaultSaffronGammaSequence):
        def calc_gamma(self, j: int, *args: object, **kwargs: object) -> float:
            raise TypeError("broken sequence")

    method = ELond(alpha=0.1, gamma_seq=Broken(gamma_exp=1.6, c=0.4374901658))
    with pytest.raises(TypeError, match="broken sequence"):
        method.test_one(10.0)
