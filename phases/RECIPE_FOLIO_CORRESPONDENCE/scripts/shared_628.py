"""
Phase 628: RECIPE_FOLIO_CORRESPONDENCE -- Shared utilities.

Thin wrapper around shared_627.py providing locked feature dimensions
and core matching functions for PL chapter-to-V folio correspondence.
"""

import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any

import sys
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_PROJECT_ROOT / 'phases' / 'PER_DOMAIN_BRIDGE_CALIBRATION' / 'scripts'))

from shared_627 import (
    # Re-export all loaders
    load_pl_structural_profile,
    load_pl_chapters,
    load_pl_english_lines,
    load_pl_channel_features,
    load_bridge_decomposition,
    load_bridge_functional_groups,
    load_b_operational_profiles,
    load_regime_mapping,
    load_b_deployment_features,
    load_brunschwig_profiles,
    compute_folio_head_channel_profile,
    compute_regime_head_profiles,
    get_folio_section,
    get_herbal_folios,
    get_stars_folios,
    # Re-export stats
    spearman_rank,
    kruskal_wallis,
    mann_whitney_u,
    mantel_test,
    euclidean_dist,
    cosine_sim,
    cohens_d,
    bonferroni_threshold,
    round_floats,
    # Re-export constants
    PROJECT_ROOT,
    CATEGORIES,
    HEAT_MODES,
    HEAT_INTENSITY,
    FIRE_DEGREE_REGIME,
    HEAD_TYPES,
)

from scripts.voynich import Transcript, Morphology

# ============================================================
# Phase 628 Constants
# ============================================================

PHASE_DIR = _PROJECT_ROOT / 'phases' / 'RECIPE_FOLIO_CORRESPONDENCE'
RESULTS_DIR = PHASE_DIR / 'results'

N_PERM = 1000
N_CV = 500
RNG = random.Random(628)

# The 8 locked dimensions (tuned on distillation->R1, frozen for all tests)
TUNED_DIMS = [
    ('heat_rate',            'k_ratio',                           -1),
    ('monitoring_rate',      'h_ratio',                            1),
    ('correction_rate',      'e_ratio',                            1),
    ('termination_rate',     'terminal_rate',                      1),
    ('consistency_frac',     'd_m_linefinal_rate',                -1),
    ('heat_rate',            'd_hl_displaced_suffix_transparency', -1),
    ('monitoring_rate',      'd_hl_header_enrichment',            -1),
    ('heat_transition_rate', 'thermo_ke',                          1),
]

# The 4 known channel mappings from Phase 627
KNOWN_DIMS = TUNED_DIMS[:4]


# ============================================================
# PL / V Data Extraction
# ============================================================

def load_family_chapters(family: str) -> List[dict]:
    """Return PL chapters for a given primary_family."""
    pl_feats = load_pl_channel_features()
    per_ch = pl_feats['T5_channel_signatures']['per_chapter']
    return [ch for ch in per_ch if ch.get('family') == family]


def load_regime_folios(regime: str) -> List[str]:
    """Return sorted folio list for a given REGIME."""
    regime_map = load_regime_mapping()
    return sorted(f for f, r in regime_map.items() if r == regime)


def build_pl_vector(chapter: dict, dims: list) -> List[float]:
    """Build PL-side feature vector from chapter channel signatures."""
    vec = []
    for pl_feat, v_feat, sign in dims:
        # PL features are in k_channel, h_channel, e_channel, t_channel sub-dicts
        val = None
        for ch_key in ['k_channel', 'h_channel', 'e_channel', 't_channel']:
            ch = chapter.get(ch_key, {})
            if pl_feat in ch:
                val = ch[pl_feat]
                break
        if val is None:
            val = chapter.get(pl_feat, 0.0)
        vec.append(float(val) if val is not None else 0.0)
    return vec


