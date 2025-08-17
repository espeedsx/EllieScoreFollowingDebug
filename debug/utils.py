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


def parse_pitch_list(pitch_str: str) -> List[int]:
    """Parse a comma-separated pitch string into a list of integers."""
    if not pitch_str.strip():
        return []
    return [int(p.strip()) for p in pitch_str.split(',') if p.strip()]


def format_time(timestamp: float) -> str:
    """Format a timestamp for display."""
    return f"{timestamp:.3f}"


def format_pitches(pitches: List[int]) -> str:
    """Format a list of pitches for display."""
    if not pitches:
        return "[]"
    return f"[{','.join(map(str, pitches))}]"


def find_latest_log(test_case_id: int) -> Optional[Path]:
    """Find the most recent log file for a test case."""
    pattern = f"test_{test_case_id}_*.log"
    log_files = list(LOGS_DIR.glob(pattern))
    
    if not log_files:
        return None
    
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
            
            return result
    
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
        return {}
    
    return {
        'count': len(decisions),
        'time_range': {
            'start': min(d['time'] for d in decisions if 'time' in d),
            'end': max(d['time'] for d in decisions if 'time' in d)
        },
        'pitch_range': {
            'min': min(d['pitch'] for d in decisions if 'pitch' in d),
            'max': max(d['pitch'] for d in decisions if 'pitch' in d)
        },
        'score_progression': [d.get('final_value', 0) for d in decisions],
        'match_count': sum(1 for d in decisions if d.get('match_flag', False)),
        'columns': sorted(set(d['column'] for d in decisions if 'column' in d)),
        'rows': sorted(set(d['row'] for d in decisions if 'row' in d))
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
        return {
            'duration_seconds': duration,
            'lines_processed': self.lines_processed,
            'dp_entries': self.dp_entries,
            'matches_found': self.matches_found,
            'failures_detected': self.failures_detected,
            'processing_rate': self.lines_processed / duration if duration > 0 else 0
        }