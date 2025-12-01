#!/usr/bin/env python3
"""
Entry point script to run the Hashiwokakero solver.
Usage: python run.py Source/Inputs/input-01.txt
"""

import sys
from pathlib import Path

# Add Source directory to python path so we can import the package
source_path = Path(__file__).parent / "Source"
sys.path.insert(0, str(source_path))

from hashiwokakero.cli import run_cli

if __name__ == "__main__":
    run_cli()
