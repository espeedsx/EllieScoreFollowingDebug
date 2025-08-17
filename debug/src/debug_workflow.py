#!/usr/bin/env python3
"""
Debug workflow orchestrator for score following system.
Coordinates the complete debug analysis pipeline.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from config import LOGS_DIR, ANALYSIS_DIR, REPORTS_DIR
from utils import setup_logging, find_latest_log, get_timestamp, format_duration, log_with_line
from run_debug_test import TestExecutor
from log_parser import parse_log_file
from failure_analyzer import analyze_log_file, FailureAnalyzer, FailureContext
from ai_analyzer import AIAnalyzer, analyze_with_ai_prompt
from log_flattener import LogFlattener
import logging


logger = setup_logging(__name__)


class DebugWorkflow:
    """Orchestrates the complete debug analysis workflow."""
    
    def __init__(self, test_case_id: int, enable_debug: bool = True):
        self.test_case_id = test_case_id
        self.enable_debug = enable_debug
        self.timestamp = get_timestamp()
        self.results = {}
        
    def run_complete_analysis(self, skip_execution: bool = False, ai_insights: Optional[str] = None, score_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Run the complete debug analysis workflow.
        
        Args:
            skip_execution: Skip test execution and use existing log
            ai_insights: Pre-generated AI insights to include in report
            score_time: Focus on first failure after this score time (seconds)
            
        Returns:
            Complete workflow results
        """
        log_with_line(logger, logging.INFO, f"Starting complete debug analysis for test case {self.test_case_id}")
        
        try:
            # Step 1: Execute test (or find existing log)
            if skip_execution:
                log_file = self._find_existing_log()
                if not log_file:
                    error_msg = f"No existing log found for test case {self.test_case_id}"
                    log_with_line(logger, logging.ERROR, error_msg)
                    raise FileNotFoundError(error_msg)
                log_with_line(logger, logging.INFO, f"Using existing log: {log_file}")
                self.results['execution'] = {'log_file': str(log_file), 'skipped': True}
            else:
                log_file = self._execute_test()
            
            # Step 2: Parse log
            parsed_data = self._parse_log(log_file)
            
            # Step 3: Analyze failures
            failure_report = self._analyze_failures(parsed_data)
            
            # Step 4: Generate AI analysis
            ai_report = self._generate_ai_analysis(failure_report, ai_insights, parsed_data, score_time)
            
            # Step 5: Create summary
            summary = self._create_summary()
            
            logger.info("Complete debug analysis finished successfully")
            return {
                'workflow_metadata': {
                    'test_case_id': self.test_case_id,
                    'timestamp': self.timestamp,
                    'success': True
                },
                'results': self.results,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                'workflow_metadata': {
                    'test_case_id': self.test_case_id,
                    'timestamp': self.timestamp,
                    'success': False,
                    'error': str(e)
                },
                'results': self.results,
                'summary': {'error': str(e)}
            }
    
    def _find_existing_log(self) -> Optional[Path]:
        """Find existing log file for test case."""
        return find_latest_log(self.test_case_id)
    
    def _execute_test(self) -> Path:
        """Execute test and return log file path."""
        log_with_line(logger, logging.INFO, "Step 1: Executing test with debug logging")
        
        executor = TestExecutor(self.test_case_id, self.enable_debug)
        execution_result = executor.run_test()
        
        self.results['execution'] = execution_result
        
        if not execution_result['success'] and not execution_result['timeout']:
            error_msg = f"Test execution failed with return code {execution_result['returncode']}"
            log_with_line(logger, logging.ERROR, error_msg, context=f"test_case={self.test_case_id}")
            raise RuntimeError(error_msg)
        
        log_file = Path(execution_result['log_file'])
        if not log_file.exists():
            error_msg = f"Log file not created: {log_file}"
            log_with_line(logger, logging.ERROR, error_msg, context=f"test_case={self.test_case_id}")
            raise FileNotFoundError(error_msg)
        
        log_with_line(logger, logging.INFO, f"Test executed successfully, log: {log_file}")
        return log_file
    
    def _parse_log(self, log_file: Path) -> Dict[str, Any]:
        """Parse log file into structured data."""
        log_with_line(logger, logging.INFO, "Step 2: Parsing debug log (smart mode - comprehensive data only around failures)")
        
        # Smart parsing: core data + comprehensive data only around failure points (±50 lines)
        parsed_data = parse_log_file(log_file, save_analysis=True, parse_comprehensive=False, failure_context_lines=50)
        
        # Validate analysis file was created
        if 'analysis_file' not in parsed_data['metadata']:
            error_msg = "Parsing metadata missing analysis_file - log parsing may have failed"
            log_with_line(logger, logging.ERROR, error_msg, context=f"log_file={log_file}")
            raise RuntimeError(error_msg)
        
        # Validate core metrics exist
        if 'metrics' not in parsed_data['metadata']:
            error_msg = "Parsing metadata missing metrics - log parsing failed"
            log_with_line(logger, logging.ERROR, error_msg, context=f"log_file={log_file}")
            raise RuntimeError(error_msg)
        
        metrics = parsed_data['metadata']['metrics']
        if metrics['dp_entries'] == 0:
            error_msg = "No DP entries found in log - parsing failed or empty test"
            log_with_line(logger, logging.ERROR, error_msg, context=f"log_file={log_file}, metrics={metrics}")
            raise RuntimeError(error_msg)
        
        self.results['parsing'] = {
            'log_file': str(log_file),
            'analysis_file': parsed_data['metadata']['analysis_file'],
            'metrics': metrics,
            'summary': parsed_data['summary']
        }
        
        # Generate flattened CSV for pattern analysis
        csv_file = self._generate_flattened_csv(log_file)
        if not csv_file.exists():
            error_msg = f"CSV file generation failed: {csv_file}"
            log_with_line(logger, logging.ERROR, error_msg, context=f"log_file={log_file}")
            raise RuntimeError(error_msg)
        
        self.results['parsing']['flattened_csv'] = str(csv_file)
        
        log_with_line(logger, logging.INFO, f"Log parsed: {metrics['dp_entries']} DP decisions")
        return parsed_data
    
    def _analyze_failures(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze failures in parsed data."""
        log_with_line(logger, logging.INFO, "Step 3: Analyzing failures")
        
        if 'comprehensive_data' not in parsed_data:
            error_msg = "Parsed data missing comprehensive_data key - parsing may have failed"
            log_with_line(logger, logging.ERROR, error_msg, context=f"parsed_keys={list(parsed_data.keys())}")
            raise RuntimeError(error_msg)
        
        if not parsed_data['comprehensive_data']:
            error_msg = "Parsed data has empty comprehensive_data - parsing may have failed"
            log_with_line(logger, logging.ERROR, error_msg, context=f"comprehensive_data_type={type(parsed_data['comprehensive_data'])}")
            raise RuntimeError(error_msg)
        
        analyzer = FailureAnalyzer(parsed_data)
        failure_report = analyzer.analyze()
        
        if not hasattr(failure_report, 'failure_contexts'):
            error_msg = "Failure analyzer returned invalid report - missing failure_contexts attribute"
            log_with_line(logger, logging.ERROR, error_msg, context=f"report_type={type(failure_report)}")
            raise RuntimeError(error_msg)
        
        # Handle successful test cases (no failures found)
        if not failure_report.failure_contexts:
            log_with_line(logger, logging.INFO, "No failures found - test case appears to be successful")
            self.results['failure_analysis'] = {
                'report': failure_report,
                'success_case': True,
                'failure_count': 0
            }
            # For successful cases, skip AI analysis and return early
            return self._create_success_summary()
        
        log_with_line(logger, logging.INFO, f"Found {len(failure_report.failure_contexts)} failure contexts for analysis")
        
        # Validate failure analysis results
        if not hasattr(failure_report, 'summary_statistics') or 'failure_type_distribution' not in failure_report.summary_statistics:
            error_msg = "Failure analysis missing failure_type_distribution - analysis may have failed"
            log_with_line(logger, logging.ERROR, error_msg, context=f"summary_stats={getattr(failure_report, 'summary_statistics', 'MISSING')}")
            raise RuntimeError(error_msg)
        
        most_critical = analyzer.get_most_critical_failure()
        
        self.results['failure_analysis'] = {
            'total_failures': failure_report.total_failures,
            'failure_types': failure_report.summary_statistics['failure_type_distribution'],
            'recommendations': failure_report.recommendations,
            'most_critical': most_critical
        }
        
        log_with_line(logger, logging.INFO, f"Found {failure_report.total_failures} failures")
        return failure_report
    
    def _generate_ai_analysis(self, failure_report: Dict[str, Any], ai_insights: Optional[str] = None, parsed_data: Optional[Dict[str, Any]] = None, score_time: Optional[float] = None) -> Dict[str, Any]:
        """Generate AI analysis prompt and report."""
        if score_time is not None:
            logger.info(f"Step 4: Generating AI analysis (focusing after score time {score_time:.3f}s)")
        else:
            logger.info("Step 4: Generating AI analysis")
        
        analyzer = AIAnalyzer(failure_report)
        
        # Get most critical failure from existing failure contexts (no redundant analysis)
        focus_context = self._get_most_critical_failure(failure_report.failure_contexts, score_time)
        
        # Validate comprehensive context exists
        if not focus_context.comprehensive_context:
            # For successful test cases, this might be normal - provide warning instead of hard failure
            log_with_line(logger, logging.WARNING, 
                         f"Focus context at {focus_context.failure_time:.3f}s lacks comprehensive data - may be normal for successful cases",
                         context=f"failure_type={focus_context.failure_type}, test_case={self.test_case_id}")
            
            # Create minimal AI analysis indicating lack of detailed data
            self.results['ai_analysis'] = {
                'prompt_generated': False,
                'insights_provided': ai_insights is not None,
                'focus_failure': f"{focus_context.failure_type} at {focus_context.failure_time:.3f}s",
                'message': 'Insufficient detailed context for AI analysis - test case may be successful'
            }
            return self.results['ai_analysis']
        
        # Validate comprehensive data is meaningful
        context_keys = list(focus_context.comprehensive_context.keys())
        expected_keys = ['timing_constraints', 'match_type_analysis', 'horizontal_rule_analysis', 
                        'cell_decisions', 'score_competition', 'ornament_context', 'algorithmic_insights']
        missing_keys = set(expected_keys) - set(context_keys)
        if missing_keys:
            raise RuntimeError(f"Comprehensive context missing expected keys: {missing_keys}")
        
        logger.info(f"Focus context has valid comprehensive data with all expected keys")
        
        # Prepare filtered failures for general analysis if needed
        filtered_failures = None
        if score_time is not None:
            filtered_failures = [fc for fc in failure_report.failure_contexts if fc.failure_time >= score_time]
            # Note: we already validated focus_context exists above, so this should have data
            if not filtered_failures:
                raise RuntimeError(f"Logic error: focus_context exists but no filtered failures found after {score_time:.3f}s")
            logger.info(f"Using {len(filtered_failures)} failures after score time {score_time:.3f}s")
        
        # Generate prompt
        prompt = analyzer.generate_analysis_prompt(focus_context, filtered_failures)
        
        # Create report (with or without AI insights)
        if ai_insights:
            report_file = analyzer.save_report(ai_insights, focus_context)
            logger.info(f"AI analysis report saved: {report_file}")
        else:
            # Save prompt and basic analysis even without AI insights
            prompt_report = analyzer.create_analysis_report("AI analysis pending - prompt generated", focus_context)
            prompt_report['ai_analysis']['prompt'] = prompt
            from config import REPORTS_DIR, get_report_filename
            from utils import save_json
            report_file = REPORTS_DIR / get_report_filename(self.test_case_id)
            save_json(prompt_report, report_file)
            logger.info(f"AI prompt and analysis saved: {report_file}")
        
        self.results['ai_analysis'] = {
            'prompt_generated': True,
            'prompt_length': len(prompt),
            'focus_context': focus_context.failure_type if focus_context else None,
            'insights_provided': ai_insights is not None,
            'report_file': str(report_file) if report_file else None,
            'prompt_preview': prompt[:200] + "..." if len(prompt) > 200 else prompt,
            'prompt': prompt  # Store full prompt for display
        }
        
        return {
            'prompt': prompt,
            'focus_context': focus_context,
            'report_file': report_file
        }
    
    def _create_summary(self) -> Dict[str, Any]:
        """Create workflow summary."""
        summary = {
            'test_case_id': self.test_case_id,
            'timestamp': self.timestamp,
            'steps_completed': list(self.results.keys()),
            'success': True
        }
        
        # Add key metrics
        if 'execution' in self.results:
            exec_res = self.results['execution']
            summary['execution_duration'] = exec_res.get('duration_seconds', 0)
            summary['execution_timeout'] = exec_res.get('timeout', False)
        
        if 'parsing' in self.results:
            parse_res = self.results['parsing']
            summary['dp_decisions'] = parse_res['metrics']['dp_entries']
            summary['matches_found'] = parse_res['metrics']['matches_found']
        
        if 'failure_analysis' in self.results:
            fail_res = self.results['failure_analysis']
            summary['total_failures'] = fail_res['total_failures']
            summary['failure_types'] = fail_res['failure_types']
            summary['has_critical_failure'] = fail_res['most_critical'] is not None
        
        if 'ai_analysis' in self.results:
            ai_res = self.results['ai_analysis']
            summary['ai_prompt_ready'] = ai_res['prompt_generated']
            summary['ai_insights_included'] = ai_res['insights_provided']
        
        return summary
    
    def _create_success_summary(self) -> Dict[str, Any]:
        """Create summary for successful test cases (no failures to analyze)."""
        logger.info("Creating success summary - test case completed without failures")
        
        return {
            'workflow_metadata': {
                'test_case_id': self.test_case_id,
                'timestamp': self.timestamp,
                'success': True,
                'result_type': 'success_case'
            },
            'results': self.results,
            'summary': {
                'test_case_id': self.test_case_id,
                'timestamp': self.timestamp,
                'steps_completed': list(self.results.keys()),
                'success': True,
                'result_type': 'success_case',
                'total_failures': 0,
                'execution_duration': self.results.get('execution', {}).get('duration_seconds', 0),
                'dp_decisions': self.results.get('parsing', {}).get('metrics', {}).get('dp_entries', 0),
                'matches_found': self.results.get('parsing', {}).get('metrics', {}).get('matches_found', 0),
                'message': 'Test case completed successfully - enhanced instrumentation data available in log and CSV files'
            }
        }
    
    def _generate_flattened_csv(self, log_file: Path) -> Path:
        """Generate flattened CSV from log file for pattern analysis."""
        logger.info("Generating flattened CSV for pattern analysis")
        
        csv_file = log_file.with_suffix('.csv')
        
        try:
            flattener = LogFlattener()
            entries = flattener.parse_log_file(log_file)
            
            if entries:
                flattener.write_csv(entries, csv_file)
                logger.info(f"Generated flattened CSV: {csv_file} ({len(entries)} entries)")
            else:
                logger.warning("No entries found for CSV generation")
                
            return csv_file
        except Exception as e:
            logger.error(f"Failed to generate flattened CSV: {e}")
            # Create empty CSV as fallback
            csv_file.touch()
            return csv_file

    def _get_most_critical_failure(self, failure_contexts: list, after_score_time: Optional[float] = None) -> FailureContext:
        """Get the most critical failure from existing failure contexts."""
        if not failure_contexts:
            raise ValueError("No failure contexts provided - cannot analyze without failures")
        
        # Filter by score time if specified
        candidate_failures = failure_contexts
        if after_score_time is not None:
            candidate_failures = [fc for fc in failure_contexts if fc.failure_time >= after_score_time]
            if not candidate_failures:
                raise ValueError(f"No failures found after score time {after_score_time:.3f}s - adjust score_time parameter")
            logger.info(f"Filtering to {len(candidate_failures)} failures after score time {after_score_time:.3f}s")
        
        # Focus primarily on no_match failures (unmatched notes)
        priority_order = ['no_match', 'wrong_match', 'score_drop']
        
        for failure_type in priority_order:
            failures_of_type = [fc for fc in candidate_failures if fc.failure_type == failure_type]
            if failures_of_type:
                # Return the first one (earliest in time)
                selected = min(failures_of_type, key=lambda fc: fc.failure_time)
                logger.info(f"Selected {failure_type} failure at {selected.failure_time:.3f}s, pitch {selected.failure_pitch}")
                return selected
        
        # Should never reach here if failure analysis is working correctly
        raise RuntimeError(f"No failures found with expected types {priority_order} - failure analysis may be broken")


def run_workflow(test_case_id: int, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to run complete workflow.
    
    Args:
        test_case_id: Test case to analyze
        **kwargs: Additional options for workflow
        
    Returns:
        Workflow results
    """
    workflow = DebugWorkflow(test_case_id, kwargs.get('enable_debug', True))
    return workflow.run_complete_analysis(
        skip_execution=kwargs.get('skip_execution', False),
        ai_insights=kwargs.get('ai_insights'),
        score_time=kwargs.get('score_time')
    )


def main():
    """Main entry point for debug workflow."""
    parser = argparse.ArgumentParser(description="Run complete score following debug workflow")
    parser.add_argument("test_case", type=int, help="Test case ID to analyze")
    parser.add_argument("--skip-execution", action="store_true", help="Skip test execution, use existing log")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug logging during execution")
    parser.add_argument("--ai-insights", type=Path, help="File containing AI insights to include")
    parser.add_argument("--score-time", type=float, help="Focus on first mismatch after this score time (seconds)")
    parser.add_argument("--output", "-o", type=Path, help="Output file for workflow results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load AI insights if provided
    ai_insights = None
    if args.ai_insights and args.ai_insights.exists():
        ai_insights = args.ai_insights.read_text(encoding='utf-8')
        logger.info(f"Loaded AI insights from: {args.ai_insights}")
    
    try:
        # Run workflow
        results = run_workflow(
            args.test_case,
            skip_execution=args.skip_execution,
            enable_debug=not args.no_debug,
            ai_insights=ai_insights,
            score_time=args.score_time
        )
        
        # Save results if output specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Workflow results saved to: {args.output}")
        
        # Print summary
        summary = results['summary']
        metadata = results['workflow_metadata']
        
        print(f"\nDebug Workflow Summary:")
        print(f"Test Case: {metadata['test_case_id']}")
        print(f"Success: {metadata['success']}")
        
        if metadata['success']:
            print(f"Steps Completed: {', '.join(summary['steps_completed'])}")
            
            if 'execution_duration' in summary:
                print(f"Execution Duration: {format_duration(summary['execution_duration'])}")
            
            if 'dp_decisions' in summary:
                print(f"DP Decisions: {summary['dp_decisions']}")
                print(f"Matches Found: {summary['matches_found']}")
            
            if 'total_failures' in summary:
                print(f"Total Failures: {summary['total_failures']}")
                if summary['total_failures'] > 0:
                    print(f"Failure Types: {summary['failure_types']}")
                    print(f"Critical Failure: {summary['has_critical_failure']}")
            
            if summary.get('ai_prompt_ready'):
                print(f"AI Analysis: Prompt ready")
                if summary.get('ai_insights_included'):
                    print("  - Insights included in report")
                else:
                    print("  - Ready for AI analysis")
            
            # Show AI prompt directly if no insights provided
            if not summary.get('ai_insights_included') and summary.get('total_failures', 0) > 0:
                ai_result = results['results'].get('ai_analysis', {})
                if 'prompt' in ai_result:
                    print(f"\n" + "="*80)
                    print(f"AI ANALYSIS PROMPT - COPY TO CLAUDE")
                    print(f"="*80)
                    print(ai_result['prompt'])
                    print(f"="*80)
                    print(f"END OF PROMPT")
                    print(f"="*80)
                    
                    print(f"\nNext Steps:")
                    print(f"1. Copy the prompt above to Claude")
                    print(f"2. Save Claude's response as insights.txt")
                    print(f"3. Re-run with --ai-insights insights.txt --skip-execution")
        else:
            print(f"Error: {metadata.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())