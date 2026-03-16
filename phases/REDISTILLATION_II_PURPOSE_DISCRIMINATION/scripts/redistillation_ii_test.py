"""Phase 597: Redistillation-ii Purpose Discrimination.

Tests whether the i-extension encodes redistillation PURPOSE beyond the
confirmed safety-routing MECHANISM (C1480-C1482). Five tests target
process-level signatures that safety-routing alone does not predict.

Expert-reviewed: dropped k-HEAD avoidance (confounded by HEAD competition)
and REGIME_4 precision (non-discriminating). Added REGIME control to T1,
a-HEAD baseline to T3, collinearity fix to T4, continuous metric to T5.
"""
import json
import os
import sys
import time
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))
sys.path.insert(0, ROOT)

from scripts.voynich import (Transcript, Morphology, CategoryClassifier,
                              decompose_middle_hmt)

REGIME_PATH = os.path.join(ROOT, 'data', 'regime_folio_mapping.json')
CLASS_TOKEN_MAP_PATH = os.path.join(ROOT, 'phases', 'CLASS_COSURVIVAL_TEST',
                                     'results', 'class_token_map.json')
DECODER_MAPS_PATH = os.path.join(ROOT, 'data', 'decoder_maps.json')

N_SHUFFLES = 1000
SEED = 42

# FL Stage Map -- canonical from voynich.py PPSemantics (17 MIDDLEs)
FL_STAGE_MAP = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    'o': 'FINAL', 'ly': 'FINAL', 'am': 'FINAL',
    'n': 'TERMINAL', 'im': 'TERMINAL', 'm': 'TERMINAL',
    'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL'
}

FL_STAGE_NUMERIC = {
    'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2,
    'LATE': 3, 'FINAL': 4, 'TERMINAL': 5
}

# Suffix mode atom partition (C1410)
MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}

EXTENSIBLE = {'e', 'i'}


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


# ============================================================
# Utilities
# ============================================================

def max_consecutive_i(middle):
    """Count max run of consecutive 'i' in a MIDDLE string."""
    max_run = current = 0
    for ch in middle:
        if ch == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run


def i_class(middle):
    """Classify MIDDLE by i-extension: 'no_i', 'single_i', 'double_ii'."""
    mc = max_consecutive_i(middle)
    if mc == 0:
        return 'no_i'
    elif mc == 1:
        return 'single_i'
    else:
        return 'double_ii'


def load_regime_map():
    """Load folio -> REGIME mapping."""
    with open(REGIME_PATH) as f:
        data = json.load(f)
    return {f: v['regime'] for f, v in data.get('regime_assignments', {}).items()}


def load_token_class_map():
    """Load token -> 49-class mapping."""
    with open(CLASS_TOKEN_MAP_PATH) as f:
        data = json.load(f)
    return {t: int(c) for t, c in data['token_to_class'].items()}


def load_macro_state_map():
    """Load class_id -> macro state label from decoder_maps.json."""
    with open(DECODER_MAPS_PATH) as f:
        data = json.load(f)
    entries = data['maps']['macro_state']['entries']
    return {k: v['value'] for k, v in entries.items()}


def fl_stage_numeric(middle):
    """Return numeric FL stage for a MIDDLE, or None if not FL vocabulary."""
    stage = FL_STAGE_MAP.get(middle)
    if stage is None:
        return None
    return FL_STAGE_NUMERIC[stage]


def e_depth(middle):
    """Count consecutive 'e' characters at start of MIDDLE (e-HEAD depth)."""
    count = 0
    for ch in middle:
        if ch == 'e':
            count += 1
        else:
            break
    return count


def atomize_suffix(sfx):
    """Break suffix into atoms (handling ee, ii runs)."""
    atoms = []
    idx = 0
    while idx < len(sfx):
        ch = sfx[idx]
        if ch in EXTENSIBLE:
            run = ch
            while idx + 1 < len(sfx) and sfx[idx + 1] == ch:
                run += ch
                idx += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        idx += 1
    return atoms


def classify_suffix_mode(sfx):
    """Classify suffix as Mode A or B based on atom majority (C1410)."""
    if not sfx:
        return None
    atoms = atomize_suffix(sfx)
    a_count = sum(1 for a in atoms if a in MODE_A_ATOMS)
    b_count = sum(1 for a in atoms if a in MODE_B_ATOMS)
    if a_count > b_count:
        return 'A'
    elif b_count > a_count:
        return 'B'
    return None


def partial_correlation_ols(x, y, covariates):
    """Spearman partial correlation: residualize x and y on covariates, then correlate."""
    if covariates.shape[1] == 0:
        return stats.spearmanr(x, y)
    x_resid = x - covariates @ np.linalg.lstsq(covariates, x, rcond=None)[0]
    y_resid = y - covariates @ np.linalg.lstsq(covariates, y, rcond=None)[0]
    return stats.spearmanr(x_resid, y_resid)


# ============================================================
# Data Assembly
# ============================================================

