"""
Phase 625: SHORT_PARAGRAPH_ARCHITECTURE -- Shared utilities.

Provides stratum assignment, whole-paragraph feature extraction,
gallows analysis, zone classification, position-matched subsampling,
and a full suite of non-parametric statistical tests (Mann-Whitney U,
Kruskal-Wallis H, Kolmogorov-Smirnov, Spearman rho, chi-squared)
implemented from scratch.

Dependencies: Phase 624 shared_624.py (which chains through Phase 623).
"""

import sys
import math
import random
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from phases.PARAGRAPH_STRUCTURAL_ISOMORPHISM.scripts.shared_624 import (
    build_corpus,
    _bin_features,
    extract_header_features,
    z_normalize,
    pca_reduce,
    section_residualize,
    silhouette_score,
    calinski_harabasz,
    kmeans,
    ward_linkage,
    cut_dendrogram,
    adjusted_rand_index,
    cosine_similarity,
    round_floats,
    euclidean_dist,
    ARC_FEATURE_NAMES,
    CATEGORIES, HEAD_SET, TERM_SET,
    LOCKED_TERMS, CHANNELED_TERMS, DIFFUSE_TERMS,
    MODE_A_SUFFIXES, MODE_B_SUFFIXES,
)

# ============================================================
# Constants
# ============================================================

PROJECT_ROOT = _PROJECT_ROOT
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'SHORT_PARAGRAPH_ARCHITECTURE' / 'results'

RNG = random.Random(625)
N_PERM = 500

STRATA = {
    'HEADER_ONLY': (0, 0),
    'MINIMAL': (1, 2),
    'SHORT': (3, 4),
    'LONG': (5, 999),
}
STRATUM_ORDER = ['HEADER_ONLY', 'MINIMAL', 'SHORT', 'LONG']

FEATURE_NAMES = [
    'log_ke_ratio', 'h_rate', 'headless_rate', 'mode_a_frac',
    'mean_opacity', 'cat_entropy', 'tokens_per_line', 'm_terminal_rate',
    'dark_frac', 'bridge_frac', 'thermal_frac'
]

# Terminal opacity values
_OPACITY_NUMERIC = {
    'LOCKED': 1.0,
    'CHANNELED': 0.5,
    'DIFFUSE': 0.0,
    'BARE': 0.0,
}


# ============================================================
# Stratum assignment
# ============================================================

def assign_stratum(paragraph):
    """Assign paragraph to a stratum based on body line count."""
    n_body = len(paragraph.get('body_lines', []))
    for name, (lo, hi) in STRATA.items():
        if lo <= n_body <= hi:
            return name
    return 'LONG'


# ============================================================
# Token flattening
# ============================================================

def get_all_tokens(paragraph):
    """Flatten all tokens from header_lines + body_lines."""
    tokens = []
    for line in paragraph.get('header_lines', []):
        tokens.extend(line.get('tokens', []))
    for line in paragraph.get('body_lines', []):
        tokens.extend(line.get('tokens', []))
    return tokens


# ============================================================
# Whole-paragraph feature extraction (11 features)
# ============================================================

