#!/usr/bin/env python3
"""
Phase 688 — qokedy context propagation tier decomposition.

For each (prev, qokedy, next) triplet, classify by (prev, next) prefix tier:
  - qo-cluster: prev qo-prefix AND next qo-prefix
  - boundary:   exactly one of {prev, next} has qo-prefix
  - cross:      neither prev nor next has qo-prefix

Compute per-tier MI(prev; next) and z-score vs 200-shuffle null restricted
to the tier.

Pre-registered (Phase 688 INDEX.md):
  T1 (primary): qokedy z_cross > +1.0 (operational embedding)
  T2 (diagnostic): z_qo_cluster - z_cross > +1.0
  T4 (comparison): same-prefix-tier decomposition for top-9 from Phase 687
"""
import sys
import json
import math
import random
import statistics
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript


def get_currier_b_tokens():
    tx = Transcript()
    tokens = []
    for tok in tx.currier_b():
        if not tok.word:
            continue
        tokens.append(tok.word)
    return tokens


def get_prefix_for_token(target_token):
    """Return the prefix of the target token as a string, for tier classification.
    Uses the empirical prefix of the token: first 2 chars if they form a known
    prefix start ('qo','ok','ot','ol','ch','sh','da','ct'), else first letter group.

    For Phase 688 we use: qokedy -> 'qo'; qotar -> 'qo'; chol -> 'ch'; etc.
    Match the literal first 2-char prefix of the target.
    """
    if len(target_token) >= 2:
        return target_token[:2]
    return target_token


def has_prefix(token, prefix):
    """True if token starts with prefix string."""
    return token.startswith(prefix)


def classify_pair(prev, nxt, target_prefix):
    """
    Classify (prev, next) pair relative to target_prefix:
      'cluster': prev AND next have target_prefix
      'boundary': exactly one of prev/next has target_prefix
      'cross': neither has target_prefix
    """
    p = has_prefix(prev, target_prefix)
    n = has_prefix(nxt, target_prefix)
    if p and n:
        return 'cluster'
    if not p and not n:
        return 'cross'
    return 'boundary'


def get_triplets_for_target(tokens, target):
    """Find all (prev, target, next) triplets for given middle target token."""
    out = []
    for i in range(1, len(tokens) - 1):
        if tokens[i] == target:
            out.append((tokens[i-1], tokens[i+1]))
    return out


def mutual_info(pairs):
    n = len(pairs)
    if n < 2:
        return 0.0
    px = Counter(p[0] for p in pairs)
    py = Counter(p[1] for p in pairs)
    pxy = Counter(pairs)
    mi = 0.0
    for (x, y), nxy in pxy.items():
        pxy_val = nxy / n
        px_val = px[x] / n
        py_val = py[y] / n
        mi += pxy_val * math.log2(pxy_val / (px_val * py_val))
    return mi


def shuffle_mi(pairs, n_shuffles, rng):
    if len(pairs) < 2:
        return [0.0] * n_shuffles
    prevs = [p[0] for p in pairs]
    nexts = [p[1] for p in pairs]
    mis = []
    for _ in range(n_shuffles):
        ps = prevs.copy()
        rng.shuffle(ps)
        mis.append(mutual_info(list(zip(ps, nexts))))
    return mis


def per_tier_mi(triplets, target_prefix, salt=0):
    """
    For triplets [(prev, next), ...], split into tiers and compute MI/z per tier.

    Returns dict tier -> {n, mi_actual, mi_null_mean, mi_null_std, z}
    """
    by_tier = defaultdict(list)
    for prev, nxt in triplets:
        by_tier[classify_pair(prev, nxt, target_prefix)].append((prev, nxt))

    out = {}
    for tier in ('cluster', 'boundary', 'cross'):
        pairs = by_tier.get(tier, [])
        n = len(pairs)
        if n < 2:
            out[tier] = {
                'n': n, 'mi_actual': 0.0, 'mi_null_mean': 0.0,
                'mi_null_std': 0.0, 'z': None, 'sufficient': False,
            }
            continue
        mi_a = mutual_info(pairs)
        rng = random.Random(42 + salt + (hash(tier) % 1000000))
        nulls = shuffle_mi(pairs, n_shuffles=200, rng=rng)
        mn = statistics.mean(nulls)
        sd = statistics.stdev(nulls) if len(nulls) > 1 else 0.0
        z = (mi_a - mn) / sd if sd > 0 else 0.0
        out[tier] = {
            'n': n,
            'mi_actual': mi_a,
            'mi_null_mean': mn,
            'mi_null_std': sd,
            'z': z,
            'sufficient': n >= 30,
        }
    return out


