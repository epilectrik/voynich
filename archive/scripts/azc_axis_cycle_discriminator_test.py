#!/usr/bin/env python3
"""
CYCLE DISCRIMINATOR TEST

Core question: Is AZC indexing EXTERNAL TIME (calendar) or INTERNAL STATE (workflow)?

TEST 1: AZC Placement x Currier A Material Compatibility
        -> Calendar signal: placement correlates with material families

TEST 2: AZC Placement x Currier B Program Type
        -> Workflow signal: placement correlates with procedural regimes

Whichever axis AZC aligns with more strongly tells us what kind of cycle this is.
"""

import os
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

os.chdir('C:/git/voynich')

print("=" * 70)
print("CYCLE DISCRIMINATOR TEST")
print("Calendar (material-indexed) vs Workflow (procedure-indexed)?")
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
        all_tokens.append(row)

# Separate by language
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

# Build vocabularies
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)

# Shared vocabularies
azc_a_shared = azc_words.intersection(a_words)
azc_b_shared = azc_words.intersection(b_words)

print(f"\nVocabulary overlap:")
print(f"  AZC-A shared: {len(azc_a_shared)} types")
print(f"  AZC-B shared: {len(azc_b_shared)} types")

# Get placement classes
placements = sorted(set(t.get('placement', 'UNK') for t in azc_tokens))
significant_placements = ['C', 'P', 'R1', 'R2', 'R3', 'S', 'S1', 'S2', 'L', 'X', 'Y']

# =========================================================================
# TEST 1: AZC Placement x Currier A Material Families
# =========================================================================

print("\n" + "=" * 70)
print("TEST 1: AZC PLACEMENT x CURRIER A MATERIAL FAMILIES")
print("Does placement correlate with material type (prefix class)?")
print("=" * 70)

# Build A prefix classes for shared vocabulary
def get_prefix(word):
    """Extract prefix from token."""
    prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'da', 'ol', 'ar', 'or', 'al', 'op']
    for pf in sorted(prefixes, key=len, reverse=True):
        if word.startswith(pf):
            return pf
    return 'other'

# Map shared A tokens to their prefix families
a_token_prefix = {}
for word in azc_a_shared:
    a_token_prefix[word] = get_prefix(word)

# For each placement, count prefix distribution of shared-A tokens
placement_a_prefixes = defaultdict(Counter)

for t in azc_tokens:
    word = t['word']
    if word in azc_a_shared:
        p = t.get('placement', 'UNK')
        prefix = a_token_prefix[word]
        placement_a_prefixes[p][prefix] += 1

# Build contingency table
prefix_classes = ['ch', 'sh', 'qo', 'ok', 'ot', 'da', 'ol', 'ar', 'other']
valid_placements = [p for p in significant_placements if sum(placement_a_prefixes[p].values()) >= 20]

print(f"\nPlacements with 20+ shared-A tokens: {len(valid_placements)}")
print(f"\nPlacement x A-Prefix distribution:")
print(f"{'Placement':<10}", end="")
for pf in prefix_classes[:6]:
    print(f"{pf:<8}", end="")
print("Total")
print("-" * 70)

contingency_a = []
for p in valid_placements:
    row = [placement_a_prefixes[p].get(pf, 0) for pf in prefix_classes]
    contingency_a.append(row)
    total = sum(row)
    print(f"{p:<10}", end="")
    for i, pf in enumerate(prefix_classes[:6]):
        pct = row[i] / total * 100 if total > 0 else 0
        print(f"{pct:>6.1f}%", end=" ")
    print(f"{total}")

# Chi-square test
contingency_a = np.array(contingency_a)
col_sums = contingency_a.sum(axis=0)
non_zero = col_sums > 0
contingency_a_clean = contingency_a[:, non_zero]

if contingency_a_clean.shape[0] >= 2 and contingency_a_clean.shape[1] >= 2:
    chi2_a, p_a, dof_a, _ = stats.chi2_contingency(contingency_a_clean)
    n = contingency_a_clean.sum()
    cramers_v_a = np.sqrt(chi2_a / (n * (min(contingency_a_clean.shape) - 1)))

    print(f"\n--- Currier A Correlation ---")
    print(f"Chi-square: {chi2_a:.1f}, df={dof_a}, p={p_a:.2e}")
    print(f"Cramer's V (Placement x A-Material): {cramers_v_a:.3f}")

# =========================================================================
# TEST 2: AZC Placement x Currier B Program Features
# =========================================================================

print("\n" + "=" * 70)
print("TEST 2: AZC PLACEMENT x CURRIER B PROGRAM FEATURES")
print("Does placement correlate with procedural regime?")
print("=" * 70)

