#!/usr/bin/env python3
"""
Phase 415: ENTRY_RESET_MECHANISM
=================================
Decomposes C1158's entry dominance finding: what opener properties drive
per-folio entry divergence variation, and can they explain additional AXM residual?

5-test battery:
  T1: OPENER_ROLE_DISTRIBUTION (do opener role fractions predict entry divergence?)
  T2: PREFIX_FAMILY_DISTRIBUTION (do opener PREFIX families predict entry divergence?)
  T3: OPENER_FOLLOWER_ROUTING (do opener→follower routing patterns predict it?)
  T4: ENTRY_DIVERGENCE_MEDIATION (do opener properties mediate C1158's dR²=0.098?)
  T5: AXM_RESIDUAL_EXTENSION (do opener properties extend AXM residual beyond entry div?)

Depends on: C1035, C1156, C1157, C1158, C1159, C958, C959, C1001, C931, C556, C557
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

# C1001 initial-specialist PREFIXes (>2x line-initial enrichment)
INITIAL_SPECIALIST_PREFIXES = {'po', 'dch', 'so', 'tch', 'pch', 'sa'}

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
    X_z = np.column_stack([np.ones(n), Z]) if Z.ndim > 1 else np.column_stack([np.ones(n), Z.reshape(-1, 1)])
    beta_x = np.linalg.lstsq(X_z, x, rcond=None)[0]
    res_x = x - X_z @ beta_x
    beta_y = np.linalg.lstsq(X_z, y, rcond=None)[0]
    res_y = y - X_z @ beta_y
    return spearman_r(res_x.tolist(), res_y.tolist())


def shannon_entropy(probs):
    """Shannon entropy of a probability distribution."""
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
    class_to_role = cmap['class_to_role']  # str(cls) -> role name

    # AXM folio data
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']
    valid_folios = set(folio_data.keys())

    morph = Morphology()

    # Build per-folio per-line token lists WITH opener properties
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
        })

    # Convert to line lists
    folio_line_lists = defaultdict(list)
    for folio in sorted(folio_lines.keys()):
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    print(f"  Folios with lines: {len(folio_line_lists)}")
    print(f"  AXM data: {len(valid_folios)} folios")

    return folio_line_lists, folio_data, valid_folios, class_to_role


# ── Per-Folio Entry Divergence (replicating Phase 414 T1) ────────

def compute_folio_entry_divergence(folio_line_lists, folio_data, valid_folios):
    """Compute per-folio entry and exit divergence vs interior (6-state JSD)."""
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

        jsd_entry = compute_jsd(m6_entry.flatten(), m6_interior.flatten())

        results[folio] = {
            'jsd_entry': jsd_entry,
            'zone_counts': {z: len(zone_trans[z]) for z in zone_trans},
        }

    return results


# ── Per-Folio Opener Properties ──────────────────────────────────

def compute_opener_properties(folio_line_lists, valid_folios):
    """Extract per-folio opener role distribution, PREFIX distribution, and routing."""
    results = {}

    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]

        opener_roles = []
        opener_prefixes = []
        opener_states = []
        entry_transitions = []  # (src_state, tgt_state) for position 0→1

        for tokens in lines:
            if len(tokens) < 4:  # need all 3 zones
                continue
            opener = tokens[0]
            follower = tokens[1]

            opener_roles.append(opener['role'])
            opener_prefixes.append(opener['prefix'] if opener['prefix'] else 'BARE')
            opener_states.append(opener['state'])
            entry_transitions.append((opener['state'], follower['state']))

        n_openers = len(opener_roles)
        if n_openers < MIN_OPENERS:
            continue

        # Role distribution
        role_counts = Counter(opener_roles)
        role_fracs = {r: role_counts.get(r, 0) / n_openers for r in ROLES}
        role_probs = [role_fracs[r] for r in ROLES if role_fracs[r] > 0]
        role_entropy = shannon_entropy(role_probs)

        # PREFIX distribution
        prefix_counts = Counter(opener_prefixes)
        total_prefixes = sum(prefix_counts.values())
        prefix_fracs = {p: c / total_prefixes for p, c in prefix_counts.most_common()}
        prefix_probs = list(prefix_fracs.values())
        prefix_entropy = shannon_entropy(prefix_probs)

        # Initial-specialist fraction (C1001)
        init_spec_count = sum(prefix_counts.get(p, 0) for p in INITIAL_SPECIALIST_PREFIXES)
        init_spec_frac = init_spec_count / total_prefixes

        # AXM return rate at entry (fraction of entry transitions with target=AXM)
        axm_returns = sum(1 for _, tgt in entry_transitions if tgt == 'AXM')
        axm_return_rate = axm_returns / len(entry_transitions)

        # Routing concentration at entry (6-state target distribution)
        tgt_counts = Counter(tgt for _, tgt in entry_transitions)
        tgt_fracs = np.array([tgt_counts.get(s, 0) / len(entry_transitions) for s in STATE_ORDER])
        routing_concentration = float(tgt_fracs.max() - tgt_fracs.mean())

        # Opener state distribution (what 6-states do openers come from?)
        opener_state_counts = Counter(opener_states)
        opener_axm_frac = opener_state_counts.get('AXM', 0) / n_openers

        # Per-cell entry routing matrix (6x6, normalized by row)
        entry_matrix = np.zeros((N_STATES, N_STATES))
        for src, tgt in entry_transitions:
            entry_matrix[STATE_IDX[src], STATE_IDX[tgt]] += 1

        results[folio] = {
            'n_openers': n_openers,
            'role_fracs': role_fracs,
            'role_entropy': role_entropy,
            'prefix_entropy': prefix_entropy,
            'init_spec_frac': init_spec_frac,
            'top_prefixes': dict(prefix_counts.most_common(5)),
            'axm_return_rate': axm_return_rate,
            'routing_concentration': routing_concentration,
            'opener_axm_frac': opener_axm_frac,
            'entry_matrix': entry_matrix,
        }

    return results


# ── Build C1035 Baseline ─────────────────────────────────────────

def build_baseline(folios, folio_data):
    """Build C1035 baseline design matrix and AXM target."""
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


# ── Test 1: OPENER_ROLE_DISTRIBUTION ─────────────────────────────

def test1_opener_role_distribution(opener_data, entry_div_data, folio_data):
    print("\n── Test 1: OPENER_ROLE_DISTRIBUTION ──")

    folios = sorted(f for f in opener_data if f in entry_div_data)
    n = len(folios)
    print(f"  Folios: {n}")

    jsd_e = np.array([entry_div_data[f]['jsd_entry'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    # Role fractions and entropy
    role_entropy = np.array([opener_data[f]['role_entropy'] for f in folios])
    role_frac_arrays = {}
    for role in ROLES:
        role_frac_arrays[role] = np.array([opener_data[f]['role_fracs'][role] for f in folios])

    # Descriptive stats
    print(f"  Opener role entropy: mean={role_entropy.mean():.4f}, std={role_entropy.std():.4f}")
    for role in ROLES:
        arr = role_frac_arrays[role]
        print(f"  {role}: mean={arr.mean():.4f}, std={arr.std():.4f}")

    # Spearman: each role fraction vs entry divergence
    role_vs_entry = {}
    role_vs_axm = {}
    sig_count = 0
    for role in ROLES:
        rho_e, p_e = spearman_r(role_frac_arrays[role].tolist(), jsd_e.tolist())
        rho_a, p_a = spearman_r(role_frac_arrays[role].tolist(), axm.tolist())
        role_vs_entry[role] = {'rho': rho_e, 'p': p_e}
        role_vs_axm[role] = {'rho': rho_a, 'p': p_a}
        print(f"  {role} vs entry_div: rho={rho_e:.4f}, p={p_e:.4f}")
        print(f"  {role} vs AXM:       rho={rho_a:.4f}, p={p_a:.4f}")
        if abs(rho_e) >= 0.30 and p_e < 0.05:
            sig_count += 1

    # Entropy vs entry divergence
    rho_ent_e, p_ent_e = spearman_r(role_entropy.tolist(), jsd_e.tolist())
    rho_ent_a, p_ent_a = spearman_r(role_entropy.tolist(), axm.tolist())
    print(f"  Role entropy vs entry_div: rho={rho_ent_e:.4f}, p={p_ent_e:.4f}")
    print(f"  Role entropy vs AXM:       rho={rho_ent_a:.4f}, p={p_ent_a:.4f}")

    # OLS: entry_divergence ~ opener role fractions (drop AUXILIARY for collinearity)
    intercept = np.ones((n, 1))
    role_features = []
    role_names_used = []
    for role in ROLES[1:]:  # drop first (AUXILIARY) for collinearity
        role_features.append(role_frac_arrays[role].reshape(-1, 1))
        role_names_used.append(role)
    X_roles = np.hstack([intercept] + role_features)
    _, _, _, r2_roles = ols_fit(X_roles, jsd_e)
    print(f"  R² (entry_div ~ role fractions): {r2_roles:.4f}")

    # Verdict
    if r2_roles >= 0.30 and sig_count >= 2:
        verdict = 'ROLE_STRUCTURED'
    elif r2_roles >= 0.10 or sig_count >= 1:
        verdict = 'ROLE_WEAK'
    else:
        verdict = 'ROLE_UNIFORM'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'role_entropy_stats': {'mean': float(role_entropy.mean()), 'std': float(role_entropy.std())},
        'role_fraction_means': {r: float(role_frac_arrays[r].mean()) for r in ROLES},
        'role_vs_entry_div': role_vs_entry,
        'role_vs_axm': role_vs_axm,
        'entropy_vs_entry_div': {'rho': rho_ent_e, 'p': p_ent_e},
        'entropy_vs_axm': {'rho': rho_ent_a, 'p': p_ent_a},
        'r2_entry_div_from_roles': r2_roles,
        'sig_role_count': sig_count,
        'verdict': verdict,
    }


# ── Test 2: PREFIX_FAMILY_DISTRIBUTION ───────────────────────────

def test2_prefix_family_distribution(opener_data, entry_div_data, folio_data):
    print("\n── Test 2: PREFIX_FAMILY_DISTRIBUTION ──")

    folios = sorted(f for f in opener_data if f in entry_div_data)
    n = len(folios)

    jsd_e = np.array([entry_div_data[f]['jsd_entry'] for f in folios])

    prefix_entropy = np.array([opener_data[f]['prefix_entropy'] for f in folios])
    init_spec_frac = np.array([opener_data[f]['init_spec_frac'] for f in folios])
    role_entropy = np.array([opener_data[f]['role_entropy'] for f in folios])

    print(f"  Prefix entropy: mean={prefix_entropy.mean():.4f}, std={prefix_entropy.std():.4f}")
    print(f"  Initial-specialist frac: mean={init_spec_frac.mean():.4f}, std={init_spec_frac.std():.4f}")

    # Aggregate top prefixes across folios
    all_prefix_counts = Counter()
    for f in folios:
        for p, c in opener_data[f]['top_prefixes'].items():
            all_prefix_counts[p] += c
    print(f"  Top opener PREFIXes (aggregate): {all_prefix_counts.most_common(10)}")

    # Spearman correlations
    rho_pe_e, p_pe_e = spearman_r(prefix_entropy.tolist(), jsd_e.tolist())
    rho_is_e, p_is_e = spearman_r(init_spec_frac.tolist(), jsd_e.tolist())
    print(f"  Prefix entropy vs entry_div: rho={rho_pe_e:.4f}, p={p_pe_e:.4f}")
    print(f"  Init-specialist frac vs entry_div: rho={rho_is_e:.4f}, p={p_is_e:.4f}")

    # Partial correlation: prefix entropy vs entry_div controlling for role entropy
    rho_partial, p_partial = partial_corr_spearman(
        prefix_entropy, jsd_e, role_entropy)
    print(f"  Partial (prefix_ent vs entry_div | role_ent): rho={rho_partial:.4f}, p={p_partial:.4f}")

    # OLS: entry_div ~ prefix features
    intercept = np.ones((n, 1))
    pe_z = standardize(prefix_entropy).reshape(-1, 1)
    is_z = standardize(init_spec_frac).reshape(-1, 1)
    X_prefix = np.hstack([intercept, pe_z, is_z])
    _, _, _, r2_prefix = ols_fit(X_prefix, jsd_e)
    print(f"  R² (entry_div ~ prefix features): {r2_prefix:.4f}")

    # Compare to T1 role R² (passed as context — compute inline)
    role_features = []
    for role in ROLES[1:]:
        role_features.append(
            np.array([opener_data[f]['role_fracs'][role] for f in folios]).reshape(-1, 1))
    X_roles = np.hstack([intercept] + role_features)
    _, _, _, r2_roles = ols_fit(X_roles, jsd_e)
    r2_increment = r2_prefix - r2_roles
    print(f"  R² increment over roles: {r2_increment:.4f}")

    # Verdict
    if r2_prefix >= 0.30 and p_partial < 0.05:
        verdict = 'PREFIX_STRUCTURED'
    elif r2_prefix >= 0.30:
        verdict = 'PREFIX_REDUNDANT'
    else:
        verdict = 'PREFIX_WEAK'
    print(f"  Verdict: {verdict}")

    return {
        'prefix_entropy_stats': {'mean': float(prefix_entropy.mean()), 'std': float(prefix_entropy.std())},
        'init_specialist_stats': {'mean': float(init_spec_frac.mean()), 'std': float(init_spec_frac.std())},
        'top_opener_prefixes': dict(all_prefix_counts.most_common(10)),
        'prefix_entropy_vs_entry_div': {'rho': rho_pe_e, 'p': p_pe_e},
        'init_specialist_vs_entry_div': {'rho': rho_is_e, 'p': p_is_e},
        'partial_prefix_ent_vs_entry_div_ctrl_role_ent': {'rho': rho_partial, 'p': p_partial},
        'r2_entry_div_from_prefix': r2_prefix,
        'r2_increment_over_roles': r2_increment,
        'verdict': verdict,
    }


# ── Test 3: OPENER_FOLLOWER_ROUTING ──────────────────────────────

def test3_opener_follower_routing(opener_data, entry_div_data, folio_data,
                                   folio_line_lists, valid_folios):
    print("\n── Test 3: OPENER_FOLLOWER_ROUTING ──")

    folios = sorted(f for f in opener_data if f in entry_div_data)
    n = len(folios)

    jsd_e = np.array([entry_div_data[f]['jsd_entry'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    # Build global entry and interior 6-state matrices
    agg_entry_trans = []
    agg_interior_trans = []
    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        for tokens in folio_line_lists[folio]:
            n_tok = len(tokens)
            for i in range(n_tok - 1):
                src_cls = tokens[i]['cls']
                tgt_cls = tokens[i + 1]['cls']
                if i == 0:
                    agg_entry_trans.append((src_cls, tgt_cls))
                elif i + 1 != n_tok - 1:
                    agg_interior_trans.append((src_cls, tgt_cls))

    m6_entry_global = normalize_rows(matrix_to_6state(build_zone_matrix(agg_entry_trans)))
    m6_interior_global = normalize_rows(matrix_to_6state(build_zone_matrix(agg_interior_trans)))

    # Top-5 cells by delta
    deltas = []
    for si in range(N_STATES):
        for ti in range(N_STATES):
            d = float(m6_entry_global[si, ti] - m6_interior_global[si, ti])
            deltas.append({'src': STATE_ORDER[si], 'tgt': STATE_ORDER[ti],
                          'delta': d, 'abs_delta': abs(d)})
    deltas.sort(key=lambda x: x['abs_delta'], reverse=True)

    print("  Top-5 global entry routing deltas (vs interior):")
    for d in deltas[:5]:
        print(f"    {d['src']}→{d['tgt']}: {d['delta']:+.4f}")

    # Per-folio features
    axm_return_rate = np.array([opener_data[f]['axm_return_rate'] for f in folios])
    routing_conc = np.array([opener_data[f]['routing_concentration'] for f in folios])

    print(f"  AXM return rate: mean={axm_return_rate.mean():.4f}, std={axm_return_rate.std():.4f}")
    print(f"  Routing concentration: mean={routing_conc.mean():.4f}, std={routing_conc.std():.4f}")

    # Spearman
    rho_arr_e, p_arr_e = spearman_r(axm_return_rate.tolist(), jsd_e.tolist())
    rho_arr_a, p_arr_a = spearman_r(axm_return_rate.tolist(), axm.tolist())
    rho_rc_e, p_rc_e = spearman_r(routing_conc.tolist(), jsd_e.tolist())
    print(f"  AXM return rate vs entry_div: rho={rho_arr_e:.4f}, p={p_arr_e:.4f}")
    print(f"  AXM return rate vs AXM_self:  rho={rho_arr_a:.4f}, p={p_arr_a:.4f}")
    print(f"  Routing conc vs entry_div:    rho={rho_rc_e:.4f}, p={p_rc_e:.4f}")

    # OLS: entry_div ~ routing features
    intercept = np.ones((n, 1))
    arr_z = standardize(axm_return_rate).reshape(-1, 1)
    rc_z = standardize(routing_conc).reshape(-1, 1)
    X_routing = np.hstack([intercept, arr_z, rc_z])
    _, _, _, r2_routing = ols_fit(X_routing, jsd_e)

    # Increment over T1 role model
    role_features = []
    for role in ROLES[1:]:
        role_features.append(
            np.array([opener_data[f]['role_fracs'][role] for f in folios]).reshape(-1, 1))
    X_roles = np.hstack([intercept] + role_features)
    _, _, _, r2_roles = ols_fit(X_roles, jsd_e)
    r2_increment = r2_routing - r2_roles
    print(f"  R² (entry_div ~ routing features): {r2_routing:.4f}")
    print(f"  R² increment over roles: {r2_increment:.4f}")

    # Verdict
    if abs(rho_arr_e) >= 0.40 and r2_routing >= 0.25:
        verdict = 'ROUTING_EXPLAINS'
    elif abs(rho_arr_e) >= 0.25 or r2_routing >= 0.10:
        verdict = 'ROUTING_PARTIAL'
    else:
        verdict = 'ROUTING_DIFFUSE'
    print(f"  Verdict: {verdict}")

    return {
        'top_entry_deltas': deltas[:5],
        'axm_return_rate_stats': {'mean': float(axm_return_rate.mean()), 'std': float(axm_return_rate.std())},
        'routing_concentration_stats': {'mean': float(routing_conc.mean()), 'std': float(routing_conc.std())},
        'axm_return_rate_vs_entry_div': {'rho': rho_arr_e, 'p': p_arr_e},
        'axm_return_rate_vs_axm_self': {'rho': rho_arr_a, 'p': p_arr_a},
        'routing_conc_vs_entry_div': {'rho': rho_rc_e, 'p': p_rc_e},
        'r2_entry_div_from_routing': r2_routing,
        'r2_increment_over_roles': r2_increment,
        'verdict': verdict,
    }


# ── Test 4: ENTRY_DIVERGENCE_MEDIATION ───────────────────────────

def test4_entry_divergence_mediation(opener_data, entry_div_data, folio_data):
    print("\n── Test 4: ENTRY_DIVERGENCE_MEDIATION ──")

    folios = sorted(f for f in opener_data if f in entry_div_data)
    n = len(folios)

    jsd_e = np.array([entry_div_data[f]['jsd_entry'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    # Build C1035 baseline
    X_base, _ = build_baseline(folios, folio_data)
    _, _, ss_base, r2_base = ols_fit(X_base, axm)
    loo_base = loo_cv_r2(X_base, axm)

    # Entry-only model (replicate C1158)
    je_z = standardize(jsd_e).reshape(-1, 1)
    X_entry = np.hstack([X_base, je_z])
    beta_entry, _, ss_entry, r2_entry = ols_fit(X_entry, axm)
    loo_entry = loo_cv_r2(X_entry, axm)
    dr2_entry = r2_entry - r2_base
    f_entry, fp_entry = f_test_increment(ss_base, ss_entry, 1, n, X_entry.shape[1])
    beta_je_alone = float(beta_entry[-1])

    print(f"  Baseline R²={r2_base:.4f}, LOO={loo_base:.4f}")
    print(f"  +Entry div: dR²={dr2_entry:.4f}, F={f_entry:.2f}, p={fp_entry:.4f}, LOO={loo_entry:.4f}")
    print(f"  [C1158 replication: expect dR²≈0.098]")

    # Collect best opener features from T1-T3
    role_entropy = np.array([opener_data[f]['role_entropy'] for f in folios])
    init_spec_frac = np.array([opener_data[f]['init_spec_frac'] for f in folios])
    axm_return_rate = np.array([opener_data[f]['axm_return_rate'] for f in folios])

    opener_feature_names = ['role_entropy', 'init_spec_frac', 'axm_return_rate']
    opener_features_raw = [role_entropy, init_spec_frac, axm_return_rate]
    opener_features_z = [standardize(f).reshape(-1, 1) for f in opener_features_raw]

    # Opener-only model (baseline + opener features)
    X_opener = np.hstack([X_base] + opener_features_z)
    _, _, ss_opener, r2_opener = ols_fit(X_opener, axm)
    loo_opener = loo_cv_r2(X_opener, axm)
    dr2_opener = r2_opener - r2_base
    f_opener, fp_opener = f_test_increment(ss_base, ss_opener, len(opener_features_z), n, X_opener.shape[1])

    print(f"  +Opener features: dR²={dr2_opener:.4f}, F={f_opener:.2f}, p={fp_opener:.4f}, LOO={loo_opener:.4f}")

    # Combined model (baseline + entry_div + opener features)
    X_combined = np.hstack([X_base, je_z] + opener_features_z)
    beta_combined, _, ss_combined, r2_combined = ols_fit(X_combined, axm)
    loo_combined = loo_cv_r2(X_combined, axm)
    dr2_combined = r2_combined - r2_base

    # Entry_div beta is at position X_base.shape[1] (first feature after base)
    beta_je_combined = float(beta_combined[X_base.shape[1]])

    # Coefficient shrinkage
    shrinkage = 1 - abs(beta_je_combined) / max(abs(beta_je_alone), 1e-10)

    print(f"  Combined: R²={r2_combined:.4f}, LOO={loo_combined:.4f}")
    print(f"  Beta_entry_div alone: {beta_je_alone:.4f}")
    print(f"  Beta_entry_div combined: {beta_je_combined:.4f}")
    print(f"  Shrinkage: {shrinkage:.4f}")

    # Partial correlation: entry_div vs AXM controlling for opener features + baseline
    Z_opener = np.column_stack(opener_features_raw)
    Z_all = np.hstack([X_base[:, 1:], Z_opener])  # drop intercept for partial corr
    rho_partial, p_partial = partial_corr_spearman(jsd_e, axm, Z_all)
    print(f"  Partial (entry_div vs AXM | baseline + opener): rho={rho_partial:.4f}, p={p_partial:.4f}")

    # Verdict
    if shrinkage > 0.50:
        verdict = 'OPENER_MEDIATES'
    elif shrinkage > 0.20:
        verdict = 'OPENER_PARTIAL_MEDIATION'
    else:
        verdict = 'OPENER_INDEPENDENT'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'baseline': {'r2': r2_base, 'loo': loo_base},
        'entry_only': {
            'dr2': dr2_entry, 'f_stat': f_entry, 'f_p': fp_entry,
            'loo': loo_entry, 'beta_entry_div': beta_je_alone,
        },
        'opener_only': {
            'dr2': dr2_opener, 'f_stat': f_opener, 'f_p': fp_opener,
            'loo': loo_opener,
        },
        'combined': {
            'r2': r2_combined, 'loo': loo_combined, 'dr2': dr2_combined,
            'beta_entry_div': beta_je_combined,
        },
        'coefficient_shrinkage': shrinkage,
        'partial_entry_div_vs_axm_ctrl_opener': {'rho': rho_partial, 'p': p_partial},
        'opener_features_used': opener_feature_names,
        'verdict': verdict,
    }


# ── Test 5: AXM_RESIDUAL_EXTENSION ──────────────────────────────

def test5_axm_residual_extension(opener_data, entry_div_data, folio_data):
    print("\n── Test 5: AXM_RESIDUAL_EXTENSION ──")

    folios = sorted(f for f in opener_data if f in entry_div_data)
    n = len(folios)

    jsd_e = np.array([entry_div_data[f]['jsd_entry'] for f in folios])
    axm = np.array([folio_data[f]['axm_self'] for f in folios])

    # Build entry model (baseline + entry_div)
    X_base, _ = build_baseline(folios, folio_data)
    je_z = standardize(jsd_e).reshape(-1, 1)
    X_entry_model = np.hstack([X_base, je_z])
    _, _, ss_entry_model, r2_entry_model = ols_fit(X_entry_model, axm)
    loo_entry_model = loo_cv_r2(X_entry_model, axm)

    print(f"  Entry model R²={r2_entry_model:.4f}, LOO={loo_entry_model:.4f}")

    # Opener features to test
    feature_specs = {
        'role_entropy': np.array([opener_data[f]['role_entropy'] for f in folios]),
        'init_spec_frac': np.array([opener_data[f]['init_spec_frac'] for f in folios]),
        'axm_return_rate': np.array([opener_data[f]['axm_return_rate'] for f in folios]),
        'opener_axm_frac': np.array([opener_data[f]['opener_axm_frac'] for f in folios]),
        'routing_concentration': np.array([opener_data[f]['routing_concentration'] for f in folios]),
    }

    # Add each feature one at a time to the entry model
    per_feature_results = {}
    best_feature = None
    best_dr2 = -999

    for fname, fvals in feature_specs.items():
        fvals_z = standardize(fvals).reshape(-1, 1)
        X_ext = np.hstack([X_entry_model, fvals_z])
        _, _, ss_ext, r2_ext = ols_fit(X_ext, axm)
        loo_ext = loo_cv_r2(X_ext, axm)
        dr2 = r2_ext - r2_entry_model
        f_stat, f_p = f_test_increment(ss_entry_model, ss_ext, 1, n, X_ext.shape[1])

        per_feature_results[fname] = {
            'dr2': dr2, 'f_stat': f_stat, 'f_p': f_p,
            'loo': loo_ext, 'loo_change': loo_ext - loo_entry_model,
        }
        print(f"  +{fname}: dR²={dr2:.4f}, F={f_stat:.2f}, p={f_p:.4f}, "
              f"LOO={loo_ext:.4f} (Δ={loo_ext - loo_entry_model:+.4f})")

        if dr2 > best_dr2:
            best_dr2 = dr2
            best_feature = fname

    # Joint model: add top 3 features
    top_features = sorted(feature_specs.keys(),
                         key=lambda f: per_feature_results[f]['dr2'], reverse=True)[:3]
    joint_z = [standardize(feature_specs[f]).reshape(-1, 1) for f in top_features]
    X_joint = np.hstack([X_entry_model] + joint_z)
    _, _, ss_joint, r2_joint = ols_fit(X_joint, axm)
    loo_joint = loo_cv_r2(X_joint, axm)
    dr2_joint = r2_joint - r2_entry_model
    f_joint, fp_joint = f_test_increment(ss_entry_model, ss_joint, len(top_features), n, X_joint.shape[1])

    print(f"  Joint top-3 ({', '.join(top_features)}): dR²={dr2_joint:.4f}, "
          f"F={f_joint:.2f}, p={fp_joint:.4f}, LOO={loo_joint:.4f}")

    # Total dR² of entry_div + opener bundle beyond C1035 baseline
    _, _, ss_base, r2_base = ols_fit(X_base, axm)
    total_dr2 = r2_joint - r2_base
    print(f"  Total dR² (entry_div + opener bundle vs C1035 baseline): {total_dr2:.4f}")

    # Verdict
    best_result = per_feature_results[best_feature]
    if best_result['dr2'] >= 0.03 and best_result['f_p'] < 0.05 and best_result['loo_change'] > 0:
        verdict = 'OPENER_EXTENDS_RESIDUAL'
    elif best_result['dr2'] >= 0.01 or (best_result['f_p'] < 0.10):
        verdict = 'OPENER_MARGINAL'
    else:
        verdict = 'OPENER_ABSORBED'
    print(f"  Best feature: {best_feature} (dR²={best_dr2:.4f})")
    print(f"  Verdict: {verdict}")

    return {
        'entry_model': {'r2': r2_entry_model, 'loo': loo_entry_model},
        'per_feature': per_feature_results,
        'best_feature': best_feature,
        'best_dr2': best_dr2,
        'joint_top3': {
            'features': top_features,
            'dr2': dr2_joint, 'f_stat': f_joint, 'f_p': fp_joint,
            'loo': loo_joint,
        },
        'total_dr2_vs_c1035': total_dr2,
        'c1035_baseline_r2': r2_base,
        'verdict': verdict,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 415: ENTRY_RESET_MECHANISM")
    print("=" * 60)

    folio_line_lists, folio_data, valid_folios, class_to_role = load_data()

    # Compute per-folio entry divergence (replicating Phase 414 T1)
    entry_div_data = compute_folio_entry_divergence(folio_line_lists, folio_data, valid_folios)
    print(f"\n  Folios with entry divergence: {len(entry_div_data)}")
    jsd_vals = [entry_div_data[f]['jsd_entry'] for f in entry_div_data]
    print(f"  Entry JSD mean={np.mean(jsd_vals):.4f}, std={np.std(jsd_vals):.4f}")

    # Compute per-folio opener properties
    opener_data = compute_opener_properties(folio_line_lists, valid_folios)
    print(f"  Folios with opener properties: {len(opener_data)}")

    # Aligned folio set
    common_folios = sorted(f for f in opener_data if f in entry_div_data and f in folio_data)
    print(f"  Common folios for analysis: {len(common_folios)}")

    t1 = test1_opener_role_distribution(opener_data, entry_div_data, folio_data)
    t2 = test2_prefix_family_distribution(opener_data, entry_div_data, folio_data)
    t3 = test3_opener_follower_routing(opener_data, entry_div_data, folio_data,
                                        folio_line_lists, valid_folios)
    t4 = test4_entry_divergence_mediation(opener_data, entry_div_data, folio_data)
    t5 = test5_axm_residual_extension(opener_data, entry_div_data, folio_data)

    # Synthesis
    t4v = t4['verdict']
    t5v = t5['verdict']

    synthesis_map = {
        ('OPENER_MEDIATES', 'OPENER_ABSORBED'): 'ENTRY_DIVERGENCE_IS_OPENER_COMPOSITION',
        ('OPENER_MEDIATES', 'OPENER_EXTENDS_RESIDUAL'): 'OPENER_IS_PRIMARY_WITH_EXTENSION',
        ('OPENER_MEDIATES', 'OPENER_MARGINAL'): 'OPENER_IS_PRIMARY_WITH_EXTENSION',
        ('OPENER_PARTIAL_MEDIATION', 'OPENER_EXTENDS_RESIDUAL'): 'MULTI_FACETED_ENTRY_MECHANISM',
        ('OPENER_PARTIAL_MEDIATION', 'OPENER_MARGINAL'): 'PARTIAL_DECOMPOSITION_NO_EXTENSION',
        ('OPENER_PARTIAL_MEDIATION', 'OPENER_ABSORBED'): 'PARTIAL_DECOMPOSITION_NO_EXTENSION',
        ('OPENER_INDEPENDENT', 'OPENER_EXTENDS_RESIDUAL'): 'INDEPENDENT_ENTRY_PLUS_OPENER',
        ('OPENER_INDEPENDENT', 'OPENER_MARGINAL'): 'ENTRY_DIVERGENCE_IRREDUCIBLE',
        ('OPENER_INDEPENDENT', 'OPENER_ABSORBED'): 'ENTRY_DIVERGENCE_IRREDUCIBLE',
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
        'phase': 'ENTRY_RESET_MECHANISM',
        'phase_number': 415,
        'depends_on': ['C1035', 'C1156', 'C1157', 'C1158', 'C1159',
                       'C958', 'C959', 'C1001', 'C931', 'C556', 'C557'],
        'n_folios': len(common_folios),
        'test1_opener_role_distribution': t1,
        'test2_prefix_family_distribution': t2,
        'test3_opener_follower_routing': t3,
        'test4_entry_divergence_mediation': t4,
        'test5_axm_residual_extension': t5,
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
    out_path = RESULTS_DIR / 'entry_reset_mechanism.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
