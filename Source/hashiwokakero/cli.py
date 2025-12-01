"""Command-line interface for the Hashiwokakero solver."""

import argparse
import sys
from pathlib import Path

from .benchmark import BenchmarkRunner
from .loader import PuzzleLoader
from .renderer import Renderer


def run_cli():
    parser = argparse.ArgumentParser(description="Hashiwokakero Solver Benchmark")
    parser.add_argument("input_file", help="Path to the input puzzle file (txt)")
    parser.add_argument("--output", "-o", help="Path to save the output solution", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed solution to stdout")

    args = parser.parse_args()
    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    print(f"Loading puzzle from {input_path}...")
    try:
        grid = PuzzleLoader.load(input_path)
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        sys.exit(1)

    print(f"Grid size: {grid.width}x{grid.height}, Islands: {len(grid.islands)}, Corridors: {len(grid.corridors)}")
    print("-" * 60)
    print(f"{'Algorithm':<15} | {'Status':<10} | {'Time (s)':<10} | {'Metrics'}")
    print("-" * 60)

    runner = BenchmarkRunner(grid)
    results = runner.run_all()

    best_result = None

    for res in results:
        metrics_str = ", ".join(f"{k}={v}" for k, v in res.metrics.items())
        print(f"{res.algorithm:<15} | {res.status:<10} | {res.time_seconds:<10.4f} | {metrics_str}")
        
        if res.status == "SAT" or res.status == "SOLVED":
            if best_result is None:
                best_result = res

    print("-" * 60)

    if best_result and best_result.solution:
        renderer = Renderer(best_result.solution)
        output_text = renderer.render()
        
        if args.verbose:
            print("\nSolution:")
            print(output_text)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_text, encoding="utf-8")
            print(f"\nSolution saved to {output_path}")
        elif not args.verbose:
             print("\n(Use --verbose to see solution or --output to save to file)")

    else:
        print("\nNo solution found by any algorithm.")

if __name__ == "__main__":
    run_cli()
