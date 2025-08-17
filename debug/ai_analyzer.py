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
        
    def generate_analysis_prompt(self, focus_context: Optional[FailureContext] = None) -> str:
        """
        Generate a focused AI analysis prompt.
        
        Args:
            focus_context: Specific failure context to focus on, or None for general analysis
            
        Returns:
            Detailed prompt for AI analysis
        """
        if focus_context:
            return self._generate_focused_prompt(focus_context)
        else:
            return self._generate_general_prompt()
    
    def _generate_focused_prompt(self, context: FailureContext) -> str:
        """Generate a prompt focused on a specific failure."""
        
        # Format context decisions for readability
        context_summary = self._format_context_decisions(context.context_decisions)
        timing_info = self._format_timing_analysis(context.timing_analysis)
        score_progression = self._format_score_progression(context.score_progression)
        
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

## Your Task
Analyze this failure and provide insights on:

1. **Root Cause**: What specific algorithm decision or parameter likely caused this failure?

2. **Decision Tree Analysis**: How did the sequence of decisions lead to the wrong outcome?

3. **Parameter Issues**: Which algorithm parameters (timing windows, scoring weights, penalties) might need adjustment?

4. **Timing Constraints**: Are the timing constraints too strict or too loose for this scenario?

5. **Alternative Strategies**: What alternative algorithmic approaches might handle this case better?

6. **Fix Recommendations**: Specific, actionable changes to prevent this type of failure.

Please be specific and reference the exact decision points and values shown in the context.
"""
        return prompt
    
    def _generate_general_prompt(self) -> str:
        """Generate a general analysis prompt for overall patterns."""
        
        # Get most critical failures for overview
        critical_failures = self.report.failure_contexts[:3]  # Top 3
        
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
        
        prompt = f"""# Score Following Algorithm Pattern Analysis

## Context
You are analyzing patterns of failures in a real-time score following algorithm. The algorithm uses dynamic programming to match musical performance against a score.

## Test Case Overview
- **Test Case ID**: {self.report.test_case_id}
- **Total Failures**: {self.report.total_failures}
- **Log File**: {Path(self.report.log_file).name}

## Failure Distribution
{self._format_failure_distribution()}

## Critical Failures
{''.join(failure_summaries)}

## Summary Statistics
{self._format_summary_statistics()}

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
            used_str = format_pitches(decision.get('used_pitches', []))
            formatted.append(
                f"Decision {i+1}: "
                f"Row {decision.get('row', '?')}, "
                f"Pitch {decision.get('pitch', '?')}, "
                f"Time {decision.get('time', 0):.3f}s\n"
                f"  - Vertical rule: {decision.get('vertical_rule', 0):.1f}\n"
                f"  - Horizontal rule: {decision.get('horizontal_rule', 0):.1f}\n"
                f"  - Final value: {decision.get('final_value', 0):.1f}\n"
                f"  - Match flag: {decision.get('match_flag', False)}\n"
                f"  - Used pitches: {used_str}\n"
                f"  - Unused count: {decision.get('unused_count', 0)}"
            )
        
        return "\n\n".join(formatted)
    
    def _format_timing_analysis(self, timing: Dict[str, Any]) -> str:
        """Format timing analysis for readability."""
        if not timing:
            return "No timing analysis available."
        
        analysis = []
        analysis.append(f"- Decision span: {timing.get('time_span', 0):.3f} seconds")
        analysis.append(f"- Average inter-onset interval: {timing.get('average_ioi', 0):.3f}s")
        analysis.append(f"- Maximum gap: {timing.get('max_gap', 0):.3f}s")
        analysis.append(f"- Time to failure: {timing.get('time_to_failure', 0):.3f}s")
        
        issues = timing.get('issues', [])
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
            formatted.append(
                f"Match {i+1}: "
                f"Pitch {match.get('pitch', '?')} at {match.get('time', 0):.3f}s, "
                f"Score {match.get('score', 0):.1f}"
            )
        
        return "\n".join(formatted)
    
    def _format_failure_distribution(self) -> str:
        """Format failure type distribution."""
        stats = self.report.summary_statistics
        dist = stats.get('failure_type_distribution', {})
        
        if not dist:
            return "No failure distribution data available."
        
        total = sum(dist.values())
        formatted = []
        for failure_type, count in dist.items():
            percentage = (count / total) * 100 if total > 0 else 0
            formatted.append(f"- {failure_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        return "\n".join(formatted)
    
    def _format_summary_statistics(self) -> str:
        """Format summary statistics."""
        stats = self.report.summary_statistics
        
        formatted = []
        
        # Temporal distribution
        temporal = stats.get('temporal_distribution', {})
        if temporal:
            formatted.append(f"**Temporal spread**: {temporal.get('first_failure', 0):.3f}s to {temporal.get('last_failure', 0):.3f}s")
        
        # Score statistics
        score_stats = stats.get('score_statistics', {})
        if score_stats:
            formatted.append(f"**Score range**: {score_stats.get('min_score', 0):.1f} to {score_stats.get('max_score', 0):.1f} (avg: {score_stats.get('avg_score', 0):.1f})")
        
        # Context statistics
        context_stats = stats.get('context_statistics', {})
        if context_stats:
            formatted.append(f"**Average context size**: {context_stats.get('avg_context_size', 0):.1f} decisions")
        
        return "\n".join(formatted) if formatted else "No summary statistics available."
    
    def _format_recommendations(self) -> str:
        """Format current recommendations."""
        if not self.report.recommendations:
            return "No recommendations generated."
        
        formatted = []
        for i, rec in enumerate(self.report.recommendations, 1):
            formatted.append(f"{i}. {rec}")
        
        return "\n".join(formatted)
    
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
                'failure_types': self.report.summary_statistics.get('failure_type_distribution', {}),
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
                logger.info(f"No failures found after score time {score_time:.3f}s")
                return "", None
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
            # Fallback to earliest failure
            focus_context = min(candidate_failures, key=lambda fc: fc.failure_time) if candidate_failures else None
            if focus_context:
                logger.info(f"Fallback: focusing on {focus_context.failure_type} at {focus_context.failure_time:.3f}s")
    
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