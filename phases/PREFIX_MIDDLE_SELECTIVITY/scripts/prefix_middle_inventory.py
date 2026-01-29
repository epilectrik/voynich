#!/usr/bin/env python3
"""
PREFIX_MIDDLE_SELECTIVITY Phase - Script 1: PREFIXxMIDDLE Inventory

Tests 1-4: Build complete PREFIXxMIDDLE contingency table from B tokens,
measure selectivity spectrum, lane alignment, and A-vs-B comparison.

Dependencies:
  - middle_classes_v2_backup.json (A_INTERNAL_STRATIFICATION)
  - pp_role_foundation.json (A_TO_B_ROLE_PROJECTION)
  - pp_classification.json (PP_CLASSIFICATION)
  - scripts/voynich.py (Transcript, Morphology)
"""

import json
import sys
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================

print("=" * 70)
print("PREFIX_MIDDLE_SELECTIVITY - Script 1: PREFIXxMIDDLE Inventory")
print("=" * 70)

# Load PP set (404 MIDDLEs)
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])
print(f"\nPP MIDDLEs loaded: {len(pp_set)}")

# Load AZC-Med/B-Native split
with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json') as f:
    role_data = json.load(f)
azc_med_set = set(role_data['azc_split']['azc_mediated'])
b_native_set = set(role_data['azc_split']['b_native'])
print(f"AZC-Mediated: {len(azc_med_set)}, B-Native: {len(b_native_set)}")

# Load material class
with open(PROJECT_ROOT / 'phases/PP_CLASSIFICATION/results/pp_classification.json') as f:
    pp_class_data = json.load(f)
# Build MIDDLE -> material class map
material_map = {}
for entry in pp_class_data.get('classifications', []):
    mid = entry.get('middle')
    mat = entry.get('material_class', 'UNKNOWN')
    if mid:
        material_map[mid] = mat

tx = Transcript()
morph = Morphology()

# ============================================================
# BUILD PREFIXxMIDDLE INVENTORIES (B-side and A-side)
# ============================================================

print("\nBuilding PREFIXxMIDDLE inventories...")

# B-side inventory
b_prefix_middle = defaultdict(Counter)  # MIDDLE -> Counter{PREFIX: count}
b_middle_prefix = defaultdict(Counter)  # PREFIX -> Counter{MIDDLE: count}
b_total_pp_tokens = 0

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    m = morph.extract(token.word)
    if m.middle and m.middle in pp_set:
        prefix_key = m.prefix if m.prefix else 'NONE'
        b_prefix_middle[m.middle][prefix_key] += 1
        b_middle_prefix[prefix_key][m.middle] += 1
        b_total_pp_tokens += 1

print(f"B-side PP tokens: {b_total_pp_tokens}")
print(f"B-side MIDDLEs observed: {len(b_prefix_middle)}")
print(f"B-side PREFIXes observed: {len(b_middle_prefix)}")

# A-side inventory
a_prefix_middle = defaultdict(Counter)  # MIDDLE -> Counter{PREFIX: count}
a_middle_prefix = defaultdict(Counter)  # PREFIX -> Counter{MIDDLE: count}
a_total_pp_tokens = 0

for token in tx.currier_a():
    if not token.word.strip() or '*' in token.word:
        continue
    m = morph.extract(token.word)
    if m.middle and m.middle in pp_set:
        prefix_key = m.prefix if m.prefix else 'NONE'
        a_prefix_middle[m.middle][prefix_key] += 1
        a_middle_prefix[prefix_key][m.middle] += 1
        a_total_pp_tokens += 1

print(f"A-side PP tokens: {a_total_pp_tokens}")
print(f"A-side MIDDLEs observed: {len(a_prefix_middle)}")
print(f"A-side PREFIXes observed: {len(a_middle_prefix)}")

# MIDDLEs in PP set but not observed in B
b_unobserved = pp_set - set(b_prefix_middle.keys())
print(f"PP MIDDLEs not observed in B: {len(b_unobserved)}")

results = {}

# ============================================================
# SECTION 2: TEST 1 — PREFIXxMIDDLE Contingency Table
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: PREFIXxMIDDLE Contingency Table")
print("=" * 70)

b_middles = sorted(b_prefix_middle.keys())
b_prefixes = sorted(b_middle_prefix.keys())

n_middles = len(b_middles)
n_prefixes = len(b_prefixes)
total_cells = n_middles * n_prefixes

