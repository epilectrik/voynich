#!/usr/bin/env python3
"""Phase 389: Rosettes Structural Validation (4 tests).

Tests whether the Rosettes metalayer (C1095) behaves like an index
at the STRUCTURAL level, not just the vocabulary level.

V1: C475 incompatibility - region independence test
V2: Bridge MIDDLE enrichment test
V3: Affordance bin distribution test
V4: PREFIX distribution test
"""
import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer, BFolioDecoder

# ============================================================
# SETUP
# ============================================================
tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

results = {
    'phase': 389,
    'name': 'ROSETTES_STRUCTURAL_VALIDATION',
    'test_count': 4,
    'verdicts': {},
}

# Region type classification (C1093)
LABEL_REGIONS = {'B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'W1'}
DESCRIPTION_REGIONS = {'C2', 'D1', 'M3', 'N1', 'N2', 'U3', 'V1', 'V2'}

def round_floats(obj, decimals=4):
    """Recursively round floats for JSON serialization."""
    if isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, decimals) for v in obj]
    return obj

# ============================================================
# PRE-COMPUTE: Load external data
# ============================================================
print("Loading pre-computed data...")

# 1. Bridge MIDDLEs (C1013)
bridge_path = ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

# 2. Affordance bins (C995)
aff_path = ROOT / 'data/middle_affordance_table.json'
with open(aff_path, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)

# Build MIDDLE -> bin mapping (entries are in 'middles' sub-key)
middle_to_bin = {}
middle_to_bin_label = {}
middles_section = aff_data.get('middles', {})
for mid_key, mid_val in middles_section.items():
    if isinstance(mid_val, dict) and 'affordance_bin' in mid_val:
        middle_to_bin[mid_key] = mid_val['affordance_bin']
        middle_to_bin_label[mid_key] = mid_val.get('affordance_label', '')
print(f"  Affordance bin mappings: {len(middle_to_bin)}")

BIN_LABELS = {
    0: 'FLOW_TERMINAL', 1: 'ROUTINE_SPECIALIZED',
    2: 'PRECISION_SPECIALIZED', 3: 'COMPOUND_TERMINAL',
    4: 'BULK_OPERATIONAL', 5: 'SETTLING_SPECIALIZED',
    6: 'HUB_UNIVERSAL', 7: 'ENERGY_SPECIALIZED',
    8: 'STABILITY_CRITICAL', 9: 'PHASE_SENSITIVE',
}

# ============================================================
# PRE-COMPUTE: Build MIDDLE sets
# ============================================================
print("Building MIDDLE inventories...")

# Rosettes: per-region MIDDLEs for f85v2
ros_region_middles = {}  # region -> list of MIDDLEs (with repeats for token counting)
ros_region_middle_sets = {}  # region -> set of unique MIDDLEs
ros_region_prefixes = {}  # region -> list of prefixes

for region in ra.get_regions('f85v2'):
    toks = ra.get_tokens('f85v2', region)
    mids = []
    pres = []
    for t in toks:
        m = morph.extract(t.word)
        if m.middle:
            mids.append(m.middle)
        if m.prefix:
            pres.append(m.prefix)
    ros_region_middles[region] = mids
    ros_region_middle_sets[region] = set(mids)
    ros_region_prefixes[region] = pres

# Rosettes: per-folio MIDDLEs (all folios)
ros_folio_middles = {}
ros_folio_prefixes = {}
for folio in ra.ROSETTES_FOLIOS:
    toks = ra.get_tokens(folio)
    mids = []
    pres = []
    for t in toks:
        m = morph.extract(t.word)
        if m.middle:
            mids.append(m.middle)
        if m.prefix:
            pres.append(m.prefix)
    ros_folio_middles[folio] = mids
    ros_folio_prefixes[folio] = pres

# Rosettes: all MIDDLEs combined
ros_all_middles = []
ros_all_prefixes = []
for folio in ra.ROSETTES_FOLIOS:
    ros_all_middles.extend(ros_folio_middles[folio])
    ros_all_prefixes.extend(ros_folio_prefixes[folio])
ros_all_middle_set = set(ros_all_middles)

# B corpus: per-line MIDDLEs (for V1 reference), excluding Rosettes
b_line_middles = defaultdict(list)  # (folio, line) -> [middles]
b_all_middles = []
b_all_prefixes = []
for tok in tx.currier_b():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    m = morph.extract(tok.word)
    if m.middle:
        b_line_middles[(tok.folio, tok.line)].append(m.middle)
        b_all_middles.append(m.middle)
    if m.prefix:
        b_all_prefixes.append(m.prefix)
b_all_middle_set = set(b_all_middles)

# A corpus: per-record MIDDLEs
a_all_middles = []
a_all_prefixes = []
for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.middle:
        a_all_middles.append(m.middle)
    if m.prefix:
        a_all_prefixes.append(m.prefix)

