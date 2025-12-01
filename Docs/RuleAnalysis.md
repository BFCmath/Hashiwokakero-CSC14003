# Rule Analysis
Based on the implementation in hashiwokakero, here is the verification of how each rule is enforced across the different modules:

### 1. Begin and end at distinct islands, travelling a straight line
**Enforced in:** `grid.py` (Static Topology)
- **Mechanism:** The `_build_corridors` method scans the grid starting from each island.
- **Code Evidence:**
  - It iterates `c = island.col + 1` (Horizontal) and `r = island.row + 1` (Vertical).
  - It collects empty cells into a list until it hits another island or the grid edge.
  - A `BridgeCorridor` is only created if it successfully reaches another island (`if pos in self._island_lookup`).
  - This guarantees bridges only exist as straight lines between two specific islands.

### 2. Must not cross any other bridges or islands
**Enforced in:** `grid.py`, `checker.py`, and `cnf_encoder.py`
- **Islands:** In `grid.py`, the scanning loop breaks immediately if it encounters a non-zero number (`if self._matrix[r][c] != 0`), ensuring a corridor never passes *through* an intervening island.
- **Bridges (Search):** In `checker.py`, `_avoid_crossings` maps every occupied cell to its orientation ("H" or "V"). If a cell is claimed by both, it returns `False`.
- **Bridges (SAT):** In `cnf_encoder.py`, `_encode_crossing_constraints` identifies cells shared by a horizontal and a vertical corridor. It adds a clause `[-h_active, -v_active]`, making it mathematically impossible for both to be active simultaneously.

### 3. May only run perpendicularly
**Enforced in:** `grid.py`
- **Mechanism:** The `Direction` enum only defines `HORIZONTAL` and `VERTICAL`.
- **Code Evidence:** The `_build_corridors` method explicitly performs only two scans: one incrementing columns (Horizontal) and one incrementing rows (Vertical). No diagonal scanning exists.

### 4. At most two bridges connect a pair of islands
**Enforced in:** `state.py`, `checker.py`, and `cnf_encoder.py`
- **State Validation:** `PuzzleState.set_corridor_value` raises a `ValueError` if a value other than 0, 1, or 2 is attempted.
- **Search:** `ConstraintChecker.available_actions` checks `if current < 2` before suggesting an increment action.
- **SAT:** `CNFEncoder._encode_corridor_domains` creates boolean variables `single` and `double` for each corridor and adds the clause `[-single, -double]`, ensuring they cannot both be true (which would imply 1+2=3 bridges).

### 5. Bridges connected to each island must match the number
**Enforced in:** `state.py`, `checker.py`, and `cnf_encoder.py`
- **Search (Pruning):** `ConstraintChecker._respect_degrees` ensures `remaining_degree >= 0` during search (you can't exceed the number).
- **Search (Goal):** `PuzzleState.islands_satisfied` checks that `remaining_degree == 0` for *all* islands to declare victory.
- **SAT:** `CNFEncoder._encode_island_degrees` uses Pseudo-Boolean constraints (`PBEnc.equals`) to enforce that `1*sum(singles) + 2*sum(doubles) == island.target`.

### 6. Connect islands into a single connected group
**Enforced in:** `state.py` and `sat_solver.py`
- **Search:** `PuzzleState.is_connected()` performs a BFS/DFS traversal starting from the first island. `PuzzleState.is_goal()` returns `True` only if `visited_count == total_islands`.
- **SAT:** Since connectivity is hard to encode statically, `PySatSolver` uses an iterative approach:
  1. It solves for all other rules first.
  2. It checks `state.is_connected()`.
  3. If disconnected, `_connectivity_clauses` finds the separated components and adds a "cut" constraint (forcing at least one bridge to cross the gap) and re-solves.