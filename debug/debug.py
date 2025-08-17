#!/usr/bin/env python3
"""
Simple launcher for the AI-powered score following debugger.
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_workflow import run_workflow
from utils import setup_logging, find_latest_log


def main():
    """Main launcher with simplified interface."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Score Following Debugger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug.py 1                    # Debug test case 1 (complete workflow)
  python debug.py 1 --quick           # Use existing log if available  
  python debug.py 1 --ai insights.txt # Include AI insights from file
  python debug.py --help-full         # Show detailed help

For complete documentation, see:
  - AI_USAGE_GUIDE.md (detailed usage instructions)
  - QUICK_REFERENCE.md (command reference)
  - EXAMPLE_WORKFLOW.md (step-by-step example)
        """
    )
    
    parser.add_argument("test_case", type=int, help="Test case ID to debug")
    parser.add_argument("--quick", action="store_true", 
                       help="Use existing log if available, otherwise run new test")
    parser.add_argument("--ai", type=Path, metavar="FILE",
                       help="File containing AI insights to integrate")
    parser.add_argument("--output", "-o", type=Path,
                       help="Save complete results to file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--help-full", action="store_true",
                       help="Show detailed help and exit")
    
    args = parser.parse_args()
    
    # Show detailed help
    if args.help_full:
        show_detailed_help()
        return 0
    
    # Setup logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger = setup_logging(__name__)
    
    try:
        print(f"🔍 AI-Powered Score Following Debugger")
        print(f"Analyzing test case {args.test_case}")
        print("-" * 50)
        
        # Check if we should skip execution
        skip_execution = False
        if args.quick:
            existing_log = find_latest_log(args.test_case)
            if existing_log:
                print(f"📁 Using existing log: {existing_log.name}")
                skip_execution = True
            else:
                print(f"⚠️  No existing log found, will run new test")
        
        # Load AI insights if provided
        ai_insights = None
        if args.ai and args.ai.exists():
            ai_insights = args.ai.read_text(encoding='utf-8')
            print(f"🧠 Including AI insights from: {args.ai}")
        
        # Run the workflow
        results = run_workflow(
            test_case_id=args.test_case,
            skip_execution=skip_execution,
            ai_insights=ai_insights
        )
        
        # Save results if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Results saved to: {args.output}")
        
        # Display summary
        display_summary(results)
        
        # Show next steps
        show_next_steps(results, args.test_case, bool(ai_insights))
        
        return 0 if results['workflow_metadata']['success'] else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


def display_summary(results):
    """Display workflow results summary."""
    metadata = results['workflow_metadata']
    summary = results.get('summary', {})
    
    print(f"\n📊 Results Summary:")
    print(f"Success: {'✅' if metadata['success'] else '❌'}")
    
    if not metadata['success']:
        print(f"Error: {metadata.get('error', 'Unknown error')}")
        return
    
    # Execution info
    if 'execution_duration' in summary:
        duration = summary['execution_duration']
        timeout = summary.get('execution_timeout', False)
        print(f"Execution: {duration:.1f}s {'(timeout)' if timeout else ''}")
    
    # Analysis info
    if 'dp_decisions' in summary:
        print(f"DP Decisions: {summary['dp_decisions']}")
        print(f"Matches Found: {summary['matches_found']}")
    
    # Failure info
    if 'total_failures' in summary:
        failures = summary['total_failures']
        print(f"Failures: {failures}")
        
        if failures > 0:
            failure_types = summary.get('failure_types', {})
            for ftype, count in failure_types.items():
                print(f"  - {ftype.replace('_', ' ')}: {count}")
    
    # AI status
    if summary.get('ai_prompt_ready'):
        if summary.get('ai_insights_included'):
            print(f"AI Analysis: ✅ Complete with insights")
        else:
            print(f"AI Analysis: 📝 Prompt ready")


def show_next_steps(results, test_case, has_insights):
    """Show recommended next steps."""
    print(f"\n🎯 Next Steps:")
    
    if not results['workflow_metadata']['success']:
        print("1. Check error messages and troubleshoot")
        print("2. Verify Serpent installation and test data")
        return
    
    summary = results.get('summary', {})
    failures = summary.get('total_failures', 0)
    
    if failures == 0:
        print("✅ No failures detected - algorithm is working well!")
        print("1. Try more challenging test cases")
        print("2. Validate with performance benchmarks")
        return
    
    if not has_insights:
        print("1. Get AI analysis:")
        print(f"   python ai_analyzer.py logs/test_{test_case}_*.log > prompt.txt")
        print("2. Send prompt.txt to Claude AI")
        print("3. Save response as insights.txt")
        print("4. Complete analysis:")
        print(f"   python debug.py {test_case} --ai insights.txt")
    else:
        print("1. Review AI recommendations in reports/")
        print("2. Implement suggested algorithm changes")
        print("3. Test improvements:")
        print(f"   python debug.py {test_case}")
        print("4. Compare before/after results")
    
    print(f"\n📚 Documentation:")
    print("- AI_USAGE_GUIDE.md (complete usage guide)")
    print("- QUICK_REFERENCE.md (command reference)")
    print("- EXAMPLE_WORKFLOW.md (step-by-step example)")


def show_detailed_help():
    """Show detailed help information."""
    print("""
🔍 AI-Powered Score Following Debugger - Detailed Help

OVERVIEW:
This tool helps debug score following algorithm failures using AI analysis.
It captures detailed algorithm decisions, identifies failure patterns, and 
generates AI prompts for systematic debugging.

WORKFLOW:
1. Capture: Run test with debug logging to capture DP decisions
2. Analyze: Parse logs and identify failure patterns  
3. Insights: Use AI to understand root causes and get fixes

BASIC USAGE:
  python debug.py 1                    # Complete analysis of test case 1
  python debug.py 1 --quick           # Use existing log if available
  python debug.py 1 --ai insights.txt # Include AI insights

DETAILED WORKFLOW:
1. Run: python debug.py 1
2. Copy generated AI prompt (or use: python ai_analyzer.py logs/test_1_*.log)
3. Send prompt to Claude AI
4. Save response as insights.txt  
5. Complete: python debug.py 1 --ai insights.txt

FILES CREATED:
- logs/test_N_*.log           # Debug log with DP decisions
- analysis/analysis_N_*.json  # Parsed structured data
- reports/report_N_*.json     # Complete analysis with AI insights

COMMON OPTIONS:
  --quick      Use existing log file if available
  --ai FILE    Include AI insights from file
  --output     Save results to JSON file
  --verbose    Show detailed execution info

TROUBLESHOOTING:
- No output: Check serpent64 installation and PATH
- Parse errors: Verify log format with cat logs/test_1_*.log
- No failures: Algorithm working correctly or try different test case
- Test hangs: Normal - process is killed after timeout

DOCUMENTATION:
- AI_USAGE_GUIDE.md: Complete usage instructions
- QUICK_REFERENCE.md: Command reference and troubleshooting  
- EXAMPLE_WORKFLOW.md: Step-by-step example walkthrough
- README.md: Technical implementation details

For more help: see documentation files or run with --verbose
    """)


if __name__ == "__main__":
    exit(main())