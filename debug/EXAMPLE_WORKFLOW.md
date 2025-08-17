# Example: Complete AI Debugging Workflow

This example walks through debugging test case 1 from start to finish.

## Step 1: Run the Debug Analysis

```bash
cd debug
python debug_workflow.py 1 --verbose
```

**Expected Output:**
```
Starting complete debug analysis for test case 1
Step 1: Executing test with debug logging
Test executed successfully, log: C:\Repos\EllieScoreFollowingDebug\debug\logs\test_1_20250116_143022.log
Step 2: Parsing debug log
Log parsed: 127 DP decisions
Step 3: Analyzing failures
Found 3 failures
Step 4: Generating AI analysis

Debug Workflow Summary:
Test Case: 1
Success: True
Steps Completed: execution, parsing, failure_analysis, ai_analysis
DP Decisions: 127
Matches Found: 15
Total Failures: 3
Failure Types: {'no_match': 2, 'wrong_match': 1}
AI Analysis: Prompt ready
```

## Step 2: Review Generated Files

Check what was created:

```bash
# View log file
ls logs/test_1_*
cat logs/test_1_*.log | head -10

# Check analysis
ls analysis/analysis_1_*
cat analysis/analysis_1_*.json | jq '.summary.match_statistics'

# Look at failure summary
python failure_analyzer.py logs/test_1_*.log
```

**Example Log Content:**
```
# Score Following Debug Log - Compact Format
DP|c:1|r:1|p:60|t:0.125|vr:0.0|hr:2.0|f:2.0|m:1|u:[60]|uc:2
DP|c:1|r:2|p:60|t:0.125|vr:-2.0|hr:0.0|f:0.0|m:0|u:[]|uc:3
DP|c:1|r:3|p:60|t:0.125|vr:-4.0|hr:0.0|f:0.0|m:0|u:[]|uc:1
MATCH|r:1|p:60|t:0.125|score:2.0
DP|c:2|r:2|p:64|t:0.250|vr:0.0|hr:2.0|f:2.0|m:1|u:[64]|uc:2
```

**Example Failure Analysis:**
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
Pitch: 67

Recommendations:
1. High rate of no-matches suggests timing constraints may be too strict
2. Large timing gaps detected - consider increasing tempo tolerance
```

## Step 3: Get AI Analysis Prompt

The workflow automatically generates an AI prompt. View it:

```bash
python ai_analyzer.py logs/test_1_*.log > ai_prompt.txt
cat ai_prompt.txt
```

**Example AI Prompt:**
```
# Score Following Algorithm Failure Analysis

## Context
You are analyzing a failure in a real-time score following algorithm...

## Failure Details
- Failure Type: no_match
- Time: 2.340 seconds
- Pitch: 67 (MIDI note number)
- Expected: Match for pitch 67 at time 2.340s
- Actual: No match found

## Decision Sequence Leading to Failure
Decision 1: Row 14, Pitch 67, Time 2.320s
  - Vertical rule: 6.0
  - Horizontal rule: 8.0
  - Final value: 8.0
  - Match flag: true
  - Used pitches: [60,64,67]
  - Unused count: 0

Decision 2: Row 15, Pitch 67, Time 2.340s
  - Vertical rule: 6.0
  - Horizontal rule: 4.0
  - Final value: 6.0
  - Match flag: false
  - Used pitches: []
  - Unused count: 3

## Score Progression
6.0 -> 8.0 -> 6.0
Trend: decreasing (from 6.0 to 6.0)

## Timing Analysis
- Decision span: 0.020 seconds
- Average inter-onset interval: 0.020s
- Maximum gap: 0.020s
- Time to failure: 0.000s

## Your Task
Analyze this failure and provide insights on:
1. Root Cause: What specific algorithm decision caused this failure?
2. Parameter Issues: Which parameters might need adjustment?
3. Fix Recommendations: Specific changes to prevent this failure?
```

## Step 4: Send to Claude AI

1. **Copy the prompt** from `ai_prompt.txt`
2. **Open Claude** (web interface or API)
3. **Paste the prompt** and send
4. **Save the response** to `ai_insights.txt`

**Example AI Response:**
```
# AI Analysis of Score Following Failure

