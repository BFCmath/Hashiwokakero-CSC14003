"""Brute-force solver for benchmarking purposes."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import List

from ..checker import ConstraintChecker
from ..grid import Grid
from ..state import PuzzleState


@dataclass
class BruteForceResult:
    state: PuzzleState | None
    elapsed: float
    visited: int
    status: str


class BruteForceSolver:
    def __init__(self, grid: Grid, checker: ConstraintChecker) -> None:
        self.grid = grid
        self.checker = checker

    def solve(self) -> BruteForceResult:
        start = perf_counter()
        order = self._sort_corridors_by_mrv()
        visited = 0

        def dfs(index: int, state: PuzzleState) -> PuzzleState | None:
            nonlocal visited
            if index == len(order):
                if state.islands_satisfied() and state.is_connected():
                    return state.copy()
                return None
            corridor_id = order[index]
            for value in (0, 1, 2):
                state.set_corridor_value(corridor_id, value)
                visited += 1
                if not self.checker.is_valid_assignment(state):
                    continue
                solution = dfs(index + 1, state)
                if solution:
                    return solution
            state.set_corridor_value(corridor_id, 0)
            return None

        initial = PuzzleState(self.grid)
        result = dfs(0, initial)
        status = "SOLVED" if result else "FAILED"
        return BruteForceResult(result, perf_counter() - start, visited, status)

    def _sort_corridors_by_mrv(self) -> List[int]:
        def corridor_priority(corridor_id: int) -> tuple:
            corridor = self.grid.corridors[corridor_id]
            island_a = self.grid.islands[corridor.island_a]
            island_b = self.grid.islands[corridor.island_b]
            min_target = min(island_a.target, island_b.target)
            sum_target = island_a.target + island_b.target
            return (min_target, sum_target)
        
        return sorted(self.grid.corridors.keys(), key=corridor_priority)
