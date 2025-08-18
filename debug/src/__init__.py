"""
Score Following Debug System

This module provides log generation and CSV processing tools for the 
score following algorithm implementation.

Key modules:
- debug: Main launcher for log and CSV generation
- run_debug_test: Executes Serpent tests with debug logging
- log_flattener: Converts debug logs to structured CSV format
- utils: Common utilities and helper functions
- config: Configuration settings and paths
"""

__version__ = "1.0.0"
__author__ = "Score Following Debug Team"

# Main entry points
from .run_debug_test import TestExecutor
from .log_flattener import LogFlattener

__all__ = [
    'TestExecutor',
    'LogFlattener'
]