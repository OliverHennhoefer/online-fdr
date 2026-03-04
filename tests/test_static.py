import random

from online_fdr.utils.static import bh, by, storey_bh

_rng = random.Random(1)
_P_VALUES = [_rng.uniform(0, 1) for _ in range(20)] + [
    _rng.uniform(0, 0.05) for _ in range(3)
]


def test_bh() -> None:
    rejections, threshold = bh(_P_VALUES, alpha=0.05)

    assert rejections == 2
    assert threshold == 0.004347826086956522


def test_storey_bh() -> None:
    rejections, threshold = storey_bh(_P_VALUES, alpha=0.05, lambda_=0.5)

    assert rejections == 2
    assert threshold == 0.0021060533511106927


def test_by() -> None:
    rejections, threshold = by(_P_VALUES, alpha=0.095)

    assert rejections == 2
    assert threshold == 0.0022121651565474923
