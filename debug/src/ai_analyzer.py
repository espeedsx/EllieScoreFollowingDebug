#!/usr/bin/env python3
"""
AI analyzer for score following debug system.
Generates AI-powered insights from failure contexts.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import asdict

from config import REPORTS_DIR, get_report_filename
from utils import setup_logging, save_json, get_timestamp, format_pitches
from failure_analyzer import FailureContext, FailureReport, analyze_log_file


logger = setup_logging(__name__)


class AIAnalyzer:
    """Generates AI analysis prompts and processes insights."""
    
    def __init__(self, failure_report: FailureReport):
        self.report = failure_report
        
    def generate_analysis_prompt(self, focus_context: Optional[FailureContext] = None, filtered_failures: Optional[List[FailureContext]] = None) -> str:
        """
        Generate a focused AI analysis prompt.
        
        Args:
            focus_context: Specific failure context to focus on, or None for general analysis
            filtered_failures: Optional filtered list of failures to use instead of all failures
            
        Returns:
            Detailed prompt for AI analysis
        """
        if focus_context:
            return self._generate_focused_prompt(focus_context)
        else:
            return self._generate_general_prompt(filtered_failures)
    
    def _generate_focused_prompt(self, context: FailureContext) -> str:
        """Generate a prompt focused on a specific failure."""
        
        # Format context decisions for readability
        context_summary = self._format_context_decisions(context.context_decisions)
        timing_info = self._format_timing_analysis(context.timing_analysis)
        score_progression = self._format_score_progression(context.score_progression)
        
        # Format comprehensive algorithm context (required)
        if not context.comprehensive_context:
            raise RuntimeError(f"Focus context at {context.failure_time:.3f}s lacks comprehensive_context - analysis pipeline broken")
        
        logger.debug(f"Formatting comprehensive context with keys: {list(context.comprehensive_context.keys())}")
        comprehensive_analysis = self._format_comprehensive_context(context.comprehensive_context)
        
        if not comprehensive_analysis:
            raise RuntimeError("Generated empty comprehensive analysis - formatting may have failed")
        
        logger.info(f"Generated comprehensive analysis: {len(comprehensive_analysis)} characters")
        
        prompt = f"""# Score Following Algorithm Failure Analysis

## Context
You are analyzing a failure in a real-time score following algorithm that uses dynamic programming to match musical performance notes against a musical score. The algorithm maintains a matrix where rows represent score events and columns represent performance events.

## Failure Details
- **Failure Type**: {context.failure_type}
- **Time**: {context.failure_time:.3f} seconds
- **Pitch**: {context.failure_pitch} (MIDI note number)
- **Expected**: {context.expected_outcome}
- **Actual**: {context.actual_outcome}

## Algorithm Context
The dynamic programming algorithm uses these key components:
- **Vertical Rule**: Advance in score without matching (penalty for missing notes)
- **Horizontal Rule**: Match performance note to score note (credit for matches)
- **Final Value**: Maximum of vertical and horizontal rule values
- **Used Pitches**: Notes already matched in current chord
- **Unused Count**: Number of expected notes not yet matched

## Decision Sequence Leading to Failure
{context_summary}

## Score Progression
The algorithm's confidence scores leading to the failure:
{score_progression}

## Timing Analysis
{timing_info}

## Preceding Successful Matches
{self._format_preceding_matches(context.preceding_matches)}

{comprehensive_analysis}

## Your Task
Analyze this failure using the ultra-detailed algorithm data and provide insights on:

1. **Root Cause Analysis**: 
   - What specific algorithm decision or parameter likely caused this failure?
   - Which timing constraint check failed and why?
   - Did the horizontal/vertical rule calculations contribute to the failure?

2. **Decision Tree Deep Dive**: 
   - How did the sequence of cell decisions lead to the wrong outcome?
   - Which decision winner (vertical vs horizontal) was chosen incorrectly?
   - What match type classifications affected the final decision?

3. **Timing Constraint Analysis**: 
   - Which specific timing checks failed for this pitch?
   - Are the IOI (inter-onset interval) limits appropriate for this musical context?
   - How do the timing constraints compare to successful nearby matches?

