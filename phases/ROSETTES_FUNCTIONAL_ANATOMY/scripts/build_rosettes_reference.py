#!/usr/bin/env python3
"""
Build comprehensive Rosettes reference JSON for f85v2.
Includes per-region tokens, morphology, structural profiles,
and physical layout notes.
"""
import sys
import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (
    Transcript, Morphology, RosettesAnalyzer,
    BFolioDecoder, BTokenAnalysis
)

RESULTS = ROOT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results'

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# Load bridge MIDDLEs
bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_middles = set(json.load(f)['t5_structural_profile']['bridge_middles'])

# Load affordance table
aff_path = ROOT / 'data' / 'middle_affordance_table.json'
with open(aff_path, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)
mid_to_bin = {}
for mk, mv in aff_data.get('middles', {}).items():
    if isinstance(mv, dict) and 'affordance_bin' in mv:
        mid_to_bin[mk] = mv['affordance_bin']

BIN_LABELS = {
    0: 'FLOW_TERMINAL', 1: 'ROUTINE_SPECIALIZED', 2: 'PRECISION_SPECIALIZED',
    3: 'COMPOUND_TERMINAL', 4: 'BULK_OPERATIONAL', 5: 'SETTLING_SPECIALIZED',
    6: 'HUB_UNIVERSAL', 7: 'ENERGY_SPECIALIZED', 8: 'STABILITY_CRITICAL',
    9: 'PHASE_SENSITIVE'
}

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

# ── Region metadata ──────────────────────────────────────────────────────────