def build_v_vector(folio: str, op_profiles: dict, deploy_features: dict,
                   dims: list) -> List[float]:
    """Build V-side feature vector from operational and deployment profiles."""
    prof = op_profiles.get(folio, {})
    deploy = deploy_features.get(folio, {})
    vec = []
    for pl_feat, v_feat, sign in dims:
        if v_feat.startswith('d_'):
            raw_key = v_feat[2:]
            val = deploy.get(raw_key, 0.0)
        else:
            val = prof.get(v_feat, 0.0)
        vec.append(float(val) if val is not None else 0.0)
    return vec


def compute_residuals(vectors: List[List[float]]) -> List[List[float]]:
    """Subtract mean vector from each vector."""
    n = len(vectors)
    if n == 0:
        return []
    d = len(vectors[0])
    means = [sum(v[i] for v in vectors) / n for i in range(d)]
    return [[v[i] - means[i] for i in range(d)] for v in vectors]


def standardize(vectors: List[List[float]]) -> List[List[float]]:
    """Z-score standardize each dimension across vectors."""
    n = len(vectors)
    if n < 2:
        return vectors
    d = len(vectors[0])
    result = []
    for i in range(d):
        vals = [v[i] for v in vectors]
        mu = sum(vals) / n
        var = sum((x - mu) ** 2 for x in vals) / n
        sd = math.sqrt(var) if var > 0 else 1.0
        for j, v in enumerate(vectors):
            if i == 0:
                result.append([0.0] * d)
            result[j][i] = (v[i] - mu) / sd
    return result


# ============================================================
# Core Matching
# ============================================================

def residual_match(pl_chapters: List[dict], v_folios: List[str],
                   dims: list, op_profiles: dict = None,
                   deploy_features: dict = None) -> dict:
    """Core residual matching: PL chapters -> V folios.

    Returns dict with:
        assignment: {chapter_idx: folio_idx}
        match_table: [{chapter, folio, distance, ratio, ...}]
        mean_distance, mean_ratio, n_confident, n_unique_nn
    """
    if op_profiles is None:
        op_profiles = load_b_operational_profiles()
    if deploy_features is None:
        deploy_features, _ = load_b_deployment_features()

    n_pl = len(pl_chapters)
    n_v = len(v_folios)

    # Build raw vectors
    pl_raw = [build_pl_vector(ch, dims) for ch in pl_chapters]
    v_raw = [build_v_vector(f, op_profiles, deploy_features, dims) for f in v_folios]

    # Apply sign flips to PL side ONLY (matching explore v10 convention)
    # Sign encodes correlation direction: -1 means PL high -> V low
    for i in range(n_pl):
        for d, (_, _, sign) in enumerate(dims):
            pl_raw[i][d] *= sign

    # Compute residuals
    pl_resid = compute_residuals(pl_raw)
    v_resid = compute_residuals(v_raw)

    # Standardize jointly
    all_vecs = pl_resid + v_resid
    all_std = standardize(all_vecs)
    pl_std = all_std[:n_pl]
    v_std = all_std[n_pl:]

    # Distance matrix
    dmat = [[0.0] * n_v for _ in range(n_pl)]
    for i in range(n_pl):
        for j in range(n_v):
            dmat[i][j] = math.sqrt(sum((pl_std[i][d] - v_std[j][d]) ** 2
                                       for d in range(len(dims))))

    # Greedy assignment via globally sorted (i,j) pairs
    assign = {}
    used = set()
    cands = sorted([(dmat[i][j], i, j)
                    for i in range(n_pl) for j in range(n_v)])
    for d_val, i, j in cands:
        if i in assign or j in used:
            continue
        assign[i] = j
        used.add(j)
        if len(assign) == n_pl:
            break

    # Improvement: pair-swaps between assigned chapters + move-to-unused
    improved = True
    while improved:
        improved = False
        keys = list(assign.keys())
        # Pair swaps
        for a in range(len(keys)):
            for b in range(a + 1, len(keys)):
                i1, i2 = keys[a], keys[b]
                j1, j2 = assign[i1], assign[i2]
                if (dmat[i1][j2] + dmat[i2][j1]
                        < dmat[i1][j1] + dmat[i2][j2] - 1e-12):
                    assign[i1], assign[i2] = j2, j1
                    improved = True
        # Move to unused folio
        for i in keys:
            j_cur = assign[i]
            aset = set(assign.values())
            for j_new in range(n_v):
                if j_new in aset:
                    continue
                if dmat[i][j_new] < dmat[i][j_cur] - 1e-12:
                    assign[i] = j_new
                    improved = True
                    j_cur = j_new

    # Build match table with ratios
    match_table = []
    for i, j in sorted(assign.items()):
        dist = dmat[i][j]
        others = sorted([(dmat[i][jj], jj) for jj in range(n_v) if jj != j])
        second_dist = others[0][0] if others else dist
        ratio = second_dist / dist if dist > 0.01 else 1.0
        ch = pl_chapters[i]
        match_table.append({
            'chapter_number': ch.get('chapter_number', ch.get('number', '?')),
            'chapter_idx': ch.get('chapter_idx', i),
            'family': ch.get('family', '?'),
            'folio': v_folios[j],
            'distance': round(dist, 4),
            'second_distance': round(second_dist, 4),
            'ratio': round(ratio, 3),
            'confident': ratio > 1.15,
            'per_dim_dist_sq': [round((pl_std[i][d] - v_std[j][d]) ** 2, 4)
                                for d in range(len(dims))],
        })

    match_table.sort(key=lambda m: m['distance'])

    total = sum(dmat[i][j] for i, j in assign.items())
    mean_d = total / n_pl
    ratios = [m['ratio'] for m in match_table]
    mean_ratio = sum(ratios) / len(ratios)
    n_confident = sum(1 for m in match_table if m['confident'])
    nn_targets = set(min(range(n_v), key=lambda j: dmat[i][j]) for i in range(n_pl))
    n_unique = len(nn_targets)

    return {
        'assignment': {str(i): j for i, j in assign.items()},
        'match_table': match_table,
        'mean_distance': round(mean_d, 4),
        'mean_ratio': round(mean_ratio, 3),
        'n_confident': n_confident,
        'n_unique_nn': n_unique,
        'n_pl': n_pl,
        'n_v': n_v,
        'dmat': dmat,
        'pl_std': pl_std,
        'v_std': v_std,
    }