def extract_paragraph_features(paragraph):
    """
    Compute 11 features over ALL tokens in the paragraph (no binning).

    Features (FEATURE_NAMES order):
        log_ke_ratio, h_rate, headless_rate, mode_a_frac,
        mean_opacity, cat_entropy, tokens_per_line, m_terminal_rate,
        dark_frac, bridge_frac, thermal_frac

    Returns:
        dict mapping feature name -> float value.
        For paragraphs with 0 tokens, returns a dict of zeros.
    """
    tokens = get_all_tokens(paragraph)
    n_tok = len(tokens)

    # Count total lines (header + body)
    n_header_lines = len(paragraph.get('header_lines', []))
    n_body_lines = len(paragraph.get('body_lines', []))
    n_lines = n_header_lines + n_body_lines

    if n_tok == 0:
        return {name: 0.0 for name in FEATURE_NAMES}

    # 1. log_ke_ratio: log((k_kernel_count + 0.5) / (e_kernel_count + 0.5))
    k_count = 0
    h_count = 0
    e_count = 0
    for t in tokens:
        for c in t.get('kernels', []):
            if c == 'k':
                k_count += 1
            elif c == 'h':
                h_count += 1
            elif c == 'e':
                e_count += 1

    log_ke_ratio = math.log((k_count + 0.5) / (e_count + 0.5))

    # 2. h_rate: count of 'h' in all token kernels / total_tokens
    h_rate = h_count / n_tok

    # 3. headless_rate: fraction of tokens where is_headless is True
    headless_count = sum(1 for t in tokens if t.get('is_headless', False))
    headless_rate = headless_count / n_tok

    # 4. mode_a_frac: fraction of tokens whose suffix_mode == 'A'
    mode_a_count = sum(1 for t in tokens if t.get('suffix_mode') == 'A')
    mode_a_frac = mode_a_count / n_tok

    # 5. mean_opacity: mean of _OPACITY_NUMERIC[terminal_opacity]
    opacity_sum = 0.0
    for t in tokens:
        tier = t.get('terminal_opacity', 'BARE')
        opacity_sum += _OPACITY_NUMERIC.get(tier, 0.0)
    mean_opacity = opacity_sum / n_tok

    # 6. cat_entropy: Shannon entropy of 8-category distribution
    cat_counts = Counter()
    for t in tokens:
        cat = t.get('category', 'UNKNOWN')
        if cat in CATEGORIES:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values())
    cat_entropy = 0.0
    if cat_total > 0:
        for cat in CATEGORIES:
            c = cat_counts.get(cat, 0)
            if c > 0:
                p = c / cat_total
                cat_entropy -= p * math.log2(p)

    # 7. tokens_per_line: total_tokens / total_lines
    tokens_per_line = n_tok / n_lines if n_lines > 0 else 0.0

    # 8. m_terminal_rate: fraction of tokens where term == 'm'
    m_count = sum(1 for t in tokens if t.get('term') == 'm')
    m_terminal_rate = m_count / n_tok

    # 9. dark_frac: fraction of tokens where is_dark is True
    dark_count = sum(1 for t in tokens if t.get('is_dark', False))
    dark_frac = dark_count / n_tok

    # 10. bridge_frac: fraction of tokens where is_bridge is True
    bridge_count = sum(1 for t in tokens if t.get('is_bridge', False))
    bridge_frac = bridge_count / n_tok

    # 11. thermal_frac: fraction of categorized tokens whose category == 'THERMAL'
    thermal_count = cat_counts.get('THERMAL', 0)
    thermal_frac = thermal_count / cat_total if cat_total > 0 else 0.0

    return {
        'log_ke_ratio': log_ke_ratio,
        'h_rate': h_rate,
        'headless_rate': headless_rate,
        'mode_a_frac': mode_a_frac,
        'mean_opacity': mean_opacity,
        'cat_entropy': cat_entropy,
        'tokens_per_line': tokens_per_line,
        'm_terminal_rate': m_terminal_rate,
        'dark_frac': dark_frac,
        'bridge_frac': bridge_frac,
        'thermal_frac': thermal_frac,
    }


# ============================================================
# Gallows information extraction
# ============================================================

def extract_gallows_info(paragraph):
    """Extract gallows information from paragraph header."""
    header_lines = paragraph.get('header_lines', [])
    if not header_lines or not header_lines[0].get('tokens'):
        return {'gallows_type': 'none', 'gallows_initial': False, 'first_word': ''}
    first_token = header_lines[0]['tokens'][0]
    word = first_token.get('word', '')
    gallows_chars = {'k', 't', 'p', 'f'}
    if word and word[0] in gallows_chars:
        return {'gallows_type': word[0], 'gallows_initial': True, 'first_word': word}
    return {'gallows_type': 'none', 'gallows_initial': False, 'first_word': word}


# ============================================================
# Zone classification (C1398 zones)
# ============================================================

