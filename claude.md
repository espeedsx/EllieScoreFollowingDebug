DO NOT RUN THE ACTUAL SERPENT TESTS. THESE TESTS GENERATE HUGE LOG FILES AND EASILY EXHAUST ALL TOKENS. DO NOT RUN THE ACTUAL SERPENT TESTS. I DON'T HAVE A LOT OF TOKENS.

DO NOT ADD QUESTIONABLE FALLBACKS. IF SOMETHING IS NOT EXPECTED, THROW EXCEPTION AND FAIL EARLY AND FAIL FAST. DO NOT USE QUESTIONABLE FALLBACKS TO HIDE BUGS THAT ARE MUCH HARDER TO IDENTIFY. REMOVE ALL QUESTIONABLE FALLBACKS. 

USE LOG_WITH_LINE() INSTEAD OF LOG()

# EllieScoreFollowing Project Context

## Project Overview

This repository implements score following algorithms for musical performance evaluation, particularly focused on the **Accomplice** system. Score following is the task of automatically tracking a musical performance in real-time by matching it against a known musical score.

### Key Features
- Dynamic programming-based score following algorithm
- Support for musical ornaments (trills, grace notes)
- Benchmarking infrastructure using the ASAP dataset
- Multiple algorithm versions and strategies
- Comprehensive evaluation and analysis tools
- **🆕 AI-Powered Debugging System** - Systematic failure analysis with AI insights

## Repository Structure

```
├── src/                          # Core implementation
│   ├── score_follower_v18_trill.srp # Trill-enhanced version
│   ├── trillfinder.srp           # Trill detection module
│   ├── labels.srp                # Annotation handling
│   ├── run_bench.srp             # Benchmark runner
│   ├── test_common.srp           # Shared test utilities
│   ├── init.srp                  # Initialization
│   ├── epsilon.srp               # Epsilon calculations
│   └── extra/                    # Supporting modules
│       ├── allegro.srp           # MIDI file handling
│       ├── readcsv.srp           # CSV reading
│       └── strparse.srp          # String parsing
├── tests/                        # Test data and results
├── sfhints/                      # Hint/label files by composer
├── EllieTrillReview/            # Trill analysis tools (Python)
├── debug/                        # 🆕 AI-powered debugging system
│   ├── debug.py                  # Simple launcher
│   ├── debug_workflow.py         # Complete analysis pipeline
│   ├── AI_USAGE_GUIDE.md         # How to use AI debugger
│   ├── QUICK_REFERENCE.md        # Command reference
│   └── EXAMPLE_WORKFLOW.md       # Step-by-step example
└── doc/                         # Documentation
```

---

# Serpent Language Quick Reference

Serpent is a Python-inspired language for real-time systems with dynamic typing, real-time GC, and OOP support.

## Core Types & Syntax
- **Types**: Integer, Real, String, Symbol, Array `[1,2,3]`, Dictionary `{'key': value}`, Object
- **Values**: `nil` (false), `t` (true), `'symbol'` (symbol), `"string"` (string)  
- **Structure**: Python-like indentation (4 spaces), `//` comments, `;` for same-line statements

## Control Flow
```serpent
if condition: ...                         // Conditionals
elif other: ... else: ...

while condition: ...                      // Loops
for i = 0 to 10 by 2: ...                // Range loop
for item at index in array: ...          // Array iteration

def func(required, optional opt = 5): ... // Functions
    var local = value                     // Local variables
    return result

class MyClass(Super):                     // Classes  
    var instance_var
    def init(param): instance_var = param
    def method(): return super.method()
```

## Essential Built-ins
```serpent
// Strings: len(s), find(s, pattern), toupper/tolower(s), chr(65), ord("A")
// Arrays: len(a), append(a, x), last(a), subseq(a, start, end), sort(a)
// Dicts: keys(d), get(d, key, default), has_key(d, key)
// Files: open(file, mode), readlines(f), close(f)
// Debug: error("msg"), display "label", vars, require "debug", breakpoint(1)
// Math: abs, sin, cos, exp, log, sqrt, int, real, max, min, random
```

## Threading & Preprocessing
```serpent
thread_ref = fork()                       // Threading
if thread_ref == nil: // child thread

#ifdef SYMBOL: ...                        // Conditional compilation
#noop debug_func                          // Disable function calls
```

