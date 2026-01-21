#!/usr/bin/env python3
"""Analyze records with multiple RI tokens."""

import json
from collections import defaultdict, Counter

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

# Group by line
lines = defaultdict(list)
for t in tokens:
    line_key = f"{t['folio']}.{t['line']}"
    lines[line_key].append(t)

# Analyze lines with 2+ RI
multi_ri_lines = []

for line_key, line_tokens in lines.items():
    ri_positions = [i for i, t in enumerate(line_tokens) if t['middle_class'] == 'exclusive']

    if len(ri_positions) >= 2:
        # Calculate gaps
        gaps = [ri_positions[i+1] - ri_positions[i] for i in range(len(ri_positions)-1)]

        # Check clustering
        has_adjacent = any(g == 1 for g in gaps)
        all_adjacent = all(g == 1 for g in gaps)
        max_gap = max(gaps)
        min_gap = min(gaps)

        # Get folio info
        folio = line_tokens[0]['folio']
        section = line_tokens[0].get('section', 'UNK')

        multi_ri_lines.append({
            'line_key': line_key,
            'folio': folio,
            'section': section,
            'line_length': len(line_tokens),
            'ri_count': len(ri_positions),
            'ri_positions': ri_positions,
            'gaps': gaps,
            'has_adjacent': has_adjacent,
            'all_adjacent': all_adjacent,
            'max_gap': max_gap,
            'ri_tokens': [line_tokens[i]['token'] for i in ri_positions],
            'ri_middles': [line_tokens[i]['middle'] for i in ri_positions],
            'all_tokens': [t['token'] for t in line_tokens],
            'ri_ratio': len(ri_positions) / len(line_tokens)
        })

print("=" * 70)
print("MULTI-RI RECORD ANALYSIS")
print("=" * 70)
print()

print(f"Total lines with 2+ RI: {len(multi_ri_lines)}")
print()

# Clustering analysis
has_adjacent = sum(1 for l in multi_ri_lines if l['has_adjacent'])
all_adjacent = sum(1 for l in multi_ri_lines if l['all_adjacent'])

print("CLUSTERING:")
print(f"  Lines with at least one adjacent RI pair: {has_adjacent} ({100*has_adjacent/len(multi_ri_lines):.1f}%)")
print(f"  Lines where ALL RI are adjacent: {all_adjacent} ({100*all_adjacent/len(multi_ri_lines):.1f}%)")
print()

# Gap distribution
all_gaps = []
for l in multi_ri_lines:
    all_gaps.extend(l['gaps'])

gap_dist = Counter(all_gaps)
print("GAP DISTRIBUTION (between consecutive RI tokens):")
for gap in sorted(gap_dist.keys()):
    count = gap_dist[gap]
    pct = 100 * count / len(all_gaps)
    bar = '#' * int(pct / 2)
    label = "ADJACENT" if gap == 1 else ""
    print(f"  Gap {gap:2d}: {count:3d} ({pct:5.1f}%) {bar} {label}")
print()

# Folio distribution
folio_counts = Counter(l['folio'] for l in multi_ri_lines)
print(f"FOLIO DISTRIBUTION (top 15):")
for folio, count in folio_counts.most_common(15):
    print(f"  {folio}: {count} multi-RI lines")
print()

# Section distribution
section_counts = Counter(l['section'] for l in multi_ri_lines)
print("SECTION DISTRIBUTION:")
for section, count in section_counts.most_common():
    # Compare to overall A distribution
    print(f"  {section}: {count} ({100*count/len(multi_ri_lines):.1f}%)")
print()

# RI count distribution
ri_count_dist = Counter(l['ri_count'] for l in multi_ri_lines)
print("RI COUNT DISTRIBUTION (among multi-RI lines):")
for ri_count in sorted(ri_count_dist.keys()):
    count = ri_count_dist[ri_count]
    print(f"  {ri_count} RI tokens: {count} lines")
print()

# Line length analysis
print("LINE LENGTH ANALYSIS:")
lengths = [l['line_length'] for l in multi_ri_lines]
print(f"  Mean line length: {sum(lengths)/len(lengths):.1f} tokens")
print(f"  Min: {min(lengths)}, Max: {max(lengths)}")

# Compare to overall A line length
all_lengths = [len(toks) for toks in lines.values()]
print(f"  (Overall A mean: {sum(all_lengths)/len(all_lengths):.1f} tokens)")
print()

# RI ratio in multi-RI lines
print("RI RATIO IN MULTI-RI LINES:")
ratios = [l['ri_ratio'] for l in multi_ri_lines]
print(f"  Mean RI ratio: {100*sum(ratios)/len(ratios):.1f}%")
high_ri = sum(1 for r in ratios if r >= 0.5)
print(f"  Lines with >=50% RI: {high_ri}")
print()

# Pure RI lines (100% RI)
pure_ri = [l for l in multi_ri_lines if l['ri_ratio'] == 1.0]
print(f"PURE RI LINES (100% RI): {len(pure_ri)}")
for l in pure_ri:
    print(f"  {l['line_key']}: {l['all_tokens']}")
print()

# High RI lines (>=50%)
print("HIGH RI LINES (>=50%):")
high_ri_lines = sorted([l for l in multi_ri_lines if l['ri_ratio'] >= 0.5],
                       key=lambda x: -x['ri_ratio'])
for l in high_ri_lines[:10]:
    print(f"  {l['line_key']}: {l['ri_count']}/{l['line_length']} = {100*l['ri_ratio']:.0f}%")
    print(f"    RI: {l['ri_tokens']}")
    print(f"    Full: {' '.join(l['all_tokens'])}")
    print()

# Look for patterns in adjacent RI
print("=" * 70)
print("ADJACENT RI PAIRS - MIDDLE ANALYSIS")
print("=" * 70)
print()

adjacent_pairs = []
for l in multi_ri_lines:
    for i, gap in enumerate(l['gaps']):
        if gap == 1:
            adjacent_pairs.append({
                'middle1': l['ri_middles'][i],
                'middle2': l['ri_middles'][i+1],
                'token1': l['ri_tokens'][i],
                'token2': l['ri_tokens'][i+1],
                'folio': l['folio'],
                'line': l['line_key']
            })

print(f"Total adjacent RI pairs: {len(adjacent_pairs)}")
print()

# Do same MIDDLEs appear together?
pair_keys = Counter((p['middle1'], p['middle2']) for p in adjacent_pairs)
print("MIDDLE pair frequencies (adjacent):")
for (m1, m2), count in pair_keys.most_common(10):
    print(f"  {m1} + {m2}: {count}")
print()

# What MIDDLEs appear in adjacent pairs?
middles_in_adjacent = Counter()
for p in adjacent_pairs:
    middles_in_adjacent[p['middle1']] += 1
    middles_in_adjacent[p['middle2']] += 1

print("MIDDLEs that appear in adjacent pairs (top 15):")
for middle, count in middles_in_adjacent.most_common(15):
    print(f"  {middle}: {count} appearances")
print()

# Folio concentration of adjacent pairs
adjacent_folios = Counter(p['folio'] for p in adjacent_pairs)
print("FOLIOS with adjacent RI pairs:")
for folio, count in adjacent_folios.most_common():
    print(f"  {folio}: {count} adjacent pairs")
