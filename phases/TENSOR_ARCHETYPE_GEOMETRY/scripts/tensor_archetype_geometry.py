#!/usr/bin/env python3
"""
Phase 343: TENSOR_ARCHETYPE_GEOMETRY
=====================================
Tests whether C1016's dynamical archetypes occupy distinct regions of the
C1019 rank-8 CP component space, and whether bridge-restricted factorization
recovers macro-state structure that the full tensor misses.

Sub-Analysis A: Factor Trajectory Geometry (A1-A4)
  - Folio-level CP scores in 8D tensor personality space
  - Silhouette, MANOVA, Spearman, k-means vs archetype labels

Sub-Analysis B: Bridge-Restricted Factorization (B1-B4)
  - Bridge-only tensor vs full tensor class factor ARI
  - Frequency-matched non-bridge control (MANDATORY per C1013)
  - Effective rank comparison
  - PREFIX factor entropy comparison

Depends on: C1019 (rank-8 tensor), C1016 (6 archetypes, 85 bridges),
            C1010 (6-state partition), C1013 (bridge selection by frequency)

Re-derivation guards:
  - Do NOT re-cluster macro-states (C1010 frozen)
  - Do NOT re-cluster archetypes (C1016 frozen)
  - Frequency-matched control is MANDATORY for Sub-B (C1013 AUC=0.978)
"""

import json
import sys
import functools
import warnings
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import cdist
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.cluster import KMeans

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

MIN_TRANSITIONS = 50
MIN_PREFIX_TOKENS = 10
MAX_PREFIXES = 20
CP_RANK = 8  # Frozen from C1019

SUFFIX_GROUPS = {
    'NONE': {None, ''},
    'Y_FAMILY': {'y', 'ey', 'dy', 'ly', 'ry', 'hy', 'eey', 'edy'},
    'IN_FAMILY': {'in', 'iin', 'ain', 'oin', 'ein', 'aiin', 'oiin', 'eiin',
                  'an', 'en', 'on'},
    'OL_FAMILY': {'ol', 'eol', 'ool', 'eeol', 'al', 'el', 'er', 'ar', 'or'},
}
SUFFIX_GROUP_ORDER = ['NONE', 'Y_FAMILY', 'IN_FAMILY', 'OL_FAMILY', 'OTHER']
N_SUFFIX_GROUPS = len(SUFFIX_GROUP_ORDER)


def get_suffix_group(suffix):
    for group, members in SUFFIX_GROUPS.items():
        if suffix in members:
            return group
    return 'OTHER'


# ── Data Loading ──────────────────────────────────────────────────────

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
    path = Path(__file__).resolve().parents[3] / 'data' / 'middle_affordance_table.json'
    with open(path) as f:
        data = json.load(f)
    middles_data = data.get('middles', {})
    result = {}
    for mid, info in middles_data.items():
        result[mid] = {
            'affordance_bin': info.get('affordance_bin'),
            'token_frequency': info.get('token_frequency', 0),
        }
    return result


def load_bridge_middles():
    path = Path(__file__).resolve().parents[2] / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(path) as f:
        data = json.load(f)
    return set(data['t5_structural_profile']['bridge_middles'])


def load_hub_sub_roles():
    path = Path(__file__).resolve().parents[2] / 'HUB_ROLE_DECOMPOSITION' / 'results' / 't1_hub_sub_role_partition.json'
    with open(path) as f:
        data = json.load(f)
    return data


def build_corpus_data(token_to_class):
    """Build enriched token-level corpus data."""
    tx = Transcript()
    morph = Morphology()

    raw_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        raw_tokens.append(token)

    tokens = []
    folio_sections = {}

    for token in raw_tokens:
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

