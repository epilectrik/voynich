#!/usr/bin/env python3
"""
AXM_RESIDUAL_DECOMPOSITION -- Phase 357
Direct attack on the 40% unexplained folio-level AXM self-transition variance (C1017).

C1017 baseline: REGIME+section (42%) + PREFIX entropy (5.1%) + hazard density (6.1%)
                + bridge geometry PC1 (6.3%) = 59.6% explained; 40.1% residual.

Pre-registered primary predictors:
  1. Paragraph count per folio
  2. Body HT density (excluding line-1 per C800)
  3. Gatekeeper class fraction ({15,20,21,22,25} as fraction of AX tokens)
  4. QO fraction of EN tokens

Pre-registered secondary predictors:
  5. Unique MIDDLE count (residualized against token count)
  6. Line count per folio

Analysis pipeline:
  S1. Replicate C1017 baseline model
  S2. Univariate Spearman correlations (Bonferroni-corrected, p < 0.0083)
  S3. Incremental R2 for each new predictor beyond baseline
  S4. Mixed-effects approximation (archetype random slopes)
  S5. Targeted interactions (max 2-3, chosen post-S3)
  S6. Random forest on residuals (non-linearity check)
  S7. Leave-one-out CV R2 for final model

Success criteria:
  - dR2 >= 0.05 for at least one predictor
  - CV R2 within 0.10 of training R2
  - Residual archetype structure reduced

Constraints respected:
  - C976-C980: 6-state partition is fixed
  - C384: No entry-level A-B coupling
  - C124: Same grammar, different parameterizations
  - C1006: AXM dwell is topology artifact (not independent DV)
  - C458: Hazard clamped, recovery free
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ─── Constants (C1010 frozen partition) ───

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,45,46,47,48,49},
    'AXm':     {3,5,18,19,42},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
N_STATES = len(STATE_ORDER)

GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}
HAZARD_MIDDLES = HAZARD_SOURCES | HAZARD_TARGETS

# EN classes (part of AXM): classes where PREFIX is qo, ch, or sh dominant
# Per C605/C977: EN = AX behavioral family. QO prefix identifies one lane.
# We identify EN tokens by PREFIX (qo or ch/sh) since EN is a PREFIX-defined concept

MIN_TRANSITIONS = 50

# ─── Data Loading ───

def load_token_to_class():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    return data['token_to_class']


def load_regime_assignments():
    path = PROJECT_ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    path = PROJECT_ROOT / 'phases' / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)

    archetype_data = data['t2_archetype_discovery']
    folio_labels = archetype_data.get('folio_labels', {})
    return {k: int(v) for k, v in folio_labels.items()}


def load_bridge_middles():
    path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(path) as f:
        data = json.load(f)
    return set(data['t5_structural_profile']['bridge_middles'])


def load_compatibility_matrix_and_index():
    """Load MIDDLE compatibility matrix and build index from Currier A MIDDLEs.

    The compat matrix is built from A vocabulary (DISCRIMINATION_SPACE_DERIVATION).
    The MIDDLE index is reconstructed by iterating A tokens, same as C1017 original.
    """
    compat_path = PROJECT_ROOT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    if not compat_path.exists():
        return None, None

    M = np.load(compat_path)

    # Build MIDDLE index from Currier A tokens (matches C1017 original)
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
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}

    return M, mid_to_idx


# ─── Corpus Building ───

def build_corpus_data(token_to_class):
    """Build token-level corpus with all needed annotations."""
    tx = Transcript()
    morph = Morphology()

    # First pass: count tokens per line for position computation
    line_counts = Counter()
    line_tokens_raw = defaultdict(list)
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        key = (token.folio, token.line)
        line_counts[key] += 1
        line_tokens_raw[key].append(token)

    tokens = []
    folio_sections = {}

    for (folio, line), raw_toks in line_tokens_raw.items():
        total_in_line = line_counts[(folio, line)]
        for pos_idx, token in enumerate(raw_toks):
            word = token.word.strip()
            if word not in token_to_class:
                continue

            cls = int(token_to_class[word])
            state = CLASS_TO_STATE.get(cls)
            if state is None:
                continue

            m = morph.extract(word)
            prefix = m.prefix if m.prefix else '__BARE__'
            middle = m.middle
            suffix = m.suffix

            # Line position quartile
            if total_in_line > 1:
                frac = pos_idx / (total_in_line - 1)
            else:
                frac = 0.5
            quartile = min(int(frac * 4) + 1, 4)

            is_hazard = middle in HAZARD_MIDDLES if middle else False
            is_gatekeeper = cls in GATEKEEPER_CLASSES

            tokens.append({
                'word': word,
                'folio': folio,
                'line': line,
                'section': token.section,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix,
                'cls': cls,
                'state': state,
                'quartile': quartile,
                'is_hazard': is_hazard,
                'is_gatekeeper': is_gatekeeper,
                'par_initial': token.par_initial,
                'line_num': int(token.line) if token.line.isdigit() else 0,
            })

            folio_sections[folio] = token.section

    return tokens, folio_sections


# ─── Transition Matrix ───

def build_folio_matrices(tokens):
    """Build per-folio 6-state transition matrices."""
    line_states = defaultdict(list)
    for t in tokens:
        line_states[(t['folio'], t['line'])].append(t['state'])

    folio_lines = defaultdict(dict)
    for (folio, line), states in line_states.items():
        folio_lines[folio][(folio, line)] = states

    results = {}
    for folio, line_dict in folio_lines.items():
        trans_counts = np.zeros((N_STATES, N_STATES), dtype=int)
        state_counts = np.zeros(N_STATES, dtype=int)

        for _, states in line_dict.items():
            for s in states:
                state_counts[STATE_IDX[s]] += 1
            for i in range(len(states) - 1):
                trans_counts[STATE_IDX[states[i]], STATE_IDX[states[i+1]]] += 1

        n_trans = int(trans_counts.sum())
        trans_prob = None
        if n_trans >= MIN_TRANSITIONS:
            row_sums = trans_counts.sum(axis=1, keepdims=True)
            row_sums = np.where(row_sums == 0, 1, row_sums)
            trans_prob = trans_counts / row_sums

        results[folio] = {
            'trans_counts': trans_counts,
            'state_counts': state_counts,
            'n_transitions': n_trans,
            'trans_prob': trans_prob,
        }
    return results


# ─── Bridge Geometry (replicate C1017.T5c) ───

def compute_bridge_geometry(tokens, folio_list):
    """Compute bridge centroid PC1/PC2 per folio via spectral embedding."""
    M, mid_to_idx = load_compatibility_matrix_and_index()
    if M is None:
        print("WARNING: Compatibility matrix not found. Bridge geometry = zeros.")
        return {f: 0.0 for f in folio_list}, {f: 0.0 for f in folio_list}

    K_EMBED = 100
    M = M.astype(np.float64)
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    k = min(K_EMBED, len(eigenvalues))
    evals = eigenvalues[:k]
    evecs = eigenvectors[:, :k]
    pos_evals = np.maximum(evals, 0)
    scaling = np.sqrt(pos_evals)
    embedding = evecs * scaling[np.newaxis, :]

    # Per-folio bridge centroid
    folio_middles = defaultdict(set)
    for t in tokens:
        if t['middle'] and t['middle'] in mid_to_idx:
            folio_middles[t['folio']].add(t['middle'])

    centroids = {}
    for folio in folio_list:
        mids = folio_middles.get(folio, set())
        if not mids:
            centroids[folio] = np.zeros(k)
            continue
        indices = [mid_to_idx[m] for m in mids if m in mid_to_idx]
        if not indices:
            centroids[folio] = np.zeros(k)
            continue
        centroids[folio] = embedding[indices].mean(axis=0)

    # PCA across folios
    X = np.array([centroids[f] for f in folio_list])
    X_centered = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    pc1_scores = X_centered @ Vt[0]
    pc2_scores = X_centered @ Vt[1]

    pc1_dict = {f: float(pc1_scores[i]) for i, f in enumerate(folio_list)}
    pc2_dict = {f: float(pc2_scores[i]) for i, f in enumerate(folio_list)}
    return pc1_dict, pc2_dict


# ─── New Predictors ───

def compute_new_predictors(tokens, folio_list):
    """Compute the 4 primary + 2 secondary new predictors."""
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t['folio']].append(t)

    predictors = {}
    for folio in folio_list:
        ftoks = folio_tokens[folio]
        n_total = len(ftoks)
        if n_total == 0:
            continue

        # ─── PRIMARY 1: Paragraph count ───
        # Count paragraph boundaries (par_initial flags)
        par_starts = sum(1 for t in ftoks if t['par_initial'])
        # If no par_initial flags, count by unique line=1 occurrences or default to 1
        if par_starts == 0:
            par_starts = 1
        paragraph_count = par_starts

        # ─── PRIMARY 2: Body HT density ───
        # HT = Human Track tokens. Per C800, BODY HT (not line-1) drives escape.
        # We approximate: HT tokens are line-1 tokens of each paragraph.
        # Actually, HT is identified by specific morphological patterns.
        # For this phase, we compute line-1 fraction as a proxy.
        # Better: identify tokens on line 1 of each paragraph
        line1_count = sum(1 for t in ftoks if t['par_initial'])
        body_count = n_total - line1_count
        # HT density per C746/C800: fraction of tokens that are on header lines
        # We invert: body_fraction = (n_total - header_tokens) / n_total
        # Actually what we want is the fraction of HT-like tokens in body lines
        # Since we can't directly identify HT tokens from class alone,
        # use paragraph header density as proxy
        ht_density_proxy = line1_count / n_total if n_total > 0 else 0

        # Better approach: Use line_num == 1 tokens as a broader HT proxy
        # Actually, let's compute this more carefully.
        # HT tokens are morphological subset of B that appear on line 1.
        # Per C870-C872: HT tokens use the same morphology but don't participate in grammar.
        # What C800 actually measured is: fraction of tokens at paragraph-initial positions.
        # Let's use two measures: (a) paragraph density, (b) line-1 density
        unique_lines = set()
        for t in ftoks:
            unique_lines.add((t['folio'], t['line']))
        lines_with_par_start = set()
        for t in ftoks:
            if t['par_initial']:
                lines_with_par_start.add((t['folio'], t['line']))

        # Line-1 tokens (broader definition)
        line1_tokens = [t for t in ftoks if t['line_num'] == 1]
        ht_line1_density = len(line1_tokens) / n_total if n_total > 0 else 0

        # ─── PRIMARY 3: Gatekeeper class fraction ───
        # C1007/C1008: classes {15,20,21,22,25} are AXM exit gatekeepers
        # Compute as fraction of AXM tokens that are gatekeepers
        axm_tokens = [t for t in ftoks if t['state'] == 'AXM']
        n_axm = len(axm_tokens)
        gatekeeper_in_axm = sum(1 for t in axm_tokens if t['is_gatekeeper'])
        gatekeeper_fraction = gatekeeper_in_axm / n_axm if n_axm > 0 else 0

        # Also compute as fraction of ALL tokens (alternative)
        gatekeeper_fraction_total = sum(1 for t in ftoks if t['is_gatekeeper']) / n_total

        # ─── PRIMARY 4: QO fraction of EN tokens ───
        # C605: EN = tokens with PREFIX qo, ch, or sh (the two-lane model)
        # QO lane vs CH/SH lane
        en_tokens = [t for t in ftoks if t['prefix'] in ('qo', 'ch', 'sh')]
        n_en = len(en_tokens)
        qo_count = sum(1 for t in en_tokens if t['prefix'] == 'qo')
        qo_fraction = qo_count / n_en if n_en > 0 else 0.5  # neutral if no EN tokens

        # ─── SECONDARY 5: Unique MIDDLE count ───
        unique_middles = set(t['middle'] for t in ftoks if t['middle'])
        vocab_size = len(unique_middles)

        # ─── SECONDARY 6: Line count ───
        line_count = len(unique_lines)

        predictors[folio] = {
            'paragraph_count': paragraph_count,
            'ht_line1_density': ht_line1_density,
            'par_header_density': line1_count / n_total if n_total > 0 else 0,
            'gatekeeper_fraction': gatekeeper_fraction,
            'gatekeeper_fraction_total': gatekeeper_fraction_total,
            'qo_fraction': qo_fraction,
            'n_en_tokens': n_en,
            'vocab_size': vocab_size,
            'line_count': line_count,
            'n_tokens': n_total,
        }

    return predictors


# ─── Regression Helpers ───

def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-10)


def ols_fit(X, y):
    """OLS regression. Returns beta, y_pred, ss_res, r2."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, y_pred, ss_res, r2


