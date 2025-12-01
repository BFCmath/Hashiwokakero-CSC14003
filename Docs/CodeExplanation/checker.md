# Checker Module Documentation (`checker.py`)

## High-Level Understanding
The `checker.py` module encapsulates the logic for validating moves and states. It ensures that bridge placements obey the rules of Hashiwokakero: no crossing bridges, and island bridge counts must not exceed their targets. It is used by search algorithms (A*, Backtracking, Brute-force) to prune invalid branches early.

## Detailed Explanation

### `ConstraintChecker` (Class)
- **Purpose**: Validates `PuzzleState` against game rules.
- **Attributes**:
  - `grid`: Reference to the static grid topology.

- **Key Methods**:
  - `is_valid_assignment(state)`: The main entry point. Checks both degree constraints and crossing constraints.
  - `_respect_degrees(state)`:
    - Iterates over all islands.
    - Returns `False` if any island has *more* bridges than its target number (i.e., `remaining_degree < 0`).
    - Note: It allows partial satisfaction (under-full islands) because it's used during intermediate search steps.
  - `_avoid_crossings(state)`:
    - Checks if any two bridges intersect.
    - **Mechanism**: It iterates through all active corridors and marks their cells in a dictionary. If a cell is already marked with a *different* orientation (e.g., Horizontal vs Vertical), a crossing is detected, and it returns `False`.
  - `available_actions(state)`:
    - Returns a list of legal moves from the current state (corridors that can be incremented without immediately violating the max-2-bridges rule).
