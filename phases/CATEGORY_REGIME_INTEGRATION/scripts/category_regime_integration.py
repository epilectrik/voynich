#!/usr/bin/env python3
"""Phase 456: CATEGORY_REGIME_INTEGRATION

7-test battery + 1 calibration probing whether the 8-category operational system
(C1250) integrates with the 4-REGIME classification (C179, C494).

Key risk: circularity. REGIMEs are defined from 15 folio features including
k_ratio, h_ratio, e_ratio. Categories are defined from atoms including k, h, e.
T3 (circularity decomposition) is the CRITICAL gate.

Tests:
  T1: Category x REGIME Contingency (chi-squared on 4x8 table)
  T2: Per-REGIME Category Centroid Signatures (JSD + permutation)
  T3: Circularity Decomposition (kernel residualization -- CRITICAL)
  T4: Section-Controlled Category-REGIME Association
  T5: Category Resolution Beyond C545 Class-Level Profiles
  T6: Category Fractions vs C1169 Residuals (univariate Spearman screen)
  T7: AXM Regression Extension (gated on T6)
  T8: REGIME Feature x Category Correlation (calibration, not scored)
"""

import json
import sys
import time
import functools
from pathlib import Path
from collections import Counter, defaultdict
from math import log2, sqrt, lgamma, exp, log

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ============================================================
# Constants
# ============================================================

N_PERM = 1000
SEED = 42
N_SCORED_TESTS = 7
BONFERRONI_P = 0.05 / N_SCORED_TESTS  # 0.00714

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
N_CATS = len(CATEGORIES)

ROLES = ['AUXILIARY', 'CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR',
         'FREQUENT_OPERATOR']
ROLE_IDX = {r: i for i, r in enumerate(ROLES)}

REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
REG_IDX = {r: i for i, r in enumerate(REGIMES)}
N_REGS = len(REGIMES)

# --- Category assignment (from Phase 452) ---
GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'halt': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {a: GLOSS_TO_CATEGORY[g] for a, g in ATOM_GLOSSES.items()}

# Kernel atoms (for circularity check)
KERNEL_ATOMS = {'k', 'h', 'e'}

# --- 6-state macro partition (C1010) ---
MACRO_STATE_PARTITION = {
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28,
                29, 31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 45, 46, 47, 48, 49},
    'AXm':     {3, 5, 18, 19, 42},
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'FL_SAFE': {38, 40},
}
STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
N_STATES = len(STATE_ORDER)
N_CLASSES = 49

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

MIN_ZONE_TRANS = 10
MIN_CLOSERS = 10


# ============================================================
# Utilities
# ============================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def auto_assign_category(atoms_str):
    """Assign category via plurality vote over atoms."""
    if not atoms_str:
        return None
    votes = Counter()
    for atom in atoms_str:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    return sorted(winners)[0]


def build_category_map():
    """Build mid_to_category dict from middle_dictionary.json."""
    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]
    for mid, minfo in mid_dict.items():
        if mid in mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat = auto_assign_category(atoms_str)
            if cat:
                mid_to_cat[mid] = cat
    return mid_to_cat


def entropy_bits(counts):
    """Shannon entropy in bits."""
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * log2(p)
    return h


def shannon_entropy(probs):
    return -sum(p * log2(p) for p in probs if p > 0)


def cramers_v(table):
    """Cramer's V from numpy contingency table."""
    n = table.sum()
    if n == 0:
        return 0.0
    chi2 = stats.chi2_contingency(table)[0]
    k = min(table.shape) - 1
    if k == 0:
        return 0.0
    return float(np.sqrt(chi2 / (n * k)))


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    ps = p.sum()
    qs = q.sum()
    if ps == 0 or qs == 0:
        return 1.0
    p = p / ps
    q = q / qs
    m = 0.5 * (p + q)
    d = 0.0
    for i in range(len(p)):
        if p[i] > 0 and m[i] > 0:
            d += 0.5 * p[i] * log2(p[i] / m[i])
        if q[i] > 0 and m[i] > 0:
            d += 0.5 * q[i] * log2(q[i] / m[i])
    return d


def verdict(p, effect=None, bonferroni=BONFERRONI_P, min_effect=None):
    """Return PASS/FAIL/WEAK verdict."""
    if p < bonferroni:
        return 'PASS'
    elif p < 0.05:
        return 'WEAK'
    return 'FAIL'


# --- OLS utilities (from residual_freedom_characterization.py) ---

def standardize(x):
    arr = np.array(x, dtype=float)
    return (arr - arr.mean()) / (arr.std() + 1e-10)


def ols_fit(X, y):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, y_pred, ss_res, r2


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


def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    df_res = n_obs - k_full
    if df_res <= 0 or ss_res_full <= 0:
        return 0.0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


# --- Matrix utilities for boundary computation ---

def build_zone_matrix(transitions, n_classes=N_CLASSES):
    m = np.zeros((n_classes, n_classes))
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


def compute_jsd_flat(p, q, epsilon=1e-10):
    """JSD between two flat arrays (for transition matrices)."""
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m_arr = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m_arr)) + 0.5 * np.sum(q * np.log2(q / m_arr)))


# ============================================================
# Data Loading
# ============================================================

