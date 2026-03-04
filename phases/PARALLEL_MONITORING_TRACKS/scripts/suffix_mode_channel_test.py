"""
Phase 494 Extension: Suffix Mode Channel Separation Test
=========================================================
Tests whether suffix Mode A and Mode B lines show distinct PREFIX channel
distributions, as predicted by the two-channel clock hypothesis.

If Mode A = heat/specification channel and Mode B = material/execution channel:
  - Mode A should be enriched in thermal PREFIXes (qo, ok, ot)
  - Mode B should be enriched in transfer/material PREFIXes (ch, sh)

Also tests:
  T2: Macro-atom enrichment by mode (C1379 fused pairs)
  T3: Kernel atom distributions by mode (k/h/e)

Structural basis: C1229, C1231, C1258, C1309, C1379
"""

import json
import sys
import os
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# SUFFIX MODE CONSTANTS (from C1231)
# ============================================================
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

MODE_A_CENTROID = [0.430, 0.019, 0.086, 0.466]  # terminal, connector, iterate, bare
MODE_B_CENTROID = [0.155, 0.031, 0.072, 0.741]

SUFFIX_CATS = ['terminal', 'connector', 'iterate', 'bare']

# Macro-atoms from C1379
MACRO_ATOMS = {
    'ke': ('k', 'e'), 'in': ('i', 'n'), 'ck': ('c', 'k'),
    'ch': ('c', 'h'), 'dy': ('d', 'y'), 'an': ('a', 'n'),
    'am': ('a', 'm'), 'ct': ('c', 't'), 'ph': ('p', 'h'),
}

# PREFIX channel groups
PREFIX_CHANNELS = {
    'qo': 'THERMAL_SOURCE',
    'ok': 'THERMAL_VESSEL_K',
    'ot': 'THERMAL_VESSEL_T',
    'ol': 'THERMAL_VESSEL_L',
    'ch': 'ASSESSMENT_CH',
    'sh': 'ASSESSMENT_SH',
    'da': 'STAGING_DA',
    'sa': 'STAGING_SA',
}

def suffix_category(suffix):
    if not suffix:
        return 'bare'
    if suffix in TERMINAL_SUFFIXES:
        return 'terminal'
    if suffix in CONNECTOR_SUFFIXES:
        return 'connector'
    if suffix in ITERATE_SUFFIXES:
        return 'iterate'
    return 'bare'

def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    counts = Counter(t['suffix_cat'] for t in line_toks)
    n = len(line_toks)
    vec = [counts.get(c, 0) / n for c in SUFFIX_CATS]
    d_a = euclidean_dist(vec, MODE_A_CENTROID)
    d_b = euclidean_dist(vec, MODE_B_CENTROID)
    return 'A' if d_a < d_b else 'B'

def get_prefix_channel(prefix):
    if not prefix:
        return 'BARE'
    for key, channel in PREFIX_CHANNELS.items():
        if key in prefix:
            return channel
    return 'OTHER'

def decompose_macro(middle):
    macro_list = sorted(MACRO_ATOMS.keys(), key=len, reverse=True)
    result = []
    remaining = middle
    while remaining:
        matched = False
        for macro in macro_list:
            if remaining.startswith(macro):
                result.append(macro)
                remaining = remaining[len(macro):]
                matched = True
                break
        if not matched:
            result.append(remaining[0])
            remaining = remaining[1:]
    return result

def chi2_test(contingency):
    """Simple chi-squared test from a dict of dicts."""
    rows = sorted(contingency.keys())
    cols = sorted(set(c for r in contingency.values() for c in r))
    matrix = [[contingency.get(r, {}).get(c, 0) for c in cols] for r in rows]
    n = sum(sum(row) for row in matrix)
    if n == 0:
        return 0, 1.0, 0

    row_totals = [sum(row) for row in matrix]
    col_totals = [sum(matrix[r][c] for r in range(len(rows))) for c in range(len(cols))]

    chi2 = 0
    for r in range(len(rows)):
        for c in range(len(cols)):
            expected = row_totals[r] * col_totals[c] / n
            if expected > 0:
                chi2 += (matrix[r][c] - expected) ** 2 / expected

    dof = (len(rows) - 1) * (len(cols) - 1)
    v = math.sqrt(chi2 / (n * (min(len(rows), len(cols)) - 1))) if n > 0 and min(len(rows), len(cols)) > 1 else 0

    return chi2, dof, v

# ============================================================
# LOAD DATA
# ============================================================
tx = Transcript()
morph = Morphology()

