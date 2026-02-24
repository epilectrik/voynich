"""
Phase 450: SEQUENTIAL_CONTENT_PREDICTION

Does sequential position predict content at three scales?
  - LINE level: Does the opener token predict the body's content?
  - PARAGRAPH level: Do pre-termination lines show detectable drift?
  - FOLIO level: Does paragraph N's vocabulary predict paragraph N+1's?

Test Battery (9 tests, Bonferroni p < 0.0056):
  T1: Opener MIDDLE -> body MIDDLE vocabulary (Jaccard)
  T2: Opener MIDDLE -> suffix mode (A vs B)
  T3: Opener MIDDLE -> kernel profile (k/h/e fractions)
  T4: Opener MIDDLE -> FL stage distribution
  T5: Penultimate-line feature divergence (vs random body lines)
  T6: Monotonic pre-termination trajectory (ordinal regression)
  T7: Consecutive paragraph MIDDLE Jaccard (within folio)
  T8: Paragraph N kernel -> paragraph N+1 kernel correlation
  T9: Paragraph N suffix mode sequence -> paragraph N+1 suffix mode

Null models:
  Null A: Shuffle opener assignments across lines within folio (T1-T4)
  Null B: Shuffle line order within paragraph (T5-T6)
  Null C: Shuffle paragraph order within folio (T7-T9)

References: C958, C959, C1162, C1237, C1240, C845, C855, C862, C670, C963,
            C1229, C1231, C777, C1031
"""

import sys, json, os
import numpy as np
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

N_PERM = 1000
BONFERRONI_ALPHA = 0.05 / 9  # 9 tests -> p < 0.0056
RNG = np.random.RandomState(42)


# ── DATA LOADING ──────────────────────────────────────────────────

def load_data():
    """Load Currier B tokens, group into paragraphs and lines."""
    tx = Transcript()
    morph = Morphology()

    # Collect all B tokens with morphology
    tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L'):
            continue  # exclude labels
        if '*' in t.word:
            continue  # exclude uncertain
        if not t.word.strip():
            continue  # exclude empty
        m = morph.extract(t.word)
        tokens.append({
            'folio': t.folio,
            'line': t.line,
            'word': t.word,
            'middle': m.middle if m else '',
            'suffix': m.suffix if m else '',
            'prefix': m.prefix if m else '',
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'line_initial': t.line_initial,
            'line_final': t.line_final,
        })

    # Extract kernel characters from MIDDLE
    for tok in tokens:
        mid = tok['middle']
        tok['kernels'] = [c for c in 'khe' if c in mid]

    # Group by folio -> paragraphs -> lines
    # Use par_initial to detect paragraph boundaries
    folio_tokens = defaultdict(list)
    for tok in tokens:
        folio_tokens[tok['folio']].append(tok)

    folios = {}
    for folio, ftoks in folio_tokens.items():
        # Sort by line number
        ftoks.sort(key=lambda t: (t['line'],))

        # Group into lines
        lines_dict = defaultdict(list)
        for tok in ftoks:
            lines_dict[tok['line']].append(tok)
        line_nums = sorted(lines_dict.keys())

        # Group lines into paragraphs using par_initial
        paragraphs = []
        current_para = []
        for ln in line_nums:
            line_toks = lines_dict[ln]
            if line_toks[0]['par_initial'] and current_para:
                paragraphs.append(current_para)
                current_para = []
            current_para.append((ln, line_toks))
        if current_para:
            paragraphs.append(current_para)

        folios[folio] = paragraphs

    return folios, tokens


# ── FEATURE EXTRACTION ────────────────────────────────────────────

KERNEL_CHARS = ['k', 'h', 'e']

# Suffix category classification (from C1231 Mode A/B centroids)
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}
# bare = no suffix (empty string)

MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])

# FL stage map (from C777)
FL_MIDDLES = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    'o': 'FINAL', 'ly': 'FINAL', 'am': 'FINAL',
    'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL',
}
FL_STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']


def classify_suffix_mode(line_toks):
    """Classify a line's suffix mode as A or B using C1231 centroids."""
    if len(line_toks) < 3:
        return None
    n = len(line_toks)
    cats = [0, 0, 0, 0]  # terminal, connector, iterate, bare
    for tok in line_toks:
        sfx = tok['suffix']
        if sfx in TERMINAL_SUFFIXES:
            cats[0] += 1
        elif sfx in CONNECTOR_SUFFIXES:
            cats[1] += 1
        elif sfx in ITERATE_SUFFIXES:
            cats[2] += 1
        else:
            cats[3] += 1  # bare (including empty)
    vec = np.array(cats, dtype=float) / n
    dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
    dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if dist_a < dist_b else 'B'


def kernel_profile(line_toks):
    """Return (k_frac, h_frac, e_frac) for a line."""
    n = len(line_toks)
    if n == 0:
        return np.array([0.0, 0.0, 0.0])
    counts = [0, 0, 0]
    for tok in line_toks:
        for i, kc in enumerate(KERNEL_CHARS):
            if kc in tok['kernels']:
                counts[i] += 1
    return np.array(counts, dtype=float) / n


def fl_distribution(line_toks):
    """Return FL stage distribution vector for a line."""
    vec = np.zeros(len(FL_STAGES))
    n_fl = 0
    for tok in line_toks:
        stage = FL_MIDDLES.get(tok['middle'])
        if stage:
            vec[FL_STAGES.index(stage)] += 1
            n_fl += 1
    if n_fl > 0:
        vec /= n_fl
    return vec


