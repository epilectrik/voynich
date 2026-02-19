#!/usr/bin/env python3
"""
Build unified Rosettes reference JSON.

Consolidates ALL rosette data into one authoritative document:
- 16 f85v2 placement regions with full per-token morphological data
- 9 rosette grid with visual descriptions and combined profiles
- 6 outside-face folios (Quire 14 back) with full token data
- Foldout physical structure, topology, corner doodles
- Pre-computed functional profiles (kernel, bins, lanes, macros)
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
OUT_PATH = ROOT / 'data' / 'rosettes_unified.json'

# ── Load infrastructure ─────────────────────────────────────────────────────

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# Bridge MIDDLEs
bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_middles = set(json.load(f)['t5_structural_profile']['bridge_middles'])

# Affordance table
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

# Existing reference JSON (for visual descriptions)
ref_path = RESULTS / 'rosettes_reference.json'
with open(ref_path, 'r', encoding='utf-8') as f:
    existing_ref = json.load(f)

# Existing functional profiling JSON
prof_path = RESULTS / 'rosettes_functional_profiling.json'
with open(prof_path, 'r', encoding='utf-8') as f:
    existing_prof = json.load(f)

# Pre-compute B section MIDDLE sets for section concentration
section_middles = {}
for tok in tx.currier_b():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    m = morph.extract(tok.word)
    mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
    if mid:
        sec = tok.section
        if sec not in section_middles:
            section_middles[sec] = set()
        section_middles[sec].add(mid)


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


# ── Region-to-rosette mapping ───────────────────────────────────────────────

# Corrected mapping from voynich.nu fRos_tr.txt
# Grid: Letter=ROW (V=top, N=mid, C=bottom), Number=COL (1=left, 2=center, 3=right)
# Labels: U=top, M=mid, B=bottom

REGION_TO_ROSETTE = {
    # Ring text
    'V1': {'rosette': 'NW', 'type': 'ring_text'},
    'V2': {'rosette': 'NORTH', 'type': 'ring_text'},
    # V3 = NE ring text (NOT TRANSCRIBED)
    'N1': {'rosette': 'WEST', 'type': 'ring_text'},
    'N2': {'rosette': 'CENTER', 'type': 'ring_text'},
    # N3 = EAST ring text (NOT TRANSCRIBED)
    # C1 = SW ring text (NOT TRANSCRIBED)
    'C2': {'rosette': 'SOUTH', 'type': 'ring_text'},
    # C3 = SE ring text (NOT TRANSCRIBED)
    # Labels
    'U1': {'rosette': 'NW', 'type': 'labels'},
    'U2': {'rosette': 'NORTH', 'type': 'labels'},
    'U3': {'rosette': 'NE', 'type': 'labels'},
    'M1': {'rosette': 'WEST', 'type': 'labels'},
    'M2': {'rosette': 'CENTER', 'type': 'labels'},
    'M3': {'rosette': 'SE', 'type': 'labels'},
    'B1': {'rosette': 'SW', 'type': 'labels'},
    'B2': {'rosette': 'SOUTH', 'type': 'labels'},
    'B3': {'rosette': 'SE', 'type': 'labels'},
    # Special
    'D1': {'rosette': 'SW', 'type': 'corner_doodle_text'},
    'W1': {'rosette': 'NW', 'type': 'margin'},
}

ROSETTE_REGIONS = {
    'NW': ['V1', 'U1', 'W1'],
    'NORTH': ['V2', 'U2'],
    'NE': ['U3'],          # V3 ring text NOT TRANSCRIBED
    'WEST': ['N1', 'M1'],
    'CENTER': ['N2', 'M2'],
    'EAST': [],            # N3 ring text NOT TRANSCRIBED, no labels on f85v2
    'SW': ['B1', 'D1'],    # C1 ring text NOT TRANSCRIBED
    'SOUTH': ['C2', 'B2'],
    'SE': ['B3', 'M3'],    # C3 ring text NOT TRANSCRIBED
}

ROSETTE_TYPE = {
    'NW': 'corner', 'NORTH': 'cardinal', 'NE': 'corner',
    'WEST': 'cardinal', 'CENTER': 'center', 'EAST': 'cardinal',
    'SW': 'corner', 'SOUTH': 'cardinal', 'SE': 'corner',
}

ROSETTE_CONNECTS = {
    'NW': ['NORTH', 'WEST'],
    'NORTH': ['CENTER', 'NW', 'NE'],
    'NE': ['NORTH', 'EAST'],
    'WEST': ['CENTER', 'NW', 'SW'],
    'CENTER': ['NORTH', 'SOUTH', 'EAST', 'WEST'],
    'EAST': ['CENTER', 'NE', 'SE'],
    'SW': ['WEST', 'SOUTH'],
    'SOUTH': ['CENTER', 'SW', 'SE'],
    'SE': ['SOUTH', 'EAST'],
}

CORNER_DOODLES = {
    'NW': 'Sun',
    'NE': 'Pie chart / T-O map',
    'SW': 'Constellation',
    'SE': 'Sun',
}

MISSING_RING_TEXT = {
    'V3_NE': 'Northeast corner ring text — not transcribed. Panel f86r6.',
    'N3_EAST': 'East cardinal ring text — not transcribed. On fold between f86r5 and f86r6.',
    'C1_SW': 'Southwest corner ring text — not transcribed. Panel f85v1.',
    'C3_SE': 'Southeast corner ring text — not transcribed. Panel f86r5.',
}

LABEL_COVERAGE = {
    'U1': 'NW rosette interior + connecting roads to N, S, SE',
    'U2': 'NORTH rosette interior + S connections',
    'U3': 'NE rosette interior + connections to N, E, toward center',
    'M1': 'WEST rosette interior + E connections',
    'M2': 'CENTER rosette interior + mushroom areas (transcriber visual note)',
    'M3': 'SE rosette interior + W connections',
    'B1': 'SW rosette interior + passages, fountains, connecting roads (most path-heavy)',
    'B2': 'SOUTH rosette windmill interior (transcriber visual note) + N connections',
    'B3': 'SE rosette + connections to S, center',
}

OUTSIDE_FACE_INFO = {
    'f85r1': {'content': 'Text-only paragraph page', 'section': 'T'},
    'f85r2': {'content': 'Cosmological sun diagram', 'section': 'C'},
    'f86v3': {'content': 'Incomplete cosmological diagram + 4 paragraph blocks + Q quadrant text', 'section': 'C'},
    'f86v4': {'content': 'Cosmological moon diagram', 'section': 'C'},
    'f86v5': {'content': 'Text-only paragraph page', 'section': 'C'},
    'f86v6': {'content': 'Text-only paragraph page', 'section': 'C'},
}


# ── Token extraction helper ─────────────────────────────────────────────────

def extract_token_detail(word):
    """Extract full morphological detail for a token word."""
    m = morph.extract(word)
    mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
    is_bridge = mid in bridge_middles if mid else False
    bn = mid_to_bin.get(mid) if mid else None
    bl = BIN_LABELS.get(bn) if bn is not None else None
    lane = BTokenAnalysis._get_prefix_lane(m.prefix) if m.prefix else None
    tc = decoder._token_to_class.get(word)
    ms = None
    if tc is not None:
        ms = decoder.MACRO_STATE.get(str(tc))

    return {
        'word': word,
        'prefix': m.prefix,
        'articulator': m.articulator,
        'middle': mid,
        'suffix': m.suffix,
        'is_bridge': is_bridge,
        'affordance_bin': bl,
        'prefix_lane': lane,
        'macro_state': ms,
        'b_class': tc,
    }


def compute_region_summary(tokens_detail):
    """Compute summary stats for a list of token detail dicts."""
    n = len(tokens_detail)
    if n == 0:
        return {'n_tokens': 0}

    middles = set()
    bridge_count = 0
    hub_count = 0
    prefix_counts = Counter()
    lane_counts = Counter()
    bin_counts = Counter()
    macro_counts = Counter()
    k_count = h_count = e_count = 0

    for td in tokens_detail:
        mid = td['middle']
        if mid:
            middles.add(mid)
            for c in mid:
                if c == 'k': k_count += 1
                elif c == 'h': h_count += 1
                elif c == 'e': e_count += 1
        if td['is_bridge']:
            bridge_count += 1
        if td['affordance_bin'] == 'HUB_UNIVERSAL':
            hub_count += 1
        if td['affordance_bin']:
            bin_counts[td['affordance_bin']] += 1
        if td['prefix_lane']:
            lane_counts[td['prefix_lane']] += 1
        if td['macro_state']:
            macro_counts[td['macro_state']] += 1
        if td.get('prefix'):
            prefix_counts[td['prefix']] += 1

    khe = k_count + h_count + e_count
    return {
        'n_tokens': n,
        'n_unique_middles': len(middles),
        'bridge_count': bridge_count,
        'bridge_frac': bridge_count / n if n else 0,
        'hub_count': hub_count,
        'hub_frac': hub_count / n if n else 0,
        'kernel': {
            'k_count': k_count, 'h_count': h_count, 'e_count': e_count,
            'khe_total': khe,
            'k_frac': k_count / khe if khe else 0,
            'h_frac': h_count / khe if khe else 0,
            'e_frac': e_count / khe if khe else 0,
            'k_to_e': k_count / e_count if e_count else None,
        },
        'dominant_bin': bin_counts.most_common(1)[0][0] if bin_counts else None,
        'dominant_lane': lane_counts.most_common(1)[0][0] if lane_counts else None,
        'dominant_macro': macro_counts.most_common(1)[0][0] if macro_counts else None,
        'affordance_bins': dict(bin_counts.most_common()),
        'prefix_lanes': dict(lane_counts.most_common()),
        'prefixes': dict(prefix_counts.most_common()),
        'macro_states': dict(macro_counts.most_common()),
        'unique_middles': sorted(middles),
        'bridge_middles': sorted(middles & bridge_middles),
        'nonbridge_middles': sorted(middles - bridge_middles),
    }


def compute_section_concentration(middles_set):
    """Compute what fraction of a rosette's MIDDLEs appear in each B section."""
    if not middles_set:
        return {}
    result = {}
    for sec, sec_mids in section_middles.items():
        overlap = middles_set & sec_mids
        result[sec] = len(overlap) / len(middles_set) if middles_set else 0
    return result


