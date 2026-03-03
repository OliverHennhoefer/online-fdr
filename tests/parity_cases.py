from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache

_BOUNDARY_VALUES = (
    0.0,
    1e-16,
    1e-12,
    1e-8,
    1e-4,
    0.249999999999,
    0.25,
    0.250000000001,
    0.499999999999,
    0.5,
    0.500000000001,
    0.999999999999,
    1.0,
)


@dataclass(frozen=True)
class SequentialParityCase:
    name: str
    p_values: list[float]


@dataclass(frozen=True)
class BatchParityCase:
    name: str
    p_values: list[float]
    batch_sizes: list[int]

    @property
    def batch_ids(self) -> list[int]:
        ids: list[int] = []
        for idx, batch_size in enumerate(self.batch_sizes, start=1):
            ids.extend([idx] * batch_size)
        return ids


def _inject_boundaries(values: list[float], seed: int) -> None:
    rng = random.Random(seed)
    positions = list(range(len(values)))
    rng.shuffle(positions)
    for boundary, pos in zip(_BOUNDARY_VALUES, positions):
        values[pos] = boundary


def _make_stream(n: int, seed: int, signal_fraction: float, signal_max: float) -> list[float]:
    rng = random.Random(seed)
    p_values = [rng.random() for _ in range(n)]

    num_signals = max(1, int(n * signal_fraction))
    for i in range(num_signals):
        p_values[i] = rng.uniform(0.0, signal_max)

    rng.shuffle(p_values)
    _inject_boundaries(p_values, seed + 10_000)
    return p_values


def _make_batch_sizes(n: int, seed: int, min_size: int, max_size: int) -> list[int]:
    rng = random.Random(seed)
    sizes: list[int] = []
    remaining = n
    while remaining > 0:
        size = min(remaining, rng.randint(min_size, max_size))
        sizes.append(size)
        remaining -= size
    return sizes


@lru_cache(maxsize=1)
def sequential_cases() -> dict[str, SequentialParityCase]:
    n = 1_200

    mixed = _make_stream(
        n=n,
        seed=101,
        signal_fraction=0.12,
        signal_max=5e-4,
    )
    null_heavy = _make_stream(
        n=n,
        seed=202,
        signal_fraction=0.02,
        signal_max=2e-5,
    )
    boundary = _make_stream(
        n=n,
        seed=303,
        signal_fraction=0.06,
        signal_max=2e-4,
    )
    for idx in range(0, n, 31):
        boundary[idx] = _BOUNDARY_VALUES[(idx // 31) % len(_BOUNDARY_VALUES)]

    return {
        "seq_long_mixed_v1": SequentialParityCase(
            name="seq_long_mixed_v1",
            p_values=mixed,
        ),
        "seq_long_null_v1": SequentialParityCase(
            name="seq_long_null_v1",
            p_values=null_heavy,
        ),
        "seq_boundary_stress_v1": SequentialParityCase(
            name="seq_boundary_stress_v1",
            p_values=boundary,
        ),
    }


@lru_cache(maxsize=1)
def batch_cases() -> dict[str, BatchParityCase]:
    n = 2_500

    mixed = _make_stream(
        n=n,
        seed=501,
        signal_fraction=0.10,
        signal_max=6e-4,
    )
    sparse = _make_stream(
        n=n,
        seed=601,
        signal_fraction=0.03,
        signal_max=3e-5,
    )

    return {
        "batch_long_mixed_v1": BatchParityCase(
            name="batch_long_mixed_v1",
            p_values=mixed,
            batch_sizes=_make_batch_sizes(n=n, seed=701, min_size=1, max_size=35),
        ),
        "batch_long_sparse_v1": BatchParityCase(
            name="batch_long_sparse_v1",
            p_values=sparse,
            batch_sizes=_make_batch_sizes(n=n, seed=801, min_size=2, max_size=45),
        ),
    }
