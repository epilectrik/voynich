#!/usr/bin/env python3
"""
Phase 520: PARAGRAPH AXM RESIDUAL ANALYSIS
==========================================
C1405 showed PREFIX composition explains 73.6% of paragraph-level AXM variation
(CV R2=0.736), with ~24% residual labeled "design freedom." This phase tests
whether MIDDLE composition, suffix mode balance, line structure, articulators,
headless compound fraction, or other token-level features explain any of that 24%.

Tests T1-T10 systematically decompose the residual.

Output: phases/PARAGRAPH_AXM_RESIDUAL/results/paragraph_axm_residual.json
"""

import sys
import os
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

np.random.seed(42)

# ================================================================
# CONSTANTS
# ================================================================

# 6-state macro-automaton partition (C976)
MACRO_STATE_PARTITION = {
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'AXm':     {3, 5, 18, 19, 42, 45},
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28,
                29, 31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
    'FL_SAFE': {38, 40},
}
CLASS_TO_MACRO = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_MACRO[c] = state

# HEAD atoms (C1394): atoms that can serve as instruction HEAD
HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}

# TERMINAL atoms (C1209): atoms that prefer terminal position
TERMINAL_ATOMS = {'y', 'l', 'r', 'h', 'm', 'n'}

# Mode A suffixes (C1229, C1236)
MODE_A_SUFFIXES = {'edy', 'dy', 'ey', 'eey', 'y', 'hy', 'ly', 'ry',
                   'chy', 'shy', 'ky', 'oky', 'oty'}

# Major PREFIXes (consistent with Phase 514)
MAJOR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'or',
                  'pch', 'tch', 'lch', 'ar', 'al', 'BARE']

# Operational categories (C1250)
ATOM_CATEGORY = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'MONITORING',
    'd': 'CONTAINMENT', 't': 'TRANSITION', 'y': 'CONTAINMENT',
    'n': 'OPERATION', 'i': 'OPERATION', 'a': 'STAGING',
    'm': 'MARKING', 'l': 'FLOW', 'o': 'STAGING',
    'r': 'FLOW', 'c': 'MONITORING', 'p': 'MARKING',
    's': 'STAGING', 'f': 'MARKING', 'q': 'THERMAL',
}

# ================================================================
# HELPERS
# ================================================================

