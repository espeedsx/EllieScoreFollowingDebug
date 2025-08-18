"""
Utility functions for the score following debug system.
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from config import LOG_PATTERNS, LOGS_DIR


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up logging for debug modules."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_with_line(logger: logging.Logger, level: int, message: str, line_number: Optional[int] = None, context: Optional[str] = None) -> None:
    """Enhanced logging with line number and context for better debugging."""
    import inspect
    
    # Get caller information if line_number not provided
    if line_number is None:
        frame = inspect.currentframe().f_back
        line_number = frame.f_lineno
        filename = frame.f_code.co_filename
        function_name = frame.f_code.co_name
        caller_context = f"{Path(filename).name}:{function_name}:{line_number}"
    else:
        caller_context = f"line:{line_number}"
    
    # Format message with context
    if context:
        formatted_message = f"[{caller_context}] {message} | Context: {context}"
    else:
        formatted_message = f"[{caller_context}] {message}"
    
    logger.log(level, formatted_message)


def parse_pitch_list(pitch_str: str) -> List[int]:
    """Parse a comma-separated pitch string into a list of integers."""
    if not pitch_str.strip():
        # Empty string is valid - represents no pitches
        return []
    
    parts = [p.strip() for p in pitch_str.split(',') if p.strip()]
    try:
        return [int(p) for p in parts]
    except ValueError as e:
        raise ValueError(f"Invalid pitch value in string '{pitch_str}': {e}")


def format_time(timestamp: float) -> str:
    """Format a timestamp for display."""
    return f"{timestamp:.3f}"


def format_pitches(pitches: List[int]) -> str:
    """Format a list of pitches for display."""
    if not pitches:
        return "[]"
    return f"[{','.join(map(str, pitches))}]"


def find_latest_log(test_case_id: int) -> Path:
    """Find the most recent log file for a test case."""
    pattern = f"test_{test_case_id}_*.log"
    log_files = list(LOGS_DIR.glob(pattern))
    
    # Exclude temporary _serpent.log files
    log_files = [f for f in log_files if not f.name.endswith('_serpent.log')]
    
    if not log_files:
        raise FileNotFoundError(f"No log files found for test case {test_case_id} in {LOGS_DIR}")
    
    # Sort by modification time, return most recent
    return max(log_files, key=lambda f: f.stat().st_mtime)


def read_log_lines(log_file: Path) -> List[str]:
    """Read lines from a log file, handling encoding issues."""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return f.readlines()
    except UnicodeDecodeError:
        with open(log_file, 'r', encoding='latin-1') as f:
            return f.readlines()


def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single log line according to our debug format."""
    line = line.strip()
    
    # Skip empty lines and comments (these are valid to skip)
    if not line or line.startswith('#'):
        return None
    
    # Try each pattern
    for pattern_name, pattern in LOG_PATTERNS.items():
        match = re.match(pattern, line)
        if match:
            result = {
                'type': pattern_name,
                'raw_line': line,
                'groups': match.groups()
            }
            
            # Parse specific patterns
            if pattern_name == 'dp_entry':
                result.update({
                    'column': int(match.group(1)),
                    'row': int(match.group(2)),
                    'pitch': int(match.group(3)),
                    'time': float(match.group(4)),
                    'vertical_rule': float(match.group(5)),
                    'horizontal_rule': float(match.group(6)),
                    'final_value': float(match.group(7)),
                    'match_flag': bool(int(match.group(8))),
                    'used_pitches': parse_pitch_list(match.group(9)),
                    'unused_count': int(match.group(10))
                })
            elif pattern_name == 'match_found':
                result.update({
                    'row': int(match.group(1)),
                    'pitch': int(match.group(2)),
                    'time': float(match.group(3)),
                    'score': float(match.group(4))
                })
            elif pattern_name == 'no_match':
                result.update({
                    'pitch': int(match.group(1)),
                    'time': float(match.group(2))
                })
            elif pattern_name == 'test_start':
                result.update({
                    'test_case': int(match.group(1)),
                    'score_file': match.group(2),
                    'performance_file': match.group(3)
                })
            elif pattern_name == 'test_end':
                result.update({
                    'test_case': int(match.group(1)),
                    'matches': int(match.group(2)),
                    'total_notes': int(match.group(3))
                })
            # Ultra-comprehensive logging patterns
            elif pattern_name == 'input_event':
                result.update({
                    'column': int(match.group(1)),
                    'pitch': int(match.group(2)),
                    'time': float(match.group(3))
                })
            elif pattern_name == 'matrix_state':
                result.update({
                    'column': int(match.group(1)),
                    'window_start': int(match.group(2)),
                    'window_end': int(match.group(3)),
                    'window_center': int(match.group(4)),
                    'current_base': int(match.group(5)),
                    'prev_base': int(match.group(6)),
                    'current_upper': int(match.group(7)),
                    'prev_upper': int(match.group(8))
                })
            elif pattern_name == 'cell_state':
                result.update({
                    'row': int(match.group(1)),
                    'value': float(match.group(2)),
                    'used_pitches': parse_pitch_list(match.group(3)),
                    'unused_count': int(match.group(4)),
                    'time': float(match.group(5))
                })
            elif pattern_name == 'vertical_rule':
                result.update({
                    'row': int(match.group(1)),
                    'up_value': float(match.group(2)),
                    'penalty': float(match.group(3)),
                    'result': float(match.group(4)),
                    'start_point': match.group(5) == 't'
                })
            elif pattern_name == 'horizontal_rule':
                result.update({
                    'row': int(match.group(1)),
                    'prev_value': float(match.group(2)),
                    'pitch': int(match.group(3)),
                    'ioi': float(match.group(4)),
                    'limit': float(match.group(5)),
                    'timing_pass': match.group(6) == 't',
                    'match_type': match.group(7),
                    'result': float(match.group(8))
                })
            elif pattern_name == 'timing_check':
                result.update({
                    'prev_time': float(match.group(1)),
                    'curr_time': float(match.group(2)),
                    'ioi': float(match.group(3)),
                    'span': float(match.group(4)),
                    'limit': float(match.group(5)),
                    'timing_pass': match.group(6) == 't',
                    'constraint_type': match.group(7)
                })
            elif pattern_name == 'match_type':
                result.update({
                    'pitch': int(match.group(1)),
                    'is_chord': match.group(2) == 't',
                    'is_trill': match.group(3) == 't',
                    'is_grace': match.group(4) == 't',
                    'is_extra': match.group(5) == 't',
                    'is_ignored': match.group(6) == 't',
                    'already_used': match.group(7) == 't',
                    'timing_ok': match.group(8) == 't',
                    'ornament_info': match.group(9)
                })
            elif pattern_name == 'cell_decision':
                result.update({
                    'row': int(match.group(1)),
                    'vertical_result': float(match.group(2)),
                    'horizontal_result': float(match.group(3)),
                    'winner': match.group(4),
                    'updated': match.group(5) == 't',
                    'final_value': float(match.group(6)),
                    'reason': match.group(7)
                })
            elif pattern_name == 'array_neighborhood':
                # Parse the comma-separated values
                vals_str = match.group(2)
                neighbor_values = [float(v.strip()) for v in vals_str.split(',') if v.strip()]
                positions_str = match.group(3)
                positions = [int(p.strip()) for p in positions_str.split(',') if p.strip()]
                if not neighbor_values:
                    raise ValueError(f"Array neighborhood at line '{line}' has no neighbor values - parsing error")
                result.update({
                    'row': int(match.group(1)),
                    'center_value': neighbor_values[len(neighbor_values)//2],
                    'neighbor_values': neighbor_values,
                    'positions': positions
                })
            elif pattern_name == 'score_competition':
                result.update({
                    'row': int(match.group(1)),
                    'current_score': float(match.group(2)),
                    'top_score': float(match.group(3)),
                    'beats_top': match.group(4) == 't',
                    'margin': float(match.group(5)),
                    'confidence': float(match.group(6))
                })
            elif pattern_name == 'ornament_processing':
                result.update({
                    'pitch': int(match.group(1)),
                    'ornament_type': match.group(2),
                    'trill_pitches': parse_pitch_list(match.group(3)),
                    'grace_pitches': parse_pitch_list(match.group(4)),
                    'ignore_pitches': parse_pitch_list(match.group(5)),
                    'credit': float(match.group(6))
                })
            elif pattern_name == 'window_movement':
                result.update({
                    'old_center': int(match.group(1)),
                    'new_center': int(match.group(2)),
                    'old_start': int(match.group(3)),
                    'new_start': int(match.group(4)),
                    'old_end': int(match.group(5)),
                    'new_end': int(match.group(6)),
                    'reason': match.group(7)
                })
            
            return result
    
    # No pattern matched - this is normal for Serpent output lines, just skip them
    return None


def save_json(data: Any, filepath: Path) -> None:
    """Save data as JSON with proper formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: Path) -> Any:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m{secs:.1f}s"


def summarize_decision_sequence(decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize a sequence of DP decisions for analysis."""
    if not decisions:
        raise ValueError("Cannot summarize empty decision sequence - no decisions provided")
    
    # Validate all decisions have required fields
    required_fields = ['time', 'pitch', 'final_value', 'match_flag', 'column', 'row']
    for i, d in enumerate(decisions):
        missing_fields = [field for field in required_fields if field not in d]
        if missing_fields:
            raise ValueError(f"Decision {i} missing required fields: {missing_fields}")
    
    return {
        'count': len(decisions),
        'time_range': {
            'start': min(d['time'] for d in decisions),
            'end': max(d['time'] for d in decisions)
        },
        'pitch_range': {
            'min': min(d['pitch'] for d in decisions),
            'max': max(d['pitch'] for d in decisions)
        },
        'score_progression': [d['final_value'] for d in decisions],
        'match_count': sum(1 for d in decisions if d['match_flag']),
        'columns': sorted(set(d['column'] for d in decisions)),
        'rows': sorted(set(d['row'] for d in decisions))
    }


class DebugMetrics:
    """Track metrics during debug analysis."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.lines_processed = 0
        self.dp_entries = 0
        self.matches_found = 0
        self.failures_detected = 0
    
    def record_line(self):
        self.lines_processed += 1
    
    def record_dp_entry(self):
        self.dp_entries += 1
    
    def record_match(self):
        self.matches_found += 1
    
    def record_failure(self):
        self.failures_detected += 1
    
    def get_summary(self) -> Dict[str, Any]:
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if duration <= 0:
            raise RuntimeError(f"Invalid duration {duration} seconds - processing time calculation failed")
        
        return {
            'duration_seconds': duration,
            'lines_processed': self.lines_processed,
            'dp_entries': self.dp_entries,
            'matches_found': self.matches_found,
            'failures_detected': self.failures_detected,
            'processing_rate': self.lines_processed / duration
        }