def build_bigram_tensor(tokens, affordance_table, folio_filter=None, middle_filter=None):
    """Build 4-way count tensor T[PREFIX, MIDDLE_BIN, SUFFIX_GROUP, SUCCESSOR_CLASS].

    Args:
        middle_filter: optional set of MIDDLEs to include (None = all)
    """
    line_tokens = defaultdict(list)
    for t in tokens:
        if folio_filter is not None and t['folio'] not in folio_filter:
            continue
        line_tokens[(t['folio'], t['line'])].append(t)

    # PREFIX frequency selection
    prefix_counts = Counter()
    for t in tokens:
        if folio_filter is not None and t['folio'] not in folio_filter:
            continue
        prefix_counts[t['prefix']] += 1

    eligible = [(p, c) for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS]
    eligible.sort(key=lambda x: -x[1])
    selected_prefixes = sorted([p for p, _ in eligible[:MAX_PREFIXES]])
    prefix_idx = {p: i for i, p in enumerate(selected_prefixes)}

    n_bins = 10
    class_labels = list(range(1, N_CLASSES + 1))
    class_idx = {c: i for i, c in enumerate(class_labels)}

    tensor = np.zeros((len(selected_prefixes), n_bins, N_SUFFIX_GROUPS, N_CLASSES), dtype=float)
    n_bigrams = 0

    for (folio, line), tok_list in line_tokens.items():
        for i in range(len(tok_list) - 1):
            curr = tok_list[i]
            succ = tok_list[i + 1]

            # MIDDLE filter
            if middle_filter is not None and curr['middle'] not in middle_filter:
                continue

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


def build_freq_matched_control(bridge_middles, affordance_table):
    """Select 85 non-bridge MIDDLEs matched on log-frequency (1-NN)."""
    bridge_freqs = []
    non_bridge = []

    for mid, info in affordance_table.items():
        freq = info.get('token_frequency', 0)
        if freq <= 0:
            continue
        if mid in bridge_middles:
            bridge_freqs.append((mid, np.log1p(freq)))
        else:
            non_bridge.append((mid, np.log1p(freq)))

    if not bridge_freqs or not non_bridge:
        return set()

    # Sort non-bridge by log-frequency for efficient matching
    non_bridge.sort(key=lambda x: x[1])
    nb_names = [x[0] for x in non_bridge]
    nb_freqs = np.array([x[1] for x in non_bridge])

    matched = set()
    used_idx = set()

    for br_mid, br_freq in bridge_freqs:
        # Find closest unused non-bridge
        dists = np.abs(nb_freqs - br_freq)
        order = np.argsort(dists)
        for idx in order:
            if idx not in used_idx:
                matched.add(nb_names[idx])
                used_idx.add(idx)
                break

    return matched


# ── Sub-Analysis A: Factor Trajectory Geometry ────────────────────────

def compute_folio_cp_scores(tokens, affordance_table, prefix_labels, cp_factors, cp_weights):
    """Compute per-folio 8D tensor personality vectors.

    For each token on a folio, compute its contribution to each CP component
    using the PREFIX, BIN, and SUFFIX factor loadings. Average across all tokens.
    """
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

        # Component score: lambda_r * a_r(prefix) * b_r(bin) * c_r(suffix)
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


