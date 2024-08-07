from itertools import accumulate

from online_fdr.abstract.abstract_online_test import AbstractOnlineTest
from online_fdr.utils.validity import check_p_val


class SAFFRON(AbstractOnlineTest):

    def __init__(self, alpha: float, lambda_: float, gamma: float):
        super().__init__(alpha)
        self.alpha: float = alpha
        self.lambda_: float = lambda_

        tmp = range(1, 10000)

        ones = [1.0] * len(tmp)
        power_results = [pow(x, gamma) for x in tmp]
        self.gamma = [one / power for one, power in zip(ones, power_results)]
        self.gamma = [i / sum(self.gamma) for i in self.gamma]

        self.w0 = (1 - self.lambda_) * self.alpha / 2

        self.num_test: int = 0
        self.last_reject: list = []
        self.candidates: list = []

    def test_one(self, p_val: float) -> bool:
        check_p_val(p_val)
        self.num_test += 1

        self.candidates.append(p_val < self.lambda_)
        is_rejected = p_val <= self.alpha

        if is_rejected:
            self.last_reject.append(self.num_test)

        sum_candidates = sum(self.candidates)
        zero_gamma = self.gamma[self.num_test - sum_candidates]

        num_last_reject = len(self.last_reject)
        if num_last_reject > 0:
            if self.last_reject[0] <= self.num_test:
                candidates_ex_first = sum(
                    self.candidates[self.last_reject[0] + 1 : self.num_test + 2]  # noqa
                )
                first_gamma = self.gamma[
                    self.num_test - self.last_reject[0] - candidates_ex_first
                ]
            else:
                first_gamma = 0

        if num_last_reject >= 2:
            idx = [self.num_test] * (num_last_reject - 1)
            gamma_idx = [g - i for g, i in zip(idx, self.last_reject[1:])]
            gamma_idx = [g - i for g, i in zip(gamma_idx, gamma_idx)]
            test = list(accumulate([int(elem) for elem in self.candidates[1:]][::-1]))[
                ::-1
            ]
            sum_gamma = self.gamma[gamma_idx - test]
        return p_val < self.alpha
