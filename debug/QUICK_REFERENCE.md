# AI Debugger Quick Reference

## 🚀 Essential Commands

### Complete Analysis (One Command)
```bash
cd debug
python debug_workflow.py 1
```
*Runs test case 1, analyzes failures, displays AI prompt ready to copy to Claude*

### Focus on Specific Time Range
```bash
cd debug
python debug_workflow.py 1 --score-time 20.5
```
*Focus on first mismatch after 20.5 seconds of score time*

### Manual Step-by-Step
```bash
# 1. Run test with debug logging
python run_debug_test.py 1

# 2. Parse and analyze failures  
python failure_analyzer.py logs/test_1_*.log

# 3. Generate AI prompt
python ai_analyzer.py logs/test_1_*.log > ai_prompt.txt

# 4. Send prompt to Claude, save response as insights.txt

# 5. Complete analysis with insights
python ai_analyzer.py logs/test_1_*.log --insights insights.txt
```

## 📁 Key Files

| File Pattern | Description |
|--------------|-------------|
| `logs/test_N_*.log` | Debug log with DP decisions |
| `analysis/analysis_N_*.json` | Parsed log data |
| `reports/report_N_*.md` | Complete analysis with AI insights |

## 🔍 Debug Log Format

### Ultra-Comprehensive Logging (New!)
*Activated with `-d` flag, captures every algorithm decision*

```
INPUT|c:1|p:60|t:0.5
MATRIX|c:1|ws:1|we:11|wc:1|cb:0|pb:0|cu:21|pu:21
CELL|r:1|v:0|u:[]|uc:0|t:-1
VRULE|r:1|up:0|pen:0|res:0|sp:nil
HRULE|r:1|pv:0|pit:60|ioi:1.5|lim:0.35|pass:t|typ:chord_matched|res:2
TIMING|pt:-1|ct:0.5|ioi:1.5|span:0|lim:0.35|pass:t|type:chord
MATCH_TYPE|pit:60|ch:t|tr:nil|gr:nil|ex:nil|ign:nil|used:nil|time:t|orn:chord_matched
DECISION|r:1|vr:0|hr:2|win:horizontal|upd:t|val:2|reason:chord_matched
ARRAY|r:1|center:2|vals:[-281474976710655,0,2,0,0]|pos:[-1, 0, 1, 2, 3]
SCORE|r:1|cur:2|top:0|beat:t|margin:2|conf:2000
ORNAMENT|pit:60|type:chord_matched|tr:[]|gr:[]|ig:[]|credit:2
```

### Log Entry Types

| Type | Description | Key Fields |
|------|-------------|------------|
| `INPUT` | Performance note received | `c`=column, `p`=pitch, `t`=time |
| `MATRIX` | DP matrix state | `ws`=window start, `we`=end, `wc`=center |
| `CELL` | Individual cell state | `r`=row, `v`=value, `u`=used pitches |
| `VRULE` | Vertical rule calculation | `up`=up value, `pen`=penalty, `res`=result |
| `HRULE` | Horizontal rule calculation | `pv`=prev value, `typ`=match type, `res`=result |
| `TIMING` | Timing constraint check | `pt`=prev time, `ct`=curr time, `pass`=result |
| `MATCH_TYPE` | Match classification | `ch`=chord, `tr`=trill, `gr`=grace, `ex`=extra |
| `DECISION` | Final cell decision | `vr`=vert result, `hr`=horiz result, `win`=winner |
| `ARRAY` | DP array neighborhood | `center`=cell value, `vals`=neighbors |
| `SCORE` | Score competition | `cur`=current, `top`=top score, `conf`=confidence |
| `ORNAMENT` | Ornament processing | `type`=ornament type, `credit`=score credit |

### Legacy Format (Still Supported)
```
DP|c:5|r:12|p:60|t:2.34|vr:8.0|hr:9.0|f:9.0|m:1|u:[60,64]|uc:1
```

| Field | Meaning |
|-------|---------|
| `c:5` | Performance note #5 |
| `r:12` | Score event #12 |
| `p:60` | MIDI pitch 60 (C4) |
| `t:2.34` | Time 2.34 seconds |
| `vr:8.0` | Vertical rule value |
| `hr:9.0` | Horizontal rule value |
| `f:9.0` | Final cell value |
| `m:1` | Match found (1) or not (0) |
| `u:[60,64]` | Used pitches |
| `uc:1` | Unused count |

## 🛠 Common Options

| Command | Options | Purpose |
|---------|---------|---------|
| `run_debug_test.py` | `--verbose` | Detailed execution output |
| | `--timeout 15` | Custom timeout (default 5s) |
| | `--no-debug` | Disable debug logging |
| `failure_analyzer.py` | `--verbose` | Detailed failure analysis |
| `ai_analyzer.py` | `--general` | Analyze all failures |
| | `--focused` | Focus on critical failure (prioritizes no_match) |
| | `--score-time N.N` | Focus on failures after score time |
| | `--insights file.txt` | Include AI insights |
| `debug_workflow.py` | `--skip-execution` | Use existing log |
| | `--score-time N.N` | Focus on failures after score time |
| | `--ai-insights file.txt` | Include AI response |
| | `--verbose` | Detailed output |

