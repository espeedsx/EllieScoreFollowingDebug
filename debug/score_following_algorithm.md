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