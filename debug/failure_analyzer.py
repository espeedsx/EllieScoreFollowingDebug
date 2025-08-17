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
            line_number=no_match.line_number
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
            return {}
        
        times = [d.time for d in decisions]
        inter_onset_intervals = [times[i] - times[i-1] for i in range(1, len(times))]
        
        # Look for timing irregularities
        avg_ioi = sum(inter_onset_intervals) / len(inter_onset_intervals) if inter_onset_intervals else 0
        
        timing_analysis = {
            'decision_count': len(decisions),
            'time_span': max(times) - min(times) if times else 0,
            'average_ioi': avg_ioi,
            'ioi_variance': sum((ioi - avg_ioi)**2 for ioi in inter_onset_intervals) / len(inter_onset_intervals) if inter_onset_intervals else 0,
            'max_gap': max(inter_onset_intervals) if inter_onset_intervals else 0,
            'min_gap': min(inter_onset_intervals) if inter_onset_intervals else 0,
            'time_to_failure': failure_time - max(times) if times else 0
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
            return {}
        
        failure_types = [fc.failure_type for fc in failure_contexts]
        failure_type_counts = {
            ft: failure_types.count(ft) for ft in set(failure_types)
        }
        
        # Timing statistics
        failure_times = [fc.failure_time for fc in failure_contexts]
        
        # Score statistics
        all_scores = []
        for fc in failure_contexts:
            all_scores.extend(fc.score_progression)
        
        return {
            'failure_type_distribution': failure_type_counts,
            'temporal_distribution': {
                'first_failure': min(failure_times) if failure_times else 0,
                'last_failure': max(failure_times) if failure_times else 0,
                'failure_span': max(failure_times) - min(failure_times) if len(failure_times) > 1 else 0
            },
            'score_statistics': {
                'min_score': min(all_scores) if all_scores else 0,
                'max_score': max(all_scores) if all_scores else 0,
                'avg_score': sum(all_scores) / len(all_scores) if all_scores else 0
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
            timing_issues.extend(fc.timing_analysis.get('issues', []))
        
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
        test_info = self.metadata.get('test_info')
        return test_info.get('test_case', 0) if test_info else 0
    
    def get_most_critical_failure(self) -> Optional[FailureContext]:
        """Get the most critical failure for focused AI analysis."""
        report = self.analyze()
        
        if not report.failure_contexts:
            return None
        
        # Focus primarily on no_match failures (unmatched notes)
        priority_order = ['no_match', 'wrong_match', 'score_drop']
        
        for failure_type in priority_order:
            failures_of_type = [fc for fc in report.failure_contexts if fc.failure_type == failure_type]
            if failures_of_type:
                # Return the first one (earliest in time)
                return min(failures_of_type, key=lambda fc: fc.failure_time)
        
        # Fallback to first failure
        return report.failure_contexts[0]


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
            type_dist = report.summary_statistics.get('failure_type_distribution', {})
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