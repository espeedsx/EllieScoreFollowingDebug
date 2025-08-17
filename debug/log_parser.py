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


class LogParser:
    """Parses debug logs into structured format."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.metrics = DebugMetrics()
        self.dp_decisions: List[DPDecision] = []
        self.matches: List[Match] = []
        self.no_matches: List[NoMatch] = []
        self.test_metadata: Optional[TestMetadata] = None
        
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
            'dp_decisions': [asdict(d) for d in self.dp_decisions],
            'matches': [asdict(m) for m in self.matches],
            'no_matches': [asdict(nm) for nm in self.no_matches],
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
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not self.dp_decisions:
            return {}
        
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
                'match_rate': len(match_decisions) / len(self.dp_decisions) if self.dp_decisions else 0
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
        
        # Return the last N decisions
        return before_failure[-context_size:] if before_failure else []
    
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


def parse_log_file(log_file: Path, save_analysis: bool = True) -> Dict[str, Any]:
    """
    Parse a log file and optionally save analysis.
    
    Args:
        log_file: Path to log file
        save_analysis: Whether to save parsed analysis to file
    
    Returns:
        Parsed log data
    """
    parser = LogParser(log_file)
    result = parser.parse()
    
    if save_analysis:
        # Generate analysis filename
        test_case = result['metadata']['test_info']['test_case'] if result['metadata']['test_info'] else 0
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