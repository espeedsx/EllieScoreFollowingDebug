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
import logging
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
    """Complete flattened representation of a DP decision with all context.
    
    Fields are ordered to prioritize immediate outcome visibility for debugging:
    
    SECTION 1: INPUT CONTEXT & OUTCOME (Columns 1-5) - What triggered this and what happened?
    SECTION 2: ALGORITHM STATE (Columns 6-8) - Current DP state and target  
    SECTION 3: DP COMPUTATION (Columns 9-12) - Core algorithm execution
    SECTION 4: MUSICAL ANALYSIS (Columns 13-15) - Musical context evaluation
    SECTION 5: ALGORITHM RESULT (Columns 16-17) - Final DP computation
    SECTION 6: DEBUGGING CONTEXT (Columns 18-19) - Analysis and diagnostics
    """
    
    # SECTION 1: INPUT CONTEXT & OUTCOME - What performance note triggered this and what was the result?
    
    # 1. INPUT GROUP - Performance note that triggered DP analysis
    input_column: int = 0
    input_pitch: int = 0
    input_perf_time: float = 0.0
    
    # 2. MATCH GROUP - Match details (populated only if successful) - MOVED UP FOR VISIBILITY
    match_row: int = 0
    match_pitch: int = 0
    match_perf_time: float = 0.0
    match_score: float = 0.0
    
    # 3. NO_MATCH GROUP - No-match details (populated only if failed) - MOVED UP FOR VISIBILITY  
    no_match_pitch: int = 0
    no_match_perf_time: float = 0.0
    
    # 4. RESULT GROUP - Final classification of this INPUT block - MOVED UP FOR VISIBILITY
    result_type: str = ""  # "match", "no_match", "unprocessed"
    
    # 5. EXPLANATION GROUP - Human-readable decision explanations - NEW SECTION
    match_explanation: str = ""        # Clear explanation of why this was a match
    no_match_explanation: str = ""     # Clear explanation of why this was not a match
    decision_explanation: str = ""     # Detailed reasoning with supporting numbers
    timing_explanation: str = ""       # Timing constraint explanation
    ornament_explanation: str = ""     # Ornament processing explanation
    
    # SECTION 2: ALGORITHM STATE - Current DP state and target
    
    # 6. MATRIX GROUP - Algorithm state: where is the search window?
    matrix_window_start: int = 0
    matrix_window_end: int = 0
    matrix_window_center: int = 0
    matrix_current_base: int = 0
    matrix_prev_base: int = 0
    matrix_current_upper: int = 0
    matrix_prev_upper: int = 0
    
    # 7. CEVENT GROUP - Target score event being evaluated
    cevent_row: int = 0
    cevent_score_time: float = 0.0
    cevent_pitch_count: int = 0
    cevent_time_span: float = 0.0
    cevent_ornament_count: int = 0
    cevent_expected: int = 0
    cevent_pitches_str: str = ""       # NEW: String representation of pitches array
    
    # 8. CELL GROUP - Previous DP cell state (starting point)
    cell_time: float = -1.0
    cell_value: float = 0.0
    cell_used_pitches: str = ""
    cell_unused_count: int = 0
    cell_score_time: float = 0.0
    
    # SECTION 3: DP COMPUTATION - Core algorithm execution in order
    
    # 9. VRULE GROUP - Vertical rule: cost of skipping score event (applied first)
    vrule_up_value: float = 0.0
    vrule_penalty: float = 0.0
    vrule_result: float = 0.0
    vrule_start_point: str = ""
    
    # 10. TIMING GROUP - Timing constraint validation (critical for horizontal rule)
    timing_prev_cell_time: float = -1.0
    timing_curr_perf_time: float = 0.0
    timing_ioi: float = 0.0
    timing_span: float = 0.0
    timing_limit: float = 0.0
    timing_pass: str = ""
    timing_constraint_type: str = ""
    
    # 11. HRULE GROUP - Horizontal rule: performance note matching logic
    hrule_prev_value: float = 0.0
    hrule_ioi: float = 0.0
    hrule_limit: float = 0.0
    hrule_timing_pass: str = ""
    hrule_match_type: str = ""
    hrule_result: float = 0.0
    
    # 12. DECISION GROUP - Final DP cell decision (vrule vs hrule winner)
    decision_vertical_result: float = 0.0
    decision_horizontal_result: float = 0.0
    decision_winner: str = ""
    decision_updated: str = ""
    decision_final_value: float = 0.0
    decision_reason: str = ""
    
    # SECTION 4: MUSICAL ANALYSIS - Musical context and ornament processing
    
    # 13. MATCHTYPE GROUP - Musical context classification (what type of match?)
    matchtype_is_chord: str = ""
    matchtype_is_trill: str = ""
    matchtype_is_grace: str = ""
    matchtype_is_extra: str = ""
    matchtype_is_ignored: str = ""
    matchtype_already_used: str = ""
    matchtype_timing_ok: str = ""
    matchtype_ornament_info: str = ""
    
    # 14. ORNAMENT GROUP - Ornament-specific processing details
    ornament_type: str = ""
    ornament_trill_pitches: str = ""
    ornament_grace_pitches: str = ""
    ornament_ignore_pitches: str = ""
    ornament_credit_applied: float = 0.0
    
    # 15. ORNAMENT_ARRAYS GROUP - String representations of ornament data - NEW
    ornament_trill_pitches_str: str = ""     # Comma-separated trill pitches
    ornament_grace_pitches_str: str = ""     # Comma-separated grace pitches  
    ornament_ignore_pitches_str: str = ""    # Comma-separated ignore pitches
    
    # SECTION 5: ALGORITHM RESULT - Final DP computation and outcomes
    
    # 16. DP GROUP - Summary of DP computation for this cell
    dp_row: int = 0
    dp_vertical_rule: float = 0.0
    dp_horizontal_rule: float = 0.0
    dp_final_value: float = 0.0
    dp_match: int = 0
    dp_used_pitches: str = ""
    dp_unused_count: int = 0
    
    # 17. SCORE GROUP - How does this cell compete globally?
    score_current_score: float = 0.0
    score_top_score: float = 0.0
    score_beats_top: str = ""
    score_margin: float = 0.0
    score_confidence: float = 0.0
    
    # SECTION 6: DEBUGGING CONTEXT - Analysis and diagnostics
    
    # 18. ARRAY GROUP - DP matrix neighborhood for validation
    array_center_value: float = 0.0
    array_neighbor_values: str = ""
    array_neighbor_positions: str = ""
    
    # 19. BUG GROUP - Algorithm bug detection and systematic issues
    bug_has_timing_bug: bool = False
    bug_description: str = ""


