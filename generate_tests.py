#!/usr/bin/env python3
"""
Script to generate Hashiwokakero test puzzles.

Usage:
    # Generate a complete test suite (12 puzzles: 3 per difficulty level)
    python generate_tests.py --suite
    
    # Generate a single puzzle
    python generate_tests.py --seed 123 --difficulty medium
    
    # Generate with custom size
    python generate_tests.py --seed 456 --size 15 --output custom_puzzle.txt

Examples:
    python generate_tests.py --suite --seed 42 --suite-dir Source/Inputs
    python generate_tests.py --difficulty hard --seed 999
"""

import sys
from pathlib import Path

# Add Source directory to path
source_dir = Path(__file__).parent / "Source"
sys.path.insert(0, str(source_dir))

from hashiwokakero.test_generator import (
    TestGenerator,
    generate_test_suite,
    generate_single_puzzle,
    DIFFICULTY_CONFIGS,
)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Hashiwokakero test puzzles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --suite                          Generate 12 puzzles (3 per difficulty)
  %(prog)s --seed 123 --difficulty hard     Generate one hard puzzle
  %(prog)s --size 15 --seed 42              Generate a 15x15 puzzle
  %(prog)s --suite --tests-per-level 5      Generate 20 puzzles (5 per difficulty)
        """
    )
    
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--difficulty", type=str, default="medium",
        choices=["easy", "medium", "hard", "expert"],
        help="Puzzle difficulty level (default: medium)"
    )
    parser.add_argument(
        "--size", type=int, default=None,
        help="Custom grid size (overrides difficulty default)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output file path (default: print to stdout)"
    )
    parser.add_argument(
        "--suite", action="store_true",
        help="Generate a complete test suite instead of single puzzle"
    )
    parser.add_argument(
        "--suite-dir", type=str, default="Source/Inputs",
        help="Output directory for test suite (default: Source/Inputs)"
    )
    parser.add_argument(
        "--tests-per-level", type=int, default=3,
        help="Number of tests per difficulty level in suite (default: 3)"
    )
    parser.add_argument(
        "--show-solution", action="store_true",
        help="Also print the solution (bridges)"
    )
    parser.add_argument(
        "--info", action="store_true",
        help="Show difficulty configuration info and exit"
    )
    
    args = parser.parse_args()
    
    # Show info mode
    if args.info:
        print("Difficulty Configurations:")
        print("-" * 60)
        for name, config in DIFFICULTY_CONFIGS.items():
            print(f"\n{name.upper()}:")
            print(f"  Grid Size:        {config.size}x{config.size}")
            print(f"  Islands:          {config.min_islands}-{config.max_islands}")
            print(f"  Min Spacing:      {config.min_spacing}")
            print(f"  Double Bridge %:  {config.double_bridge_prob * 100:.0f}%")
            print(f"  Extra Bridge %:   {config.extra_bridge_prob * 100:.0f}%")
        return
    
    if args.suite:
        # Generate complete test suite
        print(f"Generating test suite with seed={args.seed}")
        print(f"Output directory: {args.suite_dir}")
        print(f"Tests per difficulty level: {args.tests_per_level}")
        print("-" * 50)
        
        files = generate_test_suite(
            base_seed=args.seed,
            output_dir=args.suite_dir,
            tests_per_difficulty=args.tests_per_level
        )
        
        print("-" * 50)
        print(f"Generated {len(files)} test files in {args.suite_dir}/")
        
    else:
        # Generate single puzzle
        puzzle = generate_single_puzzle(
            seed=args.seed,
            difficulty=args.difficulty,
            size=args.size
        )
        
        if args.output:
            puzzle.save(args.output)
            print(f"✓ Saved puzzle to {args.output}")
            print(f"  Seed:     {puzzle.seed}")
            print(f"  Size:     {puzzle.size}x{puzzle.size}")
            print(f"  Islands:  {len(puzzle.islands)}")
            print(f"  Bridges:  {len(puzzle.bridges)}")
            print(f"  Difficulty: {puzzle.difficulty}")
        else:
            # Print to stdout
            print(puzzle.to_input_format())
            
            if args.show_solution:
                print()
                print("# === SOLUTION (for verification) ===")
                for bridge in puzzle.bridges:
                    dir_str = "horizontal" if bridge.direction.value == "H" else "vertical"
                    print(f"# Bridge: Island {bridge.island_a} <-> Island {bridge.island_b}, "
                          f"{bridge.count}x {dir_str}")
            
            print()
            print(f"# Seed: {puzzle.seed}")
            print(f"# Size: {puzzle.size}x{puzzle.size}")
            print(f"# Islands: {len(puzzle.islands)}")
            print(f"# Bridges: {len(puzzle.bridges)}")
            print(f"# Difficulty: {puzzle.difficulty}")


if __name__ == "__main__":
    main()
