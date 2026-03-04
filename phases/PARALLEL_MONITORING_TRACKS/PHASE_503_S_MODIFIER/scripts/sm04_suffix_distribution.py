#!/usr/bin/env python3
"""
SM-4: Suffix distribution shift test

Question: Does adding s to a MIDDLE change which suffixes attach?

Compare suffix distributions for s-containing vs non-s MIDDLEs:
  Pair 1: sh-initial MIDDLEs vs h-initial MIDDLEs (not sh-initial)
  Pair 2: MIDDLEs containing "ksh" vs MIDDLEs containing "kh" (not "ksh")
  Pair 3: MIDDLE="es" vs MIDDLE="e" (standalone)

For each pair, compute suffix frequency distribution, then chi-square
test for independence.

Pass: >= 2/3 pairs show significantly different suffix distributions (p < 0.05).
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology


def chi2_test(dist_a, dist_b):
    """
    Chi-square test of independence for two suffix distributions.
    Returns (chi2, df, p_approx, n_a, n_b).

    dist_a, dist_b: Counter objects mapping suffix -> count.
    Uses all suffixes present in either distribution.
    Only includes suffixes with expected >= 1 in at least one cell.
    """
    all_suffixes = sorted(set(list(dist_a.keys()) + list(dist_b.keys())))
    n_a = sum(dist_a.values())
    n_b = sum(dist_b.values())
    n_total = n_a + n_b

    if n_total == 0 or n_a == 0 or n_b == 0:
        return 0.0, 0, 1.0, n_a, n_b

    # Filter to suffixes with total count >= 2 to avoid tiny expected values
    valid_suffixes = []
    for s in all_suffixes:
        col_total = dist_a.get(s, 0) + dist_b.get(s, 0)
        if col_total >= 2:
            valid_suffixes.append(s)

    if len(valid_suffixes) < 2:
        return 0.0, 0, 1.0, n_a, n_b

    chi2 = 0.0
    for s in valid_suffixes:
        o_a = dist_a.get(s, 0)
        o_b = dist_b.get(s, 0)
        col_total = o_a + o_b

        e_a = n_a * col_total / n_total
        e_b = n_b * col_total / n_total

        if e_a > 0:
            chi2 += (o_a - e_a) ** 2 / e_a
        if e_b > 0:
            chi2 += (o_b - e_b) ** 2 / e_b

    df = len(valid_suffixes) - 1  # (2-1) * (k-1) = k-1

    # Approximate p-value using chi-square survival function
    # Use Wilson-Hilferty approximation for chi-square CDF
    p_approx = chi2_survival(chi2, df)

    return chi2, df, p_approx, n_a, n_b


def chi2_survival(x, df):
    """
    Approximate chi-square survival function P(X >= x) for df degrees of freedom.
    Uses Wilson-Hilferty normal approximation.
    """
    if df <= 0:
        return 1.0
    if x <= 0:
        return 1.0

    # Wilson-Hilferty transformation to standard normal
    z = ((x / df) ** (1.0 / 3.0) - (1 - 2.0 / (9 * df))) / math.sqrt(2.0 / (9 * df))

    # Standard normal CDF (Abramowitz & Stegun approximation)
    p_normal = normal_cdf(z)
    return 1.0 - p_normal


def normal_cdf(z):
    """Standard normal CDF using Abramowitz & Stegun approximation."""
    if z < -8:
        return 0.0
    if z > 8:
        return 1.0

    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p_coef = 0.3275911

    sign = 1.0
    if z < 0:
        sign = -1.0
    z_abs = abs(z) / math.sqrt(2.0)

    t = 1.0 / (1.0 + p_coef * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs)

    return 0.5 * (1.0 + sign * y)


def print_suffix_profile(dist, total, label, top_n=15):
    """Print a suffix frequency distribution."""
    sorted_items = sorted(dist.items(), key=lambda x: -x[1])
    print(f"  {label} (N={total}):")
    for suffix, count in sorted_items[:top_n]:
        pct = count / total * 100 if total > 0 else 0.0
        sfx_display = suffix if suffix else '(bare/none)'
        print(f"    {sfx_display:<15} {count:>5} ({pct:>5.1f}%)")
    if len(sorted_items) > top_n:
        remaining = sum(c for _, c in sorted_items[top_n:])
        print(f"    {'(others)':<15} {remaining:>5} ({remaining/total*100 if total > 0 else 0:.1f}%)")


def main():
    tx = Transcript()
    morph = Morphology()

    # Collect suffix distributions for various MIDDLE categories
    # Key = pair_group, value = Counter of suffixes
    # We need: sh-initial MIDDLEs, h-initial (not sh) MIDDLEs,
    # ksh-containing MIDDLEs, kh-containing (not ksh) MIDDLEs,
    # MIDDLE=es, MIDDLE=e

    suffix_dists = {
        'sh_initial': Counter(),
        'h_initial_no_sh': Counter(),
        'ksh_containing': Counter(),
        'kh_no_ksh': Counter(),
        'middle_es': Counter(),
        'middle_e': Counter(),
    }

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle:
            continue

        mid = m.middle
        sfx = m.suffix if m.suffix else ''  # empty string for bare/no suffix

        # Pair 1: sh-initial vs h-initial (not sh)
        if mid.startswith('sh'):
            suffix_dists['sh_initial'][sfx] += 1
        elif mid.startswith('h') and not mid.startswith('sh'):
            # h-initial but NOT sh-initial
            suffix_dists['h_initial_no_sh'][sfx] += 1

        # Pair 2: ksh-containing vs kh-containing (not ksh)
        if 'ksh' in mid:
            suffix_dists['ksh_containing'][sfx] += 1
        elif 'kh' in mid and 'ksh' not in mid:
            suffix_dists['kh_no_ksh'][sfx] += 1

        # Pair 3: MIDDLE exactly "es" vs exactly "e"
        if mid == 'es':
            suffix_dists['middle_es'][sfx] += 1
        elif mid == 'e':
            suffix_dists['middle_e'][sfx] += 1

    print("=" * 75)
    print("SM-4: Suffix distribution shift -- Does s change suffix attachment?")
    print("=" * 75)
    print()

    # Define the test pairs
    pairs = [
        {
            'name': 'Pair 1: sh-initial MIDDLEs vs h-initial (not sh) MIDDLEs',
            's_group': 'sh_initial',
            'non_s_group': 'h_initial_no_sh',
            's_label': 'sh-initial MIDDLEs',
            'non_s_label': 'h-initial (not sh) MIDDLEs',
        },
        {
            'name': 'Pair 2: ksh-containing MIDDLEs vs kh-containing (not ksh)',
            's_group': 'ksh_containing',
            'non_s_group': 'kh_no_ksh',
            's_label': 'ksh-containing MIDDLEs',
            'non_s_label': 'kh (not ksh) MIDDLEs',
        },
        {
            'name': 'Pair 3: MIDDLE="es" vs MIDDLE="e"',
            's_group': 'middle_es',
            'non_s_group': 'middle_e',
            's_label': 'MIDDLE="es"',
            'non_s_label': 'MIDDLE="e"',
        },
    ]

    sig_count = 0
    tested = 0
    pair_results = []

    for pair in pairs:
        print("-" * 75)
        print(pair['name'])
        print("-" * 75)
        print()

        dist_s = suffix_dists[pair['s_group']]
        dist_ns = suffix_dists[pair['non_s_group']]
        total_s = sum(dist_s.values())
        total_ns = sum(dist_ns.values())

        print_suffix_profile(dist_s, total_s, pair['s_label'])
        print()
        print_suffix_profile(dist_ns, total_ns, pair['non_s_label'])
        print()

        # Side-by-side comparison of shared suffixes
        all_sfx = sorted(set(list(dist_s.keys()) + list(dist_ns.keys())),
                         key=lambda x: -(dist_s.get(x, 0) + dist_ns.get(x, 0)))

        print(f"  {'Suffix':<15} {'s-form':>8} {'s-%':>7} {'non-s':>8} {'non-s%':>7}")
        print(f"  {'-'*50}")
        for sfx in all_sfx[:12]:
            sfx_display = sfx if sfx else '(bare)'
            ns = dist_s.get(sfx, 0)
            nns = dist_ns.get(sfx, 0)
            ps = ns / total_s * 100 if total_s > 0 else 0
            pns = nns / total_ns * 100 if total_ns > 0 else 0
            print(f"  {sfx_display:<15} {ns:>8} {ps:>6.1f}% {nns:>8} {pns:>6.1f}%")
        print()

        # Chi-square test
        if total_s < 5 or total_ns < 5:
            print(f"  Chi-square: SKIPPED (insufficient data: s={total_s}, non-s={total_ns})")
            pair_results.append((pair['name'], total_s, total_ns, 0, 0, 1.0, False))
            continue

        tested += 1
        chi2, df, p_val, _, _ = chi2_test(dist_s, dist_ns)
        is_sig = p_val < 0.05

        if is_sig:
            sig_count += 1

        pair_results.append((pair['name'], total_s, total_ns, chi2, df, p_val, is_sig))

        print(f"  Chi-square test:")
        print(f"    chi2 = {chi2:.2f}, df = {df}, p {'<' if p_val < 0.001 else '='} "
              f"{'<0.001' if p_val < 0.001 else f'{p_val:.4f}'}")
        print(f"    Verdict: {'SIGNIFICANT (p < 0.05)' if is_sig else 'NOT SIGNIFICANT'}")
        print()

    # ---- SUMMARY ----
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)
    print()

    header = f"{'Pair':<55} {'N(s)':>6} {'N(ns)':>6} {'chi2':>8} {'df':>4} {'p':>10} {'Sig?':>5}"
    print(header)
    print("-" * len(header))

    for name, ns, nns, chi2, df, p, is_sig in pair_results:
        short_name = name[:53]
        p_str = '<0.001' if p < 0.001 else f'{p:.4f}'
        print(f"  {short_name:<53} {ns:>6} {nns:>6} {chi2:>8.2f} {df:>4} {p_str:>10} "
              f"{'YES' if is_sig else 'NO':>5}")

    # ---- VERDICT ----
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    if tested == 0:
        print("  No pairs had sufficient data for testing -- CANNOT EVALUATE")
        overall = False
    else:
        threshold = 2
        overall = sig_count >= threshold
        print(f"  Tested: {tested}/3 pairs had sufficient data")
        print(f"  Significant (p < 0.05): {sig_count}/{tested}")
        print(f"  Threshold: >= {threshold}/3")
        print()
        print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
        if overall:
            print("  Adding s to a MIDDLE significantly changes suffix attachment patterns")
        else:
            print("  Adding s does NOT consistently change suffix attachment patterns")


if __name__ == '__main__':
    main()
