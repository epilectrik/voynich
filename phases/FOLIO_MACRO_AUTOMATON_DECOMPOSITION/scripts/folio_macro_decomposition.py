#!/usr/bin/env python3
"""
Phase 339: FOLIO_MACRO_AUTOMATON_DECOMPOSITION
===============================================
Decomposes the corpus-wide 6-state macro-automaton (C1010/C1015) to the
folio (program) level, testing whether individual programs have distinct
dynamical profiles and connecting them to design asymmetry (C458),
forgiveness gradient, and REGIME structure (C979).

Tests:
  T1: Per-folio macro-state census (occupancy, transition matrices, sparsity)
  T2: Dynamical archetype discovery (clustering, ARI vs REGIME/section)
  T3: C458 dynamical realization (hazard CV clamped, recovery CV free)
  T4: Forgiveness gradient decomposition (which transitions drive forgiveness)
  T5: Restart folio signature (f50v, f57r, f82v profiling)
  T6: Variance decomposition (ANOVA: REGIME, section, residual)
  T7: Geometry/topology independence (manifold centroids vs archetypes)
  T8: Bridge conduit test (bridge vs full manifold archetype prediction)
  T9: Synthesis / verdict

Depends on: C1010 (6-state partition), C1015 (transition matrix), C458 (design
            asymmetry), C979 (REGIME modulation), C980 (free variation envelope)
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

# Canonical 6-state partition (FROZEN, from C1010/Phase 328)
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

MIN_TRANSITIONS = 50  # Minimum transitions for reliable matrix estimation

RESTART_FOLIOS = {'f50v', 'f57r', 'f82v'}

# Hazard / escape token definitions (from SISTER analysis)
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}
HAZARD_TOKENS = HAZARD_SOURCES | HAZARD_TARGETS


# ── Data Loading ─────────────────────────────────────────────────────

def load_token_to_class():
    """Load token→class mapping from CLASS_COSURVIVAL_TEST."""
    path = Path(__file__).resolve().parents[2] / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    return data['token_to_class']


def load_regime_assignments():
    """Load folio→REGIME mapping from OPS2."""
    path = Path(__file__).resolve().parents[2] / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def build_folio_data(token_to_class):
    """Build per-folio token sequences and metadata from B corpus.

    Returns:
        folio_lines: dict of {folio: {(folio, line): [state1, state2, ...]}}
        folio_sections: dict of {folio: section_name}
        folio_tokens: dict of {folio: [word1, word2, ...]}
    """
    tx = Transcript()

    # Group tokens by (folio, line) for transition counting
    lines = defaultdict(list)   # (folio, line) → [words]
    folio_sections = {}
    folio_tokens = defaultdict(list)

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        lines[(token.folio, token.line)].append(w)
        folio_sections[token.folio] = token.section
        folio_tokens[token.folio].append(w)

    # Map words to macro states, grouped by folio
    folio_line_states = defaultdict(dict)  # folio → {(folio, line): [states]}
    n_unmapped = 0

    for (folio, line_id), words in lines.items():
        line_states = []
        for w in words:
            cls = token_to_class.get(w)
            if cls is None:
                n_unmapped += 1
                continue
            state = CLASS_TO_STATE.get(int(cls))
            if state is None:
                n_unmapped += 1
                continue
            line_states.append(state)
        if line_states:
            folio_line_states[folio][(folio, line_id)] = line_states

    print(f"  Loaded {len(folio_line_states)} folios")
    print(f"  Unmapped tokens: {n_unmapped}")

    return folio_line_states, folio_sections, folio_tokens


def compute_folio_matrices(folio_line_states):
    """Compute per-folio transition count matrices and state distributions.

    Returns dict of {folio: {
        'trans_counts': np.array (6×6),
        'state_counts': np.array (6,),
        'n_transitions': int,
        'n_tokens': int,
        'trans_prob': np.array (6×6) or None if too sparse,
        'state_dist': np.array (6,),
    }}
    """
    results = {}

    for folio, line_dict in folio_line_states.items():
        trans_counts = np.zeros((N_STATES, N_STATES), dtype=int)
        state_counts = np.zeros(N_STATES, dtype=int)
        n_tokens = 0

        for (_, _), states in line_dict.items():
            for s in states:
                state_counts[STATE_IDX[s]] += 1
                n_tokens += 1
            for i in range(len(states) - 1):
                s_from = states[i]
                s_to = states[i + 1]
                trans_counts[STATE_IDX[s_from], STATE_IDX[s_to]] += 1

        n_transitions = trans_counts.sum()

        # State distribution (always computable)
        state_dist = state_counts / state_counts.sum() if state_counts.sum() > 0 else state_counts.astype(float)

        # Transition probability matrix (only if enough data)
        trans_prob = None
        if n_transitions >= MIN_TRANSITIONS:
            row_sums = trans_counts.sum(axis=1, keepdims=True)
            # Avoid division by zero for rows with no transitions
            row_sums = np.where(row_sums == 0, 1, row_sums)
            trans_prob = trans_counts / row_sums

        results[folio] = {
            'trans_counts': trans_counts,
            'state_counts': state_counts,
            'n_transitions': int(n_transitions),
            'n_tokens': int(n_tokens),
            'trans_prob': trans_prob,
            'state_dist': state_dist,
        }

    return results


def compute_forgiveness(folio_tokens):
    """Compute forgiveness metrics per folio (replicating SISTER analysis)."""
    results = {}
    for folio, tokens in folio_tokens.items():
        if len(tokens) < 10:
            continue

        hazard_count = sum(1 for t in tokens if t in HAZARD_TOKENS)
        hazard_density = hazard_count / len(tokens)

        escape_count = sum(1 for t in tokens if t.startswith('qo'))
        escape_density = escape_count / len(tokens)

        max_safe_run = 0
        current_run = 0
        for t in tokens:
            if t in HAZARD_TOKENS:
                max_safe_run = max(max_safe_run, current_run)
                current_run = 0
            else:
                current_run += 1
        max_safe_run = max(max_safe_run, current_run)

        score = -hazard_density * 10 + escape_density * 10 + min(max_safe_run, 50) / 50

        results[folio] = {
            'hazard_density': hazard_density,
            'escape_density': escape_density,
            'max_safe_run': max_safe_run,
            'forgiveness': score,
        }

    return results


# ── T1: Per-Folio Macro-State Census ─────────────────────────────────

def run_t1(folio_matrices):
    """Census of per-folio macro-state distributions and transition matrices."""
    print("\n" + "=" * 60)
    print("T1: Per-Folio Macro-State Census")
    print("=" * 60)

    n_folios = len(folio_matrices)
    n_sufficient = sum(1 for d in folio_matrices.values() if d['n_transitions'] >= MIN_TRANSITIONS)
    n_total_transitions = sum(d['n_transitions'] for d in folio_matrices.values())
    n_total_tokens = sum(d['n_tokens'] for d in folio_matrices.values())

    print(f"\n  Total folios: {n_folios}")
    print(f"  Total mapped tokens: {n_total_tokens}")
    print(f"  Total transitions: {n_total_transitions}")
    print(f"  Folios with N>={MIN_TRANSITIONS} transitions: {n_sufficient}/{n_folios}")

    # Transition count distribution
    trans_counts = sorted([d['n_transitions'] for d in folio_matrices.values()])
    print(f"\n  Transition count distribution:")
    print(f"    Min: {trans_counts[0]}, Q1: {trans_counts[len(trans_counts)//4]}, "
          f"Median: {trans_counts[len(trans_counts)//2]}, Q3: {trans_counts[3*len(trans_counts)//4]}, "
          f"Max: {trans_counts[-1]}")

    # Low-N folios
    low_n = [(f, d['n_transitions']) for f, d in folio_matrices.items() if d['n_transitions'] < MIN_TRANSITIONS]
    if low_n:
        low_n.sort(key=lambda x: x[1])
        print(f"\n  Low-N folios (<{MIN_TRANSITIONS} transitions): {len(low_n)}")
        for f, n in low_n[:10]:
            print(f"    {f}: {n} transitions")

    # State occupancy statistics across folios
    state_dists = np.array([d['state_dist'] for d in folio_matrices.values()])
    print(f"\n  State occupancy across {n_folios} folios:")
    print(f"  {'State':<10} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8} {'CV':>8}")
    for i, s in enumerate(STATE_ORDER):
        col = state_dists[:, i]
        mean_v = col.mean()
        std_v = col.std()
        cv = std_v / mean_v if mean_v > 0 else float('inf')
        print(f"  {s:<10} {mean_v:>8.4f} {std_v:>8.4f} {col.min():>8.4f} {col.max():>8.4f} {cv:>8.3f}")

    # Sparsity metrics for sufficient-N folios
    sufficient = {f: d for f, d in folio_matrices.items() if d['n_transitions'] >= MIN_TRANSITIONS}
    if sufficient:
        zero_fracs = []
        for d in sufficient.values():
            zero_frac = (d['trans_counts'] == 0).sum() / (N_STATES * N_STATES)
            zero_fracs.append(zero_frac)
        print(f"\n  Sparsity (folios with N>={MIN_TRANSITIONS}):")
        print(f"    Mean % zero cells: {np.mean(zero_fracs)*100:.1f}%")
        print(f"    Range: {np.min(zero_fracs)*100:.1f}% - {np.max(zero_fracs)*100:.1f}%")

    # Prediction P1: >=70 folios with N>=50
    p1_pass = n_sufficient >= 70
    print(f"\n  P1: {n_sufficient} folios with N>={MIN_TRANSITIONS} (threshold: 70)")
    print(f"  Verdict: {'PASS' if p1_pass else 'FAIL'}")

    # Corpus-wide matrix from per-folio sums (sanity check)
    corpus_counts = sum(d['trans_counts'] for d in folio_matrices.values())
    corpus_total = corpus_counts.sum()
    print(f"\n  Sanity check: per-folio transition sum = {corpus_total} (should match ~13,645)")

    return {
        'n_folios': n_folios,
        'n_sufficient': n_sufficient,
        'n_total_transitions': int(n_total_transitions),
        'n_total_tokens': int(n_total_tokens),
        'transition_quantiles': {
            'min': int(trans_counts[0]),
            'q1': int(trans_counts[len(trans_counts)//4]),
            'median': int(trans_counts[len(trans_counts)//2]),
            'q3': int(trans_counts[3*len(trans_counts)//4]),
            'max': int(trans_counts[-1]),
        },
        'n_low_n': len(low_n),
        'state_occupancy_stats': {
            s: {
                'mean': round(float(state_dists[:, i].mean()), 4),
                'std': round(float(state_dists[:, i].std()), 4),
                'cv': round(float(state_dists[:, i].std() / state_dists[:, i].mean()), 3) if state_dists[:, i].mean() > 0 else None,
            }
            for i, s in enumerate(STATE_ORDER)
        },
        'mean_sparsity': round(float(np.mean(zero_fracs)), 3) if sufficient else None,
        'pass': p1_pass,
    }


# ── T2: Dynamical Archetype Discovery ────────────────────────────────

def run_t2(folio_matrices, regime_map, section_map):
    """Cluster folios by dynamical profiles and compare to REGIME/section."""
    print("\n" + "=" * 60)
    print("T2: Dynamical Archetype Discovery")
    print("=" * 60)

    # Only use folios with sufficient transitions
    sufficient = {f: d for f, d in folio_matrices.items() if d['n_transitions'] >= MIN_TRANSITIONS}
    folios = sorted(sufficient.keys())
    n = len(folios)
    print(f"\n  Using {n} folios with N>={MIN_TRANSITIONS} transitions")

    # Feature extraction: key transition features per folio
    # AXM self, AXM→FQ, FQ→AXM, FL_HAZ occupancy, FL_SAFE occupancy, CC occupancy
    features = []
    for f in folios:
        d = sufficient[f]
        tp = d['trans_prob']
        sd = d['state_dist']
        feat = [
            tp[STATE_IDX['AXM'], STATE_IDX['AXM']],       # AXM self-transition
            tp[STATE_IDX['AXM'], STATE_IDX['FQ']],         # AXM→FQ
            tp[STATE_IDX['FQ'], STATE_IDX['AXM']],         # FQ→AXM
            sd[STATE_IDX['FL_HAZ']],                        # FL_HAZ occupancy
            sd[STATE_IDX['FL_SAFE']],                       # FL_SAFE occupancy
            sd[STATE_IDX['CC']],                            # CC occupancy
        ]
        features.append(feat)

    X = np.array(features)
    feature_names = ['AXM_self', 'AXM_to_FQ', 'FQ_to_AXM', 'FL_HAZ_occ', 'FL_SAFE_occ', 'CC_occ']

    print(f"  Feature matrix: {X.shape}")
    print(f"  Features: {feature_names}")

    # Standardize for clustering
    X_std = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-10)

    # Hierarchical clustering with Ward linkage
    dist_matrix = pdist(X_std, metric='euclidean')
    Z = linkage(dist_matrix, method='ward')

    # Silhouette analysis for k=2..8
    from sklearn.metrics import silhouette_score, adjusted_rand_score

    silhouette_scores = {}
    for k in range(2, min(9, n)):
        labels = fcluster(Z, t=k, criterion='maxclust')
        sil = silhouette_score(X_std, labels, metric='euclidean')
        silhouette_scores[k] = round(float(sil), 4)
        print(f"    k={k}: silhouette={sil:.4f}")

    best_k = max(silhouette_scores, key=silhouette_scores.get)
    best_sil = silhouette_scores[best_k]
    print(f"\n  Best k: {best_k} (silhouette={best_sil:.4f})")

    # Get cluster assignments at best k
    best_labels = fcluster(Z, t=best_k, criterion='maxclust')

    # ARI vs REGIME
    regime_labels = []
    for f in folios:
        regime_labels.append(regime_map.get(f, 'UNKNOWN'))
    regime_numeric = {r: i for i, r in enumerate(sorted(set(regime_labels)))}
    regime_ints = [regime_numeric[r] for r in regime_labels]
    ari_regime = adjusted_rand_score(regime_ints, best_labels)
    print(f"  ARI(archetypes, REGIME): {ari_regime:.4f}")

    # ARI vs section
    section_labels = []
    for f in folios:
        section_labels.append(section_map.get(f, 'UNKNOWN'))
    section_numeric = {s: i for i, s in enumerate(sorted(set(section_labels)))}
    section_ints = [section_numeric[s] for s in section_labels]
    ari_section = adjusted_rand_score(section_ints, best_labels)
    print(f"  ARI(archetypes, section): {ari_section:.4f}")

    # Archetype profiles
    print(f"\n  Archetype profiles (k={best_k}):")
    for c in range(1, best_k + 1):
        mask = best_labels == c
        n_members = mask.sum()
        cluster_regimes = Counter(regime_labels[i] for i in range(len(folios)) if best_labels[i] == c)
        cluster_sections = Counter(section_labels[i] for i in range(len(folios)) if best_labels[i] == c)
        mean_feat = X[mask].mean(axis=0)
        print(f"\n  Archetype {c} (n={n_members}):")
        print(f"    REGIMEs: {dict(cluster_regimes)}")
        print(f"    Sections: {dict(cluster_sections)}")
        for j, fn in enumerate(feature_names):
            print(f"    {fn}: {mean_feat[j]:.4f}")

    # P2: optimal k > 4 OR ARI < 0.5
    p2_pass = best_k > 4 or ari_regime < 0.5
    print(f"\n  P2: best_k={best_k} (>4?) OR ARI(REGIME)={ari_regime:.4f} (<0.5?)")
    print(f"  Verdict: {'PASS' if p2_pass else 'FAIL'}")

    return {
        'n_folios_used': n,
        'feature_names': feature_names,
        'silhouette_scores': silhouette_scores,
        'best_k': best_k,
        'best_silhouette': best_sil,
        'ari_regime': round(float(ari_regime), 4),
        'ari_section': round(float(ari_section), 4),
        'archetype_sizes': {str(c): int((best_labels == c).sum()) for c in range(1, best_k + 1)},
        'folio_labels': {folios[i]: int(best_labels[i]) for i in range(n)},
        'pass': p2_pass,
    }


# ── T3: C458 Dynamical Realization ───────────────────────────────────

def run_t3(folio_matrices):
    """Test whether hazard transitions are clamped and recovery transitions are free."""
    print("\n" + "=" * 60)
    print("T3: C458 Dynamical Realization (Hazard Clamped / Recovery Free)")
    print("=" * 60)

    sufficient = {f: d for f, d in folio_matrices.items() if d['n_transitions'] >= MIN_TRANSITIONS}
    folios = sorted(sufficient.keys())
    n = len(folios)

    # Define transition groups
    # Hazard transitions: involving FL_HAZ as source or target
    fl_haz_idx = STATE_IDX['FL_HAZ']
    hazard_cells = []
    for i in range(N_STATES):
        hazard_cells.append((fl_haz_idx, i))  # FL_HAZ → any
        if i != fl_haz_idx:
            hazard_cells.append((i, fl_haz_idx))  # any → FL_HAZ
    hazard_cells = list(set(hazard_cells))

    # Recovery transitions: AXM self-loop, AXM↔FQ
    axm_idx = STATE_IDX['AXM']
    fq_idx = STATE_IDX['FQ']
    recovery_cells = [
        (axm_idx, axm_idx),    # AXM self
        (axm_idx, fq_idx),     # AXM→FQ
        (fq_idx, axm_idx),     # FQ→AXM
    ]

    # CC initiator transitions: involving CC
    cc_idx = STATE_IDX['CC']
    initiator_cells = []
    for i in range(N_STATES):
        initiator_cells.append((cc_idx, i))
        if i != cc_idx:
            initiator_cells.append((i, cc_idx))
    initiator_cells = list(set(initiator_cells))

    def compute_cv_for_group(cells, label):
        """Compute CV of each transition probability across folios."""
        cell_values = defaultdict(list)
        for f in folios:
            tp = sufficient[f]['trans_prob']
            for (r, c) in cells:
                cell_values[(r, c)].append(tp[r, c])

        cvs = []
        cell_details = []
        for (r, c), vals in cell_values.items():
            vals = np.array(vals)
            mean_v = vals.mean()
            std_v = vals.std()
            cv = std_v / mean_v if mean_v > 0.001 else None  # Skip near-zero transitions
            if cv is not None:
                cvs.append(cv)
                cell_details.append({
                    'from': STATE_ORDER[r],
                    'to': STATE_ORDER[c],
                    'mean': round(float(mean_v), 4),
                    'std': round(float(std_v), 4),
                    'cv': round(float(cv), 3),
                })

        mean_cv = np.mean(cvs) if cvs else None
        print(f"\n  {label} transitions ({len(cells)} cells, {len(cvs)} with mean>0.001):")
        print(f"    Mean CV: {mean_cv:.3f}" if mean_cv is not None else "    Mean CV: N/A")
        for d in sorted(cell_details, key=lambda x: x['cv']):
            print(f"    {d['from']}->{d['to']}: mean={d['mean']:.4f}, std={d['std']:.4f}, CV={d['cv']:.3f}")

        return mean_cv, cell_details

    hazard_cv, hazard_details = compute_cv_for_group(hazard_cells, "Hazard (FL_HAZ)")
    recovery_cv, recovery_details = compute_cv_for_group(recovery_cells, "Recovery (AXM/FQ)")
    initiator_cv, initiator_details = compute_cv_for_group(initiator_cells, "Initiator (CC)")

    # P3: hazard CV < 0.20, recovery CV > 0.50
    p3_hazard = hazard_cv is not None and hazard_cv < 0.20
    p3_recovery = recovery_cv is not None and recovery_cv > 0.50
    p3_pass = p3_hazard and p3_recovery

    print(f"\n  P3: Hazard CV={hazard_cv:.3f} (<0.20?) = {'YES' if p3_hazard else 'NO'}")
    print(f"      Recovery CV={recovery_cv:.3f} (>0.50?) = {'YES' if p3_recovery else 'NO'}")
    print(f"  Verdict: {'PASS' if p3_pass else 'FAIL'}")

    # Additional: ratio
    if hazard_cv and recovery_cv:
        ratio = recovery_cv / hazard_cv
        print(f"  Recovery/Hazard CV ratio: {ratio:.2f}x")

    return {
        'n_folios_used': n,
        'hazard_cv': round(float(hazard_cv), 4) if hazard_cv is not None else None,
        'recovery_cv': round(float(recovery_cv), 4) if recovery_cv is not None else None,
        'initiator_cv': round(float(initiator_cv), 4) if initiator_cv is not None else None,
        'hazard_details': hazard_details,
        'recovery_details': recovery_details,
        'initiator_details': initiator_details,
        'recovery_hazard_ratio': round(float(recovery_cv / hazard_cv), 2) if (hazard_cv and recovery_cv) else None,
        'pass': p3_pass,
    }


# ── T4: Forgiveness Gradient Decomposition ───────────────────────────

def run_t4(folio_matrices, forgiveness_data):
    """Which macro-state transitions drive the forgiving/brittle axis?"""
    print("\n" + "=" * 60)
    print("T4: Forgiveness Gradient Decomposition")
    print("=" * 60)

    # Only use folios with both sufficient transitions and forgiveness data
    common_folios = sorted(
        f for f in folio_matrices
        if folio_matrices[f]['n_transitions'] >= MIN_TRANSITIONS and f in forgiveness_data
    )
    n = len(common_folios)
    print(f"\n  Folios with both transition data and forgiveness: {n}")

    # Extract forgiveness scores
    forgiveness_scores = np.array([forgiveness_data[f]['forgiveness'] for f in common_folios])
    hazard_densities = np.array([forgiveness_data[f]['hazard_density'] for f in common_folios])
    escape_densities = np.array([forgiveness_data[f]['escape_density'] for f in common_folios])

    print(f"  Forgiveness range: [{forgiveness_scores.min():.3f}, {forgiveness_scores.max():.3f}]")
    print(f"  Mean forgiveness: {forgiveness_scores.mean():.3f}")

    # Extract transition features
    feature_names = []
    feature_matrix = []

    for f in common_folios:
        d = folio_matrices[f]
        tp = d['trans_prob']
        sd = d['state_dist']
        row = []

        # Key transition probabilities
        for i, si in enumerate(STATE_ORDER):
            for j, sj in enumerate(STATE_ORDER):
                # Only include transitions with enough signal (mean > 0.005 across corpus)
                row.append(tp[i, j])
                if len(feature_matrix) == 0:
                    feature_names.append(f"{si}->{sj}")

        # State occupancies
        for i, s in enumerate(STATE_ORDER):
            row.append(sd[i])
            if len(feature_matrix) == 0:
                feature_names.append(f"occ_{s}")

        feature_matrix.append(row)

    X = np.array(feature_matrix)
    print(f"  Feature matrix: {X.shape} ({len(feature_names)} features)")

    # Spearman correlations for each feature vs forgiveness
    correlations = []
    for j in range(X.shape[1]):
        col = X[:, j]
        if col.std() < 1e-10:
            continue
        rho, p = stats.spearmanr(col, forgiveness_scores)
        correlations.append({
            'feature': feature_names[j],
            'rho': round(float(rho), 4),
            'p_value': round(float(p), 6),
            'abs_rho': abs(rho),
        })

    # Sort by absolute correlation
    correlations.sort(key=lambda x: x['abs_rho'], reverse=True)

    # Bonferroni correction
    n_tests = len(correlations)
    bonferroni_threshold = 0.01 / n_tests
    n_significant = sum(1 for c in correlations if c['p_value'] < bonferroni_threshold)

    print(f"\n  Top 10 correlations with forgiveness (Bonferroni threshold: {bonferroni_threshold:.6f}):")
    for c in correlations[:10]:
        sig = "***" if c['p_value'] < bonferroni_threshold else ""
        print(f"    {c['feature']:<15} rho={c['rho']:>7.4f}  p={c['p_value']:.6f} {sig}")

    # Also correlate with component scores
    print(f"\n  Component-level correlations:")
    for label, scores in [('hazard_density', hazard_densities), ('escape_density', escape_densities)]:
        for j in range(min(X.shape[1], len(feature_names))):
            col = X[:, j]
            if col.std() < 1e-10:
                continue
            rho, p = stats.spearmanr(col, scores)
            if abs(rho) > 0.3 and p < 0.01:
                print(f"    {label} ~ {feature_names[j]}: rho={rho:.4f}, p={p:.6f}")

    # P4: >=1 significant after Bonferroni at p<0.01
    p4_pass = n_significant >= 1
    print(f"\n  P4: {n_significant} features significant after Bonferroni correction (threshold: 1)")
    print(f"  Verdict: {'PASS' if p4_pass else 'FAIL'}")

    return {
        'n_folios_used': n,
        'n_features': len(feature_names),
        'bonferroni_threshold': round(bonferroni_threshold, 8),
        'n_significant': n_significant,
        'top_correlations': correlations[:15],
        'pass': p4_pass,
    }


# ── T5: Restart Folio Signature ──────────────────────────────────────

def run_t5(folio_matrices, regime_map):
    """Profile restart folios against REGIME-matched controls."""
    print("\n" + "=" * 60)
    print("T5: Restart Folio Signature (f50v, f57r, f82v)")
    print("=" * 60)

    # Build REGIME groups for comparison
    regime_groups = defaultdict(list)
    for f, d in folio_matrices.items():
        r = regime_map.get(f, 'UNKNOWN')
        regime_groups[r].append(f)

    results = {}
    any_elevated = False

    for restart_f in sorted(RESTART_FOLIOS):
        if restart_f not in folio_matrices:
            print(f"\n  {restart_f}: NOT FOUND in data")
            continue

        d = folio_matrices[restart_f]
        regime = regime_map.get(restart_f, 'UNKNOWN')
        print(f"\n  {restart_f} (N={d['n_tokens']} tokens, {d['n_transitions']} transitions, {regime}):")

        # State distribution
        sd = d['state_dist']
        print(f"    State distribution:")
        for i, s in enumerate(STATE_ORDER):
            print(f"      {s}: {sd[i]:.4f}")

        # Compare to REGIME-matched controls
        controls = [f for f in regime_groups[regime] if f != restart_f and f not in RESTART_FOLIOS]
        if not controls:
            print(f"    No REGIME-matched controls available")
            results[restart_f] = {
                'regime': regime, 'n_tokens': d['n_tokens'],
                'n_transitions': d['n_transitions'],
                'state_dist': {s: round(float(sd[i]), 4) for i, s in enumerate(STATE_ORDER)},
                'z_scores': None,
            }
            continue

        # Compute z-scores against controls
        control_dists = np.array([folio_matrices[f]['state_dist'] for f in controls])
        control_mean = control_dists.mean(axis=0)
        control_std = control_dists.std(axis=0)

        z_scores = {}
        print(f"    Z-scores vs {len(controls)} REGIME-matched controls:")
        for i, s in enumerate(STATE_ORDER):
            if control_std[i] > 1e-6:
                z = (sd[i] - control_mean[i]) / control_std[i]
            else:
                z = 0.0
            z_scores[s] = round(float(z), 2)
            marker = " <<<" if abs(z) > 2.0 else ""
            print(f"      {s}: z={z:>6.2f} (folio={sd[i]:.4f}, ctrl_mean={control_mean[i]:.4f}){marker}")

        # Check P5 condition for f57r specifically
        if restart_f == 'f57r':
            fl_haz_z = z_scores.get('FL_HAZ', 0)
            fl_safe_z = z_scores.get('FL_SAFE', 0)
            if fl_haz_z > 1.5 or fl_safe_z < -1.5:
                any_elevated = True
                print(f"    ** f57r shows {'elevated FL_HAZ' if fl_haz_z > 1.5 else 'depressed FL_SAFE'}")

        results[restart_f] = {
            'regime': regime,
            'n_tokens': d['n_tokens'],
            'n_transitions': d['n_transitions'],
            'state_dist': {s: round(float(sd[i]), 4) for i, s in enumerate(STATE_ORDER)},
            'z_scores': z_scores,
        }

    # P5: f57r elevated FL_HAZ or depressed FL_SAFE
    # Also check: ANY restart folio with |z| > 2 for any state
    any_extreme = False
    for rf, rd in results.items():
        if rd.get('z_scores'):
            for s, z in rd['z_scores'].items():
                if abs(z) > 2.0:
                    any_extreme = True

    p5_pass = any_elevated or any_extreme
    print(f"\n  P5: f57r FL_HAZ elevated or FL_SAFE depressed = {'YES' if any_elevated else 'NO'}")
    print(f"      Any restart folio with |z|>2.0 = {'YES' if any_extreme else 'NO'}")
    print(f"  Verdict: {'PASS' if p5_pass else 'FAIL'}")

    return {
        'restart_profiles': results,
        'any_elevated_f57r': any_elevated,
        'any_extreme_z': any_extreme,
        'pass': p5_pass,
    }


# ── T6: Variance Decomposition (ANOVA) ──────────────────────────────

def run_t6(folio_matrices, regime_map, section_map):
    """Decompose folio-level transition variance into REGIME, section, residual."""
    print("\n" + "=" * 60)
    print("T6: Variance Decomposition (REGIME + Section ANOVA)")
    print("=" * 60)

    sufficient = {f: d for f, d in folio_matrices.items() if d['n_transitions'] >= MIN_TRANSITIONS}
    folios = sorted(sufficient.keys())
    n = len(folios)

    # Get REGIME and section labels
    regimes = [regime_map.get(f, 'UNKNOWN') for f in folios]
    sections = [section_map.get(f, 'UNKNOWN') for f in folios]

    unique_regimes = sorted(set(regimes))
    unique_sections = sorted(set(sections))
    print(f"\n  Folios: {n}")
    print(f"  REGIMEs: {unique_regimes} ({Counter(regimes)})")
    print(f"  Sections: {unique_sections} ({Counter(sections)})")

    # Key transition features to decompose
    feature_names = [
        ('AXM_self', STATE_IDX['AXM'], STATE_IDX['AXM']),
        ('AXM_to_FQ', STATE_IDX['AXM'], STATE_IDX['FQ']),
        ('FQ_to_AXM', STATE_IDX['FQ'], STATE_IDX['AXM']),
        ('AXM_to_FL_HAZ', STATE_IDX['AXM'], STATE_IDX['FL_HAZ']),
        ('FL_HAZ_self', STATE_IDX['FL_HAZ'], STATE_IDX['FL_HAZ']),
        ('AXM_to_CC', STATE_IDX['AXM'], STATE_IDX['CC']),
        ('CC_to_AXM', STATE_IDX['CC'], STATE_IDX['AXM']),
        ('FQ_self', STATE_IDX['FQ'], STATE_IDX['FQ']),
    ]

    # Also include state occupancies
    occ_features = [
        ('occ_AXM', STATE_IDX['AXM']),
        ('occ_FL_HAZ', STATE_IDX['FL_HAZ']),
        ('occ_FQ', STATE_IDX['FQ']),
        ('occ_CC', STATE_IDX['CC']),
    ]

    # Manual eta-squared: SS_between / SS_total for each factor
    def eta_squared_one_way(values, groups):
        """Compute eta-squared for one-way grouping."""
        grand_mean = np.mean(values)
        ss_total = np.sum((values - grand_mean) ** 2)
        if ss_total < 1e-15:
            return 0.0

        group_labels = sorted(set(groups))
        ss_between = 0
        for g in group_labels:
            mask = [i for i, gl in enumerate(groups) if gl == g]
            if mask:
                group_mean = np.mean([values[i] for i in mask])
                ss_between += len(mask) * (group_mean - grand_mean) ** 2

        return ss_between / ss_total

    print(f"\n  {'Feature':<18} {'eta2_REGIME':>12} {'eta2_SECTION':>12} {'eta2_combined':>14} {'residual':>10}")
    print(f"  {'-'*18} {'-'*12} {'-'*12} {'-'*14} {'-'*10}")

    eta_results = []

    # Transition features
    for name, r, c in feature_names:
        values = np.array([sufficient[f]['trans_prob'][r, c] for f in folios])
        eta_regime = eta_squared_one_way(values, regimes)
        eta_section = eta_squared_one_way(values, sections)

        # Combined: group by (REGIME, section) pairs
        combined_labels = [f"{regimes[i]}_{sections[i]}" for i in range(n)]
        eta_combined = eta_squared_one_way(values, combined_labels)
        residual = 1 - eta_combined

        print(f"  {name:<18} {eta_regime:>12.3f} {eta_section:>12.3f} {eta_combined:>14.3f} {residual:>10.3f}")
        eta_results.append({
            'feature': name, 'type': 'transition',
            'eta2_regime': round(float(eta_regime), 4),
            'eta2_section': round(float(eta_section), 4),
            'eta2_combined': round(float(eta_combined), 4),
            'residual': round(float(residual), 4),
        })

    # Occupancy features
    for name, idx in occ_features:
        values = np.array([sufficient[f]['state_dist'][idx] for f in folios])
        eta_regime = eta_squared_one_way(values, regimes)
        eta_section = eta_squared_one_way(values, sections)
        combined_labels = [f"{regimes[i]}_{sections[i]}" for i in range(n)]
        eta_combined = eta_squared_one_way(values, combined_labels)
        residual = 1 - eta_combined

        print(f"  {name:<18} {eta_regime:>12.3f} {eta_section:>12.3f} {eta_combined:>14.3f} {residual:>10.3f}")
        eta_results.append({
            'feature': name, 'type': 'occupancy',
            'eta2_regime': round(float(eta_regime), 4),
            'eta2_section': round(float(eta_section), 4),
            'eta2_combined': round(float(eta_combined), 4),
            'residual': round(float(residual), 4),
        })

    # Aggregate statistics
    all_eta_combined = [r['eta2_combined'] for r in eta_results]
    all_residuals = [r['residual'] for r in eta_results]
    mean_eta_combined = np.mean(all_eta_combined)
    mean_residual = np.mean(all_residuals)

    mean_eta_regime = np.mean([r['eta2_regime'] for r in eta_results])
    mean_eta_section = np.mean([r['eta2_section'] for r in eta_results])

    print(f"\n  Aggregate:")
    print(f"    Mean eta2(REGIME):         {mean_eta_regime:.3f}")
    print(f"    Mean eta2(section):        {mean_eta_section:.3f}")
    print(f"    Mean eta2(REGIME+section): {mean_eta_combined:.3f}")
    print(f"    Mean residual:             {mean_residual:.3f}")

    # P6: REGIME+section explains <70%
    p6_pass = mean_eta_combined < 0.70
    print(f"\n  P6: Mean combined eta2 = {mean_eta_combined:.3f} (<0.70?)")
    print(f"  Verdict: {'PASS' if p6_pass else 'FAIL'}")

    return {
        'n_folios_used': n,
        'n_regimes': len(unique_regimes),
        'n_sections': len(unique_sections),
        'features': eta_results,
        'mean_eta2_regime': round(float(mean_eta_regime), 4),
        'mean_eta2_section': round(float(mean_eta_section), 4),
        'mean_eta2_combined': round(float(mean_eta_combined), 4),
        'mean_residual': round(float(mean_residual), 4),
        'pass': p6_pass,
    }


# ── T7: Geometry/Topology Independence ───────────────────────────────

def run_t7(folio_matrices, folio_line_states, t2_archetypes):
    """Test whether dynamical archetypes are predictable from discrimination
    manifold coordinates alone, or require execution topology.

    Approach: build per-folio centroids in the MIDDLE discrimination manifold
    (100D spectral embedding from Currier A co-occurrence), cluster them, and
    compare to the dynamical archetypes from T2.

    If ARI(manifold clusters, archetypes) is low, archetypes require execution
    topology and are not reducible to vocabulary geometry.
    """
    print("\n" + "=" * 60)
    print("T7: Geometry/Topology Independence (Manifold vs Archetypes)")
    print("=" * 60)

    from sklearn.metrics import adjusted_rand_score

    # Load the compatibility matrix and rebuild MIDDLE ordering
    compat_path = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    if not compat_path.exists():
        print("  ERROR: Compatibility matrix not found. Skipping T7.")
        return {'pass': False, 'error': 'compat_matrix_not_found'}

    M = np.load(compat_path)
    print(f"  Loaded compatibility matrix: {M.shape}")

    # Rebuild MIDDLE ordering (same sorted order as t1_definitive_matrix.py)
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    print(f"  Currier A MIDDLEs in manifold: {len(all_middles)}")

    # Build spectral embedding (100D, matching DISCRIMINATION_SPACE_DERIVATION)
    K_EMBED = 100
    eigenvalues, eigenvectors = np.linalg.eigh(M.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    evals = eigenvalues[:K_EMBED]
    evecs = eigenvectors[:, :K_EMBED]
    pos_evals = np.maximum(evals, 0)
    scaling = np.sqrt(pos_evals)
    embedding = evecs * scaling[np.newaxis, :]
    print(f"  Embedding: {embedding.shape} ({K_EMBED}D)")

    # Compute per-B-folio centroids in the manifold
    # For each folio, find the MIDDLEs used and average their embedding coords
    sufficient_folios = sorted(f for f in folio_matrices if folio_matrices[f]['n_transitions'] >= MIN_TRANSITIONS)

    folio_centroids = {}
    folio_coverage = {}
    for folio in sufficient_folios:
        # Collect unique MIDDLEs used in this folio
        folio_middles = set()
        for (_, _), states_list in folio_line_states.get(folio, {}).items():
            pass  # states_list is already mapped to states, need raw words

        # Re-extract MIDDLEs from raw tokens
        folio_mids_in_manifold = set()
        for token in tx.currier_b():
            if token.folio != folio:
                continue
            word = token.word.strip()
            if not word or '*' in word:
                continue
            m = morph.extract(word)
            if m.middle and m.middle in mid_to_idx:
                folio_mids_in_manifold.add(m.middle)

        if not folio_mids_in_manifold:
            continue

        indices = [mid_to_idx[m] for m in folio_mids_in_manifold]
        centroid = embedding[indices].mean(axis=0)
        folio_centroids[folio] = centroid
        folio_coverage[folio] = len(folio_mids_in_manifold)

    print(f"  Folios with manifold centroids: {len(folio_centroids)}")
    coverages = list(folio_coverage.values())
    print(f"  MIDDLEs per folio in manifold: mean={np.mean(coverages):.1f}, "
          f"min={min(coverages)}, max={max(coverages)}")

    # Align: only folios in both T2 archetypes AND manifold centroids
    # T2 archetypes are keyed by folio with cluster label
    t2_folios = t2_archetypes.get('folio_labels', {})
    common = sorted(f for f in folio_centroids if f in t2_folios)
    print(f"  Folios in both manifold and T2 archetypes: {len(common)}")

    if len(common) < 20:
        print("  Too few common folios for meaningful comparison. FAIL.")
        return {'pass': False, 'n_common': len(common), 'error': 'insufficient_overlap'}

    # Build centroid matrix for common folios
    X_manifold = np.array([folio_centroids[f] for f in common])
    archetype_labels = np.array([t2_folios[f] for f in common])

    # Standardize manifold centroids
    X_std = (X_manifold - X_manifold.mean(axis=0)) / (X_manifold.std(axis=0) + 1e-10)

    # Cluster manifold centroids with same k as T2
    best_k = t2_archetypes['best_k']
    dist_matrix = pdist(X_std, metric='euclidean')
    Z = linkage(dist_matrix, method='ward')
    manifold_labels = fcluster(Z, t=best_k, criterion='maxclust')

    # ARI between manifold clusters and dynamical archetypes
    ari_manifold_vs_archetype = adjusted_rand_score(archetype_labels, manifold_labels)
    print(f"\n  ARI(manifold clusters k={best_k}, dynamical archetypes): {ari_manifold_vs_archetype:.4f}")

    # Also: nearest-centroid classification accuracy
    # Train: use archetype centroids in manifold space, predict archetype from manifold
    archetype_ids = sorted(set(archetype_labels))
    correct = 0
    for i, f in enumerate(common):
        # Leave-one-out: compute archetype centroids excluding this point
        true_label = archetype_labels[i]
        min_dist = float('inf')
        pred_label = -1
        for aid in archetype_ids:
            mask = (archetype_labels == aid)
            mask[i] = False  # exclude self
            if mask.sum() == 0:
                continue
            centroid = X_manifold[mask].mean(axis=0)
            dist = np.linalg.norm(X_manifold[i] - centroid)
            if dist < min_dist:
                min_dist = dist
                pred_label = aid
        if pred_label == true_label:
            correct += 1
    loo_accuracy = correct / len(common)
    chance_accuracy = 1.0 / best_k
    print(f"  LOO nearest-centroid accuracy: {loo_accuracy:.3f} (chance: {chance_accuracy:.3f})")

    # Permutation test for ARI
    n_perm = 1000
    null_aris = []
    for _ in range(n_perm):
        perm_labels = np.random.permutation(archetype_labels)
        null_aris.append(adjusted_rand_score(perm_labels, manifold_labels))
    null_aris = np.array(null_aris)
    p_value = (null_aris >= ari_manifold_vs_archetype).mean()
    z_score = (ari_manifold_vs_archetype - null_aris.mean()) / (null_aris.std() + 1e-10)

    print(f"  ARI permutation test: z={z_score:.2f}, p={p_value:.4f}")
    print(f"  Null ARI: mean={null_aris.mean():.4f} +/- {null_aris.std():.4f}")

    # P7: ARI(manifold, archetypes) < 0.3 → archetypes NOT predictable from geometry
    # This would confirm geometry/topology independence
    p7_pass = ari_manifold_vs_archetype < 0.3
    print(f"\n  P7: ARI={ari_manifold_vs_archetype:.4f} (<0.3 → geometry doesn't predict archetypes?)")
    print(f"  Verdict: {'PASS (independent)' if p7_pass else 'FAIL (geometry predicts archetypes)'}")

    return {
        'n_folios_manifold': len(folio_centroids),
        'n_common': len(common),
        'mean_middles_per_folio': round(float(np.mean(coverages)), 1),
        'ari_manifold_vs_archetype': round(float(ari_manifold_vs_archetype), 4),
        'loo_accuracy': round(float(loo_accuracy), 4),
        'chance_accuracy': round(float(chance_accuracy), 4),
        'ari_z_score': round(float(z_score), 2),
        'ari_p_value': round(float(p_value), 4),
        'best_k': best_k,
        'pass': p7_pass,
    }


# ── T8: Bridge Conduit Test ───────────────────────────────────────────

def run_t8(folio_matrices, t2_archetypes):
    """Test whether bridge MIDDLE density is a better predictor of dynamical
    archetypes than full manifold position.

    If bridge features predict archetypes better than full manifold centroids
    (T7), the bridge backbone (C1013-C1014) is the geometry→dynamics conduit.
    """
    print("\n" + "=" * 60)
    print("T8: Bridge Conduit Test (Bridge vs Full Manifold)")
    print("=" * 60)

    from sklearn.metrics import adjusted_rand_score

    # Load bridge MIDDLEs
    bridge_path = Path(__file__).resolve().parents[2] / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    if not bridge_path.exists():
        print("  ERROR: Bridge selection results not found. Skipping T8.")
        return {'pass': False, 'error': 'bridge_data_not_found'}

    with open(bridge_path) as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])
    print(f"  Bridge MIDDLEs: {len(bridge_set)}")

    # Load compatibility matrix and build embedding (same as T7)
    compat_path = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    M = np.load(compat_path)

    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}

    K_EMBED = 100
    eigenvalues, eigenvectors = np.linalg.eigh(M.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    evals = eigenvalues[:K_EMBED]
    evecs = eigenvectors[:, :K_EMBED]
    pos_evals = np.maximum(evals, 0)
    scaling = np.sqrt(pos_evals)
    embedding = evecs * scaling[np.newaxis, :]

    # Get archetype labels
    t2_folios = t2_archetypes.get('folio_labels', {})
    sufficient_folios = sorted(f for f in folio_matrices if folio_matrices[f]['n_transitions'] >= MIN_TRANSITIONS)

    # Per-folio: compute bridge features and non-bridge features
    folio_features = {}
    for folio in sufficient_folios:
        if folio not in t2_folios:
            continue

        # Extract MIDDLEs used in this folio
        folio_mids = set()
        folio_bridge_mids = set()
        folio_nonbridge_mids = set()

        for token in tx.currier_b():
            if token.folio != folio:
                continue
            word = token.word.strip()
            if not word or '*' in word:
                continue
            m = morph.extract(word)
            if m.middle and m.middle in mid_to_idx:
                folio_mids.add(m.middle)
                if m.middle in bridge_set:
                    folio_bridge_mids.add(m.middle)
                else:
                    folio_nonbridge_mids.add(m.middle)

        if not folio_mids:
            continue

        # Bridge density (fraction of manifold MIDDLEs that are bridges)
        bridge_density = len(folio_bridge_mids) / len(folio_mids) if folio_mids else 0

        # Bridge centroid in manifold
        bridge_indices = [mid_to_idx[m] for m in folio_bridge_mids] if folio_bridge_mids else []
        bridge_centroid = embedding[bridge_indices].mean(axis=0) if bridge_indices else np.zeros(K_EMBED)

        # Non-bridge centroid
        nonbridge_indices = [mid_to_idx[m] for m in folio_nonbridge_mids] if folio_nonbridge_mids else []
        nonbridge_centroid = embedding[nonbridge_indices].mean(axis=0) if nonbridge_indices else np.zeros(K_EMBED)

        # Full centroid
        all_indices = [mid_to_idx[m] for m in folio_mids]
        full_centroid = embedding[all_indices].mean(axis=0)

        folio_features[folio] = {
            'bridge_density': bridge_density,
            'n_bridge': len(folio_bridge_mids),
            'n_nonbridge': len(folio_nonbridge_mids),
            'bridge_centroid': bridge_centroid,
            'nonbridge_centroid': nonbridge_centroid,
            'full_centroid': full_centroid,
        }

    common = sorted(f for f in folio_features if f in t2_folios)
    print(f"  Common folios: {len(common)}")

    archetype_labels = np.array([t2_folios[f] for f in common])
    best_k = t2_archetypes['best_k']

    # Compare three feature sets for archetype prediction
    def ari_and_loo(X, labels, k, label):
        """Compute ARI and LOO accuracy for a feature set."""
        X_std = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-10)
        dist_mat = pdist(X_std, metric='euclidean')
        Z = linkage(dist_mat, method='ward')
        cluster_labels = fcluster(Z, t=k, criterion='maxclust')
        ari = adjusted_rand_score(labels, cluster_labels)

        # LOO
        archetype_ids = sorted(set(labels))
        correct = 0
        for i in range(len(common)):
            true_label = labels[i]
            min_dist = float('inf')
            pred_label = -1
            for aid in archetype_ids:
                mask = (labels == aid)
                mask[i] = False
                if mask.sum() == 0:
                    continue
                centroid = X[mask].mean(axis=0)
                dist = np.linalg.norm(X[i] - centroid)
                if dist < min_dist:
                    min_dist = dist
                    pred_label = aid
            if pred_label == true_label:
                correct += 1
        loo = correct / len(common)

        print(f"    {label}: ARI={ari:.4f}, LOO={loo:.3f}")
        return ari, loo

    # 1. Full manifold centroids (replicate T7)
    X_full = np.array([folio_features[f]['full_centroid'] for f in common])
    ari_full, loo_full = ari_and_loo(X_full, archetype_labels, best_k, "Full manifold")

    # 2. Bridge centroids only
    X_bridge = np.array([folio_features[f]['bridge_centroid'] for f in common])
    ari_bridge, loo_bridge = ari_and_loo(X_bridge, archetype_labels, best_k, "Bridge-only")

    # 3. Non-bridge centroids only
    X_nonbridge = np.array([folio_features[f]['nonbridge_centroid'] for f in common])
    ari_nonbridge, loo_nonbridge = ari_and_loo(X_nonbridge, archetype_labels, best_k, "Non-bridge-only")

    # 4. Bridge density as scalar feature (+ bridge centroid)
    bridge_densities = np.array([folio_features[f]['bridge_density'] for f in common])
    X_bridge_augmented = np.column_stack([X_bridge, bridge_densities])
    ari_bridge_aug, loo_bridge_aug = ari_and_loo(X_bridge_augmented, archetype_labels, best_k, "Bridge + density")

    # Summary
    print(f"\n  Comparison:")
    print(f"    Full manifold:   ARI={ari_full:.4f}, LOO={loo_full:.3f}")
    print(f"    Bridge-only:     ARI={ari_bridge:.4f}, LOO={loo_bridge:.3f}")
    print(f"    Non-bridge-only: ARI={ari_nonbridge:.4f}, LOO={loo_nonbridge:.3f}")
    print(f"    Bridge+density:  ARI={ari_bridge_aug:.4f}, LOO={loo_bridge_aug:.3f}")

    # Bridge advantage = bridge ARI > full ARI
    bridge_advantage = ari_bridge > ari_full
    bridge_loo_advantage = loo_bridge > loo_full
    print(f"\n  Bridge ARI advantage over full: {bridge_advantage} ({ari_bridge:.4f} vs {ari_full:.4f})")
    print(f"  Bridge LOO advantage over full: {bridge_loo_advantage} ({loo_bridge:.3f} vs {loo_full:.3f})")

    # Bridge vs non-bridge comparison
    bridge_vs_nonbridge = ari_bridge > ari_nonbridge
    print(f"  Bridge vs non-bridge: {bridge_vs_nonbridge} ({ari_bridge:.4f} vs {ari_nonbridge:.4f})")

    # Spearman: bridge density vs archetype-feature correlations
    # Bridge density vs AXM self-transition (the archetype axis)
    axm_self = np.array([folio_matrices[f]['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']]
                         for f in common])
    rho_bridge_axm, p_bridge_axm = stats.spearmanr(bridge_densities, axm_self)
    print(f"\n  Bridge density vs AXM self-transition: rho={rho_bridge_axm:.4f}, p={p_bridge_axm:.6f}")

    mean_bridge_density = float(bridge_densities.mean())
    print(f"  Mean bridge density: {mean_bridge_density:.3f}")

    # P8: Bridge features predict archetypes better than non-bridge
    # (i.e., bridge is the geometry→dynamics conduit)
    p8_pass = ari_bridge > ari_nonbridge or loo_bridge > loo_nonbridge
    print(f"\n  P8: Bridge > non-bridge in ARI or LOO?")
    print(f"  Verdict: {'PASS (bridge is conduit)' if p8_pass else 'FAIL (no bridge advantage)'}")

    return {
        'n_common': len(common),
        'n_bridge_middles': len(bridge_set),
        'mean_bridge_density': round(mean_bridge_density, 3),
        'ari_full': round(float(ari_full), 4),
        'ari_bridge': round(float(ari_bridge), 4),
        'ari_nonbridge': round(float(ari_nonbridge), 4),
        'ari_bridge_augmented': round(float(ari_bridge_aug), 4),
        'loo_full': round(float(loo_full), 4),
        'loo_bridge': round(float(loo_bridge), 4),
        'loo_nonbridge': round(float(loo_nonbridge), 4),
        'loo_bridge_augmented': round(float(loo_bridge_aug), 4),
        'bridge_advantage_ari': bridge_advantage,
        'bridge_advantage_loo': bridge_loo_advantage,
        'bridge_vs_nonbridge': bridge_vs_nonbridge,
        'rho_bridge_density_axm_self': round(float(rho_bridge_axm), 4),
        'p_bridge_density_axm_self': round(float(p_bridge_axm), 6),
        'pass': p8_pass,
    }


# ── T9: Synthesis ────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5, t6, t7, t8):
    """Combine all test results into a verdict."""
    print("\n" + "=" * 60)
    print("T9: SYNTHESIS")
    print("=" * 60)

    predictions = {
        'P1_folio_census': {
            'description': '>=70 folios with N>=50 transitions',
            'value': t1['n_sufficient'],
            'pass': t1['pass'],
        },
        'P2_archetype_discovery': {
            'description': 'Optimal k>4 OR ARI(REGIME)<0.5',
            'value': f"k={t2['best_k']}, ARI={t2['ari_regime']}",
            'pass': t2['pass'],
        },
        'P3_c458_realization': {
            'description': 'Hazard CV<0.20, recovery CV>0.50',
            'value': f"haz_cv={t3['hazard_cv']}, rec_cv={t3['recovery_cv']}",
            'pass': t3['pass'],
        },
        'P4_forgiveness_decomposition': {
            'description': '>=1 transition predicts forgiveness (Bonferroni p<0.01)',
            'value': t4['n_significant'],
            'pass': t4['pass'],
        },
        'P5_restart_signature': {
            'description': 'f57r elevated FL_HAZ or depressed FL_SAFE vs controls',
            'value': f"f57r_elevated={t5['any_elevated_f57r']}, any_extreme={t5['any_extreme_z']}",
            'pass': t5['pass'],
        },
        'P6_variance_decomposition': {
            'description': 'REGIME+section explains <70% transition variance',
            'value': t6['mean_eta2_combined'],
            'pass': t6['pass'],
        },
        'P7_geometry_topology_independence': {
            'description': 'ARI(manifold clusters, archetypes) < 0.3',
            'value': t7.get('ari_manifold_vs_archetype', 'N/A'),
            'pass': t7.get('pass', False),
        },
        'P8_bridge_conduit': {
            'description': 'Bridge features predict archetypes better than non-bridge',
            'value': f"ARI bridge={t8.get('ari_bridge', 'N/A')} vs non-bridge={t8.get('ari_nonbridge', 'N/A')}",
            'pass': t8.get('pass', False),
        },
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])
    n_total = len(predictions)

    # Verdict
    if n_pass >= 6:
        verdict = 'FOLIO_DECOMPOSITION_CONFIRMED'
    elif n_pass >= 4:
        verdict = 'FOLIO_DECOMPOSITION_SUPPORTED'
    else:
        verdict = 'FOLIO_DECOMPOSITION_INSUFFICIENT'

    for name, pred in predictions.items():
        status = 'PASS' if pred['pass'] else 'FAIL'
        print(f"  {name}: {status} (value={pred['value']})")

    print(f"\n  Overall: {n_pass}/{n_total} PASS")
    print(f"  Verdict: {verdict}")

    return {
        'predictions': {k: {'description': v['description'], 'value': str(v['value']),
                            'pass': v['pass']} for k, v in predictions.items()},
        'n_pass': n_pass,
        'n_total': n_total,
        'verdict': verdict,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    start = time.time()

    print("Phase 339: FOLIO_MACRO_AUTOMATON_DECOMPOSITION")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    regime_map = load_regime_assignments()

    print("Building per-folio token sequences...")
    folio_line_states, section_map, folio_tokens = build_folio_data(token_to_class)

    print("Computing per-folio transition matrices...")
    folio_matrices = compute_folio_matrices(folio_line_states)

    print("Computing forgiveness metrics...")
    forgiveness_data = compute_forgiveness(folio_tokens)

    # Run tests
    t1 = run_t1(folio_matrices)
    t2 = run_t2(folio_matrices, regime_map, section_map)
    t3 = run_t3(folio_matrices)
    t4 = run_t4(folio_matrices, forgiveness_data)
    t5 = run_t5(folio_matrices, regime_map)
    t6 = run_t6(folio_matrices, regime_map, section_map)
    t7 = run_t7(folio_matrices, folio_line_states, t2)
    t8 = run_t8(folio_matrices, t2)
    t9 = synthesize(t1, t2, t3, t4, t5, t6, t7, t8)

    # Save results
    results = {
        't1_folio_census': t1,
        't2_archetype_discovery': t2,
        't3_c458_realization': t3,
        't4_forgiveness_decomposition': t4,
        't5_restart_signature': t5,
        't6_variance_decomposition': t6,
        't7_geometry_topology_independence': t7,
        't8_bridge_conduit': t8,
        't9_synthesis': t9,
    }

    output_path = Path(__file__).resolve().parents[1] / 'results' / 'folio_macro_decomposition.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - start
    print(f"\nResults saved to {output_path}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
