#!/usr/bin/env python3
"""
P-O14: o-terminal redirects toward TRANSITION

If o = "ordnen" (arrange/prepare), then o in terminal position should redirect
the compound's category toward TRANSITION (preparing for state change).

For each initial atom group (e, k, a, d, i, h with N>=20), compare:
  X+o compounds vs X+non-o compounds category profiles.

Pass: >= 4/6 groups show TRANSITION enrichment >= 1.5x when o is terminal,
      AND overall TRANSITION redirect >= 2.0x.
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

    TARGET_INITIALS = ['e', 'k', 'a', 'd', 'i', 'h']

    # Collect: for each initial atom, split MIDDLEs into o-terminal vs non-o-terminal
    # initial -> {'o_term': {cat: count}, 'non_o_term': {cat: count}}
    init_o_cats = defaultdict(lambda: defaultdict(int))
    init_o_totals = defaultdict(int)
    init_nono_cats = defaultdict(lambda: defaultdict(int))
    init_nono_totals = defaultdict(int)

    # Global o-terminal vs non-o-terminal
    global_o_cats = defaultdict(int)
    global_o_total = 0
    global_nono_cats = defaultdict(int)
    global_nono_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 2:
            continue  # Need at least 2 chars for initial + terminal

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        initial = m.middle[0]
        terminal = m.middle[-1]

        if terminal == 'o':
            init_o_cats[initial][cat] += 1
            init_o_totals[initial] += 1
            global_o_cats[cat] += 1
            global_o_total += 1
        else:
            init_nono_cats[initial][cat] += 1
            init_nono_totals[initial] += 1
            global_nono_cats[cat] += 1
            global_nono_total += 1

    print("=" * 70)
    print("P-O14: o-terminal redirects toward TRANSITION (ordnen hypothesis)")
    print("=" * 70)
    print()
    print(f"Total o-terminal compound MIDDLEs: {global_o_total}")
    print(f"Total non-o-terminal compound MIDDLEs: {global_nono_total}")
    print()

    # ---- TEST 1: Overall o-terminal vs non-o-terminal category profiles ----
    print("-" * 70)
    print("TEST 1: Overall o-terminal vs non-o-terminal category profiles")
    print("-" * 70)
    print()

    print(f"{'Category':<15} {'o-term%':>9} {'non-o%':>9} {'Enrichment':>11}")
    print("-" * 50)
    overall_transition_enrich = 0
    for cat in CATEGORIES:
        o_frac = global_o_cats[cat] / global_o_total if global_o_total > 0 else 0
        nono_frac = global_nono_cats[cat] / global_nono_total if global_nono_total > 0 else 0
        enrich = o_frac / nono_frac if nono_frac > 0 else 0
        marker = ""
        if cat == 'TRANSITION':
            marker = " <-- TARGET"
            overall_transition_enrich = enrich
        print(f"  {cat:<13} {o_frac*100:>8.2f}% {nono_frac*100:>8.2f}% {enrich:>10.3f}x{marker}")

    print()
    print(f"  Overall TRANSITION enrichment (o-terminal / non-o-terminal): {overall_transition_enrich:.3f}x")

    # ---- TEST 2: Per initial-atom group analysis ----
    print()
    print("-" * 70)
    print("TEST 2: Per initial-atom group TRANSITION enrichment")
    print("-" * 70)
    print()

    groups_tested = 0
    groups_enriched = 0
    group_details = []

    for init_atom in TARGET_INITIALS:
        o_n = init_o_totals.get(init_atom, 0)
        nono_n = init_nono_totals.get(init_atom, 0)

        if o_n < 10 or nono_n < 10:
            print(f"  {init_atom}+o: N={o_n}, {init_atom}+non-o: N={nono_n} -- SKIPPED (too few)")
            continue

        groups_tested += 1

        o_trans_frac = init_o_cats[init_atom].get('TRANSITION', 0) / o_n
        nono_trans_frac = init_nono_cats[init_atom].get('TRANSITION', 0) / nono_n
        enrich = o_trans_frac / nono_trans_frac if nono_trans_frac > 0 else (999 if o_trans_frac > 0 else 0)

        enriched = enrich >= 1.5
        if enriched:
            groups_enriched += 1

        print(f"  {init_atom}+o (N={o_n}): TRANSITION = {o_trans_frac*100:.1f}%")
        print(f"  {init_atom}+non-o (N={nono_n}): TRANSITION = {nono_trans_frac*100:.1f}%")
        print(f"    Enrichment: {enrich:.3f}x {'ENRICHED' if enriched else ''}")

        # Show full profile for this group
        print(f"    Full profile ({init_atom}+o):")
        for cat in CATEGORIES:
            o_cf = init_o_cats[init_atom].get(cat, 0) / o_n if o_n > 0 else 0
            nono_cf = init_nono_cats[init_atom].get(cat, 0) / nono_n if nono_n > 0 else 0
            ce = o_cf / nono_cf if nono_cf > 0 else 0
            print(f"      {cat:<13} {o_cf*100:>7.1f}% vs {nono_cf*100:>7.1f}% = {ce:.2f}x")
        print()

        group_details.append((init_atom, o_n, nono_n, enrich, enriched))

    # ---- TEST 3: Show top o-terminal compounds ----
    print("-" * 70)
    print("TEST 3: Most frequent o-terminal MIDDLEs with categories")
    print("-" * 70)
    print()

    o_term_middles = defaultdict(int)
    o_term_cats = defaultdict(lambda: defaultdict(int))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m.middle or len(m.middle) < 2:
            continue
        if m.middle[-1] != 'o':
            continue
        cat = cc.classify(m.middle)
        if cat is None:
            continue
        o_term_middles[m.middle] += 1
        o_term_cats[m.middle][cat] += 1

    sorted_mids = sorted(o_term_middles.items(), key=lambda x: -x[1])[:20]
    print(f"{'MIDDLE':<12} {'Count':>6} {'Category':>15} {'Cat%':>7}")
    print("-" * 45)
    for mid, count in sorted_mids:
        top_cat = max(o_term_cats[mid], key=o_term_cats[mid].get) if o_term_cats[mid] else 'N/A'
        top_pct = o_term_cats[mid][top_cat] / count * 100 if count > 0 else 0
        print(f"  {mid:<10} {count:>6} {top_cat:>15} {top_pct:>6.1f}%")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O14 o-terminal TRANSITION redirect (ordnen)")
    print("=" * 70)

    pass_groups = groups_tested > 0 and groups_enriched >= 4
    pass_overall = overall_transition_enrich >= 2.0

    # Adjusted: if fewer than 6 groups testable, require proportional pass
    min_groups_needed = min(4, max(1, int(groups_tested * 0.67)))
    pass_groups_adj = groups_enriched >= min_groups_needed if groups_tested > 0 else False

    results = [
        (f">= 4/6 groups TRANSITION enriched >= 1.5x", pass_groups,
         f"{groups_enriched}/{groups_tested} groups enriched"),
        (f"Adjusted (>= {min_groups_needed}/{groups_tested} groups)", pass_groups_adj,
         f"{groups_enriched}/{groups_tested} groups enriched"),
        ("Overall TRANSITION redirect >= 2.0x", pass_overall,
         f"{overall_transition_enrich:.3f}x"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_groups and pass_overall
    overall_adj = pass_groups_adj and pass_overall
    print()
    print(f"  PRIMARY CRITERION (>=4/6 groups + overall>=2.0x): {'PASS' if overall else 'FAIL'}")
    print(f"  ADJUSTED CRITERION (>={min_groups_needed}/{groups_tested} + overall>=2.0x): {'PASS' if overall_adj else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
