import pytest

from online_fdr.utils.sequence import (
    BatchGammaSequenceSmall,
    DefaultLordGammaSequence,
    DefaultSaffronGammaSequence,
)


def test_default_saffron_requires_finite_c() -> None:
    with pytest.raises(ValueError):
        DefaultSaffronGammaSequence(gamma_exp=1.6, c=None)


def test_default_saffron_requires_summable_exponent() -> None:
    with pytest.raises(ValueError):
        DefaultSaffronGammaSequence(gamma_exp=1.0, c=0.4)


def test_default_saffron_sequence_invariants() -> None:
    seq = DefaultSaffronGammaSequence(gamma_exp=1.6, c=0.4374901658)
    vals = [seq.calc_gamma(i) for i in range(1, 5000)]

    assert all(v >= 0 for v in vals)
    assert all(a >= b for a, b in zip(vals, vals[1:]))
    assert sum(vals) < 1.0


def test_default_lord_sequence_invariants() -> None:
    seq = DefaultLordGammaSequence(c=0.07720838)
    vals = [seq.calc_gamma(i) for i in range(1, 5000)]

    assert all(v >= 0 for v in vals)
    assert all(a >= b for a, b in zip(vals, vals[1:]))
    assert sum(vals) < 1.0


def test_batch_small_gamma_requires_summable_exponent() -> None:
    seq = BatchGammaSequenceSmall(gamma_exp=1.0)
    with pytest.raises(ValueError):
        seq.calc_gamma(1, batch_size=10)


def test_batch_small_gamma_is_positive_and_decreasing() -> None:
    seq = BatchGammaSequenceSmall(gamma_exp=1.6)
    vals = [seq.calc_gamma(i, batch_size=50) for i in range(1, 50)]

    assert all(v >= 0 for v in vals)
    assert all(a >= b for a, b in zip(vals, vals[1:]))
