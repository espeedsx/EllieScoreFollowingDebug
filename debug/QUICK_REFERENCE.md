# Score Following Debug Quick Reference

## 🚀 Essential Commands

### Primary Workflow - One-Command Log and CSV Generation
```bash
cd debug/src
python debug.py 1
```
*Runs test case 1 and automatically generates both log and CSV files*

### Quick Options
```bash
cd debug/src
python debug.py 1 --quick           # Use existing log if available
python debug.py 1 --output my.csv   # Custom CSV output filename
python debug.py 1 --verbose         # Verbose output
```

### Manual Step-by-Step (Advanced)
```bash
# 1. Run test with debug logging (if needed)
cd debug/src
python run_debug_test.py 1

# 2. Convert specific log to CSV
python log_flattener.py ../logs/test_1_*.log

# 3. Files created:
# - logs/test_1_TIMESTAMP.log (raw debug log)
# - logs/test_1_TIMESTAMP.csv (flattened CSV)
```

## 📁 Output Files

| File Pattern | Description |
|--------------|-------------|
| `logs/test_N_TIMESTAMP.log` | Raw debug log with all DP decisions and explanations |
| `logs/test_N_TIMESTAMP.csv` | Flattened CSV with 90+ columns for analysis |

## 🔍 Debug Log Format

### Main Log Entries
*Automatically generated with debug flag, captures every algorithm decision*

```
INPUT|column:1|pitch:60|perf_time:0.5
DP|column:1|row:1|pitch:60|perf_time:0.5|vertical_rule:0|horizontal_rule:2|final_value:2|match:1|used_pitches:[60]|unused_count:0
MATCH|row:1|pitch:60|perf_time:0.5|score:2
MATCH_EXPLAIN|pitch:60|reason:FINAL DECISION (line 1733): Pitch 60 MATCHED at score row 1|score:2|timing:0.5|context:first_note|source_line:1733
```

### Key Log Types

| Type | Description | Key Fields |
|------|-------------|------------|
| `INPUT` | Performance note received | `column`, `pitch`, `perf_time` |
| `DP` | DP cell calculation | `column`, `row`, `pitch`, `vertical_rule`, `horizontal_rule`, `final_value`, `match` |
| `MATCH` | Successful match found | `row`, `pitch`, `perf_time`, `score` |
| `NO_MATCH` | No match found | `pitch`, `perf_time` |
| `MATCH_EXPLAIN` | Final match explanation | `pitch`, `reason`, `score`, `timing`, `source_line` |
| `NO_MATCH_EXPLAIN` | Final no-match explanation | `pitch`, `reason`, `constraint`, `timing`, `source_line` |

## 🛠 Command Options

| Command | Options | Purpose |
|---------|---------|---------|
| `debug.py` | `--quick` | Use existing log if available |
| | `--output file.csv` | Custom CSV output filename |
| | `--verbose` | Verbose output |
| `run_debug_test.py` | `--verbose` | Detailed execution output |
| | `--timeout 20` | Custom timeout (default 20s) |
| `log_flattener.py` | `--output file.csv` | Custom output filename |
| | `--verbose` | Show parsing progress |

## 📊 CSV Output Structure

The flattened CSV contains 90+ columns organized into sections:

### Key Columns for Analysis
| Column | Field | Description |
|--------|-------|-------------|
| 1-3 | `input_column`, `input_pitch`, `input_perf_time` | Performance note that triggered this calculation |
| 10 | `result_type` | "match", "no_match", or "unprocessed" |
| 11 | `match_explanation` | Human-readable match explanation (or "na") |
| 12 | `no_match_explanation` | Human-readable no-match explanation (or "na") |
| 23-29 | `cevent_*` | Expected score event details |
| 74-80 | `dp_*` | DP computation results |

### Features
- **Sorted pitch lists**: All pitch arrays sorted ascending (e.g., `[58,62,66,70,74,78,82]`)
- **"na" for empty fields**: Clean handling of missing explanations
- **Source line numbers**: Track decisions to source code lines
- **Complete context**: Every row has full algorithm state

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| No debug output | Check: `serpent64 run_bench 1 1 -d` works |
| Parse errors | Verify log format with `cat logs/test_1_*.log \| head` |
| Serpent not found | Add serpent64 to PATH |
| Test hangs | Process killed after timeout (expected) |
| CSV parsing fails | Check log file exists and has debug entries |
| Missing explanations | Ensure `-d` flag generates MATCH_EXPLAIN/NO_MATCH_EXPLAIN entries |

## ⚡ Quick Checks

```bash
# Check if test ran successfully
ls -la logs/ | tail -5

# Preview log entries
cat logs/test_1_*.log | grep "DP|" | head -5

# Check for explanation entries  
cat logs/test_1_*.log | grep "MATCH_EXPLAIN\|NO_MATCH_EXPLAIN" | head -3

# Count total entries
cat logs/test_1_*.log | wc -l

# Verify CSV was created
ls -la logs/*.csv | tail -3
```

## 🎯 Common Usage Examples

### Basic Log and CSV Generation
```bash
cd debug/src
python debug.py 1
```

### Multiple Test Cases
```bash
cd debug/src
for i in {1..5}; do
    python debug.py $i
done
```

### Using Existing Logs (Skip Test Execution)
```bash
cd debug/src
python debug.py 1 --quick
```

### Custom Output Location
```bash
cd debug/src
python debug.py 1 --output ../results/my_analysis.csv
```

### Manual Control (Advanced)
```bash
cd debug/src
python run_debug_test.py 1 --timeout 30
python log_flattener.py ../logs/test_1_*.log --output custom.csv
```

## 📈 Expected Output

### Log File Stats (per test case)
- **Total lines**: ~60,000+ 
- **DP entries**: ~5,000-10,000
- **Explanation entries**: ~300-800 (matches + no-matches)
- **File size**: ~5-15 MB

### CSV File Stats
- **Rows**: Same as DP entries (~5,000-10,000)
- **Columns**: 90+ (complete algorithm context)
- **Size**: ~2-5 MB
- **Processing time**: ~1-3 seconds