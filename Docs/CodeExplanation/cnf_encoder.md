# CNF Encoder Module Documentation (`cnf_encoder.py`)

## High-Level Understanding
The `cnf_encoder.py` module translates the rules of Hashiwokakero into Conjunctive Normal Form (CNF) for the SAT solver. It uses the `VariableRegistry` to create boolean variables and generates clauses that enforce:
1. **Domain constraints**: A corridor can have 0, 1, or 2 bridges (mutually exclusive).
2. **Degree constraints**: The sum of bridges connected to an island must equal its number.
3. **Crossing constraints**: Horizontal and vertical bridges cannot share the same cell.

## Detailed Explanation

### 1. `CNFEncoding` (Dataclass)
- **Purpose**: Container for the generated CNF formula and the registry used to create it.

### 2. `CNFEncoder` (Class)
- **Purpose**: The engine that builds the SAT formula.
- **Key Methods**:
  - `build()`: Orchestrates the encoding process and returns a `CNFEncoding` object.
  - `_corridor_vars(corridor)`: Helper to get/create the 3 variables for a corridor:
    - `single`: True if 1 bridge.
    - `double`: True if 2 bridges.
    - `active`: True if > 0 bridges (helper for crossings).
  - `_encode_corridor_domains()`:
    - Adds clauses ensuring `single` and `double` are mutually exclusive.
    - Enforces `active <-> (single OR double)`.
  - `_encode_island_degrees()`:
    - Uses `pysat.pb.PBEnc` (Pseudo-Boolean encoding) to enforce `sum(bridges) == target`.
    - Weights: `single` contributes 1, `double` contributes 2.
  - `_encode_crossing_constraints()`:
    - Identifies cells where horizontal and vertical corridors overlap.
    - Adds clauses `NOT(h_active) OR NOT(v_active)` for every such intersection, preventing collisions.
