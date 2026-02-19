#!/usr/bin/env python3
"""
Phase 396: Rosettes Functional Profiling

Comprehensive functional profiling of each rosette's vocabulary against B programs.
Six analyses compare rosette vocabulary profiles against visual themes:
  1. Kernel Profile (k/h/e density per rosette)
  2. Role Distribution (macro-state assignments)
  3. Affordance Bin Profile (9-bin distribution)
  4. B Section Concentration (Herbal, Pharma, Stars, Bio, etc.)
  5. B Paragraph Destination Mapping (Jaccard overlap)
  6. Prefix Lane Profile (SETUP, QO, CHSH, CLOSE, LINK)

Then checks each visual prediction against the functional data.
"""
import sys
import json
import time
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

# ==============================================================================
# CONSTANTS
# ==============================================================================

# Rosette region mapping (from voynich.nu fRos_tr.txt position grid)
ROSETTE_REGIONS = {
    'NW':     ['V1', 'U1', 'W1'],
    'NORTH':  ['V2', 'U2'],
    'NE':     ['U3'],
    'WEST':   ['N1', 'M1'],
    'CENTER': ['N2', 'M2'],
    'SW':     ['B1', 'D1'],
    'SOUTH':  ['C2', 'B2'],
    'SE':     ['B3', 'M3'],
}

# Expected token counts for verification
EXPECTED_TOKENS = {
    'NW': 41, 'NORTH': 39, 'NE': 2, 'WEST': 31,
    'CENTER': 60, 'SW': 34, 'SOUTH': 40, 'SE': 4,
}

# Sparse rosettes (too few tokens for reliable conclusions)
SPARSE_ROSETTES = {'NE', 'SE'}

# Visual theme predictions
VISUAL_THEMES = {
    'NORTH':  'Sharp blue spokes, stars, heat/energy. "Windmill."',
    'SOUTH':  'Matches NORTH visually (blue spokes), heat/energy.',
    'WEST':   'Soft rounded lobes, stars between, condensation/cooling.',
    'CENTER': 'Alembic vessels, concentric rings, apparatus hub. "Mushroom areas."',
    'NW':     'Botanical -- eye/lens, bead rings, plant teeth, tube. Sun doodle.',
    'NE':     'Architectural -- castle skyline, spiral text, tendrils. Pie chart doodle.',
    'SW':     'Aqueous -- eye/lens, water streams, clouds. Constellation doodle.',
    'SE':     'Overhead map -- water basin, planted grid, pipes. Sun doodle.',
}

# Affordance bin labels (all 10 bins, keyed by string for lookup)
AFFORDANCE_BIN_NAMES = [
    'FLOW_TERMINAL', 'ROUTINE_SPECIALIZED', 'PRECISION_SPECIALIZED',
    'COMPOUND_TERMINAL', 'BULK_OPERATIONAL', 'SETTLING_SPECIALIZED',
    'HUB_UNIVERSAL', 'ENERGY_SPECIALIZED', 'STABILITY_CRITICAL',
    'PHASE_SENSITIVE'
]

# Prefix lane definitions (mirrors BTokenAnalysis._get_prefix_lane)
PREFIX_LANES = {
    'qo': 'QO', 'ok': 'QO', 'ot': 'QO', 'o': 'QO',
    'ko': 'QO', 'to': 'QO', 'po': 'QO',
    'ch': 'CHSH', 'sh': 'CHSH', 'lsh': 'CHSH',
    'pch': 'PREP', 'tch': 'PREP', 'lch': 'PREP', 'dch': 'PREP',
    'fch': 'PREP', 'kch': 'PREP', 'rch': 'PREP', 'sch': 'PREP',
    'da': 'SETUP', 'sa': 'SETUP', 'so': 'SETUP',
    'al': 'CLOSE', 'ar': 'CLOSE', 'or': 'CLOSE', 'ol': 'CLOSE',
    'lk': 'LINK', 'lo': 'LINK',
    'yk': 'INIT', 'ka': 'MAINT', 'ta': 'XFER',
    'ct': 'CTRL', 'ck': 'CTRL',
    'ke': 'KE', 'te': 'TE',
}

CANONICAL_LANES = ['SETUP', 'QO', 'CHSH', 'PREP', 'CLOSE', 'LINK',
                   'INIT', 'MAINT', 'XFER', 'CTRL', 'KE', 'TE', 'BARE']

MACRO_STATES = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']

# B section code -> full name mapping
SECTION_NAMES = {
    'H': 'Herbal', 'B': 'Bio', 'S': 'Stars',
    'C': 'Cosmo', 'T': 'Text', 'P': 'Pharma',
}


# ==============================================================================
# UTILITIES
# ==============================================================================