def cv_stability(pl_chapters: List[dict], v_folios: List[str],
                 dims: list, n_trials: int = N_CV,
                 op_profiles: dict = None,
                 deploy_features: dict = None) -> dict:
    """Feature-subset cross-validation for match stability.

    Samples 60-80% of dimensions per trial, re-runs matching,
    records which folio each chapter maps to.

    Returns dict with per-chapter top match + frequency.
    """
    if op_profiles is None:
        op_profiles = load_b_operational_profiles()
    if deploy_features is None:
        deploy_features, _ = load_b_deployment_features()

    n_dims = len(dims)
    # Track folio assignments per chapter
    from collections import Counter
    ch_matches = [Counter() for _ in range(len(pl_chapters))]

    rng = random.Random(628_500)  # Separate seed for CV
    for trial in range(n_trials):
        n_sample = rng.randint(max(3, int(n_dims * 0.6)),
                               min(n_dims, int(n_dims * 0.8) + 1))
        subset = sorted(rng.sample(range(n_dims), n_sample))
        sub_dims = [dims[d] for d in subset]

        result = residual_match(pl_chapters, v_folios, sub_dims,
                                op_profiles, deploy_features)
        for m in result['match_table']:
            ch_idx = next(
                (i for i, ch in enumerate(pl_chapters)
                 if ch.get('chapter_idx', i) == m['chapter_idx']),
                None
            )
            if ch_idx is not None:
                ch_matches[ch_idx][m['folio']] += 1

    # Build results
    cv_table = []
    n_consensus = 0
    for i, counter in enumerate(ch_matches):
        if not counter:
            continue
        top2 = counter.most_common(2)
        top_folio = top2[0][0]
        top_freq = top2[0][1] / n_trials
        second_folio = top2[1][0] if len(top2) > 1 else None
        second_freq = top2[1][1] / n_trials if len(top2) > 1 else 0
        ch = pl_chapters[i]
        consensus = top_freq > 0.40
        if consensus:
            n_consensus += 1
        cv_table.append({
            'chapter_number': ch.get('chapter_number', ch.get('number', '?')),
            'chapter_idx': ch.get('chapter_idx', i),
            'top_match': top_folio,
            'top_freq': round(top_freq, 3),
            'second_match': second_folio,
            'second_freq': round(second_freq, 3),
            'consensus': consensus,
        })

    return {
        'cv_table': cv_table,
        'n_consensus': n_consensus,
        'n_chapters': len(pl_chapters),
        'n_trials': n_trials,
    }


