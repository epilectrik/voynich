"""
T2: Rare Vocabulary Fidelity

H0: Rare MIDDLEs (appearing in <5 A folios) show same A->B fidelity as common ones
H1: Rare MIDDLEs show higher specificity (less combinatorial overlap)

Method: Stratify PP by frequency tier, compute mean B-folio spread per tier
Threshold: Spearman rho < -0.3 (rarer = more specific) to support H1

Rationale: If A-B routing is just combinatorial overlap from shared vocabulary,
common MIDDLEs should work everywhere. If routing is functional, rare MIDDLEs
should show more specific A->B targeting.
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=== T2: RARE VOCABULARY FIDELITY ===\n")

# Build A folio MIDDLE inventories
print("Building A folio MIDDLE inventories...")
a_folio_middles = defaultdict(set)
for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        a_folio_middles[t.folio].add(m.middle)

# Build B folio MIDDLE inventories
b_folio_middles = defaultdict(set)
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_folio_middles[t.folio].add(m.middle)

a_folios = sorted(a_folio_middles.keys())
b_folios = sorted(b_folio_middles.keys())

print(f"  {len(a_folios)} A folios, {len(b_folios)} B folios")

# Count how many A folios each MIDDLE appears in
middle_a_count = Counter()
for fol in a_folios:
    for mid in a_folio_middles[fol]:
        middle_a_count[mid] += 1

# Count how many B folios each MIDDLE appears in
middle_b_count = Counter()
for fol in b_folios:
    for mid in b_folio_middles[fol]:
        middle_b_count[mid] += 1

# Find shared MIDDLEs (PP vocabulary)
all_a_middles = set()
for fol in a_folios:
    all_a_middles.update(a_folio_middles[fol])

all_b_middles = set()
for fol in b_folios:
    all_b_middles.update(b_folio_middles[fol])

pp_middles = all_a_middles & all_b_middles
print(f"  PP MIDDLEs (shared A-B): {len(pp_middles)}")

# Stratify by A-frequency
print("\nStratifying by A-folio frequency...")

# Frequency tiers based on how many A folios contain this MIDDLE
freq_tiers = {
    'rare': (1, 5),      # 1-5 A folios
    'uncommon': (6, 20), # 6-20 A folios
    'common': (21, 50),  # 21-50 A folios
    'ubiquitous': (51, 200), # 51+ A folios
}

tier_middles = {tier: [] for tier in freq_tiers}
for mid in pp_middles:
    a_count = middle_a_count[mid]
    for tier, (lo, hi) in freq_tiers.items():
        if lo <= a_count <= hi:
            tier_middles[tier].append(mid)
            break

for tier in freq_tiers:
    print(f"  {tier}: {len(tier_middles[tier])} MIDDLEs")

# For each MIDDLE, compute B-folio spread (how many B folios contain it)
# Higher spread = less specific
print("\nComputing B-folio spread per MIDDLE...")

tier_b_spreads = {}
for tier in freq_tiers:
    spreads = []
    for mid in tier_middles[tier]:
        b_spread = middle_b_count[mid]
        spreads.append(b_spread)
    if spreads:
        tier_b_spreads[tier] = {
            'mean': float(np.mean(spreads)),
            'median': float(np.median(spreads)),
            'std': float(np.std(spreads)),
            'n': len(spreads),
        }
    else:
        tier_b_spreads[tier] = {'mean': 0, 'median': 0, 'std': 0, 'n': 0}

print("\n=== B-FOLIO SPREAD BY A-FREQUENCY TIER ===\n")
print(f"{'Tier':<12s} {'N MIDs':>8s} {'Mean B-spread':>14s} {'Median':>10s}")
print("-" * 50)
for tier in ['rare', 'uncommon', 'common', 'ubiquitous']:
    s = tier_b_spreads[tier]
    print(f"{tier:<12s} {s['n']:>8d} {s['mean']:>14.2f} {s['median']:>10.1f}")

# Compute correlation: A-frequency vs B-spread
# If H1 is true: rarer in A -> more spread in B? Actually opposite...
# Rarer in A -> should be MORE specific in B (less spread)

a_freqs = []
b_spreads = []
for mid in pp_middles:
    a_freqs.append(middle_a_count[mid])
    b_spreads.append(middle_b_count[mid])

a_freqs = np.array(a_freqs)
b_spreads = np.array(b_spreads)

rho, p_val = stats.spearmanr(a_freqs, b_spreads)
print(f"\nA-frequency vs B-spread correlation:")
print(f"  Spearman rho: {rho:.4f}")
print(f"  p-value: {p_val:.2e}")

# Also test: normalized B-spread (B-spread / A-frequency) vs A-frequency
# This tests whether rare MIDDLEs have disproportionate B-presence
normalized_spread = b_spreads / np.maximum(a_freqs, 1)
rho_norm, p_norm = stats.spearmanr(a_freqs, normalized_spread)
print(f"\nA-frequency vs normalized B-spread:")
print(f"  Spearman rho: {rho_norm:.4f}")
print(f"  p-value: {p_norm:.2e}")

# The fidelity measure: for each MIDDLE, what fraction of its A-appearances
# correspond to its B-appearances?
# Fidelity = (A-B co-occurrence) / (A-occurrence + B-occurrence - co-occurrence)
# This is Jaccard at the MIDDLE level

print("\n=== MIDDLE-LEVEL FIDELITY ===\n")

tier_fidelities = {}
for tier in freq_tiers:
    fidelities = []
    for mid in tier_middles[tier]:
        # A folios containing this MIDDLE
        a_fols_with = [f for f in a_folios if mid in a_folio_middles[f]]
        # B folios containing this MIDDLE
        b_fols_with = [f for f in b_folios if mid in b_folio_middles[f]]

        # Co-occurrence: how many (A,B) pairs share this MIDDLE?
        # Interpretation: if MIDDLE appears in 5 A folios and 10 B folios,
        # max co-occurrence is 5*10=50 pairs. Actual is just presence-based.

        # Simpler: Jaccard of A-set vs B-set at folio level
        # But folios are different sets (A vs B), so this doesn't apply directly.

        # Better fidelity measure: does presence in few A folios predict presence in few B folios?
        # I.e., are rare-in-A middles also rare-in-B?

        fid = middle_b_count[mid]  # Just use B-spread as inverse fidelity
        fidelities.append(fid)

    if fidelities:
        tier_fidelities[tier] = {
            'mean_b_spread': float(np.mean(fidelities)),
            'median_b_spread': float(np.median(fidelities)),
            'n': len(fidelities),
        }
    else:
        tier_fidelities[tier] = {'mean_b_spread': 0, 'median_b_spread': 0, 'n': 0}

# Test the hypothesis more directly:
# For each PP MIDDLE, compute "specificity ratio" = (max A-folio coverage) / (mean A-folio coverage)
# If routing is content-specific, rare MIDDLEs should have higher specificity ratios

print("Computing specificity ratios...")

# Build coverage of each MIDDLE by each A folio (binary presence)
# Then for B folios that contain this MIDDLE, check which A folios also have it

specificity_data = []
for mid in pp_middles:
    a_count = middle_a_count[mid]
    b_count = middle_b_count[mid]

    # Skip if too few observations
    if a_count < 2 or b_count < 2:
        continue

    # "Specificity" = how concentrated is this MIDDLE's B-presence
    # relative to its A-presence?
    # One measure: coefficient of variation of A-folio coverage

    # Actually, let's measure: of the B folios containing this MIDDLE,
    # what fraction of A folios ALSO contain it?
    # This is the "A-coverage rate" per B-folio

    a_fols_with = set(f for f in a_folios if mid in a_folio_middles[f])
    b_fols_with = [f for f in b_folios if mid in b_folio_middles[f]]

    # For each B folio containing this MIDDLE,
    # count how many A folios share it
    coverage_rates = [len(a_fols_with) / len(a_folios) for _ in b_fols_with]

    # The coverage rate is the same for all B folios (it's an A-side property)
    # So this doesn't vary by B folio.

    # Better: compute A-B Jaccard for this specific MIDDLE
    # = |A folios with mid & B folios with mid share pool| / union
    # But A and B folio sets don't overlap...

    # Simplest: just record A-freq, B-freq, and their ratio
    specificity_data.append({
        'middle': mid,
        'a_freq': a_count,
        'b_freq': b_count,
        'ratio': b_count / a_count if a_count > 0 else 0,
    })

# Compute correlation between A-frequency and B/A ratio
if specificity_data:
    a_freqs_spec = [d['a_freq'] for d in specificity_data]
    ratios = [d['ratio'] for d in specificity_data]
    rho_ratio, p_ratio = stats.spearmanr(a_freqs_spec, ratios)

    print(f"\nA-frequency vs B/A ratio:")
    print(f"  Spearman rho: {rho_ratio:.4f}")
    print(f"  p-value: {p_ratio:.2e}")
else:
    rho_ratio, p_ratio = 0, 1

# Verdict
# H1 predicts: rare MIDDLEs have LOWER B-spread (more specific)
# So we expect negative correlation between A-freq and B-spread... but only if routing is real
# If just vocabulary sharing, we expect positive (common in A = common in B)

threshold_rho = -0.3

if rho < threshold_rho:
    verdict = "RARE_MORE_SPECIFIC"
    explanation = f"rho={rho:.3f} < -0.3: rare MIDDLEs have lower B-spread, supporting functional routing"
elif rho > 0.3:
    verdict = "COMMON_MORE_SPREAD"
    explanation = f"rho={rho:.3f} > 0.3: common MIDDLEs spread more in B, consistent with shared vocabulary"
else:
    verdict = "NO_PATTERN"
    explanation = f"rho={rho:.3f} shows no clear frequency-specificity relationship"

print(f"\n=== VERDICT: {verdict} ===")
print(f"  {explanation}")

# Additional interpretation
if rho > 0:
    print(f"\n  NOTE: Positive correlation means MIDDLEs common in A are also common in B.")
    print(f"  This is expected if A and B draw from a shared vocabulary pool,")
    print(f"  NOT if A functionally routes specific content to B.")

# Save results
results = {
    'test': 'T2_rare_vocabulary_fidelity',
    'pp_middles_count': len(pp_middles),
    'tier_counts': {tier: len(mids) for tier, mids in tier_middles.items()},
    'tier_b_spreads': tier_b_spreads,
    'correlations': {
        'a_freq_vs_b_spread': {'rho': float(rho), 'p': float(p_val)},
        'a_freq_vs_normalized_spread': {'rho': float(rho_norm), 'p': float(p_norm)},
        'a_freq_vs_ba_ratio': {'rho': float(rho_ratio), 'p': float(p_ratio)},
    },
    'threshold_rho': threshold_rho,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't2_rare_vocabulary_fidelity.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
