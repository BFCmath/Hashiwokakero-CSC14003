import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_and_prep_data(csv_path):
    """Loads the benchmark CSV and prepares it for plotting."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}. Please run the benchmark suite first.")
        return None

    # Extract a numeric value for sorting Grid Size (e.g., "7x7" -> 7)
    # Handle cases where Grid Size might not be in "NxN" format just in case
    def extract_dim(x):
        try:
            return int(str(x).split('x')[0])
        except:
            return 0
            
    df['Grid Dimension'] = df['Grid Size'].apply(extract_dim)
    
    # Sort the DataFrame by Grid Dimension to ensure plots are ordered correctly
    df = df.sort_values('Grid Dimension')
    
    return df

def generate_visualizations(df, output_dir):
    """Generates the 6 requested plots."""
    # Set style
    sns.set_theme(style="whitegrid")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Islands vs Time
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Num Islands', y='Time (s)', hue='Algorithm', marker='o')
    plt.title('Islands vs Execution Time')
    plt.savefig(output_dir / '1_islands_vs_time.png')
    plt.close()

    # ---------------------------------------------------------
    # 2. Islands vs Time (Log Scale)
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Num Islands', y='Time (s)', hue='Algorithm', marker='o')
    plt.yscale('log')
    plt.title('Islands vs Execution Time (Log Scale)')
    plt.savefig(output_dir / '2_islands_vs_time_log.png')
    plt.close()

    # ---------------------------------------------------------
    # 3. Islands vs Node Expanded
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Num Islands', y='Nodes/Steps', hue='Algorithm', marker='o')
    plt.title('Islands vs Nodes Expanded')
    plt.savefig(output_dir / '3_islands_vs_nodes.png')
    plt.close()

    # ---------------------------------------------------------
    # 4. Islands vs Memory
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Num Islands', y='Memory (MB)', hue='Algorithm', marker='o')
    plt.title('Islands vs Memory Usage')
    plt.savefig(output_dir / '4_islands_vs_memory.png')
    plt.close()

    # ---------------------------------------------------------
    # 5. Grid Size vs Execution Time
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Grid Dimension', y='Time (s)', hue='Algorithm', marker='o')
    plt.title('Grid Size vs Execution Time')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '5_grid_size_vs_time.png')
    plt.close()

    # ---------------------------------------------------------
    # 6. Grid Size vs Execution Time (Log Scale)
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Grid Dimension', y='Time (s)', hue='Algorithm', marker='o')
    plt.yscale('log')
    plt.title('Grid Size vs Execution Time (Log Scale)')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '6_grid_size_vs_time_log.png')
    plt.close()

    # ---------------------------------------------------------
    # 7. Grid Size vs Node Expanded
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Grid Dimension', y='Nodes/Steps', hue='Algorithm', marker='o')
    plt.title('Grid Size vs Nodes Expanded')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '7_grid_size_vs_nodes.png')
    plt.close()

    # ---------------------------------------------------------
    # 8. Grid Size vs Memory
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='Grid Dimension', y='Memory (MB)', hue='Algorithm', marker='o')
    plt.title('Grid Size vs Memory Usage')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '8_grid_size_vs_memory.png')
    plt.close()

    # ---------------------------------------------------------
    # 9. Performance Heatmap: Execution Time
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 6))
    # Pivot data: Rows=Algorithm, Cols=Grid Size, Values=Time
    heatmap_data = df.pivot_table(index='Algorithm', columns='Grid Size', values='Time (s)', aggfunc='mean')
    
    # Sort columns by grid size
    sorted_cols = df['Grid Size'].unique()
    # Filter columns that exist in heatmap_data
    sorted_cols = [c for c in sorted_cols if c in heatmap_data.columns]
    heatmap_data = heatmap_data.reindex(columns=sorted_cols)

    sns.heatmap(heatmap_data, annot=True, fmt=".4f", cmap="YlOrRd", linewidths=.5, cbar_kws={'label': 'Time (s)'})
    plt.title('Performance Heatmap: Execution Time')
    plt.tight_layout()
    plt.savefig(output_dir / '9_performance_heatmap.png')
    plt.close()

    # ---------------------------------------------------------
    # 10. Heuristic Comparison (Bar Chart)
    # ---------------------------------------------------------
    # Filter only A* algorithms
    astar_df = df[df['Algorithm'].str.startswith('A*')]
    
    if not astar_df.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(data=astar_df, x='Algorithm', y='Time (s)', estimator=np.mean, errorbar=None)
        plt.title('Average Execution Time by Heuristic (A* Variants)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / '10_heuristic_comparison_time.png')
        plt.close()

        plt.figure(figsize=(12, 6))
        sns.barplot(data=astar_df, x='Algorithm', y='Nodes/Steps', estimator=np.mean, errorbar=None)
        plt.title('Average Nodes Expanded by Heuristic (A* Variants)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / '10_heuristic_comparison_nodes.png')
        plt.close()
    else:
        print("No A* algorithms found for heuristic comparison.")

def main():
    # Define paths relative to this script
    current_dir = Path(__file__).parent
    csv_path = current_dir / "Plots" / "benchmark_results.csv"
    output_dir = current_dir / "Plots" / "Analysis"
    
    print(f"Reading data from: {csv_path}")
    df = load_and_prep_data(csv_path)
    
    if df is not None:
        print(f"Generating plots in: {output_dir}")
        generate_visualizations(df, output_dir)
        print("Done! Check the output directory for the images.")

if __name__ == "__main__":
    main()
