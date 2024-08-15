from abc import ABC


class AbstractGammaSequence(ABC):

    def __init__(self, c: float = None, gamma_exponent: float | None = None):
        self.c: float | None = c
        self.gamma_exponent: float | None = gamma_exponent

    def calc_gamma(self, j: int, alpha: float | None):
        raise NotImplementedError