def classify_paragraph_zone(features_dict, zone_centroids):
    """
    Assign a paragraph to the nearest C1398 zone based on its 8-category
    profile using Euclidean distance.

    Args:
        features_dict: dict from extract_paragraph_features() or any dict
            that contains keys matching CATEGORIES (8 category fractions).
            Expected keys: 'thermal_frac' maps to THERMAL, and the other
            categories are extracted from the raw token counts.
            Alternatively, zone_centroids keys should match the feature keys.
        zone_centroids: dict mapping zone name -> dict of 8-category fracs.
            Zone names: 'THERMAL_QO', 'CONTAINMENT_SEALING',
            'OPERATION_ITERATION', 'MONITORING_PHASE'.
            Each value is a dict with keys from CATEGORIES mapping to floats.

    Returns:
        str: name of the nearest zone.
    """
    if not zone_centroids:
        return 'UNKNOWN'

    # Build the paragraph's 8-category vector from features_dict
    # We need to reconstruct category fractions. features_dict may have
    # them directly (if caller pre-computed), or we use the category keys.
    cat_order = list(CATEGORIES)  # canonical order

    # Extract paragraph category vector
    para_vec = []
    for cat in cat_order:
        key = cat.lower() + '_frac'
        if key in features_dict:
            para_vec.append(features_dict[key])
        elif cat in features_dict:
            para_vec.append(features_dict[cat])
        else:
            para_vec.append(0.0)

    best_zone = None
    best_dist = float('inf')
    for zone_name, centroid in zone_centroids.items():
        cent_vec = []
        for cat in cat_order:
            key = cat.lower() + '_frac'
            if key in centroid:
                cent_vec.append(centroid[key])
            elif cat in centroid:
                cent_vec.append(centroid[cat])
            else:
                cent_vec.append(0.0)
        dist = euclidean_dist(para_vec, cent_vec)
        if dist < best_dist:
            best_dist = dist
            best_zone = zone_name

    return best_zone


# ============================================================
# Position-matched subsampling
# ============================================================

def position_matched_subsample(paragraph, target_n_body):
    """
    Takes a paragraph with body_lines, returns a new pseudo-paragraph
    with only the FIRST target_n_body body lines (preserving header_lines).

    This simulates what a short paragraph would look like if it were the
    beginning of a longer one.

    Args:
        paragraph: dict with 'header_lines', 'body_lines', and other keys.
        target_n_body: number of body lines to keep.

    Returns:
        dict: new paragraph dict with truncated body_lines.
    """
    result = dict(paragraph)  # shallow copy
    body = paragraph.get('body_lines', [])
    result['body_lines'] = body[:target_n_body]
    return result


# ============================================================
# Jensen-Shannon Divergence
# ============================================================

def jsd(p, q):
    """
    Jensen-Shannon divergence between two probability distributions.

    JSD = 0.5 * KL(p || m) + 0.5 * KL(q || m)
    where m = 0.5 * (p + q).

    Uses base-2 log. Handles zeros with smoothing (add 1e-10 before
    normalizing).

    Args:
        p: list of floats (probability distribution)
        q: list of floats (probability distribution)

    Returns:
        float: JSD value (0 = identical, 1 = maximally different for base-2).
    """
    if not p or not q:
        return 0.0

    n = len(p)
    if n != len(q):
        raise ValueError(f"Distributions must have same length: {len(p)} vs {len(q)}")

    # Smooth and normalize
    eps = 1e-10
    p_s = [x + eps for x in p]
    q_s = [x + eps for x in q]
    p_sum = sum(p_s)
    q_sum = sum(q_s)
    p_n = [x / p_sum for x in p_s]
    q_n = [x / q_sum for x in q_s]

    # Compute m = 0.5 * (p + q)
    m = [0.5 * (p_n[i] + q_n[i]) for i in range(n)]

    # KL divergence: KL(a || b) = sum(a_i * log2(a_i / b_i))
    def kl(a, b):
        return sum(a[i] * math.log2(a[i] / b[i]) for i in range(n) if a[i] > 0)

    return 0.5 * kl(p_n, m) + 0.5 * kl(q_n, m)


# ============================================================
# Cohen's d effect size
# ============================================================

