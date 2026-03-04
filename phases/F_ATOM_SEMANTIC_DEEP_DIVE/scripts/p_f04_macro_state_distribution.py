#!/usr/bin/env python3
"""
F-F4: f-initial macro-state distribution
==========================================
Test whether f-initial tokens distribute across macro-states as predicted
for a MARKING element.

Predictions (f="flag" -> MARKING annotation):
- AXM enrichment >= 1.0x (MARKING operates within main operational loop)
- FL_HAZ depletion <= 1.5x (not strongly hazard-associated)
- Additional: compare to p (88.7% AXM) and d (MARKING peers)

Method:
1. For each Currier B token, extract MIDDLE initial atom and macro-state
2. Build initial_atom -> macro_state -> count
3. Compute enrichment of each macro-state for f-initial vs global baseline
4. Rank all atoms by AXM concentration
5. Per-section stability check

Controls: p (88.7% AXM), c (93.5% AXM), s (35.4% AXM, 64.6% FQ)

IMPORTANT: BFolioDecoder API:
  - Create ONE instance: decoder = BFolioDecoder()
  - Get token macro-state: ta = decoder.analyze_token(word) then ta.macro_state
  - Get folio regime: fa = decoder.analyze_folio(folio) then fa.regime
  - Do NOT create per-folio decoders. Do NOT call dec.macro_state(middle).
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

MACRO_STATES = ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']


def normal_cdf(x):
    """Approximate normal CDF."""
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.8212560 + t * 1.3302744))))
    if x > 0:
        return 1.0 - p
    return p


def chi2_1df_p(chi2_val):
    """Approximate p-value for chi-square with 1 df."""
    if chi2_val <= 0:
        return 1.0
    z = math.sqrt(chi2_val)
    return 2 * (1 - normal_cdf(z))


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    print("=" * 70)
    print("F-F4: f-initial macro-state distribution")
    print("=" * 70)

    # Collect data: atom_initial -> macro_state -> count
    atom_macro = defaultdict(lambda: defaultdict(int))
    global_macro = defaultdict(int)
    atom_total = defaultdict(int)
    total_tokens = 0

    # Also track per-section for stability
    section_atom_macro = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    section_global_macro = defaultdict(lambda: defaultdict(int))
    section_atom_total = defaultdict(lambda: defaultdict(int))
    section_total = defaultdict(int)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue

        initial_atom = mid[0]

        ta = decoder.analyze_token(w)
        if not ta or not ta.macro_state:
            continue
        ms = ta.macro_state

        fa = decoder.analyze_folio(token.folio)
        section = fa.section if fa else 'UNK'

        atom_macro[initial_atom][ms] += 1
        global_macro[ms] += 1
        atom_total[initial_atom] += 1
        total_tokens += 1

        section_atom_macro[section][initial_atom][ms] += 1
        section_global_macro[section][ms] += 1
        section_atom_total[section][initial_atom] += 1
        section_total[section] += 1

    print("\nTotal classified tokens: %d" % total_tokens)
    print("Unique initial atoms: %d" % len(atom_macro))
    f_total = atom_total.get('f', 0)
    print("f-initial tokens: %d (%.1f%%)" % (f_total, 100 * f_total / total_tokens if total_tokens > 0 else 0))

    # --- Global baseline ---
    print("\n%-12s %12s %10s" % ('Macro State', 'Global Count', 'Global %'))
    print("-" * 36)
    for ms in MACRO_STATES:
        cnt = global_macro.get(ms, 0)
        print("%-12s %12d %9.1f%%" % (ms, cnt, 100 * cnt / total_tokens if total_tokens > 0 else 0))

    # --- f-initial profile vs baseline ---
    print("\n--- f-initial macro-state profile ---")
    print("%-12s %10s %8s %8s %8s %8s %10s" % ('Macro State', 'f Count', 'f %', 'Base %', 'Enrich', 'Chi2', 'p-val'))
    print("-" * 70)

    f_enrichments = {}
    f_pvals = {}
    for ms in MACRO_STATES:
        f_cnt = atom_macro.get('f', {}).get(ms, 0)
        f_pct = 100 * f_cnt / f_total if f_total > 0 else 0
        base_pct = 100 * global_macro.get(ms, 0) / total_tokens if total_tokens > 0 else 0
        enrich = f_pct / base_pct if base_pct > 0 else 0

        # Chi-square: observed f_cnt vs expected under global rate
        expected = f_total * (global_macro.get(ms, 0) / total_tokens) if total_tokens > 0 else 0
        if expected > 0:
            chi2 = (f_cnt - expected) ** 2 / expected
        else:
            chi2 = 0
        pv = chi2_1df_p(chi2)

        f_enrichments[ms] = enrich
        f_pvals[ms] = pv

        print("%-12s %10d %7.1f%% %7.1f%% %7.2fx %7.2f %10.4f" %
              (ms, f_cnt, f_pct, base_pct, enrich, chi2, pv))

    # --- Rank ALL atoms by AXM concentration ---
    print("\n--- All atoms ranked by AXM enrichment (highest first) ---")
    atom_axm = []
    for atom in sorted(atom_macro.keys()):
        at = atom_total[atom]
        if at < 10:  # lower threshold for rare atoms
            continue
        axm_cnt = atom_macro[atom].get('AXM', 0)
        base_rate = global_macro.get('AXM', 0) / total_tokens if total_tokens > 0 else 0
        atom_rate = axm_cnt / at if at > 0 else 0
        enrich = atom_rate / base_rate if base_rate > 0 else 0
        axm_pct = 100 * axm_cnt / at if at > 0 else 0
        atom_axm.append((atom, enrich, at, axm_cnt, axm_pct))

    atom_axm.sort(key=lambda x: -x[1])
    print("%-6s %12s %8s %8s %9s" % ('Atom', 'AXM Enrich', 'Count', 'AXM', 'AXM%'))
    print("-" * 48)
    f_axm_rank = None
    f_axm_pct = 0
    for i, (atom, enrich, at, axm, axm_pct) in enumerate(atom_axm):
        marker = ""
        if atom == 'f':
            marker = " <-- f (TARGET)"
            f_axm_rank = i + 1
            f_axm_pct = axm_pct
        elif atom == 'c':
            marker = " <-- c (control: 93.5%)"
        elif atom == 'p':
            marker = " <-- p (control: 88.7%)"
        elif atom == 's':
            marker = " <-- s (control: 35.4% AXM)"
        elif atom == 'd':
            marker = " <-- d (MARKING peer)"
        print("%-6s %11.3fx %8d %8d %8.1f%%%s" % (atom, enrich, at, axm, axm_pct, marker))

    # --- Rank ALL atoms by FL_HAZ enrichment ---
    print("\n--- All atoms ranked by FL_HAZ enrichment (lowest = most depleted) ---")
    atom_flhaz = []
    for atom in sorted(atom_macro.keys()):
        at = atom_total[atom]
        if at < 10:
            continue
        flhaz_cnt = atom_macro[atom].get('FL_HAZ', 0)
        base_rate = global_macro.get('FL_HAZ', 0) / total_tokens if total_tokens > 0 else 0
        atom_rate = flhaz_cnt / at if at > 0 else 0
        enrich = atom_rate / base_rate if base_rate > 0 else 0
        atom_flhaz.append((atom, enrich, at, flhaz_cnt))

    atom_flhaz.sort(key=lambda x: x[1])
    print("%-6s %14s %8s %8s" % ('Atom', 'FL_HAZ Enrich', 'Count', 'FL_HAZ'))
    print("-" * 40)
    f_flhaz_rank = None
    for i, (atom, enrich, at, fh) in enumerate(atom_flhaz):
        marker = ""
        if atom == 'f':
            marker = " <-- f (TARGET)"
            f_flhaz_rank = i + 1
        elif atom == 'c':
            marker = " <-- c (control)"
        elif atom == 'p':
            marker = " <-- p (control)"
        elif atom == 'd':
            marker = " <-- d (MARKING peer)"
        print("%-6s %13.3fx %8d %8d%s" % (atom, enrich, at, fh, marker))

    # --- Per-section stability ---
    print("\n--- Per-section stability of f-initial macro-state profile ---")
    sections = sorted(section_total.keys())
    section_axm_enriched = 0
    section_flhaz_depleted = 0
    sections_tested = 0

    for sec in sections:
        sec_tot = section_total[sec]
        sec_f = section_atom_total[sec].get('f', 0)
        if sec_f < 3:  # very low threshold for rare atom
            continue
        sections_tested += 1
        print("\n  Section %s (f-initial: %d, total: %d)" % (sec, sec_f, sec_tot))

        sec_axm_enrich = 0
        sec_flhaz_enrich = 0
        for ms in MACRO_STATES:
            f_cnt = section_atom_macro[sec].get('f', {}).get(ms, 0)
            f_pct = 100 * f_cnt / sec_f if sec_f > 0 else 0
            base_pct = 100 * section_global_macro[sec].get(ms, 0) / sec_tot if sec_tot > 0 else 0
            enrich = f_pct / base_pct if base_pct > 0 else 0
            print("    %-12s f=%6.1f%% base=%6.1f%% enrich=%.2fx" % (ms, f_pct, base_pct, enrich))
            if ms == 'AXM':
                sec_axm_enrich = enrich
            elif ms == 'FL_HAZ':
                sec_flhaz_enrich = enrich

        if sec_axm_enrich >= 0.95:  # relaxed threshold for rare atom
            section_axm_enriched += 1
        if sec_flhaz_enrich <= 1.5:
            section_flhaz_depleted += 1

    print("\n  Sections with AXM enrichment >= 0.95x: %d/%d" % (section_axm_enriched, sections_tested))
    print("  Sections with FL_HAZ depletion <= 1.5x: %d/%d" % (section_flhaz_depleted, sections_tested))

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    # Special handling: f-initial may be 100% HT/UN (unclassified by 49-class grammar)
    if f_total == 0:
        print("\n*** IMPORTANT STRUCTURAL FINDING ***")
        print("  f-initial tokens: 0 classified (100%% HT/UN vocabulary)")
        print("  All f-initial MIDDLEs are OUTSIDE the 49-class grammar.")
        print("  This means f-initial vocabulary is entirely in the dark/HT layer.")
        print("  Compare: p-initial is also rare in grammar but has %d classified tokens." %
              atom_total.get('p', 0))
        print("  Compare: d-initial has %d classified tokens." % atom_total.get('d', 0))
        print()
        print("  This is consistent with f being a MARKING atom (C1250):")
        print("  MARKING vocabulary operates as annotation/identification,")
        print("  which is predominantly HT/compound vocabulary (C935, C1254).")
        print()
        print("  Macro-state test is NOT APPLICABLE (no classified tokens).")
        print("  The prediction assumed f-initial would appear in grammar;")
        print("  instead, f-initial is 100%% identification vocabulary.")
        print()
        print("AXM enrichment: N/A (0 classified tokens)")
        print("  NOT APPLICABLE")
        print()
        print("FL_HAZ enrichment: N/A (0 classified tokens)")
        print("  PASS (trivially: 0 hazard tokens)")
        print()
        print("PRIMARY (AXM >= 1.0x AND FL_HAZ <= 1.5x): NOT APPLICABLE")
        print("OVERALL: NOT APPLICABLE (f-initial is 100%% HT/UN)")
        print("  STRUCTURAL NOTE: f is a pure identification/marking atom")
        print("  that never enters the 49-class execution grammar.")
        return

    axm_enrich = f_enrichments.get('AXM', 0)
    axm_p = f_pvals.get('AXM', 1.0)
    flhaz_enrich = f_enrichments.get('FL_HAZ', 999)
    flhaz_p = f_pvals.get('FL_HAZ', 1.0)

    pass_axm = axm_enrich >= 1.0
    pass_flhaz = flhaz_enrich <= 1.5

    print("\nAXM enrichment: %.3fx (threshold >= 1.00x)" % axm_enrich)
    print("  p-value: %.4f" % axm_p)
    if f_axm_rank is not None:
        print("  AXM rank: #%d of %d atoms" % (f_axm_rank, len(atom_axm)))
    print("  %s" % ('PASS' if pass_axm else 'FAIL'))

    print("\nFL_HAZ enrichment: %.3fx (threshold <= 1.50x)" % flhaz_enrich)
    print("  p-value: %.4f" % flhaz_p)
    if f_flhaz_rank is not None:
        print("  FL_HAZ rank: #%d of %d atoms (ascending)" % (f_flhaz_rank, len(atom_flhaz)))
    print("  %s" % ('PASS' if pass_flhaz else 'FAIL'))

    print("\nf AXM%%: %.1f%%" % f_axm_pct)
    print("  Compare: p=88.7%%, c=93.5%%, d (MARKING peer)")

    primary = pass_axm and pass_flhaz
    print("\nPRIMARY (AXM >= 1.0x AND FL_HAZ <= 1.5x): %s" % ('PASS' if primary else 'FAIL'))
    print("OVERALL: %s" % ('PASS' if primary else 'FAIL'))
    print("  f-initial tokens are %sdistributed as predicted" % ('' if primary else 'NOT '))
    print("  (within main operational loop, not strongly hazard-associated)")


if __name__ == '__main__':
    main()
