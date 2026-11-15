#!/usr/bin/env python3
"""Run from any directory with Python 3.10+; no third-party dependencies."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from turtle_loop.cli import main
if __name__ == '__main__':
    raise SystemExit(main())