# ── Process f85v2 regions ────────────────────────────────────────────────────

print('Processing f85v2 regions...')
ALL_REGIONS = ['B1', 'B2', 'B3', 'C2', 'D1', 'M1', 'M2', 'M3',
               'N1', 'N2', 'U1', 'U2', 'U3', 'V1', 'V2', 'W1']

regions_data = {}
for region in ALL_REGIONS:
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue

    # Build lines
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
    token_details = []
    for t in toks:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        token_details.append(extract_token_detail(w))

    summary = compute_region_summary(token_details)
    mapping = REGION_TO_ROSETTE.get(region, {})

    regions_data[region] = {
        'rosette': mapping.get('rosette', 'UNKNOWN'),
        'text_type': mapping.get('type', 'UNKNOWN'),
        'coverage_note': LABEL_COVERAGE.get(region, ''),
        'summary': summary,
        'lines': {k: v for k, v in sorted(lines.items(), key=lambda x: x[0])},
        'token_sequence': [td['word'] for td in token_details],
        'tokens': token_details,
    }

    print(f'  {region:3s}: {summary["n_tokens"]:3d} tokens -> {mapping.get("rosette", "?")} ({mapping.get("type", "?")})')

# ── Build rosette grid ───────────────────────────────────────────────────────

print('\nBuilding rosette grid...')
rosette_grid = {}
grid_visuals = existing_ref.get('_metadata', {}).get('rosette_grid', {})