def middle_set(line_toks):
    """Return set of MIDDLEs in a line."""
    return set(tok['middle'] for tok in line_toks if tok['middle'])


def jaccard(set_a, set_b):
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0


# ── AXIS 1: OPENER -> LINE CONTENT (T1-T4) ────────────────────────

def build_opener_line_pairs(folios):
    """Build list of (folio, opener_middle, body_toks) for all body lines."""
    pairs = []
    for folio, paragraphs in folios.items():
        for para in paragraphs:
            # Skip header line (first line), analyze body lines
            body_lines = para[1:] if len(para) > 1 else []
            for ln, line_toks in body_lines:
                if len(line_toks) < 2:
                    continue
                opener = line_toks[0]
                body = line_toks[1:]  # everything after opener
                opener_mid = opener['middle']
                if not opener_mid:
                    continue
                pairs.append({
                    'folio': folio,
                    'opener_middle': opener_mid,
                    'body_toks': body,
                    'body_middles': middle_set(body),
                    'suffix_mode': classify_suffix_mode(line_toks),
                    'kernel_prof': kernel_profile(body),
                    'fl_dist': fl_distribution(body),
                })
    return pairs


def t1_opener_middle_vocabulary(pairs):
    """T1: Does opener MIDDLE predict body MIDDLE vocabulary?

    Group lines by opener MIDDLE. For each group with >=5 lines, compute
    mean pairwise Jaccard within group. Compare to shuffled opener assignments.
    """
    # Group by opener MIDDLE
    groups = defaultdict(list)
    for p in pairs:
        groups[p['opener_middle']].append(p['body_middles'])

    # Filter to groups with >=5 lines
    valid_groups = {k: v for k, v in groups.items() if len(v) >= 5}
    if len(valid_groups) < 3:
        return {'verdict': 'SKIP', 'reason': 'too few opener groups'}

    # Observed: weighted mean intra-group Jaccard
    def mean_intra_jaccard(grps):
        total_j, total_n = 0.0, 0
        for middles_list in grps.values():
            n = len(middles_list)
            if n < 2:
                continue
            for i in range(n):
                for j in range(i + 1, n):
                    total_j += jaccard(middles_list[i], middles_list[j])
                    total_n += 1
        return total_j / total_n if total_n > 0 else 0.0

    observed = mean_intra_jaccard(valid_groups)

    # Permutation: shuffle opener assignments within folio
    all_body_middles = [p['body_middles'] for p in pairs]
    folio_indices = defaultdict(list)
    for i, p in enumerate(pairs):
        folio_indices[p['folio']].append(i)

    perm_vals = []
    for _ in range(N_PERM):
        shuffled_groups = defaultdict(list)
        for folio, indices in folio_indices.items():
            opener_mids = [pairs[i]['opener_middle'] for i in indices]
            RNG.shuffle(opener_mids)
            for idx, om in zip(indices, opener_mids):
                shuffled_groups[om].append(all_body_middles[idx])
        # Filter same way
        sg = {k: v for k, v in shuffled_groups.items() if len(v) >= 5}
        perm_vals.append(mean_intra_jaccard(sg))

    p_value = np.mean([pv >= observed for pv in perm_vals])
    ratio = observed / np.mean(perm_vals) if np.mean(perm_vals) > 0 else float('inf')

    return {
        'test': 'T1_opener_vocabulary',
        'observed_jaccard': round(observed, 4),
        'null_mean': round(np.mean(perm_vals), 4),
        'ratio': round(ratio, 3),
        'p_value': round(p_value, 4),
        'n_groups': len(valid_groups),
        'n_lines': sum(len(v) for v in valid_groups.values()),
        'pass': p_value < BONFERRONI_ALPHA,
        'verdict': 'PASS' if p_value < BONFERRONI_ALPHA else 'FAIL',
    }


