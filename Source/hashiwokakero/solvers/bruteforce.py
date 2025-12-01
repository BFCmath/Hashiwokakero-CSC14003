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
        order = list(self.grid.corridors.keys())
        visited = 0

        def dfs(index: int, state: PuzzleState) -> PuzzleState | None:
            nonlocal visited
            if index == len(order):
                return state if state.is_goal() else None
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