# AZC corpus: per-line MIDDLEs
azc_line_middles = defaultdict(list)
azc_all_prefixes = []
for tok in tx.all():
    if tok.language == 'NA' and tok.folio not in ra.ROSETTES_FOLIOS:
        m = morph.extract(tok.word)
        if m.middle:
            azc_line_middles[(tok.folio, tok.line)].append(m.middle)
        if m.prefix:
            azc_all_prefixes.append(m.prefix)

print(f"  Rosettes: {len(ros_all_middles)} tokens, {len(ros_all_middle_set)} unique MIDDLEs")
print(f"  B corpus: {len(b_all_middles)} tokens, {len(b_all_middle_set)} unique MIDDLEs")

# ============================================================
# PRE-COMPUTE: Build C475 legal pair set from AZC lines
# ============================================================
print("Building C475 legal pair set from AZC co-occurrence...")

# Legal pairs = MIDDLE pairs that co-occur on the same AZC line
# This re-derives the original C475 analysis (AZC scope per original)
# We build from AZC only, so B corpus reference rate is an independent test
c475_all_middles = set()  # all MIDDLEs that appear in AZC lines
legal_pairs = set()  # frozenset pairs that co-occur on same AZC line

for key, mids in azc_line_middles.items():
    unique_mids = set(mids)
    c475_all_middles.update(unique_mids)
    for pair in combinations(unique_mids, 2):
        legal_pairs.add(frozenset(pair))

total_possible = len(c475_all_middles) * (len(c475_all_middles) - 1) // 2
legal_rate_baseline = len(legal_pairs) / total_possible if total_possible > 0 else 0

print(f"  C475 graph MIDDLEs: {len(c475_all_middles)}")
print(f"  Legal pairs: {len(legal_pairs)} / {total_possible} ({100*legal_rate_baseline:.1f}%)")

# ============================================================
# V1: C475 INCOMPATIBILITY - REGION INDEPENDENCE TEST
# ============================================================
print("\n" + "=" * 70)
print("V1: C475 INCOMPATIBILITY - REGION INDEPENDENCE TEST")
print("=" * 70)

v1_data = {
    'c475_graph_middles': len(c475_all_middles),
    'legal_pairs_total': len(legal_pairs),
    'legal_rate_baseline': legal_rate_baseline,
    'per_region': {},
}

def compute_legal_rate(mid_set, legal_pairs_set, c475_middles):
    """Compute fraction of testable pairs that are legal."""
    testable = mid_set & c475_middles
    coverage = len(testable) / len(mid_set) if mid_set else 0
    pairs = list(combinations(testable, 2))
    if not pairs:
        return {'coverage': coverage, 'testable_middles': len(testable),
                'total_middles': len(mid_set), 'n_pairs': 0,
                'legal_count': 0, 'legal_rate': 0, 'underpowered': True}
    legal_count = sum(1 for p in pairs if frozenset(p) in legal_pairs_set)
    return {
        'coverage': coverage,
        'testable_middles': len(testable),
        'total_middles': len(mid_set),
        'n_pairs': len(pairs),
        'legal_count': legal_count,
        'legal_rate': legal_count / len(pairs),
        'underpowered': len(pairs) < 10 or coverage < 0.5,
    }

# Per-region within-region legal rates
print(f"\n{'Region':<8} {'Type':<6} {'MIDs':>5} {'C475%':>6} {'Pairs':>6} {'Legal%':>7} {'Flag':>10}")
print("-" * 55)

for region in sorted(ros_region_middle_sets.keys()):
    mid_set = ros_region_middle_sets[region]
    if not mid_set:
        continue
    rtype = 'LABEL' if region in LABEL_REGIONS else 'DESC'
    stats = compute_legal_rate(mid_set, legal_pairs, c475_all_middles)
    v1_data['per_region'][region] = {**stats, 'type': rtype}
    flag = 'UNDERP' if stats['underpowered'] else ''
    print(f"{region:<8} {rtype:<6} {stats['total_middles']:>5} "
          f"{100*stats['coverage']:>5.1f}% {stats['n_pairs']:>6} "
          f"{100*stats['legal_rate']:>6.1f}% {flag:>10}")

# Aggregate within-region: LABEL vs DESCRIPTION
label_mids_all = set()
desc_mids_all = set()
for region, mid_set in ros_region_middle_sets.items():
    if region in LABEL_REGIONS:
        label_mids_all.update(mid_set)
    elif region in DESCRIPTION_REGIONS:
        desc_mids_all.update(mid_set)

# Within-region aggregated (union of all within-region pairs)
within_label_pairs = set()
within_desc_pairs = set()
for region, mid_set in ros_region_middle_sets.items():
    testable = mid_set & c475_all_middles
    for pair in combinations(testable, 2):
        if region in LABEL_REGIONS:
            within_label_pairs.add(frozenset(pair))
        elif region in DESCRIPTION_REGIONS:
            within_desc_pairs.add(frozenset(pair))

within_label_legal = sum(1 for p in within_label_pairs if p in legal_pairs)
within_desc_legal = sum(1 for p in within_desc_pairs if p in legal_pairs)

