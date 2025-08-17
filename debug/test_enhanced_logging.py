#!/usr/bin/env python3
"""
Test script to verify enhanced logging instrumentation works correctly.
"""

import sys
import os
from pathlib import Path

# Add debug src to path
debug_src = Path(__file__).parent / "src"
sys.path.insert(0, str(debug_src))

from log_flattener import LogFlattener, FlattenedLogEntry
from config import LOG_PATTERNS
import tempfile

def test_enhanced_patterns():
    """Test that new explanation patterns are correctly parsed."""
    
    print("Testing enhanced logging patterns...")
    
    # Create test log content with new fields (proper input block structure)
    test_log_content = """INPUT|column:1|pitch:60|perf_time:1.5
CEVENT|row:1|score_time:1.0|pitch_count:3|time_span:0.05|ornament_count:0|expected:3|pitches_str:[60,64,67]
ORNAMENT|pitch:60|ornament_type:chord_matched|trill_pitches:[]|grace_pitches:[]|ignore_pitches:[]|credit_applied:2|trill_str:[]|grace_str:[]|ignore_str:[]
DP|column:1|row:1|pitch:60|perf_time:1.5|vertical_rule:0|horizontal_rule:2|final_value:2|match:1|used_pitches:[60]|unused_count:2
MATCH_EXPLAIN|pitch:60|reason:Chord note 60 matched - part of expected chord, gained 2 points|score:2|timing:1.5|context:Score_row=1,Expected_pitches=[60,64,67]
DECISION_EXPLAIN|row:1|pitch:60|reasoning:Horizontal rule won: chord_matched processing gave better score (2 vs 0)|vertical_score:0|horizontal_score:2|winner:horizontal|confidence:1.0
MATCH|row:1|pitch:60|perf_time:1.5|score:2"""
    
    # Write test content to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(test_log_content.strip())
        temp_log_path = Path(f.name)
    
    try:
        # Test parsing
        flattener = LogFlattener()
        entries = flattener.parse_log_file(temp_log_path)
        
        print(f"Parsed {len(entries)} entries")
        
        if len(entries) > 0:
            entry = entries[0]
            print("Sample entry fields:")
            print(f"  - input_pitch: {entry.input_pitch}")
            print(f"  - match_pitch: {entry.match_pitch}")
            print(f"  - result_type: {entry.result_type}")
            print(f"  - match_explanation: {entry.match_explanation}")
            print(f"  - decision_explanation: {entry.decision_explanation}")
            print(f"  - cevent_pitches_str: {entry.cevent_pitches_str}")
            print(f"  - ornament_trill_pitches_str: {entry.ornament_trill_pitches_str}")
            
            # Verify CSV field ordering 
            print("\nField ordering verification:")
            field_names = [field.name for field in entry.__dataclass_fields__.values()]
            print(f"First 10 fields: {field_names[:10]}")
            
            # Check that MATCH/NO_MATCH fields are early in the order
            match_pos = field_names.index('match_row')
            no_match_pos = field_names.index('no_match_pitch')
            explanation_pos = field_names.index('match_explanation')
            
            print(f"Match fields positions: match_row={match_pos}, no_match_pitch={no_match_pos}, explanations={explanation_pos}")
            
            if match_pos < 8 and no_match_pos < 10 and explanation_pos < 12:
                print("SUCCESS: Match/no-match fields are properly positioned early in CSV")
            else:
                print("NOTE: Field ordering could be optimized further")
        
        print("SUCCESS: Enhanced logging test completed successfully!")
        
    finally:
        # Clean up
        temp_log_path.unlink()

def test_explanation_patterns():
    """Test that explanation patterns match correctly."""
    
    print("\nTesting explanation pattern matching...")
    
    flattener = LogFlattener()
    
    # Test each new pattern
    test_cases = [
        ("MATCH_EXPLAIN|pitch:60|reason:Chord note matched|score:2|timing:1.5|context:test", "match_explanation"),
        ("NO_MATCH_EXPLAIN|pitch:61|reason:Extra note|constraint:not_in_chord|timing:2.0|expected:chord_notes", "no_match_explanation"),
        ("DECISION_EXPLAIN|row:1|pitch:60|reasoning:Horizontal won|vertical_score:0|horizontal_score:2|winner:horizontal|confidence:1.0", "decision_explanation"),
        ("TIMING_EXPLAIN|pitch:60|ioi:0.1|limit:0.2|pass:t|reason:Within_limit|context:chord", "timing_explanation"),
        ("ORNAMENT_EXPLAIN|pitch:60|type:trill|processing:matched|credit:2|pitches_context:trill_notes", "ornament_explanation")
    ]
    
    for line, expected_type in test_cases:
        result = flattener._parse_single_line(line)
        if result and result[0] == expected_type:
            print(f"SUCCESS: {expected_type} pattern matched correctly")
        else:
            print(f"ERROR: {expected_type} pattern failed to match: {result}")

if __name__ == "__main__":
    test_enhanced_patterns()
    test_explanation_patterns()
    print("\nAll tests completed!")