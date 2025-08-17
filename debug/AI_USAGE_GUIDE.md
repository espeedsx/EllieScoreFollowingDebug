# AI-Powered Score Following Debugger - Usage Guide

This guide explains how to use the AI-assisted debugging system to analyze score following failures and get actionable insights.

## Overview

The AI debugger works in three phases:
1. **Capture** - Instrument and run tests to capture DP decisions
2. **Analyze** - Parse logs and identify failure patterns  
3. **Insights** - Use AI to understand root causes and get fixes

## Phase 1: Capturing Debug Data

### Method 1: Complete Workflow (Recommended)

Run the complete analysis pipeline for any test case:

```bash
cd debug
python debug_workflow.py 1
```

This automatically:
- Runs test case 1 with debug logging
- Parses the debug log
- Analyzes failures
- Generates AI prompt
- Creates analysis files

### Method 2: Manual Execution

For more control over the process:

```bash
# Run test with debug logging (10 second timeout)
python run_debug_test.py 1 --verbose

# Check what was captured
ls logs/test_1_*.log
cat logs/test_1_*.log | head -20
```

### Troubleshooting Capture

If no debug output appears:
1. Check Serpent is working: `cd ../src && serpent64 run_bench --help`
2. Verify debug flag: `cd ../src && serpent64 run_bench 1 1 -d`
3. Check log file creation: `ls ../debug/logs/`

## Phase 2: Analyzing Failures

### Parse Debug Logs

```bash
# Parse log into structured format
python log_parser.py logs/test_1_20250116_143022.log

# View parsing summary
python log_parser.py logs/test_1_*.log --verbose
```

### Identify Failures

```bash
# Analyze failures and generate report
python failure_analyzer.py logs/test_1_*.log

# Detailed failure analysis
python failure_analyzer.py logs/test_1_*.log --verbose
```

### Understanding Failure Types

The system detects three types of failures:

1. **no_match**: Performance note not matched to any score event
2. **wrong_match**: Match found but with suspiciously low score  
3. **score_drop**: Significant decrease in algorithm confidence

Example output:
```
Failure Analysis Summary:
Input File: logs/test_1_20250116_143022.log
Test Case: 1
Total Failures: 3

Failure Types:
  no_match: 2
  wrong_match: 1

First Failure: 2.340s
Failure Type: no_match
Pitch: 60
```

## Phase 3: AI-Powered Analysis

### Generate AI Analysis Prompt

```bash
# Generate focused prompt for most critical failure
python ai_analyzer.py logs/test_1_*.log

# Generate general analysis prompt for all failures
python ai_analyzer.py logs/test_1_*.log --general
```

This creates a detailed prompt like:
```
# Score Following Algorithm Failure Analysis

## Failure Details
- Failure Type: no_match
- Time: 2.340 seconds
- Pitch: 60 (MIDI note number)
- Expected: Match for pitch 60 at time 2.340s
- Actual: No match found

## Decision Sequence Leading to Failure
Decision 1: Row 15, Pitch 60, Time 2.320s
  - Vertical rule: 8.0
  - Horizontal rule: 9.0
  - Final value: 9.0
  - Match flag: true
  - Used pitches: [60]
  - Unused count: 2

Decision 2: Row 16, Pitch 60, Time 2.340s
  - Vertical rule: 7.0
  - Horizontal rule: 5.0
  - Final value: 7.0
  - Match flag: false
  - Used pitches: []
  - Unused count: 3

## Your Task
Analyze this failure and provide insights on:
1. Root Cause: What specific algorithm decision caused this failure?
2. Parameter Issues: Which parameters might need adjustment?
3. Fix Recommendations: Specific changes to prevent this failure?
```

### Using the AI Prompt

#### Option A: Claude Web Interface

1. Copy the generated prompt
2. Paste into Claude conversation
3. Wait for analysis
4. Save the response to a text file

#### Option B: API Integration (if available)

```bash
# Save AI response to file
python ai_analyzer.py logs/test_1_*.log > ai_prompt.txt
# Send to Claude API and save response to ai_insights.txt
# Then integrate insights:
python debug_workflow.py 1 --ai-insights ai_insights.txt
```

### Example AI Analysis Response

After sending the prompt to Claude, you might get:

```
# AI Analysis of Score Following Failure

## Root Cause Analysis
The failure occurs because the timing constraint is too strict. The algorithm rejected a valid match for pitch 60 at time 2.340s because the Inter-Onset Interval (IOI) of 20ms exceeded the maximum allowed gap for chord grouping.

## Decision Tree Analysis
1. At time 2.320s: Algorithm successfully matched pitch 60 (score=9.0)
2. At time 2.340s: Same pitch appears again, but horizontal rule gave low score (5.0)
3. The low score suggests timing constraint violation in chord grouping logic

## Parameter Issues
- Chord grouping timing window appears too restrictive (current: ~100ms)
- The performance has a slight ritardando that the algorithm isn't handling well
- Default tolerance of 0.1s + time_span may be insufficient for expressive performance

## Fix Recommendations
1. Increase chord grouping tolerance from 0.1s to 0.2s
2. Add adaptive timing that considers recent IOI patterns
3. Implement grace period for repeated notes in trills/ornaments
4. Consider reducing penalty for timing violations vs. missing matches
```