def t2_opener_suffix_mode(pairs):
    """T2: Does opener MIDDLE predict body suffix mode (A vs B)?

    Chi-squared test: opener MIDDLE vs suffix mode assignment.
    Permutation null: shuffle mode labels within folio.
    """
    # Build contingency: opener_middle -> {A: count, B: count}
    valid = [(p['opener_middle'], p['suffix_mode']) for p in pairs if p['suffix_mode']]
    if len(valid) < 50:
        return {'verdict': 'SKIP', 'reason': 'too few lines with mode'}

    groups = defaultdict(lambda: {'A': 0, 'B': 0})
    for om, mode in valid:
        groups[om][mode] += 1

    # Filter to opener MIDDLEs with >=5 lines
    valid_groups = {k: v for k, v in groups.items() if v['A'] + v['B'] >= 5}
    if len(valid_groups) < 3:
        return {'verdict': 'SKIP', 'reason': 'too few opener groups'}

    # Cramer's V as effect size
    def cramers_v(grps):
        keys = sorted(grps.keys())
        table = np.array([[grps[k]['A'], grps[k]['B']] for k in keys], dtype=float)
        n = table.sum()
        if n == 0:
            return 0.0
        row_sums = table.sum(axis=1, keepdims=True)
        col_sums = table.sum(axis=0, keepdims=True)
        expected = row_sums * col_sums / n
        expected = np.maximum(expected, 1e-10)
        chi2 = ((table - expected) ** 2 / expected).sum()
        r, c = table.shape
        return np.sqrt(chi2 / (n * (min(r, c) - 1))) if min(r, c) > 1 else 0.0

    observed_v = cramers_v(valid_groups)

    # Permutation: shuffle mode labels within folio
    folio_modes = defaultdict(list)
    folio_openers = defaultdict(list)
    for p in pairs:
        if p['suffix_mode']:
            folio_modes[p['folio']].append(p['suffix_mode'])
            folio_openers[p['folio']].append(p['opener_middle'])

    perm_vals = []
    for _ in range(N_PERM):
        perm_groups = defaultdict(lambda: {'A': 0, 'B': 0})
        for folio in folio_modes:
            modes = list(folio_modes[folio])
            RNG.shuffle(modes)
            for om, mode in zip(folio_openers[folio], modes):
                perm_groups[om][mode] += 1
        pg = {k: v for k, v in perm_groups.items() if v['A'] + v['B'] >= 5}
        perm_vals.append(cramers_v(pg))

    p_value = np.mean([pv >= observed_v for pv in perm_vals])
    ratio = observed_v / np.mean(perm_vals) if np.mean(perm_vals) > 0 else float('inf')

    return {
        'test': 'T2_opener_suffix_mode',
        'observed_V': round(observed_v, 4),
        'null_mean_V': round(np.mean(perm_vals), 4),
        'ratio': round(ratio, 3),
        'p_value': round(p_value, 4),
        'n_groups': len(valid_groups),
        'n_lines': sum(v['A'] + v['B'] for v in valid_groups.values()),
        'pass': p_value < BONFERRONI_ALPHA,
        'verdict': 'PASS' if p_value < BONFERRONI_ALPHA else 'FAIL',
    }


def t3_opener_kernel_profile(pairs):
    """T3: Does opener MIDDLE predict body kernel profile?

    Group by opener MIDDLE. Compute mean kernel profile per group.
    Test: variance of group means vs shuffled.
    """
    groups = defaultdict(list)
    for p in pairs:
        groups[p['opener_middle']].append(p['kernel_prof'])

    valid_groups = {k: v for k, v in groups.items() if len(v) >= 5}
    if len(valid_groups) < 3:
        return {'verdict': 'SKIP', 'reason': 'too few opener groups'}

    # Observed: variance of group mean kernel profiles
    def group_mean_variance(grps):
        means = []
        for profiles in grps.values():
            means.append(np.mean(profiles, axis=0))
        means = np.array(means)
        return np.var(means, axis=0).sum()  # total variance across k/h/e

    observed = group_mean_variance(valid_groups)

    # Permutation: shuffle opener assignments within folio
    all_kernel_profs = [p['kernel_prof'] for p in pairs]
    folio_indices = defaultdict(list)
    for i, p in enumerate(pairs):
        folio_indices[p['folio']].append(i)

    perm_vals = []
    for _ in range(N_PERM):
        shuffled_groups = defaultdict(list)
        for folio, indices in folio_indices.items():
            opener_mids = [pairs[i]['opener_middle'] for i in indices]
            RNG.shuffle(opener_mids)
            for idx, om in zip(indices, opener_mids):
                shuffled_groups[om].append(all_kernel_profs[idx])
        sg = {k: v for k, v in shuffled_groups.items() if len(v) >= 5}
        perm_vals.append(group_mean_variance(sg))

    p_value = np.mean([pv >= observed for pv in perm_vals])
    ratio = observed / np.mean(perm_vals) if np.mean(perm_vals) > 0 else float('inf')

    # Also report per-kernel means for top openers
    top_openers = sorted(valid_groups.keys(),
                         key=lambda k: len(valid_groups[k]), reverse=True)[:5]
    top_profiles = {}
    for om in top_openers:
        prof = np.mean(valid_groups[om], axis=0)
        top_profiles[om] = {
            'k': round(float(prof[0]), 3),
            'h': round(float(prof[1]), 3),
            'e': round(float(prof[2]), 3),
            'n': len(valid_groups[om]),
        }

    return {
        'test': 'T3_opener_kernel_profile',
        'observed_variance': round(float(observed), 6),
        'null_mean_variance': round(float(np.mean(perm_vals)), 6),
        'ratio': round(ratio, 3),
        'p_value': round(p_value, 4),
        'n_groups': len(valid_groups),
        'n_lines': sum(len(v) for v in valid_groups.values()),
        'top_opener_profiles': top_profiles,
        'pass': p_value < BONFERRONI_ALPHA,
        'verdict': 'PASS' if p_value < BONFERRONI_ALPHA else 'FAIL',
    }


