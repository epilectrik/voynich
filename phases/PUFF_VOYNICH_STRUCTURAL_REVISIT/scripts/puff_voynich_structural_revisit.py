"""
Phase 490: Puff-Voynich Structural Revisit

Tests whether Voynich folio structural profiles differentiate by
plant material type, using Puff von Schrick's material categories
and blind PPC morphological classification of Voynich botanical
illustrations.

Three tests:
  D (PRIMARY): 8-category operational profile variance by material type
  A (SECONDARY): 5-apparatus profile distributional matching
  B (CONDITIONAL): Puff → Brunschwig degree → REGIME triangulation

All tests use permutation-based p-values (10,000 permutations),
Bonferroni-corrected threshold p < 0.0033, minimum effect size > 0.25.

Pre-registration: Folio assignments are written to JSON before any
test statistics are computed.
"""

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder

# ============================================================
# CONSTANTS
# ============================================================

RESULTS_DIR = PROJECT_ROOT / 'phases' / 'PUFF_VOYNICH_STRUCTURAL_REVISIT' / 'results'
N_PERMUTATIONS = 10000
BONFERRONI_THRESHOLD = 0.0033  # 0.01 / 3 tests
MIN_EFFECT_SIZE = 0.25
RANDOM_SEED = 490  # Phase number

# F-BRU-002: Brunschwig fire degree → Voynich REGIME
DEGREE_TO_REGIME = {1: 'REGIME_2', 2: 'REGIME_1', 3: 'REGIME_3'}
# REGIME_4 = precision axis (orthogonal to degree scale)

# 8 operational categories (C1250)
CATEGORIES_8 = ['THERMAL', 'FLOW', 'TRANSITION', 'OPERATION',
                'STAGING', 'CONTAINMENT', 'MARKING', 'MONITORING']

# 5 apparatus profiles (C1247-C1249)
APPARATUS_5 = ['DISTILLATION', 'SEALED_VESSEL', 'DIRECT_FIRE',
               'PRECISION', 'SUSTAINED_HEAT']

# ============================================================
# PRE-REGISTERED FOLIO ASSIGNMENTS
# ============================================================
# Source: phases/PPC_program_plant_correlation/plant_morphology_classification.md
# These are BLIND morphological classifications done WITHOUT reference
# to program metrics, product hypotheses, or structural data.
#
# Mapping PPC tags to Puff-compatible material types:
#   ROOT_HEAVY (primary) → ROOT
#   FLOWER_DOMINANT (primary) → FLOWER
#   LEAFY_HERB (primary) → HERB
#   COMPOSITE, WOODY_SHRUB → EXCLUDED (too few for group)
#
# Folios f57r, f66r, f66v are unclassified in PPC → EXCLUDED
#
# This mapping is PRE-REGISTERED: written to JSON before tests run.

FOLIO_ASSIGNMENTS = {
    # ROOT_DOMINATED (8 folios) — PPC primary tag: ROOT_HEAVY
    'f26r': 'ROOT', 'f26v': 'ROOT', 'f31r': 'ROOT', 'f34r': 'ROOT',
    'f39r': 'ROOT', 'f41v': 'ROOT', 'f43r': 'ROOT', 'f55v': 'ROOT',
    # FLOWER_DOMINATED (7 folios) — PPC primary tag: FLOWER_DOMINANT
    'f33r': 'FLOWER', 'f39v': 'FLOWER', 'f40r': 'FLOWER',
    'f40v': 'FLOWER', 'f46v': 'FLOWER', 'f50r': 'FLOWER', 'f50v': 'FLOWER',
    # LEAF_DOMINATED/HERB (6 folios) — PPC primary tag: LEAFY_HERB
    'f33v': 'HERB', 'f41r': 'HERB', 'f46r': 'HERB',
    'f48r': 'HERB', 'f48v': 'HERB', 'f55r': 'HERB',
}

# Excluded folios and reasons
EXCLUDED_FOLIOS = {
    'f34v': 'WOODY_SHRUB (only 1 folio, below minimum group size)',
    'f31v': 'COMPOSITE (ambiguous, 2 plants shown)',
    'f43v': 'COMPOSITE (ambiguous, multiple plant types)',
    'f57r': 'Not classified in PPC morphology study',
    'f66r': 'Not classified in PPC morphology study',
    'f66v': 'Not classified in PPC morphology study',
}

# ============================================================
# PRE-REGISTERED PREDICTIONS
# ============================================================

# Test D: Expected category profile directions by material type
# Based on Puff's processing descriptions:
#   FLOWER = gentle processing → more THERMAL monitoring, less vigorous OPERATION
#   HERB = standard processing → moderate across all categories
#   ROOT = vigorous preparation → more OPERATION and STAGING
PREDICTIONS_D = {
    'FLOWER': {'elevated': ['THERMAL'], 'reduced': ['OPERATION']},
    'HERB': {'elevated': [], 'reduced': []},  # baseline/moderate
    'ROOT': {'elevated': ['OPERATION', 'STAGING'], 'reduced': []},
}

