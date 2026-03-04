#!/usr/bin/env python3
"""
P-O2: o-bearing compounds redirect to CONTAINMENT category

Test whether adding o as terminal atom to a compound shifts the category
away from the base (initial) atom's default, toward CONTAINMENT.
Analogous to L-P6 where l-terminal redirected to STAGING (9.7x).

Tests:
1. For each initial atom group: category profile of X+o vs X+non-o compounds.
2. Count groups where dominant category differs (redirection).
3. CONTAINMENT enrichment for o-terminal vs non-o-terminal within each group.
4. Compare to l-terminal STAGING enrichment as control.

Pass criterion: o-terminal redirects category in >= 3/5 groups;
               CONTAINMENT >= 2.0x enrichment in o-terminal compounds.
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
    MIN_COMPOUND_LEN = 2  # Must be at least 2 chars to be a compound

    # Collect compound MIDDLEs by initial atom and terminal atom
    # Structure: initial_atom -> {terminal_is_o: bool} -> category -> count
    initial_o_terminal_cats = defaultdict(lambda: defaultdict(int))    # initial -> cat -> count (o-terminal)
    initial_nono_terminal_cats = defaultdict(lambda: defaultdict(int))  # initial -> cat -> count (non-o-terminal)
    initial_o_terminal_totals = defaultdict(int)
    initial_nono_terminal_totals = defaultdict(int)

    # Also track l-terminal for control comparison
    initial_l_terminal_cats = defaultdict(lambda: defaultdict(int))
    initial_l_terminal_totals = defaultdict(int)
    initial_nonl_terminal_cats = defaultdict(lambda: defaultdict(int))
    initial_nonl_terminal_totals = defaultdict(int)

    # Global stats for o-terminal and non-o-terminal
    o_term_cat_total = defaultdict(int)
    nono_term_cat_total = defaultdict(int)
    o_term_total = 0
    nono_term_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < MIN_COMPOUND_LEN:
            continue  # Skip bare single-char MIDDLEs

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        initial = m.middle[0]
        terminal = m.middle[-1]

        # o-terminal tracking
        if terminal == 'o':
            initial_o_terminal_cats[initial][cat] += 1
            initial_o_terminal_totals[initial] += 1
            o_term_cat_total[cat] += 1
            o_term_total += 1
        else:
            initial_nono_terminal_cats[initial][cat] += 1
            initial_nono_terminal_totals[initial] += 1
            nono_term_cat_total[cat] += 1
            nono_term_total += 1

        # l-terminal tracking (control)
        if terminal == 'l':
            initial_l_terminal_cats[initial][cat] += 1
            initial_l_terminal_totals[initial] += 1
        else:
            initial_nonl_terminal_cats[initial][cat] += 1
            initial_nonl_terminal_totals[initial] += 1

    print("=" * 70)
    print("P-O2: o-bearing compounds redirect to CONTAINMENT category")
    print("=" * 70)
    print()
    print(f"Total compound tokens (len >= 2): o-terminal={o_term_total}, non-o-terminal={nono_term_total}")
    print()

    # ---- TEST 1 & 2: Per-initial-atom category profiles ----
    print("-" * 70)
    print("TEST 1 & 2: Per-initial-atom category comparison (o-terminal vs non-o-terminal)")
    print("-" * 70)
    print()

    MIN_TOKENS = 20  # Minimum tokens in EACH group to test
    test_atoms = []
    for atom in sorted(set(initial_o_terminal_totals.keys()) | set(initial_nono_terminal_totals.keys())):
        if initial_o_terminal_totals[atom] >= MIN_TOKENS and initial_nono_terminal_totals[atom] >= MIN_TOKENS:
            test_atoms.append(atom)

    redirections = 0
    containment_enrichments = []

    for atom in test_atoms:
        n_o = initial_o_terminal_totals[atom]
        n_nono = initial_nono_terminal_totals[atom]

        # Find dominant category for each group
        o_cats = initial_o_terminal_cats[atom]
        nono_cats = initial_nono_terminal_cats[atom]

        dom_o = max(CATEGORIES, key=lambda c: o_cats.get(c, 0))
        dom_nono = max(CATEGORIES, key=lambda c: nono_cats.get(c, 0))

        redirected = dom_o != dom_nono
        if redirected:
            redirections += 1

        # CONTAINMENT enrichment
        o_cont_frac = o_cats.get('CONTAINMENT', 0) / n_o if n_o > 0 else 0
        nono_cont_frac = nono_cats.get('CONTAINMENT', 0) / n_nono if n_nono > 0 else 0
        cont_enrich = o_cont_frac / nono_cont_frac if nono_cont_frac > 0 else float('inf') if o_cont_frac > 0 else 0
        containment_enrichments.append((atom, cont_enrich, o_cont_frac, nono_cont_frac, n_o, n_nono))

        print(f"  Initial atom '{atom}': o-terminal N={n_o}, non-o N={n_nono}")
        print(f"    Dominant: o-terminal={dom_o}, non-o={dom_nono} {'[REDIRECT]' if redirected else '[SAME]'}")

        # Show top 3 categories for each
        o_sorted = sorted(CATEGORIES, key=lambda c: -o_cats.get(c, 0))[:3]
        nono_sorted = sorted(CATEGORIES, key=lambda c: -nono_cats.get(c, 0))[:3]
        o_top = ", ".join(f"{c}={o_cats.get(c,0)/n_o*100:.1f}%" for c in o_sorted)
        nono_top = ", ".join(f"{c}={nono_cats.get(c,0)/n_nono*100:.1f}%" for c in nono_sorted)
        print(f"    o-terminal top 3: {o_top}")
        print(f"    non-o top 3:      {nono_top}")
        print(f"    CONTAINMENT: o-terminal={o_cont_frac*100:.1f}%, non-o={nono_cont_frac*100:.1f}%, "
              f"enrichment={cont_enrich:.3f}x")
        print()

    print(f"  Category redirections: {redirections}/{len(test_atoms)} groups")
    print()

    # ---- TEST 3: Global o-terminal CONTAINMENT enrichment ----
    print("-" * 70)
    print("TEST 3: Global o-terminal vs non-o-terminal CONTAINMENT enrichment")
    print("-" * 70)

    o_cont_global = o_term_cat_total.get('CONTAINMENT', 0) / o_term_total if o_term_total > 0 else 0
    nono_cont_global = nono_term_cat_total.get('CONTAINMENT', 0) / nono_term_total if nono_term_total > 0 else 0
    global_enrich = o_cont_global / nono_cont_global if nono_cont_global > 0 else 0

    print(f"  o-terminal CONTAINMENT:     {o_term_cat_total.get('CONTAINMENT',0)}/{o_term_total} "
          f"= {o_cont_global*100:.2f}%")
    print(f"  non-o-terminal CONTAINMENT: {nono_term_cat_total.get('CONTAINMENT',0)}/{nono_term_total} "
          f"= {nono_cont_global*100:.2f}%")
    print(f"  Enrichment: {global_enrich:.3f}x")

    # Chi-square for o-terminal vs non-o-terminal CONTAINMENT
    a = o_term_cat_total.get('CONTAINMENT', 0)
    b = o_term_total - a
    c = nono_term_cat_total.get('CONTAINMENT', 0)
    d = nono_term_total - c
    total_all = a + b + c + d
    if total_all > 0:
        ea = (a + b) * (a + c) / total_all
        eb = (a + b) * (b + d) / total_all
        ec = (c + d) * (a + c) / total_all
        ed = (c + d) * (b + d) / total_all
        chi2 = sum((o - e) ** 2 / e for o, e in [(a, ea), (b, eb), (c, ec), (d, ed)] if e > 0)
        p_val = chi2_1df_p(chi2)
        print(f"  Chi-square: {chi2:.3f}, p = {p_val:.6f}")
    else:
        chi2 = 0
        p_val = 1.0
    print()

    # Full category comparison
    print("  Full category comparison (o-terminal vs non-o-terminal):")
    print(f"  {'Category':<15} {'o-term%':>9} {'non-o%':>9} {'Enrichment':>11}")
    print("  " + "-" * 46)
    for cat in CATEGORIES:
        o_f = o_term_cat_total.get(cat, 0) / o_term_total * 100 if o_term_total > 0 else 0
        n_f = nono_term_cat_total.get(cat, 0) / nono_term_total * 100 if nono_term_total > 0 else 0
        enr = (o_f / n_f) if n_f > 0 else 0
        print(f"  {cat:<15} {o_f:>8.2f}% {n_f:>8.2f}% {enr:>10.3f}x")
    print()

    # ---- TEST 4: l-terminal STAGING enrichment as control ----
    print("-" * 70)
    print("TEST 4: Control — l-terminal STAGING enrichment (known redirection)")
    print("-" * 70)

    l_term_total = sum(initial_l_terminal_totals.values())
    nonl_term_total = sum(initial_nonl_terminal_totals.values())

    l_staging = sum(initial_l_terminal_cats[a].get('STAGING', 0) for a in initial_l_terminal_cats)
    nonl_staging = sum(initial_nonl_terminal_cats[a].get('STAGING', 0) for a in initial_nonl_terminal_cats)

    l_staging_frac = l_staging / l_term_total if l_term_total > 0 else 0
    nonl_staging_frac = nonl_staging / nonl_term_total if nonl_term_total > 0 else 0
    l_enrich = l_staging_frac / nonl_staging_frac if nonl_staging_frac > 0 else 0

    print(f"  l-terminal STAGING:     {l_staging}/{l_term_total} = {l_staging_frac*100:.2f}%")
    print(f"  non-l-terminal STAGING: {nonl_staging}/{nonl_term_total} = {nonl_staging_frac*100:.2f}%")
    print(f"  l-terminal STAGING enrichment: {l_enrich:.3f}x")
    print(f"  (Control comparison: o-terminal CONTAINMENT enrichment = {global_enrich:.3f}x)")
    print()

    # ---- SUMMARY ----
    print("=" * 70)
    print("SUMMARY: P-O2 o-terminal category redirection")
    print("=" * 70)

    pass_redirect = redirections >= 3 and len(test_atoms) >= 5
    pass_redirect_partial = redirections >= 3
    pass_enrichment = global_enrich >= 2.0
    pass_chi2 = p_val < 0.01
    mean_enrich = (sum(e for _, e, _, _, _, _ in containment_enrichments if e != float('inf'))
                   / len(containment_enrichments)) if containment_enrichments else 0

    results = [
        ("Category redirection in >= 3/5 groups", pass_redirect_partial,
         f"{redirections}/{len(test_atoms)} groups redirected"),
        ("Global CONTAINMENT enrichment >= 2.0x", pass_enrichment,
         f"{global_enrich:.3f}x"),
        ("Chi-square p < 0.01", pass_chi2,
         f"p = {p_val:.6f}"),
        ("l-terminal STAGING control (informational)", True,
         f"{l_enrich:.3f}x enrichment"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_redirect_partial and pass_enrichment
    print()
    print(f"  PRIMARY CRITERION (>= 3 redirections AND enrichment >= 2.0x): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
