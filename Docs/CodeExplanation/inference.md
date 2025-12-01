# Inference Module Documentation (`inference.py`)

## High-Level Understanding
The `inference.py` module is the bridge *back* from the SAT world to the game world. Once the SAT solver finds a satisfying assignment (a "model"), this module interprets the true/false values of the variables and reconstructs the corresponding `PuzzleState`.

## Detailed Explanation

### `InferenceEngine` (Class)
- **Purpose**: Decodes SAT models.
- **Attributes**:
  - `grid`: The puzzle grid.
  - `registry`: The `VariableRegistry` used during encoding (essential for knowing what variable #123 represents).

- **Key Methods**:
  - `state_from_model(model)`:
    - **Input**: A list of integers (literals) from the SAT solver. Positive means true, negative means false.
    - **Process**:
      1. Creates a set of true variables.
      2. Iterates through all corridors in the grid.
      3. Checks if the `double` variable for that corridor is true -> sets 2 bridges.
      4. Else if `single` is true -> sets 1 bridge.
      5. Else -> sets 0 bridges.
    - **Output**: A fully populated `PuzzleState`.
