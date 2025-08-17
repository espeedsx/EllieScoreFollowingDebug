#!/usr/bin/env python3
"""
Log Flattener for Score Following Debug Analysis

Converts multi-line debug logs into a single flattened CSV where each row represents
one complete dynamic programming decision with all contextual information.

This enables pattern analysis to identify what conditions lead to no-match/mismatch scenarios.
"""

import re
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, fields
from collections import defaultdict
from tqdm import tqdm

from config import LOG_PATTERNS
from utils import setup_logging

logger = setup_logging(__name__)


@dataclass
class FlattenedLogEntry:
    """Complete flattened representation of a DP decision with all context."""
    
    # INPUT GROUP - Shared context for all DP decisions in same column
    input_column: int = 0
    input_pitch: int = 0
    input_perf_time: float = 0.0
    
    # MATCH GROUP - Only populated if this resulted in a successful match
    match_row: int = 0
    match_pitch: int = 0
    match_perf_time: float = 0.0
    match_score: float = 0.0
    
    # NO_MATCH GROUP - Only populated if this resulted in no match
    no_match_pitch: int = 0
    no_match_perf_time: float = 0.0
    
    # MATRIX GROUP - Shared matrix state for all decisions in same column
    matrix_window_start: int = 0
    matrix_window_end: int = 0
    matrix_window_center: int = 0
    matrix_current_base: int = 0
    matrix_prev_base: int = 0
    matrix_current_upper: int = 0
    matrix_prev_upper: int = 0
    
    # CEVENT GROUP - Shared score event context for all decisions in same row
    cevent_row: int = 0
    cevent_score_time: float = 0.0
    cevent_pitch_count: int = 0
    cevent_time_span: float = 0.0
    cevent_ornament_count: int = 0
    cevent_expected: int = 0
    
    # DP GROUP - Core dynamic programming decision
    dp_row: int = 0
    dp_vertical_rule: float = 0.0
    dp_horizontal_rule: float = 0.0
    dp_final_value: float = 0.0
    dp_match: int = 0
    dp_used_pitches: str = ""
    dp_unused_count: int = 0
    
    # CELL GROUP - Cell state before processing
    cell_time: float = -1.0
    cell_value: float = 0.0
    cell_used_pitches: str = ""
    cell_unused_count: int = 0
    cell_score_time: float = 0.0
    
    # VRULE GROUP - Vertical rule calculation details
    vrule_up_value: float = 0.0
    vrule_penalty: float = 0.0
    vrule_result: float = 0.0
    vrule_start_point: str = ""
    
    # HRULE GROUP - Horizontal rule calculation details
    hrule_prev_value: float = 0.0
    hrule_ioi: float = 0.0
    hrule_limit: float = 0.0
    hrule_timing_pass: str = ""
    hrule_match_type: str = ""
    hrule_result: float = 0.0
    
    # TIMING GROUP - Detailed timing constraint analysis
    timing_prev_cell_time: float = -1.0
    timing_curr_perf_time: float = 0.0
    timing_ioi: float = 0.0
    timing_span: float = 0.0
    timing_limit: float = 0.0
    timing_pass: str = ""
    timing_constraint_type: str = ""
    
    # MATCHTYPE GROUP - Match type classification analysis
    matchtype_is_chord: str = ""
    matchtype_is_trill: str = ""
    matchtype_is_grace: str = ""
    matchtype_is_extra: str = ""
    matchtype_is_ignored: str = ""
    matchtype_already_used: str = ""
    matchtype_timing_ok: str = ""
    matchtype_ornament_info: str = ""
    
    # DECISION GROUP - Final cell decision
    decision_vertical_result: float = 0.0
    decision_horizontal_result: float = 0.0
    decision_winner: str = ""
    decision_updated: str = ""
    decision_final_value: float = 0.0
    decision_reason: str = ""
    
    # SCORE GROUP - Score competition analysis
    score_current_score: float = 0.0
    score_top_score: float = 0.0
    score_beats_top: str = ""
    score_margin: float = 0.0
    score_confidence: float = 0.0
    
    # ORNAMENT GROUP - Ornament processing details
    ornament_type: str = ""
    ornament_trill_pitches: str = ""
    ornament_grace_pitches: str = ""
    ornament_ignore_pitches: str = ""
    ornament_credit_applied: float = 0.0
    
    # ARRAY GROUP - Array neighborhood context
    array_center_value: float = 0.0
    array_neighbor_values: str = ""
    array_neighbor_positions: str = ""
    
    # RESULT GROUP - Final result classification
    result_type: str = ""  # "match", "no_match", "unprocessed"
    
    # BUG GROUP - Algorithm bug detection
    bug_has_timing_bug: bool = False
    bug_description: str = ""


