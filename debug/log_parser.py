#!/usr/bin/env python3
"""
Log parser for score following debug system.
Parses compact debug format into structured data.
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Tuple
from dataclasses import dataclass, asdict

from config import LOGS_DIR, ANALYSIS_DIR, get_analysis_filename
from utils import (
    setup_logging, parse_log_line, read_log_lines, save_json,
    DebugMetrics, get_timestamp, summarize_decision_sequence
)


logger = setup_logging(__name__)


@dataclass
class DPDecision:
    """Represents a single dynamic programming decision."""
    column: int
    row: int
    pitch: int
    time: float
    vertical_rule: float
    horizontal_rule: float
    final_value: float
    match_flag: bool
    used_pitches: List[int]
    unused_count: int
    line_number: int


@dataclass
class Match:
    """Represents a reported match."""
    row: int
    pitch: int
    time: float
    score: float
    line_number: int


@dataclass
class NoMatch:
    """Represents a failed match attempt."""
    pitch: int
    time: float
    line_number: int


@dataclass
class TestMetadata:
    """Test case metadata."""
    test_case: int
    score_file: str
    performance_file: str
    start_line: int
    end_line: Optional[int] = None


# Ultra-comprehensive logging data classes
@dataclass
class InputEvent:
    """Represents an input performance event."""
    column: int
    pitch: int
    time: float
    line_number: int


@dataclass
class MatrixState:
    """Represents the DP matrix state."""
    column: int
    window_start: int
    window_end: int
    window_center: int
    current_base: int
    prev_base: int
    current_upper: int
    prev_upper: int
    line_number: int


@dataclass
class CellState:
    """Represents individual cell state."""
    row: int
    value: float
    used_pitches: List[int]
    unused_count: int
    time: float
    line_number: int


@dataclass
class VerticalRule:
    """Represents a vertical rule calculation."""
    row: int
    up_value: float
    penalty: float
    result: float
    start_point: bool
    line_number: int


@dataclass
class HorizontalRule:
    """Represents a horizontal rule calculation."""
    row: int
    prev_value: float
    pitch: int
    ioi: float
    limit: float
    timing_pass: bool
    match_type: str
    result: float
    line_number: int


@dataclass
class TimingCheck:
    """Represents a timing constraint check."""
    prev_time: float
    curr_time: float
    ioi: float
    span: float
    limit: float
    timing_pass: bool
    constraint_type: str
    line_number: int


@dataclass
class MatchTypeAnalysis:
    """Represents match type classification."""
    pitch: int
    is_chord: bool
    is_trill: bool
    is_grace: bool
    is_extra: bool
    is_ignored: bool
    already_used: bool
    timing_ok: bool
    ornament_info: str
    line_number: int


@dataclass
class CellDecision:
    """Represents a final cell decision."""
    row: int
    vertical_result: float
    horizontal_result: float
    winner: str
    updated: bool
    final_value: float
    reason: str
    line_number: int


@dataclass
class ArrayNeighborhood:
    """Represents DP array neighborhood context."""
    row: int
    center_value: float
    neighbor_values: List[float]
    positions: List[int]
    line_number: int


@dataclass
class ScoreCompetition:
    """Represents score competition analysis."""
    row: int
    current_score: float
    top_score: float
    beats_top: bool
    margin: float
    confidence: float
    line_number: int


@dataclass
class OrnamentProcessing:
    """Represents ornament processing details."""
    pitch: int
    ornament_type: str
    trill_pitches: List[int]
    grace_pitches: List[int]
    ignore_pitches: List[int]
    credit: float
    line_number: int


@dataclass
class WindowMovement:
    """Represents dynamic window adjustment."""
    old_center: int
    new_center: int
    old_start: int
    new_start: int
    old_end: int
    new_end: int
    reason: str
    line_number: int


class LogParser:
    """Parses debug logs into structured format."""
    
    def __init__(self, log_file: Path, parse_comprehensive: bool = False):
        self.log_file = log_file
        self.metrics = DebugMetrics()
        self.dp_decisions: List[DPDecision] = []
        self.matches: List[Match] = []
        self.no_matches: List[NoMatch] = []
        self.test_metadata: Optional[TestMetadata] = None
        self.parse_comprehensive = parse_comprehensive
        self.target_lines: Optional[set] = None  # If set, only parse comprehensive data for these line numbers
        
        # Ultra-comprehensive logging data
        self.input_events: List[InputEvent] = []
        self.matrix_states: List[MatrixState] = []
        self.cell_states: List[CellState] = []
        self.vertical_rules: List[VerticalRule] = []
        self.horizontal_rules: List[HorizontalRule] = []
        self.timing_checks: List[TimingCheck] = []
        self.match_type_analyses: List[MatchTypeAnalysis] = []
        self.cell_decisions: List[CellDecision] = []
        self.array_neighborhoods: List[ArrayNeighborhood] = []
        self.score_competitions: List[ScoreCompetition] = []
        self.ornament_processings: List[OrnamentProcessing] = []
        self.window_movements: List[WindowMovement] = []
        
    def parse(self) -> Dict[str, Any]:
        """
        Parse the entire log file.
        
        Returns:
            Structured representation of the log
        """
        logger.info(f"Parsing log file: {self.log_file}")
        
        if not self.log_file.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file}")
        
        lines = read_log_lines(self.log_file)
        
        for line_num, line in enumerate(lines, 1):
            self.metrics.record_line()
            self._parse_line(line, line_num)
        
        # Create structured result
        result = {
            'metadata': {
                'log_file': str(self.log_file),
                'parsing_timestamp': get_timestamp(),
                'metrics': self.metrics.get_summary(),
                'test_info': asdict(self.test_metadata) if self.test_metadata else None
            },
            # Legacy format (for backward compatibility)
            'dp_decisions': [asdict(d) for d in self.dp_decisions],
            'matches': [asdict(m) for m in self.matches],
            'no_matches': [asdict(nm) for nm in self.no_matches],
            
            # Ultra-comprehensive logging data
            'comprehensive_data': {
                'input_events': [asdict(e) for e in self.input_events],
                'matrix_states': [asdict(s) for s in self.matrix_states],
                'cell_states': [asdict(s) for s in self.cell_states],
                'vertical_rules': [asdict(r) for r in self.vertical_rules],
                'horizontal_rules': [asdict(r) for r in self.horizontal_rules],
                'timing_checks': [asdict(t) for t in self.timing_checks],
                'match_type_analyses': [asdict(m) for m in self.match_type_analyses],
                'cell_decisions': [asdict(d) for d in self.cell_decisions],
                'array_neighborhoods': [asdict(a) for a in self.array_neighborhoods],
                'score_competitions': [asdict(s) for s in self.score_competitions],
                'ornament_processings': [asdict(o) for o in self.ornament_processings],
                'window_movements': [asdict(w) for w in self.window_movements]
            },
            'summary': self._generate_summary()
        }
        
        logger.info(f"Parsed {len(self.dp_decisions)} DP decisions, "
                   f"{len(self.matches)} matches, {len(self.no_matches)} no-matches")
        
        return result
    
    def _parse_line(self, line: str, line_num: int):
        """Parse a single log line."""
        parsed = parse_log_line(line)
        
        if not parsed:
            return
        
        if parsed['type'] == 'dp_entry':
            self.metrics.record_dp_entry()
            decision = DPDecision(
                column=parsed['column'],
                row=parsed['row'],
                pitch=parsed['pitch'],
                time=parsed['time'],
                vertical_rule=parsed['vertical_rule'],
                horizontal_rule=parsed['horizontal_rule'],
                final_value=parsed['final_value'],
                match_flag=parsed['match_flag'],
                used_pitches=parsed['used_pitches'],
                unused_count=parsed['unused_count'],
                line_number=line_num
            )
            self.dp_decisions.append(decision)
            
        elif parsed['type'] == 'match_found':
            self.metrics.record_match()
            match = Match(
                row=parsed['row'],
                pitch=parsed['pitch'],
                time=parsed['time'],
                score=parsed['score'],
                line_number=line_num
            )
            self.matches.append(match)
            
        elif parsed['type'] == 'no_match':
            self.metrics.record_failure()
            no_match = NoMatch(
                pitch=parsed['pitch'],
                time=parsed['time'],
                line_number=line_num
            )
            self.no_matches.append(no_match)
            
        elif parsed['type'] == 'test_start':
            self.test_metadata = TestMetadata(
                test_case=parsed['test_case'],
                score_file=parsed['score_file'],
                performance_file=parsed['performance_file'],
                start_line=line_num
            )
            
        elif parsed['type'] == 'test_end':
            if self.test_metadata:
                self.test_metadata.end_line = line_num
                
        # Ultra-comprehensive logging entries (skip if disabled for performance or not in target lines)
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'input_event':
            input_event = InputEvent(
                column=parsed['column'],
                pitch=parsed['pitch'],
                time=parsed['time'],
                line_number=line_num
            )
            self.input_events.append(input_event)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'matrix_state':
            matrix_state = MatrixState(
                column=parsed['column'],
                window_start=parsed['window_start'],
                window_end=parsed['window_end'],
                window_center=parsed['window_center'],
                current_base=parsed['current_base'],
                prev_base=parsed['prev_base'],
                current_upper=parsed['current_upper'],
                prev_upper=parsed['prev_upper'],
                line_number=line_num
            )
            self.matrix_states.append(matrix_state)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'cell_state':
            cell_state = CellState(
                row=parsed['row'],
                value=parsed['value'],
                used_pitches=parsed['used_pitches'],
                unused_count=parsed['unused_count'],
                time=parsed['time'],
                line_number=line_num
            )
            self.cell_states.append(cell_state)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'vertical_rule':
            vertical_rule = VerticalRule(
                row=parsed['row'],
                up_value=parsed['up_value'],
                penalty=parsed['penalty'],
                result=parsed['result'],
                start_point=parsed['start_point'],
                line_number=line_num
            )
            self.vertical_rules.append(vertical_rule)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'horizontal_rule':
            horizontal_rule = HorizontalRule(
                row=parsed['row'],
                prev_value=parsed['prev_value'],
                pitch=parsed['pitch'],
                ioi=parsed['ioi'],
                limit=parsed['limit'],
                timing_pass=parsed['timing_pass'],
                match_type=parsed['match_type'],
                result=parsed['result'],
                line_number=line_num
            )
            self.horizontal_rules.append(horizontal_rule)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'timing_check':
            timing_check = TimingCheck(
                prev_time=parsed['prev_time'],
                curr_time=parsed['curr_time'],
                ioi=parsed['ioi'],
                span=parsed['span'],
                limit=parsed['limit'],
                timing_pass=parsed['timing_pass'],
                constraint_type=parsed['constraint_type'],
                line_number=line_num
            )
            self.timing_checks.append(timing_check)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'match_type':
            match_type_analysis = MatchTypeAnalysis(
                pitch=parsed['pitch'],
                is_chord=parsed['is_chord'],
                is_trill=parsed['is_trill'],
                is_grace=parsed['is_grace'],
                is_extra=parsed['is_extra'],
                is_ignored=parsed['is_ignored'],
                already_used=parsed['already_used'],
                timing_ok=parsed['timing_ok'],
                ornament_info=parsed['ornament_info'],
                line_number=line_num
            )
            self.match_type_analyses.append(match_type_analysis)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'cell_decision':
            cell_decision = CellDecision(
                row=parsed['row'],
                vertical_result=parsed['vertical_result'],
                horizontal_result=parsed['horizontal_result'],
                winner=parsed['winner'],
                updated=parsed['updated'],
                final_value=parsed['final_value'],
                reason=parsed['reason'],
                line_number=line_num
            )
            self.cell_decisions.append(cell_decision)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'array_neighborhood':
            array_neighborhood = ArrayNeighborhood(
                row=parsed['row'],
                center_value=parsed['center_value'],
                neighbor_values=parsed['neighbor_values'],
                positions=parsed['positions'],
                line_number=line_num
            )
            self.array_neighborhoods.append(array_neighborhood)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'score_competition':
            score_competition = ScoreCompetition(
                row=parsed['row'],
                current_score=parsed['current_score'],
                top_score=parsed['top_score'],
                beats_top=parsed['beats_top'],
                margin=parsed['margin'],
                confidence=parsed['confidence'],
                line_number=line_num
            )
            self.score_competitions.append(score_competition)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'ornament_processing':
            ornament_processing = OrnamentProcessing(
                pitch=parsed['pitch'],
                ornament_type=parsed['ornament_type'],
                trill_pitches=parsed['trill_pitches'],
                grace_pitches=parsed['grace_pitches'],
                ignore_pitches=parsed['ignore_pitches'],
                credit=parsed['credit'],
                line_number=line_num
            )
            self.ornament_processings.append(ornament_processing)
            
        elif self.parse_comprehensive and (self.target_lines is None or line_num in self.target_lines) and parsed['type'] == 'window_movement':
            window_movement = WindowMovement(
                old_center=parsed['old_center'],
                new_center=parsed['new_center'],
                old_start=parsed['old_start'],
                new_start=parsed['new_start'],
                old_end=parsed['old_end'],
                new_end=parsed['new_end'],
                reason=parsed['reason'],
                line_number=line_num
            )
            self.window_movements.append(window_movement)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not self.dp_decisions:
            raise RuntimeError("Cannot generate summary - no DP decisions found (parsing may have failed)")
        
        # Time range
        times = [d.time for d in self.dp_decisions]
        time_range = {
            'start': min(times),
            'end': max(times),
            'duration': max(times) - min(times)
        }
        
        # Pitch range
        pitches = [d.pitch for d in self.dp_decisions]
        pitch_range = {
            'min': min(pitches),
            'max': max(pitches),
            'unique_count': len(set(pitches))
        }
        
        # Score progression
        scores = [d.final_value for d in self.dp_decisions]
        score_stats = {
            'min': min(scores),
            'max': max(scores),
            'progression': scores[:10] + ['...'] if len(scores) > 10 else scores
        }
        
        # Matrix coverage
        columns = set(d.column for d in self.dp_decisions)
        rows = set(d.row for d in self.dp_decisions)
        
        # Match statistics
        match_decisions = [d for d in self.dp_decisions if d.match_flag]
        
        return {
            'total_decisions': len(self.dp_decisions),
            'time_range': time_range,
            'pitch_range': pitch_range,
            'score_stats': score_stats,
            'matrix_coverage': {
                'columns': sorted(columns),
                'rows': sorted(rows),
                'total_cells': len(columns) * len(rows)
            },
            'match_statistics': {
                'decisions_with_matches': len(match_decisions),
                'reported_matches': len(self.matches),
                'no_matches': len(self.no_matches),
                'match_rate': len(match_decisions) / len(self.dp_decisions)  # self.dp_decisions validated above
            }
        }
    
    def get_decisions_around_time(self, target_time: float, window: float = 1.0) -> List[DPDecision]:
        """Get decisions within a time window around target time."""
        return [
            d for d in self.dp_decisions
            if abs(d.time - target_time) <= window
        ]
    
    def get_decisions_around_failure(self, failure_time: float, context_size: int = 5) -> List[DPDecision]:
        """Get decisions before a failure for context analysis."""
        # Find decisions before the failure time
        before_failure = [
            d for d in self.dp_decisions
            if d.time <= failure_time
        ]
        
        if not before_failure:
            raise RuntimeError(f"No decisions found before failure time {failure_time:.3f}s - insufficient context for analysis")
        
        # Return the last N decisions
        return before_failure[-context_size:]
    
    def find_decision_sequences(self) -> List[List[DPDecision]]:
        """Group decisions into sequences by performance note (column)."""
        sequences = {}
        
        for decision in self.dp_decisions:
            col = decision.column
            if col not in sequences:
                sequences[col] = []
            sequences[col].append(decision)
        
        # Sort each sequence by row
        for col in sequences:
            sequences[col].sort(key=lambda d: d.row)
        
        return list(sequences.values())


def parse_log_file(log_file: Path, save_analysis: bool = True, parse_comprehensive: bool = False, failure_context_lines: Optional[int] = None) -> Dict[str, Any]:
    """
    Parse a log file and optionally save analysis.
    
    Args:
        log_file: Path to log file
        save_analysis: Whether to save parsed analysis to file
        parse_comprehensive: Whether to parse comprehensive log entries (slower but more detailed)
        failure_context_lines: If set, only parse comprehensive data around failure lines (±N lines)
    
    Returns:
        Parsed log data
    """
    if failure_context_lines is not None:
        # Two-pass parsing: first pass finds failures, second pass parses comprehensive data around them
        logger.info(f"Using targeted parsing with ±{failure_context_lines} line context around failures")
        parser = LogParser(log_file, parse_comprehensive=False)
        result = parser.parse()
        
        logger.info(f"First pass found {len(result['no_matches'])} no-match failures")
        
        # Find failure line numbers
        failure_lines = set()
        for no_match_dict in result['no_matches']:
            if isinstance(no_match_dict, dict):
                if 'line_number' not in no_match_dict:
                    raise RuntimeError(f"No-match entry missing required line_number field: {no_match_dict}")
                line_num = no_match_dict['line_number']
            else:
                if not hasattr(no_match_dict, 'line_number'):
                    raise RuntimeError(f"No-match object missing required line_number attribute: {no_match_dict}")
                line_num = no_match_dict.line_number
            # Add context window around failure
            for offset in range(-failure_context_lines, failure_context_lines + 1):
                failure_lines.add(line_num + offset)
        
        # Second pass: parse comprehensive data only around failure lines
        if not failure_lines:
            raise RuntimeError("No failure lines found - cannot perform targeted parsing without failures")
            
        logger.info(f"Second pass: parsing comprehensive data around {len(failure_lines)} target lines")
        parser_comprehensive = LogParser(log_file, parse_comprehensive=True)
        parser_comprehensive.target_lines = failure_lines  # Only parse these lines comprehensively
        comprehensive_result = parser_comprehensive.parse()
        
        # Validate comprehensive data was extracted
        total_entries = sum(len(v) for v in comprehensive_result['comprehensive_data'].values())
        if total_entries == 0:
            raise RuntimeError("Second pass extracted no comprehensive data - target lines may be incorrect")
        
        # Merge comprehensive data into result
        result['comprehensive_data'] = comprehensive_result['comprehensive_data']
        logger.info(f"Merged comprehensive data with {total_entries} total entries")
        
    else:
        # Normal parsing
        parser = LogParser(log_file, parse_comprehensive=parse_comprehensive)
        result = parser.parse()
    
    if save_analysis:
        # Generate analysis filename
        if not result['metadata']['test_info']:
            raise RuntimeError("Metadata missing test_info - cannot determine test case for analysis filename")
        if 'test_case' not in result['metadata']['test_info']:
            raise RuntimeError("Test info missing test_case field - cannot determine test case for analysis filename")
        test_case = result['metadata']['test_info']['test_case']
        analysis_file = ANALYSIS_DIR / get_analysis_filename(test_case)
        
        # Save analysis
        save_json(result, analysis_file)
        logger.info(f"Analysis saved to: {analysis_file}")
        result['metadata']['analysis_file'] = str(analysis_file)
    
    return result


def main():
    """Main entry point for log parsing."""
    parser = argparse.ArgumentParser(description="Parse score following debug logs")
    parser.add_argument("log_file", type=Path, help="Log file to parse")
    parser.add_argument("--no-save", action="store_true", help="Don't save analysis file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        result = parse_log_file(args.log_file, save_analysis=not args.no_save)
        
        # Print summary
        metadata = result['metadata']
        summary = result['summary']
        
        print(f"\nLog Parsing Summary:")
        print(f"Log File: {metadata['log_file']}")
        print(f"Lines Processed: {metadata['metrics']['lines_processed']}")
        print(f"DP Decisions: {metadata['metrics']['dp_entries']}")
        print(f"Matches Found: {metadata['metrics']['matches_found']}")
        print(f"Failures: {metadata['metrics']['failures_detected']}")
        
        if summary:
            print(f"Time Range: {summary['time_range']['start']:.3f} - {summary['time_range']['end']:.3f}s")
            print(f"Match Rate: {summary['match_statistics']['match_rate']:.2%}")
        
        if 'analysis_file' in metadata:
            print(f"Analysis File: {metadata['analysis_file']}")
            
    except Exception as e:
        logger.error(f"Error parsing log: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())