#!/usr/bin/env python3
"""
SM-5: Does adding s change WHERE in a line a token appears?

For paired MIDDLE families (with-s vs without-s), compare mean normalized
line position. If s is a genuine structural modifier, it should shift the
positional profile of its base.

Pairs tested:
  1. sh-initial MIDDLEs vs h-initial MIDDLEs (not sh)
  2. ksh MIDDLEs vs kh MIDDLEs (not ksh)
  3. es MIDDLEs vs e-only MIDDLEs (standalone 'e')
  4. os MIDDLEs vs o-only MIDDLEs (standalone 'o')

Method: Welch's t-test (manual implementation).
Pass: >= 2/4 pairs show significant position difference (|delta| >= 0.05 AND p < 0.05).
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology


def welch_t_test(m1, s1, n1, m2, s2, n2):
    """Compute Welch's t-statistic and approximate p-value (two-tailed).

    Returns (t_stat, df, p_value).
    """
    if n1 < 2 or n2 < 2:
        return 0.0, 0, 1.0
    if s1 == 0 and s2 == 0:
        return 0.0, max(n1 + n2 - 2, 1), 1.0

    se = math.sqrt(s1**2 / n1 + s2**2 / n2)
    if se == 0:
        return 0.0, max(n1 + n2 - 2, 1), 1.0

    t_stat = (m1 - m2) / se

    # Welch-Satterthwaite degrees of freedom
    num = (s1**2 / n1 + s2**2 / n2) ** 2
    denom_a = (s1**2 / n1) ** 2 / (n1 - 1) if n1 > 1 and s1 > 0 else 0
    denom_b = (s2**2 / n2) ** 2 / (n2 - 1) if n2 > 1 and s2 > 0 else 0
    denom = denom_a + denom_b
    if denom == 0:
        df = max(n1 + n2 - 2, 1)
    else:
        df = num / denom

    # Approximate two-tailed p-value using normal CDF for large df
    p_value = 2.0 * (1.0 - normal_cdf(abs(t_stat)))
    return t_stat, df, p_value


def normal_cdf(x):
    """Approximate CDF of standard normal using Abramowitz & Stegun."""
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


def compute_stats(positions):
    """Compute mean and std dev of a list of floats."""
    n = len(positions)
    if n == 0:
        return 0.0, 0.0, 0
    mean = sum(positions) / n
    if n < 2:
        return mean, 0.0, n
    var = sum((x - mean) ** 2 for x in positions) / (n - 1)
    return mean, math.sqrt(var), n


def main():
    tx = Transcript()
    morph = Morphology()

    print("=" * 75)
    print("SM-5: Line position shift from s-modification")
    print("=" * 75)

    # --- Pass 1: Collect per-line token data ---
    # We need to compute normalized position within each line.
    # Group tokens by (folio, line), then assign position = index / (line_length - 1).
    line_tokens = defaultdict(list)  # (folio, line) -> [(index_in_line, middle), ...]

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue
        key = (token.folio, token.line)
        line_tokens[key].append(mid)

    # --- Pass 2: Build MIDDLE -> [normalized_position, ...] ---
    middle_positions = defaultdict(list)

    for key, middles in line_tokens.items():
        n = len(middles)
        if n < 2:
            # Single-token lines: position = 0.5 (center)
            for mid in middles:
                middle_positions[mid].append(0.5)
        else:
            for i, mid in enumerate(middles):
                pos = i / (n - 1)
                middle_positions[mid].append(pos)

    # --- Define pairs ---
    # Pair 1: sh-initial MIDDLEs vs h-initial MIDDLEs (not sh-initial)
    # Pair 2: ksh MIDDLEs vs kh MIDDLEs (not ksh)
    # Pair 3: es MIDDLEs vs e-only (standalone 'e')
    # Pair 4: os MIDDLEs vs o-only (standalone 'o')

    # Collect positions by group
    sh_initial_pos = []  # MIDDLEs starting with 'sh'
    h_initial_not_sh_pos = []  # MIDDLEs starting with 'h' but not 'sh'
    ksh_pos = []  # MIDDLEs that are exactly 'ksh' or start with 'ksh'
    kh_not_ksh_pos = []  # MIDDLEs that are/start with 'kh' but not 'ksh'
    es_pos = []  # MIDDLEs that are exactly 'es' or start with 'es'
    e_only_pos = []  # standalone 'e' MIDDLE
    os_pos = []  # MIDDLEs that are exactly 'os' or start with 'os'
    o_only_pos = []  # standalone 'o' MIDDLE

    for mid, positions in middle_positions.items():
        # Pair 1: sh-initial vs h-initial (not sh)
        if mid.startswith('sh'):
            sh_initial_pos.extend(positions)
        elif mid.startswith('h') and not mid.startswith('sh'):
            h_initial_not_sh_pos.extend(positions)

        # Pair 2: ksh vs kh (not ksh)
        if len(mid) >= 3 and mid[:3] == 'ksh':
            ksh_pos.extend(positions)
        elif len(mid) >= 2 and mid[:2] == 'kh' and not (len(mid) >= 3 and mid[:3] == 'ksh'):
            kh_not_ksh_pos.extend(positions)

        # Pair 3: es vs e-only
        if len(mid) >= 2 and mid[:2] == 'es':
            es_pos.extend(positions)
        elif mid == 'e':
            e_only_pos.extend(positions)

        # Pair 4: os vs o-only
        if len(mid) >= 2 and mid[:2] == 'os':
            os_pos.extend(positions)
        elif mid == 'o':
            o_only_pos.extend(positions)

    pairs = [
        ("sh-initial vs h-initial (not sh)", sh_initial_pos, h_initial_not_sh_pos),
        ("ksh vs kh (not ksh)", ksh_pos, kh_not_ksh_pos),
        ("es vs e-only", es_pos, e_only_pos),
        ("os vs o-only", os_pos, o_only_pos),
    ]

    # --- Evaluate each pair ---
    print()
    min_n = 5
    sig_count = 0
    inconclusive_count = 0
    total_pairs = len(pairs)

    for label, s_group, base_group in pairs:
        print("-" * 75)
        print("Pair: %s" % label)
        print("-" * 75)

        m1, sd1, n1 = compute_stats(s_group)
        m2, sd2, n2 = compute_stats(base_group)

        print("  s-group:    N=%d, mean=%.4f, sd=%.4f" % (n1, m1, sd1))
        print("  base-group: N=%d, mean=%.4f, sd=%.4f" % (n2, m2, sd2))

        if n1 < min_n or n2 < min_n:
            print("  ** INCONCLUSIVE (N < %d in one group)" % min_n)
            inconclusive_count += 1
            print()
            continue

        delta = m1 - m2
        t_stat, df, p_val = welch_t_test(m1, sd1, n1, m2, sd2, n2)

        print("  Delta (s - base): %+.4f" % delta)
        print("  Welch t-stat: %.3f, df: %.1f, p-value: %.6f" % (t_stat, df, p_val))

        sig = abs(delta) >= 0.05 and p_val < 0.05
        if sig:
            sig_count += 1
            direction = "LATER in line" if delta > 0 else "EARLIER in line"
            print("  Result: SIGNIFICANT -- s-group appears %s" % direction)
        else:
            if abs(delta) < 0.05:
                print("  Result: NOT SIGNIFICANT (|delta| < 0.05)")
            else:
                print("  Result: NOT SIGNIFICANT (p >= 0.05)")
        print()

    # --- VERDICT ---
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    testable = total_pairs - inconclusive_count
    print("Pairs tested:       %d / %d" % (testable, total_pairs))
    print("Inconclusive:       %d" % inconclusive_count)
    print("Significant pairs:  %d / %d" % (sig_count, testable))
    print("Threshold:          >= 2 / %d significant" % total_pairs)
    print()

    passed = sig_count >= 2
    print("SM-5 OVERALL: %s" % ("PASS" if passed else "FAIL"))
    if passed:
        print("  s-modification shifts line position for >= 2 paired families.")
    else:
        print("  s-modification does NOT consistently shift line position.")


if __name__ == '__main__':
    main()
