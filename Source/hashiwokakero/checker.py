"""Constraint checking helpers for search algorithms."""

from __future__ import annotations

from typing import Iterable

from .grid import BridgeCorridor, Grid
from .state import PuzzleState


class ConstraintChecker:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    def is_valid_assignment(self, state: PuzzleState) -> bool:
        return self._respect_degrees(state) and self._avoid_crossings(state)

    def _respect_degrees(self, state: PuzzleState) -> bool:
        for island in self.grid.islands.values():
            remaining = state.remaining_degree(island)
            if remaining < 0:
                return False
        return True

    def _avoid_crossings(self, state: PuzzleState) -> bool:
        occupied = {}
        for corridor in self.grid.corridors.values():
            value = state.corridor_value(corridor.identifier)
            if value == 0:
                continue
            orientation = "H" if corridor.direction.name.startswith("H") else "V"
            for cell in corridor.cells:
                if cell not in occupied:
                    occupied[cell] = orientation
                elif occupied[cell] != orientation:
                    return False
        return True

    def available_actions(self, state: PuzzleState) -> Iterable[tuple[BridgeCorridor, int]]:
        for corridor in self.grid.corridors.values():
            current = state.corridor_value(corridor.identifier)
            if current < 2:
                yield corridor, current + 1
