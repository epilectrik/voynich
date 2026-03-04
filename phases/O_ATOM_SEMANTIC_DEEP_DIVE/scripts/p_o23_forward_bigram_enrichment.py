#!/usr/bin/env python3
"""
P-O23: o-terminal -> k-initial forward bigram enrichment (prepare THEN heat)

If o = "ordnen" (prepare), then o-terminal MIDDLEs should be followed by
k-initial MIDDLEs at enriched rates — the temporal "prepare then heat" signal
at the cross-token boundary.

This is the OPPOSITE direction from P-O7 (which tested k->o and found
enrichment). The ordnen hypothesis specifically predicts o->k should be
strong (prepare feeds into heat), and critically o->k > k->o (preparation
is unidirectional — you prepare BEFORE acting, not after).

Tests:
1. P(next_initial=k | terminal=o) vs P(initial=k) baseline -> enrichment
2. Also: P(next_initial=e | terminal=o) and P(next_initial=h | terminal=o)
3. Key comparison: o->k enrichment vs k->o enrichment (ordnen predicts o->k > k->o)
4. Rank: which terminal atoms most strongly predict k-initial following?
5. Controls: e->k (known process sequence), d->k, y->k (no prediction)

Pass criterion: o->k enrichment >= 1.2x AND o->k > k->o AND o->k ranked
               in top 5 among all terminal atoms for predicting k-initial
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology


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


def chi2_1df_p(chi2_val):
    """Approximate p-value for chi-square with 1 df."""
    if chi2_val <= 0:
        return 1.0
    z = math.sqrt(chi2_val)
    return 2.0 * (1.0 - normal_cdf(z))


def main():
    tx = Transcript()
    morph = Morphology()

    # ---- Build cross-token TERMINAL(N) -> INITIAL(N+1) bigram table ----
    line_middles = defaultdict(list)  # (folio, line) -> [middle, ...]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        line_key = (token.folio, token.line)
        line_middles[line_key].append(m.middle)

    # Build bigram counts
    terminal_initial = defaultdict(lambda: defaultdict(int))
    terminal_total = defaultdict(int)
    initial_total = defaultdict(int)
    grand_total = 0

    for line_key in line_middles:
        middles = line_middles[line_key]
        for i in range(len(middles) - 1):
            term_atom = middles[i][-1]    # TERMINAL of current
            init_atom = middles[i + 1][0]  # INITIAL of next

            terminal_initial[term_atom][init_atom] += 1
            terminal_total[term_atom] += 1
            initial_total[init_atom] += 1
            grand_total += 1

    print("=" * 70)
    print("P-O23: o-terminal -> k-initial forward bigram (prepare THEN heat)")
    print("=" * 70)
    print()
    print(f"Total cross-token bigrams: {grand_total}")
    print(f"Unique terminal atoms: {len(terminal_total)}")
    print(f"Unique initial atoms: {len(initial_total)}")
    print()

    # Baseline: P(initial=k)
    p_k_init = initial_total.get('k', 0) / grand_total if grand_total > 0 else 0
    print(f"Baseline P(initial=k) = {initial_total.get('k', 0)}/{grand_total} = {p_k_init:.4f}")
    print()

    # ---- TEST 1: o->k enrichment ----
    print("-" * 70)
    print("TEST 1: o-terminal -> k-initial enrichment")
    print("-" * 70)
    print()

    o_term_total = terminal_total.get('o', 0)
    o_to_k = terminal_initial.get('o', {}).get('k', 0)
    p_o_to_k = o_to_k / o_term_total if o_term_total > 0 else 0
    o_to_k_enrich = p_o_to_k / p_k_init if p_k_init > 0 else 0

    print(f"  o-terminal total transitions: {o_term_total}")
    print(f"  o-terminal -> k-initial count: {o_to_k}")
    print(f"  P(next_initial=k | terminal=o): {p_o_to_k:.4f}")
    print(f"  Baseline P(initial=k): {p_k_init:.4f}")
    print(f"  Enrichment: {o_to_k_enrich:.3f}x")

    # Chi-square for o->k
    if o_term_total > 0 and grand_total > 0:
        a = o_to_k
        b = o_term_total - o_to_k
        c = initial_total.get('k', 0) - o_to_k
        d = (grand_total - o_term_total) - c
        total_t = a + b + c + d
        if total_t > 0:
            exp_a = (a + b) * (a + c) / total_t
            exp_b = (a + b) * (b + d) / total_t
            exp_c = (c + d) * (a + c) / total_t
            exp_d = (c + d) * (b + d) / total_t
            chi2 = sum((obs - exp) ** 2 / exp if exp > 0 else 0
                       for obs, exp in [(a, exp_a), (b, exp_b), (c, exp_c), (d, exp_d)])
            chi2_p = chi2_1df_p(chi2)
            print(f"  Chi-square: {chi2:.3f}, p = {chi2_p:.6f}")

    # ---- TEST 2: o-terminal -> other kernel atoms ----
    print()
    print("-" * 70)
    print("TEST 2: o-terminal -> all kernel atoms")
    print("-" * 70)
    print()

    for target_init in ['k', 'e', 'h']:
        p_base = initial_total.get(target_init, 0) / grand_total if grand_total > 0 else 0
        o_to_target = terminal_initial.get('o', {}).get(target_init, 0)
        p_cond = o_to_target / o_term_total if o_term_total > 0 else 0
        enrich = p_cond / p_base if p_base > 0 else 0
        label = {'k': 'heat', 'e': 'cool', 'h': 'watch'}[target_init]
        print(f"  o-terminal -> {target_init}-initial ({label}): "
              f"{o_to_target}/{o_term_total} = {p_cond:.4f}, "
              f"baseline {p_base:.4f}, enrichment {enrich:.3f}x")

    # ---- TEST 3: Key comparison — o->k vs k->o ----
    print()
    print("-" * 70)
    print("TEST 3: Directional asymmetry — o->k vs k->o")
    print("-" * 70)
    print()

    k_term_total = terminal_total.get('k', 0)
    k_to_o = terminal_initial.get('k', {}).get('o', 0)
    p_o_init = initial_total.get('o', 0) / grand_total if grand_total > 0 else 0
    p_k_to_o = k_to_o / k_term_total if k_term_total > 0 else 0
    k_to_o_enrich = p_k_to_o / p_o_init if p_o_init > 0 else 0

    print(f"  o-terminal -> k-initial: {o_to_k}/{o_term_total} = {p_o_to_k:.4f}, enrichment {o_to_k_enrich:.3f}x")
    print(f"  k-terminal -> o-initial: {k_to_o}/{k_term_total} = {p_k_to_o:.4f}, enrichment {k_to_o_enrich:.3f}x")
    print()
    o_to_k_gt_k_to_o = o_to_k_enrich > k_to_o_enrich
    print(f"  o->k enrichment > k->o enrichment: {'YES' if o_to_k_gt_k_to_o else 'NO'}")
    print(f"  Ratio: {o_to_k_enrich / k_to_o_enrich:.3f}x" if k_to_o_enrich > 0 else "  Ratio: inf (k->o = 0)")
    print(f"  Ordnen prediction (o->k > k->o): {'CONFIRMED' if o_to_k_gt_k_to_o else 'FALSIFIED'}")

    # ---- TEST 4: Rank all terminal atoms by k-initial enrichment ----
    print()
    print("-" * 70)
    print("TEST 4: All terminal atoms ranked by -> k-initial enrichment")
    print("-" * 70)
    print()

    term_to_k_ranking = []
    for term_atom in sorted(terminal_total.keys()):
        if terminal_total[term_atom] < 20:
            continue
        n_to_k = terminal_initial[term_atom].get('k', 0)
        p_cond = n_to_k / terminal_total[term_atom]
        enrich = p_cond / p_k_init if p_k_init > 0 else 0
        term_to_k_ranking.append((term_atom, n_to_k, terminal_total[term_atom], p_cond, enrich))

    term_to_k_ranking.sort(key=lambda x: -x[4])

    print(f"  {'Rank':<5} {'Term':<5} {'->k count':>10} {'Term N':>8} {'P(->k)':>9} {'Enrichment':>11}")
    print(f"  {'-'*52}")

    o_rank_in_k = None
    for rank, (atom, cnt, total, p_c, enrich) in enumerate(term_to_k_ranking, 1):
        marker = ""
        if atom == 'o':
            marker = " <-- o (PREDICTED)"
            o_rank_in_k = rank
        elif atom in ('e', 'h', 'k'):
            marker = f" <-- {atom} (kernel)"
        elif atom in ('d', 'y'):
            marker = f" <-- {atom} (control)"
        print(f"  {rank:<3} {atom:<4} {cnt:>10} {total:>8} {p_c:>8.4f} {enrich:>10.3f}x{marker}")

    print()
    print(f"  o rank for predicting k-initial: #{o_rank_in_k} of {len(term_to_k_ranking)}")

    # ---- TEST 5: Controls — e->k, d->k, y->k ----
    print()
    print("-" * 70)
    print("TEST 5: Control comparisons")
    print("-" * 70)
    print()

    control_atoms = {'e': 'cool->heat (known sequence)',
                     'd': 'seal->heat (no prediction)',
                     'y': 'end->heat (no prediction)',
                     'h': 'watch->heat (no prediction)',
                     'n': 'bind->heat (no prediction)'}

    for atom, label in control_atoms.items():
        n_total = terminal_total.get(atom, 0)
        if n_total < 10:
            print(f"  {atom}-terminal -> k-initial: too few ({n_total} transitions)")
            continue
        n_to_k = terminal_initial.get(atom, {}).get('k', 0)
        p_cond = n_to_k / n_total
        enrich = p_cond / p_k_init if p_k_init > 0 else 0
        vs_o = ""
        if o_to_k_enrich > 0:
            vs_o = f"  (o->k is {o_to_k_enrich/enrich:.2f}x this)" if enrich > 0 else ""
        print(f"  {atom}-terminal -> k-initial: {n_to_k}/{n_total} = {p_cond:.4f}, "
              f"enrichment {enrich:.3f}x  [{label}]{vs_o}")

    # ---- TEST 6: Full o-terminal forward profile (what follows o?) ----
    print()
    print("-" * 70)
    print("TEST 6: Full o-terminal forward profile — what INITIAL atoms follow o?")
    print("-" * 70)
    print()

    o_forward = []
    for init_atom in sorted(initial_total.keys()):
        if initial_total[init_atom] < 20:
            continue
        cnt = terminal_initial.get('o', {}).get(init_atom, 0)
        p_cond = cnt / o_term_total if o_term_total > 0 else 0
        p_base = initial_total[init_atom] / grand_total if grand_total > 0 else 0
        enrich = p_cond / p_base if p_base > 0 else 0
        o_forward.append((init_atom, cnt, p_cond, p_base, enrich))

    o_forward.sort(key=lambda x: -x[4])

    print(f"  {'Init':<5} {'Count':>7} {'P(o->)':>9} {'P(base)':>9} {'Enrichment':>11}")
    print(f"  {'-'*44}")
    for init_atom, cnt, p_cond, p_base, enrich in o_forward:
        marker = ""
        if init_atom == 'k':
            marker = " <-- PREDICTED (heat)"
        elif init_atom == 'e':
            marker = " <-- cool"
        elif init_atom == 'h':
            marker = " <-- watch"
        print(f"  {init_atom:<4} {cnt:>7} {p_cond:>8.4f} {p_base:>8.4f} {enrich:>10.3f}x{marker}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O23 o-terminal -> k-initial forward bigram (ordnen)")
    print("=" * 70)

    pass_enrich = o_to_k_enrich >= 1.2
    pass_direction = o_to_k_gt_k_to_o
    pass_rank = o_rank_in_k is not None and o_rank_in_k <= 5

    # Additional checks vs controls
    d_to_k_enrich = 0
    y_to_k_enrich = 0
    for atom, cnt, total, p_c, enrich in term_to_k_ranking:
        if atom == 'd':
            d_to_k_enrich = enrich
        elif atom == 'y':
            y_to_k_enrich = enrich

    pass_gt_d = o_to_k_enrich > d_to_k_enrich
    pass_gt_y = o_to_k_enrich > y_to_k_enrich

    results = [
        ("o->k enrichment >= 1.2x", pass_enrich,
         f"{o_to_k_enrich:.3f}x"),
        ("o->k > k->o (directional asymmetry)", pass_direction,
         f"{o_to_k_enrich:.3f}x > {k_to_o_enrich:.3f}x"),
        ("o ranked top 5 for predicting k-initial", pass_rank,
         f"rank #{o_rank_in_k}" if o_rank_in_k else "N/A"),
        ("o->k > d->k (seal control)", pass_gt_d,
         f"{o_to_k_enrich:.3f}x > {d_to_k_enrich:.3f}x"),
        ("o->k > y->k (end control)", pass_gt_y,
         f"{o_to_k_enrich:.3f}x > {y_to_k_enrich:.3f}x"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_enrich and pass_direction and pass_rank
    print()
    print(f"  PRIMARY CRITERION (>=1.2x AND o->k>k->o AND top 5): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
