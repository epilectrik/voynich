#!/usr/bin/env python3
"""Check if singleton closers are folio-specific."""

import json
from collections import Counter, defaultdict

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

# Group by line
lines = defaultdict(list)
for t in tokens:
    line_key = f"{t['folio']}.{t['line']}"
    lines[line_key].append(t)

# Get closer details
closer_details = []
for line_key, line_tokens in lines.items():
    if len(line_tokens) > 0:
        last = line_tokens[-1]
        if last['middle_class'] == 'exclusive':
            closer_details.append({
                'middle': last['middle'],
                'token': last['token'],
                'folio': last['folio'],
                'line': line_key
            })

# Count per MIDDLE
middle_counts = Counter(c['middle'] for c in closer_details)

# Separate singletons from repeaters
singletons = [c for c in closer_details if middle_counts[c['middle']] == 1]
repeaters = [c for c in closer_details if middle_counts[c['middle']] > 1]

print("CLOSER SINGLETON ANALYSIS")
print("=" * 60)
print(f"Singleton closer tokens: {len(singletons)}")
print(f"Repeated closer tokens: {len(repeaters)}")
print()

# Check folio distribution of singletons
singleton_folios = Counter(s['folio'] for s in singletons)
print(f"Singletons spread across {len(singleton_folios)} folios")
print()

# Are there folios with many unique closers?
print("Folios with most singleton closers:")
for folio, count in singleton_folios.most_common(10):
    print(f"  {folio}: {count} unique closers")
print()

# What about the repeaters - do they repeat within or across folios?
print("REPEATED CLOSER ANALYSIS")
print("-" * 40)
repeater_middles = set(c['middle'] for c in repeaters)
print(f"Repeated closer MIDDLEs: {len(repeater_middles)}")
print()

for middle in sorted(repeater_middles, key=lambda m: -middle_counts[m]):
    occurrences = [c for c in repeaters if c['middle'] == middle]
    folios = set(c['folio'] for c in occurrences)
    print(f"{middle} ({middle_counts[middle]}x):")
    print(f"  Folios: {sorted(folios)}")
    if len(folios) < middle_counts[middle]:
        print(f"  -> Repeats within {middle_counts[middle] - len(folios) + 1} folio(s)")
    else:
        print(f"  -> Each in different folio")
    print()

# The big one: ho
print("=" * 60)
print("DETAILED: 'ho' closer distribution")
ho_closers = [c for c in closer_details if c['middle'] == 'ho']
print(f"Total 'ho' closers: {len(ho_closers)}")
ho_folios = Counter(c['folio'] for c in ho_closers)
print("By folio:")
for folio, count in ho_folios.most_common():
    print(f"  {folio}: {count}")
