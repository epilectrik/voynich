#!/usr/bin/env python3
"""
Phase 344: CP_FACTOR_CHARACTERIZATION
=======================================
Tests whether the rank-8 CP tensor factors (C1019) have interpretable
morphological identities, whether rank-8 is structurally necessary, and
whether tensor variance structure aligns with the 6-state macro-automaton
under constraint filtering.

Sub-Analysis 1: Factor Semantic Identity (S1-S4)
  - Characterize all 8 factor loadings (PREFIX, BIN, SUFFIX, CLASS)
  - Factor 2 deep dive: gatekeeper alignment, frequency null check
  - Factor 3 deep dive: why AXM-orthogonal?

Sub-Analysis 2: Rank Sensitivity Ablation (R1-R4)
  - CP at ranks 2, 4, 6, 8, 10, 12
  - ΔR², cross-validated variance, forbidden transition compliance

Sub-Analysis 3: Constrained Consistency Test (C1-C3)
  - Hazard-filtered class similarity → cluster → ARI vs C1010
  - Permutation null (1000x)

Depends on: C1019 (rank-8 tensor), C1010 (6-state partition),
            C1007 (gatekeeper classes), C986 (frequency gradient),
            C109 (forbidden transitions), C588 (suffix strata)

Re-derivation guards:
  - Do NOT re-derive C1010 (frozen)
  - Do NOT re-cluster archetypes (C1016 frozen)
  - Sub-3 is CONSISTENCY test, not derivation
  - Factor 2 vs frequency is a NULL CHECK
"""

import json
import sys
import time
import functools
import warnings
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import cosine as cosine_dist
from sklearn.metrics import adjusted_rand_score

import tensorly as tl
from tensorly.decomposition import non_negative_parafac

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore', category=RuntimeWarning)

np.random.seed(42)

# ── Constants (from C1010/C1019) ──────────────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
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
N_CLASSES = 49

MIN_PREFIX_TOKENS = 10
MAX_PREFIXES = 20
CP_RANK = 8  # Reference from C1019

SUFFIX_GROUPS = {
    'NONE': {None, ''},
    'Y_FAMILY': {'y', 'ey', 'dy', 'ly', 'ry', 'hy', 'eey', 'edy'},
    'IN_FAMILY': {'in', 'iin', 'ain', 'oin', 'ein', 'aiin', 'oiin', 'eiin',
                  'an', 'en', 'on'},
    'OL_FAMILY': {'ol', 'eol', 'ool', 'eeol', 'al', 'el', 'er', 'ar', 'or'},
}
SUFFIX_GROUP_ORDER = ['NONE', 'Y_FAMILY', 'IN_FAMILY', 'OL_FAMILY', 'OTHER']
N_SUFFIX_GROUPS = len(SUFFIX_GROUP_ORDER)

# Structural indicators
GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}
FL_HAZ_CLASSES = {7, 30}
FL_SAFE_CLASSES = {38, 40}
CC_CLASSES = {10, 11, 12}
FQ_CLASSES = {9, 13, 14, 23}

# EN classes (from t9 holdout script get_role logic)
EN_CLASSES = ({8} | set(range(31, 50))) - {7, 30, 38, 40}
# AX classes = AXM + AXm minus EN
AX_CLASSES = (MACRO_STATE_PARTITION['AXM'] | MACRO_STATE_PARTITION['AXm']) - EN_CLASSES

# Forbidden transitions (C109, from t2_forbidden_pair_pattern.json)
FORBIDDEN_PAIRS = [
    (10, 12), (10, 17), (11, 12), (11, 17),  # CC->CC
    (12, 23), (12, 9), (17, 23), (17, 9),    # CC->FQ
    (10, 23), (10, 9), (11, 23), (11, 9),    # CC->FQ
    (32, 12), (32, 17), (31, 12), (31, 17),  # EN->CC
    (9, 23),                                   # FQ->FQ
]

# Depleted pairs (from T9 holdout stability)
DEPLETED_PAIRS = [
    (11, 36), (13, 40), (9, 33), (24, 30), (14, 46), (9, 27),
    (9, 32), (5, 34), (47, 11), (19, 33), (7, 32), (11, 14),
    (3, 33), (33, 38), (18, 28), (7, 47), (13, 5), (10, 28),
]

RANKS_TO_TEST = [2, 4, 6, 8, 10, 12]
N_CV_FOLDS = 20
N_CV_HOLDOUT = 5
N_PERM = 1000

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'


def get_suffix_group(suffix):
    for group, members in SUFFIX_GROUPS.items():
        if suffix in members:
            return group
    return 'OTHER'


# ── Data Loading (reused from Phase 342) ──────────────────────────────

def load_token_to_class():
    path = Path(__file__).resolve().parents[2] / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    return data['token_to_class']


def load_regime_assignments():
    path = Path(__file__).resolve().parents[2] / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    path = Path(__file__).resolve().parents[2] / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)
    return data['t2_archetype_discovery']


def load_affordance_table():
    path = PROJECT_ROOT / 'data' / 'middle_affordance_table.json'
    with open(path) as f:
        data = json.load(f)
    middles_data = data.get('middles', {})
    result = {}
    for mid, info in middles_data.items():
        result[mid] = {
            'affordance_bin': info.get('affordance_bin'),
            'affordance_label': info.get('affordance_label', ''),
            'radial_depth': info.get('radial_depth', 0),
            'token_frequency': info.get('token_frequency', 0),
        }
    return result


