"""Phase 595: Line Ordering Information Content

Tests how much total information line ordering carries within paragraphs,
across all measurable channels simultaneously, and whether Mode A/B persistence
(C1423: 2.89% CMI) is the only sequential signal or just one of several.

Features: HEAD profile (6), TERM profile (7), suffix mode (1), line length (1) = 15 dims.
"""

import sys, os, json, time
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import norm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ── Constants ──────────────────────────────────────────────────────────

HEAD_TYPES = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_TYPES = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
HEAD_IDX = {h: i for i, h in enumerate(HEAD_TYPES)}
TERM_IDX = {t: i for i, t in enumerate(TERM_TYPES)}

# Mode A/B atom partition (C1410)
MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}

GALLOWS = {'k', 't', 'p', 'f'}

N_SHUFFLES = 1000
SEED = 42
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

# Section assignments
SECTION_MAP = {
    'f1r': 'H', 'f1v': 'H', 'f2r': 'H', 'f2v': 'H', 'f3r': 'H', 'f3v': 'H',
    'f4r': 'H', 'f4v': 'H', 'f5r': 'H', 'f5v': 'H', 'f6r': 'H', 'f6v': 'H',
    'f7r': 'H', 'f7v': 'H', 'f8r': 'H', 'f8v': 'H', 'f9r': 'H', 'f9v': 'H',
    'f10r': 'H', 'f10v': 'H', 'f11r': 'H', 'f11v': 'H', 'f13r': 'H', 'f13v': 'H',
    'f14r': 'H', 'f14v': 'H', 'f15r': 'H', 'f15v': 'H', 'f16r': 'H', 'f16v': 'H',
    'f17r': 'H', 'f17v': 'H', 'f18r': 'H', 'f18v': 'H', 'f19r': 'H', 'f19v': 'H',
    'f20r': 'H', 'f20v': 'H', 'f22r': 'H', 'f22v': 'H', 'f23r': 'H', 'f23v': 'H',
    'f24r': 'H', 'f24v': 'H', 'f25r': 'H', 'f25v': 'H',
    'f27r': 'H', 'f27v': 'H', 'f29r': 'H', 'f29v': 'H',
    'f31r': 'H', 'f31v': 'H', 'f32r': 'H', 'f32v': 'H',
    'f33r': 'H', 'f33v': 'H', 'f34r': 'H', 'f34v': 'H',
    'f35r': 'H', 'f35v': 'H', 'f36r': 'H', 'f36v': 'H',
    'f38r': 'H', 'f38v': 'H', 'f39r': 'H', 'f39v': 'H',
    'f40r': 'H', 'f40v': 'H', 'f41r': 'H', 'f41v': 'H',
    'f47r': 'H', 'f47v': 'H', 'f48r': 'H', 'f48v': 'H',
    'f49r': 'H', 'f49v': 'H', 'f50r': 'H', 'f50v': 'H',
    'f65r': 'H', 'f65v': 'H', 'f66r': 'H', 'f66v': 'H',
    'f75r': 'B', 'f75v': 'B', 'f76r': 'B', 'f76v': 'B',
    'f77r': 'B', 'f77v': 'B', 'f78r': 'B', 'f78v': 'B',
    'f79r': 'B', 'f79v': 'B', 'f80r': 'B', 'f80v': 'B',
    'f81r': 'B', 'f81v': 'B', 'f82r': 'B', 'f82v': 'B',
    'f83r': 'B', 'f83v': 'B', 'f84r': 'B', 'f84v': 'B',
    'f86v3': 'S', 'f86v4': 'S',
    'f87r': 'B', 'f87v': 'B', 'f88r': 'B', 'f88v': 'B',
    'f89r1': 'B', 'f89r2': 'B', 'f89v1': 'B', 'f89v2': 'B',
    'f99r': 'S', 'f99v': 'S', 'f100r': 'S', 'f100v': 'S',
    'f101r1': 'S', 'f101v2': 'S', 'f102r1': 'S', 'f102r2': 'S',
    'f102v1': 'S', 'f102v2': 'S', 'f103r': 'C', 'f103v': 'C',
    'f104r': 'C', 'f104v': 'C', 'f105r': 'C', 'f105v': 'C',
    'f106r': 'C', 'f106v': 'C', 'f107r': 'C', 'f107v': 'C',
    'f108r': 'C', 'f108v': 'C', 'f111r': 'C', 'f111v': 'C',
    'f112r': 'C', 'f112v': 'C', 'f113r': 'C', 'f113v': 'C',
    'f114r': 'C', 'f114v': 'C', 'f115r': 'C', 'f116r': 'C',
}


