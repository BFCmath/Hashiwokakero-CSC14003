import sys
import os
import csv
import re
import time
import argparse
from pathlib import Path

# Add Source to sys.path
current_dir = Path(__file__).parent
source_dir = current_dir / "Source"
sys.path.append(str(source_dir))

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not found. Plots will not be generated.")
    MATPLOTLIB_AVAILABLE = False

try:
    from hashiwokakero.loader import PuzzleLoader
    from hashiwokakero.benchmark import BenchmarkRunner
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
    parser = argparse.ArgumentParser(description="Run benchmark suite")
    parser.add_argument("--limit", type=int, help="Limit number of files to run")
    parser.add_argument("--file", type=str, help="Specific file name to run (e.g. input-01.txt)")
    args = parser.parse_args()

    inputs_dir = source_dir / "Inputs"
    plots_dir = current_dir / "Plots"
    plots_dir.mkdir(exist_ok=True)
    
    csv_path = plots_dir / "benchmark_results.csv"
    
    input_files = get_input_files(inputs_dir)

    if args.file:
        input_files = [f for f in input_files if f.name == args.file]
        if not input_files:
            print(f"File {args.file} not found in {inputs_dir}")
            return
    elif args.limit:
        input_files = input_files[:args.limit]
    
    if not input_files:
        print(f"No input files found in {inputs_dir}")
        return

    print(f"Found {len(input_files)} input files.")
    
    # Data structure for plotting:
    # { algorithm_name: [(num_islands, time, memory, nodes_visited, total_bridges), ...] }
    plot_data = {} 
    
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Input Name', 'Grid Size', 'Num Islands', 'Total Bridges', 'Algorithm', 'Time (s)', 'Memory (MB)', 'Nodes/Steps', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, file_path in enumerate(input_files):
            print(f"\nProcessing {file_path.name} ({i+1}/{len(input_files)})...")
            
            try:
                grid = PuzzleLoader.load(file_path)
                num_islands = len(grid.islands)
                # Calculate total bridges (sum of numbers on islands)
                # grid.islands is a Dict[int, Island], so we need to iterate over values
                total_bridges = sum(island.target for island in grid.islands.values())
                grid_size = f"{grid.width}x{grid.height}"
                
                print(f"Grid size: {grid.width}x{grid.height}, Islands: {len(grid.islands)}, Total Bridges: {total_bridges}")
                print("-" * 115)
                print(f"{'Algorithm':<15} | {'Status':<10} | {'Time (s)':<10} | {'Mem (MB)':<10} | {'Nodes':<10} | {'Metrics'}")
                print("-" * 115)

                runner = BenchmarkRunner(grid)
                results = runner.run_all()
                
                for result in results:
                    # Try to extract a "complexity" metric (nodes, steps, backtracks)
                    nodes_count = 0
                    for key in ['nodes', 'visited', 'backtracks', 'steps', 'recursive_calls', 'expanded_nodes', 'explored_nodes', 'visited_states', 'iterations']:
                        if key in result.metrics:
                            nodes_count = result.metrics[key]
                            break
                    
                    metrics_str = ", ".join(f"{k}={v}" for k, v in result.metrics.items())
                    print(f"{result.algorithm:<15} | {result.status:<10} | {result.time_seconds:<10.4f} | {result.memory_peak_mb:<10.2f} | {nodes_count:<10} | {metrics_str}")

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
                    
                    if result.status == "SOLVED" or result.status == "SAT":
                        if result.algorithm not in plot_data:
                            plot_data[result.algorithm] = []
                        # Store tuple: (num_islands, time, memory, nodes, total_bridges)
                        plot_data[result.algorithm].append((num_islands, result.time_seconds, result.memory_peak_mb, nodes_count, total_bridges))
                
                print("-" * 115)
                        
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

    print(f"Benchmark data saved to {csv_path}")

    if MATPLOTLIB_AVAILABLE:
        generate_plots(plot_data, plots_dir)

def generate_plots(plot_data, output_dir):
    # 1. Time vs Islands (Linear)
    plt.figure(figsize=(10, 6))
    for algo, data in plot_data.items():
        # Sort data by num_islands
        data.sort(key=lambda x: x[0])
        x = [d[0] for d in data]
        y = [d[1] for d in data]
        plt.plot(x, y, marker='o', label=algo)
    
    plt.xlabel('Number of Islands')
    plt.ylabel('Time (seconds)')
    plt.title('Algorithm Performance: Time vs Number of Islands')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_dir / "time_vs_islands.png")
    plt.close()

    # 2. Time vs Islands (Log Scale)
    plt.figure(figsize=(10, 6))
    for algo, data in plot_data.items():
        data.sort(key=lambda x: x[0])
        x = [d[0] for d in data]
        y = [d[1] for d in data]
        # Filter out 0 values for log scale
        y = [val if val > 0 else 0.0001 for val in y]
        plt.plot(x, y, marker='o', label=algo)
    
    plt.xlabel('Number of Islands')
    plt.ylabel('Time (seconds) - Log Scale')
    plt.yscale('log')
    plt.title('Time vs Number of Islands (Log Scale)')
    plt.legend()
    plt.grid(True, which="both", ls="-")
    plt.savefig(output_dir / "time_vs_islands_log.png")
    plt.close()
    
    # 3. Memory vs Islands
    plt.figure(figsize=(10, 6))
    for algo, data in plot_data.items():
        data.sort(key=lambda x: x[0])
        x = [d[0] for d in data]
        y = [d[2] for d in data]
        plt.plot(x, y, marker='o', label=algo)
        
    plt.xlabel('Number of Islands')
    plt.ylabel('Memory Peak (MB)')
    plt.title('Algorithm Performance: Memory vs Number of Islands')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_dir / "memory_vs_islands.png")
    plt.close()

    # 4. Nodes/Steps vs Islands (Log Scale)
    plt.figure(figsize=(10, 6))
    for algo, data in plot_data.items():
        data.sort(key=lambda x: x[0])
        x = [d[0] for d in data]
        y = [d[3] for d in data] # nodes is index 3
        # Filter out 0 values
        y = [val if val > 0 else 1 for val in y]
        plt.plot(x, y, marker='o', label=algo)
        
    plt.xlabel('Number of Islands')
    plt.ylabel('Nodes Visited / Steps (Log Scale)')
    plt.yscale('log')
    plt.title('Search Efficiency: Nodes Visited vs Islands')
    plt.legend()
    plt.grid(True, which="both", ls="-")
    plt.savefig(output_dir / "nodes_vs_islands.png")
    plt.close()

    # 5. Time vs Total Bridges (Complexity)
    plt.figure(figsize=(10, 6))
    for algo, data in plot_data.items():
        # Sort by total_bridges (index 4)
        data_sorted = sorted(data, key=lambda x: x[4])
        x = [d[4] for d in data_sorted]
        y = [d[1] for d in data_sorted] # Time
        plt.plot(x, y, marker='o', linestyle='None', label=algo) # Scatter plot might be better here
    
    plt.xlabel('Total Bridges (Sum of Island Numbers)')
    plt.ylabel('Time (seconds)')
    plt.title('Time vs Problem Complexity (Total Bridges)')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_dir / "time_vs_bridges.png")
    plt.close()
    
    print(f"Plots saved to {output_dir}")

if __name__ == "__main__":
    main()