# Test A: Expected apparatus profile directions by material type
# Based on Puff's material handling requirements:
#   FLOWER = delicate → high DISTILLATION, low DIRECT_FIRE
#   HERB = standard → moderate DISTILLATION
#   ROOT = vigorous → elevated SUSTAINED_HEAT + DIRECT_FIRE
PREDICTIONS_A = {
    'FLOWER': {'elevated': ['DISTILLATION'], 'reduced': ['DIRECT_FIRE']},
    'HERB': {'elevated': ['DISTILLATION'], 'reduced': []},
    'ROOT': {'elevated': ['SUSTAINED_HEAT', 'DIRECT_FIRE'], 'reduced': []},
}


# ============================================================
# DATA LOADING
# ============================================================

def load_puff_data():
    """Load Puff chapters with material categories."""
    path = PROJECT_ROOT / 'results' / 'puff_83_chapters.json'
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data['chapters']


def load_voynich_category_profiles():
    """Load per-folio 8-category profiles via BFolioDecoder."""
    decoder = BFolioDecoder()
    profiles = {}
    assigned_folios = set(FOLIO_ASSIGNMENTS.keys())

    for folio in assigned_folios:
        analysis = decoder.analyze_folio(folio)
        if analysis and analysis.category_profile:
            # Normalize to proportions
            total = sum(analysis.category_profile.values())
            if total > 0:
                profiles[folio] = {
                    cat: analysis.category_profile.get(cat, 0) / total
                    for cat in CATEGORIES_8
                }
            else:
                profiles[folio] = {cat: 0.0 for cat in CATEGORIES_8}

    return profiles


def load_apparatus_profiles():
    """Load per-folio 5-apparatus profiles from results."""
    path = (PROJECT_ROOT / 'phases' / 'APPARATUS_VOCABULARY_CLASSIFICATION' /
            'results' / 'apparatus_profiles.json')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    # Extract per-folio profiles (key is 'folio_scores')
    per_folio = data.get('folio_scores', {})
    profiles = {}
    for folio in FOLIO_ASSIGNMENTS:
        if folio in per_folio:
            profiles[folio] = {
                app: per_folio[folio].get(app, 0.0)
                for app in APPARATUS_5
            }

    return profiles


def load_regime_mapping():
    """Load REGIME assignments per folio."""
    path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    # Extract folio→regime mapping from regime_assignments dict
    regime_map = {}
    for folio, info in data.get('regime_assignments', {}).items():
        regime_map[folio] = info['regime']

    return regime_map


def load_brunschwig_degrees():
    """Load Brunschwig recipes, compute modal fire degree per material class."""
    path = PROJECT_ROOT / 'data' / 'brunschwig_curated_v3.json'
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    # Group fire degrees by material class
    degrees_by_class = defaultdict(list)
    for recipe in data.get('recipes', []):
        mat_class = recipe.get('material_class', '').lower()
        degree = recipe.get('fire_degree')
        if mat_class and degree is not None:
            degrees_by_class[mat_class].append(degree)

    # Compute modal degree per class
    modal_degrees = {}
    for mat_class, degrees in degrees_by_class.items():
        if degrees:
            counter = Counter(degrees)
            modal_degrees[mat_class] = counter.most_common(1)[0][0]

    return modal_degrees, degrees_by_class


# ============================================================
# STATISTICAL HELPERS
# ============================================================

def compute_group_profiles(assignments, folio_profiles, dimensions):
    """Compute mean profile vector per material-type group."""
    groups = defaultdict(list)
    for folio, mat_type in assignments.items():
        if folio in folio_profiles:
            groups[mat_type].append(folio_profiles[folio])

    group_means = {}
    for mat_type, profiles in groups.items():
        mean_vec = {}
        for dim in dimensions:
            values = [p[dim] for p in profiles]
            mean_vec[dim] = sum(values) / len(values) if values else 0
        group_means[mat_type] = mean_vec

    return group_means, groups