# Map B tokens to their grammatical features
# Use prefix patterns that indicate B-grammar roles
def get_b_role(word):
    """Classify B token by grammatical role."""
    # Kernel patterns
    if word in ['ok', 'yk', 'ak', 'ek', 'otk']:
        return 'KERNEL_K'
    if word in ['oh', 'yh', 'ah', 'eh', 'oth']:
        return 'KERNEL_H'
    if 'ol' in word or word == 'ol':
        return 'LINK'
    if word.startswith('ch') or word.startswith('sh'):
        return 'CH_SH'
    if word.startswith('qo') or word.startswith('ok'):
        return 'QO_OK'
    if word.startswith('da'):
        return 'DA'
    return 'OTHER'

# For each placement, count B-role distribution
placement_b_roles = defaultdict(Counter)

for t in azc_tokens:
    word = t['word']
    if word in azc_b_shared:
        p = t.get('placement', 'UNK')
        role = get_b_role(word)
        placement_b_roles[p][role] += 1

# Build contingency table
b_roles = ['LINK', 'CH_SH', 'QO_OK', 'DA', 'OTHER']
valid_placements_b = [p for p in significant_placements if sum(placement_b_roles[p].values()) >= 20]

print(f"\nPlacements with 20+ shared-B tokens: {len(valid_placements_b)}")
print(f"\nPlacement x B-Role distribution:")
print(f"{'Placement':<10}", end="")
for role in b_roles[:4]:
    print(f"{role:<10}", end="")
print("Total")
print("-" * 70)

contingency_b = []
for p in valid_placements_b:
    row = [placement_b_roles[p].get(role, 0) for role in b_roles]
    contingency_b.append(row)
    total = sum(row)
    print(f"{p:<10}", end="")
    for i, role in enumerate(b_roles[:4]):
        pct = row[i] / total * 100 if total > 0 else 0
        print(f"{pct:>8.1f}%", end=" ")
    print(f"{total}")

# Chi-square test
contingency_b = np.array(contingency_b)
col_sums_b = contingency_b.sum(axis=0)
non_zero_b = col_sums_b > 0
contingency_b_clean = contingency_b[:, non_zero_b]

if contingency_b_clean.shape[0] >= 2 and contingency_b_clean.shape[1] >= 2:
    chi2_b, p_b, dof_b, _ = stats.chi2_contingency(contingency_b_clean)
    n_b = contingency_b_clean.sum()
    cramers_v_b = np.sqrt(chi2_b / (n_b * (min(contingency_b_clean.shape) - 1)))

    print(f"\n--- Currier B Correlation ---")
    print(f"Chi-square: {chi2_b:.1f}, df={dof_b}, p={p_b:.2e}")
    print(f"Cramer's V (Placement x B-Role): {cramers_v_b:.3f}")

# =========================================================================
# TEST 3: LINK Density by Placement (B workflow signal)
# =========================================================================

print("\n" + "=" * 70)
print("TEST 3: LINK DENSITY BY PLACEMENT")
print("Does placement correlate with waiting behavior?")
print("=" * 70)

# Count LINK tokens per placement
link_tokens = {'ol', 'chol', 'sho', 'cho', 'dol', 'shol'}

placement_link = defaultdict(lambda: {'link': 0, 'total': 0})
for t in azc_tokens:
    p = t.get('placement', 'UNK')
    placement_link[p]['total'] += 1
    if t['word'] in link_tokens or 'ol' in t['word']:
        placement_link[p]['link'] += 1

print(f"\n{'Placement':<10} {'Total':<10} {'LINK':<10} {'LINK%':<10}")
print("-" * 45)

link_rates = []
for p in significant_placements:
    if placement_link[p]['total'] >= 50:
        total = placement_link[p]['total']
        link = placement_link[p]['link']
        rate = link / total * 100
        link_rates.append((p, rate))
        print(f"{p:<10} {total:<10} {link:<10} {rate:<10.1f}")

if link_rates:
    rates = [r[1] for r in link_rates]
    print(f"\nLINK rate range: {min(rates):.1f}% - {max(rates):.1f}%")
    print(f"LINK rate variance: {np.std(rates):.2f}")

    if max(rates) - min(rates) > 5:
        print("SIGNIFICANT variation in LINK density by placement")
        print("-> Workflow signal: placement affects waiting behavior")

# =========================================================================
# TEST 4: Cross-Folio Synchrony
# =========================================================================

print("\n" + "=" * 70)
print("TEST 4: CROSS-FOLIO SYNCHRONY")
print("Do similar placement profiles share materials or procedures?")
print("=" * 70)

# Build placement profile per folio
folio_profiles = defaultdict(Counter)
folio_a_vocab = defaultdict(set)
folio_b_vocab = defaultdict(set)

