"""
Phase 627: PER_DOMAIN_BRIDGE_CALIBRATION -- Shared utilities.

Provides data loaders for pseudo-Lull structural profiles, Phase 626
bridge decomposition, Brunschwig operational profiles, REGIME mapping,
and V-side HEAD channel computation. Reuses statistical utilities from
shared_626.py where possible.
"""

import json
import math
import random
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

import sys
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier,
    load_middle_classes, decompose_middle_hmt,
)

# ============================================================
# Constants
# ============================================================

PROJECT_ROOT = _PROJECT_ROOT
PHASE_DIR = PROJECT_ROOT / 'phases' / 'PER_DOMAIN_BRIDGE_CALIBRATION'
RESULTS_DIR = PHASE_DIR / 'results'

N_PERM = 1000
RNG = random.Random(627)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

HEAT_MODES = [
    'balneum_mariae', 'ash_fire', 'sand_bath', 'athanor',
    'dung_fire', 'gentle_fire', 'strong_fire', 'moderate_fire',
    'open_fire', 'cupellation', 'crucible', 'tripod_of_secrets',
    'solar_heat',
]

# Heat intensity ordinal (1=gentle .. 7=crucible)
HEAT_INTENSITY = {
    'balneum_mariae': 1, 'gentle_fire': 2, 'moderate_fire': 3,
    'ash_fire': 4, 'sand_bath': 4, 'dung_fire': 4,
    'open_fire': 5, 'athanor': 5, 'strong_fire': 6,
    'crucible': 7, 'cupellation': 7, 'tripod_of_secrets': 5,
    'solar_heat': 2,
}

# Fire degree -> REGIME mapping (from C1735)
FIRE_DEGREE_REGIME = {1: 'REGIME_2', 2: 'REGIME_1', 3: 'REGIME_3', 4: 'REGIME_4'}

# HEAD types in bridge functional groups
HEAD_TYPES = ['k', 'e', 'o', 't', 'h', 'a']

# ============================================================
# PL Data Loaders
# ============================================================

def load_pl_structural_profile() -> dict:
    """Load Phase 602 structural profile (209 chapters with E1-E8)."""
    path = (PROJECT_ROOT / 'phases' / 'PSEUDO_LULL_CHARACTERIZATION' /
            'results' / 'pseudo_lull_structural_profile.json')
    with open(path) as f:
        return json.load(f)


def load_pl_chapters() -> list:
    """Load PL chapter list from E1."""
    data = load_pl_structural_profile()
    return data['E1_chapters']


def load_pl_english_lines() -> list:
    """Load PL English translation lines."""
    path = (PROJECT_ROOT / 'sources' / 'pseudo_lull_testamentum' /
            'testamentum_complete_english.txt')
    with open(path, encoding='utf-8') as f:
        return f.readlines()


def load_pl_channel_features() -> dict:
    """Load Script 1 output (per-chapter subtype vectors)."""
    path = RESULTS_DIR / 'pl_channel_features.json'
    with open(path) as f:
        return json.load(f)


# ============================================================
# Phase 626 Bridge Data Loaders
# ============================================================

def load_bridge_decomposition() -> dict:
    """Load bridge_decomposition.json (T1-T5)."""
    path = (PROJECT_ROOT / 'phases' / 'A_TO_B_BRIDGE_DECOMPOSITION' /
            'results' / 'bridge_decomposition.json')
    with open(path) as f:
        return json.load(f)


def load_bridge_functional_groups() -> Tuple[Dict[str, int], Dict[int, dict]]:
    """Load functional group data from bridge decomposition.

    Returns:
        (middle_to_group, group_profiles):
        - middle_to_group: MIDDLE -> group_id (1-6)
        - group_profiles: group_id -> {n_middles, middles, top_categories, hmt_heads, ...}
    """
    data = load_bridge_decomposition()
    t5 = data['T5_functional_groups']
    middle_to_group = {m: int(g) for m, g in t5['bridge_group_assignment'].items()}
    group_profiles = {int(k): v for k, v in t5['group_profiles'].items()}
    return middle_to_group, group_profiles


