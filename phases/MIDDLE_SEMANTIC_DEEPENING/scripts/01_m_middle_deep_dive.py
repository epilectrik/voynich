"""
01_m_middle_deep_dive.py - Deep characterization of the `m` MIDDLE

The `m` MIDDLE is 7.24x enriched in REGIME_4 (precision) folios.
Only 76 tokens - the strongest signal in MIDDLE_SEMANTIC_MAPPING.

Questions:
- What contexts does `m` appear in?
- What PREFIX/SUFFIX combinations?
- What folios? What sections?
- Line position patterns?
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import json
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# Load data
tx = Transcript()
morph = Morphology()

# Find all tokens with MIDDLE containing 'm'
m_tokens = []
all_b_tokens = list(tx.currier_b())

for t in all_b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        # Check for 'm' as MIDDLE (not just containing 'm')
        if m.middle == 'm' or m.middle == 'am' or m.middle.endswith('m'):
            m_tokens.append({
                'word': t.word,
                'folio': t.folio,
                'section': t.section,
                'line': t.line,
                'line_initial': t.line_initial,
                'line_final': t.line_final,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'articulator': m.articulator
            })

print(f"Tokens with m-containing MIDDLE: {len(m_tokens)}")

# Separate pure 'm' from 'am' and others
pure_m = [t for t in m_tokens if t['middle'] == 'm']
am_tokens = [t for t in m_tokens if t['middle'] == 'am']
other_m = [t for t in m_tokens if t['middle'] not in ['m', 'am']]

print(f"\nBreakdown:")
print(f"  Pure 'm': {len(pure_m)}")
print(f"  'am': {len(am_tokens)}")
print(f"  Other m-containing: {len(other_m)}")

# Focus on pure 'm' since that's what C910 identified
print("\n" + "="*80)
print("PURE 'm' MIDDLE ANALYSIS (n={})".format(len(pure_m)))
print("="*80)

# Section distribution
print("\n--- Section Distribution ---")
section_counts = Counter(t['section'] for t in pure_m)
total = len(pure_m)
for section, count in section_counts.most_common():
    print(f"  {section}: {count} ({100*count/total:.1f}%)")

# Folio distribution
print("\n--- Folio Distribution ---")
folio_counts = Counter(t['folio'] for t in pure_m)
for folio, count in folio_counts.most_common(10):
    print(f"  {folio}: {count}")

# PREFIX distribution
print("\n--- PREFIX Distribution ---")
prefix_counts = Counter(t['prefix'] for t in pure_m)
for prefix, count in prefix_counts.most_common():
    pct = 100*count/total
    print(f"  {prefix or '(none)'}: {count} ({pct:.1f}%)")

# SUFFIX distribution
print("\n--- SUFFIX Distribution ---")
suffix_counts = Counter(t['suffix'] for t in pure_m)
for suffix, count in suffix_counts.most_common():
    pct = 100*count/total
    print(f"  {suffix or '(none)'}: {count} ({pct:.1f}%)")

# Full token forms
print("\n--- Token Forms ---")
token_counts = Counter(t['word'] for t in pure_m)
for token, count in token_counts.most_common(15):
    print(f"  {token}: {count}")

# Line position
print("\n--- Line Position ---")
positions = []
for t in pure_m:
    # Normalize to 0-1
    total_pos = t['line_initial'] + t['line_final'] - 1
    if total_pos > 0:
        norm_pos = (t['line_initial'] - 1) / total_pos
        positions.append(norm_pos)

if positions:
    print(f"  Mean position: {np.mean(positions):.3f}")
    print(f"  Std position: {np.std(positions):.3f}")
    print(f"  Median position: {np.median(positions):.3f}")

# Compare to baseline
print("\n--- Compare to Baseline ---")
# Get baseline position for all B tokens
baseline_positions = []
for t in all_b_tokens[:5000]:  # Sample
    total_pos = t.line_initial + t.line_final - 1
    if total_pos > 0:
        norm_pos = (t.line_initial - 1) / total_pos
        baseline_positions.append(norm_pos)

print(f"  'm' mean position: {np.mean(positions):.3f}")
print(f"  Baseline mean: {np.mean(baseline_positions):.3f}")
print(f"  Difference: {np.mean(positions) - np.mean(baseline_positions):.3f}")

# Neighbors analysis - what tokens appear adjacent to 'm' tokens?
print("\n" + "="*80)
print("CONTEXT ANALYSIS - What appears near 'm' tokens?")
print("="*80)

# Build line-level index
lines = defaultdict(list)
for t in all_b_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

# Find neighbors of m tokens
m_neighbors_before = []
m_neighbors_after = []

for mt in pure_m:
    key = (mt['folio'], mt['line'])
    line_tokens = lines[key]

    # Find position of m token in line
    for i, t in enumerate(line_tokens):
        if t.word == mt['word'] and t.line_initial == mt['line_initial']:
            # Found it
            if i > 0:
                m_neighbors_before.append(line_tokens[i-1].word)
            if i < len(line_tokens) - 1:
                m_neighbors_after.append(line_tokens[i+1].word)
            break

print("\n--- Tokens BEFORE 'm' tokens ---")
before_counts = Counter(m_neighbors_before)
for token, count in before_counts.most_common(10):
    print(f"  {token}: {count}")

print("\n--- Tokens AFTER 'm' tokens ---")
after_counts = Counter(m_neighbors_after)
for token, count in after_counts.most_common(10):
    print(f"  {token}: {count}")

# Analyze 'am' MIDDLE as well
print("\n" + "="*80)
print("'am' MIDDLE ANALYSIS (n={})".format(len(am_tokens)))
print("="*80)

print("\n--- Section Distribution ---")
am_section = Counter(t['section'] for t in am_tokens)
for section, count in am_section.most_common():
    print(f"  {section}: {count} ({100*count/len(am_tokens):.1f}%)")

print("\n--- PREFIX Distribution ---")
am_prefix = Counter(t['prefix'] for t in am_tokens)
for prefix, count in am_prefix.most_common():
    print(f"  {prefix or '(none)'}: {count}")

print("\n--- Token Forms ---")
am_forms = Counter(t['word'] for t in am_tokens)
for token, count in am_forms.most_common(10):
    print(f"  {token}: {count}")

# Save results
output = {
    'pure_m': {
        'count': len(pure_m),
        'section_distribution': dict(section_counts),
        'folio_distribution': dict(folio_counts),
        'prefix_distribution': {k or 'none': v for k, v in prefix_counts.items()},
        'suffix_distribution': {k or 'none': v for k, v in suffix_counts.items()},
        'token_forms': dict(token_counts),
        'mean_position': float(np.mean(positions)) if positions else None,
        'neighbors_before': dict(before_counts),
        'neighbors_after': dict(after_counts)
    },
    'am': {
        'count': len(am_tokens),
        'section_distribution': dict(am_section),
        'prefix_distribution': {k or 'none': v for k, v in am_prefix.items()},
        'token_forms': dict(am_forms)
    },
    'tokens': pure_m
}

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_DEEPENING/results/m_middle_deep_dive.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to m_middle_deep_dive.json")
