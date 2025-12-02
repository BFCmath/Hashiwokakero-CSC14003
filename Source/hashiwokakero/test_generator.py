"""
Test Generator for Hashiwokakero puzzles.

Algorithm: Reverse Engineering (Build from Solution)
-----------------------------------------------------
Instead of generating a puzzle and solving it, we:
1. Place islands randomly on the grid
2. Build a spanning tree to ensure connectivity
3. Optionally add extra bridges for complexity
4. Calculate target numbers from the bridge counts
5. Validate no crossing conflicts exist
6. Output only the islands (hiding the bridges)

This approach guarantees:
- All puzzles are solvable (we built the solution first)
- All islands are connected (spanning tree guarantees this)
- No crossing conflicts (validated during generation)
- Proper target values (calculated from actual bridges)

Author: Generated for CSC14003 - Intro to AI
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Direction(str, Enum):
    """Bridge direction."""
    HORIZONTAL = "H"
    VERTICAL = "V"


@dataclass
class PlacedIsland:
    """An island placed on the grid during generation."""
    id: int
    row: int
    col: int
    target: int = 0  # Will be calculated after bridges are placed


@dataclass
class PlacedBridge:
    """A bridge placed between two islands."""
    island_a: int
    island_b: int
    direction: Direction
    count: int  # 1 or 2 bridges
    cells: Tuple[Tuple[int, int], ...]  # Cells occupied by this bridge


@dataclass
class DifficultyConfig:
    """Configuration for puzzle difficulty."""
    size: int
    min_islands: int
    max_islands: int
    min_spacing: int  # Minimum Manhattan distance between islands
    double_bridge_prob: float  # Probability of double bridges
    extra_bridge_prob: float  # Probability of adding extra bridges beyond spanning tree
    name: str


# Predefined difficulty levels
DIFFICULTY_CONFIGS = {
    "easy": DifficultyConfig(
        size=7, min_islands=5, max_islands=15,
        min_spacing=2, double_bridge_prob=0.2, extra_bridge_prob=0.1,
        name="easy"
    ),
    "medium": DifficultyConfig(
        size=9, min_islands=10, max_islands=25,
        min_spacing=2, double_bridge_prob=0.3, extra_bridge_prob=0.2,
        name="medium"
    ),
    "hard": DifficultyConfig(
        size=13, min_islands=18, max_islands=45,
        min_spacing=2, double_bridge_prob=0.4, extra_bridge_prob=0.3,
        name="hard"
    ),
    "expert": DifficultyConfig(
        size=20, min_islands=30, max_islands=60,
        min_spacing=2, double_bridge_prob=0.5, extra_bridge_prob=0.4,
        name="expert"
    ),
}


@dataclass
class GeneratedPuzzle:
    """Result of puzzle generation."""
    matrix: List[List[int]]
    islands: List[PlacedIsland]
    bridges: List[PlacedBridge]
    seed: int
    difficulty: str
    size: int
    
    def to_input_format(self) -> str:
        """Convert to the input file format."""
        lines = []
        for row in self.matrix:
            line = " , ".join(str(cell) for cell in row)
            lines.append(line)
        return "\n".join(lines)
    
    def save(self, path: str | Path) -> None:
        """Save puzzle to file."""
        Path(path).write_text(self.to_input_format(), encoding="utf-8")


class TestGenerator:
    """
    Generates valid Hashiwokakero puzzles using reverse engineering.
    
    The key insight is that we build the solution first (islands + bridges),
    then output only the puzzle (islands with target numbers).
    """
    
    def __init__(self, seed: int):
        """
        Initialize generator with a seed for reproducibility.
        
        Args:
            seed: Random seed for deterministic generation
        """
        self.seed = seed
        self.rng = random.Random(seed)
    
    def generate(
        self,
        difficulty: str = "medium",
        custom_config: Optional[DifficultyConfig] = None
    ) -> GeneratedPuzzle:
        """
        Generate a valid Hashiwokakero puzzle.
        
        Args:
            difficulty: One of "easy", "medium", "hard", "expert"
            custom_config: Optional custom configuration
            
        Returns:
            GeneratedPuzzle object with the puzzle and solution
        """
        config = custom_config or DIFFICULTY_CONFIGS.get(difficulty)
        if config is None:
            raise ValueError(f"Unknown difficulty: {difficulty}. "
                           f"Choose from: {list(DIFFICULTY_CONFIGS.keys())}")
        
        # Retry loop in case generation fails (rare but possible)
        max_attempts = 100
        current_seed = self.seed
        for attempt in range(max_attempts):
            try:
                result = self._generate_puzzle(config)
                # Update the seed used in the result
                result.seed = current_seed
                return result
            except GenerationError:
                # Reseed with a different value for next attempt
                current_seed = self.seed * 100000 + attempt + 1
                self.rng = random.Random(current_seed)
        
        raise GenerationError(f"Failed to generate puzzle after {max_attempts} attempts")
    
    def _generate_puzzle(self, config: DifficultyConfig) -> GeneratedPuzzle:
        """Internal puzzle generation logic using incremental growth."""
        size = config.size
        
        # Use incremental growth: place islands AND bridges together
        # This guarantees connectivity and no crossing issues
        islands, bridges = self._generate_puzzle_incremental(config)
        
        # Fix bridge island_b references (ith bridge connects to (i+1)th island)
        fixed_bridges = []
        for i, bridge in enumerate(bridges):
            fixed_bridges.append(PlacedBridge(
                island_a=bridge.island_a,
                island_b=islands[i + 1].id,
                direction=bridge.direction,
                count=bridge.count,
                cells=bridge.cells
            ))
        bridges = fixed_bridges
        
        # Find all possible corridors for extra bridges
        possible_edges = self._find_possible_edges(islands, size)
        
        # Optionally add extra bridges (beyond spanning tree)
        bridges = self._add_extra_bridges(bridges, possible_edges, islands, size, config)
        
        # Calculate target values for each island
        self._calculate_targets(islands, bridges)
        
        # Validate targets are within [1, 8]
        self._validate_targets(islands)
        
        # Build the output matrix
        matrix = self._build_matrix(islands, size)
        
        return GeneratedPuzzle(
            matrix=matrix,
            islands=islands,
            bridges=bridges,
            seed=self.seed,
            difficulty=config.name,
            size=size
        )
    
    def _generate_puzzle_incremental(self, config: DifficultyConfig) -> Tuple[List[PlacedIsland], List[PlacedBridge]]:
        """
        Generate puzzle using incremental growth strategy.
        
        Instead of placing all islands then connecting:
        1. Start with 2 connected islands
        2. Repeatedly add new island connected to existing network
        3. This GUARANTEES connectivity and no crossing issues
        """
        size = config.size
        num_islands = self.rng.randint(config.min_islands, config.max_islands)
        
        islands: List[PlacedIsland] = []
        bridges: List[PlacedBridge] = []
        
        # Track occupied cells
        island_positions: Set[Tuple[int, int]] = set()
        occupied_h: Set[Tuple[int, int]] = set()  # Horizontal bridge cells
        occupied_v: Set[Tuple[int, int]] = set()  # Vertical bridge cells
        
        # Step 1: Place first island randomly
        first_row = self.rng.randint(1, size - 2)
        first_col = self.rng.randint(1, size - 2)
        islands.append(PlacedIsland(id=1, row=first_row, col=first_col))
        island_positions.add((first_row, first_col))
        
        # Step 2: Incrementally add islands, each connected to existing network
        island_id = 1
        attempts = 0
        max_attempts = num_islands * 500
        
        while len(islands) < num_islands and attempts < max_attempts:
            attempts += 1
            
            # Pick a random existing island to connect from
            source = self.rng.choice(islands)
            
            # Try to place a new island connected to this source
            new_island, bridge = self._try_add_connected_island(
                source, islands, island_positions, 
                occupied_h, occupied_v, size, config
            )
            
            if new_island is not None:
                island_id += 1
                new_island.id = island_id
                islands.append(new_island)
                island_positions.add((new_island.row, new_island.col))
                bridges.append(bridge)
                
                # Update occupied cells
                if bridge.direction == Direction.HORIZONTAL:
                    occupied_h.update(bridge.cells)
                else:
                    occupied_v.update(bridge.cells)
        
        if len(islands) < config.min_islands:
            raise GenerationError(f"Could only place {len(islands)} islands")
        
        return islands, bridges
    
    def _try_add_connected_island(
        self,
        source: PlacedIsland,
        existing_islands: List[PlacedIsland],
        island_positions: Set[Tuple[int, int]],
        occupied_h: Set[Tuple[int, int]],
        occupied_v: Set[Tuple[int, int]],
        size: int,
        config: DifficultyConfig
    ) -> Tuple[Optional[PlacedIsland], Optional[PlacedBridge]]:
        """
        Try to add a new island connected to source island.
        Returns (new_island, bridge) or (None, None) if failed.
        """
        # Try 4 directions: up, down, left, right
        directions = [
            (Direction.VERTICAL, -1, 0),   # Up
            (Direction.VERTICAL, 1, 0),    # Down
            (Direction.HORIZONTAL, 0, -1), # Left
            (Direction.HORIZONTAL, 0, 1),  # Right
        ]
        self.rng.shuffle(directions)
        
        for direction, dr, dc in directions:
            # Random distance (2 to size//2)
            min_dist = 2
            max_dist = min(size // 2, 6)
            if max_dist < min_dist:
                max_dist = min_dist
            
            distance = self.rng.randint(min_dist, max_dist)
            
            new_row = source.row + dr * distance
            new_col = source.col + dc * distance
            
            # Check bounds
            if not (0 <= new_row < size and 0 <= new_col < size):
                continue
            
            # Check not already occupied by island
            if (new_row, new_col) in island_positions:
                continue
            
            # Check minimum spacing from ALL existing islands
            too_close = False
            for island in existing_islands:
                if island.row == source.row and island.col == source.col:
                    continue
                manhattan = abs(new_row - island.row) + abs(new_col - island.col)
                if manhattan < config.min_spacing:
                    too_close = True
                    break
            if too_close:
                continue
            
            # Calculate bridge cells
            if direction == Direction.HORIZONTAL:
                if dc > 0:  # Right
                    cells = tuple((source.row, c) for c in range(source.col + 1, new_col))
                else:  # Left
                    cells = tuple((source.row, c) for c in range(new_col + 1, source.col))
            else:  # VERTICAL
                if dr > 0:  # Down
                    cells = tuple((r, source.col) for r in range(source.row + 1, new_row))
                else:  # Up
                    cells = tuple((r, source.col) for r in range(new_row + 1, source.row))
            
            # Check no island in the path
            if any(cell in island_positions for cell in cells):
                continue
            
            # Check crossing conflicts
            if direction == Direction.HORIZONTAL:
                if any(cell in occupied_v for cell in cells):
                    continue
            else:
                if any(cell in occupied_h for cell in cells):
                    continue
            
            # Success! Create new island and bridge
            new_island = PlacedIsland(id=0, row=new_row, col=new_col)
            count = 2 if self.rng.random() < config.double_bridge_prob else 1
            bridge = PlacedBridge(
                island_a=source.id,
                island_b=0,  # Will be updated
                direction=direction,
                count=count,
                cells=cells
            )
            
            return new_island, bridge
        
        return None, None
    
    def _find_possible_edges(
        self,
        islands: List[PlacedIsland],
        size: int
    ) -> List[Tuple[int, int, Direction, Tuple[Tuple[int, int], ...]]]:
        """
        Find all possible bridge corridors between islands.
        
        A valid corridor:
        - Connects two islands horizontally or vertically
        - Has no other islands in between
        
        Returns:
            List of (island_a_id, island_b_id, direction, cells)
        """
        edges = []
        island_positions: Dict[Tuple[int, int], int] = {
            (island.row, island.col): island.id for island in islands
        }
        
        # Sort islands by position for efficient scanning
        islands_by_row: Dict[int, List[PlacedIsland]] = {}
        islands_by_col: Dict[int, List[PlacedIsland]] = {}
        
        for island in islands:
            islands_by_row.setdefault(island.row, []).append(island)
            islands_by_col.setdefault(island.col, []).append(island)
        
        # Find horizontal edges (same row)
        for row, row_islands in islands_by_row.items():
            sorted_islands = sorted(row_islands, key=lambda x: x.col)
            for i in range(len(sorted_islands) - 1):
                island_a = sorted_islands[i]
                island_b = sorted_islands[i + 1]
                
                # Check no islands in between
                cells = tuple(
                    (row, c) for c in range(island_a.col + 1, island_b.col)
                )
                
                # Verify no islands in the path
                blocked = any(
                    (row, c) in island_positions
                    for c in range(island_a.col + 1, island_b.col)
                )
                
                if not blocked:
                    edges.append((island_a.id, island_b.id, Direction.HORIZONTAL, cells))
        
        # Find vertical edges (same column)
        for col, col_islands in islands_by_col.items():
            sorted_islands = sorted(col_islands, key=lambda x: x.row)
            for i in range(len(sorted_islands) - 1):
                island_a = sorted_islands[i]
                island_b = sorted_islands[i + 1]
                
                # Check no islands in between
                cells = tuple(
                    (r, col) for r in range(island_a.row + 1, island_b.row)
                )
                
                # Verify no islands in the path
                blocked = any(
                    (r, col) in island_positions
                    for r in range(island_a.row + 1, island_b.row)
                )
                
                if not blocked:
                    edges.append((island_a.id, island_b.id, Direction.VERTICAL, cells))
        
        return edges
    
    def _add_extra_bridges(
        self,
        bridges: List[PlacedBridge],
        all_edges: List[Tuple[int, int, Direction, Tuple[Tuple[int, int], ...]]],
        islands: List[PlacedIsland],
        size: int,
        config: DifficultyConfig
    ) -> List[PlacedBridge]:
        """
        Add extra bridges beyond the spanning tree for complexity.
        
        Must ensure no crossing conflicts.
        """
        # Track occupied cells by direction
        occupied_h: Set[Tuple[int, int]] = set()  # Horizontal bridge cells
        occupied_v: Set[Tuple[int, int]] = set()  # Vertical bridge cells
        
        # Mark cells from existing bridges
        existing_pairs: Set[Tuple[int, int]] = set()
        for bridge in bridges:
            existing_pairs.add((bridge.island_a, bridge.island_b))
            existing_pairs.add((bridge.island_b, bridge.island_a))
            
            if bridge.direction == Direction.HORIZONTAL:
                occupied_h.update(bridge.cells)
            else:
                occupied_v.update(bridge.cells)
        
        # Try to add extra bridges
        extra_edges = [
            e for e in all_edges
            if (e[0], e[1]) not in existing_pairs
        ]
        self.rng.shuffle(extra_edges)
        
        new_bridges = list(bridges)
        
        for island_a, island_b, direction, cells in extra_edges:
            if self.rng.random() > config.extra_bridge_prob:
                continue
            
            # Check for crossing conflicts
            if direction == Direction.HORIZONTAL:
                # Horizontal bridge cannot cross vertical bridges
                if any(cell in occupied_v for cell in cells):
                    continue
            else:
                # Vertical bridge cannot cross horizontal bridges
                if any(cell in occupied_h for cell in cells):
                    continue
            
            # Check target constraints (no island should exceed 8)
            island_a_obj = next(i for i in islands if i.id == island_a)
            island_b_obj = next(i for i in islands if i.id == island_b)
            
            # Count current bridges for each island
            count_a = sum(
                b.count for b in new_bridges
                if b.island_a == island_a or b.island_b == island_a
            )
            count_b = sum(
                b.count for b in new_bridges
                if b.island_a == island_b or b.island_b == island_b
            )
            
            # Determine bridge count
            max_add_a = 8 - count_a
            max_add_b = 8 - count_b
            max_add = min(max_add_a, max_add_b, 2)
            
            if max_add < 1:
                continue
            
            count = 2 if (max_add >= 2 and self.rng.random() < config.double_bridge_prob) else 1
            
            # Add the bridge
            new_bridges.append(PlacedBridge(
                island_a=island_a,
                island_b=island_b,
                direction=direction,
                count=count,
                cells=cells
            ))
            
            # Update occupied cells
            if direction == Direction.HORIZONTAL:
                occupied_h.update(cells)
            else:
                occupied_v.update(cells)
        
        return new_bridges
    
    def _calculate_targets(
        self,
        islands: List[PlacedIsland],
        bridges: List[PlacedBridge]
    ) -> None:
        """Calculate target values for each island based on connected bridges."""
        for island in islands:
            total = 0
            for bridge in bridges:
                if bridge.island_a == island.id or bridge.island_b == island.id:
                    total += bridge.count
            island.target = total
    
    def _validate_targets(self, islands: List[PlacedIsland]) -> None:
        """Validate all targets are within [1, 8]."""
        for island in islands:
            if island.target < 1:
                raise GenerationError(f"Island {island.id} has target {island.target} < 1")
            if island.target > 8:
                raise GenerationError(f"Island {island.id} has target {island.target} > 8")
    
    def _build_matrix(self, islands: List[PlacedIsland], size: int) -> List[List[int]]:
        """Build the output matrix with islands and zeros."""
        matrix = [[0] * size for _ in range(size)]
        
        for island in islands:
            matrix[island.row][island.col] = island.target
        
        return matrix


class GenerationError(Exception):
    """Raised when puzzle generation fails."""
    pass


def generate_test_suite(
    base_seed: int = 42,
    output_dir: str = "Inputs",
    tests_per_difficulty: int = 3
) -> List[str]:
    """
    Generate a complete test suite with puzzles of varying difficulty.
    
    Args:
        base_seed: Base random seed
        output_dir: Directory to save puzzles
        tests_per_difficulty: Number of tests per difficulty level
    
    Returns:
        List of generated file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    generated_files = []
    test_number = 1
    
    difficulties = ["easy", "medium", "hard", "expert"]
    
    for difficulty in difficulties:
        for i in range(tests_per_difficulty):
            seed = base_seed * 100 + test_number
            generator = TestGenerator(seed=seed)
            
            try:
                puzzle = generator.generate(difficulty=difficulty)
                
                filename = f"input-{test_number:02d}.txt"
                filepath = output_path / filename
                puzzle.save(filepath)
                
                generated_files.append(str(filepath))
                print(f"Generated {filename}: {puzzle.size}x{puzzle.size}, "
                      f"{len(puzzle.islands)} islands, {difficulty}")
                
            except GenerationError as e:
                print(f"Failed to generate test {test_number}: {e}")
            
            test_number += 1
    
    return generated_files


