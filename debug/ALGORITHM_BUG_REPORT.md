# Algorithm Bug Report: Invalid Cell Time Initialization

## Summary
Discovered a bug in the score following algorithm where Cell objects are initialized with `time = -1`, causing invalid IOI (Inter-Onset Interval) calculations that result in nonsensical timing constraints.

## Bug Location
**File**: `src/score_follower_v18_trill.srp`
**Lines**: 293, 840, 1422, 1429

## Bug Details

### Root Cause
```serpent
class Cell:
    def init(v)
        value = v
        used = []
        time = -1        # BUG: Invalid initialization value
        trill_time = -1
        unused_count = 0
```

### How the Bug Manifests
1. `oowcell = Cell(SF_NINF)` creates a cell with `time = -1` (line 840)
2. When algorithm goes out of window bounds: `prev = oowcell` (line 1422)
3. IOI calculation: `var ioi = time - prev.time = 28.307 - (-1) = 29.307` (line 1429)
4. This creates impossibly large IOI values (29+ seconds) that fail all timing constraints

### Impact
- Causes numerous false timing constraint failures
- Generates misleading "excess" values (e.g., 29207.3ms excess)
- Makes legitimate no-match failures look like timing issues
- Impacts algorithm's ability to match notes when using uninitialized cells

## Evidence from Logs
```
TIMING|pt:-1|ct:28.3073|ioi:29.3073|span:0|lim:0.1|pass:nil|type:chord_basic
```
- `pt:-1`: Previous time is uninitialized 
- `ioi:29.3073`: Calculated as 28.3073 - (-1) = 29.3073
- Result: Fails 0.1s timing limit by 29+ seconds

## Proposed Fixes

### Option 1: Use Current Time for Uninitialized Cells
```serpent
def init(v)
    value = v
    used = []
    time = 0  # or use current performance time when available
    trill_time = 0
    unused_count = 0
```

### Option 2: Add Initialization Flag
```serpent
class Cell:
    var value
    var used
    var time
    var trill_time  
    var unused_count
    var initialized  # NEW: track initialization state
    
    def init(v)
        value = v
        used = []
        time = -1
        trill_time = -1
        unused_count = 0
        initialized = false  # NEW
```

Then skip timing checks for uninitialized cells:
```serpent
if prev.initialized:
    var ioi = time - prev.time
    // proceed with timing checks
else:
    // skip timing constraints for uninitialized cells
```

### Option 3: Different Out-of-Window Strategy
Instead of using `oowcell` with invalid time, use a different strategy for out-of-window cells that doesn't require timing calculations.

## Recommendation
**Option 2** (initialization flag) is safest as it:
- Preserves existing algorithm logic
- Makes the initialization state explicit
- Allows proper handling of uninitialized vs. valid cells
- Minimal risk of introducing new bugs

## Next Steps
1. Choose fix strategy
2. Implement and test fix
3. Verify that "timing failures" disappear for legitimate cases
4. Re-run debug analysis to get accurate failure categorization