def cohens_d(a, b):
    """
    Cohen's d effect size between two groups.

    d = (mean_a - mean_b) / pooled_sd

    Handles edge case of zero variance (returns 0.0).

    Args:
        a: list of floats (group A values)
        b: list of floats (group B values)

    Returns:
        float: Cohen's d.
    """
    if not a or not b:
        return 0.0

    n_a = len(a)
    n_b = len(b)
    mean_a = sum(a) / n_a
    mean_b = sum(b) / n_b

    if n_a < 2 and n_b < 2:
        return 0.0

    var_a = sum((x - mean_a) ** 2 for x in a) / (n_a - 1) if n_a > 1 else 0.0
    var_b = sum((x - mean_b) ** 2 for x in b) / (n_b - 1) if n_b > 1 else 0.0

    pooled_var = ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
    pooled_sd = math.sqrt(pooled_var)

    if pooled_sd < 1e-12:
        return 0.0

    return (mean_a - mean_b) / pooled_sd


# ============================================================
# Within-section comparison
# ============================================================

def within_section_compare(values_a, values_b, sections_a, sections_b):
    """
    For each unique section that appears in BOTH groups, compute
    Mann-Whitney U and Cohen's d.

    Args:
        values_a: list of floats (group A values)
        values_b: list of floats (group B values)
        sections_a: list of str (section labels for group A)
        sections_b: list of str (section labels for group B)

    Returns:
        dict with keys:
            'per_section': dict mapping section -> {'U': .., 'z': .., 'p': ..,
                           'n_a': .., 'n_b': .., 'd': ..}
            'pooled': {'d': .., 'n_sections': .., 'n_a_total': .., 'n_b_total': ..}
    """
    # Group values by section
    sec_a = defaultdict(list)
    for v, s in zip(values_a, sections_a):
        sec_a[s].append(v)

    sec_b = defaultdict(list)
    for v, s in zip(values_b, sections_b):
        sec_b[s].append(v)

    # Find shared sections
    shared_sections = sorted(set(sec_a.keys()) & set(sec_b.keys()))

    per_section = {}
    all_resid_a = []
    all_resid_b = []

    for sec in shared_sections:
        a_vals = sec_a[sec]
        b_vals = sec_b[sec]

        if not a_vals or not b_vals:
            continue

        mw = mann_whitney_u(a_vals, b_vals)
        d = cohens_d(a_vals, b_vals)

        per_section[sec] = {
            'U': mw['U'],
            'z': mw['z'],
            'p': mw['p'],
            'n_a': mw['n_a'],
            'n_b': mw['n_b'],
            'd': d,
        }

        # Residualize for pooled effect size: subtract section mean
        sec_mean = (sum(a_vals) + sum(b_vals)) / (len(a_vals) + len(b_vals))
        all_resid_a.extend(v - sec_mean for v in a_vals)
        all_resid_b.extend(v - sec_mean for v in b_vals)

    pooled_d = cohens_d(all_resid_a, all_resid_b) if all_resid_a and all_resid_b else 0.0

    return {
        'per_section': per_section,
        'pooled': {
            'd': pooled_d,
            'n_sections': len(per_section),
            'n_a_total': len(all_resid_a),
            'n_b_total': len(all_resid_b),
        },
    }


# ============================================================
# Golden folio identification
# ============================================================

def identify_golden_folios(corpus, strata_assignments):
    """
    Find folios where paragraphs from the SAME section span multiple strata
    (at least one SHORT-or-below and one LONG).

    Args:
        corpus: list of paragraph dicts (each must have 'folio' and 'section').
        strata_assignments: dict mapping (folio, par_id) -> stratum name.

    Returns:
        list of folio IDs (sorted).
    """
    short_or_below = {'HEADER_ONLY', 'MINIMAL', 'SHORT'}

    # Group paragraphs by (folio, section)
    folio_section_strata = defaultdict(set)
    for par in corpus:
        folio = par.get('folio', '')
        section = par.get('section', '')
        par_id = par.get('id', '')
        key = (folio, par_id)
        stratum = strata_assignments.get(key, assign_stratum(par))
        folio_section_strata[(folio, section)].add(stratum)

    # Find folios where any section has both short-or-below and LONG
    golden = set()
    for (folio, section), strata in folio_section_strata.items():
        has_short_or_below = bool(strata & short_or_below)
        has_long = 'LONG' in strata
        if has_short_or_below and has_long:
            golden.add(folio)

    return sorted(golden)


