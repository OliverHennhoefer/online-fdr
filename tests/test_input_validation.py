import math

import pytest

from online_fdr.batching.bh import BatchBH
from online_fdr.batching.bh_official import BatchBHOfficial
from online_fdr.batching.by import BatchBY
from online_fdr.batching.prds import BatchPRDS
from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.investing.lord.dependent import LordDependent
from online_fdr.investing.lord.discard import LordDiscard
from online_fdr.investing.lord.plus_plus import LordPlusPlus
from online_fdr.investing.lord.three import LordThree


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