def t4_opener_fl_distribution(pairs):
    """T4: Does opener MIDDLE predict body FL stage distribution?

    Same structure as T3 but with FL stage vectors.
    """
    # Only use lines with >=1 FL token in body
    valid_pairs = [p for p in pairs if np.sum(p['fl_dist']) > 0]

    groups = defaultdict(list)
    for p in valid_pairs:
        groups[p['opener_middle']].append(p['fl_dist'])

    valid_groups = {k: v for k, v in groups.items() if len(v) >= 5}
    if len(valid_groups) < 3:
        return {'verdict': 'SKIP', 'reason': 'too few opener groups'}

    def group_mean_variance(grps):
        means = []
        for dists in grps.values():
            means.append(np.mean(dists, axis=0))
        means = np.array(means)
        return np.var(means, axis=0).sum()

    observed = group_mean_variance(valid_groups)

    # Permutation within folio
    folio_indices = defaultdict(list)
    for i, p in enumerate(valid_pairs):
        folio_indices[p['folio']].append(i)

    all_fl = [p['fl_dist'] for p in valid_pairs]

    perm_vals = []
    for _ in range(N_PERM):
        shuffled_groups = defaultdict(list)
        for folio, indices in folio_indices.items():
            opener_mids = [valid_pairs[i]['opener_middle'] for i in indices]
            RNG.shuffle(opener_mids)
            for idx, om in zip(indices, opener_mids):
                shuffled_groups[om].append(all_fl[idx])
        sg = {k: v for k, v in shuffled_groups.items() if len(v) >= 5}
        perm_vals.append(group_mean_variance(sg))

    p_value = np.mean([pv >= observed for pv in perm_vals])
    ratio = observed / np.mean(perm_vals) if np.mean(perm_vals) > 0 else float('inf')

    return {
        'test': 'T4_opener_fl_distribution',
        'observed_variance': round(float(observed), 6),
        'null_mean_variance': round(float(np.mean(perm_vals)), 6),
        'ratio': round(ratio, 3),
        'p_value': round(p_value, 4),
        'n_groups': len(valid_groups),
        'n_lines': sum(len(v) for v in valid_groups.values()),
        'pass': p_value < BONFERRONI_ALPHA,
        'verdict': 'PASS' if p_value < BONFERRONI_ALPHA else 'FAIL',
    }


# ── AXIS 2: PRE-TERMINATION DRIFT (T5-T6) ────────────────────────

def build_paragraph_lines(folios, min_body_lines=5):
    """Build paragraph data for termination analysis.
    Returns list of paragraphs, each with body_lines (excluding header).
    Only paragraphs with >= min_body_lines body lines.
    """
    paragraphs = []
    for folio, paras in folios.items():
        for para in paras:
            if len(para) < min_body_lines + 1:  # +1 for header
                continue
            body_lines = para[1:]  # skip header
            if len(body_lines) < min_body_lines:
                continue
            paragraphs.append({
                'folio': folio,
                'body_lines': body_lines,
                'n_body': len(body_lines),
            })
    return paragraphs


def line_features(line_toks):
    """Extract feature vector for a line."""
    kp = kernel_profile(line_toks)
    fl = fl_distribution(line_toks)
    mode = classify_suffix_mode(line_toks)
    mode_val = 1.0 if mode == 'A' else 0.0 if mode == 'B' else 0.5
    n_toks = len(line_toks)

    # Suffix terminal fraction
    n_terminal = sum(1 for t in line_toks if t['suffix'] in TERMINAL_SUFFIXES)
    terminal_frac = n_terminal / n_toks if n_toks > 0 else 0.0

    # Suffix bare fraction
    n_bare = sum(1 for t in line_toks if not t['suffix'])
    bare_frac = n_bare / n_toks if n_toks > 0 else 0.0

    # MIDDLE uniqueness (fraction of unique MIDDLEs)
    middles = [t['middle'] for t in line_toks if t['middle']]
    unique_frac = len(set(middles)) / len(middles) if middles else 0.0

    return np.array([
        kp[0], kp[1], kp[2],           # k, h, e fractions
        mode_val,                        # suffix mode (A=1, B=0)
        terminal_frac,                   # terminal suffix fraction
        bare_frac,                       # bare token fraction
        float(n_toks),                   # line length
        unique_frac,                     # MIDDLE uniqueness
    ])


FEATURE_NAMES = ['k_frac', 'h_frac', 'e_frac', 'suffix_mode_val',
                 'terminal_frac', 'bare_frac', 'n_tokens', 'middle_uniqueness']


