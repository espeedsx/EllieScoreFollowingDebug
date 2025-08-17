#!/usr/bin/env python3
"""
Convenience wrapper for debug_workflow.py in src/

This maintains backward compatibility for the original command structure.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the actual debug workflow from src/
try:
    from debug_workflow import main
    if __name__ == "__main__":
        sys.exit(main())
except ImportError as e:
    print(f"Error: Could not import debug_workflow from {src_dir}")
    print(f"Import error: {e}")
    print(f"Please run from debug/src/ directory or fix the path")
    sys.exit(1)