"""Grid, island, and corridor representations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Sequence, Tuple


class Direction(str, Enum):
    HORIZONTAL = "H"
    VERTICAL = "V"


@dataclass(frozen=True)
class Island:
    identifier: int
    row: int
    col: int
    target: int


@dataclass(frozen=True)
class BridgeCorridor:
    identifier: int
    island_a: int
    island_b: int
    direction: Direction
    cells: Tuple[Tuple[int, int], ...]

    @property
    def endpoints(self) -> Tuple[int, int]:
        return (self.island_a, self.island_b)


class Grid:
    """Immutable grid representation built from the raw matrix."""

    def __init__(self, matrix: Sequence[Sequence[int]]):
        self._matrix = tuple(tuple(row) for row in matrix)
        self.height = len(self._matrix)
        self.width = len(self._matrix[0])
        self.islands: Dict[int, Island] = {}
        self.corridors: Dict[int, BridgeCorridor] = {}
        self._island_lookup: Dict[Tuple[int, int], int] = {}
        self._build_islands()
        self._build_corridors()

    def _build_islands(self) -> None:
        identifier = 0
        for r, row in enumerate(self._matrix):
            for c, value in enumerate(row):
                if value > 0:
                    identifier += 1
                    island = Island(identifier=identifier, row=r, col=c, target=value)
                    self.islands[identifier] = island
                    self._island_lookup[(r, c)] = identifier

    def _build_corridors(self) -> None:
        corridor_id = 0
        for island in self.islands.values():
            # horizontal scanning to the right
            c = island.col + 1
            cells: List[Tuple[int, int]] = []
            while c < self.width:
                pos = (island.row, c)
                if pos in self._island_lookup:
                    corridor_id += 1
                    self.corridors[corridor_id] = BridgeCorridor(
                        identifier=corridor_id,
                        island_a=island.identifier,
                        island_b=self._island_lookup[pos],
                        direction=Direction.HORIZONTAL,
                        cells=tuple(cells),
                    )
                    break
                if self._matrix[island.row][c] != 0:
                    break  # blocked by implicit obstacle
                cells.append(pos)
                c += 1
            # vertical scanning downward
            r = island.row + 1
            cells = []
            while r < self.height:
                pos = (r, island.col)
                if pos in self._island_lookup:
                    corridor_id += 1
                    self.corridors[corridor_id] = BridgeCorridor(
                        identifier=corridor_id,
                        island_a=island.identifier,
                        island_b=self._island_lookup[pos],
                        direction=Direction.VERTICAL,
                        cells=tuple(cells),
                    )
                    break
                if self._matrix[r][island.col] != 0:
                    break
                cells.append(pos)
                r += 1

    def matrix(self) -> Tuple[Tuple[int, ...], ...]:
        return self._matrix

    def neighbors(self, island_id: int) -> Iterable[int]:
        for corridor in self.corridors.values():
            if corridor.island_a == island_id:
                yield corridor.island_b
            elif corridor.island_b == island_id:
                yield corridor.island_a

    def corridors_incident_to(self, island_id: int) -> List[BridgeCorridor]:
        return [
            c
            for c in self.corridors.values()
            if c.island_a == island_id or c.island_b == island_id
        ]

    def corridor_between(self, island_a: int, island_b: int) -> BridgeCorridor | None:
        for corridor in self.corridors.values():
            if {corridor.island_a, corridor.island_b} == {island_a, island_b}:
                return corridor
        return None

    def cell_contains_island(self, row: int, col: int) -> bool:
        return (row, col) in self._island_lookup

    def cell_index(self, row: int, col: int) -> int | None:
        return self._island_lookup.get((row, col))

    def cells(self) -> Iterable[Tuple[int, int]]:
        for r in range(self.height):
            for c in range(self.width):
                yield r, c