def t5_penultimate_divergence(paragraphs):
    """T5: Are penultimate lines distinguishable from random body lines?

    For each paragraph, compare last 2 body lines vs random non-final body lines.
    Use Euclidean distance of feature vectors.
    """
    if len(paragraphs) < 10:
        return {'verdict': 'SKIP', 'reason': 'too few paragraphs'}

    # For each paragraph: features of last-2 vs features of random-2 body lines
    penult_features = []
    random_features = []

    for para in paragraphs:
        body = para['body_lines']
        n = len(body)
        if n < 4:
            continue

        # Last 2 body lines
        for ln, toks in body[-2:]:
            penult_features.append(line_features(toks))

        # Random 2 from non-final lines
        non_final = body[:-2]
        if len(non_final) >= 2:
            chosen = RNG.choice(len(non_final), size=2, replace=False)
            for idx in chosen:
                ln, toks = non_final[idx]
                random_features.append(line_features(toks))

    if len(penult_features) < 20 or len(random_features) < 20:
        return {'verdict': 'SKIP', 'reason': 'too few lines'}

    penult_arr = np.array(penult_features)
    random_arr = np.array(random_features)

    # Normalize features
    all_feats = np.vstack([penult_arr, random_arr])
    feat_std = np.std(all_feats, axis=0)
    feat_std[feat_std == 0] = 1.0
    feat_mean = np.mean(all_feats, axis=0)
    penult_norm = (penult_arr - feat_mean) / feat_std
    random_norm = (random_arr - feat_mean) / feat_std

    # Observed: mean Euclidean distance between penultimate and random centroids
    penult_centroid = np.mean(penult_norm, axis=0)
    random_centroid = np.mean(random_norm, axis=0)
    observed_dist = np.linalg.norm(penult_centroid - random_centroid)

    # Per-feature differences
    feature_diffs = {}
    for i, name in enumerate(FEATURE_NAMES):
        feature_diffs[name] = {
            'penultimate_mean': round(float(np.mean(penult_arr[:, i])), 4),
            'random_mean': round(float(np.mean(random_arr[:, i])), 4),
            'diff': round(float(np.mean(penult_arr[:, i]) - np.mean(random_arr[:, i])), 4),
        }

    # Permutation: shuffle penultimate/random labels
    combined = np.vstack([penult_norm, random_norm])
    n_penult = len(penult_norm)

    perm_vals = []
    for _ in range(N_PERM):
        perm_idx = RNG.permutation(len(combined))
        perm_penult = combined[perm_idx[:n_penult]]
        perm_random = combined[perm_idx[n_penult:]]
        perm_dist = np.linalg.norm(np.mean(perm_penult, axis=0) - np.mean(perm_random, axis=0))
        perm_vals.append(perm_dist)

    p_value = np.mean([pv >= observed_dist for pv in perm_vals])
    ratio = observed_dist / np.mean(perm_vals) if np.mean(perm_vals) > 0 else float('inf')

    return {
        'test': 'T5_penultimate_divergence',
        'observed_distance': round(float(observed_dist), 4),
        'null_mean_distance': round(float(np.mean(perm_vals)), 4),
        'ratio': round(ratio, 3),
        'p_value': round(p_value, 4),
        'n_paragraphs': len(paragraphs),
        'n_penultimate_lines': len(penult_features),
        'n_random_lines': len(random_features),
        'feature_diffs': feature_diffs,
        'pass': p_value < BONFERRONI_ALPHA,
        'verdict': 'PASS' if p_value < BONFERRONI_ALPHA else 'FAIL',
    }


def t6_pre_termination_trajectory(paragraphs):
    """T6: Is there a monotonic trajectory toward termination?

    For each paragraph, compute features at each body line position.
    Test: Spearman correlation between line position and each feature.
    Stronger than T5: not just "last 2 are different" but "there's a gradient."
    """
    if len(paragraphs) < 10:
        return {'verdict': 'SKIP', 'reason': 'too few paragraphs'}

    # Collect (normalized_position, features) across all paragraphs
    positions = []
    features = []
    para_ids = []

    for pi, para in enumerate(paragraphs):
        body = para['body_lines']
        n = len(body)
        for li, (ln, toks) in enumerate(body):
            norm_pos = li / (n - 1) if n > 1 else 0.0
            positions.append(norm_pos)
            features.append(line_features(toks))
            para_ids.append(pi)

    positions = np.array(positions)
    features = np.array(features)
    para_ids = np.array(para_ids)

    # Spearman correlations for each feature
    from scipy.stats import spearmanr

    correlations = {}
    for i, name in enumerate(FEATURE_NAMES):
        rho, p = spearmanr(positions, features[:, i])
        correlations[name] = {
            'rho': round(float(rho), 4),
            'p_value': round(float(p), 4),
        }

    # Permutation: shuffle line order within each paragraph
    perm_rhos = {name: [] for name in FEATURE_NAMES}
    for _ in range(N_PERM):
        perm_positions = positions.copy()
        for pi in range(max(para_ids) + 1):
            mask = para_ids == pi
            perm_positions[mask] = RNG.permutation(perm_positions[mask])
        for i, name in enumerate(FEATURE_NAMES):
            rho, _ = spearmanr(perm_positions, features[:, i])
            perm_rhos[name].append(abs(rho))

    # P-values: fraction of permutations with |rho| >= observed |rho|
    results = {}
    n_significant = 0
    for name in FEATURE_NAMES:
        obs_abs = abs(correlations[name]['rho'])
        perm_p = np.mean([pr >= obs_abs for pr in perm_rhos[name]])
        results[name] = {
            'rho': correlations[name]['rho'],
            'perm_p': round(float(perm_p), 4),
            'significant': perm_p < BONFERRONI_ALPHA,
        }
        if perm_p < BONFERRONI_ALPHA:
            n_significant += 1

    return {
        'test': 'T6_pre_termination_trajectory',
        'feature_correlations': results,
        'n_significant_features': n_significant,
        'n_features': len(FEATURE_NAMES),
        'n_lines': len(positions),
        'n_paragraphs': len(paragraphs),
        'pass': n_significant >= 2,  # at least 2 features show trajectory
        'verdict': 'PASS' if n_significant >= 2 else 'FAIL',
    }


# ── AXIS 3: CROSS-PARAGRAPH VOCABULARY (T7-T9) ───────────────────

def build_folio_paragraph_features(folios, min_paragraphs=3):
    """Build per-paragraph feature summaries for each folio."""
    folio_paras = {}
    for folio, paragraphs in folios.items():
        if len(paragraphs) < min_paragraphs:
            continue
        para_feats = []
        for para in paragraphs:
            all_toks = []
            for ln, toks in para:
                all_toks.extend(toks)
            if len(all_toks) < 5:
                continue

            middles = middle_set(all_toks)
            kp = kernel_profile(all_toks)

            # Suffix mode: majority vote across body lines
            body_lines = para[1:] if len(para) > 1 else para
            modes = [classify_suffix_mode(toks) for ln, toks in body_lines]
            modes = [m for m in modes if m]
            mode_a_frac = sum(1 for m in modes if m == 'A') / len(modes) if modes else 0.5

            para_feats.append({
                'middles': middles,
                'kernel_profile': kp,
                'mode_a_fraction': mode_a_frac,
                'n_tokens': len(all_toks),
            })

        if len(para_feats) >= min_paragraphs:
            folio_paras[folio] = para_feats

    return folio_paras


