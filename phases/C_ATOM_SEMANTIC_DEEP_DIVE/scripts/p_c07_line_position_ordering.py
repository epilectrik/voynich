"""
P-C7: c-initial vs h-initial line position ordering
=====================================================
Test whether c-initial tokens precede h-initial tokens within lines
(adjust THEN watch).

Predictions:
- Mean line position of c-initial < mean line position of h-initial
- Delta >= 0.05
- c-initial mean position in [0.35, 0.55] (mid-process)

Method:
1. For each Currier B token, extract MIDDLE initial atom
2. Compute fractional line position
3. Compare mean line position for c-initial vs h-initial vs k-initial vs e-initial
4. Within lines containing BOTH c-initial and h-initial, test ordering
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


def welch_t_test(x, y):
    """Welch's t-test for unequal variances."""
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        return 0.0, 1.0
    m1 = sum(x) / n1
    m2 = sum(y) / n2
    v1 = sum((xi - m1) ** 2 for xi in x) / (n1 - 1)
    v2 = sum((yi - m2) ** 2 for yi in y) / (n2 - 1)
    se = math.sqrt(v1 / n1 + v2 / n2) if (v1 / n1 + v2 / n2) > 0 else 1e-15
    t_stat = (m1 - m2) / se
    # Approximate p from normal for large N
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return t_stat, p