# ── Helpers ────────────────────────────────────────────────────────────

def atomize_suffix(suffix):
    """Split suffix into atoms. Simple: single chars, except 'ee' and 'ii'."""
    if not suffix:
        return []
    atoms = []
    i = 0
    while i < len(suffix):
        if i + 1 < len(suffix) and suffix[i] == suffix[i+1] and suffix[i] in ('e', 'i'):
            atoms.append(suffix[i:i+2])
            i += 2
        else:
            atoms.append(suffix[i])
            i += 1
    return atoms


def get_line_mode(tokens_with_suffix):
    """Classify line as Mode A or B using atom partition (C1410)."""
    a_count = 0
    b_count = 0
    for suffix in tokens_with_suffix:
        if suffix:
            for atom in atomize_suffix(suffix):
                if atom in MODE_A_ATOMS:
                    a_count += 1
                elif atom in MODE_B_ATOMS:
                    b_count += 1
    if a_count + b_count == 0:
        return None
    return 'A' if a_count > b_count else 'B'


def build_line_features(line_tokens, morph):
    """Build 15-dim feature vector for a body line.

    Features: HEAD profile (6), TERM profile (7), suffix mode (1), line length (1).
    """
    head_counts = np.zeros(len(HEAD_TYPES))
    term_counts = np.zeros(len(TERM_TYPES))
    suffixes = []
    n_valid = 0

    for tok in line_tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            head, mods, term, frame = decompose_middle_hmt(m.middle)
            head = head if head else 'headless'
            if head in HEAD_IDX:
                head_counts[HEAD_IDX[head]] += 1
            if term in TERM_IDX:
                term_counts[TERM_IDX[term]] += 1
            n_valid += 1
        suffixes.append(m.suffix if m else None)

    if n_valid == 0:
        return None, None

    # Normalize to fractions
    head_frac = head_counts / n_valid
    term_frac = term_counts / n_valid

    # Mode
    mode = get_line_mode(suffixes)
    mode_val = 1.0 if mode == 'A' else 0.0 if mode == 'B' else 0.5

    # Line length
    line_len = float(len(line_tokens))

    # Concatenate: HEAD(6) + TERM(7) + mode(1) + length(1) = 15
    features = np.concatenate([head_frac, term_frac, [mode_val], [line_len]])
    return features, mode


def sequential_structure_score(feature_matrix):
    """Sum of squared consecutive differences: Sigma ||f_{i+1} - f_i||^2."""
    if len(feature_matrix) < 2:
        return 0.0
    diffs = np.diff(feature_matrix, axis=0)
    return float(np.sum(diffs ** 2))


def mi_from_contingency(table):
    """Compute mutual information in bits from a 2D contingency table."""
    table = np.asarray(table, dtype=float)
    total = table.sum()
    if total == 0:
        return 0.0
    p_joint = table / total
    p_row = table.sum(axis=1) / total
    p_col = table.sum(axis=0) / total
    mi = 0.0
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            if p_joint[i, j] > 0 and p_row[i] > 0 and p_col[j] > 0:
                mi += p_joint[i, j] * np.log2(p_joint[i, j] / (p_row[i] * p_col[j]))
    return mi


def entropy_from_counts(counts):
    """Shannon entropy in bits from a count array."""
    total = sum(counts.values()) if isinstance(counts, dict) else sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in (counts.values() if isinstance(counts, dict) else counts):
        if c > 0:
            p = c / total
            h -= p * np.log2(p)
    return h


# ── Data Assembly ──────────────────────────────────────────────────────

