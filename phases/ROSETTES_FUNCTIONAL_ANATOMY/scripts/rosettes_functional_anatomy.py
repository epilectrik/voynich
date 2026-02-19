#!/usr/bin/env python3
"""
Phase 396: Rosettes Functional Anatomy

Freeform exploratory phase characterizing each Rosettes region's vocabulary
in structural and functional terms. Builds per-region profiles including
bridge density, affordance bin distribution, prefix lane composition,
macro-state distribution, and B-corpus coverage.

f85v2 regions (C1093):
  LABEL regions: B1, B2, B3, M1, M2, U1, U2, W1
  DESCRIPTION regions: C2, N1, N2, V1, V2
  Other: D1, M3, U3

Other Rosettes folios: f85r1, f85r2, f86v3, f86v4, f86v5, f86v6
"""
import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (
    Transcript, Morphology, RosettesAnalyzer,
    BFolioDecoder, BTokenAnalysis
)

RESULTS = ROOT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results'
RESULTS.mkdir(parents=True, exist_ok=True)

# ── Constants ────────────────────────────────────────────────────────────────

ROSETTES_FOLIOS = ['f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']

F85V2_REGIONS = {
    'LABEL': ['B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'W1'],
    'DESC': ['C2', 'N1', 'N2', 'V1', 'V2'],
    'OTHER': ['D1', 'M3', 'U3'],
}

ALL_F85V2_REGIONS = []
for v in F85V2_REGIONS.values():
    ALL_F85V2_REGIONS.extend(v)

BIN_LABELS = {
    0: 'FLOW_TERMINAL', 1: 'ROUTINE_SPEC', 2: 'PRECISION_SPEC',
    3: 'COMPOUND_TERM', 4: 'BULK_OP', 5: 'SETTLING_SPEC',
    6: 'HUB_UNIVERSAL', 7: 'ENERGY_SPEC', 8: 'STABILITY_CRIT',
    9: 'PHASE_SENS'
}
FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# ── Utilities ────────────────────────────────────────────────────────────────

def round_floats(obj, decimals=4):
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj


# ── Initialize ───────────────────────────────────────────────────────────────

print('=' * 70)
print('PHASE 396: ROSETTES FUNCTIONAL ANATOMY')
print('=' * 70)
print()

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# Morphology cache
_morph_cache = {}
def get_middle(word):
    if not word or not word.strip() or '*' in word:
        return None
    if word not in _morph_cache:
        m = morph.extract(word)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
        _morph_cache[word] = mid
    return _morph_cache[word]

# Load bridge MIDDLEs
bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])

# Load affordance table
aff_path = ROOT / 'data' / 'middle_affordance_table.json'
with open(aff_path, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)
mid_to_bin = {}
for mid_key, mid_val in aff_data.get('middles', {}).items():
    if isinstance(mid_val, dict) and 'affordance_bin' in mid_val:
        mid_to_bin[mid_key] = mid_val['affordance_bin']

# Build B folio MIDDLE sets for coverage analysis
print('Building B corpus MIDDLE sets...')
b_folio_mids = defaultdict(set)
b_section_map = {}
for tok in tx.currier_b():
    mid = get_middle(tok.word)
    if mid:
        b_folio_mids[tok.folio].add(mid)
    b_section_map[tok.folio] = tok.section

b_all_folios = sorted(b_folio_mids.keys())
print(f'  B folios: {len(b_all_folios)}')


# ── Profile function ─────────────────────────────────────────────────────────

def profile_region(tokens, label):
    """Build a complete structural profile for a set of tokens."""
    words = []
    middles = set()
    middle_list = []  # with repeats
    bridge_count = 0
    prefix_counts = Counter()
    lane_counts = Counter()
    bin_counts = Counter()
    macro_counts = Counter()
    class_counts = Counter()
    token_details = []

    for tok in tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        words.append(w)
        m = morph.extract(w)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None

        is_bridge = mid in bridge_middles if mid else False
        if is_bridge:
            bridge_count += 1

        if mid:
            middles.add(mid)
            middle_list.append(mid)

        bn = mid_to_bin.get(mid) if mid else None
        if bn is not None:
            bin_counts[BIN_LABELS.get(bn, str(bn))] += 1

        if m.prefix:
            prefix_counts[m.prefix] += 1
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            lane_counts[lane] += 1

        tc = decoder._token_to_class.get(w)
        if tc is not None:
            ms = decoder.MACRO_STATE.get(str(tc))
            if ms:
                macro_counts[ms] += 1
            class_counts[tc] += 1

        token_details.append({
            'word': w,
            'prefix': m.prefix,
            'middle': mid,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'is_bridge': is_bridge,
            'bin': BIN_LABELS.get(bn, None) if bn is not None else None,
            'b_class': tc,
        })

    n = len(words)
    if n == 0:
        return None

    # B-corpus coverage: how many B folios contain each CENTER MIDDLE?
    mid_coverage = {}
    for mid in sorted(middles):
        folios_with = [f for f, mids in b_folio_mids.items() if mid in mids]
        sec_counts = Counter(b_section_map[f] for f in folios_with)
        mid_coverage[mid] = {
            'b_folios': len(folios_with),
            'is_bridge': mid in bridge_middles,
            'bin': BIN_LABELS.get(mid_to_bin.get(mid), None),
            'sections': dict(sec_counts),
        }

    bridge_frac = bridge_count / n
    hub_count = bin_counts.get('HUB_UNIVERSAL', 0)
    hub_frac = hub_count / n

    # Dominant bin
    dominant_bin = bin_counts.most_common(1)[0][0] if bin_counts else None

    # Dominant lane
    dominant_lane = lane_counts.most_common(1)[0][0] if lane_counts else None

    # Dominant macro-state
    classified = sum(macro_counts.values())
    dominant_macro = macro_counts.most_common(1)[0][0] if macro_counts else None

    return {
        'label': label,
        'n_tokens': n,
        'n_unique_middles': len(middles),
        'bridge_count': bridge_count,
        'bridge_frac': bridge_frac,
        'hub_count': hub_count,
        'hub_frac': hub_frac,
        'dominant_bin': dominant_bin,
        'bin_distribution': dict(bin_counts),
        'prefix_distribution': dict(prefix_counts),
        'lane_distribution': dict(lane_counts),
        'dominant_lane': dominant_lane,
        'macro_distribution': dict(macro_counts),
        'classified_count': classified,
        'dominant_macro': dominant_macro,
        'class_distribution': {str(k): v for k, v in class_counts.most_common()},
        'middle_coverage': mid_coverage,
        'tokens': token_details,
    }


