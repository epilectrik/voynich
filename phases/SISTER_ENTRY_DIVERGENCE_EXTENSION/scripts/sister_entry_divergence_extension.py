#!/usr/bin/env python3
"""
Phase 421: SISTER_ENTRY_DIVERGENCE_EXTENSION
==============================================
Pre-registered minimal model comparison testing whether opener sister-pair
composition (opener_ch_frac) independently predicts per-folio entry divergence
beyond the existing boundary architecture.

5-test battery:
  T1: MODEL_CASCADE (B0 -> B1 -> B2 -> B3 -> S, nested OLS + F-tests)
  T2: NESTED_LOFO (LOFO with nested preprocessing, DLOO-R2 threshold >= 0.02)
  T3: WITHIN_SECTION_LOFO (per-section LOFO sensitivity)
  T4: COEFFICIENT_ANALYSIS (sign, magnitude, stability under ablation)
  T5: SECONDARY_AXM_MEDIATION (add opener_ch_frac to C1168 dual-boundary model)

Pre-registered specification (expert-designed):
  Target Y: jsd_entry (per-folio entry divergence, Phase 415 computation)
  New lever: opener_ch_frac = ch/(ch+sh) among line-initial tokens
  Threshold: DLOO-R2(S vs B3) >= 0.02
  Coefficient sign: opener_ch_frac should be positive

Depends on: C1035, C1156-C1168, C1180, C1181, C1186, C639
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
MIN_OPENERS = 10

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

INITIAL_SPECIALIST_PREFIXES = {'po', 'dch', 'so', 'tch', 'pch', 'sa'}
ROLES = ['AUXILIARY', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL']


# ── Utilities ─────────────────────────────────────────────────────

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
    if f_stat < 0:
        return 0.0, 1.0
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
    """Standard LOO-R2 (global standardization, for backward compatibility)."""
    n = len(y)
    y_pred_loo = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        beta = np.linalg.lstsq(X[mask], y[mask], rcond=None)[0]
        y_pred_loo[i] = float((X[i:i+1] @ beta).item())
    ss_res = np.sum((y - y_pred_loo) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


def nested_lofo(X_cat, X_cont_raw, y):
    """Leave-one-folio-out with nested preprocessing.

    X_cat: (n, k_cat) dummy variables (fixed, not standardized)
    X_cont_raw: (n, k_cont) raw continuous features (standardized per fold)
    y: (n,) target

    Returns: LOO-R2
    """
    n = len(y)
    if X_cont_raw.shape[1] == 0:
        # B0: categorical only
        X = np.hstack([np.ones((n, 1)), X_cat])
        return loo_cv_r2(X, y)

    y_pred = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        # Standardize using training fold only
        mean_t = X_cont_raw[mask].mean(axis=0)
        std_t = X_cont_raw[mask].std(axis=0) + 1e-10
        X_cont_train = (X_cont_raw[mask] - mean_t) / std_t
        X_cont_test = (X_cont_raw[i:i+1] - mean_t) / std_t
        # Assemble
        X_train = np.hstack([np.ones((mask.sum(), 1)), X_cat[mask], X_cont_train])
        X_test = np.hstack([np.ones((1, 1)), X_cat[i:i+1], X_cont_test])
        beta = np.linalg.lstsq(X_train, y[mask], rcond=None)[0]
        y_pred[i] = float((X_test @ beta).item())
    ss_res = np.sum((y - y_pred) ** 2)
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


def shannon_entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)


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
    token_to_class = {t: int(c) for t, c in cmap['token_to_class'].items()}
    class_to_role = cmap['class_to_role']
    print(f"  Token-to-class entries: {len(token_to_class)}")

    # AXM folio data
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']
    valid_folios = set(folio_data.keys())
    print(f"  AXM data: {len(valid_folios)} folios")

    # Regime mapping (fallback)
    with open(PROJECT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' /
              'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_regime = {}
    for regime, folios in regime_data.items():
        for folio in folios:
            folio_regime[folio] = regime

    # Transcript pass
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
        sister_type = 'other'
        if prefix == 'ch':
            sister_type = 'ch'
        elif prefix == 'sh':
            sister_type = 'sh'

        folio_lines[t.folio][t.line].append({
            'word': w,
            'cls': cls,
            'state': CLASS_TO_STATE[cls],
            'role': class_to_role.get(str(cls), 'UNKNOWN'),
            'prefix': prefix,
            'sister_type': sister_type,
            'is_opener': t.line_initial,
        })

    # Convert to line lists (sorted by line key)
    folio_line_lists = defaultdict(list)
    for folio in sorted(folio_lines.keys()):
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    print(f"  Folios with lines: {len(folio_line_lists)}")

    return folio_line_lists, folio_data, valid_folios, class_to_role, folio_regime


# ── Feature Computation ──────────────────────────────────────────

def compute_folio_features(folio_line_lists, folio_data, valid_folios, class_to_role, folio_regime):
    """Compute all per-folio features in a single pass."""
    print("\nComputing per-folio features...")
    features = {}

    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]

        # Zone transitions (Phase 415 exact)
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

        # JSD entry + exit (6-state)
        m6_entry = matrix_to_6state(build_zone_matrix(zone_trans['ENTRY']))
        m6_interior = matrix_to_6state(build_zone_matrix(zone_trans['INTERIOR']))
        m6_exit = matrix_to_6state(build_zone_matrix(zone_trans['EXIT']))

        jsd_entry = compute_jsd(m6_entry.flatten(), m6_interior.flatten())
        jsd_exit = compute_jsd(m6_exit.flatten(), m6_interior.flatten())

        # Opener properties (Phase 415 exact, lines with >= 4 tokens)
        opener_roles = []
        opener_prefixes = []
        entry_state_transitions = []
        exit_state_transitions = []
        opener_ch_count = 0
        opener_sh_count = 0

        for tokens in lines:
            if len(tokens) < 4:
                continue
            opener = tokens[0]
            follower = tokens[1]
            penultimate = tokens[-2]
            closer = tokens[-1]

            opener_roles.append(opener['role'])
            opener_prefixes.append(opener['prefix'] if opener['prefix'] else 'BARE')
            entry_state_transitions.append((opener['state'], follower['state']))
            exit_state_transitions.append((penultimate['state'], closer['state']))

            if opener['sister_type'] == 'ch':
                opener_ch_count += 1
            elif opener['sister_type'] == 'sh':
                opener_sh_count += 1

        n_openers = len(opener_roles)
        if n_openers < MIN_OPENERS:
            continue

        # Role entropy
        role_counts = Counter(opener_roles)
        role_fracs = {r: role_counts.get(r, 0) / n_openers for r in ROLES}
        role_probs = [role_fracs[r] for r in ROLES if role_fracs[r] > 0]
        role_entropy = shannon_entropy(role_probs)

        # PREFIX entropy
        prefix_counts = Counter(opener_prefixes)
        total_prefixes = sum(prefix_counts.values())
        prefix_probs = [c / total_prefixes for c in prefix_counts.values()]
        prefix_entropy_opener = shannon_entropy(prefix_probs)

        # Initial-specialist fraction
        init_spec_count = sum(prefix_counts.get(p, 0) for p in INITIAL_SPECIALIST_PREFIXES)
        init_spec_frac = init_spec_count / total_prefixes

        # AXM return rate (entry transitions with target=AXM)
        axm_returns = sum(1 for _, tgt in entry_state_transitions if tgt == 'AXM')
        axm_return_rate = axm_returns / len(entry_state_transitions)

        # AXM departure rate (exit transitions FROM AXM to non-AXM)
        axm_exits = sum(1 for src, tgt in exit_state_transitions if src == 'AXM' and tgt != 'AXM')
        axm_sources = sum(1 for src, _ in exit_state_transitions if src == 'AXM')
        axm_departure_rate = axm_exits / max(axm_sources, 1)

        # opener_ch_frac (THE NEW LEVER)
        sister_denom = opener_ch_count + opener_sh_count
        opener_ch_frac = opener_ch_count / sister_denom if sister_denom > 0 else 0.5

        # Baseline features from folio_data
        fd = folio_data[folio]
        section = fd.get('section', 'UNKNOWN')
        regime = fd.get('regime') or folio_regime.get(folio, 'UNKNOWN')

        features[folio] = {
            'jsd_entry': jsd_entry,
            'jsd_exit': jsd_exit,
            'role_entropy': role_entropy,
            'prefix_entropy_opener': prefix_entropy_opener,
            'init_spec_frac': init_spec_frac,
            'axm_return_rate': axm_return_rate,
            'axm_departure_rate': axm_departure_rate,
            'opener_ch_frac': opener_ch_frac,
            'opener_ch_count': opener_ch_count,
            'opener_sh_count': opener_sh_count,
            'opener_sister_total': sister_denom,
            'n_openers': n_openers,
            'section': section,
            'regime': regime,
            'axm_self': fd.get('axm_self', 0),
            'prefix_entropy': fd.get('prefix_entropy', 0),
            'hazard_density': fd.get('hazard_density', 0),
            'bridge_pc1': fd.get('bridge_pc1', 0),
            'zone_counts': {z: len(zone_trans[z]) for z in zone_trans},
        }

    print(f"  Folios with all features: {len(features)}")
    defaulting = sum(1 for f in features.values() if f['opener_sister_total'] == 0)
    print(f"  Folios defaulting opener_ch_frac=0.5: {defaulting}")
    return features


# ── Design Matrix Construction ───────────────────────────────────

def build_model_cascade(features):
    """Build aligned arrays and nested continuous matrices for B0-S."""
    folios = sorted(features.keys())
    n = len(folios)

    # Target
    y = np.array([features[f]['jsd_entry'] for f in folios])

    # Categorical
    sections = [features[f]['section'] for f in folios]
    regimes = [features[f]['regime'] for f in folios]
    section_dum = build_dummies(sections)
    regime_dum = build_dummies(regimes)
    X_cat = np.hstack([section_dum, regime_dum])

    # Raw continuous features (NOT standardized — nested_lofo handles this)
    role_ent = np.array([features[f]['role_entropy'] for f in folios])
    pfx_ent_opener = np.array([features[f]['prefix_entropy_opener'] for f in folios])
    init_spec = np.array([features[f]['init_spec_frac'] for f in folios])
    axm_ret = np.array([features[f]['axm_return_rate'] for f in folios])
    haz_dens = np.array([features[f]['hazard_density'] for f in folios])
    bridge = np.array([features[f]['bridge_pc1'] for f in folios])
    pfx_ent = np.array([features[f]['prefix_entropy'] for f in folios])
    opener_ch = np.array([features[f]['opener_ch_frac'] for f in folios])

    # Nested continuous matrices
    empty = np.zeros((n, 0))
    cont = {
        'B0': empty,
        'B1': np.column_stack([role_ent, pfx_ent_opener, init_spec]),
        'B2': np.column_stack([role_ent, pfx_ent_opener, init_spec, axm_ret]),
        'B3': np.column_stack([role_ent, pfx_ent_opener, init_spec, axm_ret,
                                haz_dens, bridge, pfx_ent]),
        'S':  np.column_stack([role_ent, pfx_ent_opener, init_spec, axm_ret,
                                haz_dens, bridge, pfx_ent, opener_ch]),
    }

    print(f"\n  Design matrix: {n} folios, {X_cat.shape[1]} cat cols")
    for name, c in cont.items():
        print(f"    {name}: {c.shape[1]} continuous features")

    return folios, y, X_cat, cont, sections


# ── Test 1: MODEL_CASCADE ────────────────────────────────────────

def test1_model_cascade(y, X_cat, cont):
    """Full-sample OLS with F-test increments at each step."""
    print("\n" + "=" * 60)
    print("T1: MODEL_CASCADE")
    print("=" * 60)

    n = len(y)
    results = {}
    prev_ss_res = None
    prev_k = None
    model_order = ['B0', 'B1', 'B2', 'B3', 'S']
    feature_counts = {'B0': 0, 'B1': 3, 'B2': 4, 'B3': 7, 'S': 8}

    for name in model_order:
        c = cont[name]
        if c.shape[1] > 0:
            c_z = np.column_stack([standardize(c[:, j]) for j in range(c.shape[1])])
        else:
            c_z = np.zeros((n, 0))
        X = np.hstack([np.ones((n, 1)), X_cat, c_z])
        k = X.shape[1]
        beta, y_pred, ss_res, r2 = ols_fit(X, y)

        # Standard LOO-R2 (for comparison with nested)
        loo_r2 = loo_cv_r2(X, y)

        # F-test vs previous model
        f_stat, f_p = 0.0, 1.0
        dr2 = 0.0
        if prev_ss_res is not None:
            df_extra = k - prev_k
            if df_extra > 0:
                f_stat, f_p = f_test_increment(prev_ss_res, ss_res, df_extra, n, k)
                dr2 = r2 - results[model_order[model_order.index(name) - 1]]['r2']

        results[name] = {
            'r2': float(r2),
            'loo_r2': float(loo_r2),
            'ss_res': float(ss_res),
            'k': k,
            'dr2_vs_prev': float(dr2),
            'f_stat': float(f_stat),
            'f_p': float(f_p),
        }

        print(f"  {name}: R2={r2:.4f}  LOO-R2={loo_r2:.4f}  k={k}  dR2={dr2:.4f}  F={f_stat:.2f}  p={f_p:.4f}")
        prev_ss_res = ss_res
        prev_k = k

    # Key pre-registered metric
    dr2_S_vs_B3 = results['S']['r2'] - results['B3']['r2']
    print(f"\n  >>> dR2(S vs B3) = {dr2_S_vs_B3:.4f}")

    results['dr2_S_vs_B3'] = float(dr2_S_vs_B3)
    return results


# ── Test 2: NESTED_LOFO ──────────────────────────────────────────

def test2_nested_lofo(y, X_cat, cont):
    """LOFO with per-fold standardization — the primary test."""
    print("\n" + "=" * 60)
    print("T2: NESTED_LOFO (primary test)")
    print("=" * 60)

    results = {}
    model_order = ['B0', 'B1', 'B2', 'B3', 'S']

    for name in model_order:
        loo_r2 = nested_lofo(X_cat, cont[name], y)
        results[name] = float(loo_r2)
        print(f"  {name}: nested LOO-R2 = {loo_r2:.4f}")

    dloo = results['S'] - results['B3']
    print(f"\n  >>> DLOO-R2(S vs B3) = {dloo:.4f}")

    if dloo >= 0.02:
        verdict = 'SISTER_EXTENDS'
    elif dloo >= 0.005:
        verdict = 'SISTER_MARGINAL'
    else:
        verdict = 'SISTER_ABSORBED'

    print(f"  >>> Verdict: {verdict}")

    return {
        'nested_loo_r2': results,
        'dloo_S_vs_B3': float(dloo),
        'threshold': 0.02,
        'verdict': verdict,
    }


# ── Test 3: WITHIN_SECTION_LOFO ──────────────────────────────────

def test3_within_section_lofo(y, X_cat, cont, sections, folios, features):
    """Per-section LOFO for B3 and S."""
    print("\n" + "=" * 60)
    print("T3: WITHIN_SECTION_LOFO")
    print("=" * 60)

    unique_sections = sorted(set(sections))
    results = {}
    sections_with_gain = 0

    for sec in unique_sections:
        sec_mask = np.array([s == sec for s in sections])
        n_sec = int(sec_mask.sum())
        if n_sec < 10:
            print(f"  Section {sec}: n={n_sec} < 10, skipped")
            results[sec] = {'n': n_sec, 'skipped': True}
            continue

        y_sec = y[sec_mask]

        # Within section: regime dummies only (section is constant)
        sec_folios = [folios[i] for i in range(len(folios)) if sec_mask[i]]
        sec_regimes = [features[f]['regime'] for f in sec_folios]
        regime_dum_sec = build_dummies(sec_regimes)

        # Continuous features (subset rows)
        cont_b3_sec = cont['B3'][sec_mask]
        cont_s_sec = cont['S'][sec_mask]

        loo_b3 = nested_lofo(regime_dum_sec, cont_b3_sec, y_sec)
        loo_s = nested_lofo(regime_dum_sec, cont_s_sec, y_sec)
        dloo = loo_s - loo_b3

        if dloo >= 0.01:
            sections_with_gain += 1

        results[sec] = {
            'n': n_sec,
            'loo_b3': float(loo_b3),
            'loo_s': float(loo_s),
            'dloo': float(dloo),
        }
        print(f"  Section {sec}: n={n_sec}  B3={loo_b3:.4f}  S={loo_s:.4f}  DLOO={dloo:.4f}")

    if sections_with_gain >= 2:
        verdict = 'SECTION_ROBUST'
    elif sections_with_gain == 1:
        verdict = 'SECTION_SPECIFIC'
    else:
        verdict = 'SECTION_ABSENT'

    print(f"\n  >>> Sections with DLOO >= 0.01: {sections_with_gain}")
    print(f"  >>> Verdict: {verdict}")

    return {
        'per_section': results,
        'sections_with_gain': sections_with_gain,
        'verdict': verdict,
    }


# ── Test 4: COEFFICIENT_ANALYSIS ─────────────────────────────────

def test4_coefficient_analysis(y, X_cat, cont, features, folios, sections):
    """Sign check, ablation stability, correlation, collinearity."""
    print("\n" + "=" * 60)
    print("T4: COEFFICIENT_ANALYSIS")
    print("=" * 60)

    n = len(y)

    # Full Model S — global standardization for coefficient extraction
    c_s = cont['S']
    c_s_z = np.column_stack([standardize(c_s[:, j]) for j in range(c_s.shape[1])])
    X_s = np.hstack([np.ones((n, 1)), X_cat, c_s_z])
    beta_s, _, _, r2_s = ols_fit(X_s, y)

    # opener_ch_frac is the LAST continuous feature
    beta_opener_ch = float(beta_s[-1])
    sign_positive = beta_opener_ch > 0

    print(f"  Full S model: beta(opener_ch_frac) = {beta_opener_ch:.6f}")
    print(f"  Sign positive: {sign_positive}")

    # Ablation: drop one continuous feature at a time from S
    feature_names = ['role_entropy', 'prefix_entropy_opener', 'init_spec_frac',
                     'axm_return_rate', 'hazard_density', 'bridge_pc1', 'prefix_entropy',
                     'opener_ch_frac']
    ablation_results = {}
    for drop_idx in range(c_s.shape[1] - 1):  # Don't drop opener_ch_frac itself
        keep_cols = [j for j in range(c_s.shape[1]) if j != drop_idx]
        c_abl = c_s[:, keep_cols]
        c_abl_z = np.column_stack([standardize(c_abl[:, j]) for j in range(c_abl.shape[1])])
        X_abl = np.hstack([np.ones((n, 1)), X_cat, c_abl_z])
        beta_abl, _, _, _ = ols_fit(X_abl, y)
        # opener_ch_frac is the last column in the ablated model
        beta_ch_abl = float(beta_abl[-1])
        ablation_results[feature_names[drop_idx]] = {
            'beta_opener_ch': beta_ch_abl,
            'sign_positive': beta_ch_abl > 0,
        }
        print(f"  Ablate {feature_names[drop_idx]}: beta(opener_ch) = {beta_ch_abl:.6f}")

    # Stability: all ablations keep same sign and within 50% magnitude
    all_same_sign = all(r['sign_positive'] == sign_positive for r in ablation_results.values())
    magnitudes = [abs(r['beta_opener_ch']) for r in ablation_results.values()]
    base_mag = abs(beta_opener_ch)
    within_50 = all(m >= base_mag * 0.5 and m <= base_mag * 1.5 for m in magnitudes) if base_mag > 0 else True
    stable = all_same_sign and within_50

    # Bivariate + partial Spearman
    opener_ch_arr = np.array([features[f]['opener_ch_frac'] for f in folios])
    rho_biv, p_biv = spearman_r(opener_ch_arr.tolist(), y.tolist())
    Z_control = np.hstack([build_dummies(sections), build_dummies([features[f]['regime'] for f in folios])])
    rho_partial, p_partial = partial_corr_spearman(opener_ch_arr, y, Z_control)

    print(f"\n  Bivariate Spearman: rho={rho_biv:.4f}  p={p_biv:.4f}")
    print(f"  Partial Spearman (section+regime): rho={rho_partial:.4f}  p={p_partial:.4f}")

    # Collinearity check: R2 from regressing opener_ch_frac on all B3 features
    c_b3 = cont['B3']
    c_b3_z = np.column_stack([standardize(c_b3[:, j]) for j in range(c_b3.shape[1])])
    X_colin = np.hstack([np.ones((n, 1)), X_cat, c_b3_z])
    _, _, _, r2_colin = ols_fit(X_colin, standardize(opener_ch_arr))
    collinear = r2_colin > 0.8
    print(f"  Collinearity R2 (opener_ch ~ B3 features): {r2_colin:.4f}  {'FLAG' if collinear else 'OK'}")

    if sign_positive and stable:
        verdict = 'SIGN_CONFIRMED_STABLE'
    elif sign_positive and not stable:
        verdict = 'SIGN_CONFIRMED_UNSTABLE'
    else:
        verdict = 'SIGN_WRONG'

    print(f"\n  >>> Verdict: {verdict}")

    return {
        'beta_opener_ch_frac': beta_opener_ch,
        'sign_positive': sign_positive,
        'ablation': ablation_results,
        'ablation_all_same_sign': all_same_sign,
        'ablation_within_50pct': within_50,
        'stable': stable,
        'spearman_bivariate': {'rho': float(rho_biv), 'p': float(p_biv)},
        'spearman_partial': {'rho': float(rho_partial), 'p': float(p_partial)},
        'collinearity_r2': float(r2_colin),
        'collinear_flag': collinear,
        'verdict': verdict,
    }


# ── Test 5: SECONDARY_AXM_MEDIATION ──────────────────────────────

def test5_secondary_axm_mediation(folios, features, y_entry_div, X_cat, cont):
    """Add opener_ch_frac to C1168 dual-boundary model predicting AXM_self."""
    print("\n" + "=" * 60)
    print("T5: SECONDARY_AXM_MEDIATION")
    print("=" * 60)

    n = len(folios)

    # Target: AXM self-transition rate
    y_axm = np.array([features[f]['axm_self'] for f in folios])

    # C1168 continuous features: baseline + entry + exit
    # baseline: prefix_entropy, hazard_density, bridge_pc1
    # entry: jsd_entry, axm_return_rate
    # exit: jsd_exit, axm_departure_rate
    pfx_ent = np.array([features[f]['prefix_entropy'] for f in folios])
    haz = np.array([features[f]['hazard_density'] for f in folios])
    bridge = np.array([features[f]['bridge_pc1'] for f in folios])
    jsd_e = np.array([features[f]['jsd_entry'] for f in folios])
    axm_ret = np.array([features[f]['axm_return_rate'] for f in folios])
    jsd_x = np.array([features[f]['jsd_exit'] for f in folios])
    axm_dep = np.array([features[f]['axm_departure_rate'] for f in folios])
    opener_ch = np.array([features[f]['opener_ch_frac'] for f in folios])

    cont_c1168 = np.column_stack([pfx_ent, haz, bridge, jsd_e, axm_ret, jsd_x, axm_dep])
    cont_extended = np.column_stack([pfx_ent, haz, bridge, jsd_e, axm_ret, jsd_x, axm_dep, opener_ch])

    # Nested LOFO for both
    loo_c1168 = nested_lofo(X_cat, cont_c1168, y_axm)
    loo_extended = nested_lofo(X_cat, cont_extended, y_axm)
    dloo = loo_extended - loo_c1168

    # Full-sample for F-test
    c1168_z = np.column_stack([standardize(cont_c1168[:, j]) for j in range(cont_c1168.shape[1])])
    ext_z = np.column_stack([standardize(cont_extended[:, j]) for j in range(cont_extended.shape[1])])
    X_c1168 = np.hstack([np.ones((n, 1)), X_cat, c1168_z])
    X_ext = np.hstack([np.ones((n, 1)), X_cat, ext_z])

    _, _, ss_c1168, r2_c1168 = ols_fit(X_c1168, y_axm)
    beta_ext, _, ss_ext, r2_ext = ols_fit(X_ext, y_axm)

    f_stat, f_p = f_test_increment(ss_c1168, ss_ext, 1, n, X_ext.shape[1])
    beta_opener_ch = float(beta_ext[-1])

    print(f"  C1168 model: R2={r2_c1168:.4f}  LOO={loo_c1168:.4f}")
    print(f"  Extended:    R2={r2_ext:.4f}  LOO={loo_extended:.4f}")
    print(f"  DLOO = {dloo:.4f}  F={f_stat:.2f}  p={f_p:.4f}")
    print(f"  beta(opener_ch_frac) = {beta_opener_ch:.6f}")

    if dloo >= 0.015 and f_p < 0.05:
        verdict = 'AXM_EXTENDS'
    elif dloo > 0:
        verdict = 'AXM_MARGINAL'
    else:
        verdict = 'AXM_ABSORBED'

    print(f"\n  >>> Verdict: {verdict}")

    return {
        'c1168_r2': float(r2_c1168),
        'c1168_loo': float(loo_c1168),
        'extended_r2': float(r2_ext),
        'extended_loo': float(loo_extended),
        'dloo': float(dloo),
        'f_stat': float(f_stat),
        'f_p': float(f_p),
        'beta_opener_ch_frac': beta_opener_ch,
        'verdict': verdict,
    }


# ── Synthesis ─────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5):
    """Apply pre-registered decision tree."""
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    dloo = t2['dloo_S_vs_B3']
    sign_ok = t4['sign_positive']
    sections_robust = t3['sections_with_gain'] >= 2

    if dloo >= 0.02 and sign_ok and sections_robust:
        verdict = 'SISTER_ENTRY_LEVER_CONFIRMED'
    elif dloo >= 0.02 and sign_ok:
        verdict = 'SISTER_ENTRY_LEVER_SECTION_SPECIFIC'
    elif dloo >= 0.005 and sign_ok:
        verdict = 'SISTER_ENTRY_LEVER_MARGINAL'
    else:
        verdict = 'SISTER_ENTRY_LEVER_ABSENT'

    if t5['verdict'] == 'AXM_EXTENDS':
        verdict += '_WITH_AXM_EXTENSION'

    print(f"  Primary DLOO(S vs B3) = {dloo:.4f}  threshold = 0.02")
    print(f"  Coefficient sign positive: {sign_ok}")
    print(f"  Section-robust (>= 2 sections): {sections_robust}")
    print(f"  AXM mediation: {t5['verdict']}")
    print(f"\n  >>> OVERALL VERDICT: {verdict}")

    return {
        'verdict': verdict,
        'primary_dloo': float(dloo),
        'sign_positive': sign_ok,
        'section_robust': sections_robust,
        'axm_mediation': t5['verdict'],
        'interpretation': _interpret(verdict),
    }


def _interpret(verdict):
    if 'CONFIRMED' in verdict:
        return ("opener_ch_frac is an independent predictor of entry divergence, "
                "beyond opener routing and AXM return rate. Sister composition at "
                "openers is a genuine 'below role identity' entry control lever. "
                "Part of C1169's ~27% residual was closed only relative to a "
                "predictor set that excluded sister.")
    elif 'SECTION_SPECIFIC' in verdict:
        return ("opener_ch_frac predicts entry divergence in at least one section "
                "but the effect is not robust across sections. Sister may be a "
                "section-conditioned lever rather than a universal control parameter.")
    elif 'MARGINAL' in verdict:
        return ("opener_ch_frac shows small but above-noise improvement. The effect "
                "is detectable but below the pre-registered threshold of 0.02. "
                "Sister contributes weakly to entry divergence prediction.")
    else:
        return ("opener_ch_frac does not independently predict entry divergence "
                "beyond the existing battery. Sister is correlated with entry "
                "divergence (C1186) but does not add independent information once "
                "opener routing and AXM return rate are included. Sister is a "
                "proxy for these features, not an additional control channel.")


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 421: SISTER_ENTRY_DIVERGENCE_EXTENSION")
    print("Pre-registered minimal model comparison")
    print("=" * 60)

    folio_line_lists, folio_data, valid_folios, class_to_role, folio_regime = load_data()
    features = compute_folio_features(folio_line_lists, folio_data, valid_folios,
                                       class_to_role, folio_regime)

    folios, y, X_cat, cont, sections = build_model_cascade(features)

    t1 = test1_model_cascade(y, X_cat, cont)
    t2 = test2_nested_lofo(y, X_cat, cont)
    t3 = test3_within_section_lofo(y, X_cat, cont, sections, folios, features)
    t4 = test4_coefficient_analysis(y, X_cat, cont, features, folios, sections)
    t5 = test5_secondary_axm_mediation(folios, features, y, X_cat, cont)

    syn = synthesize(t1, t2, t3, t4, t5)

    output = {
        'phase': 'SISTER_ENTRY_DIVERGENCE_EXTENSION',
        'phase_number': 421,
        'depends_on': ['C1035', 'C1156', 'C1158', 'C1163', 'C1164',
                       'C1168', 'C1180', 'C1181', 'C1186', 'C639'],
        'pre_registration': {
            'target': 'jsd_entry (per-folio entry divergence, 6-state JSD)',
            'new_lever': 'opener_ch_frac = ch/(ch+sh) among line-initial tokens',
            'threshold': 'DLOO-R2(S vs B3) >= 0.02',
            'coefficient_sign': 'positive expected',
            'cv_scheme': 'LOFO with nested preprocessing',
        },
        'n_folios': len(folios),
        'test1_model_cascade': t1,
        'test2_nested_lofo': t2,
        'test3_within_section_lofo': t3,
        'test4_coefficient_analysis': t4,
        'test5_secondary_axm_mediation': t5,
        'synthesis': syn,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'sister_entry_divergence_extension.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
