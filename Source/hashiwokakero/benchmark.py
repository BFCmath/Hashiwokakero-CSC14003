"""Benchmark runner for comparing solver performance."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List

from .checker import ConstraintChecker
from .grid import Grid
from .sat_solver import PySatSolver
from .solvers.astar import AStarSolver
from .solvers.backtracking import BacktrackingSolver, BacktrackingFCSolver
from .solvers.bruteforce import BruteForceSolver
from .state import PuzzleState
from .solvers.astar import Heuristic

@dataclass
class BenchmarkResult:
    algorithm: str
    status: str
    time_seconds: float
    metrics: Dict[str, Any]
    solution: PuzzleState | None


class BenchmarkRunner:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.checker = ConstraintChecker(grid)

    def run_all(self) -> List[BenchmarkResult]:
        results = []
        results.append(self.run_pysat())
        results.append(self.run_astar())
        results.append(self.run_backtracking())
        results.append(self.run_backtracking_fc())
        # Brute force is often too slow for non-trivial puzzles, so we might want to skip it or warn
        # For now, we include it but users should be careful with large inputs
        results.append(self.run_bruteforce())
        return results

    def run_pysat(self) -> BenchmarkResult:
        solver = PySatSolver()
        try:
            result = solver.solve(self.grid)
            return BenchmarkResult(
                algorithm="PySAT",
                status=result.status,
                time_seconds=result.elapsed,
                metrics={"iterations": result.iterations},
                solution=result.state,
            )
        except Exception as e:
            import traceback
            return BenchmarkResult("PySAT", "ERROR", 0.0, {"error": str(e), "traceback": traceback.format_exc()}, None)

    def run_astar(self) -> BenchmarkResult:
        solver = AStarSolver(self.checker, heuristic=Heuristic.composite)
        initial_state = PuzzleState(self.grid)
        try:
            result = solver.solve(initial_state)
            return BenchmarkResult(
                algorithm="A*",
                status=result.status,
                time_seconds=result.elapsed,
                metrics={"expanded_nodes": result.expanded},
                solution=result.state,                                                                                                                                                                                                                      
            )
        except Exception as e:
            return BenchmarkResult("A*", "ERROR", 0.0, {"error": str(e)}, None)

    def run_backtracking(self) -> BenchmarkResult:
        if self.grid.height > 7:
             return BenchmarkResult(
                algorithm="Backtracking",
                status="SKIPPED",
                time_seconds=0.0,
                metrics={"reason": " N > 7"},
                solution=None,
            )
        solver = BacktrackingSolver(self.grid, self.checker)
        try:
            result = solver.solve()
            return BenchmarkResult(
                algorithm="Backtracking",
                status=result.status,
                time_seconds=result.elapsed,
                metrics={"explored_nodes": result.explored},
                solution=result.state,
            )
        except Exception as e:
            return BenchmarkResult("Backtracking", "ERROR", 0.0, {"error": str(e)}, None)

    def run_backtracking_fc(self) -> BenchmarkResult:
        """Run Backtracking with Forward Checking."""
        if self.grid.height > 13:
             return BenchmarkResult(
                algorithm="Backtracking+FC",
                status="SKIPPED",
                time_seconds=0.0,
                metrics={"reason": " N > 13"},
                solution=None,
            )
        solver = BacktrackingFCSolver(self.grid, self.checker)
        try:
            result = solver.solve()
            return BenchmarkResult(
                algorithm="Backtracking+FC",
                status=result.status,
                time_seconds=result.elapsed,
                metrics={"explored_nodes": result.explored},
                solution=result.state,
            )
        except Exception as e:
            return BenchmarkResult("Backtracking+FC", "ERROR", 0.0, {"error": str(e)}, None)

    def run_bruteforce(self) -> BenchmarkResult:
        if self.grid.height > 7:
             return BenchmarkResult(
                algorithm="BruteForce",
                status="SKIPPED",
                time_seconds=0.0,
                metrics={"reason": " N > 7"},
                solution=None,
            )

        solver = BruteForceSolver(self.grid, self.checker)
        try:
            result = solver.solve()
            return BenchmarkResult(
                algorithm="BruteForce",
                status=result.status,
                time_seconds=result.elapsed,
                metrics={"visited_nodes": result.visited},
                solution=result.state,
            )
        except Exception as e:
            return BenchmarkResult("BruteForce", "ERROR", 0.0, {"error": str(e)}, None)