def pseudo_f_statistic(assignments, folio_profiles, dimensions):
    """
    Compute multivariate pseudo-F statistic.
    Between-group sum of squares / Within-group sum of squares,
    adjusted for degrees of freedom.
    """
    groups = defaultdict(list)
    for folio, mat_type in assignments.items():
        if folio in folio_profiles:
            groups[mat_type].append(folio_profiles[folio])

    if len(groups) < 2:
        return 0.0

    # Grand mean
    all_profiles = []
    for profiles in groups.values():
        all_profiles.extend(profiles)

    n_total = len(all_profiles)
    k = len(groups)

    if n_total <= k:
        return 0.0

    grand_mean = {}
    for dim in dimensions:
        grand_mean[dim] = sum(p[dim] for p in all_profiles) / n_total

    # Between-group SS
    ss_between = 0.0
    for mat_type, profiles in groups.items():
        n_g = len(profiles)
        group_mean = {}
        for dim in dimensions:
            group_mean[dim] = sum(p[dim] for p in profiles) / n_g
        for dim in dimensions:
            ss_between += n_g * (group_mean[dim] - grand_mean[dim]) ** 2

    # Within-group SS
    ss_within = 0.0
    for mat_type, profiles in groups.items():
        n_g = len(profiles)
        group_mean = {}
        for dim in dimensions:
            group_mean[dim] = sum(p[dim] for p in profiles) / n_g
        for profile in profiles:
            for dim in dimensions:
                ss_within += (profile[dim] - group_mean[dim]) ** 2

    if ss_within == 0:
        return float('inf')

    # F = (SS_between / (k-1)) / (SS_within / (n-k))
    f_stat = (ss_between / (k - 1)) / (ss_within / (n_total - k))
    return f_stat


def eta_squared(assignments, folio_profiles, dimensions):
    """Compute eta-squared (effect size) = SS_between / SS_total."""
    groups = defaultdict(list)
    for folio, mat_type in assignments.items():
        if folio in folio_profiles:
            groups[mat_type].append(folio_profiles[folio])

    all_profiles = []
    for profiles in groups.values():
        all_profiles.extend(profiles)

    n_total = len(all_profiles)
    if n_total == 0:
        return 0.0

    grand_mean = {}
    for dim in dimensions:
        grand_mean[dim] = sum(p[dim] for p in all_profiles) / n_total

    ss_total = 0.0
    for profile in all_profiles:
        for dim in dimensions:
            ss_total += (profile[dim] - grand_mean[dim]) ** 2

    ss_between = 0.0
    for mat_type, profiles in groups.items():
        n_g = len(profiles)
        group_mean = {}
        for dim in dimensions:
            group_mean[dim] = sum(p[dim] for p in profiles) / n_g
        for dim in dimensions:
            ss_between += n_g * (group_mean[dim] - grand_mean[dim]) ** 2

    if ss_total == 0:
        return 0.0

    return ss_between / ss_total


def kruskal_wallis_h(groups_values):
    """
    Compute Kruskal-Wallis H statistic for k groups.
    groups_values: list of lists of values
    """
    # Combine all values with group labels
    all_values = []
    for g_idx, vals in enumerate(groups_values):
        for v in vals:
            all_values.append((v, g_idx))

    n = len(all_values)
    if n < 3:
        return 0.0

    # Rank all values (average ranks for ties)
    sorted_vals = sorted(all_values, key=lambda x: x[0])
    ranks = [0.0] * n

    i = 0
    while i < n:
        j = i
        while j < n and sorted_vals[j][0] == sorted_vals[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0  # 1-based average rank
        for k_idx in range(i, j):
            ranks[k_idx] = avg_rank
        i = j

    # Sum of ranks per group
    group_rank_sums = defaultdict(float)
    group_sizes = defaultdict(int)
    for idx, (val, g_idx) in enumerate(sorted_vals):
        group_rank_sums[g_idx] += ranks[idx]
        group_sizes[g_idx] += 1

    # H = (12 / (n(n+1))) * sum(R_i^2 / n_i) - 3(n+1)
    h_stat = 0.0
    for g_idx in group_rank_sums:
        r_i = group_rank_sums[g_idx]
        n_i = group_sizes[g_idx]
        if n_i > 0:
            h_stat += (r_i ** 2) / n_i

    h_stat = (12.0 / (n * (n + 1))) * h_stat - 3.0 * (n + 1)
    return max(0.0, h_stat)


def spearman_rho(x, y):
    """Compute Spearman rank correlation between two sequences."""
    n = len(x)
    if n < 3:
        return 0.0

    # Rank each sequence
    def rank_data(data):
        indexed = sorted(enumerate(data), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + 1 + j) / 2.0
            for k in range(i, j):
                ranks[indexed[k][0]] = avg_rank
            i = j
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)

    # Pearson on ranks
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n

    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    var_x = sum((rx[i] - mean_rx) ** 2 for i in range(n))
    var_y = sum((ry[i] - mean_ry) ** 2 for i in range(n))

    denom = math.sqrt(var_x * var_y)
    if denom == 0:
        return 0.0
    return cov / denom