def assemble_paragraphs():
    """Load Currier B tokens, build paragraphs, compute per-line features."""
    tx = Transcript()
    morph = Morphology()

    # Group tokens by (folio, line)
    lines_dict = defaultdict(list)
    for t in tx.currier_b():
        w = t.word.strip()
        if not w:
            continue
        if t.placement.startswith('L'):
            continue
        lines_dict[(t.folio, t.line)].append(t)

    # Build folio -> sorted lines
    folio_lines = defaultdict(list)
    for (f, l), toks in sorted(lines_dict.items()):
        folio_lines[f].append((l, toks))

    # Build paragraphs using par_initial field
    all_paragraphs = []
    for f in sorted(folio_lines):
        curr_par = []
        for l, toks in folio_lines[f]:
            if toks[0].par_initial and curr_par:
                all_paragraphs.append(curr_par)
                curr_par = []
            curr_par.append((f, l, toks))
        if curr_par:
            all_paragraphs.append(curr_par)

    # Filter: gallows-initial, sufficient body lines
    selected = []
    for par in all_paragraphs:
        # Gallows-initial check
        first_word = par[0][2][0].word.replace('*', '').strip()
        if not first_word or first_word[0] not in GALLOWS:
            continue
        # Need >= 6 body lines (line 0 = header)
        if len(par) < 7:  # 1 header + 6 body
            continue
        selected.append(par)

    # Compute features per body line
    processed = []
    for par in selected:
        folio = par[0][0]
        section = SECTION_MAP.get(folio, '?')
        header_line = par[0]
        body_lines = par[1:]

        body_features = []
        body_modes = []
        for f, l, toks in body_lines:
            feat, mode = build_line_features(toks, morph)
            if feat is not None:
                body_features.append(feat)
                body_modes.append(mode)

        if len(body_features) < 6:
            continue

        feature_matrix = np.array(body_features)

        processed.append({
            'folio': folio,
            'section': section,
            'n_body_lines': len(body_features),
            'feature_matrix': feature_matrix,
            'modes': body_modes,
            'par_ordinal': len([p for p in processed if p['folio'] == folio]),
        })

    return processed


# ── T2: Total Ordering Information ─────────────────────────────────────

def compute_t2(paragraphs, rng):
    """Permutation test on sequential structure score."""
    results_per_para = []

    for par in paragraphs:
        fm = par['feature_matrix'].copy()
        n = len(fm)

        # Center within paragraph (subtract mean, no SD normalization)
        fm_centered = fm - fm.mean(axis=0)

        real_score = sequential_structure_score(fm_centered)

        # Shuffle null
        null_scores = []
        for _ in range(N_SHUFFLES):
            perm = rng.permutation(n)
            shuffled = fm_centered[perm]
            null_scores.append(sequential_structure_score(shuffled))

        null_scores = np.array(null_scores)
        null_mean = float(null_scores.mean())
        null_sd = float(null_scores.std())

        # Two-tailed p
        p_lower = float(np.mean(null_scores <= real_score))
        p_upper = float(np.mean(null_scores >= real_score))
        p_two = 2 * min(p_lower, p_upper)

        # Effect size
        effect = (real_score - null_mean) / null_sd if null_sd > 0 else 0.0

        # Z-score for Stouffer
        z = (real_score - null_mean) / null_sd if null_sd > 0 else 0.0

        results_per_para.append({
            'folio': par['folio'],
            'section': par['section'],
            'n_body': par['n_body_lines'],
            'real_score': round(real_score, 4),
            'null_mean': round(null_mean, 4),
            'null_sd': round(null_sd, 4),
            'effect_size': round(effect, 4),
            'p_two_tailed': round(p_two, 4),
            'z': round(z, 4),
        })

    # Aggregate
    zs = [r['z'] for r in results_per_para]
    n_para = len(zs)
    stouffer_z = sum(zs) / np.sqrt(n_para) if n_para > 0 else 0.0
    stouffer_p = 2 * (1 - norm.cdf(abs(stouffer_z)))
    n_sig = sum(1 for r in results_per_para if r['p_two_tailed'] < 0.05)
    mean_effect = float(np.mean([r['effect_size'] for r in results_per_para]))

    return {
        'n_paragraphs': n_para,
        'n_significant_p05': n_sig,
        'frac_significant': round(n_sig / n_para, 4) if n_para > 0 else 0,
        'mean_effect_size': round(mean_effect, 4),
        'stouffer_z': round(stouffer_z, 4),
        'stouffer_p': round(stouffer_p, 6),
        'significant': stouffer_p < 0.01,
        'per_paragraph': results_per_para,
    }


# ── T3: Mode-Residualized Ordering Information ─────────────────────────

