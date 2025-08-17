"""
Score Following Debug System

This module provides comprehensive debugging and analysis tools for the 
score following algorithm implementation.

Key modules:
- debug_workflow: Main orchestration of the debug pipeline
- log_parser: Parses Serpent debug logs into structured data
- failure_analyzer: Analyzes failures and extracts context
- ai_analyzer: Generates AI analysis prompts and reports
- utils: Common utilities and helper functions
- config: Configuration settings and paths
"""

__version__ = "1.0.0"
__author__ = "Score Following Debug Team"

# Main entry points
from .debug_workflow import run_workflow, DebugWorkflow
from .log_parser import parse_log_file, LogParser
from .failure_analyzer import analyze_log_file, FailureAnalyzer
from .ai_analyzer import analyze_with_ai_prompt, AIAnalyzer
from .run_debug_test import TestExecutor

__all__ = [
    'run_workflow',
    'DebugWorkflow', 
    'parse_log_file',
    'LogParser',
    'analyze_log_file',
    'FailureAnalyzer',
    'analyze_with_ai_prompt',
    'AIAnalyzer',
    'TestExecutor'
]