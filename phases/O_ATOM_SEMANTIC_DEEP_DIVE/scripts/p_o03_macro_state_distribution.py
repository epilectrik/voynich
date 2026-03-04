#!/usr/bin/env python3
"""
P-O3: o-initial macro-state distribution — anti-AXM, pro-FQ

Test whether o-initial tokens are depleted at AXM and enriched at FQ.
If o = "vessel", vessel management happens between heating cycles (FQ = routine/checkout),
not during sustained heating (AXM).

Tests:
1. For each initial atom, compute macro-state distribution.
2. Rank all initial atoms by AXM fraction (o should be low) and FQ fraction (o should be high).
3. Chi-square: o-initial AXM rate vs global; o-initial FQ rate vs global.
4. Explicit k vs o comparison.
5. Per-section stability.

Pass criterion: o-initial AXM enrichment < 0.85x AND FQ enrichment > 1.2x (both p < 0.01).
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

    MACRO_STATES = ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']

    # Collect data
    atom_state_counts = defaultdict(lambda: defaultdict(int))  # atom -> state -> count
    atom_totals = defaultdict(int)
    global_state_counts = defaultdict(int)
    global_total = 0

    # Per-section
    atom_section_state = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    atom_section_totals = defaultdict(lambda: defaultdict(int))

    folio_sections = {}

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        ta = decoder.analyze_token(w)
        if ta is None or ta.macro_state is None:
            continue

        state = ta.macro_state
        initial = m.middle[0]

        # Get section
        folio = token.folio
        if folio not in folio_sections:
            try:
                fa = decoder.analyze_folio(folio)
                folio_sections[folio] = fa.section if fa and fa.section else 'UNK'
            except Exception:
                folio_sections[folio] = 'UNK'
        section = folio_sections[folio]

        atom_state_counts[initial][state] += 1
        atom_totals[initial] += 1
        global_state_counts[state] += 1
        global_total += 1

        atom_section_state[initial][section][state] += 1
        atom_section_totals[initial][section] += 1

    print("=" * 70)
    print("P-O3: o-initial macro-state distribution")
    print("=" * 70)
    print()

    # Global baselines
    print("Global macro-state distribution:")
    for st in MACRO_STATES:
        n = global_state_counts[st]
        frac = n / global_total if global_total > 0 else 0
        print(f"  {st:<10} {n:>7} ({frac*100:.2f}%)")
    print(f"  Total classified: {global_total}")
    print()

    global_axm_rate = global_state_counts['AXM'] / global_total if global_total > 0 else 0
    global_fq_rate = global_state_counts['FQ'] / global_total if global_total > 0 else 0

    # ---- TEST 1: Per-atom macro-state distributions ----
    print("-" * 70)
    print("TEST 1: Per-initial-atom macro-state distribution")
    print("-" * 70)
    print()

    # Filter atoms with enough data
    valid_atoms = [a for a in sorted(atom_totals.keys()) if atom_totals[a] >= 20]

    # Header
    header = f"{'Atom':<6} {'N':>6}"
    for st in MACRO_STATES:
        header += f" {st:>8}"
    print(header)
    print("-" * (14 + 9 * len(MACRO_STATES)))

    for atom in valid_atoms:
        n = atom_totals[atom]
        row = f"  {atom:<4} {n:>6}"
        for st in MACRO_STATES:
            frac = atom_state_counts[atom].get(st, 0) / n * 100
            row += f" {frac:>7.1f}%"
        marker = " <--" if atom == 'o' else ""
        print(row + marker)
    print()

    # ---- TEST 2: Rankings ----
    print("-" * 70)
    print("TEST 2: Atom rankings by AXM fraction (ascending) and FQ fraction (descending)")
    print("-" * 70)
    print()

    # AXM ranking (ascending = least AXM first = most depleted)
    axm_ranked = [(a, atom_state_counts[a].get('AXM', 0) / atom_totals[a])
                  for a in valid_atoms]
    axm_ranked.sort(key=lambda x: x[1])

    print("  AXM fraction (ascending — o should be low):")
    o_axm_rank = None
    for rank, (atom, frac) in enumerate(axm_ranked, 1):
        enrich = frac / global_axm_rate if global_axm_rate > 0 else 0
        marker = " <-- o-initial" if atom == 'o' else ""
        print(f"    #{rank:>2} {atom}: {frac*100:.1f}% (enrichment {enrich:.3f}x){marker}")
        if atom == 'o':
            o_axm_rank = rank
            o_axm_frac = frac
            o_axm_enrich = enrich
    print()

    # FQ ranking (descending = most FQ first)
    fq_ranked = [(a, atom_state_counts[a].get('FQ', 0) / atom_totals[a])
                 for a in valid_atoms]
    fq_ranked.sort(key=lambda x: -x[1])

    print("  FQ fraction (descending — o should be high):")
    o_fq_rank = None
    for rank, (atom, frac) in enumerate(fq_ranked, 1):
        enrich = frac / global_fq_rate if global_fq_rate > 0 else 0
        marker = " <-- o-initial" if atom == 'o' else ""
        print(f"    #{rank:>2} {atom}: {frac*100:.1f}% (enrichment {enrich:.3f}x){marker}")
        if atom == 'o':
            o_fq_rank = rank
            o_fq_frac = frac
            o_fq_enrich = enrich
    print()

    # ---- TEST 3: Chi-square tests ----
    print("-" * 70)
    print("TEST 3: Chi-square tests — o-initial AXM and FQ vs global rates")
    print("-" * 70)
    print()

    o_n = atom_totals.get('o', 0)
    o_axm_n = atom_state_counts['o'].get('AXM', 0)
    o_fq_n = atom_state_counts['o'].get('FQ', 0)

    # AXM chi-square
    a = o_axm_n
    b = o_n - o_axm_n
    c = global_state_counts['AXM'] - o_axm_n
    d = (global_total - o_n) - c
    total_all = a + b + c + d
    if total_all > 0:
        ea = (a + b) * (a + c) / total_all
        eb = (a + b) * (b + d) / total_all
        ec = (c + d) * (a + c) / total_all
        ed = (c + d) * (b + d) / total_all
        chi2_axm = sum((obs - exp) ** 2 / exp for obs, exp in [(a, ea), (b, eb), (c, ec), (d, ed)] if exp > 0)
        p_axm = chi2_1df_p(chi2_axm)
    else:
        chi2_axm, p_axm = 0, 1.0

    print(f"  AXM: o-initial = {o_axm_n}/{o_n} ({o_axm_frac*100:.1f}%), "
          f"global = {global_axm_rate*100:.1f}%, enrichment = {o_axm_enrich:.3f}x")
    print(f"    Chi-square = {chi2_axm:.3f}, p = {p_axm:.6f}")
    print()

    # FQ chi-square
    a = o_fq_n
    b = o_n - o_fq_n
    c = global_state_counts['FQ'] - o_fq_n
    d = (global_total - o_n) - c
    total_all = a + b + c + d
    if total_all > 0:
        ea = (a + b) * (a + c) / total_all
        eb = (a + b) * (b + d) / total_all
        ec = (c + d) * (a + c) / total_all
        ed = (c + d) * (b + d) / total_all
        chi2_fq = sum((obs - exp) ** 2 / exp for obs, exp in [(a, ea), (b, eb), (c, ec), (d, ed)] if exp > 0)
        p_fq = chi2_1df_p(chi2_fq)
    else:
        chi2_fq, p_fq = 0, 1.0

    print(f"  FQ: o-initial = {o_fq_n}/{o_n} ({o_fq_frac*100:.1f}%), "
          f"global = {global_fq_rate*100:.1f}%, enrichment = {o_fq_enrich:.3f}x")
    print(f"    Chi-square = {chi2_fq:.3f}, p = {p_fq:.6f}")
    print()

    # ---- TEST 4: k vs o comparison ----
    print("-" * 70)
    print("TEST 4: Explicit k vs o comparison (expected approximately inverse)")
    print("-" * 70)
    print()

    k_n = atom_totals.get('k', 0)
    if k_n > 0 and o_n > 0:
        print(f"  {'State':<10} {'k-initial':>12} {'o-initial':>12} {'k/o ratio':>10}")
        print("  " + "-" * 46)
        for st in MACRO_STATES:
            k_frac = atom_state_counts['k'].get(st, 0) / k_n
            o_frac_st = atom_state_counts['o'].get(st, 0) / o_n
            ratio = k_frac / o_frac_st if o_frac_st > 0 else float('inf') if k_frac > 0 else 1.0
            ratio_str = f"{ratio:.3f}x" if ratio != float('inf') else "inf"
            print(f"  {st:<10} {k_frac*100:>11.1f}% {o_frac_st*100:>11.1f}% {ratio_str:>10}")

        # Compute inverseness metric: correlation of their state profiles
        k_profile = [atom_state_counts['k'].get(st, 0) / k_n for st in MACRO_STATES]
        o_profile = [atom_state_counts['o'].get(st, 0) / o_n for st in MACRO_STATES]
        # Pearson correlation
        k_mean = sum(k_profile) / len(k_profile)
        o_mean = sum(o_profile) / len(o_profile)
        cov = sum((k_profile[i] - k_mean) * (o_profile[i] - o_mean) for i in range(len(MACRO_STATES)))
        k_std = math.sqrt(sum((v - k_mean) ** 2 for v in k_profile))
        o_std = math.sqrt(sum((v - o_mean) ** 2 for v in o_profile))
        pearson_r = cov / (k_std * o_std) if k_std > 0 and o_std > 0 else 0
        print(f"\n  k-o profile Pearson r = {pearson_r:.4f} (negative = inverse)")
    else:
        print("  Insufficient data for k or o atoms")
    print()

    # ---- TEST 5: Per-section stability ----
    print("-" * 70)
    print("TEST 5: Per-section stability of o-initial AXM depletion and FQ enrichment")
    print("-" * 70)
    print()

    sections_axm_depleted = 0
    sections_fq_enriched = 0
    sections_tested = 0

    for section in sorted(atom_section_totals.get('o', {}).keys()):
        o_sec_total = atom_section_totals['o'][section]
        if o_sec_total < 10:
            continue

        # Section-level global rates
        sec_total = sum(atom_section_totals[a][section] for a in atom_section_totals)
        sec_axm = sum(atom_section_state[a][section].get('AXM', 0) for a in atom_section_state)
        sec_fq = sum(atom_section_state[a][section].get('FQ', 0) for a in atom_section_state)
        sec_axm_rate = sec_axm / sec_total if sec_total > 0 else 0
        sec_fq_rate = sec_fq / sec_total if sec_total > 0 else 0

        o_sec_axm = atom_section_state['o'][section].get('AXM', 0)
        o_sec_fq = atom_section_state['o'][section].get('FQ', 0)
        o_axm_r = o_sec_axm / o_sec_total
        o_fq_r = o_sec_fq / o_sec_total
        axm_enr = o_axm_r / sec_axm_rate if sec_axm_rate > 0 else 0
        fq_enr = o_fq_r / sec_fq_rate if sec_fq_rate > 0 else 0

        sections_tested += 1
        if axm_enr < 0.90:
            sections_axm_depleted += 1
        if fq_enr > 1.1:
            sections_fq_enriched += 1

        print(f"  Section {section:>6} (N={o_sec_total}): "
              f"AXM {o_axm_r*100:.1f}% vs {sec_axm_rate*100:.1f}% ({axm_enr:.3f}x), "
              f"FQ {o_fq_r*100:.1f}% vs {sec_fq_rate*100:.1f}% ({fq_enr:.3f}x)")

    print()
    print(f"  Sections with AXM depletion (<0.90x): {sections_axm_depleted}/{sections_tested}")
    print(f"  Sections with FQ enrichment (>1.10x): {sections_fq_enriched}/{sections_tested}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O3 o-initial macro-state distribution")
    print("=" * 70)

    pass_axm = o_axm_enrich < 0.85 if o_n > 0 else False
    pass_fq = o_fq_enrich > 1.2 if o_n > 0 else False
    pass_axm_p = p_axm < 0.01
    pass_fq_p = p_fq < 0.01
    pass_section = (sections_axm_depleted >= sections_tested * 0.5 and
                    sections_fq_enriched >= sections_tested * 0.5) if sections_tested > 0 else False

    results = [
        ("AXM enrichment < 0.85x", pass_axm,
         f"{o_axm_enrich:.3f}x (rank #{o_axm_rank}/{len(valid_atoms)})" if o_n > 0 else "N/A"),
        ("FQ enrichment > 1.2x", pass_fq,
         f"{o_fq_enrich:.3f}x (rank #{o_fq_rank}/{len(valid_atoms)})" if o_n > 0 else "N/A"),
        ("AXM chi-square p < 0.01", pass_axm_p,
         f"p = {p_axm:.6f}"),
        ("FQ chi-square p < 0.01", pass_fq_p,
         f"p = {p_fq:.6f}"),
        ("Section stability (>= 50%)", pass_section,
         f"AXM: {sections_axm_depleted}/{sections_tested}, FQ: {sections_fq_enriched}/{sections_tested}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_axm and pass_fq and pass_axm_p and pass_fq_p
    print()
    print(f"  PRIMARY CRITERION (AXM < 0.85x AND FQ > 1.2x, both p < 0.01): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