# ============================================================
# Section residualization for scalar values
# ============================================================

def section_residualize_values(values, section_labels):
    """
    For a list of scalar values and corresponding section labels,
    subtract the per-section mean.

    Args:
        values: list of floats.
        section_labels: list of str (same length as values).

    Returns:
        list of floats: residualized values.
    """
    if not values:
        return []

    # Compute per-section means
    sec_sums = defaultdict(float)
    sec_counts = defaultdict(int)
    for v, s in zip(values, section_labels):
        sec_sums[s] += v
        sec_counts[s] += 1

    sec_means = {s: sec_sums[s] / sec_counts[s] for s in sec_sums}

    return [v - sec_means[s] for v, s in zip(values, section_labels)]


# ============================================================
# Statistical Tests (all from scratch, no scipy/numpy)
# ============================================================

def _rank(data):
    """
    Assign ranks to data values (1-based), handling ties with average rank.

    Args:
        data: list of floats.

    Returns:
        list of floats: ranks corresponding to each element in data.
    """
    n = len(data)
    if n == 0:
        return []

    # Create (value, original_index) pairs, sort by value
    indexed = sorted(enumerate(data), key=lambda x: x[1])

    ranks = [0.0] * n
    i = 0
    while i < n:
        # Find the run of tied values
        j = i
        while j < n and indexed[j][1] == indexed[i][1]:
            j += 1
        # Average rank for this tie group (1-based)
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j

    return ranks


def _normal_cdf(z):
    """
    Standard normal CDF using the Abramowitz & Stegun approximation.

    Accurate to ~1e-5.
    """
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0

    # Use symmetry for negative z
    if z < 0:
        return 1.0 - _normal_cdf(-z)

    # Constants for the approximation
    b0 = 0.2316419
    b1 = 0.319381530
    b2 = -0.356563782
    b3 = 1.781477937
    b4 = -1.821255978
    b5 = 1.330274429

    t = 1.0 / (1.0 + b0 * z)
    pdf = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    poly = t * (b1 + t * (b2 + t * (b3 + t * (b4 + t * b5))))

    return 1.0 - pdf * poly


def _chi2_cdf(x, df):
    """
    Chi-squared CDF using the regularized lower incomplete gamma function.

    Uses series expansion for the regularized gamma P(a, x).
    """
    if x <= 0.0 or df <= 0:
        return 0.0

    a = df / 2.0
    z = x / 2.0

    return _regularized_gamma_p(a, z)


def _regularized_gamma_p(a, x):
    """
    Regularized lower incomplete gamma function P(a, x) = gamma(a, x) / Gamma(a).

    Uses series expansion when x < a + 1, continued fraction otherwise.
    """
    if x < 0.0:
        return 0.0
    if x == 0.0:
        return 0.0

    if x < a + 1.0:
        return _gamma_series(a, x)
    else:
        return 1.0 - _gamma_cf(a, x)


def _gamma_series(a, x):
    """Series expansion for regularized lower incomplete gamma."""
    max_iter = 300
    eps = 1e-12

    ap = a
    s = 1.0 / a
    ds = s
    for _ in range(max_iter):
        ap += 1.0
        ds *= x / ap
        s += ds
        if abs(ds) < abs(s) * eps:
            break

    log_gamma_a = _log_gamma(a)
    return s * math.exp(-x + a * math.log(x) - log_gamma_a)


def _gamma_cf(a, x):
    """Continued fraction for regularized upper incomplete gamma (Lentz's method)."""
    max_iter = 300
    eps = 1e-12
    fpmin = 1e-30

    b = x + 1.0 - a
    c = 1.0 / fpmin
    d = 1.0 / b
    h = d

    for i in range(1, max_iter + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < fpmin:
            d = fpmin
        c = b + an / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break

    log_gamma_a = _log_gamma(a)
    return h * math.exp(-x + a * math.log(x) - log_gamma_a)


def _log_gamma(x):
    """
    Log-gamma function using Stirling's approximation with Lanczos coefficients.

    Accurate for x > 0.
    """
    if x <= 0:
        return 0.0

    # Lanczos approximation (g=7, n=9)
    coef = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7,
    ]

    if x < 0.5:
        # Reflection formula
        return math.log(math.pi / math.sin(math.pi * x)) - _log_gamma(1.0 - x)

    x -= 1.0
    a = coef[0]
    t = x + 7.5
    for i in range(1, 9):
        a += coef[i] / (x + i)

    return 0.5 * math.log(2.0 * math.pi) + (x + 0.5) * math.log(t) - t + math.log(a)


