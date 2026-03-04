#!/usr/bin/env python3
"""
SM-7: Do sh-PREFIX and ch-PREFIX tokens route differently to the NEXT token?

C1243 showed sh PREFIX routes to heat(k) 32% vs ch 24%. This test examines
whether the s in sh (vs h in ch) produces different cross-token MIDDLE routing.

Since sh/ch are overwhelmingly PREFIXes (sh=2329, ch=3492) rather than
MIDDLE initials (5 and 4), this test uses PREFIX-level grouping.

Method:
1. Build cross-token bigrams within lines.
2. When token N has sh PREFIX, record the MIDDLE initial atom of token N+1.
3. When token N has ch PREFIX, record the MIDDLE initial atom of token N+1.
4. Compare the two distributions.
5. Also compare the MIDDLE content of token N (what sh-PREFIX carries vs ch-PREFIX).

C1243 predicts: sh routes more to k-initial (heat) than ch does.
Pass: distributions significantly different (p < 0.05) OR top-2 following
      initial atoms differ between sh and ch contexts.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology


def normal_cdf(x):
    """Approximate CDF of standard normal."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p_const = 0.3275911
    sign = 1 if x >= 0 else -1
    x_abs = abs(x)
    t = 1.0 / (1.0 + p_const * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs / 2.0)
    return 0.5 * (1.0 + sign * y)


def chi2_p_value(chi2_val, df):
    """Approximate chi-square p-value using Wilson-Hilferty normal approximation."""
    if df <= 0 or chi2_val <= 0:
        return 1.0
    z = ((chi2_val / df) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * df))) / math.sqrt(2.0 / (9.0 * df))
    return 1.0 - normal_cdf(z)


def chi2_contingency(dist_a, dist_b, all_keys):
    """Compute chi-square statistic for two distributions over the same keys."""
    total_a = sum(dist_a.get(k, 0) for k in all_keys)
    total_b = sum(dist_b.get(k, 0) for k in all_keys)
    grand = total_a + total_b

    if grand == 0 or total_a == 0 or total_b == 0:
        return 0.0, 0, 1.0

    chi2 = 0.0
    valid_keys = 0
    for k in all_keys:
        o_a = dist_a.get(k, 0)
        o_b = dist_b.get(k, 0)
        row_total = o_a + o_b
        if row_total == 0:
            continue
        valid_keys += 1
        e_a = row_total * total_a / grand
        e_b = row_total * total_b / grand
        if e_a > 0:
            chi2 += (o_a - e_a) ** 2 / e_a
        if e_b > 0:
            chi2 += (o_b - e_b) ** 2 / e_b

    df = max(valid_keys - 1, 1)
    p_val = chi2_p_value(chi2, df)
    return chi2, df, p_val