def assemble_data():
    """Load and prepare all tokens."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    regime_map = load_regime_map()
    token_class_map = load_token_class_map()
    macro_map = load_macro_state_map()

    b_tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word:
            continue
        w = t.word.strip()
        if not w:
            continue
        m = morph.extract(w)
        if not m.middle:
            continue

        head, mods, term, frame_str = decompose_middle_hmt(m.middle)
        ic = i_class(m.middle)
        fl_num = fl_stage_numeric(m.middle)
        is_fl = fl_num is not None
        is_ey = (head == 'e' and term == 'y')
        is_a_head = (head == 'a')
        cat = cc.classify(m.middle)
        token_class = token_class_map.get(w)
        macro_state = macro_map.get(str(token_class)) if token_class is not None else None

        b_tokens.append({
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'middle': m.middle,
            'suffix': m.suffix,
            'head': head,
            'term': term,
            'i_class': ic,
            'fl_stage_num': fl_num,
            'is_fl': is_fl,
            'is_ey': is_ey,
            'is_a_head': is_a_head,
            'category': cat,
            'macro_state': macro_state,
            'regime': regime_map.get(t.folio, 'UNKNOWN'),
            'par_initial': t.par_initial,
        })

    # Currier A tokens (for T2)
    a_tokens = []
    for t in tx.currier_a():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word:
            continue
        w = t.word.strip()
        if not w:
            continue
        m = morph.extract(w)
        if not m.middle:
            continue

        head, mods, term, frame_str = decompose_middle_hmt(m.middle)
        ic = i_class(m.middle)
        ed = e_depth(m.middle) if head == 'e' else 0

        a_tokens.append({
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'middle': m.middle,
            'head': head,
            'i_class': ic,
            'e_depth': ed,
        })

    # Build indices
    line_index = defaultdict(list)
    for tok in b_tokens:
        line_index[(tok['folio'], tok['line'])].append(tok)

    folio_index = defaultdict(list)
    for tok in b_tokens:
        folio_index[tok['folio']].append(tok)

    # Build paragraphs
    paragraphs = build_paragraphs(b_tokens)

    return b_tokens, a_tokens, line_index, folio_index, paragraphs


def build_paragraphs(b_tokens):
    """Build paragraph structures from par_initial field."""
    paragraphs = []
    current_par = []
    current_folio = None
    par_idx = 0

    for tok in b_tokens:
        if tok['par_initial'] and current_par:
            paragraphs.append({
                'folio': current_folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0]['section'],
            })
            if tok['folio'] != current_folio:
                par_idx = 0
                current_folio = tok['folio']
            else:
                par_idx += 1
            current_par = [tok]
        else:
            if current_folio is None or tok['folio'] != current_folio:
                if current_par:
                    paragraphs.append({
                        'folio': current_folio,
                        'par_idx': par_idx,
                        'tokens': current_par,
                        'section': current_par[0]['section'],
                    })
                current_folio = tok['folio']
                par_idx = 0
                current_par = [tok]
            else:
                current_par.append(tok)
    if current_par:
        paragraphs.append({
            'folio': current_folio,
            'par_idx': par_idx,
            'tokens': current_par,
            'section': current_par[0]['section'],
        })

    return paragraphs


# ============================================================
# T1: e-to-y Safety Co-deployment (PRIMARY GATE)
# ============================================================

def run_t1(folio_index):
    """T1: e-to-y co-deployment at folio level with section+REGIME control."""
    folio_stats = {}
    for folio, toks in folio_index.items():
        n = len(toks)
        n_ii = sum(1 for t in toks if t['i_class'] == 'double_ii')
        n_ey = sum(1 for t in toks if t['is_ey'])
        section = toks[0]['section']
        regime = toks[0]['regime']
        folio_stats[folio] = {
            'n': n,
            'ii_frac': n_ii / n,
            'ey_frac': n_ey / n,
            'section': section,
            'regime': regime,
        }

    folios = sorted(folio_stats.keys())
    ii_vals = np.array([folio_stats[f]['ii_frac'] for f in folios])
    ey_vals = np.array([folio_stats[f]['ey_frac'] for f in folios])
    sections = [folio_stats[f]['section'] for f in folios]
    regimes = [folio_stats[f]['regime'] for f in folios]

    # Raw Spearman
    rho_raw, p_raw = stats.spearmanr(ii_vals, ey_vals)

    # Section-only control
    unique_secs = sorted(set(sections))
    sec_dummies = np.zeros((len(folios), max(len(unique_secs) - 1, 1)))
    for i, sec in enumerate(sections):
        sec_idx = unique_secs.index(sec)
        if sec_idx > 0 and len(unique_secs) > 1:
            sec_dummies[i, sec_idx - 1] = 1.0

    rho_sec, p_sec = partial_correlation_ols(ii_vals, ey_vals, sec_dummies)

    # Section + REGIME control
    unique_regs = sorted(set(regimes))
    reg_dummies = np.zeros((len(folios), max(len(unique_regs) - 1, 1)))
    for i, reg in enumerate(regimes):
        reg_idx = unique_regs.index(reg)
        if reg_idx > 0 and len(unique_regs) > 1:
            reg_dummies[i, reg_idx - 1] = 1.0

    combined = np.hstack([sec_dummies, reg_dummies])
    rho_full, p_full = partial_correlation_ols(ii_vals, ey_vals, combined)

    positive = bool(rho_full > 0.20 and p_full < 0.01)

    return {
        'n_folios': len(folios),
        'mean_ii_frac': round(float(np.mean(ii_vals)), 4),
        'mean_ey_frac': round(float(np.mean(ey_vals)), 4),
        'raw_spearman_rho': round(float(rho_raw), 4),
        'raw_spearman_p': round(float(p_raw), 6),
        'section_controlled_rho': round(float(rho_sec), 4),
        'section_controlled_p': round(float(p_sec), 6),
        'full_controlled_rho': round(float(rho_full), 4),
        'full_controlled_p': round(float(p_full), 6),
        'controls': 'section + REGIME',
        'positive': positive,
        'interpretation': ('Co-deployment (redistillation supported)'
                          if positive else
                          'No co-deployment after controls'),
    }


# ============================================================
# T2: A-side e-depth Co-occurrence (SECONDARY GATE)
# ============================================================

def run_t2(a_tokens):
    """T2: A-side e-depth co-occurrence with record length control."""
    # Group A tokens by record (line)
    a_line_index = defaultdict(list)
    for t in a_tokens:
        a_line_index[(t['folio'], t['line'])].append(t)

    records = []
    for key, toks in a_line_index.items():
        i_toks = [t for t in toks if t['i_class'] != 'no_i']
        e_toks = [t for t in toks if t['head'] == 'e' and t['e_depth'] > 0]

        if not i_toks or not e_toks:
            continue

        n_ii = sum(1 for t in i_toks if t['i_class'] == 'double_ii')
        ii_frac = n_ii / len(i_toks)
        mean_ed = np.mean([t['e_depth'] for t in e_toks])

        records.append({
            'ii_frac': ii_frac,
            'mean_e_depth': mean_ed,
            'record_length': len(toks),
        })

    if len(records) < 10:
        return {
            'status': 'INSUFFICIENT_DATA',
            'n_records': len(records),
            'positive': False,
        }

    ii_vals = np.array([r['ii_frac'] for r in records])
    ed_vals = np.array([r['mean_e_depth'] for r in records])
    len_vals = np.array([r['record_length'] for r in records])

    # Raw Spearman
    rho_raw, p_raw = stats.spearmanr(ii_vals, ed_vals)

    # Length-controlled partial correlation
    len_col = len_vals.reshape(-1, 1)
    rho_ctrl, p_ctrl = partial_correlation_ols(ii_vals, ed_vals, len_col)

    positive = bool(rho_ctrl > 0.15 and p_ctrl < 0.05)

    # Collider bias flag: raw rho near zero but controlled rho large
    # suggests length may be a collider rather than confounder
    collider_flag = bool(abs(rho_raw) < 0.05 and abs(rho_ctrl) > 0.2)

    return {
        'n_qualifying_records': len(records),
        'mean_ii_fraction': round(float(np.mean(ii_vals)), 4),
        'mean_e_depth': round(float(np.mean(ed_vals)), 4),
        'mean_record_length': round(float(np.mean(len_vals)), 1),
        'raw_spearman_rho': round(float(rho_raw), 4),
        'raw_spearman_p': round(float(p_raw), 6),
        'length_controlled_rho': round(float(rho_ctrl), 4),
        'length_controlled_p': round(float(p_ctrl), 6),
        'positive': positive,
        'collider_bias_flag': collider_flag,
        'caveat': 'AMBIGUOUS: control CREATES correlation from null raw — possible collider bias' if collider_flag else None,
    }


# ============================================================
# T3: FL State Co-occurrence (SUPPORTING)
# ============================================================

def run_t3(line_index, rng):
    """T3: FL state co-occurrence with a-HEAD baseline control."""
    # Classify each qualifying line
    line_records = []  # (group, mean_fl_stage)

    for key, toks in line_index.items():
        # Collect FL tokens whose MIDDLE is NOT 'i' or 'ii' (avoid tautology)
        fl_stages = []
        for t in toks:
            if t['is_fl'] and t['middle'] not in ('i', 'ii'):
                fl_stages.append(t['fl_stage_num'])

        if not fl_stages:
            continue

        mean_fl = np.mean(fl_stages)
        has_ii = any(t['i_class'] == 'double_ii' for t in toks)
        has_si = any(t['i_class'] == 'single_i' for t in toks)
        has_a_head_no_i = (any(t['is_a_head'] for t in toks) and
                           not any(t['i_class'] != 'no_i' for t in toks))

        if has_ii:
            group = 'ii'
        elif has_si:
            group = 'si'
        elif has_a_head_no_i:
            group = 'a_head_no_i'
        else:
            group = 'other'

        line_records.append({'group': group, 'mean_fl': mean_fl})

    # Compute group means
    groups = {}
    for g in ['ii', 'si', 'a_head_no_i', 'other']:
        vals = [r['mean_fl'] for r in line_records if r['group'] == g]
        groups[g] = {
            'n': len(vals),
            'mean': round(float(np.mean(vals)), 4) if vals else None,
            'std': round(float(np.std(vals)), 4) if vals else None,
        }

    # Key comparison: ii vs si
    ii_vals = [r['mean_fl'] for r in line_records if r['group'] == 'ii']
    si_vals = [r['mean_fl'] for r in line_records if r['group'] == 'si']
    a_no_i_vals = [r['mean_fl'] for r in line_records if r['group'] == 'a_head_no_i']

    obs_diff_ii_si = (np.mean(ii_vals) - np.mean(si_vals)) if ii_vals and si_vals else 0.0
    obs_diff_ii_abase = (np.mean(ii_vals) - np.mean(a_no_i_vals)) if ii_vals and a_no_i_vals else 0.0

    # Permutation: shuffle ii vs si labels
    perm_p_ii_si = 1.0
    if ii_vals and si_vals:
        combined = ii_vals + si_vals
        n_ii = len(ii_vals)
        perm_diffs = []
        for _ in range(N_SHUFFLES):
            rng.shuffle(combined)
            perm_diff = np.mean(combined[:n_ii]) - np.mean(combined[n_ii:])
            perm_diffs.append(perm_diff)
        # One-tailed: ii higher
        perm_p_ii_si = float(np.mean(np.array(perm_diffs) >= obs_diff_ii_si))

    # Permutation: ii vs a-HEAD baseline
    perm_p_ii_abase = 1.0
    if ii_vals and a_no_i_vals:
        combined_a = ii_vals + a_no_i_vals
        n_ii_a = len(ii_vals)
        perm_diffs_a = []
        for _ in range(N_SHUFFLES):
            rng.shuffle(combined_a)
            perm_diff_a = np.mean(combined_a[:n_ii_a]) - np.mean(combined_a[n_ii_a:])
            perm_diffs_a.append(perm_diff_a)
        perm_p_ii_abase = float(np.mean(np.array(perm_diffs_a) >= obs_diff_ii_abase))

    # Mann-Whitney for effect size
    mw_stat_si, mw_p_si = stats.mannwhitneyu(ii_vals, si_vals, alternative='greater') if ii_vals and si_vals else (0, 1)
    mw_stat_ab, mw_p_ab = stats.mannwhitneyu(ii_vals, a_no_i_vals, alternative='greater') if ii_vals and a_no_i_vals else (0, 1)

    # Positive requires ii > BOTH single-i AND a-HEAD baseline
    positive = bool(perm_p_ii_si < 0.01 and perm_p_ii_abase < 0.01 and
                    obs_diff_ii_si > 0 and obs_diff_ii_abase > 0)

    return {
        'group_stats': groups,
        'diff_ii_minus_si': round(float(obs_diff_ii_si), 4),
        'diff_ii_minus_a_baseline': round(float(obs_diff_ii_abase), 4),
        'perm_p_ii_vs_si': round(float(perm_p_ii_si), 4),
        'perm_p_ii_vs_a_baseline': round(float(perm_p_ii_abase), 4),
        'mw_p_ii_vs_si': round(float(mw_p_si), 6),
        'mw_p_ii_vs_a_baseline': round(float(mw_p_ab), 6),
        'positive': positive,
        'power_note': f"ii-lines with FL: {groups['ii']['n']}, "
                      f"si-lines with FL: {groups['si']['n']}, "
                      f"a-HEAD-no-i lines with FL: {groups['a_head_no_i']['n']}",
    }


# ============================================================
# T4: Mode A Specification Residual (SUPPORTING)
# ============================================================

def run_t4(folio_index):
    """T4: Mode A specification residual using ii-as-proportion-of-a-HEAD."""
    folio_stats = {}
    for folio, toks in folio_index.items():
        n = len(toks)
        n_a_head = sum(1 for t in toks if t['is_a_head'])
        n_ii = sum(1 for t in toks if t['i_class'] == 'double_ii')

        # Mode A classification per token suffix
        n_mode_a = 0
        n_classified = 0
        for t in toks:
            if t['suffix']:
                mode = classify_suffix_mode(t['suffix'])
                if mode:
                    n_classified += 1
                    if mode == 'A':
                        n_mode_a += 1

        if n_classified == 0 or n_a_head == 0:
            continue

        folio_stats[folio] = {
            'mode_a_frac': n_mode_a / n_classified,
            'a_head_frac': n_a_head / n,
            'ii_prop_of_a_head': n_ii / n_a_head if n_a_head > 0 else 0.0,
        }

    folios = sorted(folio_stats.keys())
    if len(folios) < 10:
        return {'status': 'INSUFFICIENT_DATA', 'positive': False}

    Y = np.array([folio_stats[f]['mode_a_frac'] for f in folios])
    X_a = np.array([folio_stats[f]['a_head_frac'] for f in folios])
    X_ii = np.array([folio_stats[f]['ii_prop_of_a_head'] for f in folios])

    # Predictor correlation (collinearity check)
    pred_corr, _ = stats.spearmanr(X_a, X_ii)

    # Linear regression: Y ~ 1 + X_a + X_ii
    X = np.column_stack([np.ones(len(folios)), X_a, X_ii])
    beta, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)

    # Residuals and t-test for ii coefficient
    Y_hat = X @ beta
    resid = Y - Y_hat
    n = len(Y)
    p = 3
    sigma2 = np.sum(resid**2) / (n - p) if n > p else 1.0

    try:
        XtX_inv = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        XtX_inv = np.eye(p)

    se_beta = np.sqrt(np.diag(np.abs(sigma2 * XtX_inv)))
    t_stat_ii = beta[2] / se_beta[2] if se_beta[2] > 0 else 0.0
    p_val_ii = float(2 * stats.t.sf(abs(t_stat_ii), df=n - p)) if n > p else 1.0

    r_sq = 1 - np.sum(resid**2) / np.sum((Y - np.mean(Y))**2)

    positive = bool(beta[2] > 0 and p_val_ii < 0.01)

    return {
        'n_folios': len(folios),
        'beta_intercept': round(float(beta[0]), 4),
        'beta_a_head': round(float(beta[1]), 4),
        'beta_ii_prop_of_a_head': round(float(beta[2]), 4),
        'se_ii': round(float(se_beta[2]), 4),
        't_stat_ii': round(float(t_stat_ii), 4),
        'p_val_ii': round(float(p_val_ii), 6),
        'r_squared': round(float(r_sq), 4),
        'predictor_correlation': round(float(pred_corr), 4),
        'positive': positive,
    }


# ============================================================
# T5: OPERATION Category Co-occurrence (SUPPORTING)
# ============================================================

def run_t5(paragraphs):
    """T5: OPERATION category co-occurrence at paragraph level."""
    par_records = []

    for par in paragraphs:
        toks = par['tokens']
        if len(toks) < 5:
            continue

        i_toks = [t for t in toks if t['i_class'] != 'no_i']
        if not i_toks:
            continue

        n_ii = sum(1 for t in i_toks if t['i_class'] == 'double_ii')
        ii_frac = n_ii / len(i_toks)

        # OPERATION category fraction
        n_op = sum(1 for t in toks if t['category'] == 'OPERATION')
        op_frac = n_op / len(toks)

        par_records.append({
            'ii_frac': ii_frac,
            'op_frac': op_frac,
            'section': par['section'],
        })

    if len(par_records) < 20:
        return {'status': 'INSUFFICIENT_DATA', 'positive': False}

    ii_vals = np.array([r['ii_frac'] for r in par_records])
    op_vals = np.array([r['op_frac'] for r in par_records])
    sections = [r['section'] for r in par_records]

    # Raw Spearman
    rho_raw, p_raw = stats.spearmanr(ii_vals, op_vals)

    # Section-controlled
    unique_secs = sorted(set(sections))
    sec_dummies = np.zeros((len(par_records), max(len(unique_secs) - 1, 1)))
    for i, sec in enumerate(sections):
        sec_idx = unique_secs.index(sec)
        if sec_idx > 0 and len(unique_secs) > 1:
            sec_dummies[i, sec_idx - 1] = 1.0

    rho_ctrl, p_ctrl = partial_correlation_ols(ii_vals, op_vals, sec_dummies)

    positive = bool(rho_ctrl > 0.15 and p_ctrl < 0.05)

    return {
        'n_paragraphs': len(par_records),
        'mean_ii_frac': round(float(np.mean(ii_vals)), 4),
        'mean_op_frac': round(float(np.mean(op_vals)), 4),
        'raw_spearman_rho': round(float(rho_raw), 4),
        'raw_spearman_p': round(float(p_raw), 6),
        'section_controlled_rho': round(float(rho_ctrl), 4),
        'section_controlled_p': round(float(p_ctrl), 6),
        'positive': positive,
    }


# ============================================================
# T6: Forgiveness Prediction (CHARACTERIZATION)
# ============================================================

def run_t6(folio_index, line_index):
    """T6: Does ii-fraction predict folio forgiveness (AXM self-transition rate)
    independently of e-to-y fraction AND section?

    Forgiveness = AXM self-transition rate (proportion of AXM→AXM among all
    AXM→X transitions). High forgiveness = system quickly returns to safe state.
    Model 1: forgiveness ~ ey_frac + section_dummies (baseline)
    Model 2: forgiveness ~ ey_frac + ii_frac + section_dummies (test)
    F-test for incremental ii term.
    """
    # Compute per-folio AXM self-transition rate
    folio_axm_self = defaultdict(lambda: {'axm_transitions': 0, 'axm_self': 0})

    for key in sorted(line_index.keys()):
        folio, line = key
        line_tokens = line_index[key]
        for i in range(len(line_tokens) - 1):
            src_ms = line_tokens[i].get('macro_state')
            tgt_ms = line_tokens[i + 1].get('macro_state')
            if src_ms == 'AXM':
                folio_axm_self[folio]['axm_transitions'] += 1
                if tgt_ms == 'AXM':
                    folio_axm_self[folio]['axm_self'] += 1

    # Build folio-level data
    folio_data = []
    for folio, toks in folio_index.items():
        n = len(toks)
        axm_info = folio_axm_self.get(folio)
        if axm_info is None or axm_info['axm_transitions'] < 10:
            continue

        forgiveness = axm_info['axm_self'] / axm_info['axm_transitions']
        ii_frac = sum(1 for t in toks if t['i_class'] == 'double_ii') / n
        ey_frac = sum(1 for t in toks if t['is_ey']) / n
        section = toks[0]['section']

        folio_data.append({
            'folio': folio,
            'forgiveness': forgiveness,
            'ii_frac': ii_frac,
            'ey_frac': ey_frac,
            'section': section,
            'axm_transitions': axm_info['axm_transitions'],
        })

    if len(folio_data) < 15:
        return {'status': 'INSUFFICIENT_DATA', 'n_folios': len(folio_data),
                'positive': False}

    n = len(folio_data)
    Y = np.array([f['forgiveness'] for f in folio_data])
    ey = np.array([f['ey_frac'] for f in folio_data])
    ii = np.array([f['ii_frac'] for f in folio_data])
    sections = [f['section'] for f in folio_data]

    # Section dummies
    unique_secs = sorted(set(sections))
    sec_dummies = np.zeros((n, max(len(unique_secs) - 1, 1)))
    for i, sec in enumerate(sections):
        sec_idx = unique_secs.index(sec)
        if sec_idx > 0 and len(unique_secs) > 1:
            sec_dummies[i, sec_idx - 1] = 1.0

    # Raw (no controls) for comparison
    X_raw1 = np.column_stack([np.ones(n), ey])
    beta_raw1, _, _, _ = np.linalg.lstsq(X_raw1, Y, rcond=None)
    ss_res_raw1 = np.sum((Y - X_raw1 @ beta_raw1) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r2_raw_ey = 1 - ss_res_raw1 / ss_tot if ss_tot > 0 else 0.0

    X_raw2 = np.column_stack([np.ones(n), ey, ii])
    beta_raw2, _, _, _ = np.linalg.lstsq(X_raw2, Y, rcond=None)
    ss_res_raw2 = np.sum((Y - X_raw2 @ beta_raw2) ** 2)
    r2_raw_ey_ii = 1 - ss_res_raw2 / ss_tot if ss_tot > 0 else 0.0

    # Raw delta-R² and F-test (without section control)
    delta_r2_raw = r2_raw_ey_ii - r2_raw_ey
    df_raw2 = n - 3
    if ss_res_raw2 > 0 and df_raw2 > 0:
        f_stat_raw = ((ss_res_raw1 - ss_res_raw2) / 1) / (ss_res_raw2 / df_raw2)
        from scipy.stats import f as f_dist
        f_p_raw = float(1 - f_dist.cdf(f_stat_raw, 1, df_raw2))
    else:
        f_stat_raw = 0.0
        f_p_raw = 1.0

    # Section-controlled Model 1: forgiveness ~ ey_frac + section_dummies
    X1 = np.column_stack([np.ones(n), ey, sec_dummies])
    beta1, _, _, _ = np.linalg.lstsq(X1, Y, rcond=None)
    ss_res1 = np.sum((Y - X1 @ beta1) ** 2)
    r2_1 = 1 - ss_res1 / ss_tot if ss_tot > 0 else 0.0
    p1 = X1.shape[1]

    # Section-controlled Model 2: forgiveness ~ ey_frac + ii_frac + section_dummies
    X2 = np.column_stack([np.ones(n), ey, ii, sec_dummies])
    beta2, _, _, _ = np.linalg.lstsq(X2, Y, rcond=None)
    ss_res2 = np.sum((Y - X2 @ beta2) ** 2)
    r2_2 = 1 - ss_res2 / ss_tot if ss_tot > 0 else 0.0
    p2 = X2.shape[1]

    delta_r2_ctrl = r2_2 - r2_1

    # F-test for incremental ii term (section-controlled)
    df2 = n - p2
    if ss_res2 > 0 and df2 > 0:
        f_stat_ctrl = ((ss_res1 - ss_res2) / 1) / (ss_res2 / df2)
        from scipy.stats import f as f_dist
        f_p_ctrl = float(1 - f_dist.cdf(f_stat_ctrl, 1, df2))
    else:
        f_stat_ctrl = 0.0
        f_p_ctrl = 1.0

    # Spearman for interpretability
    rho_ey_forg, p_ey_forg = stats.spearmanr(ey, Y)
    rho_ii_forg, p_ii_forg = stats.spearmanr(ii, Y)

    # beta_ii is at index 2 in section-controlled model (intercept=0, ey=1, ii=2, sec_dummies=3+)
    beta_ii_ctrl = float(beta2[2])

    positive = bool(delta_r2_ctrl > 0.02 and f_p_ctrl < 0.05 and beta_ii_ctrl > 0)

    return {
        'n_folios': n,
        'n_sections': len(unique_secs),
        'mean_forgiveness': round(float(np.mean(Y)), 4),
        'raw_r2_ey_only': round(float(r2_raw_ey), 4),
        'raw_r2_ey_plus_ii': round(float(r2_raw_ey_ii), 4),
        'raw_delta_r2': round(float(delta_r2_raw), 4),
        'raw_f_stat': round(float(f_stat_raw), 4),
        'raw_f_p_val': round(float(f_p_raw), 6),
        'raw_beta_ii': round(float(beta_raw2[2]), 4),
        'ctrl_r2_ey_plus_sec': round(float(r2_1), 4),
        'ctrl_r2_ey_ii_plus_sec': round(float(r2_2), 4),
        'ctrl_delta_r2': round(float(delta_r2_ctrl), 4),
        'ctrl_f_stat': round(float(f_stat_ctrl), 4),
        'ctrl_f_p_val': round(float(f_p_ctrl), 6),
        'ctrl_beta_ii': round(float(beta_ii_ctrl), 4),
        'spearman_ey_forgiveness': round(float(rho_ey_forg), 4),
        'spearman_p_ey': round(float(p_ey_forg), 6),
        'spearman_ii_forgiveness': round(float(rho_ii_forg), 4),
        'spearman_p_ii': round(float(p_ii_forg), 6),
        'positive': positive,
    }


# ============================================================
# Verdict
# ============================================================

def compute_verdict(t1, t2, t3, t4, t5, t6=None):
    """Decision logic: T1 primary gate, T2 secondary, T3-T5 supporting, T6 characterization.

    Expert review: T1 anti-correlation (rho=-0.633) is the REAL finding —
    ii and e-to-y are folio-level safety SUBSTITUTES. Redistillation predicts
    co-deployment, so this kills the redistillation hypothesis. T6 characterizes
    whether ii has independent safety contribution beyond e-to-y.
    """
    t1_pos = t1.get('positive', False)
    t6_pos = t6.get('positive', False) if t6 else False

    if t1_pos:
        # Original redistillation paths (retained for completeness)
        t2_pos = t2.get('positive', False)
        if t2_pos:
            verdict = 'REDISTILLATION_SUPPORTED'
            note = 'PRIMARY+SECONDARY gates pass (T1+T2).'
        else:
            verdict = 'REDISTILLATION_SUGGESTIVE'
            note = 'PRIMARY gate passes (T1), secondary null.'
    else:
        # T1 null/negative: redistillation is dead.
        # T1 raw rho strongly negative = safety substitution finding.
        raw_rho = t1.get('raw_spearman_rho', 0)
        substitution = raw_rho < -0.3

        if substitution and t6_pos:
            verdict = 'REDISTILLATION_DEAD_II_INDEPENDENT_SAFETY'
            note = (f'Redistillation dead (T1 raw rho={raw_rho}: safety substitution). '
                    f'ii has independent forgiveness contribution beyond e-to-y (T6).')
        elif substitution:
            # Check if ii is ANTI-forgiveness (significant but negative)
            t6_beta_ii = t6.get('ctrl_beta_ii', 0) if t6 else 0
            t6_f_p = t6.get('ctrl_f_p_val', 1) if t6 else 1
            if t6_f_p < 0.05 and t6_beta_ii < 0:
                verdict = 'REDISTILLATION_DEAD_SAFETY_SUBSTITUTION'
                note = (f'Redistillation dead (T1 raw rho={raw_rho}: safety substitution). '
                        f'ii ANTI-predicts forgiveness (T6 beta={t6_beta_ii:.3f}, p={t6_f_p:.4f}): '
                        f'two safety strategies — e-to-y permissive, ii restrictive.')
            else:
                verdict = 'REDISTILLATION_DEAD_SAFETY_SUBSTITUTION'
                note = (f'Redistillation dead (T1 raw rho={raw_rho}: safety substitution). '
                        f'ii does not independently predict forgiveness (T6).')
        else:
            verdict = 'PURE_MECHANISM'
            note = 'No redistillation signatures. No safety substitution pattern.'

    return verdict, note


# ============================================================
# Main
# ============================================================

def main():
    start = time.time()
    rng = np.random.RandomState(SEED)

    print("Phase 597: Redistillation-ii Purpose Discrimination")
    print("=" * 60)

    # Data assembly
    print("Loading data...")
    b_tokens, a_tokens, line_index, folio_index, paragraphs = assemble_data()

    # Verification counts
    i_counts = Counter(t['i_class'] for t in b_tokens)
    n_ey = sum(1 for t in b_tokens if t['is_ey'])
    n_fl = sum(1 for t in b_tokens if t['is_fl'])
    n_a_head = sum(1 for t in b_tokens if t['is_a_head'])

    print(f"  B tokens: {len(b_tokens)}")
    print(f"  A tokens: {len(a_tokens)}")
    print(f"  i-class: {dict(i_counts)}")
    print(f"  e-to-y tokens: {n_ey}")
    print(f"  FL vocabulary tokens: {n_fl} ({100*n_fl/len(b_tokens):.1f}%)")
    print(f"  a-HEAD tokens: {n_a_head}")
    print(f"  Paragraphs: {len(paragraphs)}")
    print()

    # T1: e-to-y co-deployment (PRIMARY GATE)
    print("T1: e-to-y safety co-deployment...")
    t1 = run_t1(folio_index)
    print(f"  Raw rho={t1['raw_spearman_rho']}, "
          f"Full-controlled rho={t1['full_controlled_rho']} "
          f"(p={t1['full_controlled_p']})")
    print(f"  Positive: {t1['positive']}")
    print()

    # T2: A-side e-depth (SECONDARY GATE)
    print("T2: A-side e-depth co-occurrence...")
    t2 = run_t2(a_tokens)
    if t2.get('status') == 'INSUFFICIENT_DATA':
        print(f"  INSUFFICIENT DATA ({t2['n_records']} records)")
    else:
        print(f"  Raw rho={t2['raw_spearman_rho']}, "
              f"Length-controlled rho={t2['length_controlled_rho']} "
              f"(p={t2['length_controlled_p']})")
        print(f"  Positive: {t2['positive']}")
    print()

    # T3: FL state co-occurrence (SUPPORTING)
    print("T3: FL state co-occurrence...")
    t3 = run_t3(line_index, rng)
    gs = t3['group_stats']
    print(f"  ii-lines FL mean={gs['ii']['mean']} (n={gs['ii']['n']})")
    print(f"  si-lines FL mean={gs['si']['mean']} (n={gs['si']['n']})")
    print(f"  a-HEAD-no-i FL mean={gs['a_head_no_i']['mean']} "
          f"(n={gs['a_head_no_i']['n']})")
    print(f"  perm_p(ii vs si)={t3['perm_p_ii_vs_si']}, "
          f"perm_p(ii vs a-base)={t3['perm_p_ii_vs_a_baseline']}")
    print(f"  Positive: {t3['positive']}")
    print()

    # T4: Mode A residual (SUPPORTING)
    print("T4: Mode A specification residual...")
    t4 = run_t4(folio_index)
    if t4.get('status') == 'INSUFFICIENT_DATA':
        print("  INSUFFICIENT DATA")
    else:
        print(f"  beta_ii_prop={t4['beta_ii_prop_of_a_head']}, "
              f"t={t4['t_stat_ii']}, p={t4['p_val_ii']}")
        print(f"  Predictor correlation: {t4['predictor_correlation']}")
        print(f"  Positive: {t4['positive']}")
    print()

    # T5: OPERATION category co-occurrence (SUPPORTING)
    print("T5: OPERATION category co-occurrence...")
    t5 = run_t5(paragraphs)
    if t5.get('status') == 'INSUFFICIENT_DATA':
        print("  INSUFFICIENT DATA")
    else:
        print(f"  Raw rho={t5['raw_spearman_rho']}, "
              f"Section-controlled rho={t5['section_controlled_rho']} "
              f"(p={t5['section_controlled_p']})")
        print(f"  Positive: {t5['positive']}")
    print()

    # T6: Forgiveness prediction (CHARACTERIZATION)
    print("T6: Forgiveness prediction (ii independence test)...")
    t6 = run_t6(folio_index, line_index)
    if t6.get('status') == 'INSUFFICIENT_DATA':
        print(f"  INSUFFICIENT DATA ({t6['n_folios']} folios)")
    else:
        print(f"  Raw: R²(ey)={t6['raw_r2_ey_only']}, "
              f"R²(ey+ii)={t6['raw_r2_ey_plus_ii']}, "
              f"dR²={t6['raw_delta_r2']}, F={t6['raw_f_stat']}, p={t6['raw_f_p_val']}")
        print(f"  Section-controlled: R²(ey+sec)={t6['ctrl_r2_ey_plus_sec']}, "
              f"R²(ey+ii+sec)={t6['ctrl_r2_ey_ii_plus_sec']}, "
              f"dR²={t6['ctrl_delta_r2']}, F={t6['ctrl_f_stat']}, p={t6['ctrl_f_p_val']}")
        print(f"  beta_ii: raw={t6['raw_beta_ii']}, controlled={t6['ctrl_beta_ii']}")
        print(f"  Spearman ii-forgiveness: rho={t6['spearman_ii_forgiveness']}, "
              f"p={t6['spearman_p_ii']}")
        print(f"  Positive: {t6['positive']}")
    print()

    # Verdict
    verdict, note = compute_verdict(t1, t2, t3, t4, t5, t6)
    print(f"VERDICT: {verdict}")
    print(f"  {note}")

    elapsed = round(time.time() - start, 1)
    print(f"\nRuntime: {elapsed}s")

    # Save results
    results = {
        'metadata': {
            'phase': 597,
            'script': 'redistillation_ii_test.py',
            'runtime_seconds': elapsed,
            'n_b_tokens': len(b_tokens),
            'n_a_tokens': len(a_tokens),
            'seed': SEED,
            'i_class_counts': dict(i_counts),
            'verification': {
                'ey_count': n_ey,
                'fl_vocab_count': n_fl,
                'a_head_count': n_a_head,
                'n_paragraphs': len(paragraphs),
            },
        },
        'T1_ey_co_deployment': t1,
        'T2_a_side_e_depth': t2,
        'T3_fl_state_cooccurrence': t3,
        'T4_mode_a_residual': t4,
        'T5_operation_cooccurrence': t5,
        'T6_forgiveness_prediction': t6,
        'verdict': verdict,
        'verdict_note': note,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, 'redistillation_ii_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)

    print(f"Results saved to {out_path}")


if __name__ == '__main__':
    main()