def _t_cdf(t_val, df):
    """
    CDF of Student's t-distribution using the regularized incomplete beta function.

    P(T <= t) = 1 - 0.5 * I_x(df/2, 1/2) where x = df/(df + t^2), for t >= 0.
    Uses symmetry for t < 0.
    """
    if df <= 0:
        return 0.5

    x = df / (df + t_val * t_val)

    # I_x(a, b) = regularized incomplete beta
    beta_val = _regularized_beta(x, df / 2.0, 0.5)

    if t_val >= 0:
        return 1.0 - 0.5 * beta_val
    else:
        return 0.5 * beta_val


def _regularized_beta(x, a, b):
    """
    Regularized incomplete beta function I_x(a, b).

    Uses continued fraction expansion (Lentz's method).
    """
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0

    # Use the symmetry relation if x > (a+1)/(a+b+2) for better convergence
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _regularized_beta(1.0 - x, b, a)

    # Compute the prefactor: x^a * (1-x)^b / (a * B(a,b))
    log_prefactor = (a * math.log(x) + b * math.log(1.0 - x)
                     - math.log(a)
                     - _log_beta(a, b))
    prefactor = math.exp(log_prefactor)

    # Continued fraction (Lentz's method)
    max_iter = 300
    eps = 1e-12
    fpmin = 1e-30

    # Modified Lentz's method
    c = 1.0
    d = 1.0 / max(1.0 - (a + b) * x / (a + 1.0), fpmin)
    h = d

    for m in range(1, max_iter + 1):
        # Even step: d_{2m}
        m2 = 2 * m
        num = m * (b - m) * x / ((a + m2 - 1.0) * (a + m2))
        d = 1.0 / max(1.0 + num * d, fpmin)
        c = max(1.0 + num / c, fpmin)
        h *= d * c

        # Odd step: d_{2m+1}
        num = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1.0))
        d = 1.0 / max(1.0 + num * d, fpmin)
        c = max(1.0 + num / c, fpmin)
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < eps:
            break

    return prefactor * h


def _log_beta(a, b):
    """Log of beta function: log(B(a,b)) = logGamma(a) + logGamma(b) - logGamma(a+b)."""
    return _log_gamma(a) + _log_gamma(b) - _log_gamma(a + b)


def mann_whitney_u(a, b):
    """
    Mann-Whitney U test (two-sided).

    Uses normal approximation for p-value.

    Args:
        a: list of floats (group A values).
        b: list of floats (group B values).

    Returns:
        dict with keys: 'U', 'z', 'p', 'n_a', 'n_b'.
    """
    n_a = len(a)
    n_b = len(b)

    if n_a == 0 or n_b == 0:
        return {'U': 0.0, 'z': 0.0, 'p': 1.0, 'n_a': n_a, 'n_b': n_b}

    # Combine and rank
    combined = [(v, 'a') for v in a] + [(v, 'b') for v in b]
    all_values = [v for v, _ in combined]
    ranks = _rank(all_values)

    # Sum of ranks for group A
    r_a = sum(ranks[i] for i in range(n_a))

    # U statistic for group A
    u_a = r_a - n_a * (n_a + 1) / 2.0
    # U statistic for group B
    u_b = n_a * n_b - u_a

    # Use the smaller U
    u = min(u_a, u_b)

    # Normal approximation
    mu = n_a * n_b / 2.0

    # Handle ties in variance calculation
    n = n_a + n_b
    # Count tie groups
    sorted_vals = sorted(all_values)
    tie_correction = 0.0
    i = 0
    while i < n:
        j = i
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        t = j - i
        if t > 1:
            tie_correction += t ** 3 - t
        i = j

    sigma_sq = (n_a * n_b / 12.0) * (n + 1 - tie_correction / (n * (n - 1))) if n > 1 else 0.0

    if sigma_sq <= 0:
        return {'U': u, 'z': 0.0, 'p': 1.0, 'n_a': n_a, 'n_b': n_b}

    sigma = math.sqrt(sigma_sq)
    z = (u - mu) / sigma

    # Two-sided p-value
    p = 2.0 * _normal_cdf(-abs(z))
    p = min(p, 1.0)

    return {'U': u, 'z': z, 'p': p, 'n_a': n_a, 'n_b': n_b}


