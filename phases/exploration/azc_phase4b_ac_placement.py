#!/usr/bin/env python3
"""
AZC-DEEP Phase 4b: A/C Family Placement Grammar
================================================

Analyzes placement patterns within Cluster 1 (A/C-dominated family).
Contrasts with Phase 4a Zodiac findings.

Key questions:
1. Is the non-Zodiac AZC weakly structured or permissive?
2. Does it have soft placement tendencies or none at all?
3. Is it one flat regime or several sub-modes?

Cluster 1 folios (17): 8 A + 6 C + 2 H + 1 S

Output: results/azc_phase4b_ac_placement.json
"""

import json
import os
import math
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC-DEEP PHASE 4b: A/C FAMILY PLACEMENT GRAMMAR")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

print("\nLoading data...")

# Load cluster assignments
with open('results/azc_folio_clusters.json', 'r', encoding='utf-8') as f:
    cluster_data = json.load(f)

cluster_assignments = cluster_data['cluster_assignments']

# Cluster 1 folios (A/C family)
cluster1_folios = set(f for f, c in cluster_assignments.items() if c == 1)
print(f"Cluster 1 folios: {sorted(cluster1_folios)}")
print(f"Count: {len(cluster1_folios)}")

# Load folio features for section info
with open('results/azc_folio_features.json', 'r', encoding='utf-8') as f:
    feature_data = json.load(f)

folio_features = feature_data['folios']

# Show section breakdown
section_counts = Counter(folio_features[f]['section'] for f in cluster1_folios)
print(f"Section breakdown: {dict(section_counts)}")

# Load transcription data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract Cluster 1 tokens
cluster1_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        lang = row.get('language', '')
        folio = row.get('folio', '')
        if lang in ('NA', '') and folio in cluster1_folios:
            cluster1_tokens.append(row)

print(f"Cluster 1 tokens: {len(cluster1_tokens)}")

# =============================================================================
# PLACEMENT SEQUENCE EXTRACTION
# =============================================================================

print("\nExtracting placement sequences...")

# Group tokens by folio, preserving order
folio_sequences = defaultdict(list)
for t in cluster1_tokens:
    folio = t.get('folio', '')
    placement = t.get('placement', 'UNK')
    folio_sequences[folio].append({
        'word': t.get('word', ''),
        'placement': placement,
        'line': t.get('line_number', ''),
        'line_initial': t.get('line_initial', ''),
        'line_final': t.get('line_final', ''),
        'section': folio_features.get(folio, {}).get('section', 'UNK')
    })

# Build continuous placement sequences per folio
all_placements = []
for folio in sorted(folio_sequences.keys()):
    seq = [t['placement'] for t in folio_sequences[folio]]
    all_placements.extend(seq)

print(f"Total placement tokens: {len(all_placements)}")

# Placement code inventory
placement_counts = Counter(all_placements)
print(f"\nPlacement codes in Cluster 1:")
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

# Self-transition analysis
print(f"\n--- SELF-TRANSITION RATES ---")
all_codes = [p for p, c in placement_counts.most_common() if c >= 20]

self_trans = []
for p in all_codes:
    obs = bigram_counts.get((p, p), 0)
    exp = expected_bigram(p, p, total_bigrams)
    total_from_p = sum(bigram_counts.get((p, p2), 0) for p2 in all_codes)
    self_rate = obs / total_from_p if total_from_p > 0 else 0
    ratio = obs / exp if exp > 0 else 0
    self_trans.append((p, obs, exp, ratio, self_rate))

self_trans.sort(key=lambda x: -x[3])
print(f"{'Code':<8} {'Obs':<8} {'Exp':<10} {'Ratio':<10} {'Self%':<10}")
print("-" * 50)
for p, obs, exp, ratio, self_rate in self_trans:
    print(f"{p:<8} {obs:<8} {exp:<10.1f} {ratio:<10.1f} {self_rate*100:<10.1f}")

# Compare to Zodiac
print("\n--- COMPARISON TO ZODIAC (Phase 4a) ---")
print("Zodiac self-transition rates: 98-100%")
avg_self_rate = sum(x[4] for x in self_trans) / len(self_trans) if self_trans else 0
print(f"A/C family average self-transition rate: {avg_self_rate*100:.1f}%")

# Find enriched and depleted transitions
enriched = []
depleted = []

for (p1, p2), observed in bigram_counts.items():
    if p1 in all_codes and p2 in all_codes:
        expected = expected_bigram(p1, p2, total_bigrams)
        if expected > 0:
            ratio = observed / expected
            if ratio > 2.0 and observed >= 5:
                enriched.append((p1, p2, observed, expected, ratio))

print(f"\n--- ENRICHED TRANSITIONS (ratio > 2x, n >= 5) ---")
enriched.sort(key=lambda x: -x[4])
for p1, p2, obs, exp, ratio in enriched[:15]:
    print(f"  {p1} -> {p2}: obs={obs}, exp={exp:.1f}, ratio={ratio:.1f}x")

# =============================================================================
# TEST 2: RUN-LENGTH ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 2: PLACEMENT RUN-LENGTH DISTRIBUTION")
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

# Compare to Zodiac
print("\n--- COMPARISON TO ZODIAC (Phase 4a) ---")
print("Zodiac: Mean run 40-80, Max 156, 0% singletons")
if run_stats:
    avg_mean_run = sum(r['mean'] for r in run_stats.values()) / len(run_stats)
    avg_ones_pct = sum(r['ones_pct'] for r in run_stats.values()) / len(run_stats)
    print(f"A/C family: Avg mean run {avg_mean_run:.1f}, Avg singleton rate {avg_ones_pct:.1f}%")

# =============================================================================
# TEST 3: PLACEMENT x LINE POSITION
# =============================================================================

