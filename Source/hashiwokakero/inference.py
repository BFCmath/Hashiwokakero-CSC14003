"""Utilities to interpret SAT models."""

from __future__ import annotations

from typing import Dict, Iterable

from .grid import Grid
from .state import PuzzleState
from .variables import VariableRegistry


class InferenceEngine:
    def __init__(self, grid: Grid, registry: VariableRegistry):
        self.grid = grid
        self.registry = registry

    def state_from_model(self, model: Iterable[int]) -> PuzzleState:
        assignment = set(var for var in model if var > 0)
        state = PuzzleState(self.grid)
        for corridor in self.grid.corridors.values():
            single = self.registry.var("corridor_single", corridor.identifier)
            double = self.registry.var("corridor_double", corridor.identifier)
            value = 2 if double in assignment else 1 if single in assignment else 0
            if value:
                state.set_corridor_value(corridor.identifier, value)
        return state
