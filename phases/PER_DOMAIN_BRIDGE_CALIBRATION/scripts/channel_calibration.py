"""
Phase 627 · Script 2 (CORE): Per-HEAD-channel calibration.

Compares pseudo-Lull (PL) per-chapter operational features to Voynich B-side
HEAD-channel features, mediated by REGIME grouping.  Seven tasks (T1-T7) test
structural correspondence, per-channel family contrast, k-triangulation with
Brunschwig, e-channel recovery calibration, channel independence, and negative
controls.

Input:
  - Script 1 output:   phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/pl_channel_features.json
  - Bridge decomp:     phases/A_TO_B_BRIDGE_DECOMPOSITION/results/bridge_decomposition.json
  - Operational profs:  results/folio_operational_profiles.json
  - REGIME mapping:     data/regime_folio_mapping.json
  - Deployment feats:   phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t1b_deployment_features.json
  - Brunschwig profs:   results/brunschwig_operational_profiles.json
  - PL structural prof: phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json

Output:
  phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/channel_calibration.json
"""

import sys, time, json, math, re
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared_627 import (
    PROJECT_ROOT, PHASE_DIR, RESULTS_DIR,
    N_PERM, RNG,
    HEAT_INTENSITY, FIRE_DEGREE_REGIME,
    load_pl_structural_profile, load_pl_channel_features,
    load_bridge_decomposition,
    load_b_operational_profiles, load_regime_mapping,
    load_b_deployment_features, load_brunschwig_profiles,
    compute_folio_head_channel_profile, compute_regime_head_profiles,
    get_folio_section, get_herbal_folios, get_stars_folios,
    spearman_rank, kruskal_wallis, mann_whitney_u,
    mantel_test, euclidean_dist, pairwise_upper_triangle,
    bonferroni_threshold, round_floats, _pearson,
)

# ============================================================
# Constants
# ============================================================

SCRIPT_NAME = "channel_calibration.py"
OUTPUT_PATH = RESULTS_DIR / "channel_calibration.json"

# HEAD channel features from operational profiles
HEAD_FEATURES = [
    'k_ratio', 'e_ratio', 'h_ratio',
    'thermo_ke', 'thermo_kch',
    'iteration_rate', 'checkpoint_rate', 'terminal_rate',
]

# Per-channel feature groupings (T3)
CHANNEL_FEATURES = {
    'k_channel': ['k_ratio', 'thermo_ke'],
    'h_channel': ['h_ratio', 'checkpoint_rate'],
    'e_channel': ['e_ratio', 'thermo_kch'],
    't_channel': ['terminal_rate', 'iteration_rate'],
}

# PL operational feature names (from structural profile / Script 1)
PL_FEATURES_6D = [
    'heat_rate', 'monitoring_rate', 'correction_rate',
    'termination_rate', 'chain_rate', 'mean_heat_intensity',
]

# PL -> V channel mapping for structural correspondence
PL_TO_V_MAP = {
    'heat_rate': 'k_ratio',
    'monitoring_rate': 'h_ratio',
    'correction_rate': 'e_ratio',
    'termination_rate': 'checkpoint_rate',
}

# Family -> REGIME mapping (from C1749)
FAMILY_REGIME_MAP = {
    'distillation': 'REGIME_1',
    'sublimation': 'REGIME_3',
    'fixation': 'REGIME_4',
    'dissolution': 'REGIME_2',
}

REGIME_ORDINAL = {'REGIME_1': 1, 'REGIME_2': 2, 'REGIME_3': 3, 'REGIME_4': 4}

# ============================================================
# Helpers
# ============================================================

def chapter_length(ch: dict) -> int:
    """English line count for a PL chapter."""
    return max(ch.get('en_line_end', 0) - ch.get('en_line_start', 0), 1)