for position in ['NW', 'NORTH', 'NE', 'WEST', 'CENTER', 'EAST', 'SW', 'SOUTH', 'SE']:
    region_codes = ROSETTE_REGIONS[position]
    visual_data = grid_visuals.get(position, {})

    entry = {
        'position': position,
        'type': ROSETTE_TYPE[position],
        'connects_to': ROSETTE_CONNECTS[position],
        'visual': visual_data.get('visual', ''),
    }

    if position in CORNER_DOODLES:
        entry['corner_doodle'] = CORNER_DOODLES[position]

    # Determine ring text code for this position
    ring_code_map = {'NW': 'V1', 'NORTH': 'V2', 'NE': 'V3', 'WEST': 'N1',
                     'CENTER': 'N2', 'EAST': 'N3', 'SW': 'C1', 'SOUTH': 'C2', 'SE': 'C3'}
    ring_code = ring_code_map[position]

    if ring_code in regions_data:
        rd = regions_data[ring_code]
        entry['ring_text'] = {
            'region_code': ring_code,
            'n_tokens': rd['summary']['n_tokens'],
            'tokens': rd['tokens'],
            'lines': rd['lines'],
            'summary': {k: v for k, v in rd['summary'].items()
                       if k not in ('unique_middles', 'bridge_middles', 'nonbridge_middles',
                                    'affordance_bins', 'prefix_lanes', 'prefixes', 'macro_states')},
        }
    else:
        entry['ring_text'] = {
            'region_code': ring_code,
            'status': 'NOT_TRANSCRIBED',
            'note': MISSING_RING_TEXT.get(f'{ring_code}_{position}', 'Not available in transcription'),
        }

    # Labels
    label_code_map = {'NW': 'U1', 'NORTH': 'U2', 'NE': 'U3', 'WEST': 'M1',
                      'CENTER': 'M2', 'EAST': None, 'SW': 'B1', 'SOUTH': 'B2', 'SE': 'B3'}
    label_code = label_code_map[position]

    if label_code and label_code in regions_data:
        rd = regions_data[label_code]
        entry['labels'] = {
            'region_code': label_code,
            'coverage_note': LABEL_COVERAGE.get(label_code, ''),
            'n_tokens': rd['summary']['n_tokens'],
            'tokens': rd['tokens'],
            'lines': rd['lines'],
            'summary': {k: v for k, v in rd['summary'].items()
                       if k not in ('unique_middles', 'bridge_middles', 'nonbridge_middles',
                                    'affordance_bins', 'prefix_lanes', 'prefixes', 'macro_states')},
        }
    elif label_code is None:
        entry['labels'] = {'region_code': None, 'status': 'NO_LABELS_ON_F85V2'}
    else:
        entry['labels'] = {'region_code': label_code, 'status': 'EMPTY'}

    # SE has a second label code (M3)
    if position == 'SE' and 'M3' in regions_data:
        rd = regions_data['M3']
        entry['labels_secondary'] = {
            'region_code': 'M3',
            'coverage_note': LABEL_COVERAGE.get('M3', ''),
            'n_tokens': rd['summary']['n_tokens'],
            'tokens': rd['tokens'],
            'lines': rd['lines'],
            'summary': {k: v for k, v in rd['summary'].items()
                       if k not in ('unique_middles', 'bridge_middles', 'nonbridge_middles',
                                    'affordance_bins', 'prefix_lanes', 'prefixes', 'macro_states')},
        }

    # Special regions
    if position == 'SW' and 'D1' in regions_data:
        rd = regions_data['D1']
        entry['corner_doodle_text'] = {
            'region_code': 'D1',
            'n_tokens': rd['summary']['n_tokens'],
            'tokens': rd['tokens'],
            'summary': {k: v for k, v in rd['summary'].items()
                       if k not in ('unique_middles', 'bridge_middles', 'nonbridge_middles',
                                    'affordance_bins', 'prefix_lanes', 'prefixes', 'macro_states')},
        }

    if position == 'NW' and 'W1' in regions_data:
        rd = regions_data['W1']
        entry['margin'] = {
            'region_code': 'W1',
            'n_tokens': rd['summary']['n_tokens'],
            'tokens': rd['tokens'],
            'summary': {k: v for k, v in rd['summary'].items()
                       if k not in ('unique_middles', 'bridge_middles', 'nonbridge_middles',
                                    'affordance_bins', 'prefix_lanes', 'prefixes', 'macro_states')},
        }

    # Combined profile (all tokens from all region codes for this rosette)
    all_tokens = []
    for code in region_codes:
        if code in regions_data:
            all_tokens.extend(regions_data[code]['tokens'])

    combined = compute_region_summary(all_tokens)
    combined['b_section_concentration'] = compute_section_concentration(
        set(combined.get('unique_middles', []))
    )
    entry['combined_profile'] = combined

    rosette_grid[position] = entry
    print(f'  {position:8s}: {combined["n_tokens"]:3d} tokens, '
          f'bridge={combined.get("bridge_frac", 0):.0%}, '
          f'hub={combined.get("hub_frac", 0):.0%}')