def compute_t3(paragraphs, rng):
    """T2 after regressing out mode from ALL features."""
    # Collect all body lines across all paragraphs with their mode labels
    all_features = []
    all_modes = []
    for par in paragraphs:
        for i, mode in enumerate(par['modes']):
            if mode in ('A', 'B'):
                all_features.append(par['feature_matrix'][i])
                all_modes.append(1.0 if mode == 'A' else 0.0)

    all_features = np.array(all_features)
    all_modes = np.array(all_modes)

    # Compute mode-conditional means for each feature
    n_features = all_features.shape[1]
    mode_a_mean = all_features[all_modes == 1.0].mean(axis=0) if np.sum(all_modes == 1.0) > 0 else np.zeros(n_features)
    mode_b_mean = all_features[all_modes == 0.0].mean(axis=0) if np.sum(all_modes == 0.0) > 0 else np.zeros(n_features)
    mode_diff = mode_a_mean - mode_b_mean  # Used for analytic benchmark

    # Residualize: for each body line, subtract mode-predicted value
    residualized_paragraphs = []
    for par in paragraphs:
        fm = par['feature_matrix'].copy()
        for i, mode in enumerate(par['modes']):
            if mode == 'A':
                fm[i] -= mode_a_mean
                fm[i] += all_features.mean(axis=0)  # Re-add grand mean
            elif mode == 'B':
                fm[i] -= mode_b_mean
                fm[i] += all_features.mean(axis=0)
            # else: leave as-is (MIXED/None)
        residualized_paragraphs.append(fm)

    # Run T2-style permutation test on residualized features
    results_per_para = []
    for idx, par in enumerate(paragraphs):
        fm = residualized_paragraphs[idx]
        n = len(fm)

        # Center within paragraph
        fm_centered = fm - fm.mean(axis=0)
        real_score = sequential_structure_score(fm_centered)

        null_scores = []
        for _ in range(N_SHUFFLES):
            perm = rng.permutation(n)
            shuffled = fm_centered[perm]
            null_scores.append(sequential_structure_score(shuffled))

        null_scores = np.array(null_scores)
        null_mean = float(null_scores.mean())
        null_sd = float(null_scores.std())

        effect = (real_score - null_mean) / null_sd if null_sd > 0 else 0.0
        p_lower = float(np.mean(null_scores <= real_score))
        p_upper = float(np.mean(null_scores >= real_score))
        p_two = 2 * min(p_lower, p_upper)

        results_per_para.append({
            'folio': par['folio'],
            'section': par['section'],
            'effect_size': round(effect, 4),
            'p_two_tailed': round(p_two, 4),
            'z': round(effect, 4),
        })

    zs = [r['z'] for r in results_per_para]
    n_para = len(zs)
    stouffer_z = sum(zs) / np.sqrt(n_para) if n_para > 0 else 0.0
    stouffer_p = 2 * (1 - norm.cdf(abs(stouffer_z)))
    n_sig = sum(1 for r in results_per_para if r['p_two_tailed'] < 0.05)

    # Analytic mode benchmark: expected T2 score from mode persistence alone
    # With same-mode rate 0.606, consecutive pairs have prob 0.606 of same mode
    # and 0.394 of different mode. Expected squared diff = 0.394 * ||mode_diff||^2
    mode_diff_norm_sq = float(np.sum(mode_diff ** 2))
    # Per pair: E[||f_{i+1} - f_i||^2] from mode alone
    # Same mode: diff = 0 (both centered to same mode mean)
    # Different mode: diff = mode_diff, ||diff||^2 = mode_diff_norm_sq
    # But after centering within paragraph, it's more complex. Use empirical benchmark.

    return {
        'n_paragraphs': n_para,
        'n_significant_p05': n_sig,
        'frac_significant': round(n_sig / n_para, 4) if n_para > 0 else 0,
        'mean_effect_size': round(float(np.mean([r['effect_size'] for r in results_per_para])), 4),
        'stouffer_z': round(stouffer_z, 4),
        'stouffer_p': round(stouffer_p, 6),
        'significant': stouffer_p < 0.01,
        'mode_diff_norm_squared': round(mode_diff_norm_sq, 6),
    }


# ── T4: Positional Information Content ─────────────────────────────────