def chapter_to_features(ch: dict, channel_data: dict = None) -> dict:
    """Build 6D feature vector for a PL chapter.

    Tries Script 1 channel data first; falls back to structural profile counts.
    """
    n_lines = chapter_length(ch)
    ch_key = f"{ch.get('part', '')}_{ch.get('number', '')}_{ch.get('page', '')}"

    # Try Script 1 channel data
    if channel_data and ch_key in channel_data:
        cd = channel_data[ch_key]
        return {
            'heat_rate': cd.get('heat_rate', 0.0),
            'monitoring_rate': cd.get('monitoring_rate', 0.0),
            'correction_rate': cd.get('correction_rate', 0.0),
            'termination_rate': cd.get('termination_rate', 0.0),
            'chain_rate': cd.get('chain_rate', 0.0),
            'mean_heat_intensity': cd.get('mean_heat_intensity', 0.0),
        }

    # Fall back to structural profile counts -> rates
    heat_rate = ch.get('heat_count', 0) / n_lines
    monitoring_rate = ch.get('monitoring_count', 0) / n_lines
    correction_rate = ch.get('correction_count', 0) / n_lines
    termination_rate = ch.get('termination_count', 0) / n_lines
    chain_rate = ch.get('chain_count', 0) / n_lines
    # mean_heat_intensity: approximate from family
    fam = ch.get('primary_family', '')
    intensity_by_family = {
        'distillation': 4.0, 'sublimation': 5.0, 'fixation': 3.0,
        'dissolution': 2.5, 'calcination': 6.0, 'fermentation': 2.0,
        'circulation': 3.5, 'separation': 3.0, 'coagulation': 3.0,
        'imbibition': 2.0, 'theoretical': 1.5, 'furnace_apparatus': 4.5,
        'unclassified': 2.5,
    }
    mean_heat_intensity = intensity_by_family.get(fam, 2.5) if heat_rate > 0 else 0.0

    return {
        'heat_rate': heat_rate,
        'monitoring_rate': monitoring_rate,
        'correction_rate': correction_rate,
        'termination_rate': termination_rate,
        'chain_rate': chain_rate,
        'mean_heat_intensity': mean_heat_intensity,
    }


def load_script1_channel_data() -> dict:
    """Load Script 1 output, returning per-chapter channel data keyed by chapter key.

    Returns empty dict if file not found (fallback to structural profile).
    """
    path = RESULTS_DIR / 'pl_channel_features.json'
    if not path.exists():
        print(f"  [WARN] Script 1 output not found: {path}")
        print(f"  [WARN] Falling back to structural profile counts for PL features.")
        return {}
    with open(path) as f:
        data = json.load(f)

    # Script 1 stores per-chapter data -- build lookup by chapter key
    result = {}
    chapters = data.get('T5_channel_signatures', data.get('chapters', {}))
    if isinstance(chapters, dict):
        for key, vals in chapters.items():
            result[key] = vals
    elif isinstance(chapters, list):
        for ch in chapters:
            key = ch.get('chapter_key', '')
            result[key] = ch
    return result


def zscore_columns(matrix: list, n_features: int) -> list:
    """Z-score standardize each feature column in a list of feature vectors."""
    if not matrix:
        return matrix
    n = len(matrix)
    result = [list(row) for row in matrix]
    for j in range(n_features):
        vals = [matrix[i][j] for i in range(n)]
        mu = sum(vals) / n
        var = sum((v - mu) ** 2 for v in vals) / n
        sd = math.sqrt(var) if var > 1e-12 else 1.0
        for i in range(n):
            result[i][j] = (matrix[i][j] - mu) / sd
    return result


def upper_triangle_dists(matrix: list) -> list:
    """Compute flat upper-triangle Euclidean distance matrix."""
    n = len(matrix)
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            dists.append(euclidean_dist(matrix[i], matrix[j]))
    return dists


