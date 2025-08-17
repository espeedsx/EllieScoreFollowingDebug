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
        
        # Build performance caches for fast repeated lookups
        self._build_performance_caches()
    
    def _build_performance_caches(self):
        """Build performance caches for fast repeated lookups."""
        logger.debug("Building performance caches for failure analysis")
        
        # 1. Build line-to-time lookup table (O(1) instead of O(n) lookups)
        self._line_to_time_cache = {}
        
        # Add mappings from input_events (most accurate timing)
        input_events = self.comprehensive_data.get('input_events', [])
        for event in input_events:
            if 'line_number' in event and 'time' in event:
                line_num = event['line_number']
                time = event['time']
                # Keep highest line number for each time (most specific)
                if line_num not in self._line_to_time_cache or line_num > self._line_to_time_cache[line_num][1]:
                    self._line_to_time_cache[line_num] = (time, line_num)
        
        # Add mappings from DP decisions (fallback timing)
        for decision in self.dp_decisions:
            line_num = decision.line_number
            time = decision.time
            if line_num not in self._line_to_time_cache:
                self._line_to_time_cache[line_num] = (time, line_num)
        
        # 2. Pre-convert line numbers to times and create time-sorted indices
        # This avoids calling _find_closest_time_for_pitch thousands of times during analysis
        
        # Timing checks already have time, just sort by time
        self._timing_checks_by_time = sorted(
            self.comprehensive_data.get('timing_checks', []),
            key=lambda x: x.get('curr_time', 0)
        )
        
        # Pre-convert cell decisions to include times
        cell_decisions = self.comprehensive_data.get('cell_decisions', [])
        self._cell_decisions_with_time = []
        for decision in cell_decisions:
            line_num = decision.get('line_number', 0)
            if line_num in self._line_to_time_cache:
                time_val = self._line_to_time_cache[line_num][0]
                decision_with_time = decision.copy()
                decision_with_time['_cached_time'] = time_val
                self._cell_decisions_with_time.append(decision_with_time)
        self._cell_decisions_with_time.sort(key=lambda x: x['_cached_time'])
        
        # Pre-convert score competitions to include times
        score_competitions = self.comprehensive_data.get('score_competitions', [])
        self._score_competitions_with_time = []
        for score in score_competitions:
            line_num = score.get('line_number', 0)
            if line_num in self._line_to_time_cache:
                time_val = self._line_to_time_cache[line_num][0]
                score_with_time = score.copy()
                score_with_time['_cached_time'] = time_val
                self._score_competitions_with_time.append(score_with_time)
        self._score_competitions_with_time.sort(key=lambda x: x['_cached_time'])
        
        # 3. Initialize time window cache for overlapping contexts
        self._time_window_cache = {}
        
        logger.debug(f"Built caches: {len(self._line_to_time_cache)} line mappings, "
                    f"{len(self._timing_checks_by_time)} timing checks, "
                    f"{len(self._cell_decisions_with_time)} cell decisions")
    
    def _get_items_in_time_range(self, sorted_items, start_time, end_time, time_field):
        """Ultra-fast binary search to get items in time range. O(log n) instead of O(n)."""
        import bisect
        
        if not sorted_items:
            return []
        
        # Binary search for start index
        left = 0
        right = len(sorted_items)
        while left < right:
            mid = (left + right) // 2
            if sorted_items[mid][time_field] < start_time:
                left = mid + 1
            else:
                right = mid
        start_idx = left
        
        # Binary search for end index
        left = start_idx
        right = len(sorted_items)
        while left < right:
            mid = (left + right) // 2
            if sorted_items[mid][time_field] <= end_time:
                left = mid + 1
            else:
                right = mid
        end_idx = left
        
        return sorted_items[start_idx:end_idx]
    
    def analyze(self) -> FailureReport:
        """
        Perform complete failure analysis.
        
        Returns:
            Comprehensive failure report
        """
        try:
            from tqdm import tqdm
            use_progress_bar = True
        except ImportError:
            # Fallback if tqdm not available
            class tqdm:
                def __init__(self, total=None, desc="", ncols=None):
                    self.total = total
                    self.current = 0
                    print(f"{desc}...")
                def update(self, n=1):
                    self.current += n
                def set_description(self, desc):
                    print(f"{desc}...")
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            use_progress_bar = False
        
        logger.info("Starting failure analysis")
        
        failure_contexts = []
        
        # Calculate total steps for progress bar
        total_steps = len(self.no_matches) + len(self.matches) + len(self.dp_decisions) + 2
        
        with tqdm(total=total_steps, desc="Analyzing failures", ncols=80) as pbar:
            # Analyze explicit no-matches
            pbar.set_description("Analyzing no-matches")
            for no_match in self.no_matches:
                context = self._analyze_no_match_failure(no_match)
                if context:
                    failure_contexts.append(context)
                pbar.update(1)
            
            # Analyze potential wrong matches
            pbar.set_description("Analyzing wrong matches")
            wrong_match_contexts = self._analyze_potential_wrong_matches(pbar)
            failure_contexts.extend(wrong_match_contexts)
            
            # Analyze score drops (potential missed opportunities)
            pbar.set_description("Analyzing score drops")
            score_drop_contexts = self._analyze_score_drops(pbar)
            failure_contexts.extend(score_drop_contexts)
            
            # Generate summary statistics
            pbar.set_description("Generating statistics")
            summary_stats = self._generate_summary_statistics(failure_contexts)
            pbar.update(1)
            
            # Generate recommendations
            pbar.set_description("Generating recommendations")
            recommendations = self._generate_recommendations(failure_contexts)
            pbar.update(1)
        
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
    
    def _analyze_potential_wrong_matches(self, pbar=None) -> List[FailureContext]:
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
            if pbar:
                pbar.update(1)
        
        return contexts
    
    def _analyze_score_drops(self, pbar=None) -> List[FailureContext]:
        """Analyze significant score drops that might indicate missed opportunities."""
        contexts = []
        
        # Group decisions by column (performance note)
        by_column = {}
        for decision in self.dp_decisions:
            if decision.column not in by_column:
                by_column[decision.column] = []
            by_column[decision.column].append(decision)
            if pbar:
                pbar.update(1)
        
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
        # Use 1.0 second time window for comprehensive context (cached lookups make this fast)
        time_window = 1.0  # Restored to 1.0 second for better coverage
        start_time = failure_time - time_window
        end_time = failure_time + time_window
        
        # Check time window cache for overlapping contexts (major speedup for clustered failures)
        cache_key = (round(start_time, 1), round(end_time, 1))  # Round to 0.1s for cache hits
        if cache_key in self._time_window_cache:
            cached_context = self._time_window_cache[cache_key]
            # Filter cached results for this specific pitch
            return self._filter_cached_context_for_pitch(cached_context, failure_pitch)
        
        # Extract timing constraints using fast binary search on pre-sorted data
        relevant_timing = self._get_items_in_time_range(
            self._timing_checks_by_time, start_time, end_time, 'curr_time'
        )
        
        # Extract match type analyses for this pitch (simplified - just check pitch match)
        match_analyses = self.comprehensive_data.get('match_type_analyses', [])
        relevant_match_types = [m for m in match_analyses 
                               if m.get('pitch') == failure_pitch]
        
        # Extract horizontal rule calculations (use 'pitch' field from HRULE entries)
        horizontal_rules = self.comprehensive_data.get('horizontal_rules', [])
        relevant_h_rules = [h for h in horizontal_rules 
                           if h.get('pitch') == failure_pitch]
        
        # Extract cell decisions using ultra-fast binary search (no function calls!)
        relevant_decisions = self._get_items_in_time_range(
            self._cell_decisions_with_time, start_time, end_time, '_cached_time'
        )
        
        # Extract score competitions using ultra-fast binary search
        relevant_scores = self._get_items_in_time_range(
            self._score_competitions_with_time, start_time, end_time, '_cached_time'
        )
        
        # Extract vertical rule calculations around this time
        vertical_rules = self.comprehensive_data.get('vertical_rules', [])
        relevant_v_rules = []
        for vrule in vertical_rules:
            line_num = vrule.get('line_number', 0)
            if line_num in self._line_to_time_cache:
                vrule_time = self._line_to_time_cache[line_num][0]
                if start_time <= vrule_time <= end_time:
                    relevant_v_rules.append(vrule)
        
        # Extract matrix states around this time  
        matrix_states = self.comprehensive_data.get('matrix_states', [])
        relevant_matrices = []
        for matrix in matrix_states:
            line_num = matrix.get('line_number', 0)
            if line_num in self._line_to_time_cache:
                matrix_time = self._line_to_time_cache[line_num][0]
                if start_time <= matrix_time <= end_time:
                    relevant_matrices.append(matrix)
        
        # Extract array neighborhoods around this time
        array_neighborhoods = self.comprehensive_data.get('array_neighborhoods', [])
        relevant_arrays = []
        for array in array_neighborhoods:
            line_num = array.get('line_number', 0)
            if line_num in self._line_to_time_cache:
                array_time = self._line_to_time_cache[line_num][0]
                if start_time <= array_time <= end_time:
                    relevant_arrays.append(array)
        
        # Extract window movements around this time
        window_movements = self.comprehensive_data.get('window_movements', [])
        relevant_windows = []
        for window in window_movements:
            line_num = window.get('line_number', 0)
            if line_num in self._line_to_time_cache:
                window_time = self._line_to_time_cache[line_num][0]
                if start_time <= window_time <= end_time:
                    relevant_windows.append(window)
        
        # Extract ornament processing if relevant (only check pitch)
        ornament_processings = self.comprehensive_data.get('ornament_processings', [])
        relevant_ornaments = [o for o in ornament_processings 
                             if o.get('pitch') == failure_pitch]
        
        # Build comprehensive context with actual data counts for debugging (optimized)
        failed_checks = [t for t in relevant_timing if not t.get('timing_pass', True)]
        passed_checks = [t for t in relevant_timing if t.get('timing_pass', True)]
        
        context = {
            'timing_constraints': {
                'failed_checks': failed_checks,
                'passed_checks': passed_checks,
                'total_checks': len(relevant_timing),
                'detailed_failures': self._analyze_timing_failures(failed_checks)
            },
            'match_type_analysis': {
                'classifications': relevant_match_types,
                'pitch_categorization': self._analyze_pitch_categorization(relevant_match_types)
            },
            'horizontal_rule_analysis': {
                'calculations': relevant_h_rules,
                'timing_failures': [h for h in relevant_h_rules if not h.get('timing_pass', True)],
                'match_type_distribution': self._count_match_types(relevant_h_rules) if relevant_h_rules else {},
                'detailed_calculations': self._analyze_horizontal_rules(relevant_h_rules)
            },
            'vertical_rule_analysis': {
                'calculations': relevant_v_rules,
                'detailed_penalties': self._analyze_vertical_rules(relevant_v_rules)
            },
            'cell_decisions': {
                'decisions': relevant_decisions,
                'winner_distribution': self._count_decision_winners(relevant_decisions) if relevant_decisions else {},
                'update_patterns': [d for d in relevant_decisions if d.get('updated')],
                'detailed_decisions': self._analyze_cell_decisions(relevant_decisions)
            },
            'matrix_state': {
                'states': relevant_matrices,
                'window_info': self._analyze_matrix_states(relevant_matrices)
            },
            'array_neighborhoods': {
                'neighborhoods': relevant_arrays,
                'value_analysis': self._analyze_array_neighborhoods(relevant_arrays)
            },
            'window_movements': {
                'movements': relevant_windows,
                'movement_analysis': self._analyze_window_movements(relevant_windows)
            },
            'score_competition': {
                'score_progression': [s.get('current_score', 0) for s in relevant_scores],
                'confidence_levels': [s.get('confidence', 0) for s in relevant_scores],
                'beats_top_score': any(s.get('beats_top') for s in relevant_scores),
                'detailed_competition': self._analyze_score_competition(relevant_scores)
            },
            'ornament_context': {
                'ornament_types': [o.get('ornament_type', '') for o in relevant_ornaments],
                'credit_applied': sum(o.get('credit', 0) for o in relevant_ornaments),
                'has_ornaments': len(relevant_ornaments) > 0,
                'detailed_ornaments': self._analyze_ornament_processing(relevant_ornaments)
            },
            'algorithmic_insights': {
                'likely_timing_issue': len(failed_checks) > 0,
                'ornament_interference': len(relevant_ornaments) > 0,
                'score_competition_active': len(relevant_scores) > 0,
                'decision_complexity': len(set(d.get('reason', '') for d in relevant_decisions)) if relevant_decisions else 0
            }
        }
        
        # Store in cache for future overlapping contexts (includes all pitch data)
        self._time_window_cache[cache_key] = {
            'timing_constraints': context['timing_constraints'],
            'all_match_types': relevant_match_types,
            'all_h_rules': relevant_h_rules,
            'all_v_rules': relevant_v_rules,
            'all_ornaments': relevant_ornaments,
            'cell_decisions': context['cell_decisions'],
            'score_competition': context['score_competition'],
            'matrix_state': context['matrix_state'],
            'array_neighborhoods': context['array_neighborhoods'],
            'window_movements': context['window_movements'],
            'algorithmic_insights': context['algorithmic_insights']
        }
        
        return context
    
    def _filter_cached_context_for_pitch(self, cached_context: Dict[str, Any], failure_pitch: int) -> Dict[str, Any]:
        """Filter cached comprehensive context for a specific pitch."""
        # Filter pitch-specific data from cached context
        all_match_types = cached_context.get('all_match_types', [])
        relevant_match_types = [m for m in all_match_types if m.get('pitch') == failure_pitch]
        
        all_h_rules = cached_context.get('all_h_rules', [])
        relevant_h_rules = [h for h in all_h_rules if h.get('pitch') == failure_pitch]
        
        all_v_rules = cached_context.get('all_v_rules', [])
        # Vertical rules are not pitch-specific, include all
        
        all_ornaments = cached_context.get('all_ornaments', [])
        relevant_ornaments = [o for o in all_ornaments if o.get('pitch') == failure_pitch]
        
        return {
            'timing_constraints': cached_context['timing_constraints'],
            'match_type_analysis': {
                'classifications': relevant_match_types,
                'pitch_categorization': self._analyze_pitch_categorization(relevant_match_types)
            },
            'horizontal_rule_analysis': {
                'calculations': relevant_h_rules,
                'timing_failures': [h for h in relevant_h_rules if not h.get('timing_pass', True)],
                'match_type_distribution': self._count_match_types(relevant_h_rules) if relevant_h_rules else {},
                'detailed_calculations': self._analyze_horizontal_rules(relevant_h_rules)
            },
            'vertical_rule_analysis': {
                'calculations': all_v_rules,
                'detailed_penalties': self._analyze_vertical_rules(all_v_rules)
            },
            'cell_decisions': cached_context['cell_decisions'],
            'score_competition': cached_context['score_competition'],
            'matrix_state': cached_context['matrix_state'],
            'array_neighborhoods': cached_context['array_neighborhoods'],
            'window_movements': cached_context['window_movements'],
            'ornament_context': {
                'ornament_types': [o.get('ornament_type', '') for o in relevant_ornaments],
                'credit_applied': sum(o.get('credit', 0) for o in relevant_ornaments),
                'has_ornaments': len(relevant_ornaments) > 0,
                'detailed_ornaments': self._analyze_ornament_processing(relevant_ornaments)
            },
            'algorithmic_insights': cached_context['algorithmic_insights']
        }
    
    def _find_closest_time_for_pitch(self, line_number: int) -> float:
        """Find the closest time for a given line number using cached O(1) lookup."""
        # Direct cache lookup - O(1) instead of O(n)
        if line_number in self._line_to_time_cache:
            return self._line_to_time_cache[line_number][0]
        
        # Find closest lower line number in cache
        closest_line = None
        for cached_line in self._line_to_time_cache:
            if cached_line <= line_number:
                if closest_line is None or cached_line > closest_line:
                    closest_line = cached_line
        
        if closest_line is not None:
            return self._line_to_time_cache[closest_line][0]
        
        # Fallback: use earliest available time
        if self.dp_decisions:
            logger.warning(f"No time data found for line {line_number}, using earliest DP decision time")
            return min(d.time for d in self.dp_decisions)
        
        raise RuntimeError(f"No timing data available - line-to-time cache is empty")
    
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
    
    def _analyze_timing_failures(self, failed_checks: List[Dict]) -> List[Dict]:
        """Analyze detailed timing constraint failures with tempo awareness."""
        failures = []
        for check in failed_checks[:5]:  # Limit to first 5 for prompt size
            if all(key in check for key in ['ioi', 'limit', 'constraint_type', 'curr_time']):
                # Extract performance timing information
                performance_ioi = check['ioi']
                timing_limit = check['limit']
                constraint_type = check['constraint_type']
                
                # Calculate excess timing
                excess_seconds = performance_ioi - timing_limit
                excess_ms = excess_seconds * 1000
                
                # Analyze tempo context if available
                tempo_context = self._analyze_tempo_context(check)
                
                failure_detail = {
                    'performance_ioi': performance_ioi,
                    'timing_limit': timing_limit,
                    'excess_seconds': excess_seconds,
                    'excess_ms': excess_ms,
                    'constraint_type': constraint_type,
                    'time': check['curr_time'],
                    'tempo_ratio': tempo_context.get('estimated_tempo_ratio', 'unknown'),
                    'tempo_context': tempo_context
                }
                failures.append(failure_detail)
        return failures
    
    def _analyze_tempo_context(self, timing_check: Dict) -> Dict[str, Any]:
        """Analyze tempo context for a timing check."""
        try:
            curr_time = timing_check.get('curr_time', 0)
            prev_time = timing_check.get('prev_time', 0)
            constraint_type = timing_check.get('constraint_type', 'unknown')
            ioi = timing_check.get('ioi', 0)
            
            # Check if this is a valid timing calculation
            # IOI > 10 seconds or prev_time < 0 indicates initialization issues
            is_valid_timing = prev_time >= 0 and ioi < 10.0
            
            if not is_valid_timing:
                return {
                    'performance_time_range': f"invalid (prev_time: {prev_time:.3f}s, curr_time: {curr_time:.3f}s)",
                    'performance_ioi': ioi,
                    'expected_score_ioi': self._estimate_score_ioi(constraint_type),
                    'estimated_tempo_ratio': 'invalid',
                    'tempo_interpretation': 'Invalid timing data - likely algorithm initialization artifact',
                    'note': 'Previous time is uninitialized (-1) or IOI is unrealistically large'
                }
            
            # For valid timing, calculate tempo ratio
            expected_score_ioi = self._estimate_score_ioi(constraint_type)
            tempo_ratio = 'unknown'
            if expected_score_ioi and expected_score_ioi > 0:
                tempo_ratio = ioi / expected_score_ioi
            
            return {
                'performance_time_range': f"{prev_time:.3f}s to {curr_time:.3f}s",
                'performance_ioi': ioi,
                'expected_score_ioi': expected_score_ioi,
                'estimated_tempo_ratio': tempo_ratio,
                'tempo_interpretation': self._interpret_tempo_ratio(tempo_ratio)
            }
        except Exception as e:
            return {'error': f"Tempo analysis failed: {e}"}
    
    def _estimate_score_ioi(self, constraint_type: str) -> Optional[float]:
        """Estimate expected score IOI based on constraint type."""
        # These are rough estimates based on musical context
        score_ioi_estimates = {
            'chord_basic': 0.1,      # Basic chord timing
            'chord': 0.1,            # Standard chord timing  
            'trill': 0.2,            # Trill note spacing
            'grace': 0.05,           # Grace note timing
            'melody': 0.3,           # Typical melody note spacing
        }
        return score_ioi_estimates.get(constraint_type)
    
    def _interpret_tempo_ratio(self, tempo_ratio) -> str:
        """Interpret the tempo ratio in musical terms."""
        if tempo_ratio == 'unknown':
            return 'Cannot determine tempo relationship'
        
        try:
            ratio = float(tempo_ratio)
            if ratio > 1.5:
                return f'Much slower than score (playing {ratio:.1f}x slower)'
            elif ratio > 1.1:
                return f'Slightly slower than score (playing {ratio:.1f}x slower)'
            elif ratio > 0.9:
                return f'Close to score tempo (playing {ratio:.1f}x speed)'
            elif ratio > 0.5:
                return f'Faster than score (playing {ratio:.1f}x speed)'
            else:
                return f'Much faster than score (playing {ratio:.1f}x speed)'
        except (ValueError, TypeError):
            return 'Invalid tempo ratio'
    
    def _analyze_horizontal_rules(self, h_rules: List[Dict]) -> List[Dict]:
        """Analyze detailed horizontal rule calculations with tempo awareness."""
        calculations = []
        for rule in h_rules[:5]:  # Limit for prompt size
            # Use actual field names from parsed data
            if all(key in rule for key in ['pitch', 'ioi', 'limit', 'timing_pass', 'match_type', 'result']):
                ioi = rule['ioi']
                limit = rule['limit']
                match_type = rule['match_type']
                
                # Check if IOI indicates invalid timing (initialization artifact)
                is_valid_ioi = ioi < 10.0  # Reasonable performance timing
                timing_status = "VALID" if is_valid_ioi else "INVALID (initialization artifact)"
                
                # Only do tempo analysis for valid IOI values
                tempo_context = None
                if is_valid_ioi:
                    expected_score_ioi = self._estimate_score_ioi(match_type)
                    if expected_score_ioi and expected_score_ioi > 0:
                        tempo_ratio = ioi / expected_score_ioi
                        tempo_context = {
                            'expected_score_ioi': expected_score_ioi,
                            'tempo_ratio': tempo_ratio,
                            'tempo_interpretation': self._interpret_tempo_ratio(tempo_ratio)
                        }
                
                calc_detail = {
                    'pitch': rule['pitch'],
                    'performance_ioi': ioi,
                    'timing_limit': limit,
                    'timing_pass': rule['timing_pass'],
                    'match_type': match_type,
                    'result': rule['result'],
                    'excess_ms': (ioi - limit) * 1000 if ioi > limit else 0,
                    'timing_status': timing_status,
                    'tempo_analysis': tempo_context
                }
                calculations.append(calc_detail)
        return calculations
    
    def _analyze_vertical_rules(self, v_rules: List[Dict]) -> List[Dict]:
        """Analyze detailed vertical rule penalty calculations."""
        penalties = []
        for rule in v_rules[:5]:  # Limit for prompt size
            # Use actual field names: up_value, penalty, result
            if all(key in rule for key in ['row', 'penalty', 'result']):
                penalty_detail = {
                    'row': rule['row'],
                    'penalty': rule['penalty'],
                    'up_value': rule.get('up_value', 0),
                    'result': rule['result'],
                    'start_point': rule.get('start_point', '')
                }
                penalties.append(penalty_detail)
        return penalties
    
    def _analyze_cell_decisions(self, decisions: List[Dict]) -> List[Dict]:
        """Analyze detailed cell decision reasoning."""
        decision_details = []
        for decision in decisions[:5]:  # Limit for prompt size
            # Use actual field names: vertical_result, horizontal_result, winner, reason
            if all(key in decision for key in ['row', 'vertical_result', 'horizontal_result', 'winner', 'reason']):
                detail = {
                    'row': decision['row'],
                    'vertical_value': decision['vertical_result'],
                    'horizontal_value': decision['horizontal_result'],
                    'winner': decision['winner'],
                    'reason': decision['reason'],
                    'updated': decision.get('updated', False),
                    'margin': abs(decision['vertical_result'] - decision['horizontal_result']),
                    'final_value': decision.get('final_value', 0)
                }
                decision_details.append(detail)
        return decision_details
    
    def _analyze_matrix_states(self, matrices: List[Dict]) -> Dict[str, Any]:
        """Analyze matrix window states."""
        if not matrices:
            return {}
        
        latest_matrix = matrices[-1]  # Most recent matrix state
        return {
            'window_start': latest_matrix.get('window_start', 0),
            'window_end': latest_matrix.get('window_end', 0),
            'window_center': latest_matrix.get('window_center', 0),
            'current_base': latest_matrix.get('current_base', 0),
            'prev_base': latest_matrix.get('prev_base', 0),
            'current_upper': latest_matrix.get('current_upper', 0),
            'prev_upper': latest_matrix.get('prev_upper', 0),
            'window_size': latest_matrix.get('window_end', 0) - latest_matrix.get('window_start', 0)
        }
    
    def _analyze_array_neighborhoods(self, arrays: List[Dict]) -> List[Dict]:
        """Analyze array neighborhood values."""
        neighborhoods = []
        for array in arrays[:3]:  # Limit for prompt size
            # Use actual field names: center_value, neighbor_values
            if all(key in array for key in ['row', 'center_value', 'neighbor_values']):
                neighborhood = {
                    'row': array['row'],
                    'center_value': array['center_value'],
                    'neighborhood_values': array['neighbor_values'][:5] if isinstance(array['neighbor_values'], list) else [],
                    'max_value': max(array['neighbor_values']) if isinstance(array['neighbor_values'], list) and array['neighbor_values'] else 0,
                    'positions': array.get('positions', [])
                }
                neighborhoods.append(neighborhood)
        return neighborhoods
    
    def _analyze_window_movements(self, windows: List[Dict]) -> List[Dict]:
        """Analyze window movement patterns."""
        movements = []
        for window in windows[:3]:  # Limit for prompt size
            if all(key in window for key in ['old_start', 'new_start', 'old_end', 'new_end', 'reason']):
                movement = {
                    'old_window': [window['old_start'], window['old_end']],
                    'new_window': [window['new_start'], window['new_end']],
                    'size_change': (window['new_end'] - window['new_start']) - (window['old_end'] - window['old_start']),
                    'position_shift': window['new_start'] - window['old_start'],
                    'reason': window['reason']
                }
                movements.append(movement)
        return movements
    
    def _analyze_score_competition(self, scores: List[Dict]) -> List[Dict]:
        """Analyze detailed score competition dynamics."""
        competition = []
        for score in scores[:5]:  # Limit for prompt size
            if all(key in score for key in ['row', 'current_score', 'top_score']):
                comp_detail = {
                    'row': score['row'],
                    'current_score': score['current_score'],
                    'top_score': score['top_score'],
                    'margin': score['current_score'] - score['top_score'],
                    'beats_top': score.get('beats_top', False),
                    'confidence': score.get('confidence', 0)
                }
                competition.append(comp_detail)
        return competition
    
    def _analyze_ornament_processing(self, ornaments: List[Dict]) -> List[Dict]:
        """Analyze detailed ornament processing."""
        ornament_details = []
        for ornament in ornaments[:3]:  # Limit for prompt size
            if 'ornament_type' in ornament:
                detail = {
                    'pitch': ornament.get('pitch', 0),
                    'ornament_type': ornament['ornament_type'],
                    'trill_notes': ornament.get('trill_pitches', []),
                    'grace_notes': ornament.get('grace_pitches', []),
                    'ignored_notes': ornament.get('ignore_pitches', []),
                    'credit_applied': ornament.get('credit', 0)
                }
                ornament_details.append(detail)
        return ornament_details


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