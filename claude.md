DO NOT RUN THE ACTUAL SERPENT TESTS. THESE TESTS GENERATE HUGE LOG FILES AND EASILY EXHAUST ALL TOKENS. DO NOT RUN THE ACTUAL SERPENT TESTS. I DON'T HAVE A LOT OF TOKENS.

DO NOT ADD QUESTIONABLE FALLBACKS. IF SOMETHING IS NOT EXPECTED, THROW EXCEPTION AND FAIL EARLY AND FAIL FAST. DO NOT USE QUESTIONABLE FALLBACKS TO HIDE BUGS THAT ARE MUCH HARDER TO IDENTIFY. REMOVE ALL QUESTIONABLE FALLBACKS. 

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

# Serpent Programming Language Reference

## Overview

Serpent is a programming language inspired by Python, designed for real-time systems and interactive multimedia applications. It features:

- Simple, minimal syntax with dynamic typing
- Real-time garbage collection
- Multiple virtual machines running concurrently
- Object-oriented programming support
- Non-preemptive threads with precisely timed execution

## Types

### Primitive Types
- **Integer**: 64-bit signed integer (50 bits in serpent64)
- **Real**: 64-bit IEEE double-precision floating point
- **String**: Immutable 8-bit character strings
- **Symbol**: Immutable unique strings with global value and function
- **File**: Handle for an open file

### Structured Types
- **Array**: Sequence of values of any type
- **Dictionary**: Associative array (key-value pairs)
- **Object**: Instance of a user-defined class

### Special Values
- `nil` represents false
- Symbol `t` represents true
- Global variables `true` and `false` are bound to `t` and `nil`

## Syntax

### Indentation and Structure
- Uses indentation to indicate structure (like Python)
- Statements grouped by indenting to same level
- Statements can be combined on one line with semicolon separators
- Indent with 4 spaces, never use TAB characters

### Comments
- Use `//` or `#` for comments
- Always follow with a space: `// good comment`
- `#` is darker, use sparingly for emphasis

## Expressions and Constants

### Integer Constants
- Decimal: `123`
- Octal (starts with 0): `0123`
- Hexadecimal: `0x1A` or `0X1a`

### Real Constants
- With decimal point: `56.` or `4.5`
- With exponent: `4.5e2` (450.0)

### String Constants
- Enclosed in double quotes: `"hello"`
- Escape sequences: `\n`, `\t`, `\"`, `\\`, `\123` (octal), `\x1A` (hex)
- Unicode: `\uxxxx` (4 hex digits), `\Uxxxxxxxx` (8 hex digits)

### Symbol Constants
- Single quotes: `'symbol_name'`
- Can contain escape sequences like strings

### Arrays
- Square brackets: `[1, 'a', "hi"]`
- Constructed at runtime (mutable)

### Dictionaries
- Curly braces: `{'top': 50, 'bottom': 100}`
- Key/value pairs separated by commas, colon separates key from value

## Control Structures

### Conditional Statements
```serpent
if condition:
    statement1
    statement2
elif other_condition:
    statement3
else:
    statement4
```

### Loops

#### While Loop
```serpent
while condition:
    statement1
    statement2
```

#### For Loop (Range)
```serpent
for variable = expression1 to expression2 by expression3:
    statement1
    statement2
```
- `by` part is optional (defaults to 1)
- Direction depends on sign of step

#### For Loop (Array/Iterator)
```serpent
for variable at index in expression1:
    statement1
    statement2
```
- `at index` part is optional

### Display Statement
```serpent
display "label", var1, var2
```
- Prints: `label: var1 = value1, var2 = value2`

### Print Statement
```serpent
print expr1, expr2, expr3; expr4
```
- Comma outputs space, semicolon outputs no space
- Trailing comma/semicolon suppresses newline

### Return Statement
```serpent
return expression  // expression is optional
```

## Functions and Methods

### Function Definition
```serpent
def function_name(p1, p2, p3):
    var local_variable = initial_value
    statement1
    statement2
    return result
```

### Parameter Types
- **Required**: Standard positional parameters
- **Optional**: `optional p2 = default_value`
- **Keyword**: `keyword p3 = default_value`
- **Rest**: `rest p4` (collects extra positional args in array)
- **Dictionary**: `dictionary p5` (collects extra keyword args)

Order: required, optional, keyword, rest, dictionary

### Local Variables
```serpent
var x = 1, y = 2  // Multiple declarations allowed
```

## Object-Oriented Programming

### Class Definition
```serpent
class MyClass(SuperClass):
    var instance_var
    
    def init(param):
        instance_var = param
        
    def method1(p1):
        instance_var = p1
        return this.some_other_method()
```

### Object Creation
```serpent
obj = MyClass(5)  // Calls init method
```

### Member Access
```serpent
obj.instance_var = value  // Direct access
obj.method1(param)        // Method call
```

### Inheritance
- Single inheritance supported
- Use `super` to access superclass methods: `super.init(params)`
- `this` refers to current object

## Built-in Functions (Common)

### Math
- `abs(x)`, `cos(x)`, `sin(x)`, `tan(x)`, `exp(x)`, `log(x)`, `sqrt(x)`
- `int(x)`, `real(x)`, `round(x)`, `pow(x, y)`
- `max(x, y)`, `min(x, y)`, `random()`, `random_seed(s)`

### Strings
- `len(s)`, `str(x)`, `repr(x)`
- `find(string, pattern)`, `count(s, x)`
- `chr(i)`, `ord(c)`, `hex(i)`, `oct(i)`
- `tolower(s)`, `toupper(s)`, `totitle(s)`
- `subseq(s, start, end)`

