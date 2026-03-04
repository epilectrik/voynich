#!/usr/bin/env python3
"""
P-C3: c...h junction compounds vs non-h compounds

Test whether the obligatory c->h junction (C1216: 380/380 = 100%, 11.7x
enrichment) creates a meaningful category split between c-compounds
that end in h vs those that don't.

The c->h junction is the most constrained junction in the entire system.
If c="adjust" and h="watch/monitor", then c-compounds WITH terminal h
should carry a monitoring/marking overlay.

Predictions:
  1. c-compounds ending in h (ckh, cth, cph, cfh) have MONITORING+MARKING
     combined >= 50%
  2. c-compounds NOT ending in h (ck, ct, cp, cs) have LOWER
     MONITORING+MARKING combined rate
  3. h-junction adds monitoring overlay visible as category shift

Pass criterion: h-junction group MONITORING+MARKING >= 50% AND
               h-junction enriched over non-h-junction group.

Method:
  - Split all c-initial MIDDLEs into h-terminal vs non-h-terminal
  - Compare 8-category profiles between groups
  - Chi-square for MONITORING+MARKING enrichment difference
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


def normal_cdf(x):
    """Approximate CDF of standard normal using Abramowitz & Stegun."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p_const = 0.3275911
    sign = 1 if x >= 0 else -1
    x_abs = abs(x)
    t = 1.0 / (1.0 + p_const * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs / 2.0)
    return 0.5 * (1.0 + sign * y)