# ── Process outside-face folios ──────────────────────────────────────────────

print('\nProcessing outside-face folios...')
OUTSIDE_FOLIOS = ['f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']
outside_face = {}

for folio in OUTSIDE_FOLIOS:
    toks = ra.get_tokens(folio)
    if not toks:
        continue

    # Group by placement code
    placement_groups = defaultdict(list)
    for t in toks:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        placement_groups[t.placement].append(t)

    folio_tokens = []
    folio_regions = {}
    for placement, ptoks in sorted(placement_groups.items()):
        lines = {}
        token_details = []
        for t in ptoks:
            w = t.word.strip()
            td = extract_token_detail(w)
            token_details.append(td)
            lk = str(t.line)
            if lk not in lines:
                lines[lk] = []
            lines[lk].append(w)

        summary = compute_region_summary(token_details)
        folio_regions[placement] = {
            'n_tokens': summary['n_tokens'],
            'n_lines': len(lines),
            'tokens': token_details,
            'lines': {k: v for k, v in sorted(lines.items(), key=lambda x: x[0])},
            'summary': summary,
        }
        folio_tokens.extend(token_details)

    folio_summary = compute_region_summary(folio_tokens)
    info = OUTSIDE_FACE_INFO.get(folio, {})
    track = ra._best_track(folio, list(placement_groups.keys())[0]) if placement_groups else '?'

    outside_entry = {
        'content': info.get('content', ''),
        'section': info.get('section', ''),
        'transcriber': track,
        'n_tokens': folio_summary['n_tokens'],
        'placement_codes': {p: len(toks) for p, toks in sorted(placement_groups.items())},
        'summary': folio_summary,
        'regions': folio_regions,
    }

    # Q note for f86v3
    if folio == 'f86v3' and 'Q' in folio_regions:
        outside_entry['q_note'] = (
            'Q = quadrant text on incomplete cosmological diagram. '
            f'{folio_regions["Q"]["n_tokens"]} tokens, lines 9-16.'
        )

    outside_face[folio] = outside_entry
    codes_str = ', '.join(f'{p}={len(toks)}' for p, toks in sorted(placement_groups.items()))
    print(f'  {folio}: {folio_summary["n_tokens"]} tokens [{codes_str}]')


