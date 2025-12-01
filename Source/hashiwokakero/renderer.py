"""Output rendering utilities."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .state import PuzzleState


class Renderer:
    def __init__(self, state: PuzzleState) -> None:
        self.state = state

    def render(self) -> str:
        """
        Renders the puzzle state into the required string format.
        Example output format:
        [ "0" , "2" , "=" , "5" , "-" , "-" , "2" ]
        ...
        """
        matrix = self.state.to_symbol_matrix()
        lines = []
        for row in matrix:
            # Format each row as a list of strings: [ "0" , "2" , ... ]
            # The requirement example shows spaces around commas and quotes
            # [ "0" , "2" , "=" , "5" , "-" , "-" , "2" ]
            formatted_items = [f'"{item}"' for item in row]
            line = "[ " + " , ".join(formatted_items) + " ]"
            lines.append(line)
        return "\n".join(lines)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        output_text = self.render()
        path.write_text(output_text + "\n", encoding="utf-8")