within_label_rate = within_label_legal / len(within_label_pairs) if within_label_pairs else 0
within_desc_rate = within_desc_legal / len(within_desc_pairs) if within_desc_pairs else 0

print(f"\nWithin-LABEL regions (aggregated): {within_label_legal}/{len(within_label_pairs)} = {100*within_label_rate:.1f}%")
print(f"Within-DESC regions (aggregated):  {within_desc_legal}/{len(within_desc_pairs)} = {100*within_desc_rate:.1f}%")

# Cross-region legal rates
# All MIDDLE pairs where one is from LABEL region, other from DESCRIPTION region
cross_label_desc_testable = (label_mids_all & c475_all_middles)
cross_desc_testable = (desc_mids_all & c475_all_middles)

cross_pairs = set()
for m1 in cross_label_desc_testable:
    for m2 in cross_desc_testable:
        if m1 != m2:
            cross_pairs.add(frozenset([m1, m2]))

cross_legal = sum(1 for p in cross_pairs if p in legal_pairs)
cross_rate = cross_legal / len(cross_pairs) if cross_pairs else 0

print(f"\nCross-region (LABEL x DESC): {cross_legal}/{len(cross_pairs)} = {100*cross_rate:.1f}%")
print(f"Random baseline: {100*legal_rate_baseline:.1f}%")

v1_data['within_label_rate'] = within_label_rate
v1_data['within_label_pairs'] = len(within_label_pairs)
v1_data['within_desc_rate'] = within_desc_rate
v1_data['within_desc_pairs'] = len(within_desc_pairs)
v1_data['cross_rate'] = cross_rate
v1_data['cross_pairs'] = len(cross_pairs)

# B corpus reference: within-line legal rate
b_within_pairs = set()
for key, mids in b_line_middles.items():
    testable = set(mids) & c475_all_middles
    for pair in combinations(testable, 2):
        b_within_pairs.add(frozenset(pair))

b_within_legal = sum(1 for p in b_within_pairs if p in legal_pairs)
b_within_rate = b_within_legal / len(b_within_pairs) if b_within_pairs else 0

# AZC corpus reference: within-line legal rate
azc_within_pairs = set()
for key, mids in azc_line_middles.items():
    testable = set(mids) & c475_all_middles
    for pair in combinations(testable, 2):
        azc_within_pairs.add(frozenset(pair))

azc_within_legal = sum(1 for p in azc_within_pairs if p in legal_pairs)
azc_within_rate = azc_within_legal / len(azc_within_pairs) if azc_within_pairs else 0

print(f"\nReference within-line legal rates:")
print(f"  B corpus:   {b_within_legal}/{len(b_within_pairs)} = {100*b_within_rate:.1f}%")
print(f"  AZC corpus: {azc_within_legal}/{len(azc_within_pairs)} = {100*azc_within_rate:.1f}%")

v1_data['b_within_rate'] = b_within_rate
v1_data['azc_within_rate'] = azc_within_rate

# B-exclusive MIDDLE fractions per region type
label_b_exclusive = sum(1 for m in label_mids_all if m not in c475_all_middles)
desc_b_exclusive = sum(1 for m in desc_mids_all if m not in c475_all_middles)
v1_data['label_b_exclusive_frac'] = label_b_exclusive / len(label_mids_all) if label_mids_all else 0
v1_data['desc_b_exclusive_frac'] = desc_b_exclusive / len(desc_mids_all) if desc_mids_all else 0
print(f"\nB-exclusive MIDDLEs (not in C475 graph):")
print(f"  LABEL regions: {label_b_exclusive}/{len(label_mids_all)} ({100*v1_data['label_b_exclusive_frac']:.1f}%)")
print(f"  DESC regions:  {desc_b_exclusive}/{len(desc_mids_all)} ({100*v1_data['desc_b_exclusive_frac']:.1f}%)")

# V1 Verdict
underpowered_count = sum(1 for r in v1_data['per_region'].values() if r.get('underpowered'))
total_regions = len(v1_data['per_region'])

# Key comparison: Rosettes rates vs B corpus rate
ros_min_rate = min(within_label_rate, within_desc_rate)
elevated = ros_min_rate > b_within_rate * 1.2  # Rosettes more compatible than B

if underpowered_count > total_regions / 2:
    v1_verdict = 'UNDERPOWERED'
elif within_label_rate > 0.15 and within_desc_rate > 0.15 and cross_rate < 0.075:
    v1_verdict = 'INDEPENDENT_ZONES'
elif elevated and cross_rate > b_within_rate:
    # All rates higher than B corpus = elevated compatibility (index signature)
    v1_verdict = 'ELEVATED_COMPATIBILITY'
elif within_label_rate > 0.15 and within_desc_rate > 0.15 and cross_rate > 0.15:
    v1_verdict = 'UNIFIED_UNIT'
elif max(within_label_rate, within_desc_rate) < 0.075:
    v1_verdict = 'UNSTRUCTURED'
