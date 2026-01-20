#!/usr/bin/env python3
"""Examine multi-token entries to understand MIDDLE patterns."""

import json
from collections import Counter
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(RESULTS_DIR / 'entry_data.json') as f:
    entries = json.load(f)

print("=" * 70)
print("MULTI-TOKEN ENTRY ANALYSIS")
print("=" * 70)

# Look at entries with 2+ tokens
multi_entries = [e for e in entries if e['n_tokens'] >= 2]
print(f"\nMulti-token entries: {len(multi_entries)}")

# Check MIDDLE patterns
print("\nExamining MIDDLE patterns in multi-token entries:\n")

# Sample some entries
for e in multi_entries[:20]:
    tokens = [t['token'] for t in e['tokens']]
    middles = [t['middle'] for t in e['tokens']]
    unique_middles = set(middles)

    print(f"  {e['folio']} L{e['line']}: {' '.join(tokens)}")
    print(f"    MIDDLEs: {middles}")
    print(f"    Unique: {len(unique_middles)} ({unique_middles})")
    print()

# Statistics on MIDDLE repetition
print("=" * 70)
print("MIDDLE REPETITION STATISTICS")
print("=" * 70)

same_middle_count = 0
diff_middle_count = 0

for e in multi_entries:
    middles = [t['middle'] for t in e['tokens']]
    unique = set(middles)
    if len(unique) == 1:
        same_middle_count += 1
    else:
        diff_middle_count += 1
        print(f"  DIFFERENT: {e['folio']} L{e['line']}: MIDDLEs = {middles}")

print(f"\n  Same MIDDLE repeated: {same_middle_count} ({100*same_middle_count/len(multi_entries):.1f}%)")
print(f"  Different MIDDLEs: {diff_middle_count} ({100*diff_middle_count/len(multi_entries):.1f}%)")

# What about PREFIX variation?
print("\n" + "=" * 70)
print("PREFIX VARIATION IN MULTI-TOKEN ENTRIES")
print("=" * 70)

same_prefix = 0
diff_prefix = 0

for e in multi_entries:
    prefixes = [t['prefix'] for t in e['tokens']]
    unique = set(prefixes)
    if len(unique) == 1:
        same_prefix += 1
    else:
        diff_prefix += 1

print(f"\n  Same PREFIX: {same_prefix} ({100*same_prefix/len(multi_entries):.1f}%)")
print(f"  Different PREFIXes: {diff_prefix} ({100*diff_prefix/len(multi_entries):.1f}%)")

# And SUFFIX?
print("\n" + "=" * 70)
print("SUFFIX VARIATION IN MULTI-TOKEN ENTRIES")
print("=" * 70)

same_suffix = 0
diff_suffix = 0

for e in multi_entries:
    suffixes = [t['suffix'] for t in e['tokens']]
    unique = set(suffixes)
    if len(unique) == 1:
        same_suffix += 1
    else:
        diff_suffix += 1

print(f"\n  Same SUFFIX: {same_suffix} ({100*same_suffix/len(multi_entries):.1f}%)")
print(f"  Different SUFFIXes: {diff_suffix} ({100*diff_suffix/len(multi_entries):.1f}%)")
