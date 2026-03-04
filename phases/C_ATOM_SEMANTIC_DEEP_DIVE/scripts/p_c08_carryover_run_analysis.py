"""
P-C8: c POSITIVE carryover run analysis
==========================================
Test the known positive carryover (z=+3.23, C1208) — c persists
across consecutive tokens.

Predictions:
- c-c consecutive pair enrichment >= 1.3x (above chance)
- c-c pairs concentrated at mid-line (0.3-0.7) >= 60%

Method:
1. For each line, build sequence of initial atoms
2. Count consecutive c-c pairs
3. Compare to expected rate: (c-initial rate)^2 x total pairs
4. Compute enrichment ratio
5. Where do c-c pairs fall in the line? Position distribution.
6. Compare to other atoms' carryover enrichments
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
    print("P-C8: c POSITIVE carryover run analysis")
    print("=" * 70)

    # Collect tokens organized by (folio, line)
    line_atoms = defaultdict(list)  # (folio, line) -> [(initial_atom, frac_pos), ...]

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

    # Tokens are already in order from the transcript iterator

    # Count consecutive pairs per atom
    atom_pair_count = defaultdict(int)    # atom -> count of consecutive same-atom pairs
    atom_pair_positions = defaultdict(list)  # atom -> [midpoint frac_pos of each pair]
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
    print(f"\nTotal tokens: {total_tokens}")
    print(f"Total consecutive pairs: {total_pairs}")

    print(f"\n--- All atoms ranked by carryover enrichment ---")
    atom_enrichments = []
    for atom in sorted(atom_total.keys()):
        at = atom_total[atom]
        if at < 50:
            continue
        rate = at / total_tokens
        expected_pairs = rate * rate * total_pairs
        observed_pairs = atom_pair_count.get(atom, 0)
        enrichment = observed_pairs / expected_pairs if expected_pairs > 0 else 0

        # Z-score: (obs - exp) / sqrt(exp * (1 - rate^2))
        if expected_pairs > 0:
            z = (observed_pairs - expected_pairs) / math.sqrt(expected_pairs * (1 - rate ** 2) + 1e-15)
            p = 2 * (1 - normal_cdf(abs(z)))
        else:
            z, p = 0, 1.0

        atom_enrichments.append((atom, enrichment, observed_pairs, expected_pairs, z, p, at))

    atom_enrichments.sort(key=lambda x: -x[1])

    print(f"{'Rank':<6} {'Atom':<6} {'Enrich':>8} {'Obs':>8} {'Exp':>8} {'z':>8} {'p':>10} {'N tok':>8}")
    print("-" * 66)
    c_enrichment = None
    c_z = None
    for i, (atom, enrich, obs, exp, z, p, n) in enumerate(atom_enrichments):
        marker = ""
        if atom == 'c':
            marker = " <-- c (TARGET)"
            c_enrichment = enrich
            c_z = z
        print(f"{i+1:<6} {atom:<6} {enrich:>7.3f}x {obs:>8} {exp:>7.1f} {z:>+7.2f} {p:>10.4f} {n:>8}{marker}")

    # --- c-c pair details ---
    c_pairs = atom_pair_count.get('c', 0)
    c_rate = atom_total.get('c', 0) / total_tokens if total_tokens > 0 else 0
    c_expected = c_rate ** 2 * total_pairs

    print(f"\n--- c-c consecutive pair details ---")
    print(f"  c-initial tokens: {atom_total.get('c', 0)} ({100*c_rate:.2f}%)")
    print(f"  c-c observed pairs: {c_pairs}")
    print(f"  c-c expected pairs: {c_expected:.1f}")
    print(f"  Enrichment: {c_pairs/c_expected:.3f}x" if c_expected > 0 else "  Enrichment: N/A")

    # --- Position distribution of c-c pairs ---
    c_pair_pos = atom_pair_positions.get('c', [])
    print(f"\n--- Position distribution of c-c pairs ---")
    if c_pair_pos:
        mid_line_count = sum(1 for p in c_pair_pos if 0.3 <= p <= 0.7)
        mid_line_pct = 100 * mid_line_count / len(c_pair_pos)

        print(f"  Total c-c pairs with position data: {len(c_pair_pos)}")
        print(f"  Mid-line (0.3-0.7): {mid_line_count} ({mid_line_pct:.1f}%)")

        # Quintile distribution
        quintile_counts = [0] * 5
        for p in c_pair_pos:
            q = min(int(p * 5), 4)
            quintile_counts[q] += 1
        print(f"\n  {'Quintile':<15} {'Count':>8} {'%':>8}")
        print(f"  " + "-" * 33)
        for q in range(5):
            pct = 100 * quintile_counts[q] / len(c_pair_pos) if c_pair_pos else 0
            print(f"  Q{q+1} ({q*0.2:.1f}-{(q+1)*0.2:.1f})  {quintile_counts[q]:>8} {pct:>7.1f}%")
    else:
        mid_line_pct = 0
        print("  No c-c pairs found!")

    # --- Run length distribution ---
    print(f"\n--- c-initial run length distribution ---")
    run_lengths = defaultdict(int)
    for key, atoms in line_atoms.items():
        n = len(atoms)
        if n < 3:
            continue
        current_run = 1
        for i in range(1, n):
            if atoms[i] == 'c' and atoms[i - 1] == 'c':
                current_run += 1
            else:
                if atoms[i - 1] == 'c' and current_run >= 1:
                    run_lengths[current_run] += 1
                current_run = 1 if atoms[i] == 'c' else 0
        # Final run
        if atoms[-1] == 'c' and current_run >= 1:
            run_lengths[current_run] += 1

    total_runs = sum(run_lengths.values())
    print(f"  {'Run Length':<12} {'Count':>8} {'%':>8}")
    print(f"  " + "-" * 30)
    for rl in sorted(run_lengths.keys()):
        pct = 100 * run_lengths[rl] / total_runs if total_runs > 0 else 0
        print(f"  {rl:<12} {run_lengths[rl]:>8} {pct:>7.1f}%")

    mean_run = sum(rl * cnt for rl, cnt in run_lengths.items()) / total_runs if total_runs > 0 else 0
    print(f"  Mean run length: {mean_run:.3f}")
    pct_multi = 100 * sum(cnt for rl, cnt in run_lengths.items() if rl >= 2) / total_runs if total_runs > 0 else 0
    print(f"  Multi-token runs (>=2): {pct_multi:.1f}%")

    # --- Per-section stability ---
    print(f"\n--- Per-section carryover enrichment ---")
    for sec in sorted(section_total_pairs.keys()):
        sec_c = section_atom_total[sec].get('c', 0)
        sec_tot = section_total_tokens[sec]
        if sec_c < 20 or sec_tot < 100:
            continue
        sec_rate = sec_c / sec_tot
        sec_exp = sec_rate ** 2 * section_total_pairs[sec]
        sec_obs = section_pair_count[sec].get('c', 0)
        sec_enrich = sec_obs / sec_exp if sec_exp > 0 else 0
        print(f"  {sec}: obs={sec_obs} exp={sec_exp:.1f} enrich={sec_enrich:.3f}x (c-rate={100*sec_rate:.1f}%)")

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    actual_enrichment = c_pairs / c_expected if c_expected > 0 else 0
    pass_enrichment = actual_enrichment >= 1.3
    pass_midline = mid_line_pct >= 60

    print(f"\nc-c pair enrichment: {actual_enrichment:.3f}x (threshold >= 1.3x)")
    if c_z is not None:
        print(f"  z-score: {c_z:+.2f}")
    print(f"  {'PASS' if pass_enrichment else 'FAIL'}")

    print(f"\nc-c pairs at mid-line (0.3-0.7): {mid_line_pct:.1f}% (threshold >= 60%)")
    print(f"  {'PASS' if pass_midline else 'FAIL'}")

    overall = pass_enrichment and pass_midline
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")
    print(f"  c atoms {'DO' if overall else 'do NOT'} show positive carryover concentrated mid-line")


if __name__ == '__main__':
    main()
