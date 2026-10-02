"""Compare incremental async methods with their frozen scan-based references.

Run from the repository root with ``python benchmarks/async_scaling.py``.
The default run takes several minutes because it includes the slow references.
For the original 800-test SAFFRON workload and 10,000-test scaling check, use::

    python benchmarks/async_scaling.py --methods saffron --scenarios no-discovery

Timings are descriptive and deliberately have no pass/fail threshold.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from statistics import median
from time import perf_counter

# Direct script execution puts benchmarks/, rather than the project root, first.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from online_fdr.p_values.async_methods import AddisAsync, SaffronAsync  # noqa: E402
from tests.async_reference import (  # noqa: E402
    ReferenceAddisAsync,
    ReferenceSaffronAsync,
)

AsyncMethod = SaffronAsync | AddisAsync | ReferenceSaffronAsync | ReferenceAddisAsync
MethodFactory = Callable[[], AsyncMethod]

METHODS: dict[str, tuple[MethodFactory, MethodFactory]] = {
    "saffron": (
        lambda: SaffronAsync(alpha=0.05, wealth=0.025, lambda_=0.5),
        lambda: ReferenceSaffronAsync(alpha=0.05, wealth=0.025, lambda_=0.5),
    ),
    "addis": (
        lambda: AddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
        lambda: ReferenceAddisAsync(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
    ),
}
SCENARIOS: dict[str, tuple[float, ...]] = {
    "no-discovery": (0.8,),
    "candidate-heavy": (0.1,),
    "mixed": (0.8, 1e-8, 0.1, 0.3, 0.8, 0.02),
    "discovery-heavy": (0.0,),
}


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _measure(
    factory: MethodFactory, p_values: list[float], repetitions: int
) -> tuple[float, list[float], tuple[bool | None, ...]]:
    timings: list[float] = []
    for _ in range(repetitions):
        method = factory()
        started = perf_counter()
        for p_value in p_values:
            method.test_one(p_value)
        timings.append(perf_counter() - started)
    return median(timings), method.alpha_history, method.decisions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=_positive_int, default=5)
    parser.add_argument(
        "--sizes", nargs="+", type=_positive_int, default=[200, 400, 800]
    )
    parser.add_argument(
        "--long-sizes",
        nargs="*",
        type=_positive_int,
        default=[2000, 10_000],
        help="additional optimized-only sizes for the no-discovery workload",
    )
    parser.add_argument(
        "--reference-limit",
        type=int,
        default=800,
        help="largest reference workload (0 disables references; at most 800)",
    )
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    parser.add_argument(
        "--scenarios", nargs="+", choices=SCENARIOS, default=list(SCENARIOS)
    )
    args = parser.parse_args()
    if not 0 <= args.reference_limit <= 800:
        parser.error("--reference-limit must be between 0 and 800")

    print(
        f"Immediate start/finish; median of {args.repetitions} fresh instances; "
        "times in seconds",
        flush=True,
    )
    print(
        f"{'method':<8} {'workload':<16} {'tests':>6} {'optimized':>12} "
        f"{'reference':>12} {'speedup':>10} {'discoveries':>12}",
        flush=True,
    )
    for name in args.methods:
        factory, reference_factory = METHODS[name]
        for scenario in args.scenarios:
            pattern = SCENARIOS[scenario]
            sizes = sorted(set(args.sizes))
            if scenario == "no-discovery":
                sizes = sorted(set(sizes + args.long_sizes))
            for size in sizes:
                p_values = [pattern[i % len(pattern)] for i in range(size)]
                elapsed, levels, decisions = _measure(
                    factory, p_values, args.repetitions
                )
                reference_text = speedup_text = "-"
                if size <= args.reference_limit and size in args.sizes:
                    reference_elapsed, reference_levels, reference_decisions = _measure(
                        reference_factory, p_values, args.repetitions
                    )
                    if levels != reference_levels or decisions != reference_decisions:
                        raise RuntimeError(
                            f"{name}/{scenario}/{size}: reference results differ"
                        )
                    reference_text = f"{reference_elapsed:.6f}"
                    speedup_text = f"{reference_elapsed / elapsed:.1f}x"
                print(
                    f"{name:<8} {scenario:<16} {size:>6} {elapsed:>12.6f} "
                    f"{reference_text:>12} {speedup_text:>10} "
                    f"{sum(bool(value) for value in decisions):>12}",
                    flush=True,
                )


if __name__ == "__main__":
    main()
