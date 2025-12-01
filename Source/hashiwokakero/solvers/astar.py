"""A* search solver for Hashiwokakero."""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Tuple

from ..checker import ConstraintChecker
from ..state import PuzzleState


@dataclass
class SearchResult:
    state: PuzzleState | None
    elapsed: float
    expanded: int
    status: str


class AStarSolver:
    def __init__(self, checker: ConstraintChecker, heuristic: Callable[[PuzzleState], float] | None = None) -> None:
        self.checker = checker
        self.heuristic = heuristic or (lambda st: st.deficit() / 2.0)

    def solve(self, initial: PuzzleState) -> SearchResult:
        start = perf_counter()
        counter = 0
        open_heap: list[Tuple[float, int, PuzzleState]] = []
        g_score: Dict[Tuple[Tuple[int, int], ...], int] = {}

        def signature(state: PuzzleState) -> Tuple[Tuple[int, int], ...]:
            return tuple(sorted(state.bridge_counts.items()))

        sig = signature(initial)
        g_score[sig] = 0
        heapq.heappush(open_heap, (self.heuristic(initial), counter, initial))
        closed: set[Tuple[Tuple[int, int], ...]] = set()
        expanded = 0

        while open_heap:
            _, _, current = heapq.heappop(open_heap)
            sig = signature(current)
            if sig in closed:
                continue
            if current.is_goal():
                return SearchResult(current, perf_counter() - start, expanded, "SOLVED")
            closed.add(sig)
            expanded += 1
            for corridor, value in self.checker.available_actions(current):
                next_state = current.copy()
                next_state.set_corridor_value(corridor.identifier, value)
                if not self.checker.is_valid_assignment(next_state):
                    continue
                next_sig = signature(next_state)
                tentative_g = g_score[sig] + 1
                if tentative_g >= g_score.get(next_sig, float("inf")):
                    continue
                g_score[next_sig] = tentative_g
                f_score = tentative_g + self.heuristic(next_state)
                counter += 1
                heapq.heappush(open_heap, (f_score, counter, next_state))
        return SearchResult(None, perf_counter() - start, expanded, "FAILED")
