import random

from online_fdr.core.utils.static import by
from online_fdr.p_values.batching.by import BatchBY


def _stream_with_signals(
    n: int, signal_share: float, max_batch_size: int, seed: int
) -> tuple[list[float], list[int]]:
    """Uniform p-values with a share of near-zero ones, cut into random batches."""
    random.seed(seed)

    p_vals = [random.uniform(0, 1) for _ in range(n)]
    for i in range(int(n * signal_share)):
        p_vals[i] = random.uniform(0, 0.00005)

    batch_sizes = []
    remaining = n
    while remaining > 0:
        batch_size = min(remaining, random.randint(1, max_batch_size))
        batch_sizes.append(batch_size)
        remaining -= batch_size

    random.shuffle(p_vals)
    return p_vals, batch_sizes


def test_batch_by_first_batch_uses_static_by_at_allocated_alpha() -> None:
    method = BatchBY(alpha=0.05)
    p_vals = [0.001, 0.01, 0.04, 0.2, 0.9]
    alpha_t = method.alpha0 * method.seq.calc_gamma(j=1)
    _, threshold = by(p_vals, alpha_t)

    assert method.test_batch(p_vals) == [p_val <= threshold for p_val in p_vals]
    assert method.alpha_s == [alpha_t]


def test_batch_by_large() -> None:
    """Methods in this suite are derivations without a reference implementation."""
    batch_bh = BatchBY(alpha=0.05)

    p_vals, batch_sizes = _stream_with_signals(
        n=1_000, signal_share=0.025, max_batch_size=15, seed=1
    )

    decision = []
    start_index = 0
    for batch_size in batch_sizes:
        end_index = start_index + batch_size
        batch = p_vals[start_index:end_index]
        start_index = end_index

        decision += batch_bh.test_batch(batch)

    assert sum(decision) == 9

    alpha = [round(i, 6) for i in batch_bh.alpha_s]

    n, d = float.as_integer_ratio(sum(alpha))
    assert n == 7487468567684073
    assert d == 18014398509481984
