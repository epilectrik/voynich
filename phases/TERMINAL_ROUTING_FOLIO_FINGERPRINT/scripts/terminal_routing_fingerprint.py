"""Phase 593: Terminal Routing Folio Fingerprint

Tests whether per-folio TERM→HEAD transition matrices (42-cell vectors)
vary across Currier B folios beyond noise and section effects, and whether
that variation correlates with the apparatus manifold (C1670) or accent PCs (C1367).

TERM = MIDDLE terminal atom from decompose_middle_hmt() (NOT suffix — C1564).
HEAD = MIDDLE head atom from decompose_middle_hmt().
"""

import sys, os, json, time
import numpy as np
from collections import defaultdict, Counter
from numpy.linalg import lstsq
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

# ── Constants ──────────────────────────────────────────────────────────

TERM_TYPES = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']  # 7 MIDDLE-terminal atoms
HEAD_TYPES = ['a', 'e', 'o', 'k', 't', 'headless']     # 6 HEAD atoms
N_CELLS = len(TERM_TYPES) * len(HEAD_TYPES)              # 42

TERM_IDX = {t: i for i, t in enumerate(TERM_TYPES)}
HEAD_IDX = {h: i for i, h in enumerate(HEAD_TYPES)}

MIN_TRANSITIONS = 100
SENSITIVITY_THRESHOLDS = [50, 100, 150, 200]
N_PERMS = 1000
SEED = 42

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

# ── Helpers ────────────────────────────────────────────────────────────

def get_head_and_term(word, morph):
    """Extract MIDDLE HEAD and TERM atoms. Returns (head, term) or (None, None)."""
    m = morph.extract(word)
    if not m.middle:
        return None, None
    head, mods, term, frame = decompose_middle_hmt(m.middle)
    head = head if head else 'headless'
    return head, term


def build_transition_counts(tokens_by_folio_line):
    """Build per-folio 7×6 transition count matrices.

    tokens_by_folio_line: dict of (folio, line) -> [(head, term), ...]
    Returns: dict of folio -> 7×6 numpy count matrix, and total transition counts
    """
    folio_counts = defaultdict(lambda: np.zeros((len(TERM_TYPES), len(HEAD_TYPES))))
    folio_n_transitions = Counter()

    for (folio, line), pairs in tokens_by_folio_line.items():
        for i in range(len(pairs) - 1):
            _, term_i = pairs[i]
            head_j, _ = pairs[i + 1]
            if term_i in TERM_IDX and head_j in HEAD_IDX:
                folio_counts[folio][TERM_IDX[term_i], HEAD_IDX[head_j]] += 1
                folio_n_transitions[folio] += 1

    return dict(folio_counts), dict(folio_n_transitions)


def normalize_to_proportions(count_matrix):
    """Normalize count matrix to proportions (sum = 1)."""
    total = count_matrix.sum()
    if total == 0:
        return np.ones_like(count_matrix) / count_matrix.size
    return count_matrix / total


def jsd_matrix(prop_matrix):
    """Compute pairwise JSD between rows of a proportion matrix."""
    n = prop_matrix.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = jensenshannon(prop_matrix[i], prop_matrix[j])
            D[i, j] = D[j, i] = d
    return D


def euclidean_matrix(matrix):
    """Compute pairwise Euclidean distance matrix."""
    from scipy.spatial.distance import pdist, squareform
    return squareform(pdist(matrix, metric='euclidean'))


def compute_icc(data_matrix):
    """ICC(1,1) on matrix where rows = groups (folios), cols = measures (cells).

    data_matrix: N_folios × N_cells
    Returns: (icc, MSB, MSW, k0)
    """
    k = data_matrix.shape[0]  # number of groups
    n = data_matrix.shape[1]  # number of measures per group
    if k < 2:
        return None, None, None, None

    grand_mean = data_matrix.mean()
    group_means = data_matrix.mean(axis=1)

    SSB = n * np.sum((group_means - grand_mean) ** 2)
    SSW = np.sum((data_matrix - group_means[:, None]) ** 2)

    dfB = k - 1
    dfW = k * (n - 1)

    MSB = SSB / dfB if dfB > 0 else 0
    MSW = SSW / dfW if dfW > 0 else 0

    k0 = n  # balanced design (all folios have same number of cells)

    denom = MSB + (k0 - 1) * MSW
    if denom == 0:
        return 0.0, float(MSB), float(MSW), float(k0)

    icc = (MSB - MSW) / denom
    return float(icc), float(MSB), float(MSW), float(k0)