class LogFlattener:
    """Flattens multi-line log entries into single CSV rows for analysis."""
    
    def __init__(self):
        self.patterns = {name: re.compile(pattern) for name, pattern in LOG_PATTERNS.items()}
        self.current_input_context = {}  # Shared context for current input
        self.current_dp_entries = {}  # row -> FlattenedLogEntry for current input
        self.pending_cevent_data = {}  # row -> cevent data (for entries not yet created)
        self.completed_entries = []
        self.stats = defaultdict(int)
        
    def parse_log_file(self, log_file_path: Path) -> List[FlattenedLogEntry]:
        """Parse a log file and return flattened entries."""
        logger.info(f"Parsing log file: {log_file_path}")
        
        self.current_input_context = {}
        self.current_dp_entries = {}
        self.pending_cevent_data = {}
        self.completed_entries = []
        self.stats = defaultdict(int)
        
        # Get total number of lines for progress bar
        logger.info("Counting lines for progress tracking...")
        with open(log_file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        
        logger.info(f"Processing {total_lines:,} lines...")
        
        with open(log_file_path, 'r', encoding='utf-8') as f:
            with tqdm(total=total_lines, desc="Parsing log", unit="lines", 
                     bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        pbar.update(1)
                        continue
                        
                    try:
                        self._process_line(line, line_num)
                    except Exception as e:
                        logger.warning(f"Error processing line {line_num}: {e}")
                        continue
                    
                    pbar.update(1)
                    
                    # Update progress description periodically
                    if line_num % 5000 == 0:
                        entries_so_far = len(self.current_dp_entries) + len(self.completed_entries)
                        pbar.set_description(f"Parsing log ({entries_so_far} entries)")
        
        # Add any remaining entries from the last input
        if self.current_dp_entries:
            if 'result_type' not in self.current_input_context:
                logger.warning("Final input has no MATCH/NO_MATCH result")
            self._finalize_current_input()
        
        logger.info(f"Processed {len(self.completed_entries)} complete entries")
        self._log_stats()
        
        return self.completed_entries
    
    def _process_line(self, line: str, line_num: int):
        """Process a single log line and update current entries."""
        self.stats['total_lines'] += 1
        
        # Check for MATCH/NO_MATCH results first (these are more important)
        if line.startswith('MATCH|'):
            self._handle_match_result(line)
            return
        elif line.startswith('NO_MATCH|'):
            self._handle_no_match_result(line)
            return
            
        # Try to match against all patterns
        for log_type, pattern in self.patterns.items():
            match = pattern.match(line)
            if match:
                self.stats[f'{log_type}_lines'] += 1
                self._handle_log_entry(log_type, match, line_num)
                return
        
        self.stats['unmatched_lines'] += 1
    

    def _finalize_current_input(self):
        """Finalize current input by copying shared context to all DP entries and adding to completed."""
        logger.debug(f"Finalizing input with context: {self.current_input_context}")
        logger.debug(f"DP entries count: {len(self.current_dp_entries)}")
        
        for entry in self.current_dp_entries.values():
            # Copy shared input context to this entry
            for key, value in self.current_input_context.items():
                setattr(entry, key, value)
            
            self.completed_entries.append(entry)
        
        # Reset for next input
        self.current_dp_entries = {}
        self.current_input_context = {}
        self.pending_cevent_data = {}

    def _handle_log_entry(self, log_type: str, match: re.Match, line_num: int):
        """Handle a matched log entry by updating the appropriate flattened entry."""
        
        if log_type == 'input_event':
            # Start of a new input - finalize any previous input only if it has a result
            if self.current_dp_entries and 'result_type' in self.current_input_context:
                self._finalize_current_input()
            elif self.current_dp_entries:
                # Previous input has no result yet - this shouldn't happen in normal logs
                logger.warning(f"Previous input had no MATCH/NO_MATCH result, finalizing anyway")
                self._finalize_current_input()
            
            # Store input context
            column, pitch, perf_time = match.groups()
            self.current_input_context = {
                'input_column': int(column),
                'input_pitch': int(pitch),
                'input_perf_time': float(perf_time)
            }
            logger.debug(f"Started new input: column={column}, pitch={pitch}, perf_time={perf_time}")
            
        elif log_type == 'dp_entry':
            # Start of a new DP decision within current input
            column, row, pitch, perf_time, vertical_rule, horizontal_rule, final_value, match_flag, used_pitches, unused_count = match.groups()
            
            entry = FlattenedLogEntry(
                dp_row=int(row),
                dp_vertical_rule=float(vertical_rule),
                dp_horizontal_rule=float(horizontal_rule),
                dp_final_value=float(final_value),
                dp_match=int(match_flag),
                dp_used_pitches=used_pitches,
                dp_unused_count=int(unused_count)
            )
            
            # Store by row within current input
            row_int = int(row)
            self.current_dp_entries[row_int] = entry
            
            # Apply any pending CEVENT data for this row
            if row_int in self.pending_cevent_data:
                cevent_data = self.pending_cevent_data[row_int]
                for key, value in cevent_data.items():
                    setattr(entry, key, value)
                logger.debug(f"Applied pending CEVENT to DP entry for row {row_int}")
                # Remove from pending since it's now applied
                del self.pending_cevent_data[row_int]
            
        elif log_type == 'cevent_summary':
            # Score event information
            row, score_time, pitch_count, time_span, ornament_count, expected = match.groups()
            row = int(row)
            
            # Store CEVENT data - either apply immediately or store for later
            cevent_data = {
                'cevent_row': row,
                'cevent_score_time': float(score_time),
                'cevent_pitch_count': int(pitch_count),
                'cevent_time_span': float(time_span),
                'cevent_ornament_count': int(ornament_count),
                'cevent_expected': int(expected)
            }
            
            if row in self.current_dp_entries:
                # DP entry exists - apply CEVENT data immediately
                entry = self.current_dp_entries[row]
                for key, value in cevent_data.items():
                    setattr(entry, key, value)
                logger.debug(f"Applied CEVENT for row {row}: score_time={score_time}, pitch_count={pitch_count}")
            else:
                # DP entry doesn't exist yet - store for later
                self.pending_cevent_data[row] = cevent_data
                logger.debug(f"Stored pending CEVENT for row {row}: score_time={score_time}, pitch_count={pitch_count}")
        
        elif log_type == 'cell_state':
            # Cell state information
            row, value, used_pitches, unused_count, cell_time, score_time = match.groups()
            row = int(row)
            
            if row in self.current_dp_entries:
                entry = self.current_dp_entries[row]
                entry.cell_time = float(cell_time)
                entry.cell_value = float(value)
                entry.cell_used_pitches = used_pitches
                entry.cell_unused_count = int(unused_count)
                entry.cell_score_time = float(score_time)
        
        elif log_type == 'vertical_rule':
            # Vertical rule calculation
            row, up_value, penalty, result, start_point = match.groups()
            row = int(row)
            
            if row in self.current_dp_entries:
                entry = self.current_dp_entries[row]
                entry.vrule_up_value = float(up_value)
                entry.vrule_penalty = float(penalty)
                entry.vrule_result = float(result)
                entry.vrule_start_point = start_point
        
        elif log_type == 'horizontal_rule':
            # Horizontal rule calculation
            row, prev_value, pitch, ioi, limit, timing_pass, match_type, result = match.groups()
            row = int(row)
            
            if row in self.current_dp_entries:
                entry = self.current_dp_entries[row]
                entry.hrule_prev_value = float(prev_value)
                entry.hrule_ioi = float(ioi)
                entry.hrule_limit = float(limit)
                entry.hrule_timing_pass = timing_pass
                entry.hrule_match_type = match_type
                entry.hrule_result = float(result)
        
        elif log_type == 'timing_check':
            # Detailed timing analysis - applies to most recent DP entry
            prev_cell_time, curr_perf_time, ioi, span, limit, timing_pass, constraint_type = match.groups()
            
            # Apply to the most recent DP entry (highest row number)
            if self.current_dp_entries:
                latest_row = max(self.current_dp_entries.keys())
                entry = self.current_dp_entries[latest_row]
                entry.timing_prev_cell_time = float(prev_cell_time)
                entry.timing_curr_perf_time = float(curr_perf_time)
                entry.timing_ioi = float(ioi)
                entry.timing_span = float(span)
                entry.timing_limit = float(limit)
                entry.timing_pass = timing_pass
                entry.timing_constraint_type = constraint_type
                
                # Detect algorithm bug
                if float(prev_cell_time) == -1.0 and float(ioi) > 20.0:
                    entry.bug_has_timing_bug = True
                    entry.bug_description = f"Cell time initialization bug: prev_time=-1, ioi={ioi}"
        
        elif log_type == 'match_type':
            # Match type analysis - applies to most recent DP entry (the one being analyzed)
            pitch, is_chord, is_trill, is_grace, is_extra, is_ignored, already_used, timing_ok, ornament_info = match.groups()
            
            # Apply to the most recent DP entry (should match input pitch)
            if self.current_dp_entries:
                latest_row = max(self.current_dp_entries.keys())
                entry = self.current_dp_entries[latest_row]
                entry.matchtype_is_chord = is_chord
                entry.matchtype_is_trill = is_trill
                entry.matchtype_is_grace = is_grace
                entry.matchtype_is_extra = is_extra
                entry.matchtype_is_ignored = is_ignored
                entry.matchtype_already_used = already_used
                entry.matchtype_timing_ok = timing_ok
                entry.matchtype_ornament_info = ornament_info
        
        elif log_type == 'cell_decision':
            # Cell decision result
            row, vertical_result, horizontal_result, winner, updated, final_value, reason = match.groups()
            row = int(row)
            
            if row in self.current_dp_entries:
                entry = self.current_dp_entries[row]
                entry.decision_vertical_result = float(vertical_result)
                entry.decision_horizontal_result = float(horizontal_result)
                entry.decision_winner = winner
                entry.decision_updated = updated
                entry.decision_final_value = float(final_value)
                entry.decision_reason = reason
        
        elif log_type == 'score_competition':
            # Score competition analysis
            row, current_score, top_score, beats_top, margin, confidence = match.groups()
            row = int(row)
            
            if row in self.current_dp_entries:
                entry = self.current_dp_entries[row]
                entry.score_current_score = float(current_score)
                entry.score_top_score = float(top_score)
                entry.score_beats_top = beats_top
                entry.score_margin = float(margin)
                entry.score_confidence = float(confidence)
        
        elif log_type == 'ornament_processing':
            # Ornament processing - applies to most recent DP entry
            pitch, ornament_type, trill_pitches, grace_pitches, ignore_pitches, credit_applied = match.groups()
            
            if self.current_dp_entries:
                latest_row = max(self.current_dp_entries.keys())
                entry = self.current_dp_entries[latest_row]
                entry.ornament_type = ornament_type
                entry.ornament_trill_pitches = trill_pitches
                entry.ornament_grace_pitches = grace_pitches
                entry.ornament_ignore_pitches = ignore_pitches
                entry.ornament_credit_applied = float(credit_applied)
        
        elif log_type == 'matrix_state':
            # Matrix window state - shared context for current input
            column, window_start, window_end, window_center, current_base, prev_base, current_upper, prev_upper = match.groups()
            
            # Store in shared context to be applied to all DP entries for this input
            self.current_input_context.update({
                'matrix_window_start': int(window_start),
                'matrix_window_end': int(window_end),
                'matrix_window_center': int(window_center),
                'matrix_current_base': int(current_base),
                'matrix_prev_base': int(prev_base),
                'matrix_current_upper': int(current_upper),
                'matrix_prev_upper': int(prev_upper)
            })
        
        elif log_type == 'array_neighborhood':
            # Array neighborhood context
            row, center_value, values, positions = match.groups()
            row = int(row)
            
            if row in self.current_dp_entries:
                entry = self.current_dp_entries[row]
                entry.array_center_value = float(center_value)
                entry.array_neighbor_values = values
                entry.array_neighbor_positions = positions
    
    def _handle_match_result(self, line: str):
        """Handle MATCH result line - stores match info in shared context for all DP entries."""
        match = self.patterns['match_found'].match(line)
        if match:
            row, pitch, perf_time, score = match.groups()
            
            # Store match information in shared context to be applied to ALL DP entries for this input
            self.current_input_context.update({
                'result_type': 'match',
                'match_row': int(row),
                'match_pitch': int(pitch),
                'match_perf_time': float(perf_time),
                'match_score': float(score)
            })
            logger.debug(f"Processed MATCH: row={row}, pitch={pitch}, perf_time={perf_time}, score={score}")
            
            # Finalize current input now that we have the result
            if self.current_dp_entries:
                self._finalize_current_input()
        else:
            logger.warning(f"Failed to parse MATCH line: {line}")
    
    def _handle_no_match_result(self, line: str):
        """Handle NO_MATCH result line - stores no_match info in shared context for all DP entries."""
        match = self.patterns['no_match'].match(line)
        if match:
            pitch, perf_time = match.groups()
            
            # Store no_match information in shared context to be applied to ALL DP entries for this input
            self.current_input_context.update({
                'result_type': 'no_match',
                'no_match_pitch': int(pitch),
                'no_match_perf_time': float(perf_time)
            })
            logger.debug(f"Processed NO_MATCH: pitch={pitch}, perf_time={perf_time}")
            
            # Finalize current input now that we have the result
            if self.current_dp_entries:
                self._finalize_current_input()
        else:
            logger.warning(f"Failed to parse NO_MATCH line: {line}")
    
    def _log_stats(self):
        """Log parsing statistics."""
        logger.info("Parsing Statistics:")
        for stat_name, count in sorted(self.stats.items()):
            logger.info(f"  {stat_name}: {count}")
    
    def write_csv(self, entries: List[FlattenedLogEntry], output_path: Path):
        """Write flattened entries to CSV file."""
        logger.info(f"Writing {len(entries)} entries to {output_path}")
        
        # Get all field names from the dataclass
        field_names = [field.name for field in fields(FlattenedLogEntry)]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            
            # Write with progress bar for large datasets
            with tqdm(entries, desc="Writing CSV", unit="entries", 
                     bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                for entry in pbar:
                    # Convert dataclass to dict
                    row_dict = {field.name: getattr(entry, field.name) for field in fields(entry)}
                    writer.writerow(row_dict)
        
        logger.info(f"CSV file written successfully")
    
    def analyze_patterns(self, entries: List[FlattenedLogEntry]) -> Dict[str, Any]:
        """Analyze patterns in the flattened data."""
        analysis = {
            'total_entries': len(entries),
            'result_types': defaultdict(int),
            'match_types': defaultdict(int),
            'timing_bugs': 0,
            'timing_failures': 0,
            'score_competition': defaultdict(int),
            'ornament_issues': defaultdict(int)
        }
        
        for entry in entries:
            # Result type distribution
            result_type = entry.result_type or "unprocessed"
            analysis['result_types'][result_type] += 1
            
            # Match type distribution
            if entry.hrule_match_type:
                analysis['match_types'][entry.hrule_match_type] += 1
            
            # Algorithm bugs
            if entry.bug_has_timing_bug:
                analysis['timing_bugs'] += 1
            
            # Timing failures
            if entry.timing_pass == "nil" or entry.hrule_timing_pass == "nil":
                analysis['timing_failures'] += 1
            
            # Score competition
            if entry.score_beats_top == "t":
                analysis['score_competition']['beats_top'] += 1
            elif entry.score_beats_top == "nil":
                analysis['score_competition']['below_top'] += 1
            
            # Ornament issues
            if entry.cevent_ornament_count > 0:
                analysis['ornament_issues']['has_ornaments'] += 1
                if entry.result_type == "no_match":
                    analysis['ornament_issues']['ornament_no_match'] += 1
        
        return analysis


def main():
    """Main entry point for log flattening."""
    parser = argparse.ArgumentParser(description="Flatten score following debug logs to CSV")
    parser.add_argument("log_file", help="Path to debug log file")
    parser.add_argument("--output", "-o", help="Output CSV file path (default: same as log file with .csv extension)")
    parser.add_argument("--analyze", "-a", action="store_true", help="Print pattern analysis")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    log_file = Path(args.log_file)
    if not log_file.exists():
        logger.error(f"Log file not found: {log_file}")
        return 1
    
    output_file = Path(args.output) if args.output else log_file.with_suffix('.csv')
    
    # Create flattener and process
    flattener = LogFlattener()
    entries = flattener.parse_log_file(log_file)
    
    if not entries:
        logger.error("No entries found in log file")
        return 1
    
    # Write CSV
    flattener.write_csv(entries, output_file)
    
    # Optional analysis
    if args.analyze:
        analysis = flattener.analyze_patterns(entries)
        print("\nPattern Analysis:")
        print("="*50)
        for category, data in analysis.items():
            print(f"{category}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {data}")
        print()
    
    print(f"Successfully flattened {len(entries)} log entries to {output_file}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())