def main():
    print("Loading Currier B tokens...")
    tokens = get_currier_b_tokens()
    print(f"  Total: {len(tokens)}")

    target = 'qokedy'
    target_prefix = get_prefix_for_token(target)
    print(f"\nPrimary target: {target} (prefix='{target_prefix}')")

    triplets = get_triplets_for_target(tokens, target)
    print(f"  Triplets for {target}: {len(triplets)}")

    qokedy_results = per_tier_mi(triplets, target_prefix, salt=0)

    print(f"\nPer-tier results for {target}:")
    for tier in ('cluster', 'boundary', 'cross'):
        r = qokedy_results[tier]
        suf = '' if r['sufficient'] else ' (n<30, INSUFFICIENT)'
        z_str = f"{r['z']:+.2f}" if r['z'] is not None else 'N/A'
        print(f"  {tier:9s}: n={r['n']:3d}, MI={r['mi_actual']:.3f} bits, "
              f"null={r['mi_null_mean']:.3f}, z={z_str}{suf}")

    # T1 adjudication
    cross = qokedy_results['cross']
    if not cross['sufficient']:
        t1 = 'INSUFFICIENT_DATA'
    elif cross['z'] is not None and cross['z'] > 1.0:
        t1 = 'PASS'
    else:
        t1 = 'FAIL'

    cluster_z = qokedy_results['cluster']['z']
    cross_z = qokedy_results['cross']['z']
    if (qokedy_results['cluster']['sufficient'] and
        qokedy_results['cross']['sufficient'] and
        cluster_z is not None and cross_z is not None):
        t2_diff = cluster_z - cross_z
        t2 = 'PASS' if t2_diff > 1.0 else 'FAIL'
    else:
        t2_diff = None
        t2 = 'INSUFFICIENT_DATA'

    print(f"\n  T1 (qokedy z_cross > +1.0):    "
          f"z_cross={cross_z if cross_z is not None else 'N/A'} -> {t1}")
    print(f"  T2 (z_cluster - z_cross > +1.0): "
          f"diff={t2_diff if t2_diff is not None else 'N/A'} -> {t2}")

    # T4: comparison set — top-9 from Phase 687 (excluding qokedy)
    comparison = ['qotar', 'chol', 'chcthy', 'okedy', 'dy',
                  'qokar', 's', 'shedy', 'okain']
    comparison_results = {}
    print(f"\nT4 comparison: top-9 context propagators (each at its own prefix tier):")
    for tok in comparison:
        prefix = get_prefix_for_token(tok)
        trips = get_triplets_for_target(tokens, tok)
        if len(trips) < 50:
            print(f"  {tok:10s} (prefix='{prefix}'): n_trips={len(trips)} <50, skipped")
            comparison_results[tok] = None
            continue
        res = per_tier_mi(trips, prefix, salt=hash(tok) % 1000000)
        cross_r = res['cross']
        z_str = (f"{cross_r['z']:+.2f}" if cross_r['z'] is not None else 'N/A')
        suf = '' if cross_r['sufficient'] else ' (n<30)'
        print(f"  {tok:10s} (prefix='{prefix}'): n_trips={len(trips):3d}, "
              f"n_cross={cross_r['n']:3d}, z_cross={z_str}{suf}")
        comparison_results[tok] = res

    # State-flush bottom of phase 687: also check
    flush_set = ['qokal', 'shey', 'al', 'ar', 'qoky']
    print(f"\nDiagnostic — state-flush-end tokens from Phase 687 (cross-tier):")
    flush_results = {}
    for tok in flush_set:
        prefix = get_prefix_for_token(tok)
        trips = get_triplets_for_target(tokens, tok)
        if len(trips) < 50:
            flush_results[tok] = None
            print(f"  {tok:10s}: n_trips={len(trips)} <50, skipped")
            continue
        res = per_tier_mi(trips, prefix, salt=hash(tok) % 1000000)
        cross_r = res['cross']
        z_str = f"{cross_r['z']:+.2f}" if cross_r['z'] is not None else 'N/A'
        flush_results[tok] = res
        print(f"  {tok:10s} (prefix='{prefix}'): n_cross={cross_r['n']:3d}, "
              f"z_cross={z_str}")

    # Final verdict and constraint
    print("\n" + "=" * 72)
    print(f"VERDICT: T1 = {t1}")
    if t1 == 'PASS':
        print(f"  qokedy operational embedding SUPPORTED — MI persists across cross-PREFIX pairs.")
    elif t1 == 'FAIL':
        print(f"  qokedy operational embedding REJECTED — MI is morphological clustering only.")
    else:
        print(f"  Methodology limit reached (n_cross < 30). No constraint registers.")
    print("=" * 72)

    out = {
        'phase': 688,
        'target': target,
        'target_prefix': target_prefix,
        'verdicts': {'T1': t1, 'T2': t2},
        'qokedy': qokedy_results,
        'comparison_top9': comparison_results,
        'flush_set_diagnostic': flush_results,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 't1_qokedy_tier_decomposition.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
