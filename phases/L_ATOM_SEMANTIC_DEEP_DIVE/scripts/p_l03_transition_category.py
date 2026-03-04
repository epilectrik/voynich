"""P-L3: l-bearing MIDDLEs should show elevated TRANSITION category fraction.

If l = "release/discharge", then l-atom MIDDLEs should be enriched in
TRANSITION category (C1250) compared to non-l MIDDLEs, because release
operations are inherently state-transitional.
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
# P-L3: l-atom MIDDLEs vs TRANSITION category
# ============================================================
print(f"{'='*70}")
print("P-L3: l-ATOM MIDDLEs vs OPERATIONAL CATEGORY (C1250)")
print(f"{'='*70}")
print("Prediction: l-bearing MIDDLEs enriched in TRANSITION category\n")

# Collect operational_category for l-atom vs non-l tokens
l_cat = Counter()
nol_cat = Counter()
l_total = 0
nol_total = 0

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue

    analysis = decoder.analyze_token(w)
    cat = analysis.operational_category
    if not cat:
        continue

    has_l = 'l' in mid
    if has_l:
        l_cat[cat] += 1
        l_total += 1
    else:
        nol_cat[cat] += 1
        nol_total += 1

print(f"  Tokens with l-atom MIDDLE: {l_total}")
print(f"  Tokens without l in MIDDLE: {nol_total}")

print(f"\n  {'Category':<16s} {'l-atom':>8s} {'l-%':>8s} {'no-l':>8s} {'no-l-%':>8s} {'l/no-l':>8s}")
print(f"  {'-'*16} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

all_cats = sorted(set(list(l_cat.keys()) + list(nol_cat.keys())))
for cat in all_cats:
    lc = l_cat.get(cat, 0)
    nc = nol_cat.get(cat, 0)
    l_pct = lc / l_total * 100 if l_total > 0 else 0
    n_pct = nc / nol_total * 100 if nol_total > 0 else 0
    ratio = (lc / l_total) / (nc / nol_total) if nc > 0 and nol_total > 0 else float('inf')
    sig = ''
    # Chi-square for this category
    if lc + nc > 0:
        a_val = lc
        b_val = l_total - lc
        c_val = nc
        d_val = nol_total - nc
        n = a_val + b_val + c_val + d_val
        denom = (a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val)
        if denom > 0:
            chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / denom
            z_c = math.sqrt(chi2)
            p_c = 2 * (1 - normal_cdf(z_c))
            if p_c < 0.001: sig = '***'
            elif p_c < 0.01: sig = '**'
            elif p_c < 0.05: sig = '*'
    print(f"  {cat:<16s} {lc:>8d} {l_pct:>7.1f}% {nc:>8d} {n_pct:>7.1f}% {ratio:>7.3f}x {sig}")

# ============================================================
# Break down by l-position: initial, terminal, medial
# ============================================================
print(f"\n{'='*70}")
print("l-POSITION WITHIN MIDDLE vs CATEGORY")
print(f"{'='*70}")

l_init_cat = Counter()
l_term_cat = Counter()
l_mid_cat = Counter()
l_init_total = 0
l_term_total = 0
l_mid_total = 0

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or 'l' not in mid:
        continue

    analysis = decoder.analyze_token(w)
    cat = analysis.operational_category
    if not cat:
        continue

    if mid[0] == 'l':
        l_init_cat[cat] += 1
        l_init_total += 1
    if mid[-1] == 'l':
        l_term_cat[cat] += 1
        l_term_total += 1
    if len(mid) > 2 and 'l' in mid[1:-1]:
        l_mid_cat[cat] += 1
        l_mid_total += 1

for label, counter, total in [
    ('l-initial', l_init_cat, l_init_total),
    ('l-terminal', l_term_cat, l_term_total),
    ('l-medial', l_mid_cat, l_mid_total),
]:
    if total == 0:
        continue
    print(f"\n  {label} (n={total}):")
    for cat in all_cats:
        c = counter.get(cat, 0)
        pct = c / total * 100
        # Compare to no-l baseline
        baseline = nol_cat.get(cat, 0) / nol_total * 100 if nol_total > 0 else 0
        ratio = (c / total) / (nol_cat.get(cat, 0) / nol_total) if nol_cat.get(cat, 0) > 0 and nol_total > 0 else 0
        print(f"    {cat:<16s} {c:>6d} {pct:>7.1f}% (baseline {baseline:>5.1f}%) {ratio:>6.2f}x")

# ============================================================
# Per-atom TRANSITION enrichment (comprehensive ranking)
# ============================================================
print(f"\n{'='*70}")
print("ALL ATOMS: TRANSITION CATEGORY ENRICHMENT (comprehensive)")
print(f"{'='*70}")

atoms = 'a d e h k o n i m y c p f s t r l q'.split()
atom_trans = {}

# Get baseline TRANSITION rate
total_tokens = 0
total_trans = 0

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue
    analysis = decoder.analyze_token(w)
    cat = analysis.operational_category
    if not cat:
        continue
    total_tokens += 1
    if cat == 'TRANSITION':
        total_trans += 1

baseline_trans = total_trans / total_tokens if total_tokens > 0 else 0
print(f"\n  Baseline TRANSITION rate: {baseline_trans:.4f} ({total_trans}/{total_tokens})")

# Per-atom
for atom in atoms:
    atom_count = 0
    atom_trans_count = 0
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        mid = morph.extract(w).middle
        if not mid:
            continue
        if atom not in mid:
            continue
        analysis = decoder.analyze_token(w)
        cat = analysis.operational_category
        if not cat:
            continue
        atom_count += 1
        if cat == 'TRANSITION':
            atom_trans_count += 1
    if atom_count > 0:
        rate = atom_trans_count / atom_count
        enrich = rate / baseline_trans if baseline_trans > 0 else 0
        atom_trans[atom] = (rate, enrich, atom_count, atom_trans_count)

# Sort by enrichment
print(f"\n  {'Atom':<5s} {'TRANS rate':>11s} {'enrichment':>12s} {'n':>8s} {'trans':>6s}")
print(f"  {'-'*5} {'-'*11} {'-'*12} {'-'*8} {'-'*6}")
for atom, (rate, enrich, n, tc) in sorted(atom_trans.items(), key=lambda x: -x[1][1]):
    marker = ' <-- l' if atom == 'l' else ''
    print(f"  {atom:<5s} {rate:>11.4f} {enrich:>11.3f}x {n:>8d} {tc:>6d}{marker}")

# ============================================================
# ALSO: l-atom vs CC macro_state (the 8.84x signal) by category
# ============================================================
print(f"\n{'='*70}")
print("CROSS-CHECK: CATEGORY of l-atom CC tokens specifically")
print(f"{'='*70}")

l_cc_cat = Counter()
l_cc_total = 0

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid or 'l' not in mid:
        continue
    analysis = decoder.analyze_token(w)
    ms = analysis.macro_state
    cat = analysis.operational_category
    if ms == 'CC' and cat:
        l_cc_cat[cat] += 1
        l_cc_total += 1

if l_cc_total > 0:
    print(f"\n  l-atom tokens in CC state (n={l_cc_total}):")
    for cat in sorted(l_cc_cat.keys(), key=lambda c: -l_cc_cat[c]):
        c = l_cc_cat[cat]
        print(f"    {cat:<16s} {c:>6d} ({c/l_cc_total*100:>5.1f}%)")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L3 SUMMARY")
print(f"{'='*70}")

l_trans_rate = l_cat.get('TRANSITION', 0) / l_total if l_total > 0 else 0
nol_trans_rate = nol_cat.get('TRANSITION', 0) / nol_total if nol_total > 0 else 0
enrichment = l_trans_rate / nol_trans_rate if nol_trans_rate > 0 else 0

print(f"\n  TRANSITION rate: l-atom={l_trans_rate:.4f} vs no-l={nol_trans_rate:.4f}")
print(f"  Enrichment: {enrichment:.3f}x")

if enrichment > 1.2:
    # Chi-square
    a_val = l_cat.get('TRANSITION', 0)
    b_val = l_total - a_val
    c_val = nol_cat.get('TRANSITION', 0)
    d_val = nol_total - c_val
    n = a_val + b_val + c_val + d_val
    denom = (a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val)
    chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / denom if denom > 0 else 0
    z_val = math.sqrt(chi2)
    p_val = 2 * (1 - normal_cdf(z_val))
    print(f"  Chi-square: {chi2:.2f}, p={p_val:.6f}")
    if p_val < 0.05:
        print(f"  RESULT: CONFIRMED")
    else:
        print(f"  RESULT: DIRECTIONALLY CORRECT but not significant")
else:
    print(f"  RESULT: {'CONFIRMED' if enrichment > 1.0 else 'FAILED'}")