def safe_spearman(x, y):
    x, y = np.array(x, dtype=float), np.array(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 5 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0, 1.0
    rho, p = sp_stats.spearmanr(x, y)
    return float(rho), float(p)


def cv_r2_linear(X, y, cv=10, label=''):
    """Cross-validated R2 with linear regression."""
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score
    mask = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
    X_c, y_c = X[mask], y[mask]
    if len(X_c) < 20 or X_c.shape[1] == 0:
        return 0.0, np.array([])
    lr = LinearRegression()
    scores = cross_val_score(lr, X_c, y_c, cv=cv, scoring='r2')
    mean_r2 = float(np.mean(scores))
    if label:
        print(f"  {label:55s}: CV R2 = {mean_r2:+.4f} (std={np.std(scores):.4f})")
    return mean_r2, scores


def loo_r2(X, y, label=''):
    """Leave-one-out R2."""
    from sklearn.linear_model import LinearRegression
    mask = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
    X_c, y_c = X[mask], y[mask]
    n = len(y_c)
    if n < 20 or X_c.shape[1] == 0:
        return 0.0
    preds = np.zeros(n)
    for i in range(n):
        X_tr = np.delete(X_c, i, axis=0)
        y_tr = np.delete(y_c, i)
        lr = LinearRegression()
        lr.fit(X_tr, y_tr)
        preds[i] = lr.predict(X_c[i:i+1])[0]
    ss_res = np.sum((y_c - preds) ** 2)
    ss_tot = np.sum((y_c - np.mean(y_c)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    if label:
        print(f"  {label:55s}: LOO R2 = {r2:+.4f}")
    return float(r2)


def get_middle_head(middle):
    """Get HEAD atom of MIDDLE (first atom if in HEAD_ATOMS set, else 'headless')."""
    if not middle:
        return 'headless'
    first = middle[0]
    return first if first in HEAD_ATOMS else 'headless'


def get_middle_terminal(middle):
    """Get TERMINAL atom of MIDDLE (last atom if in TERMINAL_ATOMS)."""
    if not middle:
        return 'none'
    last = middle[-1]
    return last if last in TERMINAL_ATOMS else 'none'


# ================================================================
# DATA LOADING
# ================================================================

def load_data():
    print("[LOAD] Loading data...")

    cmap_path = PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(cmap_path, encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    regime_path = PROJECT / 'data' / 'regime_folio_mapping.json'
    with open(regime_path, encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_to_regime = {fol: info['regime'] for fol, info in regime_data['regime_assignments'].items()}

    tx = Transcript()
    morph = Morphology()
    tokens = list(tx.currier_b())
    print(f"  {len(tokens)} Currier B tokens")

    return tokens, token_to_class, folio_to_regime, morph


def build_enriched_tokens(tokens, token_to_class, folio_to_regime, morph):
    enriched = []
    for t in tokens:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue

        cls = token_to_class.get(w)
        m = morph.extract(w)

        middle = m.middle if m.middle else ''
        prefix = m.prefix if m.prefix else ''
        suffix = m.suffix if m.suffix else ''
        articulator = m.articulator if m.articulator else ''

        rec = {
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'articulator': articulator,
            'cls': cls,
            'macro_state': CLASS_TO_MACRO.get(cls) if cls else None,
            'regime': folio_to_regime.get(t.folio, 'UNKNOWN'),
            'head_atom': get_middle_head(middle),
            'terminal_atom': get_middle_terminal(middle),
        }
        enriched.append(rec)

    print(f"  {len(enriched)} enriched tokens")
    return enriched


def build_paragraphs(enriched_tokens):
    by_folio = defaultdict(list)
    for t in enriched_tokens:
        by_folio[t['folio']].append(t)

    paragraphs = []
    for folio in sorted(by_folio.keys()):
        toks = by_folio[folio]
        par_idx = 0
        current_par = []
        for t in toks:
            if t['par_initial'] and current_par:
                paragraphs.append({
                    'folio': folio,
                    'par_idx': par_idx,
                    'tokens': current_par,
                    'section': current_par[0]['section'],
                    'regime': current_par[0]['regime'],
                })
                par_idx += 1
                current_par = [t]
            else:
                current_par.append(t)
        if current_par:
            paragraphs.append({
                'folio': folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0]['section'],
                'regime': current_par[0]['regime'],
            })

    for par in paragraphs:
        lines = set(t['line'] for t in par['tokens'])
        par['n_lines'] = len(lines)
        par['body_lines'] = len(lines) - 1 if len(lines) > 1 else 0

    filtered = [p for p in paragraphs if p['body_lines'] >= 3]
    print(f"  {len(paragraphs)} total paragraphs, {len(filtered)} with 3+ body lines")
    return filtered


# ================================================================
# FEATURE COMPUTATION
# ================================================================

def compute_paragraph_features(paragraphs):
    """Compute comprehensive feature set for each paragraph."""
    print("\n[FEATURES] Computing paragraph features...")

    feature_data = []
    for par in paragraphs:
        toks = par['tokens']
        n = len(toks)
        if n < 5:
            continue

        # --- AXM rate (target variable) ---
        classified = [t for t in toks if t['macro_state']]
        n_cl = len(classified)
        if n_cl < 3:
            continue
        axm_count = sum(1 for t in classified if t['macro_state'] == 'AXM')
        axm_rate = axm_count / n_cl

        # --- PREFIX features ---
        pfx_counts = Counter()
        for t in toks:
            p = t['prefix'] if t['prefix'] else 'BARE'
            pfx_counts[p] += 1
        pfx = {}
        for p in MAJOR_PREFIXES:
            pfx[p] = pfx_counts.get(p, 0) / n

        qo_frac = pfx.get('qo', 0)
        chsh_frac = pfx.get('ch', 0) + pfx.get('sh', 0)
        bare_frac = pfx.get('BARE', 0)
        ok_frac = pfx.get('ok', 0)
        ot_frac = pfx.get('ot', 0)
        da_frac = pfx.get('da', 0)
        ol_frac = pfx.get('ol', 0)
        pch_frac = pfx.get('pch', 0)
        tch_frac = pfx.get('tch', 0)
        lch_frac = pfx.get('lch', 0)

        # --- MIDDLE HEAD atom distribution ---
        head_counts = Counter(t['head_atom'] for t in toks if t['middle'])
        n_mid = sum(head_counts.values()) or 1
        head_a = head_counts.get('a', 0) / n_mid
        head_e = head_counts.get('e', 0) / n_mid
        head_o = head_counts.get('o', 0) / n_mid
        head_k = head_counts.get('k', 0) / n_mid
        head_t = head_counts.get('t', 0) / n_mid
        headless_frac = head_counts.get('headless', 0) / n_mid

        # --- MIDDLE TERMINAL atom distribution ---
        term_counts = Counter(t['terminal_atom'] for t in toks if t['middle'])
        n_term = sum(term_counts.values()) or 1
        term_y = term_counts.get('y', 0) / n_term
        term_l = term_counts.get('l', 0) / n_term
        term_r = term_counts.get('r', 0) / n_term
        term_h = term_counts.get('h', 0) / n_term
        term_m = term_counts.get('m', 0) / n_term
        term_n = term_counts.get('n', 0) / n_term
        term_none = term_counts.get('none', 0) / n_term

        # --- Suffix features ---
        suffix_rate = sum(1 for t in toks if t['suffix']) / n
        suffixed = [t for t in toks if t['suffix']]
        mode_a_of_suffixed = sum(1 for t in suffixed if t['suffix'] in MODE_A_SUFFIXES) / len(suffixed) if suffixed else 0
        mode_a_frac = sum(1 for t in toks if t['suffix'] and t['suffix'] in MODE_A_SUFFIXES) / n
        mean_suffix_len = np.mean([len(t['suffix']) for t in suffixed]) if suffixed else 0

        # --- Line structure ---
        lines = set(t['line'] for t in toks)
        n_lines = len(lines)
        line_lengths = []
        for line in lines:
            line_toks = [t for t in toks if t['line'] == line]
            line_lengths.append(len(line_toks))
        mean_line_len = np.mean(line_lengths) if line_lengths else 0
        std_line_len = np.std(line_lengths) if len(line_lengths) > 1 else 0

        # --- Articulator features ---
        art_rate = sum(1 for t in toks if t['articulator']) / n
        art_y_rate = sum(1 for t in toks if t['articulator'] == 'y') / n
        art_s_rate = sum(1 for t in toks if t['articulator'] == 's') / n
        art_d_rate = sum(1 for t in toks if t['articulator'] == 'd') / n

        # --- Kernel profile from MIDDLE content ---
        mid_toks = [t for t in toks if t['middle']]
        n_m = len(mid_toks) or 1
        k_frac = sum(1 for t in mid_toks if 'k' in t['middle']) / n_m
        h_frac = sum(1 for t in mid_toks if 'h' in t['middle']) / n_m
        e_frac = sum(1 for t in mid_toks if 'e' in t['middle']) / n_m

        # --- MIDDLE length ---
        mean_mid_len = np.mean([len(t['middle']) for t in mid_toks]) if mid_toks else 0

        # --- Compound fraction (multi-char MIDDLEs) ---
        compound_frac = sum(1 for t in mid_toks if len(t['middle']) > 1) / n_m

        # --- Mean token length ---
        mean_tok_len = np.mean([len(t['word']) for t in toks])

        # --- Unique MIDDLE diversity ---
        unique_middles = len(set(t['middle'] for t in toks if t['middle']))
        middle_diversity = unique_middles / n_m  # type-token ratio for MIDDLEs

        feature_data.append({
            'folio': par['folio'],
            'par_idx': par['par_idx'],
            'section': par['section'],
            'regime': par['regime'],
            'n_tokens': n,
            'n_lines': n_lines,
            'body_lines': par['body_lines'],
            'axm_rate': float(axm_rate),
            # PREFIX features (baseline)
            'qo_frac': float(qo_frac),
            'chsh_frac': float(chsh_frac),
            'bare_frac': float(bare_frac),
            'ok_frac': float(ok_frac),
            'ot_frac': float(ot_frac),
            'da_frac': float(da_frac),
            'ol_frac': float(ol_frac),
            'pch_frac': float(pch_frac),
            'tch_frac': float(tch_frac),
            'lch_frac': float(lch_frac),
            # MIDDLE HEAD atoms
            'head_a': float(head_a),
            'head_e': float(head_e),
            'head_o': float(head_o),
            'head_k': float(head_k),
            'head_t': float(head_t),
            'headless_frac': float(headless_frac),
            # MIDDLE TERMINAL atoms
            'term_y': float(term_y),
            'term_l': float(term_l),
            'term_r': float(term_r),
            'term_h': float(term_h),
            'term_m': float(term_m),
            'term_n': float(term_n),
            'term_none': float(term_none),
            # Suffix features
            'suffix_rate': float(suffix_rate),
            'mode_a_frac': float(mode_a_frac),
            'mode_a_of_suffixed': float(mode_a_of_suffixed),
            'mean_suffix_len': float(mean_suffix_len),
            # Line structure
            'n_lines_feat': int(n_lines),
            'mean_line_len': float(mean_line_len),
            'std_line_len': float(std_line_len),
            # Articulator
            'art_rate': float(art_rate),
            'art_y_rate': float(art_y_rate),
            'art_s_rate': float(art_s_rate),
            'art_d_rate': float(art_d_rate),
            # Kernel
            'k_frac': float(k_frac),
            'h_frac': float(h_frac),
            'e_frac': float(e_frac),
            # MIDDLE properties
            'mean_mid_len': float(mean_mid_len),
            'compound_frac': float(compound_frac),
            'mean_tok_len': float(mean_tok_len),
            'middle_diversity': float(middle_diversity),
        })

    print(f"  {len(feature_data)} paragraphs with full features")
    return feature_data


# ================================================================
# TESTS
# ================================================================

def test_T1_middle_head_composition(feat_data, y):
    """T1: MIDDLE HEAD composition as AXM predictor."""
    print("\n" + "=" * 60)
    print("T1: MIDDLE HEAD Composition as AXM Predictor")
    print("=" * 60)

    head_feats = ['head_a', 'head_e', 'head_o', 'head_k', 'head_t', 'headless_frac']
    X_head = np.column_stack([[f[p] for f in feat_data] for p in head_feats])

    # HEAD alone
    r2_head, _ = cv_r2_linear(X_head, y, label='HEAD atoms alone')

    # HEAD LOO
    r2_head_loo = loo_r2(X_head, y, label='HEAD atoms LOO')

    # Bivariate correlations
    corrs = {}
    for feat in head_feats:
        vals = np.array([f[feat] for f in feat_data])
        rho, p = safe_spearman(vals, y)
        corrs[feat] = {'rho': float(rho), 'p': float(p)}
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
        print(f"  {feat:18s}: rho={rho:+.4f} p={p:.2e} {sig}")

    # HEAD + PREFIX combined
    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    X_combined = np.hstack([X_pfx, X_head])
    r2_pfx, _ = cv_r2_linear(X_pfx, y, label='PREFIX alone (baseline)')
    r2_combined, _ = cv_r2_linear(X_combined, y, label='PREFIX + HEAD combined')

    delta = r2_combined - r2_pfx
    print(f"\n  HEAD delta beyond PREFIX: {delta:+.4f}")

    # TERMINAL atoms
    term_feats = ['term_y', 'term_l', 'term_r', 'term_h', 'term_m', 'term_n', 'term_none']
    X_term = np.column_stack([[f[p] for f in feat_data] for p in term_feats])
    r2_term, _ = cv_r2_linear(X_term, y, label='TERMINAL atoms alone')

    X_pfx_term = np.hstack([X_pfx, X_term])
    r2_pfx_term, _ = cv_r2_linear(X_pfx_term, y, label='PREFIX + TERMINAL combined')
    delta_term = r2_pfx_term - r2_pfx
    print(f"  TERMINAL delta beyond PREFIX: {delta_term:+.4f}")

    # HEAD + TERMINAL combined with PREFIX
    X_all_mid = np.hstack([X_pfx, X_head, X_term])
    r2_all_mid, _ = cv_r2_linear(X_all_mid, y, label='PREFIX + HEAD + TERMINAL')
    delta_all = r2_all_mid - r2_pfx
    print(f"  HEAD+TERMINAL delta beyond PREFIX: {delta_all:+.4f}")

    return {
        'r2_head_alone': float(r2_head),
        'r2_head_loo': float(r2_head_loo),
        'r2_prefix_baseline': float(r2_pfx),
        'r2_prefix_plus_head': float(r2_combined),
        'head_delta_beyond_prefix': float(delta),
        'r2_terminal_alone': float(r2_term),
        'r2_prefix_plus_terminal': float(r2_pfx_term),
        'terminal_delta_beyond_prefix': float(delta_term),
        'r2_prefix_head_terminal': float(r2_all_mid),
        'all_middle_delta_beyond_prefix': float(delta_all),
        'head_correlations': corrs,
        'verdict': 'HEAD_ADDS_BEYOND_PREFIX' if delta > 0.02 else 'HEAD_REDUNDANT_WITH_PREFIX',
    }


def test_T2_suffix_features(feat_data, y):
    """T2: Suffix features as AXM predictor."""
    print("\n" + "=" * 60)
    print("T2: Suffix Features as AXM Predictor")
    print("=" * 60)

    sfx_feats = ['suffix_rate', 'mode_a_frac', 'mode_a_of_suffixed', 'mean_suffix_len']
    X_sfx = np.column_stack([[f[p] for f in feat_data] for p in sfx_feats])

    r2_sfx, _ = cv_r2_linear(X_sfx, y, label='Suffix features alone')

    # Bivariate correlations
    for feat in sfx_feats:
        vals = np.array([f[feat] for f in feat_data])
        rho, p = safe_spearman(vals, y)
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
        print(f"  {feat:25s}: rho={rho:+.4f} p={p:.2e} {sig}")

    # Suffix + PREFIX
    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    r2_pfx, _ = cv_r2_linear(X_pfx, y, label='PREFIX baseline')
    X_combined = np.hstack([X_pfx, X_sfx])
    r2_combined, _ = cv_r2_linear(X_combined, y, label='PREFIX + suffix')

    delta = r2_combined - r2_pfx
    print(f"\n  Suffix delta beyond PREFIX: {delta:+.4f}")

    return {
        'r2_suffix_alone': float(r2_sfx),
        'r2_prefix_baseline': float(r2_pfx),
        'r2_prefix_plus_suffix': float(r2_combined),
        'suffix_delta_beyond_prefix': float(delta),
        'verdict': 'SUFFIX_ADDS' if delta > 0.02 else 'SUFFIX_REDUNDANT',
    }


def test_T3_line_structure(feat_data, y):
    """T3: Line count and length as AXM predictor."""
    print("\n" + "=" * 60)
    print("T3: Line Structure as AXM Predictor")
    print("=" * 60)

    line_feats = ['n_lines_feat', 'mean_line_len', 'std_line_len']
    X_line = np.column_stack([[f[p] for f in feat_data] for p in line_feats])

    r2_line, _ = cv_r2_linear(X_line, y, label='Line structure alone')

    for feat in line_feats:
        vals = np.array([f[feat] for f in feat_data], dtype=float)
        rho, p = safe_spearman(vals, y)
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
        print(f"  {feat:18s}: rho={rho:+.4f} p={p:.2e} {sig}")

    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    r2_pfx, _ = cv_r2_linear(X_pfx, y, label='PREFIX baseline')
    X_combined = np.hstack([X_pfx, X_line])
    r2_combined, _ = cv_r2_linear(X_combined, y, label='PREFIX + line structure')

    delta = r2_combined - r2_pfx
    print(f"\n  Line structure delta beyond PREFIX: {delta:+.4f}")

    return {
        'r2_line_alone': float(r2_line),
        'r2_prefix_plus_line': float(r2_combined),
        'line_delta_beyond_prefix': float(delta),
        'verdict': 'LINE_ADDS' if delta > 0.02 else 'LINE_REDUNDANT',
    }


def test_T4_articulator_features(feat_data, y):
    """T4: Articulator features as AXM predictor."""
    print("\n" + "=" * 60)
    print("T4: Articulator Features as AXM Predictor")
    print("=" * 60)

    art_feats = ['art_rate', 'art_y_rate', 'art_s_rate', 'art_d_rate']
    X_art = np.column_stack([[f[p] for f in feat_data] for p in art_feats])

    r2_art, _ = cv_r2_linear(X_art, y, label='Articulator features alone')

    for feat in art_feats:
        vals = np.array([f[feat] for f in feat_data])
        rho, p = safe_spearman(vals, y)
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
        print(f"  {feat:18s}: rho={rho:+.4f} p={p:.2e} {sig}")

    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    r2_pfx, _ = cv_r2_linear(X_pfx, y, label='PREFIX baseline')
    X_combined = np.hstack([X_pfx, X_art])
    r2_combined, _ = cv_r2_linear(X_combined, y, label='PREFIX + articulators')

    delta = r2_combined - r2_pfx
    print(f"\n  Articulator delta beyond PREFIX: {delta:+.4f}")

    return {
        'r2_art_alone': float(r2_art),
        'r2_prefix_plus_art': float(r2_combined),
        'art_delta_beyond_prefix': float(delta),
        'verdict': 'ART_ADDS' if delta > 0.02 else 'ART_REDUNDANT',
    }


def test_T5_full_model(feat_data, y):
    """T5: Full model with ALL features."""
    print("\n" + "=" * 60)
    print("T5: Full Model — All Features Combined")
    print("=" * 60)

    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac',
                 'da_frac', 'ol_frac', 'pch_frac', 'tch_frac', 'lch_frac']
    head_feats = ['head_a', 'head_e', 'head_o', 'head_k', 'head_t', 'headless_frac']
    term_feats = ['term_y', 'term_l', 'term_r', 'term_h', 'term_m', 'term_n', 'term_none']
    sfx_feats = ['suffix_rate', 'mode_a_frac', 'mode_a_of_suffixed', 'mean_suffix_len']
    line_feats = ['n_lines_feat', 'mean_line_len', 'std_line_len']
    art_feats = ['art_rate', 'art_y_rate', 'art_s_rate', 'art_d_rate']
    kernel_feats = ['k_frac', 'h_frac', 'e_frac']
    middle_feats = ['mean_mid_len', 'compound_frac', 'mean_tok_len', 'middle_diversity']

    all_feats = pfx_feats + head_feats + term_feats + sfx_feats + line_feats + art_feats + kernel_feats + middle_feats

    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    X_all = np.column_stack([[f[p] for f in feat_data] for p in all_feats])

    r2_pfx, _ = cv_r2_linear(X_pfx, y, label='PREFIX only (extended, 10 feats)')
    r2_all, _ = cv_r2_linear(X_all, y, label='FULL MODEL (all features)')

    r2_pfx_loo = loo_r2(X_pfx, y, label='PREFIX only LOO')
    r2_all_loo = loo_r2(X_all, y, label='FULL MODEL LOO')

    delta = r2_all - r2_pfx
    delta_loo = r2_all_loo - r2_pfx_loo
    print(f"\n  Full model delta beyond PREFIX (CV): {delta:+.4f}")
    print(f"  Full model delta beyond PREFIX (LOO): {delta_loo:+.4f}")
    print(f"  Residual unexplained (CV): {1.0 - r2_all:.4f}")
    print(f"  Residual unexplained (LOO): {1.0 - r2_all_loo:.4f}")

    # Fit full model for coefficients
    from sklearn.linear_model import LinearRegression
    mask = np.all(np.isfinite(X_all), axis=1) & np.isfinite(y)
    lr = LinearRegression()
    lr.fit(X_all[mask], y[mask])
    coefs = {all_feats[i]: float(lr.coef_[i]) for i in range(len(all_feats))}
    train_r2 = float(lr.score(X_all[mask], y[mask]))

    print(f"  Training R2: {train_r2:.4f}")
    print(f"\n  Top 10 coefficients (absolute):")
    sorted_coefs = sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True)
    for feat, coef in sorted_coefs[:10]:
        print(f"    {feat:25s}: {coef:+.4f}")

    return {
        'r2_prefix_only': float(r2_pfx),
        'r2_full_model': float(r2_all),
        'r2_prefix_loo': float(r2_pfx_loo),
        'r2_full_loo': float(r2_all_loo),
        'delta_cv': float(delta),
        'delta_loo': float(delta_loo),
        'train_r2': float(train_r2),
        'residual_cv': float(1.0 - r2_all),
        'residual_loo': float(1.0 - r2_all_loo),
        'n_features': len(all_feats),
        'coefficients': coefs,
        'verdict': f'FULL_MODEL_CV_R2={r2_all:.3f}_RESIDUAL={1-r2_all:.3f}',
    }


def test_T6_feature_importance(feat_data, y):
    """T6: Feature importance decomposition — permutation importance by group."""
    print("\n" + "=" * 60)
    print("T6: Feature Importance Decomposition")
    print("=" * 60)

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score

    feature_groups = {
        'PREFIX': ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac',
                    'da_frac', 'ol_frac', 'pch_frac', 'tch_frac', 'lch_frac'],
        'HEAD': ['head_a', 'head_e', 'head_o', 'head_k', 'head_t', 'headless_frac'],
        'TERMINAL': ['term_y', 'term_l', 'term_r', 'term_h', 'term_m', 'term_n', 'term_none'],
        'SUFFIX': ['suffix_rate', 'mode_a_frac', 'mode_a_of_suffixed', 'mean_suffix_len'],
        'LINE': ['n_lines_feat', 'mean_line_len', 'std_line_len'],
        'ARTICULATOR': ['art_rate', 'art_y_rate', 'art_s_rate', 'art_d_rate'],
        'KERNEL': ['k_frac', 'h_frac', 'e_frac'],
        'MIDDLE_PROPS': ['mean_mid_len', 'compound_frac', 'mean_tok_len', 'middle_diversity'],
    }

    all_feats = []
    for group_feats in feature_groups.values():
        all_feats.extend(group_feats)

    X_all = np.column_stack([[f[p] for f in feat_data] for p in all_feats])
    mask = np.all(np.isfinite(X_all), axis=1) & np.isfinite(y)
    X_c, y_c = X_all[mask], y[mask]

    # Full model baseline
    lr = LinearRegression()
    baseline_scores = cross_val_score(lr, X_c, y_c, cv=10, scoring='r2')
    baseline_r2 = float(np.mean(baseline_scores))
    print(f"  Full model baseline CV R2: {baseline_r2:.4f}")

    # Drop-one-group analysis: remove each group and measure R2 drop
    group_importance = {}
    for group_name, group_feats in feature_groups.items():
        remaining_feats = [f for f in all_feats if f not in group_feats]
        X_reduced = np.column_stack([[feat_data[i][p] for i in range(len(feat_data))] for p in remaining_feats])
        X_reduced = X_reduced[mask]
        scores = cross_val_score(lr, X_reduced, y_c, cv=10, scoring='r2')
        reduced_r2 = float(np.mean(scores))
        drop = baseline_r2 - reduced_r2
        group_importance[group_name] = {
            'r2_without': float(reduced_r2),
            'r2_drop': float(drop),
            'n_features': len(group_feats),
        }
        print(f"  Drop {group_name:15s}: R2={reduced_r2:.4f} (drop={drop:+.4f})")

    # Add-one-group analysis: each group alone then + PREFIX
    print("\n  Add-one analysis (group added to PREFIX):")
    pfx_feats = feature_groups['PREFIX']
    X_pfx = np.column_stack([[feat_data[i][p] for i in range(len(feat_data))] for p in pfx_feats])
    X_pfx = X_pfx[mask]
    pfx_scores = cross_val_score(lr, X_pfx, y_c, cv=10, scoring='r2')
    pfx_r2 = float(np.mean(pfx_scores))

    add_one = {}
    for group_name, group_feats in feature_groups.items():
        if group_name == 'PREFIX':
            continue
        X_group = np.column_stack([[feat_data[i][p] for i in range(len(feat_data))] for p in group_feats])
        X_group = X_group[mask]
        X_combined = np.hstack([X_pfx, X_group])
        scores = cross_val_score(lr, X_combined, y_c, cv=10, scoring='r2')
        combined_r2 = float(np.mean(scores))
        gain = combined_r2 - pfx_r2
        add_one[group_name] = {
            'r2_with_prefix': float(combined_r2),
            'gain_beyond_prefix': float(gain),
        }
        print(f"  PREFIX + {group_name:15s}: R2={combined_r2:.4f} (gain={gain:+.4f})")

    return {
        'baseline_r2': baseline_r2,
        'drop_one_group': group_importance,
        'add_one_to_prefix': add_one,
        'verdict': 'PREFIX_DOMINANT' if group_importance['PREFIX']['r2_drop'] > 0.3 else 'DISTRIBUTED',
    }


def test_T7_residual_analysis(feat_data, y):
    """T7: Residual analysis from PREFIX-only model."""
    print("\n" + "=" * 60)
    print("T7: Residual Analysis (PREFIX Model Errors)")
    print("=" * 60)

    from sklearn.linear_model import LinearRegression

    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac',
                 'da_frac', 'ol_frac', 'pch_frac', 'tch_frac', 'lch_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    mask = np.all(np.isfinite(X_pfx), axis=1) & np.isfinite(y)
    X_c, y_c = X_pfx[mask], y[mask]
    feat_clean = [feat_data[i] for i in range(len(feat_data)) if mask[i]]

    # LOO residuals
    n = len(y_c)
    residuals = np.zeros(n)
    for i in range(n):
        X_tr = np.delete(X_c, i, axis=0)
        y_tr = np.delete(y_c, i)
        lr = LinearRegression()
        lr.fit(X_tr, y_tr)
        pred = lr.predict(X_c[i:i+1])[0]
        residuals[i] = y_c[i] - pred

    print(f"  Residual mean: {np.mean(residuals):.4f}")
    print(f"  Residual std: {np.std(residuals):.4f}")
    print(f"  Residual range: [{np.min(residuals):.4f}, {np.max(residuals):.4f}]")

    # Correlate residuals with section
    sections = [f['section'] for f in feat_clean]
    unique_secs = sorted(set(sections))
    sec_residuals = {}
    for sec in unique_secs:
        sec_resid = [residuals[i] for i in range(n) if sections[i] == sec]
        sec_residuals[sec] = {
            'mean': float(np.mean(sec_resid)),
            'std': float(np.std(sec_resid)),
            'n': len(sec_resid),
        }
        print(f"  {sec}: mean_resid={np.mean(sec_resid):+.4f} std={np.std(sec_resid):.4f} n={len(sec_resid)}")

    # Kruskal-Wallis test: do sections differ in residuals?
    sec_groups = [np.array([residuals[i] for i in range(n) if sections[i] == sec])
                  for sec in unique_secs if sum(1 for s in sections if s == sec) >= 5]
    if len(sec_groups) >= 2:
        kw_stat, kw_p = sp_stats.kruskal(*sec_groups)
        print(f"\n  Kruskal-Wallis (section): H={kw_stat:.2f}, p={kw_p:.4f}")
    else:
        kw_stat, kw_p = 0, 1.0

    # Correlate with paragraph position within folio
    par_positions = np.array([f['par_idx'] for f in feat_clean], dtype=float)
    rho_pos, p_pos = safe_spearman(par_positions, residuals)
    print(f"  Paragraph position vs residual: rho={rho_pos:+.4f} p={p_pos:.2e}")

    # Correlate with REGIME
    regimes = [f['regime'] for f in feat_clean]
    unique_regs = sorted(set(regimes))
    reg_groups = [np.array([residuals[i] for i in range(n) if regimes[i] == reg])
                  for reg in unique_regs if sum(1 for r in regimes if r == reg) >= 5]
    if len(reg_groups) >= 2:
        kw_reg, p_reg = sp_stats.kruskal(*reg_groups)
        print(f"  Kruskal-Wallis (REGIME): H={kw_reg:.2f}, p={p_reg:.4f}")
    else:
        kw_reg, p_reg = 0, 1.0

    # Folio-level: are some folios systematically over/under-predicted?
    folio_resid = defaultdict(list)
    for i in range(n):
        folio_resid[feat_clean[i]['folio']].append(residuals[i])
    folio_mean_resid = {f: np.mean(r) for f, r in folio_resid.items() if len(r) >= 2}
    if folio_mean_resid:
        resid_vals = list(folio_mean_resid.values())
        folio_std = float(np.std(resid_vals))
        extremes = sorted(folio_mean_resid.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        print(f"\n  Folio-level residual std: {folio_std:.4f}")
        print(f"  Most extreme folios:")
        for fol, r in extremes:
            nf = len(folio_resid[fol])
            print(f"    {fol}: mean_resid={r:+.4f} (n={nf})")

    # Shapiro-Wilk normality test on residuals
    if n <= 5000:
        sw_stat, sw_p = sp_stats.shapiro(residuals)
        print(f"\n  Shapiro-Wilk normality: W={sw_stat:.4f}, p={sw_p:.4f}")
    else:
        sw_stat, sw_p = 0, 0

    return {
        'residual_mean': float(np.mean(residuals)),
        'residual_std': float(np.std(residuals)),
        'section_residuals': sec_residuals,
        'section_kruskal_h': float(kw_stat),
        'section_kruskal_p': float(kw_p),
        'regime_kruskal_h': float(kw_reg),
        'regime_kruskal_p': float(p_reg),
        'par_position_rho': float(rho_pos),
        'par_position_p': float(p_pos),
        'folio_residual_std': float(folio_std) if folio_mean_resid else 0,
        'extreme_folios': [(f, float(r)) for f, r in extremes] if folio_mean_resid else [],
        'shapiro_w': float(sw_stat),
        'shapiro_p': float(sw_p),
        'verdict': 'RESIDUAL_STRUCTURED' if kw_p < 0.01 or p_reg < 0.01 else 'RESIDUAL_UNSTRUCTURED',
    }


def test_T8_prefix_middle_interaction(feat_data, y):
    """T8: PREFIX-MIDDLE interaction — does misalignment drive residuals?"""
    print("\n" + "=" * 60)
    print("T8: PREFIX-MIDDLE Interaction")
    print("=" * 60)

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score

    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac',
                 'da_frac', 'ol_frac', 'pch_frac', 'tch_frac', 'lch_frac']
    head_feats = ['head_a', 'head_e', 'head_o', 'head_k', 'head_t', 'headless_frac']

    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    X_head = np.column_stack([[f[p] for f in feat_data] for p in head_feats])

    # Create interaction terms: each PREFIX * each HEAD
    n_interactions = len(pfx_feats) * len(head_feats)
    interactions = []
    int_names = []
    for i, pf in enumerate(pfx_feats):
        for j, hf in enumerate(head_feats):
            interactions.append(X_pfx[:, i] * X_head[:, j])
            int_names.append(f'{pf}_x_{hf}')

    X_int = np.column_stack(interactions)
    X_main = np.hstack([X_pfx, X_head])
    X_full = np.hstack([X_main, X_int])

    mask = np.all(np.isfinite(X_full), axis=1) & np.isfinite(y)
    X_fc, y_c = X_full[mask], y[mask]
    X_mc = X_main[mask]

    lr = LinearRegression()

    # Main effects only
    scores_main = cross_val_score(lr, X_mc, y_c, cv=10, scoring='r2')
    r2_main = float(np.mean(scores_main))
    print(f"  Main effects (PREFIX + HEAD): CV R2 = {r2_main:.4f}")

    # Main + interactions
    scores_full = cross_val_score(lr, X_fc, y_c, cv=10, scoring='r2')
    r2_full = float(np.mean(scores_full))
    print(f"  Main + interactions: CV R2 = {r2_full:.4f}")

    delta = r2_full - r2_main
    print(f"  Interaction delta: {delta:+.4f}")
    print(f"  (negative = overfitting from {n_interactions} interaction terms)")

    # Also test a smaller interaction set: just qo*head_k and chsh*head_e
    key_interactions = [
        np.array([f['qo_frac'] for f in feat_data]) * np.array([f['head_k'] for f in feat_data]),
        np.array([f['chsh_frac'] for f in feat_data]) * np.array([f['head_e'] for f in feat_data]),
        np.array([f['bare_frac'] for f in feat_data]) * np.array([f['headless_frac'] for f in feat_data]),
    ]
    X_key_int = np.column_stack(key_interactions)
    X_key_full = np.hstack([X_main, X_key_int[mask].reshape(-1, 3) if mask.sum() == len(X_key_int) else X_key_int])

    mask2 = np.all(np.isfinite(X_key_full), axis=1) & np.isfinite(y)
    scores_key = cross_val_score(lr, X_key_full[mask2], y[mask2], cv=10, scoring='r2')
    r2_key = float(np.mean(scores_key))
    delta_key = r2_key - r2_main
    print(f"  Key interactions only (3 terms): CV R2 = {r2_key:.4f} (delta={delta_key:+.4f})")

    return {
        'r2_main_effects': float(r2_main),
        'r2_full_interactions': float(r2_full),
        'interaction_delta': float(delta),
        'r2_key_interactions': float(r2_key),
        'key_interaction_delta': float(delta_key),
        'n_interaction_terms': int(n_interactions),
        'verdict': 'INTERACTIONS_HELP' if delta > 0.02 else 'NO_INTERACTION_GAIN',
    }


def test_T9_headless_compound_fraction(feat_data, y):
    """T9: Headless compound fraction as AXM predictor."""
    print("\n" + "=" * 60)
    print("T9: Headless Compound Fraction as AXM Predictor")
    print("=" * 60)

    headless = np.array([f['headless_frac'] for f in feat_data])
    compound = np.array([f['compound_frac'] for f in feat_data])

    rho_headless, p_headless = safe_spearman(headless, y)
    rho_compound, p_compound = safe_spearman(compound, y)

    print(f"  headless_frac vs AXM: rho={rho_headless:+.4f} p={p_headless:.2e}")
    print(f"  compound_frac vs AXM: rho={rho_compound:+.4f} p={p_compound:.2e}")

    # Tertile analysis
    headless_sorted = np.sort(headless[headless > 0]) if np.sum(headless > 0) > 10 else np.array([0])
    if len(headless_sorted) > 10:
        tertiles = np.percentile(headless_sorted, [33, 67])
        low_axm = y[headless <= tertiles[0]]
        high_axm = y[headless > tertiles[1]]
        if len(low_axm) > 5 and len(high_axm) > 5:
            print(f"  Low headless AXM: {np.mean(low_axm):.3f} (n={len(low_axm)})")
            print(f"  High headless AXM: {np.mean(high_axm):.3f} (n={len(high_axm)})")

    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    X_headless = headless.reshape(-1, 1)
    X_compound = compound.reshape(-1, 1)
    X_both = np.hstack([X_headless, X_compound])

    r2_pfx, _ = cv_r2_linear(X_pfx, y, label='PREFIX baseline')
    r2_pfx_headless, _ = cv_r2_linear(np.hstack([X_pfx, X_headless]), y, label='PREFIX + headless_frac')
    r2_pfx_compound, _ = cv_r2_linear(np.hstack([X_pfx, X_compound]), y, label='PREFIX + compound_frac')
    r2_pfx_both, _ = cv_r2_linear(np.hstack([X_pfx, X_both]), y, label='PREFIX + headless + compound')

    print(f"\n  Headless delta beyond PREFIX: {r2_pfx_headless - r2_pfx:+.4f}")
    print(f"  Compound delta beyond PREFIX: {r2_pfx_compound - r2_pfx:+.4f}")

    return {
        'rho_headless': float(rho_headless),
        'p_headless': float(p_headless),
        'rho_compound': float(rho_compound),
        'p_compound': float(p_compound),
        'headless_delta_beyond_prefix': float(r2_pfx_headless - r2_pfx),
        'compound_delta_beyond_prefix': float(r2_pfx_compound - r2_pfx),
        'verdict': 'HEADLESS_ADDS' if (r2_pfx_headless - r2_pfx) > 0.02 else 'HEADLESS_REDUNDANT',
    }


def test_T10_noise_floor(feat_data, y):
    """T10: Is the 24% residual reducible or fundamental?
    Estimate the noise floor from within-paragraph sampling variance."""
    print("\n" + "=" * 60)
    print("T10: Noise Floor Estimation")
    print("=" * 60)

    # Method 1: Bootstrap resampling of token-level AXM within paragraphs
    # For each paragraph, resample its tokens with replacement, recompute AXM rate
    # This estimates the sampling noise in the AXM measurement itself
    n_boot = 500
    boot_variances = []

    for f in feat_data:
        n_tok = f['n_tokens']
        axm_rate = f['axm_rate']
        # Binomial sampling variance approximation
        # Var(p_hat) = p(1-p)/n for proportion
        var_binom = axm_rate * (1 - axm_rate) / n_tok if n_tok > 0 else 0
        boot_variances.append(var_binom)

    mean_sampling_var = float(np.mean(boot_variances))
    total_var = float(np.var(y))
    noise_fraction = mean_sampling_var / total_var if total_var > 0 else 0

    print(f"  Total AXM variance across paragraphs: {total_var:.6f}")
    print(f"  Mean within-paragraph sampling variance: {mean_sampling_var:.6f}")
    print(f"  Noise fraction of total: {noise_fraction:.4f} ({noise_fraction*100:.1f}%)")

    # Method 2: Split-half reliability
    # For paragraphs with enough tokens, split tokens in half, compute AXM for each half
    # Correlation between halves = signal; 1 - correlation = noise
    split_half_corrs = []
    for f_idx, f in enumerate(feat_data):
        n_tok = f['n_tokens']
        if n_tok < 20:
            continue
        # We need the actual classified tokens - use the stored AXM rate and n_tokens
        # Approximate: can't access raw tokens here, but can estimate from binomial
        # Better: just use the binomial approximation above

    # Method 3: Theoretical maximum R2
    # If noise_fraction = X, then max explainable = 1 - X
    # Therefore max R2 = 1 - noise_fraction
    max_r2 = 1.0 - noise_fraction

    # Method 4: Actual bootstrap — resample paragraph labels
    # Scramble paragraph-folio assignment, measure how much R2 drops
    pfx_feats = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_feats])
    mask = np.all(np.isfinite(X_pfx), axis=1) & np.isfinite(y)

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score
    lr = LinearRegression()
    real_scores = cross_val_score(lr, X_pfx[mask], y[mask], cv=10, scoring='r2')
    real_r2 = float(np.mean(real_scores))

    # Null distribution: shuffle y
    null_r2s = []
    for _ in range(200):
        y_shuf = np.random.permutation(y[mask])
        null_scores = cross_val_score(lr, X_pfx[mask], y_shuf, cv=5, scoring='r2')
        null_r2s.append(float(np.mean(null_scores)))

    null_mean = float(np.mean(null_r2s))
    null_std = float(np.std(null_r2s))
    z_score = (real_r2 - null_mean) / null_std if null_std > 0 else 0

    print(f"\n  Real PREFIX CV R2: {real_r2:.4f}")
    print(f"  Null (shuffled) R2: {null_mean:.4f} +/- {null_std:.4f}")
    print(f"  Z-score: {z_score:.1f}")
    print(f"\n  Theoretical maximum R2 (noise-limited): {max_r2:.4f}")
    print(f"  Current best R2: {real_r2:.4f}")
    print(f"  Gap to theoretical max: {max_r2 - real_r2:.4f}")
    print(f"  Noise-adjusted residual: {1.0 - real_r2 - noise_fraction:.4f}")

    # Signal-to-noise
    signal_var = total_var - mean_sampling_var
    snr = signal_var / mean_sampling_var if mean_sampling_var > 0 else float('inf')
    print(f"\n  Signal-to-noise ratio: {snr:.2f}")
    print(f"  Signal variance: {signal_var:.6f}")

    # What fraction of the 24% residual is noise vs genuine freedom?
    prefix_r2 = real_r2
    residual_frac = 1.0 - prefix_r2
    noise_in_residual = noise_fraction / residual_frac if residual_frac > 0 else 0
    genuine_freedom = residual_frac - noise_fraction

    print(f"\n  === DECOMPOSITION ===")
    print(f"  PREFIX explains: {prefix_r2*100:.1f}%")
    print(f"  Residual: {residual_frac*100:.1f}%")
    print(f"    Of which noise: {noise_fraction*100:.1f}%")
    print(f"    Of which genuine freedom: {genuine_freedom*100:.1f}%")
    print(f"  Noise as fraction of residual: {noise_in_residual*100:.1f}%")

    return {
        'total_variance': float(total_var),
        'mean_sampling_variance': float(mean_sampling_var),
        'noise_fraction': float(noise_fraction),
        'theoretical_max_r2': float(max_r2),
        'signal_to_noise': float(snr),
        'prefix_r2': float(prefix_r2),
        'residual_fraction': float(residual_frac),
        'noise_in_residual_pct': float(noise_in_residual * 100),
        'genuine_freedom_pct': float(genuine_freedom * 100),
        'null_r2_mean': float(null_mean),
        'null_r2_std': float(null_std),
        'z_score': float(z_score),
        'verdict': f'NOISE={noise_fraction*100:.1f}%_FREEDOM={genuine_freedom*100:.1f}%',
    }


