"""
Phase 332: SURVIVOR_SET_GEOMETRY_ALIGNMENT
==========================================
Does the discrimination manifold (C982) encode viability structure?
Test: do A records with geometrically similar MIDDLE inventories
produce similar survivor sets (C502/C689)?

This is the final structural phase. Either the manifold encodes
viability (GEOMETRIC_VIABILITY) or it doesn't (ORTHOGONAL_SYSTEMS).
"""

import json
import sys
import time
import warnings
import numpy as np
from pathlib import Path
from scipy.spatial.distance import cosine as cosine_dist
from scipy.stats import spearmanr, pearsonr

warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology


def load_data():
    """Load all precomputed data."""
    data = {}

    # A-record survivors (1,579 records with a_middles and surviving_classes)
    with open(ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'a_record_survivors.json') as f:
        data['survivors'] = json.load(f)

    # Compatibility matrix (972x972)
    data['compat_matrix'] = np.load(
        ROOT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    )

    # Class-token map (for bridge MIDDLE identification)
    with open(ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        cm = json.load(f)
    data['token_to_class'] = {k: int(v) for k, v in cm['token_to_class'].items()}

    return data


def build_embeddings(compat_matrix):
    """Eigendecompose compatibility matrix, return hub-included and hub-removed embeddings."""
    M = compat_matrix.astype(np.float64)
    eigenvalues, eigenvectors = np.linalg.eigh(M)

    # Sort descending
    eigenvalues = eigenvalues[::-1]
    eigenvectors = eigenvectors[:, ::-1]

    # Hub-included: top 101 eigenvectors (including hub eigenmode)
    hub_included_vecs = eigenvectors[:, :101]
    hub_included_vals = eigenvalues[:101]
    hub_included = hub_included_vecs * np.sqrt(np.maximum(hub_included_vals, 0))

    # Hub-removed: eigenvectors 2-101 (skip hub eigenmode)
    residual_vecs = eigenvectors[:, 1:101]
    residual_vals = eigenvalues[1:101]
    residual = residual_vecs * np.sqrt(np.maximum(residual_vals, 0))

    return {
        'hub_included': hub_included,  # (972, 101)
        'residual': residual,           # (972, 100)
        'eigenvalues': eigenvalues,
        'hub_eigenvalue': float(eigenvalues[0]),
        'residual_eigenvalue_sum': float(np.sum(eigenvalues[1:101])),
    }


def reconstruct_middle_list():
    """Reconstruct the sorted MIDDLE list (defines matrix row/column order)."""
    tx = Transcript()
    morph = Morphology()
    a_middles_set = set()
    for token in tx.currier_a():
        word = token.word
        if not word.strip() or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            a_middles_set.add(m.middle)
    a_middles = sorted(a_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(a_middles)}
    return a_middles, mid_to_idx


def identify_bridge_middles(data, mid_to_idx):
    """Identify the 85 bridge MIDDLEs (C1013)."""
    tx = Transcript()
    morph = Morphology()
    token_to_class = data['token_to_class']
    a_middles_set = set(mid_to_idx.keys())

    bridge_middles = set()
    for token in tx.currier_b():
        word = token.word
        if not word.strip() or '*' in word:
            continue
        if word not in token_to_class:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in a_middles_set:
            bridge_middles.add(m.middle)

    return bridge_middles


def prepare_records(data, mid_to_idx, embeddings):
    """Prepare record data: centroids, MIDDLE sets, class sets."""
    records = data['survivors']['records']
    a_middles_set = set(mid_to_idx.keys())

    prepared = []
    for rec in records:
        # Embeddable MIDDLEs (those in the 972-MIDDLE manifold)
        embeddable = [m for m in rec['a_middles'] if m in a_middles_set]
        if len(embeddable) < 2:
            continue

        indices = [mid_to_idx[m] for m in embeddable]

        # Centroids in both embeddings
        hub_centroid = embeddings['hub_included'][indices].mean(axis=0)
        res_centroid = embeddings['residual'][indices].mean(axis=0)

        prepared.append({
            'record_id': rec['a_record'],
            'middle_set': set(embeddable),
            'all_middles': set(rec['a_middles']),
            'class_set': set(rec['surviving_classes']),
            'hub_centroid': hub_centroid,
            'res_centroid': res_centroid,
            'n_embeddable': len(embeddable),
            'n_total': len(rec['a_middles']),
            'indices': indices,
        })

    return prepared


def pairwise_jaccard_binary(sets_list, universe_size):
    """Compute pairwise Jaccard similarity using binary matrix. Returns upper triangle vector."""
    n = len(sets_list)
    # Build binary membership matrix (n_records x universe_size)
    M = np.zeros((n, universe_size), dtype=np.float32)
    for i, s in enumerate(sets_list):
        for elem in s:
            if isinstance(elem, int) and elem < universe_size:
                M[i, elem] = 1.0
            elif isinstance(elem, str):
                # For string sets, caller must convert to indices first
                pass
    return _jaccard_from_binary(M)


def pairwise_jaccard_sets(sets_list):
    """Compute pairwise Jaccard similarity for a list of sets. Returns upper triangle."""
    n = len(sets_list)
    # Build element-to-index mapping
    all_elems = set()
    for s in sets_list:
        all_elems.update(s)
    elem_to_idx = {e: i for i, e in enumerate(sorted(all_elems, key=str))}
    universe = len(elem_to_idx)

    # Binary membership matrix
    M = np.zeros((n, universe), dtype=np.float32)
    for i, s in enumerate(sets_list):
        for elem in s:
            M[i, elem_to_idx[elem]] = 1.0

    return _jaccard_from_binary(M)


def _jaccard_from_binary(M):
    """Compute Jaccard from binary membership matrix. Returns upper triangle vector."""
    # intersection = M @ M.T (dot product of binary rows)
    intersection = M @ M.T
    # union = |A| + |B| - |A & B|
    sizes = M.sum(axis=1)
    union = sizes[:, None] + sizes[None, :] - intersection
    # Jaccard = intersection / union (avoid div by zero)
    with np.errstate(divide='ignore', invalid='ignore'):
        jaccard = np.where(union > 0, intersection / union, 0.0)
    # Extract upper triangle
    idx = np.triu_indices(len(M), k=1)
    return jaccard[idx].astype(np.float64)


def pairwise_cosine_distance(centroids):
    """Compute pairwise cosine distance. Returns upper triangle vector."""
    C = np.array(centroids)
    norms = np.linalg.norm(C, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    C_norm = C / norms
    sim = C_norm @ C_norm.T
    dist = 1.0 - sim
    idx = np.triu_indices(len(C), k=1)
    return dist[idx].astype(np.float64)


def pairwise_size_sum(sizes):
    """Compute pairwise sum of sizes. Returns upper triangle vector."""
    s = np.array(sizes, dtype=np.float64)
    sm = s[:, None] + s[None, :]
    idx = np.triu_indices(len(s), k=1)
    return sm[idx]


def mantel_test(dist_a, dist_b, n_perm=1000, n_records=0):
    """Mantel test: correlation between two distance vectors (upper triangles).

    Uses row/column permutation of one matrix with numpy-vectorized extraction.
    Returns observed correlation, p-value, null distribution stats.
    """
    observed_r, _ = spearmanr(dist_a, dist_b)

    n = n_records
    idx = np.triu_indices(n, k=1)

    # Reshape dist_b into a full symmetric matrix
    full_b = np.zeros((n, n))
    full_b[idx] = dist_b
    full_b = full_b + full_b.T

    # Pre-rank dist_a for faster Spearman (rank once, then Pearson on ranks)
    from scipy.stats import rankdata
    rank_a = rankdata(dist_a)

    rng = np.random.default_rng(42)
    null_rs = np.empty(n_perm)

    for k in range(n_perm):
        if k % 100 == 0 and k > 0:
            print(f"    Mantel permutation {k}/{n_perm}...", flush=True)
        perm = rng.permutation(n)
        perm_b = full_b[np.ix_(perm, perm)]
        perm_upper = perm_b[idx]
        # Spearman = Pearson on ranks
        rank_b = rankdata(perm_upper)
        r, _ = pearsonr(rank_a, rank_b)
        null_rs[k] = r

    # Two-sided: test if |observed| exceeds |null|
    p_value = (np.sum(np.abs(null_rs) >= np.abs(observed_r)) + 1) / (n_perm + 1)

    return {
        'observed_r': float(observed_r),
        'p_value': float(p_value),
        'null_mean': float(np.mean(null_rs)),
        'null_std': float(np.std(null_rs)),
        'z_score': float((observed_r - np.mean(null_rs)) / np.std(null_rs)) if np.std(null_rs) > 0 else 0.0,
    }


def partial_correlation(x, y, z):
    """Partial Spearman correlation of x and y controlling for z."""
    # Regress x on z, get residuals
    z_mean = z.mean()
    z_var = np.sum((z - z_mean) ** 2)
    if z_var == 0:
        return spearmanr(x, y)

    # Rank-based partial correlation
    from scipy.stats import rankdata
    rx = rankdata(x)
    ry = rankdata(y)
    rz = rankdata(z)

    # Regress ranks on rz
    slope_x = np.sum((rx - rx.mean()) * (rz - rz.mean())) / np.sum((rz - rz.mean()) ** 2)
    resid_x = rx - slope_x * rz

    slope_y = np.sum((ry - ry.mean()) * (rz - rz.mean())) / np.sum((rz - rz.mean()) ** 2)
    resid_y = ry - slope_y * rz

    r, p = pearsonr(resid_x, resid_y)
    return r, p


def run_t1(prepared, mid_jaccard, res_cosine):
    """T1: Record Centroid Correlation (Mantel Test)."""
    print("\n=== T1: Record Centroid Correlation (Mantel Test) ===")

    n = len(prepared)
    print(f"  Records: {n}, Pairs: {len(mid_jaccard):,}")

    # Pearson on raw values
    pearson_r, pearson_p = pearsonr(mid_jaccard, 1.0 - res_cosine)
    print(f"  Pearson r(Jaccard, 1-cosine_dist): {pearson_r:.4f} (p={pearson_p:.2e})")

    # Spearman
    spearman_r, spearman_p = spearmanr(mid_jaccard, 1.0 - res_cosine)
    print(f"  Spearman r(Jaccard, 1-cosine_dist): {spearman_r:.4f} (p={spearman_p:.2e})")

    # Mantel test (Jaccard vs cosine distance)
    # Note: higher Jaccard = more similar, higher cosine dist = less similar
    # So we expect NEGATIVE correlation between Jaccard and cosine_distance
    # Or equivalently, POSITIVE correlation between Jaccard and cosine_similarity
    mantel = mantel_test(mid_jaccard, res_cosine, n_perm=1000, n_records=n)
    print(f"  Mantel r(Jaccard, cosine_dist): {mantel['observed_r']:.4f}")
    print(f"  Mantel p: {mantel['p_value']:.4f} (z={mantel['z_score']:.2f})")

    return {
        'n_records': n,
        'n_pairs': len(mid_jaccard),
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'spearman_r': float(spearman_r),
        'spearman_p': float(spearman_p),
        'mantel': mantel,
    }


def run_t2(prepared, mid_jaccard, res_cosine):
    """T2: Hub-Controlled Correlation."""
    print("\n=== T2: Hub-Controlled Correlation ===")

    n = len(prepared)

    # Hub-included cosine distances
    hub_centroids = [r['hub_centroid'] for r in prepared]
    hub_cosine = pairwise_cosine_distance(hub_centroids)

    # Hub-included correlation
    hub_r, hub_p = spearmanr(mid_jaccard, hub_cosine)
    print(f"  Hub-included Spearman r(Jaccard, cosine_dist): {hub_r:.4f} (p={hub_p:.2e})")

    # Residual-only (same as T1)
    res_r, res_p = spearmanr(mid_jaccard, res_cosine)
    print(f"  Hub-removed Spearman r(Jaccard, cosine_dist): {res_r:.4f} (p={res_p:.2e})")

    ratio = abs(res_r) / abs(hub_r) if abs(hub_r) > 0 else float('inf')
    print(f"  Ratio (residual/hub): {ratio:.3f}")

    return {
        'hub_included_r': float(hub_r),
        'hub_included_p': float(hub_p),
        'hub_removed_r': float(res_r),
        'hub_removed_p': float(res_p),
        'ratio': float(ratio),
    }


def run_t3(prepared, mid_jaccard, res_cosine):
    """T3: Size-Controlled Partial Correlation."""
    print("\n=== T3: Size-Controlled Partial Correlation ===")

    sizes = [r['n_embeddable'] for r in prepared]
    size_sum = pairwise_size_sum(sizes)

    # Raw correlation (same as T1 Spearman)
    raw_r, raw_p = spearmanr(mid_jaccard, res_cosine)

    # Partial correlation controlling for size
    partial_r, partial_p = partial_correlation(mid_jaccard, res_cosine, size_sum)
    print(f"  Raw Spearman r: {raw_r:.4f}")
    print(f"  Partial r (controlling size): {partial_r:.4f} (p={partial_p:.2e})")

    retention = abs(partial_r) / abs(raw_r) if abs(raw_r) > 0 else float('inf')
    print(f"  Retention: {retention:.1%} of raw correlation")

    return {
        'raw_r': float(raw_r),
        'partial_r': float(partial_r),
        'partial_p': float(partial_p),
        'retention': float(retention),
    }


def run_t4(prepared, res_cosine, mid_jaccard):
    """T4: Survivor-Set Class-Level Alignment."""
    print("\n=== T4: Survivor-Set Class-Level Alignment ===")

    n = len(prepared)

    # Class-level Jaccard
    class_sets = [r['class_set'] for r in prepared]
    class_jaccard = pairwise_jaccard_sets(class_sets)

    # Correlate with geometric distance
    spearman_r, spearman_p = spearmanr(class_jaccard, res_cosine)
    print(f"  Spearman r(class_Jaccard, cosine_dist): {spearman_r:.4f} (p={spearman_p:.2e})")

    # Mantel test
    mantel = mantel_test(class_jaccard, res_cosine, n_perm=1000, n_records=n)
    print(f"  Mantel r: {mantel['observed_r']:.4f}")
    print(f"  Mantel p: {mantel['p_value']:.4f} (z={mantel['z_score']:.2f})")

    # MIDDLE Jaccard vs class Jaccard correlation (internal consistency)
    mid_class_r, _ = spearmanr(mid_jaccard, class_jaccard)
    print(f"  MIDDLE Jaccard vs class Jaccard r: {mid_class_r:.4f}")

    return {
        'spearman_r': float(spearman_r),
        'spearman_p': float(spearman_p),
        'mantel': mantel,
        'middle_class_jaccard_r': float(mid_class_r),
    }


def run_t5(prepared, mid_to_idx, embeddings, bridge_middles, full_r_abs):
    """T5: Bridge-Dominated vs Non-Bridge Control."""
    print("\n=== T5: Bridge-Dominated vs Non-Bridge Control ===")

    # For each record, compute bridge-only and non-bridge-only centroids
    bridge_records = []
    nonbridge_records = []
    both_records = []

    for rec in prepared:
        bridge_mids = [m for m in rec['middle_set'] if m in bridge_middles]
        nonbridge_mids = [m for m in rec['middle_set'] if m not in bridge_middles]

        has_bridge = len(bridge_mids) >= 2
        has_nonbridge = len(nonbridge_mids) >= 2

        if has_bridge:
            b_idx = [mid_to_idx[m] for m in bridge_mids]
            b_centroid = embeddings['residual'][b_idx].mean(axis=0)
            bridge_records.append({
                'middle_set': rec['middle_set'],
                'centroid': b_centroid,
            })

        if has_nonbridge:
            nb_idx = [mid_to_idx[m] for m in nonbridge_mids]
            nb_centroid = embeddings['residual'][nb_idx].mean(axis=0)
            nonbridge_records.append({
                'middle_set': rec['middle_set'],
                'centroid': nb_centroid,
            })

        if has_bridge and has_nonbridge:
            both_records.append({
                'middle_set': rec['middle_set'],
                'bridge_centroid': b_centroid,
                'nonbridge_centroid': nb_centroid,
            })

    print(f"  Records with >=2 bridge MIDDLEs: {len(bridge_records)}")
    print(f"  Records with >=2 non-bridge MIDDLEs: {len(nonbridge_records)}")
    print(f"  Records with both: {len(both_records)}")

    # Bridge-only correlation
    if len(bridge_records) >= 50:
        b_mid_sets = [r['middle_set'] for r in bridge_records]
        b_jaccard = pairwise_jaccard_sets(b_mid_sets)
        b_centroids = [r['centroid'] for r in bridge_records]
        b_cosine = pairwise_cosine_distance(b_centroids)
        b_r, b_p = spearmanr(b_jaccard, b_cosine)
        print(f"  Bridge-only Spearman r: {b_r:.4f} (p={b_p:.2e})")
    else:
        b_r, b_p = float('nan'), float('nan')
        print(f"  Bridge-only: insufficient records ({len(bridge_records)})")

    # Non-bridge-only correlation
    if len(nonbridge_records) >= 50:
        nb_mid_sets = [r['middle_set'] for r in nonbridge_records]
        nb_jaccard = pairwise_jaccard_sets(nb_mid_sets)
        nb_centroids = [r['centroid'] for r in nonbridge_records]
        nb_cosine = pairwise_cosine_distance(nb_centroids)
        nb_r, nb_p = spearmanr(nb_jaccard, nb_cosine)
        print(f"  Non-bridge Spearman r: {nb_r:.4f} (p={nb_p:.2e})")
    else:
        nb_r, nb_p = float('nan'), float('nan')
        print(f"  Non-bridge: insufficient records ({len(nonbridge_records)})")

    # Ratio (full_r_abs passed from caller to avoid recomputation)
    nb_ratio = abs(nb_r) / full_r_abs if full_r_abs > 0 and not np.isnan(nb_r) else float('nan')
    print(f"  Non-bridge/full ratio: {nb_ratio:.3f}" if not np.isnan(nb_ratio) else "  Non-bridge/full ratio: N/A")

    return {
        'n_bridge_records': len(bridge_records),
        'n_nonbridge_records': len(nonbridge_records),
        'n_both': len(both_records),
        'bridge_r': float(b_r),
        'bridge_p': float(b_p),
        'nonbridge_r': float(nb_r),
        'nonbridge_p': float(nb_p),
        'nonbridge_full_ratio': float(nb_ratio),
    }


def run_t6(t1, t2, t3, t4, t5):
    """T6: Synthesis."""
    print("\n=== T6: Synthesis ===")

    # P1: MIDDLE Jaccard correlates with centroid cosine (Mantel p < 0.05)
    p1_pass = t1['mantel']['p_value'] < 0.05
    print(f"  P1 (Mantel p < 0.05): {'PASS' if p1_pass else 'FAIL'} (p={t1['mantel']['p_value']:.4f})")

    # P2: Correlation persists after hub removal (residual r > 0.05)
    p2_pass = abs(t2['hub_removed_r']) > 0.05
    print(f"  P2 (residual |r| > 0.05): {'PASS' if p2_pass else 'FAIL'} (r={t2['hub_removed_r']:.4f})")

    # P3: Size-controlled partial r > 50% of raw r
    p3_pass = t3['retention'] > 0.50
    print(f"  P3 (retention > 50%): {'PASS' if p3_pass else 'FAIL'} (retention={t3['retention']:.1%})")

    # P4: Class-level survivor Jaccard correlates (Mantel p < 0.05)
    p4_pass = t4['mantel']['p_value'] < 0.05
    print(f"  P4 (class Mantel p < 0.05): {'PASS' if p4_pass else 'FAIL'} (p={t4['mantel']['p_value']:.4f})")

    # P5: Non-bridge centroid r > 50% of full r
    p5_pass = not np.isnan(t5['nonbridge_full_ratio']) and t5['nonbridge_full_ratio'] > 0.50
    ratio_str = f"{t5['nonbridge_full_ratio']:.3f}" if not np.isnan(t5['nonbridge_full_ratio']) else "N/A"
    print(f"  P5 (non-bridge ratio > 50%): {'PASS' if p5_pass else 'FAIL'} (ratio={ratio_str})")

    # P6: Hub-removed weaker than hub-included (ratio < 0.8)
    p6_pass = t2['ratio'] < 0.8
    print(f"  P6 (residual/hub ratio < 0.8): {'PASS' if p6_pass else 'FAIL'} (ratio={t2['ratio']:.3f})")

    predictions = {
        'P1_mantel_significant': {'pass': p1_pass, 'p': t1['mantel']['p_value']},
        'P2_residual_persists': {'pass': p2_pass, 'r': t2['hub_removed_r']},
        'P3_size_controlled': {'pass': p3_pass, 'retention': t3['retention']},
        'P4_class_level': {'pass': p4_pass, 'p': t4['mantel']['p_value']},
        'P5_nonbridge_signal': {'pass': p5_pass, 'ratio': t5['nonbridge_full_ratio']},
        'P6_hub_stronger': {'pass': p6_pass, 'ratio': t2['ratio']},
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])

    # Verdict
    if p1_pass and p2_pass and p3_pass and p4_pass and p5_pass:
        verdict = 'GEOMETRIC_VIABILITY'
    elif p1_pass and (not p2_pass or not p3_pass):
        verdict = 'HUB_MEDIATED_VIABILITY'
    elif p1_pass and p2_pass and p3_pass and (not p4_pass or not p5_pass):
        verdict = 'PARTIAL_ALIGNMENT'
    elif not p1_pass:
        verdict = 'ORTHOGONAL_SYSTEMS'
    else:
        # Fallback
        if n_pass >= 4:
            verdict = 'PARTIAL_ALIGNMENT'
        elif p1_pass:
            verdict = 'HUB_MEDIATED_VIABILITY'
        else:
            verdict = 'ORTHOGONAL_SYSTEMS'

    print(f"\n  Predictions: {n_pass}/6 passed")
    print(f"\n  *** VERDICT: {verdict} ***")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'verdict': verdict,
    }


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("Phase 332: SURVIVOR_SET_GEOMETRY_ALIGNMENT")
    print("=" * 60)

    start = time.time()

    # Load data
    print("\nLoading data...")
    data = load_data()

    # Reconstruct MIDDLE list and mapping
    print("Reconstructing MIDDLE list...")
    a_middles, mid_to_idx = reconstruct_middle_list()
    print(f"  {len(a_middles)} MIDDLEs in manifold")

    # Build embeddings
    print("Computing eigenvector embeddings...")
    embeddings = build_embeddings(data['compat_matrix'])
    print(f"  Hub eigenvalue: {embeddings['hub_eigenvalue']:.2f}")
    print(f"  Residual sum (lambda_2-101): {embeddings['residual_eigenvalue_sum']:.2f}")

    # Identify bridge MIDDLEs (C1013)
    print("Identifying bridge MIDDLEs...")
    bridge_middles = identify_bridge_middles(data, mid_to_idx)
    print(f"  Bridge MIDDLEs: {len(bridge_middles)}")

    # Prepare records
    print("Preparing records...")
    prepared = prepare_records(data, mid_to_idx, embeddings)
    print(f"  Usable records (>=2 embeddable): {len(prepared)}")

    # Precompute pairwise matrices (shared across tests)
    print("Computing pairwise matrices...")
    mid_sets = [r['middle_set'] for r in prepared]
    mid_jaccard = pairwise_jaccard_sets(mid_sets)
    res_centroids = [r['res_centroid'] for r in prepared]
    res_cosine = pairwise_cosine_distance(res_centroids)
    print(f"  Pairs: {len(mid_jaccard):,}")

    # Run tests
    t1 = run_t1(prepared, mid_jaccard, res_cosine)
    full_r_abs = abs(t1['spearman_r'])
    t2 = run_t2(prepared, mid_jaccard, res_cosine)
    t3 = run_t3(prepared, mid_jaccard, res_cosine)
    t4 = run_t4(prepared, res_cosine, mid_jaccard)
    t5 = run_t5(prepared, mid_to_idx, embeddings, bridge_middles, full_r_abs)
    t6 = run_t6(t1, t2, t3, t4, t5)

    elapsed = time.time() - start

    # Save results
    def numpy_safe(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, set):
            return sorted(list(obj))
        return str(obj)

    results = {
        'phase': 'SURVIVOR_SET_GEOMETRY_ALIGNMENT',
        'phase_number': 332,
        'question': 'Does the discrimination manifold encode viability structure?',
        'n_manifold_middles': len(a_middles),
        'n_bridge_middles': len(bridge_middles),
        'n_records_total': len(data['survivors']['records']),
        'n_records_usable': len(prepared),
        'hub_eigenvalue': embeddings['hub_eigenvalue'],
        't1_centroid_correlation': t1,
        't2_hub_control': t2,
        't3_size_control': t3,
        't4_class_alignment': t4,
        't5_bridge_split': t5,
        't6_synthesis': t6,
        'elapsed_seconds': round(elapsed, 1),
    }

    out_path = ROOT / 'phases' / 'SURVIVOR_SET_GEOMETRY_ALIGNMENT' / 'results' / 'survivor_geometry.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=numpy_safe)

    print(f"\nResults saved to {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")