### Arrays
- `array(n, fill)`, `len(a)`, `isarray(x)`
- `append(a, x)`, `insert(a, i, x)`, `remove(a, x)`
- `sort(a)`, `reverse(a)`, `copy(a)`
- `index(a, x)`, `last(a)`, `clear(a)`

### Dictionaries
- `dict(n)`, `isdict(x)`, `has_key(d, k)`, `get(d, k, default)`
- `keys(d)`, `values(d)`, `clear(d)`

### File Operations
- `open(filename, mode)`, `close(f)`, `flush(f)`
- `read(f, n)`, `readline(f)`, `readlines(f)`
- `write(f, data)`, `writelines(f, lines)`
- `getcwd()`, `listdir(path)`, `isdir(path)`

### System
- `exit(code)`, `system(command)`, `getenv(key)`
- `time_date()`, `get_os()`

## Debugging

### Debug Module
```serpent
require "debug"
```

### Breakpoints
```serpent
breakpoint(1)  // Break on first call
breakpoint(n)  // Break on nth call
breakpoint(condition)  // Break when condition is non-nil
```

### Error Handling
- Run-time errors invoke debugger
- `error(message)` generates run-time error
- Stack traces available in debugger

## Preprocessing Directives

### Conditional Compilation
```serpent
#ifdef SYMBOL
    // code when SYMBOL is defined
#elifdef OTHER_SYMBOL
    // code when OTHER_SYMBOL is defined
#else
    // default code
#endif
```

### Expression-based Conditionals
```serpent
#if expression
    // code when expression is true
#elif expression
    // alternative code
#endif
```

### No-op Functions
```serpent
#noop debug_function  // Makes function calls compile to nothing
#yesop debug_function // Reinstates function
```

## Threading

### Thread Creation
```serpent
thread_ref = fork()
if thread_ref == nil:
    // This is the new thread
else:
    // This is the original thread
```

### Thread Control
- `yield()` - yield to other threads
- `suspend(thread)` - suspend a thread
- `resume(thread)` - resume a thread
- `join(thread)` - wait for thread completion

## Programming Style Guidelines

### Naming Conventions
- Variables/functions: `snake_case` (e.g., `file_length`)
- Classes: `Capitalized_with_underscores` (e.g., `Labeled_slider`)
- Constants: `ALL_CAPS` (e.g., `NOTE_ON = 0x90`)

### Code Organization
- Use blank lines to separate logical blocks
- Comment blocks before functions explaining implementation
- Keep lines under 80 characters
- Use descriptive variable names

### Long Lines
Break with string concatenation:
```serpent
"This is a long string " + 
"continued on the next line"
```

For print statements:
```serpent
print "Long output line",
print "    ", var1, var2  // Indented continuation
```

## Common Idioms

### Array Creation with Initialization
```serpent
// Instead of array(10, array(10, 0)) which shares references
matrix = [array(10, 0) for i = 0 to 10]
```

### Error Checking
```serpent
if not isarray(data):
    error("Expected array, got " + type(data))
```

### File Processing
```serpent
var f = open(filename, "r")
if f:
    var content = readlines(f)
    close(f)
else:
    error("Could not open file: " + filename)
```

### Dictionary Iteration
```serpent
for key in keys(dict):
    var value = dict[key]
    // process key-value pair
```

## Performance Considerations

- Serpent has real-time garbage collection designed for low latency
- Avoid creating large temporary objects in tight loops
- Use local variables when possible for better performance
- Consider using arrays instead of repeated string concatenation
- Profile with `gc_cycles()` and `dbg_cycles()` for performance analysis

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

# Practical Serpent Examples and Patterns

This section provides concrete examples to help understand Serpent programming patterns and idioms.

## Basic Data Types and Operations

### Arrays
```serpent
// Creating and manipulating arrays
var a = []                    // Empty array
a = [5, 6, "hi", 'symb', 3.4] // Mixed types
var item = a[3]               // Access: returns 'symb'
var tail = subseq(a, 3)       // Subsequence: ['symb', 3.4]
var range = subseq(a, 1, 3)   // Range: [6, "hi"]

// Array methods
a.append("new")               // Add to end
a.insert(1, "inserted")       // Insert at position
var last = a.last()           // Get last element
var removed = a.unappend()    // Remove and return last
a.reverse()                   // Reverse in place
var copy = a.copy()           // Shallow copy
```

### Dictionaries
```serpent
// Creating and using dictionaries
var d = {}
d['name'] = "Alice"
d['age'] = 30
d['city'] = "Pittsburgh"

// Safe access with defaults
var country = d.get('country', "USA")  // Returns "USA" if key missing
var keys = d.keys()                    // Get all keys
print d['name'], "lives in", d['city']
```

### Strings and Characters
```serpent
// String manipulation
def process_strings()
    var char_a = ord("a")             // ASCII code for 'a'
    var alphabet = ""
    for i = 0 to 26
        alphabet = alphabet + chr(char_a + i)
    
    // String functions
    display "uppercase", toupper("hello")
    display "find substring", find(alphabet, "def")
    display "convert", int("123"), real("45.67")
    
    // String access like arrays
    var third_char = "hello"[2]       // Returns "l"
```

## Control Flow Patterns

### Loop Variations
```serpent
// Different loop patterns
data = ["apple", "banana", "cherry", "date"]

// Standard for loop with index
for i = 0 to len(data)
    print i, data[i]

// For-in loop
for item in data
    print item

// For-at loop (element and index)
for item at index in data
    print index, item

// While loop
var i = 0
while i < len(data)
    print data[i]
    i = i + 1
```