for t in azc_tokens:
    folio = t.get('folio', '')
    p = t.get('placement', 'UNK')
    word = t['word']

    folio_profiles[folio][p] += 1
    if word in azc_a_shared:
        folio_a_vocab[folio].add(word)
    if word in azc_b_shared:
        folio_b_vocab[folio].add(word)

# Find folios with similar placement profiles (zodiac cluster)
zodiac_folios = [f for f in folio_profiles if f.startswith('f7') and 'r' in f or 'v' in f]

# Check if similar-profile folios share vocabulary
print(f"\nZodiac folios (f71-f73 region): {len([f for f in zodiac_folios if f.startswith('f71') or f.startswith('f72') or f.startswith('f73')])}")

# Compare vocabulary overlap within zodiac cluster
zodiac_cluster = [f for f in folio_profiles if f.startswith('f71') or f.startswith('f72') or f.startswith('f73')]

if len(zodiac_cluster) >= 2:
    # A vocabulary overlap
    a_overlaps = []
    b_overlaps = []
    for i in range(len(zodiac_cluster)):
        for j in range(i+1, len(zodiac_cluster)):
            f1, f2 = zodiac_cluster[i], zodiac_cluster[j]

            # A overlap
            a1, a2 = folio_a_vocab[f1], folio_a_vocab[f2]
            if a1 and a2:
                jaccard_a = len(a1 & a2) / len(a1 | a2)
                a_overlaps.append(jaccard_a)

            # B overlap
            b1, b2 = folio_b_vocab[f1], folio_b_vocab[f2]
            if b1 and b2:
                jaccard_b = len(b1 & b2) / len(b1 | b2)
                b_overlaps.append(jaccard_b)

    if a_overlaps and b_overlaps:
        mean_a = sum(a_overlaps) / len(a_overlaps)
        mean_b = sum(b_overlaps) / len(b_overlaps)

        print(f"\nWithin zodiac cluster:")
        print(f"  Mean A-vocabulary overlap (Jaccard): {mean_a:.3f}")
        print(f"  Mean B-vocabulary overlap (Jaccard): {mean_b:.3f}")

        if mean_a > mean_b + 0.05:
            print("  -> Same-template folios share MATERIALS more than procedures")
            print("  -> Calendar signal")
        elif mean_b > mean_a + 0.05:
            print("  -> Same-template folios share PROCEDURES more than materials")
            print("  -> Workflow signal")
        else:
            print("  -> Similar overlap for both (HYBRID)")

# =========================================================================
# VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("CYCLE DISCRIMINATOR VERDICT")
print("=" * 70)

print(f"""
CORRELATION STRENGTH COMPARISON:

  Placement x A-Material (Cramer's V): {cramers_v_a:.3f}
  Placement x B-Role (Cramer's V):     {cramers_v_b:.3f}
""")

if cramers_v_a > cramers_v_b + 0.05:
    dominant = "CALENDAR"
    explanation = "AZC placement correlates more strongly with material families"
elif cramers_v_b > cramers_v_a + 0.05:
    dominant = "WORKFLOW"
    explanation = "AZC placement correlates more strongly with procedural roles"
else:
    dominant = "HYBRID"
    explanation = "AZC shows comparable correlation with both materials and procedures"

print(f"  DOMINANT SIGNAL: {dominant}")
print(f"  Interpretation: {explanation}")

print("""
WHAT THIS MEANS:
""")

if dominant == "CALENDAR":
    print("""
  AZC appears to index EXTERNAL TIME (seasonal/calendar cycle).

  Placement codes organize WHAT materials are relevant WHEN,
  not how procedures should be executed.

  This supports the "perpetual calendar" interpretation:
  -> Zodiac sections encode timing windows for botanical work
  -> Materials are seasonally gated
  -> Procedures are material-dependent, not position-dependent
""")
elif dominant == "WORKFLOW":
    print("""
  AZC appears to index INTERNAL STATE (apparatus/workflow cycle).

  Placement codes organize HOW to proceed at each stage,
  not what materials are involved.

  This supports a "state machine" interpretation:
  -> Diagrams encode workflow positions
  -> Procedures are position-dependent
  -> Materials are selected externally
""")
else:
    print("""
  AZC shows HYBRID characteristics.

  The cycle indexes workflow states whose AVAILABILITY
  is seasonally constrained.

  This supports a "season-gated workflow" interpretation:
  -> Diagrams encode when certain workflows are legal
  -> Both material timing AND procedural state matter
  -> Realistic for botanical processing
""")

print("=" * 70)
print("CYCLE DISCRIMINATOR COMPLETE")
print("=" * 70)