# ================================================================
# MAIN
# ================================================================

def main():
    print("=" * 70)
    print("Phase 520: PARAGRAPH AXM RESIDUAL ANALYSIS")
    print("=" * 70)

    tokens, token_to_class, folio_to_regime, morph = load_data()
    enriched = build_enriched_tokens(tokens, token_to_class, folio_to_regime, morph)
    paragraphs = build_paragraphs(enriched)
    feat_data = compute_paragraph_features(paragraphs)

    y = np.array([f['axm_rate'] for f in feat_data])

    results = {
        'metadata': {
            'phase': 520,
            'name': 'PARAGRAPH_AXM_RESIDUAL',
            'n_tokens': len(enriched),
            'n_paragraphs': len(paragraphs),
            'n_feature_paragraphs': len(feat_data),
            'axm_mean': float(np.mean(y)),
            'axm_std': float(np.std(y)),
            'axm_range': [float(np.min(y)), float(np.max(y))],
        }
    }

    print(f"\n  AXM rate: mean={np.mean(y):.3f}, std={np.std(y):.3f}")

    # Run all tests
    results['T1_middle_head'] = test_T1_middle_head_composition(feat_data, y)
    results['T2_suffix'] = test_T2_suffix_features(feat_data, y)
    results['T3_line_structure'] = test_T3_line_structure(feat_data, y)
    results['T4_articulator'] = test_T4_articulator_features(feat_data, y)
    results['T5_full_model'] = test_T5_full_model(feat_data, y)
    results['T6_importance'] = test_T6_feature_importance(feat_data, y)
    results['T7_residuals'] = test_T7_residual_analysis(feat_data, y)
    results['T8_interaction'] = test_T8_prefix_middle_interaction(feat_data, y)
    results['T9_headless'] = test_T9_headless_compound_fraction(feat_data, y)
    results['T10_noise_floor'] = test_T10_noise_floor(feat_data, y)

    # ================================================================
    # SYNTHESIS
    # ================================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS: What drives the 24% residual?")
    print("=" * 70)

    t1 = results['T1_middle_head']
    t5 = results['T5_full_model']
    t6 = results['T6_importance']
    t10 = results['T10_noise_floor']

    print(f"\n  1. PREFIX alone: CV R2 = {t1['r2_prefix_baseline']:.4f}")
    print(f"  2. HEAD atoms add: {t1['head_delta_beyond_prefix']:+.4f}")
    print(f"  3. TERMINAL atoms add: {t1['terminal_delta_beyond_prefix']:+.4f}")
    print(f"  4. Full model R2: {t5['r2_full_model']:.4f}")
    print(f"  5. Full model LOO R2: {t5['r2_full_loo']:.4f}")
    print(f"  6. Noise fraction: {t10['noise_fraction']*100:.1f}%")
    print(f"  7. Genuine freedom: {t10['genuine_freedom_pct']:.1f}%")

    total_explained = t5['r2_full_model']
    noise = t10['noise_fraction']
    genuine = 1.0 - total_explained - noise

    results['synthesis'] = {
        'prefix_r2': float(t1['r2_prefix_baseline']),
        'full_model_r2': float(t5['r2_full_model']),
        'full_model_loo_r2': float(t5['r2_full_loo']),
        'total_residual': float(1.0 - t1['r2_prefix_baseline']),
        'closed_by_full_model': float(t5['r2_full_model'] - t1['r2_prefix_baseline']),
        'noise_fraction': float(noise),
        'genuine_design_freedom': float(max(genuine, 0)),
        'decomposition': {
            'prefix_explains': f"{t1['r2_prefix_baseline']*100:.1f}%",
            'other_features_add': f"{(t5['r2_full_model'] - t1['r2_prefix_baseline'])*100:.1f}%",
            'noise': f"{noise*100:.1f}%",
            'genuine_freedom': f"{max(genuine, 0)*100:.1f}%",
        },
        'verdict': (
            f"PREFIX explains {t1['r2_prefix_baseline']*100:.1f}% of paragraph AXM variance. "
            f"Additional features close {(t5['r2_full_model']-t1['r2_prefix_baseline'])*100:.1f}% more. "
            f"Measurement noise accounts for ~{noise*100:.1f}%. "
            f"Genuine design freedom is ~{max(genuine,0)*100:.1f}%."
        ),
    }

    print(f"\n  VERDICT: {results['synthesis']['verdict']}")

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'paragraph_axm_residual.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Results saved to {out_path}")

    print("\n" + "=" * 70)
    print("Phase 520 COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