def rank_vector(vals: list) -> list:
    """Compute ranks (1-based, averaged ties) for a list of values."""
    n = len(vals)
    indexed = sorted(enumerate(vals), key=lambda iv: iv[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for idx in range(i, j + 1):
            ranks[indexed[idx][0]] = avg_rank
        i = j + 1
    return ranks


def rank_rank_corr_matrix(data_dict: dict, feature_names: list) -> list:
    """Build n×n rank-rank correlation matrix for features.

    data_dict: {item_id: {feature_name: value}}
    Returns flat upper-triangle of the feature-feature correlation matrix.
    """
    items = sorted(data_dict.keys())
    n_feat = len(feature_names)
    # Compute rank vectors per feature
    rank_vecs = {}
    for feat in feature_names:
        vals = [data_dict[item].get(feat, 0.0) for item in items]
        rank_vecs[feat] = rank_vector(vals)

    # Build n_feat × n_feat correlation matrix, return upper triangle
    upper_tri = []
    for i in range(n_feat):
        for j in range(i + 1, n_feat):
            r = _pearson(rank_vecs[feature_names[i]], rank_vecs[feature_names[j]])
            upper_tri.append(r)
    return upper_tri


def mean_val(vals: list) -> float:
    """Safe mean."""
    return sum(vals) / len(vals) if vals else 0.0


# ============================================================
# T1: V-side HEAD-channel profile construction
# ============================================================

def task_t1(op_profiles, regime_map):
    """Build per-folio, per-REGIME, and within-Herbal HEAD-channel profiles."""
    print("  T1: V-side HEAD-channel profile construction...")

    # Per-folio profiles
    folio_profiles = {}
    for folio in regime_map:
        prof = compute_folio_head_channel_profile(folio, op_profiles)
        if prof:
            folio_profiles[folio] = prof

    # Per-REGIME mean profiles
    regime_profiles = compute_regime_head_profiles(op_profiles, regime_map)

    # Within-Herbal subset
    herbal_map = get_herbal_folios(regime_map)
    herbal_profiles = compute_regime_head_profiles(op_profiles, herbal_map)
    n_herbal = len(herbal_map)

    print(f"    {len(folio_profiles)} folio profiles, {n_herbal} herbal folios")

    return {
        'n_folios': len(folio_profiles),
        'n_herbal': n_herbal,
        'regime_profiles': regime_profiles,
        'herbal_regime_profiles': herbal_profiles,
    }, folio_profiles


# ============================================================
# T2: Within-family distance correspondence (P3)
# ============================================================

def task_t2(pl_chapters, channel_data, folio_profiles, regime_map):
    """Structural correspondence test: PL distillation internal structure
    vs V REGIME_1 internal structure, via Mantel on 4x4 correlation matrices."""
    print("  T2: Within-family distance correspondence (P3)...")

    # --- PL distillation chapters ---
    dist_chapters = [ch for ch in pl_chapters if ch.get('primary_family') == 'distillation']
    pl_dist_features = {}
    for i, ch in enumerate(dist_chapters):
        feats = chapter_to_features(ch, channel_data)
        ch_id = f"dist_{i}"
        pl_dist_features[ch_id] = feats

    # --- V REGIME_1 folios ---
    r1_folios = {f: folio_profiles[f] for f in regime_map
                 if regime_map[f] == 'REGIME_1' and f in folio_profiles}

    # --- Build 4x4 structural matrices ---
    pl_feature_names = list(PL_TO_V_MAP.keys())    # 4 PL features
    v_feature_names = list(PL_TO_V_MAP.values())    # 4 V features

    pl_struct = rank_rank_corr_matrix(pl_dist_features, pl_feature_names)
    v_struct = rank_rank_corr_matrix(r1_folios, v_feature_names)

    # Mantel test on 4x4 upper triangles (6 elements each)
    mantel_r, mantel_p = mantel_test(pl_struct, v_struct, n_perm=N_PERM)

    # --- Null N1: Theorica chapters ---
    theo_chapters = [ch for ch in pl_chapters if ch.get('primary_family') == 'theoretical']
    theo_features = {}
    for i, ch in enumerate(theo_chapters):
        feats = chapter_to_features(ch, channel_data)
        theo_features[f"theo_{i}"] = feats
    theo_struct = rank_rank_corr_matrix(theo_features, pl_feature_names)
    null_theo_r, _ = mantel_test(theo_struct, v_struct, n_perm=N_PERM)

    # --- Null N2: Shuffle PL family labels ---
    shuffled_rs = []
    dist_ids = list(pl_dist_features.keys())
    for _ in range(100):
        shuffled_feats = {}
        shuffled_ids = dist_ids[:]
        RNG.shuffle(shuffled_ids)
        for new_id, orig_id in zip(dist_ids, shuffled_ids):
            # Shuffle feature assignments across chapters
            orig_feats = pl_dist_features[orig_id]
            feat_keys = list(orig_feats.keys())
            RNG.shuffle(feat_keys)
            shuffled_feats[new_id] = {k: orig_feats[fk] for k, fk in zip(
                list(orig_feats.keys()), feat_keys)}
        shuf_struct = rank_rank_corr_matrix(shuffled_feats, pl_feature_names)
        r, _ = mantel_test(shuf_struct, v_struct, n_perm=50)
        shuffled_rs.append(r)
    null_shuffled_r = mean_val(shuffled_rs)

    # --- Null N3: Random PL chapter selection ---
    random_rs = []
    all_non_dist = [ch for ch in pl_chapters if ch.get('primary_family') != 'distillation']
    for _ in range(100):
        sample = RNG.sample(all_non_dist, min(len(dist_chapters), len(all_non_dist)))
        rand_feats = {}
        for i, ch in enumerate(sample):
            rand_feats[f"rand_{i}"] = chapter_to_features(ch, channel_data)
        rand_struct = rank_rank_corr_matrix(rand_feats, pl_feature_names)
        r, _ = mantel_test(rand_struct, v_struct, n_perm=50)
        random_rs.append(r)
    null_random_r = mean_val(random_rs)

    p3_pass = mantel_r > 0.20 and mantel_p < 0.05

    print(f"    PL distillation: {len(dist_chapters)} chapters")
    print(f"    V REGIME_1: {len(r1_folios)} folios")
    print(f"    Structural Mantel r={mantel_r:.4f}, p={mantel_p:.4f}")
    print(f"    Null Theorica r={null_theo_r:.4f}, Shuffled r={null_shuffled_r:.4f}, "
          f"Random r={null_random_r:.4f}")
    print(f"    P3: {'PASS' if p3_pass else 'FAIL'}")

    return {
        'pl_distillation_n': len(dist_chapters),
        'v_regime1_n': len(r1_folios),
        'structural_mantel_r': mantel_r,
        'structural_mantel_p': mantel_p,
        'null_theorica_r': null_theo_r,
        'null_shuffled_r': null_shuffled_r,
        'null_random_r': null_random_r,
        'P3_pass': p3_pass,
    }


# ============================================================
# T3: Per-channel family contrast (P1)
# ============================================================

def task_t3(folio_profiles, regime_map, op_profiles):
    """KW test across 4 REGIMEs per HEAD-channel feature, with within-Herbal replication."""
    print("  T3: Per-channel family contrast (P1)...")

    herbal_map = get_herbal_folios(regime_map)
    n_tests = sum(len(feats) for feats in CHANNEL_FEATURES.values())  # 8
    bonf_alpha = bonferroni_threshold(0.05, n_tests)

    result = {}
    any_k_pass = False

    for channel_name, feat_names in CHANNEL_FEATURES.items():
        ch_result = {'features': {}}

        for feat in feat_names:
            # Full-sample KW
            groups_full = defaultdict(list)
            for folio, regime in regime_map.items():
                if folio in folio_profiles:
                    val = folio_profiles[folio].get(feat, 0.0)
                    groups_full[regime].append(val)

            kw_H, kw_p = kruskal_wallis(dict(groups_full))

            # Within-Herbal KW
            groups_herbal = defaultdict(list)
            for folio, regime in herbal_map.items():
                if folio in folio_profiles:
                    val = folio_profiles[folio].get(feat, 0.0)
                    groups_herbal[regime].append(val)

            herb_H, herb_p = kruskal_wallis(dict(groups_herbal))

            # Per-REGIME means
            regime_means = {}
            for regime in sorted(groups_full.keys()):
                regime_means[regime] = mean_val(groups_full[regime])

            # Spearman with REGIME ordinal
            folio_vals = []
            folio_ordinals = []
            for folio, regime in regime_map.items():
                if folio in folio_profiles:
                    folio_vals.append(folio_profiles[folio].get(feat, 0.0))
                    folio_ordinals.append(REGIME_ORDINAL.get(regime, 0))
            rho, rho_p = spearman_rank(folio_ordinals, folio_vals)

            # Distillation (R1) vs rest Mann-Whitney
            r1_vals = groups_full.get('REGIME_1', [])
            rest_vals = []
            for r in ['REGIME_2', 'REGIME_3', 'REGIME_4']:
                rest_vals.extend(groups_full.get(r, []))
            dist_U, dist_p = mann_whitney_u(r1_vals, rest_vals)

            ch_result['features'][feat] = {
                'full_kw_H': kw_H,
                'full_kw_p': kw_p,
                'herbal_kw_H': herb_H,
                'herbal_kw_p': herb_p,
                'regime_means': regime_means,
                'rho': rho,
                'rho_p': rho_p,
                'dist_vs_rest_U': dist_U,
                'dist_vs_rest_p': dist_p,
            }

        # Channel-level summary: use primary feature
        primary_feat = feat_names[0]
        pf = ch_result['features'][primary_feat]
        ch_result['full_kw_H'] = pf['full_kw_H']
        ch_result['full_kw_p'] = pf['full_kw_p']
        ch_result['herbal_kw_H'] = pf['herbal_kw_H']
        ch_result['herbal_kw_p'] = pf['herbal_kw_p']
        ch_result['regime_means'] = pf['regime_means']
        ch_result['rho'] = pf['rho']
        ch_result['rho_p'] = pf['rho_p']
        ch_result['dist_vs_rest_U'] = pf['dist_vs_rest_U']
        ch_result['dist_vs_rest_p'] = pf['dist_vs_rest_p']

        # P1 check: k-channel rho > 0.35 and within-Herbal KW p < 0.05
        if channel_name == 'k_channel':
            any_k_pass = (pf['rho'] > 0.35 and pf['herbal_kw_p'] < 0.05)

        result[channel_name] = ch_result

        print(f"    {channel_name}: KW H={pf['full_kw_H']:.2f} p={pf['full_kw_p']:.4f}, "
              f"Herbal KW p={pf['herbal_kw_p']:.4f}, rho={pf['rho']:.4f}")

    result['P1_pass'] = any_k_pass
    result['bonferroni_alpha'] = bonf_alpha

    print(f"    P1 (k-channel rho>0.35 & herbal p<0.05): {'PASS' if any_k_pass else 'FAIL'}")
    return result


# ============================================================
# T4: k-channel triangulation with Brunschwig (P4)
# ============================================================

def task_t4(regime_profiles, herbal_regime_profiles, brunschwig_recipes, pl_chapters, channel_data):
    """Test ordering agreement between fire_degree, PL heat intensity, and V k_ratio."""
    print("  T4: k-channel triangulation with Brunschwig (P4)...")

    # Brunschwig fire_degree per REGIME -> mean fire degree
    regime_fire = defaultdict(list)
    for recipe in brunschwig_recipes:
        fd = recipe.get('fire_degree', 0)
        if fd == 0:
            continue
        regime = FIRE_DEGREE_REGIME.get(fd)
        if regime:
            regime_fire[regime].append(fd)

    brunschwig_regime_means = {r: mean_val(vals) for r, vals in regime_fire.items()}

    # V k_ratio per REGIME
    regime_k_means = {}
    for regime, prof in regime_profiles.items():
        regime_k_means[regime] = prof.get('k_ratio', 0.0)

    # PL distillation chapters: group by heat intensity
    dist_chapters = [ch for ch in pl_chapters if ch.get('primary_family') == 'distillation']
    pl_groups = {'low': [], 'medium': [], 'high': []}
    for ch in dist_chapters:
        feats = chapter_to_features(ch, channel_data)
        hi = feats.get('mean_heat_intensity', 0.0)
        if hi <= 2:
            pl_groups['low'].append(hi)
        elif hi <= 4:
            pl_groups['medium'].append(hi)
        else:
            pl_groups['high'].append(hi)

    pl_intensity_means = {g: mean_val(vals) for g, vals in pl_groups.items()}

    # Ordering agreement:
    # Fire degree ordering: R2 < R1 < R3 < R4 (fire degrees 1,2,3,4)
    # Check if k_ratio shows a consistent ordering with fire degree
    regimes_ordered = ['REGIME_2', 'REGIME_1', 'REGIME_3', 'REGIME_4']
    fire_order = [brunschwig_regime_means.get(r, 0.0) for r in regimes_ordered]
    k_order = [regime_k_means.get(r, 0.0) for r in regimes_ordered]

    # Spearman between fire degree ordering and k_ratio ordering
    rho_fire_k, rho_p = spearman_rank(fire_order, k_order)
    ordering_agreement = rho_fire_k > 0.0  # Positive correlation = agreement

    # Within-Herbal replication
    herbal_k_means = {}
    for regime, prof in herbal_regime_profiles.items():
        herbal_k_means[regime] = prof.get('k_ratio', 0.0)

    herbal_k_order = [herbal_k_means.get(r, 0.0) for r in regimes_ordered]
    rho_herbal, _ = spearman_rank(fire_order, herbal_k_order)
    herbal_agreement = rho_herbal > 0.0

    p4_pass = ordering_agreement and herbal_agreement

    print(f"    Brunschwig fire degree per REGIME: {brunschwig_regime_means}")
    print(f"    V k_ratio per REGIME: {regime_k_means}")
    print(f"    Fire-k Spearman rho={rho_fire_k:.4f}, p={rho_p:.4f}")
    print(f"    Herbal rho={rho_herbal:.4f}")
    print(f"    P4: {'PASS' if p4_pass else 'FAIL'}")

    return {
        'regime_k_means': regime_k_means,
        'brunschwig_ordering': regimes_ordered,
        'brunschwig_regime_fire_means': brunschwig_regime_means,
        'pl_intensity_groups': pl_intensity_means,
        'fire_k_rho': rho_fire_k,
        'fire_k_p': rho_p,
        'herbal_k_rho': rho_herbal,
        'ordering_agreement': ordering_agreement,
        'herbal_agreement': herbal_agreement,
        'P4_pass': p4_pass,
    }


# ============================================================
# T5: e-channel recovery calibration (P2)
# ============================================================

def task_t5(pl_chapters, channel_data, regime_profiles, folio_profiles, regime_map):
    """PL family correction_rate ranking vs V REGIME e_ratio ranking."""
    print("  T5: e-channel recovery calibration (P2)...")

    # PL per-family mean correction_rate
    family_correction = defaultdict(list)
    for ch in pl_chapters:
        fam = ch.get('primary_family', '')
        if fam in FAMILY_REGIME_MAP:
            feats = chapter_to_features(ch, channel_data)
            family_correction[fam].append(feats.get('correction_rate', 0.0))

    pl_family_means = {fam: mean_val(vals) for fam, vals in family_correction.items()}

    # V per-REGIME mean e_ratio and thermo_kch
    regime_e_means = {}
    regime_thermo_kch = {}
    for regime, prof in regime_profiles.items():
        regime_e_means[regime] = prof.get('e_ratio', 0.0)
        regime_thermo_kch[regime] = prof.get('thermo_kch', 0.0)

    # Spearman: PL family correction_rate ranking vs V REGIME e_ratio ranking
    # Using FAMILY_REGIME_MAP to pair them
    families_ordered = sorted(FAMILY_REGIME_MAP.keys())
    pl_corr_vals = [pl_family_means.get(f, 0.0) for f in families_ordered]
    v_e_vals = [regime_e_means.get(FAMILY_REGIME_MAP[f], 0.0) for f in families_ordered]
    rho_corr_e, rho_p = spearman_rank(pl_corr_vals, v_e_vals)

    # Within-Stars replication (Stars folios f103-f116)
    stars_folios = get_stars_folios(regime_map)
    stars_r1 = [folio_profiles[f].get('e_ratio', 0.0)
                for f in stars_folios if regime_map.get(f) == 'REGIME_1' and f in folio_profiles]
    stars_r3 = [folio_profiles[f].get('e_ratio', 0.0)
                for f in stars_folios if regime_map.get(f) == 'REGIME_3' and f in folio_profiles]

    stars_U, stars_p = mann_whitney_u(stars_r1, stars_r3)

    p2_pass = rho_p < 0.10  # Lenient for n=4 pairs

    print(f"    PL family correction rates: {pl_family_means}")
    print(f"    V REGIME e_ratio: {regime_e_means}")
    print(f"    Spearman rho={rho_corr_e:.4f}, p={rho_p:.4f}")
    print(f"    Stars R1 vs R3 e_ratio: U={stars_U:.1f}, p={stars_p:.4f} "
          f"(n_R1={len(stars_r1)}, n_R3={len(stars_r3)})")
    print(f"    P2: {'PASS' if p2_pass else 'FAIL'}")

    return {
        'pl_family_correction_rates': pl_family_means,
        'regime_e_means': regime_e_means,
        'regime_thermo_kch': regime_thermo_kch,
        'corr_e_rho': rho_corr_e,
        'corr_e_p': rho_p,
        'stars_comparison': {
            'R1_mean': mean_val(stars_r1) if stars_r1 else None,
            'R3_mean': mean_val(stars_r3) if stars_r3 else None,
            'R1_n': len(stars_r1),
            'R3_n': len(stars_r3),
            'U': stars_U,
            'p': stars_p,
        },
        'P2_pass': p2_pass,
    }


# ============================================================
# T6: Channel independence (P5)
# ============================================================

def task_t6(pl_chapters, channel_data, regime_profiles):
    """Cross-feature-to-channel Spearman matrix via REGIME mediation."""
    print("  T6: Channel independence (P5)...")

    pl_feature_names = ['heat_rate', 'monitoring_rate', 'correction_rate',
                        'termination_rate', 'chain_rate']
    v_feature_names = ['k_ratio', 'h_ratio', 'e_ratio', 'checkpoint_rate']

    # PL per-family means (4 families mapped to 4 REGIMEs)
    families = sorted(FAMILY_REGIME_MAP.keys())
    pl_family_features = {fam: defaultdict(list) for fam in families}

    for ch in pl_chapters:
        fam = ch.get('primary_family', '')
        if fam in families:
            feats = chapter_to_features(ch, channel_data)
            for feat_name in pl_feature_names:
                pl_family_features[fam][feat_name].append(feats.get(feat_name, 0.0))

    # Compute PL per-family mean per feature
    pl_regime_features = {}  # regime -> {feat: mean}
    for fam in families:
        regime = FAMILY_REGIME_MAP[fam]
        pl_regime_features[regime] = {}
        for feat_name in pl_feature_names:
            vals = pl_family_features[fam][feat_name]
            pl_regime_features[regime][feat_name] = mean_val(vals)

    # V per-REGIME means already in regime_profiles

    # Build 5x4 cross-matrix: for each (PL_feat, V_feat) pair, Spearman across 4 REGIMEs
    regimes_ordered = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    cross_matrix = {}

    # Expected diagonal mapping
    expected_diagonal = {
        'heat_rate': 'k_ratio',
        'monitoring_rate': 'h_ratio',
        'correction_rate': 'e_ratio',
        'termination_rate': 'checkpoint_rate',
    }

    off_diag_abs = []

    for pl_feat in pl_feature_names:
        pl_vals = [pl_regime_features.get(r, {}).get(pl_feat, 0.0) for r in regimes_ordered]

        for v_feat in v_feature_names:
            v_vals = [regime_profiles.get(r, {}).get(v_feat, 0.0) for r in regimes_ordered]
            rho, _ = spearman_rank(pl_vals, v_vals)
            key = f"{pl_feat}->{v_feat}"
            cross_matrix[key] = rho

            # Track off-diagonal
            if expected_diagonal.get(pl_feat) != v_feat:
                off_diag_abs.append(abs(rho))

    mean_off_diag = mean_val(off_diag_abs) if off_diag_abs else 0.0

    # Also include chain_rate -> all V features as off-diagonal
    # (chain_rate has no expected V counterpart, all pairings are off-diagonal)

    p5_pass = mean_off_diag < 0.15

    # Print diagonal values
    for pl_feat, v_feat in expected_diagonal.items():
        key = f"{pl_feat}->{v_feat}"
        print(f"    DIAGONAL {key}: rho={cross_matrix.get(key, 0.0):.4f}")
    print(f"    Mean |off-diagonal rho|: {mean_off_diag:.4f}")
    print(f"    P5: {'PASS' if p5_pass else 'FAIL'}")

    return {
        'cross_matrix': cross_matrix,
        'mean_off_diagonal_abs_rho': mean_off_diag,
        'P5_pass': p5_pass,
    }


# ============================================================
# T7: Negative controls (P6, P7)
# ============================================================

def task_t7(pl_chapters, channel_data, regime_profiles, folio_profiles, regime_map):
    """Negative controls: Theorica chapters (P6) and chapter length (P7)."""
    print("  T7: Negative controls (P6, P7)...")

    v_features_test = ['k_ratio', 'h_ratio', 'e_ratio', 'checkpoint_rate']
    regimes_ordered = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

    # ---- P6: Theorica chapters ----
    # Theorica chapters have no REGIME mapping. Split into 4 quartiles by
    # operational_density and test whether these correlate with V REGIME means.
    theo_chapters = [ch for ch in pl_chapters if ch.get('primary_family') == 'theoretical']
    theo_chapters_sorted = sorted(theo_chapters, key=lambda c: c.get('operational_density', 0.0))
    n_theo = len(theo_chapters_sorted)
    q_size = n_theo // 4

    # Build quartile groups
    quartile_features = {}
    for qi in range(4):
        start = qi * q_size
        end = start + q_size if qi < 3 else n_theo
        qchapters = theo_chapters_sorted[start:end]
        feat_accum = defaultdict(list)
        for ch in qchapters:
            feats = chapter_to_features(ch, channel_data)
            for fn in ['heat_rate', 'monitoring_rate', 'correction_rate', 'termination_rate']:
                feat_accum[fn].append(feats.get(fn, 0.0))
        quartile_features[f"Q{qi+1}"] = {fn: mean_val(vals) for fn, vals in feat_accum.items()}

    # Test: Spearman between Theorica quartile means and V REGIME means
    # Map Q1->R1, Q2->R2, Q3->R3, Q4->R4 (arbitrary mapping)
    q_names = ['Q1', 'Q2', 'Q3', 'Q4']

    pl_to_v_test = {
        'heat_rate': 'k_ratio',
        'monitoring_rate': 'h_ratio',
        'correction_rate': 'e_ratio',
        'termination_rate': 'checkpoint_rate',
    }

    theorica_results = {}
    all_ns = True
    n_tested = 0

    for pl_feat, v_feat in pl_to_v_test.items():
        pl_vals = [quartile_features[q].get(pl_feat, 0.0) for q in q_names]
        v_vals = [regime_profiles.get(r, {}).get(v_feat, 0.0) for r in regimes_ordered]
        rho, p = spearman_rank(pl_vals, v_vals)
        theorica_results[f"{pl_feat}->{v_feat}"] = {'rho': rho, 'p': p}
        n_tested += 1
        if p < 0.10:
            all_ns = False

    p6_pass = all_ns

    print(f"    P6 (Theorica): {n_tested} features tested, all NS={all_ns}")
    for key, val in theorica_results.items():
        print(f"      {key}: rho={val['rho']:.4f}, p={val['p']:.4f}")

    # ---- P7: Chapter length vs V HEAD features ----
    # PL per-family mean chapter length
    families = sorted(FAMILY_REGIME_MAP.keys())
    family_lengths = defaultdict(list)
    for ch in pl_chapters:
        fam = ch.get('primary_family', '')
        if fam in families:
            family_lengths[fam].append(chapter_length(ch))

    family_mean_lengths = {fam: mean_val(vals) for fam, vals in family_lengths.items()}

    # Spearman: family mean length (ordered by REGIME) vs V per-REGIME HEAD features
    length_vals = [family_mean_lengths.get(fam, 0.0) for fam in families]
    # Map families to REGIMEs
    regime_for_fam = [FAMILY_REGIME_MAP[fam] for fam in families]

    length_results = {}
    all_length_ns = True

    for v_feat in v_features_test:
        v_vals = [regime_profiles.get(FAMILY_REGIME_MAP[fam], {}).get(v_feat, 0.0)
                  for fam in families]
        rho, p = spearman_rank(length_vals, v_vals)
        length_results[v_feat] = {'rho': rho, 'p': p}
        if p < 0.10:
            all_length_ns = False

    p7_pass = all_length_ns

    print(f"    P7 (Chapter length): all NS={all_length_ns}")
    for key, val in length_results.items():
        print(f"      length->{key}: rho={val['rho']:.4f}, p={val['p']:.4f}")
    print(f"    P6: {'PASS' if p6_pass else 'FAIL'}")
    print(f"    P7: {'PASS' if p7_pass else 'FAIL'}")

    return {
        'theorica_test': {
            'features_tested': n_tested,
            'results': theorica_results,
            'all_ns': all_ns,
        },
        'chapter_length': {
            'family_mean_lengths': family_mean_lengths,
            'rho_values': length_results,
            'all_ns': all_length_ns,
        },
        'P6_pass': p6_pass,
        'P7_pass': p7_pass,
    }


# ============================================================
# Main
# ============================================================

def main():
    t0 = time.time()
    print(f"[{SCRIPT_NAME}] Phase 627 Script 2: Per-HEAD-channel calibration")
    print(f"{'=' * 70}")

    # Load data
    print("Loading data...")
    pl_profile = load_pl_structural_profile()
    pl_chapters = pl_profile['E1_chapters']
    channel_data = load_script1_channel_data()
    op_profiles = load_b_operational_profiles()
    regime_map = load_regime_mapping()
    brunschwig_recipes = load_brunschwig_profiles()

    print(f"  PL chapters: {len(pl_chapters)}")
    print(f"  V folios: {len(regime_map)}")
    print(f"  Brunschwig recipes: {len(brunschwig_recipes)}")
    print(f"  Script 1 channel data: {'loaded' if channel_data else 'fallback to structural profile'}")
    print()

    # T1
    t1_result, folio_profiles = task_t1(op_profiles, regime_map)
    print()

    # T2
    t2_result = task_t2(pl_chapters, channel_data, folio_profiles, regime_map)
    print()

    # T3
    t3_result = task_t3(folio_profiles, regime_map, op_profiles)
    print()

    # T4
    t4_result = task_t4(
        t1_result['regime_profiles'],
        t1_result['herbal_regime_profiles'],
        brunschwig_recipes, pl_chapters, channel_data,
    )
    print()

    # T5
    t5_result = task_t5(pl_chapters, channel_data,
                        t1_result['regime_profiles'],
                        folio_profiles, regime_map)
    print()

    # T6
    t6_result = task_t6(pl_chapters, channel_data, t1_result['regime_profiles'])
    print()

    # T7
    t7_result = task_t7(pl_chapters, channel_data,
                        t1_result['regime_profiles'],
                        folio_profiles, regime_map)
    print()

    elapsed = time.time() - t0

    # Assemble output
    output = {
        'metadata': {
            'phase': 627,
            'script': 2,
            'name': 'channel_calibration',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'elapsed_s': elapsed,
            'script1_channel_data': bool(channel_data),
        },
        'T1_v_profiles': t1_result,
        'T2_within_family_distance': t2_result,
        'T3_per_channel_contrast': t3_result,
        'T4_k_triangulation': t4_result,
        'T5_e_channel': t5_result,
        'T6_channel_independence': t6_result,
        'T7_negative_controls': t7_result,
    }

    output = round_floats(output)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"{'=' * 70}")
    print(f"[{SCRIPT_NAME}] Complete in {elapsed:.1f}s")
    print(f"  Output: {OUTPUT_PATH}")
    print()
    print("  PREDICTION SUMMARY:")
    print(f"    P1 (k-channel REGIME contrast):        {'PASS' if t3_result.get('P1_pass') else 'FAIL'}")
    print(f"    P2 (e-channel recovery calibration):    {'PASS' if t5_result.get('P2_pass') else 'FAIL'}")
    print(f"    P3 (within-family distance):            {'PASS' if t2_result.get('P3_pass') else 'FAIL'}")
    print(f"    P4 (k-channel Brunschwig triangulation):{'PASS' if t4_result.get('P4_pass') else 'FAIL'}")
    print(f"    P5 (channel independence):              {'PASS' if t6_result.get('P5_pass') else 'FAIL'}")
    print(f"    P6 (Theorica negative control):         {'PASS' if t7_result.get('P6_pass') else 'FAIL'}")
    print(f"    P7 (chapter length negative control):   {'PASS' if t7_result.get('P7_pass') else 'FAIL'}")


if __name__ == '__main__':
    main()
