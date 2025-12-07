"""A* search solver for Hashiwokakero."""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, List, Tuple
import math
from ..checker import ConstraintChecker
from ..state import PuzzleState


@dataclass
class SearchResult:
    state: PuzzleState | None
    elapsed: float
    expanded: int
    status: str


class Heuristic:
    @staticmethod
    def deficit(state: PuzzleState) -> float:
        """
        Calculates h_res: Half the sum of residual demands.
        Based on the degree constraint relaxation[cite: 22].
        """
        return sum(max(0, state.remaining_degree(island)) for island in state.grid.islands.values()) / 2.0

    @staticmethod
    def min_conn(state: PuzzleState) -> float:
        """
        Calculates h_conn: Minimum edges required to connect components (MST logic).
        Based on the connectivity constraint relaxation (Union-Find)[cite: 37].
        """
        p = {i: i for i in state.grid.islands}
        def find(x): p[x] = find(p[x]) if p[x] != x else x; return p[x]
        for cid in state.bridge_counts:
            corr = state.grid.corridors[cid]
            p[find(corr.island_a)] = find(corr.island_b)
        return len({find(i) for i in p}) - 1
    
    @staticmethod
    def bottleneck_corrected(state: PuzzleState) -> float:
        """
        h_bot*: Corrected Bottleneck Heuristic.
        Formula: ceil( 1/2 * sum( max(0, demand - available_edges) ) )
        
        Logic: 
        If an island needs 'd' bridges but only has 'k' neighbors available, 
        then (d - k) represents the "excess" demand that CANNOT be satisfied 
        by single bridges alone. It forces the creation of double bridges.
        
        Dividing by 2 and ceiling ensures Admissibility and Consistency 
        (preventing double-counting errors).
        """
        total_bottleneck = 0
        
        for island in state.grid.islands.values():
            rem_degree = state.remaining_degree(island)
            
            # If the island is already satisfied or over-saturated, skip it
            if rem_degree <= 0:
                continue

            # Count |A_i|: Number of available edges (neighboring corridors)
            # An edge is 'available' if it is not fully saturated (less than 2 bridges).
            available_edges = 0
            for corridor in state.grid.corridors_incident_to(island.identifier):
                current_bridges = state.bridge_counts.get(corridor.identifier, 0)
                if current_bridges < 2:
                    available_edges += 1
            
            # Calculate the deficit: The demand that exceeds the number of available directions.
            # This implies the necessity of double bridges.
            island_deficit = max(0, rem_degree - available_edges)
            total_bottleneck += island_deficit

        # Divide by 2.0 and apply ceiling to maintain consistency properties
        return math.ceil(total_bottleneck / 2.0)

    @staticmethod
    def composite(state: PuzzleState) -> float:
        """
        h_max: Maximum Compatibility Heuristic.
        Returns the pointwise maximum of all available admissible heuristics.
        This provides the tightest lower bound for the A* search.
        """
        return max(
            Heuristic.deficit(state),
            Heuristic.min_conn(state),
            Heuristic.bottleneck_corrected(state)
        )

class AStarSolver:
    def __init__(self, checker: ConstraintChecker, heuristic: Callable[[PuzzleState], float] | None = None) -> None:
        self.checker = checker
        self.heuristic = heuristic or Heuristic.deficit

    def solve(self, initial: PuzzleState) -> SearchResult:
        start = perf_counter()
        grid = initial.grid
        # Pre-compute corridor order for O(C) signature (no sorting)
        cid_list: List[int] = sorted(grid.corridors.keys())
        cid_index = {cid: i for i, cid in enumerate(cid_list)}
        num_corridors = len(cid_list)

        def signature(bc: Dict[int, int]) -> Tuple[int, ...]:
            vals = [0] * num_corridors
            for cid, v in bc.items():
                vals[cid_index[cid]] = v
            return tuple(vals)

        # Precompute islands list for MRV selection
        islands = list(grid.islands.values())

        counter = 0
        init_sig = signature(initial.bridge_counts)
        g_score: Dict[Tuple[int, ...], int] = {init_sig: 0}
        # Heap entries: (f, counter, g, sig, state)
        open_heap: List[Tuple[float, int, int, Tuple[int, ...], PuzzleState]] = []
        heapq.heappush(open_heap, (self.heuristic(initial), counter, 0, init_sig, initial))
        closed: set[Tuple[int, ...]] = set()
        expanded = 0

        while open_heap:
            _, _, g, sig, current = heapq.heappop(open_heap)
            if sig in closed:
                continue
            if current.is_goal():
                return SearchResult(current, perf_counter() - start, expanded, "SOLVED")
            closed.add(sig)
            expanded += 1

            # MRV: pick island with smallest positive remaining degree
            best_island = None
            best_rem = float("inf")
            for isl in islands:
                rem = current.remaining_degree(isl)
                if 0 < rem < best_rem:
                    best_rem = rem
                    best_island = isl
            if best_island is None:
                continue  # no unsatisfied island but not goal (connectivity issue)

            # Expand only corridors incident to best_island
            for corridor in grid.corridors_incident_to(best_island.identifier):
                cur_val = current.corridor_value(corridor.identifier)
                if cur_val >= 2:
                    continue
                new_val = cur_val + 1
                # Quick feasibility: neither endpoint exceeds target
                isl_a = grid.islands[corridor.island_a]
                isl_b = grid.islands[corridor.island_b]
                if current.remaining_degree(isl_a) < new_val - cur_val:
                    continue
                if current.remaining_degree(isl_b) < new_val - cur_val:
                    continue

                # Build next state
                next_bc = current.bridge_counts.copy()
                next_bc[corridor.identifier] = new_val
                next_sig = signature(next_bc)
                tentative_g = g + 1
                if tentative_g >= g_score.get(next_sig, float("inf")):
                    continue

                next_state = PuzzleState(grid, next_bc)
                if not self.checker.is_valid_assignment(next_state):
                    continue

                g_score[next_sig] = tentative_g
                f = tentative_g + self.heuristic(next_state)
                counter += 1
                heapq.heappush(open_heap, (f, counter, tentative_g, next_sig, next_state))

        return SearchResult(None, perf_counter() - start, expanded, "FAILED")