else:
    if within_label_rate > 2 * within_desc_rate or within_desc_rate > 2 * within_label_rate:
        v1_verdict = 'GRADIENT_STRUCTURE'
    else:
        v1_verdict = 'MODERATE_STRUCTURE'

v1_data['verdict'] = v1_verdict
results['verdicts']['V1_incompatibility'] = v1_verdict
results['V1_data'] = v1_data
print(f"\nV1 VERDICT: {v1_verdict}")

# ============================================================
# V2: BRIDGE MIDDLE ENRICHMENT TEST
# ============================================================
print("\n" + "=" * 70)
print("V2: BRIDGE MIDDLE ENRICHMENT TEST")
print("=" * 70)

v2_data = {
    'bridge_middle_count': len(bridge_middles),
}

# B corpus bridge rate (type-level)
b_bridge_count = sum(1 for m in b_all_middle_set if m in bridge_middles)
b_bridge_rate = b_bridge_count / len(b_all_middle_set) if b_all_middle_set else 0

# Rosettes bridge rate (type-level)
ros_bridge_count = sum(1 for m in ros_all_middle_set if m in bridge_middles)
ros_bridge_rate = ros_bridge_count / len(ros_all_middle_set) if ros_all_middle_set else 0

enrichment = ros_bridge_rate / b_bridge_rate if b_bridge_rate > 0 else 0

print(f"\nOverall bridge rates (type-level):")
print(f"  B corpus:  {b_bridge_count}/{len(b_all_middle_set)} = {100*b_bridge_rate:.1f}%")
print(f"  Rosettes:  {ros_bridge_count}/{len(ros_all_middle_set)} = {100*ros_bridge_rate:.1f}%")
print(f"  Enrichment: {enrichment:.2f}x")

v2_data['b_bridge_rate'] = b_bridge_rate
v2_data['b_bridge_count'] = b_bridge_count
v2_data['b_total_middles'] = len(b_all_middle_set)
v2_data['ros_bridge_rate'] = ros_bridge_rate
v2_data['ros_bridge_count'] = ros_bridge_count
v2_data['ros_total_middles'] = len(ros_all_middle_set)
v2_data['enrichment'] = enrichment

# Fisher's exact test (2x2: bridge/non-bridge x Rosettes/B)
# Using scipy if available, otherwise manual
try:
    from scipy.stats import fisher_exact
    table = [[ros_bridge_count, len(ros_all_middle_set) - ros_bridge_count],
             [b_bridge_count, len(b_all_middle_set) - b_bridge_count]]
    odds_ratio, p_value = fisher_exact(table, alternative='greater')
    v2_data['fisher_p'] = p_value
    v2_data['fisher_odds'] = odds_ratio
    print(f"  Fisher's exact (one-sided): p={p_value:.4e}, OR={odds_ratio:.2f}")
except ImportError:
    v2_data['fisher_p'] = None
    print("  (scipy not available for Fisher's test)")

# Per region-type
print(f"\n{'Type':<8} {'Bridges':>8} {'Total':>6} {'Rate':>7} {'Enrich':>7}")
print("-" * 42)

for rtype, regions in [('LABEL', LABEL_REGIONS), ('DESC', DESCRIPTION_REGIONS)]:
    type_mids = set()
    for region in regions:
        type_mids.update(ros_region_middle_sets.get(region, set()))
    type_bridge = sum(1 for m in type_mids if m in bridge_middles)
    type_rate = type_bridge / len(type_mids) if type_mids else 0
    type_enrich = type_rate / b_bridge_rate if b_bridge_rate > 0 else 0
    print(f"{rtype:<8} {type_bridge:>8} {len(type_mids):>6} {100*type_rate:>6.1f}% {type_enrich:>6.2f}x")
    v2_data[f'{rtype.lower()}_bridge_rate'] = type_rate
    v2_data[f'{rtype.lower()}_bridge_count'] = type_bridge
    v2_data[f'{rtype.lower()}_total'] = len(type_mids)
    v2_data[f'{rtype.lower()}_enrichment'] = type_enrich

# Per-folio
print(f"\n{'Folio':<10} {'Bridges':>8} {'Total':>6} {'Rate':>7} {'Enrich':>7}")
print("-" * 45)

v2_data['per_folio'] = {}
for folio in ra.ROSETTES_FOLIOS:
    fmids = set(ros_folio_middles[folio])
    fb = sum(1 for m in fmids if m in bridge_middles)
    fr = fb / len(fmids) if fmids else 0
    fe = fr / b_bridge_rate if b_bridge_rate > 0 else 0
    print(f"{folio:<10} {fb:>8} {len(fmids):>6} {100*fr:>6.1f}% {fe:>6.2f}x")
    v2_data['per_folio'][folio] = {'bridge_count': fb, 'total': len(fmids),
                                    'rate': fr, 'enrichment': fe}

# V2 Verdict
p_val = v2_data.get('fisher_p', 1.0) or 1.0
if enrichment > 1.5 and p_val < 0.01:
    v2_verdict = 'ENRICHED'
