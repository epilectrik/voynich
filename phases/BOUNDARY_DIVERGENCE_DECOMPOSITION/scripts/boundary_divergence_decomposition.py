#!/usr/bin/env python3
"""
Phase 414: BOUNDARY_DIVERGENCE_DECOMPOSITION
===============================================
Decomposes the C1157 boundary divergence finding to understand what drives it.

5-test battery:
  T1: ENTRY_VS_EXIT_DECOMPOSITION (which boundary zone drives the effect?)
  T2: TRANSITION_CELL_DECOMPOSITION (which state transitions shift at boundaries?)
  T3: SECTION_INDEPENDENCE (is boundary divergence a section proxy?)
  T4: VOCABULARY_MEDIATION (does vocabulary composition explain it?)
  T5: GATEKEEPER_MEDIATION (is it just gatekeeping measured differently?)

Depends on: C1035, C1156, C1157, C1007, C976, C1140
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as scipy_stats

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ─────────────────────────────────────────────────────

N_CLASSES = 49
N_STATES = 6
MIN_ZONE_TRANS = 10

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}


# ── Pure-Python Statistics ────────────────────────────────────────

def round_floats(obj, digits=6):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def spearman_r(x, y):
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    def _rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = avg_rank
            i = j + 1
        return ranks

    rx = _rank(list(x))
    ry = _rank(list(y))
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    sd_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    sd_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if sd_x == 0 or sd_y == 0:
        return 0.0, 1.0
    rho = cov / (sd_x * sd_y)
    rho = max(-1.0, min(1.0, rho))
    if n <= 2:
        return rho, 1.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-12))
    df = n - 2
    x_val = df / (df + t_stat ** 2)
    p = 1.0 - _betainc(df / 2.0, 0.5, x_val)
    return rho, p


def _betainc(a, b, x, n_iter=200):
    if x <= 0:
        return 1.0
    if x >= 1:
        return 0.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for m in range(n_iter):
        if m == 0:
            num = 1.0
        elif m % 2 == 0:
            k = m // 2
            num = (k * (b - k) * x) / ((a + 2*k - 1) * (a + 2*k))
        else:
            k = (m + 1) // 2
            num = -((a + k) * (a + b + k) * x) / ((a + 2*k) * (a + 2*k + 1))
        d = 1.0 + num * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < 1e-30:
            c = 1e-30
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-10:
            break
    return 1.0 - front * f


def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-10)


def ols_fit(X, y):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, y_pred, ss_res, r2


def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    df_res = n_obs - k_full
    if df_res <= 0 or ss_res_full <= 0:
        return 0.0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - scipy_stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


def build_dummies(labels):
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


def partial_corr_spearman(x, y, Z):
    """Partial Spearman: residualize x and y on Z via OLS, then Spearman residuals."""
    n = len(x)
    X_z = np.column_stack([np.ones(n), Z]) if Z.ndim > 1 else np.column_stack([np.ones(n), Z.reshape(-1, 1)])
    beta_x = np.linalg.lstsq(X_z, x, rcond=None)[0]
    res_x = x - X_z @ beta_x
    beta_y = np.linalg.lstsq(X_z, y, rcond=None)[0]
    res_y = y - X_z @ beta_y
    return spearman_r(res_x.tolist(), res_y.tolist())


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ── Matrix Utilities ──────────────────────────────────────────────

def normalize_rows(m):
    row_sums = m.sum(axis=1, keepdims=True)
    return m / np.maximum(row_sums, 1e-12)


def compute_jsd(p, q, epsilon=1e-10):
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m)))


def build_zone_matrix(transitions):
    m = np.zeros((N_CLASSES, N_CLASSES))
    for src, tgt in transitions:
        m[src - 1, tgt - 1] += 1
    return m


def matrix_to_6state(m49):
    m6 = np.zeros((N_STATES, N_STATES))
    for src_cls in range(1, N_CLASSES + 1):
        si = STATE_IDX[CLASS_TO_STATE[src_cls]]
        for tgt_cls in range(1, N_CLASSES + 1):
            ti = STATE_IDX[CLASS_TO_STATE[tgt_cls]]
            m6[si, ti] += m49[src_cls - 1, tgt_cls - 1]
    return m6


# ── Data Loading ──────────────────────────────────────────────────

def load_data():
    print("Loading data...")

    # Class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' /
              'class_token_map.json', encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']

    # AXM folio data
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']
    valid_folios = set(folio_data.keys())

    # Dark pipeline MIDDLEs
    with open(PROJECT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
        dark_middles = set(json.load(f))

    morph = Morphology()

    # Build per-folio per-line token lists
    folio_lines = defaultdict(lambda: defaultdict(list))
    folio_token_counts = defaultdict(lambda: {'total': 0, 'gatekeeper': 0, 'dark': 0, 'axm': 0})

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        cls = token_to_class.get(w)
        if cls is None:
            # Still count for dark pipeline fraction (all tokens, not just classified)
            m = morph.extract(w)
            mid = m.middle if m else w
            folio_token_counts[t.folio]['total'] += 1
            if mid in dark_middles:
                folio_token_counts[t.folio]['dark'] += 1
            continue
        folio_token_counts[t.folio]['total'] += 1
        if cls in GATEKEEPER_CLASSES:
            folio_token_counts[t.folio]['gatekeeper'] += 1
        if CLASS_TO_STATE[cls] == 'AXM':
            folio_token_counts[t.folio]['axm'] += 1
        m = morph.extract(w)
        mid = m.middle if m else w
        if mid in dark_middles:
            folio_token_counts[t.folio]['dark'] += 1

        folio_lines[t.folio][t.line].append({
            'word': w,
            'cls': cls,
            'state': CLASS_TO_STATE[cls],
            'is_gatekeeper': cls in GATEKEEPER_CLASSES,
        })

    # Convert to line lists
    folio_line_lists = defaultdict(list)
    folio_sections = {}
    for folio in sorted(folio_lines.keys()):
        fd = folio_data.get(folio, {})
        folio_sections[folio] = fd.get('section', '?')
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    print(f"  Folios with lines: {len(folio_line_lists)}")
    print(f"  AXM data: {len(valid_folios)} folios")

    return (folio_line_lists, folio_data, valid_folios, folio_token_counts,
            folio_sections, dark_middles)


# ── Per-Folio Boundary Divergence ─────────────────────────────────

def compute_folio_boundary_divergence(folio_line_lists, folio_data, valid_folios,
                                       exclude_gatekeepers=False):
    """Compute per-folio boundary divergence. Optionally exclude gatekeeper transitions."""
    results = {}

    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]

        zone_trans = {'ENTRY': [], 'INTERIOR': [], 'EXIT': []}
        for tokens in lines:
            n = len(tokens)
            for i in range(n - 1):
                src_cls = tokens[i]['cls']
                tgt_cls = tokens[i + 1]['cls']

                if exclude_gatekeepers:
                    if src_cls in GATEKEEPER_CLASSES or tgt_cls in GATEKEEPER_CLASSES:
                        continue

                if i == 0:
                    zone = 'ENTRY'
                elif i + 1 == n - 1:
                    zone = 'EXIT'
                else:
                    zone = 'INTERIOR'
                zone_trans[zone].append((src_cls, tgt_cls))

        if (len(zone_trans['ENTRY']) < MIN_ZONE_TRANS or
            len(zone_trans['INTERIOR']) < MIN_ZONE_TRANS or
            len(zone_trans['EXIT']) < MIN_ZONE_TRANS):
            continue

        m6_entry = matrix_to_6state(build_zone_matrix(zone_trans['ENTRY']))
        m6_interior = matrix_to_6state(build_zone_matrix(zone_trans['INTERIOR']))
        m6_exit = matrix_to_6state(build_zone_matrix(zone_trans['EXIT']))

        jsd_entry = compute_jsd(m6_entry.flatten(), m6_interior.flatten())
        jsd_exit = compute_jsd(m6_exit.flatten(), m6_interior.flatten())

        results[folio] = {
            'jsd_entry': jsd_entry,
            'jsd_exit': jsd_exit,
            'boundary_div': jsd_entry + jsd_exit,
            'zone_counts': {z: len(zone_trans[z]) for z in zone_trans},
        }

    return results


# ── Test 1: ENTRY_VS_EXIT_DECOMPOSITION ──────────────────────────

def test1_entry_vs_exit(bd_data, folio_data):
    print("\n── Test 1: ENTRY_VS_EXIT_DECOMPOSITION ──")

    folios = sorted(bd_data.keys())
    n = len(folios)
    jsd_e = np.array([bd_data[f]['jsd_entry'] for f in folios])
    jsd_x = np.array([bd_data[f]['jsd_exit'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    print(f"  JSD_entry: mean={jsd_e.mean():.4f}, std={jsd_e.std():.4f}")
    print(f"  JSD_exit:  mean={jsd_x.mean():.4f}, std={jsd_x.std():.4f}")

    # Bivariate Spearman
    rho_e, p_e = spearman_r(jsd_e.tolist(), axm.tolist())
    rho_x, p_x = spearman_r(jsd_x.tolist(), axm.tolist())
    print(f"  Entry vs AXM: rho={rho_e:.4f}, p={p_e:.4f}")
    print(f"  Exit vs AXM:  rho={rho_x:.4f}, p={p_x:.4f}")

    # Partial correlations
    rho_e_ctrl, p_e_ctrl = partial_corr_spearman(jsd_e, axm, jsd_x)
    rho_x_ctrl, p_x_ctrl = partial_corr_spearman(jsd_x, axm, jsd_e)
    print(f"  Entry|Exit vs AXM: rho={rho_e_ctrl:.4f}, p={p_e_ctrl:.4f}")
    print(f"  Exit|Entry vs AXM: rho={rho_x_ctrl:.4f}, p={p_x_ctrl:.4f}")

    # Incremental regression
    regimes = [folio_data[f]['regime'] for f in folios]
    sections = [folio_data[f]['section'] for f in folios]
    pfx = np.array([folio_data[f]['prefix_entropy'] for f in folios])
    haz = np.array([folio_data[f]['hazard_density'] for f in folios])
    pc1 = np.array([folio_data[f]['bridge_pc1'] for f in folios])

    intercept = np.ones((n, 1))
    regime_dum = build_dummies(regimes)
    section_dum = build_dummies(sections)
    pfx_z = standardize(pfx).reshape(-1, 1)
    haz_z = standardize(haz).reshape(-1, 1)
    pc1_z = standardize(pc1).reshape(-1, 1)

    X_base = np.hstack([intercept, regime_dum, section_dum, pfx_z, haz_z, pc1_z])
    _, _, ss_base, r2_base = ols_fit(X_base, axm)
    loo_base = loo_cv_r2(X_base, axm)

    je_z = standardize(jsd_e).reshape(-1, 1)
    jx_z = standardize(jsd_x).reshape(-1, 1)

    # Entry only
    X_entry = np.hstack([X_base, je_z])
    _, _, ss_entry, r2_entry = ols_fit(X_entry, axm)
    loo_entry = loo_cv_r2(X_entry, axm)
    dr2_entry = r2_entry - r2_base
    f_entry, fp_entry = f_test_increment(ss_base, ss_entry, 1, n, X_entry.shape[1])

    # Exit only
    X_exit = np.hstack([X_base, jx_z])
    _, _, ss_exit, r2_exit = ols_fit(X_exit, axm)
    loo_exit = loo_cv_r2(X_exit, axm)
    dr2_exit = r2_exit - r2_base
    f_exit, fp_exit = f_test_increment(ss_base, ss_exit, 1, n, X_exit.shape[1])

    # Both
    X_both = np.hstack([X_base, je_z, jx_z])
    _, _, ss_both, r2_both = ols_fit(X_both, axm)
    loo_both = loo_cv_r2(X_both, axm)
    dr2_both = r2_both - r2_base
    f_both, fp_both = f_test_increment(ss_base, ss_both, 2, n, X_both.shape[1])

    print(f"  Baseline R2={r2_base:.4f}, LOO={loo_base:.4f}")
    print(f"  +Entry:  dR2={dr2_entry:.4f}, F={f_entry:.2f}, p={fp_entry:.4f}, LOO={loo_entry:.4f}")
    print(f"  +Exit:   dR2={dr2_exit:.4f}, F={f_exit:.2f}, p={fp_exit:.4f}, LOO={loo_exit:.4f}")
    print(f"  +Both:   dR2={dr2_both:.4f}, F={f_both:.2f}, p={fp_both:.4f}, LOO={loo_both:.4f}")

    if dr2_exit > 2 * max(dr2_entry, 0.001):
        verdict = 'EXIT_DOMINANT'
    elif dr2_entry > 2 * max(dr2_exit, 0.001):
        verdict = 'ENTRY_DOMINANT'
    else:
        verdict = 'BOTH_CONTRIBUTE'
    print(f"  Verdict: {verdict}")

    return {
        'jsd_entry_stats': {'mean': float(jsd_e.mean()), 'std': float(jsd_e.std())},
        'jsd_exit_stats': {'mean': float(jsd_x.mean()), 'std': float(jsd_x.std())},
        'bivariate_spearman': {
            'entry_vs_axm': {'rho': rho_e, 'p': p_e},
            'exit_vs_axm': {'rho': rho_x, 'p': p_x},
        },
        'partial_spearman': {
            'entry_ctrl_exit': {'rho': rho_e_ctrl, 'p': p_e_ctrl},
            'exit_ctrl_entry': {'rho': rho_x_ctrl, 'p': p_x_ctrl},
        },
        'incremental_regression': {
            'baseline_r2': r2_base, 'baseline_loo': loo_base,
            'entry_only': {'dr2': dr2_entry, 'f_stat': f_entry, 'f_p': fp_entry, 'loo': loo_entry},
            'exit_only': {'dr2': dr2_exit, 'f_stat': f_exit, 'f_p': fp_exit, 'loo': loo_exit},
            'both': {'dr2': dr2_both, 'f_stat': f_both, 'f_p': fp_both, 'loo': loo_both},
        },
        'verdict': verdict,
    }


# ── Test 2: TRANSITION_CELL_DECOMPOSITION ────────────────────────

def test2_transition_cells(folio_line_lists, valid_folios, folio_data):
    print("\n── Test 2: TRANSITION_CELL_DECOMPOSITION ──")

    # Build aggregate zone 6-state matrices
    agg_zones = {'ENTRY': [], 'INTERIOR': [], 'EXIT': []}
    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        for tokens in folio_line_lists[folio]:
            n = len(tokens)
            for i in range(n - 1):
                src_cls = tokens[i]['cls']
                tgt_cls = tokens[i + 1]['cls']
                if i == 0:
                    zone = 'ENTRY'
                elif i + 1 == n - 1:
                    zone = 'EXIT'
                else:
                    zone = 'INTERIOR'
                agg_zones[zone].append((src_cls, tgt_cls))

    m6_entry = normalize_rows(matrix_to_6state(build_zone_matrix(agg_zones['ENTRY'])))
    m6_interior = normalize_rows(matrix_to_6state(build_zone_matrix(agg_zones['INTERIOR'])))
    m6_exit = normalize_rows(matrix_to_6state(build_zone_matrix(agg_zones['EXIT'])))

    # Compute per-cell deltas
    entry_deltas = []
    exit_deltas = []
    for si in range(N_STATES):
        for ti in range(N_STATES):
            ed = float(m6_entry[si, ti] - m6_interior[si, ti])
            xd = float(m6_exit[si, ti] - m6_interior[si, ti])
            entry_deltas.append({
                'src': STATE_ORDER[si], 'tgt': STATE_ORDER[ti],
                'delta': ed, 'abs_delta': abs(ed)
            })
            exit_deltas.append({
                'src': STATE_ORDER[si], 'tgt': STATE_ORDER[ti],
                'delta': xd, 'abs_delta': abs(xd)
            })

    entry_deltas.sort(key=lambda x: x['abs_delta'], reverse=True)
    exit_deltas.sort(key=lambda x: x['abs_delta'], reverse=True)

    # AXM→AXM fraction of total delta
    axm_idx = STATE_IDX['AXM']
    total_entry_delta = sum(d['abs_delta'] for d in entry_deltas)
    total_exit_delta = sum(d['abs_delta'] for d in exit_deltas)
    axm_axm_entry_delta = abs(float(m6_entry[axm_idx, axm_idx] - m6_interior[axm_idx, axm_idx]))
    axm_axm_exit_delta = abs(float(m6_exit[axm_idx, axm_idx] - m6_interior[axm_idx, axm_idx]))

    entry_frac = axm_axm_entry_delta / max(total_entry_delta, 1e-10)
    exit_frac = axm_axm_exit_delta / max(total_exit_delta, 1e-10)
    combined_frac = (axm_axm_entry_delta + axm_axm_exit_delta) / max(total_entry_delta + total_exit_delta, 1e-10)

    print(f"  Top entry deltas:")
    for d in entry_deltas[:5]:
        print(f"    {d['src']}→{d['tgt']}: {d['delta']:+.4f}")
    print(f"  Top exit deltas:")
    for d in exit_deltas[:5]:
        print(f"    {d['src']}→{d['tgt']}: {d['delta']:+.4f}")
    print(f"  AXM→AXM fraction: entry={entry_frac:.3f}, exit={exit_frac:.3f}, combined={combined_frac:.3f}")

    if combined_frac > 0.50:
        verdict = 'AXM_SELF_DOMINATED'
    elif combined_frac < 0.25:
        verdict = 'ROUTING_SHIFT'
    else:
        verdict = 'MULTI_TRANSITION'
    print(f"  Verdict: {verdict}")

    return {
        'top_entry_deltas': entry_deltas[:10],
        'top_exit_deltas': exit_deltas[:10],
        'axm_axm_fraction': {
            'entry': entry_frac, 'exit': exit_frac, 'combined': combined_frac
        },
        'verdict': verdict,
    }


# ── Test 3: SECTION_INDEPENDENCE ──────────────────────────────────

def test3_section_independence(bd_data, folio_data):
    print("\n── Test 3: SECTION_INDEPENDENCE ──")

    folios = sorted(bd_data.keys())
    n = len(folios)
    bd = np.array([bd_data[f]['boundary_div'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])
    sections = [folio_data[f]['section'] for f in folios]

    # ANOVA: boundary_div ~ section
    intercept = np.ones((n, 1))
    section_dum = build_dummies(sections)
    X_section = np.hstack([intercept, section_dum])
    _, _, ss_sec, r2_sec = ols_fit(X_section, bd)

    # F-test for section effect on BD
    X_null = intercept
    _, _, ss_null, _ = ols_fit(X_null, bd)
    k_sec = section_dum.shape[1]
    f_sec, fp_sec = f_test_increment(ss_null, ss_sec, k_sec, n, X_section.shape[1])

    print(f"  Section R2 on boundary_div: {r2_sec:.4f}")
    print(f"  Section ANOVA: F={f_sec:.2f}, p={fp_sec:.4f}")

    # Partial correlation: BD vs AXM controlling for section
    rho_partial, p_partial = partial_corr_spearman(bd, axm, section_dum)
    print(f"  Partial corr (BD vs AXM | section): rho={rho_partial:.4f}, p={p_partial:.4f}")

    # Incremental: BD on section-only baseline for AXM
    _, _, ss_sec_axm, r2_sec_axm = ols_fit(X_section, axm)
    loo_sec_axm = loo_cv_r2(X_section, axm)

    bd_z = standardize(bd).reshape(-1, 1)
    X_sec_bd = np.hstack([X_section, bd_z])
    _, _, ss_sec_bd, r2_sec_bd = ols_fit(X_sec_bd, axm)
    loo_sec_bd = loo_cv_r2(X_sec_bd, axm)
    dr2_sec_bd = r2_sec_bd - r2_sec_axm
    f_sec_bd, fp_sec_bd = f_test_increment(ss_sec_axm, ss_sec_bd, 1, n, X_sec_bd.shape[1])

    print(f"  Section-only baseline for AXM: R2={r2_sec_axm:.4f}, LOO={loo_sec_axm:.4f}")
    print(f"  +BD: R2={r2_sec_bd:.4f}, LOO={loo_sec_bd:.4f}, dR2={dr2_sec_bd:.4f}, "
          f"F={f_sec_bd:.2f}, p={fp_sec_bd:.4f}")

    if r2_sec > 0.60:
        verdict = 'SECTION_CONFOUNDED'
    elif r2_sec < 0.30:
        verdict = 'SECTION_INDEPENDENT'
    else:
        verdict = 'SECTION_PARTIALLY_CONFOUNDED'
    print(f"  Verdict: {verdict}")

    return {
        'section_r2_on_bd': r2_sec,
        'section_anova': {'F': f_sec, 'p': fp_sec},
        'partial_corr_bd_axm_ctrl_section': {'rho': rho_partial, 'p': p_partial},
        'incremental_on_section_baseline': {
            'section_only_r2': r2_sec_axm, 'section_only_loo': loo_sec_axm,
            'with_bd_r2': r2_sec_bd, 'with_bd_loo': loo_sec_bd,
            'dr2': dr2_sec_bd, 'f_stat': f_sec_bd, 'f_p': fp_sec_bd,
        },
        'verdict': verdict,
    }


# ── Test 4: VOCABULARY_MEDIATION ──────────────────────────────────

def test4_vocabulary_mediation(bd_data, folio_data, folio_token_counts):
    print("\n── Test 4: VOCABULARY_MEDIATION ──")

    folios = sorted(bd_data.keys())
    n = len(folios)
    bd = np.array([bd_data[f]['boundary_div'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    # Per-folio dark fraction
    dark_frac = np.array([
        folio_token_counts[f]['dark'] / max(folio_token_counts[f]['total'], 1)
        for f in folios
    ])
    bridge_pc1 = np.array([folio_data[f]['bridge_pc1'] for f in folios])

    print(f"  Dark fraction: mean={dark_frac.mean():.4f}, std={dark_frac.std():.4f}")

    # Correlations
    rho_dk_bd, p_dk_bd = spearman_r(dark_frac.tolist(), bd.tolist())
    rho_br_bd, p_br_bd = spearman_r(bridge_pc1.tolist(), bd.tolist())
    rho_dk_axm, p_dk_axm = spearman_r(dark_frac.tolist(), axm.tolist())
    rho_br_axm, p_br_axm = spearman_r(bridge_pc1.tolist(), axm.tolist())

    print(f"  Dark vs BD: rho={rho_dk_bd:.4f}, p={p_dk_bd:.4f}")
    print(f"  Bridge_PC1 vs BD: rho={rho_br_bd:.4f}, p={p_br_bd:.4f}")
    print(f"  Dark vs AXM: rho={rho_dk_axm:.4f}, p={p_dk_axm:.4f}")
    print(f"  Bridge_PC1 vs AXM: rho={rho_br_axm:.4f}, p={p_br_axm:.4f}")

    # Coefficient shrinkage test
    regimes = [folio_data[f]['regime'] for f in folios]
    sections = [folio_data[f]['section'] for f in folios]
    pfx = np.array([folio_data[f]['prefix_entropy'] for f in folios])
    haz = np.array([folio_data[f]['hazard_density'] for f in folios])
    pc1 = bridge_pc1

    intercept = np.ones((n, 1))
    regime_dum = build_dummies(regimes)
    section_dum = build_dummies(sections)
    pfx_z = standardize(pfx).reshape(-1, 1)
    haz_z = standardize(haz).reshape(-1, 1)
    pc1_z = standardize(pc1).reshape(-1, 1)
    bd_z = standardize(bd).reshape(-1, 1)
    dk_z = standardize(dark_frac).reshape(-1, 1)

    X_base = np.hstack([intercept, regime_dum, section_dum, pfx_z, haz_z, pc1_z])

    # Model A: baseline + BD
    X_a = np.hstack([X_base, bd_z])
    beta_a, _, _, r2_a = ols_fit(X_a, axm)
    beta_bd_alone = float(beta_a[-1])

    # Model B: baseline + BD + dark_frac (bridge_pc1 already in baseline)
    X_b = np.hstack([X_base, bd_z, dk_z])
    beta_b, _, _, r2_b = ols_fit(X_b, axm)
    beta_bd_with_vocab = float(beta_b[-2])  # BD is second-to-last

    shrinkage = 1 - abs(beta_bd_with_vocab) / max(abs(beta_bd_alone), 1e-10)
    print(f"  Beta_BD alone: {beta_bd_alone:.4f}")
    print(f"  Beta_BD with vocab: {beta_bd_with_vocab:.4f}")
    print(f"  Shrinkage: {shrinkage:.4f}")

    if shrinkage > 0.50:
        verdict = 'VOCABULARY_MEDIATED'
    elif shrinkage > 0.20:
        verdict = 'VOCABULARY_PARTIAL'
    else:
        verdict = 'VOCABULARY_INDEPENDENT'
    print(f"  Verdict: {verdict}")

    return {
        'dark_frac_stats': {'mean': float(dark_frac.mean()), 'std': float(dark_frac.std())},
        'correlations': {
            'dark_vs_bd': {'rho': rho_dk_bd, 'p': p_dk_bd},
            'bridge_pc1_vs_bd': {'rho': rho_br_bd, 'p': p_br_bd},
            'dark_vs_axm': {'rho': rho_dk_axm, 'p': p_dk_axm},
            'bridge_pc1_vs_axm': {'rho': rho_br_axm, 'p': p_br_axm},
        },
        'coefficient_shrinkage': {
            'beta_bd_alone': beta_bd_alone,
            'beta_bd_with_vocab': beta_bd_with_vocab,
            'shrinkage_ratio': shrinkage,
        },
        'verdict': verdict,
    }


# ── Test 5: GATEKEEPER_MEDIATION ─────────────────────────────────

def test5_gatekeeper_mediation(bd_data, folio_line_lists, folio_data, valid_folios,
                                folio_token_counts):
    print("\n── Test 5: GATEKEEPER_MEDIATION ──")

    folios = sorted(bd_data.keys())
    n = len(folios)
    bd = np.array([bd_data[f]['boundary_div'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    # Gatekeeper density per folio
    gk_density = np.array([
        folio_token_counts[f]['gatekeeper'] / max(folio_token_counts[f]['total'], 1)
        for f in folios
    ])
    gk_axm_frac = np.array([
        folio_token_counts[f]['gatekeeper'] / max(folio_token_counts[f]['axm'], 1)
        for f in folios
    ])

    print(f"  Gatekeeper density: mean={gk_density.mean():.4f}, std={gk_density.std():.4f}")
    print(f"  Gatekeeper/AXM frac: mean={gk_axm_frac.mean():.4f}")

    rho_gk_bd, p_gk_bd = spearman_r(gk_density.tolist(), bd.tolist())
    rho_gk_axm, p_gk_axm = spearman_r(gk_density.tolist(), axm.tolist())
    print(f"  GK density vs BD: rho={rho_gk_bd:.4f}, p={p_gk_bd:.4f}")
    print(f"  GK density vs AXM: rho={rho_gk_axm:.4f}, p={p_gk_axm:.4f}")

    # Partial: BD vs AXM controlling for gatekeeper density
    rho_partial, p_partial = partial_corr_spearman(bd, axm, gk_density)
    print(f"  Partial BD vs AXM | GK: rho={rho_partial:.4f}, p={p_partial:.4f}")

    # Recompute BD excluding gatekeeper transitions
    gkfree_bd = compute_folio_boundary_divergence(
        folio_line_lists, folio_data, valid_folios, exclude_gatekeepers=True)

    # Align with original folios
    gkfree_folios = [f for f in folios if f in gkfree_bd]
    n_gkfree = len(gkfree_folios)
    print(f"  Folios after GK exclusion: {n_gkfree} (original: {n})")

    gkfree_bd_vals = np.array([gkfree_bd[f]['boundary_div'] for f in gkfree_folios])
    gkfree_axm = np.array([folio_data[f]['axm_self'] for f in gkfree_folios])

    rho_gkfree, p_gkfree = spearman_r(gkfree_bd_vals.tolist(), gkfree_axm.tolist())
    print(f"  GK-free BD vs AXM: rho={rho_gkfree:.4f}, p={p_gkfree:.4f}")
    print(f"  GK-free BD: mean={gkfree_bd_vals.mean():.4f}, std={gkfree_bd_vals.std():.4f}")

    # Incremental regression: GK-free BD on C1035 baseline
    regimes = [folio_data[f]['regime'] for f in gkfree_folios]
    sections = [folio_data[f]['section'] for f in gkfree_folios]
    pfx = np.array([folio_data[f]['prefix_entropy'] for f in gkfree_folios])
    haz = np.array([folio_data[f]['hazard_density'] for f in gkfree_folios])
    pc1 = np.array([folio_data[f]['bridge_pc1'] for f in gkfree_folios])

    intercept = np.ones((n_gkfree, 1))
    regime_dum = build_dummies(regimes)
    section_dum = build_dummies(sections)
    pfx_z = standardize(pfx).reshape(-1, 1)
    haz_z = standardize(haz).reshape(-1, 1)
    pc1_z = standardize(pc1).reshape(-1, 1)

    X_base = np.hstack([intercept, regime_dum, section_dum, pfx_z, haz_z, pc1_z])
    _, _, ss_base, r2_base = ols_fit(X_base, gkfree_axm)
    loo_base = loo_cv_r2(X_base, gkfree_axm)

    gkfree_bd_z = standardize(gkfree_bd_vals).reshape(-1, 1)
    X_ext = np.hstack([X_base, gkfree_bd_z])
    _, _, ss_ext, r2_ext = ols_fit(X_ext, gkfree_axm)
    loo_ext = loo_cv_r2(X_ext, gkfree_axm)
    dr2_gkfree = r2_ext - r2_base
    f_gkfree, fp_gkfree = f_test_increment(ss_base, ss_ext, 1, n_gkfree, X_ext.shape[1])

    # Compare to original dR2 (0.0845 from Phase 413)
    original_dr2 = 0.0845
    dr2_ratio = dr2_gkfree / max(original_dr2, 1e-10)
    dr2_drop = 1 - dr2_ratio

    print(f"  GK-free baseline R2={r2_base:.4f}, LOO={loo_base:.4f}")
    print(f"  GK-free +BD: R2={r2_ext:.4f}, LOO={loo_ext:.4f}")
    print(f"  GK-free dR2={dr2_gkfree:.4f}, F={f_gkfree:.2f}, p={fp_gkfree:.4f}")
    print(f"  dR2 ratio vs original: {dr2_ratio:.3f} (drop={dr2_drop:.3f})")

    if dr2_drop > 0.50:
        verdict = 'GATEKEEPER_MEDIATED'
    elif dr2_drop > 0.20:
        verdict = 'GATEKEEPER_PARTIAL'
    else:
        verdict = 'GATEKEEPER_INDEPENDENT'
    print(f"  Verdict: {verdict}")

    return {
        'gatekeeper_density_stats': {
            'mean': float(gk_density.mean()), 'std': float(gk_density.std()),
            'mean_axm_frac': float(gk_axm_frac.mean()),
        },
        'gatekeeper_vs_bd': {'rho': rho_gk_bd, 'p': p_gk_bd},
        'gatekeeper_vs_axm': {'rho': rho_gk_axm, 'p': p_gk_axm},
        'partial_bd_axm_ctrl_gk': {'rho': rho_partial, 'p': p_partial},
        'gatekeeper_free': {
            'n_folios': n_gkfree,
            'bd_stats': {'mean': float(gkfree_bd_vals.mean()), 'std': float(gkfree_bd_vals.std())},
            'spearman_vs_axm': {'rho': rho_gkfree, 'p': p_gkfree},
            'baseline_r2': r2_base, 'baseline_loo': loo_base,
            'extended_r2': r2_ext, 'extended_loo': loo_ext,
            'dr2': dr2_gkfree, 'f_stat': f_gkfree, 'f_p': fp_gkfree,
        },
        'dr2_ratio_vs_original': dr2_ratio,
        'dr2_drop': dr2_drop,
        'verdict': verdict,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 414: BOUNDARY_DIVERGENCE_DECOMPOSITION")
    print("=" * 60)

    (folio_line_lists, folio_data, valid_folios, folio_token_counts,
     folio_sections, dark_middles) = load_data()

    # Compute per-folio boundary divergence (replicating Phase 413)
    bd_data = compute_folio_boundary_divergence(folio_line_lists, folio_data, valid_folios)
    print(f"\n  Folios with boundary divergence: {len(bd_data)}")
    bd_vals = [bd_data[f]['boundary_div'] for f in bd_data]
    print(f"  BD mean={np.mean(bd_vals):.4f}, std={np.std(bd_vals):.4f}")

    t1 = test1_entry_vs_exit(bd_data, folio_data)
    t2 = test2_transition_cells(folio_line_lists, valid_folios, folio_data)
    t3 = test3_section_independence(bd_data, folio_data)
    t4 = test4_vocabulary_mediation(bd_data, folio_data, folio_token_counts)
    t5 = test5_gatekeeper_mediation(bd_data, folio_line_lists, folio_data,
                                     valid_folios, folio_token_counts)

    # Synthesis
    gk_verdict = t5['verdict']
    sec_verdict = t3['verdict']

    if gk_verdict == 'GATEKEEPER_MEDIATED' and sec_verdict == 'SECTION_CONFOUNDED':
        overall = 'BOUNDARY_DIVERGENCE_REDUCES_TO_GATEKEEPING'
    elif gk_verdict == 'GATEKEEPER_INDEPENDENT' and sec_verdict == 'SECTION_INDEPENDENT':
        overall = 'BOUNDARY_DIVERGENCE_NOVEL_AXIS'
    else:
        overall = 'BOUNDARY_DIVERGENCE_PARTIALLY_EXPLAINED'

    print(f"\n── SYNTHESIS ──")
    print(f"  T1={t1['verdict']}")
    print(f"  T2={t2['verdict']}")
    print(f"  T3={t3['verdict']}")
    print(f"  T4={t4['verdict']}")
    print(f"  T5={t5['verdict']}")
    print(f"  Overall: {overall}")

    output = {
        'phase': 'BOUNDARY_DIVERGENCE_DECOMPOSITION',
        'phase_number': 414,
        'depends_on': ['C1035', 'C1156', 'C1157', 'C1007', 'C976', 'C1140'],
        'n_folios': len(bd_data),
        'test1_entry_vs_exit_decomposition': t1,
        'test2_transition_cell_decomposition': t2,
        'test3_section_independence': t3,
        'test4_vocabulary_mediation': t4,
        'test5_gatekeeper_mediation': t5,
        'synthesis': {
            'verdicts': {
                't1': t1['verdict'],
                't2': t2['verdict'],
                't3': t3['verdict'],
                't4': t4['verdict'],
                't5': t5['verdict'],
            },
            'overall': overall,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'boundary_divergence_decomposition.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
