"""
04_h_cluster_function.py - h-cluster (ch/sh/pch/d) functional analysis

These MIDDLEs correlate with HIGH_H (phase monitoring).
Also overlap with C907 -hy infrastructure.

Questions:
- What distinguishes ch from sh from pch?
- Line position patterns?
- PREFIX patterns?
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

# Get Currier B tokens
b_tokens = list(tx.currier_b())

# Find h-cluster tokens
h_cluster = ['ch', 'sh', 'pch', 'd', 'opch']
h_tokens = defaultdict(list)

for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle in h_cluster:
        h_tokens[m.middle].append({
            'word': t.word,
            'folio': t.folio,
            'section': t.section,
            'line': t.line,
            'line_initial': t.line_initial,
            'line_final': t.line_final,
            'prefix': m.prefix,
            'suffix': m.suffix
        })

print("h-Cluster Token Counts:")
for mid, tokens in sorted(h_tokens.items(), key=lambda x: -len(x[1])):
    print(f"  {mid}: {len(tokens)}")

# Analyze each h-cluster MIDDLE
for mid in h_cluster:
    tokens = h_tokens.get(mid, [])
    if len(tokens) < 20:
        continue

    print(f"\n" + "="*70)
    print(f"{mid.upper()} MIDDLE ANALYSIS (n={len(tokens)})")
    print("="*70)

    # PREFIX distribution
    print("\n--- PREFIX Distribution ---")
    prefix_counts = Counter(t['prefix'] for t in tokens)
    for prefix, count in prefix_counts.most_common(8):
        pct = 100*count/len(tokens)
        print(f"  {prefix or '(none)'}: {count} ({pct:.1f}%)")

    # SUFFIX distribution
    print("\n--- SUFFIX Distribution ---")
    suffix_counts = Counter(t['suffix'] for t in tokens)
    for suffix, count in suffix_counts.most_common(8):
        pct = 100*count/len(tokens)
        print(f"  {suffix or '(none)'}: {count} ({pct:.1f}%)")

    # Section distribution
    print("\n--- Section Distribution ---")
    section_counts = Counter(t['section'] for t in tokens)
    for section, count in section_counts.most_common():
        pct = 100*count/len(tokens)
        print(f"  {section}: {count} ({pct:.1f}%)")

    # Line position
    print("\n--- Line Position ---")
    positions = []
    for t in tokens:
        total_pos = t['line_initial'] + t['line_final'] - 1
        if total_pos > 0:
            norm_pos = (t['line_initial'] - 1) / total_pos
            positions.append(norm_pos)

    if positions:
        print(f"  Mean: {np.mean(positions):.3f}")
        print(f"  Std: {np.std(positions):.3f}")
        # Position breakdown
        early = sum(1 for p in positions if p < 0.33)
        mid = sum(1 for p in positions if 0.33 <= p < 0.67)
        late = sum(1 for p in positions if p >= 0.67)
        print(f"  Early (<0.33): {early} ({100*early/len(positions):.1f}%)")
        print(f"  Mid (0.33-0.67): {mid} ({100*mid/len(positions):.1f}%)")
        print(f"  Late (>=0.67): {late} ({100*late/len(positions):.1f}%)")

    # Top token forms
    print("\n--- Top Token Forms ---")
    form_counts = Counter(t['word'] for t in tokens)
    for form, count in form_counts.most_common(8):
        print(f"  {form}: {count}")

# Compare line positions across h-cluster
print("\n" + "="*70)
print("LINE POSITION COMPARISON ACROSS h-CLUSTER")
print("="*70)

print(f"\n{'MIDDLE':<10} {'Mean Pos':>10} {'Std':>8} {'Early%':>8} {'Mid%':>8} {'Late%':>8}")
print("-"*60)

for mid in h_cluster:
    tokens = h_tokens.get(mid, [])
    if len(tokens) < 20:
        continue

    positions = []
    for t in tokens:
        total_pos = t['line_initial'] + t['line_final'] - 1
        if total_pos > 0:
            norm_pos = (t['line_initial'] - 1) / total_pos
            positions.append(norm_pos)

    if positions:
        early = 100*sum(1 for p in positions if p < 0.33)/len(positions)
        mid_pct = 100*sum(1 for p in positions if 0.33 <= p < 0.67)/len(positions)
        late = 100*sum(1 for p in positions if p >= 0.67)/len(positions)
        print(f"{mid:<10} {np.mean(positions):>10.3f} {np.std(positions):>8.3f} {early:>8.1f} {mid_pct:>8.1f} {late:>8.1f}")

# -hy suffix analysis for h-cluster
print("\n" + "="*70)
print("-hy SUFFIX RATE IN h-CLUSTER")
print("="*70)

for mid in h_cluster:
    tokens = h_tokens.get(mid, [])
    if len(tokens) < 20:
        continue

    hy_count = sum(1 for t in tokens if t['suffix'] == 'hy')
    hy_rate = 100 * hy_count / len(tokens)
    print(f"  {mid}: {hy_rate:.1f}% -hy suffix ({hy_count}/{len(tokens)})")

# Save results
output = {
    'h_cluster_counts': {mid: len(tokens) for mid, tokens in h_tokens.items()},
    'by_middle': {}
}

for mid in h_cluster:
    tokens = h_tokens.get(mid, [])
    if len(tokens) >= 20:
        positions = []
        for t in tokens:
            total_pos = t['line_initial'] + t['line_final'] - 1
            if total_pos > 0:
                positions.append((t['line_initial'] - 1) / total_pos)

        output['by_middle'][mid] = {
            'count': len(tokens),
            'prefix_distribution': dict(Counter(t['prefix'] for t in tokens)),
            'suffix_distribution': dict(Counter(t['suffix'] for t in tokens)),
            'section_distribution': dict(Counter(t['section'] for t in tokens)),
            'mean_position': float(np.mean(positions)) if positions else None,
            'top_forms': dict(Counter(t['word'] for t in tokens).most_common(10))
        }

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_DEEPENING/results/h_cluster_function.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to h_cluster_function.json")