elif enrichment < 0.5:
    v2_verdict = 'DEPLETED'
else:
    v2_verdict = 'BASELINE'

v2_data['verdict'] = v2_verdict
results['verdicts']['V2_bridge_enrichment'] = v2_verdict
results['V2_data'] = v2_data
print(f"\nV2 VERDICT: {v2_verdict}")

# ============================================================
# V3: AFFORDANCE BIN DISTRIBUTION TEST
# ============================================================
print("\n" + "=" * 70)
print("V3: AFFORDANCE BIN DISTRIBUTION TEST")
print("=" * 70)

v3_data = {}

def compute_bin_distribution(middle_set, middle_to_bin_map):
    """Map MIDDLEs to affordance bins, return distribution."""
    bin_counts = Counter()
    mapped = 0
    unmapped = 0
    for mid in middle_set:
        if mid in middle_to_bin_map:
            bin_counts[middle_to_bin_map[mid]] += 1
            mapped += 1
        else:
            unmapped += 1
    return bin_counts, mapped, unmapped

def shannon_evenness(counter, n_bins=10):
    """Compute normalized Shannon entropy (evenness)."""
    total = sum(counter.values())
    if total == 0 or len(counter) <= 1:
        return 0
    h = 0
    for c in counter.values():
        if c > 0:
            p = c / total
            h -= p * math.log(p)
    return h / math.log(n_bins)

# Rosettes type-level
ros_bins, ros_mapped, ros_unmapped = compute_bin_distribution(ros_all_middle_set, middle_to_bin)
ros_evenness = shannon_evenness(ros_bins)

# B corpus type-level
b_bins, b_mapped, b_unmapped = compute_bin_distribution(b_all_middle_set, middle_to_bin)
b_evenness = shannon_evenness(b_bins)

print(f"\nBin distribution (type-level):")
print(f"  Rosettes mapped: {ros_mapped}/{ros_mapped + ros_unmapped} ({100*ros_mapped/(ros_mapped+ros_unmapped):.0f}%)")
print(f"  B corpus mapped: {b_mapped}/{b_mapped + b_unmapped} ({100*b_mapped/(b_mapped+b_unmapped):.0f}%)")

print(f"\n{'Bin':>4} {'Label':<24} {'Ros':>5} {'Ros%':>6} {'B':>5} {'B%':>6} {'Enrich':>7}")
print("-" * 62)

bridge_bins = {0, 6, 8, 9}  # bins with bridge enrichment per C1013
bridge_bin_total_ros = 0

for b in range(10):
    rc = ros_bins.get(b, 0)
    bc = b_bins.get(b, 0)
    rp = 100 * rc / ros_mapped if ros_mapped else 0
    bp = 100 * bc / b_mapped if b_mapped else 0
    enrich = (rc / ros_mapped) / (bc / b_mapped) if bc > 0 and ros_mapped > 0 and b_mapped > 0 else 0
    label = BIN_LABELS.get(b, '?')
    marker = ' *' if b in bridge_bins else ''
    print(f"{b:>4} {label:<24} {rc:>5} {rp:>5.1f}% {bc:>5} {bp:>5.1f}% {enrich:>6.2f}x{marker}")
    if b in bridge_bins:
        bridge_bin_total_ros += rc

bridge_bin_frac = bridge_bin_total_ros / ros_mapped if ros_mapped else 0

print(f"\nBridge-enriched bins (0,6,8,9): {bridge_bin_total_ros}/{ros_mapped} = {100*bridge_bin_frac:.1f}%")
print(f"Rosettes evenness: {ros_evenness:.3f}")
print(f"B corpus evenness: {b_evenness:.3f}")

v3_data['ros_bin_counts'] = dict(ros_bins)
v3_data['b_bin_counts'] = dict(b_bins)
v3_data['ros_evenness'] = ros_evenness
v3_data['b_evenness'] = b_evenness
v3_data['bridge_bin_fraction'] = bridge_bin_frac
v3_data['ros_mapped'] = ros_mapped
v3_data['ros_unmapped'] = ros_unmapped

# Per region type
for rtype, regions in [('label', LABEL_REGIONS), ('desc', DESCRIPTION_REGIONS)]:
    type_mids = set()
    for region in regions:
        type_mids.update(ros_region_middle_sets.get(region, set()))
    t_bins, t_mapped, t_unmapped = compute_bin_distribution(type_mids, middle_to_bin)
    t_evenness = shannon_evenness(t_bins)
    t_bridge_frac = sum(t_bins.get(b, 0) for b in bridge_bins) / t_mapped if t_mapped else 0
    v3_data[f'{rtype}_bin_counts'] = dict(t_bins)
    v3_data[f'{rtype}_evenness'] = t_evenness
    v3_data[f'{rtype}_bridge_bin_frac'] = t_bridge_frac
    print(f"\n  {rtype.upper()} regions: evenness={t_evenness:.3f}, bridge bins={100*t_bridge_frac:.1f}%")