def mantel_test(dist_a, dist_b, n_perms=N_PERMS, seed=SEED):
    """Mantel test: correlation between two distance matrices."""
    rng = np.random.default_rng(seed)
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]

    r_obs = np.corrcoef(a_flat, b_flat)[0, 1]

    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(n)
        b_perm = dist_b[np.ix_(perm, perm)]
        r_nulls[p] = np.corrcoef(a_flat, b_perm[idx])[0, 1]

    p_val = (np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1)
    return float(r_obs), float(p_val), float(np.mean(r_nulls)), float(np.std(r_nulls))


def partial_mantel(dist_a, dist_b, control_dists, n_perms=N_PERMS, seed=SEED):
    """Partial Mantel: residualize both matrices against controls, then correlate."""
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]

    controls = np.column_stack([cd[idx] for cd in control_dists])
    A_mat = np.column_stack([controls, np.ones(len(a_flat))])

    res_a = a_flat - A_mat @ lstsq(A_mat, a_flat, rcond=None)[0]
    res_b = b_flat - A_mat @ lstsq(A_mat, b_flat, rcond=None)[0]

    r_obs = np.corrcoef(res_a, res_b)[0, 1]

    rng = np.random.default_rng(seed)
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(len(res_a))
        r_nulls[p] = np.corrcoef(res_a, res_b[perm])[0, 1]

    p_val = (np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1)
    return float(r_obs), float(p_val)


def section_distance_matrix(folio_list, folio_section):
    """Build binary distance matrix: 0 if same section, 1 if different."""
    n = len(folio_list)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if folio_section[folio_list[i]] != folio_section[folio_list[j]]:
                D[i, j] = D[j, i] = 1.0
    return D


def fdr_correction(p_values, alpha=0.05):
    """Benjamini-Hochberg FDR correction. Returns q-values."""
    p_arr = np.array(p_values)
    n = len(p_arr)
    sorted_idx = np.argsort(p_arr)
    q_values = np.empty(n)
    for rank, idx in enumerate(sorted_idx, 1):
        q_values[idx] = p_arr[idx] * n / rank
    # Enforce monotonicity (from largest to smallest rank)
    for i in range(len(sorted_idx) - 2, -1, -1):
        idx = sorted_idx[i]
        next_idx = sorted_idx[i + 1]
        q_values[idx] = min(q_values[idx], q_values[next_idx])
    q_values = np.minimum(q_values, 1.0)
    return q_values


