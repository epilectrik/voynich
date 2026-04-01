#!/usr/bin/env python3
"""
S3: R2 Variant Mapping — Do f57v R2's parameterized variants map to zodiac folio clusters?

f57v R2 has a 12-character repeating template: oldrxk??tryc
Positions 7-8 vary across 4 cycles:
  Cycle 1: k+f  (setting A)
  Cycle 2: m+f  (setting B)
  Cycle 3: k+p  (setting C)
  Cycle 4: k+p  (repeat of C)

Three distinct settings: (k,f), (m,f), (k,p).
Question: do zodiac folios cluster into groups matching these parameter settings?
"""

import sys
import os
import json
from collections import Counter, defaultdict

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Run from repo root
REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
REPO_ROOT = os.path.normpath(REPO_ROOT)
os.chdir(REPO_ROOT)
sys.path.insert(0, REPO_ROOT)

from scripts.voynich import Transcript, Morphology

# ============================================================
# CONFIG
# ============================================================
ZODIAC_FOLIOS = [
    'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
]

# Seasonal assignments (standard zodiac folio groupings)
# Based on zodiac sign identifications in the manuscript
SEASON_MAP = {
    'f70v1': 'Spring',   # Aries (March-April)
    'f70v2': 'Spring',   # Taurus (April-May)
    'f71r':  'Spring',   # Taurus cont.
    'f71v':  'Spring',   # Gemini (May-June)
    'f72r1': 'Summer',   # Cancer (June-July)
    'f72r2': 'Summer',   # Leo (July-Aug)
    'f72r3': 'Summer',   # Leo cont.
    'f72v1': 'Autumn',   # Libra (Sept-Oct)
    'f72v2': 'Autumn',   # Scorpio (Oct-Nov)
    'f72v3': 'Autumn',   # Sagittarius (Nov-Dec)
    'f73r':  'Winter',   # Capricorn (Dec-Jan) / Aquarius
    'f73v':  'Winter',   # Aquarius / Pisces
}

R2_SETTINGS = {
    'kf': ('k', 'f'),  # Setting A: cycles 1
    'mf': ('m', 'f'),  # Setting B: cycle 2
    'kp': ('k', 'p'),  # Setting C: cycles 3,4
}

TARGET_ATOMS = {'k', 'm', 'f', 'p'}

# ============================================================
# DATA COLLECTION
# ============================================================
tx = Transcript()
morph = Morphology()

def count_atoms(tokens):
    """Count all atoms across tokens. Returns Counter of atom chars."""
    atom_counts = Counter()
    total_atoms = 0
    for tok in tokens:
        try:
            a = morph.atomize(tok.word)
            for char, role, gloss in a.atoms:
                atom_counts[char] += 1
                total_atoms += 1
        except Exception:
            continue
    return atom_counts, total_atoms


# Collect tokens per zodiac folio
zodiac_tokens = defaultdict(list)
for tok in tx.all(h_only=True):
    if tok.folio in ZODIAC_FOLIOS:
        if tok.is_label or tok.is_uncertain or not tok.word:
            continue
        zodiac_tokens[tok.folio].append(tok)

# Collect all Currier B tokens for null model
b_tokens = list(tx.currier_b())

print("=" * 80)
print("S3: R2 VARIANT MAPPING — ZODIAC FOLIO CLUSTERING")
print("=" * 80)
print()

# ============================================================
# 1. ATOM SIGNATURE PER FOLIO
# ============================================================
print("1. ATOM RATES PER ZODIAC FOLIO")
print("-" * 80)

folio_data = {}
for folio in ZODIAC_FOLIOS:
    tokens = zodiac_tokens.get(folio, [])
    atom_counts, total = count_atoms(tokens)
    if total == 0:
        continue
    rates = {a: atom_counts.get(a, 0) / total for a in TARGET_ATOMS}
    counts = {a: atom_counts.get(a, 0) for a in TARGET_ATOMS}

    # Ratios
    km_sum = counts['k'] + counts['m']
    fp_sum = counts['f'] + counts['p']
    k_km_ratio = counts['k'] / km_sum if km_sum > 0 else 0.5
    f_fp_ratio = counts['f'] / fp_sum if fp_sum > 0 else 0.5

    folio_data[folio] = {
        'season': SEASON_MAP[folio],
        'n_tokens': len(tokens),
        'n_atoms': total,
        'counts': counts,
        'rates': rates,
        'k_km_ratio': k_km_ratio,
        'f_fp_ratio': f_fp_ratio,
    }

