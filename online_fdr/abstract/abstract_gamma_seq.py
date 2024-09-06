from abc import ABC
from typing import Any


class AbstractGammaSequence(ABC):
    """Abstract class for a gamma sequence."""

    def __init__(
        self,  # fmt: skip
        c: float | None = None,
        gamma_exp: float | None = None,
        b0: float | None = None,
    ):
        self.c: float | None = c
        self.gamma_exp: float | None = gamma_exp
        self.b0: float | None = b0

    def calc_gamma(self, j: int, *args: Any, **kwargs: Any):
        """
        Calculate gamma for timestep j in the gamma sequence.

        :param j: timestep (number of tests conducted)
        :return: gamma at timestep j
        """
        raise NotImplementedError
