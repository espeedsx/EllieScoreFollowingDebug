# Score Following Debug Data Dictionary

This document describes the complete data structure used in the score following algorithm debug system, including raw log formats and the flattened CSV output structure.

## Overview

The debug system captures detailed algorithm execution logs and flattens them into a comprehensive CSV format for AI-powered analysis. Each CSV row represents one dynamic programming (DP) cell calculation with complete context.

## Raw Log Entry Format

All raw log entries follow the format: `LOG_TYPE|field1:value1|field2:value2|...`

## Flattened CSV Output Structure

The log flattener processes raw logs into a comprehensive CSV with 90+ columns organized into logical sections. Each row represents one DP cell calculation triggered by a performance note input.

### CSV Field Organization

The CSV fields are organized into 6 main sections for optimal analysis workflow:

#### SECTION 1: INPUT CONTEXT & OUTCOME (Most Important)
**What performance note triggered this and what was the result?**

| Column | Field | Type | Description |
|--------|-------|------|-------------|
| 1-3 | `input_column`, `input_pitch`, `input_perf_time` | int, int, float | Performance note that triggered this DP calculation |
| 4-7 | `match_row`, `match_pitch`, `match_perf_time`, `match_score` | int, int, float, float | Match details (only populated if successful) |
| 8-9 | `no_match_pitch`, `no_match_perf_time` | int, float | No-match details (only populated if failed) |
| 10 | `result_type` | string | Final classification: "match", "no_match", or "unprocessed" |
| 11-15 | `match_explanation`, `no_match_explanation`, `decision_explanation`, `timing_explanation`, `ornament_explanation` | string | **Human-readable final decision explanations with source line numbers** |

#### SECTION 2: ALGORITHM STATE 
**Current DP state and target**

| Column Range | Field Group | Description |
|--------------|-------------|-------------|
| 16-22 | `matrix_*` | DP window state (start, end, center, bases, bounds) |
| 23-29 | `cevent_*` | Target score event details (time, pitches, ornaments) |
| 30-34 | `cell_*` | Previous DP cell state (starting point) |

#### SECTION 3: DP COMPUTATION
**Core algorithm execution**

| Column Range | Field Group | Description |
|--------------|-------------|-------------|
| 35-38 | `vrule_*` | Vertical rule (skip score event) calculation |
| 39-45 | `timing_*` | Timing constraint validation |
| 46-51 | `hrule_*` | Horizontal rule (match performance note) calculation |
| 52-57 | `decision_*` | Final DP cell decision (vrule vs hrule winner) |

#### SECTION 4: MUSICAL ANALYSIS
**Musical context and ornament processing**

| Column Range | Field Group | Description |
|--------------|-------------|-------------|
| 58-65 | `matchtype_*` | Musical classification (chord, trill, grace, extra note) |
| 66-70 | `ornament_*` | Ornament processing details and credits |
| 71-73 | `ornament_*_str` | **Sorted pitch lists** for ornaments |

#### SECTION 5: ALGORITHM RESULT
**Final DP computation and outcomes**

| Column Range | Field Group | Description |
|--------------|-------------|-------------|
| 74-80 | `dp_*` | Summary of DP computation for this cell |
| 81-85 | `score_*` | Global score competition and confidence |

#### SECTION 6: DEBUGGING CONTEXT
**Analysis and diagnostics**

| Column Range | Field Group | Description |
|--------------|-------------|-------------|
| 86-88 | `array_*` | DP matrix neighborhood values |
| 89-90 | `bug_*` | Algorithm bug detection (timing initialization bug) |

### Key Features of CSV Output

#### 1. **Final Decision Explanations (NEW)**
Every input note has exactly one explanation showing the final decision:
- **match_explanation**: "Pitch 74 matched: FINAL DECISION (line 1733): Pitch 74 MATCHED at score row 1 | Alignment score: 2 | first_note | Expected: [74] (score=2, timing=2.00454, context=FINAL_MATCH at line 1733: Row=1 | Expected=[74] | Score=2, source_line=1733)"
- **no_match_explanation**: "Pitch 80 no match: FINAL DECISION (line 1743): Pitch 80 NO MATCH | Search window exhausted | Window=[500-520],Center=510 | Expected: [58,62,66,70,74,78,82] (constraint=search_exhausted, timing=51.2708, expected=FINAL_NO_MATCH at line 1743: Window=[500-520],Center=510 | Expected=[58,62,66,70,74,78,82], source_line=1743)"

