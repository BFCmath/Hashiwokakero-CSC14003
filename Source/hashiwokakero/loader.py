"""Input parsing utilities for Hashiwokakero."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .grid import Grid


@dataclass
class PuzzleLoader:
    """Utility class to load puzzle instances from txt files."""

    @staticmethod
    def load(path: str | Path) -> Grid:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        rows: List[List[int]] = []
        for raw_line in path.read_text(encoding="utf-8").strip().splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            tokens = [token.strip() for token in raw_line.replace("\t", " ").split(",")]
            row = [int(tok) for tok in tokens if tok]
            if not row:
                continue
            rows.append(row)
        if not rows:
            raise ValueError("Input file is empty")
        width = len(rows[0])
        for row in rows:
            if len(row) != width:
                raise ValueError("Inconsistent row lengths in input file")
        return Grid(rows)
