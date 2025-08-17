#!/usr/bin/env python3
"""
Failure analyzer for score following debug system.
Detects mismatches and extracts context for AI analysis.
"""

import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from config import ANALYSIS_DIR, FAILURE_CONTEXT_WINDOW
from utils import setup_logging, load_json, save_json, get_timestamp, format_pitches
from log_parser import DPDecision, Match, NoMatch, parse_log_file


logger = setup_logging(__name__)


@dataclass
class FailureContext:
    """Context around a failure for analysis."""
    failure_type: str  # 'no_match', 'wrong_match', 'score_drop'
    failure_time: float
    failure_pitch: int
    expected_outcome: str
    actual_outcome: str
    context_decisions: List[Dict[str, Any]]
    preceding_matches: List[Dict[str, Any]]
    score_progression: List[float]
    timing_analysis: Dict[str, Any]
    line_number: int
    
    # Ultra-comprehensive algorithm context
    comprehensive_context: Optional[Dict[str, Any]] = None


@dataclass 
class FailureReport:
    """Complete failure analysis report."""
    test_case_id: int
    log_file: str
    analysis_timestamp: str
    total_failures: int
    failure_contexts: List[FailureContext]
    summary_statistics: Dict[str, Any]
    recommendations: List[str]


class FailureAnalyzer:
    """Analyzes parsed logs to identify and contextualize failures."""
    
    def __init__(self, parsed_data: Dict[str, Any]):
        self.data = parsed_data
        self.dp_decisions = [DPDecision(**d) for d in parsed_data['dp_decisions']]
        self.matches = [Match(**m) for m in parsed_data['matches']]
        self.no_matches = [NoMatch(**nm) for nm in parsed_data['no_matches']]
        self.metadata = parsed_data['metadata']
        
        # Ultra-comprehensive data (required for proper analysis)
        if 'comprehensive_data' not in parsed_data:
            raise ValueError("No comprehensive_data key in parsed_data - parsing with comprehensive=True required")
        self.comprehensive_data = parsed_data['comprehensive_data']
        if not self.comprehensive_data:
            raise ValueError("Comprehensive_data is empty - parsing with comprehensive=True required")
        
        # Validate comprehensive data has expected structure
        expected_keys = ['input_events', 'matrix_states', 'cell_states', 'vertical_rules', 
                        'horizontal_rules', 'timing_checks', 'match_type_analyses', 
                        'cell_decisions', 'array_neighborhoods', 'score_competitions', 
                        'ornament_processings', 'window_movements']
        missing_keys = set(expected_keys) - set(self.comprehensive_data.keys())
        if missing_keys:
            raise ValueError(f"Comprehensive data missing expected keys: {missing_keys}")
        
        self.has_comprehensive_data = True
    
    def analyze(self) -> FailureReport:
        """
        Perform complete failure analysis.
        
        Returns:
            Comprehensive failure report
        """
        logger.info("Starting failure analysis")
        
        failure_contexts = []
        
        # Analyze explicit no-matches
        for no_match in self.no_matches:
            context = self._analyze_no_match_failure(no_match)
            if context:
                failure_contexts.append(context)
        
        # Analyze potential wrong matches
        wrong_match_contexts = self._analyze_potential_wrong_matches()
        failure_contexts.extend(wrong_match_contexts)
        
        # Analyze score drops (potential missed opportunities)
        score_drop_contexts = self._analyze_score_drops()
        failure_contexts.extend(score_drop_contexts)
        
        # Generate summary statistics
        summary_stats = self._generate_summary_statistics(failure_contexts)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(failure_contexts)
        
        report = FailureReport(
            test_case_id=self._get_test_case_id(),
            log_file=self.metadata['log_file'],
            analysis_timestamp=get_timestamp(),
            total_failures=len(failure_contexts),
            failure_contexts=failure_contexts,
            summary_statistics=summary_stats,
            recommendations=recommendations
        )
        
        logger.info(f"Found {len(failure_contexts)} failure contexts")
        return report
    
    def _analyze_no_match_failure(self, no_match: NoMatch) -> Optional[FailureContext]:
        """Analyze a no-match failure."""
        # Get context decisions before the failure
        context_decisions = self._get_context_before_time(
            no_match.time, FAILURE_CONTEXT_WINDOW
        )
        
        if not context_decisions:
            return None
        
        # Get preceding matches for comparison
        preceding_matches = self._get_matches_before_time(no_match.time, count=3)
        
        # Analyze score progression
        score_progression = [d.final_value for d in context_decisions]
        
        # Timing analysis
        timing_analysis = self._analyze_timing_patterns(context_decisions, no_match.time)
        
        # Extract comprehensive algorithm context (required)
        comprehensive_context = self._extract_comprehensive_context(no_match.time, no_match.pitch)
        if not comprehensive_context:
            raise RuntimeError(f"Failed to extract comprehensive context for failure at {no_match.time:.3f}s, pitch {no_match.pitch}")
        
        return FailureContext(
            failure_type='no_match',
            failure_time=no_match.time,
            failure_pitch=no_match.pitch,
            expected_outcome=f"Match for pitch {no_match.pitch} at time {no_match.time:.3f}",
            actual_outcome="No match found",
            context_decisions=[asdict(d) for d in context_decisions],
            preceding_matches=[asdict(m) for m in preceding_matches],
            score_progression=score_progression,
            timing_analysis=timing_analysis,
            line_number=no_match.line_number,
            comprehensive_context=comprehensive_context
        )
    
    def _analyze_potential_wrong_matches(self) -> List[FailureContext]:
        """Analyze potentially incorrect matches."""
        contexts = []
        
        # Look for matches with suspiciously low scores
        for match in self.matches:
            if match.score < 0:  # Negative scores indicate poor matches
                context_decisions = self._get_context_before_time(
                    match.time, FAILURE_CONTEXT_WINDOW
                )
                
                if context_decisions:
                    timing_analysis = self._analyze_timing_patterns(context_decisions, match.time)
                    
                    context = FailureContext(
                        failure_type='wrong_match',
                        failure_time=match.time,
                        failure_pitch=match.pitch,
                        expected_outcome=f"Better match for pitch {match.pitch}",
                        actual_outcome=f"Poor match with score {match.score}",
                        context_decisions=[asdict(d) for d in context_decisions],
                        preceding_matches=[asdict(m) for m in self._get_matches_before_time(match.time, 3)],
                        score_progression=[d.final_value for d in context_decisions],
                        timing_analysis=timing_analysis,
                        line_number=match.line_number
                    )
                    contexts.append(context)
        
        return contexts
    
    def _analyze_score_drops(self) -> List[FailureContext]:
        """Analyze significant score drops that might indicate missed opportunities."""
        contexts = []
        
        # Group decisions by column (performance note)
        by_column = {}
        for decision in self.dp_decisions:
            if decision.column not in by_column:
                by_column[decision.column] = []
            by_column[decision.column].append(decision)
        
        # Look for significant score drops within each column
        for column, decisions in by_column.items():
            decisions.sort(key=lambda d: d.row)
            
            for i in range(1, len(decisions)):
                prev_score = decisions[i-1].final_value
                curr_score = decisions[i].final_value
                
                # Significant drop (more than 2 points)
                if prev_score - curr_score > 2:
                    context_decisions = decisions[max(0, i-FAILURE_CONTEXT_WINDOW):i+1]
                    
                    timing_analysis = self._analyze_timing_patterns(
                        context_decisions, decisions[i].time
                    )
                    
                    context = FailureContext(
                        failure_type='score_drop',
                        failure_time=decisions[i].time,
                        failure_pitch=decisions[i].pitch,
                        expected_outcome=f"Maintain score around {prev_score}",
                        actual_outcome=f"Score dropped to {curr_score}",
                        context_decisions=[asdict(d) for d in context_decisions],
                        preceding_matches=[asdict(m) for m in self._get_matches_before_time(decisions[i].time, 3)],
                        score_progression=[d.final_value for d in context_decisions],
                        timing_analysis=timing_analysis,
                        line_number=decisions[i].line_number
                    )
                    contexts.append(context)
        
        return contexts
    
    def _get_context_before_time(self, target_time: float, count: int) -> List[DPDecision]:
        """Get N decisions before the target time."""
        before_time = [d for d in self.dp_decisions if d.time <= target_time]
        before_time.sort(key=lambda d: (d.time, d.column, d.row))
        return before_time[-count:] if len(before_time) >= count else before_time
    
    def _get_matches_before_time(self, target_time: float, count: int) -> List[Match]:
        """Get N matches before the target time."""
        before_time = [m for m in self.matches if m.time < target_time]
        before_time.sort(key=lambda m: m.time)
        return before_time[-count:] if len(before_time) >= count else before_time
    
    def _analyze_timing_patterns(self, decisions: List[DPDecision], failure_time: float) -> Dict[str, Any]:
        """Analyze timing patterns around a failure."""
        if len(decisions) < 2:
            raise ValueError(f"Cannot analyze timing patterns with {len(decisions)} decisions - need at least 2 decisions for timing analysis")
        
        times = [d.time for d in decisions]
        inter_onset_intervals = [times[i] - times[i-1] for i in range(1, len(times))]
        
        # Look for timing irregularities
        if not inter_onset_intervals:
            raise ValueError("No inter-onset intervals calculated - cannot analyze timing patterns")
        if not times:
            raise ValueError("No decision times found - cannot analyze timing patterns")
        
        avg_ioi = sum(inter_onset_intervals) / len(inter_onset_intervals)
        
        timing_analysis = {
            'decision_count': len(decisions),
            'time_span': max(times) - min(times),
            'average_ioi': avg_ioi,
            'ioi_variance': sum((ioi - avg_ioi)**2 for ioi in inter_onset_intervals) / len(inter_onset_intervals),
            'max_gap': max(inter_onset_intervals),
            'min_gap': min(inter_onset_intervals),
            'time_to_failure': failure_time - max(times)
        }
        
        # Identify timing issues
        timing_issues = []
        if timing_analysis['max_gap'] > 1.0:  # Gap > 1 second
            timing_issues.append(f"Large timing gap: {timing_analysis['max_gap']:.3f}s")
        
        if timing_analysis['time_to_failure'] > 0.5:  # Failure > 0.5s after last decision
            timing_issues.append(f"Long delay before failure: {timing_analysis['time_to_failure']:.3f}s")
        
        timing_analysis['issues'] = timing_issues
        
        return timing_analysis
    
    def _generate_summary_statistics(self, failure_contexts: List[FailureContext]) -> Dict[str, Any]:
        """Generate summary statistics for all failures."""
        if not failure_contexts:
            raise ValueError("Cannot generate summary statistics - no failure contexts provided")
        
        failure_types = [fc.failure_type for fc in failure_contexts]
        failure_type_counts = {
            ft: failure_types.count(ft) for ft in set(failure_types)
        }
        
        # Timing statistics
        failure_times = [fc.failure_time for fc in failure_contexts]
        if not failure_times:
            raise ValueError("No failure times found in failure contexts - data corruption")
        
        # Score statistics
        all_scores = []
        for fc in failure_contexts:
            all_scores.extend(fc.score_progression)
        if not all_scores:
            raise ValueError("No scores found in failure contexts - score progression data missing")
        
        return {
            'failure_type_distribution': failure_type_counts,
            'temporal_distribution': {
                'first_failure': min(failure_times),
                'last_failure': max(failure_times),
                'failure_span': max(failure_times) - min(failure_times) if len(failure_times) > 1 else 0
            },
            'score_statistics': {
                'min_score': min(all_scores),
                'max_score': max(all_scores),
                'avg_score': sum(all_scores) / len(all_scores)
            },
            'context_statistics': {
                'avg_context_size': sum(len(fc.context_decisions) for fc in failure_contexts) / len(failure_contexts),
                'avg_score_progression_length': sum(len(fc.score_progression) for fc in failure_contexts) / len(failure_contexts)
            }
        }
    
    def _generate_recommendations(self, failure_contexts: List[FailureContext]) -> List[str]:
        """Generate recommendations based on failure analysis."""
        recommendations = []
        
        if not failure_contexts:
            recommendations.append("No failures detected - algorithm performed well")
            return recommendations
        
        # Analyze failure patterns
        failure_types = [fc.failure_type for fc in failure_contexts]
        
        if failure_types.count('no_match') > len(failure_types) * 0.5:
            recommendations.append("High rate of no-matches suggests timing constraints may be too strict")
        
        if failure_types.count('wrong_match') > 0:
            recommendations.append("Wrong matches detected - consider adjusting scoring parameters")
        
        if failure_types.count('score_drop') > 0:
            recommendations.append("Score drops suggest potential alignment issues - review dynamic programming weights")
        
        # Timing-based recommendations
        timing_issues = []
        for fc in failure_contexts:
            if 'issues' not in fc.timing_analysis:
                raise ValueError(f"Timing analysis for failure context missing issues field: {fc.timing_analysis}")
            timing_issues.extend(fc.timing_analysis['issues'])
        
        if any('Large timing gap' in issue for issue in timing_issues):
            recommendations.append("Large timing gaps detected - consider increasing tempo tolerance")
        
        if any('Long delay before failure' in issue for issue in timing_issues):
            recommendations.append("Long delays before failures - may need better windowing strategy")
        
        # Score-based recommendations
        low_scores = [fc for fc in failure_contexts if min(fc.score_progression) < -5]
        if len(low_scores) > len(failure_contexts) * 0.3:
            recommendations.append("Many low scores suggest algorithm parameters need tuning")
        
        return recommendations
    
    def _get_test_case_id(self) -> int:
        """Extract test case ID from metadata."""
        if 'test_info' not in self.metadata:
            raise ValueError("Metadata missing test_info - cannot extract test case ID")
        test_info = self.metadata['test_info']
        if not test_info:
            raise ValueError("Test info is empty - cannot extract test case ID")
        if 'test_case' not in test_info:
            raise ValueError("Test info missing test_case field - cannot extract test case ID")
        return test_info['test_case']
    
    def get_most_critical_failure(self, after_score_time: Optional[float] = None) -> FailureContext:
        """Get the most critical failure for focused AI analysis."""
        report = self.analyze()
        
        if not report.failure_contexts:
            raise ValueError("No failure contexts found - cannot identify critical failure without failures")
        
        # Filter by score time if specified
        candidate_failures = report.failure_contexts
        if after_score_time is not None:
            candidate_failures = [fc for fc in report.failure_contexts if fc.failure_time >= after_score_time]
            if not candidate_failures:
                raise ValueError(f"No failures found after score time {after_score_time:.3f}s - adjust score_time parameter")
            logger.info(f"Filtering to {len(candidate_failures)} failures after score time {after_score_time:.3f}s")
        
        # Focus primarily on no_match failures (unmatched notes)
        priority_order = ['no_match', 'wrong_match', 'score_drop']
        
        for failure_type in priority_order:
            failures_of_type = [fc for fc in candidate_failures if fc.failure_type == failure_type]
            if failures_of_type:
                # Return the first one (earliest in time)
                return min(failures_of_type, key=lambda fc: fc.failure_time)
        
        # If no failures match priority order, return first available failure
        if not candidate_failures:
            raise RuntimeError("Logic error: candidate_failures is empty after validation")
        return candidate_failures[0]
    
    def _extract_comprehensive_context(self, failure_time: float, failure_pitch: int) -> Dict[str, Any]:
        """Extract comprehensive algorithm context around a failure."""
        context = {}
        
        # Debug: Check if we have comprehensive data
        logger.debug(f"Extracting comprehensive context for failure at {failure_time:.3f}s, pitch {failure_pitch}")
        logger.debug(f"Available comprehensive data keys: {list(self.comprehensive_data.keys())}")
        for key, data in self.comprehensive_data.items():
            logger.debug(f"  {key}: {len(data)} entries")
        
        # Time window for context (±1 second around failure)
        time_window = 1.0
        start_time = failure_time - time_window
        end_time = failure_time + time_window
        
        # Extract timing constraints that might have failed (timing checks don't have pitch, filter by time only)
        if 'timing_checks' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing timing_checks - parsing may have failed")
        timing_checks = self.comprehensive_data['timing_checks']
        relevant_timing = []
        for t in timing_checks:
            if 'curr_time' not in t:
                raise RuntimeError(f"Timing check missing curr_time field: {t}")
            if start_time <= t['curr_time'] <= end_time:
                relevant_timing.append(t)
        
        # Extract match type analyses for this pitch
        if 'match_type_analyses' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing match_type_analyses - parsing may have failed")
        match_analyses = self.comprehensive_data['match_type_analyses']
        relevant_match_types = []
        for m in match_analyses:
            if 'pitch' not in m:
                raise RuntimeError(f"Match type analysis missing pitch field: {m}")
            if 'line_number' not in m:
                raise RuntimeError(f"Match type analysis missing line_number field: {m}")
            if (m['pitch'] == failure_pitch and
                abs(failure_time - self._find_closest_time_for_pitch(m['line_number'])) <= time_window):
                relevant_match_types.append(m)
        
        # Extract horizontal rule calculations (use 'pitch' field from HRULE entries)
        if 'horizontal_rules' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing horizontal_rules - parsing may have failed")
        horizontal_rules = self.comprehensive_data['horizontal_rules']
        relevant_h_rules = []
        for h in horizontal_rules:
            if 'pitch' not in h:
                raise RuntimeError(f"Horizontal rule missing pitch field: {h}")
            if h['pitch'] == failure_pitch:
                relevant_h_rules.append(h)
        
        # Extract cell decisions around this time
        if 'cell_decisions' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing cell_decisions - parsing may have failed")
        cell_decisions = self.comprehensive_data['cell_decisions']
        relevant_decisions = []
        for d in cell_decisions:
            if 'line_number' not in d:
                raise RuntimeError(f"Cell decision missing line_number field: {d}")
            if abs(failure_time - self._find_closest_time_for_decision(d['line_number'])) <= time_window:
                relevant_decisions.append(d)
        
        # Extract score competition data
        if 'score_competitions' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing score_competitions - parsing may have failed")
        score_competitions = self.comprehensive_data['score_competitions']
        relevant_scores = []
        for s in score_competitions:
            if 'line_number' not in s:
                raise RuntimeError(f"Score competition missing line_number field: {s}")
            if abs(failure_time - self._find_closest_time_for_score(s['line_number'])) <= time_window:
                relevant_scores.append(s)
        
        # Extract ornament processing if relevant
        if 'ornament_processings' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing ornament_processings - parsing may have failed")
        ornament_processings = self.comprehensive_data['ornament_processings']
        relevant_ornaments = []
        for o in ornament_processings:
            if 'pitch' not in o:
                raise RuntimeError(f"Ornament processing missing pitch field: {o}")
            if 'line_number' not in o:
                raise RuntimeError(f"Ornament processing missing line_number field: {o}")
            if (o['pitch'] == failure_pitch and
                abs(failure_time - self._find_closest_time_for_ornament(o['line_number'])) <= time_window):
                relevant_ornaments.append(o)
        
        # Build comprehensive context with actual data counts for debugging
        failed_checks = []
        passed_checks = []
        for t in relevant_timing:
            if 'timing_pass' not in t:
                raise RuntimeError(f"Timing check missing timing_pass field: {t}")
            if not t['timing_pass']:
                failed_checks.append(t)
            else:
                passed_checks.append(t)
        
        context = {
            'timing_constraints': {
                'failed_checks': failed_checks,
                'passed_checks': passed_checks,
                'total_checks': len(relevant_timing)
            },
            'match_type_analysis': {
                'classifications': relevant_match_types,
                'pitch_categorization': self._analyze_pitch_categorization(relevant_match_types)
            },
            'horizontal_rule_analysis': {
                'calculations': relevant_h_rules,
                'timing_failures': [h for h in relevant_h_rules if 'timing_pass' in h and not h['timing_pass']],
                'match_type_distribution': self._count_match_types(relevant_h_rules)
            },
            'cell_decisions': {
                'decisions': relevant_decisions,
                'winner_distribution': self._count_decision_winners(relevant_decisions),
                'update_patterns': [d for d in relevant_decisions if 'updated' in d and d['updated']]
            },
            'score_competition': {
                'score_progression': [s['current_score'] if 'current_score' in s else 0 for s in relevant_scores],
                'confidence_levels': [s['confidence'] if 'confidence' in s else 0 for s in relevant_scores],
                'beats_top_score': any('beats_top' in s and s['beats_top'] for s in relevant_scores)
            },
            'ornament_context': {
                'ornament_types': [o['ornament_type'] if 'ornament_type' in o else '' for o in relevant_ornaments],
                'credit_applied': sum(o['credit'] if 'credit' in o else 0 for o in relevant_ornaments),
                'has_ornaments': len(relevant_ornaments) > 0
            },
            'algorithmic_insights': {
                'likely_timing_issue': len(failed_checks) > 0,
                'ornament_interference': len(relevant_ornaments) > 0,
                'score_competition_active': len(relevant_scores) > 0,
                'decision_complexity': len(set(d['reason'] if 'reason' in d else '' for d in relevant_decisions))
            }
        }
        
        # Debug log the extracted context (only when meaningful data found)
        has_data = any([
            len(context['timing_constraints']['failed_checks']) > 0,
            len(context['match_type_analysis']['classifications']) > 0,
            len(context['horizontal_rule_analysis']['calculations']) > 0,
            len(context['cell_decisions']['decisions']) > 0,
            len(context['score_competition']['score_progression']) > 0,
            len(context['ornament_context']['ornament_types']) > 0
        ])
        
        if has_data:
            logger.info(f"Extracted comprehensive context for pitch {failure_pitch}: "
                       f"{len(relevant_timing)} timing checks ({len(context['timing_constraints']['failed_checks'])} failed), "
                       f"{len(relevant_h_rules)} horizontal rules, "
                       f"{len(relevant_match_types)} match type analyses")
        else:
            raise RuntimeError(f"No comprehensive context data found for failure at {failure_time:.3f}s, pitch {failure_pitch} - "
                             f"targeted parsing may have missed this failure location")
        
        return context
    
    def _find_closest_time_for_pitch(self, line_number: int) -> float:
        """Find the closest time for a given line number by looking at input events."""
        if 'input_events' not in self.comprehensive_data:
            raise RuntimeError("Comprehensive data missing input_events - parsing may have failed")
        input_events = self.comprehensive_data['input_events']
        for event in input_events:
            if 'line_number' not in event:
                raise RuntimeError(f"Input event missing line_number field: {event}")
            if 'time' not in event:
                raise RuntimeError(f"Input event missing time field: {event}")
            if event['line_number'] <= line_number:
                return event['time']
        raise RuntimeError(f"No input event found for line number {line_number} - comprehensive data incomplete")
    
    def _find_closest_time_for_decision(self, line_number: int) -> float:
        """Find time for decision by looking at nearby input events."""
        return self._find_closest_time_for_pitch(line_number)
    
    def _find_closest_time_for_score(self, line_number: int) -> float:
        """Find time for score by looking at nearby input events."""
        return self._find_closest_time_for_pitch(line_number)
    
    def _find_closest_time_for_ornament(self, line_number: int) -> float:
        """Find time for ornament by looking at nearby input events."""
        return self._find_closest_time_for_pitch(line_number)
    
    def _analyze_pitch_categorization(self, match_analyses: List[Dict]) -> Dict[str, int]:
        """Analyze how the pitch was categorized."""
        categories = {
            'chord': sum(1 for m in match_analyses if 'is_chord' in m and m['is_chord']),
            'trill': sum(1 for m in match_analyses if 'is_trill' in m and m['is_trill']),
            'grace': sum(1 for m in match_analyses if 'is_grace' in m and m['is_grace']),
            'extra': sum(1 for m in match_analyses if 'is_extra' in m and m['is_extra']),
            'ignored': sum(1 for m in match_analyses if 'is_ignored' in m and m['is_ignored'])
        }
        return categories
    
    def _count_match_types(self, h_rules: List[Dict]) -> Dict[str, int]:
        """Count different match types in horizontal rules."""
        types = {}
        for rule in h_rules:
            if 'match_type' not in rule:
                raise RuntimeError(f"Horizontal rule missing match_type field: {rule}")
            match_type = rule['match_type']
            if match_type in types:
                types[match_type] += 1
            else:
                types[match_type] = 1
        return types
    
    def _count_decision_winners(self, decisions: List[Dict]) -> Dict[str, int]:
        """Count decision winners (vertical vs horizontal)."""
        winners = {}
        for decision in decisions:
            if 'winner' not in decision:
                raise RuntimeError(f"Cell decision missing winner field: {decision}")
            winner = decision['winner']
            if winner in winners:
                winners[winner] += 1
            else:
                winners[winner] = 1
        return winners


