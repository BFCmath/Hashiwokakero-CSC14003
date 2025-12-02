# Test Case Generation for Hashiwokakero

## Overview

This document describes the algorithm and methodology used to generate valid Hashiwokakero puzzle test cases. The generator uses a **Reverse Engineering** approach - building the solution first, then hiding the bridges to create the puzzle.

## Algorithm: Incremental Growth

### Why Not Traditional Approach?

The traditional approach of placing all islands randomly, then using Kruskal's algorithm to find a spanning tree often fails because:

- Random island placement can create topologies where bridges must cross
- Kruskal's algorithm doesn't consider crossing constraints
- High failure rate, especially for larger grids

### Our Solution: Build Islands and Bridges Together

Instead of placing islands first and connecting them later, we grow the puzzle incrementally:

1. Place one island at a random position
2. Repeatedly add new islands that are **already connected** to the existing network
3. Check crossing constraints **before** adding each bridge
4. This guarantees connectivity and no crossing conflicts

## Generation Steps

### Step 1: Initialize First Island

```
Place the first island at a random position (avoiding edges)
Position: row ∈ [2, size-2], col ∈ [2, size-2]
```

### Step 2: Incremental Growth Loop

```
WHILE islands.count < target_count:
    source = random.choice(existing_islands)
    (new_island, bridge) = try_add_connected_island(source)

    IF successful:
        add new_island to islands
        add bridge to bridges
        mark bridge cells as occupied
```

### Step 3: Try Add Connected Island

For each attempt, we:

1. **Choose direction**: Randomly pick from UP, DOWN, LEFT, RIGHT
2. **Choose distance**: Random value between 2 and min(size/2, 6)
3. **Validate position**:
   - Within grid bounds
   - Not occupied by another island
   - Maintains minimum spacing from other islands
   - No island blocking the path
   - No crossing with existing bridges

### Step 4: Add Extra Bridges (Optional)

After building the spanning tree, optionally add more bridges:

- Find all possible corridors not yet used
- Randomly add some (based on `extra_bridge_prob`)
- Ensure no crossing conflicts
- Ensure island targets don't exceed 8

### Step 5: Calculate Targets

```
FOR each island:
    target = SUM(bridge.count for each connected bridge)
```

### Step 6: Validate and Output

- Verify all targets are in range [1, 8]
- Generate matrix with islands only (bridges hidden)

## Difficulty Levels

### Configuration Parameters


| Parameter            | Description                                              |
| ---------------------- | ---------------------------------------------------------- |
| `size`               | Grid dimensions (N × N)                                 |
| `min_islands`        | Minimum number of islands                                |
| `max_islands`        | Maximum number of islands                                |
| `min_spacing`        | Minimum Manhattan distance between islands               |
| `double_bridge_prob` | Probability of placing 2 bridges instead of 1            |
| `extra_bridge_prob`  | Probability of adding extra bridges beyond spanning tree |

### Difficulty Configurations

#### Easy


| Parameter                 | Value  |
| --------------------------- | -------- |
| Grid Size                 | 7 × 7 |
| Islands                   | 5 - 15 |
| Min Spacing               | 2      |
| Double Bridge Probability | 20%    |
| Extra Bridge Probability  | 10%    |

**Characteristics:**

- Small grid, easy to visualize
- Fewer islands, simpler topology
- Mostly single bridges
- Few extra connections

#### Medium


| Parameter                 | Value   |
| --------------------------- | --------- |
| Grid Size                 | 9 × 9  |
| Islands                   | 10 - 25 |
| Min Spacing               | 2       |
| Double Bridge Probability | 30%     |
| Extra Bridge Probability  | 20%     |

**Characteristics:**

- Moderate grid size
- More islands to connect
- Mix of single and double bridges
- Some extra connections for complexity

#### Hard


| Parameter                 | Value    |
| --------------------------- | ---------- |
| Grid Size                 | 13 × 13 |
| Islands                   | 18 - 45  |
| Min Spacing               | 2        |
| Double Bridge Probability | 40%      |
| Extra Bridge Probability  | 30%      |

**Characteristics:**

- Large grid, harder to overview
- Many islands with complex topology
- Significant number of double bridges
- Multiple possible paths

#### Expert


| Parameter                 | Value    |
| --------------------------- | ---------- |
| Grid Size                 | 20 × 20 |
| Islands                   | 30 - 60  |
| Min Spacing               | 2        |
| Double Bridge Probability | 50%      |
| Extra Bridge Probability  | 40%      |

**Characteristics:**

- Very large grid
- Dense island placement
- Half of bridges are double
- Complex interconnections

## Crossing Prevention

Bridges cannot cross each other. We track occupied cells by direction:

```
occupied_h: Set of cells with horizontal bridges
occupied_v: Set of cells with vertical bridges

When adding a new bridge:
  - If HORIZONTAL: check that no cell is in occupied_v
  - If VERTICAL: check that no cell is in occupied_h
```

**Example of invalid crossing:**

```
    ①───────②
        │
        │     ← Vertical bridge crosses horizontal bridge
        │
        ③
```

## Guarantees


| Rule                 | How It's Guaranteed                              |
| ---------------------- | -------------------------------------------------- |
| **Connectivity**     | Each new island is connected to existing network |
| **No Crossing**      | Check before adding each bridge                  |
| **Target ∈ [1,8]**  | Validated after calculation                      |
| **Straight Bridges** | Only HORIZONTAL/VERTICAL directions              |
| **Max 2 Bridges**    | `count ∈ {1, 2}` enforced                       |
| **Solvable**         | Solution is built first                          |

## Reproducibility

The generator uses a seeded random number generator:

```python
generator = TestGenerator(seed=42)
puzzle = generator.generate(difficulty="medium")
```

**Same seed + same difficulty = same puzzle**

This allows:

- Reproducing specific test cases
- Sharing puzzles by seed number
- Debugging specific configurations

## Usage

### Command Line

```bash
# Generate single puzzle
python generate_tests.py --seed 42 --difficulty medium

# Generate test suite (3 puzzles per difficulty = 12 total)
python generate_tests.py --suite --seed 42

# Generate with custom parameters
python generate_tests.py --suite --tests-per-level 5 --seed 100

# Show configuration info
python generate_tests.py --info
```

### Output Format

```
0 , 0 , 2 , 0 , 3 , 0 , 0
0 , 0 , 0 , 0 , 0 , 0 , 0
4 , 0 , 0 , 0 , 2 , 0 , 3
0 , 0 , 0 , 0 , 0 , 0 , 0
0 , 3 , 0 , 0 , 0 , 2 , 0
0 , 0 , 0 , 0 , 0 , 0 , 0
2 , 0 , 0 , 4 , 0 , 0 , 2
```

Where:

- `0` = empty cell
- `1-8` = island with that many bridges required

## File Naming Convention

Generated test files follow this pattern:

```
input-01.txt  (easy)
input-02.txt  (easy)
input-03.txt  (easy)
input-04.txt  (medium)
input-05.txt  (medium)
input-06.txt  (medium)
input-07.txt  (hard)
input-08.txt  (hard)
input-09.txt  (hard)
input-10.txt  (expert)
input-11.txt  (expert)
input-12.txt  (expert)
```

## Summary

The test generator creates valid, solvable Hashiwokakero puzzles by:

1. Using **incremental growth** to build islands and bridges together
2. **Checking constraints** before each addition
3. **Varying difficulty** through grid size, island count, and bridge probabilities
4. Ensuring **reproducibility** through seeded random generation