def compute_t4(paragraphs, rng):
    """Test whether body-line quintile positions carry distinctive content."""
    # Collect features by quintile
    quintile_features = {q: [] for q in range(5)}
    para_means = []

    for par in paragraphs:
        fm = par['feature_matrix']
        n = len(fm)
        para_mean = fm.mean(axis=0)
        para_means.append(para_mean)

        for i in range(n):
            frac_pos = i / (n - 1) if n > 1 else 0.5
            q = min(int(frac_pos * 5), 4)
            quintile_features[q].append(fm[i] - para_mean)

    # Observed: mean deviation per quintile
    obs_quintile_means = {}
    for q in range(5):
        if quintile_features[q]:
            obs_quintile_means[q] = np.mean(quintile_features[q], axis=0)
        else:
            obs_quintile_means[q] = np.zeros(15)

    # Observed: norm of mean deviation per quintile (scalar summary)
    obs_norms = {q: float(np.linalg.norm(obs_quintile_means[q])) for q in range(5)}

    # Shuffle null
    null_norms = {q: [] for q in range(5)}
    for _ in range(N_SHUFFLES):
        shuf_quintile_features = {q: [] for q in range(5)}
        for idx, par in enumerate(paragraphs):
            fm = par['feature_matrix']
            n = len(fm)
            perm = rng.permutation(n)
            shuffled = fm[perm]
            para_mean = para_means[idx]
            for i in range(n):
                frac_pos = i / (n - 1) if n > 1 else 0.5
                q = min(int(frac_pos * 5), 4)
                shuf_quintile_features[q].append(shuffled[i] - para_mean)

        for q in range(5):
            if shuf_quintile_features[q]:
                null_norms[q].append(float(np.linalg.norm(np.mean(shuf_quintile_features[q], axis=0))))
            else:
                null_norms[q].append(0.0)

    results = {}
    for q in range(5):
        nn = np.array(null_norms[q])
        p = float(np.mean(nn >= obs_norms[q]))
        results[str(q)] = {
            'obs_norm': round(obs_norms[q], 6),
            'null_mean': round(float(nn.mean()), 6),
            'null_sd': round(float(nn.std()), 6),
            'p_value': round(p, 4),
            'significant': p < 0.01,
            'n_lines': len(quintile_features[q]),
        }

    return results


# ── T5: Lag-1 Mutual Information Audit ─────────────────────────────────

