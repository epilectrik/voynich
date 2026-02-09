#!/usr/bin/env python3
"""
Test 6: P-text Line Structure

Question: Does P-text have Currier A line structure or AZC line structure?

Key metrics:
- Currier A: median 22 tokens/line
- AZC diagram: median 8 tokens/line
- Currier B: median 31 tokens/line

If P-text is "A on AZC folios", it should have A-like line structure.
If P-text is "AZC annotation", it should have AZC-like line structure.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict
import numpy as np

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Collect tokens by category and line
ptext_lines = defaultdict(list)  # (folio, line) -> tokens
azc_diagram_lines = defaultdict(list)
currier_a_lines = defaultdict(list)
currier_b_lines = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip()
            line_num = parts[3].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            key = (folio, line_num)

            if currier == 'NA':  # AZC
                if placement == 'P' or placement.startswith('P'):
                    ptext_lines[key].append(token)
                else:
                    azc_diagram_lines[key].append(token)
            elif currier == 'A':
                currier_a_lines[key].append(token)
            elif currier == 'B':
                currier_b_lines[key].append(token)

print("=" * 70)
print("TEST 6: P-TEXT LINE STRUCTURE")
print("=" * 70)
print()

# Calculate line lengths
def line_stats(lines_dict, name):
    lengths = [len(tokens) for tokens in lines_dict.values() if len(tokens) > 0]
    if not lengths:
        return None
    return {
        'name': name,
        'n_lines': len(lengths),
        'mean': np.mean(lengths),
        'median': np.median(lengths),
        'std': np.std(lengths),
        'min': min(lengths),
        'max': max(lengths)
    }

ptext_stats = line_stats(ptext_lines, 'P-text')
azc_stats = line_stats(azc_diagram_lines, 'AZC Diagram')
a_stats = line_stats(currier_a_lines, 'Currier A')
b_stats = line_stats(currier_b_lines, 'Currier B')

print("1. LINE LENGTH COMPARISON")
print("-" * 60)
print(f"{'Category':<15} {'Lines':<8} {'Mean':<8} {'Median':<8} {'Std':<8} {'Range'}")
print("-" * 60)

for stats in [ptext_stats, azc_stats, a_stats, b_stats]:
    if stats:
        print(f"{stats['name']:<15} {stats['n_lines']:<8} {stats['mean']:<8.1f} {stats['median']:<8.1f} {stats['std']:<8.1f} {stats['min']}-{stats['max']}")

print()

# 2. Distribution comparison
print("2. LINE LENGTH DISTRIBUTION")
print("-" * 60)

def distribution_buckets(lines_dict):
    lengths = [len(tokens) for tokens in lines_dict.values() if len(tokens) > 0]
    buckets = {'1-5': 0, '6-10': 0, '11-15': 0, '16-20': 0, '21-30': 0, '31+': 0}
    for l in lengths:
        if l <= 5:
            buckets['1-5'] += 1
        elif l <= 10:
            buckets['6-10'] += 1
        elif l <= 15:
            buckets['11-15'] += 1
        elif l <= 20:
            buckets['16-20'] += 1
        elif l <= 30:
            buckets['21-30'] += 1
        else:
            buckets['31+'] += 1
    total = len(lengths)
    return {k: (v, v/total*100 if total > 0 else 0) for k, v in buckets.items()}

ptext_dist = distribution_buckets(ptext_lines)
azc_dist = distribution_buckets(azc_diagram_lines)
a_dist = distribution_buckets(currier_a_lines)

print(f"{'Bucket':<10} {'P-text':<15} {'AZC Diagram':<15} {'Currier A':<15}")
print("-" * 55)
for bucket in ['1-5', '6-10', '11-15', '16-20', '21-30', '31+']:
    p_val = f"{ptext_dist[bucket][0]} ({ptext_dist[bucket][1]:.0f}%)"
    a_val = f"{azc_dist[bucket][0]} ({azc_dist[bucket][1]:.0f}%)"
    ca_val = f"{a_dist[bucket][0]} ({a_dist[bucket][1]:.0f}%)"
    print(f"{bucket:<10} {p_val:<15} {a_val:<15} {ca_val:<15}")

print()

# 3. Statistical comparison
print("3. SIMILARITY ASSESSMENT")
print("-" * 60)

ptext_lengths = [len(tokens) for tokens in ptext_lines.values() if len(tokens) > 0]
azc_lengths = [len(tokens) for tokens in azc_diagram_lines.values() if len(tokens) > 0]
a_lengths = [len(tokens) for tokens in currier_a_lines.values() if len(tokens) > 0]

# Distance from each reference
ptext_median = np.median(ptext_lengths) if ptext_lengths else 0
azc_median = np.median(azc_lengths) if azc_lengths else 0
a_median = np.median(a_lengths) if a_lengths else 0

dist_to_azc = abs(ptext_median - azc_median)
dist_to_a = abs(ptext_median - a_median)

print(f"P-text median: {ptext_median:.1f}")
print(f"AZC diagram median: {azc_median:.1f}")
print(f"Currier A median: {a_median:.1f}")
print()
print(f"Distance P-text to AZC: {dist_to_azc:.1f}")
print(f"Distance P-text to A: {dist_to_a:.1f}")
print()

if dist_to_azc < dist_to_a:
    print("=> P-text line structure is CLOSER TO AZC than to Currier A")
    verdict = "AZC-LIKE"
elif dist_to_a < dist_to_azc:
    print("=> P-text line structure is CLOSER TO CURRIER A than to AZC")
    verdict = "A-LIKE"
else:
    print("=> P-text line structure is EQUIDISTANT from both")
    verdict = "INTERMEDIATE"

print()

# 4. Per-folio breakdown
print("4. P-TEXT LINE LENGTHS BY FOLIO")
print("-" * 60)

folio_line_lengths = defaultdict(list)
for (folio, line), tokens in ptext_lines.items():
    if len(tokens) > 0:
        folio_line_lengths[folio].append(len(tokens))

print(f"{'Folio':<12} {'Lines':<8} {'Mean':<8} {'Median':<8}")
print("-" * 40)
for folio in sorted(folio_line_lengths.keys()):
    lengths = folio_line_lengths[folio]
    print(f"{folio:<12} {len(lengths):<8} {np.mean(lengths):<8.1f} {np.median(lengths):<8.1f}")

print()
print("=" * 70)
print("VERDICT")
print("=" * 70)
print(f"""
P-text line structure: {verdict}

P-text median line length: {ptext_median:.1f} tokens
- AZC diagram median: {azc_median:.1f} tokens (distance: {dist_to_azc:.1f})
- Currier A median: {a_median:.1f} tokens (distance: {dist_to_a:.1f})

This suggests P-text is structurally {'similar to AZC annotation' if verdict == 'AZC-LIKE' else 'similar to Currier A paragraphs' if verdict == 'A-LIKE' else 'a distinct category'}.
""")
