# Dynamic Score Following Algorithm - Technical Documentation

## Overview

This document provides comprehensive technical documentation of the dynamic score following algorithm implemented in `score_follower_v18_trill.srp`. The algorithm is based on the foundational work by Dannenberg & Bloch (ICMC '85) with significant enhancements for trill handling, timing constraints, and real-time performance optimization.

**Score following** is the real-time task of tracking a musical performance against a known musical score, essentially solving a sequence alignment problem between performed notes and expected score events.

## Core Algorithm Architecture

### Problem Formulation

The score following problem is formulated as a **modified dynamic programming sequence alignment** where:

- **Performance stream**: Sequence of incoming MIDI notes with timestamps
- **Score reference**: Pre-processed sequence of compound events (Cevents) 
- **Goal**: Find the longest common subsequence while respecting musical timing constraints
- **Output**: Real-time position tracking with confidence scores

### Dynamic Programming Foundation

```
Matrix[row, col] = max(
    vertical_rule(row-1, col),     // Skip score event (missing note)
    horizontal_rule(row, col-1)    // Match performance note to score event
)
```

Where:
- **Rows** = Score events (compound events from reference track)
- **Columns** = Performance events (incoming MIDI notes)  
- **Cell values** = Cumulative alignment quality score

## Core Data Structures

### Compound Events (Cevent)

Compound events group simultaneous or near-simultaneous notes into single scoring units:

```serpent
class Cevent:
    var time       // Score time of first note (seconds)
    var pitches    // Array of MIDI pitch numbers in the chord
    var time_span  // Time difference between first and last note onsets
    var ornaments  // Trill/grace note information (Ornaments object)
    var expected   // Total number of notes expected to match
```

**Key Properties**:
- `expected = len(pitches) + len(trill_pitches_not_ignored)`
- Grace notes are not counted in `expected` (no penalty for missing)
- Time span enables timing tolerance for rolled chords

### Cell State Management

Each dynamic programming cell maintains comprehensive state:

```serpent
class Cell:
    var value        // Cumulative alignment score
    var used         // Array of matched pitches in this chord
    var time         // Time when cell was last updated (-1 if uninitialized)
    var unused_count // Number of expected pitches not yet matched
```

**Critical Implementation Detail**: Cells initialize with `time = -1`, causing the algorithm bug where IOI calculations become `current_time - (-1) = current_time + 1`, resulting in nonsensical timing values.

### Match Matrix Windowing

The algorithm uses a sliding window approach to optimize memory and computation:

```serpent
class Match_matrix:
    var cur_col       // Current column being computed
    var prev_col      // Previous column (for horizontal rule access)
    var win_center    // Expected match position
    var win_start     // Start of processing window (1-based)
    var win_end       // End of processing window (1-based)
    var win_half_len  // Window radius (default: 10 for debugging, should be 30)
    var curbase       // Offset: cur_col[0] represents matrix row curbase
    var prevbase      // Offset for previous column
```

**Window Management**:
- Window size: `win_half_len * 2 + 1`
- Window repositioning: `win_center = last_match_position + 1`
- Boundary handling: `win_start = max(start_point, win_center - win_half_len)`

## Dynamic Programming Algorithm

### Core Processing Loop

For each incoming performance note, the algorithm processes a window of score events:

```serpent
def dynamic_match(time, pitch, result):
    // 1. Initialize current column window
    mm.curbase = mm.win_start - 1
    
    // 2. Process each row in the window
    for rk = mm.win_start to mm.win_end:
        // 3. Apply vertical rule (score advancement)
        apply_vertical_rule(rk)
        
        // 4. Apply horizontal rule (note matching)
        apply_horizontal_rule(rk, pitch, time)
        
        // 5. Select best result: max(vertical, horizontal)
        finalize_cell_decision(rk)
        
        // 6. Update top score if this is the best match
        update_top_score_if_better(rk)
```

### Vertical Rule: Score Advancement

The vertical rule handles advancing through the score without matching the current performance note:

```serpent
def apply_vertical_rule(rk):
    var cur = mm.curcol(rk)
    var curup = mm.curcol(rk - 1)  // Cell above (previous score event)
    
    var vertical_penalty = 0
    if rk > match_mat.start_point:
        // Penalty for skipping expected notes
        vertical_penalty = dcm * curup.unused_count
        cur.value = curup.value - vertical_penalty
    else:
        cur.value = curup.value  // No penalty at start
    
    // Initialize for this score event
    cur.used.clear()
    cur.unused_count = current_score_event.expected
```

**Key Parameters**:
- `dcm` (dynamic cost missing) = 2: Penalty per unmatched expected note
- Boundary condition: No penalty before `start_point`

### Horizontal Rule: Note Matching

The horizontal rule handles matching the performance note to the current score event:

```serpent
def apply_horizontal_rule(rk, pitch, time):
    var prev = get_previous_cell(rk)  // From previous column
    var cur_cevt = ref_track[rk - 1]  // Current score event
    
    // Calculate timing constraint
    var ioi = time - prev.time
    var timing_limit = cur_cevt.time_span + 0.1  // 100ms + chord time span
    var timing_ok = (len(prev.used) == 0) or (ioi < timing_limit)
    
    // Determine match type and calculate value
    var horizontal_value = prev.value
    var match_type = determine_match_type(pitch, cur_cevt, prev, timing_ok)
    
    switch match_type:
        case "chord_matched":
            horizontal_value = prev.value + dmc  // Match credit
            update_used_pitches(pitch)
        case "trill_matched":  
            horizontal_value = prev.value + dmc
            // Trills don't count toward expected
        case "grace_matched":
            horizontal_value = prev.value + dgc  // Grace note credit
        case "extra_note":
            horizontal_value = prev.value - dce  // Extra note penalty
        case "chord_ignored":
            horizontal_value = prev.value  // No change for ignored notes
```

**Key Parameters**:
- `dmc` (dynamic match credit) = 2: Reward for matching expected note
- `dgc` (dynamic grace credit) = 1: Reward for matching grace note  
- `dce` (dynamic cost extra) = 1: Penalty for extra note

### Match Type Classification

The algorithm classifies each performance note into specific categories:

#### 1. Chord Note Matching
```serpent
if (pitch in cur_cevt.pitches) and (pitch not in prev.used) and timing_ok:
    // Regular chord note match
    if pitch in ornaments.ignore_pitches:
        match_type = "chord_ignored"  // No credit/penalty
    else:
        match_type = "chord_matched"  // Full credit
```

#### 2. Trill Note Matching  
```serpent
if (pitch in cur_cevt.ornaments.trill_pitches) and (ioi < trill_max_ioi):
    if pitch in prev.used:
        match_type = "trill_repeated"  // No additional credit
    elif pitch in ornaments.ignore_pitches:
        match_type = "trill_ignored"   // No credit
    else:
        match_type = "trill_matched"   // Full credit
```

**Trill Timing**: `trill_max_ioi = 0.35s` (maximum inter-onset interval for trill notes)

#### 3. Grace Note Matching
```serpent
if (pitch in cur_cevt.ornaments.grace_pitches) and (ioi < grace_max_ioi):
    // Grace notes must occur before chord notes
    var beyond_grace_notes = any(p not in grace_pitches for p in prev.used)
    if beyond_grace_notes:
        match_type = "grace_after_chord"  // Penalty
    else:
        match_type = "grace_matched"      // Grace credit
```

#### 4. Extra Note Handling
```serpent
else:
    match_type = "extra_note"  // Penalty for unmatched note
```

### Cell Decision Logic

After computing both vertical and horizontal rules, select the best result:

```serpent
def finalize_cell_decision(rk):
    var cur = mm.curcol(rk)
    var vertical_value = cur.value
    var horizontal_value = computed_horizontal_value
    
    if horizontal_value > vertical_value:
        // Horizontal rule wins - accept the match
        cur.value = horizontal_value
        cur.used = prev.used.copy()
        cur.unused_count = prev.unused_count - (1 if match else 0)
        cur.time = time
        if match:
            cur.used.append(pitch)
    // Otherwise keep vertical rule result
```

## Timing Constraint System

### IOI-Based Grouping

The algorithm uses Inter-Onset Intervals (IOI) to determine if notes belong together:

```serpent
var ioi = current_time - previous_cell_time
var timing_limit = score_event.time_span + 0.1  // 100ms base + chord span

if ioi < timing_limit:
    // Notes are close enough to group together
else:
    // Too much time has passed, treat as separate events
```

### Timing Constraint Types

1. **Chord Basic**: `time_span + 0.1s`
2. **Chord Full**: Considers ornament timing  
3. **Trill**: `trill_max_ioi = 0.35s`
4. **Grace**: `grace_max_ioi` (dynamically set)

### Algorithm Bug: Cell Time Initialization

**Critical Issue**: Cells initialize with `time = -1`, causing invalid IOI calculations:

```
ioi = current_performance_time - (-1) = current_performance_time + 1
```

This results in IOI values like 29.307 seconds for a 28.307s performance note, causing false timing constraint failures.

## Window Management Strategy

### Adaptive Window Positioning

```serpent
def update_window_position():
    if (top_score > last_top_score) and (match_position > last_max_position):
        new_center = match_position + 1
        win_start = max(start_point, new_center - win_half_len)
        win_end = min(score_length + 1, new_center + win_half_len)
```

### Memory Optimization

The algorithm maintains only two columns in memory:

```serpent
def column_swap():
    temp = prev_col
    prev_col = cur_col  
    cur_col = temp
    // Update base indices accordingly
```

**Memory Usage**: O(window_size) instead of O(score_length × performance_length)

## Performance Characteristics

### Time Complexity
- **Per Note**: O(window_size) ≈ O(20) for typical window
- **Total**: O(window_size × num_performance_notes)

### Space Complexity
- **Active Memory**: O(window_size) for two columns
- **Window Size**: Typically 21 cells (10 + 1 + 10)

### Real-Time Performance
- **Target**: Process each note within microseconds
- **Scaling**: Linear with window size, independent of total score length

## Algorithm Output and Reporting

### Match Reporting

```serpent
if cur.value > top_score and report:
    result.match_stime = cur_cevt.time      // Score time of match
    result.pos = rk - 1                     // Score position (0-based)
    result.matches = top_score              // Confidence score
    top_score = cur.value
```

### Confidence Scoring

The algorithm maintains a running confidence score based on:
- Cumulative match credits minus penalties
- Higher values indicate stronger alignment confidence
- Sudden drops may indicate tracking errors

## Integration with Real-Time Systems

### Virtual Clock Synchronization

```serpent
VirtualTime = (R - Rref) * S + Vref
```
Where:
- `R` = current real time
- `Rref` = last reset time
- `S` = speed of virtual clock  
- `Vref` = virtual score time at last reset

### Accompaniment Timing

The algorithm provides real-time position estimates for:
- Automated accompaniment synchronization
- Score display following
- Performance analysis recording

## Key Algorithmic Innovations

1. **Compound Event Grouping**: Handles chords as single units
2. **Ornament-Aware Matching**: Specialized handling for trills and grace notes
3. **Adaptive Timing Constraints**: IOI-based note grouping with score-aware limits
4. **Sliding Window Optimization**: Bounded memory usage for real-time performance
5. **Multi-Credit System**: Differentiated rewards for different note types

## Conclusion

The dynamic score following algorithm represents a sophisticated real-time sequence alignment system specifically designed for musical performance tracking. Its key strengths lie in:

- **Musical Intelligence**: Understanding of ornaments, chord structures, and timing conventions
- **Real-Time Performance**: Bounded computation and memory usage
- **Robustness**: Graceful handling of extra notes, missing notes, and timing variations
- **Extensibility**: Parameterized credit/penalty system for different musical styles

The algorithm successfully balances the competing demands of accuracy, real-time performance, and musical understanding, making it suitable for both research applications and practical musical systems.