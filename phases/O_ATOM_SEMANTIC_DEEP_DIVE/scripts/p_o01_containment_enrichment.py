#!/usr/bin/env python3
"""
P-O1: o-initial CONTAINMENT category enrichment

Test whether o-initial MIDDLEs are enriched in CONTAINMENT category vs baseline.
If o = "vessel", o-initial tokens should preferentially classify as CONTAINMENT.

Tests:
1. Rank all initial atoms by CONTAINMENT fraction.
2. Chi-square: o-initial CONTAINMENT rate vs global CONTAINMENT rate.
3. Full 8-category profile for o-initial.
4. Per-section stability.

Pass criterion: o-initial CONTAINMENT enrichment >= 1.5x, ranked top 3 among initial atoms.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


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
    decoder = BFolioDecoder()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Collect data: (initial_atom, category, section) tuples
    atom_cat_counts = defaultdict(lambda: defaultdict(int))  # atom -> cat -> count
    atom_totals = defaultdict(int)
    global_cat_counts = defaultdict(int)
    global_total = 0

    # Per-section tracking
    atom_section_cat = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # atom -> section -> cat -> count
    atom_section_totals = defaultdict(lambda: defaultdict(int))  # atom -> section -> count

    # Pre-compute folio sections
    folio_sections = {}

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

        initial_atom = m.middle[0]

        # Get section
        folio = token.folio
        if folio not in folio_sections:
            try:
                fa = decoder.analyze_folio(folio)
                folio_sections[folio] = fa.section if fa and fa.section else 'UNK'
            except Exception:
                folio_sections[folio] = 'UNK'
        section = folio_sections[folio]

        atom_cat_counts[initial_atom][cat] += 1
        atom_totals[initial_atom] += 1
        global_cat_counts[cat] += 1
        global_total += 1

        atom_section_cat[initial_atom][section][cat] += 1
        atom_section_totals[initial_atom][section] += 1

    print("=" * 70)
    print("P-O1: o-initial CONTAINMENT category enrichment")
    print("=" * 70)
    print()

    # Global baseline
    global_containment_rate = global_cat_counts['CONTAINMENT'] / global_total if global_total > 0 else 0
    print(f"Global baseline: CONTAINMENT = {global_cat_counts['CONTAINMENT']}/{global_total} "
          f"= {global_containment_rate:.4f} ({global_containment_rate*100:.2f}%)")
    print()

    # ---- TEST 1: Rank all initial atoms by CONTAINMENT fraction ----
    print("-" * 70)
    print("TEST 1: All initial atoms ranked by CONTAINMENT fraction")
    print("-" * 70)

    atom_containment = []
    for atom in sorted(atom_totals.keys()):
        n = atom_totals[atom]
        if n < 20:  # minimum count for meaningful stats
            continue
        cont_n = atom_cat_counts[atom].get('CONTAINMENT', 0)
        frac = cont_n / n
        enrichment = frac / global_containment_rate if global_containment_rate > 0 else 0
        atom_containment.append((atom, frac, cont_n, n, enrichment))

    atom_containment.sort(key=lambda x: -x[1])

    print(f"{'Atom':<6} {'CONTAINMENT%':>13} {'Count':>8} {'Total':>8} {'Enrichment':>11}")
    print("-" * 50)
    o_rank = None
    for rank, (atom, frac, cont_n, n, enrich) in enumerate(atom_containment, 1):
        marker = " <-- o-initial" if atom == 'o' else ""
        print(f"  {atom:<4} {frac*100:>12.2f}% {cont_n:>8} {n:>8} {enrich:>10.3f}x{marker}")
        if atom == 'o':
            o_rank = rank
            o_frac = frac
            o_cont_n = cont_n
            o_total = n
            o_enrichment = enrich

    print()
    if o_rank is not None:
        print(f"  o-initial rank: #{o_rank} of {len(atom_containment)} atoms")
    else:
        print("  WARNING: o-initial not found or too few tokens")

    # ---- TEST 2: Chi-square test ----
    print()
    print("-" * 70)
    print("TEST 2: Chi-square — o-initial CONTAINMENT vs global rate")
    print("-" * 70)

    if o_rank is not None:
        # 2x2 table: o-initial vs rest, CONTAINMENT vs not
        a = o_cont_n  # o-initial AND CONTAINMENT
        b = o_total - o_cont_n  # o-initial AND not CONTAINMENT
        c = global_cat_counts['CONTAINMENT'] - o_cont_n  # not o-initial AND CONTAINMENT
        d = (global_total - o_total) - c  # not o-initial AND not CONTAINMENT
        total = a + b + c + d

        expected_a = (a + b) * (a + c) / total if total > 0 else 0
        expected_b = (a + b) * (b + d) / total if total > 0 else 0
        expected_c = (c + d) * (a + c) / total if total > 0 else 0
        expected_d = (c + d) * (b + d) / total if total > 0 else 0

        chi2 = 0
        for obs, exp in [(a, expected_a), (b, expected_b), (c, expected_c), (d, expected_d)]:
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

        p_val = chi2_1df_p(chi2)

        print(f"  o-initial CONTAINMENT: {a}/{o_total} = {o_frac*100:.2f}%")
        print(f"  Global CONTAINMENT:    {global_cat_counts['CONTAINMENT']}/{global_total} = {global_containment_rate*100:.2f}%")
        print(f"  Enrichment: {o_enrichment:.3f}x")
        print(f"  Chi-square: {chi2:.3f}, p = {p_val:.6f}")
        if p_val < 0.001:
            print(f"  Significance: p < 0.001 ***")
        elif p_val < 0.01:
            print(f"  Significance: p < 0.01 **")
        elif p_val < 0.05:
            print(f"  Significance: p < 0.05 *")
        else:
            print(f"  Significance: not significant")

    # ---- TEST 3: Full 8-category profile for o-initial ----
    print()
    print("-" * 70)
    print("TEST 3: Full 8-category profile for o-initial MIDDLEs")
    print("-" * 70)

    if o_rank is not None:
        print(f"{'Category':<15} {'o-initial%':>11} {'Global%':>9} {'Enrichment':>11} {'Count':>7}")
        print("-" * 55)
        for cat in CATEGORIES:
            o_cat_n = atom_cat_counts['o'].get(cat, 0)
            o_cat_frac = o_cat_n / o_total if o_total > 0 else 0
            global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = o_cat_frac / global_frac if global_frac > 0 else 0
            print(f"  {cat:<13} {o_cat_frac*100:>10.2f}% {global_frac*100:>8.2f}% {enrich:>10.3f}x {o_cat_n:>7}")

    # ---- TEST 4: Per-section stability ----
    print()
    print("-" * 70)
    print("TEST 4: o-initial CONTAINMENT enrichment per section")
    print("-" * 70)

    sections_tested = 0
    sections_enriched = 0

    for section in sorted(atom_section_totals.get('o', {}).keys()):
        o_sec_total = atom_section_totals['o'][section]
        o_sec_cont = atom_section_cat['o'][section].get('CONTAINMENT', 0)
        if o_sec_total < 10:
            continue

        # Global containment rate in this section
        sec_total = sum(atom_section_totals[a][section] for a in atom_section_totals)
        sec_cont = sum(atom_section_cat[a][section].get('CONTAINMENT', 0) for a in atom_section_cat)
        sec_rate = sec_cont / sec_total if sec_total > 0 else 0

        o_rate = o_sec_cont / o_sec_total
        enrich = o_rate / sec_rate if sec_rate > 0 else 0

        sections_tested += 1
        if enrich >= 1.2:
            sections_enriched += 1

        print(f"  Section {section:>6}: o-initial {o_sec_cont}/{o_sec_total} = {o_rate*100:.1f}%, "
              f"section baseline {sec_rate*100:.1f}%, enrichment {enrich:.3f}x")

    print()
    print(f"  Sections with enrichment >= 1.2x: {sections_enriched}/{sections_tested}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O1 o-initial CONTAINMENT enrichment")
    print("=" * 70)

    pass_enrichment = o_enrichment >= 1.5 if o_rank is not None else False
    pass_rank = o_rank is not None and o_rank <= 3
    pass_chi2 = p_val < 0.01 if o_rank is not None else False
    pass_section = sections_enriched >= (sections_tested * 0.5) if sections_tested > 0 else False

    results = [
        ("CONTAINMENT enrichment >= 1.5x", pass_enrichment,
         f"{o_enrichment:.3f}x" if o_rank else "N/A"),
        ("Ranked top 3 among initial atoms", pass_rank,
         f"rank #{o_rank}" if o_rank else "N/A"),
        ("Chi-square p < 0.01", pass_chi2,
         f"p = {p_val:.6f}" if o_rank else "N/A"),
        ("Section stability (>= 50% sections enriched)", pass_section,
         f"{sections_enriched}/{sections_tested}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_enrichment and pass_rank
    print()
    print(f"  PRIMARY CRITERION (enrichment >= 1.5x AND rank top 3): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