print("\n" + "=" * 70)
print("TEST 3: PLACEMENT x LINE POSITION")
print("=" * 70)

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

print(f"\n{'Code':<8} {'Initial%':<12} {'Final%':<12} {'Interior%':<12} {'Role':<12}")
print("-" * 60)

for code in sorted(placement_counts.keys(), key=lambda x: -placement_counts[x]):
    if placement_counts[code] >= 20:
        init_pct = line_initial_placements.get(code, 0) / placement_counts[code] * 100
        final_pct = line_final_placements.get(code, 0) / placement_counts[code] * 100
        int_pct = interior_placements.get(code, 0) / placement_counts[code] * 100
        boundary_pct = init_pct + final_pct

        role = ""
        if boundary_pct > 70:
            role = "BOUNDARY"
        elif boundary_pct < 30:
            role = "INTERIOR"
        else:
            role = "MIXED"

        print(f"{code:<8} {init_pct:<12.1f} {final_pct:<12.1f} {int_pct:<12.1f} {role:<12}")

# =============================================================================
# TEST 4: SECTION-SPECIFIC PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("TEST 4: SECTION-SPECIFIC PLACEMENT PATTERNS")
print("=" * 70)

# Group by section
section_placements = defaultdict(list)
for folio, tokens in folio_sequences.items():
    section = folio_features.get(folio, {}).get('section', 'UNK')
    for t in tokens:
        section_placements[section].append(t['placement'])

print(f"\n{'Section':<10} {'Tokens':<10} {'Top Placements':<50}")
print("-" * 70)

for section in sorted(section_placements.keys()):
    placements = section_placements[section]
    counts = Counter(placements)
    top3 = counts.most_common(3)
    top3_str = ", ".join(f"{p}:{c}" for p, c in top3)
    print(f"{section:<10} {len(placements):<10} {top3_str}")

# Check for section-specific placement preferences
print("\n--- PLACEMENT DISTRIBUTION BY SECTION ---")
sections = sorted(section_placements.keys())
top_codes = [p for p, c in placement_counts.most_common(6)]

print(f"{'Code':<8}" + "".join(f"{s:<12}" for s in sections))
print("-" * (8 + 12 * len(sections)))

for code in top_codes:
    row = f"{code:<8}"
    for section in sections:
        counts = Counter(section_placements[section])
        total = len(section_placements[section])
        pct = counts.get(code, 0) / total * 100 if total > 0 else 0
        row += f"{pct:<12.1f}"
    print(row)

# =============================================================================
# TEST 5: CROSS-FOLIO CONSISTENCY
# =============================================================================

print("\n" + "=" * 70)
print("TEST 5: CROSS-FOLIO PLACEMENT CONSISTENCY")
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

# All pairs
all_folios = list(folio_placement_dists.keys())
if len(all_folios) >= 2:
    all_sims = []
    for i, f1 in enumerate(all_folios):
        for f2 in all_folios[i+1:]:
            sim = js_similarity(folio_placement_dists[f1], folio_placement_dists[f2])
            all_sims.append(sim)

    if all_sims:
        mean_sim = sum(all_sims) / len(all_sims)
        print(f"\nA/C family cross-folio placement similarity (JS): {mean_sim:.3f}")
        print(f"  Min: {min(all_sims):.3f}, Max: {max(all_sims):.3f}")
        print(f"\n  Compare to Zodiac family: 0.945")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("PHASE 4b SUMMARY: A/C FAMILY PLACEMENT GRAMMAR")
print("=" * 70)

summary = {
    'total_tokens': len(cluster1_tokens),
    'total_placements': len(all_placements),
    'unique_placement_codes': len(placement_counts),
    'section_breakdown': dict(section_counts),
    'self_transition_rates': {p: rate for p, obs, exp, ratio, rate in self_trans},
    'average_self_transition': avg_self_rate,
    'run_stats': run_stats,
    'placement_counts': dict(placement_counts),
    'cross_folio_similarity': mean_sim if 'mean_sim' in dir() else 0
}

print("\nKEY FINDINGS:")
print(f"1. Placement codes: {len(placement_counts)} distinct codes")
print(f"2. Average self-transition rate: {avg_self_rate*100:.1f}% (vs Zodiac 98-100%)")
if run_stats:
    print(f"3. Average singleton rate: {avg_ones_pct:.1f}% (vs Zodiac 0%)")
    print(f"4. Average run length: {avg_mean_run:.1f} (vs Zodiac 40-80)")
if 'mean_sim' in dir():
    print(f"5. Cross-folio consistency: {mean_sim:.3f} (vs Zodiac 0.945)")

# Key contrast
print("\n" + "=" * 70)
print("CONTRAST: ZODIAC vs A/C FAMILY")
print("=" * 70)
print(f"{'Metric':<30} {'Zodiac':<20} {'A/C Family':<20}")
print("-" * 70)
print(f"{'Self-transition rate':<30} {'98-100%':<20} {f'{avg_self_rate*100:.1f}%':<20}")
if run_stats:
    print(f"{'Singleton rate':<30} {'0%':<20} {f'{avg_ones_pct:.1f}%':<20}")
    print(f"{'Mean run length':<30} {'40-80':<20} {f'{avg_mean_run:.1f}':<20}")
if 'mean_sim' in dir():
    print(f"{'Cross-folio consistency':<30} {'0.945':<20} {f'{mean_sim:.3f}':<20}")
print(f"{'Ordered subscripts':<30} {'YES (exclusive)':<20} {'NO':<20}")

# =============================================================================
# SAVE RESULTS
# =============================================================================

output_path = 'results/azc_phase4b_ac_placement.json'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"\n[OK] Results saved to: {output_path}")
print("=" * 70)