def analyze_log_file(log_file_or_analysis: Path) -> FailureReport:
    """
    Analyze a log file or parsed analysis for failures.
    
    Args:
        log_file_or_analysis: Path to log file or analysis JSON
        
    Returns:
        Failure analysis report
    """
    # Determine if input is log file or analysis
    if log_file_or_analysis.suffix == '.log':
        logger.info(f"Parsing log file: {log_file_or_analysis}")
        parsed_data = parse_log_file(log_file_or_analysis, save_analysis=True)
    else:
        logger.info(f"Loading analysis file: {log_file_or_analysis}")
        parsed_data = load_json(log_file_or_analysis)
    
    # Analyze failures
    analyzer = FailureAnalyzer(parsed_data)
    report = analyzer.analyze()
    
    return report


def main():
    """Main entry point for failure analysis."""
    parser = argparse.ArgumentParser(description="Analyze score following failures")
    parser.add_argument("input_file", type=Path, help="Log file (.log) or analysis file (.json)")
    parser.add_argument("--output", "-o", type=Path, help="Output file for failure report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Analyze failures
        report = analyze_log_file(args.input_file)
        
        # Save report if output specified
        if args.output:
            save_json(asdict(report), args.output)
            logger.info(f"Report saved to: {args.output}")
        
        # Print summary
        print(f"\nFailure Analysis Summary:")
        print(f"Input File: {args.input_file}")
        print(f"Test Case: {report.test_case_id}")
        print(f"Total Failures: {report.total_failures}")
        
        if report.failure_contexts:
            print(f"\nFailure Types:")
            if 'failure_type_distribution' not in report.summary_statistics:
                raise RuntimeError("Summary statistics missing failure_type_distribution - analysis failed")
            type_dist = report.summary_statistics['failure_type_distribution']
            for failure_type, count in type_dist.items():
                print(f"  {failure_type}: {count}")
            
            print(f"\nFirst Failure: {report.failure_contexts[0].failure_time:.3f}s")
            print(f"Failure Type: {report.failure_contexts[0].failure_type}")
            print(f"Pitch: {report.failure_contexts[0].failure_pitch}")
            
            if report.recommendations:
                print(f"\nRecommendations:")
                for i, rec in enumerate(report.recommendations, 1):
                    print(f"  {i}. {rec}")
        else:
            print("No failures detected!")
            
    except Exception as e:
        logger.error(f"Error analyzing failures: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())