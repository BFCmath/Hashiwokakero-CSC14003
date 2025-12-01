"""Variable registry for CNF encodings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class VariableKey:
    kind: str
    payload: Tuple[int, ...]


class VariableRegistry:
    def __init__(self) -> None:
        self._next = 1
        self._forward: Dict[VariableKey, int] = {}
        self._reverse: Dict[int, VariableKey] = {}

    def var(self, kind: str, *payload: int) -> int:
        key = VariableKey(kind, tuple(payload))
        if key not in self._forward:
            self._forward[key] = self._next
            self._reverse[self._next] = key
            self._next += 1
        return self._forward[key]

    def lookup(self, var_id: int) -> VariableKey | None:
        return self._reverse.get(var_id)

    @property
    def count(self) -> int:
        return self._next - 1

    def reserve(self, count: int) -> None:
        """Advance the counter to reserve a block of IDs."""
        self._next += count

    def set_max(self, max_id: int) -> None:
        """Ensure the counter is at least max_id + 1."""
        if max_id >= self._next:
            self._next = max_id + 1