def t7_consecutive_paragraph_vocabulary(folio_paras):
    """T7: Do consecutive paragraphs share more vocabulary than non-consecutive?

    Within each folio, compare Jaccard of consecutive paragraph pairs
    vs non-consecutive pairs. Permutation: shuffle paragraph order.
    """
    consec_jaccards = []
    nonconsec_jaccards = []

    for folio, paras in folio_paras.items():
        n = len(paras)
        for i in range(n):
            for j in range(i + 1, n):
                j_val = jaccard(paras[i]['middles'], paras[j]['middles'])
                if j == i + 1:
                    consec_jaccards.append(j_val)
                else:
                    nonconsec_jaccards.append(j_val)

    if len(consec_jaccards) < 10:
        return {'verdict': 'SKIP', 'reason': 'too few consecutive pairs'}

    observed_diff = np.mean(consec_jaccards) - np.mean(nonconsec_jaccards)

    # Permutation: shuffle paragraph order within folio
    perm_diffs = []
    for _ in range(N_PERM):
        perm_consec = []
        perm_nonconsec = []
        for folio, paras in folio_paras.items():
            n = len(paras)
            perm_order = RNG.permutation(n)
            for i in range(n):
                for j in range(i + 1, n):
                    j_val = jaccard(paras[perm_order[i]]['middles'],
                                    paras[perm_order[j]]['middles'])
                    if j == i + 1:
                        perm_consec.append(j_val)
                    else:
                        perm_nonconsec.append(j_val)
        pd = np.mean(perm_consec) - np.mean(perm_nonconsec) if perm_consec else 0.0
        perm_diffs.append(pd)

    p_value = np.mean([pd >= observed_diff for pd in perm_diffs])

    return {
        'test': 'T7_consecutive_vocabulary',
        'consec_mean_jaccard': round(float(np.mean(consec_jaccards)), 4),
        'nonconsec_mean_jaccard': round(float(np.mean(nonconsec_jaccards)), 4),
        'observed_diff': round(float(observed_diff), 4),
        'null_mean_diff': round(float(np.mean(perm_diffs)), 4),
        'p_value': round(p_value, 4),
        'n_consec_pairs': len(consec_jaccards),
        'n_nonconsec_pairs': len(nonconsec_jaccards),
        'n_folios': len(folio_paras),
        'pass': p_value < BONFERRONI_ALPHA,
        'verdict': 'PASS' if p_value < BONFERRONI_ALPHA else 'FAIL',
    }


def t8_paragraph_kernel_autocorrelation(folio_paras):
    """T8: Does paragraph N's kernel profile predict paragraph N+1's?

    Pearson correlation between consecutive paragraphs' kernel profiles.
    """
    from scipy.stats import pearsonr

    # Collect consecutive kernel profile pairs
    pairs_k = []  # (para_n_k, para_n1_k) for each kernel dimension
    pairs_h = []
    pairs_e = []

    for folio, paras in folio_paras.items():
        for i in range(len(paras) - 1):
            kp_n = paras[i]['kernel_profile']
            kp_n1 = paras[i + 1]['kernel_profile']
            pairs_k.append((kp_n[0], kp_n1[0]))
            pairs_h.append((kp_n[1], kp_n1[1]))
            pairs_e.append((kp_n[2], kp_n1[2]))

    if len(pairs_k) < 15:
        return {'verdict': 'SKIP', 'reason': 'too few consecutive pairs'}

    kernel_results = {}
    for name, pair_list in [('k', pairs_k), ('h', pairs_h), ('e', pairs_e)]:
        x = np.array([p[0] for p in pair_list])
        y = np.array([p[1] for p in pair_list])
        if np.std(x) < 1e-10 or np.std(y) < 1e-10:
            kernel_results[name] = {'rho': 0.0, 'p_value': 1.0}
            continue
        rho, p = pearsonr(x, y)
        kernel_results[name] = {'rho': round(float(rho), 4), 'p_value': round(float(p), 4)}

    # Permutation: shuffle paragraph order within folio
    perm_rhos = {'k': [], 'h': [], 'e': []}
    for _ in range(N_PERM):
        pk, ph, pe = [], [], []
        for folio, paras in folio_paras.items():
            perm_order = RNG.permutation(len(paras))
            for i in range(len(paras) - 1):
                kp_n = paras[perm_order[i]]['kernel_profile']
                kp_n1 = paras[perm_order[i + 1]]['kernel_profile']
                pk.append((kp_n[0], kp_n1[0]))
                ph.append((kp_n[1], kp_n1[1]))
                pe.append((kp_n[2], kp_n1[2]))
        for name, pair_list in [('k', pk), ('h', ph), ('e', pe)]:
            x = np.array([p[0] for p in pair_list])
            y = np.array([p[1] for p in pair_list])
            if np.std(x) < 1e-10 or np.std(y) < 1e-10:
                perm_rhos[name].append(0.0)
            else:
                r, _ = pearsonr(x, y)
                perm_rhos[name].append(abs(r))

    # P-values
    for name in kernel_results:
        obs_abs = abs(kernel_results[name]['rho'])
        perm_p = np.mean([pr >= obs_abs for pr in perm_rhos[name]])
        kernel_results[name]['perm_p'] = round(float(perm_p), 4)
        kernel_results[name]['significant'] = perm_p < BONFERRONI_ALPHA

    any_sig = any(kernel_results[k]['significant'] for k in kernel_results)

    return {
        'test': 'T8_paragraph_kernel_autocorrelation',
        'kernel_correlations': kernel_results,
        'n_consecutive_pairs': len(pairs_k),
        'n_folios': len(folio_paras),
        'pass': any_sig,
        'verdict': 'PASS' if any_sig else 'FAIL',
    }


