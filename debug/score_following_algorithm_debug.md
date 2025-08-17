# Score Following Algorithm: Algorithm-Flow Debugging Guide

## Overview

This document provides a comprehensive debugging methodology for the EllieScoreFollowing implementation, organized around the **actual algorithm execution flow** to enable systematic identification and resolution of score following failures.

## CSV Field Organization for Algorithm-Flow Debugging

The CSV output is organized to **match the actual algorithm execution flow** for systematic debugging:

### SECTION 1: INPUT CONTEXT (Columns 1-3) - What triggered this analysis?
1. **INPUT** - Performance note that triggered analysis (input_column, input_pitch, input_perf_time)
2. **MATRIX** - Algorithm state: search window position and bounds
3. **CEVENT** - Target score event being evaluated in this DP cell

### SECTION 2: DP COMPUTATION (Columns 4-7) - Core algorithm execution in order
4. **CELL** - Previous DP cell state (starting point for computation)
5. **VRULE** - Vertical rule: cost of skipping score event (applied first)
6. **TIMING** - Timing constraint validation (critical gate for horizontal rule)
7. **HRULE** - Horizontal rule: performance note matching logic

### SECTION 3: MUSICAL ANALYSIS (Columns 8-10) - Musical context evaluation
8. **MATCHTYPE** - Musical context classification (chord/trill/grace/extra)
9. **ORNAMENT** - Ornament-specific processing details
10. **DECISION** - Final DP cell decision (vrule vs hrule winner)

### SECTION 4: ALGORITHM RESULT (Columns 11-12) - Final DP computation
11. **DP** - Summary of DP computation for this cell
12. **SCORE** - How does this cell compete globally?

### SECTION 5: FINAL OUTCOME (Columns 13-15) - Overall INPUT block result
13. **RESULT** - Final classification (match/no_match/unprocessed)
14. **MATCH** - Match details (populated only if successful)
15. **NO_MATCH** - No-match details (populated only if failed)

### SECTION 6: DEBUGGING CONTEXT (Columns 16-17) - Analysis and diagnostics
16. **ARRAY** - DP matrix neighborhood for validation
17. **BUG** - Algorithm bug detection and systematic issues

## Algorithm-Flow Debugging Methodology

### Phase 1: Input Context Analysis (Columns 1-3)

#### Step 1.1: Performance Input Validation
**Goal**: Verify the performance note that triggered the analysis
**Focus**: Column 1 (INPUT)

**Key Questions**:
- Is `input_pitch` reasonable for the musical context?
- Does `input_perf_time` show appropriate timing progression?
- Are there gaps or clusters in `input_column` sequence?

**Red Flags**:
- Extreme pitch values (< 20 or > 108 MIDI)
- Negative or backwards time progression
- Missing `input_column` sequences indicating dropped notes

#### Step 1.2: Search Window State Analysis
**Goal**: Assess whether the algorithm is looking in the right place
**Focus**: Column 2 (MATRIX)

**Critical Checks**:
- `matrix_window_center` should be near expected score position
- `matrix_window_start` and `matrix_window_end` should bracket plausible matches
- Window movement should be smooth and musically motivated

**Window State Diagnosis**:
```python
# Healthy window characteristics
window_size = matrix_window_end - matrix_window_start
reasonable_size = 15 <= window_size <= 25
center_in_window = matrix_window_start <= matrix_window_center <= matrix_window_end
```

**Common Window Problems**:
- **Window too narrow**: `window_size < 10` (may miss correct matches)
- **Window mispositioned**: `matrix_window_center` far from `cevent_row`
- **Erratic movement**: Large jumps in `matrix_window_center` between inputs

#### Step 1.3: Target Score Event Analysis
**Goal**: Understand what the algorithm is trying to match against
**Focus**: Column 3 (CEVENT)

**Score Event Validation**:
- `cevent_score_time` vs `input_perf_time` alignment reasonableness
- `cevent_expected` count matches musical complexity
- `cevent_ornament_count` indicates ornament handling requirements

**Ornament Complexity Assessment**:
```python
ornament_complexity = cevent_ornament_count / cevent_expected
# High complexity (>0.5) indicates significant ornament processing needed
```

### Phase 2: DP Computation Analysis (Columns 4-7)

#### Step 2.1: Previous Cell State Validation
**Goal**: Ensure DP computation starts from valid state
**Focus**: Column 4 (CELL)

