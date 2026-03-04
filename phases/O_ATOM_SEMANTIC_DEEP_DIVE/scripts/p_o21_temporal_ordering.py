#!/usr/bin/env python3
"""
P-O21: Temporal ordering — o-initial precedes k-initial within lines

If o = "ordnen" (arrange/prepare), then on lines containing BOTH o-initial and
k-initial MIDDLE tokens, o should tend to appear BEFORE k (prepare then heat).

This is the core temporal prediction that distinguishes "ordnen" from other
hypotheses: preparation should precede the action it prepares for.

Tests:
1. o-before-k fraction on co-occurring lines (binomial test)
2. o-before-e fraction (prepare then cool) — weaker prediction
3. o-before-h fraction (prepare then watch) — weaker prediction
4. Negative controls: d-before-k, y-before-k (no temporal prediction)
5. o-before-k must exceed both negative controls

Pass criterion: o-before-k >= 55% AND p < 0.05 AND o-before-k > d-before-k
               AND o-before-k > y-before-k
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


def binomial_p_one_sided(successes, trials, p0=0.5):
    """One-sided binomial test: P(X >= successes) under H0: p = p0.

    Uses normal approximation for large N.
    """
    if trials < 1:
        return 1.0
    if trials < 30:
        # Exact binomial for small N
        p_val = 0.0
        for k in range(successes, trials + 1):
            # C(n,k) * p^k * (1-p)^(n-k)
            log_comb = _log_comb(trials, k)
            log_prob = log_comb + k * math.log(p0) + (trials - k) * math.log(1 - p0)
            p_val += math.exp(log_prob)
        return p_val
    else:
        # Normal approximation
        mean = trials * p0
        std = math.sqrt(trials * p0 * (1 - p0))
        if std == 0:
            return 0.0 if successes > mean else 1.0
        z = (successes - 0.5 - mean) / std  # continuity correction
        return 1.0 - normal_cdf(z)


def _log_comb(n, k):
    """Log of binomial coefficient C(n, k)."""
    if k > n or k < 0:
        return float('-inf')
    if k == 0 or k == n:
        return 0.0
    # Use Stirling-like log-gamma
    return _log_factorial(n) - _log_factorial(k) - _log_factorial(n - k)


def _log_factorial(n):
    """Log factorial using direct sum (good enough for n < 500)."""
    result = 0.0
    for i in range(2, n + 1):
        result += math.log(i)
    return result


def compute_ordering_fraction(line_data, atom_a, atom_b, min_line_tokens=3):
    """Compute fraction of lines where atom_a precedes atom_b.

    For each line with >= min_line_tokens containing BOTH at least one
    atom_a-initial and one atom_b-initial MIDDLE, compute mean positions
    and record whether atom_a's mean position < atom_b's mean position.

    Returns: (a_before_b_count, total_co_occurring_lines, fraction)
    """
    a_before_b = 0
    total_lines = 0

    for line_key, middles_with_pos in line_data.items():
        if len(middles_with_pos) < min_line_tokens:
            continue

        # Collect positions of atom_a-initial and atom_b-initial MIDDLEs
        a_positions = []
        b_positions = []

        for pos, mid in middles_with_pos:
            if mid and len(mid) >= 1:
                initial = mid[0]
                if initial == atom_a:
                    a_positions.append(pos)
                if initial == atom_b:
                    b_positions.append(pos)

        # Both must be present
        if not a_positions or not b_positions:
            continue

        total_lines += 1

        # Compare mean positions
        mean_a = sum(a_positions) / len(a_positions)
        mean_b = sum(b_positions) / len(b_positions)

        if mean_a < mean_b:
            a_before_b += 1

    fraction = a_before_b / total_lines if total_lines > 0 else 0.0
    return a_before_b, total_lines, fraction


def main():
    tx = Transcript()
    morph = Morphology()

    # ---- Collect tokens grouped by line, preserving position order ----
    line_tokens = defaultdict(list)  # (folio, line) -> [(position_index, middle)]
    line_counters = defaultdict(int)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue

        line_key = (token.folio, token.line)
        pos_idx = line_counters[line_key]
        line_counters[line_key] += 1
        line_tokens[line_key].append((pos_idx, m.middle))

    print("=" * 70)
    print("P-O21: Temporal ordering — o-initial precedes k-initial (ordnen)")
    print("=" * 70)
    print()
    print(f"Total lines: {len(line_tokens)}")
    total_tokens = sum(len(v) for v in line_tokens.values())
    print(f"Total tokens: {total_tokens}")
    print()

    # ---- TEST 1: o-before-k fraction ----
    print("-" * 70)
    print("TEST 1: o-before-k ordering (PREPARE then HEAT)")
    print("-" * 70)
    print()

    o_before_k_n, ok_lines, ok_frac = compute_ordering_fraction(line_tokens, 'o', 'k')
    ok_p = binomial_p_one_sided(o_before_k_n, ok_lines, 0.5)

    print(f"  Lines with both o-initial and k-initial (>= 3 tokens): {ok_lines}")
    print(f"  o-before-k: {o_before_k_n}/{ok_lines} = {ok_frac*100:.1f}%")
    print(f"  Binomial p-value (one-sided, H0: p=0.5): {ok_p:.6f}")
    if ok_p < 0.001:
        print(f"  Significance: p < 0.001 ***")
    elif ok_p < 0.01:
        print(f"  Significance: p < 0.01 **")
    elif ok_p < 0.05:
        print(f"  Significance: p < 0.05 *")
    else:
        print(f"  Significance: not significant")

    # ---- TEST 2: o-before-e and o-before-h ----
    print()
    print("-" * 70)
    print("TEST 2: o vs other kernel atoms (e=cool, h=watch)")
    print("-" * 70)
    print()

    o_before_e_n, oe_lines, oe_frac = compute_ordering_fraction(line_tokens, 'o', 'e')
    oe_p = binomial_p_one_sided(o_before_e_n, oe_lines, 0.5)
    print(f"  o-before-e: {o_before_e_n}/{oe_lines} = {oe_frac*100:.1f}%, p = {oe_p:.6f}")

    o_before_h_n, oh_lines, oh_frac = compute_ordering_fraction(line_tokens, 'o', 'h')
    oh_p = binomial_p_one_sided(o_before_h_n, oh_lines, 0.5)
    print(f"  o-before-h: {o_before_h_n}/{oh_lines} = {oh_frac*100:.1f}%, p = {oh_p:.6f}")

    # ---- TEST 3: Negative controls — d-before-k, y-before-k ----
    print()
    print("-" * 70)
    print("TEST 3: Negative controls (atoms with no temporal prediction)")
    print("-" * 70)
    print()

    d_before_k_n, dk_lines, dk_frac = compute_ordering_fraction(line_tokens, 'd', 'k')
    dk_p = binomial_p_one_sided(d_before_k_n, dk_lines, 0.5)
    print(f"  d-before-k: {d_before_k_n}/{dk_lines} = {dk_frac*100:.1f}%, p = {dk_p:.6f}")

    y_before_k_n, yk_lines, yk_frac = compute_ordering_fraction(line_tokens, 'y', 'k')
    yk_p = binomial_p_one_sided(y_before_k_n, yk_lines, 0.5)
    print(f"  y-before-k: {y_before_k_n}/{yk_lines} = {yk_frac*100:.1f}%, p = {yk_p:.6f}")

    # Additional controls: a-before-k, n-before-k
    a_before_k_n, ak_lines, ak_frac = compute_ordering_fraction(line_tokens, 'a', 'k')
    ak_p = binomial_p_one_sided(a_before_k_n, ak_lines, 0.5)
    print(f"  a-before-k: {a_before_k_n}/{ak_lines} = {ak_frac*100:.1f}%, p = {ak_p:.6f}")

    n_before_k_n, nk_lines, nk_frac = compute_ordering_fraction(line_tokens, 'n', 'k')
    # n is TERMINAL atom (C1209: 99.4% terminal), so very few n-initial MIDDLEs
    nk_p = binomial_p_one_sided(n_before_k_n, nk_lines, 0.5)
    print(f"  n-before-k: {n_before_k_n}/{nk_lines} = {nk_frac*100:.1f}%, p = {nk_p:.6f}")

    # ---- TEST 4: Full ranking — all atoms by before-k fraction ----
    print()
    print("-" * 70)
    print("TEST 4: All atoms ranked by before-k fraction")
    print("-" * 70)
    print()

    all_atoms = list('abcdefghiklmnopqrsty')
    atom_before_k = []
    for atom in all_atoms:
        if atom == 'k':
            continue
        n_before, n_lines, frac = compute_ordering_fraction(line_tokens, atom, 'k')
        if n_lines >= 10:
            p_val = binomial_p_one_sided(n_before, n_lines, 0.5)
            atom_before_k.append((atom, n_before, n_lines, frac, p_val))

    atom_before_k.sort(key=lambda x: -x[3])

    print(f"  {'Rank':<5} {'Atom':<5} {'Before-k':>10} {'Lines':>7} {'Fraction':>10} {'p-value':>10}")
    print(f"  {'-'*52}")
    o_rank_bk = None
    for rank, (atom, n_b, n_l, frac, pv) in enumerate(atom_before_k, 1):
        marker = ""
        if atom == 'o':
            marker = " <-- o (PREDICTED)"
            o_rank_bk = rank
        elif atom in ('d', 'y'):
            marker = f" <-- {atom} (CONTROL)"
        print(f"  {rank:<3} {atom:<4} {n_b:>10} {n_l:>7} {frac*100:>9.1f}% {pv:>10.6f}{marker}")

    # ---- TEST 5: Reverse check — k-before-o (should be < 50%) ----
    print()
    print("-" * 70)
    print("TEST 5: Reverse direction — k-before-o (should be weak)")
    print("-" * 70)
    print()

    k_before_o_n, ko_lines, ko_frac = compute_ordering_fraction(line_tokens, 'k', 'o')
    ko_p = binomial_p_one_sided(k_before_o_n, ko_lines, 0.5)
    print(f"  k-before-o: {k_before_o_n}/{ko_lines} = {ko_frac*100:.1f}%, p = {ko_p:.6f}")
    print(f"  o-before-k: {o_before_k_n}/{ok_lines} = {ok_frac*100:.1f}% (from TEST 1)")
    print(f"  Asymmetry (o-before-k minus k-before-o): {(ok_frac - ko_frac)*100:+.1f}pp")

    # ---- TEST 6: Effect size — mean position difference ----
    print()
    print("-" * 70)
    print("TEST 6: Mean position difference (o vs k on co-occurring lines)")
    print("-" * 70)
    print()

    pos_diffs = []  # positive = o before k
    for line_key, middles_with_pos in line_tokens.items():
        if len(middles_with_pos) < 3:
            continue
        line_len = len(middles_with_pos)
        o_positions = []
        k_positions = []
        for pos, mid in middles_with_pos:
            if mid and len(mid) >= 1:
                if mid[0] == 'o':
                    o_positions.append(pos / max(line_len - 1, 1))  # normalize to [0, 1]
                elif mid[0] == 'k':
                    k_positions.append(pos / max(line_len - 1, 1))
        if o_positions and k_positions:
            mean_o = sum(o_positions) / len(o_positions)
            mean_k = sum(k_positions) / len(k_positions)
            pos_diffs.append(mean_k - mean_o)  # positive = o earlier

    if pos_diffs:
        mean_diff = sum(pos_diffs) / len(pos_diffs)
        # Compute t-test for mean_diff > 0
        var_diff = sum((d - mean_diff) ** 2 for d in pos_diffs) / (len(pos_diffs) - 1) if len(pos_diffs) > 1 else 0
        se_diff = math.sqrt(var_diff / len(pos_diffs)) if var_diff > 0 else 1e-10
        t_stat = mean_diff / se_diff
        t_p = 1.0 - normal_cdf(t_stat)  # one-sided

        print(f"  Lines with both o-initial and k-initial: {len(pos_diffs)}")
        print(f"  Mean normalized position difference (k_pos - o_pos): {mean_diff:+.4f}")
        print(f"  (Positive = o appears earlier than k)")
        print(f"  t-statistic: {t_stat:.3f}, one-sided p = {t_p:.6f}")
    else:
        mean_diff = 0.0
        print("  INSUFFICIENT DATA for position analysis")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O21 Temporal ordering — o precedes k (ordnen)")
    print("=" * 70)

    pass_frac = ok_frac >= 0.55
    pass_p = ok_p < 0.05
    pass_d_control = ok_frac > dk_frac
    pass_y_control = ok_frac > yk_frac
    pass_reverse = ok_frac > ko_frac
    pass_position = mean_diff > 0.0

    results = [
        ("o-before-k >= 55%", pass_frac,
         f"{ok_frac*100:.1f}%"),
        ("Binomial p < 0.05", pass_p,
         f"p = {ok_p:.6f}"),
        ("o-before-k > d-before-k (control)", pass_d_control,
         f"{ok_frac*100:.1f}% > {dk_frac*100:.1f}%"),
        ("o-before-k > y-before-k (control)", pass_y_control,
         f"{ok_frac*100:.1f}% > {yk_frac*100:.1f}%"),
        ("o-before-k > k-before-o (asymmetry)", pass_reverse,
         f"{ok_frac*100:.1f}% > {ko_frac*100:.1f}%"),
        ("Mean position diff > 0 (o earlier)", pass_position,
         f"diff = {mean_diff:+.4f}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_frac and pass_p and pass_d_control and pass_y_control
    print()
    print(f"  PRIMARY CRITERION (>=55% AND p<0.05 AND > both controls): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
