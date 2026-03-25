"""
Phase 624: PARAGRAPH_STRUCTURAL_ISOMORPHISM -- Shared utilities.

Provides arc-signature extraction, paragraph feature engineering,
clustering utilities (Ward, k-means, PCA, gap statistic), and
section residualization for paragraph-level structural analysis.

Dependencies: Phase 623 shared.py (build_corpus, constants).
"""

import math
import random
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional, Tuple, Any

import sys
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

# ============================================================
# Imports from Phase 623 shared.py
# ============================================================
from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus,
    CATEGORIES, HEAD_SET, TERM_SET,
    LOCKED_TERMS, CHANNELED_TERMS, DIFFUSE_TERMS,
    MODE_A_SUFFIXES, MODE_B_SUFFIXES,
    terminal_opacity, terminal_opacity_tier,
    suffix_mode, round_floats,
)

# ============================================================
# Constants
# ============================================================

PROJECT_ROOT = _PROJECT_ROOT
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'PARAGRAPH_STRUCTURAL_ISOMORPHISM' / 'results'

MIN_BODY_LINES = 6
MIN_BODY_LINES_SHORT = 4

RNG = random.Random(624)
N_PERM = 200

ARC_FEATURE_NAMES = [
    'log_ke_ratio', 'h_rate', 'headless_rate', 'mode_a_frac',
    'mean_opacity', 'cat_entropy', 'mean_line_length', 'm_terminal_rate', 'dark_frac'
]
BIN_NAMES = ['OPEN', 'INTERIOR', 'CLOSE']

# Opacity tier name -> numeric value mapping
_OPACITY_NUMERIC = {
    'LOCKED': 1.0,
    'CHANNELED': 0.5,
    'DIFFUSE': 0.0,
    'BARE': 0.0,
}


# ============================================================
# Clustering utilities (from Phase 573 t3_two_layer_clustering.py)
# ============================================================

