"""
online-fdr: Online False Discovery Rate Control Algorithms

A comprehensive Python library for controlling False Discovery Rate (FDR) 
and Family-Wise Error Rate (FWER) in online multiple hypothesis testing scenarios.
"""

__version__ = "1.0.0"
__author__ = "Oliver Hennhöfer"
__email__ = "oliver.hennhoefer@mail.de"

# Core imports for convenience
from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.alpha.alpha import Gai
from online_fdr.investing.lond.lond import Lond
from online_fdr.investing.lord.three import LordThree
from online_fdr.investing.lord.plus_plus import LordPlusPlus
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.investing.lord.discard import LordDiscard
from online_fdr.investing.lord.dependent import LordDependent
from online_fdr.investing.saffron.saffron import Saffron

from online_fdr.batching.bh import BatchBH
from online_fdr.batching.by import BatchBY
from online_fdr.batching.prds import BatchPRDS
from online_fdr.batching.storey_bh import BatchStoreyBH

from online_fdr.spending.alpha_spending import AlphaSpending
from online_fdr.spending.online_fallback import OnlineFallback

__all__ = [
    # Version
    "__version__",
    
    # Sequential methods
    "Addis",
    "Gai", 
    "Lond",
    "LordThree",
    "LordPlusPlus",
    "LORDMemoryDecay",
    "LordDiscard",
    "LordDependent",
    "Saffron",
    
    # Batch methods
    "BatchBH",
    "BatchBY",
    "BatchPRDS",
    "BatchStoreyBH",
    
    # Spending methods
    "AlphaSpending",
    "OnlineFallback",
]