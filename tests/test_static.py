import random
from itertools import combinations_with_replacement

import pytest

from online_fdr.core.utils.static import _bh_r_plus, bh, by, storey_bh

_rng = random.Random(1)
_P_VALUES = [_rng.uniform(0, 1) for _ in range(20)] + [
    _rng.uniform(0, 0.05) for _ in range(3)
]


def test_bh() -> None:
    rejections, threshold = bh(_P_VALUES, alpha=0.05)

    assert rejections == 2
    assert threshold == 0.004347826086956522


@pytest.mark.parametrize("alpha", [0.0, 0.05, 0.5, 1.5])
def test_bh_r_plus_matches_exhaustive_coordinate_replacement(alpha: float) -> None:
    for size in range(7):
        for values in combinations_with_replacement([0.0, 0.01, 0.05, 0.5, 1.0], size):
            p_vals = list(reversed(values))
            before = p_vals.copy()
            expected = max(
                (
                    bh(p_vals[:idx] + [0.0] + p_vals[idx + 1 :], alpha)[0]
                    for idx in range(size)
                ),
                default=0,
            )
            assert _bh_r_plus(p_vals, alpha) == expected
            assert p_vals == before


def test_storey_bh() -> None:
    rejections, threshold = storey_bh(_P_VALUES, alpha=0.05, lambda_=0.5)

    assert rejections == 2
    assert threshold == 0.0021060533511106927


def test_by() -> None:
    rejections, threshold = by(_P_VALUES, alpha=0.095)

    assert rejections == 2
    assert threshold == 0.0022121651565474923