def euclidean_dist(a, b):
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def z_normalize(vectors):
    """Z-score normalize columns. Returns (normalized, means, stds)."""
    if not vectors:
        return [], [], []
    n = len(vectors)
    d = len(vectors[0])
    means = [sum(v[j] for v in vectors) / n for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((v[j] - means[j]) ** 2 for v in vectors) / n
        stds.append(math.sqrt(var) if var > 1e-10 else 1.0)
    normed = [[(v[j] - means[j]) / stds[j] for j in range(d)] for v in vectors]
    return normed, means, stds


def ward_linkage(vectors):
    """Ward's minimum variance hierarchical clustering.
    Returns list of (i, j, distance, size) merge steps.
    """
    n = len(vectors)
    cluster_centroids = {i: list(vectors[i]) for i in range(n)}
    cluster_sizes = {i: 1 for i in range(n)}
    active = set(range(n))
    merges = []
    next_id = n
    d = len(vectors[0]) if vectors else 0

    for _ in range(n - 1):
        if len(active) < 2:
            break

        best_cost = float('inf')
        best_pair = None
        active_list = sorted(active)

        for idx_i in range(len(active_list)):
            ci = active_list[idx_i]
            for idx_j in range(idx_i + 1, len(active_list)):
                cj = active_list[idx_j]
                ni, nj = cluster_sizes[ci], cluster_sizes[cj]
                d2 = sum((cluster_centroids[ci][k] - cluster_centroids[cj][k]) ** 2
                         for k in range(d))
                cost = (ni * nj) / (ni + nj) * d2
                if cost < best_cost:
                    best_cost = cost
                    best_pair = (ci, cj)

        ci, cj = best_pair
        ni, nj = cluster_sizes[ci], cluster_sizes[cj]
        n_new = ni + nj

        new_centroid = [(ni * cluster_centroids[ci][k] + nj * cluster_centroids[cj][k]) / n_new
                        for k in range(d)]

        merges.append((ci, cj, math.sqrt(best_cost), n_new))

        cluster_centroids[next_id] = new_centroid
        cluster_sizes[next_id] = n_new

        active.discard(ci)
        active.discard(cj)
        active.add(next_id)
        next_id += 1

    return merges


def cut_dendrogram(merges, n_items, k):
    """Cut dendrogram at k clusters. Returns list of cluster labels."""
    if k >= n_items:
        return list(range(n_items))

    parent = {}
    next_id = n_items

    n_merges_needed = n_items - k
    for step, (ci, cj, dist, size) in enumerate(merges):
        if step >= n_merges_needed:
            break
        parent[ci] = next_id
        parent[cj] = next_id
        next_id += 1

    def find_root(node):
        while node in parent:
            node = parent[node]
        return node

    roots = set()
    labels = []
    for i in range(n_items):
        r = find_root(i)
        roots.add(r)
        labels.append(r)

    root_to_label = {r: idx for idx, r in enumerate(sorted(roots))}
    return [root_to_label[find_root(i)] for i in range(n_items)]


def silhouette_score(vectors, labels):
    """Compute mean silhouette score."""
    n = len(vectors)
    if n < 2:
        return 0.0
    k = max(labels) + 1
    if k < 2:
        return 0.0

    clusters = {}
    for i, l in enumerate(labels):
        clusters.setdefault(l, []).append(i)

    silhouettes = []
    for i in range(n):
        ci = labels[i]
        same = [j for j in clusters[ci] if j != i]
        if not same:
            silhouettes.append(0.0)
            continue
        a_i = sum(euclidean_dist(vectors[i], vectors[j]) for j in same) / len(same)

        b_i = float('inf')
        for cl, members in clusters.items():
            if cl == ci or not members:
                continue
            mean_d = sum(euclidean_dist(vectors[i], vectors[j]) for j in members) / len(members)
            if mean_d < b_i:
                b_i = mean_d

        if b_i == float('inf'):
            silhouettes.append(0.0)
        else:
            denom = max(a_i, b_i)
            silhouettes.append((b_i - a_i) / denom if denom > 0 else 0.0)

    return sum(silhouettes) / len(silhouettes)


def adjusted_rand_index(labels_a, labels_b):
    """Compute Adjusted Rand Index between two label vectors."""
    n = len(labels_a)
    if n < 2:
        return 0.0

    pairs_a = {}
    pairs_b = {}
    for i in range(n):
        pairs_a.setdefault(labels_a[i], set()).add(i)
        pairs_b.setdefault(labels_b[i], set()).add(i)

    sum_nij_choose2 = 0
    for ca in pairs_a.values():
        for cb in pairs_b.values():
            nij = len(ca & cb)
            sum_nij_choose2 += nij * (nij - 1) // 2

    sum_ai_choose2 = sum(len(c) * (len(c) - 1) // 2 for c in pairs_a.values())
    sum_bj_choose2 = sum(len(c) * (len(c) - 1) // 2 for c in pairs_b.values())
    n_choose2 = n * (n - 1) // 2

    expected = sum_ai_choose2 * sum_bj_choose2 / n_choose2 if n_choose2 > 0 else 0
    max_index = 0.5 * (sum_ai_choose2 + sum_bj_choose2)
    denom = max_index - expected

    if abs(denom) < 1e-10:
        return 0.0 if sum_nij_choose2 != expected else 1.0
    return (sum_nij_choose2 - expected) / denom


def nearest_centroid_classify(train_vecs, train_labels, test_vecs):
    """Simple nearest-centroid classifier."""
    labels_set = sorted(set(train_labels))
    centroids = {}
    for l in labels_set:
        members = [train_vecs[i] for i in range(len(train_vecs)) if train_labels[i] == l]
        d = len(train_vecs[0])
        centroids[l] = [sum(m[j] for m in members) / len(members) for j in range(d)]

    predictions = []
    for v in test_vecs:
        best_l = None
        best_d = float('inf')
        for l, c in centroids.items():
            d = euclidean_dist(v, c)
            if d < best_d:
                best_d = d
                best_l = l
        predictions.append(best_l)
    return predictions


# ============================================================
# New clustering utilities
# ============================================================

def cosine_similarity(a, b):
    """Cosine similarity: dot(a,b) / (||a|| * ||b||)."""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    norm_a = math.sqrt(sum(ai * ai for ai in a))
    norm_b = math.sqrt(sum(bi * bi for bi in b))
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 0.0
    return dot / (norm_a * norm_b)


def calinski_harabasz(vectors, labels):
    """
    Calinski-Harabasz index: ratio of between-cluster to within-cluster
    variance, scaled by (N-k)/(k-1).

    Higher is better.
    """
    n = len(vectors)
    if n < 2:
        return 0.0
    d = len(vectors[0])
    unique_labels = sorted(set(labels))
    k = len(unique_labels)
    if k < 2 or k >= n:
        return 0.0

    # Global centroid
    global_centroid = [sum(v[j] for v in vectors) / n for j in range(d)]

    # Per-cluster centroids and members
    cluster_members = {}
    for i, l in enumerate(labels):
        cluster_members.setdefault(l, []).append(i)

    cluster_centroids = {}
    for l, members in cluster_members.items():
        nl = len(members)
        cluster_centroids[l] = [sum(vectors[m][j] for m in members) / nl for j in range(d)]

    # Between-cluster dispersion (B_k)
    bg = 0.0
    for l, members in cluster_members.items():
        nl = len(members)
        c = cluster_centroids[l]
        bg += nl * sum((c[j] - global_centroid[j]) ** 2 for j in range(d))

    # Within-cluster dispersion (W_k)
    wg = 0.0
    for l, members in cluster_members.items():
        c = cluster_centroids[l]
        for m in members:
            wg += sum((vectors[m][j] - c[j]) ** 2 for j in range(d))

    if wg < 1e-12:
        return 0.0

    return (bg / (k - 1)) / (wg / (n - k))


def kmeans(vectors, k, max_iter=100, rng=None):
    """
    Lloyd's k-means algorithm.

    Initializes centroids by randomly selecting k distinct data points.
    Returns list of cluster labels.
    """
    if rng is None:
        rng = RNG
    n = len(vectors)
    if n == 0 or k <= 0:
        return []
    if k >= n:
        return list(range(n))

    d = len(vectors[0])

    # Random initialization: pick k distinct data points
    indices = list(range(n))
    rng_copy = random.Random(rng.random())  # avoid mutating shared RNG state unpredictably
    rng_copy.shuffle(indices)
    centroids = [list(vectors[indices[i]]) for i in range(k)]

    labels = [0] * n

    for _iteration in range(max_iter):
        # Assignment step: assign each point to nearest centroid
        new_labels = [0] * n
        for i in range(n):
            best_c = 0
            best_dist = float('inf')
            for c in range(k):
                dist = sum((vectors[i][j] - centroids[c][j]) ** 2 for j in range(d))
                if dist < best_dist:
                    best_dist = dist
                    best_c = c
            new_labels[i] = best_c

        # Check convergence
        if new_labels == labels and _iteration > 0:
            break
        labels = new_labels

        # Update step: recompute centroids
        for c in range(k):
            members = [i for i in range(n) if labels[i] == c]
            if not members:
                # Empty cluster: reinitialize to a random data point
                centroids[c] = list(vectors[rng_copy.randint(0, n - 1)])
            else:
                nm = len(members)
                centroids[c] = [sum(vectors[m][j] for m in members) / nm for j in range(d)]

    return labels


def _within_cluster_ss(vectors, labels):
    """Compute total within-cluster sum of squares (W)."""
    d = len(vectors[0]) if vectors else 0
    cluster_members = {}
    for i, l in enumerate(labels):
        cluster_members.setdefault(l, []).append(i)

    w = 0.0
    for l, members in cluster_members.items():
        nm = len(members)
        if nm == 0:
            continue
        centroid = [sum(vectors[m][j] for m in members) / nm for j in range(d)]
        for m in members:
            w += sum((vectors[m][j] - centroid[j]) ** 2 for j in range(d))
    return w


def gap_statistic(vectors, k_range, n_ref=200, rng=None):
    """
    Gap statistic for choosing optimal k.

    For each k in k_range:
      1. Cluster real data, compute log(W_real)
      2. Generate n_ref uniform reference datasets in the bounding box of data
      3. Cluster each reference, compute log(W_ref)
      4. gap[k] = mean(log(W_ref)) - log(W_real)

    Returns dict with:
      - 'gaps': {k: gap_value}
      - 'gap_se': {k: standard_error}
      - 'optimal_k': first k where gap[k] >= gap[k+1] - se[k+1]
    """
    if rng is None:
        rng = RNG

    n = len(vectors)
    if n == 0:
        return {'gaps': {}, 'gap_se': {}, 'optimal_k': None}

    d = len(vectors[0])

    # Bounding box of data
    mins = [min(v[j] for v in vectors) for j in range(d)]
    maxs = [max(v[j] for v in vectors) for j in range(d)]

    # Pre-generate reference datasets
    def generate_ref():
        return [[rng.uniform(mins[j], maxs[j]) for j in range(d)] for _ in range(n)]

    gaps = {}
    gap_se = {}

    for k in k_range:
        # Real data clustering
        real_labels = kmeans(vectors, k, rng=rng)
        w_real = _within_cluster_ss(vectors, real_labels)
        log_w_real = math.log(w_real) if w_real > 1e-12 else 0.0

        # Reference datasets
        log_w_refs = []
        for _ in range(n_ref):
            ref_data = generate_ref()
            ref_labels = kmeans(ref_data, k, rng=rng)
            w_ref = _within_cluster_ss(ref_data, ref_labels)
            log_w_refs.append(math.log(w_ref) if w_ref > 1e-12 else 0.0)

        mean_log_w_ref = sum(log_w_refs) / len(log_w_refs)
        sd_log_w_ref = math.sqrt(sum((x - mean_log_w_ref) ** 2 for x in log_w_refs) / len(log_w_refs))
        se = sd_log_w_ref * math.sqrt(1 + 1 / n_ref)

        gaps[k] = mean_log_w_ref - log_w_real
        gap_se[k] = se

    # Find optimal k: first k where gap[k] >= gap[k+1] - se[k+1]
    sorted_ks = sorted(k_range)
    optimal_k = sorted_ks[-1]  # default to largest k
    for i in range(len(sorted_ks) - 1):
        k_cur = sorted_ks[i]
        k_next = sorted_ks[i + 1]
        if gaps[k_cur] >= gaps[k_next] - gap_se[k_next]:
            optimal_k = k_cur
            break

    return {
        'gaps': gaps,
        'gap_se': gap_se,
        'optimal_k': optimal_k,
    }


def pca_reduce(vectors, variance_threshold=0.90):
    """
    PCA via power iteration with deflation.

    Centers data, computes covariance matrix, extracts eigenvectors via
    repeated power iteration, deflating the covariance after each component.

    Returns:
        (reduced_vectors, eigenvalues, eigenvectors, cumulative_variance, n_components)

    reduced_vectors: N x n_components list of lists
    eigenvalues: list of eigenvalues (descending)
    eigenvectors: list of eigenvector lists (each d-dimensional)
    cumulative_variance: list of cumulative variance ratios
    n_components: number of retained components
    """
    if not vectors:
        return [], [], [], [], 0

    n = len(vectors)
    d = len(vectors[0])

    # Center data
    means = [sum(v[j] for v in vectors) / n for j in range(d)]
    centered = [[v[j] - means[j] for j in range(d)] for v in vectors]

    # Compute covariance matrix (d x d)
    cov = [[0.0] * d for _ in range(d)]
    for i in range(d):
        for j in range(i, d):
            val = sum(centered[r][i] * centered[r][j] for r in range(n)) / n
            cov[i][j] = val
            cov[j][i] = val

    # Power iteration with deflation to extract eigenvalues/eigenvectors
    eigenvalues = []
    eigenvectors = []
    # Work on a copy of cov for deflation
    cov_work = [list(row) for row in cov]

    max_components = min(n, d)
    total_var = sum(cov[i][i] for i in range(d))
    if total_var < 1e-12:
        return [[0.0] * 1 for _ in range(n)], [0.0], [[0.0] * d], [0.0], 0

    for comp in range(max_components):
        # Power iteration to find dominant eigenvector of cov_work
        # Initialize with random vector (seeded for reproducibility)
        pi_rng = random.Random(624 + comp)
        vec = [pi_rng.gauss(0, 1) for _ in range(d)]
        # Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm < 1e-12:
            break
        vec = [x / norm for x in vec]

        for _iter in range(300):
            # Multiply: new_vec = cov_work @ vec
            new_vec = [0.0] * d
            for i in range(d):
                s = 0.0
                for j in range(d):
                    s += cov_work[i][j] * vec[j]
                new_vec[i] = s

            # Eigenvalue estimate
            eigenval = sum(new_vec[i] * vec[i] for i in range(d))

            # Normalize
            norm = math.sqrt(sum(x * x for x in new_vec))
            if norm < 1e-12:
                break
            new_vec = [x / norm for x in new_vec]

            # Check convergence (angle between old and new)
            dot = abs(sum(new_vec[i] * vec[i] for i in range(d)))
            vec = new_vec
            if dot > 1.0 - 1e-10:
                break

        # Final eigenvalue
        mv = [0.0] * d
        for i in range(d):
            for j in range(d):
                mv[i] += cov_work[i][j] * vec[j]
        eigenval = sum(mv[i] * vec[i] for i in range(d))

        if eigenval < 1e-12:
            break

        eigenvalues.append(eigenval)
        eigenvectors.append(list(vec))

        # Deflate: cov_work -= eigenval * vec @ vec^T
        for i in range(d):
            for j in range(d):
                cov_work[i][j] -= eigenval * vec[i] * vec[j]

        # Check cumulative variance
        cum_var = sum(eigenvalues) / total_var
        if cum_var >= variance_threshold:
            break

    n_components = len(eigenvalues)
    if n_components == 0:
        return [[0.0] for _ in range(n)], [0.0], [[0.0] * d], [0.0], 0

    # Cumulative variance ratios
    cumulative_variance = []
    running = 0.0
    for ev in eigenvalues:
        running += ev / total_var
        cumulative_variance.append(running)

    # Project centered data onto eigenvectors
    reduced = []
    for r in range(n):
        proj = []
        for c in range(n_components):
            val = sum(centered[r][j] * eigenvectors[c][j] for j in range(d))
            proj.append(val)
        reduced.append(proj)

    return reduced, eigenvalues, eigenvectors, cumulative_variance, n_components


# ============================================================
# Arc signature extraction helpers
# ============================================================

def _bin_features(tokens_in_bin, lines_in_bin):
    """
    Compute the 9 arc features for a set of tokens belonging to one bin.

    Args:
        tokens_in_bin: flat list of token dicts from lines in this bin
        lines_in_bin: list of line dicts (for computing mean_line_length)

    Returns:
        list of 9 floats in ARC_FEATURE_NAMES order
    """
    n_tok = len(tokens_in_bin)
    n_lines = len(lines_in_bin)

    if n_tok == 0:
        return [0.0] * 9

    # 1. log_ke_ratio: log((k_count+0.5) / (e_count+0.5))
    k_count = 0
    h_count = 0
    e_count = 0
    for t in tokens_in_bin:
        for c in t.get('kernels', []):
            if c == 'k':
                k_count += 1
            elif c == 'h':
                h_count += 1
            elif c == 'e':
                e_count += 1

    log_ke_ratio = math.log((k_count + 0.5) / (e_count + 0.5))

    # 2. h_rate: h_count / total_tokens
    h_rate = h_count / n_tok

    # 3. headless_rate
    headless_count = sum(1 for t in tokens_in_bin if t.get('is_headless', False))
    headless_rate = headless_count / n_tok

    # 4. mode_a_frac
    mode_a_count = sum(1 for t in tokens_in_bin if t.get('suffix_mode') == 'A')
    mode_a_frac = mode_a_count / n_tok

    # 5. mean_opacity: convert tier name to numeric
    opacity_sum = 0.0
    for t in tokens_in_bin:
        tier = t.get('terminal_opacity', 'BARE')
        opacity_sum += _OPACITY_NUMERIC.get(tier, 0.0)
    mean_opacity = opacity_sum / n_tok

    # 6. cat_entropy: Shannon entropy of 8-category distribution
    cat_counts = Counter()
    for t in tokens_in_bin:
        cat = t.get('category', 'UNKNOWN')
        if cat in CATEGORIES:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values())
    cat_entropy = 0.0
    if cat_total > 0:
        for cat in CATEGORIES:
            c = cat_counts.get(cat, 0)
            if c > 0:
                p = c / cat_total
                cat_entropy -= p * math.log2(p)

    # 7. mean_line_length: mean tokens per line in this bin
    if n_lines > 0:
        mean_line_length = sum(l['length'] for l in lines_in_bin) / n_lines
    else:
        mean_line_length = 0.0

    # 8. m_terminal_rate
    m_count = sum(1 for t in tokens_in_bin if t.get('term') == 'm')
    m_terminal_rate = m_count / n_tok

    # 9. dark_frac
    dark_count = sum(1 for t in tokens_in_bin if t.get('is_dark', False))
    dark_frac = dark_count / n_tok

    return [
        log_ke_ratio, h_rate, headless_rate, mode_a_frac,
        mean_opacity, cat_entropy, mean_line_length, m_terminal_rate, dark_frac
    ]


# ============================================================
# Arc signature extractors
# ============================================================

def extract_arc_signature(paragraph, min_body=6):
    """
    Extract a 27-dim arc vector from a paragraph using boundary-aware binning.

    Bins:
        OPEN:     first body line
        INTERIOR: middle body lines (line 2 through line N-1)
        CLOSE:    last body line

    Each bin yields 9 features (see ARC_FEATURE_NAMES).

    Args:
        paragraph: dict with 'header_lines', 'body_lines', 'id'
        min_body: minimum number of body lines required (default 6)

    Returns:
        (vector, metadata) where vector is a 27-element flat list,
        or (None, None) if paragraph has too few body lines.
    """
    body = paragraph.get('body_lines', [])
    if len(body) < min_body:
        return None, None

    # OPEN: first body line
    open_lines = [body[0]]
    open_tokens = body[0]['tokens']

    # INTERIOR: middle body lines
    interior_lines = body[1:-1]
    interior_tokens = []
    for line in interior_lines:
        interior_tokens.extend(line['tokens'])

    # CLOSE: last body line
    close_lines = [body[-1]]
    close_tokens = body[-1]['tokens']

    open_feats = _bin_features(open_tokens, open_lines)
    interior_feats = _bin_features(interior_tokens, interior_lines)
    close_feats = _bin_features(close_tokens, close_lines)

    vector = open_feats + interior_feats + close_feats

    metadata = {
        'paragraph_id': paragraph.get('id', '?'),
        'n_body_lines': len(body),
        'n_open_tokens': len(open_tokens),
        'n_interior_tokens': len(interior_tokens),
        'n_close_tokens': len(close_tokens),
        'n_interior_lines': len(interior_lines),
    }

    return vector, metadata


def extract_short_arc_signature(paragraph, min_body=4):
    """
    Extract an 18-dim arc vector for shorter paragraphs (4-5 body lines).

    Bins:
        BOUNDARY: first + last body line
        INTERIOR: middle body lines

    Each bin yields 9 features = 18-dim total.

    Args:
        paragraph: dict with 'header_lines', 'body_lines', 'id'
        min_body: minimum body lines required (default 4)

    Returns:
        (vector, metadata) or (None, None) if too few body lines.
    """
    body = paragraph.get('body_lines', [])
    if len(body) < min_body:
        return None, None

    # BOUNDARY: first + last body line
    boundary_lines = [body[0], body[-1]]
    boundary_tokens = body[0]['tokens'] + body[-1]['tokens']

    # INTERIOR: middle body lines
    interior_lines = body[1:-1]
    interior_tokens = []
    for line in interior_lines:
        interior_tokens.extend(line['tokens'])

    # Edge case: if only min_body=4 lines and interior is just 2 lines,
    # that's fine. If somehow interior is empty (e.g., 2-line body), bail.
    if not interior_tokens:
        return None, None

    boundary_feats = _bin_features(boundary_tokens, boundary_lines)
    interior_feats = _bin_features(interior_tokens, interior_lines)

    vector = boundary_feats + interior_feats

    metadata = {
        'paragraph_id': paragraph.get('id', '?'),
        'n_body_lines': len(body),
        'n_boundary_tokens': len(boundary_tokens),
        'n_interior_tokens': len(interior_tokens),
        'n_interior_lines': len(interior_lines),
    }

    return vector, metadata


# ============================================================
# Header feature extraction
# ============================================================

def extract_header_features(paragraph):
    """
    Extract header features from the first header line.

    Returns:
        (feature_vector, metadata) where feature_vector is a list of floats
        and metadata is a dict with string-valued extras.

    Feature vector (7 elements):
        [k_frac, h_frac, e_frac, o_frac, a_frac, ht_rate, n_tokens]

    Returns (None, None) if no header lines or no tokens.
    """
    headers = paragraph.get('header_lines', [])
    if not headers:
        return None, None

    tokens = headers[0].get('tokens', [])
    if not tokens:
        return None, None

    n = len(tokens)

    # HEAD distribution
    head_counts = Counter()
    for t in tokens:
        h = t.get('head', '')
        if h in HEAD_SET:
            head_counts[h] += 1

    k_frac = head_counts.get('k', 0) / n
    h_frac = head_counts.get('h', 0) / n  # Note: 'h' as HEAD, not kernel char
    e_frac = head_counts.get('e', 0) / n
    o_frac = head_counts.get('o', 0) / n
    a_frac = head_counts.get('a', 0) / n

    # HT rate
    ht_count = sum(1 for t in tokens if t.get('is_ht', False))
    ht_rate = ht_count / n

    # Gallows type: most common gallows-like prefix
    gallows_prefixes = {'k', 't', 'p', 'f'}
    prefix_counts = Counter()
    for t in tokens:
        pfx = t.get('prefix', '')
        if pfx and pfx in gallows_prefixes:
            prefix_counts[pfx] += 1

    if prefix_counts:
        gallows_type = prefix_counts.most_common(1)[0][0]
    else:
        gallows_type = 'none'

    # Prefix composition (all prefixes)
    all_prefix_counts = Counter()
    for t in tokens:
        pfx = t.get('prefix', '')
        if pfx:
            all_prefix_counts[pfx] += 1
    pfx_total = sum(all_prefix_counts.values())
    prefix_composition = {}
    if pfx_total > 0:
        prefix_composition = {p: c / pfx_total for p, c in all_prefix_counts.items()}

    feature_vector = [k_frac, h_frac, e_frac, o_frac, a_frac, ht_rate, float(n)]

    metadata = {
        'gallows_type': gallows_type,
        'prefix_composition': prefix_composition,
        'n_tokens': n,
        'paragraph_id': paragraph.get('id', '?'),
    }

    return feature_vector, metadata


# ============================================================
# Section residualization
# ============================================================

def section_residualize(vectors, section_labels):
    """
    Subtract per-section mean from each paragraph's vector.

    Args:
        vectors: list of lists (N x D)
        section_labels: list of section label strings (length N)

    Returns:
        (residualized_vectors, section_means)
        where section_means is a dict: section_label -> mean vector
    """
    if not vectors:
        return [], {}

    d = len(vectors[0])
    n = len(vectors)

    # Group indices by section
    section_indices = {}
    for i, s in enumerate(section_labels):
        section_indices.setdefault(s, []).append(i)

    # Compute per-section means
    section_means = {}
    for s, indices in section_indices.items():
        ns = len(indices)
        mean_vec = [sum(vectors[idx][j] for idx in indices) / ns for j in range(d)]
        section_means[s] = mean_vec

    # Subtract section mean from each vector
    residualized = []
    for i in range(n):
        s = section_labels[i]
        mean_vec = section_means[s]
        residualized.append([vectors[i][j] - mean_vec[j] for j in range(d)])

    return residualized, section_means
