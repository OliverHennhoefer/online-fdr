"""Static consumers of the public protocols and concrete keyword APIs."""

from online_fdr.core import BatchDecision, BatchTest, SequentialTest, TestDecision
from online_fdr.e_values import EBH, ELond
from online_fdr.p_values import (
    Addis,
    AddisAsync,
    AlphaSpending,
    BatchBH,
    BatchBHOfficial,
    BatchBY,
    BatchPRDS,
    BatchStoreyBH,
    Gai,
    Lond,
    LordDependent,
    LordDiscard,
    LORDMemoryDecay,
    LordPlusPlus,
    LordThree,
    NaiveTest,
    OnlineFallback,
    Saffron,
    SaffronAsync,
    WeightedGaiPlusPlus,
)


def process_one(method: SequentialTest, value: float) -> bool:
    return method.test_one(value)


def describe_one(method: SequentialTest, value: float) -> TestDecision:
    return method.test_one_detail(value)


def process_batch(method: BatchTest, values: tuple[float, ...]) -> list[bool]:
    return method.test_batch(values)


def describe_batch(method: BatchTest, values: tuple[float, ...]) -> BatchDecision:
    return method.test_batch_detail(values)


def observe_state(
    method: SequentialTest | BatchTest,
) -> tuple[float, str, float | None, float | None, int]:
    return (
        method.target_level,
        method.error_rate,
        method.last_test_level,
        method.last_rejection_threshold,
        method.num_hypotheses,
    )


def observe_batches(method: BatchTest) -> int:
    return method.num_batches


def sequential_implementations(
    addis: Addis,
    addis_async: AddisAsync,
    spending: AlphaSpending,
    gai: Gai,
    lond: Lond,
    lord_dependent: LordDependent,
    lord_discard: LordDiscard,
    lord_memory_decay: LORDMemoryDecay,
    lord_plus_plus: LordPlusPlus,
    lord_three: LordThree,
    naive: NaiveTest,
    fallback: OnlineFallback,
    saffron: Saffron,
    saffron_async: SaffronAsync,
    weighted: WeightedGaiPlusPlus,
    elond: ELond,
) -> tuple[SequentialTest, ...]:
    return (
        addis,
        addis_async,
        spending,
        gai,
        lond,
        lord_dependent,
        lord_discard,
        lord_memory_decay,
        lord_plus_plus,
        lord_three,
        naive,
        fallback,
        saffron,
        saffron_async,
        weighted,
        elond,
    )


def batch_implementations(
    bh: BatchBH,
    bh_official: BatchBHOfficial,
    by: BatchBY,
    prds: BatchPRDS,
    storey: BatchStoreyBH,
    ebh: EBH,
) -> tuple[BatchTest, ...]:
    return bh, bh_official, by, prds, storey, ebh


def concrete_keyword_apis(
    addis: Addis,
    bh: BatchBH,
    bh_official: BatchBHOfficial,
    weighted: WeightedGaiPlusPlus,
    elond: ELond,
    ebh: EBH,
) -> None:
    addis.test_one(p_val=0.1)
    addis.test_one_detail(p_val=0.1)
    bh.test_batch(p_vals=[0.1])
    bh.test_batch_detail(p_vals=[0.1])
    bh_official.test_batch(p_vals=[0.1])
    bh_official.test_batch_detail(p_vals=[0.1])
    weighted.test_one(p_val=0.1, prior_weight=2.0, penalty_weight=0.5)
    weighted.test_one_detail(p_val=0.1, prior_weight=2.0, penalty_weight=0.5)
    elond.test_one(e_value=1.0)
    elond.test_one_detail(e_value=1.0)
    ebh.test_batch(e_values=[1.0])
    ebh.test_batch_detail(e_values=[1.0])
