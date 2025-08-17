#!/usr/bin/env python3
"""Test the CEVENT pattern matching."""

import re
from config import LOG_PATTERNS

# Test the cevent pattern
cevent_pattern = LOG_PATTERNS['cevent_summary']
print(f"Pattern: {cevent_pattern}")

# Test some example lines
test_lines = [
    "CEVENT|row:83|score_time:12.5|pitch_count:3|time_span:0.0|ornament_count:2|expected:4",
    "CEVENT|row:1|score_time:0.0|pitch_count:1|time_span:0.0|ornament_count:0|expected:1",
    "CEVENT|row:100|score_time:-1.5|pitch_count:5|time_span:0.25|ornament_count:10|expected:15"
]

compiled_pattern = re.compile(cevent_pattern)

for line in test_lines:
    match = compiled_pattern.match(line)
    if match:
        print(f"✅ MATCHED: {line}")
        print(f"   Groups: {match.groups()}")
    else:
        print(f"❌ NO MATCH: {line}")
    print()