### Search Patterns
```serpent
// Different search implementations
def search_examples(data, target)
    // Linear search with for loop
    for i = 0 to len(data)
        if data[i] == target
            return i
    return -1
    
    // Using built-in index method
    return data.index(target)  // Raises error if not found
    
    // For-at pattern
    for item at i in data
        if item == target
            return i
    return -1
```

## Function and Parameter Patterns

### Parameter Types
```serpent
// Rest parameters - collect all arguments
def sum_all(rest numbers)
    var total = 0
    for num in numbers
        total = total + num
    return total

display "sum", sum_all(1, 2, 3, 4, 5)  // Returns 15

// Optional parameters with defaults
def print_quoted(text, optional quote = "\"")
    print quote + str(text) + quote

print_quoted("hello")        // "hello"
print_quoted("hello", "'")   // 'hello'

// Keyword parameters
def format_text(text, keyword prefix = "", keyword suffix = "")
    print prefix; text; suffix

format_text("Title", prefix = "<h1>", suffix = "</h1>")

// Dictionary parameters - catch extra keyword args
def process_data(required_param, dictionary extra_args)
    print "Required:", required_param
    for key in extra_args.keys()
        print key, "=", extra_args[key]

process_data("main", name = "Alice", age = 30, city = "Boston")
```

## Object-Oriented Patterns

### Basic Classes
```serpent
// Simple class with inheritance
class Account
    var balance
    
    def init(initial_amount)
        balance = initial_amount
    
    def deposit(amount)
        balance = balance + amount
        return balance
    
    def withdraw(amount)
        if balance >= amount
            balance = balance - amount
            return balance
        else
            return false

// Inheritance
class Named_account(Account)
    var name
    
    def init(account_name, initial_amount)
        super.init(initial_amount)  // Call superclass init
        name = account_name
    
    def show()
        print name, "has balance of $"; balance

// Usage
var account = Named_account("Alice", 1000)
account.deposit(500)
account.show()                    // "Alice has balance of $1500"
```

## File I/O Patterns

### File Processing
```serpent
// Reading and writing files
def process_file(input_file, output_file)
    var infile = open(input_file, "r")
    if not infile
        return "Could not open " + input_file
    
    var outfile = open(output_file, "w")
    if not outfile
        infile.close()
        return "Could not open " + output_file
    
    // Read all lines
    var lines = infile.readlines()
    infile.close()
    
    // Process and write
    for line in lines
        outfile.write(toupper(line))
    
    outfile.close()
    return "Success"

// CSV-like processing
def parse_fields(text_line)
    require "strparse"
    var parser = String_parse(text_line)
    var fields = []
    parser.skip_space()
    var field = parser.get_nonspace()
    while field != ""
        fields.append(field)
        field = parser.get_nonspace()
    return fields
```

## MIDI and Music Processing

### MIDI File Reading
```serpent
// Reading MIDI files with Allegro
require "allegro"
require "mfread"

def process_midi_file(file_path)
    var seq = allegro_smf_read(file_path)
    if not seq
        return "Could not read MIDI file"
    
    // Convert to beats for easier processing
    seq.convert_to_beats()
    
    // Process each track
    for track at track_num in seq.tracks
        print "TRACK", track_num
        for event in track
            if isinstance(event, Alg_note)
                print "Note: time="; event.time; 
                print " pitch="; event.key; 
                print " velocity="; event.loud
```

### Score Following Patterns
```serpent
// Typical score following setup patterns
require "allegro"
require "score_follower_v18_trill"

// Logging configuration
LOG_ROGER = false
LOG1 = false
LOG2 = false  
LOG3 = false

// Strategy selection
STRATEGY = 'dynamic'  // or 'static'

// File path handling
def score_path_to_labels_path(score_path)
    // Convert MIDI score path to labels path
    // Implementation specific to project structure
    return score_path.replace("midi_score", "labels")

// Event processing
class Score_event
    var time
    var pitches
    var confidence
    
    def init(event_time, pitch_list)
        time = event_time
        pitches = pitch_list
        confidence = 1.0
    
    def add_pitch(pitch)
        pitches.append(pitch)
```

## Error Handling and Debugging

### Debugging Patterns
```serpent
// Debugging setup
require "debug"

// Using display for debugging
def debug_function(data)
    display "input data", data, len(data)
    
    // Process data
    var result = process_data(data)
    
    display "result", result
    return result

// Breakpoints (when debug module loaded)
def complex_function(x)
    breakpoint(1)  // Break on first call
    var intermediate = x * 2
    breakpoint(intermediate > 10)  // Conditional break
    return intermediate + 5

// Error checking patterns
def safe_array_access(arr, index)
    if not isarray(arr)
        error("Expected array, got " + type(arr))
    
    if index < 0 or index >= len(arr)
        error("Index out of bounds: " + str(index))
    
    return arr[index]
```

## Common Project Patterns

### Module Structure
```serpent
// Standard module header
require "debug"      // For debugging
require "allegro"    // For MIDI
require "readcsv"    // For CSV files
require "strparse"   // For text parsing

// Version and constants
VERSION = "v18"
EPSILON = 0.01
MAX_ITERATIONS = 1000

// Global configuration
VERBOSE = false
OUTPUT_PATH = "../results/"

// Main processing function
def main(input_file, output_file)
    if VERBOSE
        print "Processing", input_file
    
    // Implementation here
    return "Success"
```