# Collect tokens grouped by folio/line
folio_line_data = defaultdict(list)
for token in tx.currier_b():
    w = token.word
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue
    pfx = m.prefix or ''
    folio_line_data[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'prefix': pfx,
        'suffix': m.suffix or '',
        'suffix_cat': suffix_category(m.suffix or ''),
        'section': token.section,
        'folio': token.folio,
        'line': token.line,
        'prefix_channel': get_prefix_channel(pfx),
    })

# Classify each line's suffix mode
line_modes = {}
for (folio, line), toks in folio_line_data.items():
    mode = classify_suffix_mode(toks)
    if mode:
        line_modes[(folio, line)] = mode

n_mode_a = sum(1 for m in line_modes.values() if m == 'A')
n_mode_b = sum(1 for m in line_modes.values() if m == 'B')
print(f"Lines classified: {len(line_modes)} (Mode A: {n_mode_a}, Mode B: {n_mode_b})")

# Flatten tokens with mode assignment
all_tokens = []
for (folio, line), toks in folio_line_data.items():
    mode = line_modes.get((folio, line))
    if mode is None:
        continue
    for t in toks:
        t['mode'] = mode
        all_tokens.append(t)

print(f"Total tokens with mode: {len(all_tokens)}")

results = {
    'phase': '494_extension',
    'name': 'SUFFIX_MODE_CHANNEL_SEPARATION',
    'n_lines_mode_a': n_mode_a,
    'n_lines_mode_b': n_mode_b,
    'n_tokens': len(all_tokens),
}

# ============================================================
# T1: PREFIX CHANNEL DISTRIBUTION BY MODE
# ============================================================
print("\n" + "=" * 70)
print("T1: PREFIX CHANNEL DISTRIBUTION BY MODE")
print("=" * 70)

mode_channel_counts = {'A': Counter(), 'B': Counter()}
for t in all_tokens:
    mode_channel_counts[t['mode']][t['prefix_channel']] += 1

all_channels = sorted(set(c for cc in mode_channel_counts.values() for c in cc))
n_a = sum(mode_channel_counts['A'].values())
n_b = sum(mode_channel_counts['B'].values())

print(f"\n{'Channel':<25} {'Mode A':>8} {'%':>7} {'Mode B':>8} {'%':>7} {'A/B':>7}")
print("-" * 70)

t1_details = {}
contingency = {}
for ch in all_channels:
    ca = mode_channel_counts['A'].get(ch, 0)
    cb = mode_channel_counts['B'].get(ch, 0)
    pa = ca / n_a if n_a else 0
    pb = cb / n_b if n_b else 0
    ratio = pa / pb if pb > 0 else float('inf')
    print(f"{ch:<25} {ca:>8} {pa:>7.1%} {cb:>8} {pb:>7.1%} {ratio:>7.2f}")
    t1_details[ch] = {'mode_a_count': ca, 'mode_a_pct': round(pa, 4),
                       'mode_b_count': cb, 'mode_b_pct': round(pb, 4),
                       'a_b_ratio': round(ratio, 3)}
    contingency.setdefault('A', {})[ch] = ca
    contingency.setdefault('B', {})[ch] = cb

chi2, dof, v = chi2_test(contingency)
print(f"\nChi-squared: {chi2:.1f}, dof={dof}, V={v:.4f}")

# Thermal aggregate
thermal_channels = {'THERMAL_SOURCE', 'THERMAL_VESSEL_K', 'THERMAL_VESSEL_T', 'THERMAL_VESSEL_L'}
assess_channels = {'ASSESSMENT_CH', 'ASSESSMENT_SH'}

thermal_a = sum(mode_channel_counts['A'].get(ch, 0) for ch in thermal_channels)
thermal_b = sum(mode_channel_counts['B'].get(ch, 0) for ch in thermal_channels)
assess_a = sum(mode_channel_counts['A'].get(ch, 0) for ch in assess_channels)
assess_b = sum(mode_channel_counts['B'].get(ch, 0) for ch in assess_channels)

thermal_pa = thermal_a / n_a if n_a else 0
thermal_pb = thermal_b / n_b if n_b else 0
assess_pa = assess_a / n_a if n_a else 0
assess_pb = assess_b / n_b if n_b else 0

print(f"\nAGGREGATES:")
print(f"  THERMAL (qo+ok+ot+ol): A={thermal_pa:.1%}, B={thermal_pb:.1%}, A/B={thermal_pa/thermal_pb:.3f}" if thermal_pb > 0 else "")
print(f"  ASSESSMENT (ch+sh):    A={assess_pa:.1%}, B={assess_pb:.1%}, A/B={assess_pa/assess_pb:.3f}" if assess_pb > 0 else "")

