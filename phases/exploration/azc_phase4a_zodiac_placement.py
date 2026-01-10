#!/usr/bin/env python3
"""
AZC-DEEP Phase 4a: Zodiac Family Placement Grammar
===================================================

Analyzes placement patterns within Cluster 0 (Zodiac-dominated family).

Tests:
1. Subscript transition legality (R1→R2→R3, S→S1→S2)
2. Placement bigram/trigram patterns
3. Run-length distributions per placement class
4. Radial progression constraints
5. Self-transition enrichment

Cluster 0 folios (13): f57v + all 12 Zodiac (f70v1, f70v2, f71r, f71v,
f72r1, f72r2, f72r3, f72v1, f72v2, f72v3, f73r, f73v)

Output: results/azc_phase4a_zodiac_placement.json
"""

import json
import os
import math
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC-DEEP PHASE 4a: ZODIAC FAMILY PLACEMENT GRAMMAR")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

print("\nLoading data...")

# Load cluster assignments
with open('results/azc_folio_clusters.json', 'r', encoding='utf-8') as f:
    cluster_data = json.load(f)

cluster_assignments = cluster_data['cluster_assignments']

# Cluster 0 folios (Zodiac family)
cluster0_folios = set(f for f, c in cluster_assignments.items() if c == 0)
print(f"Cluster 0 folios: {sorted(cluster0_folios)}")

# Load transcription data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract Cluster 0 tokens
cluster0_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        lang = row.get('language', '')
        folio = row.get('folio', '')
        if lang in ('NA', '') and folio in cluster0_folios:
            cluster0_tokens.append(row)

print(f"Cluster 0 tokens: {len(cluster0_tokens)}")

# =============================================================================
# PLACEMENT SEQUENCE EXTRACTION
# =============================================================================

print("\nExtracting placement sequences...")

# Group tokens by folio, preserving order
folio_sequences = defaultdict(list)
for t in cluster0_tokens:
    folio = t.get('folio', '')
    placement = t.get('placement', 'UNK')
    folio_sequences[folio].append({
        'word': t.get('word', ''),
        'placement': placement,
        'line': t.get('line_number', ''),
        'line_initial': t.get('line_initial', ''),
        'line_final': t.get('line_final', '')
    })

# Build continuous placement sequences per folio
all_placements = []
for folio in sorted(folio_sequences.keys()):
    seq = [t['placement'] for t in folio_sequences[folio]]
    all_placements.extend(seq)

print(f"Total placement tokens: {len(all_placements)}")

# Placement code inventory
placement_counts = Counter(all_placements)
print(f"\nPlacement codes in Cluster 0:")
for code, count in placement_counts.most_common(20):
    print(f"  {code}: {count} ({count/len(all_placements)*100:.1f}%)")

# =============================================================================
# TEST 1: PLACEMENT BIGRAM ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 1: PLACEMENT BIGRAM TRANSITIONS")
print("=" * 70)

# Build bigram counts
bigram_counts = Counter()
for i in range(len(all_placements) - 1):
    bigram = (all_placements[i], all_placements[i+1])
    bigram_counts[bigram] += 1

total_bigrams = sum(bigram_counts.values())
print(f"\nTotal bigrams: {total_bigrams}")
print(f"Unique bigram types: {len(bigram_counts)}")

# Compute expected frequencies under independence
placement_freq = {p: c/len(all_placements) for p, c in placement_counts.items()}

def expected_bigram(p1, p2, total):
    """Expected count under independence."""
    return placement_freq.get(p1, 0) * placement_freq.get(p2, 0) * total

# Find enriched and depleted transitions
enriched = []
depleted = []
forbidden = []

for (p1, p2), observed in bigram_counts.items():
    expected = expected_bigram(p1, p2, total_bigrams)
    if expected > 0:
        ratio = observed / expected
        if ratio > 2.0 and observed >= 10:
            enriched.append((p1, p2, observed, expected, ratio))
        elif ratio < 0.3 and expected >= 5:
            depleted.append((p1, p2, observed, expected, ratio))

# Find forbidden (never observed but expected)
all_codes = list(placement_counts.keys())
for p1 in all_codes:
    for p2 in all_codes:
        if (p1, p2) not in bigram_counts:
            expected = expected_bigram(p1, p2, total_bigrams)
            if expected >= 3:  # Should have occurred at least 3 times
                forbidden.append((p1, p2, 0, expected))

