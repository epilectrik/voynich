"""P-L6: l-terminal compounds show universal STAGING additive shift.

If l is a domain modifier (CONFIGURATION), then for each initial-atom group,
l-terminal compounds should have elevated STAGING relative to non-l-terminal
compounds from the same group. This should hold across >=3 initial-atom groups.
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT = Path(__file__).resolve().parent


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# ============================================================
# Collect: for each token, get MIDDLE initial atom, terminal atom, category
# ============================================================

atoms = set('adehkonimycpfstrlq')

# Data structure: initial_atom -> {l_terminal: {cat: count}, non_l_terminal: {cat: count}}
data = defaultdict(lambda: {
    'l_term': Counter(),
    'non_l_term': Counter(),
    'l_term_total': 0,
    'non_l_term_total': 0
})

# Also track by specific MIDDLE for deeper analysis
middle_cat = defaultdict(Counter)  # middle -> {cat: count}
middle_count = Counter()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or len(mid) < 2:  # need at least 2 chars for initial+terminal
        continue

    analysis = decoder.analyze_token(w)
    cat = analysis.operational_category
    if not cat:
        continue

    initial = mid[0]
    terminal = mid[-1]

    if initial not in atoms or terminal not in atoms:
        continue

    middle_cat[mid][cat] += 1
    middle_count[mid] += 1

    if terminal == 'l':
        data[initial]['l_term'][cat] += 1
        data[initial]['l_term_total'] += 1
    else:
        data[initial]['non_l_term'][cat] += 1
        data[initial]['non_l_term_total'] += 1

# ============================================================
# P-L6: STAGING fraction by initial atom, l-terminal vs non-l-terminal
# ============================================================
print(f"{'='*70}")
print("P-L6: STAGING FRACTION — l-TERMINAL vs NON-l-TERMINAL BY INITIAL ATOM")
print(f"{'='*70}")
print("Prediction: l-terminal has elevated STAGING in >=3 initial-atom groups\n")

print(f"  {'Init':<5s} {'l-term STAG':>12s} {'l-term n':>10s} {'non-l STAG':>12s} {'non-l n':>10s} {'ratio':>8s} {'sig':>5s}")
print(f"  {'-'*5} {'-'*12} {'-'*10} {'-'*12} {'-'*10} {'-'*8} {'-'*5}")

confirmed_groups = 0
total_testable = 0

results = []
for initial in sorted(data.keys()):
    d = data[initial]
    lt = d['l_term_total']
    nlt = d['non_l_term_total']
    if lt < 20 or nlt < 20:  # need enough data
        continue

    total_testable += 1
    lt_stag = d['l_term'].get('STAGING', 0)
    nlt_stag = d['non_l_term'].get('STAGING', 0)
    lt_frac = lt_stag / lt
    nlt_frac = nlt_stag / nlt
    ratio = lt_frac / nlt_frac if nlt_frac > 0 else float('inf')

    # Chi-square for this comparison
    a_val = lt_stag
    b_val = lt - lt_stag
    c_val = nlt_stag
    d_val = nlt - nlt_stag
    n = a_val + b_val + c_val + d_val
    denom = (a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val)
    if denom > 0:
        chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / denom
        z_val = math.sqrt(chi2)
        p_val = 2 * (1 - normal_cdf(z_val))
    else:
        chi2 = 0
        p_val = 1.0

    sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
    if ratio >= 2.0 and p_val < 0.05:
        confirmed_groups += 1

    results.append((initial, lt_frac, lt, nlt_frac, nlt, ratio, p_val, sig))

# Sort by ratio
results.sort(key=lambda x: -x[5])
for initial, lt_frac, lt_n, nlt_frac, nlt_n, ratio, p_val, sig in results:
    confirmed_marker = ' CONFIRMED' if ratio >= 2.0 and p_val < 0.05 else ''
    print(f"  {initial:<5s} {lt_frac:>11.3f}% {lt_n:>10d} {nlt_frac:>11.3f}% {nlt_n:>10d} {ratio:>7.2f}x {sig:>5s}{confirmed_marker}")

# ============================================================
# Full category breakdown for top initial atoms
# ============================================================
print(f"\n{'='*70}")
print("FULL CATEGORY BREAKDOWN FOR KEY INITIAL ATOMS")
print(f"{'='*70}")

categories = ['STAGING', 'THERMAL', 'FLOW', 'OPERATION', 'TRANSITION',
              'CONTAINMENT', 'MARKING', 'MONITORING']

for initial in ['e', 'o', 'a', 'k', 'i', 'd']:
    d = data[initial]
    lt = d['l_term_total']
    nlt = d['non_l_term_total']
    if lt < 20 or nlt < 20:
        continue

    print(f"\n  {initial}-initial MIDDLEs (l-term n={lt}, non-l-term n={nlt}):")
    print(f"    {'Category':<14s} {'l-term':>8s} {'non-l':>8s} {'shift':>8s}")
    print(f"    {'-'*14} {'-'*8} {'-'*8} {'-'*8}")
    for cat in categories:
        lt_frac = d['l_term'].get(cat, 0) / lt * 100
        nlt_frac = d['non_l_term'].get(cat, 0) / nlt * 100
        shift = lt_frac - nlt_frac
        marker = ' <<<' if cat == 'STAGING' and shift > 10 else ''
        print(f"    {cat:<14s} {lt_frac:>7.1f}% {nlt_frac:>7.1f}% {shift:>+7.1f}%{marker}")

# ============================================================
# Reverse test: l-INITIAL compounds — does initial-l also add STAGING?
# ============================================================
print(f"\n{'='*70}")
print("REVERSE: l-INITIAL vs NON-l-INITIAL BY TERMINAL ATOM")
print(f"{'='*70}")

data_rev = defaultdict(lambda: {
    'l_init': Counter(),
    'non_l_init': Counter(),
    'l_init_total': 0,
    'non_l_init_total': 0
})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or len(mid) < 2:
        continue

    analysis = decoder.analyze_token(w)
    cat = analysis.operational_category
    if not cat:
        continue

    initial = mid[0]
    terminal = mid[-1]
    if initial not in atoms or terminal not in atoms:
        continue

    if initial == 'l':
        data_rev[terminal]['l_init'][cat] += 1
        data_rev[terminal]['l_init_total'] += 1
    else:
        data_rev[terminal]['non_l_init'][cat] += 1
        data_rev[terminal]['non_l_init_total'] += 1

print(f"\n  {'Term':<5s} {'l-init STAG':>12s} {'l-init n':>10s} {'non-l STAG':>12s} {'non-l n':>10s} {'ratio':>8s}")
print(f"  {'-'*5} {'-'*12} {'-'*10} {'-'*12} {'-'*10} {'-'*8}")

rev_results = []
for terminal in sorted(data_rev.keys()):
    d = data_rev[terminal]
    li = d['l_init_total']
    nli = d['non_l_init_total']
    if li < 10 or nli < 20:
        continue
    li_stag = d['l_init'].get('STAGING', 0)
    nli_stag = d['non_l_init'].get('STAGING', 0)
    li_frac = li_stag / li
    nli_frac = nli_stag / nli
    ratio = li_frac / nli_frac if nli_frac > 0 else float('inf')
    rev_results.append((terminal, li_frac, li, nli_frac, nli, ratio))

rev_results.sort(key=lambda x: -x[5])
for terminal, li_frac, li_n, nli_frac, nli_n, ratio in rev_results:
    print(f"  {terminal:<5s} {li_frac:>11.3f}% {li_n:>10d} {nli_frac:>11.3f}% {nli_n:>10d} {ratio:>7.2f}x")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L6 SUMMARY")
print(f"{'='*70}")
print(f"\n  Testable initial-atom groups (>=20 tokens each): {total_testable}")
print(f"  Groups where l-terminal has >=2.0x STAGING enrichment (p<0.05): {confirmed_groups}")
print(f"  Predicted: >= 3 groups confirmed")

if confirmed_groups >= 3:
    print(f"  RESULT: CONFIRMED ({confirmed_groups}/{total_testable} groups show >=2.0x STAGING shift)")
elif confirmed_groups >= 1:
    print(f"  RESULT: PARTIAL ({confirmed_groups}/{total_testable} groups)")
else:
    print(f"  RESULT: FAILED (no groups show universal STAGING shift)")

# Also report whether the shift is ADDITIVE (present regardless of initial) or CONCENTRATED
staging_ratios = [r[5] for r in results if r[5] != float('inf')]
if staging_ratios:
    median_ratio = sorted(staging_ratios)[len(staging_ratios) // 2]
    min_ratio = min(staging_ratios)
    max_ratio = max(staging_ratios)
    print(f"\n  STAGING ratio range: {min_ratio:.2f}x — {max_ratio:.2f}x (median {median_ratio:.2f}x)")
    all_above_1 = sum(1 for r in staging_ratios if r > 1.0)
    print(f"  Groups with ANY positive shift: {all_above_1}/{len(staging_ratios)}")
