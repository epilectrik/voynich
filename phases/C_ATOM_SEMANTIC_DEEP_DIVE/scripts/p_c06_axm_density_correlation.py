"""
P-C6: c-density vs AXM self-transition correlation
=====================================================
Test whether c-density correlates POSITIVELY with AXM dwell
(adjustments sustain execution).

Predictions (c="adjust" → sustains main loop):
- rho(c-density, AXM self-transition) > +0.15 (pro-AXM)
- This is OPPOSITE of o which is anti-AXM (C1384 shows k positive, a/o/d negative)

Method:
1. Per-folio: compute c-initial density (c-initial count / total tokens)
2. Per-folio: compute AXM self-transition rate
3. Spearman correlation
4. Rank all atoms by AXM correlation
5. Quintile analysis
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


def spearman_rho(x, y):
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

    print("=" * 70)
    print("P-C6: c-density vs AXM self-transition correlation")
    print("=" * 70)

    # Per-folio: collect atom densities and macro-state sequences
    folio_tokens = defaultdict(list)       # folio -> [(initial_atom, macro_state), ...]
    folio_atom_count = defaultdict(lambda: defaultdict(int))
    folio_total = defaultdict(int)
    folio_section = {}

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

        fol = token.folio
        folio_tokens[fol].append((initial_atom, ms))
        folio_atom_count[fol][initial_atom] += 1
        folio_total[fol] += 1

        fa = decoder.analyze_folio(fol)
        if fa and fa.section:
            folio_section[fol] = fa.section

    # Compute per-folio AXM self-transition rate
    folio_axm_self = {}
    for fol, toks in folio_tokens.items():
        axm_first = 0
        axm_self = 0
        for i in range(len(toks) - 1):
            if toks[i][1] == 'AXM':
                axm_first += 1
                if toks[i + 1][1] == 'AXM':
                    axm_self += 1
        if axm_first >= 10:
            folio_axm_self[fol] = axm_self / axm_first

    valid_folios = sorted(folio_axm_self.keys())
    print(f"\nFolios with sufficient AXM data: {len(valid_folios)}")

    # Compute per-folio atom densities for ALL atoms
    all_atoms = set()
    for fol in valid_folios:
        all_atoms.update(folio_atom_count[fol].keys())
    all_atoms = sorted(all_atoms)

    # Rank all atoms by AXM correlation
    print(f"\n--- All atoms ranked by correlation with AXM self-transition ---")
    atom_correlations = []
    for atom in all_atoms:
        densities = []
        axm_rates = []
        for fol in valid_folios:
            d = folio_atom_count[fol].get(atom, 0) / folio_total[fol] if folio_total[fol] > 0 else 0
            densities.append(d)
            axm_rates.append(folio_axm_self[fol])

        # Require atom present in at least 20 folios
        nonzero = sum(1 for d in densities if d > 0)
        if nonzero < 20:
            continue

        rho, p = spearman_rho(densities, axm_rates)
        total_count = sum(folio_atom_count[fol].get(atom, 0) for fol in valid_folios)
        atom_correlations.append((atom, rho, p, total_count))

    atom_correlations.sort(key=lambda x: -x[1])

    print(f"{'Rank':<6} {'Atom':<6} {'rho':>8} {'p-val':>10} {'N tokens':>10} {'Sign':>6}")
    print("-" * 50)
    c_rank = None
    for i, (atom, rho, p, n) in enumerate(atom_correlations):
        sign = '+' if rho > 0 else '-'
        marker = " <-- c (TARGET)" if atom == 'c' else ""
        if atom == 'c':
            c_rank = i + 1
        print(f"{i+1:<6} {atom:<6} {rho:>+7.3f} {p:>10.4f} {n:>10} {sign:>6}{marker}")

    # --- c-specific detailed analysis ---
    c_densities = []
    axm_rates = []
    for fol in valid_folios:
        d = folio_atom_count[fol].get('c', 0) / folio_total[fol] if folio_total[fol] > 0 else 0
        c_densities.append(d)
        axm_rates.append(folio_axm_self[fol])

    c_rho, c_p = spearman_rho(c_densities, axm_rates)

    print(f"\n--- c-initial density vs AXM self-transition ---")
    print(f"  Spearman rho: {c_rho:+.4f}")
    print(f"  p-value: {c_p:.4f}")
    print(f"  c rank among all atoms: {c_rank}/{len(atom_correlations)}")

    # --- Quintile analysis ---
    print(f"\n--- Quintile analysis: folios sorted by c-density ---")
    indexed = sorted(range(len(valid_folios)), key=lambda i: c_densities[i])
    q_size = len(indexed) // 5
    print(f"{'Quintile':<10} {'c-density':>12} {'AXM self':>10} {'N folios':>10}")
    print("-" * 45)
    for q in range(5):
        start = q * q_size
        end = start + q_size if q < 4 else len(indexed)
        q_idx = indexed[start:end]
        mean_d = sum(c_densities[i] for i in q_idx) / len(q_idx)
        mean_a = sum(axm_rates[i] for i in q_idx) / len(q_idx)
        print(f"Q{q+1:<9} {mean_d:>11.4f} {mean_a:>9.3f} {len(q_idx):>10}")

    # --- Comparison to o (should be opposite sign) ---
    o_densities = []
    for fol in valid_folios:
        d = folio_atom_count[fol].get('o', 0) / folio_total[fol] if folio_total[fol] > 0 else 0
        o_densities.append(d)
    o_rho, o_p = spearman_rho(o_densities, axm_rates)

    print(f"\n--- Comparison: c vs o ---")
    print(f"  c rho: {c_rho:+.4f} (p={c_p:.4f})")
    print(f"  o rho: {o_rho:+.4f} (p={o_p:.4f})")
    print(f"  Opposite signs: {'YES' if (c_rho > 0) != (o_rho > 0) else 'NO'}")

    # --- Per-section stability ---
    print(f"\n--- Per-section stability ---")
    for sec in sorted(set(folio_section.values())):
        sec_folios = [f for f in valid_folios if folio_section.get(f) == sec]
        if len(sec_folios) < 10:
            continue
        sec_c = [folio_atom_count[f].get('c', 0) / folio_total[f] for f in sec_folios]
        sec_axm = [folio_axm_self[f] for f in sec_folios]
        rho, p = spearman_rho(sec_c, sec_axm)
        print(f"  {sec}: rho={rho:+.3f} p={p:.4f} (N={len(sec_folios)})")

    # --- VERDICT ---
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    pass_rho = c_rho > 0.15 and c_p < 0.05

    print(f"\nc-density vs AXM self-transition:")
    print(f"  rho = {c_rho:+.4f} (threshold > +0.15)")
    print(f"  p   = {c_p:.4f} (threshold < 0.05)")
    print(f"  {'PASS' if pass_rho else 'FAIL'}")

    if c_rho > 0 and o_rho < 0:
        print(f"\n  c and o have OPPOSITE signs as predicted (c pro-AXM, o anti-AXM)")
    elif c_rho > 0:
        print(f"\n  c is positive as predicted but o is also positive (unexpected)")
    else:
        print(f"\n  c is NEGATIVE — NOT pro-AXM as predicted")

    print(f"\nOVERALL: {'PASS' if pass_rho else 'FAIL'}")


if __name__ == '__main__':
    main()
