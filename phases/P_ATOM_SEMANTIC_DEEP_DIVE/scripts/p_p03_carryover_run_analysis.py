#!/usr/bin/env python3
"""
P-P3: p POSITIVE carryover run analysis
==========================================
Test the known positive carryover (z=+4.27, C1208 -- LARGEST delta +0.138
of any atom). Test if this manifests at initial-atom level.

Predictions:
- p-p consecutive pair enrichment >= 1.5x (above chance)
- p-p pairs concentrated at mid-line (0.3-0.7) >= 50%
- Cross-line: p-terminal-line to p-first-next-line enrichment < 1.0x
  (C1208 says negative cross-line carryover)

Method:
1. For each line, build sequence of initial atoms
2. Count consecutive p-p pairs
3. Compare to expected rate: (p-initial rate)^2 x total pairs
4. Compute enrichment ratio
5. Where do p-p pairs fall in the line? Position distribution.
6. Cross-line p-terminal to p-first enrichment
7. Compare to all atoms ranked by carryover enrichment
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
    print("P-P3: p POSITIVE carryover run analysis")
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
        if at < 20:  # lower threshold for p since it is rarer
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
    p_enrichment = None
    p_z = None
    p_rank_carry = None
    for i, (atom, enrich, obs, exp, z, pv, n) in enumerate(atom_enrichments):
        marker = ""
        if atom == 'p':
            marker = " <-- p (TARGET)"
            p_enrichment = enrich
            p_z = z
            p_rank_carry = i + 1
        print("%-6d %-6s %7.3fx %8d %7.1f %+7.2f %10.4f %8d%s" % (i + 1, atom, enrich, obs, exp, z, pv, n, marker))

    # --- p-p pair details ---
    p_pairs = atom_pair_count.get('p', 0)
    p_rate = atom_total.get('p', 0) / total_tokens if total_tokens > 0 else 0
    p_expected = p_rate ** 2 * total_pairs

    print("\n--- p-p consecutive pair details ---")
    print("  p-initial tokens: %d (%.2f%%)" % (atom_total.get('p', 0), 100 * p_rate))
    print("  p-p observed pairs: %d" % p_pairs)
    print("  p-p expected pairs: %.1f" % p_expected)
    if p_expected > 0:
        print("  Enrichment: %.3fx" % (p_pairs / p_expected))
    else:
        print("  Enrichment: N/A")

    # --- Position distribution of p-p pairs ---
    p_pair_pos = atom_pair_positions.get('p', [])
    print("\n--- Position distribution of p-p pairs ---")
    if p_pair_pos:
        mid_line_count = sum(1 for pos in p_pair_pos if 0.3 <= pos <= 0.7)
        mid_line_pct = 100 * mid_line_count / len(p_pair_pos)

        print("  Total p-p pairs with position data: %d" % len(p_pair_pos))
        print("  Mid-line (0.3-0.7): %d (%.1f%%)" % (mid_line_count, mid_line_pct))

        # Quintile distribution
        quintile_counts = [0] * 5
        for pos in p_pair_pos:
            q = min(int(pos * 5), 4)
            quintile_counts[q] += 1
        print()
        print("  %-15s %8s %8s" % ('Quintile', 'Count', '%'))
        print("  " + "-" * 33)
        for q in range(5):
            pct = 100 * quintile_counts[q] / len(p_pair_pos) if p_pair_pos else 0
            print("  Q%d (%.1f-%.1f)  %8d %7.1f%%" % (q + 1, q * 0.2, (q + 1) * 0.2, quintile_counts[q], pct))
    else:
        mid_line_pct = 0
        print("  No p-p pairs found!")

    # --- Run length distribution ---
    print("\n--- p-initial run length distribution ---")
    run_lengths = defaultdict(int)
    for key, atoms in line_atoms.items():
        n = len(atoms)
        if n < 3:
            continue
        current_run = 1 if atoms[0] == 'p' else 0
        for i in range(1, n):
            if atoms[i] == 'p' and atoms[i - 1] == 'p':
                current_run += 1
            else:
                if atoms[i - 1] == 'p' and current_run >= 1:
                    run_lengths[current_run] += 1
                current_run = 1 if atoms[i] == 'p' else 0
        # Final run
        if atoms[-1] == 'p' and current_run >= 1:
            run_lengths[current_run] += 1

    total_runs = sum(run_lengths.values())
    print("  %-12s %8s %8s" % ('Run Length', 'Count', '%'))
    print("  " + "-" * 30)
    for rl in sorted(run_lengths.keys()):
        pct = 100 * run_lengths[rl] / total_runs if total_runs > 0 else 0
        print("  %-12d %8d %7.1f%%" % (rl, run_lengths[rl], pct))

    mean_run = sum(rl * cnt for rl, cnt in run_lengths.items()) / total_runs if total_runs > 0 else 0
    print("  Mean run length: %.3f" % mean_run)
    pct_multi = 100 * sum(cnt for rl, cnt in run_lengths.items() if rl >= 2) / total_runs if total_runs > 0 else 0
    print("  Multi-token runs (>=2): %.1f%%" % pct_multi)

    # --- CROSS-LINE analysis ---
    print("\n--- Cross-line carryover analysis ---")
    print("  Prediction: p-terminal-line to p-first-next-line enrichment < 1.0x")
    print("  (C1208: negative cross-line carryover)")

    # Build ordered list of lines per folio
    folio_lines = defaultdict(list)
    for key in sorted(line_atoms.keys()):
        fol, line = key
        if len(line_atoms[key]) >= 2:
            folio_lines[fol].append(key)

    cross_line_pairs = 0
    cross_line_pp = 0  # terminal-p followed by initial-p
    cross_line_p_terminal = 0  # lines ending with p-initial atom
    cross_line_p_initial = 0  # lines starting with p-initial atom
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

            if terminal_atom == 'p':
                cross_line_p_terminal += 1
            if initial_atom == 'p':
                cross_line_p_initial += 1
            if terminal_atom == 'p' and initial_atom == 'p':
                cross_line_pp += 1

    if cross_line_total > 0 and cross_line_p_terminal > 0 and cross_line_p_initial > 0:
        p_term_rate = cross_line_p_terminal / cross_line_total
        p_init_rate = cross_line_p_initial / cross_line_total
        expected_pp = p_term_rate * p_init_rate * cross_line_total
        cross_enrichment = cross_line_pp / expected_pp if expected_pp > 0 else 0

        print("  Cross-line pairs: %d" % cross_line_total)
        print("  p-terminal lines: %d (%.2f%%)" % (cross_line_p_terminal, 100 * p_term_rate))
        print("  p-initial next lines: %d (%.2f%%)" % (cross_line_p_initial, 100 * p_init_rate))
        print("  p-terminal then p-initial: %d" % cross_line_pp)
        print("  Expected: %.1f" % expected_pp)
        print("  Cross-line enrichment: %.3fx" % cross_enrichment)
    else:
        cross_enrichment = float('nan')
        print("  Insufficient cross-line data")

    # --- Per-section stability ---
    print("\n--- Per-section carryover enrichment ---")
    for sec in sorted(section_total_pairs.keys()):
        sec_p = section_atom_total[sec].get('p', 0)
        sec_tot = section_total_tokens[sec]
        if sec_p < 10 or sec_tot < 100:
            continue
        sec_rate = sec_p / sec_tot
        sec_exp = sec_rate ** 2 * section_total_pairs[sec]
        sec_obs = section_pair_count[sec].get('p', 0)
        sec_enrich = sec_obs / sec_exp if sec_exp > 0 else 0
        print("  %s: obs=%d exp=%.1f enrich=%.3fx (p-rate=%.1f%%)" %
              (sec, sec_obs, sec_exp, sec_enrich, 100 * sec_rate))

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    actual_enrichment = p_pairs / p_expected if p_expected > 0 else 0
    pass_enrichment = actual_enrichment >= 1.5
    pass_midline = mid_line_pct >= 50

    # Cross-line check
    cross_line_pass = False
    if not math.isnan(cross_enrichment):
        cross_line_pass = cross_enrichment < 1.0

    print("\np-p pair enrichment: %.3fx (threshold >= 1.5x)" % actual_enrichment)
    if p_z is not None:
        print("  z-score: %+.2f" % p_z)
    if p_rank_carry is not None:
        print("  carryover rank: #%d of %d atoms" % (p_rank_carry, len(atom_enrichments)))
    print("  %s" % ('PASS' if pass_enrichment else 'FAIL'))

    print("\np-p pairs at mid-line (0.3-0.7): %.1f%% (threshold >= 50%%)" % mid_line_pct)
    print("  %s" % ('PASS' if pass_midline else 'FAIL'))

    if not math.isnan(cross_enrichment):
        print("\nCross-line p-terminal to p-initial: %.3fx (threshold < 1.0x)" % cross_enrichment)
        print("  %s" % ('PASS' if cross_line_pass else 'FAIL'))
    else:
        print("\nCross-line: insufficient data")

    overall = pass_enrichment and pass_midline
    print("\nOVERALL: %s" % ('PASS' if overall else 'FAIL'))
    print("  p atoms %s show strong positive carryover%s" %
          ('DO' if overall else 'do NOT',
           ' concentrated mid-line' if pass_midline else ''))
    if not math.isnan(cross_enrichment):
        print("  Cross-line carryover: %s (%.3fx)" %
              ('depleted as predicted' if cross_line_pass else 'NOT depleted', cross_enrichment))


if __name__ == '__main__':
    main()
