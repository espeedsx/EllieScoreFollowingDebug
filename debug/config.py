"""
Configuration file for the score following debug system.
"""

import os
from pathlib import Path

# Base paths
DEBUG_DIR = Path(__file__).parent
ROOT_DIR = DEBUG_DIR.parent
SRC_DIR = ROOT_DIR / "src"

# Log directories
LOGS_DIR = DEBUG_DIR / "logs"
ANALYSIS_DIR = DEBUG_DIR / "analysis" 
REPORTS_DIR = DEBUG_DIR / "reports"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Test execution settings
SERPENT_EXECUTABLE = "serpent64"
TEST_SCRIPT = "run_bench"
TEST_TIMEOUT = 10   # seconds

# Debug log format
DEBUG_LOG_PREFIX = "DP|"
DEBUG_FIELDS = [
    "c",     # column
    "r",     # row
    "p",     # pitch
    "t",     # time
    "vr",    # vertical rule value
    "hr",    # horizontal rule value
    "f",     # final value
    "m",     # match flag
    "u",     # used pitches
    "uc"     # unused count
]

# Analysis settings
FAILURE_CONTEXT_WINDOW = 5  # decisions before failure to analyze
MAX_LOG_SIZE_MB = 10        # maximum log file size to process
AI_ANALYSIS_MODEL = "claude-3-sonnet-20240229"

# Compact log patterns
LOG_PATTERNS = {
    "dp_entry": r"DP\|c:(\d+)\|r:(\d+)\|p:(\d+)\|t:([\d.]+)\|vr:([-\d.]+)\|hr:([-\d.]+)\|f:([-\d.]+)\|m:([01])\|u:\[([\d,]*)\]\|uc:(\d+)",
    "match_found": r"MATCH\|r:(\d+)\|p:(\d+)\|t:([\d.]+)\|score:([\d.]+)",
    "no_match": r"NO_MATCH\|p:(\d+)\|t:([\d.]+)",
    "test_start": r"TEST_START\|case:(\d+)\|score:(.*)\|perf:(.*)",
    "test_end": r"TEST_END\|case:(\d+)\|matches:(\d+)\|total:(\d+)",
    
    # Ultra-comprehensive logging patterns
    "input_event": r"INPUT\|c:(\d+)\|p:(\d+)\|t:([\d.]+)",
    "matrix_state": r"MATRIX\|c:(\d+)\|ws:(\d+)\|we:(\d+)\|wc:(\d+)\|cb:(\d+)\|pb:(\d+)\|cu:(\d+)\|pu:(\d+)",
    "cell_state": r"CELL\|r:(\d+)\|v:([-\d.]+)\|u:\[([\d,]*)\]\|uc:(\d+)\|t:([-\d.]+)",
    "vertical_rule": r"VRULE\|r:(\d+)\|up:([-\d.]+)\|pen:([-\d.]+)\|res:([-\d.]+)\|sp:(\w+)",
    "horizontal_rule": r"HRULE\|r:(\d+)\|pv:([-\d.]+)\|pit:(\d+)\|ioi:([-\d.]+)\|lim:([-\d.]+)\|pass:(\w+)\|typ:(\w+)\|res:([-\d.]+)",
    "timing_check": r"TIMING\|pt:([-\d.]+)\|ct:([-\d.]+)\|ioi:([-\d.]+)\|span:([-\d.]+)\|lim:([-\d.]+)\|pass:(\w+)\|type:(\w+)",
    "match_type": r"MATCH_TYPE\|pit:(\d+)\|ch:(\w+)\|tr:(\w+)\|gr:(\w+)\|ex:(\w+)\|ign:(\w+)\|used:(\w+)\|time:(\w+)\|orn:(\w+)",
    "cell_decision": r"DECISION\|r:(\d+)\|vr:([-\d.]+)\|hr:([-\d.]+)\|win:(\w+)\|upd:(\w+)\|val:([-\d.]+)\|reason:(\w+)",
    "array_neighborhood": r"ARRAY\|r:(\d+)\|center:([-\d.]+)\|vals:\[([-\d.,\s]+)\]\|pos:\[([-\d,\s]+)\]",
    "score_competition": r"SCORE\|r:(\d+)\|cur:([-\d.]+)\|top:([-\d.]+)\|beat:(\w+)\|margin:([-\d.]+)\|conf:([-\d.]+)",
    "ornament_processing": r"ORNAMENT\|pit:(\d+)\|type:(\w+)\|tr:\[([\d,]*)\]\|gr:\[([\d,]*)\]\|ig:\[([\d,]*)\]\|credit:([-\d.]+)",
    "window_movement": r"WINDOW_MOVE\|oc:(\d+)\|nc:(\d+)\|os:(\d+)\|ns:(\d+)\|oe:(\d+)\|ne:(\d+)\|reason:(\w+)"
}

# File naming conventions
def get_log_filename(test_case_id, timestamp=None):
    """Generate log filename for a test case."""
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"test_{test_case_id}_{timestamp}.log"

def get_analysis_filename(test_case_id, timestamp=None):
    """Generate analysis filename for a test case."""
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"analysis_{test_case_id}_{timestamp}.json"

def get_report_filename(test_case_id, timestamp=None):
    """Generate report filename for a test case."""
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"report_{test_case_id}_{timestamp}.md"