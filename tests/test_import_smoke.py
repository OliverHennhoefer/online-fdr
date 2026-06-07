import importlib

import pytest

DOCUMENTED_MODULES = [
    "online_fdr",
    "online_fdr.core",
    "online_fdr.e_values",
    "online_fdr.e_values.batch",
    "online_fdr.e_values.generation",
    "online_fdr.e_values.processes",
    "online_fdr.e_values.sequential",
    "online_fdr.e_values.toolbox",
    "online_fdr.p_values",
    "online_fdr.p_values.async_methods",
    "online_fdr.p_values.investing",
    "online_fdr.p_values.batching",
    "online_fdr.p_values.spending",
    "online_fdr.core.utils",
    "online_fdr.p_values.async_methods.addis_async",
    "online_fdr.p_values.async_methods.saffron_async",
    "online_fdr.p_values.investing.addis.addis",
    "online_fdr.p_values.investing.alpha.alpha",
    "online_fdr.p_values.investing.alpha.weighted_gai_plus_plus",
    "online_fdr.p_values.investing.lond.lond",
    "online_fdr.p_values.investing.lord.three",
    "online_fdr.p_values.investing.lord.plus_plus",
    "online_fdr.p_values.investing.lord.dependent",
    "online_fdr.p_values.investing.lord.discard",
    "online_fdr.p_values.investing.lord.mem_decay",
    "online_fdr.p_values.investing.saffron.saffron",
    "online_fdr.p_values.spending.alpha_spending",
    "online_fdr.p_values.spending.online_fallback",
    "online_fdr.p_values.batching.bh",
    "online_fdr.p_values.batching.by",
    "online_fdr.p_values.batching.prds",
    "online_fdr.p_values.batching.storey_bh",
    "online_fdr.p_values.batching.toad",
    "online_fdr.core.utils.generation",
    "online_fdr.core.utils.evaluation",
    "online_fdr.core.utils.validity",
]

DOCUMENTED_CLASS_LOCATIONS = [
    ("online_fdr.e_values", "EBH"),
    ("online_fdr.e_values", "ELond"),
    ("online_fdr.e_values.generation", "GaussianEValueGenerator"),
    ("online_fdr.e_values.processes", "LikelihoodRatioEProcess"),
    ("online_fdr.e_values.processes", "MixtureLikelihoodRatioEProcess"),
    ("online_fdr.e_values.processes", "BettingEProcess"),
    ("online_fdr.p_values.async_methods", "AddisAsync"),
    ("online_fdr.p_values.async_methods", "AsyncTestLevel"),
    ("online_fdr.p_values.async_methods", "SaffronAsync"),
    ("online_fdr.p_values.investing.addis.addis", "Addis"),
    ("online_fdr.p_values.investing.alpha.alpha", "Gai"),
    ("online_fdr.p_values.investing.alpha.weighted_gai_plus_plus", "WeightedGaiPlusPlus"),
    ("online_fdr.p_values.investing.lond.lond", "Lond"),
    ("online_fdr.p_values.investing.lord.three", "LordThree"),
    ("online_fdr.p_values.investing.lord.plus_plus", "LordPlusPlus"),
    ("online_fdr.p_values.investing.lord.dependent", "LordDependent"),
    ("online_fdr.p_values.investing.lord.discard", "LordDiscard"),
    ("online_fdr.p_values.investing.lord.mem_decay", "LORDMemoryDecay"),
    ("online_fdr.p_values.investing.saffron.saffron", "Saffron"),
    ("online_fdr.p_values.spending.alpha_spending", "AlphaSpending"),
    ("online_fdr.p_values.spending.online_fallback", "OnlineFallback"),
    ("online_fdr.p_values.batching.bh", "BatchBH"),
    ("online_fdr.p_values.batching.by", "BatchBY"),
    ("online_fdr.p_values.batching.prds", "BatchPRDS"),
    ("online_fdr.p_values.batching.storey_bh", "BatchStoreyBH"),
    ("online_fdr.p_values.batching.toad", "Toad"),
    ("online_fdr.core.utils.generation", "DataGenerator"),
    ("online_fdr.core.utils.generation", "GaussianLocationModel"),
    ("online_fdr.core.utils.generation", "BetaMixtureModel"),
    ("online_fdr.core.utils.generation", "ChiSquaredModel"),
    ("online_fdr.core.utils.generation", "SparseGaussianModel"),
    ("online_fdr.core.utils.evaluation", "MemoryDecayFDR"),
]


@pytest.mark.parametrize("module_name", DOCUMENTED_MODULES)
def test_documented_modules_import(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None


@pytest.mark.parametrize(("module_name", "class_name"), DOCUMENTED_CLASS_LOCATIONS)
def test_documented_classes_exist(module_name: str, class_name: str) -> None:
    module = importlib.import_module(module_name)
    assert hasattr(module, class_name)