print(f"\n--- ENRICHED TRANSITIONS (ratio > 2x, n >= 10) ---")
enriched.sort(key=lambda x: -x[4])
for p1, p2, obs, exp, ratio in enriched[:15]:
    print(f"  {p1} -> {p2}: obs={obs}, exp={exp:.1f}, ratio={ratio:.1f}x")

print(f"\n--- SELF-TRANSITIONS ---")
self_trans = [(p, bigram_counts.get((p, p), 0),
               expected_bigram(p, p, total_bigrams),
               bigram_counts.get((p, p), 0) / expected_bigram(p, p, total_bigrams)
               if expected_bigram(p, p, total_bigrams) > 0 else 0)
              for p in all_codes if placement_counts[p] >= 20]
self_trans.sort(key=lambda x: -x[3])
for p, obs, exp, ratio in self_trans[:10]:
    if exp > 0:
        print(f"  {p} -> {p}: obs={obs}, exp={exp:.1f}, ratio={ratio:.1f}x")

print(f"\n--- FORBIDDEN TRANSITIONS (expected >= 3, observed = 0) ---")
forbidden.sort(key=lambda x: -x[3])
for p1, p2, obs, exp in forbidden[:15]:
    print(f"  {p1} -> {p2}: expected={exp:.1f}, NEVER OBSERVED")

# =============================================================================
# TEST 2: ORDERED SUBSCRIPT TRANSITIONS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 2: ORDERED SUBSCRIPT TRANSITIONS")
print("=" * 70)

# R-series transitions
r_codes = ['R', 'R1', 'R2', 'R3', 'R4']
s_codes = ['S', 'S0', 'S1', 'S2']

print("\n--- R-SERIES TRANSITION MATRIX ---")
print(f"{'From/To':<8}" + "".join(f"{c:<8}" for c in r_codes))
for p1 in r_codes:
    row = f"{p1:<8}"
    for p2 in r_codes:
        count = bigram_counts.get((p1, p2), 0)
        row += f"{count:<8}"
    print(row)

print("\n--- S-SERIES TRANSITION MATRIX ---")
print(f"{'From/To':<8}" + "".join(f"{c:<8}" for c in s_codes))
for p1 in s_codes:
    row = f"{p1:<8}"
    for p2 in s_codes:
        count = bigram_counts.get((p1, p2), 0)
        row += f"{count:<8}"
    print(row)

# Test for ordering constraints
print("\n--- SUBSCRIPT ORDERING TESTS ---")

# R1 -> R2 -> R3 forward direction
r_forward = bigram_counts.get(('R1', 'R2'), 0) + bigram_counts.get(('R2', 'R3'), 0)
r_backward = bigram_counts.get(('R3', 'R2'), 0) + bigram_counts.get(('R2', 'R1'), 0)
print(f"R-series forward (R1->R2, R2->R3): {r_forward}")
print(f"R-series backward (R3->R2, R2->R1): {r_backward}")
if r_forward + r_backward > 0:
    r_directionality = r_forward / (r_forward + r_backward)
    print(f"R-series forward bias: {r_directionality:.1%}")

# S -> S1 -> S2 forward direction
s_forward = bigram_counts.get(('S', 'S1'), 0) + bigram_counts.get(('S1', 'S2'), 0)
s_backward = bigram_counts.get(('S2', 'S1'), 0) + bigram_counts.get(('S1', 'S'), 0)
print(f"\nS-series forward (S->S1, S1->S2): {s_forward}")
print(f"S-series backward (S2->S1, S1->S): {s_backward}")
if s_forward + s_backward > 0:
    s_directionality = s_forward / (s_forward + s_backward)
    print(f"S-series forward bias: {s_directionality:.1%}")

# =============================================================================
# TEST 3: RUN-LENGTH ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 3: PLACEMENT RUN-LENGTH DISTRIBUTION")
print("=" * 70)

def compute_runs(sequence):
    """Compute run lengths for each placement code."""
    if not sequence:
        return {}

    runs = defaultdict(list)
    current_code = sequence[0]
    current_length = 1

    for code in sequence[1:]:
        if code == current_code:
            current_length += 1
        else:
            runs[current_code].append(current_length)
            current_code = code
            current_length = 1

    # Don't forget the last run
    runs[current_code].append(current_length)

    return runs

all_runs = compute_runs(all_placements)

