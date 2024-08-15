from abc import ABC


class AbstractGammaSequence(ABC):

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
        raise NotImplementedError
