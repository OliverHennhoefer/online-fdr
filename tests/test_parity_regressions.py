import random

import pytest

from online_fdr.core.utils.static import bh, by, storey_bh
from online_fdr.p_values.batching.by import BatchBY
from online_fdr.p_values.batching.prds import BatchPRDS
from online_fdr.p_values.batching.storey_bh import BatchStoreyBH
from online_fdr.p_values.investing.addis.addis import Addis
from online_fdr.p_values.investing.lord.discard import LordDiscard
from online_fdr.p_values.naive.naive import NaiveTest
from online_fdr.p_values.spending.alpha_spending import AlphaSpending
from online_fdr.p_values.spending.functions.bonferroni import Bonferroni
from online_fdr.p_values.spending.online_fallback import OnlineFallback


def _bh_k_ground_truth(p_vals: list[float], alpha: float) -> int:
    sorted_p = sorted(p_vals)
    n = len(sorted_p)
    k = 0
    for i, p_val in enumerate(sorted_p, start=1):
        if p_val <= alpha * i / n:
            k = i
    return k


def _by_k_ground_truth(p_vals: list[float], alpha: float) -> int:
    sorted_p = sorted(p_vals)
    n = len(sorted_p)
    harmonic = sum(1 / i for i in range(1, n + 1))
    k = 0
    for i, p_val in enumerate(sorted_p, start=1):
        if p_val <= alpha * i / (n * harmonic):
            k = i
    return k


def _storey_bh_k_ground_truth(p_vals: list[float], alpha: float, lambda_: float) -> int:
    sorted_p = sorted(p_vals)
    n = len(sorted_p)
    num_above_lambda = sum(1 for p in p_vals if p > lambda_)
    pi0 = min(1.0, (1 + num_above_lambda) / (n * (1 - lambda_)))
    k = 0
    for i, p_val in enumerate(sorted_p, start=1):
        if p_val <= (i * alpha) / (n * pi0):
            k = i
    return k


def _storey_bh_r_plus_direct(p_vals: list[float], alpha: float, lambda_: float) -> int:
    best = 0
    for i, p_val in enumerate(p_vals):
        adjusted = list(p_vals)
        adjusted[i] = 0.0
        best = max(best, storey_bh(adjusted, alpha, lambda_)[0])
        adjusted[i] = p_val
    return best


def test_step_up_non_monotone_adversarial_examples() -> None:
    p_vals = [0.02, 0.021, 0.03]

    assert bh(p_vals, alpha=0.03)[0] == 3
    assert by([0.05, 0.08, 0.10], alpha=0.2)[0] == 3
    assert storey_bh(p_vals, alpha=0.03, lambda_=0.5)[0] == 3


def test_step_up_matches_ground_truth_under_fuzzing() -> None:
    rng = random.Random(7)

    for _ in range(200):
        n = rng.randint(3, 40)
        alpha = rng.uniform(0.01, 0.25)
        p_vals = [rng.random() for _ in range(n)]

        assert bh(p_vals, alpha=alpha)[0] == _bh_k_ground_truth(p_vals, alpha)
        assert by(p_vals, alpha=alpha)[0] == _by_k_ground_truth(p_vals, alpha)
        assert storey_bh(p_vals, alpha=alpha, lambda_=0.5)[
            0
        ] == _storey_bh_k_ground_truth(p_vals, alpha, 0.5)


def test_alpha_spending_rejects_on_boundary() -> None:
    method = AlphaSpending(alpha=0.05, spend_func=Bonferroni(k=1))
    assert method.test_one(0.05) is True


def test_naive_rejects_on_boundary() -> None:
    method = NaiveTest(alpha=0.05)

    assert method.test_one(0.05) is True
    assert method.num_hypotheses == 1


def test_alpha_spending_finite_horizon_raises_cleanly() -> None:
    method = AlphaSpending(alpha=0.05, spend_func=Bonferroni(k=1))
    method.test_one(0.01)
    with pytest.raises(ValueError):
        method.test_one(0.01)


def test_online_fallback_rejects_on_boundary() -> None:
    method = OnlineFallback(alpha=0.05)
    first_alpha = method.alpha0 * method.seq.calc_gamma(1)
    assert method.test_one(first_alpha) is True


@pytest.mark.parametrize("tau", [0.0, -0.1, 1.0, 1.2])
def test_addis_rejects_invalid_tau(tau: float) -> None:
    with pytest.raises(ValueError):
        Addis(alpha=0.05, wealth=0.025, lambda_=0.2, tau=tau)


@pytest.mark.parametrize("lambda_", [-0.1, 0.5, 0.7])
def test_addis_rejects_invalid_lambda_relation(lambda_: float) -> None:
    with pytest.raises(ValueError):
        Addis(alpha=0.05, wealth=0.025, lambda_=lambda_, tau=0.5)


def test_d_lord_first_reject_only_set_on_discovery() -> None:
    method = LordDiscard(alpha=0.05, wealth=0.025, tau=0.5)

    assert method.test_one(0.4) is False
    assert method.first_reject is None

    assert method.test_one(1e-12) is True
    assert method.first_reject == 2


def test_lord_discard_counts_processed_and_selected_inputs() -> None:
    method = LordDiscard(alpha=0.05, wealth=0.025, tau=0.5)

    assert method.test_one(0.8) is False
    assert method.num_hypotheses == 1
    assert method.num_hypotheses == 1
    assert method.num_selected == 0

    method.test_one(0.4)
    assert method.num_hypotheses == 2
    assert method.num_hypotheses == 2
    assert method.num_selected == 1


@pytest.mark.parametrize(
    "method",
    [
        BatchBY(alpha=0.05),
        BatchPRDS(alpha=0.05),
        BatchStoreyBH(alpha=0.05, lambda_=0.5),
    ],
)
def test_batch_methods_count_hypotheses_and_batches_explicitly(
    method,
) -> None:
    assert method.num_hypotheses == 0
    assert method.num_hypotheses == 0
    assert method.num_batches == 0

    method.test_batch([0.5, 0.8])
    assert method.num_hypotheses == 2
    assert method.num_hypotheses == 2
    assert method.num_batches == 1

    assert method.test_batch([]) == []
    assert method.num_hypotheses == 2
    assert method.num_hypotheses == 2
    assert method.num_batches == 1


def test_batch_storey_bh_r_plus_matches_direct_definition() -> None:
    rng = random.Random(11)
    method = BatchStoreyBH(alpha=0.05, lambda_=0.5)

    for _ in range(100):
        p_vals = [rng.random() for _ in range(rng.randint(2, 30))]
        alpha_batch = rng.uniform(1e-4, 0.2)
        assert method._calculate_r_plus(
            p_vals, alpha_batch
        ) == _storey_bh_r_plus_direct(p_vals, alpha_batch, method.lambda_)
