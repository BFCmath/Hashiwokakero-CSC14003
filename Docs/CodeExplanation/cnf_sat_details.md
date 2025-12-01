# CNF Encoding and SAT Solving Explained

This document details how the Hashiwokakero puzzle is translated into a boolean satisfiability problem (SAT) and solved using Conjunctive Normal Form (CNF).

## 1. What is CNF?
Conjunctive Normal Form (CNF) is a standard way of writing boolean logic formulas. A formula is in CNF if it is an **AND** of **ORs**.
- **Literal**: A boolean variable ($x$) or its negation ($\neg x$).
- **Clause**: A disjunction (OR) of literals, e.g., $(x_1 \lor \neg x_2 \lor x_3)$.
- **Formula**: A conjunction (AND) of clauses, e.g., $(C_1 \land C_2 \land \dots \land C_n)$.

For a SAT solver to find a solution, it must find a value (True/False) for every variable such that **every single clause evaluates to True**.

## 2. Encoding Hashiwokakero into CNF

To solve the puzzle, we must translate its rules into this rigid "AND of ORs" format.

### Step 1: Define Variables
We don't have "bridges" in boolean logic, only True/False. So we create boolean variables to represent the state of each corridor.
For every corridor $C_i$ (the path between two islands), we define:
- $S_i$ ("Single"): True if corridor $i$ has exactly 1 bridge.
- $D_i$ ("Double"): True if corridor $i$ has exactly 2 bridges.
- $A_i$ ("Active"): True if corridor $i$ has *any* bridge ($S_i \lor D_i$).

### Step 2: Domain Constraints (The "Physics" of the World)
A corridor cannot have 1 bridge AND 2 bridges at the same time.
- **Logic**: $\neg (S_i \land D_i)$
- **CNF Clause**: $(\neg S_i \lor \neg D_i)$
  - *Meaning*: Either $S_i$ is False, or $D_i$ is False (or both). They cannot both be True.

Also, if a corridor is "Active", it must be either Single or Double.
- **Logic**: $A_i \leftrightarrow (S_i \lor D_i)$
- **CNF Clauses**:
  1. $(\neg A_i \lor S_i \lor D_i)$  (If Active, then Single or Double)
  2. $(\neg S_i \lor A_i)$           (If Single, then Active)
  3. $(\neg D_i \lor A_i)$           (If Double, then Active)

### Step 3: Crossing Constraints
Bridges cannot cross. If a horizontal corridor $H$ and a vertical corridor $V$ share a grid cell, they cannot both be active.
- **Logic**: $\neg (A_H \land A_V)$
- **CNF Clause**: $(\neg A_H \lor \neg A_V)$
  - *Meaning*: At least one of them must be inactive.

### Step 4: Island Degree Constraints
Each island must have a specific number of bridges connected to it.
Example: An island with target 3 connected to corridors $X$ and $Y$.
- **Equation**: $Count(X) + Count(Y) = 3$
- **Weights**: Single bridges count as 1, Double bridges count as 2.
- **Formula**: $1 \cdot S_X + 2 \cdot D_X + 1 \cdot S_Y + 2 \cdot D_Y = 3$

This is a "Pseudo-Boolean" constraint. We use the PySAT library to convert this mathematical equality into a set of CNF clauses. It generates a complex web of helper variables and clauses that are only satisfiable if the sum is exactly 3.

## 3. The SAT Solving Process

Once we have thousands of these clauses, we feed them to a SAT solver (like Glucose or MiniSat).

### How the Solver Works (DPLL / CDCL Algorithm)
1. **Decision**: The solver picks a variable (e.g., "Corridor 5 is Single") and guesses it is True.
2. **Propagation**: It looks at the clauses.
   - If we have a clause $(\neg S_5 \lor \neg D_5)$ and we set $S_5=True$, then $\neg S_5$ is False. For the clause to be True, $\neg D_5$ *must* be True. So $D_5$ becomes False.
   - This chain reaction fills in other variables automatically.
3. **Conflict**: If propagation leads to a contradiction (e.g., a clause becomes False), the solver knows the guess was wrong.
4. **Backtracking & Learning**: It backtracks, flips the guess, and "learns" a new clause that prevents making that same combination of mistakes again.

### The "Lazy" Connectivity Check
One rule is hard to encode: "All islands must be connected."
Encoding this directly creates exponentially many clauses. Instead, we use a **Lazy Approach**:
1. **Solve** the puzzle ignoring connectivity.
2. **Check** the solution. Is the graph connected?
   - **Yes**: We are done!
   - **No**: The graph is broken into separated groups (e.g., Group A and Group B).
3. **Refine**: We add a new constraint: "You must build at least one bridge between Group A and Group B."
   - Clause: $(A_{bridge1} \lor A_{bridge2} \lor \dots)$ where these bridges span the gap.
4. **Repeat**: Ask the solver again. It will now find a solution that respects the new rule.

## Summary
- **CNF Encoding**: Translating "Game Rules" into "Logic Circuits" (AND/OR gates).
- **SAT Solver**: A high-speed engine that finds inputs to make the circuit output "True".
- **Inference**: Converting the solver's True/False output back into "Bridge placed here".
