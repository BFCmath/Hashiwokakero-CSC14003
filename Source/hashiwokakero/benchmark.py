"""Benchmark runner for comparing solver performance."""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass
from typing import Any, Dict, List

from .checker import ConstraintChecker
from .grid import Grid
from .sat_solver import PySatSolver
from .solvers.astar import AStarFCSolver
from .solvers.backtracking import BacktrackingSolver, BacktrackingFCSolver
from .solvers.bruteforce import BruteForceSolver
from .state import PuzzleState
from .solvers.astar import Heuristic

@dataclass
class BenchmarkResult:
    algorithm: str
    status: str
    time_seconds: float
    memory_peak_mb: float
    metrics: Dict[str, Any]
    solution: PuzzleState | None


class BenchmarkRunner:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.checker = ConstraintChecker(grid)

    def run_all(self) -> List[BenchmarkResult]:
        results = []
        results.append(self.run_pysat())
        
        # Run A* variants
        results.append(self.run_astar_variant("A* (Composite)", Heuristic.composite))
        results.append(self.run_astar_variant("A* (Deficit)", Heuristic.deficit))
        results.append(self.run_astar_variant("A* (MinConn)", Heuristic.min_conn))
        results.append(self.run_astar_variant("A* (Bottleneck)", Heuristic.bottleneck_corrected))

        # results.append(self.run_backtracking())
        results.append(self.run_backtracking_fc())
        # Brute force is often too slow for non-trivial puzzles, so we might want to skip it or warn
        # For now, we include it but users should be careful with large inputs
        results.append(self.run_bruteforce())
        return results

    def _run_with_profiling(self, name: str, func) -> BenchmarkResult:
        tracemalloc.start()
        start_time = time.perf_counter()
        try:
            result_obj = func()
            elapsed = time.perf_counter() - start_time
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            peak_mb = peak / (1024 * 1024)
            
            # Extract common fields from result object (assuming they all have status, etc.)
            # But the solvers return different result objects.
            # We need to adapt based on the solver return type.
            
            # Actually, the original code called specific methods that returned BenchmarkResult.
            # I should refactor those methods to use this helper or just add profiling inside them.
            # Adding inside them is safer to avoid changing too much logic at once.
            pass
        except Exception:
            tracemalloc.stop()
            raise

    def run_pysat(self) -> BenchmarkResult:
        solver = PySatSolver()
        tracemalloc.start()
        try:
            result = solver.solve(self.grid)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return BenchmarkResult(
                algorithm="PySAT",
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"iterations": result.iterations},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            import traceback
            return BenchmarkResult("PySAT", "ERROR", 0.0, 0.0, {"error": str(e), "traceback": traceback.format_exc()}, None)

    def run_astar_variant(self, name: str, heuristic_func) -> BenchmarkResult:
        solver = AStarFCSolver(self.checker, heuristic=heuristic_func)
        initial_state = PuzzleState(self.grid)
        tracemalloc.start()
        try:
            result = solver.solve(initial_state)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return BenchmarkResult(
                algorithm=name,
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"expanded_nodes": result.expanded},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            return BenchmarkResult(name, "ERROR", 0.0, 0.0, {"error": str(e)}, None)

    def run_backtracking(self) -> BenchmarkResult:
        if self.grid.height > 7:
             return BenchmarkResult(
                algorithm="Backtracking",
                status="SKIPPED",
                time_seconds=0.0,
                memory_peak_mb=0.0,
                metrics={"reason": " N > 7"},
                solution=None,
            )
        solver = BacktrackingSolver(self.grid, self.checker)
        tracemalloc.start()
        try:
            result = solver.solve()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return BenchmarkResult(
                algorithm="Backtracking",
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"explored_nodes": result.explored},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            return BenchmarkResult("Backtracking", "ERROR", 0.0, 0.0, {"error": str(e)}, None)

    def run_backtracking_fc(self) -> BenchmarkResult:
        """Run Backtracking with Forward Checking."""
        if self.grid.height > 13:
             return BenchmarkResult(
                algorithm="Backtracking",
                status="SKIPPED",
                time_seconds=0.0,
                memory_peak_mb=0.0,
                metrics={"reason": " N > 13"},
                solution=None,
            )
        solver = BacktrackingFCSolver(self.grid, self.checker)
        tracemalloc.start()
        try:
            result = solver.solve()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return BenchmarkResult(
                algorithm="Backtracking+FC",
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"explored_nodes": result.explored},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            return BenchmarkResult("Backtracking+FC", "ERROR", 0.0, 0.0, {"error": str(e)}, None)

    def run_bruteforce(self) -> BenchmarkResult:
        if self.grid.height > 7:
             return BenchmarkResult(
                algorithm="BruteForce",
                status="SKIPPED",
                time_seconds=0.0,
                memory_peak_mb=0.0,
                metrics={"reason": " N > 7"},
                solution=None,
            )
        solver = BruteForceSolver(self.grid, self.checker)
        tracemalloc.start()
        try:
            result = solver.solve()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return BenchmarkResult(
                algorithm="BruteForce",
                status=result.status,
                time_seconds=result.elapsed,
                memory_peak_mb=peak / (1024 * 1024),
                metrics={"visited_states": result.visited},
                solution=result.state,
            )
        except Exception as e:
            tracemalloc.stop()
            return BenchmarkResult("BruteForce", "ERROR", 0.0, 0.0, {"error": str(e)}, None)