4. **Algorithm State Investigation**:
   - What was the score competition state when the failure occurred?
   - How did the confidence levels evolve leading to the failure?
   - Were there ornament processing complications (trills, grace notes)?

5. **Parameter Optimization**:
   - Which timing limits need adjustment (chord_basic vs chord vs trill vs grace)?
   - Should the penalty values for extra notes be modified?
   - Are the scoring credits for matches appropriately balanced?

6. **Strategic Algorithmic Improvements**:
   - Would alternative match type classification help?
   - Should the window management strategy be adjusted?
   - What preprocessing could prevent this type of failure?

7. **Implementation Fixes**:
   - Specific code changes to prevent this failure type
   - Parameter value recommendations with rationale
   - Testing strategies to validate improvements

Please reference the specific algorithm data points, timing values, decision winners, and match type classifications in your analysis.
"""
        return prompt
    
    def _generate_general_prompt(self, filtered_failures: Optional[List[FailureContext]] = None) -> str:
        """Generate a general analysis prompt for overall patterns."""
        
        # Use filtered failures if provided, otherwise use all failures
        failures_to_analyze = filtered_failures if filtered_failures is not None else self.report.failure_contexts
        
        # Get most critical failures for overview
        critical_failures = failures_to_analyze[:3]  # Top 3
        
        failure_summaries = []
        for i, failure in enumerate(critical_failures, 1):
            summary = f"""
### Failure {i}: {failure.failure_type.replace('_', ' ').title()}
- Time: {failure.failure_time:.3f}s, Pitch: {failure.failure_pitch}
- Expected: {failure.expected_outcome}
- Actual: {failure.actual_outcome}
- Context decisions: {len(failure.context_decisions)}
- Score range: {min(failure.score_progression):.1f} to {max(failure.score_progression):.1f}
"""
            failure_summaries.append(summary)
        
        # Add filtering info if applicable
        filter_info = ""
        if filtered_failures is not None and len(filtered_failures) != len(self.report.failure_contexts):
            min_time = min(f.failure_time for f in filtered_failures) if filtered_failures else 0
            filter_info = f"\n- **Filtered after score time**: {min_time:.3f}s"
        
        total_failures = len(failures_to_analyze)
        
        prompt = f"""# Score Following Algorithm Pattern Analysis

## Context
You are analyzing patterns of failures in a real-time score following algorithm. The algorithm uses dynamic programming to match musical performance against a score.

## Test Case Overview
- **Test Case ID**: {self.report.test_case_id}
- **Total Failures**: {total_failures} (Original: {self.report.total_failures})
- **Log File**: {Path(self.report.log_file).name}{filter_info}

## Failure Distribution
{self._format_failure_distribution(failures_to_analyze)}

## Critical Failures
{''.join(failure_summaries)}

## Summary Statistics
{self._format_summary_statistics(failures_to_analyze)}

## Current Recommendations
{self._format_recommendations()}

## Your Task
Analyze these failure patterns and provide:

1. **Pattern Recognition**: What common patterns do you see across failures?

2. **Systematic Issues**: Are there systematic problems with the algorithm design or parameters?

3. **Priority Ranking**: Which failures should be addressed first and why?

4. **Parameter Tuning**: What specific parameter adjustments would you recommend?

5. **Algorithm Improvements**: What fundamental algorithmic improvements could prevent these failure patterns?

6. **Testing Strategy**: How should the fixes be validated?

