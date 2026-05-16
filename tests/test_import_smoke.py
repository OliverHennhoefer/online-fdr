import importlib

import pytest

DOCUMENTED_MODULES = [
    "online_fdr",
    "online_fdr.async_methods",
    "online_fdr.investing",
    "online_fdr.batching",
    "online_fdr.spending",
    "online_fdr.utils",
    "online_fdr.async_methods.addis_async",
    "online_fdr.async_methods.saffron_async",
    "online_fdr.investing.addis.addis",
    "online_fdr.investing.alpha.alpha",
    "online_fdr.investing.alpha.weighted_gai_plus_plus",
    "online_fdr.investing.lond.lond",
    "online_fdr.investing.lord.three",
    "online_fdr.investing.lord.plus_plus",
    "online_fdr.investing.lord.dependent",
    "online_fdr.investing.lord.discard",
    "online_fdr.investing.lord.mem_decay",
    "online_fdr.investing.saffron.saffron",
    "online_fdr.spending.alpha_spending",
    "online_fdr.spending.online_fallback",
    "online_fdr.batching.bh",
    "online_fdr.batching.by",
    "online_fdr.batching.prds",
    "online_fdr.batching.storey_bh",
    "online_fdr.batching.toad",
    "online_fdr.utils.generation",
    "online_fdr.utils.evaluation",
    "online_fdr.utils.validity",
]

DOCUMENTED_CLASS_LOCATIONS = [
    ("online_fdr.async_methods", "AddisAsync"),
    ("online_fdr.async_methods", "AsyncTestLevel"),
    ("online_fdr.async_methods", "SaffronAsync"),
    ("online_fdr.investing.addis.addis", "Addis"),
    ("online_fdr.investing.alpha.alpha", "Gai"),
    ("online_fdr.investing.alpha.weighted_gai_plus_plus", "WeightedGaiPlusPlus"),
    ("online_fdr.investing.lond.lond", "Lond"),
    ("online_fdr.investing.lord.three", "LordThree"),
    ("online_fdr.investing.lord.plus_plus", "LordPlusPlus"),
    ("online_fdr.investing.lord.dependent", "LordDependent"),
    ("online_fdr.investing.lord.discard", "LordDiscard"),
    ("online_fdr.investing.lord.mem_decay", "LORDMemoryDecay"),
    ("online_fdr.investing.saffron.saffron", "Saffron"),
    ("online_fdr.spending.alpha_spending", "AlphaSpending"),
    ("online_fdr.spending.online_fallback", "OnlineFallback"),
    ("online_fdr.batching.bh", "BatchBH"),
    ("online_fdr.batching.by", "BatchBY"),
    ("online_fdr.batching.prds", "BatchPRDS"),
    ("online_fdr.batching.storey_bh", "BatchStoreyBH"),
    ("online_fdr.batching.toad", "Toad"),
    ("online_fdr.utils.generation", "DataGenerator"),
    ("online_fdr.utils.generation", "GaussianLocationModel"),
    ("online_fdr.utils.generation", "BetaMixtureModel"),
    ("online_fdr.utils.generation", "ChiSquaredModel"),
    ("online_fdr.utils.generation", "SparseGaussianModel"),
    ("online_fdr.utils.evaluation", "MemoryDecayFDR"),
]


@pytest.mark.parametrize("module_name", DOCUMENTED_MODULES)
def test_documented_modules_import(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None


@pytest.mark.parametrize(("module_name", "class_name"), DOCUMENTED_CLASS_LOCATIONS)
def test_documented_classes_exist(module_name: str, class_name: str) -> None:
    module = importlib.import_module(module_name)
    assert hasattr(module, class_name)