# Print detail table
header = f"{'Folio':<8} {'Season':<8} {'#Tok':>5} {'#Atom':>6}  {'k-rate':>7} {'m-rate':>7} {'f-rate':>7} {'p-rate':>7}  {'k/(k+m)':>8} {'f/(f+p)':>8}"
print(header)
print("-" * len(header))
for folio in ZODIAC_FOLIOS:
    if folio not in folio_data:
        continue
    d = folio_data[folio]
    r = d['rates']
    print(f"{folio:<8} {d['season']:<8} {d['n_tokens']:>5} {d['n_atoms']:>6}  "
          f"{r['k']:.4f}  {r['m']:.4f}  {r['f']:.4f}  {r['p']:.4f}  "
          f"{d['k_km_ratio']:.4f}   {d['f_fp_ratio']:.4f}")

# ============================================================
# 2. VARIANT ASSIGNMENT BY SCORE
# ============================================================
print()
print("2. R2 VARIANT ASSIGNMENT (by atom-rate score)")
print("-" * 80)
print("  Setting (k,f): score = k_rate + f_rate")
print("  Setting (m,f): score = m_rate + f_rate")
print("  Setting (k,p): score = k_rate + p_rate")
print()

variant_assignments = {}
for folio in ZODIAC_FOLIOS:
    if folio not in folio_data:
        continue
    r = folio_data[folio]['rates']
    scores = {
        'kf': r['k'] + r['f'],
        'mf': r['m'] + r['f'],
        'kp': r['k'] + r['p'],
    }
    best = max(scores, key=scores.get)
    variant_assignments[folio] = best
    folio_data[folio]['variant_scores'] = scores
    folio_data[folio]['assigned_variant'] = best
    print(f"  {folio:<8} {SEASON_MAP[folio]:<8}  "
          f"kf={scores['kf']:.4f}  mf={scores['mf']:.4f}  kp={scores['kp']:.4f}  "
          f"=> {best}")

# ============================================================
# 3. RATIO-BASED CLUSTERING
# ============================================================
print()
print("3. RATIO-BASED CLUSTERING")
print("-" * 80)
print("  k/(k+m) high => k-variants, low => m-variant")
print("  f/(f+p) high => f-variants, low => p-variant")
print("  Quadrants: (high-k, high-f)=kf  (low-k, high-f)=mf  (high-k, low-f)=kp  (low-k, low-f)=mp[invalid]")
print()