def t9_paragraph_mode_autocorrelation(folio_paras):
    """T9: Does paragraph N's suffix mode composition predict paragraph N+1's?

    Pearson correlation between consecutive paragraphs' Mode A fractions.
    """
    from scipy.stats import pearsonr

    pairs = []
    for folio, paras in folio_paras.items():
        for i in range(len(paras) - 1):
            pairs.append((paras[i]['mode_a_fraction'],
                          paras[i + 1]['mode_a_fraction']))

    if len(pairs) < 15:
        return {'verdict': 'SKIP', 'reason': 'too few consecutive pairs'}

    x = np.array([p[0] for p in pairs])
    y = np.array([p[1] for p in pairs])

    if np.std(x) < 1e-10 or np.std(y) < 1e-10:
        return {
            'test': 'T9_paragraph_mode_autocorrelation',
            'rho': 0.0, 'p_value': 1.0,
            'verdict': 'FAIL',
            'reason': 'zero variance',
        }

    rho, p = pearsonr(x, y)

    # Permutation: shuffle paragraph order within folio
    perm_rhos = []
    for _ in range(N_PERM):
        perm_pairs = []
        for folio, paras in folio_paras.items():
            perm_order = RNG.permutation(len(paras))
            for i in range(len(paras) - 1):
                perm_pairs.append((paras[perm_order[i]]['mode_a_fraction'],
                                   paras[perm_order[i + 1]]['mode_a_fraction']))
        px = np.array([p[0] for p in perm_pairs])
        py = np.array([p[1] for p in perm_pairs])
        if np.std(px) < 1e-10 or np.std(py) < 1e-10:
            perm_rhos.append(0.0)
        else:
            pr, _ = pearsonr(px, py)
            perm_rhos.append(abs(pr))

    perm_p = np.mean([pr >= abs(rho) for pr in perm_rhos])

    return {
        'test': 'T9_paragraph_mode_autocorrelation',
        'rho': round(float(rho), 4),
        'parametric_p': round(float(p), 4),
        'perm_p': round(float(perm_p), 4),
        'n_pairs': len(pairs),
        'n_folios': len(folio_paras),
        'mean_mode_a': round(float(np.mean(x)), 4),
        'std_mode_a': round(float(np.std(x)), 4),
        'pass': perm_p < BONFERRONI_ALPHA,
        'verdict': 'PASS' if perm_p < BONFERRONI_ALPHA else 'FAIL',
    }


# ── MAIN ──────────────────────────────────────────────────────────