### Testing Patterns
```serpent
// Test function patterns
def test_basic_functionality()
    var test_data = [1, 2, 3, 4, 5]
    var result = my_function(test_data)
    
    if result != expected_result
        print "TEST FAILED: expected", expected_result, "got", result
        return false
    
    print "TEST PASSED"
    return true

// Running tests
def run_all_tests()
    var tests = ['test_basic_functionality', 'test_edge_cases', 'test_errors']
    var passed = 0
    
    for test_name in tests
        if funcall(test_name)
            passed = passed + 1
    
    print "Passed", passed, "of", len(tests), "tests"
```

## Performance and Optimization

### Efficient String Building
```serpent
// Efficient way to build large strings
def build_large_string()
    var parts = []
    for i = 0 to 1000
        parts.append(str(i))
        parts.append(",")
    return flatten(parts)  // Much faster than repeated concatenation
```

### Memory Management
```serpent
// Avoiding memory issues
def process_large_dataset(data)
    // Create arrays with proper initial size when possible
    var results = array(len(data), nil)
    
    for item at i in data
        results[i] = process_item(item)
        
        // Clear temporary data explicitly if needed
        if i % 100 == 0
            // Optional: force garbage collection
            // (usually not needed due to real-time GC)
    
    return results
```

These examples demonstrate the key patterns and idioms needed to write effective Serpent code for the score following project.

---

# Score Following Algorithm Implementation Details

## Core Algorithm (Dannenberg, 1985)

### Problem Definition
Score following treats a solo performance as a stream of events that must be matched against an ordered list of expected events from the score. The goal is to find the "best" match defined as the **longest common subsequence** between performance and score streams.

### Dynamic Programming Matrix
The algorithm constructs an integer matrix where:
- **Rows** = score events
- **Columns** = performance events  
- **Each cell** stores the length of the best match up to that point

### Core Algorithm Pseudocode
```pseudocode
forall i, bestlength[i, -1] <- 0;
forall j, bestlength[-1, j] <- 0;

for each new performance event p[c] do
begin
  for each score event s[r] do
  begin
    bestlength[r, c] <- max(bestlength[r - 1, c], bestlength[r, c - 1]);
    if p[c] matches s[r] then
      bestlength[r, c] <- max(bestlength[r, c],
                               1 + bestlength[r - 1, c - 1]);
  end
end
```

### Efficiency Optimizations

#### Space Optimization
- Only keep current and previous columns, not entire matrix
- Reduces memory requirements for real-time processing

#### Time Optimization (Windowing)
- Assumes performance stays close to score position
- Computes only a **window of score events** around expected match
- If no match found, slides window down by one row
- Window size must tolerate expected error rates

### Heuristics for Robustness

1. **Limit Skipping Rate**: Restrict score advancement to ≤ 2 rows per detected event
2. **Penalty for Skipping**: Deduct points for skipped events:
   ```pseudocode
   bestlength[r, c] <- max(bestlength[r - 1, c] - 1, bestlength[r, c - 1]);
   ```
3. **Earliest Match Preference**: When multiple matches tie, choose earliest score position

### Virtual Clock for Accompaniment
Synchronizes accompaniment using a virtual clock:
```
VirtualTime = (R - Rref) * S + Vref
```
- `R` = current real time
- `Rref` = last reset time  
- `Vref` = virtual score time at last reset
- `S` = speed of virtual clock

Clock resets when new matches are reported, with speed slightly adjusted for tempo following.

## Enhanced Algorithm (Dannenberg & Mukaino, 1988)

### System Architecture
The enhanced system has three main components:

1. **Preprocessor**: Groups events into compound events, detects ornaments
2. **Matcher**: Compares performance to score within windowed region
3. **Accompanist**: Plays accompaniment with real-time tempo adjustment

### Multiple Matchers Strategy

#### Motivation
- Single matcher window fails when soloist pauses or reenters unexpectedly
- Expanding window is computationally expensive

#### Implementation
- **Matchers as Objects**: Multiple concurrent instances track different hypotheses
- **Strategic Creation**: New matchers created during uncertainty (stops, extra notes)
- **Termination**: When one succeeds, others are terminated or suspended
- **Recovery**: Provides robustness against tracking errors

### Ornament Handling

#### Challenge
Trills and glissandi create **many-to-one mappings** between performance and score:
- Number of notes is indeterminate
- Exact pitches are performer-dependent

#### Preprocessor Solution
```serpent
// Ornament detection pattern
if ornament_detected(score_position)
    switch_to_ornament_state()
    while not ornament_finished()
        consume_performance_notes()
    send_compound_event_to_matcher()
```

- Detects trill/glissando markers in score
- Switches to special state during ornament
- Treats entire ornament as single compound event
- Prevents confusion from numerous rapid notes

### Delayed Decision Making

#### Problem
Matcher may misinterpret grace notes or ornamentation as primary events

#### Solution
- **Delay reports** briefly (~100ms)
- **Confirmation**: Following notes must confirm the match
- **Cancellation**: Contradictory notes cancel the report
- **Compensation**: Delay doesn't distort tempo calculations

```serpent
class Delayed_decision
    var pending_match
    var confirmation_timer
    
    def report_match(match)
        pending_match = match
        confirmation_timer = current_time() + DELAY_MS
    
    def process_confirmation(new_events)
        if confirms_match(new_events, pending_match)
            send_confirmed_match()
        else
            cancel_pending_match()
```

### Technical Optimizations

#### Octave Equivalence
- Ignore octave differences in pitch matching
- Allows performers to play in any octave
- Enables chord voicing flexibility