print(f"\n{'Code':<8} {'Runs':<8} {'Mean':<8} {'Max':<8} {'1s%':<10} {'2+%':<10}")
print("-" * 55)

run_stats = {}
for code in sorted(all_runs.keys(), key=lambda x: -len(all_runs[x])):
    runs = all_runs[code]
    if len(runs) >= 5:
        mean_len = sum(runs) / len(runs)
        max_len = max(runs)
        ones_pct = sum(1 for r in runs if r == 1) / len(runs) * 100
        two_plus_pct = sum(1 for r in runs if r >= 2) / len(runs) * 100

        run_stats[code] = {
            'count': len(runs),
            'mean': mean_len,
            'max': max_len,
            'ones_pct': ones_pct
        }

        print(f"{code:<8} {len(runs):<8} {mean_len:<8.2f} {max_len:<8} {ones_pct:<10.1f} {two_plus_pct:<10.1f}")

# =============================================================================
# TEST 4: PLACEMENT TRIGRAMS (CONTEXT PATTERNS)
# =============================================================================

print("\n" + "=" * 70)
print("TEST 4: PLACEMENT TRIGRAM PATTERNS")
print("=" * 70)

trigram_counts = Counter()
for i in range(len(all_placements) - 2):
    trigram = (all_placements[i], all_placements[i+1], all_placements[i+2])
    trigram_counts[trigram] += 1

print(f"\nTotal trigrams: {sum(trigram_counts.values())}")
print(f"Unique trigram types: {len(trigram_counts)}")

print("\n--- TOP 20 TRIGRAMS ---")
for (p1, p2, p3), count in trigram_counts.most_common(20):
    print(f"  {p1} -> {p2} -> {p3}: {count}")

# Look for structured patterns
print("\n--- SUBSCRIPT PROGRESSION TRIGRAMS ---")
subscript_trigrams = [(t, c) for t, c in trigram_counts.items()
                       if any(x in t for x in ['R1', 'R2', 'R3', 'S1', 'S2'])]
subscript_trigrams.sort(key=lambda x: -x[1])
for (p1, p2, p3), count in subscript_trigrams[:15]:
    print(f"  {p1} -> {p2} -> {p3}: {count}")

# =============================================================================
# TEST 5: PLACEMENT × LINE POSITION
# =============================================================================

print("\n" + "=" * 70)
print("TEST 5: PLACEMENT × LINE POSITION")
print("=" * 70)

# Count placements by line position
line_initial_placements = Counter()
line_final_placements = Counter()
interior_placements = Counter()

for folio, tokens in folio_sequences.items():
    for t in tokens:
        placement = t['placement']
        is_initial = t.get('line_initial', '') == '1'
        is_final = t.get('line_final', '') == '1'

        if is_initial:
            line_initial_placements[placement] += 1
        elif is_final:
            line_final_placements[placement] += 1
        else:
            interior_placements[placement] += 1

total_initial = sum(line_initial_placements.values())
total_final = sum(line_final_placements.values())
total_interior = sum(interior_placements.values())

print(f"\nLine-initial tokens: {total_initial}")
print(f"Line-final tokens: {total_final}")
print(f"Interior tokens: {total_interior}")

print(f"\n{'Code':<8} {'Initial%':<12} {'Final%':<12} {'Interior%':<12} {'Boundary?':<12}")
print("-" * 60)

for code in sorted(placement_counts.keys(), key=lambda x: -placement_counts[x]):
    if placement_counts[code] >= 20:
        init_pct = line_initial_placements.get(code, 0) / placement_counts[code] * 100
        final_pct = line_final_placements.get(code, 0) / placement_counts[code] * 100
        int_pct = interior_placements.get(code, 0) / placement_counts[code] * 100
        boundary_pct = init_pct + final_pct

        boundary_type = ""
        if boundary_pct > 70:
            boundary_type = "BOUNDARY"
        elif boundary_pct < 30:
            boundary_type = "INTERIOR"
        else:
            boundary_type = "MIXED"

        print(f"{code:<8} {init_pct:<12.1f} {final_pct:<12.1f} {int_pct:<12.1f} {boundary_type:<12}")

# =============================================================================
# TEST 6: CROSS-FOLIO PLACEMENT CONSISTENCY
# =============================================================================

print("\n" + "=" * 70)
print("TEST 6: CROSS-FOLIO PLACEMENT CONSISTENCY")
print("=" * 70)

