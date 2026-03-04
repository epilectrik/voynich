#!/usr/bin/env python3
"""
P-O13: o-initial STAGING category enrichment (ordnen hypothesis)

If o = "ordnen" (arrange/prepare), o-initial MIDDLEs should be strongly enriched
in STAGING (preparatory operations) and depleted in THERMAL (not about heat).

Tests:
1. Rank all initial atoms by STAGING enrichment
2. Show o's full 8-category profile
3. Per-section stability check (5 sections)
4. Chi-square significance for STAGING enrichment
5. Anti-THERMAL check

Pass: STAGING >= 2.0x AND THERMAL <= 0.20x AND o in top 2 for STAGING
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
    atom_cat_counts = defaultdict(lambda: defaultdict(int))
    atom_totals = defaultdict(int)
    global_cat_counts = defaultdict(int)
    global_total = 0

    # Per-section tracking
    atom_section_cat = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    atom_section_totals = defaultdict(lambda: defaultdict(int))

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
    print("P-O13: o-initial STAGING category enrichment (ordnen hypothesis)")
    print("=" * 70)
    print()

    # Global baselines
    global_staging_rate = global_cat_counts['STAGING'] / global_total if global_total > 0 else 0
    global_thermal_rate = global_cat_counts['THERMAL'] / global_total if global_total > 0 else 0
    print(f"Global baseline: STAGING = {global_cat_counts['STAGING']}/{global_total} "
          f"= {global_staging_rate*100:.2f}%")
    print(f"Global baseline: THERMAL = {global_cat_counts['THERMAL']}/{global_total} "
          f"= {global_thermal_rate*100:.2f}%")
    print()

    # ---- TEST 1: Rank all initial atoms by STAGING fraction ----
    print("-" * 70)
    print("TEST 1: All initial atoms ranked by STAGING enrichment")
    print("-" * 70)

    atom_staging = []
    for atom in sorted(atom_totals.keys()):
        n = atom_totals[atom]
        if n < 20:
            continue
        stg_n = atom_cat_counts[atom].get('STAGING', 0)
        frac = stg_n / n
        enrichment = frac / global_staging_rate if global_staging_rate > 0 else 0
        atom_staging.append((atom, frac, stg_n, n, enrichment))

    atom_staging.sort(key=lambda x: -x[4])

    print(f"{'Rank':<6} {'Atom':<6} {'STAGING%':>10} {'Count':>8} {'Total':>8} {'Enrichment':>11}")
    print("-" * 55)
    o_rank = None
    o_frac = 0
    o_stg_n = 0
    o_total = 0
    o_enrichment = 0
    for rank, (atom, frac, stg_n, n, enrich) in enumerate(atom_staging, 1):
        marker = " <-- o-initial" if atom == 'o' else ""
        print(f"  {rank:<4} {atom:<4} {frac*100:>9.2f}% {stg_n:>8} {n:>8} {enrich:>10.3f}x{marker}")
        if atom == 'o':
            o_rank = rank
            o_frac = frac
            o_stg_n = stg_n
            o_total = n
            o_enrichment = enrich

    print()
    if o_rank is not None:
        print(f"  o-initial STAGING rank: #{o_rank} of {len(atom_staging)} atoms")
    else:
        print("  WARNING: o-initial not found or too few tokens")

    # ---- TEST 2: Full 8-category profile for o-initial ----
    print()
    print("-" * 70)
    print("TEST 2: Full 8-category profile for o-initial MIDDLEs")
    print("-" * 70)

    o_thermal_enrichment = 0
    if o_rank is not None:
        print(f"{'Category':<15} {'o-initial%':>11} {'Global%':>9} {'Enrichment':>11} {'Count':>7}")
        print("-" * 55)
        for cat in CATEGORIES:
            o_cat_n = atom_cat_counts['o'].get(cat, 0)
            o_cat_frac = o_cat_n / o_total if o_total > 0 else 0
            global_frac = global_cat_counts[cat] / global_total if global_total > 0 else 0
            enrich = o_cat_frac / global_frac if global_frac > 0 else 0
            marker = ""
            if cat == 'STAGING':
                marker = " <-- PRIMARY"
            elif cat == 'THERMAL':
                marker = " <-- ANTI-THERMAL"
                o_thermal_enrichment = enrich
            print(f"  {cat:<13} {o_cat_frac*100:>10.2f}% {global_frac*100:>8.2f}% {enrich:>10.3f}x {o_cat_n:>7}{marker}")

    # ---- TEST 3: Chi-square for STAGING enrichment ----
    print()
    print("-" * 70)
    print("TEST 3: Chi-square — o-initial STAGING vs global rate")
    print("-" * 70)

    chi2_p = 1.0
    if o_rank is not None:
        a = o_stg_n
        b = o_total - o_stg_n
        c = global_cat_counts['STAGING'] - o_stg_n
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

        print(f"  o-initial STAGING: {a}/{o_total} = {o_frac*100:.2f}%")
        print(f"  Global STAGING:    {global_cat_counts['STAGING']}/{global_total} = {global_staging_rate*100:.2f}%")
        print(f"  Enrichment: {o_enrichment:.3f}x")
        print(f"  Chi-square: {chi2:.3f}, p = {chi2_p:.6f}")
        if chi2_p < 0.001:
            print(f"  Significance: p < 0.001 ***")
        elif chi2_p < 0.01:
            print(f"  Significance: p < 0.01 **")
        elif chi2_p < 0.05:
            print(f"  Significance: p < 0.05 *")
        else:
            print(f"  Significance: not significant")

    # ---- TEST 4: Per-section stability ----
    print()
    print("-" * 70)
    print("TEST 4: o-initial STAGING enrichment per section")
    print("-" * 70)

    sections_tested = 0
    sections_enriched = 0

    for section in sorted(atom_section_totals.get('o', {}).keys()):
        o_sec_total = atom_section_totals['o'][section]
        o_sec_stg = atom_section_cat['o'][section].get('STAGING', 0)
        if o_sec_total < 10:
            continue

        # Section baseline
        sec_total = sum(atom_section_totals[a][section] for a in atom_section_totals)
        sec_stg = sum(atom_section_cat[a][section].get('STAGING', 0) for a in atom_section_cat)
        sec_rate = sec_stg / sec_total if sec_total > 0 else 0

        o_rate = o_sec_stg / o_sec_total
        enrich = o_rate / sec_rate if sec_rate > 0 else 0

        sections_tested += 1
        if enrich >= 1.5:
            sections_enriched += 1

        print(f"  Section {section:>8}: o-initial {o_sec_stg}/{o_sec_total} = {o_rate*100:.1f}%, "
              f"section baseline {sec_rate*100:.1f}%, enrichment {enrich:.3f}x "
              f"{'ENRICHED' if enrich >= 1.5 else ''}")

    print()
    print(f"  Sections with STAGING enrichment >= 1.5x: {sections_enriched}/{sections_tested}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O13 o-initial STAGING enrichment (ordnen)")
    print("=" * 70)

    pass_staging = o_enrichment >= 2.0 if o_rank is not None else False
    pass_thermal = o_thermal_enrichment <= 0.20 if o_rank is not None else False
    pass_rank = o_rank is not None and o_rank <= 2
    pass_chi2 = chi2_p < 0.01 if o_rank is not None else False
    pass_section = sections_enriched >= max(1, sections_tested // 2) if sections_tested > 0 else False

    results = [
        ("STAGING enrichment >= 2.0x", pass_staging,
         f"{o_enrichment:.3f}x" if o_rank else "N/A"),
        ("THERMAL depletion <= 0.20x", pass_thermal,
         f"{o_thermal_enrichment:.3f}x" if o_rank else "N/A"),
        ("Ranked top 2 for STAGING", pass_rank,
         f"rank #{o_rank}" if o_rank else "N/A"),
        ("Chi-square p < 0.01", pass_chi2,
         f"p = {chi2_p:.6f}" if o_rank else "N/A"),
        ("Section stability (>= 50% enriched)", pass_section,
         f"{sections_enriched}/{sections_tested}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_staging and pass_thermal and pass_rank
    print()
    print(f"  PRIMARY CRITERION (STAGING>=2.0x AND THERMAL<=0.20x AND rank top 2): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