def main():
    print("Phase 450: SEQUENTIAL_CONTENT_PREDICTION")
    print("=" * 60)

    print("\nLoading data...")
    folios, all_tokens = load_data()
    print(f"  {len(all_tokens)} tokens across {len(folios)} folios")

    # -- AXIS 1: Opener -> Line Content --
    print("\n-- AXIS 1: Opener -> Line Content --")
    pairs = build_opener_line_pairs(folios)
    print(f"  {len(pairs)} opener-body pairs")

    print("\n  T1: Opener MIDDLE -> body vocabulary...")
    r1 = t1_opener_middle_vocabulary(pairs)
    print(f"    {r1['verdict']} | Jaccard {r1.get('observed_jaccard', 'N/A')} "
          f"(null {r1.get('null_mean', 'N/A')}), "
          f"ratio {r1.get('ratio', 'N/A')}x, p={r1.get('p_value', 'N/A')}")

    print("\n  T2: Opener MIDDLE -> suffix mode...")
    r2 = t2_opener_suffix_mode(pairs)
    print(f"    {r2['verdict']} | Cramer's V={r2.get('observed_V', 'N/A')} "
          f"(null {r2.get('null_mean_V', 'N/A')}), "
          f"ratio {r2.get('ratio', 'N/A')}x, p={r2.get('p_value', 'N/A')}")

    print("\n  T3: Opener MIDDLE -> kernel profile...")
    r3 = t3_opener_kernel_profile(pairs)
    print(f"    {r3['verdict']} | var {r3.get('observed_variance', 'N/A')} "
          f"(null {r3.get('null_mean_variance', 'N/A')}), "
          f"ratio {r3.get('ratio', 'N/A')}x, p={r3.get('p_value', 'N/A')}")

    print("\n  T4: Opener MIDDLE -> FL distribution...")
    r4 = t4_opener_fl_distribution(pairs)
    print(f"    {r4['verdict']} | var {r4.get('observed_variance', 'N/A')} "
          f"(null {r4.get('null_mean_variance', 'N/A')}), "
          f"ratio {r4.get('ratio', 'N/A')}x, p={r4.get('p_value', 'N/A')}")

    # -- AXIS 2: Pre-Termination Drift --
    print("\n-- AXIS 2: Pre-Termination Drift --")
    paragraphs = build_paragraph_lines(folios, min_body_lines=5)
    print(f"  {len(paragraphs)} paragraphs with 5+ body lines")

    print("\n  T5: Penultimate line divergence...")
    r5 = t5_penultimate_divergence(paragraphs)
    print(f"    {r5['verdict']} | distance {r5.get('observed_distance', 'N/A')} "
          f"(null {r5.get('null_mean_distance', 'N/A')}), "
          f"ratio {r5.get('ratio', 'N/A')}x, p={r5.get('p_value', 'N/A')}")

    print("\n  T6: Pre-termination trajectory...")
    r6 = t6_pre_termination_trajectory(paragraphs)
    print(f"    {r6['verdict']} | {r6.get('n_significant_features', 'N/A')}/{r6.get('n_features', 'N/A')} "
          f"features show significant trajectory")
    if 'feature_correlations' in r6:
        for name, vals in r6['feature_correlations'].items():
            sig = '*' if vals.get('significant') else ''
            print(f"      {name}: rho={vals['rho']}, p={vals['perm_p']}{sig}")

    # -- AXIS 3: Cross-Paragraph Vocabulary --
    print("\n-- AXIS 3: Cross-Paragraph Vocabulary --")
    folio_paras = build_folio_paragraph_features(folios, min_paragraphs=3)
    total_paras = sum(len(p) for p in folio_paras.values())
    print(f"  {total_paras} paragraphs across {len(folio_paras)} folios")

    print("\n  T7: Consecutive paragraph vocabulary...")
    r7 = t7_consecutive_paragraph_vocabulary(folio_paras)
    print(f"    {r7['verdict']} | consec {r7.get('consec_mean_jaccard', 'N/A')} "
          f"vs nonconsec {r7.get('nonconsec_mean_jaccard', 'N/A')}, "
          f"diff={r7.get('observed_diff', 'N/A')}, p={r7.get('p_value', 'N/A')}")

    print("\n  T8: Paragraph kernel autocorrelation...")
    r8 = t8_paragraph_kernel_autocorrelation(folio_paras)
    print(f"    {r8['verdict']}")
    if 'kernel_correlations' in r8:
        for k, vals in r8['kernel_correlations'].items():
            sig = '*' if vals.get('significant') else ''
            print(f"      {k}: rho={vals['rho']}, perm_p={vals['perm_p']}{sig}")

    print("\n  T9: Paragraph suffix mode autocorrelation...")
    r9 = t9_paragraph_mode_autocorrelation(folio_paras)
    print(f"    {r9['verdict']} | rho={r9.get('rho', 'N/A')}, "
          f"perm_p={r9.get('perm_p', 'N/A')}")

    # ── SUMMARY ──
    results = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
    n_pass = sum(1 for r in results if r.get('pass'))
    n_total = len(results)
    n_skip = sum(1 for r in results if r.get('verdict') == 'SKIP')
    n_tested = n_total - n_skip

    print("\n" + "=" * 60)
    print(f"SUMMARY: {n_pass}/{n_tested} tests PASS ({n_skip} skipped)")
    print(f"  Axis 1 (Opener->Content): {sum(1 for r in [r1,r2,r3,r4] if r.get('pass'))}/4")
    print(f"  Axis 2 (Pre-Termination): {sum(1 for r in [r5,r6] if r.get('pass'))}/2")
    print(f"  Axis 3 (Cross-Paragraph): {sum(1 for r in [r7,r8,r9] if r.get('pass'))}/3")

    if n_pass == 0:
        overall = "NULL — no sequential content prediction at any scale"
    elif n_pass <= 2:
        overall = "WEAK_SIGNAL — isolated sequential effects"
    elif n_pass <= 5:
        overall = "PARTIAL — sequential structure at some scales"
    else:
        overall = "STRONG — pervasive sequential content prediction"
    print(f"\n  OVERALL: {overall}")

    # ── SAVE ──
    output = {
        'phase': 'Phase 450: SEQUENTIAL_CONTENT_PREDICTION',
        'n_tests': n_total,
        'n_pass': n_pass,
        'n_skip': n_skip,
        'overall_verdict': overall,
        'bonferroni_alpha': round(BONFERRONI_ALPHA, 4),
        'n_permutations': N_PERM,
        'axis_1_opener_content': {
            'T1': r1, 'T2': r2, 'T3': r3, 'T4': r4,
            'n_pass': sum(1 for r in [r1, r2, r3, r4] if r.get('pass')),
        },
        'axis_2_pre_termination': {
            'T5': r5, 'T6': r6,
            'n_pass': sum(1 for r in [r5, r6] if r.get('pass')),
        },
        'axis_3_cross_paragraph': {
            'T7': r7, 'T8': r8, 'T9': r9,
            'n_pass': sum(1 for r in [r7, r8, r9] if r.get('pass')),
        },
        'data_summary': {
            'n_tokens': len(all_tokens),
            'n_folios': len(folios),
            'n_opener_pairs': len(pairs),
            'n_paragraphs_termination': len(paragraphs),
            'n_folios_cross_para': len(folio_paras),
        },
    }

    out_path = Path(__file__).resolve().parents[1] / 'results' / 'sequential_content_prediction.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, np.integer)):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