def permutation_p_value(observed, folio_list, folio_profiles, mat_types,
                        stat_func, dimensions, n_perm=N_PERMUTATIONS):
    """
    Generic permutation test.
    Shuffles material-type assignments among folios.
    Returns p-value (fraction of permuted stats >= observed).
    """
    rng = random.Random(RANDOM_SEED)
    count_ge = 0

    for _ in range(n_perm):
        # Shuffle material type assignments
        shuffled_types = list(mat_types)
        rng.shuffle(shuffled_types)
        shuffled_assignments = dict(zip(folio_list, shuffled_types))

        perm_stat = stat_func(shuffled_assignments, folio_profiles, dimensions)
        if perm_stat >= observed:
            count_ge += 1

    return (count_ge + 1) / (n_perm + 1)  # +1 for observed itself


# ============================================================
# TEST D: Category Distribution Matching
# ============================================================

def test_D_category_distribution(assignments, category_profiles):
    """
    PRIMARY: Test whether material-type groups have different
    8-category operational profiles.
    """
    print("  Running Test D: Category Distribution Matching...")

    # Folios with both assignment and profile data
    valid_folios = [f for f in assignments if f in category_profiles]
    valid_assignments = {f: assignments[f] for f in valid_folios}

    # Group statistics
    group_means, groups = compute_group_profiles(
        valid_assignments, category_profiles, CATEGORIES_8)

    group_sizes = {mt: len(profiles) for mt, profiles in groups.items()}

    # Multivariate pseudo-F
    observed_f = pseudo_f_statistic(valid_assignments, category_profiles, CATEGORIES_8)
    observed_eta2 = eta_squared(valid_assignments, category_profiles, CATEGORIES_8)

    # Permutation test for F
    folio_list = list(valid_assignments.keys())
    mat_types = [valid_assignments[f] for f in folio_list]

    p_value_f = permutation_p_value(
        observed_f, folio_list, category_profiles, mat_types,
        pseudo_f_statistic, CATEGORIES_8)

    # Per-category Kruskal-Wallis
    kw_results = {}
    for cat in CATEGORIES_8:
        group_vals = []
        for mt in sorted(groups.keys()):
            vals = [p[cat] for p in groups[mt]]
            group_vals.append(vals)
        h_stat = kruskal_wallis_h(group_vals)

        # Permutation p-value for this category
        count_ge = 0
        rng = random.Random(RANDOM_SEED + hash(cat))
        for _ in range(N_PERMUTATIONS):
            shuffled_types = list(mat_types)
            rng.shuffle(shuffled_types)
            shuf_groups = defaultdict(list)
            for fi, mt in zip(folio_list, shuffled_types):
                shuf_groups[mt].append(category_profiles[fi][cat])
            perm_h = kruskal_wallis_h([shuf_groups[mt] for mt in sorted(shuf_groups.keys())])
            if perm_h >= h_stat:
                count_ge += 1
        kw_p = (count_ge + 1) / (N_PERMUTATIONS + 1)

        kw_results[cat] = {
            'H_statistic': round(h_stat, 4),
            'p_value': round(kw_p, 6),
            'significant': kw_p < BONFERRONI_THRESHOLD,
            'group_means': {mt: round(group_means[mt][cat], 4) for mt in group_means},
        }

    # Verdict
    signal = p_value_f < BONFERRONI_THRESHOLD and observed_eta2 > MIN_EFFECT_SIZE

    # Check pre-registered directional predictions
    prediction_hits = 0
    prediction_total = 0
    prediction_details = {}
    for mt, preds in PREDICTIONS_D.items():
        if mt not in group_means:
            continue
        for cat in preds.get('elevated', []):
            prediction_total += 1
            # Check if this group's mean is above grand mean for this category
            grand_mean = sum(group_means[m][cat] for m in group_means) / len(group_means)
            hit = group_means[mt][cat] > grand_mean
            if hit:
                prediction_hits += 1
            prediction_details[f"{mt}_{cat}_elevated"] = {
                'predicted': 'above_grand_mean',
                'group_mean': round(group_means[mt][cat], 4),
                'grand_mean': round(grand_mean, 4),
                'hit': hit,
            }
        for cat in preds.get('reduced', []):
            prediction_total += 1
            grand_mean = sum(group_means[m][cat] for m in group_means) / len(group_means)
            hit = group_means[mt][cat] < grand_mean
            if hit:
                prediction_hits += 1
            prediction_details[f"{mt}_{cat}_reduced"] = {
                'predicted': 'below_grand_mean',
                'group_mean': round(group_means[mt][cat], 4),
                'grand_mean': round(grand_mean, 4),
                'hit': hit,
            }

    result = {
        'test': 'D',
        'name': 'Category Distribution Matching',
        'role': 'PRIMARY',
        'n_folios': len(valid_folios),
        'group_sizes': group_sizes,
        'group_mean_profiles': {
            mt: {cat: round(v, 4) for cat, v in profile.items()}
            for mt, profile in group_means.items()
        },
        'multivariate': {
            'pseudo_F': round(observed_f, 4),
            'eta_squared': round(observed_eta2, 4),
            'p_value': round(p_value_f, 6),
            'n_permutations': N_PERMUTATIONS,
            'significant': p_value_f < BONFERRONI_THRESHOLD,
            'effect_sufficient': observed_eta2 > MIN_EFFECT_SIZE,
        },
        'per_category_kruskal_wallis': kw_results,
        'pre_registered_predictions': {
            'hits': prediction_hits,
            'total': prediction_total,
            'hit_rate': round(prediction_hits / prediction_total, 3) if prediction_total > 0 else 0,
            'details': prediction_details,
        },
        'signal': signal,
        'verdict': 'SIGNAL' if signal else 'NULL',
    }

    sig_cats = [cat for cat, r in kw_results.items() if r['significant']]
    print(f"    Pseudo-F = {observed_f:.4f}, eta² = {observed_eta2:.4f}, p = {p_value_f:.6f}")
    print(f"    Signal: {'YES' if signal else 'NO'}")
    if sig_cats:
        print(f"    Significant categories: {', '.join(sig_cats)}")
    print(f"    Prediction hits: {prediction_hits}/{prediction_total}")

    return result


