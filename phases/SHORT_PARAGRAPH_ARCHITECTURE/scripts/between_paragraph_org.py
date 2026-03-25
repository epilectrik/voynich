"""
Phase 625: SHORT_PARAGRAPH_ARCHITECTURE -- Script 3: Between-Paragraph Organization

Investigates folio-level organization of short paragraphs:
  T1: HEADER_ONLY as structural punctuation (zone transition + dependency tests)
  T2: Specification-to-execution ratio by stratum
  T3: Line-length gradient by folio paragraph count
  T4: Within-folio paragraph homogeneity by folio paragraph count
  T5: Gallows transition grammar by folio paragraph count

All tests run at POOLED and SECTION-CONTROLLED (within-Recipe) levels.

Input:
  - build_corpus() from shared chain
  - C1398 zone centroids from paragraph_program_typing.json

Output: results/between_paragraph_org.json
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from phases.SHORT_PARAGRAPH_ARCHITECTURE.scripts.shared_625 import (
    build_corpus, assign_stratum, get_all_tokens, extract_paragraph_features,
    extract_gallows_info, classify_paragraph_zone, jsd,
    STRATA, STRATUM_ORDER, FEATURE_NAMES, CATEGORIES, RESULTS_DIR, RNG, N_PERM,
    round_floats, chi_squared_contingency, mann_whitney_u, spearman_rho, cohens_d,
    section_residualize_values, euclidean_dist,
)

# ============================================================
# Load C1398 zone centroids
# ============================================================

ZONE_NAMES = {
    0: 'THERMAL_QO',
    1: 'CONTAINMENT_SEALING',
    2: 'OPERATION_ITERATION',
    3: 'MONITORING_PHASE',
}


def load_zone_centroids():
    """Load zone centroids from paragraph_program_typing.json (C1398)."""
    path = (_PROJECT_ROOT / 'phases' / 'PARAGRAPH_PROGRAM_TYPING'
            / 'results' / 'paragraph_program_typing.json')
    with open(path) as f:
        data = json.load(f)
    raw = data['T1_clustering']['centroids']
    centroids = {}
    for idx_str, centroid_dict in raw.items():
        zone_name = ZONE_NAMES[int(idx_str)]
        # Extract only the 8 category dimensions
        cat_vec = {}
        for cat in CATEGORIES:
            cat_vec[cat] = centroid_dict.get(cat, 0.0)
        centroids[zone_name] = cat_vec
    return centroids


# ============================================================
# Helpers
# ============================================================

def compute_category_profile(paragraph):
    """
    Compute the 8-category fraction profile for a paragraph's tokens.
    Returns dict mapping category name -> fraction.
    """
    tokens = get_all_tokens(paragraph)
    if not tokens:
        return {cat: 0.0 for cat in CATEGORIES}
    cat_counts = Counter()
    for t in tokens:
        c = t.get('category', 'UNKNOWN')
        if c in CATEGORIES:
            cat_counts[c] += 1
    total = sum(cat_counts.values())
    if total == 0:
        return {cat: 0.0 for cat in CATEGORIES}
    return {cat: cat_counts.get(cat, 0) / total for cat in CATEGORIES}


def category_profile_vector(profile):
    """Convert category profile dict to a list in CATEGORIES order."""
    return [profile.get(cat, 0.0) for cat in CATEGORIES]


def classify_zone(paragraph, zone_centroids):
    """Classify a paragraph into its nearest C1398 zone."""
    profile = compute_category_profile(paragraph)
    return classify_paragraph_zone(profile, zone_centroids)


def folio_paragraph_count_group(n_paras):
    """Classify folio by paragraph count: LOW (2-4), MED (5-8), HIGH (9+)."""
    if n_paras <= 4:
        return 'LOW'
    elif n_paras <= 8:
        return 'MED'
    else:
        return 'HIGH'


FPC_GROUPS = ['LOW', 'MED', 'HIGH']


def kruskal_wallis_local(groups):
    """
    Kruskal-Wallis H test from scratch.
    groups: list of lists of floats.
    """
    groups = [g for g in groups if len(g) > 0]
    k = len(groups)
    if k < 2:
        return {'H': 0.0, 'df': 0, 'p': 1.0}

    all_values = []
    group_labels = []
    for gi, g in enumerate(groups):
        for v in g:
            all_values.append(v)
            group_labels.append(gi)

    n = len(all_values)
    if n < 3:
        return {'H': 0.0, 'df': k - 1, 'p': 1.0}

    ranks = _rank_values(all_values)

    rank_sums = [0.0] * k
    group_sizes = [0] * k
    for i, gi in enumerate(group_labels):
        rank_sums[gi] += ranks[i]
        group_sizes[gi] += 1

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
    p = 1.0 - _chi2_cdf_approx(h, df)
    p = max(0.0, min(1.0, p))

    return {'H': h, 'df': df, 'p': p}


def _rank_values(data):
    """Assign ranks (1-based, average ties)."""
    n = len(data)
    if n == 0:
        return []
    indexed = sorted(enumerate(data), key=lambda x: x[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k_idx in range(i, j):
            ranks[indexed[k_idx][0]] = avg_rank
        i = j
    return ranks


def _chi2_cdf_approx(x, df):
    """Chi-squared CDF via regularized gamma."""
    if x <= 0.0 or df <= 0:
        return 0.0
    a = df / 2.0
    z = x / 2.0
    return _regularized_gamma_p(a, z)


def _regularized_gamma_p(a, x):
    if x < 0.0 or x == 0.0:
        return 0.0
    if x < a + 1.0:
        return _gamma_series(a, x)
    else:
        return 1.0 - _gamma_cf(a, x)


def _gamma_series(a, x):
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
    if x <= 0:
        return 0.0
    coef = [
        0.99999999999980993, 676.5203681218851, -1259.1392167224028,
        771.32342877765313, -176.61502916214059, 12.507343278686905,
        -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
    ]
    if x < 0.5:
        return math.log(math.pi / math.sin(math.pi * x)) - _log_gamma(1.0 - x)
    x -= 1.0
    a = coef[0]
    t = x + 7.5
    for i in range(1, 9):
        a += coef[i] / (x + i)
    return 0.5 * math.log(2.0 * math.pi) + (x + 0.5) * math.log(t) - t + math.log(a)


def _normal_cdf(z):
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0
    if z < 0:
        return 1.0 - _normal_cdf(-z)
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


def fisher_combine_p(p_values):
    """Fisher's method to combine independent p-values.
    chi2 = -2 * sum(log(p_i)), df = 2*k, then chi2 CDF.
    """
    valid = [p for p in p_values if p is not None and p > 0]
    if not valid:
        return 1.0
    k = len(valid)
    chi2 = -2.0 * sum(math.log(p) for p in valid)
    df = 2 * k
    p = 1.0 - _chi2_cdf_approx(chi2, df)
    return max(0.0, min(1.0, p))


# ============================================================
# Main
# ============================================================

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Phase 625 / Script 3: Between-Paragraph Organization")
    print("=" * 70)

    # ----------------------------------------------------------
    # Build corpus
    # ----------------------------------------------------------
    print("\n[1] Building corpus...")
    corpus = build_corpus()
    zone_centroids = load_zone_centroids()

    # Flatten to list of (folio, section, paragraph, stratum, zone)
    all_paras = []  # list of dicts
    for folio, fdata in sorted(corpus.items()):
        section = fdata['section']
        for pidx, para in enumerate(fdata['paragraphs']):
            stratum = assign_stratum(para)
            zone = classify_zone(para, zone_centroids)
            feats = extract_paragraph_features(para)
            gallows = extract_gallows_info(para)
            cat_profile = compute_category_profile(para)
            n_tokens = len(get_all_tokens(para))
            all_paras.append({
                'folio': folio,
                'section': section,
                'para_idx': pidx,
                'para': para,
                'stratum': stratum,
                'zone': zone,
                'features': feats,
                'feature_vector': [feats[f] for f in FEATURE_NAMES],
                'gallows': gallows,
                'cat_profile': cat_profile,
                'cat_vector': category_profile_vector(cat_profile),
                'n_tokens': n_tokens,
            })

    n_folios = len(corpus)
    n_paragraphs = len(all_paras)
    print(f"  Corpus: {n_folios} folios, {n_paragraphs} paragraphs")

    # Group by folio for folio-level analyses
    folio_paras = defaultdict(list)
    for p in all_paras:
        folio_paras[p['folio']].append(p)

    # Sort paragraphs within each folio by para_idx (reading order)
    for folio in folio_paras:
        folio_paras[folio].sort(key=lambda x: x['para_idx'])

    # ==============================================================
    # T1: HEADER_ONLY as structural punctuation
    # ==============================================================
    print("\n[2] T1: HEADER_ONLY punctuation analysis...")

    # --- Zone transition test ---
    # Identify HEADER_ONLY paragraphs with both predecessor and successor
    cross_ho_zone_changes = 0
    cross_ho_total = 0
    baseline_zone_changes = 0
    baseline_total = 0
    # For permutation test: store per-folio data
    folio_zone_data = {}  # folio -> list of (is_ho, zone)

    for folio, plist in folio_paras.items():
        if len(plist) < 2:
            continue
        zones = [p['zone'] for p in plist]
        strata = [p['stratum'] for p in plist]
        folio_zone_data[folio] = list(zip(strata, zones))

        for i in range(len(plist)):
            if strata[i] == 'HEADER_ONLY' and 0 < i < len(plist) - 1:
                # Has predecessor and successor
                if zones[i - 1] != zones[i + 1]:
                    cross_ho_zone_changes += 1
                cross_ho_total += 1

        # Baseline: consecutive NON-HEADER_ONLY paragraphs
        for i in range(len(plist) - 1):
            if strata[i] != 'HEADER_ONLY' and strata[i + 1] != 'HEADER_ONLY':
                if zones[i] != zones[i + 1]:
                    baseline_zone_changes += 1
                baseline_total += 1

    cross_ho_rate = cross_ho_zone_changes / cross_ho_total if cross_ho_total > 0 else 0.0
    baseline_rate = baseline_zone_changes / baseline_total if baseline_total > 0 else 0.0

    print(f"  HEADER_ONLY with neighbors: {cross_ho_total}")
    print(f"  Cross-HO zone change rate: {cross_ho_rate:.3f}")
    print(f"  Baseline zone change rate: {baseline_rate:.3f}")

    # Permutation test: shuffle HEADER_ONLY positions within folios
    print(f"  Running permutation test ({N_PERM} permutations)...")
    observed_diff = cross_ho_rate - baseline_rate
    null_diffs = []
    rng_perm = RNG

    for _ in range(N_PERM):
        perm_cross_ho_changes = 0
        perm_cross_ho_total = 0
        for folio, sz_list in folio_zone_data.items():
            strata_copy = [s for s, z in sz_list]
            zones_copy = [z for s, z in sz_list]
            n_items = len(strata_copy)
            # Identify HO positions and shuffle them
            ho_indices = [i for i, s in enumerate(strata_copy) if s == 'HEADER_ONLY']
            non_ho_indices = [i for i, s in enumerate(strata_copy) if s != 'HEADER_ONLY']
            if not ho_indices or len(non_ho_indices) < 2:
                continue
            # Shuffle: reassign HEADER_ONLY label to random positions
            all_indices = list(range(n_items))
            rng_perm.shuffle(all_indices)
            shuffled_strata = ['NOT_HO'] * n_items
            for idx in all_indices[:len(ho_indices)]:
                shuffled_strata[idx] = 'HEADER_ONLY'

            for i in range(n_items):
                if shuffled_strata[i] == 'HEADER_ONLY' and 0 < i < n_items - 1:
                    if zones_copy[i - 1] != zones_copy[i + 1]:
                        perm_cross_ho_changes += 1
                    perm_cross_ho_total += 1

        perm_rate = perm_cross_ho_changes / perm_cross_ho_total if perm_cross_ho_total > 0 else 0.0
        null_diffs.append(perm_rate)

    # p-value: fraction of null >= observed cross_ho_rate
    perm_p = sum(1 for nd in null_diffs if nd >= cross_ho_rate) / len(null_diffs) if null_diffs else 1.0
    punctuation_verdict = 'PUNCTUATION' if cross_ho_rate > baseline_rate and perm_p < 0.05 else 'NO_PUNCTUATION'

    print(f"  Permutation p-value: {perm_p:.4f}")
    print(f"  Verdict: {punctuation_verdict}")

    # --- Dependency test (C845 challenge) ---
    # Paragraphs that FOLLOW a HEADER_ONLY vs all others
    print("  Running dependency test...")
    post_ho_paras = []
    other_paras = []
    post_ho_set = set()

    for folio, plist in folio_paras.items():
        for i in range(len(plist)):
            if i > 0 and plist[i - 1]['stratum'] == 'HEADER_ONLY':
                post_ho_paras.append(plist[i])
                post_ho_set.add((plist[i]['folio'], plist[i]['para_idx']))

    for p in all_paras:
        if (p['folio'], p['para_idx']) not in post_ho_set and p['stratum'] != 'HEADER_ONLY':
            other_paras.append(p)

    features_significant = []
    dep_details = {}
    for fi, fname in enumerate(FEATURE_NAMES):
        post_vals = [p['feature_vector'][fi] for p in post_ho_paras if p['n_tokens'] > 0]
        other_vals = [p['feature_vector'][fi] for p in other_paras if p['n_tokens'] > 0]
        if len(post_vals) >= 3 and len(other_vals) >= 3:
            mw = mann_whitney_u(post_vals, other_vals)
            d = cohens_d(post_vals, other_vals)
            dep_details[fname] = {
                'mw_p': mw['p'],
                'd': d,
                'mean_post_ho': sum(post_vals) / len(post_vals),
                'mean_other': sum(other_vals) / len(other_vals),
            }
            if mw['p'] < 0.05:
                features_significant.append(fname)

    dependency_verdict = 'DEPENDENT' if len(features_significant) >= 3 else 'INDEPENDENT'

    print(f"  Post-HO paragraphs: {len(post_ho_paras)}")
    print(f"  Features significant (p<0.05): {len(features_significant)} -> {features_significant}")
    print(f"  Dependency verdict: {dependency_verdict}")

    # --- Section-controlled (within-Recipe) ---
    recipe_post_ho = [p for p in post_ho_paras if p['section'] == 'H']
    recipe_other = [p for p in other_paras if p['section'] == 'H']
    sec_dep_features_sig = []
    sec_dep_details = {}
    for fi, fname in enumerate(FEATURE_NAMES):
        post_vals = [p['feature_vector'][fi] for p in recipe_post_ho if p['n_tokens'] > 0]
        other_vals = [p['feature_vector'][fi] for p in recipe_other if p['n_tokens'] > 0]
        if len(post_vals) >= 3 and len(other_vals) >= 3:
            mw = mann_whitney_u(post_vals, other_vals)
            d = cohens_d(post_vals, other_vals)
            sec_dep_details[fname] = {'mw_p': mw['p'], 'd': d}
            if mw['p'] < 0.05:
                sec_dep_features_sig.append(fname)

    t1_result = {
        'n_header_only': sum(1 for p in all_paras if p['stratum'] == 'HEADER_ONLY'),
        'n_with_neighbors': cross_ho_total,
        'cross_ho_zone_change_rate': cross_ho_rate,
        'baseline_zone_change_rate': baseline_rate,
        'permutation_p': perm_p,
        'punctuation_verdict': punctuation_verdict,
        'dependency_test': {
            'n_post_ho': len(post_ho_paras),
            'n_other': len(other_paras),
            'features_significant': features_significant,
            'feature_details': dep_details,
            'dependency_verdict': dependency_verdict,
        },
        'section_controlled': {
            'scope': 'within_Recipe',
            'n_post_ho_recipe': len(recipe_post_ho),
            'n_other_recipe': len(recipe_other),
            'features_significant': sec_dep_features_sig,
            'feature_details': sec_dep_details,
            'dependency_verdict': (
                'DEPENDENT' if len(sec_dep_features_sig) >= 3 else 'INDEPENDENT'
            ),
        },
    }

    # ==============================================================
    # T2: Specification-to-execution ratio by stratum
    # ==============================================================
    print("\n[3] T2: Specification/execution ratio by stratum...")

    EXEC_CATS = {'THERMAL', 'FLOW', 'CONTAINMENT'}
    SPEC_CATS = {'MARKING', 'STAGING'}

    def compute_spec_exec_ratio(paragraph):
        tokens = get_all_tokens(paragraph)
        if not tokens:
            return 1.0  # default
        exec_count = 0
        spec_count = 0
        for t in tokens:
            cat = t.get('category', 'UNKNOWN')
            if cat in EXEC_CATS:
                exec_count += 1
            elif cat in SPEC_CATS:
                spec_count += 1
        return (spec_count + 0.5) / (exec_count + 0.5)

    # Compute ratio for each paragraph
    for p in all_paras:
        p['spec_exec_ratio'] = compute_spec_exec_ratio(p['para'])

    # Group by stratum
    stratum_ratios = defaultdict(list)
    stratum_sections = defaultdict(list)
    for p in all_paras:
        stratum_ratios[p['stratum']].append(p['spec_exec_ratio'])
        stratum_sections[p['stratum']].append(p['section'])

    by_stratum = {}
    for s in STRATUM_ORDER:
        vals = stratum_ratios.get(s, [])
        by_stratum[s] = {
            'mean': sum(vals) / len(vals) if vals else 0.0,
            'median': sorted(vals)[len(vals) // 2] if vals else 0.0,
            'n': len(vals),
        }
        print(f"  {s}: mean={by_stratum[s]['mean']:.3f}, n={len(vals)}")

    # Kruskal-Wallis
    kw_groups = [stratum_ratios.get(s, []) for s in STRATUM_ORDER]
    kw = kruskal_wallis_local(kw_groups)
    print(f"  Kruskal-Wallis: H={kw['H']:.3f}, p={kw['p']:.6f}")

    # HEADER_ONLY vs LONG
    ho_vals = stratum_ratios.get('HEADER_ONLY', [])
    long_vals = stratum_ratios.get('LONG', [])
    ho_mean = sum(ho_vals) / len(ho_vals) if ho_vals else 0.0
    long_mean = sum(long_vals) / len(long_vals) if long_vals else 0.0
    mw_ho_long = mann_whitney_u(ho_vals, long_vals)
    d_ho_long = cohens_d(ho_vals, long_vals)
    exceeds_2x = ho_mean > 2.0 * long_mean if long_mean > 0 else False

    print(f"  HO mean: {ho_mean:.3f}, LONG mean: {long_mean:.3f}")
    print(f"  HO/LONG ratio: {ho_mean / long_mean:.2f}x" if long_mean > 0 else "  LONG mean=0")
    print(f"  Exceeds 2x: {exceeds_2x}")

    # Section-controlled (within Recipe)
    recipe_ratios = defaultdict(list)
    for p in all_paras:
        if p['section'] == 'H':
            recipe_ratios[p['stratum']].append(p['spec_exec_ratio'])

    sec_by_stratum = {}
    for s in STRATUM_ORDER:
        vals = recipe_ratios.get(s, [])
        sec_by_stratum[s] = {
            'mean': sum(vals) / len(vals) if vals else 0.0,
            'n': len(vals),
        }

    sec_kw = kruskal_wallis_local([recipe_ratios.get(s, []) for s in STRATUM_ORDER])
    sec_ho = recipe_ratios.get('HEADER_ONLY', [])
    sec_long = recipe_ratios.get('LONG', [])
    sec_ho_mean = sum(sec_ho) / len(sec_ho) if sec_ho else 0.0
    sec_long_mean = sum(sec_long) / len(sec_long) if sec_long else 0.0
    sec_mw = mann_whitney_u(sec_ho, sec_long) if sec_ho and sec_long else {'U': 0, 'z': 0, 'p': 1.0, 'n_a': 0, 'n_b': 0}
    sec_d = cohens_d(sec_ho, sec_long) if sec_ho and sec_long else 0.0

    t2_result = {
        'by_stratum': by_stratum,
        'kw': {'H': kw['H'], 'p': kw['p']},
        'ho_vs_long': {
            'ratio_ho': ho_mean,
            'ratio_long': long_mean,
            'mw_p': mw_ho_long['p'],
            'd': d_ho_long,
            'exceeds_2x': exceeds_2x,
        },
        'section_controlled': {
            'scope': 'within_Recipe',
            'by_stratum': sec_by_stratum,
            'kw': {'H': sec_kw['H'], 'p': sec_kw['p']},
            'ho_vs_long': {
                'ratio_ho': sec_ho_mean,
                'ratio_long': sec_long_mean,
                'mw_p': sec_mw['p'],
                'd': sec_d,
                'exceeds_2x': sec_ho_mean > 2.0 * sec_long_mean if sec_long_mean > 0 else False,
            },
        },
    }

    # ==============================================================
    # T3: Line-length gradient by folio paragraph count
    # ==============================================================
    print("\n[4] T3: Line-length gradient by folio paragraph count...")

    # Group folios by paragraph count group
    fpc_groups = defaultdict(list)  # group -> list of folios
    for folio, plist in folio_paras.items():
        n_paras_in_folio = len(plist)
        if n_paras_in_folio < 2:
            continue
        group = folio_paragraph_count_group(n_paras_in_folio)
        fpc_groups[group].append((folio, plist))

    t3_result = {}
    for group in FPC_GROUPS:
        folios_in_group = fpc_groups.get(group, [])
        rho_values = []
        folio_count = 0
        per_folio_p = []

        for folio, plist in folios_in_group:
            # Filter to paragraphs with body lines
            body_paras = [p for p in plist if len(p['para'].get('body_lines', [])) > 0]
            if len(body_paras) < 2:
                continue

            # First body line token count for each paragraph
            first_body_lengths = []
            ordinals = []
            for idx, p in enumerate(body_paras):
                body_lines = p['para'].get('body_lines', [])
                if body_lines:
                    first_body_lengths.append(body_lines[0]['length'])
                    ordinals.append(idx)

            if len(first_body_lengths) < 3:
                continue

            sp = spearman_rho(ordinals, first_body_lengths)
            rho_values.append(sp['rho'])
            per_folio_p.append(sp['p'])
            folio_count += 1

        mean_rho = sum(rho_values) / len(rho_values) if rho_values else 0.0
        # Fisher's method to combine p-values for pooled significance
        pooled_p = fisher_combine_p(per_folio_p) if per_folio_p else 1.0

        t3_result[group] = {
            'mean_rho': mean_rho,
            'n_folios': folio_count,
            'pooled_p': pooled_p,
        }
        print(f"  {group}: mean_rho={mean_rho:.3f}, n_folios={folio_count}, pooled_p={pooled_p:.6f}")

    # Gradient steepens for HIGH?
    high_rho = t3_result.get('HIGH', {}).get('mean_rho', 0.0)
    low_rho = t3_result.get('LOW', {}).get('mean_rho', 0.0)
    gradient_steepens = high_rho < low_rho  # More negative = steeper decline

    t3_result['gradient_steepens'] = gradient_steepens
    print(f"  Gradient steepens for HIGH: {gradient_steepens}")

    # Section-controlled (within Recipe)
    sec_t3 = {}
    for group in FPC_GROUPS:
        folios_in_group = fpc_groups.get(group, [])
        rho_values = []
        folio_count = 0
        per_folio_p = []

        for folio, plist in folios_in_group:
            # Filter to Recipe section only
            recipe_body = [p for p in plist
                           if p['section'] == 'H'
                           and len(p['para'].get('body_lines', [])) > 0]
            if len(recipe_body) < 2:
                continue

            first_body_lengths = []
            ordinals = []
            for idx, p in enumerate(recipe_body):
                body_lines = p['para'].get('body_lines', [])
                if body_lines:
                    first_body_lengths.append(body_lines[0]['length'])
                    ordinals.append(idx)

            if len(first_body_lengths) < 3:
                continue

            sp = spearman_rho(ordinals, first_body_lengths)
            rho_values.append(sp['rho'])
            per_folio_p.append(sp['p'])
            folio_count += 1

        mean_rho = sum(rho_values) / len(rho_values) if rho_values else 0.0
        pooled_p = fisher_combine_p(per_folio_p) if per_folio_p else 1.0
        sec_t3[group] = {
            'mean_rho': mean_rho,
            'n_folios': folio_count,
            'pooled_p': pooled_p,
        }

    t3_result['section_controlled'] = {
        'scope': 'within_Recipe',
        **{g: sec_t3.get(g, {'mean_rho': 0.0, 'n_folios': 0, 'pooled_p': 1.0}) for g in FPC_GROUPS},
    }

    # ==============================================================
    # T4: Within-folio paragraph homogeneity by folio paragraph count
    # ==============================================================
    print("\n[5] T4: Within-folio homogeneity by folio paragraph count...")

    folio_jsd_by_group = defaultdict(list)
    folio_jsd_sections = defaultdict(list)

    for folio, plist in folio_paras.items():
        if len(plist) < 3:
            continue
        n_paras_in_folio = len(plist)
        group = folio_paragraph_count_group(n_paras_in_folio)

        # Compute pairwise JSD between paragraph category profiles
        profiles = [p['cat_vector'] for p in plist]
        jsd_values = []
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                # Only compute JSD if both have non-zero profiles
                if sum(profiles[i]) > 0 and sum(profiles[j]) > 0:
                    jsd_values.append(jsd(profiles[i], profiles[j]))

        if jsd_values:
            mean_jsd = sum(jsd_values) / len(jsd_values)
            folio_jsd_by_group[group].append(mean_jsd)
            folio_jsd_sections[group].append(plist[0]['section'])

    t4_result = {}
    for group in FPC_GROUPS:
        vals = folio_jsd_by_group.get(group, [])
        t4_result[group] = {
            'mean_jsd': sum(vals) / len(vals) if vals else 0.0,
            'n_folios': len(vals),
        }
        print(f"  {group}: mean_jsd={t4_result[group]['mean_jsd']:.4f}, n_folios={len(vals)}")

    # Kruskal-Wallis
    kw_jsd = kruskal_wallis_local([folio_jsd_by_group.get(g, []) for g in FPC_GROUPS])
    t4_result['kw'] = {'H': kw_jsd['H'], 'p': kw_jsd['p']}
    print(f"  Kruskal-Wallis: H={kw_jsd['H']:.3f}, p={kw_jsd['p']:.6f}")

    # HIGH vs LOW
    high_jsd = folio_jsd_by_group.get('HIGH', [])
    low_jsd = folio_jsd_by_group.get('LOW', [])
    if high_jsd and low_jsd:
        mw_jsd = mann_whitney_u(high_jsd, low_jsd)
        d_jsd = cohens_d(high_jsd, low_jsd)
    else:
        mw_jsd = {'U': 0, 'z': 0, 'p': 1.0, 'n_a': len(high_jsd), 'n_b': len(low_jsd)}
        d_jsd = 0.0
    t4_result['high_vs_low'] = {'mw_p': mw_jsd['p'], 'd': d_jsd}
    print(f"  HIGH vs LOW: mw_p={mw_jsd['p']:.6f}, d={d_jsd:.3f}")

    # Section-controlled (within Recipe)
    sec_folio_jsd = defaultdict(list)
    for folio, plist in folio_paras.items():
        recipe_paras_in = [p for p in plist if p['section'] == 'H']
        if len(recipe_paras_in) < 3:
            continue
        # Use total para count for group assignment (folio-level, not section-filtered)
        n_paras_in_folio = len(plist)
        group = folio_paragraph_count_group(n_paras_in_folio)

        profiles = [p['cat_vector'] for p in recipe_paras_in]
        jsd_values = []
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                if sum(profiles[i]) > 0 and sum(profiles[j]) > 0:
                    jsd_values.append(jsd(profiles[i], profiles[j]))
        if jsd_values:
            sec_folio_jsd[group].append(sum(jsd_values) / len(jsd_values))

    sec_t4 = {}
    for group in FPC_GROUPS:
        vals = sec_folio_jsd.get(group, [])
        sec_t4[group] = {
            'mean_jsd': sum(vals) / len(vals) if vals else 0.0,
            'n_folios': len(vals),
        }

    sec_kw_jsd = kruskal_wallis_local([sec_folio_jsd.get(g, []) for g in FPC_GROUPS])
    sec_high = sec_folio_jsd.get('HIGH', [])
    sec_low = sec_folio_jsd.get('LOW', [])
    if sec_high and sec_low:
        sec_mw_jsd = mann_whitney_u(sec_high, sec_low)
        sec_d_jsd = cohens_d(sec_high, sec_low)
    else:
        sec_mw_jsd = {'U': 0, 'z': 0, 'p': 1.0, 'n_a': len(sec_high), 'n_b': len(sec_low)}
        sec_d_jsd = 0.0

    t4_result['section_controlled'] = {
        'scope': 'within_Recipe',
        **{g: sec_t4.get(g, {'mean_jsd': 0.0, 'n_folios': 0}) for g in FPC_GROUPS},
        'kw': {'H': sec_kw_jsd['H'], 'p': sec_kw_jsd['p']},
        'high_vs_low': {'mw_p': sec_mw_jsd['p'], 'd': sec_d_jsd},
    }

    # ==============================================================
    # T5: Gallows transition grammar by folio paragraph count
    # ==============================================================
    print("\n[6] T5: Gallows transition grammar by folio paragraph count...")

    GALLOWS_TYPES = ['k', 't', 'p', 'f']

    def build_gallows_transitions(folio_para_list):
        """
        Build gallows-type transition matrix for sequential paragraphs.
        Only includes paragraphs that are gallows-initial.
        Returns dict-of-dicts transition table and total count.
        """
        # Filter to gallows-initial paragraphs (in reading order)
        gallows_initial = []
        for p in folio_para_list:
            gi = p['gallows']
            if gi['gallows_initial']:
                gallows_initial.append(gi['gallows_type'])

        # Build transition counts
        table = {g1: {g2: 0 for g2 in GALLOWS_TYPES} for g1 in GALLOWS_TYPES}
        n_transitions = 0
        for i in range(len(gallows_initial) - 1):
            g_from = gallows_initial[i]
            g_to = gallows_initial[i + 1]
            if g_from in GALLOWS_TYPES and g_to in GALLOWS_TYPES:
                table[g_from][g_to] += 1
                n_transitions += 1

        return table, n_transitions

    def merge_tables(tables):
        """Merge a list of transition tables."""
        merged = {g1: {g2: 0 for g2 in GALLOWS_TYPES} for g1 in GALLOWS_TYPES}
        total = 0
        for table, n in tables:
            for g1 in GALLOWS_TYPES:
                for g2 in GALLOWS_TYPES:
                    merged[g1][g2] += table[g1][g2]
            total += n
        return merged, total

    def self_transition_rate(table, n_transitions):
        """Fraction of transitions that are same gallows type."""
        if n_transitions == 0:
            return 0.0
        self_count = sum(table[g][g] for g in GALLOWS_TYPES)
        return self_count / n_transitions

    t5_result = {}
    for group in FPC_GROUPS:
        folios_in_group = fpc_groups.get(group, [])
        group_tables = []
        for folio, plist in folios_in_group:
            table, n_trans = build_gallows_transitions(plist)
            if n_trans > 0:
                group_tables.append((table, n_trans))

        if group_tables:
            merged, total_n = merge_tables(group_tables)
            chi2_result = chi_squared_contingency(merged)
            self_rate = self_transition_rate(merged, total_n)
        else:
            chi2_result = {'chi2': 0.0, 'df': 0, 'p': 1.0, 'V': 0.0}
            total_n = 0
            self_rate = 0.0

        t5_result[group] = {
            'chi2': chi2_result['chi2'],
            'V': chi2_result['V'],
            'chi2_p': chi2_result['p'],
            'self_rate': self_rate,
            'n_transitions': total_n,
        }
        print(f"  {group}: V={chi2_result['V']:.3f}, self_rate={self_rate:.3f}, n_trans={total_n}")

    # Section-controlled (within Recipe)
    sec_t5 = {}
    for group in FPC_GROUPS:
        folios_in_group = fpc_groups.get(group, [])
        group_tables = []
        for folio, plist in folios_in_group:
            recipe_plist = [p for p in plist if p['section'] == 'H']
            if len(recipe_plist) < 2:
                continue
            table, n_trans = build_gallows_transitions(recipe_plist)
            if n_trans > 0:
                group_tables.append((table, n_trans))

        if group_tables:
            merged, total_n = merge_tables(group_tables)
            chi2_result = chi_squared_contingency(merged)
            self_rate = self_transition_rate(merged, total_n)
        else:
            chi2_result = {'chi2': 0.0, 'df': 0, 'p': 1.0, 'V': 0.0}
            total_n = 0
            self_rate = 0.0

        sec_t5[group] = {
            'chi2': chi2_result['chi2'],
            'V': chi2_result['V'],
            'chi2_p': chi2_result['p'],
            'self_rate': self_rate,
            'n_transitions': total_n,
        }

    t5_result['section_controlled'] = {
        'scope': 'within_Recipe',
        **{g: sec_t5.get(g, {'chi2': 0, 'V': 0, 'chi2_p': 1.0, 'self_rate': 0, 'n_transitions': 0})
           for g in FPC_GROUPS},
    }

    # ==============================================================
    # Assemble results
    # ==============================================================
    results = {
        'metadata': {
            'phase': 625,
            'script': 3,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_folios': n_folios,
            'n_paragraphs': n_paragraphs,
        },
        'T1_punctuation': t1_result,
        'T2_spec_exec_ratio': t2_result,
        'T3_length_gradient': t3_result,
        'T4_within_folio_homogeneity': t4_result,
        'T5_gallows_transitions': t5_result,
    }

    results = round_floats(results)

    out_path = RESULTS_DIR / 'between_paragraph_org.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results written to {out_path}")

    # ==============================================================
    # SYNTHESIS
    # ==============================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    print(f"\n  T1: HEADER_ONLY punctuation")
    print(f"    Zone-change rate across HO: {cross_ho_rate:.3f} vs baseline: {baseline_rate:.3f}")
    print(f"    Permutation p={perm_p:.4f} -> {punctuation_verdict}")
    print(f"    Dependency: {dependency_verdict} ({len(features_significant)}/11 features significant)")
    if features_significant:
        print(f"    Significant features: {', '.join(features_significant)}")
    sec_dep_v = t1_result['section_controlled']['dependency_verdict']
    print(f"    Section-controlled dependency: {sec_dep_v}")

    print(f"\n  T2: Specification/execution ratio")
    print(f"    HEADER_ONLY mean: {ho_mean:.3f}")
    print(f"    LONG mean:        {long_mean:.3f}")
    if long_mean > 0:
        print(f"    Ratio HO/LONG:    {ho_mean / long_mean:.2f}x")
    print(f"    P9 (exceeds 2x):  {exceeds_2x}")
    print(f"    KW across strata: H={kw['H']:.3f}, p={kw['p']:.6f}")

    print(f"\n  T3: Line-length gradient by folio para count")
    for g in FPC_GROUPS:
        info = t3_result.get(g, {})
        print(f"    {g}: rho={info.get('mean_rho', 0):.3f}, "
              f"n_folios={info.get('n_folios', 0)}, p={info.get('pooled_p', 1.0):.6f}")
    print(f"    Gradient steepens for HIGH: {gradient_steepens}")

    print(f"\n  T4: Within-folio homogeneity (mean pairwise JSD)")
    for g in FPC_GROUPS:
        info = t4_result.get(g, {})
        print(f"    {g}: JSD={info.get('mean_jsd', 0):.4f}, n_folios={info.get('n_folios', 0)}")
    print(f"    KW: H={kw_jsd['H']:.3f}, p={kw_jsd['p']:.6f}")
    print(f"    HIGH vs LOW: d={d_jsd:.3f}, p={mw_jsd['p']:.6f}")

    print(f"\n  T5: Gallows transition grammar")
    for g in FPC_GROUPS:
        info = t5_result.get(g, {})
        print(f"    {g}: V={info.get('V', 0):.3f}, self_rate={info.get('self_rate', 0):.3f}, "
              f"n_trans={info.get('n_transitions', 0)}")

    print("\n" + "=" * 70)
    print("Script 3 complete.")
    print("=" * 70)


if __name__ == '__main__':
    main()
