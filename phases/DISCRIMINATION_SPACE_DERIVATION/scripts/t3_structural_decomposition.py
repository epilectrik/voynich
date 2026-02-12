#!/usr/bin/env python3
"""
T3: Structural Decomposition
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Does the ~128D space have internal structure? Or is it isotropic noise?
The flat eigenvalue spectrum from the prior analysis suggests one of:
  (a) Genuinely unstructured — each dimension is independent
  (b) Block structure — decomposes into PREFIX-level subspaces
  (c) Hierarchical — nested clustering at multiple scales

Key questions:
- Does PREFIX partition the compatibility graph into communities?
- Can we factor D ≈ D_PREFIX × D_within?
- What is the community structure of the compatibility graph?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import SpectralClustering
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_matrix_and_middles():
    """Load compatibility matrix and rebuild MIDDLE list."""
    M = np.load(RESULTS_DIR / 't1_compat_matrix.npy')

    # Rebuild MIDDLE list (same order as T1)
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    middle_to_prefixes = defaultdict(set)

    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
            if m.prefix:
                middle_to_prefixes[m.middle].add(m.prefix)

    all_middles = sorted(all_middles_set)
    return M, all_middles, middle_to_prefixes


def prefix_block_structure(M, all_middles, middle_to_prefixes):
    """Test whether PREFIX creates block structure in the compatibility matrix.

    If compatibility were determined purely by PREFIX, we'd see:
    - High within-PREFIX compatibility
    - Low cross-PREFIX compatibility
    - Clear block diagonal structure
    """
    n = len(all_middles)

    # Assign primary PREFIX to each MIDDLE
    mid_prefix = {}
    for i, mid in enumerate(all_middles):
        prefixes = middle_to_prefixes.get(mid, set())
        if len(prefixes) == 1:
            mid_prefix[i] = list(prefixes)[0]
        elif len(prefixes) > 1:
            mid_prefix[i] = 'MULTI'
        else:
            mid_prefix[i] = 'NONE'

    prefix_labels = [mid_prefix.get(i, 'NONE') for i in range(n)]
    unique_prefixes = sorted(set(prefix_labels))

    print(f"  PREFIX distribution:")
    for p in unique_prefixes:
        count = prefix_labels.count(p)
        print(f"    {p}: {count}")

    # Within-PREFIX vs cross-PREFIX compatibility rates
    within_total, within_compat = 0, 0
    cross_total, cross_compat = 0, 0

    M_int = M.astype(np.int32)
    for i in range(n):
        for j in range(i + 1, n):
            if prefix_labels[i] == prefix_labels[j]:
                within_total += 1
                within_compat += int(M_int[i, j])
            else:
                cross_total += 1
                cross_compat += int(M_int[i, j])

    within_rate = within_compat / within_total if within_total > 0 else 0
    cross_rate = cross_compat / cross_total if cross_total > 0 else 0
    enrichment = within_rate / cross_rate if cross_rate > 0 else float('inf')

    print(f"\n  Within-PREFIX compatibility: {within_rate:.4f} ({within_compat}/{within_total})")
    print(f"  Cross-PREFIX compatibility: {cross_rate:.4f} ({cross_compat}/{cross_total})")
    print(f"  Enrichment ratio: {enrichment:.2f}x")

    # Per-PREFIX block analysis
    prefix_blocks = {}
    for p in unique_prefixes:
        if p in ('NONE', 'MULTI'):
            continue
        indices = [i for i, label in enumerate(prefix_labels) if label == p]
        if len(indices) < 3:
            continue
        submat = M[np.ix_(indices, indices)]
        block_density = (submat.sum() - len(indices)) / (len(indices) * (len(indices) - 1)) if len(indices) > 1 else 0
        prefix_blocks[p] = {
            'count': len(indices),
            'block_density': float(block_density),
        }
        print(f"    {p}: {len(indices)} MIDDLEs, block density={block_density:.4f}")

    return {
        'within_rate': float(within_rate),
        'cross_rate': float(cross_rate),
        'enrichment': float(enrichment),
        'prefix_blocks': prefix_blocks,
        'prefix_distribution': {p: prefix_labels.count(p) for p in unique_prefixes},
    }


def spectral_community_detection(M, n_clusters_range=[4, 6, 8, 10, 12, 16]):
    """Find natural communities in the compatibility graph using spectral clustering."""
    print(f"\n  Spectral clustering...")
    n = M.shape[0]
    results = {}

    for k in n_clusters_range:
        print(f"    k={k}...", end=" ")
        try:
            sc = SpectralClustering(
                n_clusters=k, affinity='precomputed',
                random_state=42, n_init=10
            )
            labels = sc.fit_predict(M.astype(np.float64))

            # Compute modularity
            degrees = M.sum(axis=1) - 1  # exclude diagonal
            m_edges = degrees.sum() / 2
            modularity = 0.0
            for c in range(k):
                members = np.where(labels == c)[0]
                if len(members) < 2:
                    continue
                submat = M[np.ix_(members, members)]
                internal_edges = (submat.sum() - len(members)) / 2
                expected = sum(degrees[members]) ** 2 / (4 * m_edges)
                modularity += internal_edges / m_edges - expected / m_edges

            # Cluster sizes
            sizes = [int(np.sum(labels == c)) for c in range(k)]
            sizes.sort(reverse=True)

            results[k] = {
                'modularity': float(modularity),
                'sizes': sizes,
                'max_cluster': int(max(sizes)),
                'min_cluster': int(min(sizes)),
            }
            print(f"modularity={modularity:.4f}, sizes={sizes[:5]}...")
        except Exception as e:
            print(f"ERROR: {e}")
            results[k] = {'modularity': 0, 'sizes': [], 'max_cluster': 0, 'min_cluster': 0}

    # Best modularity
    best_k = max(results.keys(), key=lambda k: results[k]['modularity'])
    print(f"  Best modularity: k={best_k} (Q={results[best_k]['modularity']:.4f})")

    return results, best_k


def prefix_vs_spectral_alignment(M, all_middles, middle_to_prefixes, best_k):
    """Compare PREFIX assignment to spectral community assignment."""
    n = len(all_middles)

    # PREFIX labels
    prefix_labels = []
    for mid in all_middles:
        prefixes = middle_to_prefixes.get(mid, set())
        if len(prefixes) == 1:
            prefix_labels.append(list(prefixes)[0])
        elif len(prefixes) > 1:
            prefix_labels.append('MULTI')
        else:
            prefix_labels.append('NONE')

    # Spectral clustering
    sc = SpectralClustering(
        n_clusters=best_k, affinity='precomputed',
        random_state=42, n_init=10
    )
    spectral_labels = sc.fit_predict(M.astype(np.float64))

    # Map PREFIX labels to integers for ARI computation
    unique_prefix = sorted(set(prefix_labels))
    prefix_int = [unique_prefix.index(p) for p in prefix_labels]

    ari = adjusted_rand_score(prefix_int, spectral_labels)
    nmi = normalized_mutual_info_score(prefix_int, spectral_labels)

    print(f"\n  PREFIX vs Spectral community alignment:")
    print(f"    ARI: {ari:.4f}")
    print(f"    NMI: {nmi:.4f}")

    if ari > 0.5:
        alignment = "STRONG"
    elif ari > 0.2:
        alignment = "MODERATE"
    elif ari > 0.05:
        alignment = "WEAK"
    else:
        alignment = "NONE"

    print(f"    Alignment: {alignment}")

    # Cross-tabulation: which PREFIXes land in which clusters?
    crosstab = defaultdict(lambda: defaultdict(int))
    for i in range(n):
        crosstab[prefix_labels[i]][int(spectral_labels[i])] += 1

    # Find dominant PREFIX per cluster
    cluster_dominant = {}
    for c in range(best_k):
        members = np.where(spectral_labels == c)[0]
        prefix_counts = defaultdict(int)
        for m in members:
            prefix_counts[prefix_labels[m]] += 1
        dominant = max(prefix_counts.items(), key=lambda x: x[1])
        cluster_dominant[c] = {
            'dominant_prefix': dominant[0],
            'count': dominant[1],
            'total': len(members),
            'purity': dominant[1] / len(members),
        }

    return {
        'ari': float(ari),
        'nmi': float(nmi),
        'alignment': alignment,
        'cluster_dominant': {str(k): v for k, v in cluster_dominant.items()},
    }


def degree_stratification(M, all_middles):
    """Analyze how degree (number of compatible partners) structures the space.

    Hub MIDDLEs (high degree) vs specialist MIDDLEs (low degree) may
    form distinct structural classes.
    """
    degrees = M.sum(axis=1) - 1
    n = len(all_middles)

    # Quartile analysis
    quartiles = np.percentile(degrees, [25, 50, 75])
    print(f"\n  Degree quartiles: {quartiles.round(1)}")

    # Compatibility rate within degree bands
    bands = [
        ('low', degrees <= quartiles[0]),
        ('mid_low', (degrees > quartiles[0]) & (degrees <= quartiles[1])),
        ('mid_high', (degrees > quartiles[1]) & (degrees <= quartiles[2])),
        ('high', degrees > quartiles[2]),
    ]

    band_compat = {}
    for name_i, mask_i in bands:
        for name_j, mask_j in bands:
            if name_i > name_j:
                continue
            idx_i = np.where(mask_i)[0]
            idx_j = np.where(mask_j)[0]
            if len(idx_i) == 0 or len(idx_j) == 0:
                continue
            submat = M[np.ix_(idx_i, idx_j)]
            if name_i == name_j:
                total = len(idx_i) * (len(idx_i) - 1) // 2
                compat = (submat.sum() - len(idx_i)) // 2
            else:
                total = len(idx_i) * len(idx_j)
                compat = submat.sum()
            rate = compat / total if total > 0 else 0
            key = f"{name_i}_x_{name_j}"
            band_compat[key] = {
                'rate': float(rate),
                'count_i': int(len(idx_i)),
                'count_j': int(len(idx_j)),
            }
            print(f"    {key}: {rate:.4f}")

    return {
        'quartiles': quartiles.tolist(),
        'band_compatibility': band_compat,
    }


def factored_dimensionality_test(M, all_middles, middle_to_prefixes):
    """Test if dimensionality decomposes as PREFIX-level + within-PREFIX.

    If the space factors, then:
    D_total ≈ D_between_PREFIX + D_within_PREFIX
    and D_between should be ≈ 3 bits (8 PREFIX families).
    """
    n = len(all_middles)

    # Build PREFIX assignment
    prefix_labels = []
    for mid in all_middles:
        prefixes = middle_to_prefixes.get(mid, set())
        if len(prefixes) == 1:
            prefix_labels.append(list(prefixes)[0])
        else:
            prefix_labels.append('NONE')

    # Between-PREFIX: average compatibility matrix per PREFIX pair
    unique_prefixes = sorted(set(prefix_labels))
    prefix_indices = {p: [i for i, l in enumerate(prefix_labels) if l == p]
                      for p in unique_prefixes}

    # Between-PREFIX matrix
    n_prefix = len(unique_prefixes)
    between_matrix = np.zeros((n_prefix, n_prefix))

    for pi, p1 in enumerate(unique_prefixes):
        for pj, p2 in enumerate(unique_prefixes):
            idx1, idx2 = prefix_indices[p1], prefix_indices[p2]
            if not idx1 or not idx2:
                continue
            submat = M[np.ix_(idx1, idx2)]
            between_matrix[pi, pj] = submat.mean()

    # Between-PREFIX effective rank
    between_eigs = np.linalg.eigvalsh(between_matrix)[::-1]
    pos_between = between_eigs[between_eigs > 0.001]
    between_rank = len(pos_between)
    print(f"\n  Between-PREFIX matrix rank: {between_rank} (of {n_prefix})")
    print(f"  Between-PREFIX top eigenvalues: {between_eigs[:5].round(3)}")

    # Within-PREFIX effective dimensionality (average)
    within_ranks = []
    for p in unique_prefixes:
        idx = prefix_indices[p]
        if len(idx) < 10:
            continue
        submat = M[np.ix_(idx, idx)].astype(np.float64)
        eigs = np.linalg.eigvalsh(submat)[::-1]
        pos_eigs = eigs[eigs > 0.5]
        within_ranks.append(len(pos_eigs))
        print(f"    {p}: {len(idx)} MIDDLEs, effective within-rank={len(pos_eigs)}")

    mean_within_rank = np.mean(within_ranks) if within_ranks else 0
    total_estimated = between_rank + mean_within_rank

    print(f"\n  Between-PREFIX rank: {between_rank}")
    print(f"  Mean within-PREFIX rank: {mean_within_rank:.1f}")
    print(f"  Factored estimate: {total_estimated:.1f}")

    factored = between_rank + mean_within_rank < 100  # arbitrary but reasonable
    print(f"  Factored decomposition {'PLAUSIBLE' if factored else 'INSUFFICIENT'}")

    return {
        'between_rank': int(between_rank),
        'between_eigenvalues': [float(x) for x in between_eigs[:10]],
        'mean_within_rank': float(mean_within_rank),
        'within_ranks': {p: int(r) for p, r in zip(
            [p for p in unique_prefixes if len(prefix_indices[p]) >= 10],
            within_ranks
        )},
        'factored_estimate': float(total_estimated),
        'factored_plausible': bool(factored),
    }


def run():
    print("=" * 70)
    print("T3: Structural Decomposition")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    M, all_middles, middle_to_prefixes = load_matrix_and_middles()
    n = len(all_middles)
    print(f"  Matrix: {n}x{n}")

    # PREFIX block structure
    print("\n[1/5] PREFIX block structure...")
    prefix_results = prefix_block_structure(M, all_middles, middle_to_prefixes)

    # Spectral community detection
    print("\n[2/5] Spectral community detection...")
    community_results, best_k = spectral_community_detection(M)

    # PREFIX vs spectral alignment
    print("\n[3/5] PREFIX vs spectral alignment...")
    alignment_results = prefix_vs_spectral_alignment(
        M, all_middles, middle_to_prefixes, best_k)

    # Degree stratification
    print("\n[4/5] Degree stratification...")
    degree_results = degree_stratification(M, all_middles)

    # Factored dimensionality
    print("\n[5/5] Factored dimensionality test...")
    factored_results = factored_dimensionality_test(M, all_middles, middle_to_prefixes)

    # Summary
    print(f"\n{'='*70}")
    print("STRUCTURAL DECOMPOSITION SUMMARY")
    print(f"{'='*70}")
    print(f"  PREFIX enrichment: {prefix_results['enrichment']:.2f}x")
    print(f"  Best spectral communities: k={best_k}")
    print(f"  PREFIX-spectral alignment: {alignment_results['alignment']} (ARI={alignment_results['ari']:.3f})")
    print(f"  Factored estimate: {factored_results['factored_estimate']:.1f}")
    print(f"  Factored plausible: {factored_results['factored_plausible']}")

    if prefix_results['enrichment'] > 3.0:
        structure = "PREFIX_DOMINATED"
    elif prefix_results['enrichment'] > 1.5:
        structure = "PREFIX_INFLUENCED"
    else:
        structure = "PREFIX_INDEPENDENT"

    print(f"  Structure verdict: {structure}")

    results = {
        'test': 'T3_structural_decomposition',
        'n_middles': n,
        'prefix_block': prefix_results,
        'spectral_communities': {str(k): v for k, v in community_results.items()},
        'best_spectral_k': best_k,
        'prefix_spectral_alignment': alignment_results,
        'degree_stratification': degree_results,
        'factored_dimensionality': factored_results,
        'structure_verdict': structure,
    }

    with open(RESULTS_DIR / 't3_structural_decomposition.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't3_structural_decomposition.json'}")


if __name__ == '__main__':
    run()
