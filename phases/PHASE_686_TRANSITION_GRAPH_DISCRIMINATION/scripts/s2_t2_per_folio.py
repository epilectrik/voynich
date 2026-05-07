#!/usr/bin/env python3
"""
T2: Per-folio order constraint test.

Hypothesis: per-folio z_mu averaged across all folios is significantly
negative (one-sample t-test p<0.001), confirming order constraints
at folio level not just corpus aggregate.

For each folio with n>=100 tokens:
  z_mu(f) = (mu_actual - mean_shuffle_mu) / std_shuffle_mu over 200 shuffles.
"""
import sys
import json
import random
import statistics
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

random.seed(42)


def filter_h_track_by_folio():
    """Group H-track tokens by folio. Returns {folio: [token_words]}."""
    tx = Transcript()
    by_folio = defaultdict(list)
    folio_section = {}
    folio_language = {}
    for tok in tx.all(h_only=True):
        if tok.is_label:
            continue
        if tok.is_uncertain:
            continue
        if not tok.word:
            continue
        by_folio[tok.folio].append(tok.word)
        folio_section[tok.folio] = tok.section
        folio_language[tok.folio] = tok.language
    return dict(by_folio), folio_section, folio_language


def build_transition_graph(tokens):
    V = set(tokens)
    edges = set()
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i+1]
        if a == b:
            continue
        edges.add(frozenset([a, b]))

    parent = {n: n for n in V}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for edge in edges:
        a, b = list(edge)
        union(a, b)

    roots = {find(n) for n in V}
    return V, edges, len(roots)


def circuit_rank(V, E, c):
    return len(E) - len(V) + c


def folio_zmu(tokens, n_shuffles=200, rng=None):
    """Compute z_mu = (mu_actual - mean(shuffle)) / std(shuffle)."""
    if rng is None:
        rng = random.Random(42)
    V, E, c = build_transition_graph(tokens)
    mu_actual = circuit_rank(V, E, c)

    shuffle_mus = []
    for _ in range(n_shuffles):
        shuffled = tokens.copy()
        rng.shuffle(shuffled)
        Vs, Es, cs = build_transition_graph(shuffled)
        shuffle_mus.append(circuit_rank(Vs, Es, cs))

    mean_s = statistics.mean(shuffle_mus)
    std_s = statistics.stdev(shuffle_mus) if len(shuffle_mus) > 1 else 0.0

    if std_s == 0:
        return None  # degenerate folio (e.g., all tokens identical)

    return {
        'mu_actual': mu_actual,
        'mean_shuffle': mean_s,
        'std_shuffle': std_s,
        'z_mu': (mu_actual - mean_s) / std_s,
        'n_tokens': len(tokens),
        'n_types': len(V),
    }


def one_sample_t_test(values, mu0=0.0):
    """Simple one-sample t-test against mu0. Returns (t, df)."""
    n = len(values)
    mean_v = statistics.mean(values)
    std_v = statistics.stdev(values)
    se = std_v / (n ** 0.5)
    t = (mean_v - mu0) / se
    df = n - 1
    return t, df, mean_v, std_v


def t_to_p_one_sided_neg(t, df):
    """Approximate one-sided p-value for t < 0 using normal approximation
    when df is large. For df > 30 the normal approximation is acceptable."""
    import math
    # Use normal approximation since df will be ~100+
    # P(T < t) = P(Z < t) for large df
    return 0.5 * (1 + math.erf(t / math.sqrt(2)))


def main():
    print("Loading H-track tokens grouped by folio...")
    by_folio, folio_section, folio_language = filter_h_track_by_folio()

    eligible_folios = [f for f, toks in by_folio.items() if len(toks) >= 100]
    print(f"  Total folios: {len(by_folio)}")
    print(f"  Folios with n>=100 tokens: {len(eligible_folios)}")

    print(f"\nComputing per-folio z_mu (200 shuffles each)...")
    results = {}
    for i, folio in enumerate(sorted(eligible_folios)):
        tokens = by_folio[folio]
        # Use folio-specific seed derived from base seed for independence
        rng = random.Random(42 + i)
        result = folio_zmu(tokens, n_shuffles=200, rng=rng)
        if result is not None:
            result['folio'] = folio
            result['section'] = folio_section.get(folio, '')
            result['language'] = folio_language.get(folio, '')
            results[folio] = result
        if (i + 1) % 20 == 0:
            print(f"    {i+1}/{len(eligible_folios)} done")

    z_values = [r['z_mu'] for r in results.values()]
    n = len(z_values)
    mean_z = statistics.mean(z_values)
    std_z = statistics.stdev(z_values)

    t, df, _, _ = one_sample_t_test(z_values, mu0=0.0)
    p_one_sided = t_to_p_one_sided_neg(t, df)

    print(f"\n  N folios analyzed: {n}")
    print(f"  Mean z_mu = {mean_z:.3f}")
    print(f"  Std z_mu = {std_z:.3f}")
    print(f"  One-sample t = {t:.3f} (df={df})")
    print(f"  One-sided p (z_mu < 0) = {p_one_sided:.6f}")

    # Distribution
    n_below_zero = sum(1 for z in z_values if z < 0)
    n_below_neg2 = sum(1 for z in z_values if z < -2)
    n_above_pos2 = sum(1 for z in z_values if z > 2)

    print(f"\n  Folios with z_mu < 0:   {n_below_zero}/{n} ({100*n_below_zero/n:.1f}%)")
    print(f"  Folios with z_mu < -2:  {n_below_neg2}/{n} ({100*n_below_neg2/n:.1f}%)")
    print(f"  Folios with z_mu > +2:  {n_above_pos2}/{n}")

    pass_dir = mean_z < 0
    pass_p = p_one_sided < 0.001
    verdict = "PASS" if (pass_dir and pass_p) else "FAIL"

    print(f"\n  Pre-reg threshold: mean(z_mu) < 0 AND one-sample t-test p<0.001")
    print(f"  Verdict: {verdict}")

    # Save full results
    out = {
        'test': 'T2',
        'hypothesis': 'mean(per-folio z_mu) < 0, one-sample t-test p<0.001',
        'n_folios_analyzed': n,
        'min_tokens_per_folio': 100,
        'shuffles_per_folio': 200,
        'mean_z_mu': mean_z,
        'std_z_mu': std_z,
        't_statistic': t,
        'df': df,
        'p_one_sided': p_one_sided,
        'n_folios_below_zero': n_below_zero,
        'n_folios_below_neg2': n_below_neg2,
        'n_folios_above_pos2': n_above_pos2,
        'threshold_p': 0.001,
        'pass_direction': pass_dir,
        'pass_p': pass_p,
        'verdict': verdict,
        'per_folio': list(results.values()),
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 't2_per_folio_zscores.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
