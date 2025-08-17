# AI Debugger Quick Reference

## 🚀 Essential Commands

### Complete Analysis (One Command)
```bash
cd debug
python debug_workflow.py 1
```
*Runs test case 1, analyzes failures, generates AI prompt*

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
| `reports/report_N_*.json` | Complete analysis with AI insights |

## 🔍 Debug Log Format

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
| | `--timeout 15` | Custom timeout (default 10s) |
| | `--no-debug` | Disable debug logging |
| `failure_analyzer.py` | `--verbose` | Detailed failure analysis |
| `ai_analyzer.py` | `--general` | Analyze all failures |
| | `--focused` | Focus on critical failure |
| | `--insights file.txt` | Include AI insights |
| `debug_workflow.py` | `--skip-execution` | Use existing log |
| | `--ai-insights file.txt` | Include AI response |
| | `--verbose` | Detailed output |

## 🧠 AI Analysis Workflow

1. **Generate Prompt**
   ```bash
   python ai_analyzer.py logs/test_1_*.log > prompt.txt
   ```

2. **Send to Claude**
   - Copy `prompt.txt` content
   - Paste into Claude conversation
   - Save response as `insights.txt`

3. **Complete Analysis**
   ```bash
   python ai_analyzer.py logs/test_1_*.log --insights insights.txt
   ```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| No debug output | Check: `serpent64 run_bench 1 1 -d` works |
| Parse errors | Verify log format with `cat logs/test_1_*.log \| head` |
| No failures found | Algorithm working correctly or thresholds too high |
| Serpent not found | Add serpent64 to PATH |
| Test hangs | Process killed after timeout (expected) |

## 📊 Failure Types

| Type | Description | Common Causes |
|------|-------------|---------------|
| `no_match` | Note not matched to score | Timing constraints too strict |
| `wrong_match` | Match with low confidence | Wrong pitch/timing alignment |
| `score_drop` | Algorithm confidence falls | Parameter mismatch |

## ⚡ Quick Checks

```bash
# Test the system
python test_debug_system.py

# Check recent logs
ls -la logs/ | tail -5

# View failure summary
python failure_analyzer.py logs/test_1_*.log | grep "Total Failures"

# Quick log preview
cat logs/test_1_*.log | grep "DP|" | head -5
```

## 🎯 Common Use Cases

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

- **Focus on one failure** - Use `--focused` for specific issues
- **Include context** - Mention musical style, difficulty
- **Ask specific questions** - Parameter values, timing constraints
- **Request actionable fixes** - Code changes, parameter adjustments

## 🔄 Iterative Debugging

1. Run analysis → Get AI insights → Implement fixes → Repeat
2. Start with most critical failures
3. Test one parameter change at a time  
4. Document successful adjustments
5. Validate with multiple test cases