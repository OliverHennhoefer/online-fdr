import random

from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.lord.three import LordThree
from online_fdr.investing.saffron.saffron import Saffron
from online_fdr.spending.online_fallback import OnlineFallback


def _fdp(decisions: list[bool]) -> float:
    rejects = sum(decisions)
    return rejects / max(rejects, 1)


def test_null_stream_fdr_sanity_for_core_methods() -> None:
    alpha = 0.05
    n_runs = 120
    n_tests = 400

    fdr_scores = {
        "saffron": [],
        "addis": [],
        "lord3": [],
    }

    for seed in range(n_runs):
        rng = random.Random(10_000 + seed)
        p_vals = [rng.random() for _ in range(n_tests)]

        methods = {
            "saffron": Saffron(alpha=alpha, wealth=0.025, lambda_=0.5),
            "addis": Addis(alpha=alpha, wealth=0.025, lambda_=0.25, tau=0.5),
            "lord3": LordThree(alpha=alpha, wealth=0.025, reward=0.025),
        }

        for name, method in methods.items():
            decisions = [method.test_one(p) for p in p_vals]
            fdr_scores[name].append(_fdp(decisions))

    for scores in fdr_scores.values():
        assert sum(scores) / len(scores) <= alpha * 1.25


def test_null_stream_fwer_sanity_for_online_fallback() -> None:
    alpha = 0.05
    n_runs = 150
    n_tests = 400

    any_reject_rate = 0
    for seed in range(n_runs):
        rng = random.Random(20_000 + seed)
        p_vals = [rng.random() for _ in range(n_tests)]
        method = OnlineFallback(alpha=alpha)
        any_reject_rate += int(any(method.test_one(p) for p in p_vals))

    empirical_fwer = any_reject_rate / n_runs
    assert empirical_fwer <= alpha * 1.25


def _simulate_saffron_discoveries(pi0: float, seed: int, n: int = 500) -> int:
    rng = random.Random(seed)
    n_null = int(n * pi0)
    p_vals = [rng.random() for _ in range(n_null)] + [
        rng.uniform(0.0, 0.001) for _ in range(n - n_null)
    ]
    rng.shuffle(p_vals)

    method = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)
    return sum(method.test_one(p) for p in p_vals)


def test_power_trend_sanity_with_more_signal() -> None:
    runs = 40
    low_signal = []
    high_signal = []

    for i in range(runs):
        low_signal.append(_simulate_saffron_discoveries(pi0=0.95, seed=30_000 + i))
        high_signal.append(_simulate_saffron_discoveries(pi0=0.80, seed=40_000 + i))

    assert sum(high_signal) / runs > sum(low_signal) / runs
