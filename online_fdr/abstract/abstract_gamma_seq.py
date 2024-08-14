from abc import ABC


class AbstractGammaSequence(ABC):

    def __init__(self, c: float):
        self.c: float = c

    def calc_gamma(self, j: int, alpha: float | None):
        raise NotImplementedError