### Integrating AI Insights

Once you have AI insights, complete the analysis:

```bash
# Create complete report with AI insights
python debug_workflow.py 1 --ai-insights ai_insights.txt

# Or add insights to existing analysis
python ai_analyzer.py logs/test_1_*.log --insights ai_insights.txt
```

This creates a comprehensive report in `reports/report_1_timestamp.json` containing:
- Original failure analysis
- AI insights and recommendations
- Actionable next steps

## Advanced Usage

### Analyzing Multiple Test Cases

```bash
# Analyze several test cases
for i in {1..5}; do
    echo "Analyzing test case $i"
    python debug_workflow.py $i --skip-execution
done
```

### Custom Analysis Focus

```bash
# Focus on specific failure type
python failure_analyzer.py logs/test_1_*.log | grep "no_match"

# Analyze timing patterns
python log_parser.py logs/test_1_*.log --verbose | grep "timing"

# Extract decisions around specific time
python -c "
from debug.log_parser import LogParser
from pathlib import Path
parser = LogParser(Path('logs/test_1_latest.log'))
result = parser.parse()
decisions = parser.get_decisions_around_time(2.340, window=0.5)
for d in decisions:
    print(f'Time {d.time}: Score {d.final_value}, Match {d.match_flag}')
"
```

### Comparing Algorithm Versions

```bash
# Run with different strategies
python debug_workflow.py 1 --output results_dynamic.json
# Edit src/run_bench.srp to change STRATEGY = 'static'
python debug_workflow.py 1 --output results_static.json

# Compare results
python -c "
import json
with open('results_dynamic.json') as f1, open('results_static.json') as f2:
    d1, d2 = json.load(f1), json.load(f2)
    print(f'Dynamic failures: {d1[\"summary\"][\"total_failures\"]}')
    print(f'Static failures: {d2[\"summary\"][\"total_failures\"]}')
"
```

## Workflow Examples

### Example 1: Debug Single Failure

```bash
# Step 1: Run with debugging
python debug_workflow.py 1

# Step 2: Check results
cat reports/report_1_*.json | jq '.failure_summary'

# Step 3: Get AI analysis prompt
python ai_analyzer.py logs/test_1_*.log > prompt.txt

# Step 4: Send to Claude, save response as insights.txt

# Step 5: Complete analysis
python ai_analyzer.py logs/test_1_*.log --insights insights.txt
```

### Example 2: Systematic Debugging Session

```bash
# Find failing test cases
python run_debug_test.py 1 2>&1 | tee execution.log

# Analyze the most problematic case
python failure_analyzer.py logs/test_1_*.log --verbose

# Focus on critical failure
python ai_analyzer.py logs/test_1_*.log --focused > critical_failure_prompt.txt

# After getting AI insights, implement fixes and re-test
# Edit algorithm parameters based on AI recommendations
python debug_workflow.py 1 --ai-insights insights.txt
```

### Example 3: Parameter Tuning Workflow

```bash
# Baseline analysis
python debug_workflow.py 1 --output baseline.json

# Edit algorithm parameters (e.g., timing windows, scoring weights)
# in src/score_follower_v18_trill.srp

# Test with new parameters
python debug_workflow.py 1 --output modified.json

# Compare results
python -c "
import json
with open('baseline.json') as f1, open('modified.json') as f2:
    b, m = json.load(f1), json.load(f2)
    print('Baseline failures:', b['summary']['total_failures'])
    print('Modified failures:', m['summary']['total_failures'])
    print('Improvement:', b['summary']['total_failures'] - m['summary']['total_failures'])
"
```

## Tips for Effective AI Analysis

### 1. Focus on Critical Failures First
- Use `--focused` mode for the most important failure
- Analyze patterns in multiple similar failures
- Prioritize no_match over score_drop failures

### 2. Provide Context in AI Prompts
- Include information about the musical piece
- Mention if it's a known difficult passage
- Add details about expected vs actual behavior

### 3. Iterate on Fixes
- Implement one AI recommendation at a time
- Re-run debug analysis after each change
- Build a library of successful parameter adjustments

### 4. Use Multiple Analysis Angles
- Compare different test cases
- Analyze both successful and failed matches
- Look for systematic patterns across failures

## Troubleshooting

### Common Issues

1. **No debug output**: Check LOG_DEBUG flag and DEBUG_LOG_FILE environment variable
2. **Parse errors**: Verify log format matches expected patterns
3. **No failures detected**: Algorithm may be working correctly, or thresholds too permissive
4. **AI prompt too long**: Use focused mode instead of general analysis

### Validation

```bash
# Verify debug system is working
python test_debug_system.py

# Check log format
python log_parser.py logs/test_1_*.log --verbose

# Validate failure detection
python failure_analyzer.py logs/test_1_*.log --verbose
```

## Next Steps

After getting AI insights:

1. **Implement Recommendations**: Modify algorithm parameters or logic
2. **Validate Changes**: Re-run tests to verify improvements
3. **Document Fixes**: Keep record of successful parameter adjustments
4. **Scale Testing**: Apply insights to broader test suite
5. **Iterative Improvement**: Use AI feedback to guide further refinements

The AI debugger is designed to make score following algorithm development more systematic and data-driven. Use it iteratively to build better understanding of how the algorithm behaves in different musical contexts.