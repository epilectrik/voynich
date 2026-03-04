#!/usr/bin/env python3
"""
P-O7: o-initial bigram chaining -- k->o->l vessel management sequence

Test cross-token sequential dependencies involving o. If o = "vessel",
vessel management should follow heating (k->o) and precede state-checking (o->l).

Tests:
1. Build TERMINAL(N) -> INITIAL(N+1) bigram table for adjacent tokens within lines.
2. What TERMINAL atom precedes o-initial tokens? Enrichment vs baseline.
3. What INITIAL atom follows o-terminal tokens? Enrichment vs baseline.
4. Key: k-terminal -> o-initial predicted enriched >= 1.3x.
5. Forward: o-terminal -> {l,n,r}-initial predicted enriched >= 1.2x.
6. Full ranking for both directions.

Pass criterion: k-terminal -> o-initial >= 1.3x; o-terminal -> {l,n,r}-initial >= 1.2x.
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


def main():
    tx = Transcript()
    morph = Morphology()

    # ---- Collect token sequence per line ----
    # Group tokens by (folio, line), preserving order
    line_tokens = defaultdict(list)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        line_key = (token.folio, token.line)
        line_tokens[line_key].append(m.middle)

    # ---- Build TERMINAL(N) -> INITIAL(N+1) bigram counts ----
    # terminal_initial_counts[term_atom][init_atom] = count
    terminal_initial_counts = defaultdict(lambda: defaultdict(int))
    # marginals
    terminal_total = defaultdict(int)  # how often each atom appears as terminal of token N
    initial_total = defaultdict(int)   # how often each atom appears as initial of token N+1
    grand_total = 0

    for line_key in sorted(line_tokens.keys()):
        middles = line_tokens[line_key]
        for i in range(len(middles) - 1):
            current_mid = middles[i]
            next_mid = middles[i + 1]

            term_atom = current_mid[-1]   # TERMINAL of current token
            init_atom = next_mid[0]       # INITIAL of next token

            terminal_initial_counts[term_atom][init_atom] += 1
            terminal_total[term_atom] += 1
            initial_total[init_atom] += 1
            grand_total += 1

    print("=" * 70)
    print("P-O7: o-initial bigram chaining (k->o->l vessel management)")
    print("=" * 70)
    print()
    print(f"Total cross-token bigrams: {grand_total}")
    print(f"Unique terminal atoms: {len(terminal_total)}")
    print(f"Unique initial atoms: {len(initial_total)}")
    print()

    # ---- TEST 1: What TERMINAL atom precedes o-initial tokens? ----
    print("-" * 70)
    print("TEST 1: TERMINAL(N) atoms preceding o-initial tokens at N+1")
    print("-" * 70)

    # Baseline: P(initial=o) overall
    o_init_total = initial_total.get('o', 0)
    p_o_init = o_init_total / grand_total if grand_total > 0 else 0

    print(f"  Baseline P(initial=o) = {o_init_total}/{grand_total} = {p_o_init:.4f}")
    print()

    # For each terminal atom, compute P(next_initial=o | terminal=atom)
    backward_enrichments = []
    for term_atom in sorted(terminal_total.keys()):
        if terminal_total[term_atom] < 20:
            continue
        count_to_o = terminal_initial_counts[term_atom].get('o', 0)
        p_cond = count_to_o / terminal_total[term_atom]
        enrich = p_cond / p_o_init if p_o_init > 0 else 0
        backward_enrichments.append((term_atom, count_to_o, terminal_total[term_atom], p_cond, enrich))

    backward_enrichments.sort(key=lambda x: -x[4])

    print(f"  {'Term atom':<10} {'->o count':>10} {'Term total':>11} {'P(->o)':>9} {'Enrichment':>11}")
    print(f"  {'-'*55}")

    k_to_o_enrichment = None
    for term_atom, cnt, total, p_cond, enrich in backward_enrichments:
        marker = ""
        if term_atom == 'k':
            marker = " <-- k-terminal (PREDICTED)"
            k_to_o_enrichment = enrich
        elif term_atom in ('e', 'h'):
            marker = f" <-- {term_atom}-terminal"
        print(f"  {term_atom:<10} {cnt:>10} {total:>11} {p_cond:>8.4f} {enrich:>10.3f}x{marker}")

    # ---- TEST 2: What INITIAL atom follows o-terminal tokens? ----
    print()
    print("-" * 70)
    print("TEST 2: INITIAL(N+1) atoms following o-terminal tokens at N")
    print("-" * 70)

    # Baseline: P(terminal=o) overall
    o_term_total = terminal_total.get('o', 0)
    p_o_term = o_term_total / grand_total if grand_total > 0 else 0

    print(f"  Baseline P(terminal=o) = {o_term_total}/{grand_total} = {p_o_term:.4f}")
    print()

    # For each initial atom, compute P(prev_terminal=o | initial=atom) -- but we want the forward view:
    # P(next_initial=atom | terminal=o)
    forward_enrichments = []
    o_term_counts = terminal_initial_counts.get('o', {})
    o_term_sum = terminal_total.get('o', 0)

    for init_atom in sorted(initial_total.keys()):
        if initial_total[init_atom] < 20:
            continue
        count_from_o = o_term_counts.get(init_atom, 0)
        # P(initial=atom | terminal=o)
        p_cond = count_from_o / o_term_sum if o_term_sum > 0 else 0
        # P(initial=atom) baseline
        p_base = initial_total[init_atom] / grand_total if grand_total > 0 else 0
        enrich = p_cond / p_base if p_base > 0 else 0
        forward_enrichments.append((init_atom, count_from_o, o_term_sum, p_cond, p_base, enrich))

    forward_enrichments.sort(key=lambda x: -x[5])

    print(f"  {'Init atom':<10} {'o-> count':>10} {'o-term N':>9} {'P(o->)':>9} {'P(base)':>9} {'Enrichment':>11}")
    print(f"  {'-'*62}")

    lnr_enrichments = {}
    for init_atom, cnt, o_n, p_cond, p_base, enrich in forward_enrichments:
        marker = ""
        if init_atom in ('l', 'n', 'r'):
            marker = f" <-- {init_atom}-initial (PREDICTED)"
            lnr_enrichments[init_atom] = enrich
        print(f"  {init_atom:<10} {cnt:>10} {o_n:>9} {p_cond:>8.4f} {p_base:>8.4f} {enrich:>10.3f}x{marker}")

    # ---- TEST 3: Key comparison — k-terminal -> o-initial ----
    print()
    print("-" * 70)
    print("TEST 3: Key enrichment — k-terminal -> o-initial")
    print("-" * 70)

    if k_to_o_enrichment is not None:
        print(f"  k-terminal -> o-initial enrichment: {k_to_o_enrichment:.3f}x")
        print(f"  Threshold: >= 1.3x")
        print(f"  Verdict: {'PASS' if k_to_o_enrichment >= 1.3 else 'FAIL'}")
    else:
        print("  WARNING: k-terminal not found or too few tokens")

    # Also show e->o and h->o for comparison
    for atom in ('e', 'h'):
        for term_atom, cnt, total, p_cond, enrich in backward_enrichments:
            if term_atom == atom:
                print(f"  {atom}-terminal -> o-initial enrichment: {enrich:.3f}x (comparison)")
                break

    # ---- TEST 4: Forward chain — o-terminal -> {l,n,r}-initial ----
    print()
    print("-" * 70)
    print("TEST 4: Forward chain — o-terminal -> {l,n,r}-initial")
    print("-" * 70)

    lnr_pass_count = 0
    for atom in ('l', 'n', 'r'):
        enrich = lnr_enrichments.get(atom, 0)
        passed = enrich >= 1.2
        if passed:
            lnr_pass_count += 1
        print(f"  o-terminal -> {atom}-initial: {enrich:.3f}x {'PASS' if passed else 'FAIL'} (threshold: >= 1.2x)")

    # ---- TEST 5: Full cross-token bigram matrix (top enrichments) ----
    print()
    print("-" * 70)
    print("TEST 5: Top 15 enriched TERMINAL -> INITIAL cross-token bigrams")
    print("-" * 70)

    all_bigram_enrichments = []
    for term_atom in terminal_total:
        if terminal_total[term_atom] < 20:
            continue
        for init_atom in initial_total:
            if initial_total[init_atom] < 20:
                continue
            count = terminal_initial_counts[term_atom].get(init_atom, 0)
            if count < 5:
                continue
            # P(init | term)
            p_cond = count / terminal_total[term_atom]
            # P(init) baseline
            p_base = initial_total[init_atom] / grand_total
            enrich = p_cond / p_base if p_base > 0 else 0
            all_bigram_enrichments.append((term_atom, init_atom, count, enrich))

    all_bigram_enrichments.sort(key=lambda x: -x[3])

    print(f"  {'TERM->INIT':<12} {'Count':>7} {'Enrichment':>11} {'Note':>25}")
    print(f"  {'-'*58}")

    for term_atom, init_atom, count, enrich in all_bigram_enrichments[:15]:
        note = ""
        if term_atom == 'k' and init_atom == 'o':
            note = "k->o PREDICTED"
        elif term_atom == 'o' and init_atom in ('l', 'n', 'r'):
            note = f"o->{init_atom} PREDICTED"
        elif term_atom == 'o' or init_atom == 'o':
            note = "o-involved"
        print(f"  {term_atom}->{init_atom:<8} {count:>7} {enrich:>10.3f}x {note:>25}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O7 o-initial bigram chaining")
    print("=" * 70)

    pass_k_to_o = k_to_o_enrichment is not None and k_to_o_enrichment >= 1.3
    pass_lnr = lnr_pass_count >= 2  # at least 2 of 3

    # Find o-initial rank among all initial atoms by backward enrichment from k
    k_to_all = []
    for term_atom, init_atom, count, enrich in all_bigram_enrichments:
        if term_atom == 'k':
            k_to_all.append((init_atom, enrich))
    k_to_all.sort(key=lambda x: -x[1])
    o_rank_from_k = None
    for i, (init_atom, enrich) in enumerate(k_to_all):
        if init_atom == 'o':
            o_rank_from_k = i + 1
            break

    results = [
        ("k-terminal -> o-initial enrichment >= 1.3x", pass_k_to_o,
         f"{k_to_o_enrichment:.3f}x" if k_to_o_enrichment is not None else "N/A"),
        ("o-terminal -> {l,n,r}-initial >= 1.2x (2/3)", pass_lnr,
         f"{lnr_pass_count}/3 pass"),
        ("o-initial rank from k-terminal", o_rank_from_k is not None and o_rank_from_k <= 5,
         f"rank #{o_rank_from_k}" if o_rank_from_k is not None else "N/A"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_k_to_o and pass_lnr
    print()
    print(f"  PRIMARY CRITERION (k->o >= 1.3x AND 2/3 lnr >= 1.2x): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
