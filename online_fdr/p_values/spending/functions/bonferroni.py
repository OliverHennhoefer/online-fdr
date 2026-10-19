from online_fdr.core.abstract.abstract_spend_func import AbstractSpendFunc
from online_fdr.core.utils.validity import check_positive_integer


class Bonferroni(AbstractSpendFunc):
    """Standard Bonferroni Spending Function[1_][2_][3_].

    [1] Bonferroni, C. E.
    "Il calcolo delle assicurazioni su gruppi di teste."
    In Studi in Onore del Professore Salvatore Ortu Carboni.
    Rome: Italy, pp. 13-60, 1935.
    [2] Bonferroni, C. E.
    "Teoria statistica delle classi e calcolo delle probabilità."
    Pubblicazioni del R Istituto Superiore di Scienze Economiche
    e Commerciali di Firenze 8, 3-62, 1936.
    [3] Dunn, O. J. "Multiple Comparisons Among Means."
    Journal of the American Statistical Association,
    56(293):52–64, 1961."""

    def __init__(self, k: int):
        check_positive_integer(k, "k")
        super().__init__(int(k))

    def spend(self, index: int, alpha: float) -> float:
        if index < 0:
            raise ValueError("index must be non-negative.")
        if self.k is None or index >= self.k:
            raise ValueError(
                "Bonferroni spending horizon exceeded. Increase k for longer runs."
            )
        return alpha / self.k