---

# Score Following Implementation

## Core Modules

### score_follower_v18_trill.srp  
Main implementation of the score following algorithm using dynamic programming with specialized trill handling and musical ornament detection. Key classes:
- `Cevent`: Compound events representing groups of simultaneous notes
- `Cell`: Dynamic programming matrix cells with alignment costs
- Support for both static and dynamic alignment strategies

### trillfinder.srp
Dedicated module for identifying and processing musical trills, grace notes, and other ornaments that can complicate score following.

### labels.srp
Handles creation and management of annotation files that mark specific musical events, alignment points, and problem areas in the score following process.

### run_bench.srp
Benchmark execution framework that:
- Reads test cases from ASAP dataset metadata
- Runs score following on MIDI score/performance pairs  
- Outputs detailed results to CSV files
- Generates error histograms and gap analysis

## Score Following Domain Concepts

### Compound Events (Cevent)
```serpent
class Cevent:
    var time       // score time of first note
    var pitches    // set of pitches in compound event
    var time_span  // difference between first and last onset times
```

### Dynamic Programming Matrix
- Used for sequence alignment between score and performance
- Cells contain alignment costs and timing information
- Supports both static and dynamic strategies

### Common Patterns in Score Following Code

#### Logging Levels
```serpent
LOG_ROGER = false
LOG1 = false  
LOG2 = false
LOG3 = false
```

#### File Path Handling
```serpent
def score_path_to_labels_path(path):
    // Convert score MIDI path to hints/labels path
```

#### MIDI Processing
```serpent
require "allegro"  // MIDI file reading
require "mfread"   // Additional MIDI utilities
```

#### CSV Data Handling
```serpent
require "readcsv"
require "writecsv"
```

## Configuration and Usage

### Algorithm Selection
In `run_bench.srp`, choose between:
```serpent
require "score_follower_v18_trill"  // Main score follower with trill handling
```

### Strategy Selection
```serpent
STRATEGY = 'dynamic'  // or 'static'
```

### Logging Levels
```serpent
LOG_ROGER = false  // Roger's debugging output
LOG1 = false       // Level 1 debug info
LOG2 = false       // Level 2 debug info  
LOG3 = false       // Level 3 debug info
```

## Running Tests

### Single Test
```bash
serpent64 run_bench.srp STARTNO
```
Where STARTNO is the test ID (line number in metadata.csv)

### Batch Tests
```bash
serpent64 run_bench.srp STARTNO ENDNO
```

### Custom Test
```bash
serpent64 run_test.srp MIDI_SCORE MIDI_PERF
```

## Data Flow

1. **Input**: MIDI score and performance files
2. **Preprocessing**: Convert to internal event representation (Cevent objects)
3. **Trill Detection**: Identify ornaments that may affect alignment
4. **Score Following**: Dynamic programming alignment algorithm
5. **Post-processing**: Generate hints/labels for problem areas
6. **Output**: Alignment results, error analysis, CSV reports

## Key Algorithms

### Dynamic Programming Matrix
The core alignment uses a dynamic programming approach similar to sequence alignment:
- Rows represent score events
- Columns represent performance events  
- Cells contain alignment costs and timing information
- Supports insertion, deletion, and substitution operations

### Trill Handling
Special processing for musical ornaments:
- Detection of rapid alternating notes
- Grouping of grace note clusters
- Adjustment of timing expectations during ornaments

### Epsilon Calculation
Adaptive timing window calculation based on performance characteristics to handle tempo variations and timing irregularities.

## Output and Analysis

### Benchmark Results (`tests/bench_result.csv`)
- `note_count`: Number of performed notes
- `matched_count`: Number of confident matches found
- `matched_pct`: Percentage of notes successfully matched
- Composer, title, and file information

### Error Analysis
- Alignment error histograms
- Gap analysis between matches
- Large error identification and reporting
- Timing deviation statistics

### Hint/Label Files (`sfhints/`)
Generated annotation files marking:
- Trill locations and characteristics
- Large timing errors
- Unmatched note regions
- Suggested algorithm parameter adjustments

## Development Guidelines

### Code Style
- Follow Serpent conventions (see Serpent Language Reference above)
- Use descriptive variable names
- Comment algorithm sections thoroughly
- Maintain consistent indentation (4 spaces)

