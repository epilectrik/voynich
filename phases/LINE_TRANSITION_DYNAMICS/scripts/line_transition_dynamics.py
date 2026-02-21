#!/usr/bin/env python3
"""
Phase 413: LINE_TRANSITION_DYNAMICS
======================================
Tests whether within-line position structure constrains token transition
dynamics, and whether position-conditioned transitions explain any of the
M2 generative model's remaining gap or the C1035 AXM residual.

5-test battery:
  T1: ZONE_TRANSITION_DIVERGENCE (49x49 matrices differ by zone?)
  T2: BOUNDARY_SPECTRAL_PROPERTIES (6-state regime shifts by zone?)
  T3: POSITION_CONDITIONED_GENERATION_IMPROVEMENT (M2p vs M2)
  T4: LINE_POSITION_AXM_RESIDUAL (boundary divergence predicts residual?)
  T5: SECTION_POSITION_INVARIANCE (effect universal or section-specific?)

Depends on: C964, C681, C958, C961, C972, C1025, C1035, C1045
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
N_PERMS = 1000
N_INST = 50

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
    """Jensen-Shannon divergence between two distributions."""
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m)))


def compute_kl(p, q, epsilon=1e-10):
    """KL divergence D(p || q)."""
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log2(p / q)))


def matrix_to_6state(m49):
    """Collapse 49x49 count matrix to 6x6 macro-state matrix."""
    m6 = np.zeros((N_STATES, N_STATES))
    for src_cls in range(1, N_CLASSES + 1):
        si = STATE_IDX[CLASS_TO_STATE[src_cls]]
        for tgt_cls in range(1, N_CLASSES + 1):
            ti = STATE_IDX[CLASS_TO_STATE[tgt_cls]]
            m6[si, ti] += m49[src_cls - 1, tgt_cls - 1]
    return m6


def stationary_dist(m):
    """Compute stationary distribution of transition matrix."""
    m_norm = normalize_rows(m)
    eigvals, eigvecs = np.linalg.eig(m_norm.T)
    idx = np.argmin(np.abs(eigvals - 1.0))
    pi = np.abs(eigvecs[:, idx].real)
    if pi.sum() > 0:
        pi = pi / pi.sum()
    return pi


def spectral_gap(m):
    """Compute spectral gap = 1 - |lambda_2|."""
    m_norm = normalize_rows(m)
    eigvals = np.sort(np.abs(np.linalg.eigvals(m_norm)))[::-1]
    if len(eigvals) < 2:
        return 0.0
    return float(1.0 - eigvals[1])


# ── Data Loading ──────────────────────────────────────────────────

def load_data():
    """Load transcript, class map, AXM data. Build per-folio per-line structure."""
    print("Loading data...")

    # Load class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' /
              'class_token_map.json', encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']
    class_to_tokens = {int(k): v for k, v in cmap['class_to_tokens'].items()}

    # Load forbidden pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' /
              'phase18a_forbidden_inventory.json', encoding='utf-8') as f:
        fdata = json.load(f)
    forbidden_middle_pairs = [(t['source'], t['target']) for t in fdata['transitions']]

    # Load AXM folio data
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']
    valid_folios = set(folio_data.keys())

    morph = Morphology()

    # Build per-folio per-line token lists with class assignments
    folio_lines = defaultdict(lambda: defaultdict(list))  # folio -> line_key -> [tokens]
    skipped = 0
    total = 0

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        cls = token_to_class.get(w)
        if cls is None:
            skipped += 1
            continue
        total += 1
        line_key = t.line
        folio_lines[t.folio][line_key].append({
            'word': w,
            'cls': cls,
            'state': CLASS_TO_STATE[cls],
        })

    # Convert to sorted line lists per folio
    all_lines = []  # list of (folio, section, [tokens])
    folio_line_lists = defaultdict(list)  # folio -> [[tokens], ...]

    for folio in sorted(folio_lines.keys()):
        fd = folio_data.get(folio, {})
        section = fd.get('section', '?')
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:  # need at least 2 tokens for a transition
                all_lines.append((folio, section, tokens))
                folio_line_lists[folio].append(tokens)

    print(f"  Tokens classified: {total}, skipped (no class): {skipped}")
    print(f"  Lines (≥2 tokens): {len(all_lines)} across {len(folio_line_lists)} folios")
    print(f"  AXM data: {len(valid_folios)} folios")

    return (all_lines, folio_line_lists, folio_data, valid_folios,
            token_to_class, class_to_tokens, forbidden_middle_pairs, morph)


# ── Zone Classification ───────────────────────────────────────────

def classify_transitions(all_lines):
    """Classify all transitions into ENTRY/INTERIOR/EXIT zones."""
    zone_trans = {'ENTRY': [], 'INTERIOR': [], 'EXIT': []}
    per_line_zones = []  # for permutation: list of (line_idx, [(src, tgt, zone), ...])

    for line_idx, (folio, section, tokens) in enumerate(all_lines):
        n = len(tokens)
        line_transitions = []
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
            line_transitions.append((src_cls, tgt_cls, zone))
        per_line_zones.append(line_transitions)

    return zone_trans, per_line_zones


def build_zone_matrix(transitions):
    """Build 49x49 count matrix from list of (src_cls, tgt_cls)."""
    m = np.zeros((N_CLASSES, N_CLASSES))
    for src, tgt in transitions:
        m[src - 1, tgt - 1] += 1
    return m


# ── Test 1: ZONE_TRANSITION_DIVERGENCE ────────────────────────────

def test1_zone_transition_divergence(zone_trans, per_line_zones):
    print("\n── Test 1: ZONE_TRANSITION_DIVERGENCE ──")

    m_entry = build_zone_matrix(zone_trans['ENTRY'])
    m_interior = build_zone_matrix(zone_trans['INTERIOR'])
    m_exit = build_zone_matrix(zone_trans['EXIT'])

    n_entry = len(zone_trans['ENTRY'])
    n_interior = len(zone_trans['INTERIOR'])
    n_exit = len(zone_trans['EXIT'])
    print(f"  Transitions: ENTRY={n_entry}, INTERIOR={n_interior}, EXIT={n_exit}")

    # Flatten to distributions for JSD
    flat_entry = m_entry.flatten()
    flat_interior = m_interior.flatten()
    flat_exit = m_exit.flatten()

    jsd_ei = compute_jsd(flat_entry, flat_interior)
    jsd_ie = compute_jsd(flat_interior, flat_exit)
    jsd_ee = compute_jsd(flat_entry, flat_exit)

    print(f"  JSD(entry,interior)={jsd_ei:.6f}")
    print(f"  JSD(interior,exit)={jsd_ie:.6f}")
    print(f"  JSD(entry,exit)={jsd_ee:.6f}")

    # Permutation null: shuffle zone labels within each line
    null_jsds = {'ei': [], 'ie': [], 'ee': []}
    rng = np.random.default_rng(42)

    for perm in range(N_PERMS):
        perm_zones = {'ENTRY': [], 'INTERIOR': [], 'EXIT': []}
        for line_transitions in per_line_zones:
            n_t = len(line_transitions)
            if n_t == 0:
                continue
            # Extract original zones for this line
            original_zones = [t[2] for t in line_transitions]
            shuffled_zones = list(original_zones)
            rng.shuffle(shuffled_zones)
            for k, (src, tgt, _) in enumerate(line_transitions):
                perm_zones[shuffled_zones[k]].append((src, tgt))

        pm_entry = build_zone_matrix(perm_zones['ENTRY'])
        pm_interior = build_zone_matrix(perm_zones['INTERIOR'])
        pm_exit = build_zone_matrix(perm_zones['EXIT'])

        null_jsds['ei'].append(compute_jsd(pm_entry.flatten(), pm_interior.flatten()))
        null_jsds['ie'].append(compute_jsd(pm_interior.flatten(), pm_exit.flatten()))
        null_jsds['ee'].append(compute_jsd(pm_entry.flatten(), pm_exit.flatten()))

    p_ei = sum(1 for v in null_jsds['ei'] if v >= jsd_ei) / N_PERMS
    p_ie = sum(1 for v in null_jsds['ie'] if v >= jsd_ie) / N_PERMS
    p_ee = sum(1 for v in null_jsds['ee'] if v >= jsd_ee) / N_PERMS

    print(f"  Null p-values: entry-int={p_ei:.4f}, int-exit={p_ie:.4f}, entry-exit={p_ee:.4f}")

    # Per-source-class KL divergence (interior as reference)
    m_entry_norm = normalize_rows(m_entry)
    m_interior_norm = normalize_rows(m_interior)
    m_exit_norm = normalize_rows(m_exit)

    class_kl = []
    min_count = 20
    for c in range(N_CLASSES):
        entry_row_count = m_entry[c].sum()
        interior_row_count = m_interior[c].sum()
        exit_row_count = m_exit[c].sum()
        if entry_row_count >= min_count and interior_row_count >= min_count:
            kl_entry = compute_kl(m_entry_norm[c], m_interior_norm[c])
        else:
            kl_entry = None
        if exit_row_count >= min_count and interior_row_count >= min_count:
            kl_exit = compute_kl(m_exit_norm[c], m_interior_norm[c])
        else:
            kl_exit = None
        if kl_entry is not None or kl_exit is not None:
            class_kl.append({
                'class': c + 1,
                'kl_entry_vs_interior': kl_entry,
                'kl_exit_vs_interior': kl_exit,
            })

    # Sort by max KL
    class_kl.sort(key=lambda x: max(x['kl_entry_vs_interior'] or 0,
                                      x['kl_exit_vs_interior'] or 0), reverse=True)
    top_10 = class_kl[:10]

    n_significant = sum(1 for p in [p_ei, p_ie, p_ee] if p < 0.05)
    verdict = 'POSITION_STRUCTURED' if n_significant >= 2 else 'POSITION_INVARIANT'
    print(f"  Verdict: {verdict}")

    return {
        'n_transitions': {'entry': n_entry, 'interior': n_interior, 'exit': n_exit},
        'jsd_pairs': {
            'entry_vs_interior': {'jsd': jsd_ei, 'null_mean': np.mean(null_jsds['ei']),
                                   'null_p': p_ei},
            'interior_vs_exit': {'jsd': jsd_ie, 'null_mean': np.mean(null_jsds['ie']),
                                  'null_p': p_ie},
            'entry_vs_exit': {'jsd': jsd_ee, 'null_mean': np.mean(null_jsds['ee']),
                               'null_p': p_ee},
        },
        'top_position_sensitive_classes': top_10,
        'verdict': verdict,
    }


# ── Test 2: BOUNDARY_SPECTRAL_PROPERTIES ─────────────────────────

def test2_boundary_spectral_properties(zone_trans):
    print("\n── Test 2: BOUNDARY_SPECTRAL_PROPERTIES ──")

    results = {}
    for zone in ['ENTRY', 'INTERIOR', 'EXIT']:
        m49 = build_zone_matrix(zone_trans[zone])
        m6 = matrix_to_6state(m49)
        m6_norm = normalize_rows(m6)

        axm_idx = STATE_IDX['AXM']
        axm_self = float(m6_norm[axm_idx, axm_idx]) if m6[axm_idx].sum() > 0 else 0.0

        pi = stationary_dist(m6)
        gap = spectral_gap(m6)

        zone_lower = zone.lower()
        results[zone_lower] = {
            'stationary': {STATE_ORDER[i]: float(pi[i]) for i in range(N_STATES)},
            'spectral_gap': gap,
            'axm_self': axm_self,
        }
        print(f"  {zone}: AXM_self={axm_self:.4f}, gap={gap:.4f}, "
              f"pi(AXM)={pi[STATE_IDX['AXM']]:.4f}")

    axm_selfs = [results[z]['axm_self'] for z in ['entry', 'interior', 'exit']]
    gaps = [results[z]['spectral_gap'] for z in ['entry', 'interior', 'exit']]
    axm_delta = max(axm_selfs) - min(axm_selfs)
    gap_delta = max(gaps) - min(gaps)

    verdict = ('BOUNDARY_REGIME_SHIFT'
               if axm_delta > 0.03 and gap_delta > 0.03
               else 'BOUNDARY_REGIME_STABLE')
    print(f"  AXM self-trans delta: {axm_delta:.4f}")
    print(f"  Spectral gap delta: {gap_delta:.4f}")
    print(f"  Verdict: {verdict}")

    # Stationary max deviation (entry vs interior)
    pi_entry = np.array([results['entry']['stationary'][s] for s in STATE_ORDER])
    pi_interior = np.array([results['interior']['stationary'][s] for s in STATE_ORDER])
    stat_max_dev = float(np.max(np.abs(pi_entry - pi_interior)))

    return {
        'per_zone': results,
        'axm_self_delta_max': axm_delta,
        'spectral_gap_delta_max': gap_delta,
        'stationary_max_deviation': stat_max_dev,
        'verdict': verdict,
    }


# ── Test 3: POSITION_CONDITIONED_GENERATION_IMPROVEMENT ──────────

def test3_position_conditioned_generation(all_lines, zone_trans,
                                           token_to_class, class_to_tokens,
                                           forbidden_middle_pairs, morph):
    print("\n── Test 3: POSITION_CONDITIONED_GENERATION_IMPROVEMENT ──")

    # Build real corpus statistics for comparison
    real_lines = [tokens for _, _, tokens in all_lines]
    real_class_counts = Counter()
    real_bigrams = set()
    real_opener_classes = Counter()
    real_closer_classes = Counter()
    for line in real_lines:
        for t in line:
            real_class_counts[t['cls']] += 1
        for i in range(len(line) - 1):
            real_bigrams.add((line[i]['cls'], line[i + 1]['cls']))
        real_opener_classes[line[0]['cls']] += 1
        real_closer_classes[line[-1]['cls']] += 1

    total_real = sum(real_class_counts.values())
    real_class_dist = np.zeros(N_CLASSES)
    for cls, count in real_class_counts.items():
        real_class_dist[cls - 1] = count / total_real

    line_lengths = [len(line) for line in real_lines]
    n_lines = len(real_lines)

    # Build aggregate transition matrix + zone matrices
    m_aggregate = np.zeros((N_CLASSES, N_CLASSES))
    for line in real_lines:
        for i in range(len(line) - 1):
            m_aggregate[line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

    m_entry = build_zone_matrix(zone_trans['ENTRY'])
    m_interior = build_zone_matrix(zone_trans['INTERIOR'])
    m_exit = build_zone_matrix(zone_trans['EXIT'])

    # Opener distribution
    opener_probs = np.zeros(N_CLASSES)
    for cls, count in real_opener_classes.items():
        opener_probs[cls - 1] = count
    opener_probs /= max(opener_probs.sum(), 1)

    # Class → token probs
    all_tokens_flat = [t for line in real_lines for t in line]
    class_token_freqs = defaultdict(Counter)
    for t in all_tokens_flat:
        class_token_freqs[t['cls']][t['word']] += 1
    class_token_probs = {}
    for cls, freq in class_token_freqs.items():
        toks = list(freq.keys())
        counts = np.array([freq[t] for t in toks], dtype=float)
        class_token_probs[cls] = (toks, counts / counts.sum())

    # Apply forbidden suppression to all matrices
    def apply_forbidden(m):
        m = m.copy()
        for src_mid, tgt_mid in forbidden_middle_pairs:
            src_classes = set()
            tgt_classes = set()
            for cls, toks_list in class_to_tokens.items():
                for tok in toks_list:
                    mid = morph.extract(tok)
                    mid_str = mid.middle if mid else tok
                    if mid_str == src_mid:
                        src_classes.add(int(cls))
                    if mid_str == tgt_mid:
                        tgt_classes.add(int(cls))
            for sc in src_classes:
                for tc in tgt_classes:
                    m[sc - 1, tc - 1] = 0
        return normalize_rows(m)

    trans_agg = apply_forbidden(m_aggregate)
    trans_entry = apply_forbidden(m_entry)
    trans_interior = apply_forbidden(m_interior)
    trans_exit = apply_forbidden(m_exit)

    def generate_standard_m2(rng):
        corpus = []
        for _ in range(n_lines):
            length = rng.choice(line_lengths)
            line = []
            cls = rng.choice(N_CLASSES, p=opener_probs) + 1
            for pos in range(length):
                if pos > 0:
                    row = trans_agg[cls - 1]
                    if row.sum() > 0:
                        cls = rng.choice(N_CLASSES, p=row) + 1
                    else:
                        cls = rng.choice(N_CLASSES, p=opener_probs) + 1
                if cls in class_token_probs:
                    toks, probs = class_token_probs[cls]
                    word = rng.choice(toks, p=probs)
                else:
                    word = f'UNK_C{cls}'
                line.append({'word': word, 'cls': cls})
            corpus.append(line)
        return corpus

    def generate_m2p(rng):
        corpus = []
        for _ in range(n_lines):
            length = rng.choice(line_lengths)
            line = []
            cls = rng.choice(N_CLASSES, p=opener_probs) + 1
            for pos in range(length):
                if pos > 0:
                    # Select zone-appropriate transition matrix
                    if pos == 1:
                        trans = trans_entry
                    elif pos == length - 1:
                        trans = trans_exit
                    else:
                        trans = trans_interior
                    row = trans[cls - 1]
                    if row.sum() > 0:
                        cls = rng.choice(N_CLASSES, p=row) + 1
                    else:
                        cls = rng.choice(N_CLASSES, p=opener_probs) + 1
                if cls in class_token_probs:
                    toks, probs = class_token_probs[cls]
                    word = rng.choice(toks, p=probs)
                else:
                    word = f'UNK_C{cls}'
                line.append({'word': word, 'cls': cls})
            corpus.append(line)
        return corpus

    def compute_metrics(corpus):
        # Class distribution JSD
        gen_class_counts = Counter()
        gen_bigrams = set()
        gen_opener_classes = Counter()
        gen_closer_classes = Counter()
        for line in corpus:
            for t in line:
                gen_class_counts[t['cls']] += 1
            for i in range(len(line) - 1):
                gen_bigrams.add((line[i]['cls'], line[i + 1]['cls']))
            gen_opener_classes[line[0]['cls']] += 1
            gen_closer_classes[line[-1]['cls']] += 1

        total_gen = sum(gen_class_counts.values())
        gen_class_dist = np.zeros(N_CLASSES)
        for cls, count in gen_class_counts.items():
            gen_class_dist[cls - 1] = count / max(total_gen, 1)

        class_jsd = compute_jsd(gen_class_dist, real_class_dist)

        # Bigram accuracy: fraction of generated bigrams seen in real
        if gen_bigrams:
            bigram_acc = len(gen_bigrams & real_bigrams) / len(gen_bigrams)
        else:
            bigram_acc = 0.0

        # Boundary class accuracy
        boundary_acc = 0.0
        n_boundary = 0
        for cls in gen_opener_classes:
            if cls in real_opener_classes:
                boundary_acc += gen_opener_classes[cls]
            n_boundary += gen_opener_classes[cls]
        for cls in gen_closer_classes:
            if cls in real_closer_classes:
                boundary_acc += gen_closer_classes[cls]
            n_boundary += gen_closer_classes[cls]
        boundary_acc = boundary_acc / max(n_boundary, 1)

        return class_jsd, bigram_acc, boundary_acc

    # Generate and compare
    m2_metrics = {'class_jsd': [], 'bigram_acc': [], 'boundary_acc': []}
    m2p_metrics = {'class_jsd': [], 'bigram_acc': [], 'boundary_acc': []}

    for inst in range(N_INST):
        rng_m2 = np.random.default_rng(1000 + inst)
        rng_m2p = np.random.default_rng(2000 + inst)

        corpus_m2 = generate_standard_m2(rng_m2)
        corpus_m2p = generate_m2p(rng_m2p)

        jsd_m2, big_m2, bnd_m2 = compute_metrics(corpus_m2)
        jsd_m2p, big_m2p, bnd_m2p = compute_metrics(corpus_m2p)

        m2_metrics['class_jsd'].append(jsd_m2)
        m2_metrics['bigram_acc'].append(big_m2)
        m2_metrics['boundary_acc'].append(bnd_m2)
        m2p_metrics['class_jsd'].append(jsd_m2p)
        m2p_metrics['bigram_acc'].append(big_m2p)
        m2p_metrics['boundary_acc'].append(bnd_m2p)

    # Paired Wilcoxon tests
    results = {}
    n_improved = 0
    for metric_name in ['class_jsd', 'bigram_acc', 'boundary_acc']:
        m2_vals = np.array(m2_metrics[metric_name])
        m2p_vals = np.array(m2p_metrics[metric_name])

        # For JSD: lower is better. For accuracy: higher is better.
        if metric_name == 'class_jsd':
            diff = m2_vals - m2p_vals  # positive = m2p better
        else:
            diff = m2p_vals - m2_vals  # positive = m2p better

        if np.all(diff == 0):
            w_p = 1.0
        else:
            _, w_p = scipy_stats.wilcoxon(diff, alternative='greater')

        improved = w_p < 0.05
        if improved:
            n_improved += 1

        results[metric_name] = {
            'm2_mean': float(m2_vals.mean()),
            'm2p_mean': float(m2p_vals.mean()),
            'wilcoxon_p': float(w_p),
            'improved': improved,
        }
        direction = "better" if improved else "similar"
        print(f"  {metric_name}: M2={m2_vals.mean():.6f}, M2p={m2p_vals.mean():.6f}, "
              f"p={w_p:.4f} ({direction})")

    verdict = ('POSITION_CONDITIONING_IMPROVES' if n_improved >= 2
               else 'POSITION_CONDITIONING_NEUTRAL')
    print(f"  Metrics improved: {n_improved}/3")
    print(f"  Verdict: {verdict}")

    return {
        'n_instantiations': N_INST,
        'metrics': results,
        'n_metrics_improved': n_improved,
        'verdict': verdict,
    }


# ── Test 4: LINE_POSITION_AXM_RESIDUAL ───────────────────────────

def test4_line_position_axm_residual(folio_line_lists, folio_data, valid_folios):
    print("\n── Test 4: LINE_POSITION_AXM_RESIDUAL ──")

    MIN_ZONE_TRANS = 10

    # Per folio: compute zone-specific 6-state transition matrices
    folio_boundary_div = {}

    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]

        zone_trans_folio = {'ENTRY': [], 'INTERIOR': [], 'EXIT': []}
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
                zone_trans_folio[zone].append((src_cls, tgt_cls))

        # Check minimum counts
        if (len(zone_trans_folio['ENTRY']) < MIN_ZONE_TRANS or
            len(zone_trans_folio['INTERIOR']) < MIN_ZONE_TRANS or
            len(zone_trans_folio['EXIT']) < MIN_ZONE_TRANS):
            continue

        # Build 6-state matrices per zone
        m6_entry = matrix_to_6state(build_zone_matrix(zone_trans_folio['ENTRY']))
        m6_interior = matrix_to_6state(build_zone_matrix(zone_trans_folio['INTERIOR']))
        m6_exit = matrix_to_6state(build_zone_matrix(zone_trans_folio['EXIT']))

        # Boundary divergence = JSD(entry, interior) + JSD(exit, interior)
        jsd_entry = compute_jsd(m6_entry.flatten(), m6_interior.flatten())
        jsd_exit = compute_jsd(m6_exit.flatten(), m6_interior.flatten())
        boundary_div = jsd_entry + jsd_exit

        folio_boundary_div[folio] = boundary_div

    n_folios = len(folio_boundary_div)
    print(f"  Folios with all zones (≥{MIN_ZONE_TRANS} trans each): {n_folios}")

    if n_folios < 15:
        print("  Too few folios for regression. Verdict: POSITION_NEUTRAL_TO_RESIDUAL")
        return {
            'n_folios_with_all_zones': n_folios,
            'verdict': 'POSITION_NEUTRAL_TO_RESIDUAL',
            'reason': 'insufficient folios',
        }

    # Build arrays aligned with folio_data
    folios_ordered = sorted(folio_boundary_div.keys())
    bd_vals = np.array([folio_boundary_div[f] for f in folios_ordered])
    axm_vals = np.array([folio_data[f]['axm_self'] for f in folios_ordered])
    residuals = np.array([folio_data[f]['c1017_residual'] for f in folios_ordered])

    bd_stats = {
        'mean': float(bd_vals.mean()),
        'std': float(bd_vals.std()),
        'min': float(bd_vals.min()),
        'max': float(bd_vals.max()),
    }
    print(f"  Boundary divergence: mean={bd_stats['mean']:.4f}, "
          f"std={bd_stats['std']:.4f}")

    rho_axm, p_axm = spearman_r(bd_vals.tolist(), axm_vals.tolist())
    rho_resid, p_resid = spearman_r(bd_vals.tolist(), residuals.tolist())
    print(f"  Spearman vs AXM self: rho={rho_axm:.4f}, p={p_axm:.4f}")
    print(f"  Spearman vs C1017 residual: rho={rho_resid:.4f}, p={p_resid:.4f}")

    # Replicate C1035 baseline on this subset, then add boundary divergence
    regimes = [folio_data[f]['regime'] for f in folios_ordered]
    sections = [folio_data[f]['section'] for f in folios_ordered]
    pfx_ent = np.array([folio_data[f]['prefix_entropy'] for f in folios_ordered])
    haz_den = np.array([folio_data[f]['hazard_density'] for f in folios_ordered])
    bridge_pc1 = np.array([folio_data[f]['bridge_pc1'] for f in folios_ordered])

    n = len(folios_ordered)
    intercept = np.ones((n, 1))
    regime_dum = build_dummies(regimes)
    section_dum = build_dummies(sections)
    pfx_z = standardize(pfx_ent).reshape(-1, 1)
    haz_z = standardize(haz_den).reshape(-1, 1)
    pc1_z = standardize(bridge_pc1).reshape(-1, 1)

    X_baseline = np.hstack([intercept, regime_dum, section_dum, pfx_z, haz_z, pc1_z])
    _, _, ss_res_base, r2_base = ols_fit(X_baseline, axm_vals)
    loo_base = loo_cv_r2(X_baseline, axm_vals)
    print(f"  C1035 baseline (n={n}): R2={r2_base:.4f}, LOO={loo_base:.4f}")

    bd_z = standardize(bd_vals).reshape(-1, 1)
    X_extended = np.hstack([X_baseline, bd_z])
    _, _, ss_res_ext, r2_ext = ols_fit(X_extended, axm_vals)
    loo_ext = loo_cv_r2(X_extended, axm_vals)

    dr2 = r2_ext - r2_base
    k_full = X_extended.shape[1]
    f_stat, f_p = f_test_increment(ss_res_base, ss_res_ext, 1, n, k_full)

    passes = dr2 > 0.03 and f_p < 0.05
    verdict = ('POSITION_MEDIATES_RESIDUAL' if passes
               else 'POSITION_NEUTRAL_TO_RESIDUAL')

    print(f"  Extended: R2={r2_ext:.4f}, LOO={loo_ext:.4f}")
    print(f"  dR2={dr2:.4f}, F={f_stat:.2f}, p={f_p:.4f} "
          f"[{'pass' if passes else 'fail'}]")
    print(f"  Verdict: {verdict}")

    return {
        'n_folios_with_all_zones': n_folios,
        'boundary_divergence_stats': bd_stats,
        'spearman_vs_axm_self': {'rho': rho_axm, 'p': p_axm},
        'spearman_vs_c1017_residual': {'rho': rho_resid, 'p': p_resid},
        'incremental_regression': {
            'c1035_baseline_r2': r2_base,
            'extended_r2': r2_ext,
            'delta_r2': dr2,
            'f_stat': f_stat,
            'f_p': f_p,
            'loo_cv_r2_baseline': loo_base,
            'loo_cv_r2_extended': loo_ext,
        },
        'verdict': verdict,
    }


# ── Test 5: SECTION_POSITION_INVARIANCE ──────────────────────────

def test5_section_position_invariance(all_lines):
    print("\n── Test 5: SECTION_POSITION_INVARIANCE ──")

    section_zone_trans = defaultdict(lambda: {'ENTRY': [], 'INTERIOR': [], 'EXIT': []})

    for folio, section, tokens in all_lines:
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
            section_zone_trans[section][zone].append((src_cls, tgt_cls))

    results = {}
    section_sensitivities = {}

    for sec in sorted(section_zone_trans.keys()):
        zt = section_zone_trans[sec]
        n_entry = len(zt['ENTRY'])
        n_interior = len(zt['INTERIOR'])
        n_exit = len(zt['EXIT'])

        if n_interior < 50:
            continue

        m_entry = build_zone_matrix(zt['ENTRY'])
        m_interior = build_zone_matrix(zt['INTERIOR'])
        m_exit = build_zone_matrix(zt['EXIT'])

        jsd_ei = compute_jsd(m_entry.flatten(), m_interior.flatten())
        jsd_ie = compute_jsd(m_interior.flatten(), m_exit.flatten())
        sensitivity = jsd_ei + jsd_ie

        results[sec] = {
            'n_lines': n_entry,  # entry count = line count
            'jsd_entry_int': jsd_ei,
            'jsd_exit_int': jsd_ie,
            'position_sensitivity': sensitivity,
        }
        section_sensitivities[sec] = sensitivity

        print(f"  Section {sec}: n={n_entry}, JSD(e,i)={jsd_ei:.6f}, "
              f"JSD(x,i)={jsd_ie:.6f}, sens={sensitivity:.6f}")

    # Kruskal-Wallis on per-folio position sensitivity by section
    # Build per-folio sensitivities grouped by section
    folio_sens_by_section = defaultdict(list)
    for folio, section, tokens in all_lines:
        pass  # we need per-folio, not per-line

    # Recompute at folio level
    folio_zone_trans = defaultdict(lambda: {'ENTRY': [], 'INTERIOR': [], 'EXIT': []})
    folio_sections = {}
    for folio, section, tokens in all_lines:
        folio_sections[folio] = section
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
            folio_zone_trans[folio][zone].append((src_cls, tgt_cls))

    for folio in sorted(folio_zone_trans.keys()):
        zt = folio_zone_trans[folio]
        if len(zt['ENTRY']) < 5 or len(zt['INTERIOR']) < 5 or len(zt['EXIT']) < 5:
            continue
        m_e = build_zone_matrix(zt['ENTRY'])
        m_i = build_zone_matrix(zt['INTERIOR'])
        m_x = build_zone_matrix(zt['EXIT'])
        jsd_ei = compute_jsd(m_e.flatten(), m_i.flatten())
        jsd_xi = compute_jsd(m_x.flatten(), m_i.flatten())
        sens = jsd_ei + jsd_xi
        sec = folio_sections[folio]
        folio_sens_by_section[sec].append(sens)

    # Kruskal-Wallis across sections
    groups = [np.array(v) for v in folio_sens_by_section.values() if len(v) >= 3]
    if len(groups) >= 2:
        kw_stat, kw_p = scipy_stats.kruskal(*groups)
    else:
        kw_stat, kw_p = 0.0, 1.0

    # CV of section-level sensitivities
    sens_values = list(section_sensitivities.values())
    if len(sens_values) >= 2:
        cv = float(np.std(sens_values) / (np.mean(sens_values) + 1e-10))
    else:
        cv = 0.0

    verdict = ('POSITION_SECTION_DEPENDENT' if kw_p < 0.05
               else 'POSITION_UNIVERSAL')
    print(f"  Kruskal-Wallis: H={kw_stat:.2f}, p={kw_p:.4f}")
    print(f"  CV of section sensitivities: {cv:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'per_section': results,
        'kruskal_wallis': {'H': float(kw_stat), 'p': float(kw_p)},
        'cv_of_section_jsds': cv,
        'verdict': verdict,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 413: LINE_TRANSITION_DYNAMICS")
    print("=" * 60)

    (all_lines, folio_line_lists, folio_data, valid_folios,
     token_to_class, class_to_tokens, forbidden_middle_pairs, morph) = load_data()

    zone_trans, per_line_zones = classify_transitions(all_lines)

    t1 = test1_zone_transition_divergence(zone_trans, per_line_zones)
    t2 = test2_boundary_spectral_properties(zone_trans)
    t3 = test3_position_conditioned_generation(
        all_lines, zone_trans, token_to_class, class_to_tokens,
        forbidden_middle_pairs, morph)
    t4 = test4_line_position_axm_residual(folio_line_lists, folio_data, valid_folios)
    t5 = test5_section_position_invariance(all_lines)

    # Synthesis
    t1_pass = t1['verdict'] == 'POSITION_STRUCTURED'
    t3_pass = t3['verdict'] == 'POSITION_CONDITIONING_IMPROVES'
    t4_pass = t4['verdict'] == 'POSITION_MEDIATES_RESIDUAL'

    if t1_pass and t3_pass and t4_pass:
        overall = 'LINE_POSITION_STRUCTURES_AND_MEDIATES_RESIDUAL'
    elif t1_pass and t3_pass:
        overall = 'LINE_POSITION_STRUCTURES_TRANSITIONS'
    elif t1_pass and t4_pass:
        overall = 'LINE_POSITION_MEDIATES_RESIDUAL'
    elif t1_pass:
        overall = 'LINE_POSITION_STRUCTURAL_NOT_GENERATIVE'
    else:
        overall = 'LINE_TRANSITIONS_POSITION_INVARIANT'

    print(f"\n── SYNTHESIS ──")
    print(f"  T1={t1['verdict']}")
    print(f"  T2={t2['verdict']}")
    print(f"  T3={t3['verdict']}")
    print(f"  T4={t4['verdict']}")
    print(f"  T5={t5['verdict']}")
    print(f"  Overall: {overall}")

    output = {
        'phase': 'LINE_TRANSITION_DYNAMICS',
        'phase_number': 413,
        'depends_on': ['C964', 'C681', 'C958', 'C961', 'C972', 'C1025', 'C1035', 'C1045'],
        'test1_zone_transition_divergence': t1,
        'test2_boundary_spectral_properties': t2,
        'test3_position_conditioned_generation': t3,
        'test4_line_position_axm_residual': t4,
        'test5_section_position_invariance': t5,
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
    out_path = RESULTS_DIR / 'line_transition_dynamics.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