REGION_META = {
    'B1': {'group': 'BOTTOM', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'Largest label region (29 tokens). Heavy ot- prefix.'},
    'B2': {'group': 'BOTTOM', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'Small label set (7 tokens). All ot/ok prefixed.'},
    'B3': {'group': 'BOTTOM', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'Minimal (2 tokens).'},
    'C2': {'group': 'CENTER', 'type': 'DESCRIPTION', 'physical_position': 'CENTER_ROSETTE', 'notes': 'Central rosette. 97% bridge, 73% HUB. Ring of alembic vessels visible in illustration. Pure apparatus vocabulary.'},
    'D1': {'group': 'D_W', 'type': 'OTHER', 'physical_position': 'TBD', 'notes': '100% bridge. Small transitional region (5 tokens). Furthest from CENTER by vocabulary.'},
    'M1': {'group': 'MIDDLE', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'STABILITY_CRITICAL dominant bin. 8 tokens.'},
    'M2': {'group': 'MIDDLE', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'Second largest label region (23 tokens). SETUP lane dominant.'},
    'M3': {'group': 'MIDDLE', 'type': 'OTHER', 'physical_position': 'TBD', 'notes': 'Minimal (2 tokens). 100% bridge.'},
    'N1': {'group': 'NORTH', 'type': 'DESCRIPTION', 'physical_position': 'NORTH_CARDINAL', 'notes': 'North rosette description text. Blue spoke pattern with star/vapor. QO-dominant, HUB-heavy.'},
    'N2': {'group': 'NORTH', 'type': 'DESCRIPTION', 'physical_position': 'NORTH_CARDINAL', 'notes': 'North rosette ring text. 37 tokens, 87% bridge.'},
    'U1': {'group': 'UPPER', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'FLOW_TERMINAL dominant. SETUP lane. 8 tokens.'},
    'U2': {'group': 'UPPER', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': '7 tokens. QO dominant lane.'},
    'U3': {'group': 'UPPER', 'type': 'OTHER', 'physical_position': 'TBD', 'notes': 'Minimal (2 tokens).'},
    'V1': {'group': 'VERT', 'type': 'DESCRIPTION', 'physical_position': 'TBD', 'notes': 'Highest HUB% of any region (83%). 93% bridge. QO dominant.'},
    'V2': {'group': 'VERT', 'type': 'DESCRIPTION', 'physical_position': 'TBD', 'notes': '91% bridge, 72% HUB. QO dominant.'},
    'W1': {'group': 'D_W', 'type': 'LABEL', 'physical_position': 'TBD', 'notes': 'Minimal (3 tokens). CLOSE lane dominant. FLOW_TERMINAL bin.'},
}

# ── Build per-region data ────────────────────────────────────────────────────

ALL_REGIONS = ['B1', 'B2', 'B3', 'C2', 'D1', 'M1', 'M2', 'M3',
               'N1', 'N2', 'U1', 'U2', 'U3', 'V1', 'V2', 'W1']

reference = {
    '_metadata': {
        'folio': 'f85v2',
        'description': 'Rosettes foldout central page (9 rosettes in 3x3 grid)',
        'transcriber': 'U (no H-track available for f85v2)',
        'total_regions': len(ALL_REGIONS),
        'layout': {
            'confirmed': {
                'CENTER': 'C2 (central rosette with ring of alembic vessels)',
                'NORTH_CARDINAL': 'N1, N2 (top center, blue spoke pattern, directly connected to CENTER)',
            },
            'inferred': {
                'SOUTH_CARDINAL': 'Possibly V1, V2 (VERT = vertical axis partner to NORTH, similar visual style)',
                'BOTTOM_LABELS': 'B1, B2, B3 (lower area labels, candidate for SW corner labels)',
            },
            'unknown': ['M1', 'M2', 'M3', 'U1', 'U2', 'U3', 'D1', 'W1'],
            'topology': '4 cardinals connect directly to CENTER via conical funnels. 4 corners connect only to adjacent cardinals. Outer ring path connects all 8 outer rosettes in a loop.',
        },
        'visual_notes': {
            'CENTER': 'Concentric rings. Innermost: ring of alembic/retort vessels (bulbous bodies, narrow necks). Blue radiating pattern (heat/vapor?). Scalloped filler rings. Outward-pointing projections at circumference connecting to cardinals.',
            'NORTH': 'Blue spoke/petal pattern filling center. Star/dot pattern between spokes (vapor/steam?). Cylindrical appearance. Dense ball/oval filler around inside rim. Conical connection to CENTER.',
            'SOUTH': 'Visually very similar to NORTH (matching blue spoke pattern). Conical connection to CENTER.',
            'SW_CORNER': 'Eye/lens-shaped central area (NOT circular). Flower/puff at center. Stars/vapor pattern. Scalloped ball pattern ring. Wave/water patterns radiating outward (blue wavy lines). Most fluid/aqueous rosette. No direct connection to CENTER.',
            'cardinal_connections': 'All 4 cardinals have similar conical funnel connections narrowing toward CENTER.',
            'corner_connections': 'Corners visually point toward CENTER but have no direct path connection.',
            'outer_paths': 'Walking-path style connections between adjacent outer rosettes forming a loop.',
        },
    },
    'regions': {},
}

# ── Process each region ──────────────────────────────────────────────────────

for region in ALL_REGIONS:
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue

    # Build line structure
    lines = {}
    for t in toks:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        lk = str(t.line)
        if lk not in lines:
            lines[lk] = []
        lines[lk].append(w)

    # Build token details
    token_list = []
    middles = set()
    bridge_count = 0
    prefix_counts = Counter()
    lane_counts = Counter()
    bin_counts = Counter()
    macro_counts = Counter()
    n = 0

    for t in toks:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        n += 1
        m = morph.extract(w)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None

        is_bridge = mid in bridge_middles if mid else False
        if is_bridge:
            bridge_count += 1
        if mid:
            middles.add(mid)

        bn = mid_to_bin.get(mid) if mid else None
        bl = BIN_LABELS.get(bn) if bn is not None else None
        if bl:
            bin_counts[bl] += 1

        lane = None
        if m.prefix:
            prefix_counts[m.prefix] += 1
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            lane_counts[lane] += 1

        tc = decoder._token_to_class.get(w)
        ms = None
        if tc is not None:
            ms = decoder.MACRO_STATE.get(str(tc))
            if ms:
                macro_counts[ms] += 1

        token_list.append({
            'word': w,
            'prefix': m.prefix,
            'articulator': m.articulator,
            'middle': mid,
            'suffix': m.suffix,
            'is_bridge': is_bridge,
            'affordance_bin': bl,
            'prefix_lane': lane,
            'macro_state': ms,
            'b_class': tc,
        })

    # Summary stats
    bridge_frac = bridge_count / n if n > 0 else 0.0
    hub_count = bin_counts.get('HUB_UNIVERSAL', 0)
    hub_frac = hub_count / n if n > 0 else 0.0

    region_data = {
        'metadata': REGION_META.get(region, {}),
        'summary': {
            'n_tokens': n,
            'n_lines': len(lines),
            'n_unique_middles': len(middles),
            'bridge_count': bridge_count,
            'bridge_frac': bridge_frac,
            'hub_count': hub_count,
            'hub_frac': hub_frac,
            'is_single_line': len(lines) == 1,
            'dominant_bin': bin_counts.most_common(1)[0][0] if bin_counts else None,
            'dominant_lane': lane_counts.most_common(1)[0][0] if lane_counts else None,
            'dominant_macro': macro_counts.most_common(1)[0][0] if macro_counts else None,
        },
        'distributions': {
            'affordance_bins': dict(bin_counts.most_common()),
            'prefix_lanes': dict(lane_counts.most_common()),
            'prefixes': dict(prefix_counts.most_common()),
            'macro_states': dict(macro_counts.most_common()),
        },
        'lines': {k: v for k, v in sorted(lines.items(), key=lambda x: x[0])},
        'token_sequence': [t['word'] for t in token_list],
        'tokens': token_list,
        'unique_middles': sorted(middles),
        'bridge_middles': sorted(middles & bridge_middles),
        'nonbridge_middles': sorted(middles - bridge_middles),
    }

    reference['regions'][region] = region_data
    print(f'{region:3s}: {n:3d} tokens, {len(lines):2d} lines, '
          f'bridge={bridge_frac:.0%}, hub={hub_frac:.0%}, '
          f'type={REGION_META.get(region, {}).get("type", "?")}')

# ── Also add other Rosettes folios (summary only) ───────────────────────────

reference['other_folios'] = {}
for folio in ['f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']:
    toks = ra.get_tokens(folio)
    if not toks:
        continue
    words = [t.word.strip() for t in toks if t.word.strip() and '*' not in t.word]
    mids = set()
    br = 0
    hub = 0
    for w in words:
        m = morph.extract(w)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
        if mid:
            mids.add(mid)
            if mid in bridge_middles:
                br += 1
            bn = mid_to_bin.get(mid)
            if bn == 6:
                hub += 1

    reference['other_folios'][folio] = {
        'n_tokens': len(words),
        'bridge_frac': br / len(words) if words else 0,
        'hub_frac': hub / len(words) if words else 0,
        'n_unique_middles': len(mids),
    }
    print(f'{folio}: {len(words)} tokens, bridge={br/len(words):.0%}')

# ── Save ─────────────────────────────────────────────────────────────────────

out_path = RESULTS / 'rosettes_reference.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(reference), f, indent=2, ensure_ascii=False)
print(f'\nSaved to: {out_path}')
