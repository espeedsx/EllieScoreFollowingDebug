"""
Configuration file for the score following debug system.
"""

import os
from pathlib import Path

# Base paths
SRC_DIR = Path(__file__).parent  # This is now debug/src
DEBUG_DIR = SRC_DIR.parent       # This is debug
ROOT_DIR = DEBUG_DIR.parent      # This is the project root
SERPENT_SRC_DIR = ROOT_DIR / "src"  # This is the Serpent source directory

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

# Readable log patterns
LOG_PATTERNS = {
    "dp_entry": r"DP\|column:(\d+)\|row:(\d+)\|pitch:(\d+)\|perf_time:([\d.]+)\|vertical_rule:([-\d.]+)\|horizontal_rule:([-\d.]+)\|final_value:([-\d.]+)\|match:([01])\|used_pitches:\[([\d,\s]*)\]\|unused_count:([-\d]+)",
    "match_found": r"MATCH\|row:(\d+)\|pitch:(\d+)\|perf_time:([\d.]+)\|score:([\d.]+)",
    "no_match": r"NO_MATCH\|pitch:(\d+)\|perf_time:([\d.]+)",
    "test_start": r"TEST_START\|test_case:(\d+)\|score_file:(.*)\|performance_file:(.*)",
    "test_end": r"TEST_END\|test_case:(\d+)\|matches_found:(\d+)\|total_notes:(\d+)",
    
    # Ultra-comprehensive logging patterns
    "input_event": r"INPUT\|column:(\d+)\|pitch:(\d+)\|perf_time:([\d.]+)",
    "matrix_state": r"MATRIX\|column:(\d+)\|window_start:(\d+)\|window_end:(\d+)\|window_center:(\d+)\|current_base:(\d+)\|prev_base:(\d+)\|current_upper:(\d+)\|prev_upper:(\d+)",
    "cell_state": r"CELL\|row:(\d+)\|value:([-\d.]+)\|used_pitches:\[([\d,\s]*)\]\|unused_count:([-\d]+)\|cell_time:([-\d.]+)\|score_time:([-\d.]+)",
    "vertical_rule": r"VRULE\|row:(\d+)\|up_value:([-\d.]+)\|penalty:([-\d.]+)\|result:([-\d.]+)\|start_point:(\w+)",
    "horizontal_rule": r"HRULE\|row:(\d+)\|prev_value:([-\d.]+)\|pitch:(\d+)\|ioi:([-\d.]+)\|limit:([-\d.]+)\|timing_pass:(\w+)\|match_type:(\w+)\|result:([-\d.]+)",
    "timing_check": r"TIMING\|prev_cell_time:([-\d.]+)\|curr_perf_time:([-\d.]+)\|ioi:([-\d.]+)\|span:([-\d.]+)\|limit:([-\d.]+)\|timing_pass:(\w+)\|constraint_type:(\w+)",
    "match_type": r"MATCH_TYPE\|pitch:(\d+)\|is_chord:(\w+)\|is_trill:(\w+)\|is_grace:(\w+)\|is_extra:(\w+)\|is_ignored:(\w+)\|already_used:(\w+)\|timing_ok:(\w+)\|ornament_info:(\w+)",
    "cell_decision": r"DECISION\|row:(\d+)\|vertical_result:([-\d.]+)\|horizontal_result:([-\d.]+)\|winner:(\w+)\|updated:(\w+)\|final_value:([-\d.]+)\|reason:(\w+)",
    "array_neighborhood": r"ARRAY\|row:(\d+)\|center_value:([-\d.]+)\|values:\[([-\d.,\s]+)\]\|positions:\[([-\d,\s]+)\]",
    "score_competition": r"SCORE\|row:(\d+)\|current_score:([-\d.]+)\|top_score:([-\d.]+)\|beats_top:(\w+)\|margin:([-\d.]+)\|confidence:([-\d.]+)",
    "ornament_processing": r"ORNAMENT\|pitch:(\d+)\|ornament_type:(\w+)\|trill_pitches:\[([\d,]*)\]\|grace_pitches:\[([\d,]*)\]\|ignore_pitches:\[([\d,]*)\]\|credit_applied:([-\d.]+)",
    "window_movement": r"WINDOW_MOVE\|old_center:(\d+)\|new_center:(\d+)\|old_start:(\d+)\|new_start:(\d+)\|old_end:(\d+)\|new_end:(\d+)\|reason:(\w+)",
    "cevent_summary": r"CEVENT\|row:(\d+)\|score_time:([-\d.]+)\|pitch_count:(\d+)\|time_span:([-\d.]+)\|ornament_count:(\d+)\|expected:(\d+)"
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