def compute_t5(paragraphs, rng):
    """Per-channel lag-1 MI with within-paragraph shuffle control."""
    # Collect consecutive pairs for each channel
    mode_pairs = []  # (mode_n, mode_{n+1})
    head_pairs = []  # (dom_head_n, dom_head_{n+1})
    term_pairs = []  # (dom_term_n, dom_term_{n+1})
    length_pairs = []  # (len_bin_n, len_bin_{n+1})

    # Compute length quartiles from all body lines
    all_lengths = []
    for par in paragraphs:
        for i in range(par['n_body_lines']):
            all_lengths.append(par['feature_matrix'][i, -1])  # last feature = length
    length_quartiles = np.percentile(all_lengths, [25, 50, 75])

    def len_bin(length):
        if length <= length_quartiles[0]:
            return 0
        elif length <= length_quartiles[1]:
            return 1
        elif length <= length_quartiles[2]:
            return 2
        return 3

    # Build pairs from real ordering
    for par in paragraphs:
        fm = par['feature_matrix']
        modes = par['modes']
        n = len(modes)
        for i in range(n - 1):
            # Mode
            if modes[i] in ('A', 'B') and modes[i+1] in ('A', 'B'):
                mode_pairs.append((0 if modes[i] == 'A' else 1, 0 if modes[i+1] == 'A' else 1))
            # Dominant HEAD (argmax of first 6 features)
            h1 = int(np.argmax(fm[i, :6]))
            h2 = int(np.argmax(fm[i+1, :6]))
            head_pairs.append((h1, h2))
            # Dominant TERM (argmax of features 6:13)
            t1 = int(np.argmax(fm[i, 6:13]))
            t2 = int(np.argmax(fm[i+1, 6:13]))
            term_pairs.append((t1, t2))
            # Length bin
            lb1 = len_bin(fm[i, -1])
            lb2 = len_bin(fm[i+1, -1])
            length_pairs.append((lb1, lb2))

    def compute_channel_mi(pairs, n_states):
        table = np.zeros((n_states, n_states))
        for a, b in pairs:
            table[a, b] += 1
        return mi_from_contingency(table)

    # Observed MIs
    mi_mode = compute_channel_mi(mode_pairs, 2)
    mi_head = compute_channel_mi(head_pairs, 6)
    mi_term = compute_channel_mi(term_pairs, 7)
    mi_length = compute_channel_mi(length_pairs, 4)

    # Marginal entropies
    h_mode = entropy_from_counts(Counter(p[0] for p in mode_pairs))
    h_head = entropy_from_counts(Counter(p[0] for p in head_pairs))
    h_term = entropy_from_counts(Counter(p[0] for p in term_pairs))
    h_length = entropy_from_counts(Counter(p[0] for p in length_pairs))

    # Shuffle null for each channel
    def shuffle_mi(paragraphs_data, channel_extractor, n_states):
        null_mis = []
        for _ in range(N_SHUFFLES):
            pairs = []
            for par in paragraphs_data:
                n = par['n_body_lines']
                perm = rng.permutation(n)
                for i in range(n - 1):
                    a = channel_extractor(par, int(perm[i]))
                    b = channel_extractor(par, int(perm[i+1]))
                    if a is not None and b is not None:
                        pairs.append((a, b))
            null_mis.append(compute_channel_mi(pairs, n_states))
        return np.array(null_mis)

    def mode_extractor(par, idx):
        m = par['modes'][idx]
        if m == 'A': return 0
        if m == 'B': return 1
        return None

    def head_extractor(par, idx):
        return int(np.argmax(par['feature_matrix'][idx, :6]))

    def term_extractor(par, idx):
        return int(np.argmax(par['feature_matrix'][idx, 6:13]))

    def length_extractor(par, idx):
        return len_bin(par['feature_matrix'][idx, -1])

    null_mode = shuffle_mi(paragraphs, mode_extractor, 2)
    null_head = shuffle_mi(paragraphs, head_extractor, 6)
    null_term = shuffle_mi(paragraphs, term_extractor, 7)
    null_length = shuffle_mi(paragraphs, length_extractor, 4)

    def channel_result(name, obs_mi, null_mi, h_x):
        p = float(np.mean(null_mi >= obs_mi))
        return {
            'mi_bits': round(obs_mi, 6),
            'h_marginal': round(h_x, 4),
            'mi_fraction_of_h': round(obs_mi / h_x, 6) if h_x > 0 else 0.0,
            'null_mean': round(float(null_mi.mean()), 6),
            'null_sd': round(float(null_mi.std()), 6),
            'p_value': round(p, 4),
            'significant': p < 0.05,
        }

    results = {
        'suffix_mode': channel_result('suffix_mode', mi_mode, null_mode, h_mode),
        'dominant_HEAD': channel_result('dominant_HEAD', mi_head, null_head, h_head),
        'dominant_TERM': channel_result('dominant_TERM', mi_term, null_term, h_term),
        'line_length': channel_result('line_length', mi_length, null_length, h_length),
    }

    # Total significant MI
    total_sig_mi = sum(v['mi_bits'] for v in results.values() if v['significant'])
    results['total_significant_mi_bits'] = round(total_sig_mi, 6)

    return results


# ── T6: Per-Folio Effect Size ──────────────────────────────────────────

def compute_t6(paragraphs, rng):
    """Per-folio sequential structure score effect sizes."""
    # Group paragraphs by folio
    folio_paras = defaultdict(list)
    for par in paragraphs:
        folio_paras[par['folio']].append(par)

    results = {}
    for folio, pars in sorted(folio_paras.items()):
        # Compute folio-level sequential structure score
        # Concatenate all body lines in paragraph order
        all_lines = []
        for par in pars:
            fm = par['feature_matrix']
            para_mean = fm.mean(axis=0)
            all_lines.extend(fm - para_mean)

        if len(all_lines) < 10:
            continue

        all_lines = np.array(all_lines)
        real_score = sequential_structure_score(all_lines)

        # Shuffle body lines within each paragraph
        null_scores = []
        for _ in range(N_SHUFFLES):
            shuffled_lines = []
            for par in pars:
                fm = par['feature_matrix']
                para_mean = fm.mean(axis=0)
                perm = rng.permutation(len(fm))
                shuffled_lines.extend(fm[perm] - para_mean)
            shuffled_lines = np.array(shuffled_lines)
            null_scores.append(sequential_structure_score(shuffled_lines))

        null_scores = np.array(null_scores)
        null_mean = float(null_scores.mean())
        null_sd = float(null_scores.std())
        effect = (real_score - null_mean) / null_sd if null_sd > 0 else 0.0

        section = SECTION_MAP.get(folio, '?')
        results[folio] = {
            'section': section,
            'n_lines': len(all_lines),
            'real_score': round(real_score, 4),
            'null_mean': round(null_mean, 4),
            'effect_size': round(effect, 4),
        }

    # Summary
    effects = [v['effect_size'] for v in results.values()]
    n_large = sum(1 for e in effects if abs(e) > 2)

    # Section breakdown
    section_effects = defaultdict(list)
    for v in results.values():
        section_effects[v['section']].append(v['effect_size'])

    section_summary = {}
    for sec, effs in sorted(section_effects.items()):
        section_summary[sec] = {
            'n_folios': len(effs),
            'mean_effect': round(float(np.mean(effs)), 4),
            'n_large': sum(1 for e in effs if abs(e) > 2),
        }

    return {
        'n_folios': len(results),
        'n_large_effect': n_large,
        'mean_effect': round(float(np.mean(effects)), 4) if effects else 0.0,
        'per_folio': results,
        'per_section': section_summary,
    }