#### Bit Vector Encoding
```serpent
// 12-bit pitch class representation
def encode_chord(pitches)
    var bit_vector = 0
    for pitch in pitches
        var pitch_class = pitch % 12
        bit_vector = bit_vector | (1 << pitch_class)
    return bit_vector

def match_quality(score_chord, perf_chord)
    var difference = score_chord ^ perf_chord  // XOR for differences
    var missing = score_chord & difference     // Missing notes
    var extra = perf_chord & difference        // Extra notes
    return calculate_match_score(missing, extra)
```

Benefits:
- Fast bitwise operations (XOR, AND)
- Efficient detection of missing/extra notes
- Tolerance for imperfectly played chords

### Algorithm Robustness Features

#### Error Recovery
- Multiple matchers provide backup hypotheses
- System can recover from temporary tracking loss
- Graceful degradation when completely lost

#### Musical Realism
- Handles grace notes, trills, glissandi
- Tolerates wrong notes, missing notes, ornamentation
- Works without steady tempo assumptions
- Adapts to performer expression

### Performance Characteristics

#### Strengths
- Real-time capable on limited hardware
- Robust against common performance variations
- Musically intelligent ornament handling
- Efficient memory and computational usage

#### Limitations
- Requires pre-annotated ornaments in score
- Limited to relatively linear score structures
- Cannot handle extensive improvisation
- Temporal matching only (ignores dynamics, articulation)

### Implementation in EllieScoreFollowing

The current implementation builds on these foundations with:
- **Compound Events (Cevent)**: Groups simultaneous notes
- **Dynamic Programming Matrix**: Core alignment algorithm
- **Trill Detection**: Automated ornament recognition
- **Multiple Strategies**: Static vs. dynamic alignment approaches
- **ASAP Dataset Integration**: Comprehensive evaluation framework

```serpent
// Modern implementation pattern
class Score_follower
    var matchers          // Array of active matchers
    var preprocessor      // Ornament detection
    var current_position  // Best estimate of score position
    var virtual_clock     // Tempo following
    
    def process_performance_event(event)
        var processed = preprocessor.handle(event)
        var best_match = nil
        var best_score = -1
        
        for matcher in matchers
            var result = matcher.process(processed)
            if result.score > best_score
                best_match = result
                best_score = result.score
        
        if best_match
            update_position(best_match)
            virtual_clock.reset(best_match.score_time)
```

This implementation maintains the core principles while extending capabilities for modern score following applications.

---

# Score Following Algorithm: Complete Technical Documentation

## Overview

This document provides comprehensive technical documentation for the EllieScoreFollowing implementation, a sophisticated real-time score following system based on the Dannenberg & Bloch (ICMC 1985) dynamic programming algorithm with extensive enhancements for musical ornament handling, timing robustness, and debugging capabilities.

## Core Algorithm Architecture

### System Components

The score following system consists of four primary classes working in concert:

#### 1. Score_follower (Main Controller)
**Purpose**: Central orchestrator managing the entire score following process
**Key Responsibilities**:
- Strategy selection and switching (static vs dynamic)
- Input note preprocessing and compound event construction
- Top-level match result reporting and confidence tracking
- Integration with MIDI processing pipeline

**Critical Data Members**:
```serpent
var ref_track        // Array of Cevent objects representing the score
var match_mat        // Match_matrix instance managing DP computation
var strategy         // 'static' or 'dynamic' algorithm strategy
var current_cevt     // Currently accumulating performance compound event
var top_score        // Best alignment score found so far
var top_row          // Score position of best alignment
var input_count      // Performance note counter for debugging
```

#### 2. Match_matrix (DP Engine) 
**Purpose**: Implements the core dynamic programming algorithm with windowed optimization
**Key Responsibilities**:
- Sliding window management within the conceptual DP matrix
- Space-optimized storage (only current and previous columns)
- Window repositioning based on match confidence
- Base/upper bound index management for efficient access

**Critical Data Members**:
```serpent
var cur_col          // Current DP column being computed
var prev_col         // Previous DP column for diagonal access
var win_center       // Expected score position (window center)
var win_start        // Beginning of active window
var win_end          // End of active window  
var curbase          // Index offset for current column
var prevbase         // Index offset for previous column
var win_half_len     // Half-window size parameter
```

**Window Management Invariants**:
- `cur_col[0]` corresponds to matrix row `curbase`
- `curbase = win_start - 1` for proper alignment
- Window size = `2 * win_half_len + 1`
- Window slides to track expected score position

#### 3. Cevent (Compound Event)
**Purpose**: Represents simultaneous notes in score/performance with ornament metadata
**Key Responsibilities**:
- Grouping simultaneous notes based on timing epsilon
- Managing ornament information (trills, grace notes, ignore lists)
- Computing expected note counts for DP scoring
- Maintaining musical timing spans and relationships

**Critical Data Members**:
```serpent
var time            // Score time of first note in compound event
var pitches         // Array of MIDI note numbers in the chord
var time_span       // Duration from first to last onset
var ornaments       // Ornaments object with trill/grace/ignore pitches
var expected        // Total expected notes (pitches + active trills)
```

**Expected Count Calculation**:
- Base: `len(pitches)` 
- Add: Trill pitches not in ignore list
- Subtract: Chord pitches in ignore list  
- Grace notes are NOT counted in expected (handled separately)

#### 4. Cell (DP Matrix Element)
**Purpose**: Individual dynamic programming matrix cell with musical context
**Key Responsibilities**:
- Storing alignment score and timing information
- Tracking which pitches have been matched
- Maintaining unused note counts for penalty calculation
- Providing musical context for decision making