def load_data():
    print("Loading data...")
    t0 = time.time()

    # Category map
    mid_to_cat = build_category_map()

    # Token-to-class map
    with open(ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' /
              'class_token_map.json', encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']
    class_to_role = cmap['class_to_role']

    # REGIME assignments
    with open(ROOT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_data = json.load(f)
    regime_assignments = regime_data['regime_assignments']

    # AXM model data (folio_data from Phase 357)
    with open(ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_json = json.load(f)
    folio_data = axm_json['folio_data']

    morph = Morphology()

    # Build per-folio data structures in single pass
    folio_tokens = defaultdict(list)    # folio -> list of token dicts
    folio_lines = defaultdict(lambda: defaultdict(list))  # folio -> line -> [tokens]

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        cls_str = token_to_class.get(w)
        if cls_str is None:
            continue
        cls = int(cls_str)
        m = morph.extract(w)
        middle = m.middle if m else None
        prefix = m.prefix if m else None
        cat = mid_to_cat.get(middle) if middle else None

        tok_data = {
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'cls': cls,
            'state': CLASS_TO_STATE.get(cls, 'AXM'),
            'role': class_to_role.get(str(cls), 'UNKNOWN'),
            'middle': middle,
            'prefix': prefix,
            'category': cat,
        }
        folio_tokens[t.folio].append(tok_data)
        folio_lines[t.folio][t.line].append(tok_data)

    # Compute per-folio category composition
    folio_cat_counts = {}
    folio_cat_fracs = {}
    for folio, tokens in folio_tokens.items():
        counts = Counter()
        for tok in tokens:
            if tok['category']:
                counts[tok['category']] += 1
        if sum(counts.values()) > 0:
            folio_cat_counts[folio] = counts
            total = sum(counts.values())
            folio_cat_fracs[folio] = {c: counts.get(c, 0) / total for c in CATEGORIES}

    # Compute per-folio role composition
    folio_role_counts = {}
    folio_role_fracs = {}
    for folio, tokens in folio_tokens.items():
        counts = Counter()
        for tok in tokens:
            r = tok['role']
            if r in ROLE_IDX:
                counts[r] += 1
        total = sum(counts.values())
        if total > 0:
            folio_role_counts[folio] = counts
            folio_role_fracs[folio] = {r: counts.get(r, 0) / total for r in ROLES}

    # Compute per-folio kernel fractions (k, h, e atom prevalence in MIDDLEs)
    folio_kernel_fracs = {}
    for folio, tokens in folio_tokens.items():
        n_tok = 0
        k_count = 0
        h_count = 0
        e_count = 0
        for tok in tokens:
            mid = tok['middle']
            if not mid:
                continue
            n_tok += 1
            if 'k' in mid:
                k_count += 1
            if 'h' in mid:
                h_count += 1
            if 'e' in mid:
                e_count += 1
        if n_tok > 0:
            folio_kernel_fracs[folio] = {
                'k_frac': k_count / n_tok,
                'h_frac': h_count / n_tok,
                'e_frac': e_count / n_tok,
            }

    # Assign REGIMEs to folios
    folio_regime = {}
    for folio in folio_tokens:
        if folio in regime_assignments:
            folio_regime[folio] = regime_assignments[folio]['regime']

    # Get section labels from folio_data
    folio_section = {}
    for folio in folio_tokens:
        if folio in folio_data:
            folio_section[folio] = folio_data[folio]['section']

    # Valid folios: have category, regime, and section data
    valid_folios = sorted(
        f for f in folio_tokens
        if f in folio_cat_fracs and f in folio_regime and f in folio_section
    )

    # Build folio line lists for boundary computation
    folio_line_lists = defaultdict(list)
    for folio in valid_folios:
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    elapsed = time.time() - t0
    print(f"  Loaded {len(folio_tokens)} folios, {sum(len(v) for v in folio_tokens.values())} tokens")
    print(f"  Categorized: {len(folio_cat_fracs)} folios with category data")
    print(f"  REGIME-assigned: {len(folio_regime)} folios")
    print(f"  Valid (cat+regime+section): {len(valid_folios)} folios")
    print(f"  Time: {elapsed:.1f}s")

    return {
        'folio_tokens': folio_tokens,
        'folio_lines': folio_lines,
        'folio_line_lists': folio_line_lists,
        'folio_cat_counts': folio_cat_counts,
        'folio_cat_fracs': folio_cat_fracs,
        'folio_role_counts': folio_role_counts,
        'folio_role_fracs': folio_role_fracs,
        'folio_kernel_fracs': folio_kernel_fracs,
        'folio_regime': folio_regime,
        'folio_section': folio_section,
        'folio_data': folio_data,
        'valid_folios': valid_folios,
        'class_to_role': class_to_role,
    }


# ============================================================
# Boundary data computation (replicated from residual_freedom_characterization.py)
# ============================================================

def compute_folio_divergence(folio_line_lists, valid_folios):
    """Compute per-folio entry AND exit divergence vs interior."""
    results = {}
    for folio in valid_folios:
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
        jsd_entry = compute_jsd_flat(m6_entry.flatten(), m6_interior.flatten())
        jsd_exit = compute_jsd_flat(m6_exit.flatten(), m6_interior.flatten())
        results[folio] = {'jsd_entry': jsd_entry, 'jsd_exit': jsd_exit}
    return results


def compute_boundary_properties(folio_line_lists, valid_folios):
    """Extract per-folio opener AND closer properties."""
    results = {}
    for folio in valid_folios:
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]
        opener_states = []
        entry_transitions = []
        exit_transitions = []
        exit_total = 0

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
            exit_total += 1

        if exit_total < MIN_CLOSERS:
            continue

        # AXM return rate
        axm_returns = sum(1 for _, tgt in entry_transitions if tgt == 'AXM')
        axm_return_rate = axm_returns / len(entry_transitions) if entry_transitions else 0

        # AXM departure rate
        axm_exits = sum(1 for src, tgt in exit_transitions if src == 'AXM' and tgt != 'AXM')
        axm_sources = sum(1 for src, _ in exit_transitions if src == 'AXM')
        axm_departure_rate = axm_exits / max(axm_sources, 1)

        results[folio] = {
            'axm_return_rate': axm_return_rate,
            'axm_departure_rate': axm_departure_rate,
        }
    return results


# ============================================================
# T1: Category x REGIME Contingency
# ============================================================

def test_t1(data):
    print("\n=== T1: Category x REGIME Contingency ===")
    valid = data['valid_folios']
    cat_counts = data['folio_cat_counts']
    regime = data['folio_regime']

    # Build 4x8 contingency table (token counts pooled per REGIME)
    table = np.zeros((N_REGS, N_CATS), dtype=float)
    for folio in valid:
        r = regime[folio]
        ri = REG_IDX[r]
        counts = cat_counts.get(folio, {})
        for cat, cnt in counts.items():
            ci = CAT_IDX[cat]
            table[ri, ci] += cnt

    total_tokens = table.sum()
    chi2, p, dof, expected = stats.chi2_contingency(table)
    v = cramers_v(table)

    # Per-REGIME category centroids
    centroids = {}
    for ri, reg in enumerate(REGIMES):
        row_total = table[ri].sum()
        if row_total > 0:
            centroids[reg] = {CATEGORIES[ci]: float(table[ri, ci] / row_total)
                              for ci in range(N_CATS)}

    v_str = verdict(p, v)
    print(f"  Contingency: chi2={chi2:.1f}, p={p:.2e}, dof={dof}, V={v:.4f}")
    print(f"  Total tokens: {int(total_tokens)}")
    print(f"  Verdict: {v_str}")
    for reg in REGIMES:
        top = sorted(centroids.get(reg, {}).items(), key=lambda x: -x[1])[:3]
        top_str = ', '.join(f"{c}={v:.1%}" for c, v in top)
        print(f"    {reg}: {top_str}")

    return {
        'test': 'T1_category_regime_contingency',
        'chi2': float(chi2),
        'p': float(p),
        'dof': int(dof),
        'cramers_v': float(v),
        'total_tokens': int(total_tokens),
        'centroids': centroids,
        'verdict': v_str,
    }


# ============================================================
# T2: Per-REGIME Category Centroid Signatures
# ============================================================

def test_t2(data):
    print("\n=== T2: Per-REGIME Category Centroid Signatures ===")
    valid = data['valid_folios']
    cat_fracs = data['folio_cat_fracs']
    regime = data['folio_regime']

    # Group folios by REGIME
    regime_folios = defaultdict(list)
    for f in valid:
        regime_folios[regime[f]].append(f)

    # Compute per-REGIME mean category vector
    def regime_centroid(reg):
        folios = regime_folios[reg]
        vecs = np.array([[cat_fracs[f].get(c, 0) for c in CATEGORIES] for f in folios])
        return vecs.mean(axis=0)

    centroids = {reg: regime_centroid(reg) for reg in REGIMES if regime_folios[reg]}

    # Mean pairwise JSD across regime centroids
    pairs = []
    for i, r1 in enumerate(REGIMES):
        for r2 in REGIMES[i+1:]:
            if r1 in centroids and r2 in centroids:
                pairs.append((r1, r2, jsd(centroids[r1], centroids[r2])))
    observed_mean_jsd = np.mean([p[2] for p in pairs]) if pairs else 0.0

    # Permutation null
    rng = np.random.RandomState(SEED)
    folio_list = list(valid)
    regime_list = [regime[f] for f in folio_list]
    null_jsds = []
    for _ in range(N_PERM):
        perm = rng.permutation(regime_list)
        perm_regime = {folio_list[i]: perm[i] for i in range(len(folio_list))}
        perm_regime_folios = defaultdict(list)
        for f in folio_list:
            perm_regime_folios[perm_regime[f]].append(f)
        perm_centroids = {}
        for reg in REGIMES:
            if perm_regime_folios[reg]:
                vecs = np.array([[cat_fracs[f].get(c, 0) for c in CATEGORIES]
                                 for f in perm_regime_folios[reg]])
                perm_centroids[reg] = vecs.mean(axis=0)
        perm_pairs = []
        for i, r1 in enumerate(REGIMES):
            for r2 in REGIMES[i+1:]:
                if r1 in perm_centroids and r2 in perm_centroids:
                    perm_pairs.append(jsd(perm_centroids[r1], perm_centroids[r2]))
        null_jsds.append(np.mean(perm_pairs) if perm_pairs else 0.0)

    null_mean = np.mean(null_jsds)
    null_std = np.std(null_jsds)
    z = (observed_mean_jsd - null_mean) / (null_std + 1e-10)
    # Convert z to p-value (one-tailed, observed > null)
    p_val = 1 - stats.norm.cdf(z)

    v_str = verdict(p_val)
    print(f"  Observed mean JSD: {observed_mean_jsd:.6f}")
    print(f"  Null mean: {null_mean:.6f}, std: {null_std:.6f}")
    print(f"  z={z:.2f}, p={p_val:.2e}")
    print(f"  Verdict: {v_str}")

    # Which categories drive discrimination
    overall_centroid = np.mean([centroids[r] for r in REGIMES if r in centroids], axis=0)
    drivers = {}
    for reg in REGIMES:
        if reg in centroids:
            delta = centroids[reg] - overall_centroid
            drivers[reg] = {CATEGORIES[i]: float(delta[i]) for i in range(N_CATS)}

    for reg in REGIMES:
        if reg in drivers:
            top_pos = sorted([(c, d) for c, d in drivers[reg].items() if d > 0.005],
                             key=lambda x: -x[1])[:2]
            top_neg = sorted([(c, d) for c, d in drivers[reg].items() if d < -0.005],
                             key=lambda x: x[1])[:2]
            pos_str = ', '.join(f"+{c}={d:+.3f}" for c, d in top_pos) if top_pos else 'none'
            neg_str = ', '.join(f"-{c}={d:+.3f}" for c, d in top_neg) if top_neg else 'none'
            print(f"    {reg}: UP=[{pos_str}], DOWN=[{neg_str}]")

    return {
        'test': 'T2_regime_centroid_signatures',
        'observed_mean_jsd': float(observed_mean_jsd),
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z': float(z),
        'p': float(p_val),
        'pairwise_jsd': {f"{r1}-{r2}": float(d) for r1, r2, d in pairs},
        'drivers': drivers,
        'verdict': v_str,
    }


# ============================================================
# T3: Circularity Decomposition (CRITICAL)
# ============================================================

def test_t3(data):
    print("\n=== T3: Circularity Decomposition (CRITICAL) ===")
    valid = data['valid_folios']
    cat_fracs = data['folio_cat_fracs']
    kernel_fracs = data['folio_kernel_fracs']
    regime = data['folio_regime']

    # Get folios with kernel data
    folios_with_kernel = [f for f in valid if f in kernel_fracs]
    n = len(folios_with_kernel)
    print(f"  Folios with kernel data: {n}")

    if n < 20:
        print("  SKIP: insufficient folios with kernel data")
        return {'test': 'T3_circularity_decomposition', 'verdict': 'SKIP', 'reason': 'n<20'}

    # Build kernel matrix (n x 3)
    K = np.array([[kernel_fracs[f]['k_frac'], kernel_fracs[f]['h_frac'],
                    kernel_fracs[f]['e_frac']] for f in folios_with_kernel])

    # Residualize each category fraction on kernel composition
    residualized = {}  # cat -> array of residuals
    r2_kernel = {}  # cat -> R2 from kernel regression (shows circularity)
    for cat in CATEGORIES:
        y = np.array([cat_fracs[f].get(cat, 0) for f in folios_with_kernel])
        # OLS: category_frac ~ intercept + k_frac + h_frac + e_frac
        X = np.column_stack([np.ones(n), K])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        y_pred = X @ beta
        resid = y - y_pred
        ss_res = np.sum(resid ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        residualized[cat] = resid
        r2_kernel[cat] = float(r2)

    print("  Kernel R2 per category (circularity diagnostic):")
    for cat in CATEGORIES:
        flag = " ** CIRCULAR" if r2_kernel[cat] > 0.3 else ""
        print(f"    {cat}: R2={r2_kernel[cat]:.3f}{flag}")

    # Build residualized contingency: discretize residuals into above/below median
    # Use 4x(N_CATS) table: REGIME x category-residual-bin
    # For each category: above-median = 1, below-median = 0
    resid_table = np.zeros((N_REGS, N_CATS), dtype=float)
    for fi, folio in enumerate(folios_with_kernel):
        ri = REG_IDX[regime[folio]]
        for ci, cat in enumerate(CATEGORIES):
            resid_table[ri, ci] += residualized[cat][fi]

    # Build a proper contingency: per REGIME, count folios above/below median
    # for each category. Then test overall association.
    # Better approach: MANOVA-like -- test if REGIME predicts residualized category vector
    # Use chi-squared on discretized 4x(2*8) table
    medians = {cat: np.median(residualized[cat]) for cat in CATEGORIES}
    # Build binary feature vector per folio: for each category, 1 if above median
    folio_binary = {}
    for fi, folio in enumerate(folios_with_kernel):
        bits = tuple(1 if residualized[cat][fi] > medians[cat] else 0
                     for cat in CATEGORIES)
        folio_binary[folio] = bits

    # Test: for each category separately, is the above-median rate different by REGIME?
    cat_chi2_results = {}
    total_chi2 = 0.0
    total_dof = 0
    for ci, cat in enumerate(CATEGORIES):
        # 4x2 table: REGIME x (above, below median)
        sub_table = np.zeros((N_REGS, 2), dtype=float)
        for fi, folio in enumerate(folios_with_kernel):
            ri = REG_IDX[regime[folio]]
            above = 1 if residualized[cat][fi] > medians[cat] else 0
            sub_table[ri, above] += 1
        # Remove empty rows
        mask = sub_table.sum(axis=1) > 0
        if mask.sum() < 2:
            continue
        sub_table_clean = sub_table[mask]
        if sub_table_clean.min() == 0:
            # Add small constant for stability
            sub_table_clean = sub_table_clean + 0.5
        try:
            chi2_cat, p_cat, dof_cat, _ = stats.chi2_contingency(sub_table_clean)
            total_chi2 += chi2_cat
            total_dof += dof_cat
            cat_chi2_results[cat] = {'chi2': float(chi2_cat), 'p': float(p_cat), 'dof': int(dof_cat)}
        except ValueError:
            pass

    # Combined test
    if total_dof > 0:
        combined_p = 1 - stats.chi2.cdf(total_chi2, total_dof)
    else:
        combined_p = 1.0

    # Also: ANOVA-like test using Kruskal-Wallis on each residualized category
    kw_results = {}
    kw_significant = 0
    kw_total = 0
    for cat in CATEGORIES:
        groups = defaultdict(list)
        for fi, folio in enumerate(folios_with_kernel):
            groups[regime[folio]].append(residualized[cat][fi])
        group_list = [v for v in groups.values() if len(v) >= 3]
        if len(group_list) >= 2:
            kw_h, kw_p = stats.kruskal(*group_list)
            kw_results[cat] = {'H': float(kw_h), 'p': float(kw_p)}
            kw_total += 1
            if kw_p < 0.05:  # nominal
                kw_significant += 1

    # Combined KW: use Fisher's method
    kw_ps = [kw_results[cat]['p'] for cat in CATEGORIES if cat in kw_results]
    if kw_ps:
        fisher_stat = -2 * sum(log(max(p, 1e-300)) for p in kw_ps)
        fisher_dof = 2 * len(kw_ps)
        fisher_p = 1 - stats.chi2.cdf(fisher_stat, fisher_dof)
    else:
        fisher_p = 1.0
        fisher_stat = 0.0
        fisher_dof = 0

    v_str = verdict(fisher_p)
    print(f"  Combined chi2 (discretized): chi2={total_chi2:.1f}, dof={total_dof}, p={combined_p:.2e}")
    print(f"  Fisher combined KW: stat={fisher_stat:.1f}, dof={fisher_dof}, p={fisher_p:.2e}")
    print(f"  KW individually significant (nominal): {kw_significant}/{kw_total}")
    print(f"  Verdict: {v_str}")
    for cat in CATEGORIES:
        if cat in kw_results:
            sig = "*" if kw_results[cat]['p'] < 0.05 else ""
            print(f"    {cat}: KW H={kw_results[cat]['H']:.2f}, p={kw_results[cat]['p']:.4f} "
                  f"(kernel R2={r2_kernel[cat]:.3f}){sig}")

    return {
        'test': 'T3_circularity_decomposition',
        'n_folios': n,
        'r2_kernel': r2_kernel,
        'combined_chi2': float(total_chi2),
        'combined_dof': int(total_dof),
        'combined_p': float(combined_p),
        'fisher_stat': float(fisher_stat),
        'fisher_dof': int(fisher_dof),
        'fisher_p': float(fisher_p),
        'kw_results': kw_results,
        'kw_significant': kw_significant,
        'kw_total': kw_total,
        'cat_chi2_results': cat_chi2_results,
        'verdict': v_str,
    }


# ============================================================
# T4: Section-Controlled Category-REGIME Association
# ============================================================

def test_t4(data):
    print("\n=== T4: Section-Controlled Category-REGIME Association ===")
    valid = data['valid_folios']
    cat_counts = data['folio_cat_counts']
    regime = data['folio_regime']
    section = data['folio_section']

    sections = sorted(set(section[f] for f in valid))
    total_chi2 = 0.0
    total_dof = 0
    section_results = {}

    for sec in sections:
        sec_folios = [f for f in valid if section[f] == sec]
        if len(sec_folios) < 5:
            continue
        # Build 4x8 table for this section
        # Only include REGIMEs present in this section
        sec_regimes = sorted(set(regime[f] for f in sec_folios))
        if len(sec_regimes) < 2:
            continue
        table = np.zeros((len(sec_regimes), N_CATS), dtype=float)
        reg_map = {r: i for i, r in enumerate(sec_regimes)}
        for folio in sec_folios:
            ri = reg_map[regime[folio]]
            counts = cat_counts.get(folio, {})
            for cat, cnt in counts.items():
                ci = CAT_IDX[cat]
                table[ri, ci] += cnt
        # Remove zero columns
        col_sums = table.sum(axis=0)
        nonzero = col_sums > 0
        if nonzero.sum() < 2:
            continue
        table_clean = table[:, nonzero]
        # Remove rows with zero total
        row_sums = table_clean.sum(axis=1)
        nonzero_rows = row_sums > 0
        if nonzero_rows.sum() < 2:
            continue
        table_clean = table_clean[nonzero_rows]
        try:
            chi2, p, dof, _ = stats.chi2_contingency(table_clean)
            total_chi2 += chi2
            total_dof += dof
            section_results[sec] = {
                'n_folios': len(sec_folios),
                'n_regimes': len(sec_regimes),
                'chi2': float(chi2),
                'p': float(p),
                'dof': int(dof),
            }
        except ValueError:
            pass

    if total_dof > 0:
        combined_p = 1 - stats.chi2.cdf(total_chi2, total_dof)
    else:
        combined_p = 1.0

    v_str = verdict(combined_p)
    print(f"  Sections tested: {len(section_results)}")
    for sec in sorted(section_results.keys()):
        sr = section_results[sec]
        sig = "*" if sr['p'] < 0.05 else ""
        print(f"    Section {sec}: {sr['n_folios']} folios, {sr['n_regimes']} REGIMEs, "
              f"chi2={sr['chi2']:.1f}, p={sr['p']:.3f}{sig}")
    print(f"  Combined: chi2={total_chi2:.1f}, dof={total_dof}, p={combined_p:.2e}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T4_section_controlled_association',
        'section_results': section_results,
        'combined_chi2': float(total_chi2),
        'combined_dof': int(total_dof),
        'combined_p': float(combined_p),
        'verdict': v_str,
    }


# ============================================================
# T5: Category Resolution Beyond C545 Class-Level Profiles
# ============================================================

def test_t5(data):
    print("\n=== T5: Category Resolution Beyond C545 Class-Level Profiles ===")
    valid = data['valid_folios']
    cat_fracs = data['folio_cat_fracs']
    role_fracs = data['folio_role_fracs']
    regime = data['folio_regime']

    # For each REGIME pair: compute JSD on role vectors vs category vectors
    regime_folios = defaultdict(list)
    for f in valid:
        regime_folios[regime[f]].append(f)

    pair_results = {}
    for i, r1 in enumerate(REGIMES):
        for r2 in REGIMES[i+1:]:
            if not regime_folios[r1] or not regime_folios[r2]:
                continue
            # Role centroids
            role_c1 = np.mean([[role_fracs[f].get(r, 0) for r in ROLES]
                               for f in regime_folios[r1]], axis=0)
            role_c2 = np.mean([[role_fracs[f].get(r, 0) for r in ROLES]
                               for f in regime_folios[r2]], axis=0)
            jsd_role = jsd(role_c1, role_c2)
            # Category centroids
            cat_c1 = np.mean([[cat_fracs[f].get(c, 0) for c in CATEGORIES]
                              for f in regime_folios[r1]], axis=0)
            cat_c2 = np.mean([[cat_fracs[f].get(c, 0) for c in CATEGORIES]
                              for f in regime_folios[r2]], axis=0)
            jsd_cat = jsd(cat_c1, cat_c2)
            pair_results[f"{r1}-{r2}"] = {
                'jsd_role': float(jsd_role),
                'jsd_cat': float(jsd_cat),
                'cat_exceeds_role': jsd_cat > jsd_role,
            }

    cat_exceeds = sum(1 for v in pair_results.values() if v['cat_exceeds_role'])
    total_pairs = len(pair_results)
    mean_jsd_role = np.mean([v['jsd_role'] for v in pair_results.values()])
    mean_jsd_cat = np.mean([v['jsd_cat'] for v in pair_results.values()])

    # Partial correlation: category-REGIME controlling for role
    # Build category dummy vector (above/below median for top 2 discriminating categories)
    # Use a simpler approach: multinomial logistic-like
    # Actually: test if adding category fracs to role fracs improves REGIME prediction
    # Use a chi-squared approach: compare full model (role+cat) vs reduced (role only)
    # Build feature matrix for each folio: [role_fracs, cat_fracs]
    n = len(valid)
    Y_regime = [regime[f] for f in valid]

    # Role-only prediction: MANOVA on role fracs x REGIME
    role_matrix = np.array([[role_fracs[f].get(r, 0) for r in ROLES] for f in valid])
    cat_matrix = np.array([[cat_fracs[f].get(c, 0) for c in CATEGORIES] for f in valid])

    # Test: does category add information beyond role?
    # Use Kruskal-Wallis on each category fraction, controlling for role composition
    # Simple approach: residualize category fracs on role fracs, then test REGIME association
    role_X = np.column_stack([np.ones(n), role_matrix])
    cat_resid_on_role = {}
    for ci, cat in enumerate(CATEGORIES):
        y = cat_matrix[:, ci]
        beta = np.linalg.lstsq(role_X, y, rcond=None)[0]
        resid = y - role_X @ beta
        cat_resid_on_role[cat] = resid

    # KW test on residualized category fractions by REGIME
    kw_sig = 0
    kw_total = 0
    kw_details = {}
    for cat in CATEGORIES:
        groups = defaultdict(list)
        for fi, f in enumerate(valid):
            groups[regime[f]].append(cat_resid_on_role[cat][fi])
        group_list = [v for v in groups.values() if len(v) >= 3]
        if len(group_list) >= 2:
            h, p = stats.kruskal(*group_list)
            kw_details[cat] = {'H': float(h), 'p': float(p)}
            kw_total += 1
            if p < 0.05:
                kw_sig += 1

    # Fisher combination
    kw_ps = [kw_details[cat]['p'] for cat in CATEGORIES if cat in kw_details]
    if kw_ps:
        fisher_stat = -2 * sum(log(max(p, 1e-300)) for p in kw_ps)
        fisher_dof = 2 * len(kw_ps)
        fisher_p = 1 - stats.chi2.cdf(fisher_stat, fisher_dof)
    else:
        fisher_p = 1.0
        fisher_stat = 0.0
        fisher_dof = 0

    v_str = verdict(fisher_p)
    print(f"  Mean JSD: role={mean_jsd_role:.6f}, category={mean_jsd_cat:.6f}")
    print(f"  Category exceeds role: {cat_exceeds}/{total_pairs} pairs")
    print(f"  Role-residualized category KW: {kw_sig}/{kw_total} significant (nominal)")
    print(f"  Fisher combined: stat={fisher_stat:.1f}, dof={fisher_dof}, p={fisher_p:.2e}")
    print(f"  Verdict: {v_str}")
    for pair, vals in sorted(pair_results.items()):
        marker = "CAT>" if vals['cat_exceeds_role'] else "ROLE>"
        print(f"    {pair}: role={vals['jsd_role']:.6f}, cat={vals['jsd_cat']:.6f} [{marker}]")

    return {
        'test': 'T5_category_beyond_class_profiles',
        'pair_results': pair_results,
        'cat_exceeds_count': cat_exceeds,
        'total_pairs': total_pairs,
        'mean_jsd_role': float(mean_jsd_role),
        'mean_jsd_cat': float(mean_jsd_cat),
        'kw_role_residualized': kw_details,
        'kw_sig': kw_sig,
        'kw_total': kw_total,
        'fisher_stat': float(fisher_stat),
        'fisher_dof': int(fisher_dof),
        'fisher_p': float(fisher_p),
        'verdict': v_str,
    }


# ============================================================
# T6: Category Fractions vs C1169 Residuals
# ============================================================

def test_t6(data):
    print("\n=== T6: Category Fractions vs C1169 Residuals ===")
    valid = data['valid_folios']
    cat_fracs = data['folio_cat_fracs']
    folio_data = data['folio_data']
    folio_line_lists = data['folio_line_lists']

    # Compute boundary data
    print("  Computing divergence data...")
    div_data = compute_folio_divergence(folio_line_lists, valid)
    print("  Computing boundary properties...")
    boundary_data = compute_boundary_properties(folio_line_lists, valid)

    # Get folios with complete data (folio_data + div_data + boundary_data + cat_fracs)
    complete_folios = [f for f in valid
                       if f in folio_data
                       and f in div_data
                       and f in boundary_data
                       and f in cat_fracs]
    n = len(complete_folios)
    print(f"  Complete folios for AXM model: {n}")

    if n < 30:
        print("  SKIP: insufficient complete folios")
        return {'test': 'T6_category_vs_residuals', 'verdict': 'SKIP', 'reason': f'n={n}<30'}

    # Build C1169 dual-boundary model
    axm_self = np.array([folio_data[f]['axm_self'] for f in complete_folios])
    regimes_list = [folio_data[f]['regime'] for f in complete_folios]
    sections_list = [folio_data[f]['section'] for f in complete_folios]
    pfx = np.array([folio_data[f]['prefix_entropy'] for f in complete_folios])
    haz = np.array([folio_data[f]['hazard_density'] for f in complete_folios])
    pc1 = np.array([folio_data[f]['bridge_pc1'] for f in complete_folios])

    intercept = np.ones((n, 1))
    regime_dum = build_dummies(regimes_list)
    section_dum = build_dummies(sections_list)
    pfx_z = standardize(pfx).reshape(-1, 1)
    haz_z = standardize(haz).reshape(-1, 1)
    pc1_z = standardize(pc1).reshape(-1, 1)

    X_base = np.hstack([intercept, regime_dum, section_dum, pfx_z, haz_z, pc1_z])

    # Add boundary terms
    jsd_entry = np.array([div_data[f]['jsd_entry'] for f in complete_folios])
    axm_return = np.array([boundary_data[f]['axm_return_rate'] for f in complete_folios])
    jsd_exit = np.array([div_data[f]['jsd_exit'] for f in complete_folios])
    axm_departure = np.array([boundary_data[f]['axm_departure_rate'] for f in complete_folios])

    je_z = standardize(jsd_entry).reshape(-1, 1)
    arr_z = standardize(axm_return).reshape(-1, 1)
    jx_z = standardize(jsd_exit).reshape(-1, 1)
    dep_z = standardize(axm_departure).reshape(-1, 1)

    X_dual = np.hstack([X_base, je_z, arr_z, jx_z, dep_z])
    beta, y_pred, ss_res, r2 = ols_fit(X_dual, axm_self)
    loo = loo_cv_r2(X_dual, axm_self)
    residuals = axm_self - y_pred

    print(f"  C1169 replication: R2={r2:.4f}, LOO={loo:.4f}")

    # Univariate Spearman screen: each category fraction vs residuals
    spearman_results = {}
    p_values = []
    for cat in CATEGORIES:
        cat_vals = np.array([cat_fracs[f].get(cat, 0) for f in complete_folios])
        rho, p = stats.spearmanr(cat_vals, residuals)
        spearman_results[cat] = {'rho': float(rho), 'p': float(p)}
        p_values.append((cat, float(p)))

    # Holm correction
    p_values.sort(key=lambda x: x[1])
    holm_results = {}
    any_significant = False
    significant_cats = []
    for rank, (cat, p) in enumerate(p_values):
        holm_threshold = 0.05 / (len(p_values) - rank)
        sig = p < holm_threshold
        holm_results[cat] = {'p': p, 'holm_threshold': holm_threshold, 'significant': sig}
        if sig:
            any_significant = True
            significant_cats.append(cat)

    # Verdict
    v_str = verdict(min(p for _, p in p_values) * len(CATEGORIES))  # Bonferroni-equivalent
    if any_significant:
        v_str = 'PASS'  # Override: Holm is less conservative than Bonferroni
    elif min(p for _, p in p_values) < 0.05:
        v_str = 'WEAK'

    print(f"  Spearman correlations with C1169 residuals:")
    for cat in CATEGORIES:
        sr = spearman_results[cat]
        sig = "***" if cat in significant_cats else ""
        print(f"    {cat}: rho={sr['rho']:+.3f}, p={sr['p']:.4f}{sig}")
    print(f"  Holm-significant: {significant_cats if significant_cats else 'none'}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T6_category_vs_residuals',
        'n_folios': n,
        'model_r2': float(r2),
        'model_loo': float(loo),
        'spearman_results': spearman_results,
        'holm_results': holm_results,
        'significant_categories': significant_cats,
        'verdict': v_str,
        # Pass through for T7
        '_complete_folios': complete_folios,
        '_X_dual': X_dual,
        '_axm_self': axm_self,
        '_ss_res_dual': ss_res,
        '_r2_dual': r2,
        '_loo_dual': loo,
    }


# ============================================================
# T7: AXM Regression Extension (gated on T6)
# ============================================================

def test_t7(data, t6_result):
    print("\n=== T7: AXM Regression Extension (gated on T6) ===")

    sig_cats = t6_result.get('significant_categories', [])
    if not sig_cats:
        print("  SKIP: T6 found no significant categories")
        return {
            'test': 'T7_axm_regression_extension',
            'verdict': 'SKIP',
            'reason': 'T6 found no significant categories',
        }

    complete_folios = t6_result['_complete_folios']
    X_dual = t6_result['_X_dual']
    axm_self = t6_result['_axm_self']
    ss_res_dual = t6_result['_ss_res_dual']
    r2_dual = t6_result['_r2_dual']
    loo_dual = t6_result['_loo_dual']
    cat_fracs = data['folio_cat_fracs']
    n = len(complete_folios)

    # Add significant category fractions as predictors
    new_cols = []
    for cat in sig_cats:
        cat_vals = np.array([cat_fracs[f].get(cat, 0) for f in complete_folios])
        new_cols.append(standardize(cat_vals).reshape(-1, 1))
    X_extended = np.hstack([X_dual] + new_cols)

    beta_ext, y_pred_ext, ss_res_ext, r2_ext = ols_fit(X_extended, axm_self)
    loo_ext = loo_cv_r2(X_extended, axm_self)

    delta_r2 = r2_ext - r2_dual
    delta_loo = loo_ext - loo_dual
    k_full = X_extended.shape[1]
    df_extra = len(sig_cats)
    f_stat, f_p = f_test_increment(ss_res_dual, ss_res_ext, df_extra, n, k_full)

    v_str = verdict(f_p)
    # Additional check: LOO must not decrease
    if v_str == 'PASS' and delta_loo < 0:
        v_str = 'WEAK'
        print("  NOTE: F-test significant but LOO decreased -- downgraded to WEAK")

    print(f"  Added {len(sig_cats)} category predictors: {sig_cats}")
    print(f"  Original: R2={r2_dual:.4f}, LOO={loo_dual:.4f}")
    print(f"  Extended: R2={r2_ext:.4f}, LOO={loo_ext:.4f}")
    print(f"  Delta R2={delta_r2:+.4f}, Delta LOO={delta_loo:+.4f}")
    print(f"  F-test: F={f_stat:.2f}, p={f_p:.4f}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T7_axm_regression_extension',
        'added_categories': sig_cats,
        'n_folios': n,
        'original_r2': float(r2_dual),
        'original_loo': float(loo_dual),
        'extended_r2': float(r2_ext),
        'extended_loo': float(loo_ext),
        'delta_r2': float(delta_r2),
        'delta_loo': float(delta_loo),
        'f_stat': float(f_stat),
        'f_p': float(f_p),
        'verdict': v_str,
    }


# ============================================================
# T8: REGIME Feature x Category Correlation (Calibration)
# ============================================================

def test_t8(data):
    print("\n=== T8: REGIME Feature x Category Correlation (Calibration -- NOT SCORED) ===")
    valid = data['valid_folios']
    cat_fracs = data['folio_cat_fracs']
    folio_data = data['folio_data']
    kernel_fracs = data['folio_kernel_fracs']

    # Available features from folio_data
    feature_keys = ['prefix_entropy', 'hazard_density', 'bridge_pc1',
                    'qo_fraction', 'vocab_residual']

    # Add kernel fractions as proxy for k_ratio, h_ratio, e_ratio
    # (Not identical to REGIME GMM features, but closely related)

    folios = [f for f in valid if f in folio_data and f in kernel_fracs]
    n = len(folios)
    print(f"  Folios with feature data: {n}")

    correlations = []
    for feat in feature_keys:
        vals = [folio_data[f].get(feat) for f in folios]
        if any(v is None for v in vals):
            continue
        vals = np.array(vals, dtype=float)
        for cat in CATEGORIES:
            cat_vals = np.array([cat_fracs[f].get(cat, 0) for f in folios])
            rho, p = stats.spearmanr(vals, cat_vals)
            correlations.append({
                'feature': feat,
                'category': cat,
                'rho': float(rho),
                'p': float(p),
                'circular': False,
            })

    # Kernel fractions
    for kf in ['k_frac', 'h_frac', 'e_frac']:
        vals = np.array([kernel_fracs[f][kf] for f in folios])
        expected_circular = {
            'k_frac': ['THERMAL'],
            'h_frac': ['MONITORING'],
            'e_frac': ['THERMAL'],  # e='cool' maps to THERMAL
        }
        for cat in CATEGORIES:
            cat_vals = np.array([cat_fracs[f].get(cat, 0) for f in folios])
            rho, p = stats.spearmanr(vals, cat_vals)
            is_circular = cat in expected_circular.get(kf, [])
            correlations.append({
                'feature': kf,
                'category': cat,
                'rho': float(rho),
                'p': float(p),
                'circular': is_circular,
            })

    # Sort by |rho|
    correlations.sort(key=lambda x: -abs(x['rho']))

    print("  Top 15 correlations (sorted by |rho|):")
    for i, corr in enumerate(correlations[:15]):
        circ_flag = " [CIRCULAR]" if corr['circular'] else ""
        sig = "*" if corr['p'] < 0.05 else ""
        print(f"    {corr['feature']:20s} x {corr['category']:12s}: "
              f"rho={corr['rho']:+.3f}, p={corr['p']:.4f}{sig}{circ_flag}")

    return {
        'test': 'T8_feature_category_correlation',
        'n_folios': n,
        'correlations': correlations[:30],  # Top 30 for JSON
        'verdict': 'CALIBRATION',
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("Phase 456: CATEGORY_REGIME_INTEGRATION")
    print("=" * 60)
    t_start = time.time()

    data = load_data()
    results = {
        'phase_name': 'CATEGORY_REGIME_INTEGRATION',
        'phase_number': 456,
        'n_valid_folios': len(data['valid_folios']),
        'bonferroni_p': BONFERRONI_P,
        'n_scored_tests': N_SCORED_TESTS,
    }

    # Run all tests
    r1 = test_t1(data)
    r2 = test_t2(data)
    r3 = test_t3(data)
    r4 = test_t4(data)
    r5 = test_t5(data)
    r6 = test_t6(data)

    # T7 gated on T6
    r7 = test_t7(data, r6)

    # T8 calibration
    r8 = test_t8(data)

    # Clean T6 result (remove internal arrays)
    r6_clean = {k: v for k, v in r6.items() if not k.startswith('_')}

    tests = [r1, r2, r3, r4, r5, r6_clean, r7, r8]
    results['tests'] = tests

    # Overall verdict
    scored = [r for r in [r1, r2, r3, r4, r5, r6_clean, r7] if r.get('verdict') not in ('SKIP', 'CALIBRATION')]
    n_pass = sum(1 for r in scored if r['verdict'] == 'PASS')
    n_weak = sum(1 for r in scored if r['verdict'] == 'WEAK')
    n_fail = sum(1 for r in scored if r['verdict'] == 'FAIL')

    # T3 circularity gate
    t3_pass = r3.get('verdict') == 'PASS'
    if n_pass >= 5:
        overall = 'CATEGORY_REGIME_INTEGRATED'
    elif n_pass >= 3:
        overall = 'CATEGORY_REGIME_PARTIAL'
    else:
        overall = 'CATEGORY_REGIME_INDEPENDENT'

    if not t3_pass and overall == 'CATEGORY_REGIME_INTEGRATED':
        overall = 'CATEGORY_REGIME_PARTIAL'
        print("\n  ** T3 CIRCULARITY GATE: Overall capped at PARTIAL (T3 did not pass)")

    results['summary'] = {
        'n_pass': n_pass,
        'n_weak': n_weak,
        'n_fail': n_fail,
        'n_skip': sum(1 for r in [r1, r2, r3, r4, r5, r6_clean, r7] if r.get('verdict') == 'SKIP'),
        't3_circularity_gate': t3_pass,
        'overall_verdict': overall,
    }

    elapsed = time.time() - t_start

    # Summary table
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in tests:
        v = r.get('verdict', '?')
        test_name = r.get('test', '?')
        # Get p-value (different tests store it differently)
        p = r.get('p', r.get('combined_p', r.get('fisher_p', r.get('f_p', None))))
        p_str = f"p={p:.2e}" if p is not None else "N/A"
        print(f"  {test_name:45s} {v:12s} {p_str}")
    print(f"\n  PASS={n_pass} WEAK={n_weak} FAIL={n_fail}")
    print(f"  T3 circularity gate: {'PASSED' if t3_pass else 'FAILED'}")
    print(f"  Overall: {overall}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'category_regime_integration.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\n  Results saved to: {out_path}")


if __name__ == '__main__':
    main()
