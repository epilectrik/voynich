#!/usr/bin/env python3
"""
T4: Inter-Region Incompatibility Topology
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

Build the exclusion graph between geometric regions. Which clusters are
mutually incompatible (never co-occur)? What does the topology look like?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import mannwhitneyu
from sklearn.mixture import GaussianMixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99
N_PERM = 500  # Permutation tests

QO_INITIALS = set('ktp')
CHSH_INITIALS = set('eo')


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
    return sorted(all_middles_set)


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * scaling[np.newaxis, :], eigenvalues


def main():
    print("=" * 60)
    print("T4: Inter-Region Incompatibility Topology")
    print("=" * 60)

    # Load
    print("\n[1] Loading data...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    embedding, eigenvalues = build_residual_embedding(compat_matrix)
    n = len(all_middles)

    # Baseline compatibility
    total_pairs = n * (n - 1) // 2
    compat_count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if compat_matrix[i, j] > 0:
                compat_count += 1
    baseline_rate = compat_count / total_pairs
    print(f"  Baseline compatibility: {compat_count}/{total_pairs} = {baseline_rate:.4f}")

    # Cluster using GMM k=5 (from T2)
    print("\n[2] Clustering (GMM k=5 from T2)...")
    gmm = GaussianMixture(n_components=5, random_state=42, n_init=3,
                           covariance_type='diag', max_iter=300)
    labels = gmm.fit_predict(embedding)
    cluster_sizes = Counter(labels)
    for c in sorted(cluster_sizes):
        print(f"  Cluster {c}: {cluster_sizes[c]} MIDDLEs")

    # Build cluster-level compatibility matrix
    print("\n[3] Building cluster-level compatibility matrix...")
    cluster_ids = sorted(set(labels))
    k = len(cluster_ids)

    # Pre-compute cluster membership
    cluster_members = {c: np.where(labels == c)[0] for c in cluster_ids}

    # Compute cross-cluster compatibility rates
    compat_rates = np.zeros((k, k))
    compat_counts_matrix = np.zeros((k, k), dtype=int)
    pair_counts = np.zeros((k, k), dtype=int)

    for ci_idx, ci in enumerate(cluster_ids):
        for cj_idx, cj in enumerate(cluster_ids):
            if cj < ci:
                continue
            members_i = cluster_members[ci]
            members_j = cluster_members[cj]

            n_compat = 0
            n_pairs = 0
            if ci == cj:
                # Within-cluster
                for ii, mi in enumerate(members_i):
                    for jj in range(ii + 1, len(members_i)):
                        mj = members_i[jj]
                        n_pairs += 1
                        if compat_matrix[mi, mj] > 0:
                            n_compat += 1
            else:
                # Between-cluster
                for mi in members_i:
                    for mj in members_j:
                        n_pairs += 1
                        if compat_matrix[mi, mj] > 0:
                            n_compat += 1

            rate = n_compat / n_pairs if n_pairs > 0 else 0
            compat_rates[ci_idx, cj_idx] = rate
            compat_rates[cj_idx, ci_idx] = rate
            compat_counts_matrix[ci_idx, cj_idx] = n_compat
            compat_counts_matrix[cj_idx, ci_idx] = n_compat
            pair_counts[ci_idx, cj_idx] = n_pairs
            pair_counts[cj_idx, ci_idx] = n_pairs

    # Print compatibility matrix
    print(f"\n  Compatibility rates (baseline={baseline_rate:.4f}):")
    header = "     " + "  ".join(f"  C{c}" for c in cluster_ids)
    print(header)
    for ci_idx, ci in enumerate(cluster_ids):
        row = f"  C{ci}"
        for cj_idx in range(k):
            rate = compat_rates[ci_idx, cj_idx]
            row += f" {rate:5.3f}"
        print(row)

    # Enrichment/depletion
    print(f"\n  Enrichment vs baseline:")
    enrichment = np.zeros((k, k))
    for ci_idx in range(k):
        for cj_idx in range(k):
            if baseline_rate > 0:
                enrichment[ci_idx, cj_idx] = compat_rates[ci_idx, cj_idx] / baseline_rate
            else:
                enrichment[ci_idx, cj_idx] = 0

    header = "     " + "  ".join(f"  C{c}" for c in cluster_ids)
    print(header)
    for ci_idx, ci in enumerate(cluster_ids):
        row = f"  C{ci}"
        for cj_idx in range(k):
            e = enrichment[ci_idx, cj_idx]
            row += f" {e:5.2f}"
        print(row)

    # Permutation test for significance
    print(f"\n[4] Permutation test ({N_PERM} permutations)...")
    rng = np.random.RandomState(42)

    null_rates = {(ci, cj): [] for ci in range(k) for cj in range(ci, k)}
    for perm in range(N_PERM):
        perm_labels = rng.permutation(labels)
        perm_members = {c: np.where(perm_labels == c)[0] for c in cluster_ids}

        for ci_idx, ci in enumerate(cluster_ids):
            for cj_idx, cj in enumerate(cluster_ids):
                if cj < ci:
                    continue
                mi = perm_members[ci]
                mj = perm_members[cj]

                # Sample to keep it fast
                if ci == cj:
                    if len(mi) < 2:
                        continue
                    sample_size = min(500, len(mi) * (len(mi) - 1) // 2)
                    pairs = set()
                    while len(pairs) < sample_size:
                        a, b = rng.choice(len(mi), 2, replace=False)
                        pairs.add((min(mi[a], mi[b]), max(mi[a], mi[b])))
                    n_compat = sum(1 for a, b in pairs if compat_matrix[a, b] > 0)
                    null_rates[(ci_idx, cj_idx)].append(n_compat / len(pairs))
                else:
                    sample_size = min(500, len(mi) * len(mj))
                    pairs = set()
                    while len(pairs) < sample_size:
                        a = mi[rng.randint(len(mi))]
                        b = mj[rng.randint(len(mj))]
                        pairs.add((a, b))
                    n_compat = sum(1 for a, b in pairs if compat_matrix[a, b] > 0)
                    null_rates[(ci_idx, cj_idx)].append(n_compat / len(pairs))

    # Compute z-scores and p-values
    print(f"\n  Z-scores (positive = enriched, negative = depleted):")
    z_matrix = np.zeros((k, k))
    sig_matrix = np.zeros((k, k))
    for ci_idx in range(k):
        for cj_idx in range(ci_idx, k):
            null = null_rates.get((ci_idx, cj_idx), [])
            if not null:
                continue
            null_mean = np.mean(null)
            null_std = np.std(null)
            if null_std > 0:
                z = (compat_rates[ci_idx, cj_idx] - null_mean) / null_std
            else:
                z = 0
            z_matrix[ci_idx, cj_idx] = z
            z_matrix[cj_idx, ci_idx] = z
            sig_matrix[ci_idx, cj_idx] = 1 if abs(z) > 2.0 else 0
            sig_matrix[cj_idx, ci_idx] = sig_matrix[ci_idx, cj_idx]

    header = "     " + "  ".join(f"  C{c}" for c in cluster_ids)
    print(header)
    for ci_idx, ci in enumerate(cluster_ids):
        row = f"  C{ci}"
        for cj_idx in range(k):
            z = z_matrix[ci_idx, cj_idx]
            marker = '*' if abs(z) > 2.0 else ' '
            row += f" {z:+4.1f}{marker}"
        print(row)

    # Build exclusion and affinity graphs
    print(f"\n[5] Building exclusion/affinity graphs...")
    exclusion_edges = []
    affinity_edges = []
    for ci_idx in range(k):
        for cj_idx in range(ci_idx + 1, k):
            z = z_matrix[ci_idx, cj_idx]
            if z < -2.0:
                exclusion_edges.append((ci_idx, cj_idx, float(z)))
            elif z > 2.0:
                affinity_edges.append((ci_idx, cj_idx, float(z)))

    print(f"  Exclusion edges (z < -2.0): {len(exclusion_edges)}")
    for ci, cj, z in exclusion_edges:
        print(f"    C{ci}-C{cj}: z={z:.1f}")
    print(f"  Affinity edges (z > +2.0): {len(affinity_edges)}")
    for ci, cj, z in affinity_edges:
        print(f"    C{ci}-C{cj}: z={z:.1f}")

    # Build cluster property summaries for interpretation
    print(f"\n[6] Cluster property summaries for exclusion interpretation...")
    tx = Transcript()
    morph = Morphology()
    a_counts = Counter()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            a_counts[m.middle] += 1

    for c in cluster_ids:
        members = cluster_members[c]
        mids = [all_middles[i] for i in members]
        n_qo = sum(1 for m in mids if m[0] in QO_INITIALS)
        n_chsh = sum(1 for m in mids if m[0] in CHSH_INITIALS)
        n_k = sum(1 for m in mids if 'k' in m)
        n_e = sum(1 for m in mids if 'e' in m)
        n_h = sum(1 for m in mids if 'h' in m)
        mean_freq = np.mean([a_counts.get(m, 0) for m in mids])
        mean_len = np.mean([len(m) for m in mids])
        mean_norm = np.mean([np.linalg.norm(embedding[i]) for i in members])

        print(f"  C{c} (n={len(mids)}): "
              f"QO={n_qo/len(mids):.0%} CHSH={n_chsh/len(mids):.0%} | "
              f"k={n_k/len(mids):.0%} e={n_e/len(mids):.0%} h={n_h/len(mids):.0%} | "
              f"freq={mean_freq:.0f} len={mean_len:.1f} depth={mean_norm:.2f}")

    # Topology characterization
    print(f"\n[7] Topology characterization...")
    n_total_pairs = k * (k - 1) // 2
    n_exclusion = len(exclusion_edges)
    n_affinity = len(affinity_edges)
    n_neutral = n_total_pairs - n_exclusion - n_affinity

    print(f"  Total cluster pairs: {n_total_pairs}")
    print(f"  Exclusion pairs: {n_exclusion}")
    print(f"  Affinity pairs: {n_affinity}")
    print(f"  Neutral pairs: {n_neutral}")

    # Check for bipartiteness
    # Simple check: can we 2-color the exclusion graph?
    if n_exclusion > 0:
        from collections import deque
        adj = defaultdict(set)
        for ci, cj, z in exclusion_edges:
            adj[ci].add(cj)
            adj[cj].add(ci)

        color = {}
        is_bipartite = True
        for start in range(k):
            if start in color:
                continue
            if start not in adj:
                continue
            queue = deque([start])
            color[start] = 0
            while queue:
                node = queue.popleft()
                for neighbor in adj[node]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[node]
                        queue.append(neighbor)
                    elif color[neighbor] == color[node]:
                        is_bipartite = False
                        break
                if not is_bipartite:
                    break

        print(f"  Exclusion graph bipartite: {is_bipartite}")
        if is_bipartite and color:
            side_0 = [c for c, col in color.items() if col == 0]
            side_1 = [c for c, col in color.items() if col == 1]
            print(f"    Side A: {side_0}")
            print(f"    Side B: {side_1}")
    else:
        is_bipartite = True
        print(f"  No exclusion edges — trivially bipartite")

    # Verdict
    print("\n" + "=" * 60)

    if n_exclusion >= 2 and not all(
        abs(z_matrix[ci, cj]) < 2 for ci in range(k) for cj in range(ci + 1, k)
    ):
        # Check if exclusion correlates with properties beyond frequency
        freq_only = True
        for ci, cj, z in exclusion_edges:
            mids_i = [all_middles[idx] for idx in cluster_members[ci]]
            mids_j = [all_middles[idx] for idx in cluster_members[cj]]
            freq_i = np.mean([a_counts.get(m, 0) for m in mids_i])
            freq_j = np.mean([a_counts.get(m, 0) for m in mids_j])
            # Check if one is high-freq and other is low — that would be trivial
            if not (freq_i > 50 and freq_j < 5) and not (freq_j > 50 and freq_i < 5):
                freq_only = False

        if freq_only:
            verdict = "DEGREE_ARTIFACT"
            explanation = (
                f"{n_exclusion} exclusion pairs, but all involve high vs low frequency "
                f"clusters. Exclusion is a degree effect, not structural."
            )
        else:
            chromatic_est = 2 if is_bipartite else min(3, n_exclusion + 1)
            verdict = "INTERPRETABLE_TOPOLOGY"
            explanation = (
                f"{n_exclusion} exclusion pairs, {n_affinity} affinity pairs. "
                f"Bipartite={is_bipartite}. Estimated chromatic number={chromatic_est}. "
                f"Exclusion structure is non-trivial."
            )
    elif n_exclusion == 0:
        verdict = "FULLY_CONNECTED"
        explanation = "No significant exclusion pairs. All clusters are compatible."
    else:
        verdict = "WEAK_STRUCTURE"
        explanation = f"Only {n_exclusion} exclusion pair(s). Minimal topology."

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T4_incompatibility_topology',
        'n_middles': len(all_middles),
        'baseline_compatibility': float(baseline_rate),
        'n_clusters': k,
        'cluster_sizes': {str(c): int(cluster_sizes[c]) for c in cluster_ids},
        'compat_rates': {f"{ci}-{cj}": float(compat_rates[ci, cj])
                         for ci in range(k) for cj in range(ci, k)},
        'enrichment': {f"{ci}-{cj}": float(enrichment[ci, cj])
                       for ci in range(k) for cj in range(ci, k)},
        'z_scores': {f"{ci}-{cj}": float(z_matrix[ci, cj])
                     for ci in range(k) for cj in range(ci, k)},
        'exclusion_edges': [{'pair': f"{ci}-{cj}", 'z': z}
                            for ci, cj, z in exclusion_edges],
        'affinity_edges': [{'pair': f"{ci}-{cj}", 'z': z}
                           for ci, cj, z in affinity_edges],
        'is_bipartite': is_bipartite,
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't4_incompatibility_topology.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't4_incompatibility_topology.json'}")


if __name__ == '__main__':
    main()