# Count non-zero cells
nonzero = 0
for mid in b_middles:
    nonzero += len(b_prefix_middle[mid])
sparsity = 1.0 - (nonzero / total_cells) if total_cells > 0 else 0.0

print(f"\nContingency dimensions: {n_middles} MIDDLEs x {n_prefixes} PREFIXes")
print(f"Total cells: {total_cells}, Non-zero: {nonzero}, Sparsity: {sparsity:.3f}")
print(f"Total B-side PP tokens: {b_total_pp_tokens}")

# PREFIX diversity per MIDDLE
middle_diversity = {}
for mid in b_middles:
    n_pfx = len(b_prefix_middle[mid])
    middle_diversity[mid] = n_pfx

diversity_dist = Counter(middle_diversity.values())
print(f"\nPREFIX diversity per MIDDLE:")
for k in sorted(diversity_dist.keys()):
    print(f"  {k} PREFIX(es): {diversity_dist[k]} MIDDLEs")

# Categorize diversity
exclusive_1 = [m for m, d in middle_diversity.items() if d == 1]
low_2_3 = [m for m, d in middle_diversity.items() if d in (2, 3)]
high_4plus = [m for m, d in middle_diversity.items() if d >= 4]

print(f"\nExclusive (1 PREFIX): {len(exclusive_1)} ({100*len(exclusive_1)/n_middles:.1f}%)")
print(f"Low diversity (2-3): {len(low_2_3)} ({100*len(low_2_3)/n_middles:.1f}%)")
print(f"High diversity (4+): {len(high_4plus)} ({100*len(high_4plus)/n_middles:.1f}%)")

# PREFIX diversity per PREFIX (how many MIDDLEs each PREFIX serves)
prefix_diversity = {}
for pfx in b_prefixes:
    prefix_diversity[pfx] = len(b_middle_prefix[pfx])

print(f"\nMIDDLE diversity per PREFIX (top 10):")
for pfx in sorted(prefix_diversity, key=prefix_diversity.get, reverse=True)[:10]:
    total = sum(b_middle_prefix[pfx].values())
    print(f"  {pfx:8s}: {prefix_diversity[pfx]:3d} MIDDLEs, {total:5d} tokens")

# C276 comparison: how many MIDDLEs exclusive to one PREFIX (B-side)?
# C276 said 28 exclusive at type level; C423 said 80% exclusive
# Note: C276/C423 were measured across all tokens (not just B-side PP)
print(f"\nC276/C423 Comparison:")
print(f"  B-side exclusive (1 PREFIX): {len(exclusive_1)}/{n_middles} = {100*len(exclusive_1)/n_middles:.1f}%")
print(f"  C276 reference: 28 MIDDLEs exclusive (measured on full vocabulary)")
print(f"  C423 reference: 80% PREFIX-exclusive (measured on full vocabulary)")

results['contingency'] = {
    'dimensions': {'middles': n_middles, 'prefixes': n_prefixes},
    'total_cells': total_cells,
    'nonzero_cells': nonzero,
    'sparsity': round(sparsity, 4),
    'total_b_pp_tokens': b_total_pp_tokens,
    'prefix_list': b_prefixes,
    'middle_prefix_diversity': {m: d for m, d in sorted(middle_diversity.items(), key=lambda x: -x[1])[:50]},
    'diversity_distribution': {str(k): v for k, v in sorted(diversity_dist.items())},
    'exclusivity_spectrum': {
        'exclusive_1': len(exclusive_1),
        'low_2_3': len(low_2_3),
        'high_4plus': len(high_4plus),
        'exclusive_pct': round(100 * len(exclusive_1) / n_middles, 1),
    },
    'prefix_diversity': {pfx: prefix_diversity[pfx] for pfx in sorted(prefix_diversity, key=prefix_diversity.get, reverse=True)},
    'c276_comparison': f"{len(exclusive_1)} exclusive vs C276's 28 (different scope: B-side PP vs full vocab)",
    'c423_comparison': f"{100*len(exclusive_1)/n_middles:.1f}% exclusive vs C423's 80% (different scope)",
}

# ============================================================
# SECTION 3: TEST 2 — PREFIX Selectivity Spectrum
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: PREFIX Selectivity Spectrum")
print("=" * 70)

MIN_B_TOKENS = 10

testable_middles = {m: b_prefix_middle[m] for m in b_middles if sum(b_prefix_middle[m].values()) >= MIN_B_TOKENS}
excluded_count = n_middles - len(testable_middles)

