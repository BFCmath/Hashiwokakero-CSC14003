# State Module Documentation (`state.py`)

## High-Level Understanding
The `state.py` module manages the **dynamic** aspect of the puzzle. While `Grid` is static, `PuzzleState` tracks the current configuration of bridges placed on the board. It serves as the "node" in search algorithms (A*, Backtracking), providing methods to modify the board, check for goal states (connectivity, degree satisfaction), and calculate heuristics. It is designed to be copied efficiently to support branching search strategies.

## Detailed Explanation

### `PuzzleState` (Class)
- **Purpose**: Represents a snapshot of the game board during solving.
- **Attributes**:
  - `grid`: Reference to the static `Grid` object.
  - `bridge_counts`: A dictionary mapping `corridor_id` -> `count` (1 or 2). If a corridor is not in the map, it has 0 bridges.

- **Key Methods**:
  - `copy()`: Creates a shallow copy of the state (crucial for search algorithms to branch without affecting the parent state).
  - `corridor_value(id)` / `set_corridor_value(id, val)`: Getters/setters for bridge counts. Validates input (0, 1, 2).
  - `remaining_degree(island)`: Calculates how many more bridges an island needs (`target - current_bridges`).
  - `is_connected()`: Uses BFS/DFS to check if all islands with bridges form a single connected component. This is a key rule of Hashiwokakero.
  - `occupied_cells()`: Returns all grid cells currently occupied by bridges, along with their orientation. Used for collision detection and rendering.
  - `islands_satisfied()`: Checks if every island has exactly the required number of bridges.
  - `is_goal()`: Returns `True` if all islands are satisfied AND the graph is connected.
  - `deficit()`: A heuristic function returning the total number of missing bridges across all islands. Used by A* and greedy strategies.
  - `available_actions()`: Generator that yields valid moves (corridors that can accept more bridges).
  - `to_symbol_matrix()`: Converts the current state into a 2D character grid for printing/debugging (e.g., drawing `=`, `-`, `|`, `$`).
