import online_fdr
from online_fdr.async_methods import AddisAsync, AsyncTestLevel, SaffronAsync
from online_fdr.batching.bh import BatchBH
from online_fdr.batching.by import BatchBY
from online_fdr.batching.prds import BatchPRDS
from online_fdr.batching.storey_bh import BatchStoreyBH
from online_fdr.batching.toad import Toad
from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.alpha.alpha import Gai
from online_fdr.investing.alpha.weighted_gai_plus_plus import WeightedGaiPlusPlus
from online_fdr.investing.lond.lond import Lond
from online_fdr.investing.lord.dependent import LordDependent
from online_fdr.investing.lord.discard import LordDiscard
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.investing.lord.plus_plus import LordPlusPlus
from online_fdr.investing.lord.three import LordThree
from online_fdr.investing.saffron.saffron import Saffron
from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.online_fallback import OnlineFallback

EXPECTED_PUBLIC_API = [
    "__version__",
    "Addis",
    "Gai",
    "Lond",
    "LordThree",
    "LordPlusPlus",
    "LORDMemoryDecay",
    "LordDiscard",
    "LordDependent",
    "Saffron",
    "SaffronAsync",
    "AddisAsync",
    "AsyncTestLevel",
    "WeightedGaiPlusPlus",
    "BatchBH",
    "BatchBY",
    "BatchPRDS",
    "BatchStoreyBH",
    "Toad",
    "AlphaSpending",
    "OnlineFallback",
]

EXPECTED_BINDINGS = {
    "Addis": Addis,
    "Gai": Gai,
    "Lond": Lond,
    "LordThree": LordThree,
    "LordPlusPlus": LordPlusPlus,
    "LORDMemoryDecay": LORDMemoryDecay,
    "LordDiscard": LordDiscard,
    "LordDependent": LordDependent,
    "Saffron": Saffron,
    "SaffronAsync": SaffronAsync,
    "AddisAsync": AddisAsync,
    "AsyncTestLevel": AsyncTestLevel,
    "WeightedGaiPlusPlus": WeightedGaiPlusPlus,
    "BatchBH": BatchBH,
    "BatchBY": BatchBY,
    "BatchPRDS": BatchPRDS,
    "BatchStoreyBH": BatchStoreyBH,
    "Toad": Toad,
    "AlphaSpending": AlphaSpending,
    "OnlineFallback": OnlineFallback,
}


def test_public_api_all_is_stable() -> None:
    assert online_fdr.__all__ == EXPECTED_PUBLIC_API


def test_public_api_bindings_are_expected() -> None:
    for symbol, expected in EXPECTED_BINDINGS.items():
        assert getattr(online_fdr, symbol) is expected


def test_public_api_version_is_nonempty_string() -> None:
    assert isinstance(online_fdr.__version__, str)
    assert online_fdr.__version__
