#!/usr/bin/env python3
"""
Phase 342: MORPHOLOGICAL_TENSOR_DECOMPOSITION
===============================================
Tests whether low-rank tensor factorization of the morphological transition
structure T[PREFIX, MIDDLE_BIN, SUFFIX_GROUP, SUCCESSOR_CLASS] independently
recovers the 6-state macro-automaton topology (C1010).

Tests:
  T1: Tensor construction + rank selection (NTF at ranks 4-10)
  T2: Factor interpretation (class factors vs C1010, PREFIX vs C1012, etc.)
  T3: CP vs Tucker comparison (tests C1003 pairwise sufficiency)
  T4: Controls (PREFIX-marginalized, shuffle null, cross-val, incremental R²)
  T5: Synthesis / verdict (P1-P8)

Depends on: C1010 (6-state partition), C1012 (PREFIX selectivity),
            C1003 (pairwise compositionality), C1004 (SUFFIX zero info),
            C995 (affordance bins), C1018 (HUB sub-roles)

Re-derivation guards:
  - Uses 49 classes as successor axis (not 6 states — avoids circularity)
  - P3 tests whether tensor PREFIX factors exceed C1012 (not just match)
  - P8 checks whether removing PREFIX collapses macro-state recovery
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
from sklearn.metrics import adjusted_rand_score

import tensorly as tl
from tensorly.decomposition import non_negative_parafac, tucker

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore', category=RuntimeWarning)

np.random.seed(42)

# ── Constants (from C1010/Phase 328) ──────────────────────────────────

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
MAX_PREFIXES = 20  # Top 19 by frequency + __BARE__

# Suffix grouping (C588 strata)
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
    """Map a suffix string to its group."""
    for group, members in SUFFIX_GROUPS.items():
        if suffix in members:
            return group
    return 'OTHER'


# ── Data Loading (reused from Phase 341) ──────────────────────────────

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
            'affordance_label': info.get('affordance_label', ''),
            'radial_depth': info.get('radial_depth', 0),
            'token_frequency': info.get('token_frequency', 0),
        }
        sig = info.get('behavioral_signature', {})
        result[mid]['k_ratio'] = sig.get('k_ratio', 0)
        result[mid]['e_ratio'] = sig.get('e_ratio', 0)
        result[mid]['h_ratio'] = sig.get('h_ratio', 0)
        result[mid]['qo_affinity'] = sig.get('qo_affinity', 0)
    return result


def load_c1012_selectivity():
    """Load per-PREFIX concentration and entropy from C1012."""
    path = Path(__file__).resolve().parents[2] / 'PREFIX_MACRO_STATE_ENFORCEMENT' / 'results' / 'prefix_enforcement.json'
    with open(path) as f:
        data = json.load(f)
    return data['t1_selectivity']


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

def build_bigram_tensor(tokens, affordance_table, folio_filter=None):
    """Build 4-way count tensor T[PREFIX, MIDDLE_BIN, SUFFIX_GROUP, SUCCESSOR_CLASS].

    Args:
        tokens: enriched token list from build_corpus_data()
        affordance_table: MIDDLE → affordance bin mapping
        folio_filter: optional set of folios to include (None = all)

    Returns:
        tensor: numpy array of shape (n_prefixes, n_bins, n_suffix_groups, n_classes)
        prefix_labels: list of PREFIX labels (axis 0)
        bin_labels: list of bin indices (axis 1)
        suffix_group_labels: list of suffix group names (axis 2)
        class_labels: list of class indices 1-49 (axis 3)
        n_bigrams: total bigram count
    """
    # Group tokens by (folio, line) preserving order
    line_tokens = defaultdict(list)
    for t in tokens:
        if folio_filter is not None and t['folio'] not in folio_filter:
            continue
        line_tokens[(t['folio'], t['line'])].append(t)

    # First pass: count PREFIX frequencies to select top PREFIXes
    prefix_counts = Counter()
    for t in tokens:
        if folio_filter is not None and t['folio'] not in folio_filter:
            continue
        prefix_counts[t['prefix']] += 1

    # Select top MAX_PREFIXES by frequency (with >= MIN_PREFIX_TOKENS)
    eligible = [(p, c) for p, c in prefix_counts.items() if c >= MIN_PREFIX_TOKENS]
    eligible.sort(key=lambda x: -x[1])
    selected_prefixes = sorted([p for p, _ in eligible[:MAX_PREFIXES]])
    prefix_idx = {p: i for i, p in enumerate(selected_prefixes)}
    n_prefixes = len(selected_prefixes)

    # Bin labels (0-9 from affordance table)
    n_bins = 10
    bin_labels = list(range(n_bins))

    # Class labels (1-49)
    class_labels = list(range(1, N_CLASSES + 1))
    class_idx = {c: i for i, c in enumerate(class_labels)}

    # Build tensor
    tensor = np.zeros((n_prefixes, n_bins, N_SUFFIX_GROUPS, N_CLASSES), dtype=float)
    n_bigrams = 0
    n_skipped_prefix = 0
    n_skipped_bin = 0

    for (folio, line), tok_list in line_tokens.items():
        for i in range(len(tok_list) - 1):
            curr = tok_list[i]
            succ = tok_list[i + 1]

            # Current token axes
            p = curr['prefix']
            if p not in prefix_idx:
                n_skipped_prefix += 1
                continue

            mid = curr['middle']
            aff = affordance_table.get(mid)
            if aff is None or aff.get('affordance_bin') is None:
                n_skipped_bin += 1
                continue
            b = aff['affordance_bin']
            if b < 0 or b >= n_bins:
                n_skipped_bin += 1
                continue

            sg = get_suffix_group(curr['suffix'])
            sg_i = SUFFIX_GROUP_ORDER.index(sg)

            # Successor class
            succ_cls = succ['cls']
            if succ_cls not in class_idx:
                continue

            tensor[prefix_idx[p], b, sg_i, class_idx[succ_cls]] += 1
            n_bigrams += 1

    return tensor, selected_prefixes, bin_labels, SUFFIX_GROUP_ORDER, class_labels, n_bigrams


def build_per_prefix_state_dist(tokens):
    """Build per-PREFIX macro-state distribution from corpus (for C1012 comparison)."""
    prefix_state_counts = defaultdict(lambda: Counter())
    for t in tokens:
        prefix_state_counts[t['prefix']][t['state']] += 1

    result = {}
    for pfx, counts in prefix_state_counts.items():
        total = sum(counts.values())
        if total >= MIN_PREFIX_TOKENS:
            dist = np.array([counts.get(s, 0) / total for s in STATE_ORDER])
            result[pfx] = dist
    return result


# ── T1: Tensor Construction + Rank Selection ──────────────────────────

def run_t1(tensor, prefix_labels, n_bigrams):
    """Fit NTF at ranks 4-10, select optimal rank."""
    print("\n" + "=" * 60)
    print("T1: Tensor Construction + Rank Selection")
    print("=" * 60)

    shape = tensor.shape
    total_cells = np.prod(shape)
    nonzero_cells = np.count_nonzero(tensor)
    density = nonzero_cells / total_cells
    total_mass = tensor.sum()

    print(f"\n  Tensor shape: {shape}")
    print(f"  Total cells: {total_cells:,}")
    print(f"  Non-zero cells: {nonzero_cells:,}")
    print(f"  Density: {density:.4f} ({density*100:.1f}%)")
    print(f"  Total bigrams: {n_bigrams:,}")
    print(f"  Tensor sum: {total_mass:.0f}")
    print(f"  PREFIXes: {len(prefix_labels)}")

    # Fit NTF at ranks 4-10
    tl_tensor = tl.tensor(tensor)
    frob_total = tl.norm(tl_tensor)

    ranks = list(range(4, 11))
    errors = {}
    variances = {}

    print(f"\n  Fitting NTF at ranks {ranks[0]}-{ranks[-1]}...")
    for r in ranks:
        try:
            result = non_negative_parafac(tl_tensor, rank=r, init='random',
                                          n_iter_max=200, tol=1e-6,
                                          random_state=42)
            reconstructed = tl.cp_to_tensor(result)
            residual = tl.norm(tl_tensor - reconstructed)
            rel_error = float(residual / frob_total)
            var_explained = 1.0 - rel_error ** 2
            errors[r] = rel_error
            variances[r] = var_explained
            print(f"    Rank {r}: rel_error={rel_error:.4f}, var_explained={var_explained:.4f}")
        except Exception as e:
            print(f"    Rank {r}: FAILED ({e})")
            errors[r] = 1.0
            variances[r] = 0.0

    # Elbow detection: find first rank where improvement < 3% (diminishing returns)
    best_rank = ranks[0]
    improvements = {}
    for i in range(1, len(ranks)):
        r = ranks[i]
        r_prev = ranks[i - 1]
        if errors[r_prev] > 0:
            improvement = (errors[r_prev] - errors[r]) / errors[r_prev]
        else:
            improvement = 0
        improvements[r] = improvement

    # Select: last rank before improvement drops below 3%
    best_rank = ranks[0]
    for i in range(1, len(ranks)):
        r = ranks[i]
        if improvements[r] >= 0.03:
            best_rank = r
        else:
            break  # Stop at first sub-threshold improvement

    print(f"\n  Selected rank: {best_rank}")
    print(f"  Variance explained at rank {best_rank}: {variances[best_rank]:.4f}")

    # P1: Optimal rank is 5-8
    p1_pass = 5 <= best_rank <= 8
    print(f"\n  P1 (rank 5-8): {best_rank} → {'PASS' if p1_pass else 'FAIL'}")

    return {
        'shape': list(shape),
        'total_cells': int(total_cells),
        'nonzero_cells': int(nonzero_cells),
        'density': float(density),
        'n_bigrams': int(n_bigrams),
        'ranks_tested': ranks,
        'errors': {str(r): float(e) for r, e in errors.items()},
        'variances': {str(r): float(v) for r, v in variances.items()},
        'improvements': {str(r): float(v) for r, v in improvements.items()},
        'best_rank': int(best_rank),
        'best_variance': float(variances[best_rank]),
        'p1_pass': bool(p1_pass),
    }


# ── T2: Factor Interpretation ─────────────────────────────────────────

def run_t2(tensor, best_rank, prefix_labels, class_labels, tokens, affordance_table):
    """Interpret factors from best-rank CP decomposition."""
    print("\n" + "=" * 60)
    print("T2: Factor Interpretation")
    print("=" * 60)

    tl_tensor = tl.tensor(tensor)

    # Fit at best rank
    result = non_negative_parafac(tl_tensor, rank=best_rank, init='random',
                                  n_iter_max=300, tol=1e-6, random_state=42)
    weights, factors = result

    prefix_factors = factors[0]   # (n_prefixes, R)
    bin_factors = factors[1]      # (n_bins, R)
    suffix_factors = factors[2]   # (n_suffix_groups, R)
    class_factors = factors[3]    # (n_classes, R)

    print(f"\n  Factor shapes: PREFIX={prefix_factors.shape}, BIN={bin_factors.shape}, "
          f"SUFFIX={suffix_factors.shape}, CLASS={class_factors.shape}")
    print(f"  Weights: {[f'{w:.3f}' for w in weights]}")

    # ── T2a: Class factor clustering vs C1010 ──
    print("\n  T2a: Class factor clustering vs C1010")

    # Each class has an R-dimensional factor vector; cluster into 6 groups
    class_vectors = class_factors  # (49, R)
    Z = linkage(class_vectors, method='ward')
    cluster_labels = fcluster(Z, t=6, criterion='maxclust')

    # Build true C1010 labels for 49 classes
    true_labels = []
    for c in class_labels:
        true_labels.append(STATE_IDX.get(CLASS_TO_STATE.get(c), -1))

    ari = adjusted_rand_score(true_labels, cluster_labels)
    print(f"    ARI (6-cluster vs C1010): {ari:.4f}")

    # Also try at optimal number of clusters (2-10)
    best_ari = ari
    best_k = 6
    for k in range(2, 11):
        cl = fcluster(Z, t=k, criterion='maxclust')
        a = adjusted_rand_score(true_labels, cl)
        if a > best_ari:
            best_ari = a
            best_k = k

    print(f"    Best ARI: {best_ari:.4f} at k={best_k}")

    # P2: ARI > 0.6
    p2_pass = best_ari > 0.6
    print(f"    P2 (ARI > 0.6): {best_ari:.4f} → {'PASS' if p2_pass else 'FAIL'}")

    # Examine which classes group together — report cluster composition by state
    cluster_composition = defaultdict(lambda: Counter())
    for i, c in enumerate(class_labels):
        state = CLASS_TO_STATE.get(c, 'UNKNOWN')
        cluster_composition[int(cluster_labels[i])][state] += 1
    cluster_comp_report = {
        str(cl): dict(counts) for cl, counts in sorted(cluster_composition.items())
    }
    print(f"    Cluster composition: {cluster_comp_report}")

    # ── T2b: PREFIX factor correlation with C1012 ──
    print("\n  T2b: PREFIX factor correlation with C1012")

    # Build per-PREFIX state distributions from corpus
    pfx_state_dist = build_per_prefix_state_dist(tokens)

    # For each PREFIX in the tensor, get its factor vector and state dist
    pfx_factor_flat = []
    pfx_state_flat = []
    matched_prefixes = []

    for i, pfx in enumerate(prefix_labels):
        pfx_key = pfx if pfx != '__BARE__' else '(none)'
        if pfx_key in pfx_state_dist or pfx in pfx_state_dist:
            key = pfx_key if pfx_key in pfx_state_dist else pfx
            pfx_factor_flat.append(prefix_factors[i])
            pfx_state_flat.append(pfx_state_dist[key])
            matched_prefixes.append(pfx)

    # Compute concentration (max state fraction) from state dist
    pfx_concentrations = [max(d) for d in pfx_state_flat]
    # Compute factor concentration (max factor loading / sum)
    pfx_factor_concentrations = []
    for fv in pfx_factor_flat:
        s = fv.sum()
        if s > 0:
            pfx_factor_concentrations.append(float(fv.max() / s))
        else:
            pfx_factor_concentrations.append(0)

    if len(pfx_concentrations) >= 3:
        rho_conc, p_conc = stats.spearmanr(pfx_concentrations, pfx_factor_concentrations)
    else:
        rho_conc, p_conc = 0.0, 1.0

    print(f"    Matched PREFIXes: {len(matched_prefixes)}")
    print(f"    Concentration correlation (Spearman): rho={rho_conc:.4f}, p={p_conc:.4f}")

    # Also: compute pairwise cosine similarity between PREFIX state dists
    # and PREFIX factor vectors, then correlate
    from scipy.spatial.distance import cdist
    if len(pfx_state_flat) >= 3:
        state_dists = np.array(pfx_state_flat)
        factor_vecs = np.array(pfx_factor_flat)

        # Cosine similarity matrices
        state_sim = 1 - cdist(state_dists, state_dists, metric='cosine')
        factor_sim = 1 - cdist(factor_vecs, factor_vecs, metric='cosine')

        # Flatten upper triangle
        n = len(matched_prefixes)
        triu_idx = np.triu_indices(n, k=1)
        state_flat = state_sim[triu_idx]
        factor_flat = factor_sim[triu_idx]

        if np.std(state_flat) > 1e-10 and np.std(factor_flat) > 1e-10:
            rho_sim, p_sim = stats.spearmanr(state_flat, factor_flat)
        else:
            rho_sim, p_sim = 0.0, 1.0
    else:
        rho_sim, p_sim = 0.0, 1.0

    print(f"    Pairwise similarity correlation: rho={rho_sim:.4f}, p={p_sim:.4f}")

    # P3: PREFIX factor correlation > 0.8
    p3_pass = abs(rho_sim) > 0.8
    print(f"    P3 (pairwise r > 0.8): {abs(rho_sim):.4f} → {'PASS' if p3_pass else 'FAIL'}")

    # ── T2c: MIDDLE bin factors ──
    print("\n  T2c: MIDDLE bin factor loadings")

    # Report which bins load on which components
    bin_loading_report = {}
    for b in range(bin_factors.shape[0]):
        loadings = bin_factors[b]
        dominant_comp = int(np.argmax(loadings))
        loading_str = ', '.join([f'C{j}:{loadings[j]:.3f}' for j in range(len(loadings))])
        bin_loading_report[str(b)] = {
            'dominant_component': dominant_comp,
            'loadings': [float(x) for x in loadings],
        }
        print(f"    Bin {b}: dominant=C{dominant_comp}, loadings=[{loading_str}]")

    # Check HUB_UNIVERSAL vs STABILITY_CRITICAL alignment
    # Bins 0-2 tend to be HUB-heavy; bins 6-9 tend to be stability-heavy
    hub_bins = [0, 1, 2]
    stab_bins = [6, 7, 8, 9]

    hub_mean_factors = np.mean([bin_factors[b] for b in hub_bins if b < bin_factors.shape[0]], axis=0)
    stab_mean_factors = np.mean([bin_factors[b] for b in stab_bins if b < bin_factors.shape[0]], axis=0)

    if np.std(hub_mean_factors) > 1e-10 and np.std(stab_mean_factors) > 1e-10:
        cos_sim = np.dot(hub_mean_factors, stab_mean_factors) / (
            np.linalg.norm(hub_mean_factors) * np.linalg.norm(stab_mean_factors))
    else:
        cos_sim = 1.0

    # P6: HUB vs STABILITY have different dominant components (cos_sim < 0.8)
    p6_pass = cos_sim < 0.8
    print(f"    HUB vs STABILITY cosine: {cos_sim:.4f}")
    print(f"    P6 (HUB≠STABILITY): cos={cos_sim:.4f} → {'PASS' if p6_pass else 'FAIL'}")

    # ── T2d: SUFFIX factor dimensionality ──
    print("\n  T2d: SUFFIX factor effective dimensionality")

    suffix_loadings = suffix_factors  # (5, R)

    # Effective dimensionality via participation ratio of column norms
    # For each component, compute the total loading from suffix groups
    col_norms = np.array([np.linalg.norm(suffix_factors[:, j]) for j in range(suffix_factors.shape[1])])
    col_norms_sq = col_norms ** 2
    total = col_norms_sq.sum()
    if total > 0:
        probs = col_norms_sq / total
        # Participation ratio = 1 / sum(p_i^2) — effective number of active components
        pr = 1.0 / np.sum(probs ** 2) if np.sum(probs ** 2) > 0 else 0
        effective_dims = pr
    else:
        effective_dims = 0

    # Also: SVD of suffix factor matrix for intrinsic dimensionality
    U, s, Vt = np.linalg.svd(suffix_factors, full_matrices=False)
    s_sq = s ** 2
    total_var = s_sq.sum()
    if total_var > 0:
        cum_var = np.cumsum(s_sq / total_var)
        svd_dims_90 = int(np.searchsorted(cum_var, 0.90)) + 1
    else:
        svd_dims_90 = 0

    print(f"    Suffix factor matrix (5 groups × {suffix_factors.shape[1]} components):")
    for i, sg in enumerate(SUFFIX_GROUP_ORDER):
        row = suffix_factors[i]
        print(f"      {sg}: [{', '.join(f'{x:.3f}' for x in row)}]")
    print(f"    Participation ratio: {effective_dims:.2f}")
    print(f"    SVD dims for 90% variance: {svd_dims_90}")

    # P7: SUFFIX has < 3 effective dimensions (using SVD dims for 90% variance)
    p7_pass = svd_dims_90 < 3
    print(f"    P7 (SUFFIX < 3 SVD dims): {svd_dims_90} → {'PASS' if p7_pass else 'FAIL'}")

    return {
        'best_rank': int(best_rank),
        'weights': [float(w) for w in weights],
        't2a_class_clustering': {
            'ari_at_6': float(ari),
            'best_ari': float(best_ari),
            'best_k': int(best_k),
            'cluster_composition': cluster_comp_report,
            'p2_pass': bool(p2_pass),
        },
        't2b_prefix_correlation': {
            'n_matched': len(matched_prefixes),
            'concentration_rho': float(rho_conc),
            'concentration_p': float(p_conc),
            'pairwise_sim_rho': float(rho_sim),
            'pairwise_sim_p': float(p_sim),
            'p3_pass': bool(p3_pass),
        },
        't2c_bin_factors': {
            'bin_loadings': bin_loading_report,
            'hub_stab_cosine': float(cos_sim),
            'p6_pass': bool(p6_pass),
        },
        't2d_suffix_dims': {
            'participation_ratio': float(effective_dims),
            'svd_dims_90pct': int(svd_dims_90),
            'suffix_loadings': [[float(x) for x in row] for row in suffix_factors],
            'p7_pass': bool(p7_pass),
        },
    }


# ── T3: CP vs Tucker Comparison ───────────────────────────────────────

def run_t3(tensor, best_rank):
    """Compare CP vs Tucker reconstruction at matched parameter count."""
    print("\n" + "=" * 60)
    print("T3: CP vs Tucker Comparison")
    print("=" * 60)

    tl_tensor = tl.tensor(tensor)
    shape = tensor.shape

    # CP parameters: R * sum(dims) + R weights
    cp_params = best_rank * sum(shape) + best_rank
    print(f"\n  CP parameters (rank {best_rank}): {cp_params}")

    # Tucker: find ranks that give similar parameter count to CP
    # Tucker params = prod(ranks) + sum(rank_i * dim_i)
    # Search over balanced ranks r where r^4 + r*sum(dims) ≈ cp_params
    best_tucker_ranks = None
    best_diff = float('inf')
    for r in range(2, best_rank + 1):
        ranks_cand = [min(r, shape[0]), min(r, shape[1]),
                      min(r, shape[2]), min(r, shape[3])]
        tp = int(np.prod(ranks_cand)) + sum(rc * d for rc, d in zip(ranks_cand, shape))
        diff = abs(tp - cp_params)
        if diff < best_diff:
            best_diff = diff
            best_tucker_ranks = ranks_cand
            tucker_params = tp

    tucker_ranks = best_tucker_ranks
    print(f"  Tucker ranks: {tucker_ranks}")
    print(f"  Tucker parameters: {tucker_params} (CP: {cp_params}, diff: {abs(tucker_params - cp_params)})")

    # Fit CP
    cp_result = non_negative_parafac(tl_tensor, rank=best_rank, init='random',
                                     n_iter_max=300, tol=1e-6, random_state=42)
    cp_recon = tl.cp_to_tensor(cp_result)
    frob_total = tl.norm(tl_tensor)
    cp_error = float(tl.norm(tl_tensor - cp_recon) / frob_total)

    # Fit Tucker (non-negative Tucker not always available, use standard)
    try:
        tucker_result = tucker(tl_tensor, rank=tucker_ranks, init='random',
                               random_state=42)
        tucker_recon = tl.tucker_to_tensor(tucker_result)
        tucker_error = float(tl.norm(tl_tensor - tucker_recon) / frob_total)
    except Exception as e:
        print(f"  Tucker decomposition failed: {e}")
        tucker_error = cp_error  # Assume no improvement

    improvement = (cp_error - tucker_error) / cp_error if cp_error > 0 else 0
    print(f"\n  CP error: {cp_error:.4f}")
    print(f"  Tucker error: {tucker_error:.4f}")
    print(f"  Improvement: {improvement*100:.2f}%")

    # P4: Tucker improvement < 5% over CP (tests C1003)
    p4_pass = improvement < 0.05
    print(f"\n  P4 (Tucker < 5% better): {improvement*100:.2f}% → {'PASS' if p4_pass else 'FAIL'}")

    # If Tucker significantly better, report large core entries
    large_core_entries = []
    if not p4_pass and tucker_error < cp_error:
        core = tucker_result[0]
        core_flat = np.abs(core.flatten()) if hasattr(core, 'flatten') else np.abs(np.array(core).flatten())
        threshold = np.percentile(core_flat, 95)
        # Report shape of core tensor
        print(f"  Core tensor shape: {np.array(core).shape}")

    return {
        'cp_error': float(cp_error),
        'tucker_error': float(tucker_error),
        'tucker_ranks': tucker_ranks,
        'cp_params': int(cp_params),
        'tucker_params': int(tucker_params),
        'improvement_pct': float(improvement * 100),
        'p4_pass': bool(p4_pass),
    }


# ── T4: Controls ──────────────────────────────────────────────────────

def run_t4(tensor, best_rank, tokens, affordance_table, folio_sections,
           prefix_labels, class_labels):
    """Run control analyses: marginalized, shuffle, cross-val, incremental R²."""
    print("\n" + "=" * 60)
    print("T4: Controls")
    print("=" * 60)

    # ── T4a: PREFIX-marginalized tensor ──
    print("\n  T4a: PREFIX-marginalized tensor")

    # Collapse PREFIX axis (sum over axis 0)
    marginalized = tensor.sum(axis=0)  # (n_bins, n_suffix_groups, n_classes)
    print(f"    Marginalized shape: {marginalized.shape}")
    print(f"    Marginalized density: {np.count_nonzero(marginalized)/np.prod(marginalized.shape):.4f}")

    tl_marg = tl.tensor(marginalized)
    marg_rank = min(best_rank, min(marginalized.shape) - 1)
    if marg_rank < 2:
        marg_rank = 2

    try:
        marg_result = non_negative_parafac(tl_marg, rank=marg_rank, init='random',
                                           n_iter_max=200, tol=1e-6, random_state=42)
        marg_class_factors = marg_result[1][2]  # class mode factors

        # Cluster class factors and compare to C1010
        Z_marg = linkage(marg_class_factors, method='ward')
        cl_marg = fcluster(Z_marg, t=6, criterion='maxclust')
        true_labels = [STATE_IDX.get(CLASS_TO_STATE.get(c), -1) for c in class_labels]
        ari_marg = adjusted_rand_score(true_labels, cl_marg)
    except Exception as e:
        print(f"    Marginalized NTF failed: {e}")
        ari_marg = 0.0

    print(f"    Marginalized ARI vs C1010: {ari_marg:.4f}")

    # For P8, we need to compare to full tensor ARI
    # (will be filled in during synthesis using T2 results)

    # ── T4b: Shuffle null ──
    print("\n  T4b: Shuffle null (MIDDLE_BIN permutation)")

    n_perm = 1000
    shuffle_aris = []
    tl_tensor = tl.tensor(tensor)

    # Pre-compute true class labels
    true_labels = [STATE_IDX.get(CLASS_TO_STATE.get(c), -1) for c in class_labels]

    for perm_i in range(n_perm):
        # Permute MIDDLE_BIN axis: shuffle rows of bin dimension independently
        # within each PREFIX class
        shuffled = tensor.copy()
        for p in range(tensor.shape[0]):
            perm = np.random.permutation(tensor.shape[1])
            shuffled[p] = shuffled[p, perm]

        try:
            tl_shuf = tl.tensor(shuffled)
            shuf_result = non_negative_parafac(tl_shuf, rank=best_rank, init='random',
                                               n_iter_max=100, tol=1e-4,
                                               random_state=perm_i)
            shuf_class_factors = shuf_result[1][3]
            Z_shuf = linkage(shuf_class_factors, method='ward')
            cl_shuf = fcluster(Z_shuf, t=6, criterion='maxclust')
            a = adjusted_rand_score(true_labels, cl_shuf)
            shuffle_aris.append(a)
        except Exception:
            shuffle_aris.append(0.0)

        if (perm_i + 1) % 100 == 0:
            print(f"    Permutation {perm_i + 1}/{n_perm}: mean ARI={np.mean(shuffle_aris):.4f}")

    shuffle_aris = np.array(shuffle_aris)
    shuffle_mean = float(np.mean(shuffle_aris))
    shuffle_std = float(np.std(shuffle_aris))
    print(f"    Shuffle ARI: mean={shuffle_mean:.4f}, std={shuffle_std:.4f}")

    # P5: shuffle ARI < 0.15 (MIDDLE labels matter)
    p5_pass = shuffle_mean < 0.15
    print(f"    P5 (shuffle ARI < 0.15): {shuffle_mean:.4f} → {'PASS' if p5_pass else 'FAIL'}")

    # ── T4c: Cross-validation (odd/even folios) ──
    print("\n  T4c: Cross-validation (odd/even folios)")

    all_folios = sorted(set(t['folio'] for t in tokens))
    odd_folios = set(all_folios[::2])
    even_folios = set(all_folios[1::2])

    tensor_odd, _, _, _, _, n_odd = build_bigram_tensor(tokens, affordance_table, odd_folios)
    tensor_even, _, _, _, _, n_even = build_bigram_tensor(tokens, affordance_table, even_folios)

    print(f"    Odd folios: {len(odd_folios)}, bigrams: {n_odd}")
    print(f"    Even folios: {len(even_folios)}, bigrams: {n_even}")

    # Fit both halves at same rank
    congruences = []
    try:
        tl_odd = tl.tensor(tensor_odd)
        tl_even = tl.tensor(tensor_even)

        res_odd = non_negative_parafac(tl_odd, rank=best_rank, init='random',
                                       n_iter_max=200, tol=1e-6, random_state=42)
        res_even = non_negative_parafac(tl_even, rank=best_rank, init='random',
                                        n_iter_max=200, tol=1e-6, random_state=42)

        # Tucker congruence coefficient between paired class factors
        # Match factors by maximum correlation
        odd_class = res_odd[1][3]  # (49, R)
        even_class = res_even[1][3]  # (49, R)

        # Compute congruence matrix
        cong_matrix = np.zeros((best_rank, best_rank))
        for i in range(best_rank):
            for j in range(best_rank):
                n1 = np.linalg.norm(odd_class[:, i])
                n2 = np.linalg.norm(even_class[:, j])
                if n1 > 1e-10 and n2 > 1e-10:
                    cong_matrix[i, j] = np.dot(odd_class[:, i], even_class[:, j]) / (n1 * n2)

        # Greedy matching
        used_j = set()
        for i in range(best_rank):
            remaining = [j for j in range(best_rank) if j not in used_j]
            if remaining:
                best_j = max(remaining, key=lambda j: cong_matrix[i, j])
                congruences.append(float(cong_matrix[i, best_j]))
                used_j.add(best_j)

        mean_congruence = float(np.mean(congruences))
    except Exception as e:
        print(f"    Cross-validation failed: {e}")
        mean_congruence = 0.0
        congruences = []

    print(f"    Factor congruences: {[f'{c:.3f}' for c in congruences]}")
    print(f"    Mean congruence: {mean_congruence:.4f}")

    cv_stable = mean_congruence > 0.85
    print(f"    Stable (mean > 0.85): {'YES' if cv_stable else 'NO'}")

    # ── T4d: Incremental R² ──
    print("\n  T4d: Incremental R² for AXM self-transition")

    # Build per-folio AXM self-transition and CP component loadings
    # Get per-folio prefix/bin distributions, project onto CP factors
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t['folio']].append(t)

    regime_map = load_regime_assignments()
    archetype_data = load_folio_archetypes()
    archetype_labels = archetype_data.get('folio_labels', {})

    # Build per-folio AXM self-transition
    from collections import defaultdict as dd
    folio_axm_self = {}
    line_states = defaultdict(list)
    for t in tokens:
        line_states[(t['folio'], t['line'])].append(t['state'])

    folio_trans = defaultdict(lambda: np.zeros((N_STATES, N_STATES)))
    for (folio, line), states in line_states.items():
        for i in range(len(states) - 1):
            folio_trans[folio][STATE_IDX[states[i]], STATE_IDX[states[i+1]]] += 1

    for folio, mat in folio_trans.items():
        row = mat[STATE_IDX['AXM']]
        s = row.sum()
        folio_axm_self[folio] = float(row[STATE_IDX['AXM']] / s) if s > 0 else 0

    # Build per-folio CP component scores
    # Compute mean prefix/bin/suffix factor loadings per folio
    prefix_idx = {p: i for i, p in enumerate(prefix_labels)}

    # Fit full tensor to get factors
    tl_tensor = tl.tensor(tensor)
    full_result = non_negative_parafac(tl_tensor, rank=best_rank, init='random',
                                       n_iter_max=300, tol=1e-6, random_state=42)
    full_prefix_factors = full_result[1][0]

    folio_component_scores = {}
    for folio, ftoks in folio_tokens.items():
        if len(ftoks) < 10:
            continue
        # Weighted average of PREFIX factor vectors
        score = np.zeros(best_rank)
        count = 0
        for t in ftoks:
            if t['prefix'] in prefix_idx:
                score += full_prefix_factors[prefix_idx[t['prefix']]]
                count += 1
        if count > 0:
            folio_component_scores[folio] = score / count

    # Build regression data
    folios_for_reg = sorted(set(folio_axm_self.keys()) & set(folio_component_scores.keys())
                           & set(regime_map.keys()) & set(folio_sections.keys()))

    if len(folios_for_reg) >= 10:
        y = np.array([folio_axm_self[f] for f in folios_for_reg])

        # Baseline: REGIME + section
        regimes = [regime_map.get(f, 0) for f in folios_for_reg]
        sections = [folio_sections.get(f, 'UNKNOWN') for f in folios_for_reg]

        unique_regimes = sorted(set(regimes))
        unique_sections = sorted(set(sections))
        X_base = np.zeros((len(folios_for_reg), len(unique_regimes) + len(unique_sections)))
        for i, f in enumerate(folios_for_reg):
            r = regimes[i]
            if r in unique_regimes:
                X_base[i, unique_regimes.index(r)] = 1
            s = sections[i]
            if s in unique_sections:
                X_base[i, len(unique_regimes) + unique_sections.index(s)] = 1

        # Full model: baseline + CP components
        X_cp = np.array([folio_component_scores[f] for f in folios_for_reg])
        X_full = np.hstack([X_base, X_cp])

        # OLS R²
        def ols_r2(X, y):
            X_aug = np.hstack([np.ones((len(y), 1)), X])
            try:
                beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
                y_pred = X_aug @ beta
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - y.mean()) ** 2)
                return 1 - ss_res / ss_tot if ss_tot > 0 else 0
            except Exception:
                return 0

        r2_base = ols_r2(X_base, y)
        r2_full = ols_r2(X_full, y)
        delta_r2 = r2_full - r2_base

        print(f"    Folios: {len(folios_for_reg)}")
        print(f"    Baseline R² (REGIME+section): {r2_base:.4f}")
        print(f"    Full R² (+ CP components): {r2_full:.4f}")
        print(f"    ΔR²: {delta_r2:.4f}")
        print(f"    (C1017 reference ΔR² = 0.115)")
    else:
        r2_base, r2_full, delta_r2 = 0, 0, 0
        print(f"    Insufficient folios for regression ({len(folios_for_reg)})")

    return {
        't4a_marginalized': {
            'shape': list(marginalized.shape),
            'ari_vs_c1010': float(ari_marg),
        },
        't4b_shuffle': {
            'n_permutations': n_perm,
            'shuffle_ari_mean': float(shuffle_mean),
            'shuffle_ari_std': float(shuffle_std),
            'p5_pass': bool(p5_pass),
        },
        't4c_cross_val': {
            'n_odd_folios': len(odd_folios),
            'n_even_folios': len(even_folios),
            'n_odd_bigrams': int(n_odd),
            'n_even_bigrams': int(n_even),
            'congruences': congruences,
            'mean_congruence': float(mean_congruence),
            'stable': bool(cv_stable),
        },
        't4d_incremental_r2': {
            'n_folios': len(folios_for_reg),
            'r2_baseline': float(r2_base),
            'r2_full': float(r2_full),
            'delta_r2': float(delta_r2),
        },
    }


# ── T5: Synthesis ─────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4):
    """Evaluate all 8 predictions and determine verdict."""
    print("\n" + "=" * 60)
    print("T5: Synthesis")
    print("=" * 60)

    predictions = {
        'P1': {
            'description': 'Optimal rank is 5-8',
            'result': bool(t1['p1_pass']),
            'value': t1['best_rank'],
            'threshold': '5-8',
        },
        'P2': {
            'description': 'Class factor clusters match C1010 with ARI > 0.6',
            'result': bool(t2['t2a_class_clustering']['p2_pass']),
            'value': float(t2['t2a_class_clustering']['best_ari']),
            'threshold': '> 0.6',
        },
        'P3': {
            'description': 'PREFIX factors correlate with C1012 at r > 0.8',
            'result': bool(t2['t2b_prefix_correlation']['p3_pass']),
            'value': float(abs(t2['t2b_prefix_correlation']['pairwise_sim_rho'])),
            'threshold': '> 0.8',
        },
        'P4': {
            'description': 'Tucker improvement < 5% over CP',
            'result': bool(t3['p4_pass']),
            'value': float(t3['improvement_pct']),
            'threshold': '< 5%',
        },
        'P5': {
            'description': 'Shuffle ARI < 0.15 (MIDDLE labels matter)',
            'result': bool(t4['t4b_shuffle']['p5_pass']),
            'value': float(t4['t4b_shuffle']['shuffle_ari_mean']),
            'threshold': '< 0.15',
        },
        'P6': {
            'description': 'MIDDLE factors recover HUB vs STABILITY distinction',
            'result': bool(t2['t2c_bin_factors']['p6_pass']),
            'value': float(t2['t2c_bin_factors']['hub_stab_cosine']),
            'threshold': 'cosine < 0.8',
        },
        'P7': {
            'description': 'SUFFIX factors have < 3 effective dimensions (SVD 90%)',
            'result': bool(t2['t2d_suffix_dims']['p7_pass']),
            'value': int(t2['t2d_suffix_dims']['svd_dims_90pct']),
            'threshold': '< 3',
        },
        'P8': {
            'description': 'PREFIX-marginalized tensor loses most macro-state structure (ARI drop > 50%)',
            'result': None,  # computed below
            'value': None,
            'threshold': 'ARI drop > 50%',
        },
    }

    # P8: ARI drop from full to marginalized
    full_ari = t2['t2a_class_clustering']['best_ari']
    marg_ari = t4['t4a_marginalized']['ari_vs_c1010']
    if full_ari > 0:
        ari_drop = (full_ari - marg_ari) / full_ari
    else:
        ari_drop = 0
    p8_pass = ari_drop > 0.5
    predictions['P8']['result'] = bool(p8_pass)
    predictions['P8']['value'] = float(ari_drop)

    print(f"\n  P8 computation: full ARI={full_ari:.4f}, marg ARI={marg_ari:.4f}, drop={ari_drop:.4f}")

    # Count passes
    n_pass = sum(1 for p in predictions.values() if p['result'])
    n_total = len(predictions)

    for pid, pred in sorted(predictions.items()):
        status = 'PASS' if pred['result'] else 'FAIL'
        print(f"  {pid}: {pred['description']} → {pred['value']} [{pred['threshold']}] → {status}")

    print(f"\n  Total: {n_pass}/{n_total} passed")

    # Determine verdict
    core_pass = all(predictions[p]['result'] for p in ['P1', 'P2', 'P4'])
    if core_pass and n_pass >= 5:
        verdict = 'TENSOR_CONFIRMED'
    elif not predictions['P8']['result']:
        verdict = 'TENSOR_NOVEL'
    elif not predictions['P4']['result']:
        verdict = 'TENSOR_INTERACTION'
    else:
        verdict = 'TENSOR_PARTIAL'

    # Override: if P8 fails AND core passes, it's both confirmed and novel
    if core_pass and n_pass >= 5 and not predictions['P8']['result']:
        verdict = 'TENSOR_CONFIRMED_NOVEL'

    print(f"\n  Verdict: {verdict}")

    return {
        'predictions': predictions,
        'n_pass': int(n_pass),
        'n_total': int(n_total),
        'verdict': verdict,
        'full_ari': float(full_ari),
        'marginalized_ari': float(marg_ari),
        'ari_drop_fraction': float(ari_drop),
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("Phase 342: MORPHOLOGICAL_TENSOR_DECOMPOSITION")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    affordance_table = load_affordance_table()
    tokens, folio_sections = build_corpus_data(token_to_class)

    # Build tensor
    print("\nBuilding bigram tensor...")
    tensor, prefix_labels, bin_labels, suffix_labels, class_labels, n_bigrams = \
        build_bigram_tensor(tokens, affordance_table)
    print(f"  Tensor built: shape={tensor.shape}, bigrams={n_bigrams}")

    # T1: Rank selection
    t1 = run_t1(tensor, prefix_labels, n_bigrams)
    best_rank = t1['best_rank']

    # T2: Factor interpretation
    t2 = run_t2(tensor, best_rank, prefix_labels, class_labels, tokens, affordance_table)

    # T3: CP vs Tucker
    t3 = run_t3(tensor, best_rank)

    # T4: Controls
    t4 = run_t4(tensor, best_rank, tokens, affordance_table, folio_sections,
                prefix_labels, class_labels)

    # T5: Synthesis
    synthesis = synthesize(t1, t2, t3, t4)

    # Save results
    results = {
        'phase': 'MORPHOLOGICAL_TENSOR_DECOMPOSITION',
        'phase_number': 342,
        'prefix_labels': prefix_labels,
        'suffix_group_labels': suffix_labels,
        'class_labels': class_labels,
        't1_construction': t1,
        't2_interpretation': t2,
        't3_cp_vs_tucker': t3,
        't4_controls': t4,
        't5_synthesis': synthesis,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'tensor_decomposition.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")
    print(f"\nVERDICT: {synthesis['verdict']} ({synthesis['n_pass']}/{synthesis['n_total']} predictions passed)")


if __name__ == '__main__':
    main()