def main():
    tx = Transcript()
    morph = Morphology()

    print("=" * 75)
    print("SM-7: sh-PREFIX vs ch-PREFIX cross-token MIDDLE routing")
    print("=" * 75)
    print()
    print("C1243: sh PREFIX routes to k-initial 32.0%%, ch PREFIX 24.0%%, ratio 1.33x")
    print("Testing whether s in sh modifies routing compared to h in ch.")

    # --- Pass 1: Collect line-grouped tokens with morphology ---
    line_tokens = defaultdict(list)  # (folio, line) -> [(prefix, middle, word), ...]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        pfx = m.prefix
        if not mid:
            continue
        key = (token.folio, token.line)
        line_tokens[key].append((pfx, mid, w))

    # --- Pass 2: Build cross-token routing from sh-PREFIX and ch-PREFIX ---
    sh_next_initial = Counter()  # next token's MIDDLE initial atom
    ch_next_initial = Counter()
    sh_next_middle = Counter()   # next token's full MIDDLE
    ch_next_middle = Counter()
    sh_own_middle = Counter()    # current token's MIDDLE (what sh carries)
    ch_own_middle = Counter()    # current token's MIDDLE (what ch carries)
    sh_own_initial = Counter()   # current token's MIDDLE initial atom
    ch_own_initial = Counter()

    sh_source_count = 0
    ch_source_count = 0

    for key in sorted(line_tokens.keys()):
        tokens = line_tokens[key]
        for i in range(len(tokens) - 1):
            pfx_n, mid_n, word_n = tokens[i]
            pfx_n1, mid_n1, word_n1 = tokens[i + 1]

            if not mid_n or not mid_n1:
                continue

            next_initial = mid_n1[0]

            if pfx_n == 'sh':
                sh_next_initial[next_initial] += 1
                sh_next_middle[mid_n1] += 1
                sh_own_middle[mid_n] += 1
                sh_own_initial[mid_n[0]] += 1
                sh_source_count += 1
            elif pfx_n == 'ch':
                ch_next_initial[next_initial] += 1
                ch_next_middle[mid_n1] += 1
                ch_own_middle[mid_n] += 1
                ch_own_initial[mid_n[0]] += 1
                ch_source_count += 1

    print()
    print("sh-PREFIX source tokens (non-final in line): %d" % sh_source_count)
    print("ch-PREFIX source tokens (non-final in line): %d" % ch_source_count)

    # --- What sh carries vs what ch carries ---
    print()
    print("-" * 75)
    print("MIDDLE content carried by sh vs ch (initial atom of own MIDDLE)")
    print("-" * 75)
    print()

    own_atoms = sorted(set(sh_own_initial.keys()) | set(ch_own_initial.keys()))
    print("%-6s %10s %8s %10s %8s" % ("Atom", "sh-count", "sh-%", "ch-count", "ch-%"))
    print("-" * 50)
    for atom in own_atoms:
        sh_n = sh_own_initial.get(atom, 0)
        ch_n = ch_own_initial.get(atom, 0)
        sh_pct = 100 * sh_n / sh_source_count if sh_source_count > 0 else 0
        ch_pct = 100 * ch_n / ch_source_count if ch_source_count > 0 else 0
        marker = ""
        if atom == 'e':
            marker = "  <-- C1203: sh more e-enriched"
        elif atom == 'k':
            marker = "  <-- C1203: ch more k-enriched"
        print("%-6s %10d %7.1f%% %10d %7.1f%%%s" % (atom, sh_n, sh_pct, ch_n, ch_pct, marker))

    # --- Display next-token routing distributions ---
    all_atoms = sorted(set(sh_next_initial.keys()) | set(ch_next_initial.keys()))

    print()
    print("-" * 75)
    print("Next-token MIDDLE initial atom distributions (cross-token routing)")
    print("-" * 75)
    print()
    print("%-6s %10s %8s %10s %8s %10s" % (
        "Atom", "sh-count", "sh-%", "ch-count", "ch-%", "sh/ch ratio"))
    print("-" * 60)

    for atom in all_atoms:
        sh_n = sh_next_initial.get(atom, 0)
        ch_n = ch_next_initial.get(atom, 0)
        sh_pct = 100 * sh_n / sh_source_count if sh_source_count > 0 else 0
        ch_pct = 100 * ch_n / ch_source_count if ch_source_count > 0 else 0
        ratio = sh_pct / ch_pct if ch_pct > 0 else float('inf') if sh_pct > 0 else 0

        marker = ""
        if atom == 'k':
            marker = "  <-- heat (C1243 prediction: sh > ch)"
        elif atom == 'e':
            marker = "  <-- cool"
        elif atom == 'h':
            marker = "  <-- monitor"
        elif atom == 'o':
            marker = "  <-- arrange"

        if ratio == float('inf'):
            ratio_str = "inf"
        else:
            ratio_str = "%.3f" % ratio

        print("%-6s %10d %7.1f%% %10d %7.1f%% %10s%s" % (
            atom, sh_n, sh_pct, ch_n, ch_pct, ratio_str, marker))

    # --- Top-2 analysis ---
    print()
    print("-" * 75)
    print("Top-2 following initial atoms")
    print("-" * 75)
    print()

    sh_top2 = sh_next_initial.most_common(2)
    ch_top2 = ch_next_initial.most_common(2)
    sh_top2_atoms = [a for a, _ in sh_top2]
    ch_top2_atoms = [a for a, _ in ch_top2]

    print("  sh-PREFIX top-2: %s" % ", ".join(
        ["%s (%.1f%%)" % (a, 100 * n / sh_source_count) for a, n in sh_top2]))
    print("  ch-PREFIX top-2: %s" % ", ".join(
        ["%s (%.1f%%)" % (a, 100 * n / ch_source_count) for a, n in ch_top2]))

    top2_differ = sh_top2_atoms != ch_top2_atoms
    print("  Top-2 differ: %s" % ("YES" if top2_differ else "NO"))

    # --- k-atom comparison (C1243 replication) ---
    print()
    print("-" * 75)
    print("C1243 replication: k-initial following rate")
    print("-" * 75)
    print()

    sh_k_pct = 100 * sh_next_initial.get('k', 0) / sh_source_count if sh_source_count > 0 else 0
    ch_k_pct = 100 * ch_next_initial.get('k', 0) / ch_source_count if ch_source_count > 0 else 0
    k_ratio = sh_k_pct / ch_k_pct if ch_k_pct > 0 else float('inf')

    print("  sh-PREFIX -> k-initial next: %.1f%% (%d/%d)" % (
        sh_k_pct, sh_next_initial.get('k', 0), sh_source_count))
    print("  ch-PREFIX -> k-initial next: %.1f%% (%d/%d)" % (
        ch_k_pct, ch_next_initial.get('k', 0), ch_source_count))
    if k_ratio != float('inf'):
        print("  sh/ch ratio: %.3f" % k_ratio)
    else:
        print("  sh/ch ratio: inf (ch has 0 k-initial followers)")
    print("  C1243 PREFIX-level: sh->k 32.0%%, ch->k 24.0%%, ratio 1.33x")
    if k_ratio > 1.0:
        print("  Direction MATCHES C1243 (sh routes more to k)")
    else:
        print("  Direction DOES NOT match C1243")

    # --- Chi-square test ---
    print()
    print("-" * 75)
    print("Chi-square test: sh vs ch next-token initial distributions")
    print("-" * 75)
    print()

    chi2, df, p_val = chi2_contingency(sh_next_initial, ch_next_initial, set(all_atoms))
    print("  Chi-square: %.3f" % chi2)
    print("  Degrees of freedom: %d" % df)
    print("  p-value: %.6f" % p_val)
    chi2_sig = p_val < 0.05
    print("  Significant (p < 0.05): %s" % ("YES" if chi2_sig else "NO"))

    # --- Top-10 next MIDDLEs for context ---
    print()
    print("-" * 75)
    print("Top-10 next MIDDLEs following sh-PREFIX and ch-PREFIX tokens")
    print("-" * 75)
    print()

    print("  After sh-PREFIX token:")
    for mid, n in sh_next_middle.most_common(10):
        print("    %-15s  %4d  (%.1f%%)" % (mid, n, 100 * n / sh_source_count))

    print()
    print("  After ch-PREFIX token:")
    for mid, n in ch_next_middle.most_common(10):
        print("    %-15s  %4d  (%.1f%%)" % (mid, n, 100 * n / ch_source_count))

    # --- VERDICT ---
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    passed = chi2_sig or top2_differ
    print("  Chi-square significant (p < 0.05): %s" % ("PASS" if chi2_sig else "FAIL"))
    print("  Top-2 atoms differ:                %s" % ("PASS" if top2_differ else "FAIL"))
    print()
    print("SM-7 OVERALL: %s" % ("PASS" if passed else "FAIL"))
    if passed:
        print("  sh-PREFIX and ch-PREFIX tokens route to different next-token MIDDLE profiles.")
        if chi2_sig and k_ratio > 1.0:
            print("  C1243 finding replicated: sh routes more to k-initial than ch.")
    else:
        print("  sh-PREFIX and ch-PREFIX do NOT show different cross-token routing.")


if __name__ == '__main__':
    main()
