def format_result(i: int, result: bool, p_val: float, thresh: float | None) -> None:
    if thresh is None:
        print(f"[{i + 1}] {result} ({p_val:.3f} was discarded)")
        return

    operator = "<" if p_val < thresh else ">"
    print(f"[{i + 1}] {result} ({p_val:.3f} {operator} {thresh:.6f})")
