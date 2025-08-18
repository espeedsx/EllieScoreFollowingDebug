#!/usr/bin/env python3
"""
Simple launcher for score following debug log and CSV generation.
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_debug_test import TestExecutor
from log_flattener import LogFlattener
from utils import setup_logging, find_latest_log
import logging


def main():
    """Main launcher for log and CSV generation."""
    parser = argparse.ArgumentParser(
        description="Score Following Debug Log and CSV Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug.py 1                    # Generate log and CSV for test case 1
  python debug.py 1 --quick           # Use existing log if available  
  python debug.py 1 --output my.csv   # Custom CSV output filename

For complete documentation, see QUICK_REFERENCE.md
        """
    )
    
    parser.add_argument("test_case", type=int, help="Test case ID to debug")
    parser.add_argument("--quick", action="store_true", 
                       help="Use existing log if available, otherwise run new test")
    parser.add_argument("--output", "-o", type=Path,
                       help="Custom CSV output filename")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger = setup_logging(__name__)
    
    try:
        print("Score Following Debug Log and CSV Generator")
        print(f"Processing test case {args.test_case}")
        print("-" * 50)
        
        log_file = None
        
        # Check if we should use existing log
        if args.quick:
            existing_log = find_latest_log(args.test_case)
            if existing_log:
                print(f"Using existing log: {existing_log.name}")
                log_file = existing_log
            else:
                print("No existing log found, will run new test")
        
        # Run test to generate log if needed
        if log_file is None:
            print(f"Running test case {args.test_case} with debug logging...")
            executor = TestExecutor(test_case_id=args.test_case, enable_debug=True)
            result = executor.run_test()
            log_file = Path(result['log_file'])
            print(f"Debug log created: {log_file.name}")
        
        # Generate CSV from log
        print("Converting log to CSV...")
        flattener = LogFlattener()
        entries = flattener.parse_log_file(log_file)
        
        # Determine CSV output filename
        if args.output:
            csv_file = args.output
        else:
            csv_file = log_file.with_suffix('.csv')
        
        # Write CSV
        flattener.write_csv(entries, csv_file)
        print(f"CSV created: {csv_file.name}")
        
        # Display summary
        print(f"\nSummary:")
        print(f"Log file: {log_file}")
        print(f"CSV file: {csv_file}")
        print(f"Total entries: {len(entries):,}")
        
        # Check for explanations
        match_explanations = sum(1 for e in entries if e.match_explanation != 'na')
        no_match_explanations = sum(1 for e in entries if e.no_match_explanation != 'na')
        print(f"Match explanations: {match_explanations:,}")
        print(f"No-match explanations: {no_match_explanations:,}")
        
        print("\nLog and CSV generation complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())