"""Mutable puzzle state used by search algorithms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from .grid import BridgeCorridor, Grid, Island


@dataclass
class PuzzleState:
    grid: Grid
    bridge_counts: Dict[int, int] = field(default_factory=dict)

    def copy(self) -> "PuzzleState":
        return PuzzleState(self.grid, dict(self.bridge_counts))

    def corridor_value(self, corridor_id: int) -> int:
        return self.bridge_counts.get(corridor_id, 0)

    def set_corridor_value(self, corridor_id: int, value: int) -> None:
        if value not in (0, 1, 2):
            raise ValueError("Bridge value must be 0, 1, or 2")
        if value == 0:
            self.bridge_counts.pop(corridor_id, None)
        else:
            self.bridge_counts[corridor_id] = value

    def remaining_degree(self, island: Island) -> int:
        used = 0
        for corridor in self.grid.corridors_incident_to(island.identifier):
            value = self.corridor_value(corridor.identifier)
            used += value
        return island.target - used

    def is_connected(self) -> bool:
        islands = list(self.grid.islands.keys())
        if not islands:
            return True
        visited = set()
        stack = [islands[0]]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for corridor in self.grid.corridors_incident_to(node):
                if self.corridor_value(corridor.identifier) == 0:
                    continue
                neighbor = corridor.island_b if corridor.island_a == node else corridor.island_a
                if neighbor not in visited:
                    stack.append(neighbor)
        return len(visited) == len(islands)

    def occupied_cells(self) -> List[Tuple[int, int, str]]:
        """Return list of occupied cells as (row, col, orientation)."""
        occupied: List[Tuple[int, int, str]] = []
        for corridor in self.grid.corridors.values():
            value = self.corridor_value(corridor.identifier)
            if value == 0:
                continue
            orientation = "H" if corridor.direction.name.startswith("H") else "V"
            for cell in corridor.cells:
                occupied.append((*cell, orientation))
        return occupied

    def islands_satisfied(self) -> bool:
        return all(self.remaining_degree(island) == 0 for island in self.grid.islands.values())

    def is_goal(self) -> bool:
        return self.islands_satisfied() and self.is_connected()

    def deficit(self) -> int:
        return sum(max(0, self.remaining_degree(island)) for island in self.grid.islands.values())

    def available_actions(self) -> Iterable[Tuple[BridgeCorridor, int]]:
        for corridor in self.grid.corridors.values():
            current = self.corridor_value(corridor.identifier)
            if current < 2:
                yield corridor, current + 1

    def to_symbol_matrix(self) -> List[List[str]]:
        matrix = [["0" for _ in range(self.grid.width)] for _ in range(self.grid.height)]
        for island in self.grid.islands.values():
            matrix[island.row][island.col] = str(island.target)
        for corridor in self.grid.corridors.values():
            value = self.corridor_value(corridor.identifier)
            if value == 0:
                continue
            if corridor.direction == corridor.direction.HORIZONTAL:
                symbol = "=" if value == 2 else "-"
            else:
                symbol = "$" if value == 2 else "|"
            for cell in corridor.cells:
                row, col = cell
                matrix[row][col] = symbol
        return matrix