def load_head_redistribution() -> dict:
    """Load HEAD redistribution transition table from T4."""
    data = load_bridge_decomposition()
    return data['T4_head_redistribution']


# ============================================================
# V-side Data Loaders (from shared_626.py equivalents)
# ============================================================

def load_b_operational_profiles() -> Dict[str, dict]:
    """Load B folio -> 12 operational dimensions."""
    path = PROJECT_ROOT / 'results' / 'folio_operational_profiles.json'
    with open(path) as f:
        data = json.load(f)
    result = {}
    dims = data['dimensions']
    for p in data['profiles']:
        folio = p['folio']
        result[folio] = {d: p[d] for d in dims}
        result[folio]['material_category'] = p.get('material_category')
        result[folio]['output_category'] = p.get('output_category')
        result[folio]['kernel_balance'] = p.get('kernel_balance')
    return result


def load_regime_mapping() -> Dict[str, str]:
    """Load B folio -> REGIME string."""
    path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    with open(path) as f:
        data = json.load(f)
    result = {}
    for folio, info in data['regime_assignments'].items():
        result[folio] = info['regime']
    return result


def load_b_deployment_features() -> Tuple[Dict[str, dict], list]:
    """Load B folio -> 56-feature vector, and feature names list."""
    path = (PROJECT_ROOT / 'phases' / 'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL' /
            'results' / 't1b_deployment_features.json')
    with open(path) as f:
        data = json.load(f)
    all_names = []
    for group in ['zone', 'adjacency', 'closure', 'headless', 'paragraph']:
        all_names.extend(data['feature_names'].get(group, []))
    result = {}
    for folio, features in data['folio_features'].items():
        result[folio] = {name: features.get(name, 0.0) for name in all_names}
    return result, all_names


def load_brunschwig_profiles() -> list:
    """Load 245 Brunschwig recipes with fire_degree."""
    path = PROJECT_ROOT / 'results' / 'brunschwig_operational_profiles.json'
    with open(path) as f:
        data = json.load(f)
    return data.get('recipes', data.get('profiles', []))


# ============================================================
# V-side HEAD Channel Computation
# ============================================================

def compute_folio_head_channel_profile(folio: str, op_profiles: dict) -> dict:
    """Compute HEAD-channel profile for a B folio.

    Returns dict with k_frac, e_frac, h_frac, o_frac, t_frac based on
    operational profiles (kernel distribution from raw_kernel_dist).
    """
    prof = op_profiles.get(folio)
    if not prof:
        return {}
    return {
        'k_ratio': prof.get('k_ratio', 0.0),
        'e_ratio': prof.get('e_ratio', 0.0),
        'h_ratio': prof.get('h_ratio', 0.0),
        'thermo_ke': prof.get('thermo_ke', 0.0),
        'thermo_kch': prof.get('thermo_kch', 0.0),
        'iteration_rate': prof.get('iteration_rate', 0.0),
        'checkpoint_rate': prof.get('checkpoint_rate', 0.0),
        'terminal_rate': prof.get('terminal_rate', 0.0),
    }


def compute_bridge_head_density(folio: str, bridge_data: dict,
                                 op_profiles: dict) -> dict:
    """Compute per-HEAD bridge MIDDLE density for a B folio.

    Uses T2_b_consequence -> b_head_dist per bridge MIDDLE, aggregated
    to folio level via operational profile token counts.
    """
    t2 = bridge_data.get('T2_b_consequence', {})
    # Count bridge MIDDLE occurrences per HEAD in this folio
    # We approximate using the B-side head distribution
    profile = op_profiles.get(folio, {})
    k_r = profile.get('k_ratio', 0.0)
    e_r = profile.get('e_ratio', 0.0)
    h_r = profile.get('h_ratio', 0.0)
    # o and t need separate computation from deployment features
    return {
        'k_head_density': k_r,
        'e_head_density': e_r,
        'h_head_density': h_r,
    }