## 🧠 AI Analysis Workflow

1. **Run Complete Analysis**
   ```bash
   python debug_workflow.py 1
   ```
   *Displays AI prompt ready to copy*

2. **Send to Claude**
   - Copy prompt from console output (between the === lines)
   - Paste into Claude conversation
   - Save response as `insights.txt`

3. **Complete Analysis with Insights**
   ```bash
   python debug_workflow.py 1 --ai-insights insights.txt --skip-execution
   ```

### Manual Prompt Generation
```bash
# Generate and save prompt to prompt.txt (easiest)
python get_prompt.py 1 --score-time 25.0

# Or output directly to console  
python ai_analyzer.py logs/test_1_*.log --score-time 25.0
```

### Where is the AI Prompt?
- **Console output**: When running `debug_workflow.py` or `ai_analyzer.py`
- **Saved file**: Run `python get_prompt.py 1` → creates `prompt.txt`
- **In reports**: Stored in `reports/report_N_*.md` files

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| No debug output | Check: `serpent64 run_bench 1 1 -d` works |
| Parse errors | Verify log format with `cat logs/test_1_*.log \| head` |
| No failures found | Algorithm working correctly or thresholds too high |
| Serpent not found | Add serpent64 to PATH |
| Test hangs | Process killed after timeout (expected) |
| Ultra-comprehensive logs too large | Normal - expect 50K+ entries per test |
| Missing comprehensive logs | Ensure `-d` flag is used for ultra-detailed logging |

## 📊 Failure Types

| Type | Description | Common Causes | Priority |
|------|-------------|---------------|-----------|
| `no_match` | Note not matched to score | Timing constraints too strict | **High** |
| `wrong_match` | Match with low confidence | Wrong pitch/timing alignment | Medium |
| `score_drop` | Algorithm confidence falls | Parameter mismatch | Low |

## ⚡ Quick Checks

```bash
# Test the system
python test_debug_system.py

# Check recent logs
ls -la logs/ | tail -5

# View failure summary
python failure_analyzer.py logs/test_1_*.log | grep "Total Failures"

# Quick log preview (legacy format)
cat logs/test_1_*.log | grep "DP|" | head -5

# Ultra-comprehensive log preview (new format)
cat logs/test_1_*.log | grep -E "^(INPUT|DECISION|SCORE)" | head -10

# Count comprehensive log entries
cat logs/test_1_*.log | grep -E "^(INPUT|MATRIX|CELL|VRULE|HRULE|TIMING|MATCH_TYPE|DECISION|ARRAY|SCORE|ORNAMENT)" | wc -l
```

## 🎯 Common Use Cases

### Ultra-Comprehensive Algorithm Analysis (New!)
```bash
# Run with full algorithm logging
python run_debug_test.py 1

# Analyze specific algorithm components
cat logs/test_1_*.log | grep "TIMING" | head -10    # Timing constraints
cat logs/test_1_*.log | grep "DECISION" | head -10  # Cell decisions  
cat logs/test_1_*.log | grep "SCORE" | head -10     # Score competition

# Parse comprehensive logs
python log_parser.py logs/test_1_*.log --verbose
```

### Debug Single Failure
```bash
python debug_workflow.py 1 --verbose
# Send generated prompt to Claude
```

### Compare Algorithm Changes
```bash
# Before changes
python debug_workflow.py 1 --output before.json

# After changes  
python debug_workflow.py 1 --output after.json

# Compare
grep "total_failures" before.json after.json
```

### Batch Analysis
```bash
for i in {1..5}; do
    python debug_workflow.py $i --output results_$i.json
done
```

### Use Existing Logs
```bash
python debug_workflow.py 1 --skip-execution
```

## 📝 AI Prompt Tips

- **Focus on one failure** - Default behavior prioritizes unmatched notes (no_match)
- **Include context** - Mention musical style, difficulty
- **Ask specific questions** - Parameter values, timing constraints
- **Request actionable fixes** - Code changes, parameter adjustments
- **Copy from console** - Full prompt displayed after running debug_workflow.py

## 📈 Ultra-Comprehensive Logging Stats

### Expected Log Volume (per test case)
- **Total lines**: ~60,000+ 
- **Debug entries**: ~50,000+
- **Performance events**: ~300-800
- **DP decisions**: ~5,000-10,000
- **File size**: ~5-15 MB

### Performance Impact
- **Execution time**: +50-100% with `-d` flag
- **Storage**: Highly efficient compact format
- **Parsing**: ~1-3 seconds per log file
- **Memory**: Handles large logs efficiently

### Logging Control
- **No debug**: Standard execution, minimal logging
- **With `-d`**: Ultra-comprehensive algorithm logging
- **Legacy logs**: Still supported alongside new format
- **Existing levels**: LOG1, LOG2, LOG_ROGER preserved

## 🔄 Iterative Debugging

1. Run analysis → Get AI insights → Implement fixes → Repeat
2. Start with most critical failures
3. Test one parameter change at a time  
4. Document successful adjustments
5. Validate with multiple test cases