def convert_numpy(obj):
    """Recursively convert numpy types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj


# ── Main ───────────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    rng = np.random.default_rng(SEED)
    results = {}

    # ── T1: Build Per-Folio Transition Matrices ────────────────────────
    print("T1: Building per-folio transition matrices...")

    tx = Transcript()
    morph = Morphology()

    # Collect (head, term) pairs per (folio, line) for B tokens
    tokens_by_folio_line = defaultdict(list)
    folio_section = {}

    for token in tx.currier_b():
        head, term = get_head_and_term(token.word, morph)
        if head is not None:
            tokens_by_folio_line[(token.folio, token.line)].append((head, term))
        if token.folio not in folio_section:
            folio_section[token.folio] = token.section

    folio_counts, folio_n_transitions = build_transition_counts(tokens_by_folio_line)

    # Sensitivity analysis: how many folios pass each threshold
    sensitivity = {}
    for thresh in SENSITIVITY_THRESHOLDS:
        n_pass = sum(1 for n in folio_n_transitions.values() if n >= thresh)
        sensitivity[str(thresh)] = n_pass

    # Filter to folios with >= MIN_TRANSITIONS
    valid_folios = sorted([f for f, n in folio_n_transitions.items() if n >= MIN_TRANSITIONS])
    print(f"  {len(valid_folios)} folios with >= {MIN_TRANSITIONS} transitions "
          f"(of {len(folio_n_transitions)} total)")

    # Build proportion matrix
    prop_matrix = np.zeros((len(valid_folios), N_CELLS))
    count_matrix = np.zeros((len(valid_folios), N_CELLS))
    for i, folio in enumerate(valid_folios):
        counts = folio_counts[folio]
        count_matrix[i] = counts.flatten()
        prop_matrix[i] = normalize_to_proportions(counts).flatten()

    # Spot-check: verify TERM extraction uses MIDDLE atoms
    spot_check = {}
    test_words = ['chody', 'daiin', 'shedy', 'qokeedy', 'okal']
    for w in test_words:
        h, t = get_head_and_term(w, morph)
        spot_check[w] = {'head': h, 'term': t}

    results['T1'] = {
        'n_b_folios_total': len(folio_n_transitions),
        'n_valid_folios': len(valid_folios),
        'valid_folios': valid_folios,
        'min_transitions': MIN_TRANSITIONS,
        'sensitivity_analysis': sensitivity,
        'transition_counts': {f: folio_n_transitions[f] for f in valid_folios},
        'mean_transitions': float(np.mean([folio_n_transitions[f] for f in valid_folios])),
        'median_transitions': float(np.median([folio_n_transitions[f] for f in valid_folios])),
        'term_types': TERM_TYPES,
        'head_types': HEAD_TYPES,
        'spot_check_term_extraction': spot_check,
        'global_transition_matrix': count_matrix.sum(axis=0).reshape(
            len(TERM_TYPES), len(HEAD_TYPES)).tolist(),
    }

    # ── T0: PCA Dimensionality Reduction ───────────────────────────────
    print("T0: PCA dimensionality reduction...")

    # Center the proportion matrix
    centered = prop_matrix - prop_matrix.mean(axis=0)
    cov = np.cov(centered, rowvar=True)  # folio × folio covariance

    # PCA via SVD on centered data
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    explained_var = S ** 2 / np.sum(S ** 2)
    cumulative_var = np.cumsum(explained_var)

    # Effective rank: PCs needed for 90% variance
    effective_rank = int(np.searchsorted(cumulative_var, 0.90) + 1)

    # PCA-reduced vectors (top PCs covering 90% variance)
    pca_vectors = U[:, :effective_rank] * S[:effective_rank]

    # Per-terminal-row variance decomposition
    terminal_row_variance = {}
    for t_idx, t_name in enumerate(TERM_TYPES):
        row_start = t_idx * len(HEAD_TYPES)
        row_end = row_start + len(HEAD_TYPES)
        row_data = prop_matrix[:, row_start:row_end]
        terminal_row_variance[t_name] = float(np.var(row_data, axis=0).sum())

    # Top PC loadings
    pc_loadings = {}
    for pc in range(min(5, effective_rank + 2)):
        if pc >= Vt.shape[0]:
            break
        loadings = Vt[pc].reshape(len(TERM_TYPES), len(HEAD_TYPES))
        top_cells = []
        flat = Vt[pc]
        top_idx = np.argsort(np.abs(flat))[::-1][:5]
        for idx in top_idx:
            t_i = idx // len(HEAD_TYPES)
            h_i = idx % len(HEAD_TYPES)
            top_cells.append({
                'term': TERM_TYPES[t_i],
                'head': HEAD_TYPES[h_i],
                'loading': float(flat[idx])
            })
        pc_loadings[f'PC{pc+1}'] = {
            'variance_explained': float(explained_var[pc]),
            'cumulative': float(cumulative_var[pc]),
            'top_loadings': top_cells
        }

    results['T0'] = {
        'effective_rank': effective_rank,
        'variance_explained': explained_var[:10].tolist(),
        'cumulative_variance': cumulative_var[:10].tolist(),
        'pc_loadings': pc_loadings,
        'terminal_row_variance': terminal_row_variance,
        'apparatus_manifold_effective_rank': 5.88,
        'comparison': 'routing_rank_vs_apparatus'
    }
    print(f"  Effective rank: {effective_rank} (90% variance)")
    print(f"  PC1: {explained_var[0]:.1%}, PC2: {explained_var[1]:.1%}")

    # ── T2: Folio Distinguishability ───────────────────────────────────
    print("T2: Folio distinguishability test...")

    # Primary: JSD distance matrix on proportion vectors
    jsd_dist = jsd_matrix(prop_matrix)
    mean_jsd = float(jsd_dist[np.triu_indices(len(valid_folios), k=1)].mean())

    # Permutation distance test: shuffle tokens across folios within section
    print("  Running permutation distance test...")
    section_assignments = [folio_section[f] for f in valid_folios]
    unique_sections = sorted(set(section_assignments))

    # Group folio indices by section
    section_folio_indices = defaultdict(list)
    for i, s in enumerate(section_assignments):
        section_folio_indices[s].append(i)

    # For token-shuffle: we need the raw (term, head) pairs per folio
    folio_raw_pairs = defaultdict(list)
    for (folio, line), pairs in tokens_by_folio_line.items():
        if folio not in valid_folios:
            continue
        for i in range(len(pairs) - 1):
            _, term_i = pairs[i]
            head_j, _ = pairs[i + 1]
            if term_i in TERM_IDX and head_j in HEAD_IDX:
                folio_raw_pairs[folio].append((term_i, head_j))

    # Token-shuffle null: shuffle (term, head) assignments within each folio
    null_mean_jsds = []
    for perm_i in range(N_PERMS):
        null_prop = np.zeros_like(prop_matrix)
        for fi, folio in enumerate(valid_folios):
            pairs = folio_raw_pairs[folio]
            terms = [p[0] for p in pairs]
            heads = [p[1] for p in pairs]
            rng.shuffle(terms)
            rng.shuffle(heads)
            counts = np.zeros((len(TERM_TYPES), len(HEAD_TYPES)))
            for t, h in zip(terms, heads):
                counts[TERM_IDX[t], HEAD_IDX[h]] += 1
            null_prop[fi] = normalize_to_proportions(counts).flatten()
        null_jsd = jsd_matrix(null_prop)
        null_mean_jsds.append(float(null_jsd[np.triu_indices(len(valid_folios), k=1)].mean()))

    token_shuffle_p = (np.sum(np.array(null_mean_jsds) >= mean_jsd) + 1) / (N_PERMS + 1)

    # Supplementary ICC on PCA-reduced vectors
    icc, MSB, MSW, k0 = compute_icc(pca_vectors)

    # Bootstrap ICC CI
    icc_boots = []
    for _ in range(N_PERMS):
        boot_idx = rng.choice(len(valid_folios), size=len(valid_folios), replace=True)
        boot_icc, _, _, _ = compute_icc(pca_vectors[boot_idx])
        if boot_icc is not None:
            icc_boots.append(boot_icc)
    icc_ci = (float(np.percentile(icc_boots, 2.5)), float(np.percentile(icc_boots, 97.5)))

    # Folio-length confound check
    folio_trans_counts = np.array([folio_n_transitions[f] for f in valid_folios])
    folio_mean_dists = np.array([jsd_dist[i].sum() / (len(valid_folios) - 1)
                                  for i in range(len(valid_folios))])
    length_rho, length_p = spearmanr(folio_trans_counts, folio_mean_dists)

    length_confound_significant = length_p < 0.05

    results['T2'] = {
        'mean_jsd': mean_jsd,
        'token_shuffle_null_mean': float(np.mean(null_mean_jsds)),
        'token_shuffle_null_p95': float(np.percentile(null_mean_jsds, 95)),
        'token_shuffle_null_p99': float(np.percentile(null_mean_jsds, 99)),
        'token_shuffle_p_value': float(token_shuffle_p),
        'exceeds_token_shuffle_null': bool(mean_jsd > np.percentile(null_mean_jsds, 99)),
        'icc': icc,
        'icc_MSB': MSB,
        'icc_MSW': MSW,
        'icc_bootstrap_ci_95': icc_ci,
        'folio_length_confound': {
            'spearman_rho': float(length_rho),
            'p_value': float(length_p),
            'significant': bool(length_confound_significant),
            'interpretation': 'Short folios artifactually distinctive' if length_confound_significant
                            else 'No length confound detected'
        }
    }

    # If length confound, regress out and recompute
    if length_confound_significant:
        print("  Length confound detected — regressing out folio length...")
        log_counts = np.log(folio_trans_counts)
        # Regress each cell proportion on log(count)
        corrected_prop = np.zeros_like(prop_matrix)
        for j in range(N_CELLS):
            slope, intercept = np.polyfit(log_counts, prop_matrix[:, j], 1)
            corrected_prop[:, j] = prop_matrix[:, j] - slope * log_counts
        # Re-normalize rows to sum to 1 (shift to positive, then normalize)
        for i in range(corrected_prop.shape[0]):
            row = corrected_prop[i]
            row = row - row.min() + 1e-10  # shift to positive
            corrected_prop[i] = row / row.sum()

        jsd_dist_corrected = jsd_matrix(corrected_prop)
        mean_jsd_corrected = float(jsd_dist_corrected[np.triu_indices(len(valid_folios), k=1)].mean())
        results['T2']['corrected_mean_jsd'] = mean_jsd_corrected

        # Use corrected for downstream
        prop_for_downstream = corrected_prop
        jsd_for_downstream = jsd_dist_corrected
        # Re-run PCA on corrected
        centered_c = corrected_prop - corrected_prop.mean(axis=0)
        U_c, S_c, Vt_c = np.linalg.svd(centered_c, full_matrices=False)
        expl_c = S_c ** 2 / np.sum(S_c ** 2)
        cum_c = np.cumsum(expl_c)
        eff_rank_c = int(np.searchsorted(cum_c, 0.90) + 1)
        pca_for_downstream = U_c[:, :eff_rank_c] * S_c[:eff_rank_c]
        results['T2']['corrected_effective_rank'] = eff_rank_c
    else:
        prop_for_downstream = prop_matrix
        jsd_for_downstream = jsd_dist
        pca_for_downstream = pca_vectors

    folio_signal_exists = results['T2']['exceeds_token_shuffle_null']
    print(f"  Mean JSD: {mean_jsd:.6f}")
    print(f"  Token-shuffle null p99: {np.percentile(null_mean_jsds, 99):.6f}")
    print(f"  Signal exists: {folio_signal_exists}")
    print(f"  ICC: {icc:.4f} [{icc_ci[0]:.4f}, {icc_ci[1]:.4f}]")
    print(f"  Length confound: rho={length_rho:.3f}, p={length_p:.4f}")

    # ── T3: Within-Section Folio Discrimination ────────────────────────
    print("T3: Within-section folio discrimination...")

    # Load REGIME assignments
    regime_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data',
                               'regime_folio_mapping.json')
    with open(regime_path) as f:
        regime_data = json.load(f)
    folio_regime = {f: v['regime'] for f, v in regime_data['regime_assignments'].items()}

    # Section-level analysis
    t3_results = {
        'sections': {},
        'overall_silhouette': None,
        'section_structure_real': False,
        'c1570_criterion_met': False,
        'regime_confound': {}
    }

    # Distance matrix for PCA-reduced vectors (Euclidean on PCA space)
    pca_dist = euclidean_matrix(pca_for_downstream)

    # Section-shuffled null: test if section structure is real
    section_labels = np.array([folio_section[f] for f in valid_folios])

    def mean_within_section_distance(dist_mat, labels):
        within = []
        for s in set(labels):
            idx = np.where(labels == s)[0]
            if len(idx) < 2:
                continue
            for i in range(len(idx)):
                for j in range(i + 1, len(idx)):
                    within.append(dist_mat[idx[i], idx[j]])
        return np.mean(within) if within else 0

    real_within_dist = mean_within_section_distance(pca_dist, section_labels)

    null_within_dists = []
    for _ in range(N_PERMS):
        shuffled = rng.permutation(section_labels)
        null_within_dists.append(mean_within_section_distance(pca_dist, shuffled))

    section_p = (np.sum(np.array(null_within_dists) <= real_within_dist) + 1) / (N_PERMS + 1)
    t3_results['section_structure_real'] = bool(section_p < 0.05)
    t3_results['section_p_value'] = float(section_p)
    t3_results['mean_within_section_distance'] = float(real_within_dist)
    t3_results['null_within_section_p05'] = float(np.percentile(null_within_dists, 5))

    # Silhouette scores
    silhouettes = []
    for i in range(len(valid_folios)):
        s_i = section_labels[i]
        same = [pca_dist[i, j] for j in range(len(valid_folios))
                if j != i and section_labels[j] == s_i]
        diff = [pca_dist[i, j] for j in range(len(valid_folios))
                if section_labels[j] != s_i]
        if same and diff:
            a = np.mean(same)
            b = np.mean(diff)
            silhouettes.append((b - a) / max(a, b))
    t3_results['overall_silhouette'] = float(np.mean(silhouettes)) if silhouettes else 0

    # Per-section LOO nearest-neighbor classification
    any_section_significant = False
    for section in unique_sections:
        sec_idx = [i for i, s in enumerate(section_assignments) if s == section]
        sec_folios = [valid_folios[i] for i in sec_idx]

        if len(sec_idx) < 3:
            t3_results['sections'][section] = {
                'n_folios': len(sec_idx),
                'skipped': True,
                'reason': 'fewer than 3 folios'
            }
            continue

        # LOO-1NN on PCA-reduced vectors
        sec_pca = pca_for_downstream[sec_idx]
        n_sec = len(sec_idx)
        correct = 0
        for i in range(n_sec):
            dists = np.array([np.linalg.norm(sec_pca[i] - sec_pca[j])
                             for j in range(n_sec) if j != i])
            nearest = np.argmin(dists)
            # nearest index maps to sec_idx (excluding i)
            actual_nearest = [j for j in range(n_sec) if j != i][nearest]
            if sec_folios[actual_nearest] != sec_folios[i]:
                correct += 1  # correctly identified as different folio

        # Actually, LOO-1NN accuracy = can we correctly identify the folio?
        # With LOO on n folios: predict which folio it is.
        # chance = 1/n_sec
        loo_accuracy = correct / n_sec  # this is wrong, let me fix

        # Correct LOO: For each folio, find nearest neighbor among remaining.
        # "Above chance" = nearest neighbor is not random.
        # Better: compute mean within-section pairwise distance and test if
        # variance in pairwise distances is structured (some pairs closer).
        # But the plan says LOO accuracy, so:
        # Each folio is left out. Nearest neighbor found. If it's the "correct"
        # folio... but each folio is unique, so "correct" doesn't apply.

        # What we actually want: can we distinguish folios within the section?
        # Test: within-section pairwise distances have more variance than
        # expected under permutation (if all folios were interchangeable,
        # shuffling folio labels wouldn't change distance structure).

        # Permutation test on within-section distance variance
        sec_dists = pca_dist[np.ix_(sec_idx, sec_idx)]
        triu = np.triu_indices(n_sec, k=1)
        real_dist_var = float(np.var(sec_dists[triu]))

        null_vars = []
        # Get all tokens for this section
        sec_all_pairs = []
        sec_folio_sizes = []
        for fi in sec_idx:
            f = valid_folios[fi]
            pairs = folio_raw_pairs[f]
            sec_all_pairs.extend(pairs)
            sec_folio_sizes.append(len(pairs))

        for _ in range(N_PERMS):
            # Shuffle all tokens within section, redistribute to folio-sized chunks
            shuffled_pairs = list(sec_all_pairs)
            rng.shuffle(shuffled_pairs)
            null_prop = np.zeros((n_sec, N_CELLS))
            offset = 0
            for fi_local in range(n_sec):
                chunk = shuffled_pairs[offset:offset + sec_folio_sizes[fi_local]]
                offset += sec_folio_sizes[fi_local]
                counts = np.zeros((len(TERM_TYPES), len(HEAD_TYPES)))
                for t, h in chunk:
                    counts[TERM_IDX[t], HEAD_IDX[h]] += 1
                null_prop[fi_local] = normalize_to_proportions(counts).flatten()

            # PCA project into existing space
            null_centered = null_prop - prop_matrix.mean(axis=0)
            if length_confound_significant:
                null_centered = null_prop - corrected_prop.mean(axis=0)
            # Project into PCA space
            n_pcs = pca_for_downstream.shape[1]
            null_pca = null_centered @ Vt[:n_pcs].T if not length_confound_significant \
                       else null_centered @ Vt_c[:eff_rank_c].T
            null_dists = euclidean_matrix(null_pca)
            null_vars.append(float(np.var(null_dists[triu])))

        var_p = (np.sum(np.array(null_vars) >= real_dist_var) + 1) / (N_PERMS + 1)
        section_significant = var_p < 0.05
        if section_significant:
            any_section_significant = True

        t3_results['sections'][section] = {
            'n_folios': n_sec,
            'folios': sec_folios,
            'real_distance_variance': real_dist_var,
            'null_variance_p95': float(np.percentile(null_vars, 95)),
            'p_value': float(var_p),
            'significant': bool(section_significant)
        }
        print(f"  Section {section}: {n_sec} folios, dist_var={real_dist_var:.6f}, "
              f"p={var_p:.4f}, sig={section_significant}")

    # REGIME confound test
    regime_labels = np.array([folio_regime.get(f, 'UNKNOWN') for f in valid_folios])

    for section in unique_sections:
        sec_idx = [i for i, s in enumerate(section_assignments) if s == section]
        if len(sec_idx) < 3:
            continue

        sec_regimes = regime_labels[sec_idx]
        unique_regimes_in_sec = set(sec_regimes)

        if len(unique_regimes_in_sec) < 2:
            t3_results['regime_confound'][section] = {
                'n_regimes': len(unique_regimes_in_sec),
                'skipped': True,
                'reason': 'only one REGIME in section'
            }
            continue

        # Mean within-REGIME distance vs across-REGIME within section
        sec_dists = pca_dist[np.ix_(sec_idx, sec_idx)]
        within_regime = []
        across_regime = []
        for i in range(len(sec_idx)):
            for j in range(i + 1, len(sec_idx)):
                if sec_regimes[i] == sec_regimes[j]:
                    within_regime.append(sec_dists[i, j])
                else:
                    across_regime.append(sec_dists[i, j])

        if within_regime and across_regime:
            mean_within = float(np.mean(within_regime))
            mean_across = float(np.mean(across_regime))
            regime_ratio = mean_within / mean_across if mean_across > 0 else 1.0

            t3_results['regime_confound'][section] = {
                'n_regimes': len(unique_regimes_in_sec),
                'mean_within_regime_dist': mean_within,
                'mean_across_regime_dist': mean_across,
                'ratio': float(regime_ratio),
                'regime_explains': bool(regime_ratio < 0.8)
            }
        else:
            t3_results['regime_confound'][section] = {
                'n_regimes': len(unique_regimes_in_sec),
                'skipped': True,
                'reason': 'insufficient within/across pairs'
            }

    # Overall REGIME confound: does REGIME explain the within-section signal?
    regime_explanations = [v.get('regime_explains', False)
                           for v in t3_results['regime_confound'].values()
                           if not v.get('skipped', False)]
    regime_fully_explains = all(regime_explanations) if regime_explanations else False
    t3_results['regime_fully_explains'] = regime_fully_explains

    # C1570 criterion verdict
    if any_section_significant and not regime_fully_explains:
        t3_results['c1570_criterion_met'] = True
        t3_results['c1570_verdict'] = 'C1570_EXTENDED'
    elif any_section_significant and regime_fully_explains:
        t3_results['c1570_criterion_met'] = False
        t3_results['c1570_verdict'] = 'REGIME_MEDIATED'
    else:
        t3_results['c1570_criterion_met'] = False
        t3_results['c1570_verdict'] = 'SECTION_ONLY'

    results['T3'] = t3_results
    print(f"  Section structure real: {t3_results['section_structure_real']} (p={section_p:.4f})")
    print(f"  Any section significant: {any_section_significant}")
    print(f"  REGIME fully explains: {regime_fully_explains}")
    print(f"  C1570 verdict: {t3_results['c1570_verdict']}")

    # ── T4: Apparatus Manifold Correlation ─────────────────────────────
    print("T4: Apparatus manifold correlation...")

    # Load apparatus features
    apparatus_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                   'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS', 'results',
                                   't0_feature_matrix_assembly.json')
    with open(apparatus_path) as f:
        apparatus_data = json.load(f)

    apparatus_folios = apparatus_data['folios']
    apparatus_raw = np.array(apparatus_data['space_A']['raw'])  # 76 × 11
    apparatus_folio_map = {f: i for i, f in enumerate(apparatus_folios)}

    # Find overlapping folios
    overlap_folios = [f for f in valid_folios if f in apparatus_folio_map]
    overlap_routing_idx = [valid_folios.index(f) for f in overlap_folios]
    overlap_apparatus_idx = [apparatus_folio_map[f] for f in overlap_folios]

    print(f"  Overlapping folios: {len(overlap_folios)}")

    if len(overlap_folios) >= 10:
        # Build distance matrices for overlapping folios
        routing_jsd_overlap = jsd_for_downstream[np.ix_(overlap_routing_idx, overlap_routing_idx)]
        apparatus_overlap = apparatus_raw[overlap_apparatus_idx]
        apparatus_dist = euclidean_matrix(apparatus_overlap)

        # Mantel test
        mantel_r, mantel_p, mantel_null_mean, mantel_null_std = mantel_test(
            routing_jsd_overlap, apparatus_dist)

        # Section distance matrix for partial Mantel
        sec_dist = section_distance_matrix(overlap_folios, folio_section)

        # Partial Mantel (section-controlled)
        partial_r, partial_p = partial_mantel(routing_jsd_overlap, apparatus_dist, [sec_dist])

        results['T4'] = {
            'n_overlap_folios': len(overlap_folios),
            'mantel_r': mantel_r,
            'mantel_p': mantel_p,
            'mantel_null_mean': mantel_null_mean,
            'mantel_null_std': mantel_null_std,
            'partial_mantel_r': partial_r,
            'partial_mantel_p': partial_p,
            'apparatus_correlated': bool(mantel_p < 0.05 and partial_p < 0.05),
            'section_mediated_only': bool(mantel_p < 0.05 and partial_p >= 0.05)
        }
        print(f"  Mantel r={mantel_r:.4f}, p={mantel_p:.4f}")
        print(f"  Partial Mantel r={partial_r:.4f}, p={partial_p:.4f}")
    else:
        results['T4'] = {
            'n_overlap_folios': len(overlap_folios),
            'skipped': True,
            'reason': 'fewer than 10 overlapping folios'
        }

    # ── T5: Accent PC Correlation ──────────────────────────────────────
    print("T5: Accent PC correlation...")

    accent_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                'FOLIO_ACCENT_VECTOR', 'results',
                                'folio_accent_vector.json')
    with open(accent_path) as f:
        accent_data = json.load(f)

    accent_scores = accent_data['T1_pca']['folio_scores']

    # Find overlapping folios
    accent_overlap = [f for f in valid_folios if f in accent_scores]
    accent_routing_idx = [valid_folios.index(f) for f in accent_overlap]

    print(f"  Accent overlap folios: {len(accent_overlap)}")

    if len(accent_overlap) >= 10:
        n_routing_pcs = pca_for_downstream.shape[1]
        routing_pcs_overlap = pca_for_downstream[accent_routing_idx]
        accent_pcs_overlap = np.array([
            [accent_scores[f]['PC1'], accent_scores[f]['PC2'], accent_scores[f]['PC3']]
            for f in accent_overlap
        ])

        # Spearman correlations: routing PCs × accent PCs
        n_r = routing_pcs_overlap.shape[1]
        n_a = accent_pcs_overlap.shape[1]
        correlations = []
        p_values_raw = []
        for ri in range(n_r):
            for ai in range(n_a):
                rho, p = spearmanr(routing_pcs_overlap[:, ri], accent_pcs_overlap[:, ai])
                correlations.append({
                    'routing_pc': f'rPC{ri+1}',
                    'accent_pc': f'aPC{ai+1}',
                    'spearman_rho': float(rho),
                    'p_value': float(p)
                })
                p_values_raw.append(p)

        # FDR correction
        q_values = fdr_correction(p_values_raw)
        for i, corr in enumerate(correlations):
            corr['q_value'] = float(q_values[i])
            corr['significant_fdr'] = bool(q_values[i] < 0.05)

        n_significant = sum(1 for c in correlations if c['significant_fdr'])

        results['T5'] = {
            'n_overlap_folios': len(accent_overlap),
            'n_routing_pcs': n_r,
            'n_accent_pcs': n_a,
            'correlations': correlations,
            'n_significant_fdr': n_significant,
            'total_tests': len(correlations)
        }
        print(f"  {n_significant}/{len(correlations)} significant after FDR correction")
    else:
        results['T5'] = {
            'n_overlap_folios': len(accent_overlap),
            'skipped': True,
            'reason': 'fewer than 10 overlapping folios'
        }

    # ── Decision Logic ─────────────────────────────────────────────────
    print("\nDecision logic...")

    verdict_components = {}

    # T2 decision
    if folio_signal_exists:
        verdict_components['T2'] = 'FOLIO_SIGNAL_EXISTS'
    else:
        verdict_components['T2'] = 'ROUTING_HOMOGENEOUS'

    # T3 decision
    verdict_components['T3'] = t3_results['c1570_verdict']

    # T4 decision
    if 'mantel_r' in results.get('T4', {}):
        t4 = results['T4']
        if t4['apparatus_correlated']:
            verdict_components['T4'] = 'APPARATUS_CORRELATED'
        elif t4['section_mediated_only']:
            verdict_components['T4'] = 'SECTION_MEDIATED_CORRELATION'
        else:
            verdict_components['T4'] = 'ROUTING_INDEPENDENT'
    else:
        verdict_components['T4'] = 'INSUFFICIENT_DATA'

    # Special case: T3 fails but T4 partial Mantel succeeds
    if (verdict_components['T3'] == 'SECTION_ONLY' and
        verdict_components['T4'] == 'APPARATUS_CORRELATED'):
        verdict_components['special'] = 'CROSS_SECTION_APPARATUS_LINK'

    # Final verdict
    if verdict_components['T2'] == 'ROUTING_HOMOGENEOUS':
        final_verdict = 'ROUTING_HOMOGENEOUS'
    elif verdict_components['T3'] == 'SECTION_ONLY':
        if verdict_components['T4'] == 'APPARATUS_CORRELATED':
            final_verdict = 'SECTION_ONLY_APPARATUS_LINKED'
        else:
            final_verdict = 'SECTION_ONLY'
    elif verdict_components['T3'] == 'REGIME_MEDIATED':
        final_verdict = 'REGIME_MEDIATED'
    elif verdict_components['T3'] == 'C1570_EXTENDED':
        if verdict_components['T4'] == 'APPARATUS_CORRELATED':
            final_verdict = 'FOLIO_FINGERPRINT_APPARATUS_CORRELATED'
        else:
            final_verdict = 'FOLIO_FINGERPRINT_INDEPENDENT'
    else:
        final_verdict = 'INDETERMINATE'

    results['verdict'] = {
        'components': verdict_components,
        'final': final_verdict,
        'c1570_criterion_1_met': t3_results['c1570_criterion_met'],
        'folio_signal_exists': folio_signal_exists
    }

    elapsed = time.time() - t_start
    results['_metadata'] = {
        'phase': 593,
        'name': 'TERMINAL_ROUTING_FOLIO_FINGERPRINT',
        'runtime_seconds': round(elapsed, 1),
        'n_permutations': N_PERMS,
        'min_transitions': MIN_TRANSITIONS,
        'seed': SEED,
        'n_valid_folios': len(valid_folios)
    }

    print(f"\n{'='*60}")
    print(f"FINAL VERDICT: {final_verdict}")
    print(f"  T2 (folio signal): {verdict_components['T2']}")
    print(f"  T3 (C1570 criterion): {verdict_components['T3']}")
    print(f"  T4 (apparatus): {verdict_components['T4']}")
    print(f"  C1570 criterion #1 met: {t3_results['c1570_criterion_met']}")
    print(f"  Runtime: {elapsed:.1f}s")

    # Write results
    out_path = os.path.join(RESULTS_DIR, 'terminal_routing_fingerprint_results.json')
    with open(out_path, 'w') as f:
        json.dump(convert_numpy(results), f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