def chi2_1df_p(chi2_val):
    """Approximate p-value for chi-square with 1 df."""
    if chi2_val <= 0:
        return 1.0
    z = math.sqrt(chi2_val)
    return 2.0 * (1.0 - normal_cdf(z))


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Collect category counts for c-initial MIDDLEs, split by h-terminal
    h_junction_cats = defaultdict(int)     # h-terminal c-compounds
    non_h_junction_cats = defaultdict(int)  # non-h-terminal c-compounds
    h_junction_total = 0
    non_h_junction_total = 0

    # Per-MIDDLE tracking for detail output
    middle_cats = defaultdict(lambda: defaultdict(int))
    middle_totals = defaultdict(int)

    # Global baseline
    global_cat_counts = defaultdict(int)
    global_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        global_cat_counts[cat] += 1
        global_total += 1

        # Only process c-initial compound MIDDLEs (length > 1)
        if m.middle[0] != 'c':
            continue
        if len(m.middle) < 2:
            continue  # skip standalone 'c'

        middle_cats[m.middle][cat] += 1
        middle_totals[m.middle] += 1

        if m.middle[-1] == 'h':
            h_junction_cats[cat] += 1
            h_junction_total += 1
        else:
            non_h_junction_cats[cat] += 1
            non_h_junction_total += 1

    print("=" * 70)
    print("P-C3: c...h junction compounds vs non-h compounds")
    print("=" * 70)
    print()
    print(f"c-initial compound MIDDLEs found:")
    print(f"  h-terminal:     {h_junction_total} tokens")
    print(f"  non-h-terminal: {non_h_junction_total} tokens")
    print(f"  Global total:   {global_total} tokens")
    print()

    # ---- TEST 1: List all c-initial compound MIDDLEs ----
    print("-" * 70)
    print("TEST 1: All c-initial compound MIDDLEs by frequency")
    print("-" * 70)
    print()

    all_c_compounds = sorted(middle_totals.items(), key=lambda x: -x[1])
    print(f"{'MIDDLE':<10} {'N':>5} {'h-term?':>8} {'TopCat':>14} {'MON+MARK%':>10}")
    print("-" * 50)
    for mid, total in all_c_compounds:
        h_term = "YES" if mid[-1] == 'h' else "no"
        top_cat = max(middle_cats[mid], key=middle_cats[mid].get) if middle_cats[mid] else 'N/A'
        mon_mark = middle_cats[mid].get('MONITORING', 0) + middle_cats[mid].get('MARKING', 0)
        mon_mark_pct = mon_mark / total * 100 if total > 0 else 0
        print(f"  {mid:<8} {total:>5} {h_term:>8} {top_cat:>14} {mon_mark_pct:>9.1f}%")

    # ---- TEST 2: Category profiles for both groups ----
    print()
    print("-" * 70)
    print("TEST 2: 8-category profile comparison")
    print("-" * 70)
    print()

    print(f"{'Category':<15} {'h-junction%':>12} {'non-h%':>12} {'Global%':>10} {'h-enrich':>10} {'non-h-enrich':>13}")
    print("-" * 75)

    h_mon_mark = 0
    non_h_mon_mark = 0

    for cat in CATEGORIES:
        h_n = h_junction_cats.get(cat, 0)
        nh_n = non_h_junction_cats.get(cat, 0)
        h_frac = h_n / h_junction_total if h_junction_total > 0 else 0
        nh_frac = nh_n / non_h_junction_total if non_h_junction_total > 0 else 0
        global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
        h_enrich = h_frac / global_frac if global_frac > 0 else 0
        nh_enrich = nh_frac / global_frac if global_frac > 0 else 0

        if cat in ('MONITORING', 'MARKING'):
            h_mon_mark += h_frac
            non_h_mon_mark += nh_frac

        marker = ""
        if cat in ('MONITORING', 'MARKING'):
            marker = "  <--"

        print(f"  {cat:<13} {h_frac*100:>11.2f}% {nh_frac*100:>11.2f}% {global_frac*100:>9.2f}% "
              f"{h_enrich:>9.3f}x {nh_enrich:>12.3f}x{marker}")

    print()
    print(f"  Combined MONITORING+MARKING:")
    print(f"    h-junction:     {h_mon_mark*100:.1f}%")
    print(f"    non-h-junction: {non_h_mon_mark*100:.1f}%")

    # ---- TEST 3: Chi-square for MONITORING+MARKING difference ----
    print()
    print("-" * 70)
    print("TEST 3: Chi-square -- h-junction vs non-h MONITORING+MARKING")
    print("-" * 70)

    h_mm_n = h_junction_cats.get('MONITORING', 0) + h_junction_cats.get('MARKING', 0)
    nh_mm_n = non_h_junction_cats.get('MONITORING', 0) + non_h_junction_cats.get('MARKING', 0)

    # 2x2: (h-junction vs non-h) x (MON+MARK vs other)
    a = h_mm_n
    b = h_junction_total - h_mm_n
    c_val = nh_mm_n
    d = non_h_junction_total - nh_mm_n
    total_2x2 = a + b + c_val + d

    chi2 = 0.0
    p_val = 1.0
    if total_2x2 > 0 and (a + b) > 0 and (c_val + d) > 0 and (a + c_val) > 0 and (b + d) > 0:
        ea = (a + b) * (a + c_val) / total_2x2
        eb = (a + b) * (b + d) / total_2x2
        ec = (c_val + d) * (a + c_val) / total_2x2
        ed = (c_val + d) * (b + d) / total_2x2

        for obs, exp in [(a, ea), (b, eb), (c_val, ec), (d, ed)]:
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

        p_val = chi2_1df_p(chi2)

    print(f"  h-junction MON+MARK: {h_mm_n}/{h_junction_total} = {h_mon_mark*100:.1f}%")
    print(f"  non-h MON+MARK:      {nh_mm_n}/{non_h_junction_total} = {non_h_mon_mark*100:.1f}%")
    print(f"  Chi-square: {chi2:.3f}, p = {p_val:.6f}")
    if p_val < 0.001:
        print(f"  Significance: p < 0.001 ***")
    elif p_val < 0.01:
        print(f"  Significance: p < 0.01 **")
    elif p_val < 0.05:
        print(f"  Significance: p < 0.05 *")
    else:
        print(f"  Significance: not significant")

    # ---- TEST 4: Per-compound detail for key compounds ----
    print()
    print("-" * 70)
    print("TEST 4: Detailed profiles for key c-compounds")
    print("-" * 70)
    print()

    key_compounds = ['ck', 'ckh', 'ct', 'cth', 'cph', 'cfh', 'cp', 'cs']
    for mid in key_compounds:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print(f"  {mid}: NOT FOUND")
            continue

        h_term = "h-junction" if mid[-1] == 'h' else "non-h"
        direct_cat = cc.classify(mid) or 'N/A'
        print(f"  {mid} (N={total}, {h_term}, direct={direct_cat}):")
        for cat in CATEGORIES:
            n = middle_cats[mid].get(cat, 0)
            if n > 0:
                print(f"    {cat:<15} {n:>5} ({n/total*100:>5.1f}%)")
        print()

    # ---- SUMMARY ----
    print("=" * 70)
    print("SUMMARY: P-C3 c...h junction category split")
    print("=" * 70)

    pass_h_threshold = h_mon_mark >= 0.50
    pass_h_enriched = h_mon_mark > non_h_mon_mark
    pass_chi2 = p_val < 0.05
    pass_h_count = h_junction_total >= 50  # sufficient data

    results = [
        ("h-junction MONITORING+MARKING >= 50%", pass_h_threshold,
         f"{h_mon_mark*100:.1f}%"),
        ("h-junction more enriched than non-h", pass_h_enriched,
         f"{h_mon_mark*100:.1f}% vs {non_h_mon_mark*100:.1f}%"),
        ("Chi-square significant (p < 0.05)", pass_chi2,
         f"chi2={chi2:.3f}, p={p_val:.6f}"),
        ("Sufficient h-junction data (N >= 50)", pass_h_count,
         f"N={h_junction_total}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    primary = pass_h_threshold and pass_h_enriched
    print()
    print(f"  PRIMARY CRITERION (h-junction MON+MARK >= 50% AND > non-h): {'PASS' if primary else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary else 'FAIL'}")


if __name__ == '__main__':
    main()