# ── Profile all regions ──────────────────────────────────────────────────────

all_profiles = {}

# f85v2 individual regions
print('\n--- f85v2 Regions ---')
for region in ALL_F85V2_REGIONS:
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue
    p = profile_region(toks, f'f85v2:{region}')
    if p:
        all_profiles[f'f85v2:{region}'] = p
        region_type = 'LABEL' if region in F85V2_REGIONS['LABEL'] else ('DESC' if region in F85V2_REGIONS['DESC'] else 'OTHER')
        print(f'  {region:3s} ({region_type:5s}): {p["n_tokens"]:3d} tokens, '
              f'bridge={p["bridge_frac"]:.0%}, hub={p["hub_frac"]:.0%}, '
              f'dominant={p["dominant_bin"]}, lane={p["dominant_lane"]}')

# Other Rosettes folios (whole-folio profiles)
print('\n--- Other Rosettes Folios ---')
for folio in ROSETTES_FOLIOS:
    if folio == 'f85v2':
        continue
    toks = ra.get_tokens(folio)
    if not toks:
        continue
    p = profile_region(toks, folio)
    if p:
        all_profiles[folio] = p
        print(f'  {folio:6s}: {p["n_tokens"]:3d} tokens, '
              f'bridge={p["bridge_frac"]:.0%}, hub={p["hub_frac"]:.0%}, '
              f'dominant={p["dominant_bin"]}, lane={p["dominant_lane"]}')


# ── Summary tables ───────────────────────────────────────────────────────────

print()
print('=' * 70)
print('SUMMARY: BRIDGE AND HUB DENSITY BY REGION')
print('=' * 70)

# Sort by bridge fraction descending
sorted_profiles = sorted(all_profiles.items(), key=lambda x: x[1]['bridge_frac'], reverse=True)

print(f'\n{"Region":<15} {"Tokens":<8} {"Bridge%":<10} {"HUB%":<8} {"Dom.Bin":<22} {"Dom.Lane":<10} {"Dom.Macro":<10}')
print('-' * 90)
for key, p in sorted_profiles:
    print(f'{key:<15} {p["n_tokens"]:<8} {p["bridge_frac"]:<10.1%} {p["hub_frac"]:<8.1%} '
          f'{(p["dominant_bin"] or "-"):<22} {(p["dominant_lane"] or "-"):<10} {(p["dominant_macro"] or "-"):<10}')


# ── CENTER deep dive ─────────────────────────────────────────────────────────

print()
print('=' * 70)
print('CENTER (C2) DEEP DIVE')
print('=' * 70)

c2 = all_profiles.get('f85v2:C2')
if c2:
    print(f'\nTokens: {c2["n_tokens"]}')
    print(f'Bridge: {c2["bridge_frac"]:.1%} ({c2["bridge_count"]}/{c2["n_tokens"]})')
    print(f'HUB: {c2["hub_frac"]:.1%}')
    print(f'\nAffordance bins:')
    for label, count in sorted(c2['bin_distribution'].items(), key=lambda x: -x[1]):
        print(f'  {label}: {count}')
    print(f'\nPrefix lanes:')
    for lane, count in sorted(c2['lane_distribution'].items(), key=lambda x: -x[1]):
        print(f'  {lane}: {count}')
    print(f'\nMacro-states:')
    for ms, count in sorted(c2['macro_distribution'].items(), key=lambda x: -x[1]):
        print(f'  {ms}: {count}')
    print(f'\nMIDDLE B-corpus coverage:')
    for mid, cov in sorted(c2['middle_coverage'].items(), key=lambda x: -x[1]['b_folios']):
        secs = ', '.join(f'{s}={n}' for s, n in sorted(cov['sections'].items()))
        print(f'  {mid:<10} {cov["b_folios"]:3d}/82 folios  [{cov["bin"] or "?"}]  {secs}')


# ── Save results ─────────────────────────────────────────────────────────────

out_path = RESULTS / 'rosettes_functional_anatomy.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(all_profiles), f, indent=2)
print(f'\nResults saved to: {out_path}')