**Critical State Checks**:
- `cell_time` should not be -1 except for initialization
- `cell_value` should show reasonable DP score progression
- `cell_used_pitches` should contain musically logical pitch sets
- `cell_unused_count` should match expected notes remaining

**State Initialization Bug Detection**:
```python
has_initialization_bug = (cell_time == -1.0) and (input_column > 1)
# First input can have cell_time = -1, but subsequent inputs should not
```

#### Step 2.2: Vertical Rule Analysis
**Goal**: Understand cost of skipping score events
**Focus**: Column 5 (VRULE)

**Vertical Rule Formula**: `new_score = up_value - penalty`
- `vrule_up_value`: Score from cell above
- `vrule_penalty`: Cost based on `dcm * unused_count`
- `vrule_result`: Final vertical rule score

**Vertical Rule Problems**:
- **Excessive skipping**: Very high penalties for skipping complex chords
- **Wrong penalties**: `vrule_penalty` not matching `dcm * unused_count`
- **Start point issues**: `vrule_start_point` handling edge cases incorrectly

#### Step 2.3: Timing Constraint Analysis (Critical Gate)
**Goal**: Determine if timing allows horizontal rule matching
**Focus**: Column 6 (TIMING)

**Timing Validation Logic**:
```python
ioi = timing_curr_perf_time - timing_prev_cell_time
timing_passes = (ioi < timing_limit) or (timing_prev_cell_time == -1)
```

**Timing Constraint Types**:
- **chord**: `timing_limit = cevent_time_span + 0.1`
- **trill**: `timing_limit = trill_max_ioi` (typically 0.2s)
- **grace**: `timing_limit = grace_max_ioi` (typically 0.1s)

**Timing Failure Analysis**:
```python
timing_violation = timing_pass == "nil"
severe_violation = timing_ioi > (timing_limit * 2)
# Severe violations indicate parameter tuning needed
```

#### Step 2.4: Horizontal Rule Analysis
**Goal**: Understand performance note matching logic
**Focus**: Column 7 (HRULE)

**Horizontal Rule Cases** (in order of evaluation):
1. **Chord Match**: `hrule_match_type = "chord_matched"`
2. **Trill Match**: `hrule_match_type = "trill_matched"`
3. **Grace Match**: `hrule_match_type = "grace_matched"`
4. **Extra Note**: `hrule_match_type = "extra"`

**Credit Assignment Validation**:
- Chord matches: `credit = dmc = 2`
- Trill matches: `credit = dmc = 2` (same as chord)
- Grace matches: `credit = dgc = 1` (reduced)
- Extra notes: `penalty = dce = 1`

### Phase 3: Musical Analysis (Columns 8-10)

#### Step 3.1: Musical Context Classification
**Goal**: Verify correct identification of musical context
**Focus**: Column 8 (MATCHTYPE)

**Classification Validation**:
```python
# Mutually exclusive classifications
is_chord = matchtype_is_chord == "t"
is_trill = matchtype_is_trill == "t"
is_grace = matchtype_is_grace == "t"
is_extra = matchtype_is_extra == "t"

# Only one should be true
classification_count = sum([is_chord, is_trill, is_grace, is_extra])
valid_classification = classification_count <= 1
```

**Common Misclassification Patterns**:
- **Trill misidentified as chord**: Check `matchtype_ornament_info`
- **Grace note timing**: `matchtype_timing_ok` vs actual timing constraints
- **Already used logic**: `matchtype_already_used` preventing valid rematches

#### Step 3.2: Ornament Processing Validation
**Goal**: Ensure ornaments are handled according to musical rules
**Focus**: Column 9 (ORNAMENT)

**Ornament Type Analysis**:
- `ornament_type`: Should match `hrule_match_type` for ornament cases
- `ornament_credit_applied`: Should match expected credit values
- Ignore pitches: Should receive 0 credit but no penalty

**Ornament Processing Rules**:
```python
# Trill processing
if ornament_type == "trill_matched":
    expected_credit = 2  # dmc
    credit_correct = ornament_credit_applied == expected_credit

# Grace processing  
if ornament_type == "grace_matched":
    expected_credit = 1  # dgc
    credit_correct = ornament_credit_applied == expected_credit
```

#### Step 3.3: DP Decision Analysis
**Goal**: Validate the final choice between vertical and horizontal rules
**Focus**: Column 10 (DECISION)