print(f"\nTestable MIDDLEs (>={MIN_B_TOKENS} B tokens): {len(testable_middles)}")
print(f"Excluded: {excluded_count}")

# Compute concentration and entropy for each testable MIDDLE
selectivity_data = {}
for mid, pfx_counts in testable_middles.items():
    total = sum(pfx_counts.values())
    fracs = {pfx: c / total for pfx, c in pfx_counts.items()}
    concentration = max(fracs.values())
    # Shannon entropy
    entropy = -sum(f * math.log2(f) for f in fracs.values() if f > 0)
    dominant_prefix = max(fracs, key=fracs.get)

    # Classify
    if concentration >= 0.95:
        category = 'locked'
    elif concentration >= 0.70:
        category = 'dominant'
    else:
        # Check bimodal: two prefixes each >= 0.25
        above_25 = sum(1 for f in fracs.values() if f >= 0.25)
        if above_25 >= 2:
            category = 'bimodal'
        else:
            category = 'promiscuous'

    selectivity_data[mid] = {
        'concentration': concentration,
        'entropy': entropy,
        'category': category,
        'dominant_prefix': dominant_prefix,
        'n_prefixes': len(pfx_counts),
        'total_tokens': total,
        'prefix_fracs': {pfx: round(f, 4) for pfx, f in sorted(fracs.items(), key=lambda x: -x[1])},
    }

# Category sizes
categories = Counter(d['category'] for d in selectivity_data.values())
print(f"\nSelectivity categories:")
for cat in ['locked', 'dominant', 'bimodal', 'promiscuous']:
    n = categories.get(cat, 0)
    pct = 100 * n / len(testable_middles) if testable_middles else 0
    print(f"  {cat:12s}: {n:3d} ({pct:.1f}%)")

# Concentration distribution
concentrations = [d['concentration'] for d in selectivity_data.values()]
entropies = [d['entropy'] for d in selectivity_data.values()]

conc_bins = {'0.50-0.60': 0, '0.60-0.70': 0, '0.70-0.80': 0, '0.80-0.90': 0, '0.90-1.00': 0}
for c in concentrations:
    if c < 0.60:
        conc_bins['0.50-0.60'] += 1
    elif c < 0.70:
        conc_bins['0.60-0.70'] += 1
    elif c < 0.80:
        conc_bins['0.70-0.80'] += 1
    elif c < 0.90:
        conc_bins['0.80-0.90'] += 1
    else:
        conc_bins['0.90-1.00'] += 1

print(f"\nConcentration distribution:")
for bin_label, count in conc_bins.items():
    print(f"  {bin_label}: {count}")

print(f"\nConcentration stats: mean={np.mean(concentrations):.3f}, median={np.median(concentrations):.3f}, "
      f"min={min(concentrations):.3f}, max={max(concentrations):.3f}")
print(f"Entropy stats: mean={np.mean(entropies):.3f}, median={np.median(entropies):.3f}, "
      f"min={min(entropies):.3f}, max={max(entropies):.3f}")

# Top locked MIDDLEs (examples)
locked = [(m, d) for m, d in selectivity_data.items() if d['category'] == 'locked']
locked.sort(key=lambda x: -x[1]['total_tokens'])
print(f"\nTop locked MIDDLEs (by frequency, first 10):")
for mid, d in locked[:10]:
    print(f"  {mid:8s}: PREFIX={d['dominant_prefix']:6s}, conc={d['concentration']:.3f}, n={d['total_tokens']}")

# Top promiscuous MIDDLEs
promisc = [(m, d) for m, d in selectivity_data.items() if d['category'] == 'promiscuous']
promisc.sort(key=lambda x: -x[1]['total_tokens'])
print(f"\nTop promiscuous MIDDLEs (by frequency, first 10):")
for mid, d in promisc[:10]:
    pfx_str = ', '.join(f"{k}:{v:.2f}" for k, v in list(d['prefix_fracs'].items())[:4])
    print(f"  {mid:8s}: {pfx_str}, n={d['total_tokens']}")