# ── Controls ───────────────────────────────────────────────────────────

def section_stratification(paragraphs, rng):
    """T2 by section."""
    section_paras = defaultdict(list)
    for par in paragraphs:
        section_paras[par['section']].append(par)

    results = {}
    for sec, pars in sorted(section_paras.items()):
        if len(pars) < 5:
            continue
        # Run mini-T2
        zs = []
        for par in pars:
            fm = par['feature_matrix'] - par['feature_matrix'].mean(axis=0)
            real = sequential_structure_score(fm)
            nulls = []
            for _ in range(500):
                perm = rng.permutation(len(fm))
                nulls.append(sequential_structure_score(fm[perm]))
            nulls = np.array(nulls)
            z = (real - nulls.mean()) / nulls.std() if nulls.std() > 0 else 0.0
            zs.append(z)

        stouffer = sum(zs) / np.sqrt(len(zs))
        results[sec] = {
            'n_paragraphs': len(pars),
            'stouffer_z': round(stouffer, 4),
            'mean_z': round(float(np.mean(zs)), 4),
        }

    return results


def paragraph_length_stratification(paragraphs, rng):
    """T2 by paragraph length."""
    strata = {'short': [], 'medium': [], 'long': []}
    for par in paragraphs:
        n = par['n_body_lines']
        if n <= 7:
            strata['short'].append(par)
        elif n <= 11:
            strata['medium'].append(par)
        else:
            strata['long'].append(par)

    results = {}
    for name, pars in strata.items():
        if len(pars) < 3:
            results[name] = {'n_paragraphs': len(pars), 'stouffer_z': 0.0, 'note': 'too_few'}
            continue
        zs = []
        for par in pars:
            fm = par['feature_matrix'] - par['feature_matrix'].mean(axis=0)
            real = sequential_structure_score(fm)
            nulls = []
            for _ in range(500):
                perm = rng.permutation(len(fm))
                nulls.append(sequential_structure_score(fm[perm]))
            nulls = np.array(nulls)
            z = (real - nulls.mean()) / nulls.std() if nulls.std() > 0 else 0.0
            zs.append(z)

        stouffer = sum(zs) / np.sqrt(len(zs))
        results[name] = {
            'n_paragraphs': len(pars),
            'stouffer_z': round(stouffer, 4),
            'mean_z': round(float(np.mean(zs)), 4),
        }

    return results


# ── Verdict ────────────────────────────────────────────────────────────

def compute_verdict(t2, t3, t4):
    """Decision logic from plan."""
    if not t2['significant']:
        return 'ORDERING_NULL'

    # T2 significant -- check T3 (mode-residualized)
    if not t3['significant']:
        return 'MODE_ONLY'

    # Both significant -- check T4 for where signal lives
    q_sig = [t4[str(q)]['significant'] for q in range(5)]
    boundary_sig = q_sig[0] or q_sig[4]
    interior_sig = any(q_sig[1:4])

    if boundary_sig and not interior_sig:
        return 'BOUNDARY_ENRICHED'
    elif interior_sig:
        return 'DISTRIBUTED_SEQUENTIAL'
    else:
        return 'MODE_RESIDUAL_UNLOCALIZED'


