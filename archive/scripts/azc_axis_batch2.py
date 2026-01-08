#!/usr/bin/env python3
"""
AZC Axis Connectivity Tests - Batch 2

Tests:
- Test 2: Placement × Repetition
- Test 3: Placement × Line Boundary
- Test 5: Placement × A Section (H/P/T)
- Test 11: Section × Placement Distribution
"""

import json
import os
from collections import Counter, defaultdict
import math

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC AXIS CONNECTIVITY TESTS - BATCH 2")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract tokens
azc_tokens = []
a_tokens = []
b_tokens = []

for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        lang = row.get('language', '')
        if lang == 'NA' or lang == '':
            azc_tokens.append(row)
        elif lang == 'A':
            a_tokens.append(row)
        elif lang == 'B':
            b_tokens.append(row)

# Get AZC-only vocabulary
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

# Shared vocabulary
shared_ab = azc_words.intersection(a_words).intersection(b_words)

print(f"\nLoaded {len(azc_only_tokens)} AZC-only tokens")
print(f"Shared A+B vocabulary: {len(shared_ab)} types")

# =============================================================================
# TEST 2: PLACEMENT × REPETITION
# =============================================================================

print("\n" + "=" * 70)
print("TEST 2: PLACEMENT × REPETITION")
print("=" * 70)

# Group by folio
by_folio = defaultdict(list)
for t in azc_only_tokens:
    by_folio[t.get('folio', '')].append(t)

# For each folio, count repetitions per placement class
placement_repetitions = defaultdict(list)  # placement -> list of repetition counts

for folio, tokens in by_folio.items():
    # Count words per placement in this folio
    placement_words = defaultdict(Counter)
    for t in tokens:
        placement = t.get('placement', 'UNK')
        word = t['word']
        placement_words[placement][word] += 1

    # For each placement, record max repetition count
    for placement, word_counts in placement_words.items():
        for word, count in word_counts.items():
            if count > 1:  # Only track actual repetitions
                placement_repetitions[placement].append(count)

print("\nRepetition depth by placement class:")
print(f"{'Placement':<10} {'Rep Events':<12} {'Mean Depth':<12} {'Max Depth':<10}")
print("-" * 50)

placement_rep_stats = {}
for placement in sorted(placement_repetitions.keys()):
    reps = placement_repetitions[placement]
    if reps:
        mean_rep = sum(reps) / len(reps)
        max_rep = max(reps)
        placement_rep_stats[placement] = {
            'count': len(reps),
            'mean': mean_rep,
            'max': max_rep
        }
        print(f"{placement:<10} {len(reps):<12} {mean_rep:<12.2f} {max_rep:<10}")

# Test correlation between placement and repetition
print("\n--- Placement classes by mean repetition depth ---")
sorted_by_rep = sorted(placement_rep_stats.items(), key=lambda x: -x[1]['mean'])
for p, stats in sorted_by_rep[:10]:
    print(f"  {p}: mean={stats['mean']:.2f}, max={stats['max']}, events={stats['count']}")

# =============================================================================
# TEST 3: PLACEMENT × LINE BOUNDARY
# =============================================================================

print("\n" + "=" * 70)
print("TEST 3: PLACEMENT × LINE BOUNDARY")
print("=" * 70)

# Check line_initial and line_final by placement
placement_boundary = defaultdict(lambda: {'initial': 0, 'final': 0, 'total': 0})

for t in azc_only_tokens:
    placement = t.get('placement', 'UNK')
    placement_boundary[placement]['total'] += 1

    # Check line_initial
    li = t.get('line_initial', '')
    if li == '1' or li == 1:
        placement_boundary[placement]['initial'] += 1

    # Check line_final
    lf = t.get('line_final', '')
    if lf == '1' or lf == 1:
        placement_boundary[placement]['final'] += 1

print("\nLine boundary concentration by placement:")
print(f"{'Placement':<10} {'Total':<8} {'Initial':<10} {'Init %':<10} {'Final':<8} {'Final %':<10}")
print("-" * 65)

