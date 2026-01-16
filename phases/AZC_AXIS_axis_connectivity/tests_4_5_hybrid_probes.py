#!/usr/bin/env python3
"""
TESTS 4-5: HYBRID STRUCTURE PROBES

Following the HYBRID verdict from cycle discriminator (V_A=0.152, V_B=0.139),
these tests probe the hybrid structure further.

TEST 4: Temporal Drift vs Structural Reset
         -> Does vocabulary shift gradually across zodiac folios (calendar drift)?
         -> Or reset sharply at diagram boundaries (structural)?

TEST 5: Forbidden Token Seasonality
         -> Are forbidden token-placement pairs uniformly distributed?
         -> Or do they cluster in specific zodiac positions (seasonal gating)?
"""

import os
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

os.chdir('C:/git/voynich')

print("=" * 70)
print("TESTS 4-5: HYBRID STRUCTURE PROBES")
print("Probing the season-gated workflow interpretation")
print("=" * 70)

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip('\"') != 'H':
            continue
        all_tokens.append(row)

# Separate by language
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

# Get vocabularies
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words

print(f"\nLoaded {len(azc_tokens)} AZC tokens")
print(f"AZC-only vocabulary: {len(azc_only)} types")

# Get folios in order
folios = sorted(set(t.get('folio', '') for t in azc_tokens))
zodiac_folios = [f for f in folios if f.startswith('f7')]

print(f"Zodiac folios (f7x): {len(zodiac_folios)}")

# =========================================================================
# TEST 4: TEMPORAL DRIFT VS STRUCTURAL RESET
# =========================================================================

print("\n" + "=" * 70)
print("TEST 4: TEMPORAL DRIFT VS STRUCTURAL RESET")
print("Does vocabulary shift gradually (calendar) or reset sharply (structural)?")
print("=" * 70)

# Build vocabulary per folio
folio_vocab = defaultdict(set)
for t in azc_tokens:
    folio = t.get('folio', '')
    folio_vocab[folio].add(t['word'])

# Calculate Jaccard similarity between consecutive zodiac folios
consecutive_similarities = []
for i in range(len(zodiac_folios) - 1):
    f1, f2 = zodiac_folios[i], zodiac_folios[i+1]
    v1, v2 = folio_vocab[f1], folio_vocab[f2]

    if v1 and v2:
        jaccard = len(v1 & v2) / len(v1 | v2)
        consecutive_similarities.append((f1, f2, jaccard))

print(f"\nConsecutive folio vocabulary similarity (Jaccard):")
print(f"{'Folio 1':<12} {'Folio 2':<12} {'Jaccard':<10}")
print("-" * 40)

for f1, f2, j in consecutive_similarities:
    # Mark potential resets (low similarity)
    marker = "*** RESET ***" if j < 0.3 else ""
    print(f"{f1:<12} {f2:<12} {j:<10.3f} {marker}")

if consecutive_similarities:
    jaccards = [j for _, _, j in consecutive_similarities]
    mean_j = sum(jaccards) / len(jaccards)
    std_j = np.std(jaccards)

    print(f"\nMean consecutive similarity: {mean_j:.3f}")
    print(f"Std deviation: {std_j:.3f}")

    # Count resets (sharp drops)
    resets = sum(1 for j in jaccards if j < 0.3)

    print(f"\nReset count (Jaccard < 0.3): {resets}/{len(jaccards)}")

    # Test: is similarity uniform (calendar drift) or bimodal (structural reset)?
    if std_j < 0.1:
        drift_verdict = "GRADUAL_DRIFT"
        drift_meaning = "Vocabulary shifts smoothly - calendar-like progression"
    elif resets >= 3:
        drift_verdict = "STRUCTURAL_RESET"
        drift_meaning = "Sharp vocabulary breaks - diagram-boundary driven"
    else:
        drift_verdict = "MIXED"
        drift_meaning = "Some drift, some reset - hybrid pattern"

    print(f"\nTEST 4 VERDICT: {drift_verdict}")
    print(f"Interpretation: {drift_meaning}")

# =========================================================================
# TEST 5: FORBIDDEN TOKEN SEASONALITY
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5: FORBIDDEN TOKEN SEASONALITY")
print("Are forbidden pairs uniformly distributed or seasonally clustered?")
print("=" * 70)

# Get placements
placements = sorted(set(t.get('placement', 'UNK') for t in azc_tokens))

# Build token-placement distribution
token_placement = defaultdict(Counter)
for t in azc_tokens:
    word = t['word']
    if word in azc_only:  # Focus on AZC-only tokens
        p = t.get('placement', 'UNK')
        token_placement[word][p] += 1

# Identify forbidden pairs (tokens that NEVER appear in certain placements)
# Focus on frequent tokens
token_totals = Counter(t['word'] for t in azc_tokens if t['word'] in azc_only)
frequent_tokens = {t for t, c in token_totals.items() if c >= 5}

forbidden_pairs = []
for token in frequent_tokens:
    present_placements = set(token_placement[token].keys())
    absent_placements = set(placements) - present_placements

    for p in absent_placements:
        if p not in ['UNK', '']:  # Skip unknown placements
            forbidden_pairs.append((token, p))

print(f"\nForbidden token-placement pairs: {len(forbidden_pairs)}")
print(f"Frequent AZC-only tokens: {len(frequent_tokens)}")

# Now check: are forbidden pairs clustered by folio position?
# Get which folios have each placement
placement_folios = defaultdict(set)
for t in azc_tokens:
    p = t.get('placement', 'UNK')
    folio = t.get('folio', '')
    placement_folios[p].add(folio)