Focus on actionable insights that can guide algorithm improvements.
"""
        return prompt
    
    def _format_context_decisions(self, decisions: List[Dict[str, Any]]) -> str:
        """Format decision context for readability."""
        if not decisions:
            return "No context decisions available."
        
        formatted = []
        for i, decision in enumerate(decisions):
            # Validate required fields
            required_fields = ['used_pitches', 'row', 'pitch', 'time', 'vertical_rule', 'horizontal_rule', 'final_value', 'match_flag', 'unused_count']
            for field in required_fields:
                if field not in decision:
                    raise ValueError(f"Decision {i+1} missing required field '{field}': {decision}")
            
            used_str = format_pitches(decision['used_pitches'])
            formatted.append(
                f"Decision {i+1}: "
                f"Row {decision['row']}, "
                f"Pitch {decision['pitch']}, "
                f"Time {decision['time']:.3f}s\n"
                f"  - Vertical rule: {decision['vertical_rule']:.1f}\n"
                f"  - Horizontal rule: {decision['horizontal_rule']:.1f}\n"
                f"  - Final value: {decision['final_value']:.1f}\n"
                f"  - Match flag: {decision['match_flag']}\n"
                f"  - Used pitches: {used_str}\n"
                f"  - Unused count: {decision['unused_count']}"
            )
        
        return "\n\n".join(formatted)
    
    def _format_timing_analysis(self, timing: Dict[str, Any]) -> str:
        """Format timing analysis for readability."""
        if not timing:
            return "No timing analysis available."
        
        # Validate required timing fields
        required_fields = ['time_span', 'average_ioi', 'max_gap', 'time_to_failure', 'issues']
        for field in required_fields:
            if field not in timing:
                raise ValueError(f"Timing analysis missing required field '{field}': {timing}")
        
        analysis = []
        analysis.append(f"- Decision span: {timing['time_span']:.3f} seconds")
        analysis.append(f"- Average inter-onset interval: {timing['average_ioi']:.3f}s")
        analysis.append(f"- Maximum gap: {timing['max_gap']:.3f}s")
        analysis.append(f"- Time to failure: {timing['time_to_failure']:.3f}s")
        
        issues = timing['issues']
        if issues:
            analysis.append(f"- Issues detected: {', '.join(issues)}")
        
        return "\n".join(analysis)
    
    def _format_score_progression(self, scores: List[float]) -> str:
        """Format score progression for readability."""
        if not scores:
            return "No score progression available."
        
        # Show all scores if 10 or fewer, otherwise show first/last few
        if len(scores) <= 10:
            score_str = " -> ".join(f"{s:.1f}" for s in scores)
        else:
            first_few = " -> ".join(f"{s:.1f}" for s in scores[:3])
            last_few = " -> ".join(f"{s:.1f}" for s in scores[-3:])
            score_str = f"{first_few} -> ... -> {last_few}"
        
        trend = "increasing" if scores[-1] > scores[0] else "decreasing" if scores[-1] < scores[0] else "stable"
        
        return f"{score_str}\nTrend: {trend} (from {scores[0]:.1f} to {scores[-1]:.1f})"
    
    def _format_preceding_matches(self, matches: List[Dict[str, Any]]) -> str:
        """Format preceding matches for context."""
        if not matches:
            return "No preceding matches available."
        
        formatted = []
        for i, match in enumerate(matches):
            # Validate required match fields
            required_fields = ['pitch', 'time', 'score']
            for field in required_fields:
                if field not in match:
                    raise ValueError(f"Match {i+1} missing required field '{field}': {match}")
            
            formatted.append(
                f"Match {i+1}: "
                f"Pitch {match['pitch']} at {match['time']:.3f}s, "
                f"Score {match['score']:.1f}"
            )
        
        return "\n".join(formatted)
    
    def _format_comprehensive_context(self, comprehensive_context: Dict[str, Any]) -> str:
        """Format comprehensive algorithm context for AI analysis."""
        if not comprehensive_context:
            return ""
        
        sections = []
        
        # Timing Constraints Analysis
        if 'timing_constraints' not in comprehensive_context:
            raise ValueError("Comprehensive context missing timing_constraints - analysis pipeline broken")
        timing_data = comprehensive_context['timing_constraints']
        if timing_data:
            sections.append("## Ultra-Comprehensive Algorithm Analysis")
            sections.append("\n### Timing Constraint Details")
            
            required_timing_fields = ['failed_checks', 'passed_checks', 'total_checks']
            for field in required_timing_fields:
                if field not in timing_data:
                    raise ValueError(f"Timing data missing required field '{field}': {timing_data}")
            
            failed_checks = timing_data['failed_checks']
            passed_checks = timing_data['passed_checks']
            total_checks = timing_data['total_checks']
            
            sections.append(f"- **Total timing checks**: {total_checks}")
            sections.append(f"- **Failed checks**: {len(failed_checks)}")
            sections.append(f"- **Passed checks**: {len(passed_checks)}")
            
            if failed_checks:
                sections.append("\n**Failed Timing Constraints:**")
                for i, check in enumerate(failed_checks[:3]):  # Show first 3
                    check_required_fields = ['ioi', 'limit', 'constraint_type']
                    for field in check_required_fields:
                        if field not in check:
                            raise ValueError(f"Failed timing check {i+1} missing required field '{field}': {check}")
                    sections.append(f"  {i+1}. IOI: {check['ioi']:.3f}s > Limit: {check['limit']:.3f}s (Type: {check['constraint_type']})")
        
        # Match Type Analysis
        if 'match_type_analysis' not in comprehensive_context:
            raise ValueError("Comprehensive context missing match_type_analysis - analysis pipeline broken")
        match_data = comprehensive_context['match_type_analysis']
        if match_data:
            sections.append("\n### Match Type Classification")
            if 'pitch_categorization' not in match_data:
                raise ValueError("Match type analysis missing pitch_categorization field")
            categorization = match_data['pitch_categorization']
            
            for category, count in categorization.items():
                if count > 0:
                    sections.append(f"- **{category.title()}**: {count} classification{'s' if count != 1 else ''}")
        
        # Horizontal Rule Analysis
        if 'horizontal_rule_analysis' not in comprehensive_context:
            raise ValueError("Comprehensive context missing horizontal_rule_analysis - analysis pipeline broken")
        h_rule_data = comprehensive_context['horizontal_rule_analysis']
        if h_rule_data:
            sections.append("\n### Horizontal Rule Calculations")
            
            required_h_rule_fields = ['calculations', 'timing_failures', 'match_type_distribution']
            for field in required_h_rule_fields:
                if field not in h_rule_data:
                    raise ValueError(f"Horizontal rule analysis missing required field '{field}': {h_rule_data}")
            
            calculations = h_rule_data['calculations']
            timing_failures = h_rule_data['timing_failures']
            match_types = h_rule_data['match_type_distribution']
            
            sections.append(f"- **Total calculations**: {len(calculations)}")
            sections.append(f"- **Timing failures**: {len(timing_failures)}")
            
            if match_types:
                sections.append("- **Match type distribution**:")
                for match_type, count in match_types.items():
                    sections.append(f"  - {match_type}: {count}")
        
        # Cell Decision Analysis  
        if 'cell_decisions' not in comprehensive_context:
            raise ValueError("Comprehensive context missing cell_decisions - analysis pipeline broken")
        decision_data = comprehensive_context['cell_decisions']
        if decision_data:
            sections.append("\n### Cell Decision Analysis")
            
            required_decision_fields = ['decisions', 'winner_distribution', 'update_patterns']
            for field in required_decision_fields:
                if field not in decision_data:
                    raise ValueError(f"Cell decisions missing required field '{field}': {decision_data}")
            
            decisions = decision_data['decisions']
            winners = decision_data['winner_distribution']
            updates = decision_data['update_patterns']
            
            sections.append(f"- **Total decisions**: {len(decisions)}")
            sections.append(f"- **Cell updates**: {len(updates)}")
            
            if winners:
                sections.append("- **Decision winners**:")
                for winner, count in winners.items():
                    sections.append(f"  - {winner}: {count}")
        
        # Score Competition Analysis
        if 'score_competition' not in comprehensive_context:
            raise ValueError("Comprehensive context missing score_competition - analysis pipeline broken")
        score_data = comprehensive_context['score_competition']
        if score_data:
            sections.append("\n### Score Competition State")
            
            required_score_fields = ['score_progression', 'confidence_levels', 'beats_top_score']
            for field in required_score_fields:
                if field not in score_data:
                    raise ValueError(f"Score competition missing required field '{field}': {score_data}")
            
            progression = score_data['score_progression']
            confidence = score_data['confidence_levels']
            beats_top = score_data['beats_top_score']
            
            if progression:
                sections.append(f"- **Score progression**: {progression[0]:.1f} → {progression[-1]:.1f}")
            if confidence:
                sections.append(f"- **Confidence range**: {min(confidence):.1f} to {max(confidence):.1f}")
            sections.append(f"- **Beats top score**: {beats_top}")
        
        # Ornament Context
        if 'ornament_context' not in comprehensive_context:
            raise ValueError("Comprehensive context missing ornament_context - analysis pipeline broken")
        ornament_data = comprehensive_context['ornament_context']
        if ornament_data:
            sections.append("\n### Ornament Processing")
            
            required_ornament_fields = ['has_ornaments', 'ornament_types', 'credit_applied']
            for field in required_ornament_fields:
                if field not in ornament_data:
                    raise ValueError(f"Ornament context missing required field '{field}': {ornament_data}")
            
            has_ornaments = ornament_data['has_ornaments']
            ornament_types = ornament_data['ornament_types']
            credit = ornament_data['credit_applied']
            
            sections.append(f"- **Ornaments present**: {has_ornaments}")
            if ornament_types:
                unique_types = list(set(ornament_types))
                sections.append(f"- **Ornament types**: {', '.join(unique_types)}")
            sections.append(f"- **Credit applied**: {credit}")
        
        # Algorithmic Insights
        if 'algorithmic_insights' not in comprehensive_context:
            raise ValueError("Comprehensive context missing algorithmic_insights - analysis pipeline broken")
        insights_data = comprehensive_context['algorithmic_insights']
        if insights_data:
            sections.append("\n### Algorithmic Insights")
            
            required_insights_fields = ['likely_timing_issue', 'ornament_interference', 'score_competition_active', 'decision_complexity']
            for field in required_insights_fields:
                if field not in insights_data:
                    raise ValueError(f"Algorithmic insights missing required field '{field}': {insights_data}")
            
            timing_issue = insights_data['likely_timing_issue']
            ornament_interference = insights_data['ornament_interference']
            score_competition_active = insights_data['score_competition_active']
            decision_complexity = insights_data['decision_complexity']
            
            sections.append(f"- **Likely timing issue**: {timing_issue}")
            sections.append(f"- **Ornament interference**: {ornament_interference}")
            sections.append(f"- **Score competition active**: {score_competition_active}")
            sections.append(f"- **Decision complexity**: {decision_complexity} different decision reasons")
        
        return "\n".join(sections)
    
    def _format_failure_distribution(self, failures: Optional[List[FailureContext]] = None) -> str:
        """Format failure type distribution."""
        if failures is None:
            stats = self.report.summary_statistics
            if 'failure_type_distribution' not in stats:
                raise ValueError("Summary statistics missing failure_type_distribution field")
            dist = stats['failure_type_distribution']
        else:
            # Calculate distribution from filtered failures
            dist = {}
            for failure in failures:
                failure_type = failure.failure_type
                if failure_type in dist:
                    dist[failure_type] += 1
                else:
                    dist[failure_type] = 1
        
        if not dist:
            return "No failure distribution data available."
        
        total = sum(dist.values())
        formatted = []
        for failure_type, count in dist.items():
            percentage = (count / total) * 100 if total > 0 else 0
            formatted.append(f"- {failure_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        return "\n".join(formatted)
    
    def _format_summary_statistics(self, failures: Optional[List[FailureContext]] = None) -> str:
        """Format summary statistics."""
        if failures is None:
            stats = self.report.summary_statistics
            
            formatted = []
            
            # Temporal distribution
            if 'temporal_distribution' not in stats:
                raise ValueError("Summary statistics missing temporal_distribution field")
            temporal = stats['temporal_distribution']
            if temporal:
                required_temporal_fields = ['first_failure', 'last_failure']
                for field in required_temporal_fields:
                    if field not in temporal:
                        raise ValueError(f"Temporal distribution missing required field '{field}': {temporal}")
                formatted.append(f"**Temporal spread**: {temporal['first_failure']:.3f}s to {temporal['last_failure']:.3f}s")
            
            # Score statistics
            if 'score_statistics' not in stats:
                raise ValueError("Summary statistics missing score_statistics field")
            score_stats = stats['score_statistics']
            if score_stats:
                required_score_fields = ['min_score', 'max_score', 'avg_score']
                for field in required_score_fields:
                    if field not in score_stats:
                        raise ValueError(f"Score statistics missing required field '{field}': {score_stats}")
                formatted.append(f"**Score range**: {score_stats['min_score']:.1f} to {score_stats['max_score']:.1f} (avg: {score_stats['avg_score']:.1f})")
            
            # Context statistics
            if 'context_statistics' not in stats:
                raise ValueError("Summary statistics missing context_statistics field")
            context_stats = stats['context_statistics']
            if context_stats:
                if 'avg_context_size' not in context_stats:
                    raise ValueError(f"Context statistics missing avg_context_size field: {context_stats}")
                formatted.append(f"**Average context size**: {context_stats['avg_context_size']:.1f} decisions")
        else:
            # Calculate stats from filtered failures
            if not failures:
                return "No failures in selected time range."
            
            formatted = []
            
            # Temporal distribution
            times = [f.failure_time for f in failures]
            formatted.append(f"**Temporal spread**: {min(times):.3f}s to {max(times):.3f}s")
            
            # Score statistics 
            all_scores = []
            for f in failures:
                all_scores.extend(f.score_progression)
            if all_scores:
                formatted.append(f"**Score range**: {min(all_scores):.1f} to {max(all_scores):.1f} (avg: {sum(all_scores)/len(all_scores):.1f})")
            
            # Context statistics
            context_sizes = [len(f.context_decisions) for f in failures]
            if context_sizes:
                formatted.append(f"**Average context size**: {sum(context_sizes)/len(context_sizes):.1f} decisions")
        
        return "\n".join(formatted) if formatted else "No summary statistics available."
    
    def _format_recommendations(self) -> str:
        """Format current recommendations."""
        if not self.report.recommendations:
            return "No recommendations generated."
        
        formatted = []
        for i, rec in enumerate(self.report.recommendations, 1):
            formatted.append(f"{i}. {rec}")
        
        return "\n".join(formatted)
    
    def _get_failure_type_distribution(self) -> Dict[str, int]:
        """Get failure type distribution with validation."""
        if 'failure_type_distribution' not in self.report.summary_statistics:
            raise ValueError("Report summary statistics missing failure_type_distribution field")
        return self.report.summary_statistics['failure_type_distribution']
    
    def create_analysis_report(self, ai_insights: str, focus_context: Optional[FailureContext] = None) -> Dict[str, Any]:
        """
        Create a complete analysis report including AI insights.
        
        Args:
            ai_insights: AI-generated analysis text
            focus_context: The specific context that was analyzed, if any
            
        Returns:
            Complete analysis report
        """
        return {
            'metadata': {
                'test_case_id': self.report.test_case_id,
                'analysis_timestamp': get_timestamp(),
                'log_file': self.report.log_file,
                'focus_context_type': focus_context.failure_type if focus_context else 'general',
                'total_failures': self.report.total_failures
            },
            'failure_summary': {
                'total_failures': self.report.total_failures,
                'failure_types': self._get_failure_type_distribution(),
                'critical_failure': asdict(focus_context) if focus_context else None
            },
            'ai_analysis': {
                'prompt_type': 'focused' if focus_context else 'general',
                'insights': ai_insights,
                'generated_at': get_timestamp()
            },
            'original_recommendations': self.report.recommendations,
            'raw_failure_report': asdict(self.report)
        }
    
    def save_report(self, ai_insights: str, focus_context: Optional[FailureContext] = None, output_file: Optional[Path] = None) -> Path:
        """
        Save complete analysis report to file.
        
        Args:
            ai_insights: AI-generated analysis text
            focus_context: The specific context analyzed, if any
            output_file: Output file path, or None to auto-generate
            
        Returns:
            Path to saved report file
        """
        if output_file is None:
            output_file = REPORTS_DIR / get_report_filename(self.report.test_case_id)
        
        report = self.create_analysis_report(ai_insights, focus_context)
        save_json(report, output_file)
        
        logger.info(f"AI analysis report saved to: {output_file}")
        return output_file


def analyze_with_ai_prompt(input_file: Path, focused: bool = True, score_time: Optional[float] = None) -> Tuple[str, Optional[FailureContext]]:
    """
    Generate AI analysis prompt from log or failure report.
    
    Args:
        input_file: Path to log file or failure report
        focused: Whether to focus on most critical failure or do general analysis
        score_time: Focus on first failure after this score time (seconds)
        
    Returns:
        Tuple of (prompt_text, focus_context)
    """
    # Load or generate failure report
    if input_file.suffix == '.json' and 'failure' in input_file.name.lower():
        # Load existing failure report
        logger.info(f"Loading failure report: {input_file}")
        report_data = json.loads(input_file.read_text())
        report = FailureReport(**report_data)
    else:
        # Analyze log file to generate failure report
        logger.info(f"Analyzing input file: {input_file}")
        report = analyze_log_file(input_file)
    
    # Create AI analyzer
    analyzer = AIAnalyzer(report)
    
    # Determine focus context
    focus_context = None
    if focused and report.failure_contexts:
        # Filter by score time if specified
        candidate_failures = report.failure_contexts
        if score_time is not None:
            candidate_failures = [fc for fc in report.failure_contexts if fc.failure_time >= score_time]
            if not candidate_failures:
                raise ValueError(f"No failures found after score time {score_time:.3f}s - adjust score_time parameter")
            logger.info(f"Filtering to {len(candidate_failures)} failures after score time {score_time:.3f}s")
        
        # Get most critical failure (prioritize no_match failures)
        priority_order = ['no_match', 'wrong_match', 'score_drop']
        
        for failure_type in priority_order:
            failures_of_type = [fc for fc in candidate_failures if fc.failure_type == failure_type]
            if failures_of_type:
                # Return the first one (earliest in time)
                focus_context = min(failures_of_type, key=lambda fc: fc.failure_time)
                break
        
        if focus_context:
            if score_time is not None:
                logger.info(f"Focusing on {focus_context.failure_type} at {focus_context.failure_time:.3f}s (after score time {score_time:.3f}s)")
            else:
                logger.info(f"Focusing on {focus_context.failure_type} at {focus_context.failure_time:.3f}s")
        else:
            # No failure of priority types found - use earliest available failure
            if not candidate_failures:
                raise RuntimeError("Logic error: candidate_failures is empty after validation")
            focus_context = min(candidate_failures, key=lambda fc: fc.failure_time)
            logger.info(f"No priority failures found, focusing on earliest: {focus_context.failure_type} at {focus_context.failure_time:.3f}s")
    
    # Generate prompt
    prompt = analyzer.generate_analysis_prompt(focus_context)
    
    return prompt, focus_context


def main():
    """Main entry point for AI analysis."""
    parser = argparse.ArgumentParser(description="Generate AI analysis for score following failures")
    parser.add_argument("input_file", type=Path, help="Log file or failure report JSON")
    parser.add_argument("--general", action="store_true", help="Generate general analysis instead of focused")
    parser.add_argument("--score-time", type=float, help="Focus on first failure after this score time (seconds)")
    parser.add_argument("--output", "-o", type=Path, help="Output file for AI prompt")
    parser.add_argument("--insights", type=Path, help="File containing AI insights to incorporate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Generate prompt
        focused = not args.general
        prompt, focus_context = analyze_with_ai_prompt(args.input_file, focused=focused, score_time=args.score_time)
        
        # Save prompt if output specified
        if args.output:
            args.output.write_text(prompt, encoding='utf-8')
            logger.info(f"AI prompt saved to: {args.output}")
        else:
            print(prompt)
        
        # If insights provided, create complete report
        if args.insights and args.insights.exists():
            insights_text = args.insights.read_text(encoding='utf-8')
            
            # Load failure report for analyzer
            if args.input_file.suffix == '.json':
                report_data = json.loads(args.input_file.read_text())
                report = FailureReport(**report_data)
            else:
                report = analyze_log_file(args.input_file)
            
            # Create analyzer and save report
            analyzer = AIAnalyzer(report)
            report_file = analyzer.save_report(insights_text, focus_context)
            print(f"\nComplete analysis report saved to: {report_file}")
        
        # Print summary
        print(f"\nAI Analysis Prompt Summary:")
        print(f"Input: {args.input_file}")
        print(f"Type: {'Focused' if focused else 'General'}")
        if focus_context:
            print(f"Focus: {focus_context.failure_type} at {focus_context.failure_time:.3f}s")
        print(f"Prompt length: {len(prompt)} characters")
            
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())