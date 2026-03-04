#!/usr/bin/env python3
"""
P-P4: p-initial macro-state distribution
=========================================
Test whether p-initial tokens distribute across macro-states as predicted
for a MARKING/pause element.

Predictions (p="pause" -> operational marking):
- AXM enrichment >= 1.2x (operational main loop)
- FL_HAZ depletion <= 1.0x (not hazard-associated)
- Additional: p AXM% should be < 90% (less AXM-confined than c)

Method:
1. For each Currier B token, extract MIDDLE initial atom and macro-state
2. Build initial_atom -> macro_state -> count
3. Compute enrichment of each macro-state for p-initial vs global baseline
4. Rank all atoms by AXM concentration and FL_HAZ depletion
5. Per-section stability check
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
    print("P-P4: p-initial macro-state distribution")
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

        ts = decoder.analyze_token(w)
        if not ts or not ts.macro_state:
            continue
        ms = ts.macro_state

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
    p_total = atom_total.get('p', 0)
    print("p-initial tokens: %d (%.1f%%)" % (p_total, 100 * p_total / total_tokens if total_tokens > 0 else 0))

    # --- Global baseline ---
    print("\n%-12s %12s %10s" % ('Macro State', 'Global Count', 'Global %'))
    print("-" * 36)
    for ms in MACRO_STATES:
        cnt = global_macro.get(ms, 0)
        print("%-12s %12d %9.1f%%" % (ms, cnt, 100 * cnt / total_tokens if total_tokens > 0 else 0))

    # --- p-initial profile vs baseline ---
    print("\n--- p-initial macro-state profile ---")
    print("%-12s %10s %8s %8s %8s %8s %10s" % ('Macro State', 'p Count', 'p %', 'Base %', 'Enrich', 'Chi2', 'p-val'))
    print("-" * 70)

    p_enrichments = {}
    p_pvals = {}
    for ms in MACRO_STATES:
        p_cnt = atom_macro.get('p', {}).get(ms, 0)
        p_pct = 100 * p_cnt / p_total if p_total > 0 else 0
        base_pct = 100 * global_macro.get(ms, 0) / total_tokens if total_tokens > 0 else 0
        enrich = p_pct / base_pct if base_pct > 0 else 0

        # Chi-square: observed p_cnt vs expected under global rate
        expected = p_total * (global_macro.get(ms, 0) / total_tokens) if total_tokens > 0 else 0
        if expected > 0:
            chi2 = (p_cnt - expected) ** 2 / expected
        else:
            chi2 = 0
        pv = chi2_1df_p(chi2)

        p_enrichments[ms] = enrich
        p_pvals[ms] = pv

        print("%-12s %10d %7.1f%% %7.1f%% %7.2fx %7.2f %10.4f" %
              (ms, p_cnt, p_pct, base_pct, enrich, chi2, pv))

    # --- Rank ALL atoms by AXM concentration ---
    print("\n--- All atoms ranked by AXM enrichment (highest first) ---")
    atom_axm = []
    for atom in sorted(atom_macro.keys()):
        at = atom_total[atom]
        if at < 20:
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
    p_axm_rank = None
    p_axm_pct = 0
    for i, (atom, enrich, at, axm, axm_pct) in enumerate(atom_axm):
        marker = " <-- p" if atom == 'p' else ""
        print("%-6s %11.3fx %8d %8d %8.1f%%%s" % (atom, enrich, at, axm, axm_pct, marker))
        if atom == 'p':
            p_axm_rank = i + 1
            p_axm_pct = axm_pct

    # --- Rank ALL atoms by FL_HAZ depletion ---
    print("\n--- All atoms ranked by FL_HAZ enrichment (lowest = most depleted) ---")
    atom_flhaz = []
    for atom in sorted(atom_macro.keys()):
        at = atom_total[atom]
        if at < 20:
            continue
        flhaz_cnt = atom_macro[atom].get('FL_HAZ', 0)
        base_rate = global_macro.get('FL_HAZ', 0) / total_tokens if total_tokens > 0 else 0
        atom_rate = flhaz_cnt / at if at > 0 else 0
        enrich = atom_rate / base_rate if base_rate > 0 else 0
        atom_flhaz.append((atom, enrich, at, flhaz_cnt))

    atom_flhaz.sort(key=lambda x: x[1])
    print("%-6s %14s %8s %8s" % ('Atom', 'FL_HAZ Enrich', 'Count', 'FL_HAZ'))
    print("-" * 40)
    p_flhaz_rank = None
    for i, (atom, enrich, at, fh) in enumerate(atom_flhaz):
        marker = " <-- p" if atom == 'p' else ""
        print("%-6s %13.3fx %8d %8d%s" % (atom, enrich, at, fh, marker))
        if atom == 'p':
            p_flhaz_rank = i + 1

    # --- Per-section stability ---
    print("\n--- Per-section stability of p-initial macro-state profile ---")
    sections = sorted(section_total.keys())
    section_axm_enriched = 0
    section_flhaz_depleted = 0
    sections_tested = 0

    for sec in sections:
        sec_tot = section_total[sec]
        sec_p = section_atom_total[sec].get('p', 0)
        if sec_p < 5:
            continue
        sections_tested += 1
        print("\n  Section %s (p-initial: %d, total: %d)" % (sec, sec_p, sec_tot))

        sec_axm_enrich = 0
        sec_flhaz_enrich = 0
        for ms in MACRO_STATES:
            p_cnt = section_atom_macro[sec].get('p', {}).get(ms, 0)
            p_pct = 100 * p_cnt / sec_p if sec_p > 0 else 0
            base_pct = 100 * section_global_macro[sec].get(ms, 0) / sec_tot if sec_tot > 0 else 0
            enrich = p_pct / base_pct if base_pct > 0 else 0
            print("    %-12s p=%6.1f%% base=%6.1f%% enrich=%.2fx" % (ms, p_pct, base_pct, enrich))
            if ms == 'AXM':
                sec_axm_enrich = enrich
            elif ms == 'FL_HAZ':
                sec_flhaz_enrich = enrich

        if sec_axm_enrich >= 1.1:
            section_axm_enriched += 1
        if sec_flhaz_enrich <= 1.1:
            section_flhaz_depleted += 1

    print("\n  Sections with AXM enrichment >= 1.1x: %d/%d" % (section_axm_enriched, sections_tested))
    print("  Sections with FL_HAZ depletion <= 1.1x: %d/%d" % (section_flhaz_depleted, sections_tested))

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    axm_enrich = p_enrichments.get('AXM', 0)
    axm_p = p_pvals.get('AXM', 1.0)
    flhaz_enrich = p_enrichments.get('FL_HAZ', 999)
    flhaz_p = p_pvals.get('FL_HAZ', 1.0)

    pass_axm = axm_enrich >= 1.2
    pass_flhaz = flhaz_enrich <= 1.0
    pass_not_confined = p_axm_pct < 90

    print("\nAXM enrichment: %.3fx (threshold >= 1.20x)" % axm_enrich)
    print("  p-value: %.4f" % axm_p)
    if p_axm_rank is not None:
        print("  AXM rank: #%d of %d atoms" % (p_axm_rank, len(atom_axm)))
    print("  %s" % ('PASS' if pass_axm else 'FAIL'))

    print("\nFL_HAZ enrichment: %.3fx (threshold <= 1.00x)" % flhaz_enrich)
    print("  p-value: %.4f" % flhaz_p)
    if p_flhaz_rank is not None:
        print("  FL_HAZ rank: #%d of %d atoms (ascending)" % (p_flhaz_rank, len(atom_flhaz)))
    print("  %s" % ('PASS' if pass_flhaz else 'FAIL'))

    print("\np AXM%%: %.1f%% (threshold < 90%% -- less confined than c)" % p_axm_pct)
    print("  %s" % ('PASS' if pass_not_confined else 'FAIL'))

    primary = pass_axm and pass_flhaz
    overall = primary and pass_not_confined
    print("\nPRIMARY (AXM >= 1.2x AND FL_HAZ <= 1.0x): %s" % ('PASS' if primary else 'FAIL'))
    print("SUB-CRITERION (AXM%% < 90%%): %s" % ('PASS' if pass_not_confined else 'FAIL'))
    print("OVERALL: %s" % ('PASS' if overall else 'FAIL'))
    print("  p-initial tokens are %sdistributed as predicted" % ('' if overall else 'NOT '))
    print("  (operational main loop, not hazard-associated, not over-confined)")


if __name__ == '__main__':
    main()