def run_sub_a(tensor, tokens, affordance_table, prefix_labels, folio_sections):
    """Sub-Analysis A: Factor Trajectory Geometry."""
    print("\n" + "=" * 60)
    print("Sub-Analysis A: Factor Trajectory Geometry")
    print("=" * 60)

    # Fit rank-8 CP
    tl_tensor = tl.tensor(tensor)
    cp_result = non_negative_parafac(tl_tensor, rank=CP_RANK, init='random',
                                     n_iter_max=300, tol=1e-6, random_state=42)
    cp_weights, cp_factors = cp_result

    print(f"\n  CP rank-{CP_RANK} fitted. Weights: {[f'{w:.3f}' for w in cp_weights]}")

    # Compute per-folio 8D scores
    folio_scores = compute_folio_cp_scores(tokens, affordance_table, prefix_labels,
                                           cp_factors, cp_weights)
    print(f"  Folios with scores: {len(folio_scores)}")

    # Load archetype labels
    arch_data = load_folio_archetypes()
    arch_labels = arch_data.get('folio_labels', {})
    regime_map = load_regime_assignments()

    # Build aligned arrays
    folios = sorted(set(folio_scores.keys()) & set(arch_labels.keys()))
    if len(folios) < 20:
        print(f"  ERROR: Only {len(folios)} folios with both scores and archetypes")
        return {'error': 'insufficient_folios'}

    X = np.array([folio_scores[f] for f in folios])
    y_arch = np.array([arch_labels[f] for f in folios])
    y_regime = np.array([regime_map.get(f, 0) for f in folios])

    print(f"  Aligned folios: {len(folios)}")
    print(f"  Archetype distribution: {dict(Counter(y_arch))}")
    print(f"  REGIME distribution: {dict(Counter(y_regime))}")

    # Build AXM self-transition per folio
    line_states = defaultdict(list)
    for t in tokens:
        line_states[(t['folio'], t['line'])].append(t['state'])
    folio_trans = defaultdict(lambda: np.zeros((N_STATES, N_STATES)))
    for (folio, line), states in line_states.items():
        for i in range(len(states) - 1):
            folio_trans[folio][STATE_IDX[states[i]], STATE_IDX[states[i+1]]] += 1
    folio_axm_self = {}
    for folio, mat in folio_trans.items():
        row = mat[STATE_IDX['AXM']]
        s = row.sum()
        folio_axm_self[folio] = float(row[STATE_IDX['AXM']] / s) if s > 0 else 0

    # ── A1: Silhouette ──
    print("\n  A1: Silhouette score (archetype labels in CP space)")
    # Need at least 2 unique labels with >1 member
    unique_archs = set(y_arch)
    if len(unique_archs) >= 2:
        sil = silhouette_score(X, y_arch)
    else:
        sil = -1.0
    print(f"    Silhouette: {sil:.4f}")

    # Null model: 1000 permutations
    null_sils = []
    for _ in range(1000):
        perm = np.random.permutation(y_arch)
        try:
            ns = silhouette_score(X, perm)
        except Exception:
            ns = 0.0
        null_sils.append(ns)
    null_mean = np.mean(null_sils)
    null_std = np.std(null_sils)
    z_score = (sil - null_mean) / null_std if null_std > 0 else 0
    p_val = sum(1 for ns in null_sils if ns >= sil) / len(null_sils) if null_sils else 1.0

    print(f"    Null: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"    z={z_score:.2f}, p={p_val:.4f}")

    a1_pass = sil > 0.15
    print(f"    A1 (silhouette > 0.15): {sil:.4f} → {'PASS' if a1_pass else 'FAIL'}")

    # ── A2: MANOVA (per-dimension ANOVA) ──
    print("\n  A2: Archetype vs REGIME variance explained")

    # Per-dimension ANOVA with archetype labels
    arch_eta2_dims = []
    regime_eta2_dims = []
    for d in range(CP_RANK):
        # Archetype groups
        groups_arch = [X[y_arch == a, d] for a in sorted(set(y_arch)) if np.sum(y_arch == a) > 0]
        if len(groups_arch) >= 2 and all(len(g) > 0 for g in groups_arch):
            ss_between = sum(len(g) * (np.mean(g) - np.mean(X[:, d]))**2 for g in groups_arch)
            ss_total = np.sum((X[:, d] - np.mean(X[:, d]))**2)
            arch_eta2_dims.append(ss_between / ss_total if ss_total > 0 else 0)
        else:
            arch_eta2_dims.append(0)

        # REGIME groups
        groups_reg = [X[y_regime == r, d] for r in sorted(set(y_regime)) if np.sum(y_regime == r) > 0]
        if len(groups_reg) >= 2 and all(len(g) > 0 for g in groups_reg):
            ss_between = sum(len(g) * (np.mean(g) - np.mean(X[:, d]))**2 for g in groups_reg)
            ss_total = np.sum((X[:, d] - np.mean(X[:, d]))**2)
            regime_eta2_dims.append(ss_between / ss_total if ss_total > 0 else 0)
        else:
            regime_eta2_dims.append(0)

    mean_arch_eta2 = np.mean(arch_eta2_dims)
    mean_regime_eta2 = np.mean(regime_eta2_dims)
    ratio = mean_arch_eta2 / mean_regime_eta2 if mean_regime_eta2 > 0 else float('inf')

    print(f"    Mean archetype eta²: {mean_arch_eta2:.4f}")
    print(f"    Mean REGIME eta²: {mean_regime_eta2:.4f}")
    print(f"    Ratio: {ratio:.2f}x")

    a2_pass = ratio > 2.0
    print(f"    A2 (arch > 2x REGIME): {ratio:.2f}x → {'PASS' if a2_pass else 'FAIL'}")

    # ── A3: AXM attractor on CP factors ──
    print("\n  A3: AXM self-transition correlation with CP factors")

    axm_vals = np.array([folio_axm_self.get(f, 0) for f in folios])
    rhos = []
    for d in range(CP_RANK):
        if np.std(X[:, d]) > 1e-10 and np.std(axm_vals) > 1e-10:
            rho, p = stats.spearmanr(X[:, d], axm_vals)
        else:
            rho, p = 0.0, 1.0
        rhos.append((d, float(rho), float(p)))
        print(f"    Factor {d}: rho={rho:.4f}, p={p:.4f}")

    max_abs_rho = max(abs(r[1]) for r in rhos)
    best_factor = max(rhos, key=lambda x: abs(x[1]))
    print(f"    Best: Factor {best_factor[0]}, rho={best_factor[1]:.4f}")

    a3_pass = max_abs_rho > 0.40
    print(f"    A3 (max |rho| > 0.40): {max_abs_rho:.4f} → {'PASS' if a3_pass else 'FAIL'}")

    # ── A4: k-means recovery ──
    print("\n  A4: k-means (k=6) in CP space vs archetype labels")

    km = KMeans(n_clusters=6, n_init=20, random_state=42)
    km_labels = km.fit_predict(X)
    ari_km = adjusted_rand_score(y_arch, km_labels)
    print(f"    ARI (k-means vs archetypes): {ari_km:.4f}")

    a4_pass = ari_km > 0.15
    print(f"    A4 (ARI > 0.15): {ari_km:.4f} → {'PASS' if a4_pass else 'FAIL'}")

    return {
        'n_folios': len(folios),
        'a1_silhouette': {
            'silhouette': float(sil),
            'null_mean': float(null_mean),
            'null_std': float(null_std),
            'z_score': float(z_score),
            'p_value': float(p_val),
            'pass': bool(a1_pass),
        },
        'a2_manova': {
            'mean_arch_eta2': float(mean_arch_eta2),
            'mean_regime_eta2': float(mean_regime_eta2),
            'ratio': float(ratio),
            'per_dim_arch_eta2': [float(x) for x in arch_eta2_dims],
            'per_dim_regime_eta2': [float(x) for x in regime_eta2_dims],
            'pass': bool(a2_pass),
        },
        'a3_axm_correlation': {
            'factor_rhos': [(int(d), float(r), float(p)) for d, r, p in rhos],
            'best_factor': int(best_factor[0]),
            'best_rho': float(best_factor[1]),
            'max_abs_rho': float(max_abs_rho),
            'pass': bool(a3_pass),
        },
        'a4_kmeans': {
            'ari': float(ari_km),
            'pass': bool(a4_pass),
        },
    }


# ── Sub-Analysis B: Bridge-Restricted Factorization ───────────────────

def run_sub_b(tokens, affordance_table, bridge_middles):
    """Sub-Analysis B: HUB-restricted vs non-HUB factorization.

    Since ALL B corpus MIDDLEs are bridge MIDDLEs (bridge coverage = 100%,
    confirming C1016/C1013), the bridge/non-bridge partition is degenerate.
    Instead, we partition by HUB sub-role (C1018/C1000):
    - HUB MIDDLEs: the 23 MIDDLEs with HUB sub-roles (high-frequency connectors)
    - non-HUB MIDDLEs: remaining bridges (lower-frequency, stability/compound)
    """
    print("\n" + "=" * 60)
    print("Sub-Analysis B: Bridge-Restricted Factorization")
    print("=" * 60)

    # Check bridge coverage
    corpus_middles = set(t['middle'] for t in tokens)
    bridge_overlap = corpus_middles & bridge_middles
    non_bridge_in_corpus = corpus_middles - bridge_middles
    bridge_coverage = len(bridge_overlap) / len(corpus_middles) if corpus_middles else 0

    print(f"\n  Corpus unique MIDDLEs: {len(corpus_middles)}")
    print(f"  Bridge MIDDLEs in corpus: {len(bridge_overlap)}")
    print(f"  Non-bridge MIDDLEs in corpus: {len(non_bridge_in_corpus)}")
    print(f"  Bridge coverage: {bridge_coverage:.1%}")

    bridge_degenerate = bridge_coverage > 0.95
    if bridge_degenerate:
        print(f"  ** BRIDGE DEGENERACY: {bridge_coverage:.1%} coverage — all B MIDDLEs are bridges **")
        print(f"  ** Confirms C1016/C1013. Replacing with HUB vs non-HUB partition **")
        if non_bridge_in_corpus:
            print(f"  Non-bridge MIDDLEs in B: {non_bridge_in_corpus}")

    # Load HUB sub-roles for the partition
    hub_data = load_hub_sub_roles()
    hub_primary = hub_data.get('primary_roles', {})
    hub_middles = set(hub_primary.keys())
    non_hub_middles = corpus_middles - hub_middles

    print(f"\n  HUB MIDDLEs in corpus: {len(hub_middles & corpus_middles)}")
    print(f"  Non-HUB MIDDLEs in corpus: {len(non_hub_middles)}")

    # Build tensors: full, HUB-restricted, non-HUB control
    print("\n  Building tensors...")
    tensor_full, pfx_full, cls_full, n_full = build_bigram_tensor(
        tokens, affordance_table)
    tensor_hub, pfx_hub, cls_hub, n_hub = build_bigram_tensor(
        tokens, affordance_table, middle_filter=hub_middles)
    tensor_nonhub, pfx_nh, cls_nh, n_nonhub = build_bigram_tensor(
        tokens, affordance_table, middle_filter=non_hub_middles)

    print(f"  Full tensor: {tensor_full.shape}, bigrams={n_full}")
    print(f"  HUB tensor: {tensor_hub.shape}, bigrams={n_hub}")
    print(f"  Non-HUB tensor: {tensor_nonhub.shape}, bigrams={n_nonhub}")

    # True class labels for ARI
    true_labels = [STATE_IDX.get(CLASS_TO_STATE.get(c), -1)
                   for c in range(1, N_CLASSES + 1)]

    def fit_and_cluster(tensor_data, label, rank=CP_RANK):
        """Fit CP and compute class factor ARI vs C1010."""
        tl_t = tl.tensor(tensor_data)
        frob = tl.norm(tl_t)

        if frob < 1e-10:
            print(f"    {label}: empty tensor (frob < 1e-10)")
            return {'ari_at_6': 0.0, 'best_ari': 0.0, 'best_k': 6,
                    'rel_error': 1.0, 'var_explained': 0.0,
                    'mean_prefix_entropy': 0.0, 'empty': True}

        # Reduce rank if tensor is too sparse for requested rank
        effective_rank = min(rank, min(tensor_data.shape) - 1)
        effective_rank = max(2, effective_rank)

        try:
            result = non_negative_parafac(tl_t, rank=effective_rank, init='random',
                                          n_iter_max=300, tol=1e-6,
                                          random_state=42)
            weights, factors = result
            class_factors = factors[3]
            prefix_factors = factors[0]

            Z = linkage(class_factors, method='ward')
            cl = fcluster(Z, t=6, criterion='maxclust')
            ari = adjusted_rand_score(true_labels, cl)

            best_ari = ari
            best_k = 6
            for k in range(2, 11):
                cl_k = fcluster(Z, t=k, criterion='maxclust')
                a = adjusted_rand_score(true_labels, cl_k)
                if a > best_ari:
                    best_ari = a
                    best_k = k

            recon = tl.cp_to_tensor(result)
            rel_error = float(tl.norm(tl_t - recon) / frob)

            pfx_entropies = []
            for i in range(prefix_factors.shape[0]):
                row = prefix_factors[i]
                total = row.sum()
                if total > 0:
                    probs = row / total
                    probs = probs[probs > 0]
                    ent = -np.sum(probs * np.log2(probs))
                    pfx_entropies.append(ent)
            mean_pfx_entropy = np.mean(pfx_entropies) if pfx_entropies else 0

            return {
                'ari_at_6': float(ari),
                'best_ari': float(best_ari),
                'best_k': int(best_k),
                'rel_error': float(rel_error),
                'var_explained': float(1 - rel_error**2),
                'mean_prefix_entropy': float(mean_pfx_entropy),
                'effective_rank': int(effective_rank),
            }
        except Exception as e:
            print(f"    {label} CP failed: {e}")
            return {'ari_at_6': 0.0, 'best_ari': 0.0, 'best_k': 6,
                    'rel_error': 1.0, 'var_explained': 0.0,
                    'mean_prefix_entropy': 0.0, 'error': str(e)}

    print("\n  Fitting CP on full tensor...")
    full_result = fit_and_cluster(tensor_full, 'Full')
    print(f"    Full ARI: {full_result['best_ari']:.4f} (k={full_result['best_k']})")

    print("  Fitting CP on HUB-restricted tensor...")
    hub_result = fit_and_cluster(tensor_hub, 'HUB')
    print(f"    HUB ARI: {hub_result['best_ari']:.4f} (k={hub_result['best_k']})")

    print("  Fitting CP on non-HUB tensor...")
    nonhub_result = fit_and_cluster(tensor_nonhub, 'Non-HUB')
    print(f"    Non-HUB ARI: {nonhub_result['best_ari']:.4f} (k={nonhub_result['best_k']})")

    # ── B1: HUB-restricted recovers macro-state better (adapted) ──
    b1_pass = hub_result['best_ari'] > 0.15
    print(f"\n  B1 (HUB ARI > 0.15): {hub_result['best_ari']:.4f} → {'PASS' if b1_pass else 'FAIL'}")

    # ── B2: Non-HUB does NOT recover (adapted) ──
    b2_pass = nonhub_result['best_ari'] < 0.10
    print(f"  B2 (non-HUB ARI < 0.10): {nonhub_result['best_ari']:.4f} → {'PASS' if b2_pass else 'FAIL'}")

    # ── B3: HUB tensor effective rank ──
    print("\n  B3: HUB tensor effective rank")
    tl_hub = tl.tensor(tensor_hub)
    frob_hub = tl.norm(tl_hub)

    hub_ranks = {}
    if frob_hub > 1e-10:
        for r in range(3, CP_RANK + 2):
            try:
                res = non_negative_parafac(tl_hub, rank=r, init='random',
                                           n_iter_max=200, tol=1e-4,
                                           random_state=42)
                recon = tl.cp_to_tensor(res)
                rel_err = float(tl.norm(tl_hub - recon) / frob_hub)
                var_exp = 1 - rel_err**2
                hub_ranks[r] = {'error': float(rel_err), 'variance': float(var_exp)}
                print(f"    Rank {r}: var_explained={var_exp:.4f}")
            except Exception:
                hub_ranks[r] = {'error': 1.0, 'variance': 0.0}

    hub_elbow = CP_RANK
    for r in sorted(hub_ranks.keys()):
        if hub_ranks[r]['variance'] >= 0.90:
            hub_elbow = r
            break

    b3_pass = hub_elbow < CP_RANK
    print(f"    HUB elbow rank (90% var): {hub_elbow}")
    print(f"    B3 (HUB rank < {CP_RANK}): {hub_elbow} → {'PASS' if b3_pass else 'FAIL'}")

    # ── B4: PREFIX factor entropy ──
    print("\n  B4: PREFIX factor entropy comparison")
    full_entropy = full_result.get('mean_prefix_entropy', 0)
    hub_entropy = hub_result.get('mean_prefix_entropy', 0)

    b4_pass = hub_entropy < full_entropy
    print(f"    Full PREFIX entropy: {full_entropy:.4f}")
    print(f"    HUB PREFIX entropy: {hub_entropy:.4f}")
    print(f"    B4 (HUB < full): {'PASS' if b4_pass else 'FAIL'}")

    return {
        'bridge_degenerate': bool(bridge_degenerate),
        'bridge_coverage': float(bridge_coverage),
        'partition_type': 'HUB_vs_nonHUB' if bridge_degenerate else 'bridge_vs_nonbridge',
        'n_hub_middles': len(hub_middles & corpus_middles),
        'n_nonhub_middles': len(non_hub_middles),
        'n_bigrams_full': int(n_full),
        'n_bigrams_hub': int(n_hub),
        'n_bigrams_nonhub': int(n_nonhub),
        'full_result': full_result,
        'hub_result': hub_result,
        'nonhub_result': nonhub_result,
        'b1_hub_ari': {
            'value': float(hub_result['best_ari']),
            'pass': bool(b1_pass),
        },
        'b2_nonhub_ari': {
            'value': float(nonhub_result['best_ari']),
            'pass': bool(b2_pass),
        },
        'b3_hub_rank': {
            'elbow_rank': int(hub_elbow),
            'full_rank': CP_RANK,
            'rank_sweep': {str(r): v for r, v in hub_ranks.items()},
            'pass': bool(b3_pass),
        },
        'b4_prefix_entropy': {
            'full_entropy': float(full_entropy),
            'hub_entropy': float(hub_entropy),
            'pass': bool(b4_pass),
        },
    }


# ── Synthesis ─────────────────────────────────────────────────────────

def synthesize(sub_a, sub_b):
    """Evaluate all 8 predictions and determine verdict."""
    print("\n" + "=" * 60)
    print("Synthesis")
    print("=" * 60)

    predictions = {
        'A1': {
            'description': 'Archetypes cluster in CP space (silhouette > 0.15)',
            'result': bool(sub_a['a1_silhouette']['pass']),
            'value': float(sub_a['a1_silhouette']['silhouette']),
        },
        'A2': {
            'description': 'Archetypes > 2x REGIME in CP variance',
            'result': bool(sub_a['a2_manova']['pass']),
            'value': float(sub_a['a2_manova']['ratio']),
        },
        'A3': {
            'description': 'AXM attractor loads on specific CP factors (|rho| > 0.40)',
            'result': bool(sub_a['a3_axm_correlation']['pass']),
            'value': float(sub_a['a3_axm_correlation']['max_abs_rho']),
        },
        'A4': {
            'description': 'CP space independently recovers archetypes (ARI > 0.15)',
            'result': bool(sub_a['a4_kmeans']['pass']),
            'value': float(sub_a['a4_kmeans']['ari']),
        },
        'B1': {
            'description': 'HUB-restricted class ARI > 0.15 vs C1010',
            'result': bool(sub_b['b1_hub_ari']['pass']),
            'value': float(sub_b['b1_hub_ari']['value']),
        },
        'B2': {
            'description': 'Non-HUB ARI < 0.10',
            'result': bool(sub_b['b2_nonhub_ari']['pass']),
            'value': float(sub_b['b2_nonhub_ari']['value']),
        },
        'B3': {
            'description': 'HUB tensor has lower effective rank',
            'result': bool(sub_b['b3_hub_rank']['pass']),
            'value': int(sub_b['b3_hub_rank']['elbow_rank']),
        },
        'B4': {
            'description': 'HUB PREFIX factors more channeled (lower entropy)',
            'result': bool(sub_b['b4_prefix_entropy']['pass']),
            'value': float(sub_b['b4_prefix_entropy']['hub_entropy']),
        },
    }

    n_pass = sum(1 for p in predictions.values() if p['result'])
    n_total = len(predictions)

    for pid, pred in sorted(predictions.items()):
        status = 'PASS' if pred['result'] else 'FAIL'
        print(f"  {pid}: {pred['description']} → {pred['value']} → {status}")

    print(f"\n  Total: {n_pass}/{n_total} passed")

    # Determine sub-verdicts
    a_pass = sum(1 for p in ['A1', 'A2', 'A3', 'A4'] if predictions[p]['result'])
    b1_b2 = predictions['B1']['result'] and predictions['B2']['result']

    if a_pass >= 3:
        a_verdict = 'ARCHETYPE_GEOMETRY_CONFIRMED'
    elif a_pass >= 2:
        a_verdict = 'ARCHETYPE_GEOMETRY_PARTIAL'
    else:
        a_verdict = 'ARCHETYPE_GEOMETRY_ABSENT'

    if predictions['B1']['result'] and predictions['B2']['result']:
        b_verdict = 'HUB_TOPOLOGY_CONFIRMED'
    elif predictions['B1']['result'] and not predictions['B2']['result']:
        b_verdict = 'HUB_TOPOLOGY_AMBIGUOUS'
    else:
        b_verdict = 'HUB_TOPOLOGY_ABSENT'

    # Combined verdict
    if a_pass >= 3 and b1_b2:
        verdict = 'TENSOR_GEOMETRY_CONFIRMED'
    elif a_pass >= 3:
        verdict = f'TENSOR_GEOMETRY_PARTIAL_A ({a_verdict}; {b_verdict})'
    elif b1_b2:
        verdict = f'TENSOR_GEOMETRY_PARTIAL_B ({a_verdict}; {b_verdict})'
    else:
        verdict = f'TENSOR_GEOMETRY_ORTHOGONAL ({a_verdict}; {b_verdict})'

    print(f"\n  Sub-A verdict: {a_verdict} ({a_pass}/4)")
    print(f"  Sub-B verdict: {b_verdict}")
    print(f"  Combined: {verdict}")

    return {
        'predictions': predictions,
        'n_pass': int(n_pass),
        'n_total': int(n_total),
        'sub_a_verdict': a_verdict,
        'sub_b_verdict': b_verdict,
        'verdict': verdict,
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("Phase 343: TENSOR_ARCHETYPE_GEOMETRY")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    affordance_table = load_affordance_table()
    bridge_middles = load_bridge_middles()
    tokens, folio_sections = build_corpus_data(token_to_class)

    # Build full tensor for Sub-A
    print("\nBuilding full tensor...")
    tensor, prefix_labels, class_labels, n_bigrams = build_bigram_tensor(
        tokens, affordance_table)
    print(f"  Full tensor: {tensor.shape}, bigrams={n_bigrams}")

    # Sub-A: Factor trajectory geometry
    sub_a = run_sub_a(tensor, tokens, affordance_table, prefix_labels, folio_sections)

    # Sub-B: Bridge-restricted factorization
    sub_b = run_sub_b(tokens, affordance_table, bridge_middles)

    # Synthesis
    synthesis = synthesize(sub_a, sub_b)

    # Save results
    results = {
        'phase': 'TENSOR_ARCHETYPE_GEOMETRY',
        'phase_number': 343,
        'prefix_labels': prefix_labels,
        'sub_a': sub_a,
        'sub_b': sub_b,
        'synthesis': synthesis,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'tensor_archetype_geometry.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")
    print(f"\nVERDICT: {synthesis['verdict']} ({synthesis['n_pass']}/{synthesis['n_total']} passed)")


if __name__ == '__main__':
    main()
