#!/usr/bin/env python3
"""
P-O4: k-o anti-correlation as complementary line occupancy

Test whether k-initial and o-initial tokens avoid sharing lines.
If k=heat and o=vessel, they describe different aspects and occupy different lines.

Tests:
1. Per-line: does this line contain o-initial? Does it contain k-initial?
2. K-density on o-lines vs non-o-lines. O-density on k-lines vs non-k-lines.
3. Spearman rho: o-initial fraction vs k-initial fraction across lines with >= 4 tokens.
4. Full pairwise initial-atom correlation matrix.
5. Per-section stability.

Pass criterion: k-density on o-lines <= 0.75x AND line-level rho < -0.30 (p < 0.001).
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


def spearman_rho(x_vals, y_vals):
    """Compute Spearman rank correlation and approximate p-value."""
    n = len(x_vals)
    if n < 3:
        return 0.0, 1.0

    def rank_data(vals):
        indexed = sorted(enumerate(vals), key=lambda p: p[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx][0]] = avg_rank
            i = j + 1
        return ranks

    rx = rank_data(x_vals)
    ry = rank_data(y_vals)

    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n

    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    std_rx = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    std_ry = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))

    if std_rx == 0 or std_ry == 0:
        return 0.0, 1.0

    rho = cov / (std_rx * std_ry)

    # Approximate p-value using t-distribution approximation
    if abs(rho) >= 1.0:
        return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho * rho))
    # Use normal approximation for large n
    p_val = 2.0 * (1.0 - normal_cdf(abs(t_stat)))
    return rho, p_val


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    # Step 1: Collect per-line data
    # line_key = (folio, line_id) -> list of initial atoms
    line_atoms = defaultdict(list)
    line_totals = defaultdict(int)
    folio_sections = {}

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        folio = token.folio
        line_id = token.line
        key = (folio, line_id)

        initial = m.middle[0]
        line_atoms[key].append(initial)
        line_totals[key] += 1

        if folio not in folio_sections:
            try:
                fa = decoder.analyze_folio(folio)
                folio_sections[folio] = fa.section if fa and fa.section else 'UNK'
            except Exception:
                folio_sections[folio] = 'UNK'

    print("=" * 70)
    print("P-O4: k-o anti-correlation as complementary line occupancy")
    print("=" * 70)
    print()
    print(f"Total lines with classified tokens: {len(line_atoms)}")

    # Pre-compute per-line atom counts and fractions
    line_atom_counts = {}  # key -> {atom: count}
    for key, atoms in line_atoms.items():
        counts = defaultdict(int)
        for a in atoms:
            counts[a] += 1
        line_atom_counts[key] = dict(counts)

    # Determine all atoms with sufficient representation
    all_atoms = set()
    atom_line_presence = defaultdict(int)  # atom -> number of lines containing it
    for key, counts in line_atom_counts.items():
        for atom in counts:
            all_atoms.add(atom)
            atom_line_presence[atom] += 1

    valid_atoms = sorted([a for a in all_atoms if atom_line_presence[a] >= 20])

    # ---- TEST 1 & 2: k-density on o-lines and vice versa ----
    print()
    print("-" * 70)
    print("TEST 1 & 2: Cross-density analysis")
    print("-" * 70)
    print()

    # o-lines vs non-o-lines
    o_lines = set(k for k, counts in line_atom_counts.items() if 'o' in counts)
    non_o_lines = set(line_atom_counts.keys()) - o_lines
    k_lines = set(k for k, counts in line_atom_counts.items() if 'k' in counts)
    non_k_lines = set(line_atom_counts.keys()) - k_lines

    def atom_density_on_lines(atom, line_set):
        """Compute average fraction of tokens that are atom-initial on given lines."""
        if not line_set:
            return 0.0
        fracs = []
        for key in line_set:
            total = line_totals[key]
            count = line_atom_counts[key].get(atom, 0)
            if total > 0:
                fracs.append(count / total)
        return sum(fracs) / len(fracs) if fracs else 0.0

    k_on_o = atom_density_on_lines('k', o_lines)
    k_on_non_o = atom_density_on_lines('k', non_o_lines)
    k_ratio = k_on_o / k_on_non_o if k_on_non_o > 0 else 0

    o_on_k = atom_density_on_lines('o', k_lines)
    o_on_non_k = atom_density_on_lines('o', non_k_lines)
    o_ratio = o_on_k / o_on_non_k if o_on_non_k > 0 else 0

    print(f"  k-initial density on o-lines:     {k_on_o:.4f}")
    print(f"  k-initial density on non-o-lines:  {k_on_non_o:.4f}")
    print(f"  Ratio: {k_ratio:.3f}x")
    print()
    print(f"  o-initial density on k-lines:     {o_on_k:.4f}")
    print(f"  o-initial density on non-k-lines:  {o_on_non_k:.4f}")
    print(f"  Ratio: {o_ratio:.3f}x")
    print()

    # Co-occurrence table
    both_ko = len(o_lines & k_lines)
    only_k = len(k_lines - o_lines)
    only_o = len(o_lines - k_lines)
    neither = len(set(line_atom_counts.keys()) - o_lines - k_lines)
    total_lines = len(line_atom_counts)

    print(f"  Co-occurrence (lines): both k&o={both_ko}, k-only={only_k}, "
          f"o-only={only_o}, neither={neither}")
    expected_both = len(k_lines) * len(o_lines) / total_lines if total_lines > 0 else 0
    print(f"  Expected co-occurrence (independent): {expected_both:.1f}")
    cooc_ratio = both_ko / expected_both if expected_both > 0 else 0
    print(f"  Co-occurrence ratio: {cooc_ratio:.3f}x (< 1 = avoidance)")
    print()

    # ---- TEST 3: Spearman correlation ----
    print("-" * 70)
    print("TEST 3: Spearman correlation — o-initial vs k-initial fractions per line")
    print("-" * 70)
    print()

    MIN_LINE_TOKENS = 4
    o_fracs = []
    k_fracs = []
    for key in line_atom_counts:
        total = line_totals[key]
        if total < MIN_LINE_TOKENS:
            continue
        o_f = line_atom_counts[key].get('o', 0) / total
        k_f = line_atom_counts[key].get('k', 0) / total
        o_fracs.append(o_f)
        k_fracs.append(k_f)

    rho_ko, p_ko = spearman_rho(k_fracs, o_fracs)
    print(f"  Lines with >= {MIN_LINE_TOKENS} tokens: {len(o_fracs)}")
    print(f"  Spearman rho (k vs o): {rho_ko:.4f}, p = {p_ko:.8f}")
    if p_ko < 0.001:
        print(f"  Significance: p < 0.001 ***")
    elif p_ko < 0.01:
        print(f"  Significance: p < 0.01 **")
    elif p_ko < 0.05:
        print(f"  Significance: p < 0.05 *")
    else:
        print(f"  Significance: not significant")
    print()

    # ---- TEST 4: Full pairwise correlation matrix ----
    print("-" * 70)
    print("TEST 4: Pairwise initial-atom line-fraction correlations")
    print("-" * 70)
    print()

    # Pre-compute per-line fractions for all valid atoms
    atom_fracs_per_line = {a: [] for a in valid_atoms}
    valid_lines = []
    for key in line_atom_counts:
        total = line_totals[key]
        if total < MIN_LINE_TOKENS:
            continue
        valid_lines.append(key)
        for a in valid_atoms:
            atom_fracs_per_line[a].append(line_atom_counts[key].get(a, 0) / total)

    # Compute all pairwise correlations
    pair_rhos = []
    for i, a1 in enumerate(valid_atoms):
        for j, a2 in enumerate(valid_atoms):
            if j <= i:
                continue
            rho_pair, p_pair = spearman_rho(atom_fracs_per_line[a1], atom_fracs_per_line[a2])
            pair_rhos.append((a1, a2, rho_pair, p_pair))

    # Sort by rho (most negative first)
    pair_rhos.sort(key=lambda x: x[2])

    print(f"  Most anti-correlated pairs (top 10):")
    print(f"  {'Pair':<8} {'rho':>8} {'p-value':>12}")
    print("  " + "-" * 30)
    ko_rank = None
    for rank, (a1, a2, rho_p, p_p) in enumerate(pair_rhos[:10], 1):
        marker = " <--" if (a1 == 'k' and a2 == 'o') or (a1 == 'o' and a2 == 'k') else ""
        print(f"  {a1}-{a2:<5} {rho_p:>8.4f} {p_p:>12.8f}{marker}")

    # Find k-o rank
    for rank, (a1, a2, rho_p, p_p) in enumerate(pair_rhos, 1):
        if (a1 == 'k' and a2 == 'o') or (a1 == 'o' and a2 == 'k'):
            ko_rank = rank
            break

    print()
    if ko_rank is not None:
        print(f"  k-o pair rank among {len(pair_rhos)} pairs: #{ko_rank} "
              f"(1 = most anti-correlated)")
    print()

    print(f"  Most positively correlated pairs (top 10):")
    print(f"  {'Pair':<8} {'rho':>8} {'p-value':>12}")
    print("  " + "-" * 30)
    for a1, a2, rho_p, p_p in pair_rhos[-10:][::-1]:
        print(f"  {a1}-{a2:<5} {rho_p:>8.4f} {p_p:>12.8f}")
    print()

    # ---- TEST 5: Per-section stability ----
    print("-" * 70)
    print("TEST 5: Per-section stability of k-o anti-correlation")
    print("-" * 70)
    print()

    section_lines = defaultdict(list)  # section -> list of (o_frac, k_frac)
    for key in line_atom_counts:
        total = line_totals[key]
        if total < MIN_LINE_TOKENS:
            continue
        folio = key[0]
        section = folio_sections.get(folio, 'UNK')
        o_f = line_atom_counts[key].get('o', 0) / total
        k_f = line_atom_counts[key].get('k', 0) / total
        section_lines[section].append((o_f, k_f))

    sections_anticorr = 0
    sections_tested = 0

    for section in sorted(section_lines.keys()):
        pairs = section_lines[section]
        if len(pairs) < 20:
            continue
        sections_tested += 1
        o_vals = [p[0] for p in pairs]
        k_vals = [p[1] for p in pairs]
        rho_sec, p_sec = spearman_rho(k_vals, o_vals)
        anticorr = rho_sec < -0.10
        if anticorr:
            sections_anticorr += 1

        # Also compute k-density ratio for this section
        o_lines_sec = set()
        non_o_lines_sec = set()
        for idx, key in enumerate(line_atom_counts):
            total = line_totals[key]
            if total < MIN_LINE_TOKENS:
                continue
            folio = key[0]
            if folio_sections.get(folio, 'UNK') != section:
                continue
            if 'o' in line_atom_counts[key]:
                o_lines_sec.add(key)
            else:
                non_o_lines_sec.add(key)

        k_on_o_sec = atom_density_on_lines('k', o_lines_sec)
        k_on_non_o_sec = atom_density_on_lines('k', non_o_lines_sec)
        ratio_sec = k_on_o_sec / k_on_non_o_sec if k_on_non_o_sec > 0 else 0

        print(f"  Section {section:>6} (N={len(pairs):>5}): rho={rho_sec:>7.4f}, p={p_sec:.6f}, "
              f"k-density ratio={ratio_sec:.3f}x {'[ANTI]' if anticorr else '[WEAK]'}")

    print()
    print(f"  Sections with anti-correlation (rho < -0.10): {sections_anticorr}/{sections_tested}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O4 k-o complementary line occupancy")
    print("=" * 70)

    pass_density = k_ratio <= 0.75
    pass_rho = rho_ko < -0.30
    pass_rho_p = p_ko < 0.001
    pass_section = sections_anticorr >= sections_tested * 0.5 if sections_tested > 0 else False
    pass_rank = ko_rank is not None and ko_rank <= 5

    results = [
        ("k-density on o-lines <= 0.75x", pass_density,
         f"{k_ratio:.3f}x"),
        ("Spearman rho < -0.30", pass_rho,
         f"rho = {rho_ko:.4f}"),
        ("Spearman p < 0.001", pass_rho_p,
         f"p = {p_ko:.8f}"),
        ("k-o among top 5 most anti-correlated", pass_rank,
         f"rank #{ko_rank}/{len(pair_rhos)}" if ko_rank else "N/A"),
        ("Section stability (>= 50% sections anti-correlated)", pass_section,
         f"{sections_anticorr}/{sections_tested}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_density and pass_rho and pass_rho_p
    print()
    print(f"  PRIMARY CRITERION (density <= 0.75x AND rho < -0.30, p < 0.001): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
