def format_result(i: int, result: bool, p_val: float, threshold: float):
    print(f"[{i + 1}] {result} ({p_val:.3f}; threshold {threshold:.6f})")