**Critical Data Members**:
```serpent
var value           // DP alignment score  
var time            // Time of last matched note
var used            // Array of matched pitches in this alignment path
var unused_count    // Number of expected notes not yet matched
```

### Algorithm Strategies

#### Static Strategy
**When Used**: Default strategy, suitable for performances with regular timing
**Characteristics**:
- Uses epsilon-based note grouping (default 75ms)
- Simple DP scoring: +1 for match, penalties for missing/extra/wrong notes
- Fixed cost parameters: `scm` (missing), `sce` (extra), `scw` (wrong)
- Compound event matching via `cevt_match()` with configurable threshold

**DP Rules**:
1. **Vertical (Skip Score)**: `score = curcol(rk-1) - scm`
2. **Horizontal (Skip Performance)**: `score = prevcol(rk) - sce`  
3. **Diagonal (Match/Mismatch)**: `score = prevcol(rk-1) + (1 if match else -scw)`

#### Dynamic Strategy  
**When Used**: Complex performances with irregular timing, ornaments, expressive timing
**Characteristics**:
- Individual note processing (no epsilon grouping)
- Context-aware scoring with musical semantics
- Timing constraint validation for all matches
- Sophisticated ornament handling (trills, grace notes)
- Adaptive cost parameters based on musical context

**DP Rules**:
1. **Vertical (Skip Score)**: `score = curcol(rk-1) - (dcm * unused_count)`
2. **Horizontal (Match with Constraints)**: Complex rule with multiple musical cases
3. **No Diagonal Rule**: Uses horizontal rule for matching logic

## Dynamic Programming Implementation

### Mathematical Formulation

The score following problem is formulated as finding the optimal alignment between:
- **Performance Stream**: P = [p₁, p₂, ..., pₙ] (time-ordered notes)
- **Score Stream**: S = [s₁, s₂, ..., sₘ] (compound events with ornament metadata)

**Objective**: Maximize alignment score function:
```
Score(i,j) = max {
    Score(i-1,j) - VerticalCost(sᵢ),      // Skip score event
    Score(i,j-1) - HorizontalCost(pⱼ),    // Skip performance note  
    Score(i-1,j-1) + DiagonalReward(sᵢ,pⱼ) // Match/mismatch
}
```

### Dynamic Strategy DP Rules (Core Algorithm)

#### Vertical Rule: Score Event Skipping
**Purpose**: Handle missing notes in performance
**Formula**: `new_score = prev_up_score - (dcm × unused_count)`
**When Applied**: Always computed first for each cell
**Parameters**:
- `dcm = 2`: Dynamic cost multiplier for missing notes
- `unused_count`: Number of expected notes not yet matched in score event

**Musical Interpretation**: 
- Penalty scales with number of missing notes in chord
- More severe penalty for skipping large chords
- Allows algorithm to skip difficult passages gracefully

```serpent
// Vertical rule implementation
if start_point_check:
    vertical_penalty = dcm * curup.unused_count
    cur.value = curup.value - vertical_penalty
else:
    cur.value = curup.value
```

#### Horizontal Rule: Performance Note Matching
**Purpose**: Process incoming performance notes with musical context awareness
**Complexity**: Multiple cases based on musical semantics
**Parameters**:
- `dmc = 2`: Dynamic match credit for successful note matches
- `dgc = 1`: Dynamic grace note credit (lower than chord notes)
- `dce = 1`: Dynamic cost for extra notes

**Case 1: Chord Note Matching**
```serpent
if ((pitch in cur_cevt.pitches) and 
    (pitch not in prev.used) and 
    timing_ok):
    
    if pitch in ignore_pitches:
        score = prev.value  // No credit, but no penalty
    else:
        score = prev.value + dmc  // Full credit
        report_match = true
```

**Case 2: Trill Note Matching**  
```serpent
if ((pitch in trill_pitches) and
    ((len(prev.used) == 0) or (ioi < trill_max_ioi))):
    
    if (pitch in prev.used) or (pitch in ignore_pitches):
        score = prev.value  // No additional credit
    else:
        score = prev.value + dmc  // Same credit as chord note
```

**Case 3: Grace Note Matching**
```serpent
if ((pitch in grace_pitches) and
    ((len(prev.used) == 0) or (ioi < grace_max_ioi))):
    
    if beyond_grace_notes:
        score = prev.value - dce  // Penalty for late grace note
    else:
        score = prev.value + dgc  // Reduced credit
```

**Case 4: No Match (Extra Note)**
```serpent
else:
    score = prev.value - dce  // Penalty for extra note
    time = prev.time  // Don't advance timing
```

### Timing Constraints

#### Purpose: Ensure musical plausibility of alignments
**Core Principle**: Inter-onset intervals (IOI) must be musically reasonable

#### Timing Validation Rules:

1. **Chord Notes**: `IOI < cevent.time_span + 0.1`
   - Based on score timing span of compound event
   - Allows slight performance timing variation

2. **Trill Notes**: `IOI < trill_max_ioi` (typically 0.2 seconds)
   - Rapid note repetition characteristic of trills
   - Prevents matching distant notes as trill continuations

3. **Grace Notes**: `IOI < grace_max_ioi` (typically 0.1 seconds)  
   - Very tight timing for ornamental notes
   - Must occur immediately before or during main notes

4. **First Note Exception**: First note in sequence always passes timing
   - Prevents initial timing constraint violations
   - Allows algorithm to start alignment process

```serpent
// Timing constraint implementation
var timing_limit = (grace_max_ioi if prev_unused_count == cur_cevt.expected 
                   else cur_cevt.time_span + 0.1)
var timing_ok = ((len(prev.used) == 0) or (time - prev.time < timing_limit))
```