results['selectivity'] = {
    'n_testable': len(testable_middles),
    'n_excluded': excluded_count,
    'min_tokens': MIN_B_TOKENS,
    'category_sizes': {cat: categories.get(cat, 0) for cat in ['locked', 'dominant', 'bimodal', 'promiscuous']},
    'category_pcts': {cat: round(100 * categories.get(cat, 0) / len(testable_middles), 1)
                      for cat in ['locked', 'dominant', 'bimodal', 'promiscuous']},
    'concentration_distribution': conc_bins,
    'concentration_stats': {
        'mean': round(float(np.mean(concentrations)), 4),
        'median': round(float(np.median(concentrations)), 4),
        'min': round(float(min(concentrations)), 4),
        'max': round(float(max(concentrations)), 4),
        'std': round(float(np.std(concentrations)), 4),
    },
    'entropy_stats': {
        'mean': round(float(np.mean(entropies)), 4),
        'median': round(float(np.median(entropies)), 4),
        'min': round(float(min(entropies)), 4),
        'max': round(float(max(entropies)), 4),
    },
    'per_middle': {m: d for m, d in sorted(selectivity_data.items(), key=lambda x: -x[1]['total_tokens'])},
}

# ============================================================
# SECTION 4: TEST 3 — Lane Alignment of PREFIX Selectivity
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: Lane Alignment of PREFIX Selectivity")
print("=" * 70)

# C649 rule: initial character determines lane prediction
# k/t/p -> QO-predicting, e/o -> CHSH-predicting, other -> neutral
def lane_prediction(middle):
    if not middle:
        return 'neutral'
    first = middle[0]
    if first in ('k', 't', 'p'):
        return 'QO'
    elif first in ('e', 'o'):
        return 'CHSH'
    else:
        return 'neutral'

# EN-family prefixes (from C570/C576)
EN_PREFIXES = {'ch', 'sh', 'qo'}
# AX/FQ prefixes
AX_PREFIXES = {'ok', 'ot', 'ct'}
# INFRA prefixes
INFRA_PREFIXES = {'da', 'do', 'sa', 'so'}

# Cross-tabulate: lane prediction x selectivity category (testable MIDDLEs only)
crosstab = defaultdict(Counter)
for mid, d in selectivity_data.items():
    lane = lane_prediction(mid)
    crosstab[lane][d['category']] += 1

print(f"\nLane Prediction x Selectivity Category:")
print(f"{'Lane':<10} {'locked':>8} {'dominant':>10} {'bimodal':>9} {'promiscuous':>13} {'total':>7}")
print("-" * 60)
for lane in ['QO', 'CHSH', 'neutral']:
    row = crosstab[lane]
    total = sum(row.values())
    print(f"{lane:<10} {row.get('locked',0):>8} {row.get('dominant',0):>10} {row.get('bimodal',0):>9} {row.get('promiscuous',0):>13} {total:>7}")

# Chi-squared test (lane x category)
from scipy.stats import chi2_contingency
cats_order = ['locked', 'dominant', 'bimodal', 'promiscuous']
lanes_order = ['QO', 'CHSH', 'neutral']
obs_table = []
for lane in lanes_order:
    row = [crosstab[lane].get(cat, 0) for cat in cats_order]
    obs_table.append(row)
obs_arr = np.array(obs_table)

# Remove zero columns for chi2
nonzero_cols = obs_arr.sum(axis=0) > 0
obs_filtered = obs_arr[:, nonzero_cols]
cats_filtered = [c for c, nz in zip(cats_order, nonzero_cols) if nz]

if obs_filtered.shape[1] >= 2 and all(obs_filtered.sum(axis=0) > 0):
    chi2, p_val, dof, expected = chi2_contingency(obs_filtered)
    cramers_v = math.sqrt(chi2 / (obs_filtered.sum() * (min(obs_filtered.shape) - 1))) if obs_filtered.sum() > 0 else 0
    print(f"\nChi-squared (lane x category): chi2={chi2:.2f}, p={p_val:.4f}, dof={dof}, Cramér's V={cramers_v:.3f}")
else:
    chi2, p_val, dof, cramers_v = float('nan'), float('nan'), 0, float('nan')
    print(f"\nChi-squared: insufficient data")

# Dominant PREFIX analysis by lane
lane_dominant_prefix = defaultdict(Counter)
for mid, d in selectivity_data.items():
    lane = lane_prediction(mid)
    dp = d['dominant_prefix']
    lane_dominant_prefix[lane][dp] += 1

print(f"\nDominant PREFIX distribution by lane prediction:")
for lane in ['QO', 'CHSH', 'neutral']:
    print(f"\n  {lane}:")
    total = sum(lane_dominant_prefix[lane].values())
    for pfx, count in lane_dominant_prefix[lane].most_common(8):
        is_en = pfx in EN_PREFIXES
        is_ax = pfx in AX_PREFIXES
        label = " (EN)" if is_en else (" (AX/FQ)" if is_ax else "")
        print(f"    {pfx:8s}: {count:3d} ({100*count/total:.1f}%){label}")