def compute_regime_head_profiles(op_profiles: dict,
                                  regime_map: dict) -> Dict[str, dict]:
    """Compute per-REGIME mean HEAD-channel profiles."""
    regime_vals = defaultdict(lambda: defaultdict(list))
    for folio, regime in regime_map.items():
        prof = compute_folio_head_channel_profile(folio, op_profiles)
        if not prof:
            continue
        for feat, val in prof.items():
            regime_vals[regime][feat].append(val)

    result = {}
    for regime, feats in regime_vals.items():
        result[regime] = {}
        for feat, vals in feats.items():
            result[regime][feat] = sum(vals) / len(vals) if vals else 0.0
    return result


def get_folio_section(folio: str) -> str:
    """Determine section (H or P) for a B folio."""
    match = re.search(r'(\d+)', folio)
    if not match:
        return 'H'
    num = int(match.group(1))
    if 87 <= num <= 102:
        return 'P'
    return 'H'


def get_herbal_folios(regime_map: dict) -> Dict[str, str]:
    """Get within-Herbal (H-section) folio -> REGIME mapping."""
    return {f: r for f, r in regime_map.items() if get_folio_section(f) == 'H'}


def get_stars_folios(regime_map: dict) -> set:
    """Get Stars-section folios (f103-f116)."""
    result = set()
    for folio in regime_map:
        match = re.search(r'(\d+)', folio)
        if match:
            num = int(match.group(1))
            if 103 <= num <= 116:
                result.add(folio)
    return result


# ============================================================
# Statistical Utilities
# ============================================================

def spearman_rank(x: list, y: list) -> Tuple[float, float]:
    """Spearman rank correlation with permutation p-value."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    def _rank(vals):
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

    rx = _rank(x)
    ry = _rank(y)
    rho = _pearson(rx, ry)

    # Permutation p-value
    count_ge = 0
    perm_y = list(range(n))
    for _ in range(N_PERM):
        RNG.shuffle(perm_y)
        ry_perm = [ry[perm_y[i]] for i in range(n)]
        r_perm = _pearson(rx, ry_perm)
        if abs(r_perm) >= abs(rho):
            count_ge += 1

    p = (count_ge + 1) / (N_PERM + 1)
    return rho, p


def _pearson(x: list, y: list) -> float:
    """Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    return cov / (sx * sy)


def kruskal_wallis(groups: Dict[str, list]) -> Tuple[float, float]:
    """Kruskal-Wallis H test."""
    all_vals = []
    group_ids = []
    for gid, vals in groups.items():
        for v in vals:
            all_vals.append(v)
            group_ids.append(gid)

    n = len(all_vals)
    if n < 3:
        return 0.0, 1.0

    # Rank all values
    indexed = sorted(enumerate(all_vals), key=lambda iv: iv[1])
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

    # Compute H
    group_rank_sums = defaultdict(lambda: [0.0, 0])
    for idx, gid in enumerate(group_ids):
        group_rank_sums[gid][0] += ranks[idx]
        group_rank_sums[gid][1] += 1

    H = 0.0
    for gid, (rsum, ni) in group_rank_sums.items():
        if ni > 0:
            H += (rsum ** 2) / ni
    H = (12 / (n * (n + 1))) * H - 3 * (n + 1)

    # Chi-sq approximation with k-1 df
    k = len(groups)
    if k < 2:
        return 0.0, 1.0
    df = k - 1
    p = _chi2_sf(H, df)
    return H, p


