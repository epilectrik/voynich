"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Script 6: Compositional Drift

Integration script: builds per-folio maturity vectors from Script 3 complexity
gradient features, Script 5 grammar temperature, and freshly computed lexical
metrics (Heaps beta, hapax fraction, dark/bridge rates, sister ratio,
within-domain parameterization entropy).

Tests for compositional ordering via:
  1. PCA on section-residualized, C1715-projected maturity matrix
  2. PC1 vs quire number (Spearman rho)
  3. Consecutive-folio atom JSD (Mantel test)
  4. 1000-permutation null for folio-to-quire assignment
"""
import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus, RNG, RESULTS_DIR, CHANNEL_NAMES,
    compute_folio_prefix_dists, extract_line_features, round_floats,
)

# ============================================================
# Constants
# ============================================================

N_PERM = 1000  # Permutation count for folio-level tests (spec: 1000)
SISTER_THRESHOLD = 3  # Shared with >= 3 OTHER folios to count as "sister"

# The 9 complexity gradient features (from Script 3)
GRADIENT_FEATURES = [
    'mod_density', 'mod_entropy', 'headless_rate', 'compound_rate',
    'mean_middle_len', 'atom_diversity', 'distinct_frames',
    'atom_variance', 'cond_entropy_rate',
]

# Grammar temperature sub-metrics (from Script 5)
TEMPERATURE_KEYS = [
    'T_composite', 'T_buffer', 'T_modifier', 'T_opacity',
    'T_pfx_head', 'T_pfx_mid',
]

# 18 atom characters used for JSD profiles
ATOM_CHARS = list('acdefghiklmnoprsty')


# ============================================================
# Statistical helpers
# ============================================================

def _rank(values):
    """Assign ranks to values (average rank for ties)."""
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and values[indexed[j + 1]] == values[indexed[j]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(x, y):
    """Compute Spearman rank correlation coefficient."""
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    rx = _rank(x)
    ry = _rank(y)
    n = len(x)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    std_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    std_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if std_x == 0 or std_y == 0:
        return 0.0
    return cov / (std_x * std_y)


def pearson_r(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 3 or len(y) != n:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    sx = math.sqrt(sum((x[i] - mx) ** 2 for i in range(n)))
    sy = math.sqrt(sum((y[i] - my) ** 2 for i in range(n)))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def _normal_cdf(z):
    """Approximation of standard normal CDF (Abramowitz & Stegun)."""
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1.0 if z >= 0 else -1.0
    z_abs = abs(z) / math.sqrt(2.0)
    t = 1.0 / (1.0 + p * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs)
    return 0.5 * (1.0 + sign * y)


def spearman_p_value(rho, n):
    """Approximate two-sided p-value for Spearman rho via t-distribution normal approx."""
    if n < 4:
        return 1.0
    t_stat = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho ** 2))
    return 2.0 * (1.0 - _normal_cdf(abs(t_stat)))


# ============================================================
# Per-folio complexity gradient slopes (recomputed from corpus)
# ============================================================

def _char_entropy(chars):
    """Shannon entropy of character distribution in bits."""
    if not chars:
        return 0.0
    counts = Counter(chars)
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    H = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            H -= p * math.log2(p)
    return H


def _token_middle_entropy(middle):
    """Shannon entropy of character distribution in a single MIDDLE."""
    return _char_entropy(list(middle)) if middle else 0.0


def _conditional_entropy(categories):
    """H(category_t | category_{t-1}) from consecutive pairs."""
    if len(categories) < 2:
        return 0.0
    pair_counts = Counter()
    prev_counts = Counter()
    for i in range(len(categories) - 1):
        pair_counts[(categories[i], categories[i + 1])] += 1
        prev_counts[categories[i]] += 1
    total = sum(pair_counts.values())
    if total == 0:
        return 0.0
    H = 0.0
    for (prev, curr), count in pair_counts.items():
        p_joint = count / total
        p_cond = count / prev_counts[prev]
        if p_cond > 0:
            H -= p_joint * math.log2(p_cond)
    return H


def compute_line_complexity(line_dict):
    """Compute 9 complexity features for a single body line (matches Script 3)."""
    tokens = line_dict['tokens']
    n = len(tokens)
    if n == 0:
        return {f: 0.0 for f in GRADIENT_FEATURES}

    mod_density = sum(len(t['mods']) for t in tokens) / n
    all_mod_chars = []
    for t in tokens:
        all_mod_chars.extend(list(t['mods']))
    mod_entropy = _char_entropy(all_mod_chars)
    headless_rate = sum(1 for t in tokens if t['is_headless']) / n
    compound_rate = sum(1 for t in tokens if t['is_compound']) / n
    mean_middle_len = sum(len(t['middle']) for t in tokens) / n
    all_middle_chars = set()
    for t in tokens:
        all_middle_chars.update(set(t['middle']))
    atom_diversity = len(all_middle_chars) / n
    frames = set()
    for t in tokens:
        frames.add((t['head'], t['term']))
    distinct_frames = len(frames) / n
    per_token_ent = [_token_middle_entropy(t['middle']) for t in tokens]
    if n >= 2:
        me = sum(per_token_ent) / n
        atom_variance = math.sqrt(sum((e - me) ** 2 for e in per_token_ent) / n)
    else:
        atom_variance = 0.0
    cond_entropy_rate = _conditional_entropy([t['category'] for t in tokens])

    return {
        'mod_density': mod_density, 'mod_entropy': mod_entropy,
        'headless_rate': headless_rate, 'compound_rate': compound_rate,
        'mean_middle_len': mean_middle_len, 'atom_diversity': atom_diversity,
        'distinct_frames': distinct_frames, 'atom_variance': atom_variance,
        'cond_entropy_rate': cond_entropy_rate,
    }


def compute_folio_gradient_slopes(corpus):
    """
    For each folio, compute mean complexity-gradient slope across its paragraphs.
    Returns: {folio: {feature: mean_slope, ...}, ...}
    """
    MIN_BODY = 5
    folio_slopes = {}

    for folio, fdata in sorted(corpus.items()):
        para_slopes = {f: [] for f in GRADIENT_FEATURES}
        for para in fdata['paragraphs']:
            body = para['body_lines']
            if len(body) < MIN_BODY:
                continue
            positions = [i / (len(body) - 1) for i in range(len(body))]
            feat_vecs = {f: [] for f in GRADIENT_FEATURES}
            for line_dict in body:
                feats = compute_line_complexity(line_dict)
                for f in GRADIENT_FEATURES:
                    feat_vecs[f].append(feats[f])
            for f in GRADIENT_FEATURES:
                rho = spearman_rho(feat_vecs[f], positions)
                para_slopes[f].append(rho)

        # Mean slope across qualifying paragraphs
        mean_slopes = {}
        for f in GRADIENT_FEATURES:
            vals = para_slopes[f]
            mean_slopes[f] = sum(vals) / len(vals) if vals else 0.0
        folio_slopes[folio] = mean_slopes

    return folio_slopes


# ============================================================
# Freshly computed per-folio lexical metrics
# ============================================================

def compute_heaps_beta(words, rng):
    """
    Compute Heaps' beta via log-log regression of type-token curve.
    Returns (transcript_beta, shuffled_beta, ratio).
    """
    if len(words) < 10:
        return (0.0, 0.0, 1.0)

    def _fit_beta(word_seq):
        """Fit log(types) = beta * log(tokens) + c via OLS on sampled points."""
        types_seen = set()
        # Sample ~20 points along the curve to avoid dominated regression
        n = len(word_seq)
        sample_points = sorted(set(
            [max(1, int(n * i / 20)) for i in range(1, 21)] + [n]
        ))
        log_tokens = []
        log_types = []
        for idx, w in enumerate(word_seq):
            types_seen.add(w)
            pos = idx + 1
            if pos in sample_points:
                if pos > 0 and len(types_seen) > 0:
                    log_tokens.append(math.log(pos))
                    log_types.append(math.log(len(types_seen)))

        if len(log_tokens) < 3:
            return 0.0
        # OLS: y = beta * x + c
        n_pts = len(log_tokens)
        sx = sum(log_tokens)
        sy = sum(log_types)
        sxx = sum(x * x for x in log_tokens)
        sxy = sum(x * y for x, y in zip(log_tokens, log_types))
        denom = n_pts * sxx - sx * sx
        if abs(denom) < 1e-12:
            return 0.0
        beta = (n_pts * sxy - sx * sy) / denom
        return beta

    # Transcript order
    beta_transcript = _fit_beta(words)

    # Shuffled order
    shuffled = list(words)
    rng.shuffle(shuffled)
    beta_shuffled = _fit_beta(shuffled)

    ratio = beta_transcript / beta_shuffled if abs(beta_shuffled) > 1e-12 else 1.0
    return (beta_transcript, beta_shuffled, ratio)


def compute_fresh_metrics(corpus, rng):
    """
    Compute per-folio fresh lexical metrics:
      - heaps_beta_transcript, heaps_beta_shuffled, heaps_ratio
      - hapax_fraction
      - dark_rate, bridge_rate
      - sister_ratio
      - parameterization_entropy (C1569)
    Returns: {folio: {metric: value, ...}, ...}
    """
    # Collect per-folio word lists and MIDDLE inventories
    folio_words = {}
    folio_middles = {}
    folio_tokens = {}

    for folio, fdata in sorted(corpus.items()):
        words = []
        middles = []
        tokens = []
        for para in fdata['paragraphs']:
            for line in para['header_lines'] + para['body_lines']:
                for t in line['tokens']:
                    words.append(t['word'])
                    middles.append(t['middle'])
                    tokens.append(t)
        folio_words[folio] = words
        folio_middles[folio] = middles
        folio_tokens[folio] = tokens

    # Pre-compute MIDDLE type sets per folio for sister ratio
    folio_middle_sets = {f: set(mids) for f, mids in folio_middles.items()}
    all_folios = sorted(folio_words.keys())

    # Count how many folios each MIDDLE type appears in
    middle_folio_count = Counter()
    for f, mset in folio_middle_sets.items():
        for m in mset:
            middle_folio_count[m] += 1

    results = {}
    for folio in all_folios:
        words = folio_words[folio]
        middles = folio_middles[folio]
        tokens = folio_tokens[folio]
        n_tok = len(tokens)

        # Heaps beta
        bt, bs, ratio = compute_heaps_beta(words, rng)

        # Hapax fraction
        word_counts = Counter(words)
        hapax = sum(1 for c in word_counts.values() if c == 1)
        hapax_frac = hapax / len(word_counts) if word_counts else 0.0

        # Dark pipeline rate
        dark_count = sum(1 for t in tokens if t['is_dark'])
        dark_rate = dark_count / n_tok if n_tok > 0 else 0.0

        # Bridge rate
        bridge_count = sum(1 for t in tokens if t['is_bridge'])
        bridge_rate = bridge_count / n_tok if n_tok > 0 else 0.0

        # Sister ratio: fraction of folio MIDDLE types shared with >= SISTER_THRESHOLD other folios
        mset = folio_middle_sets[folio]
        if mset:
            # A MIDDLE is "sister" if it appears in (count - 1) >= SISTER_THRESHOLD other folios
            # (subtract 1 for the folio itself)
            sister_count = sum(
                1 for m in mset
                if (middle_folio_count[m] - 1) >= SISTER_THRESHOLD
            )
            sister_ratio = sister_count / len(mset)
        else:
            sister_ratio = 0.0

        # Within-domain parameterization entropy (C1569)
        # Entropy of continuous feature distribution within the folio
        # Use the 18-channel features aggregated per folio
        section = corpus[folio]['section']
        param_entropy = _compute_parameterization_entropy(tokens)

        results[folio] = {
            'heaps_beta_transcript': bt,
            'heaps_beta_shuffled': bs,
            'heaps_ratio': ratio,
            'hapax_fraction': hapax_frac,
            'dark_rate': dark_rate,
            'bridge_rate': bridge_rate,
            'sister_ratio': sister_ratio,
            'param_entropy': param_entropy,
        }

    return results


def _compute_parameterization_entropy(tokens):
    """
    Within-domain parameterization entropy (C1569):
    entropy of the distribution of continuous features (prefix, suffix_mode,
    kernel type, terminal type) within a folio's token population.

    Uses Shannon entropy over the joint distribution of
    (prefix, suffix_mode, terminal_opacity) tuples.
    """
    if not tokens:
        return 0.0
    tuples = []
    for t in tokens:
        tuples.append((t['prefix'], t['suffix_mode'], t['terminal_opacity']))
    counts = Counter(tuples)
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    H = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            H -= p * math.log2(p)
    return H


# ============================================================
# Matrix construction and PCA
# ============================================================

def build_maturity_matrix(folios, gradient_slopes, temperature_data, fresh_metrics):
    """
    Build n_folios x D maturity matrix.

    Features:
      - 9 gradient slopes (from Script 3 recomputation)
      - 6 temperature values (from Script 5)
      - 8 fresh metrics
    Total: up to 23 features (drop zero-variance columns).
    """
    feature_names = []
    # Gradient slopes
    for f in GRADIENT_FEATURES:
        feature_names.append(f'grad_{f}')
    # Temperature
    for k in TEMPERATURE_KEYS:
        feature_names.append(k)
    # Fresh metrics
    fresh_keys = [
        'heaps_beta_transcript', 'heaps_beta_shuffled', 'heaps_ratio',
        'hapax_fraction', 'dark_rate', 'bridge_rate',
        'sister_ratio', 'param_entropy',
    ]
    for k in fresh_keys:
        feature_names.append(k)

    # Build matrix
    n = len(folios)
    D = len(feature_names)
    matrix = [[0.0] * D for _ in range(n)]

    for i, folio in enumerate(folios):
        col = 0
        # Gradient slopes
        slopes = gradient_slopes.get(folio, {})
        for f in GRADIENT_FEATURES:
            matrix[i][col] = slopes.get(f, 0.0)
            col += 1
        # Temperature
        tdata = temperature_data.get(folio, {})
        for k in TEMPERATURE_KEYS:
            matrix[i][col] = tdata.get(k, 1.0)
            col += 1
        # Fresh
        fdata = fresh_metrics.get(folio, {})
        for k in fresh_keys:
            matrix[i][col] = fdata.get(k, 0.0)
            col += 1

    # Remove zero-variance columns
    used_features = []
    used_cols = []
    for j in range(D):
        col_vals = [matrix[i][j] for i in range(n)]
        mean = sum(col_vals) / n
        var = sum((v - mean) ** 2 for v in col_vals) / n
        if var > 1e-12:
            used_features.append(feature_names[j])
            used_cols.append(j)

    filtered = [[matrix[i][j] for j in used_cols] for i in range(n)]
    return filtered, used_features


def section_residualize(matrix, folios, corpus):
    """Z-score each feature within section."""
    n = len(folios)
    D = len(matrix[0]) if n > 0 else 0

    # Group folios by section
    section_map = defaultdict(list)
    for i, f in enumerate(folios):
        sec = corpus[f]['section']
        section_map[sec].append(i)

    result = [row[:] for row in matrix]  # deep copy

    for j in range(D):
        for sec, indices in section_map.items():
            vals = [matrix[i][j] for i in indices]
            n_s = len(vals)
            if n_s < 2:
                for i in indices:
                    result[i][j] = 0.0
                continue
            mean = sum(vals) / n_s
            std = math.sqrt(sum((v - mean) ** 2 for v in vals) / n_s)
            if std < 1e-12:
                for i in indices:
                    result[i][j] = 0.0
            else:
                for i in indices:
                    result[i][j] = (matrix[i][j] - mean) / std

    return result


def _build_c1715_features(folios, corpus):
    """
    Build the 5-feature matrix [prefix_entropy, k_frac, h_frac, e_frac, suffix_rate]
    per folio for C1715 projection.
    """
    n = len(folios)
    feat_matrix = [[0.0] * 5 for _ in range(n)]

    for i, folio in enumerate(folios):
        fdata = corpus[folio]
        all_tokens = []
        for para in fdata['paragraphs']:
            for line in para['header_lines'] + para['body_lines']:
                all_tokens.extend(line['tokens'])

        n_tok = len(all_tokens)
        if n_tok == 0:
            continue

        # prefix_entropy
        pfx_counts = Counter(t['prefix'] for t in all_tokens if t['prefix'])
        total_pfx = sum(pfx_counts.values())
        pfx_ent = 0.0
        if total_pfx > 0:
            for c in pfx_counts.values():
                p = c / total_pfx
                if p > 0:
                    pfx_ent -= p * math.log2(p)
        feat_matrix[i][0] = pfx_ent

        # k_frac, h_frac, e_frac
        k_c = sum(1 for t in all_tokens for c in t['kernels'] if c == 'k')
        h_c = sum(1 for t in all_tokens for c in t['kernels'] if c == 'h')
        e_c = sum(1 for t in all_tokens for c in t['kernels'] if c == 'e')
        khe = k_c + h_c + e_c
        feat_matrix[i][1] = k_c / khe if khe > 0 else 0.0
        feat_matrix[i][2] = h_c / khe if khe > 0 else 0.0
        feat_matrix[i][3] = e_c / khe if khe > 0 else 0.0

        # suffix_rate
        sfx_count = sum(1 for t in all_tokens if t['suffix'])
        feat_matrix[i][4] = sfx_count / n_tok

    return feat_matrix


def project_out_pcs(matrix, projection_matrix, n_pcs=2):
    """
    Project out the first n_pcs principal components of projection_matrix
    from matrix. Both are n x D_main and n x D_proj respectively.

    Steps:
      1. Z-score projection features
      2. Compute covariance/correlation matrix of projection features
      3. Eigendecompose to get top n_pcs PCs
      4. Compute folio scores on those PCs
      5. Regress out those scores from each column of matrix
    """
    n = len(matrix)
    D_proj = len(projection_matrix[0])
    D_main = len(matrix[0])

    # Z-score projection features
    proj_z = [[0.0] * D_proj for _ in range(n)]
    for j in range(D_proj):
        vals = [projection_matrix[i][j] for i in range(n)]
        mean = sum(vals) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in vals) / n)
        if std < 1e-12:
            for i in range(n):
                proj_z[i][j] = 0.0
        else:
            for i in range(n):
                proj_z[i][j] = (projection_matrix[i][j] - mean) / std

    # Correlation matrix (since z-scored, cov = corr)
    corr = [[0.0] * D_proj for _ in range(D_proj)]
    for a in range(D_proj):
        for b in range(D_proj):
            corr[a][b] = sum(proj_z[i][a] * proj_z[i][b] for i in range(n)) / n

    # Eigendecomposition via power iteration (sufficient for 5x5)
    eigvecs = []
    eigvals = []
    work_corr = [row[:] for row in corr]

    for _ in range(min(n_pcs, D_proj)):
        vec = [1.0 / math.sqrt(D_proj)] * D_proj
        for iteration in range(200):
            # Multiply
            new_vec = [0.0] * D_proj
            for a in range(D_proj):
                for b in range(D_proj):
                    new_vec[a] += work_corr[a][b] * vec[b]
            # Normalize
            norm = math.sqrt(sum(v * v for v in new_vec))
            if norm < 1e-15:
                break
            vec = [v / norm for v in new_vec]

        # Eigenvalue
        Av = [0.0] * D_proj
        for a in range(D_proj):
            for b in range(D_proj):
                Av[a] += work_corr[a][b] * vec[b]
        lam = sum(vec[a] * Av[a] for a in range(D_proj))

        eigvecs.append(vec)
        eigvals.append(lam)

        # Deflate
        for a in range(D_proj):
            for b in range(D_proj):
                work_corr[a][b] -= lam * vec[a] * vec[b]

    if not eigvecs:
        return matrix

    # Compute folio scores on each PC
    pc_scores = []  # list of [score_1, ..., score_n] per PC
    for vec in eigvecs:
        scores = []
        for i in range(n):
            s = sum(proj_z[i][j] * vec[j] for j in range(D_proj))
            scores.append(s)
        pc_scores.append(scores)

    # Regress out PC scores from each column of matrix
    residual = [row[:] for row in matrix]
    for j in range(D_main):
        y = [matrix[i][j] for i in range(n)]
        for pc_idx in range(len(pc_scores)):
            scores = pc_scores[pc_idx]
            # Simple OLS: beta = cov(y, s) / var(s)
            s_mean = sum(scores) / n
            y_mean = sum(y) / n
            cov_ys = sum((y[i] - y_mean) * (scores[i] - s_mean) for i in range(n))
            var_s = sum((scores[i] - s_mean) ** 2 for i in range(n))
            if var_s < 1e-12:
                continue
            beta = cov_ys / var_s
            y = [y[i] - beta * scores[i] for i in range(n)]
        for i in range(n):
            residual[i][j] = y[i]

    return residual


def pca_eigendecomposition(matrix):
    """
    PCA via eigendecomposition of the correlation matrix (z-scored features).
    Returns: eigenvalues (descending), eigenvectors, pc_scores (n x n_pcs).
    """
    n = len(matrix)
    D = len(matrix[0]) if n > 0 else 0
    if D == 0 or n < 3:
        return [], [], []

    # Z-score columns
    z_mat = [[0.0] * D for _ in range(n)]
    for j in range(D):
        vals = [matrix[i][j] for i in range(n)]
        mean = sum(vals) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in vals) / n)
        if std < 1e-12:
            for i in range(n):
                z_mat[i][j] = 0.0
        else:
            for i in range(n):
                z_mat[i][j] = (matrix[i][j] - mean) / std

    # Correlation matrix
    corr = [[0.0] * D for _ in range(D)]
    for a in range(D):
        for b in range(D):
            corr[a][b] = sum(z_mat[i][a] * z_mat[i][b] for i in range(n)) / n

    # Power iteration for top PCs (extract up to min(D, 10))
    n_extract = min(D, 10)
    eigvals = []
    eigvecs = []
    work = [row[:] for row in corr]

    for _ in range(n_extract):
        vec = [RNG.gauss(0, 1) for _ in range(D)]
        norm = math.sqrt(sum(v * v for v in vec))
        if norm < 1e-15:
            break
        vec = [v / norm for v in vec]

        for iteration in range(300):
            new_vec = [0.0] * D
            for a in range(D):
                for b in range(D):
                    new_vec[a] += work[a][b] * vec[b]
            norm = math.sqrt(sum(v * v for v in new_vec))
            if norm < 1e-15:
                break
            new_vec = [v / norm for v in new_vec]
            # Convergence check
            diff = sum((new_vec[a] - vec[a]) ** 2 for a in range(D))
            vec = new_vec
            if diff < 1e-12:
                break

        Av = [0.0] * D
        for a in range(D):
            for b in range(D):
                Av[a] += work[a][b] * vec[b]
        lam = sum(vec[a] * Av[a] for a in range(D))
        if lam < 1e-10:
            break

        eigvals.append(lam)
        eigvecs.append(vec)

        # Deflate
        for a in range(D):
            for b in range(D):
                work[a][b] -= lam * vec[a] * vec[b]

    # Compute PC scores
    total_var = sum(eigvals)
    explained = [lam / total_var if total_var > 0 else 0.0 for lam in eigvals]

    pc_scores = []
    for i in range(n):
        scores = []
        for vec in eigvecs:
            s = sum(z_mat[i][j] * vec[j] for j in range(D))
            scores.append(s)
        pc_scores.append(scores)

    return eigvals, explained, pc_scores


# ============================================================
# Consecutive-folio atom JSD (Mantel test)
# ============================================================

def build_atom_profiles(corpus, folios):
    """Build per-folio 18-atom frequency profiles."""
    profiles = {}
    for folio in folios:
        fdata = corpus[folio]
        atom_counts = Counter()
        total = 0
        for para in fdata['paragraphs']:
            for line in para['header_lines'] + para['body_lines']:
                for t in line['tokens']:
                    for c in t['middle']:
                        if c in ATOM_CHARS:
                            atom_counts[c] += 1
                            total += 1
        if total > 0:
            profiles[folio] = {a: atom_counts.get(a, 0) / total for a in ATOM_CHARS}
        else:
            profiles[folio] = {a: 1.0 / len(ATOM_CHARS) for a in ATOM_CHARS}
    return profiles


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions (dicts with same keys)."""
    keys = set(list(p.keys()) + list(q.keys()))
    m = {k: (p.get(k, 0.0) + q.get(k, 0.0)) / 2 for k in keys}
    d = 0.0
    for k in keys:
        pk = p.get(k, 0.0)
        qk = q.get(k, 0.0)
        mk = m[k]
        if pk > 0 and mk > 0:
            d += 0.5 * pk * math.log2(pk / mk)
        if qk > 0 and mk > 0:
            d += 0.5 * qk * math.log2(qk / mk)
    return d


