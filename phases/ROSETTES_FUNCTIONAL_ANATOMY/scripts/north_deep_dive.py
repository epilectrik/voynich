"""Deep dive on NORTH rosette (N1, N2 regions) token content."""
import sys
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (
    Transcript, Morphology, RosettesAnalyzer,
    BFolioDecoder, BTokenAnalysis
)

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# Load bridge + affordance
bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_middles = set(json.load(f)['t5_structural_profile']['bridge_middles'])

aff_path = ROOT / 'data' / 'middle_affordance_table.json'
with open(aff_path, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)
mid_to_bin = {}
mid_to_label = {}
for mk, mv in aff_data.get('middles', {}).items():
    if isinstance(mv, dict) and 'affordance_bin' in mv:
        mid_to_bin[mk] = mv['affordance_bin']
        mid_to_label[mk] = mv.get('affordance_label', '')

BIN_LABELS = {
    0: 'FLOW_TERMINAL', 1: 'ROUTINE_SPEC', 2: 'PRECISION_SPEC',
    3: 'COMPOUND_TERM', 5: 'SETTLING_SPEC',
    6: 'HUB_UNIVERSAL', 7: 'ENERGY_SPEC', 8: 'STABILITY_CRIT',
    9: 'PHASE_SENS'
}

def analyze_tokens(tokens, label):
    print(f'\n{"=" * 70}')
    print(f'{label}')
    print(f'{"=" * 70}')

    print(f'\n{"Word":<15} {"PREFIX":<8} {"MIDDLE":<10} {"SUFFIX":<8} {"ART":<5} '
          f'{"Bridge":<7} {"Bin":<20} {"Lane":<8} {"Macro":<8}')
    print('-' * 100)

    words = []
    for tok in tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        words.append(w)
        m = morph.extract(w)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None

        is_bridge = 'YES' if (mid and mid in bridge_middles) else 'no'
        bn = mid_to_bin.get(mid) if mid else None
        bl = BIN_LABELS.get(bn, '') if bn is not None else ''

        lane = ''
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)

        tc = decoder._token_to_class.get(w)
        ms = ''
        if tc is not None:
            ms = decoder.MACRO_STATE.get(str(tc), '')

        art = m.articulator or ''

        print(f'{w:<15} {(m.prefix or "-"):<8} {(mid or "-"):<10} {(m.suffix or "-"):<8} '
              f'{art:<5} {is_bridge:<7} {bl:<20} {lane:<8} {ms:<8}')

    print(f'\nTotal: {len(words)} tokens')

    # Summarize patterns
    prefix_seq = []
    lane_seq = []
    for tok in tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.prefix:
            prefix_seq.append(m.prefix)
            lane_seq.append(BTokenAnalysis._get_prefix_lane(m.prefix))
        else:
            prefix_seq.append('-')
            lane_seq.append('-')

    print(f'\nPrefix sequence: {" ".join(prefix_seq)}')
    print(f'Lane sequence: {" ".join(lane_seq)}')

    # Check for patterns: repeated words, repeated MIDDLEs
    word_counts = Counter(words)
    repeated = {w: c for w, c in word_counts.items() if c > 1}
    if repeated:
        print(f'\nRepeated words: {repeated}')

    mid_seq = []
    for tok in tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else '-'
        mid_seq.append(mid)

    mid_counts = Counter(mid_seq)
    print(f'\nMIDDLE frequency: {dict(mid_counts.most_common())}')

    # Suffix pattern
    suf_seq = []
    for tok in tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        suf_seq.append(m.suffix or '-')

    suf_counts = Counter(suf_seq)
    print(f'SUFFIX frequency: {dict(suf_counts.most_common())}')

# Get N1 and N2 tokens
n1_tokens = ra.get_tokens('f85v2', 'N1')
n2_tokens = ra.get_tokens('f85v2', 'N2')

analyze_tokens(n1_tokens, 'N1 (NORTH description region 1)')
analyze_tokens(n2_tokens, 'N2 (NORTH description region 2)')

# Combined analysis
print(f'\n{"=" * 70}')
print('COMBINED N1+N2 ANALYSIS')
print(f'{"=" * 70}')

all_mids = set()
all_words = []
for tok in list(n1_tokens) + list(n2_tokens):
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    all_words.append(w)
    m = morph.extract(w)
    mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
    if mid:
        all_mids.add(mid)

bridge_mids = all_mids & bridge_middles
nonbridge_mids = all_mids - bridge_middles

print(f'Total tokens: {len(all_words)}')
print(f'Unique MIDDLEs: {len(all_mids)}')
print(f'Bridge MIDDLEs: {sorted(bridge_mids)}')
print(f'Non-bridge MIDDLEs: {sorted(nonbridge_mids)}')

# What's distinctive about NORTH vs CENTER?
print(f'\n--- NORTH-specific vocabulary (in N but not CENTER) ---')
# Load CENTER data
c2_tokens = ra.get_tokens('f85v2', 'C2')
c2_mids = set()
for tok in c2_tokens:
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
    if mid:
        c2_mids.add(mid)

north_only = all_mids - c2_mids
center_only = c2_mids - all_mids
shared = all_mids & c2_mids

print(f'NORTH-only MIDDLEs: {sorted(north_only)}')
print(f'CENTER-only MIDDLEs: {sorted(center_only)}')
print(f'Shared: {sorted(shared)}')

# Check the NORTH-only MIDDLEs' bins
print(f'\nNORTH-only MIDDLE bins:')
for mid in sorted(north_only):
    bn = mid_to_bin.get(mid)
    bl = BIN_LABELS.get(bn, '?') if bn is not None else 'NOT_IN_B'
    is_br = 'bridge' if mid in bridge_middles else 'non-bridge'
    print(f'  {mid:<10} {bl:<20} {is_br}')