# Permutation test for thermal A/B ratio
import random
random.seed(42)
n_perms = 10000
observed_thermal_diff = thermal_pa - thermal_pb

all_thermal_flags = []
all_modes = []
for t in all_tokens:
    all_thermal_flags.append(1 if t['prefix_channel'] in thermal_channels else 0)
    all_modes.append(t['mode'])

perm_diffs = []
for _ in range(n_perms):
    random.shuffle(all_modes)
    perm_a = sum(f for f, m in zip(all_thermal_flags, all_modes) if m == 'A')
    perm_b = sum(f for f, m in zip(all_thermal_flags, all_modes) if m == 'B')
    perm_n_a = sum(1 for m in all_modes if m == 'A')
    perm_n_b = sum(1 for m in all_modes if m == 'B')
    if perm_n_a > 0 and perm_n_b > 0:
        perm_diffs.append(perm_a / perm_n_a - perm_b / perm_n_b)

p_thermal = sum(1 for d in perm_diffs if d >= observed_thermal_diff) / len(perm_diffs)
print(f"  Thermal enrichment permutation p={p_thermal:.4f} (10K perms)")

# Same for assessment
observed_assess_diff = assess_pb - assess_pa  # B should be higher for assessment

all_assess_flags = [1 if t['prefix_channel'] in assess_channels else 0 for t in all_tokens]
all_modes_2 = [t['mode'] for t in all_tokens]

perm_diffs_a = []
for _ in range(n_perms):
    random.shuffle(all_modes_2)
    perm_a = sum(f for f, m in zip(all_assess_flags, all_modes_2) if m == 'A')
    perm_b = sum(f for f, m in zip(all_assess_flags, all_modes_2) if m == 'B')
    perm_n_a = sum(1 for m in all_modes_2 if m == 'A')
    perm_n_b = sum(1 for m in all_modes_2 if m == 'B')
    if perm_n_a > 0 and perm_n_b > 0:
        perm_diffs_a.append(perm_b / perm_n_b - perm_a / perm_n_a)

p_assess = sum(1 for d in perm_diffs_a if d >= observed_assess_diff) / len(perm_diffs_a)
print(f"  Assessment enrichment permutation p={p_assess:.4f} (10K perms)")

results['T1_prefix_channel'] = {
    'chi2': round(chi2, 1),
    'dof': dof,
    'cramers_v': round(v, 4),
    'thermal_mode_a_pct': round(thermal_pa, 4),
    'thermal_mode_b_pct': round(thermal_pb, 4),
    'thermal_a_b_ratio': round(thermal_pa / thermal_pb, 3) if thermal_pb > 0 else None,
    'thermal_p': round(p_thermal, 4),
    'assess_mode_a_pct': round(assess_pa, 4),
    'assess_mode_b_pct': round(assess_pb, 4),
    'assess_a_b_ratio': round(assess_pa / assess_pb, 3) if assess_pb > 0 else None,
    'assess_p': round(p_assess, 4),
    'per_channel': t1_details,
    'verdict': 'PASS' if p_thermal < 0.05 and thermal_pa > thermal_pb else 'FAIL',
}

# ============================================================
# T2: MACRO-ATOM ENRICHMENT BY MODE
# ============================================================
print("\n" + "=" * 70)
print("T2: MACRO-ATOM ENRICHMENT BY MODE")
print("=" * 70)

macro_mode_counts = {'A': Counter(), 'B': Counter()}
total_by_mode = {'A': 0, 'B': 0}

for t in all_tokens:
    mid = t['middle']
    if len(mid) < 2:
        continue
    atoms = decompose_macro(mid)
    total_by_mode[t['mode']] += 1
    for atom in atoms:
        if atom in MACRO_ATOMS:
            macro_mode_counts[t['mode']][atom] += 1

n_ma = total_by_mode['A']
n_mb = total_by_mode['B']

print(f"\n{'Macro-atom':<12} {'Mode A':>8} {'%':>7} {'Mode B':>8} {'%':>7} {'A/B':>7}")
print("-" * 55)

t2_details = {}
for ma in sorted(MACRO_ATOMS.keys()):
    ca = macro_mode_counts['A'].get(ma, 0)
    cb = macro_mode_counts['B'].get(ma, 0)
    pa = ca / n_ma if n_ma else 0
    pb = cb / n_mb if n_mb else 0
    ratio = pa / pb if pb > 0 else float('inf')
    print(f"{ma:<12} {ca:>8} {pa:>7.1%} {cb:>8} {pb:>7.1%} {ratio:>7.2f}")
    t2_details[ma] = {'a_pct': round(pa, 4), 'b_pct': round(pb, 4), 'ratio': round(ratio, 3)}