### Window Management Algorithm

#### Purpose: Optimize DP computation by limiting search space
**Core Insight**: Performance typically stays close to expected score position

#### Window Structure:
- **Center**: Expected score position based on timing/tempo
- **Size**: `2 * win_half_len + 1` (typically 21 rows)
- **Bounds**: `[win_start, win_end)` with safety constraints

#### Window Movement Strategy:
1. **Successful Match**: Move center toward match position
2. **No Match**: Slide window down by 1 row
3. **Confidence-Based**: Higher scores justify larger movements
4. **Boundary Constraints**: Never exceed score start/end

```serpent
// Window repositioning logic
if match_found:
    new_center = match_row + confidence_adjustment
else:
    new_center = old_center + 1  // Slide down

// Apply safety constraints  
new_center = max(new_center, start_point + win_half_len)
new_center = min(new_center, length - win_half_len)
```

## Musical Context Processing

### Compound Event Construction

#### Score Processing Pipeline:
1. **MIDI Input**: Raw note events with timing and pitch
2. **Epsilon Grouping**: Cluster simultaneous notes (configurable epsilon)
3. **Ornament Integration**: Apply trill/grace annotations from labels
4. **Expected Count Calculation**: Compute total expected notes per event

```serpent
// Cevent construction from MIDI notes
def ref_to_cevts(note_track, channel, labels):
    var cevts = []
    var current_cevent = nil
    
    for note in note_track:
        if note.chan != channel: continue
        
        // Group notes by timing epsilon
        if not current_cevent or (note.time - current_cevent.time > epsilon):
            current_cevent = Cevent(note.time)
            cevts.append(current_cevent)
        
        current_cevent.add_note(note.key)
    
    // Apply ornament labels
    apply_ornament_labels(cevts, labels)
    return cevts
```

### Ornament Handling System

#### Trill Processing
**Purpose**: Handle rapid alternating note patterns that occur frequently in classical music
**Challenge**: Variable number of notes, indeterminate pitches
**Solution**: Treat as compound events with special matching rules

**Trill Detection**:
- Manual annotation via labels file
- Automatic detection via `trillfinder.srp` (rapid alternating pitches)
- Integration with score compound events

**Trill Matching Logic**:
```serpent
// Trill note matching
if pitch in trill_pitches:
    if timing_ok and not already_used:
        credit = dmc  // Same as chord note
        add_to_used_list(pitch)
    else:
        credit = 0  // No penalty, but no additional credit
```

#### Grace Note Processing  
**Purpose**: Handle ornamental notes that occur just before main notes
**Characteristics**: Very tight timing constraints, lower scoring weight
**Musical Context**: Must occur before moving to next chord

**Grace Note Logic**:
```serpent
if pitch in grace_pitches:
    if beyond_grace_notes:  // Already moved to chord notes
        penalty = dce  // Late grace note
    else:
        credit = dgc  // Reduced credit (1 vs 2 for chord)
```

#### Ignore Pitch Mechanism
**Purpose**: Handle ornament variations that shouldn't be expected
**Use Cases**: 
- Trill variations (upper/lower neighbors)
- Optional ornament notes
- Performance-dependent decorations

**Implementation**: Ignore pitches receive no credit but no penalty

### Performance Event Processing

#### Input Note Pipeline:
1. **Timing Analysis**: Calculate inter-onset interval from previous note
2. **Compound Event Grouping**: Determine if note continues current cevent  
3. **DP Matrix Update**: Process note through dynamic programming
4. **Match Reporting**: Report successful alignments with confidence

#### Epsilon-Based Grouping (Static Strategy):
```serpent
def eps_test(evt_time):
    var result = evt_time - last_evt_time > epsilon
    last_evt_time = evt_time
    return result

// In static_match():
if eps_test(time):  // New compound event
    current_cevt = Cevent(time)
    match_mat.swap()  // Move to next DP column
```

## Advanced Features and Debugging Infrastructure

### Multi-Strategy Support

#### Strategy Switching:
- **Runtime Selection**: Can switch between static/dynamic during execution
- **Performance Adaptation**: Choose strategy based on musical complexity
- **Graceful Transition**: Proper state management during switches

```serpent
def set_strategy(new_strategy):
    if new_strategy == strategy: return
    
    // Reinitialize matrix with new strategy
    if new_strategy == 'static':
        cur_col = [0 for i = 0 to len(cur_col)]
        prev_col = [SF_NINF for i = 0 to len(prev_col)]
    elif new_strategy == 'dynamic':
        cur_col = [Cell(0) for i = 0 to len(cur_col)]
        prev_col = [Cell(SF_NINF) for i = 0 to len(prev_col)]
    
    strategy = new_strategy
```

### Comprehensive Debug Logging System

#### Design Principles:
- **Selective Instrumentation**: Debug levels control verbosity
- **Compact Format**: Minimize token usage for AI analysis
- **Complete Context**: Capture all decision-making information
- **Non-Invasive**: Zero performance impact when disabled

#### Debug Log Hierarchy:
- `LOG_DEBUG`: Complete DP decision logging (for AI analysis)
- `LOG_ROGER`: Algorithm developer debugging output
- `LOG1`: High-level algorithm flow
- `LOG2`: Detailed DP calculations  
- `LOG3`: Matrix state and intermediate values

