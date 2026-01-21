#!/usr/bin/env python3
"""Analyze singleton PP MIDDLEs - what makes them special?"""

import json
from collections import Counter, defaultdict

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json') as f:
    tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    mc = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])

# Count PP MIDDLE frequencies
pp_middle_counts = Counter()
pp_middle_tokens = defaultdict(list)

for t in tokens:
    if t['middle'] not in ri_middles:
        pp_middle_counts[t['middle']] += 1
        pp_middle_tokens[t['middle']].append(t)

# Get singleton PP MIDDLEs
singleton_middles = [m for m, c in pp_middle_counts.items() if c == 1]
high_freq_middles = [m for m, c in pp_middle_counts.items() if c >= 50]

print("=" * 60)
print("SINGLETON PP MIDDLE ANALYSIS")
print("=" * 60)
print()

# PREFIX distribution
singleton_prefixes = Counter()
highfreq_prefixes = Counter()

for m in singleton_middles:
    for t in pp_middle_tokens[m]:
        singleton_prefixes[t['prefix']] += 1

for m in high_freq_middles:
    for t in pp_middle_tokens[m]:
        highfreq_prefixes[t['prefix']] += 1

print("PREFIX distribution:")
print(f"{'PREFIX':<8} {'Singleton':>10} {'High-freq':>10} {'Ratio':>10}")
print("-" * 45)

all_prefixes = set(singleton_prefixes.keys()) | set(highfreq_prefixes.keys())
for p in sorted(all_prefixes, key=lambda x: singleton_prefixes[x] + highfreq_prefixes[x], reverse=True)[:12]:
    s = singleton_prefixes[p]
    h = highfreq_prefixes[p]
    ratio = s / h if h > 0 else float('inf')
    print(f"{p:<8} {s:>10} {h:>10} {ratio:>10.2f}")
print()

# SUFFIX distribution
singleton_suffixes = Counter()
highfreq_suffixes = Counter()

for m in singleton_middles:
    for t in pp_middle_tokens[m]:
        singleton_suffixes[t['suffix']] += 1

for m in high_freq_middles:
    for t in pp_middle_tokens[m]:
        highfreq_suffixes[t['suffix']] += 1

print("SUFFIX distribution:")
print(f"{'SUFFIX':<8} {'Singleton':>10} {'High-freq':>10}")
print("-" * 35)

all_suffixes = set(singleton_suffixes.keys()) | set(highfreq_suffixes.keys())
for s in sorted(all_suffixes, key=lambda x: singleton_suffixes[x] + highfreq_suffixes[x], reverse=True)[:10]:
    sing = singleton_suffixes[s]
    high = highfreq_suffixes[s]
    print(f"{s if s else '(empty)':<8} {sing:>10} {high:>10}")
print()

# Folio distribution
singleton_folios = set()
for m in singleton_middles:
    for t in pp_middle_tokens[m]:
        singleton_folios.add(t['folio'])

print(f"Singleton PP MIDDLEs appear in {len(singleton_folios)} folios")
print()

# MIDDLE length distribution
singleton_lengths = [len(m) for m in singleton_middles]
highfreq_lengths = [len(m) for m in high_freq_middles]

print("MIDDLE length:")
print(f"  Singletons: mean={sum(singleton_lengths)/len(singleton_lengths):.1f}, range={min(singleton_lengths)}-{max(singleton_lengths)}")
print(f"  High-freq: mean={sum(highfreq_lengths)/len(highfreq_lengths):.1f}, range={min(highfreq_lengths)}-{max(highfreq_lengths)}")
print()

# Show singleton examples with full token
print("SINGLETON PP MIDDLE EXAMPLES (full tokens):")
for m in singleton_middles[:20]:
    t = pp_middle_tokens[m][0]
    print(f"  {t['token']:<15} prefix={t['prefix']:<4} middle={m:<8} suffix={t['suffix']:<4} folio={t['folio']}")
