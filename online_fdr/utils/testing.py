import random


def generate_test_data(n, h0_prop, max_batch_size=15, seed=1) -> ([float], [float]):
    random.seed(seed)

    h1_p = int(n * h0_prop)
    p_vals = [random.uniform(0, 1) for _ in range(n)]

    for i in range(h1_p):
        p_vals[i] = random.uniform(0, 0.00005)

    if max_batch_size is not None:
        batch_sizes = []
        remaining = n
        while remaining > 0:
            batch_size = min(remaining, random.randint(1, max_batch_size))
            batch_sizes.append(batch_size)
            remaining -= batch_size
    else:
        batch_sizes = [n]

    random.shuffle(p_vals)

    return p_vals, batch_sizes


def get_test_data() -> dict:
    return {
        "id": [
            "A15432",
            "B90969",
            "C18705",
            "B49731",
            "E99902",
            "C38292",
            "A30619",
            "D46627",
            "E29198",
            "A41418",
            "D51456",
            "C88669",
            "E03673",
            "A63155",
            "B66033",
        ],
        "date": [
            "2014-12-01",
            "2014-12-01",
            "2014-12-01",
            "2015-09-21",
            "2015-09-21",
            "2015-09-21",
            "2015-09-21",
            "2015-09-21",
            "2016-05-19",
            "2016-05-19",
            "2016-11-12",
            "2017-03-27",
            "2017-03-27",
            "2017-03-27",
            "2017-03-27",
        ],
        "p_value": [
            2.90e-14,
            0.00143,
            0.06514,
            0.00174,
            0.00171,
            3.61e-05,
            0.79149,
            0.27201,
            0.28295,
            7.59e-08,
            0.69274,
            0.30443,
            0.000487,
            0.72342,
            0.54757,
        ],
    }
