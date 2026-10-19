import warnings

import numpy as np
import pytest

from online_fdr.core.utils.generation import create_genomics_generator
from online_fdr.e_values import weighted_arithmetic_mean
from online_fdr.e_values.processes import MixtureLikelihoodRatioEProcess


@pytest.mark.parametrize("bad_size", [0, -3, 1.5, True])
def test_data_generator_invalid_batch_size_preserves_cursor(bad_size) -> None:
    generator = create_genomics_generator(n=10)
    generator.sample_batch(5)
    with pytest.raises(ValueError, match="size"):
        generator.sample_batch(bad_size)
    assert generator.current_idx == 5
    p_vals, _ = generator.sample_batch(np.int64(5))
    assert len(p_vals) == 5
    assert generator.current_idx == 10


def test_overflowing_numpy_weights_do_not_warn() -> None:
    weights = [np.float64(1.5e308)] * 2
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert weighted_arithmetic_mean([2.0, 4.0], weights) == pytest.approx(3.0)


def test_mixture_weight_mismatch_names_components() -> None:
    with pytest.raises(ValueError, match="likelihood-ratio components"):
        MixtureLikelihoodRatioEProcess([lambda x: 0.0], weights=[1.0, 2.0])


def test_release_version_check_runs_without_a_tag() -> None:
    from pathlib import Path

    workflow = (Path(__file__).parents[1] / ".github/workflows/release.yml").read_text(
        encoding="utf-8"
    )
    step = workflow.split("- name: Validate release version", 1)[1].split("- name:")[0]
    assert "if: startsWith(github.ref, 'refs/tags/')" not in step
    assert 'GITHUB_REF_TYPE"] != "tag"' in step