# ── Main ───────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)

    print("Phase 595: Line Ordering Information Content")
    print("=" * 60)

    # Data assembly
    print("\nAssembling paragraphs...")
    paragraphs = assemble_paragraphs()
    n_para = len(paragraphs)
    total_body = sum(p['n_body_lines'] for p in paragraphs)
    sections = Counter(p['section'] for p in paragraphs)
    print(f"  Qualifying paragraphs: {n_para}")
    print(f"  Total body lines: {total_body}")
    print(f"  By section: {dict(sorted(sections.items()))}")

    # T2: Total Ordering Information
    print(f"\nT2: Total ordering information ({N_SHUFFLES} shuffles)...")
    t2 = compute_t2(paragraphs, rng)
    print(f"  Stouffer z = {t2['stouffer_z']}, p = {t2['stouffer_p']}")
    print(f"  Significant (p<0.01): {t2['significant']}")
    print(f"  Mean effect size: {t2['mean_effect_size']}")
    print(f"  Paragraphs p<0.05: {t2['n_significant_p05']}/{t2['n_paragraphs']} ({t2['frac_significant']})")

    # T3: Mode-Residualized
    print(f"\nT3: Mode-residualized ordering ({N_SHUFFLES} shuffles)...")
    t3 = compute_t3(paragraphs, rng)
    print(f"  Stouffer z = {t3['stouffer_z']}, p = {t3['stouffer_p']}")
    print(f"  Significant (p<0.01): {t3['significant']}")
    print(f"  Mean effect size: {t3['mean_effect_size']}")
    print(f"  Mode diff norm^2: {t3['mode_diff_norm_squared']}")

    # T4: Positional Information
    print(f"\nT4: Positional information ({N_SHUFFLES} shuffles)...")
    t4 = compute_t4(paragraphs, rng)
    for q in range(5):
        r = t4[str(q)]
        sig = " *" if r['significant'] else ""
        print(f"  Q{q}: norm={r['obs_norm']}, null_mean={r['null_mean']}, p={r['p_value']}, n={r['n_lines']}{sig}")

    # T5: Lag-1 MI Audit
    print(f"\nT5: Lag-1 MI audit ({N_SHUFFLES} shuffles)...")
    t5 = compute_t5(paragraphs, rng)
    for ch, val in sorted(t5.items()):
        if ch == 'total_significant_mi_bits':
            continue
        sig = " *" if val['significant'] else ""
        print(f"  {ch}: MI={val['mi_bits']} bits, H={val['h_marginal']}, frac={val['mi_fraction_of_h']}, p={val['p_value']}{sig}")
    print(f"  Total significant MI: {t5['total_significant_mi_bits']} bits")

    # T6: Per-Folio Effect Sizes
    print(f"\nT6: Per-folio effect sizes...")
    t6 = compute_t6(paragraphs, rng)
    print(f"  Folios tested: {t6['n_folios']}")
    print(f"  Mean effect: {t6['mean_effect']}")
    print(f"  |effect|>2: {t6['n_large_effect']}")
    for sec, val in sorted(t6['per_section'].items()):
        print(f"  {sec}: n={val['n_folios']}, mean_eff={val['mean_effect']}, n_large={val['n_large']}")

    # Controls
    print("\nControls...")
    sec_strat = section_stratification(paragraphs, rng)
    print("  Section stratification:")
    for sec, val in sorted(sec_strat.items()):
        print(f"    {sec}: n={val['n_paragraphs']}, stouffer_z={val['stouffer_z']}")

    len_strat = paragraph_length_stratification(paragraphs, rng)
    print("  Length stratification:")
    for name, val in sorted(len_strat.items()):
        print(f"    {name}: n={val['n_paragraphs']}, stouffer_z={val.get('stouffer_z', 'N/A')}")

    # Verdict
    verdict = compute_verdict(t2, t3, t4)
    print(f"\n{'=' * 60}")
    print(f"VERDICT: {verdict}")
    print(f"{'=' * 60}")

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    # Save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'metadata': {
            'phase': 595,
            'script': 'line_ordering_information.py',
            'runtime_seconds': round(elapsed, 1),
            'n_paragraphs': n_para,
            'n_body_lines': total_body,
            'sections': dict(sorted(sections.items())),
            'seed': SEED,
        },
        'T2_total_ordering': {k: v for k, v in t2.items() if k != 'per_paragraph'},
        'T2_per_paragraph': t2['per_paragraph'],
        'T3_mode_residualized': t3,
        'T4_positional': t4,
        'T5_lag1_mi': t5,
        'T6_per_folio': {k: v for k, v in t6.items() if k != 'per_folio'},
        'T6_per_folio_detail': t6['per_folio'],
        'controls': {
            'section_stratification': sec_strat,
            'length_stratification': len_strat,
        },
        'verdict': verdict,
    }

    out_path = os.path.join(RESULTS_DIR, 'line_ordering_information_results.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