#### Compact Log Format Design:
```
INPUT|column:N|pitch:P|perf_time:T
MATRIX|column:N|window_start:S|window_end:E|window_center:C|...
CEVENT|row:R|score_time:T|pitch_count:N|time_span:S|ornament_count:O|expected:E
CELL|row:R|value:V|used_pitches:[P1,P2]|unused_count:U|cell_time:T|score_time:S
TIMING|prev_cell_time:T|curr_perf_time:T|ioi:I|span:S|limit:L|timing_pass:P|constraint_type:C
VRULE|row:R|up_value:V|penalty:P|result:R|start_point:S
HRULE|row:R|prev_value:V|pitch:P|ioi:I|limit:L|timing_pass:P|match_type:M|result:R
DECISION|row:R|vertical_result:V|horizontal_result:H|winner:W|updated:U|final_value:F|reason:R
DP|column:C|row:R|pitch:P|perf_time:T|vertical_rule:V|horizontal_rule:H|final_value:F|match:M|used_pitches:[P1,P2]|unused_count:U
MATCH|row:R|pitch:P|perf_time:T|score:S
NO_MATCH|pitch:P|perf_time:T
```

#### AI-Optimized Analysis Pipeline:
1. **Compact Capture**: Store every DP decision in minimal format
2. **Block Processing**: Group logs by INPUT boundaries  
3. **Context Extraction**: Identify failure patterns and decision contexts
4. **Focused Prompts**: Generate specific AI analysis requests
5. **Iterative Improvement**: Apply insights to algorithm parameters

### Performance Optimization Features

#### Space Optimization:
- **Two-Column Storage**: Only current and previous DP columns
- **Window Bounds**: Limit computation to relevant score region
- **Cell Reuse**: Efficient memory management for Cell objects

#### Time Optimization:
- **Early Termination**: Skip cells with impossible scores
- **Incremental Updates**: Only recompute changed portions
- **Vectorized Operations**: Batch similar calculations where possible

#### Real-Time Considerations:
- **Bounded Computation**: Guaranteed maximum processing time per note
- **Graceful Degradation**: Reduce window size under time pressure
- **Priority Processing**: Focus computation on most promising alignments

## Implementation Details and Parameter Specifications

### Algorithm Parameters

#### Static Strategy Parameters:
```serpent
epsilon = 0.075        // Note grouping threshold (seconds)
static_threshold = 0.5 // Match confidence threshold
scm = 1               // Static cost of missing notes
sce = 0               // Static cost of extra notes  
scw = 1               // Static cost of wrong notes
```

#### Dynamic Strategy Parameters:
```serpent
dmc = 2               // Dynamic match credit
dgc = 1               // Dynamic grace note credit
dcm = 2               // Dynamic cost of missing notes
dce = 1               // Dynamic cost of extra notes
win_half_len = 10     // Window half-size (total window = 21)
trill_max_ioi = 0.2   // Maximum trill inter-onset interval
grace_max_ioi = 0.1   // Maximum grace note inter-onset interval
```

### Data Structure Specifications

#### Match_matrix Invariants:
- `cur_col[0]` represents matrix row `curbase`
- `curbase = win_start - 1` for proper indexing
- `win_end = win_center + win_half_len` (bounded by score length)
- `prev_upper_bound` saved from previous column's `win_end`

#### Cell Object Properties:
- `value`: DP score (can be negative)
- `time`: Last match time (initialized to -1)
- `used`: Array of matched pitches (for duplicate detection)
- `unused_count`: Expected notes not yet matched

#### Cevent Construction Rules:
- `pitches`: Core chord tones only
- `ornaments.trill_pitches`: Trill decoration notes
- `ornaments.grace_pitches`: Grace note decorations  
- `ornaments.ignore_pitches`: Performance-optional notes
- `expected = len(pitches) + active_trill_count - ignored_chord_count`

### Error Handling and Edge Cases

#### Boundary Conditions:
- **Empty Performance**: Graceful degradation with all vertical moves
- **Empty Score**: Reject all performance notes as extra
- **Window Boundaries**: Safe indexing with out-of-window cell
- **Timing Initialization**: First note always passes timing constraints

#### Robustness Mechanisms:
- **Score Bounds Checking**: Prevent array access violations
- **Overflow Protection**: Use bounded integer arithmetic  
- **Invalid State Recovery**: Reset to known good state on errors
- **Graceful Fallbacks**: Default to safe behaviors on unexpected input

#### Debug Assertions:
```serpent
// Critical invariant checks (when debugging enabled)
assert(win_start >= 1)
assert(win_end <= length + 1)
assert(curbase == win_start - 1)
assert(len(cur_col) >= win_end - win_start)
```

### Integration Points

#### MIDI Processing Integration:
- **Input**: Alg_note objects from MIDI parser
- **Timing**: Convert MIDI beats to seconds using tempo map
- **Channel Filtering**: Process only specified instrument channel
- **Note Grouping**: Epsilon-based simultaneous note detection

#### Label System Integration:
- **Trill Labels**: `trill [pitch1, pitch2, ...]` with start/stop times
- **Grace Labels**: `grace [pitch1, pitch2, ...]` or `grace insert [...]`
- **Epsilon Labels**: `epsilon value` to adjust grouping threshold
- **Parameter Labels**: Dynamic adjustment of algorithm parameters

#### Accompaniment System Integration:
- **Match Reporting**: Real-time score position updates
- **Confidence Scoring**: Match quality assessment for tempo following
- **Error Recovery**: Graceful handling of tracking loss
- **State Synchronization**: Coordinate with virtual clock system

This comprehensive technical documentation provides the detailed algorithmic understanding needed for effective debugging, optimization, and enhancement of the score following system. The combination of mathematical rigor, implementation specifics, and debugging infrastructure enables systematic analysis and improvement of algorithm performance.