#### 2. **Sorted Pitch Lists (NEW)**
All pitch lists are automatically sorted in ascending order:
- **cevent_pitches_str**: `[58,62,66,70,74,78,82]` (was `[70,74,78,82,58,62,66]`)
- **dp_used_pitches**: `[60,64,67]` (sorted)
- **ornament pitch fields**: All sorted for consistency
- **Pitch lists in explanations**: Also sorted automatically

#### 3. **"na" for Empty Fields (NEW)**
Empty explanation fields show "na" instead of blanks for cleaner analysis:
- Entries with matches: `match_explanation="Pitch 74 matched..."`, `no_match_explanation="na"`
- Entries with no matches: `match_explanation="na"`, `no_match_explanation="Pitch 80 no match..."`

#### 4. **Complete Context Per Row**
Each row contains everything needed to understand one DP decision:
- Input that triggered it
- Algorithm state when it happened  
- All intermediate calculations
- Final decision and reasoning
- Musical context and constraints

## Raw Algorithm Log Types

### DP (Dynamic Programming Decision)
Records each cell calculation in the dynamic programming matrix.

| Field | Type | Description |
|-------|------|-------------|
| `column` | int | Performance note column number (input sequence) |
| `row` | int | Score event row number |
| `pitch` | int | MIDI pitch number (0-127) |
| `perf_time` | float | Performance time in seconds |
| `vertical_rule` | float | Vertical rule result (advance in score without match) |
| `horizontal_rule` | float | Horizontal rule result (match performance to score) |
| `final_value` | float | Final cell value (max of vertical/horizontal rules) |
| `match` | int | 1 if match found, 0 if no match |
| `used_pitches` | list | Comma-separated list of matched pitches in this chord |
| `unused_count` | int | Number of expected pitches not yet matched |

**Example:** `DP|column:127|row:83|pitch:67|perf_time:28.307|vertical_rule:241.0|horizontal_rule:241.0|final_value:241.0|match:0|used_pitches:[]|unused_count:1`

### MATCH (Successful Match)
Records when a performance note successfully matches a score position.

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Score row that was matched |
| `pitch` | int | MIDI pitch that was matched |
| `perf_time` | float | Performance time of the match |
| `score` | float | Algorithm confidence score for this match |

**Example:** `MATCH|row:78|pitch:67|perf_time:28.212|score:252.0`

### NO_MATCH (Failed Match)
Records when a performance note cannot be matched to any score position.

| Field | Type | Description |
|-------|------|-------------|
| `pitch` | int | MIDI pitch that failed to match |
| `perf_time` | float | Performance time when match failed |

**Example:** `NO_MATCH|pitch:67|perf_time:28.307`

## Test Control Log Types

### TEST_START (Test Case Begin)
Marks the beginning of a test case.

| Field | Type | Description |
|-------|------|-------------|
| `test_case` | int | Test case identifier |
| `score_file` | string | Path to score MIDI file |
| `performance_file` | string | Path to performance MIDI file |

**Example:** `TEST_START|test_case:1|score_file:unknown|performance_file:unknown`

### TEST_END (Test Case End)
Marks the end of a test case.

| Field | Type | Description |
|-------|------|-------------|
| `test_case` | int | Test case identifier |
| `matches_found` | int | Number of successful matches |
| `total_notes` | int | Total number of performance notes |

**Example:** `TEST_END|test_case:1|matches_found:unknown|total_notes:unknown`

## Comprehensive Algorithm Analysis Log Types

### INPUT (Performance Note Input)
Records each incoming performance note.

| Field | Type | Description |
|-------|------|-------------|
| `column` | int | Sequential input number |
| `pitch` | int | MIDI pitch number |
| `perf_time` | float | Performance time in seconds |

**Example:** `INPUT|column:127|pitch:67|perf_time:28.307`