boundary_stats = {}
for placement in sorted(placement_boundary.keys()):
    stats = placement_boundary[placement]
    if stats['total'] >= 50:  # Only significant placements
        init_pct = stats['initial'] / stats['total'] * 100
        final_pct = stats['final'] / stats['total'] * 100
        boundary_stats[placement] = {
            'total': stats['total'],
            'initial': stats['initial'],
            'initial_pct': init_pct,
            'final': stats['final'],
            'final_pct': final_pct
        }
        print(f"{placement:<10} {stats['total']:<8} {stats['initial']:<10} {init_pct:<10.1f} {stats['final']:<8} {final_pct:<10.1f}")

# Identify boundary-specialist placements
print("\n--- Boundary specialists ---")
for p, stats in boundary_stats.items():
    if stats['initial_pct'] > 50:
        print(f"  {p}: LINE-INITIAL specialist ({stats['initial_pct']:.1f}%)")
    if stats['final_pct'] > 50:
        print(f"  {p}: LINE-FINAL specialist ({stats['final_pct']:.1f}%)")

# =============================================================================
# TEST 5: PLACEMENT × A SECTION (H/P/T)
# =============================================================================

print("\n" + "=" * 70)
print("TEST 5: PLACEMENT × A SECTION (via nearby shared vocabulary)")
print("=" * 70)

# For each AZC-only token, look at nearby shared vocabulary and determine
# which A-section that vocabulary comes from

# First, build A-section vocabulary maps
a_section_vocab = defaultdict(set)
for t in a_tokens:
    section = t.get('section', '')
    word = t['word']
    a_section_vocab[section].add(word)

print(f"\nA-section vocabulary sizes:")
for sec in ['H', 'P', 'T']:
    print(f"  {sec}: {len(a_section_vocab[sec])} types")

# Group all AZC tokens by line
by_line = defaultdict(list)
for t in azc_tokens:  # All AZC tokens, not just unique
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t)

# For each AZC-only token, find nearby shared vocab and its A-section affiliation
placement_section_affinity = defaultdict(Counter)

for key, line_tokens in by_line.items():
    for i, t in enumerate(line_tokens):
        if t['word'] not in azc_only:
            continue

        placement = t.get('placement', 'UNK')

        # Look at neighboring tokens (±2)
        neighbors = []
        for j in range(max(0, i-2), min(len(line_tokens), i+3)):
            if j != i:
                neighbors.append(line_tokens[j]['word'])

        # Check which A-section the neighbors belong to
        for neighbor in neighbors:
            if neighbor in shared_ab:
                for sec in ['H', 'P', 'T']:
                    if neighbor in a_section_vocab[sec]:
                        placement_section_affinity[placement][sec] += 1

print("\nPlacement × A-section affinity (via shared neighbors):")
print(f"{'Placement':<10} {'H':<8} {'P':<8} {'T':<8} {'Dominant':<10}")
print("-" * 50)

for placement in sorted(placement_section_affinity.keys()):
    counts = placement_section_affinity[placement]
    total = sum(counts.values())
    if total >= 20:
        h_pct = counts['H'] / total * 100 if total else 0
        p_pct = counts['P'] / total * 100 if total else 0
        t_pct = counts['T'] / total * 100 if total else 0
        dominant = max(counts, key=counts.get) if counts else 'N/A'
        print(f"{placement:<10} {h_pct:<8.1f} {p_pct:<8.1f} {t_pct:<8.1f} {dominant:<10}")

# =============================================================================
# TEST 11: SECTION × PLACEMENT DISTRIBUTION
# =============================================================================

print("\n" + "=" * 70)
print("TEST 11: AZC SECTION × PLACEMENT DISTRIBUTION")
print("=" * 70)

# Check if Z, A, C sections have different placement profiles
section_placement = defaultdict(Counter)
for t in azc_only_tokens:
    section = t.get('section', '')
    placement = t.get('placement', '')
    section_placement[section][placement] += 1

