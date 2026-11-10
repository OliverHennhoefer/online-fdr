"""Docstring examples are documentation, so they have to run and be true."""

import doctest
import importlib
import pkgutil

import pytest

import online_fdr

MODULES = sorted(
    info.name for info in pkgutil.walk_packages(online_fdr.__path__, "online_fdr.")
)


@pytest.mark.parametrize("module_name", MODULES)
def test_docstring_examples_run_and_print_what_they_state(module_name: str) -> None:
    module = importlib.import_module(module_name)

    results = doctest.testmod(module, optionflags=doctest.ELLIPSIS)

    assert results.failed == 0