**Decision Logic Validation**:
```python
vertical_wins = decision_vertical_result >= decision_horizontal_result
horizontal_wins = decision_horizontal_result > decision_vertical_result

expected_winner = "vertical" if vertical_wins else "horizontal"
actual_winner = decision_winner

decision_consistent = (expected_winner == actual_winner)
```

**Decision Quality Assessment**:
- **Clear winner**: Large margin between `decision_vertical_result` and `decision_horizontal_result`
- **Close call**: Small margin may indicate parameter sensitivity
- **Wrong winner**: `decision_winner` doesn't match higher score

### Phase 4: Algorithm Result Analysis (Columns 11-12)

#### Step 4.1: DP Computation Summary Validation
**Goal**: Verify DP computation summary matches detailed analysis
**Focus**: Column 11 (DP)

**Summary Consistency Checks**:
```python
# DP summary should match decision results
dp_vertical_matches_vrule = abs(dp_vertical_rule - vrule_result) < 0.001
dp_horizontal_matches_hrule = abs(dp_horizontal_rule - hrule_result) < 0.001
dp_final_matches_decision = abs(dp_final_value - decision_final_value) < 0.001
```

**Match Flag Validation**:
```python
# dp_match should be 1 only if horizontal rule won and had positive credit
horizontal_won = decision_winner == "horizontal"
positive_credit = hrule_result > hrule_prev_value
dp_match_correct = (dp_match == 1) == (horizontal_won and positive_credit)
```

#### Step 4.2: Global Score Competition Analysis
**Goal**: Understand how this cell competes across all possibilities
**Focus**: Column 12 (SCORE)

**Competition Metrics**:
- `score_beats_top`: Does this cell beat the current best?
- `score_margin`: How much better/worse than current best?
- `score_confidence`: Algorithm's confidence in this match

**Competition Analysis**:
```python
beats_top = score_beats_top == "t"
significant_margin = abs(score_margin) > 1.0
high_confidence = score_confidence > 0.8

strong_match = beats_top and significant_margin and high_confidence
```

### Phase 5: Final Outcome Analysis (Columns 13-15)

#### Step 5.1: Result Classification Validation
**Goal**: Verify INPUT block outcome is correctly classified
**Focus**: Column 13 (RESULT)

**Result Type Logic**:
```python
# Result should be based on best scoring cell across all rows
has_match = match_row > 0
has_no_match = no_match_pitch > 0
result_consistent = (
    (result_type == "match" and has_match and not has_no_match) or
    (result_type == "no_match" and has_no_match and not has_match) or
    (result_type == "unprocessed" and not has_match and not has_no_match)
)
```

#### Step 5.2: Match Details Validation
**Goal**: Verify successful match details are reasonable
**Focus**: Column 14 (MATCH)

**Match Validation Checks**:
```python
if result_type == "match":
    # Match details should be populated
    valid_match_row = 1 <= match_row <= max_score_events
    valid_match_pitch = 20 <= match_pitch <= 108
    reasonable_score = match_score >= 0
    
    # Match should correspond to input
    pitch_matches = match_pitch == input_pitch
    time_matches = abs(match_perf_time - input_perf_time) < 0.001
```

#### Step 5.3: No-Match Analysis
**Goal**: Understand why no match was found
**Focus**: Column 15 (NO_MATCH)

**No-Match Diagnosis**:
```python
if result_type == "no_match":
    # Analyze why no match occurred
    timing_failures = timing_pass == "nil"
    window_misposition = matrix_window_center_far_from_expected
    insufficient_score = all_scores_below_threshold
```

### Phase 6: Debugging Context Analysis (Columns 16-17)

#### Step 6.1: DP Matrix Neighborhood Validation
**Goal**: Validate DP computation within local context
**Focus**: Column 16 (ARRAY)

**Neighborhood Consistency**:
```python
# Center value should match dp_final_value
center_matches = abs(array_center_value - dp_final_value) < 0.001

# Neighbor values should show reasonable progression
neighbor_values = parse_neighbor_values(array_neighbor_values)
reasonable_progression = check_dp_progression(neighbor_values)
```

#### Step 6.2: Systematic Bug Detection
**Goal**: Identify algorithmic bugs and parameter issues
**Focus**: Column 17 (BUG)

**Bug Pattern Detection**:
```python
# Known bug patterns
timing_initialization_bug = bug_has_timing_bug
systematic_failure = bug_description.contains("systematic")
parameter_sensitivity = bug_description.contains("parameter")
```

## Systematic Debugging Workflow