def binomial_p(successes, trials, p0=0.5):
    """Approximate binomial test using normal approximation."""
    if trials < 10:
        return 1.0
    observed = successes / trials
    se = math.sqrt(p0 * (1 - p0) / trials)
    z = (observed - p0) / se if se > 0 else 0
    return 1 - normal_cdf(z)  # one-tailed: observed > p0


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    print("=" * 70)
    print("P-C7: c-initial vs h-initial line position ordering")
    print("=" * 70)

    # Collect tokens organized by (folio, line)
    # Each token: (word, middle, initial_atom, position_in_line)
    line_tokens = defaultdict(list)

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
        line_tokens[key].append((w, mid, initial_atom))

    # Compute fractional line positions
    atom_positions = defaultdict(list)  # atom -> [frac_pos, ...]
    line_atom_positions = defaultdict(lambda: defaultdict(list))  # (folio,line) -> atom -> [frac_pos]

    section_atom_positions = defaultdict(lambda: defaultdict(list))

    for key, tokens in line_tokens.items():
        n = len(tokens)
        if n < 3:
            continue

        # Tokens are already in order from the transcript iterator

        fol = key[0]
        fa = decoder.analyze_folio(fol)
        section = fa.section if fa else 'UNK'

        for idx, (w, mid, initial_atom) in enumerate(tokens):
            frac = idx / (n - 1) if n > 1 else 0.5
            atom_positions[initial_atom].append(frac)
            line_atom_positions[key][initial_atom].append(frac)
            section_atom_positions[section][initial_atom].append(frac)

    # --- Full atom position ranking ---
    print(f"\n--- All atoms ranked by mean line position ---")
    atom_stats = []
    for atom in sorted(atom_positions.keys()):
        positions = atom_positions[atom]
        if len(positions) < 20:
            continue
        mean_pos = sum(positions) / len(positions)
        atom_stats.append((atom, mean_pos, len(positions)))

    atom_stats.sort(key=lambda x: x[1])
    print(f"{'Rank':<6} {'Atom':<6} {'Mean Pos':>10} {'N':>8}")
    print("-" * 34)
    c_pos_mean = None
    h_pos_mean = None
    for i, (atom, mean_p, n) in enumerate(atom_stats):
        marker = ""
        if atom == 'c':
            marker = " <-- c (TARGET)"
            c_pos_mean = mean_p
        elif atom == 'h':
            marker = " <-- h"
            h_pos_mean = mean_p
        elif atom == 'k':
            marker = " <-- k"
        elif atom == 'e':
            marker = " <-- e"
        print(f"{i+1:<6} {atom:<6} {mean_p:>9.4f} {n:>8}{marker}")

    # --- c vs h direct comparison ---
    c_positions = atom_positions.get('c', [])
    h_positions = atom_positions.get('h', [])

    c_mean = sum(c_positions) / len(c_positions) if c_positions else 0
    h_mean = sum(h_positions) / len(h_positions) if h_positions else 0
    delta = h_mean - c_mean

    t_stat, p_val = welch_t_test(c_positions, h_positions)

    print(f"\n--- c-initial vs h-initial line position ---")
    print(f"  c-initial mean: {c_mean:.4f} (N={len(c_positions)})")
    print(f"  h-initial mean: {h_mean:.4f} (N={len(h_positions)})")
    print(f"  Delta (h - c):  {delta:+.4f} (threshold >= +0.05)")
    print(f"  Welch t-test:   t={t_stat:.3f}, p={p_val:.6f}")

    # Also compare k and e
    k_positions = atom_positions.get('k', [])
    e_positions = atom_positions.get('e', [])
    k_mean = sum(k_positions) / len(k_positions) if k_positions else 0
    e_mean = sum(e_positions) / len(e_positions) if e_positions else 0

    print(f"\n  Context: kernel atom positions")
    print(f"    k-initial mean: {k_mean:.4f} (N={len(k_positions)})")
    print(f"    e-initial mean: {e_mean:.4f} (N={len(e_positions)})")
    print(f"    Expected from C873: e(0.404) < h(0.410) < k(0.443)")

    # --- Within-line paired ordering test ---
    print(f"\n--- Within-line c-before-h ordering test ---")
    c_before_h = 0
    h_before_c = 0
    tied = 0
    lines_with_both = 0

    for key, atom_pos_dict in line_atom_positions.items():
        c_pos_list = atom_pos_dict.get('c', [])
        h_pos_list = atom_pos_dict.get('h', [])

        if not c_pos_list or not h_pos_list:
            continue

        lines_with_both += 1
        # Compare mean positions within this line
        c_line_mean = sum(c_pos_list) / len(c_pos_list)
        h_line_mean = sum(h_pos_list) / len(h_pos_list)

        if c_line_mean < h_line_mean:
            c_before_h += 1
        elif h_line_mean < c_line_mean:
            h_before_c += 1
        else:
            tied += 1

    total_paired = c_before_h + h_before_c
    c_before_pct = 100 * c_before_h / total_paired if total_paired > 0 else 0
    binom_p = binomial_p(c_before_h, total_paired) if total_paired > 0 else 1.0

    print(f"  Lines with both c-initial and h-initial: {lines_with_both}")
    print(f"  c before h: {c_before_h} ({c_before_pct:.1f}%)")
    print(f"  h before c: {h_before_c} ({100 - c_before_pct:.1f}%)")
    print(f"  Tied: {tied}")
    print(f"  Binomial p (one-tailed, c > 50%): {binom_p:.4f}")

    # --- Position distribution by quintile ---
    print(f"\n--- c-initial position distribution by quintile ---")
    quintile_counts = [0] * 5
    for p in c_positions:
        q = min(int(p * 5), 4)
        quintile_counts[q] += 1
    total_c = len(c_positions)
    print(f"{'Quintile':<10} {'Count':>8} {'%':>8} {'Expected':>10}")
    for q in range(5):
        pct = 100 * quintile_counts[q] / total_c if total_c > 0 else 0
        print(f"Q{q+1} ({q*0.2:.1f}-{(q+1)*0.2:.1f}) {quintile_counts[q]:>6} {pct:>7.1f}% {100/5:>9.1f}%")

    # --- Per-section stability ---
    print(f"\n--- Per-section c vs h position ---")
    for sec in sorted(section_atom_positions.keys()):
        sec_c = section_atom_positions[sec].get('c', [])
        sec_h = section_atom_positions[sec].get('h', [])
        if len(sec_c) < 20 or len(sec_h) < 20:
            continue
        sc_mean = sum(sec_c) / len(sec_c)
        sh_mean = sum(sec_h) / len(sec_h)
        d = sh_mean - sc_mean
        print(f"  {sec}: c={sc_mean:.4f} h={sh_mean:.4f} delta={d:+.4f} (N_c={len(sec_c)}, N_h={len(sec_h)})")

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    pass_ordering = delta >= 0.05 and p_val < 0.05
    pass_position = 0.35 <= c_mean <= 0.55

    print(f"\nc before h ordering:")
    print(f"  Delta (h - c) = {delta:+.4f} (threshold >= +0.05)")
    print(f"  p-value = {p_val:.6f} (threshold < 0.05)")
    print(f"  {'PASS' if pass_ordering else 'FAIL'}")

    print(f"\nc-initial mean position in [0.35, 0.55]:")
    print(f"  Mean = {c_mean:.4f}")
    print(f"  {'PASS' if pass_position else 'FAIL'}")

    if total_paired > 0:
        pass_paired = c_before_pct > 50 and binom_p < 0.05
        print(f"\nWithin-line c-before-h:")
        print(f"  c first in {c_before_pct:.1f}% of paired lines")
        print(f"  {'PASS' if pass_paired else 'FAIL'}")

    overall = pass_ordering and pass_position
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")
    print(f"  c-initial tokens {'DO' if overall else 'do NOT'} precede h-initial as predicted")


if __name__ == '__main__':
    main()