### MATRIX (Matrix State)
Records the state of the dynamic programming matrix window.

| Field | Type | Description |
|-------|------|-------------|
| `column` | int | Current column being processed |
| `window_start` | int | Start row of processing window |
| `window_end` | int | End row of processing window |
| `window_center` | int | Center row of processing window |
| `current_base` | int | Base row for current column |
| `prev_base` | int | Base row for previous column |
| `current_upper` | int | Upper bound for current column |
| `prev_upper` | int | Upper bound for previous column |

**Example:** `MATRIX|column:127|window_start:68|window_end:88|window_center:78|current_base:67|prev_base:67|current_upper:88|prev_upper:88`

### CELL (Cell State)
Records the state of a specific matrix cell before processing.

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Row number of the cell |
| `value` | float | Current value stored in the cell |
| `used_pitches` | list | Pitches already matched to this cell |
| `unused_count` | int | Number of expected pitches not yet matched |
| `cell_time` | float | Time when this cell was last updated |
| `score_time` | float | Score time for this event |

**Example:** `CELL|row:83|value:238|used_pitches:[]|unused_count:1|cell_time:-1|score_time:12.5`

### VRULE (Vertical Rule Calculation)
Records vertical rule processing (advancing in score without matching).

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Score row being processed |
| `up_value` | float | Value from cell above |
| `penalty` | float | Penalty applied for skipping |
| `result` | float | Final vertical rule result |
| `start_point` | string | Whether this is a valid start point |

**Example:** `VRULE|row:83|up_value:245|penalty:4|result:241|start_point:t`

### HRULE (Horizontal Rule Calculation)
Records horizontal rule processing (matching performance to score).

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Score row being processed |
| `prev_value` | float | Value from previous column |
| `pitch` | int | Performance pitch being matched |
| `ioi` | float | Inter-onset interval (time since last match to this row) |
| `limit` | float | Timing constraint limit |
| `timing_pass` | string | Whether timing constraint passed |
| `match_type` | string | Type of match (chord, trill, grace, extra_note, etc.) |
| `result` | float | Final horizontal rule result |

**Example:** `HRULE|row:83|prev_value:242|pitch:67|ioi:29.307|limit:0.35|timing_pass:t|match_type:extra_note|result:241`

### TIMING (Timing Constraint Check)
Records detailed timing constraint validation.

| Field | Type | Description |
|-------|------|-------------|
| `prev_cell_time` | float | Time of previous match (-1 if uninitialized) |
| `curr_perf_time` | float | Current performance note time |
| `ioi` | float | Inter-onset interval (curr_perf_time - prev_cell_time) |
| `span` | float | Score event time span |
| `limit` | float | Timing constraint limit |
| `timing_pass` | string | Whether constraint passed (t/nil) |
| `constraint_type` | string | Type of constraint (chord_basic, chord, trill, grace) |

**Example:** `TIMING|prev_cell_time:-1|curr_perf_time:28.307|ioi:29.307|span:0|limit:0.1|timing_pass:nil|constraint_type:chord_basic`

### MATCH_TYPE (Match Type Analysis)
Records classification of how a pitch relates to the score.

| Field | Type | Description |
|-------|------|-------------|
| `pitch` | int | MIDI pitch being classified |
| `is_chord` | string | Whether pitch is in expected chord |
| `is_trill` | string | Whether pitch is part of a trill |
| `is_grace` | string | Whether pitch is a grace note |
| `is_extra` | string | Whether pitch is an extra note |
| `is_ignored` | string | Whether pitch should be ignored |
| `already_used` | string | Whether pitch already matched |
| `timing_ok` | string | Whether timing constraints are satisfied |
| `ornament_info` | string | Additional ornament information |

**Example:** `MATCH_TYPE|pitch:67|is_chord:t|is_trill:nil|is_grace:nil|is_extra:t|is_ignored:nil|already_used:t|timing_ok:nil|ornament_info:extra_note`

### DECISION (Cell Decision)
Records the final decision for updating a matrix cell.

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Score row |
| `vertical_result` | float | Result from vertical rule |
| `horizontal_result` | float | Result from horizontal rule |
| `winner` | string | Which rule won (vertical/horizontal) |
| `updated` | string | Whether cell was updated |
| `final_value` | float | Final value stored in cell |
| `reason` | string | Reason for the decision |

