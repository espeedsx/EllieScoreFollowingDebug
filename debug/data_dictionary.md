# Score Following Debug Log Data Dictionary

This document describes all the log entry types and their fields in the score following algorithm debug logs.

## Log Entry Format

All log entries follow the format: `LOG_TYPE|field1:value1|field2:value2|...`

## Basic Algorithm Log Types

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

## Analysis Recommendations

- Use `DP` entries for main algorithm flow
- Use `TIMING` entries to debug timing constraints
- Use `MATCH_TYPE` entries to understand classification issues
- Use `DECISION` entries to see rule competition
- Watch for the Cell Initialization Bug in timing entries