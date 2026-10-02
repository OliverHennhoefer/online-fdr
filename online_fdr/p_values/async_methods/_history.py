from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


class _FenwickCounter:
    """Growing integer prefix sums with updates to previously appended entries."""

    def __init__(self, values: Iterable[int] = ()):
        self._tree = [0, *values]
        for index in range(1, len(self._tree)):
            parent = index + (index & -index)
            if parent < len(self._tree):
                self._tree[parent] += self._tree[index]

    def __len__(self) -> int:
        return len(self._tree) - 1

    def prefix(self, end_exclusive: int) -> int:
        if not 0 <= end_exclusive <= len(self):
            raise IndexError("prefix end is outside the counter")
        total = 0
        while end_exclusive:
            total += self._tree[end_exclusive]
            end_exclusive -= end_exclusive & -end_exclusive
        return total

    def append(self, value: int) -> None:
        index = len(self._tree)
        # A newly created parent must also include its existing descendants.
        previous = self.prefix(index - 1) - self.prefix(index - (index & -index))
        self._tree.append(value + previous)

    def add(self, index: int, delta: int) -> None:
        if not 0 <= index < len(self):
            raise IndexError("update index is outside the counter")
        index += 1
        while index < len(self._tree):
            self._tree[index] += delta
            index += index & -index


@dataclass
class _AsyncHistoryIndex:
    """Derived accounting; persistent state remains in the original records."""

    signature: tuple[float, ...]
    counts: _FenwickCounter
    rejections: list[int]
