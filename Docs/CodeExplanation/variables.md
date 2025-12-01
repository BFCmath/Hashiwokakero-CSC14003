# Variables Module Documentation (`variables.py`)

## High-Level Understanding
The `variables.py` module manages the mapping between high-level semantic concepts (e.g., "Corridor 5 has 1 bridge") and the integer variables required by the SAT solver (CNF format). It ensures a consistent, bidirectional mapping so that we can encode constraints into SAT clauses and decode the SAT model back into a puzzle solution.

## Detailed Explanation

### 1. `VariableKey` (Dataclass)
- **Purpose**: A structured key to identify a logical variable.
- **Attributes**:
  - `kind`: A string describing the variable type (e.g., "corridor_single", "corridor_active").
  - `payload`: A tuple of integers (e.g., corridor ID) to distinguish instances.
- **Role**: Ensures that `var("corridor_single", 1)` always refers to the same concept.

### 2. `VariableRegistry` (Class)
- **Purpose**: The central registry for variable ID assignment.
- **Attributes**:
  - `_forward`: Map from `VariableKey` -> `int` (SAT variable ID).
  - `_reverse`: Map from `int` -> `VariableKey`.
  - `_next`: Counter for the next available variable ID (starts at 1).

- **Key Methods**:
  - `var(kind, *payload)`:
    - Looks up the key. If it exists, returns the existing ID.
    - If new, assigns a new ID, stores the mapping, and increments the counter.
  - `lookup(var_id)`: Retrieves the `VariableKey` for a given integer ID. Used during decoding (inference).
  - `count`: Returns the total number of variables created.
