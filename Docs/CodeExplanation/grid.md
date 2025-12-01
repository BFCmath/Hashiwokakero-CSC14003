# Grid Module Documentation (`grid.py`)

## High-Level Understanding
The `grid.py` module defines the core data structures representing the static topology of a Hashiwokakero puzzle. It parses the raw input matrix into semantic objects: **Islands** (nodes) and **BridgeCorridors** (potential edges). This module is responsible for understanding the board layout, identifying where bridges can legally be placed, and providing efficient lookups for neighbors and spatial relationships. It is immutable once initialized; dynamic state (like placed bridges) is handled separately in `PuzzleState`.

## Detailed Explanation

### 1. `Direction` (Enum)
- **Purpose**: Represents the orientation of a bridge.
- **Values**: `HORIZONTAL` ("H"), `VERTICAL` ("V").
- **Usage**: Used by `BridgeCorridor` to indicate direction and by the renderer/checker to determine cell occupancy patterns.

### 2. `Island` (Dataclass)
- **Purpose**: Represents a numbered island on the board.
- **Attributes**:
  - `identifier`: Unique integer ID for the island.
  - `row`, `col`: Coordinates on the grid.
  - `target`: The number on the island (required bridge count).
- **Role**: Acts as a node in the graph.

### 3. `BridgeCorridor` (Dataclass)
- **Purpose**: Represents a potential connection between two islands.
- **Attributes**:
  - `identifier`: Unique ID for the corridor.
  - `island_a`, `island_b`: IDs of the connected islands.
  - `direction`: Orientation (Horizontal/Vertical).
  - `cells`: Tuple of `(row, col)` coordinates for all empty cells between the two islands.
- **Role**: Represents an edge in the graph. It pre-calculates the path so we don't need to scan the grid repeatedly.

### 4. `Grid` (Class)
- **Purpose**: The main container for the puzzle's static structure.
- **Key Methods**:
  - `__init__`: Takes a 2D matrix, identifies islands, and scans for all possible corridors.
  - `_build_islands`: Scans the matrix for non-zero numbers and creates `Island` objects.
  - `_build_corridors`: Performs horizontal and vertical scans from each island to find reachable neighbors, stopping at obstacles or grid boundaries.
  - `neighbors(island_id)`: Returns IDs of islands reachable from a given island.
  - `corridors_incident_to(island_id)`: Returns all `BridgeCorridor` objects connected to an island.
  - `corridor_between(a, b)`: Finds the specific corridor connecting two islands, if one exists.
  - `cell_contains_island`: Helper to check if a coordinate is an island.
