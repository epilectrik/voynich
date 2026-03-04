"""
P-C5: c-initial macro-state distribution
=========================================
Test whether c-initial tokens appear proactively (not triggered by hazards).

Predictions (c="adjust" → proactive mid-process):
- FL_HAZ <= 0.8x enrichment (proactive, not hazard-triggered)
- FQ >= 1.1x enrichment (active processing context)
- Both p < 0.05

Method:
1. For each Currier B token, extract MIDDLE initial atom and macro-state
2. Build initial_atom → macro_state → count
3. Compute enrichment of each macro-state for c-initial vs global baseline
4. Chi-square test for FL_HAZ depletion and FQ enrichment
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
    print("P-C5: c-initial macro-state distribution")
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

    print(f"\nTotal classified tokens: {total_tokens}")
    print(f"Unique initial atoms: {len(atom_macro)}")
    c_total = atom_total.get('c', 0)
    print(f"c-initial tokens: {c_total} ({100*c_total/total_tokens:.1f}%)")

    # --- Global baseline ---
    print(f"\n{'Macro State':<12} {'Global Count':>12} {'Global %':>10}")
    print("-" * 36)
    for ms in MACRO_STATES:
        cnt = global_macro.get(ms, 0)
        print(f"{ms:<12} {cnt:>12} {100*cnt/total_tokens:>9.1f}%")

    # --- c-initial profile vs baseline ---
    print(f"\n--- c-initial macro-state profile ---")
    print(f"{'Macro State':<12} {'c Count':>10} {'c %':>8} {'Base %':>8} {'Enrich':>8} {'Chi2':>8} {'p-val':>10}")
    print("-" * 70)

    c_enrichments = {}
    c_pvals = {}
    for ms in MACRO_STATES:
        c_cnt = atom_macro.get('c', {}).get(ms, 0)
        c_pct = 100 * c_cnt / c_total if c_total > 0 else 0
        base_pct = 100 * global_macro.get(ms, 0) / total_tokens if total_tokens > 0 else 0
        enrich = c_pct / base_pct if base_pct > 0 else 0

        # Chi-square: observed c_cnt vs expected under global rate
        expected = c_total * (global_macro.get(ms, 0) / total_tokens) if total_tokens > 0 else 0
        if expected > 0:
            chi2 = (c_cnt - expected) ** 2 / expected
        else:
            chi2 = 0
        p = chi2_1df_p(chi2)

        c_enrichments[ms] = enrich
        c_pvals[ms] = p

        print(f"{ms:<12} {c_cnt:>10} {c_pct:>7.1f}% {base_pct:>7.1f}% {enrich:>7.2f}x {chi2:>7.2f} {p:>10.4f}")

    # --- Rank ALL atoms by FL_HAZ depletion ---
    print(f"\n--- All atoms ranked by FL_HAZ enrichment (lowest = most depleted) ---")
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
    print(f"{'Atom':<6} {'FL_HAZ Enrich':>14} {'Count':>8} {'FL_HAZ':>8}")
    print("-" * 40)
    for atom, enrich, at, fh in atom_flhaz:
        marker = " <-- c" if atom == 'c' else ""
        print(f"{atom:<6} {enrich:>13.3f}x {at:>8} {fh:>8}{marker}")

    # --- Rank ALL atoms by FQ enrichment ---
    print(f"\n--- All atoms ranked by FQ enrichment (highest first) ---")
    atom_fq = []
    for atom in sorted(atom_macro.keys()):
        at = atom_total[atom]
        if at < 20:
            continue
        fq_cnt = atom_macro[atom].get('FQ', 0)
        base_rate = global_macro.get('FQ', 0) / total_tokens if total_tokens > 0 else 0
        atom_rate = fq_cnt / at if at > 0 else 0
        enrich = atom_rate / base_rate if base_rate > 0 else 0
        atom_fq.append((atom, enrich, at, fq_cnt))

    atom_fq.sort(key=lambda x: -x[1])
    print(f"{'Atom':<6} {'FQ Enrich':>11} {'Count':>8} {'FQ':>8}")
    print("-" * 36)
    for atom, enrich, at, fq in atom_fq:
        marker = " <-- c" if atom == 'c' else ""
        print(f"{atom:<6} {enrich:>10.3f}x {at:>8} {fq:>8}{marker}")

    # --- Per-section stability ---
    print(f"\n--- Per-section stability of c-initial macro-state profile ---")
    sections = sorted(section_total.keys())
    for sec in sections:
        sec_tot = section_total[sec]
        sec_c = section_atom_total[sec].get('c', 0)
        if sec_c < 10:
            continue
        print(f"\n  Section {sec} (c-initial: {sec_c}, total: {sec_tot})")
        for ms in MACRO_STATES:
            c_cnt = section_atom_macro[sec].get('c', {}).get(ms, 0)
            c_pct = 100 * c_cnt / sec_c if sec_c > 0 else 0
            base_pct = 100 * section_global_macro[sec].get(ms, 0) / sec_tot if sec_tot > 0 else 0
            enrich = c_pct / base_pct if base_pct > 0 else 0
            print(f"    {ms:<12} c={c_pct:>6.1f}% base={base_pct:>6.1f}% enrich={enrich:.2f}x")

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    flhaz_enrich = c_enrichments.get('FL_HAZ', 999)
    flhaz_p = c_pvals.get('FL_HAZ', 1.0)
    fq_enrich = c_enrichments.get('FQ', 0)
    fq_p = c_pvals.get('FQ', 1.0)

    pass_flhaz = flhaz_enrich <= 0.8 and flhaz_p < 0.05
    pass_fq = fq_enrich >= 1.1 and fq_p < 0.05

    print(f"\nFL_HAZ enrichment: {flhaz_enrich:.3f}x (threshold <= 0.80x)")
    print(f"  p-value: {flhaz_p:.4f} (threshold < 0.05)")
    print(f"  {'PASS' if pass_flhaz else 'FAIL'}")

    print(f"\nFQ enrichment: {fq_enrich:.3f}x (threshold >= 1.10x)")
    print(f"  p-value: {fq_p:.4f} (threshold < 0.05)")
    print(f"  {'PASS' if pass_fq else 'FAIL'}")

    overall = pass_flhaz and pass_fq
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")
    print(f"  c-initial tokens are {'NOT ' if not overall else ''}distributed as predicted")
    print(f"  (proactive mid-process, not hazard-triggered)")


if __name__ == '__main__':
    main()
