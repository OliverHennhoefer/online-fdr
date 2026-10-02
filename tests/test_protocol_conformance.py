from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSUMERS = ROOT / "tests" / "typing" / "protocol_consumers.py"


def _type_check(source: Path, cache: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--disallow-any-expr",
            "--follow-imports=silent",
            "--no-incremental",
            "--cache-dir",
            str(cache),
            str(source),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_builtin_methods_satisfy_public_protocols(tmp_path: Path) -> None:
    result = _type_check(CONSUMERS, tmp_path / "mypy")

    assert result.returncode == 0, result.stdout + result.stderr


def test_protocol_state_is_read_only(tmp_path: Path) -> None:
    source = tmp_path / "read_only_consumer.py"
    source.write_text(
        "from online_fdr.core import BatchTest, SequentialTest\n"
        "def mutate(single: SequentialTest, batch: BatchTest) -> None:\n"
        "    single.target_level = 0.1\n"
        "    single.error_rate = 'FWER'\n"
        "    single.last_test_level = 0.1\n"
        "    single.last_rejection_threshold = 0.1\n"
        "    single.num_hypotheses = 1\n"
        "    batch.num_batches = 1\n",
        encoding="utf-8",
    )

    result = _type_check(source, tmp_path / "mypy")

    assert result.returncode == 1, result.stdout + result.stderr
    for name in (
        "target_level",
        "error_rate",
        "last_test_level",
        "last_rejection_threshold",
        "num_hypotheses",
        "num_batches",
    ):
        assert f'Property "{name}" defined in' in result.stdout, result.stdout
    assert result.stdout.count(" is read-only") == 6, result.stdout