# Which macro-atoms are mode-A dominant vs mode-B dominant?
a_dominant = [ma for ma, d in t2_details.items() if d['ratio'] > 1.15]
b_dominant = [ma for ma, d in t2_details.items() if d['ratio'] < 0.87]
neutral = [ma for ma, d in t2_details.items() if 0.87 <= d['ratio'] <= 1.15]

print(f"\nMode A enriched (>1.15x): {a_dominant}")
print(f"Mode B enriched (<0.87x): {b_dominant}")
print(f"Neutral: {neutral}")

results['T2_macro_atom_mode'] = {
    'per_macro': t2_details,
    'a_dominant': a_dominant,
    'b_dominant': b_dominant,
    'neutral': neutral,
}

# ============================================================
# T3: KERNEL ATOM DISTRIBUTION BY MODE
# ============================================================
print("\n" + "=" * 70)
print("T3: KERNEL ATOMS BY MODE")
print("=" * 70)

kernel_mode = {'A': Counter(), 'B': Counter()}
kernel_total = {'A': 0, 'B': 0}

for t in all_tokens:
    mid = t['middle']
    kernel_total[t['mode']] += 1
    for ka in 'khe':
        if ka in mid:
            kernel_mode[t['mode']][ka] += 1

print(f"\n{'Kernel':<8} {'Mode A':>8} {'%':>7} {'Mode B':>8} {'%':>7} {'A/B':>7}")
print("-" * 45)

t3_details = {}
for ka in 'khe':
    ca = kernel_mode['A'].get(ka, 0)
    cb = kernel_mode['B'].get(ka, 0)
    pa = ca / kernel_total['A'] if kernel_total['A'] else 0
    pb = cb / kernel_total['B'] if kernel_total['B'] else 0
    ratio = pa / pb if pb > 0 else float('inf')
    print(f"{ka:<8} {ca:>8} {pa:>7.1%} {cb:>8} {pb:>7.1%} {ratio:>7.2f}")
    t3_details[ka] = {'a_pct': round(pa, 4), 'b_pct': round(pb, 4), 'ratio': round(ratio, 3)}

# k/e ratio by mode (thermal balance)
k_a = kernel_mode['A'].get('k', 0)
e_a = kernel_mode['A'].get('e', 0)
k_b = kernel_mode['B'].get('k', 0)
e_b = kernel_mode['B'].get('e', 0)
ke_ratio_a = k_a / e_a if e_a > 0 else float('inf')
ke_ratio_b = k_b / e_b if e_b > 0 else float('inf')
print(f"\nk/e ratio:  Mode A = {ke_ratio_a:.3f}, Mode B = {ke_ratio_b:.3f}")
print(f"  (A has {'more heating' if ke_ratio_a > ke_ratio_b else 'more cooling'} relative to B)")

t3_details['ke_ratio_a'] = round(ke_ratio_a, 3)
t3_details['ke_ratio_b'] = round(ke_ratio_b, 3)
results['T3_kernel_mode'] = t3_details

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

t1_pass = results['T1_prefix_channel']['verdict'] == 'PASS'
thermal_ratio = results['T1_prefix_channel'].get('thermal_a_b_ratio', 1.0) or 1.0
assess_ratio = results['T1_prefix_channel'].get('assess_a_b_ratio', 1.0) or 1.0

print(f"""
T1 PREFIX CHANNEL SEPARATION:
  Thermal PREFIXes: Mode A {thermal_pa:.1%} vs Mode B {thermal_pb:.1%} (ratio {thermal_ratio:.3f})
  Assessment PREFIXes: Mode A {assess_pa:.1%} vs Mode B {assess_pb:.1%} (ratio {assess_ratio:.3f})
  Thermal enrichment p = {p_thermal:.4f}
  Assessment enrichment p = {p_assess:.4f}
  Chi-squared V = {v:.4f}
  Verdict: {'PASS - Mode A is thermally enriched' if t1_pass else 'FAIL'}

T2 MACRO-ATOM MODE SEPARATION:
  Mode A dominant: {a_dominant}
  Mode B dominant: {b_dominant}
  Neutral: {neutral}

T3 KERNEL MODE SEPARATION:
  k/e ratio: A={ke_ratio_a:.3f}, B={ke_ratio_b:.3f}
  Mode A is {'heating-dominant' if ke_ratio_a > ke_ratio_b else 'cooling-dominant'}
""")

# Write results
output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'suffix_mode_channel_test.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results written to {output_path}")
