from abc import ABC


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

    def calc_gamma(self, j: int, alpha: float | None):
        """
        Calculate gamma for timestep j in the gamma sequence.

        :param j: timestep (number of tests conducted)
        :param alpha: significance level
        :return: gamma at timestep j
        """
        raise NotImplementedError