## Root Cause Analysis
The failure occurs due to overly restrictive timing constraints in the horizontal rule. The algorithm successfully matched pitch 67 at time 2.320s (score 8.0), but when the same pitch appears 20ms later at 2.340s, the horizontal rule score drops to 4.0, indicating a timing constraint violation.

## Decision Tree Analysis
1. At 2.320s: Successful match (score 8.0) - all chord notes matched
2. At 2.340s: Same pitch attempted again but rejected due to timing
3. The algorithm interprets this as a new performance event rather than part of the same chord

## Parameter Issues
1. **Chord grouping window too small**: Current timing tolerance appears insufficient for this performance style
2. **Repeated note penalty**: Algorithm may be penalizing rapid repetition of the same pitch
3. **IOI constraints**: 20ms interval exceeds allowable chord grouping threshold

## Timing Constraints Analysis
- The 20ms gap suggests this could be a trill or ornament
- Current algorithm doesn't recognize this as ornamental figure
- Timing window of ~0.1s + time_span may be too restrictive

## Fix Recommendations
1. **Increase chord grouping tolerance** from 0.1s to 0.2s in the horizontal rule
2. **Add trill detection** for rapid alternating or repeated notes
3. **Implement adaptive timing** that considers recent IOI patterns
4. **Adjust penalty weights**: Reduce cost of extra notes vs missing matches
5. **Add ornament preprocessing** to group rapid note sequences

## Specific Code Changes
In `score_follower_v18_trill.srp`, line ~1318:
- Change: `time - prev.time < cur_cevt.time_span + 0.1`
- To: `time - prev.time < cur_cevt.time_span + 0.2`

Additionally, consider adding rapid note detection before the timing check.
```

## Step 5: Complete Analysis with AI Insights

```bash
# Save AI response to file (ai_insights.txt)
# Then integrate it:
python ai_analyzer.py logs/test_1_*.log --insights ai_insights.txt
```

**Output:**
```
AI analysis report saved to: C:\Repos\EllieScoreFollowingDebug\debug\reports\report_1_20250116_143456.json
```

## Step 6: Review Complete Report

```bash
cat reports/report_1_*.json | jq '.ai_analysis.insights' | head -20
```

The complete report contains:
- Original failure analysis
- AI insights and recommendations  
- Actionable fix suggestions
- Code change locations

## Step 7: Implement Fixes

Based on AI recommendations, edit the algorithm:

```bash
# Edit the score follower
nano ../src/score_follower_v18_trill.srp

# Find line ~1318 and increase timing tolerance
# Change: time - prev.time < cur_cevt.time_span + 0.1
# To:     time - prev.time < cur_cevt.time_span + 0.2
```

## Step 8: Validate Changes

```bash
# Test with modified algorithm
python debug_workflow.py 1 --output after_fix.json

# Compare results
python -c "
import json
with open('after_fix.json') as f:
    data = json.load(f)
    print(f'Failures after fix: {data[\"summary\"][\"total_failures\"]}')
"
```

**Expected Improvement:**
```
Failures after fix: 1
(Reduced from 3 to 1)
```

## Step 9: Document and Iterate

1. **Document the fix** in your notes
2. **Test multiple cases** to ensure the fix generalizes
3. **Run more complex tests** to validate robustness
4. **Iterate** on remaining failures

## Summary

This workflow demonstrates:
- ✅ **Systematic debugging** - Captured exact decision sequence
- ✅ **AI-powered analysis** - Got specific root cause and fixes  
- ✅ **Actionable results** - Concrete code changes to implement
- ✅ **Validation** - Measured improvement after changes

The AI debugger transforms trial-and-error debugging into a systematic, data-driven process for improving the score following algorithm.