**Example:** `DECISION|row:83|vertical_result:241|horizontal_result:241|winner:vertical|updated:nil|final_value:241|reason:extra_note`

### ARRAY (Array Neighborhood)
Records the neighborhood values around a matrix cell.

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Center row |
| `center_value` | float | Value at center position |
| `values` | list | Comma-separated neighbor values |
| `positions` | list | Comma-separated neighbor positions |

**Example:** `ARRAY|row:83|center_value:241|values:[245,241,241,236,232]|positions:[81,82,83,84,85]`

### SCORE (Score Competition)
Records how current score compares to top score.

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Score row |
| `current_score` | float | Current cell score |
| `top_score` | float | Best score seen so far |
| `beats_top` | string | Whether current beats top score |
| `margin` | float | Difference from top score |
| `confidence` | float | Confidence level (0-1) |

**Example:** `SCORE|row:83|current_score:241|top_score:252|beats_top:nil|margin:-11|confidence:0.956345`

### ORNAMENT (Ornament Processing)
Records ornament detection and processing.

| Field | Type | Description |
|-------|------|-------------|
| `pitch` | int | Performance pitch |
| `ornament_type` | string | Type of ornament processing |
| `trill_pitches` | list | Pitches identified as trill notes |
| `grace_pitches` | list | Pitches identified as grace notes |
| `ignore_pitches` | list | Pitches to be ignored |
| `credit_applied` | float | Score credit applied for ornament |

**Example:** `ORNAMENT|pitch:60|ornament_type:chord_matched|trill_pitches:[]|grace_pitches:[]|ignore_pitches:[]|credit_applied:2`

### WINDOW_MOVE (Window Movement)
Records when the processing window is moved.

| Field | Type | Description |
|-------|------|-------------|
| `old_center` | int | Previous window center |
| `new_center` | int | New window center |
| `old_start` | int | Previous window start |
| `new_start` | int | New window start |
| `old_end` | int | Previous window end |
| `new_end` | int | New window end |
| `reason` | string | Reason for window movement |

**Example:** `WINDOW_MOVE|old_center:77|new_center:78|old_start:67|new_start:68|old_end:87|new_end:88|reason:advance`

### CEVENT (Current Score Event Summary)
Records summary information about the current score event being processed.

| Field | Type | Description |
|-------|------|-------------|
| `row` | int | Score row number (matrix row) |
| `score_time` | float | Score time of this event (seconds) |
| `pitch_count` | int | Number of pitches in the main chord |
| `time_span` | float | Time difference between first and last note onsets |
| `ornament_count` | int | Total number of ornament pitches (trill + grace + ignore) |
| `expected` | int | Number of notes expected to match this event |

**Example:** `CEVENT|row:83|score_time:12.5|pitch_count:3|time_span:0.0|ornament_count:2|expected:4`

## Data Types

### Common Data Types
- **int**: Integer values (row/column numbers, pitches, counts)
- **float**: Floating-point values (times, scores, IOI values)
- **string**: Text values (match types, boolean flags as t/nil)
- **list**: Comma-separated values in square brackets `[item1,item2,item3]`

### Boolean Representation
- `t` = true
- `nil` = false/null

### Special Values
- `-1`: Uninitialized time values
- `SF_NINF`: Negative infinity (for impossible states)
- `unknown`: Placeholder for unavailable information

## Known Algorithm Issues

### Cell Initialization Bug
When `prev_cell_time` is `-1`, IOI calculations become invalid:
- **Symptom**: Very large IOI values (>29 seconds)
- **Cause**: `ioi = curr_perf_time - (-1) = curr_perf_time + 1`
- **Impact**: Causes false timing constraint failures
- **Detection**: Look for `prev_cell_time:-1` with large `ioi` values

## Usage Notes

1. **Time Units**: All times are in seconds
2. **Pitch Range**: MIDI pitches 0-127 (middle C = 60)
3. **Log Order**: Entries appear in chronological processing order
4. **Performance Focus**: Algorithm processes performance notes sequentially
5. **Matrix Coordinates**: (row, column) = (score_event, performance_note)

