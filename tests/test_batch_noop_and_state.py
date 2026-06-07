import pytest

from online_fdr.p_values.batching.bh import BatchBH
from online_fdr.p_values.batching.bh_official import BatchBHOfficial
from online_fdr.p_values.batching.by import BatchBY
from online_fdr.p_values.batching.prds import BatchPRDS
from online_fdr.p_values.batching.storey_bh import BatchStoreyBH


def _snapshot_state(method) -> dict:
    tracked = {}
    for key, value in method.__dict__.items():
        if key in {"seq", "poly_seq", "half_seq"}:
            continue
        if isinstance(value, list):
            tracked[key] = list(value)
        else:
            tracked[key] = value
    return tracked


@pytest.mark.parametrize(
    "method",
    [
        BatchBH(alpha=0.05),
        BatchBY(alpha=0.05),
        BatchPRDS(alpha=0.05),
        BatchStoreyBH(alpha=0.05, lambda_=0.5),
        BatchBHOfficial(alpha=0.05),
    ],
)
def test_empty_batch_is_noop(method) -> None:
    before = _snapshot_state(method)
    assert method.test_batch([]) == []
    after = _snapshot_state(method)
    assert after == before


def test_empty_batch_after_non_empty_is_still_noop() -> None:
    method = BatchBH(alpha=0.05)
    method.test_batch([0.01, 0.2, 0.5])
    before = _snapshot_state(method)
    assert method.test_batch([]) == []
    assert _snapshot_state(method) == before
