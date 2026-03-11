"""T3: Landscape Correspondence with Manifold for Phase 580.

Do SA/TD/FR landscape classes map onto manifold regions?
Test separately in Space A and Space B. Decide C1669.
"""
import json, os, math
from collections import defaultdict
import numpy as np

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

LANDSCAPE_CLASSES = ['STABLE_AMPLIFIER', 'THRESHOLD_DEPENDENT', 'FORGIVING_RECIRCULATOR']
LANDSCAPE_SHORT = {
    'STABLE_AMPLIFIER': 'SA',
    'THRESHOLD_DEPENDENT': 'TD',
    'FORGIVING_RECIRCULATOR': 'FR'
}


def spearman_rank(x, y):
    """Pure-Python Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0

    def rank_data(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            mean_rank = (i + j) / 2.0 + 1.0
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = mean_rank
            i = j + 1
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((rx[i] - mean_rx) ** 2 for i in range(n))
    den_y = sum((ry[i] - mean_ry) ** 2 for i in range(n))
    den = math.sqrt(den_x * den_y)
    if den < 1e-12:
        return 0.0
    return num / den


def kruskal_wallis(groups):
    """Pure-Python Kruskal-Wallis H test. Returns (H, k, p_value)."""
    all_vals = []
    for g_idx, g in enumerate(groups):
        for v in g:
            all_vals.append((v, g_idx))
    n_total = len(all_vals)
    if n_total < 3:
        return (0.0, len(groups), 1.0)

    sorted_vals = sorted(range(n_total), key=lambda i: all_vals[i][0])
    ranks = [0.0] * n_total
    i = 0
    while i < n_total:
        j = i
        while j < n_total - 1 and all_vals[sorted_vals[j]][0] == all_vals[sorted_vals[j + 1]][0]:
            j += 1
        mean_rank = (i + j) / 2.0 + 1.0
        for ki in range(i, j + 1):
            ranks[sorted_vals[ki]] = mean_rank
        i = j + 1

    group_rank_sums = defaultdict(float)
    group_counts = defaultdict(int)
    for idx in range(n_total):
        g_idx = all_vals[idx][1]
        group_rank_sums[g_idx] += ranks[idx]
        group_counts[g_idx] += 1

    h = 0.0
    for g_idx in group_counts:
        ni = group_counts[g_idx]
        ri = group_rank_sums[g_idx]
        if ni > 0:
            h += (ri ** 2) / ni
    h = (12.0 / (n_total * (n_total + 1))) * h - 3.0 * (n_total + 1)

    # p-value: chi2 SF with df = k-1
    df = len(groups) - 1
    if df == 2:
        p = math.exp(-h / 2) if h > 0 else 1.0
    elif df == 1:
        # Normal approximation
        z = math.sqrt(max(h, 0))
        p = math.erfc(z / math.sqrt(2))
    else:
        if h <= 0:
            p = 1.0
        else:
            z = ((h / df) ** (1 / 3) - 1 + 2 / (9 * df)) / math.sqrt(2 / (9 * df))
            p = 0.5 * math.erfc(z / math.sqrt(2))
    return (round(h, 4), len(groups), round(p, 6))


def analyze_landscape_in_space(folios, meta, space_t1):
    """Analyze landscape class structure in one PC space."""
    n = len(folios)
    pcs = space_t1['pcs_for_80pct']
    scores = space_t1['folio_scores']
    pc_names = [f'PC{k + 1}' for k in range(pcs)]

    X = np.array([[scores[f][pc] for pc in pc_names] for f in folios])

    groups_by_class = {lc: [] for lc in LANDSCAPE_CLASSES}
    for i, f in enumerate(folios):
        lc = meta[f]['landscape_class']
        groups_by_class[lc].append(i)

    class_counts = {LANDSCAPE_SHORT[lc]: len(groups_by_class[lc])
                    for lc in LANDSCAPE_CLASSES}

    # Mean PC scores per class
    centroids = {}
    for lc in LANDSCAPE_CLASSES:
        idx = groups_by_class[lc]
        short = LANDSCAPE_SHORT[lc]
        centroids[short] = X[idx].mean(axis=0).tolist() if idx else [0] * pcs

    # Kruskal-Wallis per PC
    kw_results = {}
    sig_count = 0
    for k in range(pcs):
        grps = [X[groups_by_class[lc], k].tolist()
                for lc in LANDSCAPE_CLASSES if groups_by_class[lc]]
        h, ng, p = kruskal_wallis(grps)
        kw_results[pc_names[k]] = {'H': h, 'p': p, 'significant_01': p < 0.01}
        if p < 0.01:
            sig_count += 1

    # Nearest-centroid classification
    land_centroids = {}
    for lc in LANDSCAPE_CLASSES:
        idx = groups_by_class[lc]
        if idx:
            land_centroids[lc] = X[idx].mean(axis=0)

    correct = 0
    for i, f in enumerate(folios):
        true_lc = meta[f]['landscape_class']
        min_d = float('inf')
        best_lc = None
        for lc, cent in land_centroids.items():
            d = float(np.linalg.norm(X[i] - cent))
            if d < min_d:
                min_d = d
                best_lc = lc
        if best_lc == true_lc:
            correct += 1
    classification_accuracy = correct / n

    # Between-class / within-class distance ratio
    between_dists = {}
    for i_lc in range(len(LANDSCAPE_CLASSES)):
        for j_lc in range(i_lc + 1, len(LANDSCAPE_CLASSES)):
            lc1, lc2 = LANDSCAPE_CLASSES[i_lc], LANDSCAPE_CLASSES[j_lc]
            s1, s2 = LANDSCAPE_SHORT[lc1], LANDSCAPE_SHORT[lc2]
            if lc1 in land_centroids and lc2 in land_centroids:
                between_dists[f'{s1}-{s2}'] = round(
                    float(np.linalg.norm(land_centroids[lc1] - land_centroids[lc2])), 4)

    within_dists = {}
    for lc in LANDSCAPE_CLASSES:
        idx = groups_by_class[lc]
        short = LANDSCAPE_SHORT[lc]
        if len(idx) > 1 and lc in land_centroids:
            dists = [float(np.linalg.norm(X[i] - land_centroids[lc])) for i in idx]
            within_dists[short] = round(float(np.mean(dists)), 4)

    mean_between = float(np.mean(list(between_dists.values()))) if between_dists else 0
    mean_within = float(np.mean(list(within_dists.values()))) if within_dists else 1
    bw_ratio = mean_between / mean_within if mean_within > 1e-12 else 0

    return {
        'pcs_used': pcs,
        'class_counts': class_counts,
        'centroids': centroids,
        'kruskal_wallis_per_PC': kw_results,
        'n_significant_PCs': sig_count,
        'classification_accuracy': round(classification_accuracy, 4),
        'between_class_distances': between_dists,
        'within_class_distances': within_dists,
        'between_within_ratio': round(bw_ratio, 4)
    }


def main():
    with open(os.path.join(RESULTS_DIR, 't0_feature_matrix_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_manifold_embedding.json')) as f:
        t1 = json.load(f)

    folios = t0['folios']
    meta = t0['folio_metadata']
    n = len(folios)

    result_A = analyze_landscape_in_space(folios, meta, t1['space_A'])
    result_B = analyze_landscape_in_space(folios, meta, t1['space_B'])

    # Cross-space Spearman: Space A PCs vs Space B features
    space_A_scores = t1['space_A']['folio_scores']
    pcs_A = t1['space_A']['pcs_for_80pct']
    B_std = np.array(t0['space_B']['standardized'])
    B_names = t0['metadata']['space_B_features']

    cross_space_corr = {}
    for k in range(pcs_A):
        pc_name = f'PC{k + 1}'
        pc_vals = [space_A_scores[f][pc_name] for f in folios]
        for j, bname in enumerate(B_names):
            b_vals = [B_std[i][j] for i in range(n)]
            rho = spearman_rank(pc_vals, b_vals)
            cross_space_corr[f'{pc_name}_vs_{bname}'] = round(rho, 4)

    # C1669 decision
    sig_A = result_A['n_significant_PCs']
    bw_A = result_A['between_within_ratio']
    sig_B = result_B['n_significant_PCs']
    three_pole_A = bw_A > 1.0

    if sig_A >= 2 and three_pole_A:
        verdict = 'LANDSCAPE_ALIGNED'
    elif sig_B >= 2 or sig_A >= 1:
        verdict = 'LANDSCAPE_WEAK'
    else:
        verdict = 'LANDSCAPE_INDEPENDENT'

    output = {
        'metadata': {
            'phase': '580',
            'script': 't3_landscape_correspondence.py',
            'n_folios': n
        },
        'space_A': result_A,
        'space_B': result_B,
        'cross_space_correlations': cross_space_corr,
        'cross_space_comparison': {
            'A_classification_accuracy': result_A['classification_accuracy'],
            'B_classification_accuracy': result_B['classification_accuracy'],
            'A_n_sig_PCs': sig_A,
            'B_n_sig_PCs': sig_B,
            'better_space': 'A' if result_A['classification_accuracy'] > result_B['classification_accuracy'] else 'B'
        },
        'C1669': {
            'verdict': verdict,
            'sig_PCs_A': sig_A,
            'three_pole_reproduced_A': three_pole_A,
            'bw_ratio_A': result_A['between_within_ratio'],
            'rationale': (f"Space A: {sig_A} significant PCs, "
                          f"three-pole {'reproduced' if three_pole_A else 'not reproduced'} "
                          f"(B/W={bw_A:.2f})")
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't3_landscape_correspondence.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T3: Landscape correspondence analysis complete")
    print(f"  Space A: {sig_A} sig PCs, accuracy={result_A['classification_accuracy']:.2f}, "
          f"B/W={result_A['between_within_ratio']:.2f}")
    for pc, kw in result_A['kruskal_wallis_per_PC'].items():
        print(f"    {pc}: H={kw['H']:.2f}, p={kw['p']:.4f} {'***' if kw['significant_01'] else ''}")
    print(f"  Space B: {sig_B} sig PCs, accuracy={result_B['classification_accuracy']:.2f}, "
          f"B/W={result_B['between_within_ratio']:.2f}")
    print(f"  Cross-space correlations:")
    for k, v in cross_space_corr.items():
        if abs(v) > 0.3:
            print(f"    {k}: {v}")
    print(f"  C1669: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