## Human-Readable Explanation Log Types (NEW)

### MATCH_EXPLAIN (Final Match Decision)
Records the final decision when a performance note successfully matches a score position.

| Field | Type | Description |
|-------|------|-------------|
| `pitch` | int | Performance pitch that was matched |
| `reason` | string | Complete explanation of why this was a match |
| `score` | float | Algorithm confidence score |
| `timing` | float | Performance time when match occurred |
| `context` | string | Additional context about the match |
| `source_line` | int | Source code line number where decision was made (1733) |

**Example:** `MATCH_EXPLAIN|pitch:74|reason:FINAL DECISION (line 1733): Pitch 74 MATCHED at score row 1 | Alignment score: 2 | first_note | Expected: [74]|score:2|timing:2.00454|context:FINAL_MATCH at line 1733: Row=1 | Expected=[74] | Score=2|source_line:1733`

### NO_MATCH_EXPLAIN (Final No-Match Decision) 
Records the final decision when a performance note cannot be matched to any score position.

| Field | Type | Description |
|-------|------|-------------|
| `pitch` | int | Performance pitch that failed to match |
| `reason` | string | Complete explanation of why no match was found |
| `constraint` | string | Type of constraint that prevented matching |
| `timing` | float | Performance time when match failed |
| `expected` | string | What the algorithm was expecting to find |
| `source_line` | int | Source code line number where decision was made (1743) |

**Example:** `NO_MATCH_EXPLAIN|pitch:80|reason:FINAL DECISION (line 1743): Pitch 80 NO MATCH | Search window exhausted | Window=[500-520],Center=510 | Expected: [70,74,78,82,58,62,66]|constraint:search_exhausted|timing:51.2708|expected:FINAL_NO_MATCH at line 1743: Window=[500-520],Center=510 | Expected=[70,74,78,82,58,62,66]|source_line:1743`

## Processing Enhancements (NEW)

### Pitch List Sorting
All pitch lists in the output are automatically sorted in ascending order for consistency:
- **Raw format**: `[70,74,78,82,58,62,66]`
- **Processed format**: `[58,62,66,70,74,78,82]`

This applies to:
- `cevent_pitches_str`: Score event chord pitches
- `dp_used_pitches`: Already matched pitches  
- `cell_used_pitches`: Cell state pitches
- `ornament_*_pitches_str`: Ornament pitch lists
- **Pitch lists within explanation text**: Also automatically sorted

### Empty Field Handling
Empty explanation fields are replaced with "na" for cleaner analysis:
- Prevents confusion between empty strings and null values
- Makes it clear when explanations are not available
- Improves consistency for AI analysis

### Input Block Processing
The system processes logs in input blocks:
1. **INPUT** line starts a new block
2. All **DP**, **MATRIX**, **TIMING**, etc. lines are collected
3. **MATCH/NO_MATCH** line indicates end of processing
4. **MATCH_EXPLAIN/NO_MATCH_EXPLAIN** provides final explanation
5. Block is converted to multiple CSV rows (one per DP cell)

## Analysis Recommendations

### CSV Analysis Workflow
1. **Start with SECTION 1** (columns 1-15): Understand input and outcome
2. **Check explanation fields** (columns 11-15): Get human-readable reasoning
3. **Examine timing constraints** (columns 39-45): Debug timing failures  
4. **Review musical classification** (columns 58-65): Understand match types
5. **Validate with DP computation** (columns 35-57): Verify algorithm logic

### Common Analysis Patterns
- **Filter by result_type**: Focus on "match" or "no_match" entries
- **Group by input_column**: See all DP cells for one performance note
- **Sort by input_perf_time**: Follow chronological performance order
- **Search explanation fields**: Find specific failure patterns
- **Check bug_has_timing_bug**: Identify systematic algorithm issues

### Raw Log Analysis (Advanced)
- Use `DP` entries for main algorithm flow
- Use `TIMING` entries to debug timing constraints
- Use `MATCH_TYPE` entries to understand classification issues
- Use `DECISION` entries to see rule competition
- Watch for the Cell Initialization Bug in timing entries