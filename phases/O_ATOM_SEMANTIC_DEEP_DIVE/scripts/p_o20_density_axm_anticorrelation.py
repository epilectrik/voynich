#!/usr/bin/env python3
"""
P-O20: o-density anti-correlates with AXM self-transition (preparation is transient)

If o = "ordnen" (arrange/prepare), folios with higher o-density should have LOWER
AXM self-transition rates (more preparation = less dwelling in the main loop).

This extends P-O9 (vessel hypothesis) with ordnen-specific thresholds and
deeper analysis:

Tests:
1. Per-folio Spearman correlation (o-density vs AXM self-transition)
2. Rank ALL atoms by AXM dwell anticorrelation
3. Quintile analysis (monotonic decrease expected)
4. Within-section stability
5. o vs other anti-AXM atoms comparison

Pass: rho < -0.30 AND ranked top 3 AND >= 4/5 quintiles monotonically decreasing
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


def spearman_rho(x, y):
    """Compute Spearman rank correlation and two-tailed p-value."""
    n = len(x)
    if n < 5:
        return 0.0, 1.0

    def rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j + 1]] == vals[indexed[j]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(x)
    ry = rank(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return 0.0, 1.0
    rho = num / (den_x * den_y)
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-15))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()

    ALL_ATOMS = list('abcdefghiklmnopqrsty')

    # Build per-folio data
    folio_tokens = defaultdict(list)  # folio -> [(word, middle, macro_state)]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle if m.middle else ''
        ts = decoder.analyze_token(w)
        macro = ts.macro_state if ts else None
        folio_tokens[token.folio].append((w, mid, macro))

    # Get folio sections
    folio_sections = {}
    for folio in folio_tokens:
        fi = decoder.analyze_folio(folio)
        if fi and fi.section:
            folio_sections[folio] = fi.section

    # Compute per-folio metrics
    folio_atom_density = defaultdict(dict)  # atom -> folio -> density
    folio_axm_self = {}

    for folio, toks in folio_tokens.items():
        total = len(toks)
        if total < 20:
            continue

        # Atom densities (based on initial atom of MIDDLE)
        atom_counts = defaultdict(int)
        for w, mid, macro in toks:
            if mid and len(mid) >= 1:
                atom_counts[mid[0]] += 1

        for a in ALL_ATOMS:
            folio_atom_density[a][folio] = atom_counts.get(a, 0) / total

        # AXM self-transition rate
        axm_first = 0
        axm_both = 0
        for i in range(len(toks) - 1):
            if toks[i][2] == 'AXM':
                axm_first += 1
                if toks[i + 1][2] == 'AXM':
                    axm_both += 1

        if axm_first >= 5:
            folio_axm_self[folio] = axm_both / axm_first

    print("=" * 70)
    print("P-O20: o-density anti-correlates with AXM self-transition (ordnen)")
    print("=" * 70)
    print()

    # ---- TEST 1: o-density vs AXM self-transition ----
    print("-" * 70)
    print("TEST 1: Per-folio o-density vs AXM self-transition")
    print("-" * 70)
    print()

    common_folios = sorted(set(folio_atom_density['o'].keys()) & set(folio_axm_self.keys()))
    print(f"Folios with both metrics: {len(common_folios)}")

    rho_o = 0.0
    p_o = 1.0
    if len(common_folios) >= 10:
        x_o = [folio_atom_density['o'][f] for f in common_folios]
        y_axm = [folio_axm_self[f] for f in common_folios]
        rho_o, p_o = spearman_rho(x_o, y_axm)
        print(f"  Spearman rho = {rho_o:+.4f}, p = {p_o:.6f}")
        print(f"  Mean o-density: {sum(x_o)/len(x_o):.4f}")
        print(f"  Mean AXM-self: {sum(y_axm)/len(y_axm):.4f}")
    else:
        print("  INSUFFICIENT DATA")

    # ---- TEST 2: Rank ALL atoms by AXM dwell anticorrelation ----
    print()
    print("-" * 70)
    print("TEST 2: All atoms ranked by AXM self-transition correlation")
    print("-" * 70)
    print()

    atom_corrs = []
    for a in ALL_ATOMS:
        if a not in folio_atom_density:
            continue
        cf = sorted(set(folio_atom_density[a].keys()) & set(folio_axm_self.keys()))
        if len(cf) < 10:
            continue
        xa = [folio_atom_density[a][f] for f in cf]
        ya = [folio_axm_self[f] for f in cf]
        r, pv = spearman_rho(xa, ya)
        atom_corrs.append((a, r, pv, len(cf)))

    atom_corrs.sort(key=lambda x: x[1])  # Most anti-AXM first

    print(f"{'Rank':<5} {'Atom':<5} {'rho':>8} {'p-value':>10} {'N':>5}")
    print("-" * 38)
    o_rank_overall = None
    for rank, (a, r, pv, n) in enumerate(atom_corrs, 1):
        marker = " <-- O" if a == 'o' else ""
        if a == 'o':
            o_rank_overall = rank
        print(f"  {rank:<3} {a:<4} {r:>+.4f} {pv:>10.6f} {n:>5}{marker}")

    print()
    print(f"  o rank: #{o_rank_overall} of {len(atom_corrs)}")

    # ---- TEST 3: Quintile analysis ----
    print()
    print("-" * 70)
    print("TEST 3: Quintile analysis (o-density -> AXM self-transition)")
    print("-" * 70)
    print()

    quintile_mono = 0
    if len(common_folios) >= 15:
        sorted_by_o = sorted(range(len(common_folios)), key=lambda i: x_o[i])
        q_size = len(sorted_by_o) // 5
        quintile_means = []

        if q_size > 0:
            print(f"{'Quintile':<10} {'o-density':>10} {'AXM-self':>10} {'N':>5}")
            print("-" * 40)
            for qi in range(5):
                start = qi * q_size
                end = start + q_size if qi < 4 else len(sorted_by_o)
                indices = sorted_by_o[start:end]
                mean_o = sum(x_o[i] for i in indices) / len(indices)
                mean_axm = sum(y_axm[i] for i in indices) / len(indices)
                quintile_means.append(mean_axm)
                print(f"  Q{qi+1:<7} {mean_o:>10.4f} {mean_axm:>10.4f} {len(indices):>5}")

            # Check monotonic decrease
            for qi in range(1, 5):
                if quintile_means[qi] <= quintile_means[qi - 1]:
                    quintile_mono += 1

            print()
            print(f"  Monotonically decreasing transitions: {quintile_mono}/4")
            print(f"  (Need >= 3/4 for weak monotonicity, 4/4 for strong)")
    else:
        print("  INSUFFICIENT DATA for quintile analysis")

    # ---- TEST 4: Within-section stability ----
    print()
    print("-" * 70)
    print("TEST 4: Within-section o-AXM correlation")
    print("-" * 70)
    print()

    section_folios = defaultdict(list)
    for f in common_folios:
        sec = folio_sections.get(f, 'UNK')
        section_folios[sec].append(f)

    section_results = {}
    sections_negative = 0
    sections_tested = 0
    for sec in sorted(section_folios.keys()):
        sf = section_folios[sec]
        if len(sf) < 8:
            print(f"  Section {sec}: N={len(sf)} (too few)")
            continue
        xs = [folio_atom_density['o'][f] for f in sf]
        ys = [folio_axm_self[f] for f in sf]
        r, pv = spearman_rho(xs, ys)
        section_results[sec] = (r, pv, len(sf))
        sections_tested += 1
        if r < 0:
            sections_negative += 1
        print(f"  Section {sec}: rho={r:+.4f}, p={pv:.4f}, N={len(sf)}")

    # ---- TEST 5: o vs other anti-AXM atoms ----
    print()
    print("-" * 70)
    print("TEST 5: o compared to other strong anti-AXM atoms")
    print("-" * 70)
    print()

    # Get top 5 anti-AXM atoms
    top5 = atom_corrs[:5]
    for a, r, pv, n in top5:
        marker = " <-- O" if a == 'o' else ""
        print(f"  {a}: rho={r:+.4f}, p={pv:.6f}, N={n}{marker}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O20 o-density anti-AXM dwell (ordnen)")
    print("=" * 70)

    pass_rho = rho_o < -0.30
    pass_rank = o_rank_overall is not None and o_rank_overall <= 3
    pass_quintile = quintile_mono >= 3  # At least 3/4 monotonic
    pass_section = sections_tested > 0 and sections_negative >= max(1, sections_tested // 2)
    pass_p = p_o < 0.01

    results = [
        ("rho < -0.30", pass_rho,
         f"rho = {rho_o:+.4f}"),
        ("Ranked top 3 anti-AXM", pass_rank,
         f"rank #{o_rank_overall}" if o_rank_overall else "N/A"),
        ("Quintile monotonicity >= 3/4", pass_quintile,
         f"{quintile_mono}/4 monotonic"),
        ("Section stability (majority negative)", pass_section,
         f"{sections_negative}/{sections_tested} negative"),
        ("p-value < 0.01", pass_p,
         f"p = {p_o:.6f}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_rho and pass_rank and pass_quintile
    print()
    print(f"  PRIMARY CRITERION (rho<-0.30 AND top 3 AND quintile>=3/4): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
