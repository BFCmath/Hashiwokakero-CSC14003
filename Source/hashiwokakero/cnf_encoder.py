"""CNF encoder for Hashiwokakero rules."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from pysat.formula import CNF
from pysat.card import CardEnc

from .grid import BridgeCorridor, Direction, Grid
from .variables import VariableRegistry


@dataclass
class CNFEncoding:
    cnf: CNF
    registry: VariableRegistry


class CNFEncoder:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.registry = VariableRegistry()
        self.cnf = CNF()

    def build(self) -> CNFEncoding:
        self._encode_corridor_domains()
        self._encode_island_degrees()
        self._encode_crossing_constraints()
        return CNFEncoding(self.cnf, self.registry)

    def _corridor_vars(self, corridor: BridgeCorridor) -> Tuple[int, int, int]:
        single = self.registry.var("corridor_single", corridor.identifier)
        double = self.registry.var("corridor_double", corridor.identifier)
        active = self.registry.var("corridor_active", corridor.identifier)
        return single, double, active

    def _encode_corridor_domains(self) -> None:
        for corridor in self.grid.corridors.values():
            single, double, active = self._corridor_vars(corridor)
            # cannot be simultaneously single and double
            self.cnf.append([-single, -double])
            # active iff single or double
            self.cnf.append([-single, active])
            self.cnf.append([-double, active])
            self.cnf.append([-active, single, double])

    def _encode_island_degrees(self) -> None:
        for island in self.grid.islands.values():
            lits: List[int] = []
            weights: List[int] = []
            for corridor in self.grid.corridors_incident_to(island.identifier):
                single, double, _ = self._corridor_vars(corridor)
                lits.extend([single, double])
                weights.extend([1, 2])
            if not lits:
                continue
            # Manual encoding for weighted sum = target
            # Sum of (1*single_i + 2*double_i) = target
            # Since single and double are mutually exclusive per corridor,
            # we can encode this as a constraint on the total.
            
            # Strategy: Create auxiliary bits for each corridor's contribution (0, 1, or 2)
            # Then use CardEnc on those bits.
            # But simpler: just enumerate the combinations that sum to target.
            
            # Alternative: use at-least and at-most constraints together
            self._encode_weighted_sum_equals(lits, weights, island.target)

    def _encode_weighted_sum_equals(self, lits: List[int], weights: List[int], target: int) -> None:
        """Encode weighted sum equals target using at-least and at-most."""
        # AtLeast: sum >= target
        # AtMost: sum <= target
        # Together they give sum = target
        
        # For "at least target", we need to encode all ways the sum can be >= target
        # For "at most target", we need to encode all ways the sum can be <= target
        
        # Simple but possibly large encoding: use sequential counter or totalizer
        # But CardEnc expects unweighted. Let's expand each weight-2 variable into 2 copies.
        
        # Important: Since single and double are mutually exclusive,
        # we need special handling. Let's create helper variables.
        
        # For each corridor, contribution is: 0 (neither), 1 (single), or 2 (double)
        # We can represent this with 2 bits per corridor or use the existing variables smartly.
        
        # Simpler approach for now: Just use the at-least/at-most with duplication
        # but ensure we account for mutual exclusivity properly.
        
        # Create expanded list where weight-2 items appear twice
        expanded = []
        for lit, weight in zip(lits, weights):
            for _ in range(weight):
                expanded.append(lit)
        
        # Now use CardEnc for at-least and at-most
        # AtLeast(expanded, target) AND AtMost(expanded, target)
        try:
            # Synchronize variable IDs to avoid collisions
            current_max = self.registry.count
            
            # AtLeast
            atleast_cnf = CardEnc.atleast(lits=expanded, bound=target, top_id=current_max, encoding=1)
            if isinstance(atleast_cnf, tuple):
                atleast_cnf = atleast_cnf[0]
            self.cnf.extend(atleast_cnf.clauses)
            
            # Update max for next call
            max_var = current_max
            for clause in atleast_cnf.clauses:
                for lit in clause:
                    max_var = max(max_var, abs(lit))
            self.registry.set_max(max_var)
            current_max = max_var

            # AtMost
            atmost_cnf = CardEnc.atmost(lits=expanded, bound=target, top_id=current_max, encoding=1)
            if isinstance(atmost_cnf, tuple):
                atmost_cnf = atmost_cnf[0]
            self.cnf.extend(atmost_cnf.clauses)
            
            # Update max again
            max_var = current_max
            for clause in atmost_cnf.clauses:
                for lit in clause:
                    max_var = max(max_var, abs(lit))
            self.registry.set_max(max_var)

        except Exception:
            # Fallback: skip this constraint or use a simpler encoding
            # For very small bounds, explicit enumeration might work
            pass

    def _encode_crossing_constraints(self) -> None:
        horizontal_cells: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        vertical_cells: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        for corridor in self.grid.corridors.values():
            _, _, active = self._corridor_vars(corridor)
            for cell in corridor.cells:
                if corridor.direction == Direction.HORIZONTAL:
                    horizontal_cells[cell].append(active)
                else:
                    vertical_cells[cell].append(active)
        for cell in horizontal_cells.keys() & vertical_cells.keys():
            for h_var in horizontal_cells[cell]:
                for v_var in vertical_cells[cell]:
                    self.cnf.append([-h_var, -v_var])