# Compute median thresholds
k_km_vals = [folio_data[f]['k_km_ratio'] for f in ZODIAC_FOLIOS if f in folio_data]
f_fp_vals = [folio_data[f]['f_fp_ratio'] for f in ZODIAC_FOLIOS if f in folio_data]
k_km_median = sorted(k_km_vals)[len(k_km_vals) // 2]
f_fp_median = sorted(f_fp_vals)[len(f_fp_vals) // 2]

print(f"  k/(k+m) median threshold: {k_km_median:.4f}")
print(f"  f/(f+p) median threshold: {f_fp_median:.4f}")
print()

ratio_assignments = {}
for folio in ZODIAC_FOLIOS:
    if folio not in folio_data:
        continue
    d = folio_data[folio]
    high_k = d['k_km_ratio'] >= k_km_median
    high_f = d['f_fp_ratio'] >= f_fp_median

    if high_k and high_f:
        quad = 'kf'
    elif not high_k and high_f:
        quad = 'mf'
    elif high_k and not high_f:
        quad = 'kp'
    else:
        quad = 'mp'  # not expected from R2

    ratio_assignments[folio] = quad
    folio_data[folio]['ratio_quadrant'] = quad
    print(f"  {folio:<8} {d['season']:<8}  "
          f"k/(k+m)={d['k_km_ratio']:.4f} {'HIGH' if high_k else 'LOW ':>4}  "
          f"f/(f+p)={d['f_fp_ratio']:.4f} {'HIGH' if high_f else 'LOW ':>4}  "
          f"=> {quad}")

# ============================================================
# 4. COMPARE TO SEASONAL ASSIGNMENTS
# ============================================================
print()
print("4. SEASONAL vs R2 VARIANT COMPARISON")
print("-" * 80)

# Cross-tabulation: season x variant (score-based)
seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
variants = ['kf', 'mf', 'kp']

print("\n  Score-based variant assignment by season:")
print(f"  {'Season':<10} {'kf':>4} {'mf':>4} {'kp':>4}  Folios")
print(f"  {'-'*10} {'-'*4} {'-'*4} {'-'*4}  {'-'*40}")
for season in seasons:
    season_folios = [f for f in ZODIAC_FOLIOS if SEASON_MAP.get(f) == season and f in variant_assignments]
    cts = Counter(variant_assignments[f] for f in season_folios)
    folio_list = ', '.join(f"{f}({variant_assignments[f]})" for f in season_folios)
    print(f"  {season:<10} {cts.get('kf',0):>4} {cts.get('mf',0):>4} {cts.get('kp',0):>4}  {folio_list}")

print("\n  Ratio-based quadrant assignment by season:")
print(f"  {'Season':<10} {'kf':>4} {'mf':>4} {'kp':>4} {'mp':>4}  Folios")
print(f"  {'-'*10} {'-'*4} {'-'*4} {'-'*4} {'-'*4}  {'-'*40}")
for season in seasons:
    season_folios = [f for f in ZODIAC_FOLIOS if SEASON_MAP.get(f) == season and f in ratio_assignments]
    cts = Counter(ratio_assignments[f] for f in season_folios)
    folio_list = ', '.join(f"{f}({ratio_assignments[f]})" for f in season_folios)
    print(f"  {season:<10} {cts.get('kf',0):>4} {cts.get('mf',0):>4} {cts.get('kp',0):>4} {cts.get('mp',0):>4}  {folio_list}")

# ============================================================
# 5. STATISTICAL TEST
# ============================================================
print()
print("5. CHI-SQUARED TEST: R2 variant vs Season")
print("-" * 80)

# Build contingency table (score-based)
# Manual chi-squared implementation (no scipy dependency)
import math

def chi2_test(table, row_labels, col_labels):
    """Manual chi-squared test for independence on a 2D list-of-lists."""
    nrows = len(table)
    ncols = len(table[0])
    row_sums = [sum(table[i]) for i in range(nrows)]
    col_sums = [sum(table[i][j] for i in range(nrows)) for j in range(ncols)]
    total = sum(row_sums)

    if total == 0:
        return None, None, None, None

    expected = [[row_sums[i] * col_sums[j] / total for j in range(ncols)] for i in range(nrows)]
    chi2 = 0.0
    for i in range(nrows):
        for j in range(ncols):
            if expected[i][j] > 0:
                chi2 += (table[i][j] - expected[i][j]) ** 2 / expected[i][j]

    dof = (nrows - 1) * (ncols - 1)

    # Approximate p-value using Wilson-Hilferty approximation for chi2 CDF
    if dof > 0:
        z = (chi2 / dof) ** (1/3) - (1 - 2 / (9 * dof))
        z /= math.sqrt(2 / (9 * dof))
        # Standard normal CDF approximation
        p_val = 0.5 * math.erfc(z / math.sqrt(2))
    else:
        p_val = 1.0

    return chi2, p_val, dof, expected

# Only use variants that actually appear
used_variants = sorted(set(variant_assignments.values()))
contingency = []
for season in seasons:
    row = []
    for v in used_variants:
        count = sum(1 for f in ZODIAC_FOLIOS
                    if SEASON_MAP.get(f) == season
                    and variant_assignments.get(f) == v)
        row.append(count)
    contingency.append(row)

print(f"\n  Contingency table (score-based):")
print(f"  {'':>10}", '  '.join(f"{v:>4}" for v in used_variants))
for i, season in enumerate(seasons):
    print(f"  {season:>10}", '  '.join(f"{contingency[i][j]:>4}" for j in range(len(used_variants))))

# Chi-squared
try:
    chi2, p_val, dof, expected = chi2_test(contingency, seasons, used_variants)
    print(f"\n  Chi-squared = {chi2:.4f}, p ~ {p_val:.4f}, dof = {dof}")
    print(f"  Expected frequencies:")
    print(f"  {'':>10}", '  '.join(f"{v:>6}" for v in used_variants))
    for i, season in enumerate(seasons):
        print(f"  {season:>10}", '  '.join(f"{expected[i][j]:>6.2f}" for j in range(len(used_variants))))
    if p_val < 0.05:
        print(f"\n  => SIGNIFICANT (p < 0.05): Variant assignments associate with seasons.")
    else:
        print(f"\n  => NOT SIGNIFICANT (p >= 0.05): No clear association between variants and seasons.")
except Exception as e:
    print(f"\n  Chi-squared test failed: {e}")
    chi2, p_val, dof = None, None, None

# Per-season atom counts
print(f"\n  Actual k, m, f, p COUNTS per season:")
print(f"  {'Season':<10} {'k':>6} {'m':>6} {'f':>6} {'p':>6}  {'k/(k+m)':>8} {'f/(f+p)':>8}")
print(f"  {'-'*10} {'-'*6} {'-'*6} {'-'*6} {'-'*6}  {'-'*8} {'-'*8}")
season_stats = {}
for season in seasons:
    season_folios_list = [f for f in ZODIAC_FOLIOS if SEASON_MAP.get(f) == season and f in folio_data]
    k_tot = sum(folio_data[f]['counts']['k'] for f in season_folios_list)
    m_tot = sum(folio_data[f]['counts']['m'] for f in season_folios_list)
    f_tot = sum(folio_data[f]['counts']['f'] for f in season_folios_list)
    p_tot = sum(folio_data[f]['counts']['p'] for f in season_folios_list)
    km = k_tot + m_tot
    fp = f_tot + p_tot
    k_km = k_tot / km if km > 0 else 0
    f_fp = f_tot / fp if fp > 0 else 0
    season_stats[season] = {
        'k': k_tot, 'm': m_tot, 'f': f_tot, 'p': p_tot,
        'k_km_ratio': k_km, 'f_fp_ratio': f_fp
    }
    print(f"  {season:<10} {k_tot:>6} {m_tot:>6} {f_tot:>6} {p_tot:>6}  "
          f"{k_km:>8.4f} {f_fp:>8.4f}")

# ============================================================
# 6. NULL MODEL: ALL CURRIER B
# ============================================================
print()
print("6. NULL MODEL: CURRIER B BASELINE")
print("-" * 80)

b_atom_counts, b_total = count_atoms(b_tokens)
b_rates = {a: b_atom_counts.get(a, 0) / b_total for a in TARGET_ATOMS}
b_km = b_atom_counts['k'] + b_atom_counts['m']
b_fp = b_atom_counts['f'] + b_atom_counts['p']
b_k_km = b_atom_counts['k'] / b_km if b_km > 0 else 0
b_f_fp = b_atom_counts['f'] / b_fp if b_fp > 0 else 0

print(f"  Currier B total atoms: {b_total}")
print(f"  k-rate: {b_rates['k']:.4f}  (count: {b_atom_counts['k']})")
print(f"  m-rate: {b_rates['m']:.4f}  (count: {b_atom_counts['m']})")
print(f"  f-rate: {b_rates['f']:.4f}  (count: {b_atom_counts['f']})")
print(f"  p-rate: {b_rates['p']:.4f}  (count: {b_atom_counts['p']})")
print(f"  k/(k+m): {b_k_km:.4f}")
print(f"  f/(f+p): {b_f_fp:.4f}")

# Compare zodiac spread to B baseline
zodiac_k_km = [folio_data[f]['k_km_ratio'] for f in ZODIAC_FOLIOS if f in folio_data]
zodiac_f_fp = [folio_data[f]['f_fp_ratio'] for f in ZODIAC_FOLIOS if f in folio_data]

print(f"\n  Zodiac k/(k+m) range: {min(zodiac_k_km):.4f} - {max(zodiac_k_km):.4f} (spread: {max(zodiac_k_km)-min(zodiac_k_km):.4f})")
print(f"  Zodiac f/(f+p) range: {min(zodiac_f_fp):.4f} - {max(zodiac_f_fp):.4f} (spread: {max(zodiac_f_fp)-min(zodiac_f_fp):.4f})")

# Compute per-folio B variation for comparison
b_folio_tokens = defaultdict(list)
for tok in b_tokens:
    b_folio_tokens[tok.folio].append(tok)

b_folio_ratios_km = []
b_folio_ratios_fp = []
for folio, toks in b_folio_tokens.items():
    ac, at = count_atoms(toks)
    if at < 20:  # skip tiny folios
        continue
    km = ac.get('k', 0) + ac.get('m', 0)
    fp = ac.get('f', 0) + ac.get('p', 0)
    if km > 0:
        b_folio_ratios_km.append(ac.get('k', 0) / km)
    if fp > 0:
        b_folio_ratios_fp.append(ac.get('f', 0) / fp)

if b_folio_ratios_km:
    print(f"\n  ALL B folios k/(k+m) range: {min(b_folio_ratios_km):.4f} - {max(b_folio_ratios_km):.4f} (spread: {max(b_folio_ratios_km)-min(b_folio_ratios_km):.4f})")
    print(f"  ALL B folios f/(f+p) range: {min(b_folio_ratios_fp):.4f} - {max(b_folio_ratios_fp):.4f} (spread: {max(b_folio_ratios_fp)-min(b_folio_ratios_fp):.4f})")

    zodiac_km_spread = max(zodiac_k_km) - min(zodiac_k_km)
    b_km_spread = max(b_folio_ratios_km) - min(b_folio_ratios_km)
    zodiac_fp_spread = max(zodiac_f_fp) - min(zodiac_f_fp)
    b_fp_spread = max(b_folio_ratios_fp) - min(b_folio_ratios_fp)

    print(f"\n  Zodiac k/(k+m) spread / B spread = {zodiac_km_spread/b_km_spread:.3f}" if b_km_spread > 0 else "")
    print(f"  Zodiac f/(f+p) spread / B spread = {zodiac_fp_spread/b_fp_spread:.3f}" if b_fp_spread > 0 else "")

    if zodiac_km_spread < b_km_spread * 0.5 and zodiac_fp_spread < b_fp_spread * 0.5:
        print("  => Zodiac variation is SMALLER than normal B variation — not meaningful.")
    elif zodiac_km_spread > b_km_spread * 0.8 or zodiac_fp_spread > b_fp_spread * 0.8:
        print("  => Zodiac variation is COMPARABLE to full B variation — potentially meaningful.")
    else:
        print("  => Zodiac variation is moderate relative to B baseline.")

# ============================================================
# 7. SUMMARY TABLE
# ============================================================
print()
print("7. FULL DETAIL TABLE")
print("=" * 120)
header = (f"{'Folio':<8} {'Season':<8} {'#Tok':>5} {'k':>5} {'m':>5} {'f':>5} {'p':>5}  "
          f"{'k-rate':>7} {'m-rate':>7} {'f-rate':>7} {'p-rate':>7}  "
          f"{'k/(k+m)':>8} {'f/(f+p)':>8}  {'Score':>6} {'Ratio':>6}")
print(header)
print("-" * 120)
for folio in ZODIAC_FOLIOS:
    if folio not in folio_data:
        continue
    d = folio_data[folio]
    r = d['rates']
    c = d['counts']
    sv = d.get('assigned_variant', '?')
    rv = d.get('ratio_quadrant', '?')
    print(f"{folio:<8} {d['season']:<8} {d['n_tokens']:>5} "
          f"{c['k']:>5} {c['m']:>5} {c['f']:>5} {c['p']:>5}  "
          f"{r['k']:>7.4f} {r['m']:>7.4f} {r['f']:>7.4f} {r['p']:>7.4f}  "
          f"{d['k_km_ratio']:>8.4f} {d['f_fp_ratio']:>8.4f}  "
          f"{sv:>6} {rv:>6}")

# ============================================================
# SAVE JSON
# ============================================================
output = {
    'description': 'S3: R2 variant mapping to zodiac folio clusters',
    'r2_settings': {k: {'atom1': v[0], 'atom2': v[1]} for k, v in R2_SETTINGS.items()},
    'folio_data': {},
    'season_stats': season_stats,
    'null_model': {
        'b_total_atoms': b_total,
        'b_rates': {a: round(b_rates[a], 6) for a in TARGET_ATOMS},
        'b_k_km_ratio': round(b_k_km, 6),
        'b_f_fp_ratio': round(b_f_fp, 6),
    },
    'chi_squared': {
        'statistic': round(chi2, 4) if chi2 is not None else None,
        'p_value': round(p_val, 6) if p_val is not None else None,
        'dof': dof,
    },
    'thresholds': {
        'k_km_median': round(k_km_median, 6),
        'f_fp_median': round(f_fp_median, 6),
    },
}

for folio in ZODIAC_FOLIOS:
    if folio not in folio_data:
        continue
    d = folio_data[folio]
    output['folio_data'][folio] = {
        'season': d['season'],
        'n_tokens': d['n_tokens'],
        'n_atoms': d['n_atoms'],
        'counts': {a: d['counts'][a] for a in TARGET_ATOMS},
        'rates': {a: round(d['rates'][a], 6) for a in TARGET_ATOMS},
        'k_km_ratio': round(d['k_km_ratio'], 6),
        'f_fp_ratio': round(d['f_fp_ratio'], 6),
        'variant_scores': {k: round(v, 6) for k, v in d.get('variant_scores', {}).items()},
        'assigned_variant_score': d.get('assigned_variant', ''),
        'assigned_variant_ratio': d.get('ratio_quadrant', ''),
    }

out_path = 'phases/AZC_ATOM_SEASONAL/results/s3_r2_variant_mapping.json'
with open(out_path, 'w', encoding='utf-8') as fout:
    json.dump(output, fout, indent=2)
print(f"\nSaved: {out_path}")
