# Score Following Debug System

This directory contains an AI-assisted debugging system for the score following algorithm. The system instruments the core dynamic programming algorithm to capture detailed decision logs and uses AI to analyze failures.

## Overview

The debug system consists of:

1. **Instrumented Serpent Code** - Captures DP decisions in compact format
2. **Python Analysis Tools** - Parse logs and identify failure patterns
3. **AI Analysis Engine** - Generate insights from failure contexts
4. **Workflow Orchestrator** - Coordinate the complete pipeline

## Quick Start

### 1. Run Complete Analysis Workflow

```bash
cd debug
python debug_workflow.py 1
```

This will:
- Execute test case 1 with debug logging
- Parse the debug log
- Analyze failures
- Generate AI analysis prompt

### 📚 **For Detailed Instructions, See:**
- **[AI_USAGE_GUIDE.md](AI_USAGE_GUIDE.md)** - Complete guide to using the AI debugger
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference and troubleshooting

### 2. Individual Components

```bash
# Run test with debug logging
python run_debug_test.py 1

# Parse existing log
python log_parser.py logs/test_1_*.log

# Analyze failures
python failure_analyzer.py logs/test_1_*.log

# Generate AI prompt
python ai_analyzer.py logs/test_1_*.log
```

### 3. Test the System

```bash
python test_debug_system.py
```

## Directory Structure

```
debug/
├── config.py           # Configuration and paths
├── utils.py            # Utility functions
├── run_debug_test.py   # Test execution with timeout
├── log_parser.py       # Parse compact debug logs
├── failure_analyzer.py # Failure detection and context
├── ai_analyzer.py      # AI prompt generation
├── debug_workflow.py   # Complete workflow orchestrator
├── test_debug_system.py # System test script
├── logs/               # Debug log files
├── analysis/           # Parsed analysis data  
└── reports/            # AI analysis reports
```

## Debug Log Format

The system uses a compact format optimized for AI analysis:

```
DP|c:N|r:R|p:P|t:T.T|vr:VR|hr:HR|f:F|m:M|u:[P1,P2]|uc:U
```

Where:
- `c:N` = column (performance note number)
- `r:R` = row (score event number)  
- `p:P` = pitch (MIDI note number)
- `t:T.T` = time (seconds)
- `vr:VR` = vertical rule value
- `hr:HR` = horizontal rule value
- `f:F` = final cell value
- `m:M` = match flag (1/0)
- `u:[P1,P2]` = used pitches list
- `uc:U` = unused count

## Serpent Code Changes

### Added to run_bench.srp:
- `LOG_DEBUG` flag (`-d` option)
- Environment variable `DEBUG_LOG_FILE` support

### Added to score_follower_v18_trill.srp:
- Debug logging functions
- Compact DP decision logging in `dynamic_match()`
- Match/no-match result logging
- Debug file initialization

## Workflow Steps

1. **Test Execution**: Run Serpent program with debug flag and timeout
2. **Log Parsing**: Convert compact logs to structured JSON
3. **Failure Analysis**: Identify mismatches and extract context
4. **AI Analysis**: Generate focused prompts for AI insights
5. **Report Generation**: Combine analysis into actionable reports

## Analysis Types

### Failure Detection
- **No Match**: Performance note not matched to any score event
- **Wrong Match**: Match with suspiciously low score
- **Score Drop**: Significant decrease in algorithm confidence

### Context Extraction
- N decisions before failure
- Timing analysis
- Score progression
- Preceding successful matches

### AI Insights
- Root cause analysis
- Parameter tuning recommendations
- Algorithm improvement suggestions

## Usage Examples

### Debug Single Test Case
```bash
python debug_workflow.py 1 --verbose
```

### Use Existing Log
```bash
python debug_workflow.py 1 --skip-execution
```

### Include AI Insights
```bash
# First run to get prompt
python debug_workflow.py 1 > ai_prompt.txt

# Get AI insights and save to file
# ... (copy prompt to Claude, save response) ...

# Complete analysis with insights
python debug_workflow.py 1 --ai-insights ai_insights.txt
```

### Analyze Specific Failure
```bash
python failure_analyzer.py logs/test_1_*.log --verbose
python ai_analyzer.py logs/test_1_*.log --focused
```

## Configuration

Edit `config.py` to customize:
- Timeout settings
- Log file naming
- Analysis parameters
- Debug format

## Troubleshooting

### Common Issues

1. **Serpent64 not found**: Ensure serpent64 is in PATH
2. **Test timeout**: Increase `TEST_TIMEOUT` in config.py
3. **No debug output**: Check LOG_DEBUG flag and DEBUG_LOG_FILE env var
4. **Parse errors**: Verify log format matches expected patterns

### Debug the Debugger

```bash
# Verbose logging
python debug_workflow.py 1 --verbose

# Check log contents
cat logs/test_1_*.log | grep "DP|"

# Validate parsing
python log_parser.py logs/test_1_*.log --verbose
```

## Integration with Main System

The debug system is designed to be:
- **Non-invasive**: Minimal impact when disabled
- **Storage-efficient**: Compact log format
- **AI-optimized**: Structured data for analysis
- **Modular**: Each component can be used independently

## Future Enhancements

- Real-time visualization of DP matrix
- Automated parameter optimization
- Integration with performance benchmarks
- Multi-test case pattern analysis