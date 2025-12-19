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
    
    # Replace 0 values with NaN for metrics where Status is SKIPPED or value is 0
    # This prevents lines from dropping to zero in plots, which is misleading
    metrics = ['Time (s)', 'Memory (MB)', 'Nodes/Steps']
    for col in metrics:
        if col in df.columns:
            # Set to NaN if Status is SKIPPED
            df.loc[df['Status'] == 'SKIPPED', col] = np.nan
            # Also set to NaN if value is 0 (to avoid log(0) issues and misleading drops)
            df.loc[df[col] == 0, col] = np.nan

    return df

def generate_visualizations(df, output_dir):
    """Generates the 6 requested plots."""
    # Set style
    sns.set_theme(style="whitegrid")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Common plotting arguments for consistency
    plot_kwargs = {
        'hue': 'Algorithm',
        'style': 'Algorithm',  # Different markers
        'markers': True,       # Different markers
        'dashes': False,       # Force solid lines
        'errorbar': None,     # Remove shaded confidence interval for clarity
        'linewidth': 2,        # Thicker lines
        'markersize': 8        # Larger markers
    }

    # ---------------------------------------------------------
    # 1. Islands vs Time
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Num Islands', y='Time (s)', **plot_kwargs)
    plt.title('Islands vs Execution Time')
    plt.savefig(output_dir / '1_islands_vs_time.png')
    plt.close()

    # ---------------------------------------------------------
    # 2. Islands vs Time (Log Scale)
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Num Islands', y='Time (s)', **plot_kwargs)
    plt.yscale('log')
    plt.title('Islands vs Execution Time (Log Scale)')
    plt.savefig(output_dir / '2_islands_vs_time_log.png')
    plt.close()

    # ---------------------------------------------------------
    # 3. Islands vs Node Expanded
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Num Islands', y='Nodes/Steps', **plot_kwargs)
    plt.title('Islands vs Nodes Expanded')
    plt.savefig(output_dir / '3_islands_vs_nodes.png')
    plt.close()

    # ---------------------------------------------------------
    # 4. Islands vs Memory
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Num Islands', y='Memory (MB)', **plot_kwargs)
    plt.title('Islands vs Memory Usage')
    plt.savefig(output_dir / '4_islands_vs_memory.png')
    plt.close()

    # ---------------------------------------------------------
    # 4b. Islands vs Memory (Log Scale)
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Num Islands', y='Memory (MB)', **plot_kwargs)
    plt.yscale('log')
    plt.title('Islands vs Memory Usage (Log Scale)')
    plt.savefig(output_dir / '4b_islands_vs_memory_log.png')
    plt.close()

    # ---------------------------------------------------------
    # 5. Grid Size vs Execution Time
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Grid Dimension', y='Time (s)', **plot_kwargs)
    plt.title('Grid Size vs Execution Time')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '5_grid_size_vs_time.png')
    plt.close()

    # ---------------------------------------------------------
    # 6. Grid Size vs Execution Time (Log Scale)
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Grid Dimension', y='Time (s)', **plot_kwargs)
    plt.yscale('log')
    plt.title('Grid Size vs Execution Time (Log Scale)')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '6_grid_size_vs_time_log.png')
    plt.close()

    # ---------------------------------------------------------
    # 7. Grid Size vs Node Expanded
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Grid Dimension', y='Nodes/Steps', **plot_kwargs)
    plt.title('Grid Size vs Nodes Expanded')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '7_grid_size_vs_nodes.png')
    plt.close()

    # ---------------------------------------------------------
    # 8. Grid Size vs Memory
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Grid Dimension', y='Memory (MB)', **plot_kwargs)
    plt.title('Grid Size vs Memory Usage')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '8_grid_size_vs_memory.png')
    plt.close()

    # ---------------------------------------------------------
    # 8b. Grid Size vs Memory (Log Scale)
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='Grid Dimension', y='Memory (MB)', **plot_kwargs)
    plt.yscale('log')
    plt.title('Grid Size vs Memory Usage (Log Scale)')
    plt.xlabel('Grid Dimension (N for NxN)')
    plt.savefig(output_dir / '8b_grid_size_vs_memory_log.png')
    plt.close()

    # ---------------------------------------------------------
    # 9. Performance Heatmap: Execution Time
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 6))
    
    # Filter out SKIPPED runs so they become NaN in pivot_table
    df_heatmap = df[df['Status'] != 'SKIPPED']
    
    # Pivot data: Rows=Algorithm, Cols=Grid Size, Values=Time
    heatmap_data = df_heatmap.pivot_table(index='Algorithm', columns='Grid Size', values='Time (s)', aggfunc='mean')
    
    # Sort columns by grid size
    sorted_cols = df['Grid Size'].unique()
    # Reindex to ensure all grid sizes are present
    heatmap_data = heatmap_data.reindex(columns=sorted_cols)

    # Fill NaNs with -1 for coloring purposes (so they are not masked)
    heatmap_plot_data = heatmap_data.fillna(-1)
    
    # Create annotation matrix
    annot_data = heatmap_plot_data.apply(lambda col: col.map(lambda x: "Skip" if x == -1 else f"{x:.4f}"))

    # Custom colormap: Use 'lightgray' for values below vmin (i.e., -1)
    cmap = sns.color_palette("YlOrRd", as_cmap=True).copy()
    cmap.set_under('lightgray')

    # Plot with vmin=0 so -1 falls into 'under' color
    sns.heatmap(heatmap_plot_data, annot=annot_data, fmt="", cmap=cmap, 
                linewidths=.5, cbar_kws={'label': 'Time (s)'}, vmin=0)
    
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
        # Time Comparison
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(data=astar_df, x='Algorithm', y='Time (s)', hue='Algorithm', estimator=np.mean, errorbar=None, palette='viridis', legend=False)
        plt.title('Average Execution Time by Heuristic (A* Variants)')
        plt.xticks(rotation=0)
        # Add value labels on top of bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.4f', padding=3)
        plt.tight_layout()
        plt.savefig(output_dir / '10_heuristic_comparison_time.png')
        plt.close()

        # Nodes Comparison
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(data=astar_df, x='Algorithm', y='Nodes/Steps', hue='Algorithm', estimator=np.mean, errorbar=None, palette='viridis', legend=False)
        plt.title('Average Nodes Expanded by Heuristic (A* Variants)')
        plt.xticks(rotation=0)
        # Add value labels on top of bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', padding=3)
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
