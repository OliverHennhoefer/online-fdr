"""
online-fdr: Online False Discovery Rate Control Algorithms

A comprehensive Python library for controlling False Discovery Rate (FDR)
and Family-Wise Error Rate (FWER) with p-value and e-value procedures.
"""

__version__ = "0.1.0"
__author__ = "Oliver Hennhöfer"
__email__ = "oliver.hennhoefer@mail.de"

from online_fdr import e_values, p_values

__all__ = [
    "__version__",
    "e_values",
    "p_values",
]
