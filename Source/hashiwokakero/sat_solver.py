"""SAT-based solver built on top of PySAT."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import List

from pysat.solvers import Solver

from .cnf_encoder import CNFEncoder
from .grid import Grid
from .inference import InferenceEngine
from .state import PuzzleState
from .variables import VariableRegistry


@dataclass
class SatResult:
    state: PuzzleState | None
    elapsed: float
    iterations: int
    status: str


class PySatSolver:
    def __init__(self, backend: str = "glucose4") -> None:
        self.backend = backend

    def solve(self, grid: Grid, enforce_connectivity: bool = True) -> SatResult:
        encoder = CNFEncoder(grid)
        encoding = encoder.build()
        engine = InferenceEngine(grid, encoding.registry)
        start = perf_counter()
        iterations = 0
        with Solver(name=self.backend, bootstrap_with=encoding.cnf.clauses) as solver:
            while True:
                iterations += 1
                if not solver.solve():
                    return SatResult(None, perf_counter() - start, iterations, "UNSAT")
                model = solver.get_model()
                state = engine.state_from_model(model)
                if not enforce_connectivity:
                    return SatResult(state, perf_counter() - start, iterations, "SAT")
                cuts = self._connectivity_clauses(grid, encoding.registry, state)
                if not cuts:
                    return SatResult(state, perf_counter() - start, iterations, "SAT")
                for clause in cuts:
                    solver.add_clause(clause)

    def _connectivity_clauses(
        self, grid: Grid, registry: VariableRegistry, state: PuzzleState
    ) -> List[List[int]]:
        islands = list(grid.islands.keys())
        if not islands:
            return []
        parent = {island: island for island in islands}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            parent[rb] = ra

        for corridor in grid.corridors.values():
            if state.corridor_value(corridor.identifier) == 0:
                continue
            union(corridor.island_a, corridor.island_b)

        root = find(islands[0])
        components = {}
        for island in islands:
            components.setdefault(find(island), []).append(island)
        if len(components) == 1:
            return []
        clauses: List[List[int]] = []
        for comp_root, members in components.items():
            if comp_root == root:
                continue
            literals: List[int] = []
            for corridor in grid.corridors.values():
                a_comp = find(corridor.island_a)
                b_comp = find(corridor.island_b)
                if {a_comp, b_comp} == {comp_root, root}:
                    literals.append(registry.var("corridor_active", corridor.identifier))
            if literals:
                clauses.append(literals)
        return clauses
