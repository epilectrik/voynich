#!/usr/bin/env python3
"""
T2: Discrimination Fit
B_EXCLUSIVE_GEOMETRIC_INTEGRATION phase

Test whether B-exclusive MIDDLE pairs respect A's incompatibility topology (C475).
Build B-internal co-occurrence for B-exclusive pairs. Compare sparsity to A's matrix.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'


def reconstruct_middle_list():
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    return sorted(all_middles_set), {m: i for i, m in enumerate(sorted(all_middles_set))}


def main():
    print("=" * 60)
    print("T2: Discrimination Fit")
    print("=" * 60)

    # Setup
    print("\n[1] Loading A compatibility matrix...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    a_middles, a_mid_to_idx = reconstruct_middle_list()
    a_set = set(a_middles)
    n_a = len(a_middles)

    # A matrix properties
    a_density = np.sum(compat_matrix) / (n_a * (n_a - 1))
    print(f"  A matrix: {n_a}×{n_a}, density={a_density:.4f}")

    # Build B line-level MIDDLE co-occurrence
    print("\n[2] Building B-line MIDDLE co-occurrence...")
    tx = Transcript()
    morph = Morphology()

    line_middles = defaultdict(set)
    b_mid_counts = Counter()

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            key = (token.folio, token.line)
            line_middles[key].add(m.middle)
            b_mid_counts[m.middle] += 1

    # Separate B MIDDLEs into shared vs exclusive
    all_b_middles = set(b_mid_counts.keys())
    shared = all_b_middles & a_set
    exclusive = all_b_middles - a_set
    print(f"  B unique MIDDLEs: {len(all_b_middles)}")
    print(f"  Shared: {len(shared)}, Exclusive: {len(exclusive)}")

    # Build co-occurrence pairs
    exc_exc_pairs = set()  # exclusive-exclusive
    exc_sha_pairs = set()  # exclusive-shared
    sha_sha_pairs = set()  # shared-shared

    exc_exc_cooccur = Counter()
    exc_sha_cooccur = Counter()

    for key, middles in line_middles.items():
        mid_list = sorted(middles)
        for i in range(len(mid_list)):
            for j in range(i + 1, len(mid_list)):
                m1, m2 = mid_list[i], mid_list[j]
                m1_exc = m1 in exclusive
                m2_exc = m2 in exclusive

                if m1_exc and m2_exc:
                    pair = (m1, m2)
                    exc_exc_pairs.add(pair)
                    exc_exc_cooccur[pair] += 1
                elif m1_exc or m2_exc:
                    pair = (m1, m2)
                    exc_sha_pairs.add(pair)
                    exc_sha_cooccur[pair] += 1
                else:
                    sha_sha_pairs.add((m1, m2))

    print(f"\n  Co-occurrence pair counts:")
    print(f"  Exclusive-Exclusive: {len(exc_exc_pairs)}")
    print(f"  Exclusive-Shared: {len(exc_sha_pairs)}")
    print(f"  Shared-Shared: {len(sha_sha_pairs)}")

    # Step 3: Sparsity analysis for exclusive-exclusive
    print("\n[3] Exclusive-exclusive co-occurrence sparsity...")
    n_exc = len(exclusive)
    max_exc_pairs = n_exc * (n_exc - 1) // 2
    exc_density = len(exc_exc_pairs) / max_exc_pairs if max_exc_pairs > 0 else 0
    print(f"  N exclusive: {n_exc}")
    print(f"  Possible pairs: {max_exc_pairs}")
    print(f"  Observed pairs: {len(exc_exc_pairs)}")
    print(f"  Density: {exc_density:.4f}")
    print(f"  A density: {a_density:.4f}")
    print(f"  Ratio (exc/A): {exc_density / a_density:.2f}" if a_density > 0 else "")

    # Step 4: For shared-shared pairs, check against A compatibility
    print("\n[4] Shared-shared compatibility check against A matrix...")
    n_sha_compat = 0
    n_sha_incompat = 0
    for m1, m2 in sha_sha_pairs:
        if m1 in a_mid_to_idx and m2 in a_mid_to_idx:
            i, j = a_mid_to_idx[m1], a_mid_to_idx[m2]
            if compat_matrix[i, j] > 0:
                n_sha_compat += 1
            else:
                n_sha_incompat += 1

    sha_compat_rate = n_sha_compat / (n_sha_compat + n_sha_incompat) if (n_sha_compat + n_sha_incompat) > 0 else 0
    print(f"  Shared-shared pairs checked: {n_sha_compat + n_sha_incompat}")
    print(f"  A-compatible: {n_sha_compat} ({sha_compat_rate:.1%})")
    print(f"  A-incompatible: {n_sha_incompat}")

    # Step 5: Exclusive-shared: do exclusives co-occur with compatible A neighborhoods?
    print("\n[5] Exclusive-shared neighborhood analysis...")
    # For each exclusive MIDDLE, what shared MIDDLEs does it co-occur with?
    exc_neighborhoods = defaultdict(set)
    for pair in exc_sha_pairs:
        m1, m2 = pair
        if m1 in exclusive:
            exc_neighborhoods[m1].add(m2)
        if m2 in exclusive:
            exc_neighborhoods[m2].add(m1)

    # For each exclusive, compute A-compatibility rate of its shared neighbors
    exc_neighbor_compat = {}
    for exc_mid, neighbors in exc_neighborhoods.items():
        # Get A-indices of neighbors
        neighbor_indices = [a_mid_to_idx[n] for n in neighbors if n in a_mid_to_idx]
        if len(neighbor_indices) < 2:
            continue

        # Compute pairwise A-compatibility within the neighborhood
        n_compat = 0
        n_total = 0
        for i in range(len(neighbor_indices)):
            for j in range(i + 1, len(neighbor_indices)):
                n_total += 1
                if compat_matrix[neighbor_indices[i], neighbor_indices[j]] > 0:
                    n_compat += 1

        if n_total > 0:
            exc_neighbor_compat[exc_mid] = n_compat / n_total

    if exc_neighbor_compat:
        compat_rates = list(exc_neighbor_compat.values())
        print(f"  Exclusives with >=2 shared neighbors: {len(exc_neighbor_compat)}")
        print(f"  Mean A-compatibility of neighbor sets: {np.mean(compat_rates):.3f}")
        print(f"  Median: {np.median(compat_rates):.3f}")
        print(f"  A baseline density: {a_density:.4f}")
        print(f"  Enrichment: {np.mean(compat_rates) / a_density:.1f}×")

    # Step 6: Clustering coefficient comparison
    print("\n[6] Co-occurrence clustering coefficient...")
    # For exclusive-exclusive: build adjacency and compute clustering
    exc_list = sorted(exclusive)
    exc_to_idx = {m: i for i, m in enumerate(exc_list)}

    # Build adjacency
    exc_adj = defaultdict(set)
    for m1, m2 in exc_exc_pairs:
        exc_adj[m1].add(m2)
        exc_adj[m2].add(m1)

    # Clustering coefficient
    clustering_coeffs = []
    for mid in exc_list:
        neighbors = exc_adj.get(mid, set())
        k = len(neighbors)
        if k < 2:
            continue
        # Count edges among neighbors
        n_list = sorted(neighbors)
        edges = 0
        for i in range(len(n_list)):
            for j in range(i + 1, len(n_list)):
                if (n_list[i], n_list[j]) in exc_exc_pairs or \
                   (n_list[j], n_list[i]) in exc_exc_pairs:
                    edges += 1
        cc = 2 * edges / (k * (k - 1))
        clustering_coeffs.append(cc)

    if clustering_coeffs:
        print(f"  Nodes with degree>=2: {len(clustering_coeffs)}")
        print(f"  Mean clustering coefficient: {np.mean(clustering_coeffs):.3f}")
        print(f"  A matrix clustering (C983): 0.873")
        print(f"  Ratio: {np.mean(clustering_coeffs) / 0.873:.2f}")

    # Verdict
    print("\n" + "=" * 60)

    neighbor_enrichment = np.mean(compat_rates) / a_density if exc_neighbor_compat and a_density > 0 else 0
    density_similar = 0.1 < (exc_density / a_density) < 10 if a_density > 0 else False
    neighbors_compatible = neighbor_enrichment > 5

    if neighbors_compatible and density_similar:
        verdict = "SAME_TOPOLOGY"
        explanation = (
            f"B-exclusive pairs follow A's incompatibility topology: "
            f"neighbor enrichment {neighbor_enrichment:.1f}×, "
            f"density ratio {exc_density/a_density:.2f}. "
            f"Same constraint logic, extended vocabulary."
        )
    elif neighbors_compatible:
        verdict = "COMPATIBLE_TOPOLOGY"
        explanation = (
            f"Exclusive neighbors are A-compatible ({neighbor_enrichment:.1f}× enrichment) "
            f"but density differs ({exc_density/a_density:.2f}×). "
            f"Compatible extension with different sparsity."
        )
    else:
        verdict = "DIVERGENT_TOPOLOGY"
        explanation = (
            f"B-exclusive neighborhoods show different compatibility structure "
            f"(enrichment {neighbor_enrichment:.1f}×). "
            f"Potentially independent constraint system."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T2_discrimination_fit',
        'n_exclusive': len(exclusive),
        'n_shared': len(shared),
        'pair_counts': {
            'exc_exc': len(exc_exc_pairs),
            'exc_sha': len(exc_sha_pairs),
            'sha_sha': len(sha_sha_pairs),
        },
        'density': {
            'exclusive': float(exc_density),
            'a_matrix': float(a_density),
            'ratio': float(exc_density / a_density) if a_density > 0 else None,
        },
        'shared_compat_rate': float(sha_compat_rate),
        'neighbor_analysis': {
            'n_exclusives_analyzed': len(exc_neighbor_compat),
            'mean_compat_rate': float(np.mean(compat_rates)) if exc_neighbor_compat else None,
            'enrichment': float(neighbor_enrichment),
        },
        'clustering': {
            'mean_cc': float(np.mean(clustering_coeffs)) if clustering_coeffs else None,
            'a_baseline': 0.873,
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't2_discrimination_fit.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't2_discrimination_fit.json'}")


if __name__ == '__main__':
    main()
