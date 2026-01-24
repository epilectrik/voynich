#!/usr/bin/env python3
"""Check 'riech' occurrences for sensory monitoring context."""

import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read source text
with open('sources/brunschwig_1500_text.txt', encoding='utf-8') as f:
    lines = f.readlines()

print("=== 'riech' occurrences with context ===\n")

count = 0
for i, line in enumerate(lines, 1):
    if 'riech' in line.lower():
        count += 1
        context_start = max(0, i-2)
        context_end = min(len(lines), i+3)
        print(f"\n--- Match {count} at line {i} ---")
        for j in range(context_start, context_end):
            marker = ">>>" if j == i-1 else "   "
            text = lines[j].strip()[:120]
            print(f"  {marker} {j+1}: {text}")
        if count >= 30:  # Limit
            print(f"\n... (showing first 30 of {len([l for l in lines if 'riech' in l.lower()])} matches)")
            break

# Also check if any are in procedure context vs. use context
print("\n\n=== Summary: riech context analysis ===")
print("Looking for pattern: riech in procedure vs. riech in application use...")

# Most riech occurrences are in the 'uses' section (A, B, C descriptions of what the water does)
# vs. riech in the procedure section (how to make it)
