import math
from fractions import Fraction

import numpy as np
import pytest

from online_fdr.core.utils.sequence import DefaultLondGammaSequence
from online_fdr.core.utils.validity import (
    check_e_value,
    check_p_val,
    check_p_vals_batch,
)
from online_fdr.p_values.batching.bh import BatchBH
from online_fdr.p_values.batching.bh_official import BatchBHOfficial
from online_fdr.p_values.batching.by import BatchBY
from online_fdr.p_values.batching.prds import BatchPRDS
from online_fdr.p_values.batching.storey_bh import BatchStoreyBH
from online_fdr.p_values.investing.lord.dependent import LordDependent
from online_fdr.p_values.investing.lord.discard import LordDiscard
from online_fdr.p_values.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.p_values.investing.lord.plus_plus import LordPlusPlus
from online_fdr.p_values.investing.lord.three import LordThree


@pytest.mark.parametrize(
    ("factory", "invalid_batch"),
    [
        (lambda: BatchBH(alpha=0.05), [0.1, math.nan]),
        (lambda: BatchBY(alpha=0.05), [0.1, math.inf]),
        (lambda: BatchPRDS(alpha=0.05), [0.1, -0.01]),
        (lambda: BatchStoreyBH(alpha=0.05, lambda_=0.5), [0.1, 1.01]),
        (lambda: BatchBHOfficial(alpha=0.05), [0.1, "x"]),
    ],
)
def test_batch_methods_reject_invalid_p_values(factory, invalid_batch) -> None:
    method = factory()
    with pytest.raises(ValueError):
        method.test_batch(invalid_batch)


@pytest.mark.parametrize("invalid_p_val", ["x", math.inf, math.nan])
def test_single_p_value_validation_rejects_invalid_values(invalid_p_val) -> None:
    with pytest.raises(ValueError):
        check_p_val(invalid_p_val)


@pytest.mark.parametrize("tau", [0.0, -0.1, 1.0, 1.1])
def test_lord_discard_rejects_invalid_tau(tau: float) -> None:
    with pytest.raises(ValueError):
        LordDiscard(alpha=0.05, wealth=0.025, tau=tau)


@pytest.mark.parametrize("reward", [0.0, -0.001, 0.04])
def test_lord_three_rejects_invalid_reward_budget(reward: float) -> None:
    with pytest.raises(ValueError):
        LordThree(alpha=0.05, wealth=0.02, reward=reward)


@pytest.mark.parametrize("reward", [0.0, -0.001, 0.04])
def test_lord_dependent_rejects_invalid_reward_budget(reward: float) -> None:
    with pytest.raises(ValueError):
        LordDependent(alpha=0.05, wealth=0.02, reward=reward)


def test_lord_plus_plus_rejects_non_guaranteed_reward() -> None:
    with pytest.raises(ValueError):
        LordPlusPlus(alpha=0.05, wealth=0.025, reward=0.01)


def test_lord_plus_plus_allows_default_and_alpha_reward() -> None:
    LordPlusPlus(alpha=0.05, wealth=0.025)
    LordPlusPlus(alpha=0.05, wealth=0.025, reward=0.05)


@pytest.mark.parametrize(
    "p_val", [np.float32(0.25), np.float64(0.25), np.int64(1), Fraction(1, 4)]
)
def test_p_value_checks_accept_any_real_scalar(p_val) -> None:
    check_p_val(p_val)
    check_p_vals_batch([p_val])
    check_e_value(p_val)
    assert BatchBH(alpha=0.05).test_batch([p_val]) == [False]


@pytest.mark.parametrize("flag", [True, False, np.True_])
def test_p_value_checks_refuse_booleans(flag) -> None:
    with pytest.raises(ValueError):
        check_p_val(flag)
    with pytest.raises(ValueError):
        check_p_vals_batch([0.5, flag])
    with pytest.raises(ValueError):
        check_e_value(flag)


def test_lond_gamma_sequence_accepts_a_numpy_alpha() -> None:
    seq = DefaultLondGammaSequence(c=0.07720838)
    assert seq.calc_gamma(3, alpha=np.float32(0.5)) == seq.calc_gamma(3, alpha=0.5)
    with pytest.raises(ValueError):
        seq.calc_gamma(3, alpha=True)


@pytest.mark.parametrize("lag", [-1, 1.5, True, "2"])
def test_lord_memory_decay_refuses_an_invalid_lag(lag) -> None:
    with pytest.raises(ValueError, match="l must be"):
        LORDMemoryDecay(alpha=0.05, l=lag)