# For each forbidden pair, count in which zodiac "region" the forbidding happens
# Divide zodiac into early, middle, late
if zodiac_folios:
    n = len(zodiac_folios)
    early = set(zodiac_folios[:n//3])
    middle = set(zodiac_folios[n//3:2*n//3])
    late = set(zodiac_folios[2*n//3:])

    print(f"\nZodiac regions:")
    print(f"  Early: {len(early)} folios")
    print(f"  Middle: {len(middle)} folios")
    print(f"  Late: {len(late)} folios")

    # For each placement, count which regions it appears in
    placement_regions = {}
    for p in placements:
        if p in ['UNK', '']:
            continue
        p_folios = placement_folios[p]
        regions = []
        if p_folios & early:
            regions.append('E')
        if p_folios & middle:
            regions.append('M')
        if p_folios & late:
            regions.append('L')
        placement_regions[p] = regions

    print(f"\nPlacement x Region presence:")
    print(f"{'Placement':<10} {'Regions':<15} {'Coverage':<10}")
    print("-" * 40)

    region_coverage = Counter()
    for p, regions in sorted(placement_regions.items()):
        coverage = len(regions) / 3 * 100
        region_str = ",".join(regions) if regions else "(none)"
        region_coverage[len(regions)] += 1
        print(f"{p:<10} {region_str:<15} {coverage:<10.0f}%")

    print(f"\nCoverage distribution:")
    print(f"  Full coverage (all 3 regions): {region_coverage[3]}")
    print(f"  Partial coverage (1-2 regions): {region_coverage[1] + region_coverage[2]}")
    print(f"  No coverage: {region_coverage[0]}")

    # Seasonality verdict
    partial_coverage = region_coverage[1] + region_coverage[2]
    full_coverage = region_coverage[3]

    if partial_coverage > full_coverage:
        season_verdict = "SEASONAL_CLUSTERING"
        season_meaning = "Placements are region-specific - seasonal gating confirmed"
    elif full_coverage > partial_coverage * 2:
        season_verdict = "UNIFORM"
        season_meaning = "Placements appear uniformly - no seasonal pattern"
    else:
        season_verdict = "MIXED"
        season_meaning = "Some placements seasonal, some uniform"

    print(f"\nTEST 5 VERDICT: {season_verdict}")
    print(f"Interpretation: {season_meaning}")

# =========================================================================
# TEST 5B: FORBIDDEN PAIR CONCENTRATION
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5B: FORBIDDEN PAIR CONCENTRATION BY PLACEMENT")
print("Which placements have the most forbidden tokens?")
print("=" * 70)

# Count forbidden pairs by placement
forbidden_by_placement = Counter()
for token, placement in forbidden_pairs:
    forbidden_by_placement[placement] += 1

print(f"\n{'Placement':<10} {'Forbidden Tokens':<20} {'% of All Forbidden':<20}")
print("-" * 55)

total_forbidden = len(forbidden_pairs)
for p, count in forbidden_by_placement.most_common():
    pct = count / total_forbidden * 100 if total_forbidden > 0 else 0
    print(f"{p:<10} {count:<20} {pct:<20.1f}")

# Which placements are most restrictive?
placement_token_counts = Counter()
for t in azc_tokens:
    p = t.get('placement', 'UNK')
    if t['word'] in frequent_tokens:
        placement_token_counts[p] += 1

print(f"\nPlacement restrictiveness (forbidden / total observed):")
print(f"{'Placement':<10} {'Observed':<12} {'Forbidden':<12} {'Restrictive%':<12}")
print("-" * 50)

for p in sorted(forbidden_by_placement.keys()):
    observed = placement_token_counts.get(p, 0)
    forbidden = forbidden_by_placement[p]
    restrictive = forbidden / max(1, len(frequent_tokens)) * 100
    print(f"{p:<10} {observed:<12} {forbidden:<12} {restrictive:<12.1f}")

# =========================================================================
# COMBINED VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("TESTS 4-5 COMBINED VERDICT")
print("=" * 70)

print(f"""
TEST 4 (Temporal Drift): {drift_verdict if 'drift_verdict' in dir() else 'N/A'}
TEST 5 (Seasonality): {season_verdict if 'season_verdict' in dir() else 'N/A'}

HYBRID STRUCTURE CHARACTERIZATION:
""")

# Determine overall hybrid character
if 'drift_verdict' in dir() and 'season_verdict' in dir():
    if drift_verdict == "STRUCTURAL_RESET" and season_verdict == "SEASONAL_CLUSTERING":
        print("""
  SEASON-GATED WORKFLOW (STRONG)

  Both tests confirm the hybrid interpretation:
  - Vocabulary resets at structural boundaries (not gradual drift)
  - Placements cluster by zodiac region (seasonal gating)

  The AZC sections encode:
  1. WHICH workflows are available (seasonal/material constraint)
  2. HOW to execute them (structural/procedural constraint)

  This is a GENUINE HYBRID - neither pure calendar nor pure state machine.
""")
    elif drift_verdict == "GRADUAL_DRIFT" and season_verdict == "UNIFORM":
        print("""
  CALENDAR-DOMINANT

  Both tests favor calendar interpretation:
  - Vocabulary drifts gradually (temporal progression)
  - Placements are uniform (not seasonally gated)

  The AZC sections may encode primarily temporal information
  with workflows as secondary annotation.
""")
    else:
        print(f"""
  MIXED HYBRID

  Tests show mixed signals:
  - Drift pattern: {drift_verdict}
  - Seasonality: {season_verdict}

  The hybrid nature is confirmed but neither axis dominates.
  Both material timing and procedural state contribute.
""")

print("=" * 70)
print("TESTS 4-5 COMPLETE")
print("=" * 70)
