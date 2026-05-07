#!/usr/bin/env python3
"""
T1-T4: Mutual information through daiin/dar/saiin in Currier B.

For each token T appearing in middle position of (prev, T, next) triplets:
  I(prev; next | T) = empirical MI of prev/next given T as middle.

Compare to null (200 shuffles of prev within T): z_T = (I_actual - mean_null) / std_null.

Low z_T = state-flush behavior (predecessor doesn't predict successor).
High z_T = context propagation through T.

Pre-registered tests (per Phase 687 INDEX.md):
  T1: daiin z_T < median across eligible tokens
  T2: daiin z_T < +1.0 (not significantly above shuffle)
  T3: dar AND saiin both below median
  T4: at least one of {chedy, qokedy, qokeedy, qokeey, shedy} has z > 2 (sanity check)
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
    for tok in tx.currier_b():  # excludes labels and uncertain by default
        if not tok.word:
            continue
        tokens.append(tok.word)
    return tokens


def build_triplet_index(tokens):
    """For each middle token T, collect list of (prev, next) pairs."""
    triplets = defaultdict(list)
    for i in range(1, len(tokens) - 1):
        triplets[tokens[i]].append((tokens[i-1], tokens[i+1]))
    return triplets


def mutual_info(pairs):
    """Plug-in MI estimator: I(X;Y) from list of (x,y) tuples."""
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
    """Null distribution: shuffle prevs independently of nexts within T."""
    prevs = [p[0] for p in pairs]
    nexts = [p[1] for p in pairs]
    mis = []
    for _ in range(n_shuffles):
        prev_shuf = prevs.copy()
        rng.shuffle(prev_shuf)
        mis.append(mutual_info(list(zip(prev_shuf, nexts))))
    return mis


def main():
    print("Loading Currier B tokens (H-track, no labels, no asterisks)...")
    tokens = get_currier_b_tokens()
    print(f"  Total tokens: {len(tokens)}")

    print("\nBuilding triplet index...")
    triplets = build_triplet_index(tokens)
    print(f"  Distinct middle tokens: {len(triplets)}")

    eligible = {t: pairs for t, pairs in triplets.items() if len(pairs) >= 50}
    print(f"  Tokens with n_triplets >= 50: {len(eligible)}")

    print(f"\nComputing MI per eligible token (200 shuffles each)...")
    results = {}
    for i, (token, pairs) in enumerate(eligible.items()):
        n = len(pairs)
        mi_actual = mutual_info(pairs)
        # Per-token RNG seed (deterministic but token-distinct)
        token_seed = (42 + abs(hash(token))) % (2**31 - 1)
        rng = random.Random(token_seed)
        mi_null = shuffle_mi(pairs, n_shuffles=200, rng=rng)
        mean_null = statistics.mean(mi_null)
        std_null = statistics.stdev(mi_null) if len(mi_null) > 1 else 0.0
        z = (mi_actual - mean_null) / std_null if std_null > 0 else 0.0
        results[token] = {
            'n_triplets': n,
            'n_distinct_prev': len(set(p[0] for p in pairs)),
            'n_distinct_next': len(set(p[1] for p in pairs)),
            'mi_actual': mi_actual,
            'mi_null_mean': mean_null,
            'mi_null_std': std_null,
            'z': z,
        }
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(eligible)} done")

    # Rank by z (ascending = most state-flush-like)
    ranked = sorted(results.items(), key=lambda x: x[1]['z'])
    z_values = [r['z'] for r in results.values()]
    median_z = statistics.median(z_values)

    print(f"\n  Median z across {len(results)} eligible tokens: {median_z:.2f}")
    print(f"  Range: [{min(z_values):.2f}, {max(z_values):.2f}]")

    # ==== Pre-registered tests ====
    print("\n" + "=" * 72)
    print("PRE-REGISTERED TESTS")
    print("=" * 72)

    target_tokens = ['daiin', 'dar', 'saiin']
    target_results = {}
    for token in target_tokens:
        if token in results:
            r = results[token]
            rank = next(i for i, (t, _) in enumerate(ranked) if t == token)
            percentile = 100 * rank / len(ranked)
            target_results[token] = {
                'z': r['z'],
                'rank': rank + 1,
                'percentile': percentile,
                'n_triplets': r['n_triplets'],
                'mi_actual': r['mi_actual'],
                'mi_null_mean': r['mi_null_mean'],
            }
            print(f"\n  {token}: z={r['z']:+.2f}, rank={rank+1}/{len(ranked)} ({percentile:.0f}th %ile)")
            print(f"    n_triplets={r['n_triplets']}, distinct_prev={r['n_distinct_prev']}, distinct_next={r['n_distinct_next']}")
            print(f"    MI_actual={r['mi_actual']:.3f} bits, MI_null_mean={r['mi_null_mean']:.3f} bits")
        else:
            target_results[token] = None
            print(f"\n  {token}: NOT ELIGIBLE (n_triplets < 50)")

    # T1: daiin z < median
    daiin_z = target_results.get('daiin', {}).get('z') if target_results.get('daiin') else None
    t1_pass = daiin_z is not None and daiin_z < median_z
    print(f"\nT1 — daiin z < median ({median_z:.2f}): "
          f"daiin={daiin_z if daiin_z is not None else 'N/A'} -> "
          f"{'PASS' if t1_pass else 'FAIL'}")

    # T2: daiin z < +1.0
    t2_pass = daiin_z is not None and daiin_z < 1.0
    print(f"T2 — daiin z < +1.0: "
          f"daiin={daiin_z if daiin_z is not None else 'N/A'} -> "
          f"{'PASS' if t2_pass else 'FAIL'}")

    # T3: dar AND saiin both below median
    dar_z = target_results.get('dar', {}).get('z') if target_results.get('dar') else None
    saiin_z = target_results.get('saiin', {}).get('z') if target_results.get('saiin') else None
    dar_below = dar_z is not None and dar_z < median_z
    saiin_below = saiin_z is not None and saiin_z < median_z
    t3_pass = dar_below and saiin_below
    t3_partial = dar_below or saiin_below
    print(f"T3 — dar AND saiin < median: "
          f"dar={dar_z}, saiin={saiin_z} -> "
          f"{'PASS' if t3_pass else 'PARTIAL' if t3_partial else 'FAIL'}")

    # T4: methodology sanity check
    content_refs = ['chedy', 'qokedy', 'qokeedy', 'qokeey', 'shedy']
    content_zs = {}
    for token in content_refs:
        if token in results:
            content_zs[token] = results[token]['z']
    t4_pass = any(z > 2 for z in content_zs.values())
    print(f"T4 — at least one content ref token with z > 2: ", end='')
    for t, z in content_zs.items():
        marker = ' [*]' if z > 2 else ''
        print(f"{t}={z:+.2f}{marker}", end=' ')
    print(f"-> {'PASS' if t4_pass else 'FAIL'}")

    # ==== Summary ====
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  T1 (daiin < median):        {'PASS' if t1_pass else 'FAIL'}")
    print(f"  T2 (daiin < +1.0):          {'PASS' if t2_pass else 'FAIL'}")
    print(f"  T3 (dar AND saiin < median): {'PASS' if t3_pass else 'PARTIAL' if t3_partial else 'FAIL'}")
    print(f"  T4 (methodology sanity):    {'PASS' if t4_pass else 'FAIL'}")

    if not t4_pass:
        print(f"\n  WARNING: T4 failed — methodology underpowered. Constraint registration suspended.")
    elif t1_pass and t2_pass:
        print(f"\n  daiin state-flush hypothesis: SUPPORTED (T1 and T2 both pass)")
    elif t1_pass and not t2_pass:
        print(f"\n  daiin state-flush hypothesis: PARTIAL (unusually low MI but some propagation)")
    else:
        print(f"\n  daiin state-flush hypothesis: REJECTED (T1 failed)")

    print(f"\nTop 10 lowest z (most state-flush-like):")
    for t, r in ranked[:10]:
        print(f"  {t:20s}  z={r['z']:+.2f}  n={r['n_triplets']}  MI={r['mi_actual']:.2f}")

    print(f"\nTop 10 highest z (most context-propagating):")
    for t, r in ranked[-10:]:
        print(f"  {t:20s}  z={r['z']:+.2f}  n={r['n_triplets']}  MI={r['mi_actual']:.2f}")

    # Save
    out = {
        'phase': 687,
        'verdicts': {
            'T1': 'PASS' if t1_pass else 'FAIL',
            'T2': 'PASS' if t2_pass else 'FAIL',
            'T3': 'PASS' if t3_pass else ('PARTIAL' if t3_partial else 'FAIL'),
            'T4': 'PASS' if t4_pass else 'FAIL',
        },
        'state_flush_verdict': (
            'SUPPORTED' if t1_pass and t2_pass else
            'PARTIAL' if t1_pass and not t2_pass else
            'REJECTED' if t4_pass else 'METHODOLOGY_FAILED'
        ),
        'median_z': median_z,
        'min_z': min(z_values),
        'max_z': max(z_values),
        'n_eligible_tokens': len(eligible),
        'target_tokens': target_results,
        'content_reference_zs': content_zs,
        'top_10_lowest_z': [
            {'token': t, 'z': r['z'], 'n': r['n_triplets'],
             'mi': r['mi_actual'], 'mi_null_mean': r['mi_null_mean']}
            for t, r in ranked[:10]
        ],
        'top_10_highest_z': [
            {'token': t, 'z': r['z'], 'n': r['n_triplets'],
             'mi': r['mi_actual'], 'mi_null_mean': r['mi_null_mean']}
            for t, r in ranked[-10:]
        ],
        'all_results': results,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 't1_mi_per_token.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
