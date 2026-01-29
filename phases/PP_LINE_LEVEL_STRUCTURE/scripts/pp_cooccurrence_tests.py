"""
PP_LINE_LEVEL_STRUCTURE - Script 1: Co-occurrence Tests (T1-T3)

Tests whether PP MIDDLE co-occurrence within Currier A lines is random
or structured. Gated execution: T1 -> T2 -> T3.

Phase: PP_LINE_LEVEL_STRUCTURE
Constraints: C728-C730 (provisional)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

N_PERM = 1000
rng = np.random.RandomState(42)


def load_data():
    """Pre-compute per-folio, per-line PP MIDDLE structures in O(n)."""
    analyzer = RecordAnalyzer()
    folios = analyzer.get_folios()

    folio_records = {}
    folio_pp_pool = {}
    folio_line_pp = {}  # folio -> list of lists of PP MIDDLEs per line

    for fol in folios:
        records = analyzer.analyze_folio(fol)
        folio_records[fol] = records
        pool = set()
        line_pp = []
        for rec in records:
            line_mids = []
            for t in rec.tokens:
                if t.is_pp and t.middle:
                    pool.add(t.middle)
                    line_mids.append(t.middle)
            line_pp.append(line_mids)
        folio_pp_pool[fol] = pool
        folio_line_pp[fol] = line_pp

    return folios, folio_records, folio_pp_pool, folio_line_pp


def count_within_line_pairs(folio_line_pp):
    """Count co-occurring PP MIDDLE pairs across all lines with 2+ PP tokens."""
    pair_counts = defaultdict(int)
    total_pairs = 0
    lines_with_2plus = 0

    for fol, line_pp_list in folio_line_pp.items():
        for line_mids in line_pp_list:
            if len(line_mids) < 2:
                continue
            lines_with_2plus += 1
            mid_set = set(line_mids)
            for a, b in combinations(sorted(mid_set), 2):
                pair_counts[(a, b)] += 1
                total_pairs += 1

    return pair_counts, total_pairs, lines_with_2plus


def shuffle_within_folio(folio_line_pp, rng):
    """Shuffle PP MIDDLEs within each folio, preserving line lengths."""
    shuffled = {}
    for fol, line_pp_list in folio_line_pp.items():
        # Pool all PP MIDDLEs in this folio
        all_mids = []
        line_lengths = []
        for line_mids in line_pp_list:
            all_mids.extend(line_mids)
            line_lengths.append(len(line_mids))

        # Shuffle
        rng.shuffle(all_mids)

        # Redistribute preserving line lengths
        new_lines = []
        idx = 0
        for length in line_lengths:
            new_lines.append(all_mids[idx:idx + length])
            idx += length
        shuffled[fol] = new_lines

    return shuffled


def test_T1(folio_line_pp):
    """T1: PP MIDDLE Co-occurrence Structure.

    Null: PP MIDDLEs on each line are random draws from the folio pool.
    Test: permutation test on unique pair count and pair count variance.
    """
    print("=== T1: PP MIDDLE Co-occurrence Structure ===")

    # Observed
    obs_pairs, obs_total, lines_2plus = count_within_line_pairs(folio_line_pp)
    obs_unique = len(obs_pairs)
    obs_counts = list(obs_pairs.values())
    obs_variance = float(np.var(obs_counts)) if obs_counts else 0.0
    obs_max = max(obs_counts) if obs_counts else 0

    print(f"Lines with 2+ PP tokens: {lines_2plus}")
    print(f"Total within-line pairs: {obs_total}")
    print(f"Unique co-occurring pairs: {obs_unique}")
    print(f"Pair count variance: {obs_variance:.4f}")
    print(f"Max pair count: {obs_max}")

    # Top-10 enriched pairs
    top_pairs = sorted(obs_pairs.items(), key=lambda x: -x[1])[:10]
    print("Top 10 enriched pairs:")
    for (a, b), cnt in top_pairs:
        print(f"  {a} + {b}: {cnt}")

    # Permutation null
    null_unique = []
    null_variance = []
    for i in range(N_PERM):
        shuffled = shuffle_within_folio(folio_line_pp, rng)
        perm_pairs, _, _ = count_within_line_pairs(shuffled)
        null_unique.append(len(perm_pairs))
        perm_counts = list(perm_pairs.values())
        null_variance.append(float(np.var(perm_counts)) if perm_counts else 0.0)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_unique = np.array(null_unique)
    null_variance = np.array(null_variance)

    # p-values (two-sided for unique, upper-tail for variance)
    p_unique = float(np.mean(null_unique <= obs_unique))  # fewer unique = more concentrated
    p_unique_upper = float(np.mean(null_unique >= obs_unique))  # more unique = more dispersed
    p_variance = float(np.mean(null_variance >= obs_variance))

    # Enrichment ratio for top-10% pairs
    if obs_counts:
        threshold = np.percentile(obs_counts, 90)
        enriched = [c for c in obs_counts if c >= threshold]
        null_means = [float(np.mean(list(p.values()))) if p else 0
                      for p in [count_within_line_pairs(shuffle_within_folio(folio_line_pp, rng))[0]
                                for _ in range(50)]]
        enrichment_ratio = float(np.mean(enriched) / np.mean(null_means)) if null_means and np.mean(null_means) > 0 else 0
    else:
        enrichment_ratio = 0.0

    # Pass criteria: p < 0.01 for unique OR variance
    pass_unique = p_unique < 0.01 or p_unique_upper < 0.01
    pass_variance = p_variance < 0.01
    t1_pass = pass_unique or pass_variance

    result = {
        'test': 'T1_cooccurrence',
        'lines_with_2plus_pp': lines_2plus,
        'total_within_line_pairs': obs_total,
        'observed_unique_pairs': obs_unique,
        'observed_variance': obs_variance,
        'observed_max_count': obs_max,
        'null_unique_mean': float(np.mean(null_unique)),
        'null_unique_std': float(np.std(null_unique)),
        'null_variance_mean': float(np.mean(null_variance)),
        'null_variance_std': float(np.std(null_variance)),
        'p_unique_lower': p_unique,
        'p_unique_upper': p_unique_upper,
        'p_variance': p_variance,
        'enrichment_ratio_top10pct': enrichment_ratio,
        'top_10_pairs': [{'pair': list(p), 'count': c} for p, c in top_pairs],
        'pass_unique': pass_unique,
        'pass_variance': pass_variance,
        'PASS': t1_pass,
        'verdict': 'PASS' if t1_pass else 'FAIL'
    }

    direction = "FEWER" if p_unique < 0.01 else ("MORE" if p_unique_upper < 0.01 else "NORMAL")
    print(f"\nObserved unique: {obs_unique}, Null mean: {np.mean(null_unique):.1f} +/- {np.std(null_unique):.1f}")
    print(f"Unique pairs direction: {direction} (p_lower={p_unique:.4f}, p_upper={p_unique_upper:.4f})")
    print(f"Observed variance: {obs_variance:.4f}, Null mean: {np.mean(null_variance):.4f} +/- {np.std(null_variance):.4f}")
    print(f"Variance p={p_variance:.4f}")
    print(f"T1 verdict: {'PASS' if t1_pass else 'FAIL'}")

    return result, obs_pairs


def test_T2(folio_line_pp, obs_pairs):
    """T2: Incompatibility as Driver.

    Computes within-folio avoidance pairs (MIDDLEs in same folio but never
    on same line) and tests whether avoidance explains all T1 non-randomness.
    """
    print("\n=== T2: Incompatibility as Driver ===")

    # Step 1: Compute within-folio avoidance pairs
    # For each folio, find all MIDDLE pairs that exist in the folio
    # but never appear on the same line
    avoidance_pairs = set()  # pairs that never co-occur within any line
    cooccurring_pairs = set()  # pairs that DO co-occur within at least one line

    for fol, line_pp_list in folio_line_pp.items():
        # All PP MIDDLEs in this folio
        folio_mids = set()
        for line_mids in line_pp_list:
            folio_mids.update(line_mids)

        # All possible pairs within this folio
        folio_possible = set()
        for a, b in combinations(sorted(folio_mids), 2):
            folio_possible.add((a, b))

        # Pairs that co-occur within a line
        for line_mids in line_pp_list:
            if len(line_mids) < 2:
                continue
            mid_set = set(line_mids)
            for a, b in combinations(sorted(mid_set), 2):
                cooccurring_pairs.add((a, b))

        # Avoidance: in folio but never on same line
        for pair in folio_possible:
            if pair not in cooccurring_pairs:
                avoidance_pairs.add(pair)

    # Remove from avoidance any pair that co-occurs in ANY folio
    avoidance_pairs -= cooccurring_pairs

    print(f"Total co-occurring pairs (observed): {len(cooccurring_pairs)}")
    print(f"Within-folio avoidance pairs: {len(avoidance_pairs)}")

    # Step 2: Check how many shuffled within-line pairs are avoidance pairs
    # In the free shuffle, avoidance pairs CAN land on the same line
    avoidance_in_shuffle = []
    legal_variance_null = []

    for i in range(N_PERM):
        shuffled = shuffle_within_folio(folio_line_pp, rng)
        perm_pairs, _, _ = count_within_line_pairs(shuffled)

        # Count avoidance pairs that appear in shuffle
        avoidance_count = sum(1 for p in perm_pairs if p in avoidance_pairs)
        avoidance_in_shuffle.append(avoidance_count)

        # Legal-only variance
        legal_counts = [c for p, c in perm_pairs.items() if p not in avoidance_pairs]
        legal_variance_null.append(float(np.var(legal_counts)) if legal_counts else 0.0)

        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    avoidance_in_shuffle = np.array(avoidance_in_shuffle)
    legal_variance_null = np.array(legal_variance_null)

    # Observed legal-only stats
    legal_obs_counts = [c for p, c in obs_pairs.items() if p not in avoidance_pairs]
    obs_legal_variance = float(np.var(legal_obs_counts)) if legal_obs_counts else 0.0
    obs_legal_unique = len(legal_obs_counts)

    # Avoidance rate in observed data (should be 0 by definition)
    obs_avoidance_count = sum(1 for p in obs_pairs if p in avoidance_pairs)

    # C475 line-level scope: illegal pairs should be ~0 in observed data
    total_obs_pairs = sum(obs_pairs.values())
    illegal_rate = obs_avoidance_count / total_obs_pairs if total_obs_pairs > 0 else 0

    # Among legal pairs: does variance exceed null?
    p_legal_variance = float(np.mean(legal_variance_null >= obs_legal_variance))

    # Mean avoidance pairs in shuffle (these are the "false positives" the free shuffle creates)
    mean_avoidance_in_shuffle = float(np.mean(avoidance_in_shuffle))

    # Pass criteria
    avoidance_confirmed = illegal_rate < 0.02  # C475 holds at line level
    structure_beyond = p_legal_variance < 0.05  # structure beyond incompatibility

    t2_pass = structure_beyond  # The key question: is there structure BEYOND incompatibility?

    result = {
        'test': 'T2_incompatibility_driver',
        'cooccurring_pair_types': len(cooccurring_pairs),
        'avoidance_pair_types': len(avoidance_pairs),
        'observed_avoidance_violations': obs_avoidance_count,
        'illegal_rate': illegal_rate,
        'avoidance_confirmed': avoidance_confirmed,
        'mean_avoidance_in_shuffle': mean_avoidance_in_shuffle,
        'observed_legal_unique': obs_legal_unique,
        'observed_legal_variance': obs_legal_variance,
        'null_legal_variance_mean': float(np.mean(legal_variance_null)),
        'null_legal_variance_std': float(np.std(legal_variance_null)),
        'p_legal_variance': p_legal_variance,
        'structure_beyond_incompatibility': structure_beyond,
        'PASS': t2_pass,
        'verdict': 'PASS' if t2_pass else 'FAIL'
    }

    print(f"\nObserved avoidance violations: {obs_avoidance_count} (rate: {illegal_rate:.4f})")
    print(f"Avoidance confirmed (C475 at line level): {avoidance_confirmed}")
    print(f"Mean avoidance pairs in free shuffle: {mean_avoidance_in_shuffle:.1f}")
    print(f"Legal-only observed variance: {obs_legal_variance:.4f}")
    print(f"Legal-only null variance: {np.mean(legal_variance_null):.4f} +/- {np.std(legal_variance_null):.4f}")
    print(f"Legal variance p={p_legal_variance:.4f}")
    print(f"Structure beyond incompatibility: {structure_beyond}")
    print(f"T2 verdict: {'PASS' if t2_pass else 'FAIL'}")

    return result


def test_T3(folio_line_pp, obs_pairs, avoidance_pairs=None):
    """T3: Attraction Clusters (gated on T2 PASS).

    Build co-occurrence graph from enriched legal pairs, detect communities.
    """
    print("\n=== T3: Attraction Clusters ===")

    # Compute expected co-occurrence per pair under null
    # Use mean from 200 shuffles for better estimate
    pair_expected = defaultdict(float)
    for i in range(200):
        shuffled = shuffle_within_folio(folio_line_pp, rng)
        perm_pairs, _, _ = count_within_line_pairs(shuffled)
        for p, c in perm_pairs.items():
            pair_expected[p] += c / 200.0
        if (i + 1) % 50 == 0:
            print(f"  Computing expected: {i + 1}/200")

    # Build enrichment graph: edges where observed/expected > 1.5x
    # Only among legal pairs (not avoidance pairs)
    if avoidance_pairs is None:
        avoidance_pairs = set()

    edges = []
    nodes = set()
    enrichment_ratios = {}
    for pair, obs_count in obs_pairs.items():
        if pair in avoidance_pairs:
            continue
        exp = pair_expected.get(pair, 0)
        if exp > 0:
            ratio = obs_count / exp
            enrichment_ratios[pair] = ratio
            if ratio > 1.5:
                edges.append(pair)
                nodes.add(pair[0])
                nodes.add(pair[1])

    print(f"Enriched edges (obs/exp > 1.5x): {len(edges)}")
    print(f"Nodes in enrichment graph: {len(nodes)}")

    if len(edges) < 3 or len(nodes) < 6:
        print("Insufficient edges/nodes for community detection")
        result = {
            'test': 'T3_attraction_clusters',
            'enriched_edges': len(edges),
            'enriched_nodes': len(nodes),
            'PASS': False,
            'verdict': 'FAIL (insufficient data)',
            'reason': 'Too few enriched edges for community detection'
        }
        return result

    # Build adjacency for community detection
    # Use simple greedy modularity (no external deps beyond numpy/scipy)
    from collections import deque

    # Build adjacency list
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    # Connected components first
    visited = set()
    components = []
    node_list = sorted(nodes)
    for n in node_list:
        if n in visited:
            continue
        comp = set()
        queue = deque([n])
        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)
            comp.add(curr)
            for nb in adj[curr]:
                if nb not in visited:
                    queue.append(nb)
        components.append(comp)

    # Modularity Q for the component partition
    m = len(edges)
    degree = {n: len(adj[n]) for n in nodes}

    def modularity(partition):
        """Compute Newman-Girvan modularity."""
        q = 0.0
        for community in partition:
            for u in community:
                for v in community:
                    if u >= v:
                        continue
                    aij = 1.0 if v in adj[u] else 0.0
                    q += aij - (degree.get(u, 0) * degree.get(v, 0)) / (2.0 * m)
        return q / (2.0 * m) if m > 0 else 0.0

    obs_Q = modularity(components)

    # Permutation test for Q: shuffle node labels
    null_Q = []
    for i in range(N_PERM):
        # Shuffle node assignments to components
        shuffled_nodes = list(node_list)
        rng.shuffle(shuffled_nodes)
        # Create fake partition with same sizes
        fake_partition = []
        idx = 0
        for comp in components:
            fake_partition.append(set(shuffled_nodes[idx:idx + len(comp)]))
            idx += len(comp)
        null_Q.append(modularity(fake_partition))
        if (i + 1) % 200 == 0:
            print(f"  Modularity permutation {i + 1}/{N_PERM}")

    null_Q = np.array(null_Q)
    p_modularity = float(np.mean(null_Q >= obs_Q))

    # Count clusters with 3+ members
    large_clusters = [c for c in components if len(c) >= 3]

    t3_pass = obs_Q > 0.3 and p_modularity < 0.01 and len(large_clusters) >= 3

    result = {
        'test': 'T3_attraction_clusters',
        'enriched_edges': len(edges),
        'enriched_nodes': len(nodes),
        'n_components': len(components),
        'component_sizes': sorted([len(c) for c in components], reverse=True),
        'large_clusters_3plus': len(large_clusters),
        'modularity_Q': float(obs_Q),
        'null_Q_mean': float(np.mean(null_Q)),
        'null_Q_std': float(np.std(null_Q)),
        'p_modularity': p_modularity,
        'PASS': t3_pass,
        'verdict': 'PASS' if t3_pass else 'FAIL'
    }

    # Report cluster contents if present
    if large_clusters:
        result['clusters'] = [sorted(list(c)) for c in sorted(large_clusters, key=len, reverse=True)[:5]]

    print(f"\nModularity Q: {obs_Q:.4f} (null: {np.mean(null_Q):.4f} +/- {np.std(null_Q):.4f})")
    print(f"p_modularity: {p_modularity:.4f}")
    print(f"Components: {len(components)}, with 3+ members: {len(large_clusters)}")
    print(f"Component sizes: {sorted([len(c) for c in components], reverse=True)[:10]}")
    print(f"T3 verdict: {'PASS' if t3_pass else 'FAIL'}")

    return result


def main():
    print("PP_LINE_LEVEL_STRUCTURE - Script 1: Co-occurrence Tests")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    folios, folio_records, folio_pp_pool, folio_line_pp = load_data()

    # Summary stats
    total_lines = sum(len(v) for v in folio_line_pp.values())
    lines_with_pp = sum(1 for v in folio_line_pp.values() for l in v if len(l) > 0)
    lines_with_2pp = sum(1 for v in folio_line_pp.values() for l in v if len(l) >= 2)
    total_pp = sum(len(l) for v in folio_line_pp.values() for l in v)
    all_mids = set()
    for v in folio_line_pp.values():
        for l in v:
            all_mids.update(l)

    print(f"Folios: {len(folios)}")
    print(f"Total lines: {total_lines}")
    print(f"Lines with PP tokens: {lines_with_pp}")
    print(f"Lines with 2+ PP tokens: {lines_with_2pp}")
    print(f"Total PP token occurrences: {total_pp}")
    print(f"Unique PP MIDDLEs: {len(all_mids)}")

    results = {}

    # T1: Co-occurrence structure
    t1_result, obs_pairs = test_T1(folio_line_pp)
    results['T1_cooccurrence'] = t1_result

    if not t1_result['PASS']:
        print("\n--- T1 FAIL: PP co-occurrence is random. Stopping gated chain. ---")
        results['gate_status'] = 'T1_FAIL_STOP'
        results['T2_incompatibility_driver'] = {'skipped': True, 'reason': 'T1 FAIL'}
        results['T3_attraction_clusters'] = {'skipped': True, 'reason': 'T1 FAIL'}
    else:
        print("\n--- T1 PASS: PP co-occurrence is non-random. Proceeding to T2. ---")

        # T2: Incompatibility as driver
        t2_result = test_T2(folio_line_pp, obs_pairs)
        results['T2_incompatibility_driver'] = t2_result

        if not t2_result['PASS']:
            print("\n--- T2 FAIL: Incompatibility explains all structure. Skipping T3. ---")
            results['gate_status'] = 'T2_FAIL_STOP'
            results['T3_attraction_clusters'] = {'skipped': True, 'reason': 'T2 FAIL'}
        else:
            print("\n--- T2 PASS: Structure beyond incompatibility. Proceeding to T3. ---")
            t3_result = test_T3(folio_line_pp, obs_pairs)
            results['T3_attraction_clusters'] = t3_result
            results['gate_status'] = 'T3_COMPLETE'

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key in ['T1_cooccurrence', 'T2_incompatibility_driver', 'T3_attraction_clusters']:
        r = results[key]
        if r.get('skipped'):
            print(f"  {key}: SKIPPED ({r['reason']})")
        else:
            print(f"  {key}: {r['verdict']}")

    # Save results
    output_path = RESULTS_DIR / 'pp_cooccurrence_tests.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