# EN-family dominance by lane
for lane in ['QO', 'CHSH', 'neutral']:
    total = sum(lane_dominant_prefix[lane].values())
    en_count = sum(lane_dominant_prefix[lane].get(p, 0) for p in EN_PREFIXES)
    print(f"\n  {lane}: EN-family dominant = {en_count}/{total} ({100*en_count/total:.1f}%)" if total > 0 else "")

results['lane_alignment'] = {
    'crosstab': {lane: dict(crosstab[lane]) for lane in lanes_order},
    'chi2': round(chi2, 3) if not math.isnan(chi2) else None,
    'p_value': round(p_val, 6) if not math.isnan(p_val) else None,
    'dof': dof,
    'cramers_v': round(cramers_v, 4) if not math.isnan(cramers_v) else None,
    'dominant_prefix_by_lane': {lane: dict(lane_dominant_prefix[lane].most_common(10)) for lane in lanes_order},
    'en_family_dominance': {},
}
for lane in lanes_order:
    total = sum(lane_dominant_prefix[lane].values())
    en_count = sum(lane_dominant_prefix[lane].get(p, 0) for p in EN_PREFIXES)
    results['lane_alignment']['en_family_dominance'][lane] = {
        'en_dominant': en_count,
        'total': total,
        'pct': round(100 * en_count / total, 1) if total > 0 else 0,
    }

# ============================================================
# SECTION 5: TEST 4 — A-Side vs B-Side PREFIX Inventory
# ============================================================

print("\n" + "=" * 70)
print("TEST 4: A-Side vs B-Side PREFIX Inventory")
print("=" * 70)

MIN_AB_TOKENS = 5

# MIDDLEs with enough tokens in both systems
ab_middles = []
for mid in pp_set:
    a_total = sum(a_prefix_middle[mid].values()) if mid in a_prefix_middle else 0
    b_total = sum(b_prefix_middle[mid].values()) if mid in b_prefix_middle else 0
    if a_total >= MIN_AB_TOKENS and b_total >= MIN_AB_TOKENS:
        ab_middles.append(mid)

print(f"\nMIDDLEs with >={MIN_AB_TOKENS} tokens in both A and B: {len(ab_middles)}")
print(f"  (of {len(pp_set)} total PP)")

# Per-MIDDLE Jaccard between A-side and B-side PREFIX sets
jaccard_scores = []
a_only_prefixes = defaultdict(set)  # MIDDLE -> set of A-only PREFIXes
b_only_prefixes = defaultdict(set)  # MIDDLE -> set of B-only PREFIXes
shared_prefixes = defaultdict(set)

for mid in ab_middles:
    a_pfx_set = set(a_prefix_middle[mid].keys())
    b_pfx_set = set(b_prefix_middle[mid].keys())
    intersection = a_pfx_set & b_pfx_set
    union = a_pfx_set | b_pfx_set
    jaccard = len(intersection) / len(union) if union else 0
    jaccard_scores.append(jaccard)

    a_only = a_pfx_set - b_pfx_set
    b_only = b_pfx_set - a_pfx_set
    if a_only:
        a_only_prefixes[mid] = a_only
    if b_only:
        b_only_prefixes[mid] = b_only
    shared_prefixes[mid] = intersection

print(f"\nJaccard (A PREFIX set vs B PREFIX set):")
print(f"  Mean:   {np.mean(jaccard_scores):.3f}")
print(f"  Median: {np.median(jaccard_scores):.3f}")
print(f"  Min:    {min(jaccard_scores):.3f}")
print(f"  Max:    {max(jaccard_scores):.3f}")

# Direction: which system has more PREFIXes per MIDDLE?
a_wider = 0
b_wider = 0
equal = 0
for mid in ab_middles:
    a_n = len(a_prefix_middle[mid])
    b_n = len(b_prefix_middle[mid])
    if a_n > b_n:
        a_wider += 1
    elif b_n > a_n:
        b_wider += 1
    else:
        equal += 1

print(f"\nPREFIX breadth comparison:")
print(f"  A has more PREFIXes: {a_wider}")
print(f"  B has more PREFIXes: {b_wider}")
print(f"  Equal: {equal}")

if a_wider > b_wider:
    direction = "A_WIDER"
    print(f"  Direction: A offers more PREFIX combinations (B selects from A's offerings)")