### Testing
- Use ASAP dataset for standardized evaluation
- Generate comprehensive error analysis
- Compare different algorithm versions and strategies
- Document parameter sensitivity

### Debugging
- Use `require "debug"` for interactive debugging
- Leverage built-in `display` statements for value inspection
- Use logging levels to control output verbosity
- Profile with `gc_cycles()` for performance analysis

## Dependencies

### Required Serpent Modules
- `allegro` - MIDI file reading/writing
- `debug` - Interactive debugging support
- `readcsv`/`writecsv` - CSV file handling
- `mfread` - Additional MIDI utilities
- `cmdline` - Command line argument parsing

### External Data
- **ASAP Dataset**: Large collection of classical music MIDI scores and performances
- Located at: `../../asap-dataset-master/`
- Metadata file: `metadata.csv` with test case information

## Research Context

This implementation is based on the foundational work:
- Dannenberg & Bloch ICMC '85 paper on score following
- Extended with modern trill handling techniques
- Evaluated against comprehensive classical music dataset
- Designed for real-time interactive music systems

---

# 🧠 AI-Powered Debugging System

## Overview

The `debug/` directory contains a comprehensive AI-assisted debugging system that instruments the score following algorithm to capture detailed decision logs and uses AI to analyze failures systematically.

## Key Features

- **Compact Logging**: Captures every dynamic programming decision in storage-efficient format
- **Failure Detection**: Automatically identifies no-matches, wrong matches, and score drops
- **Context Extraction**: Gets decision sequences leading to failures for analysis
- **AI Analysis**: Generates focused prompts for AI-powered root cause analysis
- **Cost Optimized**: Selective analysis minimizes AI token usage

## Quick Start

```bash
# Complete AI-powered analysis of test case 1
cd debug
python debug.py 1

# Follow the AI analysis workflow:
# 1. Copy generated prompt to Claude AI
# 2. Save AI response as insights.txt  
# 3. Complete analysis: python debug.py 1 --ai insights.txt
```

## System Components

### Core Tools
- `debug.py` - Simple launcher with unified interface
- `debug_workflow.py` - Complete analysis pipeline orchestrator
- `run_debug_test.py` - Test execution with timeout and logging
- `log_parser.py` - Parse compact debug logs into structured data
- `failure_analyzer.py` - Detect failures and extract context
- `ai_analyzer.py` - Generate AI prompts and integrate insights

### Documentation
- `AI_USAGE_GUIDE.md` - Complete guide to using the AI debugger
- `QUICK_REFERENCE.md` - Command reference and troubleshooting
- `EXAMPLE_WORKFLOW.md` - Step-by-step walkthrough with examples
- `README.md` - Technical implementation details

## Debug Log Format

The system uses a compact format optimized for AI analysis:

```
DP|c:N|r:R|p:P|t:T|vr:VR|hr:HR|f:F|m:M|u:[P1,P2]|uc:U
```

Where:
- `c:N` = column (performance note number)
- `r:R` = row (score event number)
- `p:P` = pitch (MIDI note number)
- `t:T` = time (seconds)
- `vr:VR` = vertical rule value
- `hr:HR` = horizontal rule value  
- `f:F` = final cell value
- `m:M` = match flag (1/0)
- `u:[P1,P2]` = used pitches list
- `uc:U` = unused count

## Workflow Process

1. **Instrument & Capture**: Run test with `-d` flag to log DP decisions
2. **Parse & Analyze**: Convert logs to structured data and identify failures
3. **AI Analysis**: Generate focused prompts for specific failure contexts
4. **Get Insights**: Send prompts to Claude AI for root cause analysis
5. **Implement Fixes**: Apply AI recommendations and validate improvements

## Usage Examples

### Basic Debugging
```bash
python debug.py 1                    # Debug test case 1
python debug.py 1 --quick           # Use existing log if available
python debug.py 1 --ai insights.txt # Include AI insights
```

### Manual Control
```bash
python run_debug_test.py 1          # Just run test with logging
python failure_analyzer.py logs/test_1_*.log  # Analyze failures
python ai_analyzer.py logs/test_1_*.log > prompt.txt  # Generate AI prompt
```

