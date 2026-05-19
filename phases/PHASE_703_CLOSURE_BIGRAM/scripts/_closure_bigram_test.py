"""
PHASE_703: Closure protocol bigram grammar test.

Tests whether C2030's Voynich-wide LATE-class adjacency clustering has
internal bigram grammar (directional asymmetries + forbidden pairs).

Pre-registered decision rules (LOCKED in INDEX.md):
  Test 1 — Directional asymmetry: at least 1 (A,B) pair with FDR-corrected
    p < 0.05 on observed(A->B) vs observed(B->A) binomial test (null p=0.5)
    AND |asymmetry| >= 30%, with N(A->B) + N(B->A) >= 5.

  Test 2 — Forbidden bigrams: at least 1 (A,B) pair with observed=0,
    null-expected >= 5, and empirical null p(observed=0) < 0.005 across
    200 within-line shuffle permutations.

  Tier 2 if BOTH tests pass; Tier 3 if exactly one; no constraint if neither.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_703_CLOSURE_BIGRAM' / 'results' / 'closure_bigram_test.json'

# LATE inventory — LOCKED pre-test (see INDEX.md)
LATE_INVENTORY = ['ar', 'ary', 'aly', 'al', 'dar', 'dal', 'dary', 'daly',
                   'or', 'ory', 'oly', 'ol']

N_PERM = 200
N_FLOOR_FDR = 5
N_FLOOR_FORBIDDEN_EXPECTED = 5
ASYMMETRY_EFFECT_FLOOR = 0.30
FDR_THRESHOLD = 0.05
FORBIDDEN_NULL_P_THRESHOLD = 0.005


def binomial_two_sided_p(k, n, p=0.5):
    """Two-sided binomial test p-value for observing k successes in n trials."""
    if n == 0:
        return 1.0
    # Compute exact two-sided p-value
    from math import comb
    expected = n * p
    obs_dev = abs(k - expected)
    p_val = 0.0
    for i in range(n + 1):
        if abs(i - expected) >= obs_dev:
            p_val += comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return min(1.0, p_val)


def benjamini_hochberg(p_values_with_keys, alpha=0.05):
    """Apply Benjamini-Hochberg FDR correction.

    Args: list of (key, p_value) tuples.
    Returns: list of (key, p_value, p_adjusted, reject_null).
    """
    if not p_values_with_keys:
        return []
    sorted_items = sorted(p_values_with_keys, key=lambda x: x[1])
    n = len(sorted_items)
    results = []
    # Compute BH-adjusted p-values
    bh_adjusted = []
    for i, (key, p) in enumerate(sorted_items):
        rank = i + 1
        adj = min(1.0, p * n / rank)
        bh_adjusted.append((key, p, adj))
    # Enforce monotonicity (BH adjusted should be non-decreasing as p increases)
    for i in range(len(bh_adjusted) - 2, -1, -1):
        key, p, adj = bh_adjusted[i]
        _, _, next_adj = bh_adjusted[i + 1]
        if adj > next_adj:
            bh_adjusted[i] = (key, p, next_adj)
    for key, p, adj in bh_adjusted:
        results.append((key, p, adj, adj < alpha))
    return results


def collect_late_sequences():
    """For each line in Currier B P-placement, get sequence of LATE-class MIDDLE strings.

    Returns: list of (folio, line_num, list_of_(token_idx, late_middle)).
    Non-LATE tokens are NOT in the sequence — but we keep position info to
    detect adjacency: only adjacent LATE-LATE means token_idx difference of 1.
    """
    tx = Transcript()
    morph = Morphology()

    late_set = set(LATE_INVENTORY)
    lines = []  # list of (folio, line, [(token_idx, middle, word)])
    line_buffer = defaultdict(list)  # (folio, line) -> list of (token_idx_within_line, middle, word)

    for t in tx.currier_b(h_only=True, exclude_labels=True, exclude_uncertain=True):
        if not (t.placement and t.placement.startswith('P')):
            continue
        if not t.word.strip():
            continue
        word = t.word.lower()
        try:
            m = morph.extract(word)
            middle = m.middle
        except Exception:
            middle = None
        key = (t.folio, t.line)
        idx = len(line_buffer[key])
        line_buffer[key].append((idx, middle, word))

    for (folio, line), tokens in line_buffer.items():
        if line is None or line == '':
            continue
        lines.append((folio, line, tokens))

    return lines, late_set


def extract_late_bigrams(lines, late_set):
    """Extract adjacent LATE-LATE bigrams from within-line sequences.

    Returns: Counter of (middle_first, middle_second).
    Adjacency = token_idx difference of 1 within the same line.
    """
    bigrams = Counter()
    for (folio, line, tokens) in lines:
        for i in range(len(tokens) - 1):
            idx_a, mid_a, _ = tokens[i]
            idx_b, mid_b, _ = tokens[i + 1]
            if mid_a in late_set and mid_b in late_set:
                bigrams[(mid_a, mid_b)] += 1
    return bigrams


def within_line_shuffle_null(lines, late_set, n_perm=N_PERM, seed=703):
    """Within-line shuffle null distribution of LATE-LATE bigram counts.

    For each permutation: shuffle order of MIDDLEs within each line, then
    re-extract LATE-LATE bigrams. Accumulates per-bigram null counts.
    """
    rng = random.Random(seed)
    null_counts = defaultdict(list)  # bigram -> list of null counts (length n_perm)
    n_lines = len(lines)
    print(f"  Running {n_perm} within-line shuffle permutations...")
    for perm_i in range(n_perm):
        perm_bigrams = Counter()
        for (folio, line, tokens) in lines:
            n = len(tokens)
            if n < 2:
                continue
            middles = [t[1] for t in tokens]
            shuffled = list(middles)
            rng.shuffle(shuffled)
            for i in range(n - 1):
                a, b = shuffled[i], shuffled[i + 1]
                if a in late_set and b in late_set:
                    perm_bigrams[(a, b)] += 1
        # Store this permutation's count for every observed and possible bigram
        for a in LATE_INVENTORY:
            for b in LATE_INVENTORY:
                null_counts[(a, b)].append(perm_bigrams.get((a, b), 0))
        if (perm_i + 1) % 50 == 0:
            print(f"    permutation {perm_i + 1}/{n_perm}")
    return null_counts


def run_directional_asymmetry_test(bigrams):
    """Test for directional asymmetries among LATE-LATE bigrams.

    For each unordered pair {A, B} with A != B, compare obs(A->B) vs obs(B->A).
    Null: each direction equally likely under within-line shuffle (binomial p=0.5).
    """
    pair_results = []
    seen = set()
    for a in LATE_INVENTORY:
        for b in LATE_INVENTORY:
            if a == b:
                continue
            key = tuple(sorted([a, b]))
            if key in seen:
                continue
            seen.add(key)
            n_ab = bigrams.get((a, b), 0)
            n_ba = bigrams.get((b, a), 0)
            total = n_ab + n_ba
            if total < N_FLOOR_FDR:
                continue
            asymmetry = (n_ab - n_ba) / total
            # Two-sided binomial test
            k = max(n_ab, n_ba)
            p = binomial_two_sided_p(k, total, p=0.5)
            pair_results.append({
                'pair_sorted': key,
                'a': a, 'b': b,
                'n_a_to_b': n_ab, 'n_b_to_a': n_ba,
                'total': total,
                'asymmetry': asymmetry,
                'binomial_p': p,
            })
    # FDR correction
    p_keyed = [(i, r['binomial_p']) for i, r in enumerate(pair_results)]
    bh = benjamini_hochberg(p_keyed, alpha=FDR_THRESHOLD)
    for (i, p, p_adj, reject) in bh:
        pair_results[i]['p_adjusted_BH'] = p_adj
        pair_results[i]['FDR_significant'] = reject
        pair_results[i]['passes_effect_size_floor'] = abs(pair_results[i]['asymmetry']) >= ASYMMETRY_EFFECT_FLOOR
        pair_results[i]['passes_registration'] = reject and pair_results[i]['passes_effect_size_floor']
    return sorted(pair_results, key=lambda r: r['binomial_p'])


def run_forbidden_test(bigrams, null_counts):
    """Identify forbidden bigrams: observed=0, expected >= 5, empirical null p < 0.005."""
    forbidden = []
    for a in LATE_INVENTORY:
        for b in LATE_INVENTORY:
            observed = bigrams.get((a, b), 0)
            if observed > 0:
                continue
            null = null_counts.get((a, b), [])
            if not null:
                continue
            expected = sum(null) / len(null)
            if expected < N_FLOOR_FORBIDDEN_EXPECTED:
                continue
            # Empirical p: fraction of null samples with count == 0
            null_zeros = sum(1 for c in null if c == 0)
            null_p = null_zeros / len(null)
            std = (sum((c - expected) ** 2 for c in null) / len(null)) ** 0.5
            forbidden.append({
                'a': a, 'b': b,
                'observed': 0,
                'null_expected': expected,
                'null_std': std,
                'null_min': min(null), 'null_max': max(null),
                'empirical_null_p_observed_zero': null_p,
                'passes_registration': null_p < FORBIDDEN_NULL_P_THRESHOLD,
            })
    return sorted(forbidden, key=lambda r: r['empirical_null_p_observed_zero'])


def main():
    print("=" * 90)
    print("PHASE_703 CLOSURE BIGRAM GRAMMAR TEST")
    print("=" * 90)

    print("\nStep 1: Collect within-line LATE token sequences (Currier B, P-placement)...")
    lines, late_set = collect_late_sequences()
    print(f"  Total lines collected: {len(lines)}")

    print("\nStep 2: Extract LATE-LATE adjacent bigrams...")
    bigrams = extract_late_bigrams(lines, late_set)
    total_late_late = sum(bigrams.values())
    print(f"  Total LATE-LATE adjacent bigrams: {total_late_late}")
    print(f"  Unique bigram types observed: {len(bigrams)}")
    print(f"\n  Top 15 bigrams:")
    for (a, b), c in bigrams.most_common(15):
        print(f"    {a} -> {b}: {c}")

    print("\nStep 3: Run within-line shuffle null for forbidden-pair test...")
    null_counts = within_line_shuffle_null(lines, late_set, n_perm=N_PERM)

    print("\nStep 4: Directional asymmetry test...")
    asym_results = run_directional_asymmetry_test(bigrams)
    print(f"  Pairs with N >= {N_FLOOR_FDR}: {len(asym_results)}")
    print(f"\n  {'pair (lex sorted)':<22}{'a':>6}{'b':>6}{'A->B':>8}{'B->A':>8}"
          f"{'asym':>8}{'p_raw':>10}{'p_BH':>10}{'reg?':>6}")
    print("  " + "-" * 86)
    for r in asym_results[:20]:
        reg = "PASS" if r['passes_registration'] else ""
        print(f"  {str(r['pair_sorted']):<22}"
              f"{r['a']:>6}{r['b']:>6}"
              f"{r['n_a_to_b']:>8}{r['n_b_to_a']:>8}"
              f"{r['asymmetry']:>+8.3f}{r['binomial_p']:>10.5f}"
              f"{r['p_adjusted_BH']:>10.5f}{reg:>6}")

    n_asym_pass = sum(1 for r in asym_results if r['passes_registration'])
    print(f"\n  Asymmetries passing registration (FDR + effect-size): {n_asym_pass}")

    print("\nStep 5: Forbidden bigram test...")
    forbidden_results = run_forbidden_test(bigrams, null_counts)
    print(f"  Candidates (observed=0, expected>={N_FLOOR_FORBIDDEN_EXPECTED}): {len(forbidden_results)}")
    print(f"\n  {'a':>6}{'b':>6}{'obs':>6}{'expected':>10}{'null_std':>10}"
          f"{'null_p(obs=0)':>16}{'reg?':>6}")
    print("  " + "-" * 60)
    for r in forbidden_results:
        reg = "PASS" if r['passes_registration'] else ""
        print(f"  {r['a']:>6}{r['b']:>6}{r['observed']:>6}{r['null_expected']:>10.2f}"
              f"{r['null_std']:>10.3f}{r['empirical_null_p_observed_zero']:>16.4f}{reg:>6}")

    n_forbidden_pass = sum(1 for r in forbidden_results if r['passes_registration'])
    print(f"\n  Forbidden bigrams passing registration: {n_forbidden_pass}")

    # Verdict
    print("\n" + "=" * 90)
    print("VERDICT")
    print("=" * 90)

    if n_asym_pass >= 1 and n_forbidden_pass >= 1:
        verdict = ("TIER 2 REGISTRABLE: closure has internal bigram grammar. "
                   f"{n_asym_pass} directional asymmetries + {n_forbidden_pass} forbidden bigrams "
                   "both pass pre-registered thresholds.")
    elif n_asym_pass >= 1:
        verdict = ("TIER 3: directional asymmetries detected ({n_asym_pass}) but no "
                   "forbidden bigrams. Closure has directional preference but no hard "
                   "constraint structure.")
        verdict = verdict.format(n_asym_pass=n_asym_pass)
    elif n_forbidden_pass >= 1:
        verdict = ("TIER 3: forbidden bigrams detected ({n_forbidden_pass}) but no "
                   "directional asymmetries. Closure has hard constraints but no preference.")
        verdict = verdict.format(n_forbidden_pass=n_forbidden_pass)
    else:
        verdict = ("NO CONSTRAINT: neither directional asymmetry nor forbidden bigrams "
                   "pass pre-registered thresholds. Closure clustering (C2030) appears "
                   "to be unstructured at the bigram level.")

    print(f"\n  {verdict}")

    # Summary stats
    print(f"\nDescriptive stats:")
    print(f"  Total LATE-LATE bigrams: {total_late_late}")
    print(f"  Unique bigram types: {len(bigrams)} of {len(LATE_INVENTORY)**2} possible")
    print(f"  Most-asymmetric pair: {asym_results[0] if asym_results else None}")
    print(f"  Strongest forbidden candidate: {forbidden_results[0] if forbidden_results else None}")

    out = {
        "method": "PHASE_703 closure protocol bigram grammar test",
        "late_inventory": LATE_INVENTORY,
        "pre_registered_thresholds": {
            "N_floor_FDR": N_FLOOR_FDR,
            "N_floor_forbidden_expected": N_FLOOR_FORBIDDEN_EXPECTED,
            "asymmetry_effect_floor": ASYMMETRY_EFFECT_FLOOR,
            "FDR_threshold": FDR_THRESHOLD,
            "forbidden_null_p_threshold": FORBIDDEN_NULL_P_THRESHOLD,
        },
        "total_lines": len(lines),
        "total_late_late_bigrams": total_late_late,
        "bigram_counts": {f"{a}->{b}": c for (a, b), c in bigrams.most_common()},
        "directional_asymmetry_results": asym_results,
        "forbidden_bigram_results": forbidden_results,
        "n_asymmetries_passing": n_asym_pass,
        "n_forbidden_passing": n_forbidden_pass,
        "verdict": verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