def _chi2_sf(x: float, df: int) -> float:
    """Survival function for chi-squared distribution (approximation)."""
    if x <= 0:
        return 1.0
    if df == 1:
        z = math.sqrt(x)
        return 2 * (1 - _norm_cdf(z))
    elif df == 2:
        return math.exp(-x / 2)
    else:
        # Wilson-Hilferty approximation
        z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        return 1 - _norm_cdf(z)


def _norm_cdf(z: float) -> float:
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    if z < -8:
        return 0.0
    if z > 8:
        return 1.0
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    z_abs = abs(z)
    t = 1.0 / (1.0 + p * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs / 2)
    return 0.5 * (1.0 + sign * y)


def mann_whitney_u(x: list, y: list) -> Tuple[float, float]:
    """Mann-Whitney U test."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, 1.0

    all_vals = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    all_vals.sort(key=lambda vg: vg[0])
    n = nx + ny

    # Assign ranks with ties
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and all_vals[j + 1][0] == all_vals[j][0]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for idx in range(i, j + 1):
            ranks[idx] = avg_rank
        i = j + 1

    # Sum ranks for x
    r_x = sum(ranks[i] for i in range(n) if all_vals[i][1] == 'x')
    U = r_x - nx * (nx + 1) / 2
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)
    if sigma < 1e-12:
        return U, 1.0
    z = (U - mu) / sigma
    p = 2 * (1 - _norm_cdf(abs(z)))
    return U, p


def mantel_test(D1: list, D2: list, n_perm: int = N_PERM,
                rng: random.Random = None) -> Tuple[float, float]:
    """Mantel test: correlation between two distance matrices (flat upper-triangle).

    Returns (r, p_value).
    """
    if rng is None:
        rng = RNG

    if len(D1) == 0 or len(D2) == 0:
        return 0.0, 1.0

    r_obs = _pearson(D1, D2)
    if abs(r_obs) < 1e-12:
        return 0.0, 1.0

    # Recover n from n*(n-1)/2
    n = int((1 + math.sqrt(1 + 8 * len(D1))) / 2)

    count_ge = 0
    indices = list(range(n))
    for _ in range(n_perm):
        perm = indices[:]
        rng.shuffle(perm)
        d2_perm = []
        for i in range(n):
            for j in range(i + 1, n):
                pi, pj = perm[i], perm[j]
                ii, jj = min(pi, pj), max(pi, pj)
                idx = ii * n - ii * (ii + 1) // 2 + jj - ii - 1
                d2_perm.append(D2[idx])
        r_perm = _pearson(D1, d2_perm)
        if r_perm >= r_obs:
            count_ge += 1

    p_value = (count_ge + 1) / (n_perm + 1)
    return r_obs, p_value


def euclidean_dist(a: list, b: list) -> float:
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def cosine_sim(a: list, b: list) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    na = math.sqrt(sum(ai * ai for ai in a))
    nb = math.sqrt(sum(bi * bi for bi in b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return dot / (na * nb)


def cohens_d(a: list, b: list) -> float:
    """Cohen's d effect size."""
    if len(a) < 2 or len(b) < 2:
        return 0.0
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    var_a = sum((x - mean_a) ** 2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (len(b) - 1)
    pooled_sd = math.sqrt(((len(a) - 1) * var_a + (len(b) - 1) * var_b) /
                          (len(a) + len(b) - 2))
    if pooled_sd < 1e-12:
        return 0.0
    return (mean_a - mean_b) / pooled_sd


def pairwise_upper_triangle(items: list, dist_fn) -> list:
    """Compute upper-triangle pairwise distances."""
    n = len(items)
    result = []
    for i in range(n):
        for j in range(i + 1, n):
            result.append(dist_fn(items[i], items[j]))
    return result


def bonferroni_threshold(alpha: float, n_tests: int) -> float:
    """Bonferroni-corrected significance threshold."""
    return alpha / n_tests


def round_floats(obj, digits=6):
    """Round all floats in a nested structure."""
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [round_floats(x, digits) for x in obj]
    return obj