def kruskal_wallis(groups):
    """
    Kruskal-Wallis H test.

    Args:
        groups: list of lists of floats.

    Returns:
        dict with keys: 'H', 'df', 'p'.
    """
    # Filter out empty groups
    groups = [g for g in groups if len(g) > 0]
    k = len(groups)

    if k < 2:
        return {'H': 0.0, 'df': 0, 'p': 1.0}

    # Combine all values and rank
    all_values = []
    group_labels = []
    for gi, g in enumerate(groups):
        for v in g:
            all_values.append(v)
            group_labels.append(gi)

    n = len(all_values)
    if n < 3:
        return {'H': 0.0, 'df': k - 1, 'p': 1.0}

    ranks = _rank(all_values)

    # Sum of ranks per group
    rank_sums = [0.0] * k
    group_sizes = [0] * k
    for i, gi in enumerate(group_labels):
        rank_sums[gi] += ranks[i]
        group_sizes[gi] += 1

    # H statistic
    h = (12.0 / (n * (n + 1))) * sum(
        rank_sums[gi] ** 2 / group_sizes[gi] for gi in range(k)
    ) - 3.0 * (n + 1)

    # Tie correction
    sorted_vals = sorted(all_values)
    tie_correction = 0.0
    i = 0
    while i < n:
        j = i
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        t = j - i
        if t > 1:
            tie_correction += t ** 3 - t
        i = j

    denom = 1.0 - tie_correction / (n ** 3 - n) if n > 1 else 1.0
    if denom > 0:
        h /= denom

    df = k - 1
    p = 1.0 - _chi2_cdf(h, df)
    p = max(0.0, min(1.0, p))

    return {'H': h, 'df': df, 'p': p}


def ks_test(a, b):
    """
    Two-sample Kolmogorov-Smirnov test.

    Uses the standard asymptotic formula for p-value.

    Args:
        a: list of floats (sample A).
        b: list of floats (sample B).

    Returns:
        dict with keys: 'D', 'p'.
    """
    n_a = len(a)
    n_b = len(b)

    if n_a == 0 or n_b == 0:
        return {'D': 0.0, 'p': 1.0}

    # Sort both samples
    a_sorted = sorted(a)
    b_sorted = sorted(b)

    # Merge and compute CDFs using two-pointer approach.
    # When values are equal, advance both pointers to handle ties correctly.
    d_max = 0.0
    i = 0
    j = 0
    while i < n_a and j < n_b:
        if a_sorted[i] < b_sorted[j]:
            i += 1
        elif a_sorted[i] > b_sorted[j]:
            j += 1
        else:
            # Equal values: advance both pointers
            i += 1
            j += 1
        cdf_a = i / n_a
        cdf_b = j / n_b
        d = abs(cdf_a - cdf_b)
        if d > d_max:
            d_max = d

    # Asymptotic p-value: P(D > d) ~ 2 * sum_{k=1}^{inf} (-1)^(k+1) * exp(-2*k^2*lambda^2)
    # where lambda = D * sqrt(n_eff), n_eff = sqrt(n_a * n_b / (n_a + n_b))
    n_eff = math.sqrt(n_a * n_b / (n_a + n_b))
    lam = (n_eff + 0.12 + 0.11 / n_eff) * d_max  # Stephens correction

    if lam <= 0:
        return {'D': d_max, 'p': 1.0}

    # Kolmogorov survival function (series expansion)
    p = 0.0
    for k in range(1, 101):
        term = 2.0 * ((-1) ** (k + 1)) * math.exp(-2.0 * k * k * lam * lam)
        p += term
        if abs(term) < 1e-12:
            break

    p = max(0.0, min(1.0, p))

    return {'D': d_max, 'p': p}


