#!/usr/bin/env python3
"""
A/C INTERNAL CHARACTERIZATION - PROBE 2: MIDDLE INCOMPATIBILITY DENSITY

Question: Are A/C folios activating more densely incompatible subsets
          of the MIDDLE space than Zodiac folios?

Method:
1. Load global MIDDLE incompatibility matrix (C475: 95.7% pairs illegal)
2. For each AZC folio, extract MIDDLE vocabulary
3. Compute local incompatibility density: (illegal pairs / total pairs among folio MIDDLEs)
4. Compare A/C family vs Zodiac family

Prediction: A/C will show higher local incompatibility density - fine discrimination
            means more mutually exclusive constraints active simultaneously.
"""

import csv
import json
import math
from collections import defaultdict, Counter
from scipy import stats
import numpy as np
from itertools import combinations

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qok', 'qot', 'qo', 'ch', 'sh', 'ok', 'ot', 'ct', 'ol', 'or', 'al', 'ar', 's', 'k', 'd', 'y', 'o', 'a']

# Zodiac AZC folios
ZODIAC_FOLIOS = {
    'f70v1', 'f70v2',
    'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
    'f57v'
}

def decompose_token(token):
    """Extract MIDDLE component from token."""
    if not token or len(token) < 2:
        return token

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break

    suffixes = ['dy', 'ey', 'ly', 'ry', 'y']
    for s in suffixes:
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break

    return token

# ============================================================
# LOAD GLOBAL INCOMPATIBILITY DATA
# ============================================================

print("=" * 70)
print("A/C x MIDDLE INCOMPATIBILITY DENSITY TEST")
print("=" * 70)
print()
print("Question: Are A/C folios activating more densely incompatible")
print("          subsets of the MIDDLE space?")
print()

# Load global incompatibility data
print("Loading global MIDDLE incompatibility data...")
with open('results/middle_incompatibility.json', 'r', encoding='utf-8') as f:
    incompat_data = json.load(f)

global_sparsity = incompat_data['summary']['sparsity']
print(f"  Global sparsity: {global_sparsity:.4f} ({global_sparsity*100:.1f}% pairs illegal)")
print()

# Build set of legal pairs from the main component
# Legal pairs are those that co-occur (observed > 0)
legal_pairs = set()
if 'strongest_bridges' in incompat_data:
    for bridge in incompat_data['strongest_bridges']:
        # Structure is [[m1, m2], count]
        pair, count = bridge
        m1, m2 = pair
        legal_pairs.add(tuple(sorted([m1, m2])))

# Also check if we have cooccurrence data
# Since the JSON may not have full co-occurrence, we'll need to recompute
# from the transcription for accurate folio-level analysis

print("Building co-occurrence matrix from transcription...")

# ============================================================
# BUILD LINE-LEVEL CO-OCCURRENCE FROM SCRATCH
# ============================================================

# Load AZC tokens and build per-line MIDDLE sets
folio_line_middles = defaultdict(lambda: defaultdict(set))
folio_family = {}
ac_folios = set()
zodiac_folios_found = set()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        language = row.get('language', '').strip()
        line_num = row.get('line_number', '0')

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        middle = decompose_token(word)
        if not middle:
            continue

        # Identify AZC folios
        if folio in ZODIAC_FOLIOS:
            zodiac_folios_found.add(folio)
            folio_line_middles[folio][line_num].add(middle)
            folio_family[folio] = 'ZODIAC'
        elif language not in ('A', 'B'):
            ac_folios.add(folio)
            folio_line_middles[folio][line_num].add(middle)
            folio_family[folio] = 'AC'

print(f"  Zodiac folios: {len(zodiac_folios_found)}")
print(f"  A/C folios: {len(ac_folios)}")
print()

# Build global co-occurrence from ALL AZC lines
print("Building global co-occurrence matrix...")
global_cooccurrence = Counter()

for folio, lines in folio_line_middles.items():
    for line_num, middles in lines.items():
        middles_list = list(middles)
        for i in range(len(middles_list)):
            for j in range(i + 1, len(middles_list)):
                pair = tuple(sorted([middles_list[i], middles_list[j]]))
                global_cooccurrence[pair] += 1

# Pairs that co-occur at least once are "legal"
legal_pairs = {pair for pair, count in global_cooccurrence.items() if count > 0}
print(f"  Legal pairs (co-occur at least once): {len(legal_pairs)}")
print()

# ============================================================
# COMPUTE LOCAL INCOMPATIBILITY DENSITY PER FOLIO
# ============================================================

print("=" * 70)
print("COMPUTING LOCAL INCOMPATIBILITY DENSITY")
print("=" * 70)
print()

def compute_folio_incompatibility(folio, lines):
    """Compute incompatibility density for a folio's MIDDLE vocabulary."""
    # Collect all unique MIDDLEs on this folio
    all_middles = set()
    for line_middles in lines.values():
        all_middles.update(line_middles)

    if len(all_middles) < 2:
        return None

    # Count all possible pairs
    middles_list = list(all_middles)
    n_middles = len(middles_list)
    total_pairs = n_middles * (n_middles - 1) // 2

    # Count illegal pairs (those that never co-occur globally)
    illegal_count = 0
    legal_count = 0
    for i in range(n_middles):
        for j in range(i + 1, n_middles):
            pair = tuple(sorted([middles_list[i], middles_list[j]]))
            if pair in legal_pairs:
                legal_count += 1
            else:
                illegal_count += 1

    # Density = fraction of pairs that are illegal
    density = illegal_count / total_pairs if total_pairs > 0 else 0

    return {
        'n_middles': n_middles,
        'total_pairs': total_pairs,
        'legal_pairs': legal_count,
        'illegal_pairs': illegal_count,
        'incompatibility_density': density
    }