def build_corpus_data(token_to_class):
    """Build enriched token-level corpus data."""
    tx = Transcript()
    morph = Morphology()

    tokens = []
    folio_sections = {}

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue

        cls = token_to_class.get(w)
        if cls is None:
            continue
        state = CLASS_TO_STATE.get(int(cls))
        if state is None:
            continue

        m = morph.extract(w)
        prefix = m.prefix if m.prefix else '__BARE__'
        middle = m.middle if m.middle else None
        suffix = m.suffix if m.suffix else None

        if middle is None:
            continue

        tokens.append({
            'word': w,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'cls': int(cls),
            'state': state,
        })
        folio_sections[token.folio] = token.section

    print(f"  Corpus tokens loaded: {len(tokens)}")
    print(f"  Folios: {len(folio_sections)}")
    return tokens, folio_sections


# ── Tensor Construction ───────────────────────────────────────────────

def build_bigram_tensor(tokens, affordance_table, folio_filter=None, forced_prefixes=None):
    """Build 4-way count tensor T[PREFIX, MIDDLE_BIN, SUFFIX_GROUP, SUCCESSOR_CLASS].

    Args:
        forced_prefixes: if provided, use these PREFIXes (for CV consistency)
    """
    line_tokens = defaultdict(list)
    for t in tokens:
        if folio_filter is not None and t['folio'] not in folio_filter:
            continue
        line_tokens[(t['folio'], t['line'])].append(t)

    if forced_prefixes is not None:
        selected_prefixes = sorted(forced_prefixes)
    else:
        prefix_counts = Counter()
        for t in tokens:
            if folio_filter is not None and t['folio'] not in folio_filter:
                continue
            prefix_counts[t['prefix']] += 1

        eligible = [(p, c) for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS]
        eligible.sort(key=lambda x: -x[1])
        selected_prefixes = sorted([p for p, _ in eligible[:MAX_PREFIXES]])

    prefix_idx = {p: i for i, p in enumerate(selected_prefixes)}
    n_prefixes = len(selected_prefixes)

    n_bins = 10
    class_labels = list(range(1, N_CLASSES + 1))
    class_idx = {c: i for i, c in enumerate(class_labels)}

    tensor = np.zeros((n_prefixes, n_bins, N_SUFFIX_GROUPS, N_CLASSES), dtype=float)
    n_bigrams = 0

    for (folio, line), tok_list in line_tokens.items():
        for i in range(len(tok_list) - 1):
            curr = tok_list[i]
            succ = tok_list[i + 1]

            p = curr['prefix']
            if p not in prefix_idx:
                continue

            mid = curr['middle']
            aff = affordance_table.get(mid)
            if aff is None or aff.get('affordance_bin') is None:
                continue
            b = aff['affordance_bin']
            if b < 0 or b >= n_bins:
                continue

            sg = get_suffix_group(curr['suffix'])
            sg_i = SUFFIX_GROUP_ORDER.index(sg)

            succ_cls = succ['cls']
            if succ_cls not in class_idx:
                continue

            tensor[prefix_idx[p], b, sg_i, class_idx[succ_cls]] += 1
            n_bigrams += 1

    return tensor, selected_prefixes, class_labels, n_bigrams


# ── Utility Functions ─────────────────────────────────────────────────

def gini_coefficient(arr):
    """Compute Gini coefficient of a non-negative array."""
    arr = np.array(arr, dtype=float)
    if arr.sum() == 0:
        return 0.0
    arr = np.sort(arr)
    n = len(arr)
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) - (n + 1) * np.sum(arr)) / (n * np.sum(arr)))