def permutation_test(pl_chapters: List[dict], v_folios: List[str],
                     dims: list, n_perm: int = N_PERM,
                     op_profiles: dict = None,
                     deploy_features: dict = None) -> dict:
    """Within-family permutation test.

    Fixes the distance matrix from real matching, then tests whether
    the OPTIMIZED assignment is significantly better than RANDOM
    chapter-to-folio assignments.

    Returns percentile of real assignment and p-value.
    """
    if op_profiles is None:
        op_profiles = load_b_operational_profiles()
    if deploy_features is None:
        deploy_features, _ = load_b_deployment_features()

    # Real match — get distance matrix and optimal assignment
    real = residual_match(pl_chapters, v_folios, dims, op_profiles, deploy_features)
    dmat = real['dmat']
    n_pl = real['n_pl']
    n_v = real['n_v']

    real_distance = real['mean_distance']
    real_ratio = real['mean_ratio']
    real_confident = real['n_confident']

    # Permutation null: randomly assign chapters to folios
    # (shuffle folio indices, compute total distance for random assignment)
    perm_distances = []
    perm_ratios = []
    perm_confident = []

    rng = random.Random(628_999)
    folio_indices = list(range(n_v))
    for _ in range(n_perm):
        rng.shuffle(folio_indices)
        # Random 1:1 assignment: chapter i -> folio_indices[i]
        perm_assign = {i: folio_indices[i] for i in range(n_pl)}
        total_d = sum(dmat[i][perm_assign[i]] for i in range(n_pl))
        perm_distances.append(total_d / n_pl)

        # Compute ratios for this random assignment
        ratios = []
        n_conf = 0
        for i in range(n_pl):
            j = perm_assign[i]
            d = dmat[i][j]
            others = sorted(dmat[i][jj] for jj in range(n_v) if jj != j)
            second_d = others[0] if others else d
            ratio = second_d / d if d > 0.01 else 1.0
            ratios.append(ratio)
            if ratio > 1.15:
                n_conf += 1
        perm_ratios.append(sum(ratios) / len(ratios))
        perm_confident.append(n_conf)

    # Compute p-values (fraction of permutations as good or better)
    p_distance = sum(1 for d in perm_distances if d <= real_distance) / n_perm
    p_ratio = sum(1 for r in perm_ratios if r >= real_ratio) / n_perm
    p_confident = sum(1 for c in perm_confident if c >= real_confident) / n_perm

    return {
        'real_mean_ratio': round(real_ratio, 4),
        'real_n_confident': real_confident,
        'real_mean_distance': round(real_distance, 4),
        'perm_mean_ratio_mean': round(sum(perm_ratios) / n_perm, 4),
        'perm_mean_confident_mean': round(sum(perm_confident) / n_perm, 2),
        'perm_mean_distance_mean': round(sum(perm_distances) / n_perm, 4),
        'p_ratio': round(p_ratio, 4),
        'p_confident': round(p_confident, 4),
        'p_distance': round(p_distance, 4),
        'n_perm': n_perm,
        'percentile_ratio': round(100 * (1 - p_ratio), 1),
        'percentile_confident': round(100 * (1 - p_confident), 1),
    }
