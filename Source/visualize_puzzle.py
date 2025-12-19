import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argparse
import ast
import sys
from pathlib import Path

def parse_input(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    grid = []
    for line in lines:
        if not line.strip(): continue
        # Remove spaces and split by comma
        row = [int(x.strip()) for x in line.strip().split(',')]
        grid.append(row)
    return grid

def parse_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    grid = []
    for line in lines:
        if not line.strip(): continue
        try:
            # Try to parse as python list
            row = ast.literal_eval(line.strip())
            grid.append(row)
        except:
            # Fallback manual parsing
            clean_line = line.strip().strip('[]')
            parts = [p.strip().strip('"\'') for p in clean_line.split(',')]
            grid.append(parts)
    return grid

def draw_grid(ax, grid, title, is_output=False):
    height = len(grid)
    width = len(grid[0])
    
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(height - 0.5, -0.5) # Invert y axis
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=16, pad=20)

    # Draw grid lines
    for x in range(width + 1):
        ax.axvline(x - 0.5, color='#EEEEEE', lw=1)
    for y in range(height + 1):
        ax.axhline(y - 0.5, color='#EEEEEE', lw=1)

    # Draw bridges first (so they are under islands)
    if is_output:
        for y in range(height):
            for x in range(width):
                cell = str(grid[y][x])
                
                if cell == '-': # Single Horizontal
                    ax.plot([x-1, x+1], [y, y], color='#333333', lw=2, zorder=1)
                elif cell == '=': # Double Horizontal
                    ax.plot([x-1, x+1], [y-0.1, y-0.1], color='#333333', lw=2, zorder=1)
                    ax.plot([x-1, x+1], [y+0.1, y+0.1], color='#333333', lw=2, zorder=1)
                elif cell == '|': # Single Vertical
                    ax.plot([x, x], [y-1, y+1], color='#333333', lw=2, zorder=1)
                elif cell in ['"', '$']: # Double Vertical
                    ax.plot([x-0.1, x-0.1], [y-1, y+1], color='#333333', lw=2, zorder=1)
                    ax.plot([x+0.1, x+0.1], [y-1, y+1], color='#333333', lw=2, zorder=1)

    # Draw islands
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            val = str(cell)
            
            is_island = False
            if is_output:
                if val.isdigit() and val != '0':
                    is_island = True
            else:
                if isinstance(cell, int) and cell > 0:
                    is_island = True
                    val = str(cell)
            
            if is_island:
                circle = patches.Circle((x, y), 0.4, edgecolor='black', facecolor='white', lw=1.5, zorder=2)
                ax.add_patch(circle)
                ax.text(x, y, val, ha='center', va='center', fontsize=14, fontweight='bold', zorder=3)

def visualize(input_file, output_file, save_path=None):
    try:
        input_grid = parse_input(input_file)
        output_grid = parse_output(output_file)
    except Exception as e:
        print(f"Error parsing files: {e}")
        sys.exit(1)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    draw_grid(axes[0], input_grid, "Input Puzzle")
    draw_grid(axes[1], output_grid, "Solved Puzzle", is_output=True)
    
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.3)
    
    if save_path:
        save_p = Path(save_path)
        # If path is a directory or has no extension, treat as directory
        if save_p.suffix == '':
            save_p.mkdir(parents=True, exist_ok=True)
            input_name = Path(input_file).stem
            save_p = save_p / f"{input_name}_viz.png"
        else:
            save_p.parent.mkdir(parents=True, exist_ok=True)
            
        plt.savefig(save_p)
        print(f"Visualization saved to {save_p}")
        plt.close()
    else:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize Hashiwokakero Puzzle")
    parser.add_argument("input_file", nargs='?', help="Path to input file")
    parser.add_argument("output_file", nargs='?', help="Path to output file")
    parser.add_argument("--save", help="Path/Directory to save the visualization image", default=None)
    args = parser.parse_args()
    
    if not args.input_file:
        # Batch mode: Process all files in Inputs/Outputs
        current_dir = Path(__file__).parent
        inputs_dir = current_dir / "Inputs"
        outputs_dir = current_dir / "Outputs"
        viz_dir = current_dir / "Plots" / "Puzzles"
        
        if not inputs_dir.exists():
            print(f"Error: Inputs directory not found at {inputs_dir}")
            sys.exit(1)
            
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all input files
        input_files = sorted(list(inputs_dir.glob("input-*.txt")))
        
        if not input_files:
            print("No input files found.")
            sys.exit(0)
            
        print(f"Found {len(input_files)} input files. Generating visualizations in {viz_dir}...")
        
        count = 0
        for in_file in input_files:
            # Determine output filename: input-01.txt -> output-01.txt
            out_name = in_file.name.replace("input", "output")
            out_file = outputs_dir / out_name
            
            if out_file.exists():
                print(f"Visualizing {in_file.name}...")
                try:
                    visualize(str(in_file), str(out_file), str(viz_dir))
                    count += 1
                except Exception as e:
                    print(f"Failed to visualize {in_file.name}: {e}")
            else:
                print(f"Skipping {in_file.name}: Output file {out_name} not found.")
                
        print(f"Done. Generated {count} visualizations.")
        
    elif args.input_file and args.output_file:
        # Single file mode
        visualize(args.input_file, args.output_file, args.save)
    else:
        print("Error: Please provide both input and output files for single mode, or no arguments for batch mode.")
        parser.print_help()
