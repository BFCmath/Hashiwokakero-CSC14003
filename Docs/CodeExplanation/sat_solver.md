# SAT Solver Module Documentation (`sat_solver.py`)

## High-Level Understanding
The `sat_solver.py` module implements the SAT-based solving strategy. It wraps the PySAT library (`glucose4` solver) and orchestrates the "Lazy Constraint" approach for connectivity. Since encoding "the graph must be connected" into static CNF is expensive, this solver first solves for degrees and non-crossing, checks if the result is connected, and if not, adds "cut" constraints to ban that specific disconnected partition, repeating until a connected solution is found.

## Detailed Explanation

### `SatResult` (Dataclass)
- **Purpose**: Standardized return type for the solver.
- **Fields**: `state` (solution), `elapsed` (time), `iterations` (number of solve calls), `status` ("SAT"/"UNSAT").

### `PySatSolver` (Class)
- **Purpose**: The main SAT solver class.
- **Key Methods**:
  - `solve(grid, enforce_connectivity)`:
    - Builds the initial CNF (degrees + crossings).
    - Enters a loop:
      1. Calls `solver.solve()`.
      2. If UNSAT, returns failure.
      3. If SAT, decodes the model into a `PuzzleState`.
      4. Checks connectivity. If connected (or check disabled), returns success.
      5. If disconnected, generates "cut constraints" (clauses that say "you must add a bridge crossing the gap between these components").
      6. Adds these new clauses to the running solver and repeats.
  - `_connectivity_clauses(grid, registry, state)`:
    - Uses Union-Find (Disjoint Set) to identify connected components.
    - If more than 1 component exists, it finds the "cut" (set of all potential bridges connecting Component A to the rest).
    - Generates a clause: `OR(potential_bridges)` -> "At least one bridge must be active across this cut."