# ── Compute total counts ─────────────────────────────────────────────────────

rosettes_total = sum(rd['summary']['n_tokens'] for rd in regions_data.values())
outside_total = sum(of['n_tokens'] for of in outside_face.values())

# ── Assemble unified JSON ────────────────────────────────────────────────────

print('\nAssembling unified JSON...')

unified = {
    '_metadata': {
        'version': '1.0',
        'description': 'Unified Rosettes foldout reference — Quire 14 bifolio',
        'source_mapping': 'voynich.nu fRos_tr.txt',
        'grid_system': 'Letter=ROW (V=top, N=mid, C=bottom), Number=COL (1=left, 2=center, 3=right)',
        'label_system': 'Letter=ROW (U=top, M=mid, B=bottom), Number=COL (1=left, 2=center, 3=right)',
        'transcriber': 'U (no H-track available for f85v2)',
        'rosettes_folio': 'f85v2',
        'rosettes_tokens': rosettes_total,
        'rosettes_regions': len(regions_data),
        'outside_face_folios': OUTSIDE_FOLIOS,
        'outside_face_tokens': outside_total,
        'total_quire14_tokens': rosettes_total + outside_total,
    },

    'foldout_structure': {
        '_note': 'Quire 14 bifolio — single sheet, 3 folds, 6 panels per side',
        'inside_face': {
            '_note': 'The 9-rosette diagram — one continuous illustration spanning all 6 panels',
            'top_row': ['f85v2 (NW)', 'f86r4 (NORTH)', 'f86r6 (NE)'],
            'bottom_row': ['f85v1 (SW)', 'f86r3 (SOUTH)', 'f86r5 (SE)'],
            'middle_row_note': 'WEST, CENTER, EAST sit on fold lines between panels',
            'binding': 'f85v1 -- f86r3 fold',
            'transcription_note': 'ALL rosettes text transcribed under f85v2. The f86r panels do not appear as separate folios.',
        },
        'outside_face': {
            '_note': '6 independent pages visible when foldout is closed. NOT part of the 9-rosette diagram.',
            **{folio: info['content'] for folio, info in OUTSIDE_FACE_INFO.items()},
        },
    },

    'region_to_rosette_map': REGION_TO_ROSETTE,

    'rosette_grid': rosette_grid,

    'topology': {
        'cardinal_connections': 'All 4 cardinals (N,S,E,W) connect to CENTER via conical funnels',
        'corner_connections': 'Corners connect only to adjacent cardinals, not directly to CENTER',
        'outer_ring': 'Walking-path loop connecting all 8 outer rosettes',
        'corner_doodles': CORNER_DOODLES,
        'diagonal_symmetry': 'NW-SE diagonal: both suns. SW-NE diagonal: constellation/pie chart.',
    },

    'missing_ring_text': MISSING_RING_TEXT,

    'transcriber_notes': {
        'source': 'voynich.nu fRos_tr.txt',
        'B1_SW': 'Passages, fountains, connecting roads to S, SE',
        'B2_SOUTH': 'Transcriber describes SOUTH interior as windmill',
        'M2_CENTER': 'Transcriber describes CENTER as having mushroom areas (M2.1-M2.22, M2.51-M2.55)',
    },

    'regions': regions_data,

    'outside_face': outside_face,

    'functional_profiles': {
        '_note': 'Pre-computed from rosettes_functional_profiling.py (Phase 396)',
        'kernel_profiles': existing_prof.get('analysis_1_kernel_profiles', {}),
        'macro_state_profiles': existing_prof.get('analysis_2_macro_state_profiles', {}),
        'affordance_profiles': existing_prof.get('analysis_3_affordance_profiles', {}),
        'section_concentration': existing_prof.get('analysis_4_section_profiles', {}),
        'destination_profiles': existing_prof.get('analysis_5_destination_profiles', {}),
    },
}

# ── Save ─────────────────────────────────────────────────────────────────────

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(round_floats(unified), f, indent=2, ensure_ascii=False)

print(f'\nSaved unified JSON to: {OUT_PATH}')
print(f'  Rosettes tokens: {rosettes_total}')
print(f'  Outside-face tokens: {outside_total}')
print(f'  Total Quire 14: {rosettes_total + outside_total}')
print(f'  Rosette grid positions: {len(rosette_grid)}')
print(f'  Missing ring texts: {len(MISSING_RING_TEXT)}')
