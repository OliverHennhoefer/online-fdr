import online_fdr
from online_fdr import e_values, p_values
from online_fdr.e_values import EBH, ELond, make_power_calibrator
from online_fdr.p_values import Addis, BatchBH, Saffron

EXPECTED_PUBLIC_API = [
    "__version__",
    "e_values",
    "p_values",
]

EXPECTED_BINDINGS = {
    "e_values": e_values,
    "p_values": p_values,
}


def test_public_api_all_is_stable() -> None:
    assert online_fdr.__all__ == EXPECTED_PUBLIC_API


def test_public_api_bindings_are_expected() -> None:
    for symbol, expected in EXPECTED_BINDINGS.items():
        assert getattr(online_fdr, symbol) is expected


def test_lane_level_imports_are_available() -> None:
    assert p_values.Addis is Addis
    assert p_values.Saffron is Saffron
    assert p_values.BatchBH is BatchBH
    assert e_values.EBH is EBH
    assert e_values.ELond is ELond
    assert e_values.make_power_calibrator is make_power_calibrator


def test_public_api_version_is_nonempty_string() -> None:
    assert isinstance(online_fdr.__version__, str)
    assert online_fdr.__version__
