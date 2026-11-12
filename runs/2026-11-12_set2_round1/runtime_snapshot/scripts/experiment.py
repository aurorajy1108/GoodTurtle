#!/usr/bin/env python3
"""Run context-transfer or two-solver experiments from the repository root."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from turtle_loop.experiments import main
if __name__ == '__main__':
    raise SystemExit(main())