# ============================================================
# TEST A: Apparatus Profile Distributional Matching
# ============================================================

def test_A_apparatus_distribution(assignments, apparatus_profiles):
    """
    SECONDARY: Test whether material-type groups have different
    5-apparatus profiles.
    """
    print("  Running Test A: Apparatus Profile Distributional Matching...")

    valid_folios = [f for f in assignments if f in apparatus_profiles]
    valid_assignments = {f: assignments[f] for f in valid_folios}

    # Group statistics
    group_means, groups = compute_group_profiles(
        valid_assignments, apparatus_profiles, APPARATUS_5)

    group_sizes = {mt: len(profiles) for mt, profiles in groups.items()}

    # Multivariate pseudo-F
    observed_f = pseudo_f_statistic(valid_assignments, apparatus_profiles, APPARATUS_5)
    observed_eta2 = eta_squared(valid_assignments, apparatus_profiles, APPARATUS_5)

    # Permutation test for F
    folio_list = list(valid_assignments.keys())
    mat_types = [valid_assignments[f] for f in folio_list]

    p_value_f = permutation_p_value(
        observed_f, folio_list, apparatus_profiles, mat_types,
        pseudo_f_statistic, APPARATUS_5)

    # Per-apparatus Kruskal-Wallis
    kw_results = {}
    for app in APPARATUS_5:
        group_vals = []
        for mt in sorted(groups.keys()):
            vals = [p[app] for p in groups[mt]]
            group_vals.append(vals)
        h_stat = kruskal_wallis_h(group_vals)

        count_ge = 0
        rng = random.Random(RANDOM_SEED + hash(app))
        for _ in range(N_PERMUTATIONS):
            shuffled_types = list(mat_types)
            rng.shuffle(shuffled_types)
            shuf_groups = defaultdict(list)
            for fi, mt in zip(folio_list, shuffled_types):
                shuf_groups[mt].append(apparatus_profiles[fi][app])
            perm_h = kruskal_wallis_h([shuf_groups[mt] for mt in sorted(shuf_groups.keys())])
            if perm_h >= h_stat:
                count_ge += 1
        kw_p = (count_ge + 1) / (N_PERMUTATIONS + 1)

        kw_results[app] = {
            'H_statistic': round(h_stat, 4),
            'p_value': round(kw_p, 6),
            'significant': kw_p < BONFERRONI_THRESHOLD,
            'group_means': {mt: round(group_means[mt][app], 6) for mt in group_means},
        }

    # Check predictions
    prediction_hits = 0
    prediction_total = 0
    prediction_details = {}
    for mt, preds in PREDICTIONS_A.items():
        if mt not in group_means:
            continue
        for app in preds.get('elevated', []):
            prediction_total += 1
            grand_mean = sum(group_means[m][app] for m in group_means) / len(group_means)
            hit = group_means[mt][app] > grand_mean
            if hit:
                prediction_hits += 1
            prediction_details[f"{mt}_{app}_elevated"] = {
                'predicted': 'above_grand_mean',
                'group_mean': round(group_means[mt][app], 6),
                'grand_mean': round(grand_mean, 6),
                'hit': hit,
            }
        for app in preds.get('reduced', []):
            prediction_total += 1
            grand_mean = sum(group_means[m][app] for m in group_means) / len(group_means)
            hit = group_means[mt][app] < grand_mean
            if hit:
                prediction_hits += 1
            prediction_details[f"{mt}_{app}_reduced"] = {
                'predicted': 'below_grand_mean',
                'group_mean': round(group_means[mt][app], 6),
                'grand_mean': round(grand_mean, 6),
                'hit': hit,
            }

    signal = p_value_f < BONFERRONI_THRESHOLD and observed_eta2 > MIN_EFFECT_SIZE

    result = {
        'test': 'A',
        'name': 'Apparatus Profile Distributional Matching',
        'role': 'SECONDARY',
        'n_folios': len(valid_folios),
        'group_sizes': group_sizes,
        'group_mean_profiles': {
            mt: {app: round(v, 6) for app, v in profile.items()}
            for mt, profile in group_means.items()
        },
        'multivariate': {
            'pseudo_F': round(observed_f, 4),
            'eta_squared': round(observed_eta2, 4),
            'p_value': round(p_value_f, 6),
            'n_permutations': N_PERMUTATIONS,
            'significant': p_value_f < BONFERRONI_THRESHOLD,
            'effect_sufficient': observed_eta2 > MIN_EFFECT_SIZE,
        },
        'per_apparatus_kruskal_wallis': kw_results,
        'pre_registered_predictions': {
            'hits': prediction_hits,
            'total': prediction_total,
            'hit_rate': round(prediction_hits / prediction_total, 3) if prediction_total > 0 else 0,
            'details': prediction_details,
        },
        'signal': signal,
        'verdict': 'SIGNAL' if signal else 'NULL',
    }

    sig_apps = [app for app, r in kw_results.items() if r['significant']]
    print(f"    Pseudo-F = {observed_f:.4f}, eta² = {observed_eta2:.4f}, p = {p_value_f:.6f}")
    print(f"    Signal: {'YES' if signal else 'NO'}")
    if sig_apps:
        print(f"    Significant apparatus: {', '.join(sig_apps)}")
    print(f"    Prediction hits: {prediction_hits}/{prediction_total}")

    return result