elif b_wider > a_wider:
    direction = "B_WIDER"
    print(f"  Direction: B uses more PREFIX combinations than A records show")
else:
    direction = "BALANCED"
    print(f"  Direction: Balanced PREFIX breadth")

# Count of MIDDLEs with A-only or B-only PREFIXes
n_a_only = len(a_only_prefixes)
n_b_only = len(b_only_prefixes)
print(f"\nMIDDLEs with A-only PREFIXes: {n_a_only}")
print(f"MIDDLEs with B-only PREFIXes: {n_b_only}")

# Examples of A-only and B-only
if a_only_prefixes:
    print(f"\nA-only PREFIX examples (first 5):")
    for mid in sorted(a_only_prefixes, key=lambda m: -sum(a_prefix_middle[m].values()))[:5]:
        a_pfx = a_only_prefixes[mid]
        print(f"  {mid:8s}: A-only PREFIXes = {sorted(a_pfx)}, shared = {sorted(shared_prefixes[mid])}")

if b_only_prefixes:
    print(f"\nB-only PREFIX examples (first 5):")
    for mid in sorted(b_only_prefixes, key=lambda m: -sum(b_prefix_middle[m].values()))[:5]:
        b_pfx = b_only_prefixes[mid]
        print(f"  {mid:8s}: B-only PREFIXes = {sorted(b_pfx)}, shared = {sorted(shared_prefixes[mid])}")

results['ab_comparison'] = {
    'n_compared': len(ab_middles),
    'min_tokens': MIN_AB_TOKENS,
    'jaccard_stats': {
        'mean': round(float(np.mean(jaccard_scores)), 4),
        'median': round(float(np.median(jaccard_scores)), 4),
        'min': round(float(min(jaccard_scores)), 4),
        'max': round(float(max(jaccard_scores)), 4),
        'std': round(float(np.std(jaccard_scores)), 4),
    },
    'breadth_comparison': {
        'a_wider': a_wider,
        'b_wider': b_wider,
        'equal': equal,
        'direction': direction,
    },
    'a_only_prefix_middles': n_a_only,
    'b_only_prefix_middles': n_b_only,
}

# ============================================================
# SECTION 6: SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY: PREFIXxMIDDLE Inventory")
print("=" * 70)

print(f"""
CONTINGENCY TABLE:
  {n_middles} PP MIDDLEs x {n_prefixes} PREFIXes
  Sparsity: {sparsity:.3f} ({100*sparsity:.1f}% zero cells)
  Total B-side PP tokens: {b_total_pp_tokens}

EXCLUSIVITY SPECTRUM:
  Exclusive (1 PREFIX):  {len(exclusive_1):3d} ({100*len(exclusive_1)/n_middles:.1f}%)
  Low (2-3 PREFIXes):   {len(low_2_3):3d} ({100*len(low_2_3)/n_middles:.1f}%)
  High (4+ PREFIXes):   {len(high_4plus):3d} ({100*len(high_4plus)/n_middles:.1f}%)

SELECTIVITY CATEGORIES (>={MIN_B_TOKENS} tokens, n={len(testable_middles)}):
  Locked (>=0.95):      {categories.get('locked',0):3d} ({100*categories.get('locked',0)/len(testable_middles):.1f}%)
  Dominant (0.70-0.95): {categories.get('dominant',0):3d} ({100*categories.get('dominant',0)/len(testable_middles):.1f}%)
  Bimodal (2x>=0.25):   {categories.get('bimodal',0):3d} ({100*categories.get('bimodal',0)/len(testable_middles):.1f}%)
  Promiscuous (<0.50):  {categories.get('promiscuous',0):3d} ({100*categories.get('promiscuous',0)/len(testable_middles):.1f}%)

CONCENTRATION: mean={np.mean(concentrations):.3f}, median={np.median(concentrations):.3f}

LANE x SELECTIVITY: chi2={chi2:.2f}, p={p_val:.4f}, V={cramers_v:.3f}

A vs B PREFIX INVENTORY:
  Compared: {len(ab_middles)} MIDDLEs
  Jaccard: mean={np.mean(jaccard_scores):.3f}, median={np.median(jaccard_scores):.3f}
  Direction: {direction} (A wider: {a_wider}, B wider: {b_wider}, Equal: {equal})
""")

# Save results
output_path = RESULTS_DIR / 'prefix_middle_inventory.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"Results saved to {output_path}")