def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    """F-test for nested model comparison."""
    df_res = n_obs - k_full
    if df_res <= 0 or ss_res_full <= 0:
        return 0.0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


def build_dummies(labels):
    """Build dummy variables from categorical labels (drop first)."""
    unique = sorted(set(labels))
    if len(unique) <= 1:
        return np.zeros((len(labels), 0))
    dummies = np.zeros((len(labels), len(unique) - 1))
    for i, label in enumerate(labels):
        idx = unique.index(label)
        if idx > 0:
            dummies[i, idx - 1] = 1
    return dummies


def loo_cv_r2(X, y):
    """Leave-one-out cross-validated R2."""
    n = len(y)
    y_pred_loo = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_train, y_train = X[mask], y[mask]
        X_test = X[i:i+1]
        beta = np.linalg.lstsq(X_train, y_train, rcond=None)[0]
        y_pred_loo[i] = float(X_test @ beta)
    ss_res = np.sum((y - y_pred_loo) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


# ─── Main Analysis ───

def main():
    print("Loading data...")
    token_to_class = load_token_to_class()
    regimes = load_regime_assignments()
    archetypes = load_folio_archetypes()

    print("Building corpus...")
    tokens, folio_sections = build_corpus_data(token_to_class)
    print(f"  {len(tokens)} classified tokens")

    print("Building transition matrices...")
    folio_matrices = build_folio_matrices(tokens)

    # Filter to folios with sufficient transitions
    valid_folios = sorted([
        f for f, fm in folio_matrices.items()
        if fm['trans_prob'] is not None and f in regimes
    ])
    print(f"  {len(valid_folios)} folios with >= {MIN_TRANSITIONS} transitions")

    # ─── Dependent variable: AXM self-transition ───
    axm_self = np.array([
        folio_matrices[f]['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']]
        for f in valid_folios
    ])

    # ─── Baseline predictors (replicate C1017) ───
    print("Computing baseline predictors (C1017 replication)...")
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    prefix_entropy = []
    hazard_density = []
    regime_labels = []
    section_labels = []
    archetype_labels = []

    for f in valid_folios:
        ftoks = folio_token_groups[f]

        # PREFIX entropy
        pfx_counts = Counter(t['prefix'] for t in ftoks)
        pfx_total = sum(pfx_counts.values())
        pfx_probs = np.array(list(pfx_counts.values())) / pfx_total
        pfx_ent = -sum(p * np.log2(p) for p in pfx_probs if p > 0)
        prefix_entropy.append(pfx_ent)

        # Hazard density
        haz_frac = sum(1 for t in ftoks if t['is_hazard']) / len(ftoks)
        hazard_density.append(haz_frac)

        regime_labels.append(regimes.get(f, 'R0'))
        section_labels.append(folio_sections.get(f, 'X'))
        archetype_labels.append(archetypes.get(f, -1))

    prefix_entropy = np.array(prefix_entropy)
    hazard_density = np.array(hazard_density)

    # Bridge geometry PC1
    print("Computing bridge geometry...")
    bridge_pc1, bridge_pc2 = compute_bridge_geometry(tokens, valid_folios)
    bridge_pc1_arr = np.array([bridge_pc1[f] for f in valid_folios])

    # ─── New predictors ───
    print("Computing new predictors...")
    new_preds = compute_new_predictors(tokens, valid_folios)

    paragraph_count = np.array([new_preds[f]['paragraph_count'] for f in valid_folios])
    ht_line1_density = np.array([new_preds[f]['ht_line1_density'] for f in valid_folios])
    gatekeeper_fraction = np.array([new_preds[f]['gatekeeper_fraction'] for f in valid_folios])
    qo_fraction = np.array([new_preds[f]['qo_fraction'] for f in valid_folios])
    vocab_size = np.array([new_preds[f]['vocab_size'] for f in valid_folios])
    line_count = np.array([new_preds[f]['line_count'] for f in valid_folios])
    n_tokens_per_folio = np.array([new_preds[f]['n_tokens'] for f in valid_folios])

    # Residualize vocab_size against token count
    X_tok = np.column_stack([np.ones(len(valid_folios)), n_tokens_per_folio])
    beta_vocab = np.linalg.lstsq(X_tok, vocab_size, rcond=None)[0]
    vocab_residual = vocab_size - X_tok @ beta_vocab

    n = len(valid_folios)
    print(f"\n{'='*70}")
    print(f"  AXM RESIDUAL DECOMPOSITION -- n={n} folios")
    print(f"{'='*70}")

    # ─── S1: Replicate C1017 baseline ───
    print("\n--- S1: C1017 BASELINE REPLICATION ---")

    regime_dummies = build_dummies(regime_labels)
    section_dummies = build_dummies(section_labels)

    # Standardize continuous predictors
    pfx_z = standardize(prefix_entropy)
    haz_z = standardize(hazard_density)
    pc1_z = standardize(bridge_pc1_arr)

    # Baseline: REGIME + section only
    X_base = np.column_stack([np.ones(n), regime_dummies, section_dummies])
    _, _, ss_res_base, r2_base = ols_fit(X_base, axm_self)

    # C1017 full: + PREFIX entropy + hazard density + bridge PC1
    X_c1017 = np.column_stack([X_base, pfx_z, haz_z, pc1_z])
    beta_c1017, y_pred_c1017, ss_res_c1017, r2_c1017 = ols_fit(X_c1017, axm_self)

    # C1017 residuals
    residuals_c1017 = axm_self - y_pred_c1017

    ss_tot = np.sum((axm_self - axm_self.mean()) ** 2)
    delta_r2_c1017 = r2_c1017 - r2_base

    print(f"  R2 (REGIME+section):    {r2_base:.4f}")
    print(f"  R2 (C1017 full model):  {r2_c1017:.4f}")
    print(f"  dR2 (morphological):    {delta_r2_c1017:.4f}")
    print(f"  Residual variance:      {1 - r2_c1017:.4f}")

    k_c1017 = X_c1017.shape[1]

    # ─── S2: Univariate Screening ───
    print("\n--- S2: UNIVARIATE SCREENING (Bonferroni p < 0.0083) ---")

    new_predictor_names = [
        'paragraph_count', 'ht_line1_density', 'gatekeeper_fraction',
        'qo_fraction', 'vocab_residual', 'line_count'
    ]
    new_predictor_arrays = [
        paragraph_count, ht_line1_density, gatekeeper_fraction,
        qo_fraction, vocab_residual, line_count
    ]

    screening_results = {}
    for name, arr in zip(new_predictor_names, new_predictor_arrays):
        # Correlation with AXM self-transition
        rho_axm, p_axm = stats.spearmanr(arr, axm_self)

        # Correlation with C1017 residuals (more informative)
        rho_resid, p_resid = stats.spearmanr(arr, residuals_c1017)

        # Summary stats
        screening_results[name] = {
            'rho_axm': float(rho_axm),
            'p_axm': float(p_axm),
            'rho_residual': float(rho_resid),
            'p_residual': float(p_resid),
            'bonferroni_sig_axm': p_axm < 0.0083,
            'bonferroni_sig_resid': p_resid < 0.0083,
            'mean': float(arr.mean()),
            'std': float(arr.std()),
            'min': float(arr.min()),
            'max': float(arr.max()),
        }

        sig_marker_axm = '***' if p_axm < 0.0083 else ('*' if p_axm < 0.05 else '')
        sig_marker_resid = '***' if p_resid < 0.0083 else ('*' if p_resid < 0.05 else '')
        print(f"  {name:25s}  rho_axm={rho_axm:+.3f} (p={p_axm:.4f}){sig_marker_axm:4s}"
              f"  rho_resid={rho_resid:+.3f} (p={p_resid:.4f}){sig_marker_resid}")

    # ─── S3: Incremental R2 ───
    print("\n--- S3: INCREMENTAL R2 BEYOND C1017 BASELINE ---")

    incremental_results = {}
    for name, arr in zip(new_predictor_names, new_predictor_arrays):
        arr_z = standardize(arr)
        X_extended = np.column_stack([X_c1017, arr_z])
        _, _, ss_res_ext, r2_ext = ols_fit(X_extended, axm_self)
        delta_r2 = r2_ext - r2_c1017
        f_stat, p_f = f_test_increment(ss_res_c1017, ss_res_ext, 1, n, k_c1017 + 1)

        incremental_results[name] = {
            'r2_extended': float(r2_ext),
            'delta_r2': float(delta_r2),
            'f_stat': float(f_stat),
            'p_value': float(p_f),
            'significant': p_f < 0.0083,
        }

        sig_marker = '***' if p_f < 0.0083 else ('*' if p_f < 0.05 else '')
        print(f"  {name:25s}  dR2={delta_r2:+.4f}  F={f_stat:.2f}  p={p_f:.4f}  {sig_marker}")

    # ─── S4: Additive model with significant predictors ───
    print("\n--- S4: ADDITIVE MODEL (significant predictors) ---")

    # Select predictors with incremental p < 0.05 (liberal for model building)
    significant_preds = []
    significant_names = []
    for name, arr in zip(new_predictor_names, new_predictor_arrays):
        if incremental_results[name]['p_value'] < 0.05:
            significant_preds.append(standardize(arr))
            significant_names.append(name)

    if significant_preds:
        X_additive = np.column_stack([X_c1017] + [p.reshape(-1,1) for p in significant_preds])
        beta_add, y_pred_add, ss_res_add, r2_add = ols_fit(X_additive, axm_self)
        residuals_add = axm_self - y_pred_add
        delta_r2_add = r2_add - r2_c1017
        f_add, p_f_add = f_test_increment(ss_res_c1017, ss_res_add, len(significant_preds), n, X_additive.shape[1])

        print(f"  Predictors included: {significant_names}")
        print(f"  R2 (additive):    {r2_add:.4f}")
        print(f"  dR2 vs C1017:     {delta_r2_add:.4f}")
        print(f"  F-test:           F={f_add:.2f}, p={p_f_add:.6f}")

        # LOO CV for additive model
        loo_r2_add = loo_cv_r2(X_additive, axm_self)
        print(f"  LOO CV R2:        {loo_r2_add:.4f}")
        print(f"  Train-CV gap:     {r2_add - loo_r2_add:.4f}")
    else:
        print("  No predictors reached p < 0.05. Additive model = C1017 baseline.")
        r2_add = r2_c1017
        ss_res_add = ss_res_c1017
        delta_r2_add = 0.0
        f_add, p_f_add = 0.0, 1.0
        loo_r2_add = None
        residuals_add = residuals_c1017
        significant_names = []

    additive_model_results = {
        'predictors_included': significant_names,
        'r2_additive': float(r2_add),
        'delta_r2_vs_c1017': float(delta_r2_add),
        'f_stat': float(f_add),
        'p_value': float(p_f_add),
        'loo_cv_r2': float(loo_r2_add) if loo_r2_add is not None else None,
    }

    # ─── S5: Archetype-stratified slope analysis ───
    print("\n--- S5: ARCHETYPE-STRATIFIED ANALYSIS ---")

    archetype_analysis = {}
    unique_archetypes = sorted(set(archetype_labels))
    valid_archetypes = [a for a in unique_archetypes if a != -1]

    for arch in valid_archetypes:
        mask = np.array([a == arch for a in archetype_labels])
        n_arch = mask.sum()
        if n_arch < 5:
            continue

        y_arch = axm_self[mask]
        resid_arch = residuals_c1017[mask]

        arch_results = {'n': int(n_arch), 'mean_axm_self': float(y_arch.mean())}

        # Test each new predictor within archetype
        for name, arr in zip(new_predictor_names, new_predictor_arrays):
            arr_arch = arr[mask]
            if arr_arch.std() < 1e-10:
                arch_results[name] = {'rho': 0.0, 'p': 1.0}
                continue
            rho, p = stats.spearmanr(arr_arch, resid_arch)
            arch_results[name] = {'rho': float(rho), 'p': float(p)}

        archetype_analysis[f'archetype_{arch}'] = arch_results

    # Print summary
    for arch_key, arch_data in archetype_analysis.items():
        print(f"\n  {arch_key} (n={arch_data['n']}, mean AXM self={arch_data['mean_axm_self']:.3f}):")
        for name in new_predictor_names:
            if name in arch_data and isinstance(arch_data[name], dict):
                rho = arch_data[name]['rho']
                p = arch_data[name]['p']
                sig = '*' if p < 0.05 else ''
                print(f"    {name:25s}  rho={rho:+.3f} (p={p:.3f}){sig}")

    # ─── S5b: Mixed-effects approximation ───
    # Test whether archetype moderates the effect of each predictor
    # by including archetype × predictor interaction in the full model
    print("\n--- S5b: ARCHETYPE INTERACTION TESTS ---")

    interaction_tests = {}
    arch_array = np.array(archetype_labels)
    arch_dummies = build_dummies([str(a) for a in archetype_labels])

    for name, arr in zip(new_predictor_names[:4], new_predictor_arrays[:4]):
        arr_z = standardize(arr)
        # Model without interaction: C1017 + predictor
        X_no_int = np.column_stack([X_c1017, arr_z])
        _, _, ss_no_int, r2_no_int = ols_fit(X_no_int, axm_self)

        # Model with interaction: C1017 + predictor + archetype_dummies + predictor × archetype
        # But we need enough df. Only do this if we have enough folios.
        if n > k_c1017 + 1 + arch_dummies.shape[1] + arch_dummies.shape[1] + 5:
            interaction_terms = arr_z.reshape(-1, 1) * arch_dummies
            X_with_int = np.column_stack([X_c1017, arr_z, arch_dummies, interaction_terms])
            _, _, ss_with_int, r2_with_int = ols_fit(X_with_int, axm_self)

            df_extra = arch_dummies.shape[1]  # number of interaction terms
            f_int, p_int = f_test_increment(ss_no_int, ss_with_int, df_extra, n, X_with_int.shape[1])

            interaction_tests[name] = {
                'r2_without_interaction': float(r2_no_int),
                'r2_with_interaction': float(r2_with_int),
                'delta_r2_interaction': float(r2_with_int - r2_no_int),
                'f_stat': float(f_int),
                'p_value': float(p_int),
            }

            sig = '***' if p_int < 0.0083 else ('*' if p_int < 0.05 else '')
            print(f"  {name:25s}  dR2(interaction)={r2_with_int - r2_no_int:.4f}  "
                  f"F={f_int:.2f}  p={p_int:.4f}  {sig}")
        else:
            print(f"  {name:25s}  Insufficient df for interaction test")
            interaction_tests[name] = {'note': 'insufficient_df'}

    # ─── S6: Targeted Interactions ───
    print("\n--- S6: TARGETED INTERACTIONS ---")

    # Test interactions among significant predictors
    targeted_interactions = {}
    if len(significant_names) >= 2:
        for i in range(len(significant_names)):
            for j in range(i+1, len(significant_names)):
                name_i = significant_names[i]
                name_j = significant_names[j]
                idx_i = new_predictor_names.index(name_i)
                idx_j = new_predictor_names.index(name_j)
                arr_i_z = standardize(new_predictor_arrays[idx_i])
                arr_j_z = standardize(new_predictor_arrays[idx_j])
                interaction = arr_i_z * arr_j_z

                X_main = np.column_stack([X_c1017, arr_i_z, arr_j_z])
                _, _, ss_main, r2_main = ols_fit(X_main, axm_self)

                X_int = np.column_stack([X_main, interaction])
                _, _, ss_int, r2_int = ols_fit(X_int, axm_self)

                f_int, p_int = f_test_increment(ss_main, ss_int, 1, n, X_int.shape[1])

                key = f"{name_i}_x_{name_j}"
                targeted_interactions[key] = {
                    'r2_main': float(r2_main),
                    'r2_interaction': float(r2_int),
                    'delta_r2': float(r2_int - r2_main),
                    'f_stat': float(f_int),
                    'p_value': float(p_int),
                }

                sig = '***' if p_int < 0.0083 else ('*' if p_int < 0.05 else '')
                print(f"  {key:45s}  dR2={r2_int - r2_main:.4f}  F={f_int:.2f}  p={p_int:.4f}  {sig}")

    # Also test pre-specified interactions from expert advice
    prespec_interactions = [
        ('paragraph_count', 'hazard_density', hazard_density),
        ('gatekeeper_fraction', 'ht_line1_density', ht_line1_density),
    ]
    for name_a, name_b, arr_b in prespec_interactions:
        idx_a = new_predictor_names.index(name_a)
        arr_a_z = standardize(new_predictor_arrays[idx_a])
        arr_b_z = standardize(arr_b)
        interaction = arr_a_z * arr_b_z

        X_main = np.column_stack([X_c1017, arr_a_z, arr_b_z])
        _, _, ss_main, _ = ols_fit(X_main, axm_self)

        X_int = np.column_stack([X_main, interaction])
        _, _, ss_int, r2_int = ols_fit(X_int, axm_self)
        r2_main = 1 - ss_main / ss_tot

        f_int, p_int = f_test_increment(ss_main, ss_int, 1, n, X_int.shape[1])

        key = f"{name_a}_x_{name_b}_prespec"
        targeted_interactions[key] = {
            'r2_main': float(r2_main),
            'r2_interaction': float(r2_int),
            'delta_r2': float(r2_int - r2_main),
            'f_stat': float(f_int),
            'p_value': float(p_int),
        }
        sig = '***' if p_int < 0.0083 else ('*' if p_int < 0.05 else '')
        print(f"  {key:45s}  dR2={r2_int - r2_main:.4f}  F={f_int:.2f}  p={p_int:.4f}  {sig}")

    if not targeted_interactions:
        print("  No interactions tested (insufficient significant predictors)")

    # ─── S7: Random Forest on Residuals (Non-Linearity Check) ───
    print("\n--- S7: RANDOM FOREST NON-LINEARITY CHECK ---")

    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import cross_val_score

        # Build feature matrix for RF
        X_rf = np.column_stack([
            paragraph_count, ht_line1_density, gatekeeper_fraction,
            qo_fraction, vocab_residual, line_count
        ])

        # Predict C1017 residuals with RF
        rf = RandomForestRegressor(n_estimators=500, max_features='sqrt',
                                   min_samples_leaf=5, random_state=42)
        rf.fit(X_rf, residuals_c1017)
        rf_train_r2 = rf.score(X_rf, residuals_c1017)

        # Cross-validated R2 (5-fold)
        cv_scores = cross_val_score(rf, X_rf, residuals_c1017, cv=5, scoring='r2')
        rf_cv_r2 = cv_scores.mean()
        rf_cv_std = cv_scores.std()

        # Feature importances
        importances = rf.feature_importances_
        importance_dict = {
            name: float(imp)
            for name, imp in zip(new_predictor_names, importances)
        }

        # Permutation test for RF (is RF significantly better than null?)
        n_perm = 200
        perm_scores = []
        for _ in range(n_perm):
            y_perm = np.random.permutation(residuals_c1017)
            rf_perm = RandomForestRegressor(n_estimators=100, max_features='sqrt',
                                            min_samples_leaf=5, random_state=42)
            perm_cv = cross_val_score(rf_perm, X_rf, y_perm, cv=5, scoring='r2')
            perm_scores.append(perm_cv.mean())
        perm_scores = np.array(perm_scores)
        rf_z = (rf_cv_r2 - perm_scores.mean()) / (perm_scores.std() + 1e-10)
        rf_p = (perm_scores >= rf_cv_r2).mean()

        rf_results = {
            'train_r2': float(rf_train_r2),
            'cv_r2_mean': float(rf_cv_r2),
            'cv_r2_std': float(rf_cv_std),
            'cv_folds': [float(s) for s in cv_scores],
            'permutation_z': float(rf_z),
            'permutation_p': float(rf_p),
            'feature_importances': importance_dict,
            'non_linear_signal': rf_p < 0.05,
        }

        print(f"  Train R2 on residuals:   {rf_train_r2:.4f}")
        print(f"  CV R2 on residuals:      {rf_cv_r2:.4f} +/- {rf_cv_std:.4f}")
        print(f"  Permutation z-score:     {rf_z:.2f}")
        print(f"  Permutation p-value:     {rf_p:.4f}")
        print(f"  Non-linear signal:       {'YES' if rf_p < 0.05 else 'NO'}")
        print(f"\n  Feature importances:")
        for name in sorted(importance_dict, key=lambda x: importance_dict[x], reverse=True):
            print(f"    {name:25s}  {importance_dict[name]:.4f}")

    except ImportError:
        print("  sklearn not available -- skipping RF analysis")
        rf_results = {'note': 'sklearn_not_available'}

    # ─── S8: LOO CV for Best Model ───
    print("\n--- S8: LEAVE-ONE-OUT CV FOR MODELS ---")

    # C1017 baseline LOO
    loo_c1017 = loo_cv_r2(X_c1017, axm_self)
    print(f"  C1017 baseline LOO R2:  {loo_c1017:.4f} (train: {r2_c1017:.4f}, gap: {r2_c1017 - loo_c1017:.4f})")

    # Build best model: C1017 + all significant new predictors
    if significant_preds:
        X_best = np.column_stack([X_c1017] + [p.reshape(-1, 1) for p in significant_preds])
        _, _, _, r2_best = ols_fit(X_best, axm_self)
        loo_best = loo_cv_r2(X_best, axm_self)
        print(f"  Best additive LOO R2:   {loo_best:.4f} (train: {r2_best:.4f}, gap: {r2_best - loo_best:.4f})")
    else:
        r2_best = r2_c1017
        loo_best = loo_c1017

    cv_results = {
        'c1017_train_r2': float(r2_c1017),
        'c1017_loo_r2': float(loo_c1017),
        'c1017_gap': float(r2_c1017 - loo_c1017),
        'best_train_r2': float(r2_best),
        'best_loo_r2': float(loo_best),
        'best_gap': float(r2_best - loo_best),
        'best_predictors': significant_names,
    }

    # ─── S9: Residual Archetype Structure Check ───
    print("\n--- S9: RESIDUAL ARCHETYPE STRUCTURE ---")

    # Check if archetypes still explain residual variance after new predictors
    if significant_preds:
        residuals_best = axm_self - (X_best @ np.linalg.lstsq(X_best, axm_self, rcond=None)[0])
    else:
        residuals_best = residuals_c1017

    # ANOVA: residuals by archetype
    arch_groups_c1017 = defaultdict(list)
    arch_groups_best = defaultdict(list)
    for i, arch in enumerate(archetype_labels):
        if arch != -1:
            arch_groups_c1017[arch].append(residuals_c1017[i])
            arch_groups_best[arch].append(residuals_best[i])

    if len(arch_groups_c1017) >= 2:
        f_c1017, p_c1017 = stats.f_oneway(*[np.array(v) for v in arch_groups_c1017.values()])
        f_best, p_best = stats.f_oneway(*[np.array(v) for v in arch_groups_best.values()])

        print(f"  C1017 residual ~ archetype: F={f_c1017:.2f}, p={p_c1017:.6f}")
        print(f"  Best  residual ~ archetype: F={f_best:.2f}, p={p_best:.6f}")
        print(f"  Archetype structure {'REDUCED' if p_best > p_c1017 else 'NOT reduced'}")

        residual_archetype = {
            'c1017_F': float(f_c1017),
            'c1017_p': float(p_c1017),
            'best_F': float(f_best),
            'best_p': float(p_best),
            'reduced': p_best > p_c1017,
        }
    else:
        residual_archetype = {'note': 'insufficient_archetypes'}
        print("  Insufficient archetype labels for ANOVA")

    # ─── Summary ───
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  C1017 baseline R2:        {r2_c1017:.4f}")
    print(f"  Best additive R2:         {r2_best:.4f}")
    print(f"  Total dR2 from new preds: {r2_best - r2_c1017:.4f}")
    print(f"  LOO CV R2 (best):         {loo_best:.4f}")
    print(f"  Train-CV gap:             {r2_best - loo_best:.4f}")
    print(f"  Significant predictors:   {significant_names}")
    if isinstance(rf_results, dict) and 'non_linear_signal' in rf_results:
        print(f"  Non-linear signal (RF):   {'YES' if rf_results['non_linear_signal'] else 'NO'}")
    print(f"  Remaining unexplained:    {1 - r2_best:.4f}")

    # ─── Write Results ───
    results = {
        'phase_name': 'AXM_RESIDUAL_DECOMPOSITION',
        'phase_number': 357,
        'n_folios': n,
        'n_tokens': len(tokens),
        'dependent_variable': 'AXM_self_transition',
        'axm_self_stats': {
            'mean': float(axm_self.mean()),
            'std': float(axm_self.std()),
            'min': float(axm_self.min()),
            'max': float(axm_self.max()),
        },
        's1_baseline_replication': {
            'r2_regime_section': float(r2_base),
            'r2_c1017_full': float(r2_c1017),
            'delta_r2_morphological': float(delta_r2_c1017),
            'residual_variance': float(1 - r2_c1017),
        },
        's2_univariate_screening': screening_results,
        's3_incremental_r2': incremental_results,
        's4_additive_model': additive_model_results,
        's5_archetype_analysis': archetype_analysis,
        's5b_interaction_tests': interaction_tests,
        's6_targeted_interactions': targeted_interactions,
        's7_random_forest': rf_results,
        's8_loo_cv': cv_results,
        's9_residual_archetype': residual_archetype,
        'folio_data': {
            f: {
                'axm_self': float(axm_self[i]),
                'regime': regime_labels[i],
                'section': section_labels[i],
                'archetype': archetype_labels[i],
                'prefix_entropy': float(prefix_entropy[i]),
                'hazard_density': float(hazard_density[i]),
                'bridge_pc1': float(bridge_pc1_arr[i]),
                'paragraph_count': int(paragraph_count[i]),
                'ht_line1_density': float(ht_line1_density[i]),
                'gatekeeper_fraction': float(gatekeeper_fraction[i]),
                'qo_fraction': float(qo_fraction[i]),
                'vocab_size': int(vocab_size[i]),
                'vocab_residual': float(vocab_residual[i]),
                'line_count': int(line_count[i]),
                'n_tokens': int(n_tokens_per_folio[i]),
                'c1017_residual': float(residuals_c1017[i]),
            }
            for i, f in enumerate(valid_folios)
        },
        'predictions': {
            'P1': {'description': 'paragraph_count dR2 >= 0.05', 'threshold': 0.05},
            'P2': {'description': 'gatekeeper_fraction dR2 >= 0.05', 'threshold': 0.05},
            'P3': {'description': 'At least one predictor Bonferroni-significant with residuals', 'threshold': 0.0083},
            'P4': {'description': 'LOO CV R2 within 0.10 of training', 'threshold': 0.10},
            'P5': {'description': 'RF non-linear signal significant (p < 0.05)', 'threshold': 0.05},
            'P6': {'description': 'Residual archetype F reduced by >= 50%', 'threshold': 0.50},
            'P7': {'description': 'Total explained variance >= 0.65', 'threshold': 0.65},
        },
    }

    # Evaluate predictions
    results['predictions']['P1']['result'] = float(incremental_results.get('paragraph_count', {}).get('delta_r2', 0))
    results['predictions']['P1']['pass'] = incremental_results.get('paragraph_count', {}).get('delta_r2', 0) >= 0.05

    results['predictions']['P2']['result'] = float(incremental_results.get('gatekeeper_fraction', {}).get('delta_r2', 0))
    results['predictions']['P2']['pass'] = incremental_results.get('gatekeeper_fraction', {}).get('delta_r2', 0) >= 0.05

    any_bonferroni = any(v.get('bonferroni_sig_resid', False) for v in screening_results.values())
    results['predictions']['P3']['result'] = any_bonferroni
    results['predictions']['P3']['pass'] = any_bonferroni

    cv_gap = r2_best - loo_best
    results['predictions']['P4']['result'] = float(cv_gap)
    results['predictions']['P4']['pass'] = abs(cv_gap) < 0.10

    if isinstance(rf_results, dict) and 'non_linear_signal' in rf_results:
        results['predictions']['P5']['result'] = rf_results.get('permutation_p', 1.0)
        results['predictions']['P5']['pass'] = rf_results.get('non_linear_signal', False)
    else:
        results['predictions']['P5']['result'] = None
        results['predictions']['P5']['pass'] = False

    if isinstance(residual_archetype, dict) and 'c1017_F' in residual_archetype:
        f_reduction = 1 - residual_archetype['best_F'] / residual_archetype['c1017_F'] if residual_archetype['c1017_F'] > 0 else 0
        results['predictions']['P6']['result'] = float(f_reduction)
        results['predictions']['P6']['pass'] = f_reduction >= 0.50
    else:
        results['predictions']['P6']['result'] = None
        results['predictions']['P6']['pass'] = False

    results['predictions']['P7']['result'] = float(r2_best)
    results['predictions']['P7']['pass'] = r2_best >= 0.65

    n_pass = sum(1 for p in results['predictions'].values() if p.get('pass', False))
    n_total = len(results['predictions'])
    results['verdict'] = f"{n_pass}/{n_total} PASS"

    print(f"\n--- PREDICTION OUTCOMES ---")
    for pk, pv in results['predictions'].items():
        status = 'PASS' if pv.get('pass') else 'FAIL'
        print(f"  {pk}: {pv['description']} -> {pv.get('result')} -> {status}")
    print(f"\n  VERDICT: {results['verdict']}")

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'axm_residual_decomposition.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults written to: {out_path}")


if __name__ == '__main__':
    main()