folio_results = {}
zodiac_densities = []
ac_densities = []

for folio, lines in folio_line_middles.items():
    result = compute_folio_incompatibility(folio, lines)
    if result is None:
        continue

    result['family'] = folio_family.get(folio, 'UNKNOWN')
    folio_results[folio] = result

    if result['family'] == 'ZODIAC':
        zodiac_densities.append(result['incompatibility_density'])
    elif result['family'] == 'AC':
        ac_densities.append(result['incompatibility_density'])

print(f"Folios with data: {len(folio_results)}")
print(f"  Zodiac: {len(zodiac_densities)}")
print(f"  A/C: {len(ac_densities)}")
print()

# ============================================================
# STATISTICAL COMPARISON
# ============================================================

print("=" * 70)
print("STATISTICAL COMPARISON: A/C vs ZODIAC")
print("=" * 70)
print()

print("LOCAL INCOMPATIBILITY DENSITY (fraction of pairs that are illegal):")
print()

if zodiac_densities:
    zodiac_mean = np.mean(zodiac_densities)
    zodiac_std = np.std(zodiac_densities)
    print(f"  ZODIAC: mean = {zodiac_mean:.4f}, std = {zodiac_std:.4f}, n = {len(zodiac_densities)}")
else:
    zodiac_mean = 0
    print("  ZODIAC: No data")

if ac_densities:
    ac_mean = np.mean(ac_densities)
    ac_std = np.std(ac_densities)
    print(f"  A/C:    mean = {ac_mean:.4f}, std = {ac_std:.4f}, n = {len(ac_densities)}")
else:
    ac_mean = 0
    print("  A/C: No data")

print()
print(f"  Global baseline: {global_sparsity:.4f}")
print()

# Mann-Whitney U test
if len(zodiac_densities) >= 3 and len(ac_densities) >= 3:
    u_stat, p_value = stats.mannwhitneyu(ac_densities, zodiac_densities, alternative='greater')

    print("Mann-Whitney U test (A/C > Zodiac):")
    print(f"  U-statistic: {u_stat:.2f}")
    print(f"  P-value: {p_value:.6f}")
    print()

    # Effect size
    n1, n2 = len(ac_densities), len(zodiac_densities)
    effect_size = 1 - (2 * u_stat) / (n1 * n2)
    print(f"  Effect size (r): {effect_size:.3f}")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if p_value < 0.01 and ac_mean > zodiac_mean:
        verdict = "STRONG SIGNAL"
        interpretation = "A/C folios activate more densely incompatible MIDDLE subsets than Zodiac"
    elif p_value < 0.05 and ac_mean > zodiac_mean:
        verdict = "WEAK SIGNAL"
        interpretation = "A/C folios show marginally higher incompatibility density"
    elif p_value > 0.05:
        verdict = "NO SIGNAL"
        interpretation = "A/C and Zodiac show similar local incompatibility densities"
    else:
        verdict = "UNEXPECTED"
        interpretation = "Results do not match prediction"

    print(f"Verdict: {verdict}")
    print(f"P-value: {p_value:.4f} (threshold: 0.05)")
    print()
    print(f"Interpretation: {interpretation}")
else:
    u_stat = 0
    p_value = 1.0
    effect_size = 0
    verdict = "INSUFFICIENT DATA"
    interpretation = "Not enough folios for statistical comparison"
    print(f"Verdict: {verdict}")

# ============================================================
# DETAILED BREAKDOWN
# ============================================================

print()
print("=" * 70)
print("DETAILED BREAKDOWN BY FOLIO")
print("=" * 70)
print()

print(f"{'Folio':<12} {'Family':<10} {'MIDDLEs':>8} {'Legal':>8} {'Illegal':>10} {'Density':>10}")
print("-" * 68)

for folio in sorted(folio_results.keys()):
    r = folio_results[folio]
    print(f"{folio:<12} {r['family']:<10} {r['n_middles']:>8} {r['legal_pairs']:>8} {r['illegal_pairs']:>10} {r['incompatibility_density']:>10.4f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    "probe": "AC_MIDDLE_INCOMPATIBILITY_DENSITY",
    "question": "Are A/C folios activating more densely incompatible MIDDLE subsets?",
    "prediction": "A/C > Zodiac (fine discrimination = more mutually exclusive constraints)",
    "method": {
        "incompatibility_source": "C475 (line-level co-occurrence)",
        "metric": "fraction of folio's MIDDLE pairs that never co-occur globally"
    },
    "global_baseline": {
        "sparsity": float(global_sparsity),
        "legal_pairs_global": len(legal_pairs)
    },
    "summary": {
        "zodiac_folios": len(zodiac_densities),
        "ac_folios": len(ac_densities),
        "zodiac_mean_density": float(zodiac_mean) if zodiac_densities else None,
        "ac_mean_density": float(ac_mean) if ac_densities else None,
        "zodiac_std": float(zodiac_std) if zodiac_densities else None,
        "ac_std": float(ac_std) if ac_densities else None
    },
    "statistical_test": {
        "test": "Mann-Whitney U (one-sided, A/C > Zodiac)",
        "u_statistic": float(u_stat),
        "p_value": float(p_value),
        "effect_size_r": float(effect_size)
    },
    "verdict": verdict,
    "interpretation": interpretation,
    "folio_details": folio_results
}

with open('results/ac_incompatibility_density.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to results/ac_incompatibility_density.json")
