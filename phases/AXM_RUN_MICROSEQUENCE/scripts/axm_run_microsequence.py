#!/usr/bin/env python3
"""
AXM_RUN_MICROSEQUENCE -- Phase 360
====================================
Tests whether micro-sequential dynamics within AXM runs — the temporal
ordering of class-level tokens — can decompose C1035's 57% irreducible
AXM self-transition residual.

Three consecutive phases eliminated composition-level strata:
  C1035 (357): aggregate folio statistics — no signal
  C1036 (358): AXM boundary transitions — frequency-neutral
  C1037 (359): within-AXM class composition — redundant

This phase tests the LAST candidate stratum: sequential dynamics.
C1024 shows MIDDLE carries 0.070 bits of execution asymmetry.
C969 shows CMI = 0.012 bits corpus-wide. Neither decomposed per-folio.

Three measures:
  M1: Conditional transition entropy gradients inside AXM runs
  M2: Per-folio MIDDLE asymmetry (forward/reverse JSD decomposition)
  M3: Per-folio conditional mutual information (CMI) decomposition

Pre-registered hypotheses:
  P1: Entropy gradient slope predicts residual (LOO incr R2 > 0.02)
  P2: MIDDLE asymmetry features predict residual (LOO incr R2 > 0.02)
  P3: Per-folio CMI variance exceeds permutation null (p < 0.01)
  P4: Combined micro-sequential features predict residual (LOO incr R2 > 0.02)
  P5: Entropy gradient curvature differs by archetype (ANOVA p < 0.01)
  P6: MIDDLE asymmetry CV > class-composition CV (sequence > composition)

Global decision rule: If P1, P2, P4 all LOO incr R2 < 0.01,
  micro-sequential stratum is empty → residual confirmed irreducible.

Pipeline: S1-S10
  S1: Extract AXM class-level runs per folio
  S2: M1: Conditional transition entropy gradients
  S3: M2: Per-folio MIDDLE asymmetry (JSD decomposition)
  S4: M3: Per-folio CMI decomposition + permutation test
  S5: Residual prediction: entropy gradient features
  S6: Residual prediction: MIDDLE asymmetry features
  S7: Residual prediction: CMI
  S8: Combined prediction
  S9: Archetype stratification
  S10: Evaluate P1-P6

Depends on: C1035, C1036, C1037, C1024, C969, C1010, C458, C980
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# -- Constants --

AXM_CLASSES_SET = {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,
                   31,32,33,34,35,36,37,39,41,43,44,46,47,48,49}
AXM_CLASS_ORDER = sorted(AXM_CLASSES_SET)  # 32 classes
N_AXM = len(AXM_CLASS_ORDER)
AXM_IDX = {c: i for i, c in enumerate(AXM_CLASS_ORDER)}

MACRO_STATE_PARTITION = {
    'AXM': AXM_CLASSES_SET,
    'AXm': {3, 5, 18, 19, 42, 45},
    'FL_HAZ': {7, 30},
    'FQ': {9, 13, 14, 23},
    'CC': {10, 11, 12},
    'FL_SAFE': {38, 40},
}

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

MIN_AXM_TRANSITIONS = 30  # Min within-AXM-run transitions per folio
MAX_POSITION = 6           # Cap entropy gradient position depth
MIN_POS_COUNT = 5          # Min transitions at a position depth for entropy
MIN_CLASS_COUNT = 5        # Min transitions from a class for JSD
N_PERMUTATIONS = 200       # CMI variance permutation null


# -- Data Loading --

def load_token_to_class():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        return json.load(f)['token_to_class']


def load_c1035_data():
    path = PROJECT_ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
    with open(path) as f:
        return json.load(f)['folio_data']


def load_regime_assignments():
    path = PROJECT_ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    path = PROJECT_ROOT / 'phases' / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)
    return {k: int(v) for k, v in data['t2_archetype_discovery']['folio_labels'].items()}


# -- S1: Extract AXM Runs --

def extract_axm_runs(token_to_class):
    """Extract per-folio AXM class-level runs from Currier B tokens.

    An AXM run is a maximal consecutive sequence of AXM-state tokens
    within a line. Each run records the class sequence.

    Returns:
        folio_runs: {folio: [run_classes_list, ...]}
        folio_sections: {folio: section}
        folio_bigram_counts: {folio: int}  # total within-run bigrams
    """
    tx = Transcript()

    # Build line-organized class sequences
    lines = defaultdict(list)  # (folio, line) -> [class_int, ...]
    folio_sections = {}

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        folio_sections[token.folio] = token.section

        cls = token_to_class.get(w)
        if cls is None:
            continue
        cls = int(cls)

        lines[(token.folio, token.line)].append(cls)

    # Extract AXM runs from each line
    folio_runs = defaultdict(list)
    folio_bigram_counts = defaultdict(int)

    for (folio, line_id), class_seq in lines.items():
        i = 0
        while i < len(class_seq):
            if class_seq[i] in AXM_CLASSES_SET:
                run_start = i
                run_classes = []
                while i < len(class_seq) and class_seq[i] in AXM_CLASSES_SET:
                    run_classes.append(class_seq[i])
                    i += 1
                if len(run_classes) >= 2:  # Need at least 1 bigram
                    folio_runs[folio].append(run_classes)
                    folio_bigram_counts[folio] += len(run_classes) - 1
            else:
                i += 1

    return dict(folio_runs), folio_sections, dict(folio_bigram_counts)


# -- S2: Conditional Transition Entropy Gradients --

def compute_entropy_gradient(runs, max_pos=MAX_POSITION, min_count=MIN_POS_COUNT):
    """Compute position-indexed conditional entropy within AXM runs.

    For each position depth t (1, 2, ...), pool all transitions at that
    depth across all runs. Compute H(class_t | class_{t-1}) at each depth.

    Returns:
        positions: list of position indices with valid data
        entropies: list of conditional entropies at each position
        slope: linear slope of H vs position (positive = divergent)
        curvature: quadratic coefficient (if enough positions)
        n_transitions_by_pos: list of transition counts per position
    """
    # Collect transitions by position depth
    # Position 1 = first transition in run (index 0→1)
    pos_transitions = defaultdict(list)  # pos -> [(from_cls, to_cls), ...]

    for run in runs:
        for t in range(1, len(run)):
            pos = t  # Position depth (1-indexed)
            if pos <= max_pos:
                pos_transitions[pos].append((run[t-1], run[t]))

    # Compute conditional entropy at each position
    positions = []
    entropies = []
    n_by_pos = []

    for pos in sorted(pos_transitions.keys()):
        transitions = pos_transitions[pos]
        if len(transitions) < min_count:
            continue

        # Compute H(class_t | class_{t-1}) from transition pairs
        # Group by source class
        source_groups = defaultdict(list)
        for src, tgt in transitions:
            source_groups[src].append(tgt)

        # Weighted conditional entropy
        n_total = len(transitions)
        h_cond = 0.0
        for src, targets in source_groups.items():
            p_src = len(targets) / n_total
            # Target distribution for this source
            tgt_counts = Counter(targets)
            tgt_probs = np.array(list(tgt_counts.values()), dtype=float)
            tgt_probs = tgt_probs / tgt_probs.sum()
            h_src = float(scipy_entropy(tgt_probs, base=2))
            h_cond += p_src * h_src

        positions.append(pos)
        entropies.append(h_cond)
        n_by_pos.append(n_total)

    # Fit linear slope
    slope = 0.0
    curvature = 0.0

    if len(positions) >= 2:
        pos_arr = np.array(positions, dtype=float)
        ent_arr = np.array(entropies, dtype=float)
        # Linear fit
        coeffs = np.polyfit(pos_arr, ent_arr, 1)
        slope = float(coeffs[0])

    if len(positions) >= 3:
        pos_arr = np.array(positions, dtype=float)
        ent_arr = np.array(entropies, dtype=float)
        # Quadratic fit
        coeffs2 = np.polyfit(pos_arr, ent_arr, 2)
        curvature = float(coeffs2[0])

    return positions, entropies, slope, curvature, n_by_pos


# -- S3: Per-Folio MIDDLE Asymmetry (JSD) --

def jsd(p, q):
    """Jensen-Shannon divergence between two distributions (bits, base 2)."""
    p = np.asarray(p, dtype=float) + 1e-12
    q = np.asarray(q, dtype=float) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * scipy_entropy(p, m, base=2) + 0.5 * scipy_entropy(q, m, base=2))


def compute_folio_jsd(runs, min_class=MIN_CLASS_COUNT):
    """Compute per-class JSD (forward vs reverse) from within-AXM-run bigrams.

    Build 32x32 forward and reverse transition matrices from AXM class
    bigrams within runs. Compute JSD per source class.

    Returns:
        jsd_mean: weighted mean JSD across classes
        jsd_var: variance of per-class JSD
        jsd_skew: skewness of per-class JSD distribution
        n_classes_computed: how many classes had enough data
        per_class_jsds: {class_id: jsd_value}
    """
    # Build forward transition matrix (32x32 using AXM_IDX)
    fwd = np.zeros((N_AXM, N_AXM))
    for run in runs:
        for i in range(len(run) - 1):
            src_idx = AXM_IDX.get(run[i])
            tgt_idx = AXM_IDX.get(run[i+1])
            if src_idx is not None and tgt_idx is not None:
                fwd[src_idx, tgt_idx] += 1

    # Build reverse transition matrix (reverse each run, then count)
    rev = np.zeros((N_AXM, N_AXM))
    for run in runs:
        rev_run = list(reversed(run))
        for i in range(len(rev_run) - 1):
            src_idx = AXM_IDX.get(rev_run[i])
            tgt_idx = AXM_IDX.get(rev_run[i+1])
            if src_idx is not None and tgt_idx is not None:
                rev[src_idx, tgt_idx] += 1

    # Per-class JSD
    row_counts = fwd.sum(axis=1)
    per_class_jsds = {}
    weights = []
    jsd_values = []

    for idx in range(N_AXM):
        if row_counts[idx] < min_class:
            continue
        cls = AXM_CLASS_ORDER[idx]
        j = jsd(fwd[idx], rev[idx])
        per_class_jsds[cls] = round(j, 6)
        jsd_values.append(j)
        weights.append(row_counts[idx])

    if not jsd_values:
        return 0.0, 0.0, 0.0, 0, {}

    jsd_arr = np.array(jsd_values)
    w_arr = np.array(weights)

    jsd_mean = float(np.average(jsd_arr, weights=w_arr))
    jsd_var = float(np.var(jsd_arr))

    # Skewness
    if len(jsd_arr) >= 3 and jsd_arr.std() > 0:
        jsd_skew = float(np.mean(((jsd_arr - jsd_arr.mean()) / jsd_arr.std()) ** 3))
    else:
        jsd_skew = 0.0

    return jsd_mean, jsd_var, jsd_skew, len(jsd_values), per_class_jsds


# -- S4: Per-Folio CMI --

def compute_folio_cmi(runs):
    """Compute conditional mutual information from within-AXM-run class trigrams.

    CMI = H(class_t | class_{t-1}) - H(class_t | class_{t-1}, class_{t-2})

    Uses empirical conditional entropies from bigram and trigram counts.

    Returns:
        cmi: float (bits)
        n_trigrams: int
        n_bigrams: int
    """
    # Collect bigrams and trigrams
    bigram_counts = Counter()  # (class_{t-1}, class_t)
    trigram_counts = Counter()  # (class_{t-2}, class_{t-1}, class_t)
    context_counts = Counter()  # class_{t-1} for bigrams
    bicontext_counts = Counter()  # (class_{t-2}, class_{t-1}) for trigrams

    for run in runs:
        for i in range(1, len(run)):
            bigram_counts[(run[i-1], run[i])] += 1
            context_counts[run[i-1]] += 1
        for i in range(2, len(run)):
            trigram_counts[(run[i-2], run[i-1], run[i])] += 1
            bicontext_counts[(run[i-2], run[i-1])] += 1

    n_bigrams = sum(bigram_counts.values())
    n_trigrams = sum(trigram_counts.values())

    if n_bigrams == 0 or n_trigrams == 0:
        return 0.0, n_trigrams, n_bigrams

    # H(class_t | class_{t-1}) from bigrams
    h_bigram = 0.0
    total_bi = sum(context_counts.values())
    for ctx, ctx_count in context_counts.items():
        p_ctx = ctx_count / total_bi
        # Conditional distribution P(class_t | class_{t-1} = ctx)
        targets = {k[1]: v for k, v in bigram_counts.items() if k[0] == ctx}
        total_tgt = sum(targets.values())
        if total_tgt == 0:
            continue
        probs = np.array(list(targets.values()), dtype=float) / total_tgt
        h_ctx = float(scipy_entropy(probs, base=2))
        h_bigram += p_ctx * h_ctx

    # H(class_t | class_{t-1}, class_{t-2}) from trigrams
    h_trigram = 0.0
    total_tri = sum(bicontext_counts.values())
    for bictx, bictx_count in bicontext_counts.items():
        p_bictx = bictx_count / total_tri
        # Conditional distribution P(class_t | class_{t-1} = bictx[1], class_{t-2} = bictx[0])
        targets = {k[2]: v for k, v in trigram_counts.items()
                   if k[0] == bictx[0] and k[1] == bictx[1]}
        total_tgt = sum(targets.values())
        if total_tgt == 0:
            continue
        probs = np.array(list(targets.values()), dtype=float) / total_tgt
        h_bictx = float(scipy_entropy(probs, base=2))
        h_trigram += p_bictx * h_bictx

    cmi = h_bigram - h_trigram
    return float(cmi), n_trigrams, n_bigrams


# -- OLS/LOO Utilities --

def ols_fit(X, y):
    """OLS regression. Returns coefficients, R-squared, predictions."""
    n = X.shape[0]
    X_aug = np.column_stack([np.ones(n), X])
    beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    y_pred = X_aug @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, r2, y_pred


def loo_cv_r2(X, y):
    """Leave-one-out cross-validated R-squared."""
    n = X.shape[0]
    predictions = np.zeros(n)

    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_train = X[mask]
        y_train = y[mask]

        X_aug = np.column_stack([np.ones(X_train.shape[0]), X_train])
        beta = np.linalg.lstsq(X_aug, y_train, rcond=None)[0]

        x_test = np.concatenate([[1], X[i]])
        predictions[i] = x_test @ beta

    ss_res = np.sum((y - predictions) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


def eta_squared(values, groups):
    """Compute eta-squared for one-way grouping."""
    grand_mean = np.mean(values)
    ss_total = np.sum((values - grand_mean) ** 2)
    if ss_total < 1e-15:
        return 0.0

    ss_between = 0
    for g in set(groups):
        mask = [i for i, gl in enumerate(groups) if gl == g]
        if mask:
            group_mean = np.mean([values[i] for i in mask])
            ss_between += len(mask) * (group_mean - grand_mean) ** 2

    return ss_between / ss_total


# -- Main --

def main():
    start = time.time()

    print("Phase 360: AXM_RUN_MICROSEQUENCE")
    print("=" * 70)

    # ---- Load data ----
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    c1035_data = load_c1035_data()
    regimes = load_regime_assignments()
    archetypes = load_folio_archetypes()

    # ---- S1: Extract AXM Runs ----
    print("\n--- S1: EXTRACT AXM CLASS-LEVEL RUNS ---")
    folio_runs, folio_sections, folio_bigram_counts = extract_axm_runs(token_to_class)

    # Filter to folios with enough within-run transitions AND C1035 residuals
    valid_folios = sorted(
        f for f in folio_runs
        if folio_bigram_counts.get(f, 0) >= MIN_AXM_TRANSITIONS
        and f in c1035_data
    )
    n = len(valid_folios)
    print(f"  {len(folio_runs)} folios with AXM runs")
    print(f"  {n} folios with >= {MIN_AXM_TRANSITIONS} within-run bigrams and C1035 data")

    total_runs = sum(len(folio_runs[f]) for f in valid_folios)
    total_bigrams = sum(folio_bigram_counts[f] for f in valid_folios)
    run_lengths = [len(r) for f in valid_folios for r in folio_runs[f]]
    print(f"  Total AXM runs (len >= 2): {total_runs}")
    print(f"  Total within-run bigrams: {total_bigrams}")
    print(f"  Run length stats: mean={np.mean(run_lengths):.2f}, "
          f"median={np.median(run_lengths):.1f}, "
          f"max={max(run_lengths)}, "
          f"Q75={np.percentile(run_lengths, 75):.0f}")

    # Prepare target vectors
    y_residual = np.array([c1035_data[f]['c1017_residual'] for f in valid_folios])
    y_axm_self = np.array([c1035_data[f]['axm_self'] for f in valid_folios])

    # Build C1017 baseline predictor matrix
    regime_set = sorted(set(regimes.get(f, 0) for f in valid_folios))
    section_set = sorted(set(folio_sections.get(f, '') for f in valid_folios))

    X_baseline = []
    for f in valid_folios:
        d = c1035_data[f]
        row = []
        for r in regime_set[1:]:
            row.append(1.0 if regimes.get(f, 0) == r else 0.0)
        for s in section_set[1:]:
            row.append(1.0 if folio_sections.get(f, '') == s else 0.0)
        row.extend([
            d['prefix_entropy'],
            d['hazard_density'],
            d['bridge_pc1']
        ])
        X_baseline.append(row)
    X_baseline = np.array(X_baseline)

    # Baseline LOO R2
    r2_baseline_loo = loo_cv_r2(X_baseline, y_axm_self)
    _, r2_baseline_train, _ = ols_fit(X_baseline, y_axm_self)
    print(f"\n  C1017 baseline: train R2={r2_baseline_train:.4f}, LOO R2={r2_baseline_loo:.4f}")

    # ---- S2: Entropy Gradient ----
    print("\n--- S2: CONDITIONAL TRANSITION ENTROPY GRADIENTS ---")

    folio_slopes = {}
    folio_curvatures = {}
    folio_n_positions = {}

    for f in valid_folios:
        positions, entropies, slope, curvature, n_by_pos = \
            compute_entropy_gradient(folio_runs[f])
        folio_slopes[f] = slope
        folio_curvatures[f] = curvature
        folio_n_positions[f] = len(positions)

    slopes = np.array([folio_slopes[f] for f in valid_folios])
    curvatures = np.array([folio_curvatures[f] for f in valid_folios])
    n_pos_arr = np.array([folio_n_positions[f] for f in valid_folios])

    print(f"  Entropy gradient slopes: mean={slopes.mean():.4f}, "
          f"std={slopes.std():.4f}, min={slopes.min():.4f}, max={slopes.max():.4f}")
    print(f"  Curvatures: mean={curvatures.mean():.4f}, std={curvatures.std():.4f}")
    print(f"  Valid positions per folio: mean={n_pos_arr.mean():.1f}, "
          f"min={n_pos_arr.min()}, max={n_pos_arr.max()}")

    # Corpus-level entropy gradient (pool all folios)
    all_runs = [r for f in valid_folios for r in folio_runs[f]]
    corp_pos, corp_ent, corp_slope, corp_curv, corp_n = \
        compute_entropy_gradient(all_runs)
    print(f"\n  Corpus entropy gradient:")
    for i, (p, e, nc) in enumerate(zip(corp_pos, corp_ent, corp_n)):
        print(f"    Position {p}: H={e:.4f} bits ({nc} transitions)")
    print(f"  Corpus slope: {corp_slope:.4f}, curvature: {corp_curv:.4f}")

    # ---- S3: Per-Folio MIDDLE Asymmetry (JSD) ----
    print("\n--- S3: PER-FOLIO MIDDLE ASYMMETRY (JSD) ---")

    folio_jsd_mean = {}
    folio_jsd_var = {}
    folio_jsd_skew = {}
    folio_jsd_nclasses = {}

    for f in valid_folios:
        jm, jv, js, nc, _ = compute_folio_jsd(folio_runs[f])
        folio_jsd_mean[f] = jm
        folio_jsd_var[f] = jv
        folio_jsd_skew[f] = js
        folio_jsd_nclasses[f] = nc

    jsd_means = np.array([folio_jsd_mean[f] for f in valid_folios])
    jsd_vars = np.array([folio_jsd_var[f] for f in valid_folios])
    jsd_skews = np.array([folio_jsd_skew[f] for f in valid_folios])
    jsd_nclass = np.array([folio_jsd_nclasses[f] for f in valid_folios])

    print(f"  JSD mean: mean={jsd_means.mean():.6f}, std={jsd_means.std():.6f}")
    print(f"  JSD variance: mean={jsd_vars.mean():.6f}, std={jsd_vars.std():.6f}")
    print(f"  JSD skewness: mean={jsd_skews.mean():.4f}, std={jsd_skews.std():.4f}")
    print(f"  Classes computed per folio: mean={jsd_nclass.mean():.1f}, "
          f"min={jsd_nclass.min()}, max={jsd_nclass.max()}")
    print(f"  JSD mean CV: {jsd_means.std() / jsd_means.mean():.4f}" if jsd_means.mean() > 0 else "")

    # Corpus-level JSD for validation
    corp_jsd_mean, corp_jsd_var, corp_jsd_skew, corp_nc, corp_per_class = \
        compute_folio_jsd(all_runs)
    print(f"\n  Corpus JSD (all AXM runs): weighted mean = {corp_jsd_mean:.6f} bits")
    print(f"  (C1024 corpus MIDDLE asymmetry = 0.070 bits — different scope)")

    # ---- S4: Per-Folio CMI ----
    print("\n--- S4: PER-FOLIO CMI DECOMPOSITION ---")

    folio_cmi = {}
    folio_n_trigrams = {}
    folio_n_bigrams = {}

    for f in valid_folios:
        cmi_val, n_tri, n_bi = compute_folio_cmi(folio_runs[f])
        folio_cmi[f] = cmi_val
        folio_n_trigrams[f] = n_tri
        folio_n_bigrams[f] = n_bi

    cmi_arr = np.array([folio_cmi[f] for f in valid_folios])
    n_tri_arr = np.array([folio_n_trigrams[f] for f in valid_folios])

    print(f"  Per-folio CMI: mean={cmi_arr.mean():.6f}, std={cmi_arr.std():.6f}")
    print(f"  CMI range: min={cmi_arr.min():.6f}, max={cmi_arr.max():.6f}")
    print(f"  Trigrams per folio: mean={n_tri_arr.mean():.0f}, "
          f"min={n_tri_arr.min()}, max={n_tri_arr.max()}")
    print(f"  (C969 corpus EN lane CMI = 0.012 bits — different scope)")

    # Permutation test for CMI variance
    # Pool all runs, randomly reassign to pseudo-folios, recompute CMI
    print("\n  CMI variance permutation test...")
    observed_var = float(np.var(cmi_arr))

    # Collect all runs with folio sizes
    all_runs_pool = []
    folio_sizes = []
    for f in valid_folios:
        runs_f = folio_runs[f]
        folio_sizes.append(len(runs_f))
        all_runs_pool.extend(runs_f)

    perm_vars = []
    for perm_i in range(N_PERMUTATIONS):
        # Shuffle runs across pseudo-folios
        perm_order = np.random.permutation(len(all_runs_pool))
        shuffled_runs = [all_runs_pool[j] for j in perm_order]

        # Partition into pseudo-folios with same sizes
        perm_cmis = []
        offset = 0
        for sz in folio_sizes:
            pseudo_runs = shuffled_runs[offset:offset + sz]
            offset += sz
            cmi_val, _, _ = compute_folio_cmi(pseudo_runs)
            perm_cmis.append(cmi_val)

        perm_vars.append(float(np.var(perm_cmis)))

    perm_vars = np.array(perm_vars)
    p_cmi_var = float(np.mean(perm_vars >= observed_var))

    print(f"  Observed CMI variance: {observed_var:.8f}")
    print(f"  Permutation null mean: {perm_vars.mean():.8f}")
    print(f"  Permutation p-value: {p_cmi_var:.4f}")

    # ---- S5: Residual Prediction — Entropy Gradient ----
    print("\n--- S5: RESIDUAL PREDICTION — ENTROPY GRADIENT ---")

    X_ent = np.column_stack([slopes, curvatures])
    _, r2_ent_train, _ = ols_fit(X_ent, y_residual)
    r2_ent_loo = loo_cv_r2(X_ent, y_residual)
    print(f"  Entropy gradient on residual: train R2={r2_ent_train:.4f}, LOO R2={r2_ent_loo:.4f}")

    # Incremental over C1017
    X_combined_ent = np.column_stack([X_baseline, slopes, curvatures])
    _, r2_comb_ent_train, _ = ols_fit(X_combined_ent, y_axm_self)
    r2_comb_ent_loo = loo_cv_r2(X_combined_ent, y_axm_self)
    incr_ent = r2_comb_ent_loo - r2_baseline_loo
    print(f"  C1017 + entropy gradient: train R2={r2_comb_ent_train:.4f}, LOO R2={r2_comb_ent_loo:.4f}")
    print(f"  Incremental LOO R2: {incr_ent:+.4f}")

    # Spearman correlation with residual
    from scipy.stats import spearmanr
    rho_slope, p_slope = spearmanr(slopes, y_residual)
    rho_curv, p_curv = spearmanr(curvatures, y_residual)
    print(f"  Slope vs residual: rho={rho_slope:.4f}, p={p_slope:.4f}")
    print(f"  Curvature vs residual: rho={rho_curv:.4f}, p={p_curv:.4f}")

    # ---- S6: Residual Prediction — MIDDLE Asymmetry ----
    print("\n--- S6: RESIDUAL PREDICTION — MIDDLE ASYMMETRY ---")

    X_jsd = np.column_stack([jsd_means, jsd_vars, jsd_skews])
    _, r2_jsd_train, _ = ols_fit(X_jsd, y_residual)
    r2_jsd_loo = loo_cv_r2(X_jsd, y_residual)
    print(f"  JSD features on residual: train R2={r2_jsd_train:.4f}, LOO R2={r2_jsd_loo:.4f}")

    # Incremental over C1017
    X_combined_jsd = np.column_stack([X_baseline, jsd_means, jsd_vars, jsd_skews])
    _, r2_comb_jsd_train, _ = ols_fit(X_combined_jsd, y_axm_self)
    r2_comb_jsd_loo = loo_cv_r2(X_combined_jsd, y_axm_self)
    incr_jsd = r2_comb_jsd_loo - r2_baseline_loo
    print(f"  C1017 + JSD features: train R2={r2_comb_jsd_train:.4f}, LOO R2={r2_comb_jsd_loo:.4f}")
    print(f"  Incremental LOO R2: {incr_jsd:+.4f}")

    rho_jsd_mean, p_jsd_mean = spearmanr(jsd_means, y_residual)
    print(f"  JSD mean vs residual: rho={rho_jsd_mean:.4f}, p={p_jsd_mean:.4f}")

    # ---- S7: Residual Prediction — CMI ----
    print("\n--- S7: RESIDUAL PREDICTION — CMI ---")

    X_cmi = cmi_arr.reshape(-1, 1)
    _, r2_cmi_train, _ = ols_fit(X_cmi, y_residual)
    r2_cmi_loo = loo_cv_r2(X_cmi, y_residual)
    print(f"  CMI on residual: train R2={r2_cmi_train:.4f}, LOO R2={r2_cmi_loo:.4f}")

    # Incremental over C1017
    X_combined_cmi = np.column_stack([X_baseline, cmi_arr])
    _, r2_comb_cmi_train, _ = ols_fit(X_combined_cmi, y_axm_self)
    r2_comb_cmi_loo = loo_cv_r2(X_combined_cmi, y_axm_self)
    incr_cmi = r2_comb_cmi_loo - r2_baseline_loo
    print(f"  C1017 + CMI: train R2={r2_comb_cmi_train:.4f}, LOO R2={r2_comb_cmi_loo:.4f}")
    print(f"  Incremental LOO R2: {incr_cmi:+.4f}")

    rho_cmi, p_cmi = spearmanr(cmi_arr, y_residual)
    print(f"  CMI vs residual: rho={rho_cmi:.4f}, p={p_cmi:.4f}")

    # ---- S8: Combined Prediction ----
    print("\n--- S8: COMBINED MICRO-SEQUENTIAL PREDICTION ---")

    X_all_micro = np.column_stack([slopes, curvatures, jsd_means, jsd_vars, jsd_skews, cmi_arr])
    _, r2_all_train, _ = ols_fit(X_all_micro, y_residual)
    r2_all_loo = loo_cv_r2(X_all_micro, y_residual)
    print(f"  All micro-sequential on residual: train R2={r2_all_train:.4f}, LOO R2={r2_all_loo:.4f}")

    # Incremental over C1017
    X_combined_all = np.column_stack([X_baseline, slopes, curvatures,
                                      jsd_means, jsd_vars, jsd_skews, cmi_arr])
    _, r2_comb_all_train, _ = ols_fit(X_combined_all, y_axm_self)
    r2_comb_all_loo = loo_cv_r2(X_combined_all, y_axm_self)
    incr_all = r2_comb_all_loo - r2_baseline_loo
    print(f"  C1017 + all micro: train R2={r2_comb_all_train:.4f}, LOO R2={r2_comb_all_loo:.4f}")
    print(f"  Incremental LOO R2: {incr_all:+.4f}")

    # ---- S9: Archetype Stratification ----
    print("\n--- S9: ARCHETYPE STRATIFICATION ---")

    folio_arch = [archetypes.get(f, -1) for f in valid_folios]
    arch_set = sorted(set(folio_arch))

    # ANOVA: slope by archetype
    from scipy.stats import f_oneway
    arch_groups_slope = [slopes[np.array(folio_arch) == a] for a in arch_set if sum(np.array(folio_arch) == a) >= 2]
    if len(arch_groups_slope) >= 2:
        f_stat_slope, p_slope_anova = f_oneway(*arch_groups_slope)
    else:
        f_stat_slope, p_slope_anova = 0.0, 1.0

    eta2_slope = eta_squared(slopes, folio_arch)
    print(f"  Slope by archetype: F={f_stat_slope:.3f}, p={p_slope_anova:.4f}, eta2={eta2_slope:.4f}")

    # ANOVA: curvature by archetype
    arch_groups_curv = [curvatures[np.array(folio_arch) == a] for a in arch_set if sum(np.array(folio_arch) == a) >= 2]
    if len(arch_groups_curv) >= 2:
        f_stat_curv, p_curv_anova = f_oneway(*arch_groups_curv)
    else:
        f_stat_curv, p_curv_anova = 0.0, 1.0

    eta2_curv = eta_squared(curvatures, folio_arch)
    print(f"  Curvature by archetype: F={f_stat_curv:.3f}, p={p_curv_anova:.4f}, eta2={eta2_curv:.4f}")

    # ANOVA: JSD mean by archetype
    arch_groups_jsd = [jsd_means[np.array(folio_arch) == a] for a in arch_set if sum(np.array(folio_arch) == a) >= 2]
    if len(arch_groups_jsd) >= 2:
        f_stat_jsd, p_jsd_anova = f_oneway(*arch_groups_jsd)
    else:
        f_stat_jsd, p_jsd_anova = 0.0, 1.0

    eta2_jsd = eta_squared(jsd_means, folio_arch)
    print(f"  JSD mean by archetype: F={f_stat_jsd:.3f}, p={p_jsd_anova:.4f}, eta2={eta2_jsd:.4f}")

    # ANOVA: CMI by archetype
    arch_groups_cmi = [cmi_arr[np.array(folio_arch) == a] for a in arch_set if sum(np.array(folio_arch) == a) >= 2]
    if len(arch_groups_cmi) >= 2:
        f_stat_cmi_a, p_cmi_anova = f_oneway(*arch_groups_cmi)
    else:
        f_stat_cmi_a, p_cmi_anova = 0.0, 1.0

    eta2_cmi = eta_squared(cmi_arr, folio_arch)
    print(f"  CMI by archetype: F={f_stat_cmi_a:.3f}, p={p_cmi_anova:.4f}, eta2={eta2_cmi:.4f}")

    # Per-archetype summary
    print(f"\n  Per-archetype means:")
    print(f"  {'Arch':>5} {'N':>4} {'Slope':>8} {'Curv':>8} {'JSD':>10} {'CMI':>10}")
    for a in arch_set:
        mask = np.array(folio_arch) == a
        na = mask.sum()
        if na == 0:
            continue
        print(f"  {a:>5} {na:>4} {slopes[mask].mean():>8.4f} {curvatures[mask].mean():>8.4f} "
              f"{jsd_means[mask].mean():>10.6f} {cmi_arr[mask].mean():>10.6f}")

    # ---- S10: Sample-Size Control Diagnostic ----
    print("\n--- S10: SAMPLE-SIZE CONTROL DIAGNOSTIC ---")

    # Compute per-folio transition counts
    n_trans = np.array([folio_bigram_counts[f] for f in valid_folios], dtype=float)
    log_n_trans = np.log(n_trans)

    # Check: is CMI correlated with sample size?
    rho_cmi_size, p_cmi_size = spearmanr(cmi_arr, log_n_trans)
    print(f"  CMI vs log(n_transitions): rho={rho_cmi_size:.4f}, p={p_cmi_size:.6f}")

    # Check: is JSD mean correlated with sample size?
    rho_jsd_size, p_jsd_size = spearmanr(jsd_means, log_n_trans)
    print(f"  JSD mean vs log(n_transitions): rho={rho_jsd_size:.4f}, p={p_jsd_size:.6f}")

    # Check: is sample size correlated with residual?
    rho_size_resid, p_size_resid = spearmanr(log_n_trans, y_residual)
    print(f"  log(n_transitions) vs residual: rho={rho_size_resid:.4f}, p={p_size_resid:.6f}")

    # Residualize JSD mean against sample size
    _, _, jsd_pred_from_size = ols_fit(log_n_trans.reshape(-1, 1), jsd_means)
    jsd_resid = jsd_means - jsd_pred_from_size

    rho_jsd_resid_vs_residual, p_jsd_resid_vs_residual = spearmanr(jsd_resid, y_residual)
    print(f"\n  Size-residualized JSD vs C1035 residual: "
          f"rho={rho_jsd_resid_vs_residual:.4f}, p={p_jsd_resid_vs_residual:.4f}")

    # Incremental LOO with residualized JSD
    X_jsd_resid = np.column_stack([jsd_resid, jsd_vars, jsd_skews])
    X_combined_jsd_resid = np.column_stack([X_baseline, jsd_resid, jsd_vars, jsd_skews])
    _, r2_comb_jsd_resid_train, _ = ols_fit(X_combined_jsd_resid, y_axm_self)
    r2_comb_jsd_resid_loo = loo_cv_r2(X_combined_jsd_resid, y_axm_self)
    incr_jsd_resid = r2_comb_jsd_resid_loo - r2_baseline_loo
    print(f"  C1017 + size-residualized JSD: LOO R2={r2_comb_jsd_resid_loo:.4f}, "
          f"incremental={incr_jsd_resid:+.4f}")

    # Residualize CMI against sample size
    _, _, cmi_pred_from_size = ols_fit(log_n_trans.reshape(-1, 1), cmi_arr)
    cmi_resid = cmi_arr - cmi_pred_from_size

    rho_cmi_resid_vs_residual, p_cmi_resid_vs_residual = spearmanr(cmi_resid, y_residual)
    print(f"  Size-residualized CMI vs C1035 residual: "
          f"rho={rho_cmi_resid_vs_residual:.4f}, p={p_cmi_resid_vs_residual:.4f}")

    # Incremental LOO with residualized CMI
    X_combined_cmi_resid = np.column_stack([X_baseline, cmi_resid])
    _, r2_comb_cmi_resid_train, _ = ols_fit(X_combined_cmi_resid, y_axm_self)
    r2_comb_cmi_resid_loo = loo_cv_r2(X_combined_cmi_resid, y_axm_self)
    incr_cmi_resid = r2_comb_cmi_resid_loo - r2_baseline_loo
    print(f"  C1017 + size-residualized CMI: LOO R2={r2_comb_cmi_resid_loo:.4f}, "
          f"incremental={incr_cmi_resid:+.4f}")

    # Combined without CMI (JSD only + entropy)
    X_no_cmi = np.column_stack([slopes, curvatures, jsd_means, jsd_vars, jsd_skews])
    X_combined_no_cmi = np.column_stack([X_baseline, slopes, curvatures,
                                         jsd_means, jsd_vars, jsd_skews])
    _, r2_comb_nocmi_train, _ = ols_fit(X_combined_no_cmi, y_axm_self)
    r2_comb_nocmi_loo = loo_cv_r2(X_combined_no_cmi, y_axm_self)
    incr_nocmi = r2_comb_nocmi_loo - r2_baseline_loo
    print(f"\n  C1017 + entropy + JSD (no CMI): LOO R2={r2_comb_nocmi_loo:.4f}, "
          f"incremental={incr_nocmi:+.4f}")

    # Miller-Madow bias correction for CMI
    # CMI_corrected = CMI_raw - (k_bigram - k_trigram) / (2 * N * ln(2))
    # where k = number of observed distinct types
    print(f"\n  Miller-Madow CMI bias correction:")
    cmi_corrected = []
    for f in valid_folios:
        runs_f = folio_runs[f]
        bigram_types = set()
        trigram_types = set()
        n_bi = 0
        n_tri = 0
        for run in runs_f:
            for i in range(1, len(run)):
                bigram_types.add((run[i-1], run[i]))
                n_bi += 1
            for i in range(2, len(run)):
                trigram_types.add((run[i-2], run[i-1], run[i]))
                n_tri += 1
        k_bi = len(bigram_types)
        k_tri = len(trigram_types)
        raw_cmi = folio_cmi[f]
        # Bias ~ (k-1)/(2*N*ln2) for each entropy term
        bias_bigram = (k_bi - 1) / (2 * max(n_bi, 1) * np.log(2)) if n_bi > 0 else 0
        bias_trigram = (k_tri - 1) / (2 * max(n_tri, 1) * np.log(2)) if n_tri > 0 else 0
        correction = bias_bigram - bias_trigram
        cmi_corrected.append(max(0, raw_cmi - correction))

    cmi_corrected = np.array(cmi_corrected)
    print(f"  Raw CMI mean: {cmi_arr.mean():.4f}, Corrected CMI mean: {cmi_corrected.mean():.4f}")
    print(f"  Mean bias correction: {(cmi_arr - cmi_corrected).mean():.4f} bits")

    rho_cmi_corr, p_cmi_corr = spearmanr(cmi_corrected, y_residual)
    print(f"  Corrected CMI vs residual: rho={rho_cmi_corr:.4f}, p={p_cmi_corr:.4f}")

    X_cmi_corr = cmi_corrected.reshape(-1, 1)
    X_combined_cmi_corr = np.column_stack([X_baseline, cmi_corrected])
    _, r2_comb_cmi_corr_train, _ = ols_fit(X_combined_cmi_corr, y_axm_self)
    r2_comb_cmi_corr_loo = loo_cv_r2(X_combined_cmi_corr, y_axm_self)
    incr_cmi_corr = r2_comb_cmi_corr_loo - r2_baseline_loo
    print(f"  C1017 + corrected CMI: LOO R2={r2_comb_cmi_corr_loo:.4f}, "
          f"incremental={incr_cmi_corr:+.4f}")

    # ---- S11: Evaluate Predictions ----
    print("\n--- S11: EVALUATE PREDICTIONS ---")

    # C1037 class-composition CV for P6
    c1037_composition_cv = 1.048  # From C1037: mean CV of hazard-adjacent class proportions

    jsd_cv = float(jsd_means.std() / jsd_means.mean()) if jsd_means.mean() > 0 else 0.0

    p1_pass = incr_ent > 0.02
    p2_pass = incr_jsd > 0.02
    p3_pass = p_cmi_var < 0.01
    p4_pass = incr_all > 0.02
    p5_pass = p_curv_anova < 0.01
    p6_pass = jsd_cv > c1037_composition_cv

    predictions = {
        'P1': {
            'description': 'Entropy gradient predicts residual (LOO incr R2 > 0.02)',
            'result': f'Incremental LOO R2={incr_ent:+.4f}',
            'incr_loo_r2': round(incr_ent, 4),
            'pass': bool(p1_pass)
        },
        'P2': {
            'description': 'MIDDLE asymmetry predicts residual (LOO incr R2 > 0.02)',
            'result': f'Incremental LOO R2={incr_jsd:+.4f}',
            'incr_loo_r2': round(incr_jsd, 4),
            'pass': bool(p2_pass)
        },
        'P3': {
            'description': 'Per-folio CMI variance exceeds permutation null (p < 0.01)',
            'result': f'p={p_cmi_var:.4f}, observed var={observed_var:.8f}',
            'p_value': round(p_cmi_var, 4),
            'observed_var': round(observed_var, 8),
            'pass': bool(p3_pass)
        },
        'P4': {
            'description': 'Combined micro-sequential features predict residual (LOO incr R2 > 0.02)',
            'result': f'Incremental LOO R2={incr_all:+.4f}',
            'incr_loo_r2': round(incr_all, 4),
            'pass': bool(p4_pass)
        },
        'P5': {
            'description': 'Entropy gradient curvature differs by archetype (ANOVA p < 0.01)',
            'result': f'F={f_stat_curv:.3f}, p={p_curv_anova:.4f}',
            'f_stat': round(f_stat_curv, 3),
            'p_value': round(p_curv_anova, 4),
            'pass': bool(p5_pass)
        },
        'P6': {
            'description': 'MIDDLE asymmetry CV > class-composition CV',
            'result': f'JSD CV={jsd_cv:.4f} vs composition CV={c1037_composition_cv:.4f}',
            'jsd_cv': round(jsd_cv, 4),
            'composition_cv': round(c1037_composition_cv, 4),
            'pass': bool(p6_pass)
        }
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])

    # Global decision rule
    global_fail = incr_ent < 0.01 and incr_jsd < 0.01 and incr_all < 0.01
    if global_fail:
        verdict = 'MICROSEQUENCE_STRATUM_EMPTY'
    elif n_pass >= 3:
        verdict = 'MICROSEQUENCE_SIGNAL_FOUND'
    else:
        verdict = 'MICROSEQUENCE_WEAK_SIGNAL'

    print(f"\n  Prediction outcomes:")
    for pid, pred in predictions.items():
        status = 'PASS' if pred['pass'] else 'FAIL'
        print(f"    {pid}: {status} — {pred['result']}")

    print(f"\n  {n_pass}/6 passed")
    print(f"  Global decision rule (P1,P2,P4 all incr < 0.01): {'MET' if global_fail else 'NOT MET'}")
    print(f"  Verdict: {verdict}")

    # ---- Save Results ----
    results = {
        'phase_name': 'AXM_RUN_MICROSEQUENCE',
        'phase_number': 360,
        'n_folios': n,
        's1_run_statistics': {
            'total_runs': total_runs,
            'total_bigrams': total_bigrams,
            'run_length_mean': round(float(np.mean(run_lengths)), 2),
            'run_length_median': round(float(np.median(run_lengths)), 1),
            'run_length_max': int(max(run_lengths)),
        },
        's2_entropy_gradient': {
            'corpus_slope': round(corp_slope, 4),
            'corpus_curvature': round(corp_curv, 4),
            'corpus_positions': {str(p): round(e, 4) for p, e in zip(corp_pos, corp_ent)},
            'folio_slope_mean': round(float(slopes.mean()), 4),
            'folio_slope_std': round(float(slopes.std()), 4),
            'folio_curvature_mean': round(float(curvatures.mean()), 4),
            'folio_curvature_std': round(float(curvatures.std()), 4),
        },
        's3_middle_asymmetry': {
            'corpus_jsd_mean': round(corp_jsd_mean, 6),
            'folio_jsd_mean_mean': round(float(jsd_means.mean()), 6),
            'folio_jsd_mean_std': round(float(jsd_means.std()), 6),
            'folio_jsd_mean_cv': round(jsd_cv, 4),
            'folio_jsd_var_mean': round(float(jsd_vars.mean()), 6),
            'folio_jsd_skew_mean': round(float(jsd_skews.mean()), 4),
            'classes_computed_mean': round(float(jsd_nclass.mean()), 1),
        },
        's4_cmi': {
            'folio_cmi_mean': round(float(cmi_arr.mean()), 6),
            'folio_cmi_std': round(float(cmi_arr.std()), 6),
            'folio_cmi_min': round(float(cmi_arr.min()), 6),
            'folio_cmi_max': round(float(cmi_arr.max()), 6),
            'cmi_variance_observed': round(observed_var, 8),
            'cmi_variance_perm_mean': round(float(perm_vars.mean()), 8),
            'cmi_variance_perm_p': round(p_cmi_var, 4),
            'n_permutations': N_PERMUTATIONS,
        },
        's5_entropy_prediction': {
            'r2_on_residual_train': round(r2_ent_train, 4),
            'r2_on_residual_loo': round(r2_ent_loo, 4),
            'r2_combined_train': round(r2_comb_ent_train, 4),
            'r2_combined_loo': round(r2_comb_ent_loo, 4),
            'incremental_loo': round(incr_ent, 4),
            'slope_vs_residual_rho': round(rho_slope, 4),
            'slope_vs_residual_p': round(p_slope, 4),
            'curvature_vs_residual_rho': round(rho_curv, 4),
            'curvature_vs_residual_p': round(p_curv, 4),
        },
        's6_jsd_prediction': {
            'r2_on_residual_train': round(r2_jsd_train, 4),
            'r2_on_residual_loo': round(r2_jsd_loo, 4),
            'r2_combined_train': round(r2_comb_jsd_train, 4),
            'r2_combined_loo': round(r2_comb_jsd_loo, 4),
            'incremental_loo': round(incr_jsd, 4),
            'jsd_mean_vs_residual_rho': round(rho_jsd_mean, 4),
            'jsd_mean_vs_residual_p': round(p_jsd_mean, 4),
        },
        's7_cmi_prediction': {
            'r2_on_residual_train': round(r2_cmi_train, 4),
            'r2_on_residual_loo': round(r2_cmi_loo, 4),
            'r2_combined_train': round(r2_comb_cmi_train, 4),
            'r2_combined_loo': round(r2_comb_cmi_loo, 4),
            'incremental_loo': round(incr_cmi, 4),
            'cmi_vs_residual_rho': round(rho_cmi, 4),
            'cmi_vs_residual_p': round(p_cmi, 4),
        },
        's8_combined_prediction': {
            'r2_on_residual_train': round(r2_all_train, 4),
            'r2_on_residual_loo': round(r2_all_loo, 4),
            'r2_combined_train': round(r2_comb_all_train, 4),
            'r2_combined_loo': round(r2_comb_all_loo, 4),
            'incremental_loo': round(incr_all, 4),
        },
        's10_size_control': {
            'cmi_vs_log_n_rho': round(rho_cmi_size, 4),
            'cmi_vs_log_n_p': round(float(p_cmi_size), 6),
            'jsd_vs_log_n_rho': round(rho_jsd_size, 4),
            'jsd_vs_log_n_p': round(float(p_jsd_size), 6),
            'log_n_vs_residual_rho': round(rho_size_resid, 4),
            'log_n_vs_residual_p': round(float(p_size_resid), 6),
            'jsd_resid_vs_residual_rho': round(rho_jsd_resid_vs_residual, 4),
            'jsd_resid_vs_residual_p': round(float(p_jsd_resid_vs_residual), 4),
            'incr_loo_jsd_residualized': round(incr_jsd_resid, 4),
            'cmi_resid_vs_residual_rho': round(rho_cmi_resid_vs_residual, 4),
            'cmi_resid_vs_residual_p': round(float(p_cmi_resid_vs_residual), 4),
            'incr_loo_cmi_residualized': round(incr_cmi_resid, 4),
            'incr_loo_no_cmi': round(incr_nocmi, 4),
            'cmi_raw_mean': round(float(cmi_arr.mean()), 4),
            'cmi_corrected_mean': round(float(cmi_corrected.mean()), 4),
            'cmi_bias_correction_mean': round(float((cmi_arr - cmi_corrected).mean()), 4),
            'cmi_corrected_vs_residual_rho': round(rho_cmi_corr, 4),
            'cmi_corrected_vs_residual_p': round(float(p_cmi_corr), 4),
            'incr_loo_cmi_corrected': round(incr_cmi_corr, 4),
        },
        's9_archetype_stratification': {
            'slope_anova_F': round(f_stat_slope, 3),
            'slope_anova_p': round(p_slope_anova, 4),
            'slope_eta2': round(eta2_slope, 4),
            'curvature_anova_F': round(f_stat_curv, 3),
            'curvature_anova_p': round(p_curv_anova, 4),
            'curvature_eta2': round(eta2_curv, 4),
            'jsd_anova_F': round(f_stat_jsd, 3),
            'jsd_anova_p': round(p_jsd_anova, 4),
            'jsd_eta2': round(eta2_jsd, 4),
            'cmi_anova_F': round(f_stat_cmi_a, 3),
            'cmi_anova_p': round(p_cmi_anova, 4),
            'cmi_eta2': round(eta2_cmi, 4),
        },
        'c1017_baseline': {
            'r2_train': round(r2_baseline_train, 4),
            'r2_loo': round(r2_baseline_loo, 4),
        },
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': 6,
        'global_decision_rule_met': global_fail,
        'verdict': verdict,
    }

    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)
    results_path = results_dir / 'axm_run_microsequence.json'

    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            converted = convert(obj)
            if converted is not obj:
                return converted
            return super().default(obj)

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {results_path}")

    elapsed = time.time() - start
    print(f"\nPhase 360 complete in {elapsed:.1f}s")


if __name__ == '__main__':
    main()
