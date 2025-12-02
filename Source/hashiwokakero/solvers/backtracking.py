"""Backtracking solvers: Basic and with Forward Checking."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, Optional, Set

from ..checker import ConstraintChecker
from ..grid import Grid, Island, BridgeCorridor
from ..state import PuzzleState


@dataclass
class BacktrackingResult:
    state: PuzzleState | None
    elapsed: float
    explored: int
    status: str


class BacktrackingSolver:
    """Basic Backtracking solver without Forward Checking."""
    
    def __init__(self, grid: Grid, checker: ConstraintChecker) -> None:
        self.grid = grid
        self.checker = checker
        self.explored = 0

    def solve(self) -> BacktrackingResult:
        start = perf_counter()
        self.explored = 0
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
            for new_value in range(current + 1, 3):
                state.set_corridor_value(corridor.identifier, new_value)
                if self.checker.is_valid_assignment(state):
                    result = self._search(state)
                    if result:
                        return result
                # Backtrack về giá trị ban đầu
                state.set_corridor_value(corridor.identifier, current)
        return None

    def _select_island(self, state: PuzzleState) -> Island | None:
        """MRV heuristic: chọn đảo có remaining degree nhỏ nhất."""
        candidates = [
            island
            for island in self.grid.islands.values()
            if state.remaining_degree(island) > 0
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda isl: state.remaining_degree(isl))


class BacktrackingFCSolver:
    """Backtracking solver with Forward Checking."""
    
    def __init__(self, grid: Grid, checker: ConstraintChecker) -> None:
        self.grid = grid
        self.checker = checker
        self.explored = 0

    def solve(self) -> BacktrackingResult:
        start = perf_counter()
        self.explored = 0
        state = PuzzleState(self.grid)
        # Khởi tạo domain cho mỗi corridor: {0, 1, 2}
        domains: Dict[int, Set[int]] = {
            corridor.identifier: {0, 1, 2}
            for corridor in self.grid.corridors.values()
        }
        solution = self._search(state, domains)
        status = "SOLVED" if solution else "FAILED"
        return BacktrackingResult(solution, perf_counter() - start, self.explored, status)

    def _search(self, state: PuzzleState, domains: Dict[int, Set[int]]) -> Optional[PuzzleState]:
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
            # Thử TẤT CẢ giá trị hợp lệ: current+1 đến 2
            for new_value in range(current + 1, 3):
                # Kiểm tra giá trị có trong domain không
                if new_value not in domains[corridor.identifier]:
                    continue
                    
                state.set_corridor_value(corridor.identifier, new_value)
                
                if self.checker.is_valid_assignment(state):
                    # Forward Checking: thu hẹp domain của các biến liên quan
                    new_domains, valid = self._forward_check(state, domains, corridor)
                    
                    if valid:
                        result = self._search(state, new_domains)
                        if result:
                            return result
                
                # Backtrack về giá trị ban đầu
                state.set_corridor_value(corridor.identifier, current)
        return None

    def _forward_check(
        self, 
        state: PuzzleState, 
        domains: Dict[int, Set[int]], 
        assigned_corridor: BridgeCorridor
    ) -> tuple[Dict[int, Set[int]], bool]:
        """
        Forward Checking: Sau khi gán giá trị cho một corridor,
        thu hẹp domain của các corridor liên quan.
        
        Returns:
            (new_domains, valid): new_domains là domain mới, valid=False nếu có domain rỗng
        """
        new_domains = {cid: set(vals) for cid, vals in domains.items()}
        
        # Cố định giá trị của corridor vừa gán
        current_value = state.corridor_value(assigned_corridor.identifier)
        new_domains[assigned_corridor.identifier] = {current_value}
        
        # Kiểm tra các đảo liên quan đến corridor vừa gán
        affected_islands = [assigned_corridor.island_a, assigned_corridor.island_b]
        
        for island_id in affected_islands:
            island = self.grid.islands[island_id]
            remaining = state.remaining_degree(island)
            
            # Nếu đảo đã thỏa mãn (remaining = 0), các corridor khác không được tăng
            if remaining == 0:
                for corridor in self.grid.corridors_incident_to(island_id):
                    if corridor.identifier == assigned_corridor.identifier:
                        continue
                    cid = corridor.identifier
                    current = state.corridor_value(cid)
                    # Corridor này không thể tăng thêm
                    new_domains[cid] = {v for v in new_domains[cid] if v <= current}
                    if not new_domains[cid]:
                        return new_domains, False
            
            # Nếu remaining < 0, không hợp lệ
            elif remaining < 0:
                return new_domains, False
            
            # Kiểm tra xem đảo có thể đạt được target không
            else:
                # Tính tổng max có thể đạt được từ các corridor
                max_possible = 0
                for corridor in self.grid.corridors_incident_to(island_id):
                    cid = corridor.identifier
                    current = state.corridor_value(cid)
                    max_in_domain = max(new_domains[cid]) if new_domains[cid] else current
                    max_possible += max(current, max_in_domain)
                
                # Nếu max có thể < target, không thể thỏa mãn
                if max_possible < island.target:
                    return new_domains, False
                
                # Thu hẹp domain: loại bỏ giá trị quá lớn
                for corridor in self.grid.corridors_incident_to(island_id):
                    cid = corridor.identifier
                    current = state.corridor_value(cid)
                    if current > 0:
                        continue  # Đã gán, bỏ qua
                    
                    max_allowed = min(2, remaining)
                    new_domains[cid] = {v for v in new_domains[cid] if v <= max_allowed}
                    if not new_domains[cid]:
                        return new_domains, False
        
        return new_domains, True

    def _select_island(self, state: PuzzleState) -> Island | None:
        """MRV heuristic: chọn đảo có remaining degree nhỏ nhất."""
        candidates = [
            island
            for island in self.grid.islands.values()
            if state.remaining_degree(island) > 0
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda isl: state.remaining_degree(isl))