print("\nPlacement distribution by AZC section:")
all_placements = sorted(set(p for counts in section_placement.values() for p in counts.keys()))

# Header
header_str = f"{'Section':<10}"
for p in all_placements[:10]:  # Top 10 placements
    header_str += f"{p:<8}"
print(header_str)
print("-" * 90)

section_profiles = {}
for section in ['Z', 'A', 'C']:
    if section in section_placement:
        counts = section_placement[section]
        total = sum(counts.values())
        row = f"{section:<10}"
        profile = {}
        for p in all_placements[:10]:
            pct = counts[p] / total * 100 if total else 0
            row += f"{pct:<8.1f}"
            profile[p] = pct
        print(row)
        section_profiles[section] = profile

# Chi-square test for section-placement independence
print("\n--- Testing Section-Placement Independence ---")

def chi_square_contingency(data):
    """Simple chi-square calculation."""
    sections = list(data.keys())
    placements = sorted(set(p for counts in data.values() for p in counts.keys()))

    # Build matrix
    n = sum(sum(data[s].values()) for s in sections)
    row_totals = {s: sum(data[s].values()) for s in sections}
    col_totals = {p: sum(data[s].get(p, 0) for s in sections) for p in placements}

    chi2 = 0
    for s in sections:
        for p in placements:
            observed = data[s].get(p, 0)
            expected = (row_totals[s] * col_totals[p]) / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    k = min(len(sections), len(placements))
    cramers_v = math.sqrt(chi2 / (n * (k - 1))) if k > 1 and n > 0 else 0

    return chi2, cramers_v

chi2, v = chi_square_contingency(section_placement)
print(f"Chi-square: {chi2:.2f}")
print(f"Cramer's V: {v:.3f}")

if v >= 0.3:
    print("Result: STRONG section-placement dependency")
elif v >= 0.2:
    print("Result: MODERATE section-placement dependency")
elif v >= 0.1:
    print("Result: WEAK section-placement dependency")
else:
    print("Result: NO significant section-placement dependency")

# Identify section-specific placements
print("\n--- Section-specific placement patterns ---")
for section in ['Z', 'A', 'C']:
    if section in section_placement:
        counts = section_placement[section]
        total = sum(counts.values())
        top = counts.most_common(3)
        top_str = ", ".join(f"{p}:{c/total*100:.1f}%" for p, c in top)
        print(f"  {section}: {top_str}")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("BATCH 2 SUMMARY")
print("=" * 70)

results = {
    'test2_repetition': {
        'placement_stats': placement_rep_stats,
        'repetition_varies_by_placement': len(set(s['mean'] for s in placement_rep_stats.values() if s['count'] >= 5)) > 1
    },
    'test3_boundary': {
        'boundary_stats': boundary_stats,
        'boundary_specialists_found': any(s['initial_pct'] > 50 or s['final_pct'] > 50 for s in boundary_stats.values())
    },
    'test5_a_section': {
        'placement_section_affinity': {p: dict(c) for p, c in placement_section_affinity.items()},
    },
    'test11_section_placement': {
        'chi_square': chi2,
        'cramers_v': v,
        'section_profiles': section_profiles,
        'dependency_detected': v >= 0.1
    }
}

print(f"""
TEST 2 - Placement × Repetition:
  Repetition depth varies by placement: {results['test2_repetition']['repetition_varies_by_placement']}

TEST 3 - Placement × Line Boundary:
  Boundary specialists found: {results['test3_boundary']['boundary_specialists_found']}

TEST 5 - Placement × A Section:
  Cross-system affinity detected: {len(placement_section_affinity) > 0}

TEST 11 - Section × Placement:
  Cramer's V: {v:.3f}
  Section-placement dependency: {'DETECTED' if v >= 0.1 else 'NOT DETECTED'}
""")

# Save results
with open('phases/AZC_AXIS_axis_connectivity/batch2_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("Results saved to: phases/AZC_AXIS_axis_connectivity/batch2_results.json")
print("\n" + "=" * 70)
print("BATCH 2 COMPLETE")
print("=" * 70)
