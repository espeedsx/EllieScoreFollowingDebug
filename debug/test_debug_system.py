#!/usr/bin/env python3
"""
Test script for the complete debug system.
"""

import sys
from pathlib import Path

# Add debug directory to path
sys.path.insert(0, str(Path(__file__).parent))

from debug_workflow import run_workflow
from utils import setup_logging

def main():
    """Test the complete debug system with test case 1."""
    logger = setup_logging(__name__)
    
    print("Testing Score Following Debug System")
    print("="*50)
    
    try:
        # Run complete workflow for test case 1
        print("Running complete debug workflow for test case 1...")
        results = run_workflow(test_case_id=1, enable_debug=True)
        
        # Check if workflow succeeded
        if results['workflow_metadata']['success']:
            print("✓ Workflow completed successfully!")
            
            summary = results['summary']
            print(f"\nSummary:")
            print(f"- Test case: {summary.get('test_case_id', 'N/A')}")
            print(f"- Steps completed: {', '.join(summary.get('steps_completed', []))}")
            
            if 'execution_duration' in summary:
                print(f"- Execution duration: {summary['execution_duration']:.2f}s")
            
            if 'dp_decisions' in summary:
                print(f"- DP decisions logged: {summary['dp_decisions']}")
                print(f"- Matches found: {summary['matches_found']}")
            
            if 'total_failures' in summary:
                print(f"- Total failures detected: {summary['total_failures']}")
                if summary['total_failures'] > 0:
                    print(f"- Failure types: {summary['failure_types']}")
            
            if summary.get('ai_prompt_ready'):
                print("✓ AI analysis prompt is ready")
            
            print(f"\nNext steps:")
            print("1. Review the generated files in debug/logs/, debug/analysis/, debug/reports/")
            print("2. Use the AI analysis prompt with Claude to get insights")
            print("3. Run with AI insights to complete the analysis")
            
        else:
            print("✗ Workflow failed!")
            print(f"Error: {results['workflow_metadata'].get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"✗ Test failed: {e}")
        return 1
    
    print("\n" + "="*50)
    print("Debug system test completed!")
    return 0

if __name__ == "__main__":
    exit(main())