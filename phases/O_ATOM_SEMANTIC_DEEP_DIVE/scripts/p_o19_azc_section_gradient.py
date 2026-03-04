#!/usr/bin/env python3
"""
P-O19: AZC gradient tracks TRANSITION or STAGING (ordnen hypothesis)

If o = "ordnen" (arrange/prepare), o-initial rate should vary across systems/sections
in a way that correlates with TRANSITION or STAGING category rates, NOT with
CONTAINMENT (the failed vessel hypothesis).

Tests:
1. Collect o-initial rate per section (B, C, H, S, T) plus AZC
2. Correlate with all 8 category rates per section using Spearman
3. Control: k-initial vs THERMAL (should be strong positive)

Pass: TRANSITION or STAGING rho >= +0.50 AND CONTAINMENT |rho| < 0.50
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


def spearman_rho(x, y):
    """Compute Spearman rank correlation and two-tailed p-value."""
    n = len(x)
    if n < 4:
        return 0.0, 1.0

    def normal_cdf(z):
        if z < -8: return 0.0
        if z > 8: return 1.0
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        p_c = 0.3275911
        sign = 1 if z >= 0 else -1
        z_abs = abs(z)
        t = 1.0 / (1.0 + p_c * z_abs)
        val = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs / 2.0)
        return 0.5 * (1.0 + sign * val)

    def rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j + 1]] == vals[indexed[j]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[indexed[k]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(x)
    ry = rank(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return 0.0, 1.0
    rho = num / (den_x * den_y)
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-15))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    decoder = BFolioDecoder()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Collect per-section: atom rates and category rates
    # Sections from B folios + AZC as special section
    section_atom_counts = defaultdict(lambda: defaultdict(int))  # section -> atom -> count
    section_atom_totals = defaultdict(int)  # section -> total tokens with classifiable middle
    section_cat_counts = defaultdict(lambda: defaultdict(int))  # section -> cat -> count
    section_cat_totals = defaultdict(int)

    folio_sections = {}

    # Process Currier B tokens
    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        folio = token.folio
        if folio not in folio_sections:
            try:
                fa = decoder.analyze_folio(folio)
                folio_sections[folio] = fa.section if fa and fa.section else 'UNK'
            except Exception:
                folio_sections[folio] = 'UNK'
        section = folio_sections[folio]

        initial = m.middle[0]
        section_atom_counts[section][initial] += 1
        section_atom_totals[section] += 1

        cat = cc.classify(m.middle)
        if cat is not None:
            section_cat_counts[section][cat] += 1
            section_cat_totals[section] += 1

    # Process AZC tokens
    for token in tx.azc():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        section_atom_counts['AZC'][m.middle[0]] += 1
        section_atom_totals['AZC'] += 1

        cat = cc.classify(m.middle)
        if cat is not None:
            section_cat_counts['AZC'][cat] += 1
            section_cat_totals['AZC'] += 1

    print("=" * 70)
    print("P-O19: AZC gradient tracks TRANSITION or STAGING (ordnen)")
    print("=" * 70)
    print()

    # Show sections available
    all_sections = sorted(section_atom_totals.keys())
    print(f"Sections available: {all_sections}")
    for sec in all_sections:
        print(f"  {sec}: {section_atom_totals[sec]} tokens (atom), {section_cat_totals[sec]} tokens (cat)")
    print()

    # ---- TEST 1: o-initial rate per section ----
    print("-" * 70)
    print("TEST 1: o-initial rate per section")
    print("-" * 70)
    print()

    o_rates = {}
    k_rates = {}
    for sec in all_sections:
        total = section_atom_totals[sec]
        if total < 50:
            continue
        o_n = section_atom_counts[sec].get('o', 0)
        k_n = section_atom_counts[sec].get('k', 0)
        o_rates[sec] = o_n / total
        k_rates[sec] = k_n / total
        print(f"  {sec:<8}: o-initial = {o_n}/{total} = {o_rates[sec]*100:.2f}%, "
              f"k-initial = {k_n}/{total} = {k_rates[sec]*100:.2f}%")

    # ---- TEST 2: Category rates per section ----
    print()
    print("-" * 70)
    print("TEST 2: Category rates per section")
    print("-" * 70)
    print()

    cat_rates = defaultdict(dict)  # cat -> {section: rate}
    header = f"{'Section':<8}" + "".join(f"{cat[:6]:>8}" for cat in CATEGORIES)
    print(f"  {header}")
    print("  " + "-" * (8 + 8 * len(CATEGORIES)))
    for sec in all_sections:
        total = section_cat_totals.get(sec, 0)
        if total < 50:
            continue
        row = f"  {sec:<8}"
        for cat in CATEGORIES:
            n = section_cat_counts[sec].get(cat, 0)
            rate = n / total if total > 0 else 0
            cat_rates[cat][sec] = rate
            row += f"{rate*100:>7.1f}%"
        print(row)

    # ---- TEST 3: Correlate o-initial rate with each category rate ----
    print()
    print("-" * 70)
    print("TEST 3: Spearman correlation of o-initial rate with category rates")
    print("-" * 70)
    print()

    # Use sections present in both o_rates and cat_rates
    common_secs = sorted(set(o_rates.keys()) & set(next(iter(cat_rates.values())).keys())) if cat_rates else []

    if len(common_secs) < 4:
        print(f"  WARNING: Only {len(common_secs)} common sections -- correlations unreliable")

    o_vals = [o_rates[s] for s in common_secs]

    print(f"{'Category':<15} {'rho':>8} {'p-value':>10} {'Verdict':>10}")
    print("-" * 48)

    target_corrs = {}
    for cat in CATEGORIES:
        cat_vals = [cat_rates[cat].get(s, 0) for s in common_secs]
        rho, p = spearman_rho(o_vals, cat_vals)
        target_corrs[cat] = (rho, p)
        marker = ""
        if cat in ('TRANSITION', 'STAGING') and rho >= 0.50:
            marker = " <-- TARGET MATCH"
        elif cat == 'CONTAINMENT' and abs(rho) >= 0.50:
            marker = " <-- SHOULD NOT MATCH"
        print(f"  {cat:<13} {rho:>+.4f} {p:>10.4f} {marker}")

    # ---- TEST 4: k-initial vs THERMAL control ----
    print()
    print("-" * 70)
    print("TEST 4: Control — k-initial rate vs THERMAL category rate")
    print("-" * 70)
    print()

    k_vals = [k_rates.get(s, 0) for s in common_secs]
    thermal_vals = [cat_rates['THERMAL'].get(s, 0) for s in common_secs]
    k_thermal_rho, k_thermal_p = spearman_rho(k_vals, thermal_vals)
    print(f"  k-initial vs THERMAL: rho = {k_thermal_rho:+.4f}, p = {k_thermal_p:.4f}")
    print(f"  Control passes (rho > +0.50)? {'YES' if k_thermal_rho > 0.50 else 'NO'}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O19 AZC gradient tracks TRANSITION/STAGING (ordnen)")
    print("=" * 70)

    trans_rho = target_corrs.get('TRANSITION', (0, 1))[0]
    staging_rho = target_corrs.get('STAGING', (0, 1))[0]
    contain_rho = target_corrs.get('CONTAINMENT', (0, 1))[0]
    best_target = max(trans_rho, staging_rho)
    best_target_name = 'TRANSITION' if trans_rho >= staging_rho else 'STAGING'

    pass_target = best_target >= 0.50
    pass_contain = abs(contain_rho) < 0.50
    pass_control = k_thermal_rho > 0.50
    pass_n = len(common_secs) >= 4

    results = [
        (f"TRANSITION or STAGING rho >= +0.50", pass_target,
         f"best = {best_target_name} rho={best_target:+.3f}"),
        (f"CONTAINMENT |rho| < 0.50", pass_contain,
         f"|rho| = {abs(contain_rho):.3f}"),
        (f"Control: k vs THERMAL rho > +0.50", pass_control,
         f"rho = {k_thermal_rho:+.3f}"),
        (f"Sufficient sections (>= 4)", pass_n,
         f"N = {len(common_secs)}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_target and pass_contain
    print()
    print(f"  PRIMARY CRITERION (target>=+0.50 AND |containment|<0.50): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
