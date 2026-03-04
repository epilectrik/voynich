#!/usr/bin/env python3
"""
P-O17: o-initial anti-AXM and pro-FQ macro-state (ordnen hypothesis)

If o = "ordnen" (arrange/prepare), o-initial tokens should:
- Be ANTI-AXM: preparations are transient, not dwelling in the main loop
- Be PRO-FQ: arrangements involve frequent/iteration operations
- Be #1 anti-AXM among NEUTRAL atoms {d, y, o, i}

Also tests k vs o complementarity: k should be pro-AXM (thermal dwell),
o should be anti-AXM (preparation transient).

Pass: AXM <= 0.80x AND FQ >= 1.15x AND o ranked #1 NEUTRAL anti-AXM
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder


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
    decoder = BFolioDecoder()

    MACRO_STATES = ['AXM', 'AXm', 'CC', 'FL_HAZ', 'FL_SAFE', 'FQ']
    NEUTRAL_ATOMS = {'d', 'y', 'o', 'i'}

    # Collect: initial_atom -> macro_state -> count
    atom_macro_counts = defaultdict(lambda: defaultdict(int))
    atom_totals = defaultdict(int)
    global_macro_counts = defaultdict(int)
    global_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        ts = decoder.analyze_token(w)
        if not ts or not ts.macro_state:
            continue

        macro = ts.macro_state
        initial = m.middle[0]

        atom_macro_counts[initial][macro] += 1
        atom_totals[initial] += 1
        global_macro_counts[macro] += 1
        global_total += 1

    print("=" * 70)
    print("P-O17: o-initial anti-AXM and pro-FQ (ordnen hypothesis)")
    print("=" * 70)
    print()

    # Global baselines
    print("Global macro-state distribution:")
    for ms in MACRO_STATES:
        n = global_macro_counts[ms]
        print(f"  {ms:<10} {n:>6} ({n/global_total*100:.1f}%)")
    print(f"  TOTAL    {global_total:>6}")
    print()

    global_axm_rate = global_macro_counts['AXM'] / global_total if global_total > 0 else 0
    global_fq_rate = global_macro_counts['FQ'] / global_total if global_total > 0 else 0

    # ---- TEST 1: o-initial macro-state profile ----
    print("-" * 70)
    print("TEST 1: o-initial macro-state profile")
    print("-" * 70)
    print()

    o_total = atom_totals.get('o', 0)
    o_axm_enrich = 0
    o_fq_enrich = 0

    if o_total > 0:
        print(f"o-initial tokens: {o_total}")
        print()
        print(f"{'MacroState':<12} {'o-init%':>9} {'Global%':>9} {'Enrichment':>11}")
        print("-" * 45)
        for ms in MACRO_STATES:
            o_frac = atom_macro_counts['o'][ms] / o_total
            g_frac = global_macro_counts[ms] / global_total if global_total > 0 else 0
            enrich = o_frac / g_frac if g_frac > 0 else 0
            marker = ""
            if ms == 'AXM':
                o_axm_enrich = enrich
                marker = " <-- ANTI-AXM target"
            elif ms == 'FQ':
                o_fq_enrich = enrich
                marker = " <-- PRO-FQ target"
            print(f"  {ms:<10} {o_frac*100:>8.2f}% {g_frac*100:>8.2f}% {enrich:>10.3f}x{marker}")
    else:
        print("  WARNING: No o-initial tokens found")

    # ---- TEST 2: Rank all initial atoms by AXM enrichment (ascending = most anti-AXM first) ----
    print()
    print("-" * 70)
    print("TEST 2: All initial atoms ranked by AXM enrichment")
    print("-" * 70)
    print()

    atom_axm_list = []
    for atom in sorted(atom_totals.keys()):
        n = atom_totals[atom]
        if n < 20:
            continue
        axm_n = atom_macro_counts[atom].get('AXM', 0)
        frac = axm_n / n
        enrich = frac / global_axm_rate if global_axm_rate > 0 else 0
        group = 'NEUTRAL' if atom in NEUTRAL_ATOMS else ('KERNEL' if atom in {'k', 'e', 'h'} else 'OTHER')
        atom_axm_list.append((atom, frac, axm_n, n, enrich, group))

    atom_axm_list.sort(key=lambda x: x[4])  # Ascending (most anti-AXM first)

    print(f"{'Rank':<6} {'Atom':<6} {'AXM%':>8} {'Count':>8} {'Total':>8} {'Enrichment':>11} {'Group':>10}")
    print("-" * 65)
    o_axm_rank = None
    o_neutral_rank = None
    neutral_idx = 0
    for rank, (atom, frac, axm_n, n, enrich, group) in enumerate(atom_axm_list, 1):
        marker = " <--" if atom == 'o' else ""
        if atom in NEUTRAL_ATOMS:
            neutral_idx += 1
        if atom == 'o':
            o_axm_rank = rank
            o_neutral_rank = neutral_idx
        print(f"  {rank:<4} {atom:<4} {frac*100:>7.2f}% {axm_n:>8} {n:>8} {enrich:>10.3f}x {group:>10}{marker}")

    print()
    print(f"  o overall AXM rank: #{o_axm_rank} of {len(atom_axm_list)} (1 = most anti-AXM)")
    print(f"  o NEUTRAL AXM rank: #{o_neutral_rank} of {sum(1 for _,_,_,_,_,g in atom_axm_list if g == 'NEUTRAL')}")

    # ---- TEST 3: k vs o complementarity ----
    print()
    print("-" * 70)
    print("TEST 3: k vs o complementarity (k pro-AXM, o anti-AXM)")
    print("-" * 70)
    print()

    k_total = atom_totals.get('k', 0)
    k_axm_enrich = 0
    if k_total > 0:
        k_axm_frac = atom_macro_counts['k'].get('AXM', 0) / k_total
        k_axm_enrich = k_axm_frac / global_axm_rate if global_axm_rate > 0 else 0

    print(f"  k-initial: AXM enrichment = {k_axm_enrich:.3f}x (N={k_total})")
    print(f"  o-initial: AXM enrichment = {o_axm_enrich:.3f}x (N={o_total})")
    print(f"  k/o ratio: {k_axm_enrich / o_axm_enrich:.3f}x" if o_axm_enrich > 0 else "  k/o ratio: N/A")
    print()
    complementary = k_axm_enrich > 1.0 and o_axm_enrich < 1.0
    print(f"  Complementary (k>1.0, o<1.0)? {'YES' if complementary else 'NO'}")

    # ---- TEST 4: Chi-square significance ----
    print()
    print("-" * 70)
    print("TEST 4: Chi-square — o-initial AXM depletion significance")
    print("-" * 70)
    print()

    chi2_p = 1.0
    if o_total > 0:
        o_axm_n = atom_macro_counts['o'].get('AXM', 0)
        a = o_axm_n
        b = o_total - o_axm_n
        c = global_macro_counts['AXM'] - o_axm_n
        d = (global_total - o_total) - c
        total_table = a + b + c + d

        exp_a = (a + b) * (a + c) / total_table if total_table > 0 else 0
        exp_b = (a + b) * (b + d) / total_table if total_table > 0 else 0
        exp_c = (c + d) * (a + c) / total_table if total_table > 0 else 0
        exp_d = (c + d) * (b + d) / total_table if total_table > 0 else 0

        chi2 = 0
        for obs, exp in [(a, exp_a), (b, exp_b), (c, exp_c), (d, exp_d)]:
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

        chi2_p = chi2_1df_p(chi2)
        print(f"  Chi-square: {chi2:.3f}, p = {chi2_p:.6f}")
        if chi2_p < 0.001:
            print(f"  Significance: p < 0.001 ***")
        elif chi2_p < 0.01:
            print(f"  Significance: p < 0.01 **")
        elif chi2_p < 0.05:
            print(f"  Significance: p < 0.05 *")
        else:
            print(f"  Significance: not significant")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O17 o-initial anti-AXM pro-FQ (ordnen)")
    print("=" * 70)

    pass_axm = o_axm_enrich <= 0.80
    pass_fq = o_fq_enrich >= 1.15
    pass_neutral_rank = o_neutral_rank == 1 if o_neutral_rank is not None else False
    pass_complement = complementary
    pass_sig = chi2_p < 0.01

    results = [
        ("AXM enrichment <= 0.80x", pass_axm,
         f"{o_axm_enrich:.3f}x"),
        ("FQ enrichment >= 1.15x", pass_fq,
         f"{o_fq_enrich:.3f}x"),
        ("o ranked #1 NEUTRAL anti-AXM", pass_neutral_rank,
         f"rank #{o_neutral_rank}" if o_neutral_rank else "N/A"),
        ("k-o complementary (k>1, o<1)", pass_complement,
         f"k={k_axm_enrich:.3f}x, o={o_axm_enrich:.3f}x"),
        ("Chi-square p < 0.01", pass_sig,
         f"p = {chi2_p:.6f}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_axm and pass_fq and pass_neutral_rank
    print()
    print(f"  PRIMARY CRITERION (AXM<=0.80x AND FQ>=1.15x AND #1 NEUTRAL): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