def build_distance_matrices(folios, corpus, atom_profiles):
    """
    Build quire-distance and feature-distance matrices for Mantel test.
    Feature distance = JSD of 18-atom profiles.
    Quire distance = |quire_i - quire_j|.
    Returns: (quire_dists, feature_dists) as flat vectors (upper triangle).
    """
    n = len(folios)
    quire_dists = []
    feature_dists = []

    for i in range(n):
        for j in range(i + 1, n):
            qi = corpus[folios[i]]['quire']
            qj = corpus[folios[j]]['quire']
            quire_dists.append(abs(qi - qj))

            pi = atom_profiles[folios[i]]
            pj = atom_profiles[folios[j]]
            feature_dists.append(jsd(pi, pj))

    return quire_dists, feature_dists


def mantel_test(quire_dists, feature_dists, n_folios, rng, n_perm=N_PERM):
    """
    Mantel test: Pearson correlation between distance matrices,
    permuted by shuffling folio labels.
    """
    observed_r = pearson_r(quire_dists, feature_dists)

    # Build index mapping for permutation
    n = n_folios
    n_pairs = len(quire_dists)

    # Pre-compute upper-triangle index pairs
    pair_indices = []
    for i in range(n):
        for j in range(i + 1, n):
            pair_indices.append((i, j))

    # For permutation: we need the original quire values per folio
    # and then recompute the quire distance matrix under shuffled labels
    # More efficient: just permute folio indices and recompute quire dists

    # Extract quire values in folio order (we need these to rebuild dist matrix)
    # Actually, we need access to the original per-folio quire values
    # This function only has the flat distance vectors, so we reconstruct
    # quire-per-folio from the distance matrix structure.

    # Alternative approach: permute the feature_dists ordering (equivalent to
    # shuffling folio labels). This is the standard Mantel approach.
    null_rs = []
    indices = list(range(n))

    for _ in range(n_perm):
        rng.shuffle(indices)
        # Rebuild feature distance vector under permuted folio order
        perm_feature = []
        for i in range(n):
            for j in range(i + 1, n):
                # Map permuted indices to original pair index
                oi, oj = indices[i], indices[j]
                if oi < oj:
                    flat_idx = _upper_tri_idx(oi, oj, n)
                else:
                    flat_idx = _upper_tri_idx(oj, oi, n)
                perm_feature.append(feature_dists[flat_idx])
        null_r = pearson_r(quire_dists, perm_feature)
        null_rs.append(null_r)

    # p-value: fraction of null >= observed (if observed > 0) or <= observed (if < 0)
    if observed_r >= 0:
        p_value = sum(1 for r in null_rs if r >= observed_r) / n_perm
    else:
        p_value = sum(1 for r in null_rs if r <= observed_r) / n_perm

    return {
        'observed_r': observed_r,
        'p_value': p_value,
        'n_pairs': n_pairs,
    }