### 1. Rapid Triage (Columns 1, 13-15)
```python
# Quick assessment of INPUT block outcomes
def rapid_triage(csv_data):
    success_rate = (csv_data['result_type'] == 'match').mean()
    failure_patterns = csv_data[csv_data['result_type'] == 'no_match']
    
    # Identify failure clusters
    failure_times = failure_patterns['input_perf_time']
    temporal_clusters = find_temporal_clusters(failure_times)
    
    return {
        'success_rate': success_rate,
        'failure_clusters': temporal_clusters,
        'dominant_failure_cause': analyze_failure_causes(failure_patterns)
    }
```

### 2. Algorithm State Analysis (Columns 2-3)
```python
def analyze_algorithm_state(failures):
    # Window positioning analysis
    window_issues = failures[
        abs(failures['matrix_window_center'] - failures['cevent_row']) > 5
    ]
    
    # Target complexity analysis
    complex_targets = failures[failures['cevent_ornament_count'] > 2]
    
    return {
        'window_misposition_rate': len(window_issues) / len(failures),
        'ornament_failure_rate': len(complex_targets) / len(failures)
    }
```

### 3. DP Computation Analysis (Columns 4-7)
```python
def analyze_dp_computation(failures):
    # Timing constraint failures
    timing_failures = failures[failures['timing_pass'] == 'nil']
    
    # Vertical vs horizontal rule analysis
    vertical_wins = failures[failures['decision_winner'] == 'vertical']
    horizontal_fails = failures[
        (failures['hrule_timing_pass'] == 'nil') | 
        (failures['hrule_match_type'] == 'extra')
    ]
    
    return {
        'timing_constraint_failure_rate': len(timing_failures) / len(failures),
        'excessive_skipping_rate': len(vertical_wins) / len(failures),
        'horizontal_rule_failure_rate': len(horizontal_fails) / len(failures)
    }
```

### 4. Musical Context Analysis (Columns 8-10)
```python
def analyze_musical_context(failures):
    # Ornament processing issues
    ornament_failures = failures[failures['ornament_type'] != '']
    misclassifications = failures[
        (failures['matchtype_is_chord'] == 't') & 
        (failures['ornament_type'].str.contains('trill|grace'))
    ]
    
    return {
        'ornament_processing_failure_rate': len(ornament_failures) / len(failures),
        'classification_error_rate': len(misclassifications) / len(failures)
    }
```

### 5. Parameter Tuning Recommendations
```python
def generate_tuning_recommendations(analysis_results):
    recommendations = []
    
    # Timing constraint adjustments
    if analysis_results['timing_constraint_failure_rate'] > 0.3:
        recommendations.append("Increase timing limits: trill_max_ioi, grace_max_ioi")
    
    # DP cost rebalancing
    if analysis_results['excessive_skipping_rate'] > 0.5:
        recommendations.append("Decrease dcm (cost of missing notes)")
    
    # Window size adjustments
    if analysis_results['window_misposition_rate'] > 0.2:
        recommendations.append("Increase win_half_len for wider search window")
    
    return recommendations
```

## Algorithm Performance Optimization

### Critical Path Analysis

Based on the algorithm execution flow, the **critical performance bottlenecks** are:

1. **Timing Constraint Evaluation** (Column 6): Most frequent failure point
2. **Musical Context Classification** (Column 8): Computational complexity
3. **Window Management** (Column 2): Search space optimization
4. **Ornament Processing** (Column 9): Special case handling

### Performance Tuning Guidelines

#### 1. Timing Parameter Optimization
```python
# Adaptive timing limits based on musical context
def adaptive_timing_limits(cevent):
    base_limit = cevent.time_span + 0.1
    if cevent.ornament_count > 0:
        return base_limit * 1.5  # More lenient for ornaments
    return base_limit
```

#### 2. Window Size Optimization
```python
# Dynamic window sizing based on performance complexity
def adaptive_window_size(performance_regularity):
    base_size = 10
    if performance_regularity < 0.7:  # Irregular performance
        return base_size * 1.5
    return base_size
```

#### 3. DP Cost Function Tuning
```python
# Context-sensitive cost parameters
def adaptive_dp_costs(musical_context):
    if musical_context.has_ornaments:
        return {'dcm': 1.5, 'dce': 0.5}  # More forgiving for ornaments
    return {'dcm': 2.0, 'dce': 1.0}  # Standard costs
```

This algorithm-flow debugging methodology enables systematic identification of performance bottlenecks and targeted optimization of the score following system based on the actual execution sequence and musical context.