### Comparison Analysis
```bash
# Before algorithm changes
python debug.py 1 --output before.json

# After changes  
python debug.py 1 --output after.json

# Compare results
grep "total_failures" before.json after.json
```

## AI Analysis Benefits

- **Systematic**: Data-driven rather than trial-and-error debugging
- **Focused**: Analyzes specific failure contexts, not entire logs
- **Cost-Efficient**: Compact format minimizes AI token usage
- **Actionable**: Provides specific parameter adjustments and code changes
- **Iterative**: Enables continuous improvement through AI feedback

## Integration with Main System

The debug system is designed to be:
- **Non-Invasive**: Zero impact when LOG_DEBUG is disabled
- **Modular**: Each component can be used independently
- **Storage-Efficient**: Compact logging optimized for analysis
- **AI-Optimized**: Structured data format designed for LLM consumption

See the documentation files in `debug/` for complete usage instructions and examples.

---

# Essential Serpent Patterns for Score Following

## Basic Operations
```serpent
// Arrays: [1, 2, 3], a.append(x), a.last(), subseq(a, start, end)
// Dictionaries: {'key': value}, d.get('key', default), d.keys()
// Strings: toupper(s), find(s, pattern), chr(65) -> "A", ord("A") -> 65

// Loops
for i = 0 to len(array): ...           // Range
for item in array: ...                 // Elements  
for item at index in array: ...        // Elements + index

// Functions with parameters
def func(required, optional opt = 5, keyword kw = "default", rest args): ...
```

## Classes and Error Handling
```serpent
class MyClass(SuperClass):
    var instance_var
    def init(param): instance_var = param
    def method(): return super.method()

// Error handling
if not expected_condition: error("Message")
require "debug"; breakpoint(1)  // Debug on first call
display "label", var1, var2    // Debug output
```

## Score Following Specific Patterns
```serpent
// Module setup
require "allegro"; require "score_follower_v18_trill"
LOG_ROGER = false; LOG1 = false; STRATEGY = 'dynamic'

// MIDI processing
var seq = allegro_smf_read(file_path)
seq.convert_to_beats()
for event in track:
    if isinstance(event, Alg_note): process_note(event.key, event.time)

// File I/O
var f = open(filename, "r")
if f: var lines = f.readlines(); f.close()
else: error("Could not open " + filename)

// CSV parsing with strparse
require "strparse"
var parser = String_parse(line)
var field = parser.get_nonspace()
```

---

# Score Following Algorithm Details

## Core DP Algorithm (Dannenberg, 1985)
**Goal**: Find longest common subsequence between performance and score streams using dynamic programming matrix (rows=score, columns=performance).

```pseudocode
// Core DP recurrence
bestlength[r, c] = max(
    bestlength[r-1, c],           // Skip score event  
    bestlength[r, c-1],           // Skip performance note
    bestlength[r-1, c-1] + match  // Match (1 if match, 0 if not)
)
```

**Optimizations**: 
- **Windowing**: Only compute score window around expected position, slide down if no match
- **Space**: Keep only current/previous columns, not full matrix
- **Robustness**: Limit skipping rate, penalize skips, prefer earliest matches
- **Virtual Clock**: `VirtualTime = (R - Rref) * S + Vref` for tempo following

## Enhanced Algorithm (Dannenberg & Mukaino, 1988)

**Architecture**: Preprocessor (compound events, ornaments) → Matcher (windowed DP) → Accompanist (tempo following)

**Key Enhancements**:
- **Multiple Matchers**: Concurrent instances for robustness during stops/re-entries
- **Ornament Handling**: Trills/glissandi as compound events to handle many-to-one mappings
- **Delayed Decisions**: ~100ms confirmation delays to prevent grace note misinterpretation  
- **Bit Vector Matching**: 12-bit pitch classes for octave equivalence and chord tolerance

```serpent
// Ornament pattern: consume rapid notes as single compound event
if ornament_detected(score_position):
    while not ornament_finished(): consume_performance_notes()
    send_compound_event_to_matcher()

// Bit vector encoding for chord matching
def encode_chord(pitches):
    return sum(1 << (pitch % 12) for pitch in pitches)
```

**Current Implementation**: Uses Cevent (compound events), Cell (DP matrix), static/dynamic strategies, trill detection, ASAP dataset integration.

