"""Backtracking solver with simple heuristics."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Optional

from ..checker import ConstraintChecker
from ..grid import Grid, Island
from ..state import PuzzleState


@dataclass
class BacktrackingResult:
    state: PuzzleState | None
    elapsed: float
    explored: int
    status: str


class BacktrackingSolver:
    def __init__(self, grid: Grid, checker: ConstraintChecker) -> None:
        self.grid = grid
        self.checker = checker
        self.explored = 0

    def solve(self) -> BacktrackingResult:
        start = perf_counter()
        state = PuzzleState(self.grid)
        solution = self._search(state)
        status = "SOLVED" if solution else "FAILED"
        return BacktrackingResult(solution, perf_counter() - start, self.explored, status)

    def _search(self, state: PuzzleState) -> Optional[PuzzleState]:
        self.explored += 1
        if state.is_goal():
            return state.copy()
        island = self._select_island(state)
        if island is None:
            return None
        for corridor in self.grid.corridors_incident_to(island.identifier):
            current = state.corridor_value(corridor.identifier)
            if current >= 2:
                continue
            state.set_corridor_value(corridor.identifier, current + 1)
            if self.checker.is_valid_assignment(state):
                result = self._search(state)
                if result:
                    return result
            state.set_corridor_value(corridor.identifier, current)
        return None

    def _select_island(self, state: PuzzleState) -> Island | None:
        candidates = [
            island
            for island in self.grid.islands.values()
            if state.remaining_degree(island) > 0
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda isl: state.remaining_degree(isl))