# Per-folio
v3_data['per_folio'] = {}
for folio in ra.ROSETTES_FOLIOS:
    fmids = set(ros_folio_middles[folio])
    f_bins, f_mapped, f_unmapped = compute_bin_distribution(fmids, middle_to_bin)
    f_evenness = shannon_evenness(f_bins)
    f_bridge_frac = sum(f_bins.get(b, 0) for b in bridge_bins) / f_mapped if f_mapped else 0
    v3_data['per_folio'][folio] = {
        'bin_counts': dict(f_bins),
        'evenness': f_evenness,
        'bridge_bin_frac': f_bridge_frac,
    }

# V3 Verdict
# Check enrichment pattern: are all 4 bridge bins enriched and specialized depleted?
bridge_bins_enriched = sum(1 for b in bridge_bins
                          if ros_mapped > 0 and b_mapped > 0
                          and ros_bins.get(b, 0) / ros_mapped > b_bins.get(b, 0) / b_mapped)
spec_bins = {1, 3, 5, 7}
spec_bins_depleted = sum(1 for b in spec_bins
                         if ros_mapped > 0 and b_mapped > 0
                         and ros_bins.get(b, 0) / ros_mapped < b_bins.get(b, 0) / b_mapped)

if bridge_bin_frac > 0.65 and bridge_bins_enriched >= 3:
    v3_verdict = 'BRIDGE_CONCENTRATED'
elif ros_evenness > b_evenness * 1.15:
    v3_verdict = 'ELEVATED_EVENNESS'
elif abs(ros_evenness - b_evenness) / max(b_evenness, 0.001) < 0.10:
    v3_verdict = 'B_LIKE'
else:
    bins_with_10pct = sum(1 for b in range(10) if ros_bins.get(b, 0) / max(ros_mapped, 1) > 0.10)
    if bins_with_10pct <= 3:
        v3_verdict = 'SPECIALIZED'
    else:
        v3_verdict = 'MODERATE_SPREAD'

v3_data['bridge_bins_enriched'] = bridge_bins_enriched
v3_data['spec_bins_depleted'] = spec_bins_depleted

v3_data['verdict'] = v3_verdict
results['verdicts']['V3_affordance_bins'] = v3_verdict
results['V3_data'] = v3_data
print(f"\nV3 VERDICT: {v3_verdict}")

# ============================================================
# V4: PREFIX DISTRIBUTION TEST
# ============================================================
print("\n" + "=" * 70)
print("V4: PREFIX DISTRIBUTION TEST")
print("=" * 70)

v4_data = {}

def prefix_distribution(prefix_list):
    """Compute prefix frequency distribution."""
    c = Counter(prefix_list)
    total = sum(c.values())
    dist = {p: count / total for p, count in c.most_common()} if total else {}
    return c, dist, total

def prefix_ratio(counter):
    """Compute (ok+ot)/(qo+ch) ratio."""
    ok_ot = counter.get('ok', 0) + counter.get('ot', 0)
    qo_ch = counter.get('qo', 0) + counter.get('ch', 0)
    return ok_ot / qo_ch if qo_ch > 0 else float('inf')

def jensen_shannon(p_dist, q_dist):
    """Compute Jensen-Shannon divergence between two distributions."""
    all_keys = set(p_dist.keys()) | set(q_dist.keys())
    if not all_keys:
        return 0
    jsd = 0
    for k in all_keys:
        p = p_dist.get(k, 0)
        q = q_dist.get(k, 0)
        m = (p + q) / 2
        if p > 0 and m > 0:
            jsd += 0.5 * p * math.log(p / m)
        if q > 0 and m > 0:
            jsd += 0.5 * q * math.log(q / m)
    return jsd

# Corpus distributions
ros_pre_c, ros_pre_d, ros_pre_t = prefix_distribution(ros_all_prefixes)
b_pre_c, b_pre_d, b_pre_t = prefix_distribution(b_all_prefixes)
a_pre_c, a_pre_d, a_pre_t = prefix_distribution(a_all_prefixes)
azc_pre_c, azc_pre_d, azc_pre_t = prefix_distribution(azc_all_prefixes)

ros_ratio = prefix_ratio(ros_pre_c)
b_ratio = prefix_ratio(b_pre_c)
a_ratio = prefix_ratio(a_pre_c)
azc_ratio = prefix_ratio(azc_pre_c)

# Evenness
ros_pre_evenness = shannon_evenness(ros_pre_c, n_bins=max(len(ros_pre_c), 2))
b_pre_evenness = shannon_evenness(b_pre_c, n_bins=max(len(b_pre_c), 2))
a_pre_evenness = shannon_evenness(a_pre_c, n_bins=max(len(a_pre_c), 2))
azc_pre_evenness = shannon_evenness(azc_pre_c, n_bins=max(len(azc_pre_c), 2))

# JSD between Rosettes and each baseline
jsd_ros_b = jensen_shannon(ros_pre_d, b_pre_d)
jsd_ros_a = jensen_shannon(ros_pre_d, a_pre_d)
jsd_ros_azc = jensen_shannon(ros_pre_d, azc_pre_d)

