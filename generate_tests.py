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
        "--visualize", "-v", action="store_true",default=True,
        help="Visualize puzzles and solutions when generating"
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
        print("=" * 60)
        
        # Generate puzzles with visualization
        from hashiwokakero.test_generator import GenerationError
        output_path = Path(args.suite_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        test_number = 1
        difficulties = ["easy", "medium", "hard", "expert"]
        
        for difficulty in difficulties:
            for i in range(args.tests_per_level):
                seed = args.seed * 100 + test_number
                generator = TestGenerator(seed=seed)
                
                try:
                    puzzle = generator.generate(difficulty=difficulty)
                    
                    filename = f"input-{test_number:02d}.txt"
                    filepath = output_path / filename
                    puzzle.save(filepath)
                    generated_files.append(str(filepath))
                    
                    print(f"\n{'='*60}")
                    print(f"TEST {test_number:02d}: {filename} ({difficulty})")
                    print(f"Size: {puzzle.size}x{puzzle.size}, Islands: {len(puzzle.islands)}, Bridges: {len(puzzle.bridges)}")
                    print("="*60)
                    
                    if args.visualize:
                        print("\nPUZZLE:")
                        print(puzzle.visualize_puzzle())
                        print("\nSOLUTION:")
                        print(puzzle.visualize_solution())
                    
                except GenerationError as e:
                    print(f"\n❌ Failed to generate test {test_number}: {e}")
                
                test_number += 1
        
        print("\n" + "=" * 60)
        print(f"✓ Generated {len(generated_files)} test files in {args.suite_dir}/")
        
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
