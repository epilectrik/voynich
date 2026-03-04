#!/usr/bin/env python3
"""
F-F3: f NEUTRAL carryover run analysis
========================================
Test the carryover behavior of f-initial MIDDLEs. f = "flag" (MARKING)
has only 215 MIDDLE occurrences, so expect NEUTRAL carryover (C1208
classifies f as NEUTRAL along with d, l, o, q).

Predictions:
- f-f consecutive pair enrichment < 2.0x (NEUTRAL, unlike p's 8.126x POSITIVE)
- If < 3 pairs found, mark INCONCLUSIVE (f is rare at ~1% initial rate)

Controls: p carryover 8.126x (POSITIVE), c carryover (from Phase 499)

Note: f is extremely rare as initial atom (~215 MIDDLE occ across all B),
so we expect very few consecutive pairs. The prediction is specifically
that enrichment will be LOW -- consistent with NEUTRAL carryover class.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder


def normal_cdf(x):
    """Approximate normal CDF."""
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.8212560 + t * 1.3302744))))
    if x > 0:
        return 1.0 - p
    return p


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    print("=" * 70)
    print("F-F3: f NEUTRAL carryover run analysis")
    print("=" * 70)

    # Collect tokens organized by (folio, line)
    line_atoms = defaultdict(list)  # (folio, line) -> [initial_atom, ...]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue
        initial_atom = mid[0]
        key = (token.folio, token.line)
        line_atoms[key].append(initial_atom)

    # Count consecutive pairs per atom
    atom_pair_count = defaultdict(int)       # atom -> count of consecutive same-atom pairs
    atom_pair_positions = defaultdict(list)   # atom -> [midpoint frac_pos of each pair]
    atom_total = defaultdict(int)
    total_pairs = 0
    total_tokens = 0

    # Per-section tracking
    section_pair_count = defaultdict(lambda: defaultdict(int))
    section_total_pairs = defaultdict(int)
    section_atom_total = defaultdict(lambda: defaultdict(int))
    section_total_tokens = defaultdict(int)

    for key, atoms in line_atoms.items():
        n = len(atoms)
        if n < 3:
            continue

        fol = key[0]
        fa = decoder.analyze_folio(fol)
        section = fa.section if fa else 'UNK'

        for i in range(n):
            atom = atoms[i]
            atom_total[atom] += 1
            total_tokens += 1
            section_atom_total[section][atom] += 1
            section_total_tokens[section] += 1

        for i in range(n - 1):
            total_pairs += 1
            section_total_pairs[section] += 1
            a1 = atoms[i]
            a2 = atoms[i + 1]

            if a1 == a2:
                atom_pair_count[a1] += 1
                section_pair_count[section][a1] += 1
                # Compute fractional position of midpoint
                frac1 = i / (n - 1) if n > 1 else 0.5
                frac2 = (i + 1) / (n - 1) if n > 1 else 0.5
                midpoint = (frac1 + frac2) / 2
                atom_pair_positions[a1].append(midpoint)

    # --- All atoms ranked by carryover enrichment ---
    print("\nTotal tokens: %d" % total_tokens)
    print("Total consecutive pairs: %d" % total_pairs)

    print("\n--- All atoms ranked by carryover enrichment ---")
    atom_enrichments = []
    for atom in sorted(atom_total.keys()):
        at = atom_total[atom]
        if at < 10:  # lower threshold for rare atoms
            continue
        rate = at / total_tokens
        expected_pairs = rate * rate * total_pairs
        observed_pairs = atom_pair_count.get(atom, 0)
        enrichment = observed_pairs / expected_pairs if expected_pairs > 0 else 0

        # Z-score: (obs - exp) / sqrt(exp * (1 - rate^2))
        if expected_pairs > 0:
            z = (observed_pairs - expected_pairs) / math.sqrt(expected_pairs * (1 - rate ** 2) + 1e-15)
            p_val = 2 * (1 - normal_cdf(abs(z)))
        else:
            z, p_val = 0, 1.0

        atom_enrichments.append((atom, enrichment, observed_pairs, expected_pairs, z, p_val, at))

    atom_enrichments.sort(key=lambda x: -x[1])

    print("%-6s %-6s %8s %8s %8s %8s %10s %8s" % ('Rank', 'Atom', 'Enrich', 'Obs', 'Exp', 'z', 'p', 'N tok'))
    print("-" * 66)
    f_enrichment = None
    f_z = None
    f_rank_carry = None
    for i, (atom, enrich, obs, exp, z, pv, n) in enumerate(atom_enrichments):
        marker = ""
        if atom == 'f':
            marker = " <-- f (TARGET)"
            f_enrichment = enrich
            f_z = z
            f_rank_carry = i + 1
        elif atom == 'p':
            marker = " <-- p (control: POSITIVE 8.126x)"
        elif atom == 'c':
            marker = " <-- c (control)"
        elif atom == 'd':
            marker = " <-- d (control: NEUTRAL)"
        print("%-6d %-6s %7.3fx %8d %7.1f %+7.2f %10.4f %8d%s" % (i + 1, atom, enrich, obs, exp, z, pv, n, marker))

    # --- f-f pair details ---
    f_pairs = atom_pair_count.get('f', 0)
    f_rate = atom_total.get('f', 0) / total_tokens if total_tokens > 0 else 0
    f_expected = f_rate ** 2 * total_pairs

    print("\n--- f-f consecutive pair details ---")
    print("  f-initial tokens: %d (%.2f%%)" % (atom_total.get('f', 0), 100 * f_rate))
    print("  f-f observed pairs: %d" % f_pairs)
    print("  f-f expected pairs: %.1f" % f_expected)
    if f_expected > 0:
        print("  Enrichment: %.3fx" % (f_pairs / f_expected))
    else:
        print("  Enrichment: N/A (expected = 0)")

    # Inconclusive check
    inconclusive = f_pairs < 3
    if inconclusive:
        print("  *** WARNING: N(pairs) = %d < 3 -- results will be INCONCLUSIVE ***" % f_pairs)

    # --- Position distribution of f-f pairs ---
    f_pair_pos = atom_pair_positions.get('f', [])
    print("\n--- Position distribution of f-f pairs ---")
    if f_pair_pos:
        mid_line_count = sum(1 for pos in f_pair_pos if 0.3 <= pos <= 0.7)
        mid_line_pct = 100 * mid_line_count / len(f_pair_pos)

        print("  Total f-f pairs with position data: %d" % len(f_pair_pos))
        print("  Mid-line (0.3-0.7): %d (%.1f%%)" % (mid_line_count, mid_line_pct))

        # Quintile distribution
        quintile_counts = [0] * 5
        for pos in f_pair_pos:
            q = min(int(pos * 5), 4)
            quintile_counts[q] += 1
        print()
        print("  %-15s %8s %8s" % ('Quintile', 'Count', '%'))
        print("  " + "-" * 33)
        for q in range(5):
            pct = 100 * quintile_counts[q] / len(f_pair_pos) if f_pair_pos else 0
            print("  Q%d (%.1f-%.1f)  %8d %7.1f%%" % (q + 1, q * 0.2, (q + 1) * 0.2, quintile_counts[q], pct))
    else:
        mid_line_pct = 0
        print("  No f-f pairs found!")

    # --- Run length distribution ---
    print("\n--- f-initial run length distribution ---")
    run_lengths = defaultdict(int)
    for key, atoms in line_atoms.items():
        n = len(atoms)
        if n < 3:
            continue
        current_run = 1 if atoms[0] == 'f' else 0
        for i in range(1, n):
            if atoms[i] == 'f' and atoms[i - 1] == 'f':
                current_run += 1
            else:
                if atoms[i - 1] == 'f' and current_run >= 1:
                    run_lengths[current_run] += 1
                current_run = 1 if atoms[i] == 'f' else 0
        # Final run
        if atoms[-1] == 'f' and current_run >= 1:
            run_lengths[current_run] += 1

    total_runs = sum(run_lengths.values())
    print("  %-12s %8s %8s" % ('Run Length', 'Count', '%'))
    print("  " + "-" * 30)
    for rl in sorted(run_lengths.keys()):
        pct = 100 * run_lengths[rl] / total_runs if total_runs > 0 else 0
        print("  %-12d %8d %7.1f%%" % (rl, run_lengths[rl], pct))

    if total_runs > 0:
        mean_run = sum(rl * cnt for rl, cnt in run_lengths.items()) / total_runs
        pct_multi = 100 * sum(cnt for rl, cnt in run_lengths.items() if rl >= 2) / total_runs
        print("  Mean run length: %.3f" % mean_run)
        print("  Multi-token runs (>=2): %.1f%%" % pct_multi)
    else:
        print("  No runs found")

    # --- CROSS-LINE analysis ---
    print("\n--- Cross-line carryover analysis ---")
    print("  (Testing whether f-terminal lines are followed by f-initial lines)")

    # Build ordered list of lines per folio
    folio_lines = defaultdict(list)
    for key in sorted(line_atoms.keys()):
        fol, line = key
        if len(line_atoms[key]) >= 2:
            folio_lines[fol].append(key)

    cross_line_pairs = 0
    cross_line_ff = 0  # terminal-f followed by initial-f
    cross_line_f_terminal = 0
    cross_line_f_initial = 0
    cross_line_total = 0

    for fol, keys in folio_lines.items():
        for i in range(len(keys) - 1):
            curr_atoms = line_atoms[keys[i]]
            next_atoms = line_atoms[keys[i + 1]]
            if not curr_atoms or not next_atoms:
                continue

            cross_line_total += 1
            terminal_atom = curr_atoms[-1]
            initial_atom = next_atoms[0]

            if terminal_atom == 'f':
                cross_line_f_terminal += 1
            if initial_atom == 'f':
                cross_line_f_initial += 1
            if terminal_atom == 'f' and initial_atom == 'f':
                cross_line_ff += 1

    if cross_line_total > 0 and cross_line_f_terminal > 0 and cross_line_f_initial > 0:
        f_term_rate = cross_line_f_terminal / cross_line_total
        f_init_rate = cross_line_f_initial / cross_line_total
        expected_ff = f_term_rate * f_init_rate * cross_line_total
        cross_enrichment = cross_line_ff / expected_ff if expected_ff > 0 else 0

        print("  Cross-line pairs: %d" % cross_line_total)
        print("  f-terminal lines: %d (%.2f%%)" % (cross_line_f_terminal, 100 * f_term_rate))
        print("  f-initial next lines: %d (%.2f%%)" % (cross_line_f_initial, 100 * f_init_rate))
        print("  f-terminal then f-initial: %d" % cross_line_ff)
        print("  Expected: %.1f" % expected_ff)
        print("  Cross-line enrichment: %.3fx" % cross_enrichment)
    else:
        cross_enrichment = float('nan')
        print("  Insufficient cross-line data (f-terminal: %d, f-initial next: %d)" %
              (cross_line_f_terminal, cross_line_f_initial))

    # --- Per-section stability ---
    print("\n--- Per-section carryover enrichment ---")
    for sec in sorted(section_total_pairs.keys()):
        sec_f = section_atom_total[sec].get('f', 0)
        sec_tot = section_total_tokens[sec]
        if sec_f < 5 or sec_tot < 100:
            continue
        sec_rate = sec_f / sec_tot
        sec_exp = sec_rate ** 2 * section_total_pairs[sec]
        sec_obs = section_pair_count[sec].get('f', 0)
        sec_enrich = sec_obs / sec_exp if sec_exp > 0 else 0
        print("  %s: obs=%d exp=%.1f enrich=%.3fx (f-rate=%.1f%%)" %
              (sec, sec_obs, sec_exp, sec_enrich, 100 * sec_rate))

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    actual_enrichment = f_pairs / f_expected if f_expected > 0 else 0

    if inconclusive:
        print("\n*** INCONCLUSIVE: only %d f-f pairs found (need >= 3 for reliable test) ***" % f_pairs)
        print("  f-f pair enrichment: %.3fx (threshold < 2.0x for NEUTRAL)" % actual_enrichment)
        if f_z is not None:
            print("  z-score: %+.2f" % f_z)
        if f_rank_carry is not None:
            print("  carryover rank: #%d of %d atoms" % (f_rank_carry, len(atom_enrichments)))
        print()
        print("  Prediction was: enrichment < 2.0x (NEUTRAL carryover)")
        if actual_enrichment < 2.0:
            print("  Direction consistent with NEUTRAL, but sample too small")
        else:
            print("  Direction inconsistent with NEUTRAL, but sample too small")
        print("\n  OVERALL: INCONCLUSIVE (insufficient f-f pairs)")
    else:
        pass_enrichment = actual_enrichment < 2.0

        print("\nf-f pair enrichment: %.3fx (threshold < 2.0x for NEUTRAL)" % actual_enrichment)
        if f_z is not None:
            print("  z-score: %+.2f" % f_z)
        if f_rank_carry is not None:
            print("  carryover rank: #%d of %d atoms" % (f_rank_carry, len(atom_enrichments)))
        print("  %s" % ('PASS' if pass_enrichment else 'FAIL'))

        print("\nControls:")
        for atom, enrich, obs, exp, z, pv, n in atom_enrichments:
            if atom == 'p':
                print("  p (POSITIVE): %.3fx enrichment, N=%d pairs" % (enrich, obs))
            elif atom == 'd':
                print("  d (NEUTRAL):  %.3fx enrichment, N=%d pairs" % (enrich, obs))

        overall = pass_enrichment
        print("\nOVERALL: %s" % ('PASS' if overall else 'FAIL'))
        print("  f atoms %s show NEUTRAL carryover (< 2.0x)" %
              ('DO' if overall else 'do NOT'))
        print("  (Compare: p = POSITIVE 8.126x, d = NEUTRAL)")


if __name__ == '__main__':
    main()