print(f"\nPrefix ratio (ok+ot)/(qo+ch):")
print(f"  Rosettes: {ros_ratio:.3f}")
print(f"  B corpus: {b_ratio:.3f}")
print(f"  A corpus: {a_ratio:.3f}")
print(f"  AZC:      {azc_ratio:.3f}")

print(f"\nPrefix evenness (Shannon H / ln(N)):")
print(f"  Rosettes: {ros_pre_evenness:.3f} (N={len(ros_pre_c)})")
print(f"  B corpus: {b_pre_evenness:.3f} (N={len(b_pre_c)})")
print(f"  A corpus: {a_pre_evenness:.3f} (N={len(a_pre_c)})")
print(f"  AZC:      {azc_pre_evenness:.3f} (N={len(azc_pre_c)})")

print(f"\nJSD from Rosettes to:")
print(f"  B corpus: {jsd_ros_b:.4f}")
print(f"  A corpus: {jsd_ros_a:.4f}")
print(f"  AZC:      {jsd_ros_azc:.4f}")

v4_data['prefix_ratios'] = {'ros': ros_ratio, 'b': b_ratio, 'a': a_ratio, 'azc': azc_ratio}
v4_data['prefix_evenness'] = {
    'ros': ros_pre_evenness, 'b': b_pre_evenness,
    'a': a_pre_evenness, 'azc': azc_pre_evenness,
}
v4_data['jsd'] = {'ros_b': jsd_ros_b, 'ros_a': jsd_ros_a, 'ros_azc': jsd_ros_azc}
v4_data['ros_prefix_counts'] = dict(ros_pre_c.most_common())
v4_data['b_prefix_counts'] = dict(b_pre_c.most_common(15))

# Top prefixes comparison
print(f"\n{'Prefix':<8} {'Ros':>6} {'Ros%':>6} {'B':>6} {'B%':>6} {'A':>6} {'AZC':>6}")
print("-" * 50)
all_pres = sorted(set(list(ros_pre_c.keys()) + list(b_pre_c.keys())[:10]),
                  key=lambda p: ros_pre_c.get(p, 0) + b_pre_c.get(p, 0), reverse=True)
for p in all_pres[:12]:
    rn = ros_pre_c.get(p, 0)
    rp = 100 * rn / ros_pre_t if ros_pre_t else 0
    bn = b_pre_c.get(p, 0)
    bp = 100 * bn / b_pre_t if b_pre_t else 0
    an = a_pre_c.get(p, 0)
    azn = azc_pre_c.get(p, 0)
    print(f"{p:<8} {rn:>6} {rp:>5.1f}% {bn:>6} {bp:>5.1f}% {an:>6} {azn:>6}")

# Per-region type
for rtype, regions in [('label', LABEL_REGIONS), ('desc', DESCRIPTION_REGIONS)]:
    type_pres = []
    for region in regions:
        type_pres.extend(ros_region_prefixes.get(region, []))
    tc, td, tt = prefix_distribution(type_pres)
    tr = prefix_ratio(tc)
    v4_data[f'{rtype}_prefix_ratio'] = tr
    v4_data[f'{rtype}_prefix_counts'] = dict(tc.most_common(10))
    print(f"\n  {rtype.upper()} regions: ratio={tr:.3f}, top={tc.most_common(5)}")

# Per-folio gradient test (C1088)
print(f"\nPer-folio prefix ratio (ok+ot)/(qo+ch) - C1088 gradient test:")
v4_data['per_folio'] = {}
for folio in ra.ROSETTES_FOLIOS:
    fc = Counter(ros_folio_prefixes[folio])
    fr = prefix_ratio(fc)
    v4_data['per_folio'][folio] = {'prefix_ratio': fr, 'prefix_counts': dict(fc.most_common(8))}
    print(f"  {folio}: ratio={fr:.3f} ({dict(fc.most_common(5))})")

# V4 Verdict: Check gradient
folio_ratios = [v4_data['per_folio'][f]['prefix_ratio']
                for f in ra.ROSETTES_FOLIOS
                if v4_data['per_folio'][f]['prefix_ratio'] != float('inf')]

# Check if monotonically decreasing (AZC->B = high ratio -> low ratio)
if len(folio_ratios) >= 3:
    decreasing_pairs = sum(1 for i in range(len(folio_ratios)-1) if folio_ratios[i] >= folio_ratios[i+1])
    gradient_strength = decreasing_pairs / (len(folio_ratios) - 1)
else:
    gradient_strength = 0

if gradient_strength > 0.7 and max(folio_ratios) > 2 * min(folio_ratios):
    v4_verdict = 'GRADIENT_CONFIRMED'
elif ros_pre_evenness > max(b_pre_evenness, a_pre_evenness, azc_pre_evenness):
    v4_verdict = 'INDEX_PROFILE'
