from abc import ABC, abstractmethod
from typing import Any


class AbstractGammaSequence(ABC):
    """Abstract class for a gamma sequence."""

    def __init__(
        self,  # fmt: skip
        c: float | None = None,
        gamma_exp: float | None = None,
        b0: float | None = None,
    ):
        self.c: float = 0.0 if c is None else float(c)
        self.gamma_exp: float = 0.0 if gamma_exp is None else float(gamma_exp)
        self.b0: float = 0.0 if b0 is None else float(b0)
        self.has_c: bool = c is not None

    @abstractmethod
    def calc_gamma(self, j: int, *args: Any, **kwargs: Any) -> float:
        """
        Calculate gamma for timestep j in the gamma sequence.

        :param j: timestep (number of tests conducted)
        :return: gamma at timestep j
        """
        raise NotImplementedError
