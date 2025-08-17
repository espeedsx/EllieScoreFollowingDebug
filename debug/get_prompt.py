#!/usr/bin/env python3
"""
Simple script to generate AI prompt and save to prompt.txt for easy copying.
"""

import sys
import argparse
from pathlib import Path
from ai_analyzer import analyze_with_ai_prompt
from utils import find_latest_log

def main():
    parser = argparse.ArgumentParser(description="Generate AI prompt and save to prompt.txt")
    parser.add_argument("test_case", type=int, nargs='?', default=1, help="Test case ID (default: 1)")
    parser.add_argument("--output", "-o", type=Path, default="prompt.txt", help="Output file (default: prompt.txt)")
    
    args = parser.parse_args()
    
    # Find latest log file for test case
    log_file = find_latest_log(args.test_case)
    if not log_file:
        print(f"No log file found for test case {args.test_case}")
        print("Run: python debug_workflow.py {args.test_case} first")
        return 1
    
    print(f"Using log file: {log_file}")
    
    # Generate prompt
    try:
        prompt, focus_context = analyze_with_ai_prompt(log_file, focused=True)
        
        # Save to file
        args.output.write_text(prompt, encoding='utf-8')
        
        print(f"AI prompt saved to: {args.output}")
        print(f"Focus: {focus_context.failure_type if focus_context else 'general'}")
        print(f"Length: {len(prompt)} characters")
        print(f"\nNext steps:")
        print(f"1. Copy {args.output} content to Claude")
        print(f"2. Save Claude's response as insights.txt")
        print(f"3. Run: python debug_workflow.py {args.test_case} --ai-insights insights.txt --skip-execution")
        
    except Exception as e:
        print(f"Error generating prompt: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())