def round_floats(obj, decimals=4):
    """Round floats for JSON serialization, handling numpy types."""
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        if obj != obj or abs(obj) == float('inf'):  # nan or inf
            return None
        return round(obj, decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    # Handle numpy types if present
    try:
        import numpy as np
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return round(float(obj), decimals)
    except ImportError:
        pass
    return obj


def safe_div(a, b, default=0.0):
    """Safe division, returns default if b is 0."""
    return a / b if b != 0 else default


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return safe_div(inter, union)


def get_prefix_lane(prefix):
    """Map prefix to execution lane."""
    if prefix is None:
        return 'BARE'
    return PREFIX_LANES.get(prefix, prefix.upper())


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    t0 = time.time()

    print('=' * 70)
    print('PHASE 396: ROSETTES FUNCTIONAL PROFILING')
    print('=' * 70)
    print()

    # ── Initialize infrastructure ─────────────────────────────────────────
    print('Initializing...')
    ra = RosettesAnalyzer()
    morph = Morphology()
    tx = Transcript()

    # Load affordance table
    aff_path = ROOT / 'data' / 'middle_affordance_table.json'
    with open(aff_path, 'r', encoding='utf-8') as f:
        aff_data = json.load(f)
    middle_to_aff_bin = {}
    middle_to_aff_family = {}
    for mid, entry in aff_data.get('middles', {}).items():
        if 'affordance_label' in entry:
            middle_to_aff_bin[mid] = entry['affordance_label']
        if 'primary_family' in entry:
            middle_to_aff_family[mid] = entry['primary_family']

    # Load bridge MIDDLEs
    bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    bridge_middles = set()
    if bridge_path.exists():
        with open(bridge_path, 'r', encoding='utf-8') as f:
            bridge_data = json.load(f)
        bm_list = bridge_data.get('t5_structural_profile', {}).get('bridge_middles', [])
        bridge_middles = set(bm_list)
        print(f'  Loaded {len(bridge_middles)} bridge MIDDLEs')
    else:
        print('  WARNING: bridge_selection.json not found, skipping bridge analysis')

    # ── Extract rosette tokens and MIDDLEs ────────────────────────────────
    print('Extracting rosette tokens...')
    rosette_tokens = {}   # rosette_name -> [Token]
    rosette_middles = {}  # rosette_name -> set of MIDDLEs
    rosette_words = {}    # rosette_name -> list of words (for macro-state lookup)
    rosette_prefixes = {} # rosette_name -> list of prefixes (for lane analysis)

    for rname, regions in ROSETTE_REGIONS.items():
        tokens = []
        for region in regions:
            toks = ra.get_tokens('f85v2', region)
            tokens.extend(toks)
        rosette_tokens[rname] = tokens

        middles = set()
        words = []
        prefixes = []
        for tok in tokens:
            w = tok.word
            if not w.strip() or '*' in w:
                continue
            words.append(w)
            m = morph.extract(w)
            if m and m.middle and m.middle != '_EMPTY_':
                middles.add(m.middle)
            prefixes.append(m.prefix if m else None)

        rosette_middles[rname] = middles
        rosette_words[rname] = words
        rosette_prefixes[rname] = prefixes

    # Verify token counts
    print()
    print('Token counts per rosette:')
    for rname in ROSETTE_REGIONS:
        n = len(rosette_tokens[rname])
        expected = EXPECTED_TOKENS.get(rname, '?')
        flag = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        print(f'  {rname:8s}: {n:3d} tokens, {len(rosette_middles[rname]):3d} unique MIDDLEs{flag}')
    print()

    # All rosette MIDDLEs combined (for computing averages)
    all_rosette_middles = set()
    for mids in rosette_middles.values():
        all_rosette_middles |= mids

    # ══════════════════════════════════════════════════════════════════════
    # PRE-COMPUTE B CORPUS DATA (expensive, do once)
    # ══════════════════════════════════════════════════════════════════════
    print('Pre-computing B corpus data...')

    # B section MIDDLE sets
    print('  Building B section MIDDLE sets...')
    section_middles = defaultdict(set)  # section -> set of MIDDLEs
    b_tokens = list(tx.currier_b())
    for tok in b_tokens:
        if not tok.word.strip() or '*' in tok.word:
            continue
        m = morph.extract(tok.word)
        if m and m.middle and m.middle != '_EMPTY_':
            section_middles[tok.section].add(m.middle)

    b_sections = sorted(section_middles.keys())
    print(f'  Found {len(b_sections)} B sections: {", ".join(b_sections)}')

    # B folio list (unique folios from B tokens)
    b_folios = sorted(set(tok.folio for tok in b_tokens))
    print(f'  {len(b_folios)} B folios')

    # BFolioDecoder for macro-state and paragraph analysis
    print('  Initializing BFolioDecoder (this loads 49-class maps)...')
    decoder = BFolioDecoder()

    # Pre-compute token_to_class and MACRO_STATE lookups for all rosette words
    # (avoids re-analyzing in loop)
    word_to_macro = {}
    for rname, words in rosette_words.items():
        for w in words:
            if w not in word_to_macro:
                tc = decoder._token_to_class.get(w)
                ms = decoder.MACRO_STATE.get(str(tc)) if tc is not None else None
                word_to_macro[w] = ms

    # Pre-compute B paragraph MIDDLE sets (the bottleneck)
    print('  Building B paragraph MIDDLE sets (this takes 30-60s)...')
    t_para = time.time()
    b_para_middles = {}  # (folio, para_id) -> set of MIDDLEs
    for i, folio in enumerate(b_folios):
        if (i + 1) % 20 == 0:
            print(f'    ... folio {i+1}/{len(b_folios)}')
        try:
            paras = decoder.analyze_folio_paragraphs(folio)
            for pa in paras:
                key = (folio, pa.paragraph_id)
                mids = set()
                for la in pa.lines:
                    for ta in la.tokens:
                        m_result = morph.extract(ta.word)
                        if m_result and m_result.middle and m_result.middle != '_EMPTY_':
                            mids.add(m_result.middle)
                b_para_middles[key] = mids
        except Exception as e:
            # Some folios may fail; skip silently
            pass

    print(f'  Built {len(b_para_middles)} B paragraph profiles in {time.time()-t_para:.1f}s')
    print()

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS 1: KERNEL PROFILE PER ROSETTE
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ANALYSIS 1: KERNEL PROFILE PER ROSETTE')
    print('=' * 70)
    print()
    print('Character-level kernel density across all MIDDLEs per rosette.')
    print('k=energy input, h=hazard/reaction, e=escape/cooling')
    print()

    kernel_profiles = {}
    for rname in ROSETTE_REGIONS:
        k_count = h_count = e_count = total_chars = 0
        for mid in rosette_middles[rname]:
            for c in mid:
                total_chars += 1
                if c == 'k':
                    k_count += 1
                elif c == 'h':
                    h_count += 1
                elif c == 'e':
                    e_count += 1

        khe_total = k_count + h_count + e_count
        k_frac = safe_div(k_count, khe_total)
        h_frac = safe_div(h_count, khe_total)
        e_frac = safe_div(e_count, khe_total)
        k_to_e = safe_div(k_frac, e_frac, default=float('inf'))

        kernel_profiles[rname] = {
            'k_count': k_count, 'h_count': h_count, 'e_count': e_count,
            'total_chars': total_chars, 'khe_total': khe_total,
            'k_frac': k_frac, 'h_frac': h_frac, 'e_frac': e_frac,
            'k_to_e': k_to_e if k_to_e != float('inf') else None,
        }

        sparse = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        k2e_str = f'{k_to_e:.2f}' if k_to_e != float('inf') else 'INF'
        print(f'  {rname:8s}: k={k_frac:.3f}  h={h_frac:.3f}  e={e_frac:.3f}  '
              f'k/e={k2e_str:>5s}  (khe={khe_total}, chars={total_chars}){sparse}')

    print()

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS 2: ROLE DISTRIBUTION (MACRO-STATE) PER ROSETTE
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ANALYSIS 2: MACRO-STATE DISTRIBUTION PER ROSETTE')
    print('=' * 70)
    print()
    print('Macro-states: AXM=major scaffold, AXm=minor scaffold, FL_HAZ=hazard flow,')
    print('              FQ=frequency, CC=control change, FL_SAFE=safe flow')
    print()

    macro_profiles = {}
    for rname in ROSETTE_REGIONS:
        counts = Counter()
        unmapped = 0
        for w in rosette_words[rname]:
            ms = word_to_macro.get(w)
            if ms:
                counts[ms] += 1
            else:
                unmapped += 1

        total = sum(counts.values())
        dist = {}
        for state in MACRO_STATES:
            dist[state] = safe_div(counts.get(state, 0), total)

        macro_profiles[rname] = {
            'counts': dict(counts),
            'total_mapped': total,
            'unmapped': unmapped,
            'distribution': dist,
        }

        sparse = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        parts = [f'{s}={dist[s]:.2f}' for s in MACRO_STATES if dist[s] > 0]
        print(f'  {rname:8s}: {" ".join(parts):60s}  (n={total}, unmapped={unmapped}){sparse}')

    print()

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS 3: AFFORDANCE BIN PROFILE PER ROSETTE
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ANALYSIS 3: AFFORDANCE BIN PROFILE PER ROSETTE')
    print('=' * 70)
    print()

    # Compute all-rosettes average first
    all_aff_counts = Counter()
    all_aff_total = 0
    for mid in all_rosette_middles:
        abin = middle_to_aff_bin.get(mid)
        if abin:
            all_aff_counts[abin] += 1
            all_aff_total += 1
    all_aff_avg = {bn: safe_div(all_aff_counts.get(bn, 0), all_aff_total)
                   for bn in AFFORDANCE_BIN_NAMES}

    affordance_profiles = {}
    for rname in ROSETTE_REGIONS:
        counts = Counter()
        unmapped = 0
        for mid in rosette_middles[rname]:
            abin = middle_to_aff_bin.get(mid)
            if abin:
                counts[abin] += 1
            else:
                unmapped += 1

        total = sum(counts.values())
        dist = {}
        enriched = []
        depleted = []
        for bn in AFFORDANCE_BIN_NAMES:
            frac = safe_div(counts.get(bn, 0), total)
            dist[bn] = frac
            avg = all_aff_avg.get(bn, 0)
            if avg > 0:
                ratio = safe_div(frac, avg)
                if ratio > 1.5:
                    enriched.append((bn, ratio))
                elif ratio < 0.5 and frac > 0:
                    depleted.append((bn, ratio))
                elif frac == 0 and avg > 0.02:
                    depleted.append((bn, 0.0))

        affordance_profiles[rname] = {
            'counts': dict(counts),
            'total_mapped': total,
            'unmapped': unmapped,
            'distribution': dist,
            'enriched': enriched,
            'depleted': depleted,
        }

        sparse = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        # Show top 3 bins by fraction
        top3 = sorted(dist.items(), key=lambda x: -x[1])[:3]
        top3_str = ', '.join(f'{bn[:12]}={v:.2f}' for bn, v in top3)
        print(f'  {rname:8s}: {top3_str:55s} (mapped={total}, unmapped={unmapped}){sparse}')
        if enriched:
            enr_str = ', '.join(f'{bn[:12]} {r:.1f}x' for bn, r in enriched)
            print(f'            ENRICHED: {enr_str}')
        if depleted:
            dep_str = ', '.join(f'{bn[:12]} {r:.1f}x' for bn, r in depleted)
            print(f'            DEPLETED: {dep_str}')

    print()
    print('  All-rosettes average:')
    for bn in AFFORDANCE_BIN_NAMES:
        print(f'    {bn:25s}: {all_aff_avg[bn]:.3f}')
    print()

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS 4: B SECTION CONCENTRATION PER ROSETTE
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ANALYSIS 4: B SECTION CONCENTRATION PER ROSETTE')
    print('=' * 70)
    print()
    print('Fraction of each rosette\'s MIDDLEs that appear in each B section.')
    print()

    section_profiles = {}
    for rname in ROSETTE_REGIONS:
        mids = rosette_middles[rname]
        if not mids:
            section_profiles[rname] = {'distribution': {}, 'n_middles': 0}
            continue

        dist = {}
        for sec in b_sections:
            overlap = mids & section_middles[sec]
            dist[sec] = safe_div(len(overlap), len(mids))

        section_profiles[rname] = {
            'distribution': dist,
            'n_middles': len(mids),
        }

        sparse = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        # Show top 3 sections with full names
        top3 = sorted(dist.items(), key=lambda x: -x[1])[:3]
        top3_str = ', '.join(f'{SECTION_NAMES.get(s,s)}({s})={v:.2f}' for s, v in top3)
        print(f'  {rname:8s}: {top3_str:55s} (n_mids={len(mids)}){sparse}')

    print()

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS 5: B PARAGRAPH DESTINATION MAPPING
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ANALYSIS 5: B PARAGRAPH DESTINATION MAPPING')
    print('=' * 70)
    print()
    print('Jaccard overlap of each rosette\'s MIDDLEs with each B paragraph.')
    print('Top-5 destination paragraphs per rosette.')
    print()

    destination_profiles = {}
    rosette_dest_sets = {}  # rname -> set of (folio, para_id) that have overlap > 0

    for rname in ROSETTE_REGIONS:
        mids = rosette_middles[rname]
        if not mids:
            destination_profiles[rname] = {'top5': [], 'n_destinations': 0}
            rosette_dest_sets[rname] = set()
            continue

        overlaps = []
        for (folio, pid), para_mids in b_para_middles.items():
            j = jaccard(mids, para_mids)
            if j > 0:
                overlaps.append({
                    'folio': folio,
                    'paragraph': pid,
                    'jaccard': j,
                    'shared_count': len(mids & para_mids),
                })

        overlaps.sort(key=lambda x: -x['jaccard'])
        top5 = overlaps[:5]

        # Destination set: paragraphs with any overlap
        dest_set = set((o['folio'], o['paragraph']) for o in overlaps)
        rosette_dest_sets[rname] = dest_set

        destination_profiles[rname] = {
            'top5': top5,
            'n_destinations': len(dest_set),
            'n_with_overlap': len(overlaps),
        }

        sparse = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        print(f'  {rname:8s}: {len(dest_set)} destination paragraphs{sparse}')
        for item in top5:
            print(f'            {item["folio"]}:{item["paragraph"]:3s}  '
                  f'J={item["jaccard"]:.3f}  shared={item["shared_count"]}')

    # Pairwise Jaccard between rosettes' destination sets
    print()
    print('  Pairwise Jaccard of destination sets (do rosettes point to SAME or DIFFERENT paragraphs?):')
    rosette_names = [r for r in ROSETTE_REGIONS if r not in SPARSE_ROSETTES]
    pairwise_dest = {}
    print(f'  {"":8s}', end='')
    for r2 in rosette_names:
        print(f'  {r2:8s}', end='')
    print()
    for r1 in rosette_names:
        print(f'  {r1:8s}', end='')
        for r2 in rosette_names:
            j = jaccard(rosette_dest_sets.get(r1, set()),
                       rosette_dest_sets.get(r2, set()))
            pairwise_dest[(r1, r2)] = j
            print(f'  {j:8.3f}', end='')
        print()

    print()

    # ══════════════════════════════════════════════════════════════════════
    # ANALYSIS 6: PREFIX LANE PROFILE PER ROSETTE
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ANALYSIS 6: PREFIX LANE PROFILE PER ROSETTE')
    print('=' * 70)
    print()
    print('Lanes: SETUP, QO, CHSH, PREP, CLOSE, LINK, INIT, MAINT, XFER, CTRL, KE, TE, BARE')
    print()

    lane_profiles = {}
    for rname in ROSETTE_REGIONS:
        counts = Counter()
        for pfx in rosette_prefixes[rname]:
            lane = get_prefix_lane(pfx)
            counts[lane] += 1

        total = sum(counts.values())
        dist = {}
        for lane in CANONICAL_LANES:
            dist[lane] = safe_div(counts.get(lane, 0), total)
        # Also capture any non-canonical lanes
        for lane, cnt in counts.items():
            if lane not in dist:
                dist[lane] = safe_div(cnt, total)

        lane_profiles[rname] = {
            'counts': dict(counts),
            'total': total,
            'distribution': dist,
        }

        sparse = ' (SPARSE)' if rname in SPARSE_ROSETTES else ''
        # Show non-zero lanes
        nonzero = [(lane, dist[lane]) for lane in CANONICAL_LANES if dist.get(lane, 0) > 0]
        nz_str = ', '.join(f'{l}={v:.2f}' for l, v in nonzero)
        print(f'  {rname:8s}: {nz_str}{sparse}')

    print()

    # ══════════════════════════════════════════════════════════════════════
    # ROSETTE PROFILE CARDS
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('ROSETTE PROFILE CARDS')
    print('=' * 70)

    for rname in ROSETTE_REGIONS:
        sparse = ' ** SPARSE **' if rname in SPARSE_ROSETTES else ''
        print()
        print(f'--- {rname} ---{sparse}')
        print(f'  Visual theme: {VISUAL_THEMES.get(rname, "N/A")}')
        print(f'  Tokens: {len(rosette_tokens[rname])}, Unique MIDDLEs: {len(rosette_middles[rname])}')

        # Bridge density
        bridge_overlap = rosette_middles[rname] & bridge_middles
        bridge_frac = safe_div(len(bridge_overlap), len(rosette_middles[rname]))
        print(f'  Bridge MIDDLEs: {len(bridge_overlap)}/{len(rosette_middles[rname])} ({bridge_frac:.1%})')

        # Kernel
        kp = kernel_profiles[rname]
        k2e_str = f'{kp["k_to_e"]:.2f}' if kp["k_to_e"] is not None else 'INF'
        print(f'  Kernel: k={kp["k_frac"]:.3f} h={kp["h_frac"]:.3f} e={kp["e_frac"]:.3f} k/e={k2e_str}')

        # Macro-state
        mp = macro_profiles[rname]
        ms_parts = [f'{s}={mp["distribution"][s]:.2f}'
                    for s in MACRO_STATES if mp['distribution'][s] > 0]
        print(f'  Macro-state: {" ".join(ms_parts)} (mapped={mp["total_mapped"]})')

        # Top affordance bins
        ap = affordance_profiles[rname]
        top_bins = sorted(ap['distribution'].items(), key=lambda x: -x[1])[:3]
        tb_str = ', '.join(f'{b[:15]}={v:.2f}' for b, v in top_bins)
        print(f'  Top affordance: {tb_str}')

        # Top B sections
        sp = section_profiles[rname]
        if sp['distribution']:
            top_secs = sorted(sp['distribution'].items(), key=lambda x: -x[1])[:3]
            ts_str = ', '.join(f'{SECTION_NAMES.get(s,s)}({s})={v:.2f}' for s, v in top_secs)
            print(f'  Top B sections: {ts_str}')

        # Top destinations
        dp = destination_profiles[rname]
        if dp['top5']:
            t1 = dp['top5'][0]
            print(f'  Top destination: {t1["folio"]}:{t1["paragraph"]} J={t1["jaccard"]:.3f}')
        print(f'  Total B paragraph destinations: {dp.get("n_destinations", 0)}')

        # Prefix lanes
        lp = lane_profiles[rname]
        nz_lanes = [(l, lp['distribution'][l]) for l in CANONICAL_LANES
                    if lp['distribution'].get(l, 0) > 0]
        nl_str = ', '.join(f'{l}={v:.2f}' for l, v in nz_lanes)
        print(f'  Prefix lanes: {nl_str}')

    print()

    # ══════════════════════════════════════════════════════════════════════
    # COMPARISON TABLE
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('COMPARISON TABLE')
    print('=' * 70)
    print()

    # Table: kernel ratios
    print('Kernel k/e ratio (>1 = heating, <1 = cooling):')
    print(f'  {"Rosette":8s}  {"k_frac":>7s}  {"h_frac":>7s}  {"e_frac":>7s}  {"k/e":>7s}  {"Label":s}')
    print(f'  {"--------":8s}  {"-------":>7s}  {"-------":>7s}  {"-------":>7s}  {"-------":>7s}  {"-----":s}')
    for rname in ROSETTE_REGIONS:
        kp = kernel_profiles[rname]
        sparse = '(sparse)' if rname in SPARSE_ROSETTES else ''
        k2e_str = f'{kp["k_to_e"]:.2f}' if kp["k_to_e"] is not None else 'INF'
        label = ''
        if kp['k_to_e'] is not None:
            if kp['k_to_e'] > 1.5:
                label = 'HEATING'
            elif kp['k_to_e'] < 0.67:
                label = 'COOLING'
            else:
                label = 'BALANCED'
        else:
            label = 'NO_E'
        print(f'  {rname:8s}  {kp["k_frac"]:7.3f}  {kp["h_frac"]:7.3f}  {kp["e_frac"]:7.3f}  '
              f'{k2e_str:>7s}  {label} {sparse}')
    print()

    # Table: dominant macro-state
    print('Dominant macro-state per rosette:')
    print(f'  {"Rosette":8s}  {"Dominant":12s}  {"Frac":>6s}  {"2nd":12s}  {"Frac":>6s}')
    print(f'  {"--------":8s}  {"--------":12s}  {"----":>6s}  {"---":12s}  {"----":>6s}')
    for rname in ROSETTE_REGIONS:
        mp = macro_profiles[rname]
        sorted_states = sorted(mp['distribution'].items(), key=lambda x: -x[1])
        if sorted_states and sorted_states[0][1] > 0:
            d1_name, d1_frac = sorted_states[0]
            d2_name, d2_frac = sorted_states[1] if len(sorted_states) > 1 else ('', 0)
            sparse = ' (sparse)' if rname in SPARSE_ROSETTES else ''
            print(f'  {rname:8s}  {d1_name:12s}  {d1_frac:6.2f}  {d2_name:12s}  {d2_frac:6.2f}{sparse}')
        else:
            print(f'  {rname:8s}  (no data)')
    print()

    # Table: B section concentration
    print('B section with highest concentration per rosette:')
    print(f'  {"Rosette":8s}  {"Section":12s}  {"Frac":>6s}  {"2nd Section":12s}  {"Frac":>6s}')
    print(f'  {"--------":8s}  {"-------":12s}  {"----":>6s}  {"-----------":12s}  {"----":>6s}')
    for rname in ROSETTE_REGIONS:
        sp = section_profiles[rname]
        if sp['distribution']:
            sorted_secs = sorted(sp['distribution'].items(), key=lambda x: -x[1])
            s1_code, s1_frac = sorted_secs[0]
            s2_code, s2_frac = sorted_secs[1] if len(sorted_secs) > 1 else ('', 0)
            s1_label = f'{SECTION_NAMES.get(s1_code, s1_code)}({s1_code})'
            s2_label = f'{SECTION_NAMES.get(s2_code, s2_code)}({s2_code})' if s2_code else ''
            sparse = ' (sparse)' if rname in SPARSE_ROSETTES else ''
            print(f'  {rname:8s}  {s1_label:12s}  {s1_frac:6.2f}  {s2_label:12s}  {s2_frac:6.2f}{sparse}')
        else:
            print(f'  {rname:8s}  (no data)')
    print()

    # Table: destination divergence
    print('Destination divergence (mean Jaccard between rosette destination sets):')
    total_j = 0
    count_j = 0
    for i, r1 in enumerate(rosette_names):
        for j, r2 in enumerate(rosette_names):
            if j > i:
                total_j += pairwise_dest.get((r1, r2), 0)
                count_j += 1
    mean_dest_j = safe_div(total_j, count_j)
    print(f'  Mean pairwise Jaccard: {mean_dest_j:.3f}')
    print(f'  (High = rosettes point to SAME paragraphs; Low = DIFFERENT)')
    print()

    # ══════════════════════════════════════════════════════════════════════
    # VISUAL ALIGNMENT SECTION
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('VISUAL ALIGNMENT: PREDICTIONS vs RESULTS')
    print('=' * 70)
    print()

    # Prediction 1: NORTH/SOUTH "heat" rosettes should be k-enriched
    print('PREDICTION 1: N/S "heat" rosettes should be k-enriched (k/e > 1)')
    n_ke = kernel_profiles['NORTH']['k_to_e']
    s_ke = kernel_profiles['SOUTH']['k_to_e']
    w_ke = kernel_profiles['WEST']['k_to_e']
    c_ke = kernel_profiles['CENTER']['k_to_e']
    nw_ke = kernel_profiles['NW']['k_to_e']
    sw_ke = kernel_profiles['SW']['k_to_e']

    def fmt_ke(v):
        return f'{v:.2f}' if v is not None else 'INF'

    print(f'  NORTH k/e = {fmt_ke(n_ke)}, SOUTH k/e = {fmt_ke(s_ke)}')
    print(f'  Others: WEST={fmt_ke(w_ke)}, CENTER={fmt_ke(c_ke)}, NW={fmt_ke(nw_ke)}, SW={fmt_ke(sw_ke)}')

    heat_pass = True
    if n_ke is not None and n_ke <= 1.0:
        heat_pass = False
    if s_ke is not None and s_ke <= 1.0:
        heat_pass = False
    if n_ke is None:
        heat_pass = True  # INF means no e at all, which is maximally k-enriched
    if s_ke is None:
        heat_pass = True

    verdict = 'SUPPORTED' if heat_pass else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict}')
    print()

    # Prediction 2: WEST "condensation" rosette should be e-enriched
    print('PREDICTION 2: WEST "condensation" rosette should be e-enriched (k/e < 1)')
    w_kfrac = kernel_profiles['WEST']['k_frac']
    w_efrac = kernel_profiles['WEST']['e_frac']
    print(f'  WEST k_frac={w_kfrac:.3f}, e_frac={w_efrac:.3f}, k/e={fmt_ke(w_ke)}')

    cool_pass = w_ke is not None and w_ke < 1.0
    verdict = 'SUPPORTED' if cool_pass else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict}')
    print()

    # Prediction 3: CENTER "apparatus hub" should be connector-enriched
    print('PREDICTION 3: CENTER "apparatus hub" should be connector-enriched')
    c_hub = affordance_profiles['CENTER']['distribution'].get('HUB_UNIVERSAL', 0)
    # Compare to average
    avg_hub = all_aff_avg.get('HUB_UNIVERSAL', 0)
    enrichment = safe_div(c_hub, avg_hub) if avg_hub > 0 else 0
    print(f'  CENTER HUB_UNIVERSAL = {c_hub:.3f} (avg = {avg_hub:.3f}, enrichment = {enrichment:.1f}x)')
    # Also check macro-state: should have more AXM/AXm (scaffold)
    c_axm = macro_profiles['CENTER']['distribution'].get('AXM', 0)
    c_axm_minor = macro_profiles['CENTER']['distribution'].get('AXm', 0)
    avg_axm = sum(macro_profiles[r]['distribution'].get('AXM', 0) for r in rosette_names) / len(rosette_names)
    print(f'  CENTER AXM={c_axm:.2f}, AXm={c_axm_minor:.2f} (avg AXM={avg_axm:.2f} across non-sparse)')

    hub_pass = enrichment > 1.2 or (c_axm + c_axm_minor) > avg_axm
    verdict = 'SUPPORTED' if hub_pass else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict}')
    print()

    # Prediction 4: NW "botanical" should align with Herbal (H) sections
    print('PREDICTION 4: NW "botanical" should concentrate in Herbal (H) B sections')
    nw_herbal = section_profiles['NW']['distribution'].get('H', 0)
    nw_top_sec = sorted(section_profiles['NW']['distribution'].items(),
                        key=lambda x: -x[1])[:3] if section_profiles['NW']['distribution'] else []
    print(f'  NW Herbal(H) fraction = {nw_herbal:.3f}')
    if nw_top_sec:
        print(f'  NW top sections: {", ".join(f"{SECTION_NAMES.get(s,s)}({s})={v:.3f}" for s, v in nw_top_sec)}')

    # Compare: is NW's Herbal fraction higher than average?
    avg_herbal = safe_div(
        sum(section_profiles[r]['distribution'].get('H', 0)
            for r in rosette_names),
        len(rosette_names))
    print(f'  Average Herbal(H) fraction (non-sparse) = {avg_herbal:.3f}')
    botanical_pass = nw_herbal > avg_herbal
    verdict = 'SUPPORTED' if botanical_pass else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict}')
    print()

    # Prediction 5: SW "aqueous" should differ from NW "botanical"
    print('PREDICTION 5: SW "aqueous" should differ from NW "botanical" in functional profile')
    # Compare kernel profiles
    sw_ke_val = kernel_profiles['SW']['k_to_e']
    nw_ke_val = kernel_profiles['NW']['k_to_e']
    print(f'  NW k/e = {fmt_ke(nw_ke_val)}, SW k/e = {fmt_ke(sw_ke_val)}')
    # Compare top affordance bins
    nw_top_aff = sorted(affordance_profiles['NW']['distribution'].items(), key=lambda x: -x[1])[:2]
    sw_top_aff = sorted(affordance_profiles['SW']['distribution'].items(), key=lambda x: -x[1])[:2]
    print(f'  NW top affordance: {", ".join(f"{b[:15]}={v:.2f}" for b, v in nw_top_aff)}')
    print(f'  SW top affordance: {", ".join(f"{b[:15]}={v:.2f}" for b, v in sw_top_aff)}')
    # Jaccard of their MIDDLE sets
    nw_sw_j = jaccard(rosette_middles['NW'], rosette_middles['SW'])
    print(f'  NW-SW MIDDLE overlap: J={nw_sw_j:.3f}')

    differ = nw_sw_j < 0.3  # they should be quite different
    verdict = 'SUPPORTED' if differ else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict} (J={nw_sw_j:.3f}, threshold < 0.30)')
    print()

    # Prediction 6: NORTH and SOUTH should be functionally similar
    print('PREDICTION 6: NORTH and SOUTH should be functionally similar (visual match)')
    ns_mid_j = jaccard(rosette_middles['NORTH'], rosette_middles['SOUTH'])
    print(f'  NORTH-SOUTH MIDDLE overlap: J={ns_mid_j:.3f}')
    ns_dest_j = jaccard(rosette_dest_sets.get('NORTH', set()),
                        rosette_dest_sets.get('SOUTH', set()))
    print(f'  NORTH-SOUTH destination overlap: J={ns_dest_j:.3f}')
    # Compare kernel profiles
    n_kfrac = kernel_profiles['NORTH']['k_frac']
    s_kfrac = kernel_profiles['SOUTH']['k_frac']
    n_efrac = kernel_profiles['NORTH']['e_frac']
    s_efrac = kernel_profiles['SOUTH']['e_frac']
    print(f'  NORTH kernel: k={n_kfrac:.3f} e={n_efrac:.3f}')
    print(f'  SOUTH kernel: k={s_kfrac:.3f} e={s_efrac:.3f}')

    similar = ns_dest_j > 0.5
    verdict = 'SUPPORTED' if similar else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict} (destination J={ns_dest_j:.3f}, threshold > 0.50)')
    print()

    # Prediction 7: Each rosette points to DIFFERENT B paragraphs (functional specialization)
    print('PREDICTION 7: Rosettes point to different B paragraph destinations (specialization)')
    print(f'  Mean pairwise destination Jaccard = {mean_dest_j:.3f}')
    specialized = mean_dest_j < 0.7
    verdict = 'SUPPORTED' if specialized else 'NOT SUPPORTED'
    print(f'  VERDICT: {verdict} (threshold < 0.70 for specialization)')
    print()

    # ══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    print('=' * 70)
    print('SUMMARY')
    print('=' * 70)
    print()

    # Count predictions
    predictions = [
        ('N/S heat -> k-enriched', heat_pass),
        ('WEST condensation -> e-enriched', cool_pass),
        ('CENTER apparatus -> connector-enriched', hub_pass),
        ('NW botanical -> Herbal concentration', botanical_pass),
        ('SW aqueous differs from NW botanical', differ),
        ('NORTH-SOUTH functional similarity', similar),
        ('Rosettes are functionally specialized', specialized),
    ]

    n_supported = sum(1 for _, p in predictions if p)
    n_total = len(predictions)
    print(f'Visual-functional alignment: {n_supported}/{n_total} predictions supported')
    print()
    for label, passed in predictions:
        status = 'SUPPORTED' if passed else 'NOT SUPPORTED'
        print(f'  [{status:14s}] {label}')
    print()

    elapsed = time.time() - t0
    print(f'Completed in {elapsed:.1f}s')
    print()

    # ══════════════════════════════════════════════════════════════════════
    # SAVE JSON
    # ══════════════════════════════════════════════════════════════════════
    output = {
        '_metadata': {
            'phase': '396',
            'analysis': 'rosettes_functional_profiling',
            'description': 'Per-rosette functional profiling against B programs',
            'folio': 'f85v2',
            'n_rosettes': len(ROSETTE_REGIONS),
            'sparse_rosettes': sorted(SPARSE_ROSETTES),
            'n_b_paragraphs': len(b_para_middles),
            'n_b_folios': len(b_folios),
            'elapsed_seconds': round(elapsed, 1),
        },
        'rosette_regions': {k: v for k, v in ROSETTE_REGIONS.items()},
        'rosette_token_counts': {r: len(rosette_tokens[r]) for r in ROSETTE_REGIONS},
        'rosette_middle_counts': {r: len(rosette_middles[r]) for r in ROSETTE_REGIONS},
        'rosette_middles': {r: sorted(rosette_middles[r]) for r in ROSETTE_REGIONS},
        'analysis_1_kernel_profiles': kernel_profiles,
        'analysis_2_macro_state_profiles': {
            r: {
                'counts': mp['counts'],
                'total_mapped': mp['total_mapped'],
                'unmapped': mp['unmapped'],
                'distribution': mp['distribution'],
            } for r, mp in macro_profiles.items()
        },
        'analysis_3_affordance_profiles': {
            r: {
                'counts': ap['counts'],
                'total_mapped': ap['total_mapped'],
                'unmapped': ap['unmapped'],
                'distribution': ap['distribution'],
                'enriched': [(bn, ratio) for bn, ratio in ap['enriched']],
                'depleted': [(bn, ratio) for bn, ratio in ap['depleted']],
            } for r, ap in affordance_profiles.items()
        },
        'analysis_3_all_rosettes_average': all_aff_avg,
        'analysis_4_section_profiles': section_profiles,
        'analysis_5_destination_profiles': {
            r: {
                'top5': dp['top5'],
                'n_destinations': dp.get('n_destinations', 0),
                'n_with_overlap': dp.get('n_with_overlap', 0),
            } for r, dp in destination_profiles.items()
        },
        'analysis_5_pairwise_destination_jaccard': {
            f'{r1}-{r2}': pairwise_dest.get((r1, r2), 0)
            for r1 in rosette_names for r2 in rosette_names if r1 < r2
        },
        'analysis_5_mean_destination_jaccard': mean_dest_j,
        'analysis_6_lane_profiles': lane_profiles,
        'visual_alignment': {
            'predictions': {
                label: {'supported': passed}
                for label, passed in predictions
            },
            'n_supported': n_supported,
            'n_total': n_total,
        },
    }

    out_path = RESULTS / 'rosettes_functional_profiling.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, ensure_ascii=True)
    print(f'Saved: {out_path}')


if __name__ == '__main__':
    main()
