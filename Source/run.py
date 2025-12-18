import sys
import os
import csv
import re
import time
import argparse
from pathlib import Path

# Add Source to sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from hashiwokakero.loader import PuzzleLoader
    from hashiwokakero.benchmark import BenchmarkRunner
    from hashiwokakero.renderer import Renderer # Import Renderer for visualization
except ImportError as e:
    print(f"Error importing project modules: {e}")
    sys.exit(1)

def get_input_files(inputs_dir):
    files = list(inputs_dir.glob("input-*.txt"))
    # Sort by number in filename
    def extract_number(path):
        match = re.search(r"input-(\d+)\.txt", path.name)
        return int(match.group(1)) if match else 0
    
    return sorted(files, key=extract_number)

def main():
    parser = argparse.ArgumentParser(description="Run benchmark suite or solve single puzzle")
    
    # Benchmark selection arguments
    parser.add_argument("--limit", type=int, help="Limit number of files to run")
    parser.add_argument("--file", type=str, help="Specific file name or path to run (e.g. input-01.txt)")
    parser.add_argument("--start", type=int, help="Start index (1-based) of files to run")
    parser.add_argument("--end", type=int, help="End index (1-based) of files to run")
    
    # Single run / Output argument
    parser.add_argument("--output", "-o", help="Path to save the output solution (txt)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed solution to stdout")
    parser.add_argument("--no-csv", action="store_true", help="Do not save results to CSV (useful for single runs)")

    args = parser.parse_args()

    inputs_dir = current_dir / "Inputs"
    plots_dir = current_dir / "Plots"
    plots_dir.mkdir(exist_ok=True)
    
    csv_path = plots_dir / "benchmark_results.csv"
    
    input_files = get_input_files(inputs_dir)

    # Handle file selection
    if args.file:
        # Check if it's a direct path
        if os.path.exists(args.file):
            input_files = [Path(args.file)]
        else:
            # Check if it's a filename in Inputs dir
            filtered = [f for f in input_files if f.name == args.file]
            if not filtered:
                print(f"File {args.file} not found in {inputs_dir} or current directory.")
                return
            input_files = filtered
    else:
        # Range selection logic
        start_idx = 0
        end_idx = len(input_files)
        
        if args.start:
            start_idx = max(0, args.start - 1)
        
        if args.end:
            end_idx = min(len(input_files), args.end)
            
        if args.limit:
            end_idx = min(end_idx, start_idx + args.limit)
            
        input_files = input_files[start_idx:end_idx]
    
    if not input_files:
        print(f"No input files found.")
        return

    print(f"Found {len(input_files)} input files to process.")
    
    # Prepare CSV writing
    write_csv = not args.no_csv
    csv_file = None
    writer = None
    
    if write_csv:
        # Warning if overwriting in single file mode
        if len(input_files) == 1 and csv_path.exists():
            print(f"Warning: Overwriting {csv_path} with single file result. Use --no-csv to prevent this.")
            
        csv_file = open(csv_path, 'w', newline='')
        fieldnames = ['Input Name', 'Grid Size', 'Num Islands', 'Total Bridges', 'Algorithm', 'Time (s)', 'Memory (MB)', 'Nodes/Steps', 'Status']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
    # Main Processing Loop
    for i, file_path in enumerate(input_files):
        print(f"\nProcessing {file_path.name} ({i+1}/{len(input_files)})...")
        
        try:
            grid = PuzzleLoader.load(file_path)
            num_islands = len(grid.islands)
            total_bridges = sum(island.target for island in grid.islands.values())
            grid_size = f"{grid.width}x{grid.height}"
            
            print(f"Grid size: {grid.width}x{grid.height}, Islands: {len(grid.islands)}, Total Bridges: {total_bridges}")
            print("-" * 115)
            print(f"{'Algorithm':<15} | {'Status':<10} | {'Time (s)':<10} | {'Mem (MB)':<10} | {'Nodes':<10} | {'Metrics'}")
            print("-" * 115)

            runner = BenchmarkRunner(grid)
            results = runner.run_all()
            
            best_result = None

            for result in results:
                # Extract metrics
                nodes_count = 0
                for key in ['nodes', 'visited', 'backtracks', 'steps', 'recursive_calls', 'expanded_nodes', 'explored_nodes', 'visited_states', 'iterations']:
                    if key in result.metrics:
                        nodes_count = result.metrics[key]
                        break
                
                metrics_str = ", ".join(f"{k}={v}" for k, v in result.metrics.items())
                print(f"{result.algorithm:<15} | {result.status:<10} | {result.time_seconds:<10.4f} | {result.memory_peak_mb:<10.2f} | {nodes_count:<10} | {metrics_str}")

                # Write to CSV
                if write_csv:
                    writer.writerow({
                        'Input Name': file_path.name,
                        'Grid Size': grid_size,
                        'Num Islands': num_islands,
                        'Total Bridges': total_bridges,
                        'Algorithm': result.algorithm,
                        'Time (s)': result.time_seconds,
                        'Memory (MB)': result.memory_peak_mb,
                        'Nodes/Steps': nodes_count,
                        'Status': result.status
                    })
                
                # Track best result for rendering
                if result.status in ["SOLVED", "SAT"]:
                    # Prefer A* or Backtracking over others if multiple solved, or just take the first one
                    if best_result is None:
                        best_result = result
            
            print("-" * 115)

            # Rendering Logic
            if best_result and best_result.solution:
                renderer = Renderer(best_result.solution)
                output_text = renderer.render()
                
                if args.verbose:
                    print("\nSolution Visualization:")
                    print(output_text)
                
                # Determine output path
                if args.output:
                    # If processing multiple files, we might need unique names, but usually --output is used with --file
                    out_path = Path(args.output)
                    if len(input_files) > 1:
                        # Append filename to directory if multiple files
                        if out_path.is_dir() or (not out_path.suffix):
                            out_path.mkdir(parents=True, exist_ok=True)
                            out_path = out_path / f"output-{file_path.stem}.txt"
                else:
                    # Default behavior: Save to Outputs/output-xx.txt
                    outputs_dir = current_dir / "Outputs"
                    outputs_dir.mkdir(exist_ok=True)
                    # Replace 'input' with 'output' in filename if present, else prepend
                    name_part = file_path.stem.replace("input", "output") if "input" in file_path.stem else f"output-{file_path.stem}"
                    out_path = outputs_dir / f"{name_part}.txt"
                    
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(output_text, encoding="utf-8")
                print(f"Solution saved to {out_path}")

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

    if write_csv:
        csv_file.close()
        print(f"\nBenchmark data saved to {csv_path}")
        print("To generate plots, run: python visualize_plots.py")

if __name__ == "__main__":
    main()