# ============================================================
# TEST B: Three-Way Triangulation
# ============================================================

def test_B_triangulation(assignments, regime_map, brunschwig_degrees):
    """
    CONDITIONAL: Test the chain Puff material → Brunschwig degree → REGIME.
    Only runs if both Test D and Test A show signal.
    """
    print("  Running Test B: Three-Way Triangulation...")

    modal_degrees, degrees_by_class = brunschwig_degrees

    # Step 1: Map Puff material types to expected REGIME via Brunschwig
    # Puff ROOT → Brunschwig 'root' → modal degree → REGIME
    # Puff HERB → Brunschwig 'herb' → modal degree → REGIME
    # Puff FLOWER → Brunschwig 'flower' → modal degree → REGIME
    puff_to_brunschwig = {
        'ROOT': 'root',
        'HERB': 'herb',
        'FLOWER': 'flower',
    }

    material_to_expected_regime = {}
    material_to_degree = {}
    for puff_type, brun_class in puff_to_brunschwig.items():
        if brun_class in modal_degrees:
            degree = modal_degrees[brun_class]
            material_to_degree[puff_type] = degree
            if degree in DEGREE_TO_REGIME:
                material_to_expected_regime[puff_type] = DEGREE_TO_REGIME[degree]

    print(f"    Material→Degree→REGIME chain:")
    for mt in sorted(material_to_expected_regime.keys()):
        deg = material_to_degree[mt]
        regime = material_to_expected_regime[mt]
        deg_dist = Counter(degrees_by_class.get(puff_to_brunschwig[mt], []))
        print(f"      {mt} → degree {deg} (dist: {dict(deg_dist)}) → {regime}")

    # Step 2: For each assigned folio, check REGIME match
    matches = 0
    total = 0
    per_folio_results = []

    for folio, mat_type in assignments.items():
        if mat_type not in material_to_expected_regime:
            continue
        if folio not in regime_map:
            continue

        expected = material_to_expected_regime[mat_type]
        actual = regime_map[folio]
        match = expected == actual
        if match:
            matches += 1
        total += 1

        per_folio_results.append({
            'folio': folio,
            'material_type': mat_type,
            'expected_regime': expected,
            'actual_regime': actual,
            'match': match,
        })

    match_rate = matches / total if total > 0 else 0

    # Step 3: Permutation test
    # Shuffle folio-to-material assignments, recompute match rate
    folio_list = [r['folio'] for r in per_folio_results]
    actual_regimes = [regime_map[f] for f in folio_list]
    mat_types_list = [assignments[f] for f in folio_list]

    rng = random.Random(RANDOM_SEED + 999)
    count_ge = 0
    perm_match_rates = []

    for _ in range(N_PERMUTATIONS):
        shuffled_mats = list(mat_types_list)
        rng.shuffle(shuffled_mats)
        perm_matches = 0
        for fi, mt, actual_reg in zip(folio_list, shuffled_mats, actual_regimes):
            if mt in material_to_expected_regime:
                if material_to_expected_regime[mt] == actual_reg:
                    perm_matches += 1
        perm_rate = perm_matches / total if total > 0 else 0
        perm_match_rates.append(perm_rate)
        if perm_rate >= match_rate:
            count_ge += 1

    p_value = (count_ge + 1) / (N_PERMUTATIONS + 1)

    # Effect size: (observed - mean_perm) / std_perm
    mean_perm = sum(perm_match_rates) / len(perm_match_rates)
    var_perm = sum((r - mean_perm) ** 2 for r in perm_match_rates) / len(perm_match_rates)
    std_perm = math.sqrt(var_perm) if var_perm > 0 else 0
    z_score = (match_rate - mean_perm) / std_perm if std_perm > 0 else 0

    # Per-group match rates
    group_match_rates = {}
    for mt in sorted(set(mat_types_list)):
        mt_folios = [r for r in per_folio_results if r['material_type'] == mt]
        mt_matches = sum(1 for r in mt_folios if r['match'])
        group_match_rates[mt] = {
            'matches': mt_matches,
            'total': len(mt_folios),
            'rate': round(mt_matches / len(mt_folios), 3) if mt_folios else 0,
            'expected_regime': material_to_expected_regime.get(mt, 'N/A'),
        }

    signal = p_value < BONFERRONI_THRESHOLD and abs(z_score) > 2.0

    result = {
        'test': 'B',
        'name': 'Three-Way Triangulation',
        'role': 'CONDITIONAL',
        'chain': {
            'material_to_degree': material_to_degree,
            'material_to_regime': material_to_expected_regime,
            'degree_distribution_by_class': {
                mt: dict(Counter(degrees_by_class.get(bc, [])))
                for mt, bc in puff_to_brunschwig.items()
            },
        },
        'n_folios': total,
        'matches': matches,
        'match_rate': round(match_rate, 4),
        'permutation': {
            'p_value': round(p_value, 6),
            'mean_perm_rate': round(mean_perm, 4),
            'std_perm_rate': round(std_perm, 4),
            'z_score': round(z_score, 2),
            'n_permutations': N_PERMUTATIONS,
        },
        'per_group_match_rates': group_match_rates,
        'per_folio_results': per_folio_results,
        'signal': signal,
        'verdict': 'TRIANGULATION_HOLDS' if signal else 'CHAIN_BREAKS',
    }

    print(f"    Match rate: {matches}/{total} = {match_rate:.3f}")
    print(f"    Permutation mean: {mean_perm:.3f}, p = {p_value:.6f}, z = {z_score:.2f}")
    print(f"    Signal: {'YES' if signal else 'NO'}")

    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("Phase 490: Puff-Voynich Structural Revisit")
    print("=" * 70)

    random.seed(RANDOM_SEED)

    # Step 1: Write pre-registered assignments BEFORE any computation
    print("\n1. Writing pre-registered folio assignments...")
    pre_reg = {
        'phase': 490,
        'pre_registration': True,
        'description': 'Folio-to-material-type assignments based on PPC blind morphological classification',
        'source': 'phases/PPC_program_plant_correlation/plant_morphology_classification.md',
        'assignments': FOLIO_ASSIGNMENTS,
        'excluded': EXCLUDED_FOLIOS,
        'group_sizes': dict(Counter(FOLIO_ASSIGNMENTS.values())),
        'predictions_D': PREDICTIONS_D,
        'predictions_A': PREDICTIONS_A,
        'reordering_note': 'All tests are distributional, not positional. Results invariant to folio binding order.',
    }

    pre_reg_path = RESULTS_DIR / 'pre_registered_assignments.json'
    with open(pre_reg_path, 'w') as f:
        json.dump(pre_reg, f, indent=2)
    print(f"  Written to {pre_reg_path}")

    # Step 2: Load all data
    print("\n2. Loading data...")

    print("  Loading Puff chapters...")
    puff_chapters = load_puff_data()
    print(f"    {len(puff_chapters)} chapters loaded")

    print("  Loading Voynich category profiles...")
    category_profiles = load_voynich_category_profiles()
    print(f"    {len(category_profiles)} folios with category profiles")

    print("  Loading apparatus profiles...")
    apparatus_profiles = load_apparatus_profiles()
    print(f"    {len(apparatus_profiles)} folios with apparatus profiles")

    print("  Loading REGIME mapping...")
    regime_map = load_regime_mapping()
    print(f"    {len(regime_map)} folios with REGIME assignments")

    print("  Loading Brunschwig fire degrees...")
    brunschwig_modal, brunschwig_degrees = load_brunschwig_degrees()
    print(f"    {len(brunschwig_modal)} material classes with modal degrees")

    # Step 3: Run tests
    print("\n3. Running test battery...")
    print(f"  Bonferroni threshold: p < {BONFERRONI_THRESHOLD}")
    print(f"  Minimum effect size: {MIN_EFFECT_SIZE}")
    print(f"  Permutations: {N_PERMUTATIONS}")

    # Test D (PRIMARY — always runs)
    print("\n--- Test D (PRIMARY) ---")
    result_D = test_D_category_distribution(FOLIO_ASSIGNMENTS, category_profiles)

    # Test A (SECONDARY — always runs)
    print("\n--- Test A (SECONDARY) ---")
    result_A = test_A_apparatus_distribution(FOLIO_ASSIGNMENTS, apparatus_profiles)

    # Test B (CONDITIONAL — only if D AND A show signal)
    result_B = None
    if result_D['signal'] and result_A['signal']:
        print("\n--- Test B (CONDITIONAL — triggered by D+A signal) ---")
        result_B = test_B_triangulation(
            FOLIO_ASSIGNMENTS, regime_map, (brunschwig_modal, brunschwig_degrees))
    else:
        print(f"\n--- Test B SKIPPED ---")
        reasons = []
        if not result_D['signal']:
            reasons.append('Test D showed no signal')
        if not result_A['signal']:
            reasons.append('Test A showed no signal')
        print(f"  Reason: {'; '.join(reasons)}")
        result_B = {
            'test': 'B',
            'name': 'Three-Way Triangulation',
            'role': 'CONDITIONAL',
            'skipped': True,
            'skip_reason': '; '.join(reasons),
            'verdict': 'SKIPPED',
        }

    # Step 4: Overall assessment
    print("\n" + "=" * 70)
    print("OVERALL ASSESSMENT")
    print("=" * 70)

    d_signal = result_D['signal']
    a_signal = result_A['signal']
    b_signal = result_B.get('signal', False)

    if d_signal and a_signal and b_signal:
        overall = 'PUFF_CONNECTION_CONFIRMED'
        interpretation = ('Material types predict both operational category profiles '
                          'and apparatus profiles, and the Puff→Brunschwig→REGIME '
                          'chain holds. Structural connection to Puff confirmed.')
    elif d_signal and a_signal:
        overall = 'PARTIAL_SIGNAL'
        if result_B.get('skipped'):
            interpretation = 'Should not reach here — B should have run'
        else:
            interpretation = ('Material types predict grammar but the '
                              'Puff→Brunschwig→REGIME chain breaks.')
    elif d_signal:
        overall = 'CATEGORY_ONLY'
        interpretation = ('Category profiles differentiate by material type, '
                          'but apparatus profiles do not. Moderate finding.')
    else:
        overall = 'CEILING_CONFIRMED'
        interpretation = ('No material-type differentiation in operational category '
                          'profiles. The early evidential ceiling is confirmed with '
                          'modern structural tools. Puff connection remains suggestive '
                          'but not structurally diagnostic.')

    print(f"  Test D: {result_D['verdict']}")
    print(f"  Test A: {result_A['verdict']}")
    print(f"  Test B: {result_B['verdict']}")
    print(f"  Overall: {overall}")
    print(f"  {interpretation}")

    # Step 5: Write results
    output = {
        'phase': 490,
        'name': 'PUFF_VOYNICH_STRUCTURAL_REVISIT',
        'description': ('Revisit of Puff-Voynich connection with modern structural tools. '
                        'Tests whether Voynich folio profiles differentiate by plant '
                        'material type from PPC blind morphological classification.'),
        'methodology': {
            'assignment_source': 'PPC blind morphological classification',
            'assignment_method': 'Pre-registered before test computation',
            'significance_threshold': BONFERRONI_THRESHOLD,
            'effect_size_threshold': MIN_EFFECT_SIZE,
            'n_permutations': N_PERMUTATIONS,
            'reordering_robust': True,
            'reordering_note': 'All tests are distributional, not positional. Results invariant to folio ordering.',
        },
        'folio_assignments': {
            'total_assigned': len(FOLIO_ASSIGNMENTS),
            'total_excluded': len(EXCLUDED_FOLIOS),
            'groups': dict(Counter(FOLIO_ASSIGNMENTS.values())),
            'assignments': FOLIO_ASSIGNMENTS,
            'exclusions': EXCLUDED_FOLIOS,
        },
        'puff_context': {
            'total_chapters': len(puff_chapters),
            'category_distribution': dict(Counter(ch.get('category') for ch in puff_chapters)),
        },
        'test_D': result_D,
        'test_A': result_A,
        'test_B': result_B,
        'overall': {
            'verdict': overall,
            'interpretation': interpretation,
            'D_signal': d_signal,
            'A_signal': a_signal,
            'B_signal': b_signal,
        },
    }

    output_path = RESULTS_DIR / 'puff_voynich_structural_revisit.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults written to {output_path}")


if __name__ == '__main__':
    main()
