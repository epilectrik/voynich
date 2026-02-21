#!/usr/bin/env python3
"""
Phase 416: EXIT_DIVERGENCE_SYMMETRY
=====================================
Tests whether exit divergence carries independent signal beyond the entry bundle
(entry_div + AXM_return_rate) established in Phases 413-415.

5-test battery:
  T1: EXIT_DIVERGENCE_BASELINE (collinearity with entry, partial correlations)
  T2: CLOSER_ROUTING_PROFILE (closer token properties, AXM departure rate)
  T3: GATEKEEPER_EXIT_MECHANISM (gatekeeper/hazard density at exit)
  T4: EXIT_INCREMENTAL_SIGNAL (add exit features to entry bundle)
  T5: DUAL_BOUNDARY_ARCHITECTURE (full model, per-section analysis)

Depends on: C1035, C1156-C1165, C1007-C1009, C976
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
ROLES = ['AUXILIARY', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL']


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
    if Z.ndim == 1:
        Z = Z.reshape(-1, 1)
    X_z = np.column_stack([np.ones(n), Z])
    beta_x = np.linalg.lstsq(X_z, x, rcond=None)[0]
    res_x = x - X_z @ beta_x
    beta_y = np.linalg.lstsq(X_z, y, rcond=None)[0]
    res_y = y - X_z @ beta_y
    return spearman_r(res_x.tolist(), res_y.tolist())


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

    folio_lines = defaultdict(lambda: defaultdict(list))
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

        folio_lines[t.folio][t.line].append({
            'word': w,
            'cls': cls,
            'state': CLASS_TO_STATE[cls],
            'role': class_to_role.get(str(cls), 'UNKNOWN'),
            'prefix': prefix,
            'is_gatekeeper': cls in GATEKEEPER_CLASSES,
        })

    folio_line_lists = defaultdict(list)
    for folio in sorted(folio_lines.keys()):
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    print(f"  Folios with lines: {len(folio_line_lists)}")
    print(f"  AXM data: {len(valid_folios)} folios")

    return folio_line_lists, folio_data, valid_folios, class_to_role


# ── Per-Folio Entry+Exit Divergence ──────────────────────────────

def compute_folio_divergence(folio_line_lists, folio_data, valid_folios):
    """Compute per-folio entry AND exit divergence vs interior."""
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

        results[folio] = {
            'jsd_entry': jsd_entry,
            'jsd_exit': jsd_exit,
            'zone_counts': {z: len(zone_trans[z]) for z in zone_trans},
        }

    return results


# ── Per-Folio Opener + Closer Properties ─────────────────────────

def compute_boundary_properties(folio_line_lists, valid_folios):
    """Extract per-folio opener AND closer properties."""
    results = {}

    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]

        opener_states = []
        closer_roles = []
        closer_prefixes = []
        closer_states = []
        entry_transitions = []
        exit_transitions = []
        exit_gatekeeper_count = 0
        exit_hazard_target_count = 0
        exit_total = 0

        for tokens in lines:
            if len(tokens) < 4:
                continue
            opener = tokens[0]
            closer = tokens[-1]
            follower = tokens[1]
            penultimate = tokens[-2]

            # Entry properties (replicate Phase 415)
            opener_states.append(opener['state'])
            entry_transitions.append((opener['state'], follower['state']))

            # Exit properties (new)
            closer_roles.append(closer['role'])
            closer_prefixes.append(closer['prefix'] if closer['prefix'] else 'BARE')
            closer_states.append(closer['state'])
            exit_transitions.append((penultimate['state'], closer['state']))

            # Gatekeeper at exit zone
            if penultimate['is_gatekeeper'] or closer['is_gatekeeper']:
                exit_gatekeeper_count += 1
            exit_total += 1

            # Hazard-target transitions at exit (transition TO FL_HAZ)
            if closer['state'] == 'FL_HAZ':
                exit_hazard_target_count += 1

        n_lines = len(closer_roles)
        if n_lines < MIN_CLOSERS:
            continue

        # Entry: AXM return rate (replicate Phase 415)
        axm_returns = sum(1 for _, tgt in entry_transitions if tgt == 'AXM')
        axm_return_rate = axm_returns / len(entry_transitions)

        # Exit: AXM departure rate (fraction of exit transitions FROM AXM to non-AXM)
        axm_exits = sum(1 for src, tgt in exit_transitions if src == 'AXM' and tgt != 'AXM')
        axm_sources = sum(1 for src, _ in exit_transitions if src == 'AXM')
        axm_departure_rate = axm_exits / max(axm_sources, 1)

        # Exit: routing entropy (diversity of exit targets)
        exit_tgt_counts = Counter(tgt for _, tgt in exit_transitions)
        exit_tgt_probs = [c / n_lines for c in exit_tgt_counts.values()]
        exit_routing_entropy = shannon_entropy(exit_tgt_probs)

        # Closer role distribution
        closer_role_counts = Counter(closer_roles)
        closer_role_fracs = {r: closer_role_counts.get(r, 0) / n_lines for r in ROLES}

        # Gatekeeper exit fraction
        gatekeeper_exit_frac = exit_gatekeeper_count / max(exit_total, 1)

        # Hazard-target exit fraction
        hazard_exit_frac = exit_hazard_target_count / max(exit_total, 1)

        results[folio] = {
            'n_lines': n_lines,
            'axm_return_rate': axm_return_rate,
            'axm_departure_rate': axm_departure_rate,
            'exit_routing_entropy': exit_routing_entropy,
            'closer_role_fracs': closer_role_fracs,
            'gatekeeper_exit_frac': gatekeeper_exit_frac,
            'hazard_exit_frac': hazard_exit_frac,
        }

    return results


# ── Build Baseline ───────────────────────────────────────────────

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


# ── Test 1: EXIT_DIVERGENCE_BASELINE ─────────────────────────────

def test1_exit_divergence_baseline(div_data, boundary_data, folio_data):
    print("\n── Test 1: EXIT_DIVERGENCE_BASELINE ──")

    folios = sorted(f for f in div_data if f in boundary_data and f in folio_data)
    n = len(folios)
    print(f"  Folios: {n}")

    jsd_entry = np.array([div_data[f]['jsd_entry'] for f in folios])
    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])
    axm_return = np.array([boundary_data[f]['axm_return_rate'] for f in folios])

    print(f"  jsd_entry: mean={jsd_entry.mean():.4f}, std={jsd_entry.std():.4f}")
    print(f"  jsd_exit:  mean={jsd_exit.mean():.4f}, std={jsd_exit.std():.4f}")

    # Bivariate correlations
    rho_ee, p_ee = spearman_r(jsd_entry.tolist(), jsd_exit.tolist())
    rho_exit_axm, p_exit_axm = spearman_r(jsd_exit.tolist(), axm.tolist())
    rho_entry_axm, p_entry_axm = spearman_r(jsd_entry.tolist(), axm.tolist())
    print(f"  jsd_entry vs jsd_exit: rho={rho_ee:.4f}, p={p_ee:.4f}")
    print(f"  jsd_exit vs AXM:       rho={rho_exit_axm:.4f}, p={p_exit_axm:.4f}")
    print(f"  jsd_entry vs AXM:      rho={rho_entry_axm:.4f}, p={p_entry_axm:.4f}")

    # Partial: exit vs AXM controlling for entry
    rho_partial_entry, p_partial_entry = partial_corr_spearman(jsd_exit, axm, jsd_entry)
    print(f"  Partial (exit vs AXM | entry): rho={rho_partial_entry:.4f}, p={p_partial_entry:.4f}")

    # Partial: exit vs AXM controlling for entry_div + AXM_return (full entry bundle)
    Z_entry_bundle = np.column_stack([jsd_entry, axm_return])
    rho_partial_bundle, p_partial_bundle = partial_corr_spearman(jsd_exit, axm, Z_entry_bundle)
    print(f"  Partial (exit vs AXM | entry + AXM_return): rho={rho_partial_bundle:.4f}, p={p_partial_bundle:.4f}")

    # Verdict
    if abs(rho_partial_bundle) >= 0.25 and p_partial_bundle < 0.05:
        verdict = 'EXIT_INDEPENDENT'
    elif p_partial_bundle < 0.10:
        verdict = 'EXIT_MARGINAL'
    else:
        verdict = 'EXIT_REDUNDANT'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'jsd_entry_stats': {'mean': float(jsd_entry.mean()), 'std': float(jsd_entry.std())},
        'jsd_exit_stats': {'mean': float(jsd_exit.mean()), 'std': float(jsd_exit.std())},
        'bivariate': {
            'entry_vs_exit': {'rho': rho_ee, 'p': p_ee},
            'exit_vs_axm': {'rho': rho_exit_axm, 'p': p_exit_axm},
            'entry_vs_axm': {'rho': rho_entry_axm, 'p': p_entry_axm},
        },
        'partial_exit_vs_axm_ctrl_entry': {'rho': rho_partial_entry, 'p': p_partial_entry},
        'partial_exit_vs_axm_ctrl_entry_bundle': {'rho': rho_partial_bundle, 'p': p_partial_bundle},
        'verdict': verdict,
    }


# ── Test 2: CLOSER_ROUTING_PROFILE ──────────────────────────────

def test2_closer_routing_profile(div_data, boundary_data, folio_data):
    print("\n── Test 2: CLOSER_ROUTING_PROFILE ──")

    folios = sorted(f for f in div_data if f in boundary_data and f in folio_data)
    n = len(folios)

    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    axm_departure = np.array([boundary_data[f]['axm_departure_rate'] for f in folios])
    exit_routing_ent = np.array([boundary_data[f]['exit_routing_entropy'] for f in folios])

    print(f"  AXM departure rate: mean={axm_departure.mean():.4f}, std={axm_departure.std():.4f}")
    print(f"  Exit routing entropy: mean={exit_routing_ent.mean():.4f}, std={exit_routing_ent.std():.4f}")

    # Closer role fractions
    for role in ROLES:
        arr = np.array([boundary_data[f]['closer_role_fracs'][role] for f in folios])
        rho_e, p_e = spearman_r(arr.tolist(), jsd_exit.tolist())
        rho_a, p_a = spearman_r(arr.tolist(), axm.tolist())
        print(f"  Closer {role}: mean={arr.mean():.3f}, vs exit_div rho={rho_e:.4f}, vs AXM rho={rho_a:.4f}")

    # Key feature correlations
    rho_dep_exit, p_dep_exit = spearman_r(axm_departure.tolist(), jsd_exit.tolist())
    rho_dep_axm, p_dep_axm = spearman_r(axm_departure.tolist(), axm.tolist())
    rho_ent_exit, p_ent_exit = spearman_r(exit_routing_ent.tolist(), jsd_exit.tolist())
    print(f"  AXM departure vs exit_div: rho={rho_dep_exit:.4f}, p={p_dep_exit:.4f}")
    print(f"  AXM departure vs AXM_self: rho={rho_dep_axm:.4f}, p={p_dep_axm:.4f}")
    print(f"  Exit routing entropy vs exit_div: rho={rho_ent_exit:.4f}, p={p_ent_exit:.4f}")

    # OLS: exit_div ~ closer features
    intercept = np.ones((n, 1))
    dep_z = standardize(axm_departure).reshape(-1, 1)
    ent_z = standardize(exit_routing_ent).reshape(-1, 1)
    X_closer = np.hstack([intercept, dep_z, ent_z])
    _, _, _, r2_closer = ols_fit(X_closer, jsd_exit)
    print(f"  R² (exit_div ~ closer features): {r2_closer:.4f}")

    if r2_closer >= 0.30:
        verdict = 'CLOSER_STRUCTURED'
    elif r2_closer >= 0.10:
        verdict = 'CLOSER_WEAK'
    else:
        verdict = 'CLOSER_UNIFORM'
    print(f"  Verdict: {verdict}")

    return {
        'axm_departure_stats': {'mean': float(axm_departure.mean()), 'std': float(axm_departure.std())},
        'exit_routing_entropy_stats': {'mean': float(exit_routing_ent.mean()), 'std': float(exit_routing_ent.std())},
        'axm_departure_vs_exit_div': {'rho': rho_dep_exit, 'p': p_dep_exit},
        'axm_departure_vs_axm_self': {'rho': rho_dep_axm, 'p': p_dep_axm},
        'exit_routing_entropy_vs_exit_div': {'rho': rho_ent_exit, 'p': p_ent_exit},
        'r2_exit_div_from_closer': r2_closer,
        'verdict': verdict,
    }


# ── Test 3: GATEKEEPER_EXIT_MECHANISM ────────────────────────────

def test3_gatekeeper_exit_mechanism(div_data, boundary_data, folio_data):
    print("\n── Test 3: GATEKEEPER_EXIT_MECHANISM ──")

    folios = sorted(f for f in div_data if f in boundary_data and f in folio_data)
    n = len(folios)

    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    gk_exit = np.array([boundary_data[f]['gatekeeper_exit_frac'] for f in folios])
    haz_exit = np.array([boundary_data[f]['hazard_exit_frac'] for f in folios])

    print(f"  Gatekeeper exit frac: mean={gk_exit.mean():.4f}, std={gk_exit.std():.4f}")
    print(f"  Hazard exit frac: mean={haz_exit.mean():.4f}, std={haz_exit.std():.4f}")

    rho_gk_exit, p_gk_exit = spearman_r(gk_exit.tolist(), jsd_exit.tolist())
    rho_gk_axm, p_gk_axm = spearman_r(gk_exit.tolist(), axm.tolist())
    rho_haz_exit, p_haz_exit = spearman_r(haz_exit.tolist(), jsd_exit.tolist())
    rho_haz_axm, p_haz_axm = spearman_r(haz_exit.tolist(), axm.tolist())

    print(f"  GK exit frac vs exit_div: rho={rho_gk_exit:.4f}, p={p_gk_exit:.4f}")
    print(f"  GK exit frac vs AXM_self: rho={rho_gk_axm:.4f}, p={p_gk_axm:.4f}")
    print(f"  Hazard exit frac vs exit_div: rho={rho_haz_exit:.4f}, p={p_haz_exit:.4f}")
    print(f"  Hazard exit frac vs AXM_self: rho={rho_haz_axm:.4f}, p={p_haz_axm:.4f}")

    # OLS
    intercept = np.ones((n, 1))
    gk_z = standardize(gk_exit).reshape(-1, 1)
    haz_z = standardize(haz_exit).reshape(-1, 1)
    X_gk = np.hstack([intercept, gk_z, haz_z])
    _, _, _, r2_gk = ols_fit(X_gk, jsd_exit)
    print(f"  R² (exit_div ~ GK + hazard): {r2_gk:.4f}")

    if r2_gk >= 0.25 and (abs(rho_gk_exit) >= 0.40 or abs(rho_haz_exit) >= 0.40):
        verdict = 'GATEKEEPER_EXPLAINS_EXIT'
    elif r2_gk >= 0.10:
        verdict = 'GATEKEEPER_PARTIAL'
    else:
        verdict = 'GATEKEEPER_INDEPENDENT'
    print(f"  Verdict: {verdict}")

    return {
        'gatekeeper_exit_stats': {'mean': float(gk_exit.mean()), 'std': float(gk_exit.std())},
        'hazard_exit_stats': {'mean': float(haz_exit.mean()), 'std': float(haz_exit.std())},
        'gk_exit_vs_exit_div': {'rho': rho_gk_exit, 'p': p_gk_exit},
        'gk_exit_vs_axm': {'rho': rho_gk_axm, 'p': p_gk_axm},
        'hazard_exit_vs_exit_div': {'rho': rho_haz_exit, 'p': p_haz_exit},
        'hazard_exit_vs_axm': {'rho': rho_haz_axm, 'p': p_haz_axm},
        'r2_exit_div_from_gk_haz': r2_gk,
        'verdict': verdict,
    }


# ── Test 4: EXIT_INCREMENTAL_SIGNAL ─────────────────────────────

def test4_exit_incremental_signal(div_data, boundary_data, folio_data):
    print("\n── Test 4: EXIT_INCREMENTAL_SIGNAL ──")

    folios = sorted(f for f in div_data if f in boundary_data and f in folio_data)
    n = len(folios)

    jsd_entry = np.array([div_data[f]['jsd_entry'] for f in folios])
    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])
    axm_return = np.array([boundary_data[f]['axm_return_rate'] for f in folios])
    axm_departure = np.array([boundary_data[f]['axm_departure_rate'] for f in folios])
    gk_exit = np.array([boundary_data[f]['gatekeeper_exit_frac'] for f in folios])

    # Build current best model: baseline + entry_div + AXM_return
    X_base, _ = build_baseline(folios, folio_data)
    je_z = standardize(jsd_entry).reshape(-1, 1)
    arr_z = standardize(axm_return).reshape(-1, 1)
    X_entry_bundle = np.hstack([X_base, je_z, arr_z])
    _, _, ss_entry_bundle, r2_entry_bundle = ols_fit(X_entry_bundle, axm)
    loo_entry_bundle = loo_cv_r2(X_entry_bundle, axm)

    print(f"  Entry bundle (baseline + entry_div + AXM_return):")
    print(f"    R²={r2_entry_bundle:.4f}, LOO={loo_entry_bundle:.4f}")

    # Add jsd_exit
    jx_z = standardize(jsd_exit).reshape(-1, 1)
    X_plus_exit = np.hstack([X_entry_bundle, jx_z])
    _, _, ss_plus_exit, r2_plus_exit = ols_fit(X_plus_exit, axm)
    loo_plus_exit = loo_cv_r2(X_plus_exit, axm)
    dr2_exit = r2_plus_exit - r2_entry_bundle
    f_exit, fp_exit = f_test_increment(ss_entry_bundle, ss_plus_exit, 1, n, X_plus_exit.shape[1])
    print(f"  +jsd_exit: dR²={dr2_exit:.4f}, F={f_exit:.2f}, p={fp_exit:.4f}, LOO={loo_plus_exit:.4f}")

    # Add AXM departure rate
    dep_z = standardize(axm_departure).reshape(-1, 1)
    X_plus_dep = np.hstack([X_entry_bundle, dep_z])
    _, _, ss_plus_dep, r2_plus_dep = ols_fit(X_plus_dep, axm)
    loo_plus_dep = loo_cv_r2(X_plus_dep, axm)
    dr2_dep = r2_plus_dep - r2_entry_bundle
    f_dep, fp_dep = f_test_increment(ss_entry_bundle, ss_plus_dep, 1, n, X_plus_dep.shape[1])
    print(f"  +AXM_departure: dR²={dr2_dep:.4f}, F={f_dep:.2f}, p={fp_dep:.4f}, LOO={loo_plus_dep:.4f}")

    # Add gatekeeper exit fraction
    gk_z = standardize(gk_exit).reshape(-1, 1)
    X_plus_gk = np.hstack([X_entry_bundle, gk_z])
    _, _, ss_plus_gk, r2_plus_gk = ols_fit(X_plus_gk, axm)
    loo_plus_gk = loo_cv_r2(X_plus_gk, axm)
    dr2_gk = r2_plus_gk - r2_entry_bundle
    f_gk, fp_gk = f_test_increment(ss_entry_bundle, ss_plus_gk, 1, n, X_plus_gk.shape[1])
    print(f"  +GK_exit_frac: dR²={dr2_gk:.4f}, F={f_gk:.2f}, p={fp_gk:.4f}, LOO={loo_plus_gk:.4f}")

    # All exit features jointly
    X_plus_all = np.hstack([X_entry_bundle, jx_z, dep_z, gk_z])
    _, _, ss_plus_all, r2_plus_all = ols_fit(X_plus_all, axm)
    loo_plus_all = loo_cv_r2(X_plus_all, axm)
    dr2_all = r2_plus_all - r2_entry_bundle
    f_all, fp_all = f_test_increment(ss_entry_bundle, ss_plus_all, 3, n, X_plus_all.shape[1])
    print(f"  +all exit features: dR²={dr2_all:.4f}, F={f_all:.2f}, p={fp_all:.4f}, LOO={loo_plus_all:.4f}")

    # Find best single exit feature
    features = {
        'jsd_exit': {'dr2': dr2_exit, 'f_stat': f_exit, 'f_p': fp_exit, 'loo': loo_plus_exit},
        'axm_departure': {'dr2': dr2_dep, 'f_stat': f_dep, 'f_p': fp_dep, 'loo': loo_plus_dep},
        'gk_exit_frac': {'dr2': dr2_gk, 'f_stat': f_gk, 'f_p': fp_gk, 'loo': loo_plus_gk},
    }
    best_feat = max(features, key=lambda k: features[k]['dr2'])
    best = features[best_feat]

    if best['dr2'] >= 0.03 and best['f_p'] < 0.05 and best['loo'] > loo_entry_bundle:
        verdict = 'EXIT_EXTENDS'
    elif best['dr2'] >= 0.01 or best['f_p'] < 0.10:
        verdict = 'EXIT_MARGINAL'
    else:
        verdict = 'EXIT_ABSORBED'
    print(f"  Best exit feature: {best_feat} (dR²={best['dr2']:.4f})")
    print(f"  Verdict: {verdict}")

    return {
        'entry_bundle': {'r2': r2_entry_bundle, 'loo': loo_entry_bundle},
        'per_feature': features,
        'all_exit_features': {'dr2': dr2_all, 'f_stat': f_all, 'f_p': fp_all, 'loo': loo_plus_all},
        'best_feature': best_feat,
        'verdict': verdict,
    }


# ── Test 5: DUAL_BOUNDARY_ARCHITECTURE ──────────────────────────

def test5_dual_boundary_architecture(div_data, boundary_data, folio_data):
    print("\n── Test 5: DUAL_BOUNDARY_ARCHITECTURE ──")

    folios = sorted(f for f in div_data if f in boundary_data and f in folio_data)
    n = len(folios)

    jsd_entry = np.array([div_data[f]['jsd_entry'] for f in folios])
    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])
    axm_return = np.array([boundary_data[f]['axm_return_rate'] for f in folios])
    axm_departure = np.array([boundary_data[f]['axm_departure_rate'] for f in folios])
    sections = [folio_data[f]['section'] for f in folios]

    X_base, _ = build_baseline(folios, folio_data)

    # Entry-only bundle
    je_z = standardize(jsd_entry).reshape(-1, 1)
    arr_z = standardize(axm_return).reshape(-1, 1)
    X_entry_only = np.hstack([X_base, je_z, arr_z])
    _, _, _, r2_entry_only = ols_fit(X_entry_only, axm)
    loo_entry_only = loo_cv_r2(X_entry_only, axm)

    # Exit-only bundle
    jx_z = standardize(jsd_exit).reshape(-1, 1)
    dep_z = standardize(axm_departure).reshape(-1, 1)
    X_exit_only = np.hstack([X_base, jx_z, dep_z])
    _, _, _, r2_exit_only = ols_fit(X_exit_only, axm)
    loo_exit_only = loo_cv_r2(X_exit_only, axm)

    # Full dual model
    X_dual = np.hstack([X_base, je_z, arr_z, jx_z, dep_z])
    _, _, ss_dual, r2_dual = ols_fit(X_dual, axm)
    loo_dual = loo_cv_r2(X_dual, axm)

    print(f"  Entry-only bundle: R²={r2_entry_only:.4f}, LOO={loo_entry_only:.4f}")
    print(f"  Exit-only bundle:  R²={r2_exit_only:.4f}, LOO={loo_exit_only:.4f}")
    print(f"  Dual model:        R²={r2_dual:.4f}, LOO={loo_dual:.4f}")

    # Entry/exit partial correlation controlling for baseline
    Z_base = X_base[:, 1:]  # drop intercept
    rho_ee_partial, p_ee_partial = partial_corr_spearman(jsd_entry, jsd_exit, Z_base)
    print(f"  Partial (entry vs exit | baseline): rho={rho_ee_partial:.4f}, p={p_ee_partial:.4f}")

    # Per-section analysis
    unique_sections = sorted(set(sections))
    section_results = {}
    sections_exit_helps = 0

    for sec in unique_sections:
        sec_mask = np.array([s == sec for s in sections])
        n_sec = sec_mask.sum()
        if n_sec < 10:
            print(f"  Section {sec}: n={n_sec} (too small, skipping)")
            continue

        axm_sec = axm[sec_mask]
        je_sec = standardize(jsd_entry[sec_mask]).reshape(-1, 1)
        arr_sec = standardize(axm_return[sec_mask]).reshape(-1, 1)
        jx_sec = standardize(jsd_exit[sec_mask]).reshape(-1, 1)
        dep_sec = standardize(axm_departure[sec_mask]).reshape(-1, 1)
        intercept_sec = np.ones((n_sec, 1))

        # Entry-only within section
        X_e_sec = np.hstack([intercept_sec, je_sec, arr_sec])
        _, _, _, r2_e_sec = ols_fit(X_e_sec, axm_sec)

        # Dual within section
        X_d_sec = np.hstack([intercept_sec, je_sec, arr_sec, jx_sec, dep_sec])
        _, _, _, r2_d_sec = ols_fit(X_d_sec, axm_sec)

        dr2_sec = r2_d_sec - r2_e_sec
        print(f"  Section {sec}: n={n_sec}, entry R²={r2_e_sec:.4f}, dual R²={r2_d_sec:.4f}, dR²={dr2_sec:.4f}")

        section_results[sec] = {
            'n': int(n_sec),
            'r2_entry_only': r2_e_sec,
            'r2_dual': r2_d_sec,
            'dr2_exit': dr2_sec,
        }
        if dr2_sec >= 0.03:
            sections_exit_helps += 1

    # Verdict
    exit_dr2 = r2_dual - r2_entry_only
    exit_loo_gain = loo_dual - loo_entry_only
    if exit_dr2 >= 0.03 and exit_loo_gain > 0 and sections_exit_helps >= 2:
        verdict = 'DUAL_CHANNEL'
    elif sections_exit_helps >= 1 and exit_dr2 >= 0.01:
        verdict = 'ASYMMETRIC_CHANNEL'
    else:
        verdict = 'SINGLE_CHANNEL'
    print(f"  Exit increment in dual: dR²={exit_dr2:.4f}, LOO gain={exit_loo_gain:+.4f}")
    print(f"  Sections where exit helps (dR²≥0.03): {sections_exit_helps}")
    print(f"  Verdict: {verdict}")

    return {
        'entry_only': {'r2': r2_entry_only, 'loo': loo_entry_only},
        'exit_only': {'r2': r2_exit_only, 'loo': loo_exit_only},
        'dual_model': {'r2': r2_dual, 'loo': loo_dual},
        'exit_increment_in_dual': {'dr2': exit_dr2, 'loo_gain': exit_loo_gain},
        'partial_entry_vs_exit_ctrl_baseline': {'rho': rho_ee_partial, 'p': p_ee_partial},
        'per_section': section_results,
        'sections_exit_helps': sections_exit_helps,
        'verdict': verdict,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 416: EXIT_DIVERGENCE_SYMMETRY")
    print("=" * 60)

    folio_line_lists, folio_data, valid_folios, class_to_role = load_data()

    # Compute per-folio entry + exit divergence
    div_data = compute_folio_divergence(folio_line_lists, folio_data, valid_folios)
    print(f"\n  Folios with divergence: {len(div_data)}")

    # Compute per-folio boundary properties (opener + closer)
    boundary_data = compute_boundary_properties(folio_line_lists, valid_folios)
    print(f"  Folios with boundary properties: {len(boundary_data)}")

    common = sorted(f for f in div_data if f in boundary_data and f in folio_data)
    print(f"  Common folios: {len(common)}")

    t1 = test1_exit_divergence_baseline(div_data, boundary_data, folio_data)
    t2 = test2_closer_routing_profile(div_data, boundary_data, folio_data)
    t3 = test3_gatekeeper_exit_mechanism(div_data, boundary_data, folio_data)
    t4 = test4_exit_incremental_signal(div_data, boundary_data, folio_data)
    t5 = test5_dual_boundary_architecture(div_data, boundary_data, folio_data)

    # Synthesis
    t4v = t4['verdict']
    t5v = t5['verdict']

    synthesis_map = {
        ('EXIT_EXTENDS', 'DUAL_CHANNEL'): 'EXIT_INDEPENDENT_CHANNEL',
        ('EXIT_EXTENDS', 'ASYMMETRIC_CHANNEL'): 'EXIT_SECTION_SPECIFIC',
        ('EXIT_EXTENDS', 'SINGLE_CHANNEL'): 'EXIT_SECTION_SPECIFIC',
        ('EXIT_MARGINAL', 'DUAL_CHANNEL'): 'EXIT_MARGINAL_CONTRIBUTION',
        ('EXIT_MARGINAL', 'ASYMMETRIC_CHANNEL'): 'EXIT_MARGINAL_CONTRIBUTION',
        ('EXIT_MARGINAL', 'SINGLE_CHANNEL'): 'EXIT_MARGINAL_CONTRIBUTION',
        ('EXIT_ABSORBED', 'DUAL_CHANNEL'): 'EXIT_SECTION_RESIDUAL_ONLY',
        ('EXIT_ABSORBED', 'ASYMMETRIC_CHANNEL'): 'EXIT_SECTION_RESIDUAL_ONLY',
        ('EXIT_ABSORBED', 'SINGLE_CHANNEL'): 'ENTRY_SUBSUMES_EXIT',
    }
    overall = synthesis_map.get((t4v, t5v), 'UNCLASSIFIED')

    print(f"\n── SYNTHESIS ──")
    print(f"  T1={t1['verdict']}")
    print(f"  T2={t2['verdict']}")
    print(f"  T3={t3['verdict']}")
    print(f"  T4={t4['verdict']}")
    print(f"  T5={t5['verdict']}")
    print(f"  Overall: {overall}")

    output = {
        'phase': 'EXIT_DIVERGENCE_SYMMETRY',
        'phase_number': 416,
        'depends_on': ['C1035', 'C1156', 'C1157', 'C1158', 'C1159',
                       'C1163', 'C1165', 'C1007', 'C1008', 'C1009', 'C976'],
        'n_folios': len(common),
        'test1_exit_divergence_baseline': t1,
        'test2_closer_routing_profile': t2,
        'test3_gatekeeper_exit_mechanism': t3,
        'test4_exit_incremental_signal': t4,
        'test5_dual_boundary_architecture': t5,
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
    out_path = RESULTS_DIR / 'exit_divergence_symmetry.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
