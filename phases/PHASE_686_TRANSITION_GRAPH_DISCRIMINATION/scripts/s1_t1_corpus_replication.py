#!/usr/bin/env python3
"""
T1: Corpus-level replication of Earnhart's mu < shuffle mu result.

Hypothesis: mu_actual < mean(mu_shuffle) at one-sided p<0.001 over 1000
frequency-shuffles preserving unigram counts.

Locked methodology (Phase 686 INDEX.md):
- H-track only, no labels, no asterisks, no empty tokens
- Full corpus (matching Earnhart's "Full manuscript" row: A + B + AZC mixed)
- Token = exact word string (no morphological normalization)
- Self-loops excluded from incidence graph (Earnhart Remark 4.2)
- Edges undirected (graph treated as 1-simplicial complex for Hodge)
- mu = |E| - |V| + c
- 1000 shuffles, RNG seed = 42
"""
import sys
import json
import random
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

random.seed(42)


def filter_h_track():
    """All H-track tokens, no labels, no asterisks, no empty."""
    tx = Transcript()
    tokens = []
    for tok in tx.all(h_only=True):
        if tok.is_label:
            continue
        if tok.is_uncertain:
            continue
        if not tok.word:
            continue
        tokens.append(tok.word)
    return tokens


def build_transition_graph(tokens):
    """
    Build undirected transition graph.

    Returns: (V, E, c) where V is set of types, E is set of frozenset edges,
    c is number of connected components.
    """
    V = set(tokens)
    edges = set()
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i+1]
        if a == b:
            continue  # self-loops excluded per Remark 4.2
        edges.add(frozenset([a, b]))

    # Connected components via union-find
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


def main():
    print("Loading H-track tokens (full corpus, no labels, no asterisks)...")
    tokens = filter_h_track()
    print(f"  Total tokens: {len(tokens)}")
    print(f"  Unique types: {len(set(tokens))}")

    print("\nBuilding actual transition graph...")
    V, E, c = build_transition_graph(tokens)
    mu_actual = circuit_rank(V, E, c)
    print(f"  |V| = {len(V)}")
    print(f"  |E| = {len(E)}")
    print(f"  c  = {c}")
    print(f"  mu_actual = {mu_actual}")

    print(f"\nRunning 1000 frequency-shuffles (preserving unigram counts)...")
    shuffle_mus = []
    for i in range(1000):
        shuffled = tokens.copy()
        random.shuffle(shuffled)
        Vs, Es, cs = build_transition_graph(shuffled)
        shuffle_mus.append(circuit_rank(Vs, Es, cs))
        if (i + 1) % 100 == 0:
            print(f"    {i+1}/1000 done")

    mean_shuffle = statistics.mean(shuffle_mus)
    std_shuffle = statistics.stdev(shuffle_mus)
    z = (mu_actual - mean_shuffle) / std_shuffle

    n_le = sum(1 for m in shuffle_mus if m <= mu_actual)
    p_one_sided = max(n_le, 1) / len(shuffle_mus)

    print(f"\n  mean(mu_shuffle) = {mean_shuffle:.1f}")
    print(f"  std(mu_shuffle)  = {std_shuffle:.2f}")
    print(f"  z = {z:.2f}")
    print(f"  one-sided p (mu_actual <= mu_shuffle) = {p_one_sided:.4f}")

    threshold_z = -3.09
    pass_z = z < threshold_z
    pass_p = p_one_sided < 0.001
    verdict = "PASS" if (pass_z and pass_p) else "FAIL"

    print(f"\n  Pre-reg threshold: z < -3.09 AND p < 0.001")
    print(f"  Verdict: {verdict}")

    print(f"\n  Earnhart reference (full manuscript):")
    print(f"    mu_actual_earnhart = 22675")
    print(f"    mean_shuffle_earnhart = 24506")
    print(f"    Earnhart gap: {22675 - 24506} = -1831")
    print(f"    Our gap: {mu_actual - mean_shuffle:.1f}")

    out = {
        'test': 'T1',
        'hypothesis': 'mu_actual < mean(mu_shuffle), one-sided p<0.001',
        'tokens': len(tokens),
        'unique_types': len(set(tokens)),
        'mu_actual': mu_actual,
        'V': len(V),
        'E': len(E),
        'c': c,
        'mean_shuffle_mu': mean_shuffle,
        'std_shuffle_mu': std_shuffle,
        'min_shuffle_mu': min(shuffle_mus),
        'max_shuffle_mu': max(shuffle_mus),
        'z': z,
        'p_one_sided': p_one_sided,
        'n_shuffles': 1000,
        'threshold_z': threshold_z,
        'threshold_p': 0.001,
        'pass_z': pass_z,
        'pass_p': pass_p,
        'verdict': verdict,
        'earnhart_reference': {
            'mu_actual': 22675,
            'mean_shuffle_mu': 24506,
            'gap': -1831,
        },
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 't1_corpus_replication.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
