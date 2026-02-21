#!/usr/bin/env python3
"""
Phase 417: RESIDUAL_FREEDOM_CHARACTERIZATION
=============================================
Tests whether the remaining ~27% AXM residual (from Phase 416 dual boundary model)
is genuinely irreducible design freedom or contains unmeasured structure.

5-test battery:
  T1: UNIVARIATE_RESIDUAL_SCAN (Spearman of ~25 candidates with residuals, Holm correction)
  T2: NONLINEAR_RESIDUAL_DETECTION (Random Forest on residuals, permutation test)
  T3: SPATIAL_AUTOCORRELATION (lag-1 autocorrelation in manuscript order)
  T4: DESIGN_FREEDOM_PROFILE (normality, C458 asymmetry, regime homogeneity)
  T5: EXHAUSTIVE_OLS_EXTENSION (gated: only if T1/T2 find signal)

Depends on: C1035, C1168, C458, C980, C976
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
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ─────────────────────────────────────────────────────

N_CLASSES = 49
N_STATES = 6
MIN_ZONE_TRANS = 10
MIN_CLOSERS = 10

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

# LINK classes (C366): class 6 = LINK operator
LINK_CLASS = 6

# Kernel classes for k/h/e fractions
KERNEL_CLASSES = {
    'k': {1, 2, 3, 4, 5, 6},       # k-kernel (core operators)
    'h': {7, 30, 38, 40},           # h-kernel (flow operators)
    'e': {9, 13, 14, 23, 10, 11, 12},  # e-kernel (FQ + CC)
}


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


def shannon_entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)


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

def compute_jsd(p, q, epsilon=1e-10):
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m_arr = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m_arr)) + 0.5 * np.sum(q * np.log2(q / m_arr)))


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

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' /
              'class_token_map.json', encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']
    class_to_role = cmap['class_to_role']

    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']
    valid_folios = set(folio_data.keys())

    morph = Morphology()
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Single transcript pass: collect line data AND compute new per-folio metrics
    folio_lines = defaultdict(lambda: defaultdict(list))
    folio_token_counts = Counter()
    folio_link_counts = Counter()
    folio_ht_counts = Counter()  # HT-type tokens
    folio_compound_counts = Counter()
    folio_articulator_counts = Counter()
    folio_word_lengths = defaultdict(list)
    folio_middles = defaultdict(set)
    folio_unique_middles = defaultdict(set)  # Track per-folio for uniqueness

    all_folio_middles = defaultdict(Counter)  # folio -> {middle: count}

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue

        m = morph.extract(w)
        prefix = m.prefix if m else None
        middle = m.middle if m else None

        folio_lines[t.folio][t.line].append({
            'word': w,
            'cls': cls,
            'state': CLASS_TO_STATE[cls],
            'role': class_to_role.get(str(cls), 'UNKNOWN'),
            'prefix': prefix,
            'is_gatekeeper': cls in GATEKEEPER_CLASSES,
        })

        # Per-folio metric accumulation
        folio_token_counts[t.folio] += 1

        # LINK density
        if cls == LINK_CLASS:
            folio_link_counts[t.folio] += 1

        # HT density (classes in HT set — approximate via HT/UN membership)
        # Use a simple proxy: tokens with articulator are often HT-associated
        if m and m.has_articulator:
            folio_ht_counts[t.folio] += 1
            folio_articulator_counts[t.folio] += 1

        # Word length
        folio_word_lengths[t.folio].append(len(w))

        # MIDDLE tracking
        if middle:
            folio_middles[t.folio].add(middle)
            all_folio_middles[t.folio][middle] += 1

            # Compound MIDDLE detection
            if mid_analyzer.is_compound(middle):
                folio_compound_counts[t.folio] += 1

    # Compute folio-unique MIDDLEs (appear in only one folio)
    middle_folio_map = defaultdict(set)
    for folio, middles in folio_middles.items():
        for mid in middles:
            middle_folio_map[mid].add(folio)
    for folio in folio_middles:
        folio_unique_middles[folio] = {mid for mid in folio_middles[folio]
                                        if len(middle_folio_map[mid]) == 1}

    # Build folio line lists (for transition analysis)
    folio_line_lists = defaultdict(list)
    for folio in sorted(folio_lines.keys()):
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    # Compute per-folio new metrics
    new_metrics = {}
    for folio in valid_folios:
        n_tok = folio_token_counts.get(folio, 0)
        if n_tok == 0:
            continue
        new_metrics[folio] = {
            'link_density': folio_link_counts.get(folio, 0) / n_tok,
            'ht_density_approx': folio_ht_counts.get(folio, 0) / n_tok,
            'compound_rate': folio_compound_counts.get(folio, 0) / n_tok,
            'articulator_rate': folio_articulator_counts.get(folio, 0) / n_tok,
            'mean_word_length': np.mean(folio_word_lengths.get(folio, [0])),
            'folio_unique_middle_count': len(folio_unique_middles.get(folio, set())),
            'n_distinct_middles': len(folio_middles.get(folio, set())),
        }

    # Compute kernel fractions per folio
    for folio in valid_folios:
        if folio not in folio_line_lists:
            continue
        k_count = 0
        h_count = 0
        e_count = 0
        total = 0
        for line_tokens in folio_line_lists[folio]:
            for tok in line_tokens:
                c = tok['cls']
                total += 1
                if c in KERNEL_CLASSES['k']:
                    k_count += 1
                elif c in KERNEL_CLASSES['h']:
                    h_count += 1
                elif c in KERNEL_CLASSES['e']:
                    e_count += 1
        if total > 0 and folio in new_metrics:
            new_metrics[folio]['k_frac'] = k_count / total
            new_metrics[folio]['h_frac'] = h_count / total
            new_metrics[folio]['e_frac'] = e_count / total

    print(f"  Folios with lines: {len(folio_line_lists)}")
    print(f"  AXM data: {len(valid_folios)} folios")
    print(f"  New metrics computed: {len(new_metrics)} folios")

    return folio_line_lists, folio_data, valid_folios, class_to_role, new_metrics


# ── Replicate Phase 416 Dual Model ───────────────────────────────

def compute_folio_divergence(folio_line_lists, folio_data, valid_folios):
    """Compute per-folio entry AND exit divergence vs interior (replicate Phase 416)."""
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
        results[folio] = {'jsd_entry': jsd_entry, 'jsd_exit': jsd_exit}
    return results


def compute_boundary_properties(folio_line_lists, valid_folios):
    """Extract per-folio opener AND closer properties (replicate Phase 416)."""
    results = {}
    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]
        opener_states = []
        entry_transitions = []
        exit_transitions = []
        exit_gatekeeper_count = 0
        exit_total = 0
        # Entry opener role tracking
        role_counts = Counter()

        for tokens in lines:
            if len(tokens) < 4:
                continue
            opener = tokens[0]
            follower = tokens[1]
            penultimate = tokens[-2]
            closer = tokens[-1]

            opener_states.append(opener['state'])
            entry_transitions.append((opener['state'], follower['state']))
            exit_transitions.append((penultimate['state'], closer['state']))
            role_counts[opener['role']] += 1

            if penultimate['is_gatekeeper'] or closer['is_gatekeeper']:
                exit_gatekeeper_count += 1
            exit_total += 1

        n_lines = exit_total
        if n_lines < MIN_CLOSERS:
            continue

        # AXM return rate
        axm_returns = sum(1 for _, tgt in entry_transitions if tgt == 'AXM')
        axm_return_rate = axm_returns / len(entry_transitions)

        # AXM departure rate
        axm_exits = sum(1 for src, tgt in exit_transitions if src == 'AXM' and tgt != 'AXM')
        axm_sources = sum(1 for src, _ in exit_transitions if src == 'AXM')
        axm_departure_rate = axm_exits / max(axm_sources, 1)

        # Exit routing entropy
        exit_tgt_counts = Counter(tgt for _, tgt in exit_transitions)
        exit_tgt_probs = [c / n_lines for c in exit_tgt_counts.values()]
        exit_routing_entropy = shannon_entropy(exit_tgt_probs)

        # Gatekeeper exit fraction
        gatekeeper_exit_frac = exit_gatekeeper_count / max(exit_total, 1)

        # Hazard exit fraction
        hazard_exit_count = sum(1 for _, tgt in exit_transitions if tgt == 'FL_HAZ')
        hazard_exit_frac = hazard_exit_count / max(exit_total, 1)

        # Opener role entropy
        total_roles = sum(role_counts.values())
        role_probs = [c / total_roles for c in role_counts.values()]
        role_entropy = shannon_entropy(role_probs)

        # Init specialist fraction (from Phase 415)
        INIT_SPECIALIST_PREFIXES = {'po', 'dch', 'so', 'tch', 'pch', 'sa'}
        # We don't have prefix data here directly; we'll use role_entropy and routing_concentration
        # Routing concentration
        axm_frac_entry = sum(1 for s in opener_states if s == 'AXM') / max(len(opener_states), 1)

        results[folio] = {
            'n_lines': n_lines,
            'axm_return_rate': axm_return_rate,
            'axm_departure_rate': axm_departure_rate,
            'exit_routing_entropy': exit_routing_entropy,
            'gatekeeper_exit_frac': gatekeeper_exit_frac,
            'hazard_exit_frac': hazard_exit_frac,
            'role_entropy': role_entropy,
            'opener_axm_frac': axm_frac_entry,
        }

    return results


def build_baseline(folios, folio_data):
    n = len(folios)
    axm = np.array([folio_data[f]['axm_self'] for f in folios])
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
    return X_base, axm


def build_current_best_model(folios, folio_data, div_data, boundary_data):
    """Build the Phase 416 dual boundary model, return residuals."""
    X_base, axm = build_baseline(folios, folio_data)

    jsd_entry = np.array([div_data[f]['jsd_entry'] for f in folios])
    axm_return = np.array([boundary_data[f]['axm_return_rate'] for f in folios])
    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in folios])
    axm_departure = np.array([boundary_data[f]['axm_departure_rate'] for f in folios])

    je_z = standardize(jsd_entry).reshape(-1, 1)
    arr_z = standardize(axm_return).reshape(-1, 1)
    jx_z = standardize(jsd_exit).reshape(-1, 1)
    dep_z = standardize(axm_departure).reshape(-1, 1)

    X_dual = np.hstack([X_base, je_z, arr_z, jx_z, dep_z])
    beta, y_pred, ss_res, r2 = ols_fit(X_dual, axm)
    loo = loo_cv_r2(X_dual, axm)
    residuals = axm - y_pred

    return X_dual, axm, residuals, y_pred, r2, loo


# ── Candidate Predictor Assembly ──────────────────────────────────

def assemble_candidates(folios, folio_data, boundary_data, new_metrics):
    """Build predictor matrix from all candidates NOT in current model."""
    predictors = {}

    # From AXM JSON (not in model: paragraph_count, ht_line1_density,
    # gatekeeper_fraction, qo_fraction, vocab_residual, line_count, vocab_size, n_tokens)
    for key in ['paragraph_count', 'ht_line1_density', 'gatekeeper_fraction',
                'qo_fraction', 'vocab_residual', 'line_count', 'vocab_size', 'n_tokens']:
        vals = []
        ok = True
        for f in folios:
            v = folio_data[f].get(key)
            if v is None:
                ok = False
                break
            vals.append(v)
        if ok:
            predictors[key] = np.array(vals)

    # From boundary properties (not in model: exit_routing_entropy, gk_exit_frac,
    # hazard_exit_frac, role_entropy, opener_axm_frac)
    for key in ['exit_routing_entropy', 'gatekeeper_exit_frac', 'hazard_exit_frac',
                'role_entropy', 'opener_axm_frac']:
        vals = []
        ok = True
        for f in folios:
            if f not in boundary_data:
                ok = False
                break
            v = boundary_data[f].get(key)
            if v is None:
                ok = False
                break
            vals.append(v)
        if ok:
            predictors[key] = np.array(vals)

    # From new transcript metrics
    for key in ['link_density', 'ht_density_approx', 'compound_rate', 'articulator_rate',
                'mean_word_length', 'folio_unique_middle_count', 'n_distinct_middles',
                'k_frac', 'h_frac', 'e_frac']:
        vals = []
        ok = True
        for f in folios:
            if f not in new_metrics:
                ok = False
                break
            v = new_metrics[f].get(key)
            if v is None:
                ok = False
                break
            vals.append(v)
        if ok:
            predictors[key] = np.array(vals)

    return predictors


# ── Folio Ordering ────────────────────────────────────────────────

def folio_sort_key(folio):
    """Parse folio name to physical manuscript order (e.g. f75r -> 75.0, f75v -> 75.5)."""
    digits = ''.join(c for c in folio if c.isdigit())
    num = int(digits) if digits else 0
    side = 0 if folio.endswith('r') else 1
    return (num, side)


# ── Test 1: UNIVARIATE_RESIDUAL_SCAN ─────────────────────────────

def test1_univariate_residual_scan(residuals, predictors, folios):
    print("\n── Test 1: UNIVARIATE_RESIDUAL_SCAN ──")

    n = len(residuals)
    n_predictors = len(predictors)
    print(f"  n={n}, candidate predictors={n_predictors}")

    # Spearman correlation of each predictor with residuals
    results_list = []
    for name, vals in sorted(predictors.items()):
        rho, p = spearman_r(vals.tolist(), residuals.tolist())
        results_list.append({'name': name, 'rho': rho, 'p': p})

    # Sort by |rho| descending
    results_list.sort(key=lambda x: abs(x['rho']), reverse=True)

    # Holm-Bonferroni correction
    p_values = sorted([(r['p'], r['name']) for r in results_list])
    holm_results = {}
    any_significant = False
    for rank_idx, (p_val, name) in enumerate(p_values):
        adjusted_alpha = 0.05 / (n_predictors - rank_idx)
        sig = p_val < adjusted_alpha
        holm_results[name] = {'p': p_val, 'holm_alpha': adjusted_alpha, 'significant': sig}
        if sig:
            any_significant = True

    # Print top 10
    print(f"\n  Top 10 by |rho|:")
    for r in results_list[:10]:
        holm = holm_results[r['name']]
        sig_marker = " ***HOLM-SIG***" if holm['significant'] else ""
        print(f"    {r['name']:30s} rho={r['rho']:+.4f}  p={r['p']:.4f}{sig_marker}")

    # Count uncorrected significant
    n_uncorrected_sig = sum(1 for r in results_list if r['p'] < 0.05)
    n_holm_sig = sum(1 for v in holm_results.values() if v['significant'])
    print(f"\n  Uncorrected significant (p<0.05): {n_uncorrected_sig}/{n_predictors}")
    print(f"  Holm-Bonferroni significant: {n_holm_sig}/{n_predictors}")

    verdict = 'SIGNAL_DETECTED' if any_significant else 'UNIVARIATE_CLOSED'
    print(f"  Verdict: {verdict}")

    return {
        'n_predictors': n_predictors,
        'n_folios': n,
        'top_10': [{k: round_floats(v) for k, v in r.items()} for r in results_list[:10]],
        'n_uncorrected_sig': n_uncorrected_sig,
        'n_holm_sig': n_holm_sig,
        'holm_significant': [r['name'] for r in results_list if holm_results[r['name']]['significant']],
        'verdict': verdict,
    }


# ── Test 2: NONLINEAR_RESIDUAL_DETECTION ─────────────────────────

def test2_nonlinear_rf(residuals, predictors):
    print("\n── Test 2: NONLINEAR_RESIDUAL_DETECTION ──")

    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import cross_val_score
    except ImportError:
        print("  sklearn not available — skipping RF test")
        return {
            'verdict': 'SKIPPED',
            'reason': 'sklearn not available',
        }

    # Build feature matrix
    pred_names = sorted(predictors.keys())
    X_rf = np.column_stack([predictors[name] for name in pred_names])
    n, p = X_rf.shape
    print(f"  Feature matrix: {n} x {p}")

    # Train RF on residuals
    rf = RandomForestRegressor(n_estimators=500, max_features='sqrt',
                               min_samples_leaf=5, random_state=42)

    # 5-fold CV
    cv_scores = cross_val_score(rf, X_rf, residuals, cv=5, scoring='r2')
    cv_r2 = cv_scores.mean()
    cv_std = cv_scores.std()
    print(f"  RF 5-fold CV R²: {cv_r2:.4f} ± {cv_std:.4f}")
    print(f"  Per-fold: {[f'{s:.4f}' for s in cv_scores]}")

    # Permutation test
    n_perm = 200
    perm_scores = []
    print(f"  Running {n_perm} permutations...")
    for i in range(n_perm):
        y_perm = np.random.permutation(residuals)
        rf_perm = RandomForestRegressor(n_estimators=100, max_features='sqrt',
                                        min_samples_leaf=5, random_state=i)
        perm_cv = cross_val_score(rf_perm, X_rf, y_perm, cv=5, scoring='r2')
        perm_scores.append(perm_cv.mean())

    perm_scores = np.array(perm_scores)
    perm_mean = perm_scores.mean()
    perm_std = perm_scores.std()
    perm_p = float((perm_scores >= cv_r2).sum() / n_perm)
    print(f"  Permutation null: mean={perm_mean:.4f}, std={perm_std:.4f}")
    print(f"  Permutation p-value: {perm_p:.4f}")

    # Feature importances (fit on full data)
    rf.fit(X_rf, residuals)
    importances = rf.feature_importances_
    imp_ranked = sorted(zip(pred_names, importances), key=lambda x: x[1], reverse=True)
    print(f"  Top 5 features by importance:")
    for name, imp in imp_ranked[:5]:
        print(f"    {name:30s} importance={imp:.4f}")

    if cv_r2 > 0 and perm_p < 0.05:
        verdict = 'NONLINEAR_SIGNAL'
    else:
        verdict = 'NONLINEAR_CLOSED'
    print(f"  Verdict: {verdict}")

    return {
        'n_features': p,
        'cv_r2': float(cv_r2),
        'cv_std': float(cv_std),
        'cv_per_fold': cv_scores.tolist(),
        'permutation_n': n_perm,
        'permutation_null_mean': float(perm_mean),
        'permutation_null_std': float(perm_std),
        'permutation_p': perm_p,
        'top_5_importances': [{'name': n, 'importance': float(i)} for n, i in imp_ranked[:5]],
        'verdict': verdict,
    }


# ── Test 3: SPATIAL_AUTOCORRELATION ──────────────────────────────

def test3_spatial_autocorrelation(residuals, folios):
    print("\n── Test 3: SPATIAL_AUTOCORRELATION ──")

    n = len(folios)

    # Sort folios by manuscript order
    order = sorted(range(n), key=lambda i: folio_sort_key(folios[i]))
    ordered_resid = residuals[order]
    ordered_folios = [folios[i] for i in order]

    print(f"  Folio order: {ordered_folios[0]} ... {ordered_folios[-1]}")

    # Lag-1 autocorrelation
    def lag_autocorr(x, lag):
        n_x = len(x)
        if n_x <= lag:
            return 0.0
        mean_x = x.mean()
        var_x = x.var()
        if var_x == 0:
            return 0.0
        cov = np.mean((x[:-lag] - mean_x) * (x[lag:] - mean_x))
        return float(cov / var_x)

    ac_lag1 = lag_autocorr(ordered_resid, 1)
    ac_lag2 = lag_autocorr(ordered_resid, 2)
    print(f"  Lag-1 autocorrelation: {ac_lag1:.4f}")
    print(f"  Lag-2 autocorrelation: {ac_lag2:.4f}")

    # Permutation test for lag-1
    n_perm = 1000
    perm_ac = np.zeros(n_perm)
    for i in range(n_perm):
        perm_resid = np.random.permutation(ordered_resid)
        perm_ac[i] = lag_autocorr(perm_resid, 1)

    # Two-sided p-value
    perm_p = float(np.sum(np.abs(perm_ac) >= abs(ac_lag1)) / n_perm)
    print(f"  Permutation p-value (two-sided): {perm_p:.4f}")
    print(f"  Permutation null: mean={perm_ac.mean():.4f}, std={perm_ac.std():.4f}")

    # Runs test (above/below median)
    median_r = np.median(ordered_resid)
    above = ordered_resid >= median_r
    runs = 1
    for i in range(1, n):
        if above[i] != above[i - 1]:
            runs += 1
    n_above = above.sum()
    n_below = n - n_above
    # Expected runs under null
    if n_above > 0 and n_below > 0:
        expected_runs = 1 + 2 * n_above * n_below / n
        var_runs = (2 * n_above * n_below * (2 * n_above * n_below - n)) / (n**2 * (n - 1))
        if var_runs > 0:
            z_runs = (runs - expected_runs) / math.sqrt(var_runs)
            p_runs = 2 * (1 - scipy_stats.norm.cdf(abs(z_runs)))
        else:
            z_runs = 0.0
            p_runs = 1.0
    else:
        expected_runs = 1.0
        z_runs = 0.0
        p_runs = 1.0
    print(f"  Runs test: runs={runs}, expected={expected_runs:.1f}, z={z_runs:.4f}, p={p_runs:.4f}")

    if perm_p < 0.05:
        verdict = 'SPATIAL_STRUCTURE'
    else:
        verdict = 'SPATIALLY_RANDOM'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'lag1_autocorrelation': ac_lag1,
        'lag2_autocorrelation': ac_lag2,
        'permutation_n': n_perm,
        'permutation_p': perm_p,
        'permutation_null_mean': float(perm_ac.mean()),
        'permutation_null_std': float(perm_ac.std()),
        'runs_test': {
            'runs': runs,
            'expected': float(expected_runs),
            'z': float(z_runs),
            'p': float(p_runs),
        },
        'verdict': verdict,
    }


# ── Test 4: DESIGN_FREEDOM_PROFILE ──────────────────────────────

def test4_design_freedom_profile(residuals, y_pred, folios, folio_data, predictors):
    print("\n── Test 4: DESIGN_FREEDOM_PROFILE ──")

    n = len(residuals)

    # 4a: Residual diagnostics
    print("\n  4a: Residual diagnostics")

    # Shapiro-Wilk normality
    sw_stat, sw_p = scipy_stats.shapiro(residuals)
    print(f"    Shapiro-Wilk: W={sw_stat:.4f}, p={sw_p:.4f}")

    # Residual vs fitted (heteroscedasticity)
    rho_rf, p_rf = spearman_r(y_pred.tolist(), np.abs(residuals).tolist())
    print(f"    |Residual| vs fitted: rho={rho_rf:.4f}, p={p_rf:.4f}")

    # Per-section residual variance
    sections = [folio_data[f]['section'] for f in folios]
    unique_sections = sorted(set(sections))
    section_vars = {}
    for sec in unique_sections:
        sec_resid = [residuals[i] for i in range(n) if sections[i] == sec]
        section_vars[sec] = float(np.var(sec_resid))
        print(f"    Section {sec}: n={len(sec_resid)}, var={section_vars[sec]:.6f}")

    # Residual mean (should be ~0)
    resid_mean = float(residuals.mean())
    resid_std = float(residuals.std())
    print(f"    Residual mean={resid_mean:.6f}, std={resid_std:.4f}")

    # 4b: C458 asymmetry test
    print("\n  4b: C458 asymmetry test")
    # Clamped dimensions (already in model -> residual should NOT correlate)
    # Free dimensions (not in model -> residual MIGHT correlate)

    # Recovery-free dimensions to test:
    c458_free = {}
    c458_clamped = {}
    for key in ['link_density', 'gatekeeper_exit_frac', 'hazard_exit_frac']:
        if key in predictors:
            c458_free[key] = predictors[key]
    # Clamped proxies not in model (gatekeeper_fraction, k_frac)
    for key in ['gatekeeper_fraction', 'k_frac']:
        if key in predictors:
            c458_clamped[key] = predictors[key]

    free_results = {}
    for name, vals in c458_free.items():
        rho, p = spearman_r(vals.tolist(), residuals.tolist())
        free_results[name] = {'rho': rho, 'p': p}
        print(f"    FREE {name:30s} rho={rho:+.4f}  p={p:.4f}")

    clamped_results = {}
    for name, vals in c458_clamped.items():
        rho, p = spearman_r(vals.tolist(), residuals.tolist())
        clamped_results[name] = {'rho': rho, 'p': p}
        print(f"    CLAMPED {name:30s} rho={rho:+.4f}  p={p:.4f}")

    # Asymmetry detection: any free dimension significant AND no clamped dimension significant?
    any_free_sig = any(r['p'] < 0.05 for r in free_results.values())
    any_clamped_sig = any(r['p'] < 0.05 for r in clamped_results.values())

    # 4c: Regime residual homogeneity
    print("\n  4c: Regime residual homogeneity")
    regimes = [folio_data[f]['regime'] for f in folios]
    unique_regimes = sorted(set(regimes))
    regime_groups = []
    for reg in unique_regimes:
        group = [residuals[i] for i in range(n) if regimes[i] == reg]
        regime_groups.append(group)
        print(f"    {reg}: n={len(group)}, mean={np.mean(group):.4f}, std={np.std(group):.4f}")

    kw_stat, kw_p = scipy_stats.kruskal(*regime_groups)
    print(f"    Kruskal-Wallis: H={kw_stat:.4f}, p={kw_p:.4f}")

    # Verdict
    if kw_p < 0.05:
        verdict_4 = 'REGIME_RESIDUAL_STRUCTURE'
    elif any_free_sig and not any_clamped_sig:
        verdict_4 = 'ASYMMETRIC_FREEDOM'
    elif sw_p > 0.05 and not any_free_sig and not any_clamped_sig:
        verdict_4 = 'NORMAL_RESIDUAL'
    else:
        verdict_4 = 'SYMMETRIC_FREEDOM'
    print(f"  Verdict: {verdict_4}")

    return {
        'diagnostics': {
            'shapiro_wilk': {'W': float(sw_stat), 'p': float(sw_p)},
            'abs_resid_vs_fitted': {'rho': rho_rf, 'p': p_rf},
            'residual_mean': resid_mean,
            'residual_std': resid_std,
            'section_variances': section_vars,
        },
        'c458_asymmetry': {
            'free_dimensions': free_results,
            'clamped_dimensions': clamped_results,
            'any_free_significant': any_free_sig,
            'any_clamped_significant': any_clamped_sig,
        },
        'regime_homogeneity': {
            'kruskal_wallis_H': float(kw_stat),
            'kruskal_wallis_p': float(kw_p),
        },
        'verdict': verdict_4,
    }


# ── Test 5: EXHAUSTIVE_OLS_EXTENSION (GATED) ─────────────────────

def test5_exhaustive_extension(residuals, predictors, X_best, axm, t1_result, t2_result):
    print("\n── Test 5: EXHAUSTIVE_OLS_EXTENSION ──")

    # Gate check
    t1_signal = t1_result['verdict'] == 'SIGNAL_DETECTED'
    t2_signal = t2_result.get('verdict') == 'NONLINEAR_SIGNAL'

    if not t1_signal and not t2_signal:
        print("  Gate: T1=CLOSED, T2=CLOSED → skipping extension test")
        print("  Verdict: RESIDUAL_CLOSED")
        return {
            'gated': True,
            'gate_reason': 'T1 UNIVARIATE_CLOSED and T2 NONLINEAR_CLOSED',
            'verdict': 'RESIDUAL_CLOSED',
        }

    print(f"  Gate: T1={'SIGNAL' if t1_signal else 'CLOSED'}, T2={'SIGNAL' if t2_signal else 'CLOSED'} → running extension")

    n = len(axm)

    # Get top candidates from T1 (by |rho|)
    top_candidates = []
    if t1_signal:
        for item in t1_result['top_10'][:5]:
            name = item['name']
            if name in predictors:
                top_candidates.append(name)
    # Also add top RF importance features if available
    if t2_signal and 'top_5_importances' in t2_result:
        for item in t2_result['top_5_importances'][:3]:
            name = item['name']
            if name in predictors and name not in top_candidates:
                top_candidates.append(name)

    top_candidates = top_candidates[:5]  # cap at 5
    print(f"  Testing candidates: {top_candidates}")

    # Current best model stats
    _, _, ss_best, r2_best = ols_fit(X_best, axm)
    loo_best = loo_cv_r2(X_best, axm)
    k_best = X_best.shape[1]

    per_feature = {}
    for name in top_candidates:
        feat_z = standardize(predictors[name]).reshape(-1, 1)
        X_ext = np.hstack([X_best, feat_z])
        _, _, ss_ext, r2_ext = ols_fit(X_ext, axm)
        loo_ext = loo_cv_r2(X_ext, axm)
        dr2 = r2_ext - r2_best
        f_stat, f_p = f_test_increment(ss_best, ss_ext, 1, n, X_ext.shape[1])
        per_feature[name] = {
            'dr2': float(dr2),
            'f_stat': float(f_stat),
            'f_p': float(f_p),
            'loo': float(loo_ext),
            'loo_gain': float(loo_ext - loo_best),
        }
        print(f"    +{name:30s} dR²={dr2:.4f}, F={f_stat:.2f}, p={f_p:.4f}, LOO={loo_ext:.4f} ({loo_ext-loo_best:+.4f})")

    # Joint model with all candidates
    feat_cols = [standardize(predictors[name]).reshape(-1, 1) for name in top_candidates]
    X_joint = np.hstack([X_best] + feat_cols)
    _, _, ss_joint, r2_joint = ols_fit(X_joint, axm)
    loo_joint = loo_cv_r2(X_joint, axm)
    dr2_joint = r2_joint - r2_best
    f_joint, fp_joint = f_test_increment(ss_best, ss_joint, len(top_candidates), n, X_joint.shape[1])
    print(f"\n    Joint ({len(top_candidates)} features): dR²={dr2_joint:.4f}, F={f_joint:.2f}, p={fp_joint:.4f}, LOO={loo_joint:.4f} ({loo_joint-loo_best:+.4f})")

    # Best single feature
    if per_feature:
        best_name = max(per_feature, key=lambda k: per_feature[k]['dr2'])
        best = per_feature[best_name]
        if best['dr2'] >= 0.02 and best['f_p'] < 0.05 and best['loo_gain'] > 0:
            verdict = 'RESIDUAL_EXTENDS'
        elif best['dr2'] >= 0.01 or best['f_p'] < 0.10:
            verdict = 'RESIDUAL_MARGINAL'
        else:
            verdict = 'RESIDUAL_CLOSED'
    else:
        verdict = 'RESIDUAL_CLOSED'
    print(f"  Verdict: {verdict}")

    return {
        'gated': False,
        'current_best': {'r2': float(r2_best), 'loo': float(loo_best)},
        'candidates_tested': top_candidates,
        'per_feature': per_feature,
        'joint_model': {
            'n_features': len(top_candidates),
            'dr2': float(dr2_joint),
            'f_stat': float(f_joint),
            'f_p': float(fp_joint),
            'loo': float(loo_joint),
            'loo_gain': float(loo_joint - loo_best),
        },
        'verdict': verdict,
    }


# ── Synthesis ────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5):
    t1v = t1['verdict']
    t2v = t2['verdict']
    t3v = t3['verdict']

    if t1v == 'UNIVARIATE_CLOSED' and t2v in ('NONLINEAR_CLOSED', 'SKIPPED'):
        if t3v == 'SPATIAL_STRUCTURE':
            overall = 'RESIDUAL_SPATIALLY_STRUCTURED'
        else:
            overall = 'RESIDUAL_GENUINELY_FREE'
    elif t1v == 'SIGNAL_DETECTED' and t2v in ('NONLINEAR_CLOSED', 'SKIPPED'):
        overall = 'RESIDUAL_LINEAR_STRUCTURE'
    elif t1v == 'UNIVARIATE_CLOSED' and t2v == 'NONLINEAR_SIGNAL':
        overall = 'RESIDUAL_NONLINEAR_STRUCTURE'
    elif t1v == 'SIGNAL_DETECTED' and t2v == 'NONLINEAR_SIGNAL':
        overall = 'RESIDUAL_RICHLY_STRUCTURED'
    else:
        overall = 'UNCLASSIFIED'

    return overall


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 417: RESIDUAL_FREEDOM_CHARACTERIZATION")
    print("=" * 60)

    folio_line_lists, folio_data, valid_folios, class_to_role, new_metrics = load_data()

    # Compute divergence and boundary properties (replicate Phase 416)
    div_data = compute_folio_divergence(folio_line_lists, folio_data, valid_folios)
    print(f"\n  Folios with divergence: {len(div_data)}")

    boundary_data = compute_boundary_properties(folio_line_lists, valid_folios)
    print(f"  Folios with boundary properties: {len(boundary_data)}")

    common = sorted(f for f in div_data if f in boundary_data and f in folio_data and f in new_metrics)
    print(f"  Common folios: {len(common)}")

    # Build current best model and extract residuals
    print("\n  Building Phase 416 dual boundary model...")
    X_best, axm, residuals, y_pred, r2_best, loo_best = build_current_best_model(
        common, folio_data, div_data, boundary_data)
    print(f"  Best model: R²={r2_best:.4f}, LOO={loo_best:.4f}")
    print(f"  Residual mean={residuals.mean():.6f}, std={residuals.std():.4f}")

    # Assemble candidate predictors
    predictors = assemble_candidates(common, folio_data, boundary_data, new_metrics)
    print(f"\n  Candidate predictors assembled: {len(predictors)}")
    for name in sorted(predictors.keys()):
        print(f"    {name}: n={len(predictors[name])}, mean={predictors[name].mean():.4f}, std={predictors[name].std():.4f}")

    # Run 5-test battery
    t1 = test1_univariate_residual_scan(residuals, predictors, common)
    t2 = test2_nonlinear_rf(residuals, predictors)
    t3 = test3_spatial_autocorrelation(residuals, common)
    t4 = test4_design_freedom_profile(residuals, y_pred, common, folio_data, predictors)
    t5 = test5_exhaustive_extension(residuals, predictors, X_best, axm, t1, t2)

    # Synthesis
    overall = synthesize(t1, t2, t3, t4, t5)

    print(f"\n── SYNTHESIS ──")
    print(f"  T1={t1['verdict']}")
    print(f"  T2={t2['verdict']}")
    print(f"  T3={t3['verdict']}")
    print(f"  T4={t4['verdict']}")
    print(f"  T5={t5['verdict']}")
    print(f"  Overall: {overall}")

    output = {
        'phase': 'RESIDUAL_FREEDOM_CHARACTERIZATION',
        'phase_number': 417,
        'depends_on': ['C1035', 'C1168', 'C458', 'C980', 'C976'],
        'n_folios': len(common),
        'current_best_model': {
            'r2': float(r2_best),
            'loo': float(loo_best),
            'description': 'C1035 baseline + entry_div + AXM_return + jsd_exit + AXM_departure',
        },
        'n_candidate_predictors': len(predictors),
        'candidate_predictor_names': sorted(predictors.keys()),
        'test1_univariate_residual_scan': t1,
        'test2_nonlinear_rf': t2,
        'test3_spatial_autocorrelation': t3,
        'test4_design_freedom_profile': t4,
        'test5_exhaustive_extension': t5,
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
    out_path = RESULTS_DIR / 'residual_freedom_characterization.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
