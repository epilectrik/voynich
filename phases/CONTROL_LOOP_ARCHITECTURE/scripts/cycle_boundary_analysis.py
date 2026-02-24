#!/usr/bin/env python3
"""
Gap 1: Cycle Boundary Detection

What marks the boundary between extraction cycles (lines)?
C1227 says 36.4% of cross-line FL pairs regress (mainly LATE->MEDIAL).
But what about the other 63.6%? Is FL regression the ONLY cycle boundary
signal, or do prefix channel switches (C1228) and suffix mode transitions
co-occur?

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/cycle_boundary_analysis.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SETUP
# ============================================================
tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# FL stage ordering for regression detection
FL_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'TERMINAL': 4}

def classify_fl_transition(prev_fl, curr_fl):
    """Classify FL transition as FORWARD, STATIC, or REGRESS."""
    if prev_fl is None or curr_fl is None:
        return None
    p = FL_ORDER.get(prev_fl)
    c = FL_ORDER.get(curr_fl)
    if p is None or c is None:
        return None
    if c > p:
        return 'FORWARD'
    elif c == p:
        return 'STATIC'
    else:
        return 'REGRESS'

def get_channel_from_roles(role_sequence):
    """Get dominant prefix channel from role sequence."""
    roles = [r for r in role_sequence if r]
    if not roles:
        return 'MIXED'
    kernel_roles = sum(1 for r in roles if r == 'EN_KERNEL')
    energy_roles = sum(1 for r in roles if r == 'EN_QO')
    infra_roles = sum(1 for r in roles if r in ('CC_INIT', 'PREP_TIER'))
    scaffold_roles = sum(1 for r in roles if r in ('AX_SCAFFOLD', 'AX_LATE'))
    counts = {'KERNEL': kernel_roles, 'ENERGY': energy_roles,
              'INFRA': infra_roles, 'SCAFFOLD': scaffold_roles}
    return max(counts, key=counts.get) if any(v > 0 for v in counts.values()) else 'MIXED'

# ============================================================
# DECODE ALL B FOLIOS
# ============================================================
print("Decoding all B folios for FL and mode data...")

b_folios = sorted(set(t.folio for t in tx.currier_b()))
cross_line_data = []
all_line_summaries = []
decoded = 0

for folio in b_folios:
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
    except Exception as e:
        print(f"  Skip {folio}: {e}")
        continue
    decoded += 1

    for para in paragraphs:
        prev_line = None
        for line_a in para.lines:
            # FL stages for this line
            non_none_fl = [f for f in line_a.fl_stages if f]
            fl_first = non_none_fl[0] if non_none_fl else None
            fl_last = non_none_fl[-1] if non_none_fl else None

            mode = line_a.suffix_mode
            channel = get_channel_from_roles(line_a.role_sequence)

            line_summary = {
                'folio': folio,
                'para': para.paragraph_id,
                'line': line_a.line_id,
                'tokens': line_a.token_count,
                'fl_first': fl_first,
                'fl_last': fl_last,
                'mode': mode,
                'channel': channel,
                'line_type': line_a.line_type,
                'is_header': line_a.is_header,
            }
            all_line_summaries.append(line_summary)

            # Cross-line transition (within same paragraph, skip headers)
            if prev_line is not None and not line_a.is_header:
                prev_fl_last = prev_line['fl_last']
                curr_fl_first = fl_first

                fl_trans = classify_fl_transition(prev_fl_last, curr_fl_first)
                mode_trans = None
                if prev_line['mode'] and mode:
                    mode_trans = f"{prev_line['mode']}->{mode}"
                channel_switch = prev_line['channel'] != channel

                cross_line_data.append({
                    'folio': folio,
                    'para': para.paragraph_id,
                    'fl_transition': fl_trans,
                    'fl_from': prev_fl_last,
                    'fl_to': curr_fl_first,
                    'mode_transition': mode_trans,
                    'channel_switch': channel_switch,
                })

            prev_line = line_summary

print(f"  Decoded {decoded} folios, {len(all_line_summaries)} lines, {len(cross_line_data)} cross-line transitions")

# ============================================================
# ANALYSIS
# ============================================================
print(f"\nTotal cross-line transitions: {len(cross_line_data)}")

# 1. FL transition distribution
fl_trans_counts = Counter(d['fl_transition'] for d in cross_line_data if d['fl_transition'])
total_fl = sum(fl_trans_counts.values()) or 1
print(f"\n=== FL TRANSITION TYPES ===")
for k, v in fl_trans_counts.most_common():
    print(f"  {k:10s}: {v:4d} ({v/total_fl*100:.1f}%)")

# 2. FL regression detail
regress_pairs = Counter()
for d in cross_line_data:
    if d['fl_transition'] == 'REGRESS':
        regress_pairs[f"{d['fl_from']}->{d['fl_to']}"] += 1
print(f"\n=== FL REGRESSION PAIRS ===")
for k, v in regress_pairs.most_common(10):
    print(f"  {k:25s}: {v:4d}")

# 3. Mode transitions
mode_trans_counts = Counter(d['mode_transition'] for d in cross_line_data if d['mode_transition'])
total_mode = sum(mode_trans_counts.values()) or 1
print(f"\n=== MODE TRANSITIONS ===")
for k, v in mode_trans_counts.most_common():
    print(f"  {k:6s}: {v:4d} ({v/total_mode*100:.1f}%)")

# Calculate alternation rate
alternating = sum(v for k, v in mode_trans_counts.items() if k in ('A->B', 'B->A'))
same = sum(v for k, v in mode_trans_counts.items() if k in ('A->A', 'B->B'))
alt_total = alternating + same
alt_rate = alternating / alt_total * 100 if alt_total > 0 else 0
print(f"  Alternation rate: {alt_rate:.1f}%")

# 4. Channel switches
channel_switches = Counter(d['channel_switch'] for d in cross_line_data)
total_ch = sum(channel_switches.values()) or 1
print(f"\n=== CHANNEL SWITCHING ===")
print(f"  SWITCH: {channel_switches[True]:4d} ({channel_switches[True]/total_ch*100:.1f}%)")
print(f"  SAME:   {channel_switches[False]:4d} ({channel_switches[False]/total_ch*100:.1f}%)")

# 5. JOINT ANALYSIS: FL transition x mode transition x channel switch
print(f"\n=== JOINT TRANSITIONS (FL x MODE x CHANNEL) ===")
joint = Counter()
for d in cross_line_data:
    if d['fl_transition'] and d['mode_transition']:
        key = (d['fl_transition'], d['mode_transition'], 'SW' if d['channel_switch'] else 'SAME')
        joint[key] += 1
total_joint = sum(joint.values()) or 1
for (fl, mode, ch), v in joint.most_common(20):
    print(f"  FL:{fl:8s} MODE:{mode:4s} CH:{ch:4s}: {v:4d} ({v/total_joint*100:.1f}%)")

# 6. What characterizes NON-regressing vs REGRESSING transitions?
print(f"\n=== NON-REGRESSING vs REGRESSING ===")
for fl_type in ['FORWARD', 'STATIC', 'REGRESS']:
    subset = [d for d in cross_line_data if d['fl_transition'] == fl_type]
    if not subset:
        continue
    mode_alts = sum(1 for d in subset if d['mode_transition'] in ('A->B', 'B->A'))
    ch_switches = sum(1 for d in subset if d['channel_switch'])
    n = len(subset)
    print(f"  {fl_type}:")
    print(f"    Count: {n}")
    print(f"    Mode alternation rate: {mode_alts/n*100:.1f}%")
    print(f"    Channel switch rate:   {ch_switches/n*100:.1f}%")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'total_cross_line_transitions': len(cross_line_data),
    'folios_decoded': decoded,
    'fl_transition_distribution': {k: v for k, v in fl_trans_counts.most_common()},
    'fl_transition_pcts': {k: round(v/total_fl*100, 1) for k, v in fl_trans_counts.most_common()},
    'regression_pairs': {k: v for k, v in regress_pairs.most_common(10)},
    'mode_transition_distribution': {k: v for k, v in mode_trans_counts.most_common()},
    'mode_alternation_rate': round(alt_rate, 1),
    'channel_switch_rate': round(channel_switches[True]/total_ch*100, 1),
    'non_regressing_profile': {},
    'regressing_profile': {},
}

for fl_type in ['FORWARD', 'STATIC', 'REGRESS']:
    subset = [d for d in cross_line_data if d['fl_transition'] == fl_type]
    if not subset:
        continue
    n = len(subset)
    mode_alts = sum(1 for d in subset if d['mode_transition'] in ('A->B', 'B->A'))
    ch_switches = sum(1 for d in subset if d['channel_switch'])
    profile = {
        'count': n,
        'pct': round(n/len(cross_line_data)*100, 1),
        'mode_alternation_rate': round(mode_alts/n*100, 1),
        'channel_switch_rate': round(ch_switches/n*100, 1),
    }
    if fl_type == 'REGRESS':
        results['regressing_profile'] = profile
    else:
        results['non_regressing_profile'][fl_type] = profile

output_path = OUTPUT_DIR / 'cycle_boundary_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
