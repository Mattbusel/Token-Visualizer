#!/usr/bin/env python3
"""Backward-compatible entry point. The code now lives in token_visualizer.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from token_visualizer import *  # noqa: E402,F401,F403
from token_visualizer import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