# Compare placement distributions across folios
folio_placement_dists = {}
for folio, tokens in folio_sequences.items():
    placements = [t['placement'] for t in tokens]
    total = len(placements)
    if total > 0:
        dist = {p: placements.count(p)/total for p in set(placements)}
        folio_placement_dists[folio] = dist

# Compute pairwise Jensen-Shannon similarity
def js_similarity(p, q):
    all_keys = set(p.keys()) | set(q.keys())
    p_sum = sum(p.values())
    q_sum = sum(q.values())
    if p_sum == 0 or q_sum == 0:
        return 0.0

    p_norm = {k: p.get(k, 0) / p_sum for k in all_keys}
    q_norm = {k: q.get(k, 0) / q_sum for k in all_keys}
    m = {k: (p_norm[k] + q_norm[k]) / 2 for k in all_keys}

    def kl(a, b):
        return sum(a[k] * math.log2(a[k] / b[k]) for k in all_keys if a[k] > 0 and b[k] > 0)

    js_div = (kl(p_norm, m) + kl(q_norm, m)) / 2
    return 1.0 - js_div

# Zodiac vs Zodiac
zodiac_folios = [f for f in folio_placement_dists.keys() if f.startswith('f7')]
if len(zodiac_folios) >= 2:
    zodiac_sims = []
    for i, f1 in enumerate(zodiac_folios):
        for f2 in zodiac_folios[i+1:]:
            sim = js_similarity(folio_placement_dists[f1], folio_placement_dists[f2])
            zodiac_sims.append(sim)

    if zodiac_sims:
        mean_zodiac_sim = sum(zodiac_sims) / len(zodiac_sims)
        print(f"\nZodiac folio placement similarity (JS): {mean_zodiac_sim:.3f}")
        print(f"  Min: {min(zodiac_sims):.3f}, Max: {max(zodiac_sims):.3f}")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("PHASE 4a SUMMARY: ZODIAC FAMILY PLACEMENT GRAMMAR")
print("=" * 70)

summary = {
    'total_tokens': len(cluster0_tokens),
    'total_placements': len(all_placements),
    'unique_placement_codes': len(placement_counts),
    'bigram_analysis': {
        'total_bigrams': total_bigrams,
        'unique_bigrams': len(bigram_counts),
        'enriched_count': len(enriched),
        'forbidden_count': len(forbidden)
    },
    'subscript_ordering': {
        'r_forward': r_forward,
        'r_backward': r_backward,
        'r_directionality': r_directionality if r_forward + r_backward > 0 else 0,
        's_forward': s_forward,
        's_backward': s_backward,
        's_directionality': s_directionality if s_forward + s_backward > 0 else 0
    },
    'run_stats': run_stats,
    'placement_counts': dict(placement_counts),
    'top_bigrams': [(f"{p1}->{p2}", c) for (p1, p2), c in bigram_counts.most_common(30)],
    'top_trigrams': [(f"{p1}->{p2}->{p3}", c) for (p1, p2, p3), c in trigram_counts.most_common(20)]
}

# Key findings
print("\nKEY FINDINGS:")
print(f"1. Placement codes: {len(placement_counts)} distinct codes in Zodiac family")
print(f"2. Bigram structure: {len(enriched)} enriched, {len(forbidden)} forbidden transitions")

if r_forward + r_backward > 0:
    if r_directionality > 0.7:
        print(f"3. R-series: STRONG forward bias ({r_directionality:.0%})")
    elif r_directionality > 0.5:
        print(f"3. R-series: Weak forward bias ({r_directionality:.0%})")
    else:
        print(f"3. R-series: Backward bias ({r_directionality:.0%})")

if s_forward + s_backward > 0:
    if s_directionality > 0.7:
        print(f"4. S-series: STRONG forward bias ({s_directionality:.0%})")
    elif s_directionality > 0.5:
        print(f"4. S-series: Weak forward bias ({s_directionality:.0%})")
    else:
        print(f"4. S-series: Backward bias ({s_directionality:.0%})")

# Self-transition summary
high_self = [p for p, obs, exp, ratio in self_trans if ratio > 5 and exp > 0]
if high_self:
    print(f"5. High self-transition codes: {', '.join(high_self)}")

# =============================================================================
# SAVE RESULTS
# =============================================================================

output_path = 'results/azc_phase4a_zodiac_placement.json'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"\n[OK] Results saved to: {output_path}")
print("=" * 70)