def spearman_rho(x, y):
    """
    Spearman rank correlation.

    Uses t-distribution approximation for p-value.

    Args:
        x: list of floats.
        y: list of floats.

    Returns:
        dict with keys: 'rho', 'p', 'n'.
    """
    n = len(x)
    if n != len(y):
        raise ValueError(f"x and y must have same length: {len(x)} vs {len(y)}")

    if n < 3:
        return {'rho': 0.0, 'p': 1.0, 'n': n}

    # Rank both variables
    rank_x = _rank(x)
    rank_y = _rank(y)

    # Pearson correlation on ranks
    mean_rx = sum(rank_x) / n
    mean_ry = sum(rank_y) / n

    cov_xy = sum((rank_x[i] - mean_rx) * (rank_y[i] - mean_ry) for i in range(n))
    var_x = sum((rank_x[i] - mean_rx) ** 2 for i in range(n))
    var_y = sum((rank_y[i] - mean_ry) ** 2 for i in range(n))

    denom = math.sqrt(var_x * var_y)
    if denom < 1e-12:
        return {'rho': 0.0, 'p': 1.0, 'n': n}

    rho = cov_xy / denom

    # Clamp rho to [-1, 1] for numerical safety
    rho = max(-1.0, min(1.0, rho))

    # t-test for significance: t = rho * sqrt((n-2) / (1 - rho^2))
    if abs(rho) >= 1.0 - 1e-12:
        # Perfect correlation
        return {'rho': rho, 'p': 0.0, 'n': n}

    t_val = rho * math.sqrt((n - 2) / (1.0 - rho * rho))
    df = n - 2

    # Two-sided p-value from t-distribution
    p = 2.0 * (1.0 - _t_cdf(abs(t_val), df))
    p = max(0.0, min(1.0, p))

    return {'rho': rho, 'p': p, 'n': n}


def chi_squared_contingency(table):
    """
    Chi-squared test on a contingency table.

    Args:
        table: dict of dicts: row_label -> col_label -> count.
            Example: {'A': {'X': 10, 'Y': 20}, 'B': {'X': 15, 'Y': 25}}

    Returns:
        dict with keys: 'chi2', 'df', 'p', 'V' (Cramer's V).
    """
    if not table:
        return {'chi2': 0.0, 'df': 0, 'p': 1.0, 'V': 0.0}

    rows = sorted(table.keys())
    # Collect all column keys
    all_cols = set()
    for r in rows:
        all_cols.update(table[r].keys())
    cols = sorted(all_cols)

    n_rows = len(rows)
    n_cols = len(cols)

    if n_rows < 2 or n_cols < 2:
        return {'chi2': 0.0, 'df': 0, 'p': 1.0, 'V': 0.0}

    # Build observed matrix
    observed = []
    for r in rows:
        row_vals = []
        for c in cols:
            row_vals.append(table[r].get(c, 0))
        observed.append(row_vals)

    # Row and column totals
    row_totals = [sum(observed[i]) for i in range(n_rows)]
    col_totals = [sum(observed[i][j] for i in range(n_rows)) for j in range(n_cols)]
    grand_total = sum(row_totals)

    if grand_total == 0:
        return {'chi2': 0.0, 'df': 0, 'p': 1.0, 'V': 0.0}

    # Expected frequencies and chi-squared
    chi2 = 0.0
    for i in range(n_rows):
        for j in range(n_cols):
            expected = row_totals[i] * col_totals[j] / grand_total
            if expected > 0:
                chi2 += (observed[i][j] - expected) ** 2 / expected

    df = (n_rows - 1) * (n_cols - 1)
    p = 1.0 - _chi2_cdf(chi2, df) if df > 0 else 1.0
    p = max(0.0, min(1.0, p))

    # Cramer's V
    min_dim = min(n_rows - 1, n_cols - 1)
    if min_dim > 0 and grand_total > 0:
        v = math.sqrt(chi2 / (grand_total * min_dim))
    else:
        v = 0.0

    return {'chi2': chi2, 'df': df, 'p': p, 'V': v}
