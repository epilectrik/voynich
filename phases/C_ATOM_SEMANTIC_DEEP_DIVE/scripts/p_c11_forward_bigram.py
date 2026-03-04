"""
P-C11: Forward bigram — c→h cross-token enrichment

Tests cross-token sequential dependencies: does c-terminal in token N
predict h-initial in token N+1?

Predictions (based on {c,h} cluster and c→h junction):
- c-terminal → h-initial cross-token enrichment >= 1.2x
- c→k enrichment <= 1.1x (c doesn't feed into heating directly)
- h-terminal → c-initial should also show enrichment (feedback)

Based on:
- {c,h} monitoring cluster r=+0.746 (C1207)
- c→h obligatory junction 380/380 = 100%, 11.7x enrichment (C1216)
- POSITIVE carryover z=+3.23 (C1208)
- C1212: TERMINAL(N)->INITIAL(N+1) is strongest sequential signal
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology


# All atoms used in MIDDLEs
ATOMS = list('acdefhiklmnopqrsty')
# Focus atoms for initial/terminal
INITIAL_ATOMS = list('aceioqd')  # Common initial atoms per C1209
TERMINAL_ATOMS = list('chlmnry')  # Common terminal atoms per C1209


def main():
    print("=" * 70)
    print("P-C11: Forward bigram - c->h cross-token enrichment")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()

    # --- Build adjacent token pairs within lines ---
    # Group tokens by (folio, line)
    line_tokens = defaultdict(list)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m or not m.middle:
            continue
        mid = m.middle
        if len(mid) == 0:
            continue
        line_key = (token.folio, token.line)
        line_tokens[line_key].append(mid)

    # --- Build TERMINAL(N) -> INITIAL(N+1) bigram counts ---
    # terminal_initial[t_char][i_char] = count
    terminal_initial = defaultdict(lambda: defaultdict(int))
    terminal_total = defaultdict(int)
    initial_total = defaultdict(int)
    total_pairs = 0

    for line_key in sorted(line_tokens.keys()):
        mids = line_tokens[line_key]
        for i in range(len(mids) - 1):
            t_char = mids[i][-1]   # terminal of token N
            i_char = mids[i + 1][0]  # initial of token N+1
            terminal_initial[t_char][i_char] += 1
            terminal_total[t_char] += 1
            initial_total[i_char] += 1
            total_pairs += 1

    print(f"\nTotal adjacent token pairs: {total_pairs}")
    print(f"Unique terminal atoms: {len(terminal_total)}")
    print(f"Unique initial atoms: {len(initial_total)}")

    # --- Compute baseline initial rates ---
    baseline_initial = {}
    for ch in initial_total:
        baseline_initial[ch] = initial_total[ch] / total_pairs

    # --- Compute enrichment: P(initial | terminal) / P(initial) ---
    print("\n--- c-terminal forward connections (enrichment vs baseline) ---\n")
    print(f"{'c-term -> X-init':<20} {'Count':>6} {'P(X|c)':>8} {'Baseline':>8} {'Enrich':>8}")
    print("-" * 55)

    c_forward = {}
    if terminal_total.get('c', 0) > 0:
        c_total = terminal_total['c']
        for i_ch in sorted(initial_total.keys()):
            count = terminal_initial['c'].get(i_ch, 0)
            p_given_c = count / c_total
            base = baseline_initial.get(i_ch, 0)
            enrich = p_given_c / base if base > 0 else 0
            c_forward[i_ch] = (count, p_given_c, base, enrich)

        # Sort by enrichment
        for i_ch, (count, p_gc, base, enrich) in sorted(c_forward.items(), key=lambda x: -x[1][3]):
            if count > 0:
                print(f"c -> {i_ch:<15} {count:>6} {p_gc:>7.4f} {base:>7.4f} {enrich:>7.2f}x")
    else:
        print("(No c-terminal tokens found)")

    # --- c-initial backward connections ---
    print("\n--- c-initial backward connections (what precedes c?) ---\n")
    print(f"{'X-term -> c-init':<20} {'Count':>6} {'P(c|X)':>8} {'Baseline':>8} {'Enrich':>8}")
    print("-" * 55)

    c_backward = {}
    c_base_rate = baseline_initial.get('c', 0)
    for t_ch in sorted(terminal_total.keys()):
        count = terminal_initial[t_ch].get('c', 0)
        t_total = terminal_total[t_ch]
        p_c_given_t = count / t_total if t_total > 0 else 0
        enrich = p_c_given_t / c_base_rate if c_base_rate > 0 else 0
        c_backward[t_ch] = (count, p_c_given_t, c_base_rate, enrich)

    for t_ch, (count, p_ct, base, enrich) in sorted(c_backward.items(), key=lambda x: -x[1][3]):
        if count > 0:
            print(f"{t_ch} -> c{' ' * 14} {count:>6} {p_ct:>7.4f} {base:>7.4f} {enrich:>7.2f}x")

    # --- Focus: c→h and h→c ---
    print("\n--- KEY BIGRAMS ---\n")

    c_to_h = c_forward.get('h', (0, 0, 0, 0))
    c_to_k = c_forward.get('k', (0, 0, 0, 0))
    h_to_c = c_backward.get('h', (0, 0, 0, 0))

    print(f"c-terminal -> h-initial: count={c_to_h[0]}, enrichment={c_to_h[3]:.2f}x")
    print(f"c-terminal -> k-initial: count={c_to_k[0]}, enrichment={c_to_k[3]:.2f}x")
    print(f"h-terminal -> c-initial: count={h_to_c[0]}, enrichment={h_to_c[3]:.2f}x")

    # --- Reference: o→l bigram (for comparison per spec) ---
    print("\n--- Reference bigram: o-terminal -> l-initial ---")
    if terminal_total.get('o', 0) > 0:
        o_total = terminal_total['o']
        o_to_l_count = terminal_initial['o'].get('l', 0)
        p_l_given_o = o_to_l_count / o_total
        l_base = baseline_initial.get('l', 0)
        o_to_l_enrich = p_l_given_o / l_base if l_base > 0 else 0
        print(f"o -> l: count={o_to_l_count}, enrichment={o_to_l_enrich:.2f}x")
    else:
        print("(No o-terminal tokens)")

    # --- Top 15 enriched bigrams overall ---
    print("\n--- Top 15 most enriched TERMINAL->INITIAL bigrams ---\n")
    print(f"{'Bigram':<10} {'Count':>6} {'P(I|T)':>8} {'Base':>8} {'Enrich':>8}")
    print("-" * 45)

    all_bigrams = []
    for t_ch in terminal_total:
        t_total = terminal_total[t_ch]
        for i_ch in initial_total:
            count = terminal_initial[t_ch].get(i_ch, 0)
            if count < 5:
                continue  # Skip very rare
            p_given_t = count / t_total
            base = baseline_initial.get(i_ch, 0)
            enrich = p_given_t / base if base > 0 else 0
            all_bigrams.append((f"{t_ch}->{i_ch}", count, p_given_t, base, enrich))

    all_bigrams.sort(key=lambda x: -x[4])
    for bigram, count, p_gt, base, enrich in all_bigrams[:15]:
        marker = " ***" if 'c' in bigram else ""
        print(f"{bigram:<10} {count:>6} {p_gt:>7.4f} {base:>7.4f} {enrich:>7.2f}x{marker}")

    # --- Verdicts ---
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    # P1: c→h >= 1.2x
    c_h_enrich = c_to_h[3]
    p1 = c_h_enrich >= 1.2
    print(f"P1: c-terminal -> h-initial enrichment = {c_h_enrich:.2f}x >= 1.2x: {'PASS' if p1 else 'FAIL'}")

    # P2: c→k <= 1.1x
    c_k_enrich = c_to_k[3]
    p2 = c_k_enrich <= 1.1
    print(f"P2: c-terminal -> k-initial enrichment = {c_k_enrich:.2f}x <= 1.1x: {'PASS' if p2 else 'FAIL'}")

    # P3: h→c shows some enrichment (informational)
    h_c_enrich = h_to_c[3]
    p3 = h_c_enrich >= 1.0
    print(f"P3: h-terminal -> c-initial enrichment = {h_c_enrich:.2f}x >= 1.0x (informational): {'PASS' if p3 else 'FAIL'}")

    overall = p1 and p2
    print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")
    if overall:
        print("  c->h cross-token enrichment confirmed; c does not feed k directly")
        print("  Consistent with 'adjust then monitor' sequential pattern")
    else:
        print("  c->h cross-token pattern does NOT match predictions")
        if not p1:
            print(f"  c->h only {c_h_enrich:.2f}x (needed >= 1.2x)")
        if not p2:
            print(f"  c->k was {c_k_enrich:.2f}x (needed <= 1.1x)")


if __name__ == '__main__':
    main()