def cosine_similarity(a, b):
    """Cosine similarity between two vectors."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def shannon_entropy(arr):
    """Shannon entropy in bits."""
    arr = np.array(arr, dtype=float)
    s = arr.sum()
    if s <= 0:
        return 0.0
    p = arr / s
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def ols_r2(X, y):
    """OLS R-squared."""
    X_aug = np.hstack([np.ones((len(y), 1)), X])
    try:
        beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
        y_pred = X_aug @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0
    except Exception:
        return 0


def build_folio_axm_self(tokens):
    """Compute per-folio AXM self-transition probability."""
    line_states = defaultdict(list)
    for t in tokens:
        line_states[(t['folio'], t['line'])].append(t['state'])

    folio_trans = defaultdict(lambda: np.zeros((N_STATES, N_STATES)))
    for (folio, line), states in line_states.items():
        for i in range(len(states) - 1):
            folio_trans[folio][STATE_IDX[states[i]], STATE_IDX[states[i+1]]] += 1

    result = {}
    for folio, mat in folio_trans.items():
        row = mat[STATE_IDX['AXM']]
        s = row.sum()
        result[folio] = float(row[STATE_IDX['AXM']] / s) if s > 0 else 0
    return result


def compute_folio_cp_scores(tokens, affordance_table, prefix_labels, cp_factors, cp_weights):
    """Compute per-folio tensor personality vectors (token-weighted centroid in CP space)."""
    prefix_idx = {p: i for i, p in enumerate(prefix_labels)}
    prefix_factors, bin_factors, suffix_factors, class_factors = cp_factors
    rank = len(cp_weights)

    folio_scores = defaultdict(lambda: {'sum': np.zeros(rank), 'count': 0})

    for t in tokens:
        p = t['prefix']
        if p not in prefix_idx:
            continue

        mid = t['middle']
        aff = affordance_table.get(mid)
        if aff is None or aff.get('affordance_bin') is None:
            continue
        b = aff['affordance_bin']
        if b < 0 or b >= 10:
            continue

        sg = get_suffix_group(t['suffix'])
        sg_i = SUFFIX_GROUP_ORDER.index(sg)

        p_i = prefix_idx[p]
        score = np.array([
            float(cp_weights[r]) *
            float(prefix_factors[p_i, r]) *
            float(bin_factors[b, r]) *
            float(suffix_factors[sg_i, r])
            for r in range(rank)
        ])

        folio_scores[t['folio']]['sum'] += score
        folio_scores[t['folio']]['count'] += 1

    result = {}
    for folio, data in folio_scores.items():
        if data['count'] >= 10:
            result[folio] = data['sum'] / data['count']
    return result


def compute_delta_r2(tokens, affordance_table, prefix_labels, cp_factors,
                     cp_weights, folio_sections, folio_axm_self, regime_map):
    """Compute incremental R² of CP factors over REGIME+section baseline."""
    folio_scores = compute_folio_cp_scores(tokens, affordance_table, prefix_labels,
                                            cp_factors, cp_weights)

    folios = sorted(set(folio_scores.keys()) & set(folio_axm_self.keys())
                    & set(regime_map.keys()) & set(folio_sections.keys()))

    if len(folios) < 10:
        return 0.0, 0.0, 0.0, len(folios)

    y = np.array([folio_axm_self[f] for f in folios])
    regimes = [regime_map.get(f, 0) for f in folios]
    sections = [folio_sections.get(f, 'UNKNOWN') for f in folios]

    unique_regimes = sorted(set(regimes))
    unique_sections = sorted(set(sections))
    X_base = np.zeros((len(folios), len(unique_regimes) + len(unique_sections)))
    for i, f in enumerate(folios):
        r_idx = unique_regimes.index(regimes[i])
        X_base[i, r_idx] = 1
        s_idx = unique_sections.index(sections[i])
        X_base[i, len(unique_regimes) + s_idx] = 1

    rank = len(cp_weights)
    X_cp = np.array([folio_scores[f][:rank] for f in folios])
    X_full = np.hstack([X_base, X_cp])

    r2_base = ols_r2(X_base, y)
    r2_full = ols_r2(X_full, y)
    delta_r2 = r2_full - r2_base

    return r2_base, r2_full, delta_r2, len(folios)


# ── Sub-Analysis 1: Factor Semantic Identity ──────────────────────────

def run_sub1(tensor, tokens, affordance_table, prefix_labels, class_labels, folio_sections):
    """Characterize all 8 CP factors and perform deep dives on Factors 2 and 3."""
    print("\n" + "=" * 60)
    print("Sub-Analysis 1: Factor Semantic Identity")
    print("=" * 60)

    # Fit rank-8 CP
    tl_tensor = tl.tensor(tensor)
    cp_result = non_negative_parafac(tl_tensor, rank=CP_RANK, init='random',
                                      n_iter_max=300, tol=1e-6, random_state=42)
    cp_weights, cp_factors = cp_result

    prefix_factors = cp_factors[0]   # (n_prefixes, 8)
    bin_factors = cp_factors[1]      # (10, 8)
    suffix_factors = cp_factors[2]   # (5, 8)
    class_factors = cp_factors[3]    # (49, 8)

    # Verify reconstruction
    recon = tl.cp_to_tensor(cp_result)
    frob_total = tl.norm(tl_tensor)
    rel_error = float(tl.norm(tl_tensor - recon) / frob_total)
    var_explained = 1.0 - rel_error ** 2
    print(f"\n  Rank-8 variance explained: {var_explained:.4f}")
    print(f"  Weights: {[f'{w:.3f}' for w in cp_weights]}")

    # ── Characterize all 8 factors ──
    print("\n  Factor Profiles:")
    factor_profiles = []

    class_arr = np.array(class_labels)
    prefix_ginis = []

    for r in range(CP_RANK):
        # PREFIX loadings
        pfx_loadings = prefix_factors[:, r]
        pfx_sorted_idx = np.argsort(-pfx_loadings)[:3]
        pfx_top3 = [(prefix_labels[i], float(pfx_loadings[i])) for i in pfx_sorted_idx]
        pfx_gini = gini_coefficient(pfx_loadings)
        prefix_ginis.append(pfx_gini)

        # BIN loadings
        bin_loadings = bin_factors[:, r]
        bin_sorted_idx = np.argsort(-bin_loadings)[:3]
        bin_top3 = [(int(i), float(bin_loadings[i])) for i in bin_sorted_idx]
        bin_gini = gini_coefficient(bin_loadings)

        # SUFFIX loadings
        sfx_loadings = suffix_factors[:, r]
        sfx_dominant_idx = int(np.argmax(sfx_loadings))
        sfx_dominant = SUFFIX_GROUP_ORDER[sfx_dominant_idx]
        sfx_entropy = shannon_entropy(sfx_loadings)

        # CLASS loadings — per-macro-state mean
        cls_loadings = class_factors[:, r]
        state_means = {}
        for state, state_classes in MACRO_STATE_PARTITION.items():
            idxs = [i for i, c in enumerate(class_labels) if c in state_classes]
            if idxs:
                state_means[state] = float(np.mean(cls_loadings[idxs]))
            else:
                state_means[state] = 0.0
        dominant_state = max(state_means, key=state_means.get)

        profile = {
            'factor': r,
            'weight': float(cp_weights[r]),
            'prefix_top3': pfx_top3,
            'prefix_gini': pfx_gini,
            'bin_top3': bin_top3,
            'bin_gini': bin_gini,
            'suffix_dominant': sfx_dominant,
            'suffix_entropy': sfx_entropy,
            'class_macro_state_means': state_means,
            'class_dominant_state': dominant_state,
        }
        factor_profiles.append(profile)

        print(f"\n  Factor {r} (weight={cp_weights[r]:.3f}):")
        print(f"    PREFIX top3: {pfx_top3}, Gini={pfx_gini:.3f}")
        print(f"    BIN top3: {bin_top3}, Gini={bin_gini:.3f}")
        print(f"    SUFFIX dominant: {sfx_dominant}, entropy={sfx_entropy:.3f}")
        print(f"    CLASS dominant state: {dominant_state}")
        print(f"    State means: {', '.join(f'{s}={v:.4f}' for s,v in state_means.items())}")

    # ── S4: PREFIX selectivity (mean Gini) ──
    mean_gini = float(np.mean(prefix_ginis))
    s4_pass = mean_gini > 0.30
    print(f"\n  S4 (mean PREFIX Gini > 0.30): {mean_gini:.4f} -> {'PASS' if s4_pass else 'FAIL'}")

    # ── Factor 2 deep dive ──
    print("\n  --- Factor 2 Deep Dive (rho=-0.738 with AXM) ---")

    f2_class = class_factors[:, 2]

    # S1: Cosine with gatekeeper indicator
    gk_indicator = np.array([1.0 if c in GATEKEEPER_CLASSES else 0.0 for c in class_labels])
    gk_cosine = cosine_similarity(f2_class, gk_indicator)
    s1_pass = abs(gk_cosine) > 0.30
    print(f"    Gatekeeper cosine: {gk_cosine:.4f}")
    print(f"    S1 (|cosine| > 0.30): {'PASS' if s1_pass else 'FAIL'}")

    # S2: Frequency gradient null check
    # Build per-class token frequency from corpus
    class_freq = Counter()
    for t in tokens:
        class_freq[t['cls']] += 1
    freq_vector = np.array([class_freq.get(c, 0) for c in class_labels], dtype=float)

    if np.std(f2_class) > 1e-10 and np.std(freq_vector) > 1e-10:
        freq_rho, freq_p = stats.spearmanr(f2_class, freq_vector)
    else:
        freq_rho, freq_p = 0.0, 1.0

    # S2 PASSES if frequency correlation is LOW (meaning Factor 2 is NOT just frequency)
    s2_pass = abs(freq_rho) < 0.60
    print(f"    Frequency Spearman: rho={freq_rho:.4f}, p={freq_p:.4f}")
    print(f"    S2 (|rho_freq| < 0.60 = not frequency artifact): {'PASS' if s2_pass else 'FAIL'}")

    # Additional: cosine with specific state indicators
    f2_state_cosines = {}
    for state, state_classes in MACRO_STATE_PARTITION.items():
        indicator = np.array([1.0 if c in state_classes else 0.0 for c in class_labels])
        cos = cosine_similarity(f2_class, indicator)
        f2_state_cosines[state] = cos
    print(f"    State cosines: {', '.join(f'{s}={v:.3f}' for s,v in f2_state_cosines.items())}")

    factor2_results = {
        'gatekeeper_cosine': gk_cosine,
        'frequency_spearman_rho': float(freq_rho),
        'frequency_spearman_p': float(freq_p),
        'state_cosines': {k: float(v) for k, v in f2_state_cosines.items()},
        'class_loadings': [float(x) for x in f2_class],
    }

    # ── Factor 3 deep dive ──
    print("\n  --- Factor 3 Deep Dive (rho=-0.011 with AXM) ---")

    f3_class = class_factors[:, 3]

    # Build structural indicator vectors
    indicators = {
        'FL_HAZ': np.array([1.0 if c in FL_HAZ_CLASSES else 0.0 for c in class_labels]),
        'FL_SAFE': np.array([1.0 if c in FL_SAFE_CLASSES else 0.0 for c in class_labels]),
        'FL_HAZ_vs_SAFE': np.array([1.0 if c in FL_HAZ_CLASSES else (-1.0 if c in FL_SAFE_CLASSES else 0.0)
                                     for c in class_labels]),
        'CC': np.array([1.0 if c in CC_CLASSES else 0.0 for c in class_labels]),
        'FQ': np.array([1.0 if c in FQ_CLASSES else 0.0 for c in class_labels]),
        'EN_vs_AX': np.array([1.0 if c in EN_CLASSES else (-1.0 if c in AX_CLASSES else 0.0)
                               for c in class_labels]),
        'gatekeeper': gk_indicator,
        'frequency': freq_vector / (freq_vector.max() + 1e-10),  # Normalized
    }

    f3_cosines = {}
    for name, vec in indicators.items():
        cos = cosine_similarity(f3_class, vec)
        f3_cosines[name] = cos
        print(f"    {name} cosine: {cos:.4f}")

    best_indicator = max(f3_cosines, key=lambda k: abs(f3_cosines[k]))
    best_cosine = abs(f3_cosines[best_indicator])
    s3_pass = best_cosine > 0.40
    print(f"    Best: {best_indicator} (|cos|={best_cosine:.4f})")
    print(f"    S3 (max |cosine| > 0.40): {'PASS' if s3_pass else 'FAIL'}")

    # Factor 3 state cosines
    f3_state_cosines = {}
    for state, state_classes in MACRO_STATE_PARTITION.items():
        indicator = np.array([1.0 if c in state_classes else 0.0 for c in class_labels])
        cos = cosine_similarity(f3_class, indicator)
        f3_state_cosines[state] = cos
    print(f"    State cosines: {', '.join(f'{s}={v:.3f}' for s,v in f3_state_cosines.items())}")

    factor3_results = {
        'indicator_cosines': {k: float(v) for k, v in f3_cosines.items()},
        'best_indicator': best_indicator,
        'best_cosine': best_cosine,
        'state_cosines': {k: float(v) for k, v in f3_state_cosines.items()},
        'class_loadings': [float(x) for x in f3_class],
    }

    # ── Also report AXM correlation for all factors (verify C1020) ──
    folio_axm_self = build_folio_axm_self(tokens)
    regime_map = load_regime_assignments()
    folio_scores = compute_folio_cp_scores(tokens, affordance_table, prefix_labels,
                                            cp_factors, cp_weights)
    folios = sorted(set(folio_scores.keys()) & set(folio_axm_self.keys()))
    if len(folios) >= 10:
        X_scores = np.array([folio_scores[f] for f in folios])
        axm_vals = np.array([folio_axm_self[f] for f in folios])
        factor_rhos = []
        for d in range(CP_RANK):
            if np.std(X_scores[:, d]) > 1e-10:
                rho, p = stats.spearmanr(X_scores[:, d], axm_vals)
            else:
                rho, p = 0.0, 1.0
            factor_rhos.append({'factor': d, 'rho': float(rho), 'p': float(p)})
        print(f"\n  AXM correlations (verification):")
        for fr in factor_rhos:
            print(f"    Factor {fr['factor']}: rho={fr['rho']:.4f}")
    else:
        factor_rhos = []

    return {
        'var_explained': var_explained,
        'factor_profiles': factor_profiles,
        'factor2_deep_dive': factor2_results,
        'factor3_deep_dive': factor3_results,
        'axm_correlations': factor_rhos,
        's1': {'value': abs(gk_cosine), 'description': 'Factor 2 gatekeeper cosine', 'pass': s1_pass},
        's2': {'value': abs(freq_rho), 'description': 'Factor 2 frequency rho (PASS = low)', 'pass': s2_pass},
        's3': {'value': best_cosine, 'description': f'Factor 3 best indicator ({best_indicator})', 'pass': s3_pass},
        's4': {'value': mean_gini, 'description': 'Mean PREFIX Gini', 'pass': s4_pass},
    }, cp_result  # Return cp_result for reuse


# ── Sub-Analysis 2: Rank Sensitivity Ablation ─────────────────────────

def run_sub2(tensor, tokens, affordance_table, prefix_labels, class_labels,
             folio_sections):
    """Test rank sensitivity: is rank-8 structurally necessary?"""
    print("\n" + "=" * 60)
    print("Sub-Analysis 2: Rank Sensitivity Ablation")
    print("=" * 60)

    tl_tensor = tl.tensor(tensor)
    frob_total = float(tl.norm(tl_tensor))

    folio_axm_self = build_folio_axm_self(tokens)
    regime_map = load_regime_assignments()

    true_labels = [STATE_IDX.get(CLASS_TO_STATE.get(c), -1) for c in class_labels]

    # All forbidden + depleted pairs combined
    all_constrained_pairs = set(FORBIDDEN_PAIRS + DEPLETED_PAIRS)

    rank_results = {}

    for rank in RANKS_TO_TEST:
        print(f"\n  Rank {rank}:")

        # Fit CP (CP rank is not bounded by min(dim) — unlike SVD)
        effective_rank = rank

        try:
            cp_result = non_negative_parafac(tl_tensor, rank=effective_rank, init='random',
                                              n_iter_max=300, tol=1e-6, random_state=42)
            cp_weights, cp_factors = cp_result

            # Variance explained
            recon = tl.cp_to_tensor(cp_result)
            rel_error = float(tl.norm(tl_tensor - recon) / frob_total)
            var_explained = 1.0 - rel_error ** 2
            print(f"    Variance: {var_explained:.4f}")

            # ARI vs C1010
            class_factors = cp_factors[3]  # (49, rank)
            Z = linkage(class_factors, method='ward')
            cl = fcluster(Z, t=6, criterion='maxclust')
            ari = adjusted_rand_score(true_labels, cl)
            print(f"    ARI vs C1010: {ari:.4f}")

            # ΔR²
            r2_base, r2_full, delta_r2, n_fol = compute_delta_r2(
                tokens, affordance_table, prefix_labels, cp_factors,
                cp_weights, folio_sections, folio_axm_self, regime_map)
            print(f"    deltaR2: {delta_r2:.4f} (base={r2_base:.4f}, full={r2_full:.4f}, n={n_fol})")

            # Forbidden transition compliance
            # Reconstruct class-class transition weights from tensor
            # Sum over PREFIX, BIN, SUFFIX: get T_marginal[current_class_proxy, successor_class]
            # Actually: the tensor is T[PREFIX, BIN, SUFFIX, SUCCESSOR_CLASS]
            # The class of the current token is embedded in PREFIX+BIN+SUFFIX, not explicit
            # For compliance, check the reconstructed tensor mass at forbidden pairs
            # by computing class factor similarity matrix
            S = class_factors @ class_factors.T  # (49, 49) similarity
            n_compliant = 0
            n_checked = 0
            for src, tgt in all_constrained_pairs:
                src_idx = class_labels.index(src) if src in class_labels else None
                tgt_idx = class_labels.index(tgt) if tgt in class_labels else None
                if src_idx is not None and tgt_idx is not None:
                    n_checked += 1
                    # Compliant if similarity is low relative to mean
                    mean_s = np.mean(S)
                    if S[src_idx, tgt_idx] < 0.5 * mean_s:
                        n_compliant += 1

            compliance = n_compliant / n_checked if n_checked > 0 else 0
            print(f"    Compliance: {compliance:.4f} ({n_compliant}/{n_checked})")

            rank_results[str(rank)] = {
                'effective_rank': effective_rank,
                'variance': var_explained,
                'ari': float(ari),
                'delta_r2': delta_r2,
                'r2_base': r2_base,
                'r2_full': r2_full,
                'n_folios': n_fol,
                'compliance': compliance,
                'n_compliant': n_compliant,
                'n_checked': n_checked,
            }

        except Exception as e:
            print(f"    FAILED: {e}")
            rank_results[str(rank)] = {
                'effective_rank': effective_rank,
                'variance': 0.0, 'ari': 0.0, 'delta_r2': 0.0,
                'compliance': 0.0, 'error': str(e),
            }

    # ── Cross-validation ──
    print(f"\n  Cross-validation: {N_CV_FOLDS} folds, {N_CV_HOLDOUT} folios held out")

    all_folios = sorted(set(t['folio'] for t in tokens))
    rng = np.random.default_rng(42)

    cv_results = {str(r): [] for r in RANKS_TO_TEST}

    for fold in range(N_CV_FOLDS):
        holdout_idx = rng.choice(len(all_folios), N_CV_HOLDOUT, replace=False)
        holdout_folios = set(all_folios[i] for i in holdout_idx)
        train_folios = set(all_folios) - holdout_folios

        # Build train tensor with full PREFIX set forced for consistency
        train_tensor, train_pfx, _, n_train = build_bigram_tensor(
            tokens, affordance_table, train_folios, forced_prefixes=prefix_labels)
        # Build test tensor with same PREFIX set
        test_tensor, _, _, n_test = build_bigram_tensor(
            tokens, affordance_table, holdout_folios, forced_prefixes=prefix_labels)

        if n_train < 100 or n_test < 10:
            continue

        tl_train = tl.tensor(train_tensor)
        tl_test = tl.tensor(test_tensor)
        frob_test = float(tl.norm(tl_test))

        if frob_test < 1e-10:
            continue

        for rank in RANKS_TO_TEST:
            try:
                cp_train = non_negative_parafac(tl_train, rank=rank, init='random',
                                                 n_iter_max=200, tol=1e-5, random_state=fold)
                recon = tl.cp_to_tensor(cp_train)
                # Reconstruction error on test: use cosine similarity between
                # flattened test tensor and reconstruction (scale-invariant)
                test_flat = test_tensor.flatten()
                recon_flat = recon.flatten()
                test_norm = np.linalg.norm(test_flat)
                recon_norm = np.linalg.norm(recon_flat)
                if test_norm > 1e-10 and recon_norm > 1e-10:
                    cv_cosine = float(np.dot(test_flat, recon_flat) / (test_norm * recon_norm))
                else:
                    cv_cosine = 0.0
                cv_results[str(rank)].append(cv_cosine)
            except Exception:
                pass

        if (fold + 1) % 5 == 0:
            print(f"    Fold {fold+1}/{N_CV_FOLDS}")

    cv_summary = {}
    for r_str, vals in cv_results.items():
        if vals:
            cv_summary[r_str] = {
                'mean_cv_cosine': float(np.mean(vals)),
                'std_cv_cosine': float(np.std(vals)),
                'n_folds': len(vals),
            }
        else:
            cv_summary[r_str] = {'mean_cv_cosine': 0.0, 'std_cv_cosine': 0.0, 'n_folds': 0}

    print("\n  CV Results:")
    for r_str in sorted(cv_summary.keys(), key=int):
        cv = cv_summary[r_str]
        print(f"    Rank {r_str}: CV cosine = {cv['mean_cv_cosine']:.4f} +/- {cv['std_cv_cosine']:.4f} (n={cv['n_folds']})")

    # ── Predictions ──
    dr2_8 = rank_results.get('8', {}).get('delta_r2', 0)
    dr2_6 = rank_results.get('6', {}).get('delta_r2', 0)
    dr2_10 = rank_results.get('10', {}).get('delta_r2', 0)

    # R1: ΔR²(8) / ΔR²(6) > 1.5
    r1_ratio = dr2_8 / dr2_6 if dr2_6 > 0 else float('inf')
    r1_pass = r1_ratio > 1.5
    print(f"\n  R1 (deltaR2 ratio 8/6 > 1.5): {r1_ratio:.4f} -> {'PASS' if r1_pass else 'FAIL'}")

    # R2: CV cosine gap (rank-8 minus rank-6) > 0.05
    cv_8 = cv_summary.get('8', {}).get('mean_cv_cosine', 0)
    cv_6 = cv_summary.get('6', {}).get('mean_cv_cosine', 0)
    cv_gap = cv_8 - cv_6
    r2_pass = cv_gap > 0.05
    print(f"  R2 (CV cosine gap 8-6 > 0.05): {cv_gap:.4f} -> {'PASS' if r2_pass else 'FAIL'}")

    # R3: ΔR²(10) - ΔR²(8) < 0.03 (diminishing returns)
    dr2_gap_10_8 = dr2_10 - dr2_8
    r3_pass = dr2_gap_10_8 < 0.03
    print(f"  R3 (deltaR2 gap 10-8 < 0.03): {dr2_gap_10_8:.4f} -> {'PASS' if r3_pass else 'FAIL'}")

    # R4: Forbidden transition compliance increases with rank
    compliance_vals = [(int(r), rank_results[r].get('compliance', 0)) for r in sorted(rank_results.keys(), key=int)]
    if len(compliance_vals) >= 3:
        ranks_arr = np.array([x[0] for x in compliance_vals])
        comp_arr = np.array([x[1] for x in compliance_vals])
        comp_rho, comp_p = stats.spearmanr(ranks_arr, comp_arr)
    else:
        comp_rho = 0.0
    r4_pass = comp_rho > 0.80
    print(f"  R4 (compliance-rank Spearman > 0.80): {comp_rho:.4f} -> {'PASS' if r4_pass else 'FAIL'}")

    return {
        'rank_results': rank_results,
        'cv_results': cv_summary,
        'r1': {'value': float(r1_ratio), 'description': 'deltaR2 ratio rank-8/rank-6', 'pass': r1_pass},
        'r2': {'value': float(cv_gap), 'description': 'CV cosine gap 8-6', 'pass': r2_pass},
        'r3': {'value': float(dr2_gap_10_8), 'description': 'deltaR2 gap 10-8', 'pass': r3_pass},
        'r4': {'value': float(comp_rho), 'description': 'Compliance-rank Spearman', 'pass': r4_pass},
    }


# ── Sub-Analysis 3: Constrained Consistency Test ──────────────────────

def run_sub3(tensor, class_labels):
    """Test whether hazard-filtered class similarity converges toward C1010."""
    print("\n" + "=" * 60)
    print("Sub-Analysis 3: Constrained Consistency Test")
    print("=" * 60)
    print("  (CONSISTENCY test, NOT derivation — C1010 is frozen input)")

    # Fit rank-8 CP
    tl_tensor = tl.tensor(tensor)
    cp_result = non_negative_parafac(tl_tensor, rank=CP_RANK, init='random',
                                      n_iter_max=300, tol=1e-6, random_state=42)
    cp_weights, cp_factors = cp_result
    class_factors = cp_factors[3]  # (49, 8)

    frob_total = float(tl.norm(tl_tensor))
    recon = tl.cp_to_tensor(cp_result)
    rel_error = float(tl.norm(tl_tensor - recon) / frob_total)
    var_explained = 1.0 - rel_error ** 2

    # Compute class similarity matrix
    # Normalize class factors for cosine-like similarity
    norms = np.linalg.norm(class_factors, axis=1, keepdims=True)
    norms = np.where(norms < 1e-10, 1.0, norms)
    class_normed = class_factors / norms
    S = class_normed @ class_normed.T  # (49, 49) cosine similarity

    # True C1010 labels
    true_labels = np.array([STATE_IDX.get(CLASS_TO_STATE.get(c), -1) for c in class_labels])

    # Unconstrained: cluster raw similarity
    Z_raw = linkage(class_factors, method='ward')
    cl_raw = fcluster(Z_raw, t=6, criterion='maxclust')
    ari_unconstrained = adjusted_rand_score(true_labels, cl_raw)
    print(f"\n  Unconstrained ARI: {ari_unconstrained:.4f}")

    # Apply constraint mask
    S_masked = S.copy()
    all_constrained = set(FORBIDDEN_PAIRS + DEPLETED_PAIRS)
    n_zeroed = 0
    for src, tgt in all_constrained:
        src_idx = class_labels.index(src) if src in class_labels else None
        tgt_idx = class_labels.index(tgt) if tgt in class_labels else None
        if src_idx is not None and tgt_idx is not None:
            S_masked[src_idx, tgt_idx] = 0.0
            S_masked[tgt_idx, src_idx] = 0.0
            n_zeroed += 1

    print(f"  Zeroed {n_zeroed} constrained pairs in similarity matrix")

    # Convert masked similarity to distance for clustering
    # distance = 1 - similarity (clip to [0, 2])
    D_masked = np.clip(1.0 - S_masked, 0, 2)
    np.fill_diagonal(D_masked, 0)

    # Cluster
    from scipy.spatial.distance import squareform
    D_condensed = squareform(D_masked, checks=False)
    Z_masked = linkage(D_condensed, method='ward')
    cl_masked = fcluster(Z_masked, t=6, criterion='maxclust')
    ari_constrained = adjusted_rand_score(true_labels, cl_masked)
    print(f"  Constrained ARI: {ari_constrained:.4f}")

    # C1: Constrained ARI > unconstrained (0.053)
    c1_pass = ari_constrained > 0.10
    print(f"  C1 (constrained ARI > 0.10): {ari_constrained:.4f} -> {'PASS' if c1_pass else 'FAIL'}")

    # ── Null model: random constraint sets ──
    print(f"\n  Running {N_PERM} permutation controls...")
    rng = np.random.default_rng(42)

    # Pool of all possible class pairs (excluding diagonal)
    all_pairs = [(i, j) for i in range(49) for j in range(49) if i != j]
    n_to_zero = n_zeroed  # Same number of pairs as real constraints

    null_aris = []
    for perm in range(N_PERM):
        # Random subset of pairs
        perm_idx = rng.choice(len(all_pairs), n_to_zero, replace=False)
        S_perm = S.copy()
        for idx in perm_idx:
            i, j = all_pairs[idx]
            S_perm[i, j] = 0.0
            S_perm[j, i] = 0.0

        D_perm = np.clip(1.0 - S_perm, 0, 2)
        np.fill_diagonal(D_perm, 0)
        try:
            D_cond = squareform(D_perm, checks=False)
            Z_perm = linkage(D_cond, method='ward')
            cl_perm = fcluster(Z_perm, t=6, criterion='maxclust')
            null_aris.append(adjusted_rand_score(true_labels, cl_perm))
        except Exception:
            null_aris.append(0.0)

        if (perm + 1) % 200 == 0:
            print(f"    Permutation {perm+1}/{N_PERM}: mean null ARI={np.mean(null_aris):.4f}")

    null_mean = float(np.mean(null_aris))
    null_std = float(np.std(null_aris))
    z_score = (ari_constrained - null_mean) / null_std if null_std > 0 else 0
    p_value = sum(1 for na in null_aris if na >= ari_constrained) / len(null_aris)

    print(f"\n  Null: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"  z={z_score:.2f}, p={p_value:.4f}")

    # C2: z > 2.0
    c2_pass = z_score > 2.0
    print(f"  C2 (z > 2.0): {z_score:.2f} -> {'PASS' if c2_pass else 'FAIL'}")

    # C3: Filtered variance explained (tensor reconstruction still valid)
    c3_pass = var_explained > 0.85
    print(f"  C3 (var_explained > 0.85): {var_explained:.4f} -> {'PASS' if c3_pass else 'FAIL'}")

    return {
        'unconstrained_ari': float(ari_unconstrained),
        'constrained_ari': float(ari_constrained),
        'n_zeroed_pairs': n_zeroed,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': float(z_score),
        'p_value': float(p_value),
        'var_explained': var_explained,
        'c1': {'value': float(ari_constrained), 'description': 'Constrained ARI > 0.10', 'pass': c1_pass},
        'c2': {'value': float(z_score), 'description': 'z-score > 2.0 vs null', 'pass': c2_pass},
        'c3': {'value': var_explained, 'description': 'Reconstruction variance > 0.85', 'pass': c3_pass},
    }


# ── Synthesis ─────────────────────────────────────────────────────────

def synthesize(sub1, sub2, sub3):
    """Combine sub-analysis verdicts."""
    print("\n" + "=" * 60)
    print("Synthesis")
    print("=" * 60)

    predictions = {}

    # Sub-1 predictions
    for key in ['s1', 's2', 's3', 's4']:
        p = sub1[key]
        predictions[key.upper()] = {
            'description': p['description'],
            'result': p['pass'],
            'value': p['value'],
        }

    # Sub-2 predictions
    for key in ['r1', 'r2', 'r3', 'r4']:
        p = sub2[key]
        predictions[key.upper()] = {
            'description': p['description'],
            'result': p['pass'],
            'value': p['value'],
        }

    # Sub-3 predictions
    for key in ['c1', 'c2', 'c3']:
        p = sub3[key]
        predictions[key.upper()] = {
            'description': p['description'],
            'result': p['pass'],
            'value': p['value'],
        }

    n_pass = sum(1 for p in predictions.values() if p['result'])
    n_total = len(predictions)

    # Sub-1 verdict
    s1_pass = sub1['s1']['pass']
    s2_pass = sub1['s2']['pass']
    s3_pass = sub1['s3']['pass']

    if s1_pass and s2_pass:
        sub1_verdict = 'GATEKEEPER_ENCODED'
    elif not s1_pass and s2_pass:
        sub1_verdict = 'DYNAMICS_NOVEL'
    elif not s2_pass:
        sub1_verdict = 'FREQUENCY_ARTIFACT'
    else:
        sub1_verdict = 'DYNAMICS_NOVEL'

    if s3_pass:
        sub1_verdict += '+FACTOR3_IDENTIFIED'
    else:
        sub1_verdict += '+FACTOR3_CRYPTIC'

    # Sub-2 verdict
    r1_pass = sub2['r1']['pass']
    r3_pass = sub2['r3']['pass']

    if r1_pass and r3_pass:
        sub2_verdict = 'RANK_NECESSARY'
    elif not r1_pass:
        sub2_verdict = 'RANK_CONTINUOUS'
    elif not r3_pass:
        sub2_verdict = 'RANK_UNDERFIT'
    else:
        sub2_verdict = 'RANK_INDETERMINATE'

    # Sub-3 verdict
    c1_pass = sub3['c1']['pass']
    c2_pass = sub3['c2']['pass']

    if c1_pass and c2_pass:
        sub3_verdict = 'ARCHITECTURALLY_CONSISTENT'
    else:
        sub3_verdict = 'ORTHOGONAL_CONFIRMED'

    verdict = f"{sub1_verdict}; {sub2_verdict}; {sub3_verdict}"

    print(f"\n  Sub-1: {sub1_verdict}")
    print(f"  Sub-2: {sub2_verdict}")
    print(f"  Sub-3: {sub3_verdict}")
    print(f"\n  Predictions: {n_pass}/{n_total} passed")
    print(f"\n  VERDICT: {verdict}")

    for key, p in sorted(predictions.items()):
        status = 'PASS' if p['result'] else 'FAIL'
        print(f"    {key}: {p['description']} = {p['value']:.4f} -> {status}")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': n_total,
        'sub_1_verdict': sub1_verdict,
        'sub_2_verdict': sub2_verdict,
        'sub_3_verdict': sub3_verdict,
        'verdict': verdict,
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    print("=" * 60)
    print("Phase 344: CP_FACTOR_CHARACTERIZATION")
    print("=" * 60)

    # Load data
    print("\n[0/4] Loading data...")
    token_to_class = load_token_to_class()
    affordance_table = load_affordance_table()
    tokens, folio_sections = build_corpus_data(token_to_class)

    # Build tensor
    print("\n[0/4] Building tensor...")
    tensor, prefix_labels, class_labels, n_bigrams = build_bigram_tensor(
        tokens, affordance_table)
    print(f"  Tensor shape: {tensor.shape}")
    print(f"  Bigrams: {n_bigrams}")
    print(f"  PREFIXes: {prefix_labels}")

    # Sub-1
    print("\n[1/4] Sub-Analysis 1...")
    sub1_results, cp_result = run_sub1(tensor, tokens, affordance_table,
                                        prefix_labels, class_labels, folio_sections)

    # Sub-2
    print("\n[2/4] Sub-Analysis 2...")
    sub2_results = run_sub2(tensor, tokens, affordance_table, prefix_labels,
                            class_labels, folio_sections)

    # Sub-3
    print("\n[3/4] Sub-Analysis 3...")
    sub3_results = run_sub3(tensor, class_labels)

    # Synthesis
    print("\n[4/4] Synthesis...")
    synthesis = synthesize(sub1_results, sub2_results, sub3_results)

    # Save results
    results = {
        'phase': 'CP_FACTOR_CHARACTERIZATION',
        'phase_number': 344,
        'prefix_labels': prefix_labels,
        'n_bigrams': n_bigrams,
        'tensor_shape': list(tensor.shape),
        'sub_1': sub1_results,
        'sub_2': sub2_results,
        'sub_3': sub3_results,
        'synthesis': synthesis,
    }

    # Clean up numpy types for JSON
    def clean_for_json(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [clean_for_json(x) for x in obj]
        return obj

    results = clean_for_json(results)

    with open(RESULTS_DIR / 'cp_factor_characterization.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 'cp_factor_characterization.json'}")

    elapsed = time.time() - t_start
    print(f"\nTotal time: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
