# Solvers Package Documentation (`solvers/`)

## High-Level Understanding
This package contains the alternative search algorithms required for benchmarking and comparison against the SAT approach. It includes A* (heuristic search), Brute-Force (baseline), and Backtracking (DFS). All solvers share the same `PuzzleState` and `ConstraintChecker` infrastructure.

## Detailed Explanation

### 1. `astar.py` (`AStarSolver`)
- **Algorithm**: A* Search.
- **Heuristic**: `deficit / 2` (admissible). Since each bridge connects 2 islands, the total missing degree divided by 2 is a lower bound on bridges needed.
- **Process**:
  - Uses a priority queue (`heapq`) storing `(f_score, counter, state)`.
  - Expands states by trying all valid bridge increments.
  - Uses a `closed` set (based on a tuple signature of bridge counts) to avoid cycles and redundant work.
  - Returns the first goal state found.

### 2. `backtracking.py` (`BacktrackingSolver`)
- **Algorithm**: Depth-First Search (DFS) with Forward Checking.
- **Heuristic**: Variable Ordering (Most Constrained Variable).
- **Process**:
  - `_select_island`: Picks the island with the *smallest* remaining degree (fail-first principle).
  - Tries adding bridges to its neighbors.
  - Recursively calls `_search`.
  - Backtracks (undoes move) if a dead-end is reached.

### 3. `bruteforce.py` (`BruteForceSolver`)
- **Algorithm**: Naive DFS / Enumeration.
- **Process**:
  - Iterates through corridors in a fixed order.
  - Tries 0, 1, 2 bridges for each.
  - Checks validity after every assignment.
  - Does **not** use smart variable ordering or lookahead.
  - Intended purely as a slow baseline to demonstrate the efficiency of A* and SAT.
