#!/usr/bin/env python3
"""
Cycle Tensor Analysis

Build a 3D contingency tensor: FL_transition x mode_transition x channel_transition
Test true independence vs hidden structure.
If not independent, find what co-occurs more/less than expected.

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/cycle_tensor_analysis.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

FL_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'TERMINAL': 4}

def classify_fl_transition(prev_fl, curr_fl):
    if prev_fl is None or curr_fl is None:
        return None
    p = FL_ORDER.get(prev_fl)
    c = FL_ORDER.get(curr_fl)
    if p is None or c is None:
        return None
    if c > p: return 'FWD'
    elif c == p: return 'STA'
    else: return 'REG'

def get_channel(role_sequence):
    roles = [r for r in role_sequence if r]
    if not roles:
        return 'MIX'
    kernel = sum(1 for r in roles if r == 'EN_KERNEL')
    energy = sum(1 for r in roles if r == 'EN_QO')
    infra = sum(1 for r in roles if r in ('CC_INIT', 'PREP_TIER'))
    scaffold = sum(1 for r in roles if r in ('AX_SCAFFOLD', 'AX_LATE'))
    counts = {'KRN': kernel, 'ENR': energy, 'INF': infra, 'SCF': scaffold}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else 'MIX'

# ============================================================
# COLLECT TRANSITIONS
# ============================================================
print("Decoding all B folios...")

b_folios = sorted(set(t.folio for t in tx.currier_b()))
transitions = []

for folio in b_folios:
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
    except:
        continue

    for para in paragraphs:
        prev = None
        for line_a in para.lines:
            non_none_fl = [f for f in line_a.fl_stages if f]
            fl_first = non_none_fl[0] if non_none_fl else None
            fl_last = non_none_fl[-1] if non_none_fl else None
            mode = line_a.suffix_mode
            channel = get_channel(line_a.role_sequence)

            if prev is not None and not line_a.is_header:
                fl_trans = classify_fl_transition(prev['fl_last'], fl_first)
                mode_trans = f"{prev['mode']}{mode}" if prev['mode'] and mode else None
                ch_trans = f"{prev['channel']}->{channel}"

                if fl_trans and mode_trans:
                    transitions.append({
                        'fl': fl_trans,
                        'mode': mode_trans,
                        'ch_from': prev['channel'],
                        'ch_to': channel,
                        'ch_switch': prev['channel'] != channel,
                    })

            prev = {'fl_last': fl_last, 'mode': mode, 'channel': channel}

print(f"Total transitions: {len(transitions)}")

# ============================================================
# BUILD 3D TENSOR: FL x MODE x CHANNEL_SWITCH
# ============================================================
FL_LABELS = ['REG', 'STA', 'FWD']
MODE_LABELS = ['AA', 'AB', 'BA', 'BB']
CH_LABELS = [False, True]  # SAME, SWITCH

tensor = {}
for fl in FL_LABELS:
    for mode in MODE_LABELS:
        for ch in CH_LABELS:
            tensor[(fl, mode, ch)] = 0

for t in transitions:
    key = (t['fl'], t['mode'], t['ch_switch'])
    if key in tensor:
        tensor[key] += 1

N = sum(tensor.values())
print(f"Tensor total: {N}")

# Marginals
fl_marginal = Counter()
mode_marginal = Counter()
ch_marginal = Counter()
for (fl, mode, ch), count in tensor.items():
    fl_marginal[fl] += count
    mode_marginal[mode] += count
    ch_marginal[ch] += count

# ============================================================
# TEST INDEPENDENCE: Chi-squared
# ============================================================
print("\n=== INDEPENDENCE TEST (Chi-squared) ===")

# Expected under full independence
chi2_full = 0
df_full = 0
deviations = []

for fl in FL_LABELS:
    for mode in MODE_LABELS:
        for ch in CH_LABELS:
            observed = tensor[(fl, mode, ch)]
            expected = fl_marginal[fl] * mode_marginal[mode] * ch_marginal[ch] / (N * N)
            if expected > 0:
                chi2_contrib = (observed - expected) ** 2 / expected
                chi2_full += chi2_contrib
                df_full += 1
                ratio = observed / expected if expected > 0 else 0
                deviations.append({
                    'fl': fl, 'mode': mode, 'ch': 'SW' if ch else 'SAME',
                    'observed': observed, 'expected': round(expected, 1),
                    'ratio': round(ratio, 3), 'chi2': round(chi2_contrib, 2),
                })

df_full -= 1  # subtract 1 for the constraint that total = N
# Actual df for 3-way independence: (3-1)*(4-1)*(2-1) + pairwise terms...
# Simpler: df = cells - 1 - (free marginal params) = 24 - 1 - (2+3+1) = 17
df_actual = (len(FL_LABELS) * len(MODE_LABELS) * len(CH_LABELS)) - 1 - (len(FL_LABELS)-1) - (len(MODE_LABELS)-1) - (len(CH_LABELS)-1)

print(f"  Chi2 = {chi2_full:.2f}, df = {df_actual}")
# Critical values: df=17, p=0.05 -> 27.59, p=0.01 -> 33.41
if chi2_full < 27.59:
    print(f"  p > 0.05: INDEPENDENT (no significant structure)")
    independent = True
elif chi2_full < 33.41:
    print(f"  0.01 < p < 0.05: WEAKLY DEPENDENT")
    independent = False
else:
    print(f"  p < 0.01: DEPENDENT (significant structure)")
    independent = False

# Cramér's V (effect size)
k = min(len(FL_LABELS) * len(MODE_LABELS), len(CH_LABELS))  # min dimension
cramers_v = math.sqrt(chi2_full / (N * (k - 1))) if k > 1 else 0
print(f"  Cramér's V = {cramers_v:.4f}")

# ============================================================
# PAIRWISE INDEPENDENCE TESTS
# ============================================================
print("\n=== PAIRWISE INDEPENDENCE ===")

# FL x MODE
print("\n  FL x MODE:")
fl_mode = Counter()
for t in transitions:
    if t['mode'] in MODE_LABELS:
        fl_mode[(t['fl'], t['mode'])] += 1

chi2_fm = 0
fl_m = Counter(t['fl'] for t in transitions if t['mode'] in MODE_LABELS)
mode_m = Counter(t['mode'] for t in transitions if t['mode'] in MODE_LABELS)
n_fm = sum(fl_mode.values())

print(f"\n  {'':6s}", end='')
for mode in MODE_LABELS:
    print(f"  {mode:>6s}", end='')
print(f"  {'TOTAL':>6s}")

for fl in FL_LABELS:
    print(f"  {fl:6s}", end='')
    for mode in MODE_LABELS:
        obs = fl_mode.get((fl, mode), 0)
        exp = fl_m[fl] * mode_m[mode] / n_fm
        ratio = obs / exp if exp > 0 else 0
        chi2_fm += (obs - exp) ** 2 / exp if exp > 0 else 0
        # Show ratio (observed/expected)
        marker = '*' if abs(ratio - 1) > 0.15 else ' '
        print(f"  {ratio:5.2f}{marker}", end='')
    print(f"  {fl_m[fl]:6d}")

df_fm = (len(FL_LABELS) - 1) * (len(MODE_LABELS) - 1)
print(f"\n  Chi2 = {chi2_fm:.2f}, df = {df_fm}")
print(f"  {'INDEPENDENT' if chi2_fm < 12.59 else 'DEPENDENT'} (crit @ p=0.05 = 12.59)")

# FL x CHANNEL
print("\n  FL x CHANNEL:")
fl_ch = Counter()
for t in transitions:
    fl_ch[(t['fl'], t['ch_switch'])] += 1

chi2_fc = 0
ch_m = Counter(t['ch_switch'] for t in transitions)
n_fc = sum(fl_ch.values())

for fl in FL_LABELS:
    for ch in [False, True]:
        obs = fl_ch.get((fl, ch), 0)
        exp = fl_m[fl] * ch_m[ch] / n_fc
        chi2_fc += (obs - exp) ** 2 / exp if exp > 0 else 0

df_fc = (len(FL_LABELS) - 1) * 1
print(f"  Chi2 = {chi2_fc:.2f}, df = {df_fc}")
print(f"  {'INDEPENDENT' if chi2_fc < 5.99 else 'DEPENDENT'} (crit @ p=0.05 = 5.99)")

# MODE x CHANNEL
print("\n  MODE x CHANNEL:")
mode_ch = Counter()
for t in transitions:
    if t['mode'] in MODE_LABELS:
        mode_ch[(t['mode'], t['ch_switch'])] += 1

chi2_mc = 0
n_mc = sum(mode_ch.values())

for mode in MODE_LABELS:
    for ch in [False, True]:
        obs = mode_ch.get((mode, ch), 0)
        exp = mode_m[mode] * ch_m[ch] / n_mc
        chi2_mc += (obs - exp) ** 2 / exp if exp > 0 else 0

df_mc = (len(MODE_LABELS) - 1) * 1
print(f"  Chi2 = {chi2_mc:.2f}, df = {df_mc}")
print(f"  {'INDEPENDENT' if chi2_mc < 7.81 else 'DEPENDENT'} (crit @ p=0.05 = 7.81)")

# ============================================================
# CHANNEL TRANSITION MATRIX (4x4)
# ============================================================
print("\n=== CHANNEL TRANSITION MATRIX ===")
CH_NAMES = ['KRN', 'ENR', 'INF', 'SCF', 'MIX']
ch_trans_matrix = Counter()
for t in transitions:
    ch_trans_matrix[(t['ch_from'], t['ch_to'])] += 1

ch_from_totals = Counter()
for (fr, to), c in ch_trans_matrix.items():
    ch_from_totals[fr] += c

# Overall channel distribution
ch_overall = Counter()
for t in transitions:
    ch_overall[t['ch_from']] += 1
    ch_overall[t['ch_to']] += 1
ch_total = sum(ch_overall.values())

print(f"\n  Channel distribution:")
for ch in CH_NAMES:
    if ch_overall[ch] > 0:
        print(f"    {ch}: {ch_overall[ch]} ({ch_overall[ch]/ch_total*100:.1f}%)")

print(f"\n  Transition matrix (rows=from, cols=to, values=observed/expected ratio):")
print(f"  {'FROM':>6s}", end='')
for to_ch in CH_NAMES:
    if ch_overall[to_ch] > 0:
        print(f"  {to_ch:>6s}", end='')
print()

n_ch = sum(ch_trans_matrix.values())
for from_ch in CH_NAMES:
    if ch_from_totals[from_ch] == 0:
        continue
    print(f"  {from_ch:>6s}", end='')
    for to_ch in CH_NAMES:
        if ch_overall[to_ch] == 0:
            continue
        obs = ch_trans_matrix.get((from_ch, to_ch), 0)
        # Expected under independence
        to_total = sum(ch_trans_matrix.get((f, to_ch), 0) for f in CH_NAMES)
        exp = ch_from_totals[from_ch] * to_total / n_ch if n_ch > 0 else 0
        ratio = obs / exp if exp > 0 else 0
        marker = '*' if ratio > 1.3 or ratio < 0.7 else ' '
        print(f"  {ratio:5.2f}{marker}", end='')
    print()

# Self-transition rates
print(f"\n  Self-transition rates:")
for ch in CH_NAMES:
    if ch_from_totals[ch] > 0:
        self_rate = ch_trans_matrix.get((ch, ch), 0) / ch_from_totals[ch]
        print(f"    {ch}: {self_rate*100:.1f}%")

# ============================================================
# MOST OVER/UNDER-REPRESENTED CELLS
# ============================================================
print("\n=== MOST OVER/UNDER-REPRESENTED TENSOR CELLS ===")
sorted_devs = sorted(deviations, key=lambda d: abs(d['ratio'] - 1), reverse=True)
print(f"\n  Top deviations from independence:")
for d in sorted_devs[:10]:
    direction = 'OVER' if d['ratio'] > 1 else 'UNDER'
    print(f"    FL:{d['fl']} MODE:{d['mode']} CH:{d['ch']}: obs={d['observed']} exp={d['expected']} ratio={d['ratio']} ({direction})")

# ============================================================
# REDUCED MODEL: Is it really just 2D (FL x MODE)?
# ============================================================
print("\n=== REDUCED MODEL: FL x MODE only ===")
print("  (Testing if channel adds anything beyond FL and MODE)")

# Mutual information: I(CH ; FL,MODE)
# If channel is truly independent of FL and MODE, this should be ~0
mi_ch_flmode = 0
for fl in FL_LABELS:
    for mode in MODE_LABELS:
        for ch in [False, True]:
            p_joint = tensor.get((fl, mode, ch), 0) / N if N > 0 else 0
            p_flmode = sum(tensor.get((fl, mode, c), 0) for c in [False, True]) / N if N > 0 else 0
            p_ch = ch_marginal[ch] / N if N > 0 else 0
            if p_joint > 0 and p_flmode > 0 and p_ch > 0:
                mi_ch_flmode += p_joint * math.log2(p_joint / (p_flmode * p_ch))

print(f"  I(CH ; FL,MODE) = {mi_ch_flmode:.6f} bits")
print(f"  Max possible = {math.log2(2):.3f} bits (1 bit for binary channel)")
print(f"  Channel carries {mi_ch_flmode/math.log2(2)*100:.2f}% of possible information about FL+MODE")

# Compare: I(MODE ; FL)
mi_mode_fl = 0
for fl in FL_LABELS:
    for mode in MODE_LABELS:
        p_joint = fl_mode.get((fl, mode), 0) / n_fm if n_fm > 0 else 0
        p_fl = fl_m[fl] / n_fm if n_fm > 0 else 0
        p_mode = mode_m[mode] / n_fm if n_fm > 0 else 0
        if p_joint > 0 and p_fl > 0 and p_mode > 0:
            mi_mode_fl += p_joint * math.log2(p_joint / (p_fl * p_mode))

print(f"  I(MODE ; FL) = {mi_mode_fl:.6f} bits")
print(f"  Max possible = {math.log2(min(3,4)):.3f} bits")
print(f"  MODE carries {mi_mode_fl/math.log2(3)*100:.2f}% of possible information about FL")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'total_transitions': len(transitions),
    'tensor_total': N,
    'independence_test': {
        'three_way_chi2': round(chi2_full, 2),
        'three_way_df': df_actual,
        'three_way_independent': independent,
        'cramers_v': round(cramers_v, 4),
    },
    'pairwise_tests': {
        'FL_x_MODE': {'chi2': round(chi2_fm, 2), 'df': df_fm, 'independent': chi2_fm < 12.59},
        'FL_x_CHANNEL': {'chi2': round(chi2_fc, 2), 'df': df_fc, 'independent': chi2_fc < 5.99},
        'MODE_x_CHANNEL': {'chi2': round(chi2_mc, 2), 'df': df_mc, 'independent': chi2_mc < 7.81},
    },
    'mutual_information': {
        'CH_given_FL_MODE_bits': round(mi_ch_flmode, 6),
        'MODE_given_FL_bits': round(mi_mode_fl, 6),
        'channel_info_pct': round(mi_ch_flmode / math.log2(2) * 100, 2),
        'mode_fl_info_pct': round(mi_mode_fl / math.log2(3) * 100, 2),
    },
    'top_deviations': sorted_devs[:10],
}

output_path = OUTPUT_DIR / 'cycle_tensor_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
