# Loader Module Documentation (`loader.py`)

## High-Level Understanding
The `loader.py` module is responsible for reading puzzle instances from text files and converting them into `Grid` objects. It handles file I/O, parsing the comma-separated integer format, and basic validation of the input structure (e.g., ensuring rectangular dimensions). It acts as the bridge between the raw `input-XX.txt` files and the internal object model.

## Detailed Explanation

### `PuzzleLoader` (Class)
- **Purpose**: A utility class (namespace) for loading operations.
- **Key Methods**:
  - `load(path)`:
    - **Input**: File path (string or `Path` object).
    - **Process**:
      1. Reads the file content.
      2. Splits lines and comma-separated values.
      3. Converts tokens to integers (0 for empty, 1-8 for islands).
      4. Validates that all rows have the same length.
      5. Instantiates and returns a `Grid` object.
    - **Error Handling**: Raises `FileNotFoundError` if the file is missing, or `ValueError` for malformed/inconsistent inputs.