elif jsd_ros_b < min(jsd_ros_a, jsd_ros_azc) and jsd_ros_b < 0.05:
    v4_verdict = 'B_LIKE'
elif jsd_ros_azc < min(jsd_ros_a, jsd_ros_b):
    v4_verdict = 'AZC_LIKE'
else:
    v4_verdict = 'MIXED_PROFILE'

v4_data['gradient_strength'] = gradient_strength
v4_data['verdict'] = v4_verdict
results['verdicts']['V4_prefix_distribution'] = v4_verdict
results['V4_data'] = v4_data
print(f"\nV4 VERDICT: {v4_verdict}")

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

# Score each test 0 (B-like) to 1 (index-like)
scores = {}

# V1 score
v1_score_map = {'INDEPENDENT_ZONES': 1.0, 'ELEVATED_COMPATIBILITY': 0.8,
                'GRADIENT_STRUCTURE': 0.7, 'MODERATE_STRUCTURE': 0.5,
                'UNIFIED_UNIT': 0.3, 'UNSTRUCTURED': 0.0, 'UNDERPOWERED': None}
scores['V1'] = v1_score_map.get(v1_verdict, 0.5)

# V2 score
v2_score_map = {'ENRICHED': 1.0, 'BASELINE': 0.3, 'DEPLETED': 0.0}
scores['V2'] = v2_score_map.get(v2_verdict, 0.5)

# V3 score
v3_score_map = {'BRIDGE_CONCENTRATED': 1.0, 'ELEVATED_EVENNESS': 0.8,
                'MODERATE_SPREAD': 0.5, 'B_LIKE': 0.2, 'SPECIALIZED': 0.1}
scores['V3'] = v3_score_map.get(v3_verdict, 0.5)

# V4 score
v4_score_map = {'GRADIENT_CONFIRMED': 1.0, 'INDEX_PROFILE': 0.9,
                'MIXED_PROFILE': 0.5, 'AZC_LIKE': 0.4, 'B_LIKE': 0.0}
scores['V4'] = v4_score_map.get(v4_verdict, 0.5)

# Mean score (excluding None/underpowered)
valid_scores = [v for v in scores.values() if v is not None]
mean_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

# Check label vs description gradient
label_scores = []
desc_scores = []
# V2: label vs desc enrichment
if v2_data.get('label_enrichment', 0) > 1.5:
    label_scores.append(1.0)
else:
    label_scores.append(0.3)
if v2_data.get('desc_enrichment', 0) > 1.5:
    desc_scores.append(1.0)
else:
    desc_scores.append(0.3)
# V3: label vs desc bridge bin fraction
if v3_data.get('label_bridge_bin_frac', 0) > 0.7:
    label_scores.append(1.0)
else:
    label_scores.append(0.3)
if v3_data.get('desc_bridge_bin_frac', 0) > 0.7:
    desc_scores.append(1.0)
else:
    desc_scores.append(0.3)

label_mean = sum(label_scores) / len(label_scores) if label_scores else 0
desc_mean = sum(desc_scores) / len(desc_scores) if desc_scores else 0

# Overall classification
if mean_score > 0.7:
    overall = 'STRUCTURAL_INDEX'
elif label_mean > 0.6 and desc_mean < 0.5:
    overall = 'GRADIENT_INDEX'
elif mean_score < 0.3:
    overall = 'STRUCTURAL_B'
elif all(v == 0 or v is None for v in scores.values()):
    overall = 'NULL_RESULT'
else:
    overall = 'PARTIAL_INDEX'

results['scores'] = scores
results['mean_score'] = mean_score
results['label_region_score'] = label_mean
results['desc_region_score'] = desc_mean
results['overall'] = overall

print(f"\nTest scores (0=B-like, 1=Index-like):")
for test, score in scores.items():
    verdict = results['verdicts'].get(f'{test}_incompatibility') or \
              results['verdicts'].get(f'{test}_bridge_enrichment') or \
              results['verdicts'].get(f'{test}_affordance_bins') or \
              results['verdicts'].get(f'{test}_prefix_distribution') or '?'
    print(f"  {test}: {score} ({verdict})")

print(f"\nMean score: {mean_score:.2f}")
print(f"LABEL region score: {label_mean:.2f}")
print(f"DESC region score:  {desc_mean:.2f}")
print(f"\n{'='*70}")
print(f"OVERALL CLASSIFICATION: {overall}")
print(f"{'='*70}")

if overall in ('STRUCTURAL_INDEX', 'GRADIENT_INDEX'):
    print(f"\nNote (C384): Any index function operates through vocabulary-mediated")
    print(f"correlation (C384.a), NOT through direct A-to-B addressing.")

# ============================================================
# SAVE RESULTS
# ============================================================
output_path = ROOT / 'phases/ROSETTES_STRUCTURAL_VALIDATION/results/rosettes_structural_validation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(results), f, indent=2)

print(f"\nResults saved to: {output_path}")
print(f"Tests: {results['test_count']}, Verdicts: {list(results['verdicts'].values())}")