def generate_single_puzzle(
    seed: int,
    difficulty: str = "medium",
    size: Optional[int] = None
) -> GeneratedPuzzle:
    """
    Generate a single puzzle with given parameters.
    
    Args:
        seed: Random seed for reproducibility
        difficulty: Difficulty level
        size: Optional custom size (overrides difficulty default)
    
    Returns:
        GeneratedPuzzle object
    """
    generator = TestGenerator(seed=seed)
    
    if size is not None:
        # Create custom config with specified size
        base_config = DIFFICULTY_CONFIGS[difficulty]
        custom_config = DifficultyConfig(
            size=size,
            min_islands=max(4, size // 2),
            max_islands=min(size * 2, (size * size) // 4),
            min_spacing=base_config.min_spacing,
            double_bridge_prob=base_config.double_bridge_prob,
            extra_bridge_prob=base_config.extra_bridge_prob,
            name=f"{difficulty}_{size}x{size}"
        )
        return generator.generate(custom_config=custom_config)
    
    return generator.generate(difficulty=difficulty)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Hashiwokakero test puzzles"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Base random seed for reproducibility"
    )
    parser.add_argument(
        "--difficulty", type=str, default="medium",
        choices=["easy", "medium", "hard", "expert"],
        help="Puzzle difficulty level"
    )
    parser.add_argument(
        "--size", type=int, default=None,
        help="Custom grid size (overrides difficulty default)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output file path (default: print to stdout)"
    )
    parser.add_argument(
        "--suite", action="store_true",
        help="Generate a complete test suite instead of single puzzle"
    )
    parser.add_argument(
        "--suite-dir", type=str, default="Inputs",
        help="Output directory for test suite"
    )
    parser.add_argument(
        "--tests-per-level", type=int, default=3,
        help="Number of tests per difficulty level in suite"
    )
    
    args = parser.parse_args()
    
    if args.suite:
        # Generate complete test suite
        files = generate_test_suite(
            base_seed=args.seed,
            output_dir=args.suite_dir,
            tests_per_difficulty=args.tests_per_level
        )
        print(f"\nGenerated {len(files)} test files in {args.suite_dir}/")
    else:
        # Generate single puzzle
        puzzle = generate_single_puzzle(
            seed=args.seed,
            difficulty=args.difficulty,
            size=args.size
        )
        
        if args.output:
            puzzle.save(args.output)
            print(f"Saved puzzle to {args.output}")
            print(f"Size: {puzzle.size}x{puzzle.size}")
            print(f"Islands: {len(puzzle.islands)}")
            print(f"Bridges: {len(puzzle.bridges)}")
        else:
            print(puzzle.to_input_format())
            print()
            print(f"# Seed: {puzzle.seed}")
            print(f"# Size: {puzzle.size}x{puzzle.size}")
            print(f"# Islands: {len(puzzle.islands)}")
            print(f"# Bridges: {len(puzzle.bridges)}")