def _upper_tri_idx(i, j, n):
    """Convert (i, j) with i < j to flat upper-triangle index."""
    return i * n - i * (i + 1) // 2 + (j - i - 1)


# ============================================================
# Verdict logic
# ============================================================

def determine_verdict(pc1_quire_p, mantel_p):
    """
    COMPOSITIONAL_ORDERING_DETECTED: PC1 vs quire rho significant (p < 0.05)
    CONSECUTIVE_COHERENCE_ONLY: Mantel significant but PC1 not
    NO_COMPOSITIONAL_ORDERING: neither (consistent with C1399/C1400)
    """
    if pc1_quire_p < 0.05:
        return 'COMPOSITIONAL_ORDERING_DETECTED'
    elif mantel_p < 0.05:
        return 'CONSECUTIVE_COHERENCE_ONLY'
    else:
        return 'NO_COMPOSITIONAL_ORDERING'


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 623, Script 6: Compositional Drift")
    print("=" * 55)

    # ---- Step 1: Load corpus ----
    print("\n[1/8] Building corpus...")
    corpus = build_corpus()
    all_folios = sorted(corpus.keys())
    n_folios = len(all_folios)
    print(f"  {n_folios} folios")

    # ---- Step 2: Load Script 5 temperature data ----
    print("\n[2/8] Loading grammar temperature (Script 5)...")
    temp_path = RESULTS_DIR / 'grammar_temperature.json'
    with open(temp_path) as f:
        temp_data = json.load(f)
    per_folio_temp = temp_data.get('per_folio', {})
    print(f"  Loaded temperature for {len(per_folio_temp)} folios")

    # ---- Step 3: Recompute per-folio gradient slopes (Script 3 features) ----
    print("\n[3/8] Computing per-folio complexity gradient slopes...")
    gradient_slopes = compute_folio_gradient_slopes(corpus)
    n_with_slopes = sum(
        1 for f in all_folios
        if any(abs(gradient_slopes.get(f, {}).get(g, 0.0)) > 1e-12
               for g in GRADIENT_FEATURES)
    )
    print(f"  {n_with_slopes}/{n_folios} folios with non-zero gradient slopes")

    # ---- Step 4: Compute fresh metrics ----
    print("\n[4/8] Computing fresh lexical metrics (Heaps, hapax, dark, bridge, sister, entropy)...")
    fresh = compute_fresh_metrics(corpus, RNG)
    # Report means
    for key in ['heaps_beta_transcript', 'heaps_beta_shuffled', 'heaps_ratio',
                'hapax_fraction', 'dark_rate', 'bridge_rate', 'sister_ratio',
                'param_entropy']:
        vals = [fresh[f][key] for f in all_folios]
        mean = sum(vals) / len(vals)
        print(f"  {key}: mean={mean:.4f}")

    # ---- Step 5: Build maturity matrix ----
    print("\n[5/8] Building maturity matrix...")
    matrix, features_used = build_maturity_matrix(
        all_folios, gradient_slopes, per_folio_temp, fresh
    )
    D = len(features_used)
    print(f"  {n_folios} x {D} matrix ({D} features with variance)")
    print(f"  Features: {features_used}")

    # Section-residualize
    print("  Section-residualizing (z-score within section)...")
    residualized = section_residualize(matrix, all_folios, corpus)

    # Project out C1715 PCs
    print("  Projecting out C1715 PCs (PREFIX/kernel axis, suffix_rate/e_frac axis)...")
    c1715_features = _build_c1715_features(all_folios, corpus)
    projected = project_out_pcs(residualized, c1715_features, n_pcs=2)

    # ---- Step 6: PCA on residuals ----
    print("\n[6/8] PCA on projected residuals...")
    eigvals, explained, pc_scores = pca_eigendecomposition(projected)

    if eigvals:
        print(f"  Top 5 eigenvalues: {[round(e, 4) for e in eigvals[:5]]}")
        print(f"  Top 5 explained:   {[round(e, 4) for e in explained[:5]]}")
    else:
        print("  WARNING: PCA produced no eigenvalues.")

    # PC1 vs quire number
    quires = [corpus[f]['quire'] for f in all_folios]
    if pc_scores and len(pc_scores[0]) > 0:
        pc1 = [pc_scores[i][0] for i in range(n_folios)]
        pc1_rho = spearman_rho(pc1, quires)
        pc1_p = spearman_p_value(pc1_rho, n_folios)
    else:
        pc1_rho = 0.0
        pc1_p = 1.0

    print(f"  PC1 vs quire: rho={pc1_rho:.4f}, p={pc1_p:.6f}")

    # Permutation null for PC1 vs quire
    print(f"  Running {N_PERM} permutation null for PC1 vs quire...")
    null_rhos = []
    quires_copy = list(quires)
    for perm_i in range(N_PERM):
        RNG.shuffle(quires_copy)
        null_rho = spearman_rho(pc1 if pc_scores else [0.0] * n_folios, quires_copy)
        null_rhos.append(null_rho)

    perm_p = sum(1 for r in null_rhos if abs(r) >= abs(pc1_rho)) / N_PERM
    print(f"  Permutation p-value: {perm_p:.4f}")

    # ---- Step 7: Consecutive-folio atom JSD + Mantel test ----
    print("\n[7/8] Consecutive-folio atom JSD (Mantel test)...")
    atom_profiles = build_atom_profiles(corpus, all_folios)
    quire_dists, feature_dists = build_distance_matrices(
        all_folios, corpus, atom_profiles
    )
    mantel_result = mantel_test(
        quire_dists, feature_dists, n_folios, RNG, N_PERM
    )
    print(f"  Mantel observed r: {mantel_result['observed_r']:.4f}")
    print(f"  Mantel p-value:    {mantel_result['p_value']:.4f}")
    print(f"  N pairs:           {mantel_result['n_pairs']}")

    # ---- Step 8: Verdict ----
    print("\n[8/8] Determining verdict...")
    # Use permutation p for PC1 (more conservative than analytic)
    verdict_p = perm_p
    verdict = determine_verdict(verdict_p, mantel_result['p_value'])
    print(f"  VERDICT: {verdict}")

    # Heaps summary
    heaps_betas = {
        f: {
            'transcript': fresh[f]['heaps_beta_transcript'],
            'shuffled': fresh[f]['heaps_beta_shuffled'],
            'ratio': fresh[f]['heaps_ratio'],
        }
        for f in all_folios
    }
    mean_bt = sum(fresh[f]['heaps_beta_transcript'] for f in all_folios) / n_folios
    mean_bs = sum(fresh[f]['heaps_beta_shuffled'] for f in all_folios) / n_folios
    mean_ratio = sum(fresh[f]['heaps_ratio'] for f in all_folios) / n_folios

    # Predictions
    predictions = {
        'compositional_ordering': verdict == 'COMPOSITIONAL_ORDERING_DETECTED',
        'consecutive_coherence': verdict in (
            'COMPOSITIONAL_ORDERING_DETECTED', 'CONSECUTIVE_COHERENCE_ONLY'
        ),
        'section_dominates_maturity': verdict == 'NO_COMPOSITIONAL_ORDERING',
        'consistent_with_C1399': verdict == 'NO_COMPOSITIONAL_ORDERING',
        'heaps_transcript_gt_shuffled': mean_bt < mean_bs,
    }

    # ---- Assemble output ----
    output = {
        'phase': 623,
        'name': 'compositional_drift',
        'n_folios': n_folios,
        'features_used': features_used,
        'pca': {
            'eigenvalues': round_floats(eigvals[:10]),
            'explained_variance': round_floats(explained[:10]),
            'pc1_quire_rho': round(pc1_rho, 6),
            'pc1_quire_p': round(pc1_p, 6),
            'pc1_quire_perm_p': round(perm_p, 6),
        },
        'mantel': round_floats(mantel_result),
        'heaps': {
            'per_folio_betas': round_floats(heaps_betas),
            'mean_transcript_beta': round(mean_bt, 6),
            'mean_shuffled_beta': round(mean_bs, 6),
            'ratio': round(mean_ratio, 6),
        },
        'verdict': verdict,
        'predictions': round_floats(predictions),
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'compositional_drift.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