class LogFlattener:
    """Flattens multi-line log entries into single CSV rows for analysis."""
    
    def __init__(self):
        self.patterns = {name: re.compile(pattern) for name, pattern in LOG_PATTERNS.items()}
        self.current_input_logs = []  # All logs for current input
        self.completed_entries = []
        self.stats = defaultdict(int)
        
    def parse_log_file(self, log_file_path: Path) -> List[FlattenedLogEntry]:
        """Parse a log file and return flattened entries."""
        logger.info(f"Parsing log file: {log_file_path}")
        
        self.current_input_logs = []
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
                        entries_so_far = len(self.completed_entries)
                        pbar.set_description(f"Parsing log ({entries_so_far} entries)")
        
        # Process any remaining input
        if self.current_input_logs:
            self._process_input_logs()
        
        logger.info(f"Processed {len(self.completed_entries)} complete entries")
        self._log_stats()
        
        return self.completed_entries
    
    def _process_line(self, line: str, line_num: int):
        """Process a single log line by collecting it for later processing."""
        self.stats['total_lines'] += 1
        
        # Check if this is an INPUT line (starts new input block)
        if line.startswith('INPUT|'):
            # Process any previous input block
            if self.current_input_logs:
                self._process_input_logs()
            # Start new input block
            self.current_input_logs = [line]
            return
        
        # Check if this is a MATCH/NO_MATCH (ends current input block)
        if line.startswith('MATCH|') or line.startswith('NO_MATCH|'):
            # Add to current block and process it
            self.current_input_logs.append(line)
            self._process_input_logs()
            return
        
        # Add to current input block if we have one
        if self.current_input_logs:
            self.current_input_logs.append(line)
        
        # Track unmatched lines for stats
        matched = False
        for log_type, pattern in self.patterns.items():
            if pattern.match(line):
                self.stats[f'{log_type}_lines'] += 1
                matched = True
                break
        
        if not matched and not line.startswith(('MATCH|', 'NO_MATCH|', 'INPUT|')):
            self.stats['unmatched_lines'] += 1
    

    def _process_input_logs(self):
        """Process all logs for one complete input to create flattened entries."""
        if not self.current_input_logs:
            return
            
        logger.debug(f"Processing input block with {len(self.current_input_logs)} log lines")
        
        # Parse all logs into structured data
        input_data = {}
        dp_entries = {}
        result_data = {}
        
        for line in self.current_input_logs:
            log_entry = self._parse_single_line(line)
            if not log_entry:
                continue
                
            log_type, data = log_entry
            
            if log_type == 'input_event':
                input_data = data
            elif log_type == 'dp_entry':
                row = data['dp_row']
                if row not in dp_entries:
                    dp_entries[row] = {}
                dp_entries[row]['dp'] = data
            elif log_type in ['cevent_summary', 'cell_state', 'vertical_rule', 'horizontal_rule', 
                              'timing_check', 'match_type', 'cell_decision', 'score_competition',
                              'ornament_processing', 'matrix_state', 'array_neighborhood',
                              'match_explanation', 'no_match_explanation', 'decision_explanation', 
                              'timing_explanation', 'ornament_explanation']:
                # Store by row if it has row info, otherwise apply to all
                if 'row' in data:
                    row = data['row']
                    if row not in dp_entries:
                        dp_entries[row] = {}
                    dp_entries[row][log_type] = data
                else:
                    # Matrix state applies to all entries
                    input_data[log_type] = data
            elif log_type in ['match_found', 'no_match']:
                result_data = {'type': log_type, 'data': data}
        
        # Create flattened entries
        for row, row_data in dp_entries.items():
            if 'dp' not in row_data:
                continue  # Skip if no DP entry for this row
                
            entry = FlattenedLogEntry()
            
            # Apply input data
            for key, value in input_data.items():
                if isinstance(value, dict):
                    # Matrix state or similar - apply all fields
                    for field, field_value in value.items():
                        if hasattr(entry, field):
                            setattr(entry, field, field_value)
                else:
                    if hasattr(entry, key):
                        setattr(entry, key, value)
            
            # Apply DP data
            for key, value in row_data['dp'].items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
            
            # Apply other row-specific data
            for log_type, data in row_data.items():
                if log_type != 'dp':
                    for key, value in data.items():
                        if hasattr(entry, key):
                            setattr(entry, key, value)
            
            # Apply result data
            if result_data:
                if result_data['type'] == 'match_found':
                    entry.result_type = 'match'
                    for key, value in result_data['data'].items():
                        if hasattr(entry, key):
                            setattr(entry, key, value)
                elif result_data['type'] == 'no_match':
                    entry.result_type = 'no_match'
                    for key, value in result_data['data'].items():
                        if hasattr(entry, key):
                            setattr(entry, key, value)
            
            self.completed_entries.append(entry)
        
        # Clear for next input
        self.current_input_logs = []

    def _parse_single_line(self, line: str):
        """Parse a single line and return (log_type, data) or None."""
        
        # Handle special cases first
        if line.startswith('MATCH|'):
            match = self.patterns['match_found'].match(line)
            if match:
                row, pitch, perf_time, score = match.groups()
                return ('match_found', {
                    'match_row': int(row),
                    'match_pitch': int(pitch), 
                    'match_perf_time': float(perf_time),
                    'match_score': float(score)
                })
        
        if line.startswith('NO_MATCH|'):
            match = self.patterns['no_match'].match(line)
            if match:
                pitch, perf_time = match.groups()
                return ('no_match', {
                    'no_match_pitch': int(pitch),
                    'no_match_perf_time': float(perf_time)
                })
        
        # Try all patterns
        for log_type, pattern in self.patterns.items():
            match = pattern.match(line)
            if match:
                return (log_type, self._extract_data(log_type, match))
        
        return None
    
    def _extract_data(self, log_type: str, match):
        """Extract data from a matched pattern into a dictionary."""
        groups = match.groups()
        
        if log_type == 'input_event':
            column, pitch, perf_time = groups
            return {
                'input_column': int(column),
                'input_pitch': int(pitch),
                'input_perf_time': float(perf_time)
            }
        
        elif log_type == 'dp_entry':
            column, row, pitch, perf_time, vertical_rule, horizontal_rule, final_value, match_flag, used_pitches, unused_count = groups
            return {
                'dp_row': int(row),
                'dp_vertical_rule': float(vertical_rule),
                'dp_horizontal_rule': float(horizontal_rule),
                'dp_final_value': float(final_value),
                'dp_match': int(match_flag),
                'dp_used_pitches': used_pitches,
                'dp_unused_count': int(unused_count)
            }
        
        elif log_type == 'cevent_summary':
            row, score_time, pitch_count, time_span, ornament_count, expected, pitches_str = groups
            return {
                'row': int(row),
                'cevent_row': int(row),
                'cevent_score_time': float(score_time),
                'cevent_pitch_count': int(pitch_count),
                'cevent_time_span': float(time_span),
                'cevent_ornament_count': int(ornament_count),
                'cevent_expected': int(expected),
                'cevent_pitches_str': pitches_str
            }
        
        elif log_type == 'cell_state':
            row, value, used_pitches, unused_count, cell_time, score_time = groups
            return {
                'row': int(row),
                'cell_time': float(cell_time),
                'cell_value': float(value),
                'cell_used_pitches': used_pitches,
                'cell_unused_count': int(unused_count),
                'cell_score_time': float(score_time)
            }
        
        elif log_type == 'vertical_rule':
            row, up_value, penalty, result, start_point = groups
            return {
                'row': int(row),
                'vrule_up_value': float(up_value),
                'vrule_penalty': float(penalty),
                'vrule_result': float(result),
                'vrule_start_point': start_point
            }
        
        elif log_type == 'horizontal_rule':
            row, prev_value, pitch, ioi, limit, timing_pass, match_type, result = groups
            return {
                'row': int(row),
                'hrule_prev_value': float(prev_value),
                'hrule_ioi': float(ioi),
                'hrule_limit': float(limit),
                'hrule_timing_pass': timing_pass,
                'hrule_match_type': match_type,
                'hrule_result': float(result)
            }
        
        elif log_type == 'timing_check':
            prev_cell_time, curr_perf_time, ioi, span, limit, timing_pass, constraint_type = groups
            return {
                'timing_prev_cell_time': float(prev_cell_time),
                'timing_curr_perf_time': float(curr_perf_time),
                'timing_ioi': float(ioi),
                'timing_span': float(span),
                'timing_limit': float(limit),
                'timing_pass': timing_pass,
                'timing_constraint_type': constraint_type,
                'bug_has_timing_bug': float(prev_cell_time) == -1.0 and float(ioi) > 20.0,
                'bug_description': f"Cell time initialization bug: prev_time=-1, ioi={ioi}" if float(prev_cell_time) == -1.0 and float(ioi) > 20.0 else ""
            }
        
        elif log_type == 'match_type':
            pitch, is_chord, is_trill, is_grace, is_extra, is_ignored, already_used, timing_ok, ornament_info = groups
            return {
                'matchtype_is_chord': is_chord,
                'matchtype_is_trill': is_trill,
                'matchtype_is_grace': is_grace,
                'matchtype_is_extra': is_extra,
                'matchtype_is_ignored': is_ignored,
                'matchtype_already_used': already_used,
                'matchtype_timing_ok': timing_ok,
                'matchtype_ornament_info': ornament_info
            }
        
        elif log_type == 'cell_decision':
            row, vertical_result, horizontal_result, winner, updated, final_value, reason = groups
            return {
                'row': int(row),
                'decision_vertical_result': float(vertical_result),
                'decision_horizontal_result': float(horizontal_result),
                'decision_winner': winner,
                'decision_updated': updated,
                'decision_final_value': float(final_value),
                'decision_reason': reason
            }
        
        elif log_type == 'score_competition':
            row, current_score, top_score, beats_top, margin, confidence = groups
            return {
                'row': int(row),
                'score_current_score': float(current_score),
                'score_top_score': float(top_score),
                'score_beats_top': beats_top,
                'score_margin': float(margin),
                'score_confidence': float(confidence)
            }
        
        elif log_type == 'ornament_processing':
            pitch, ornament_type, trill_pitches, grace_pitches, ignore_pitches, credit_applied, trill_str, grace_str, ignore_str = groups
            return {
                'ornament_type': ornament_type,
                'ornament_trill_pitches': trill_pitches,
                'ornament_grace_pitches': grace_pitches,
                'ornament_ignore_pitches': ignore_pitches,
                'ornament_credit_applied': float(credit_applied),
                'ornament_trill_pitches_str': trill_str,
                'ornament_grace_pitches_str': grace_str,
                'ornament_ignore_pitches_str': ignore_str
            }
        
        elif log_type == 'matrix_state':
            column, window_start, window_end, window_center, current_base, prev_base, current_upper, prev_upper = groups
            return {
                'matrix_window_start': int(window_start),
                'matrix_window_end': int(window_end),
                'matrix_window_center': int(window_center),
                'matrix_current_base': int(current_base),
                'matrix_prev_base': int(prev_base),
                'matrix_current_upper': int(current_upper),
                'matrix_prev_upper': int(prev_upper)
            }
        
        elif log_type == 'array_neighborhood':
            row, center_value, values, positions = groups
            return {
                'row': int(row),
                'array_center_value': float(center_value),
                'array_neighbor_values': values,
                'array_neighbor_positions': positions
            }
        
        elif log_type == 'match_explanation':
            pitch, reason, score, timing, context = groups
            return {
                'match_explanation': f"Pitch {pitch} matched: {reason} (score={score}, timing={timing}, context={context})"
            }
        
        elif log_type == 'no_match_explanation':
            pitch, reason, constraint, timing, expected = groups
            return {
                'no_match_explanation': f"Pitch {pitch} no match: {reason} (constraint={constraint}, timing={timing}, expected={expected})"
            }
        
        elif log_type == 'decision_explanation':
            row, pitch, reasoning, vertical_score, horizontal_score, winner, confidence = groups
            return {
                'decision_explanation': f"Row {row} pitch {pitch}: {reasoning} (vertical={vertical_score}, horizontal={horizontal_score}, winner={winner}, confidence={confidence})"
            }
        
        elif log_type == 'timing_explanation':
            pitch, ioi, limit, pass_status, reason, context = groups
            return {
                'timing_explanation': f"Pitch {pitch} timing: {reason} (IOI={ioi}, limit={limit}, pass={pass_status}, context={context})"
            }
        
        elif log_type == 'ornament_explanation':
            pitch, orn_type, processing, credit, pitches_context = groups
            return {
                'ornament_explanation': f"Pitch {pitch} ornament {orn_type}: {processing} (credit={credit}, context={pitches_context})"
            }
        
        # Default: return empty dict for unknown types
        return {}
    
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