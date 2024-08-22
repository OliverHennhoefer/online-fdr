def format_result(i: int, result: bool, p_val: float, thresh: float | None):
    try:
        operator = "<" if p_val < thresh else ">"
    except TypeError:
        operator = None
    (
        print(f"[{i + 1}] {result} ({p_val:.3f} was discarded)")
        if thresh is None
        else print(f"[{i + 1}] {result} ({p_val:.3f} {operator} {thresh:.6f})")
    )
