"""Phase 562 T2: Folio Budget & Paragraph Cloud Instantiation

Instantiates each folio with:
  A. Domain budget (6D fracs + deviation from section template + Mahalanobis distance)
  B. Paragraph emphasis cloud (per-qualifying-paragraph 6D vectors, cloud centroid,
     dispersion, EMD to section cloud, per-paragraph cloud-relative position)
  C. Headless regime (structured object per C1574: hl_rate, pseudo_head_dist,
     subtype_dist, displaced_nonkt_rate, suffix_bifurcation, deviation_from_section)
  D. Per-folio hazard posture, closure class, headless subtype, terminal distributions

Input:
  - phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t1_domain_decomposition.json
  - phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t1_section_templates.json

Output:
  - phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t2_folio_budgets.json
"""
import json
import math
import time
import os
from pathlib import Path
from collections import Counter, defaultdict

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from scipy.stats import wasserstein_distance as wd_1d
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# =====================================================================
# Constants
# =====================================================================

DOMAINS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
DOMAIN_ORDER = {d: i for i, d in enumerate(DOMAINS)}
N_DOMAINS = len(DOMAINS)

HAZARD_POSTURES = ['IMMUNE', 'ZERO', 'LOW', 'HIGH']
CLOSURE_CLASSES = ['SPEC_OPEN', 'WORK_TRANSPARENT', 'WORK_SEMI',
                   'CLOSE_OPAQUE', 'CLOSE_TRANSITIONAL']
HEADLESS_SUBTYPES = ['PSEUDO_D', 'PSEUDO_I', 'PSEUDO_L',
                     'PARAMETRIC_CPF', 'OTHER_HEADLESS']
TERMINALS = ['bare', 'h', 'r', 'y', 'n', 'm', 'l']

MIN_PARA_BODY_LINES = 3
MIN_PARA_TOKENS = 15

RIDGE = 1e-6  # Regularization for singular covariance


# =====================================================================
# Derived evaluation target functions (identical to T1)
# =====================================================================

def derive_hazard_posture(token):
    """Derive hazard posture from token composition using Tier 2 rules."""
    if token.get('head') == 'k':
        return 'IMMUNE'
    if token.get('head') == 'e' and token.get('term') == 'y':
        return 'ZERO'
    if token.get('head') == 'a' and (token.get('i_count') or 0) >= 2:
        return 'ZERO'
    if token.get('has_quenching_mod') and token.get('head') in ('e', 'o', 't'):
        return 'ZERO'
    if token.get('is_safe_pathway'):
        return 'ZERO'
    if token.get('head') == 'a' and token.get('term') in ('l', 'r'):
        return 'HIGH'
    if not token.get('source_immune') and token.get('frame_hazard') == 'HIGH':
        return 'HIGH'
    return 'LOW'


def derive_closure_class(token):
    """Derive closure class from terminal opacity and line zone."""
    opacity = token.get('terminal_opacity')
    term = token.get('term')
    zone = token.get('line_zone', 'WORK')
    if term == 'm':
        return 'CLOSE_TRANSITIONAL'
    if zone == 'SPEC' and opacity == 'TRANSPARENT':
        return 'SPEC_OPEN'
    if zone == 'WORK' and opacity == 'TRANSPARENT':
        return 'WORK_TRANSPARENT'
    if zone == 'CLOSE' and opacity == 'OPAQUE':
        return 'CLOSE_OPAQUE'
    if opacity in ('OPAQUE', None) and zone == 'WORK':
        return 'WORK_SEMI'
    return 'WORK_SEMI'


def derive_headless_subtype(token):
    """Derive headless subtype from pseudo-head atom."""
    if token.get('domain') != 'HEADLESS':
        return 'HEADED'
    ph = token.get('pseudo_head_atom')
    if ph == 'd':
        return 'PSEUDO_D'
    if ph == 'i':
        return 'PSEUDO_I'
    if ph == 'l':
        return 'PSEUDO_L'
    if ph in ('c', 'p', 'f'):
        return 'PARAMETRIC_CPF'
    return 'OTHER_HEADLESS'


# =====================================================================
# Linear algebra helpers
# =====================================================================

def _mat_inv_6(cov_list, ridge=RIDGE):
    """Invert a 6x6 covariance matrix with ridge regularization.

    Returns inverse as list-of-lists. Uses numpy if available, otherwise
    falls back to pure-Python Gauss-Jordan.
    """
    n = len(cov_list)
    if HAS_NUMPY:
        C = np.array(cov_list, dtype=float)
        C += ridge * np.eye(n)
        try:
            C_inv = np.linalg.inv(C)
        except np.linalg.LinAlgError:
            # Pseudoinverse as last resort
            C_inv = np.linalg.pinv(C)
        return C_inv.tolist()
    else:
        # Pure-Python Gauss-Jordan elimination
        # Augment with identity
        aug = []
        for i in range(n):
            row = [cov_list[i][j] + (ridge if i == j else 0.0) for j in range(n)]
            row += [1.0 if i == j else 0.0 for j in range(n)]
            aug.append(row)
        for col in range(n):
            # Partial pivoting
            max_row = col
            max_val = abs(aug[col][col])
            for row in range(col + 1, n):
                if abs(aug[row][col]) > max_val:
                    max_val = abs(aug[row][col])
                    max_row = row
            aug[col], aug[max_row] = aug[max_row], aug[col]
            pivot = aug[col][col]
            if abs(pivot) < 1e-15:
                pivot = 1e-15
            for j in range(2 * n):
                aug[col][j] /= pivot
            for row in range(n):
                if row == col:
                    continue
                factor = aug[row][col]
                for j in range(2 * n):
                    aug[row][j] -= factor * aug[col][j]
        # Extract inverse
        return [aug[i][n:2*n] for i in range(n)]


def mahalanobis(x, mu, cov_inv):
    """Mahalanobis distance: d = sqrt((x-mu)^T C_inv (x-mu))."""
    n = len(x)
    diff = [x[i] - mu[i] for i in range(n)]
    # diff^T @ cov_inv @ diff
    inner = 0.0
    for i in range(n):
        for j in range(n):
            inner += diff[i] * cov_inv[i][j] * diff[j]
    # Numerical guard: inner may be slightly negative due to floating point
    return math.sqrt(max(inner, 0.0))


# =====================================================================
# Distribution helpers
# =====================================================================

def dist_from_counter(counter, categories):
    """Normalize Counter over fixed category set."""
    total = sum(counter.values())
    if total == 0:
        return {c: 1.0 / len(categories) for c in categories}
    return {c: counter.get(c, 0) / total for c in categories}


def token_to_domain_vec(tokens):
    """Convert token list to 6D domain fraction vector."""
    if not tokens:
        return [1.0 / N_DOMAINS] * N_DOMAINS
    counter = Counter(t['domain'] for t in tokens)
    total = len(tokens)
    return [counter.get(d, 0) / total for d in DOMAINS]


def covariance_6d(vectors):
    """Compute 6x6 covariance matrix from list of 6D vectors."""
    n = len(vectors)
    if n < 2:
        return [[0.0] * N_DOMAINS for _ in range(N_DOMAINS)]
    means = [0.0] * N_DOMAINS
    for v in vectors:
        for i in range(N_DOMAINS):
            means[i] += v[i]
    means = [m / n for m in means]
    cov = [[0.0] * N_DOMAINS for _ in range(N_DOMAINS)]
    for v in vectors:
        for i in range(N_DOMAINS):
            for j in range(N_DOMAINS):
                cov[i][j] += (v[i] - means[i]) * (v[j] - means[j])
    for i in range(N_DOMAINS):
        for j in range(N_DOMAINS):
            cov[i][j] /= (n - 1)
    return cov


def mean_6d(vectors):
    """Compute mean of list of 6D vectors."""
    n = len(vectors)
    if n == 0:
        return [1.0 / N_DOMAINS] * N_DOMAINS
    m = [0.0] * N_DOMAINS
    for v in vectors:
        for i in range(N_DOMAINS):
            m[i] += v[i]
    return [x / n for x in m]


def deviation_vector(vec, ref):
    """Signed deviation: vec - ref per dimension."""
    return [vec[i] - ref[i] for i in range(len(vec))]


def emd_6d(cloud_a, cloud_b):
    """Earth Mover's Distance between two 6D point clouds.

    Computed as sum of per-dimension 1D Wasserstein distances.
    Each cloud is a list of 6D vectors.
    """
    if not cloud_a or not cloud_b:
        return 0.0

    total = 0.0
    for dim in range(N_DOMAINS):
        vals_a = sorted(v[dim] for v in cloud_a)
        vals_b = sorted(v[dim] for v in cloud_b)
        if HAS_SCIPY:
            total += wd_1d(vals_a, vals_b)
        else:
            total += _manual_wasserstein_1d(vals_a, vals_b)
    return total


def _manual_wasserstein_1d(u_sorted, v_sorted):
    """Manual 1D Wasserstein distance (area between CDFs)."""
    # Merge all unique values
    all_vals = sorted(set(u_sorted + v_sorted))
    if not all_vals:
        return 0.0

    nu = len(u_sorted)
    nv = len(v_sorted)
    area = 0.0
    ui = 0
    vi = 0
    prev_x = all_vals[0]

    for x in all_vals:
        # CDF values at prev_x
        cdf_u = ui / nu
        cdf_v = vi / nv
        area += abs(cdf_u - cdf_v) * (x - prev_x)
        # Advance indices
        while ui < nu and u_sorted[ui] <= x:
            ui += 1
        while vi < nv and v_sorted[vi] <= x:
            vi += 1
        prev_x = x

    return area


def nn_rank(idx, distances):
    """Nearest-neighbor rank for point at idx within a distance list.

    Returns 0-based rank (0 = closest to centroid, n-1 = farthest).
    """
    dist_with_idx = sorted(enumerate(distances), key=lambda t: t[1])
    for rank, (i, _) in enumerate(dist_with_idx):
        if i == idx:
            return rank
    return len(distances) - 1


# =====================================================================
# Main
# =====================================================================

def main():
    t0 = time.time()
    print("=== Phase 562 T2: Folio Budget & Paragraph Cloud ===")

    # ---------------------------------------------------------------
    # Load inputs
    # ---------------------------------------------------------------
    base_dir = Path(__file__).resolve().parents[2]

    corpus_path = (base_dir / 'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL' /
                   'results' / 't1_domain_decomposition.json')
    templates_path = (base_dir / 'SECTION_TEMPLATE_TRACE_EXECUTOR' /
                      'results' / 't1_section_templates.json')

    print(f"  Loading corpus from {corpus_path}...")
    with open(corpus_path) as f:
        corpus_data = json.load(f)
    corpus = corpus_data['corpus_tokens']
    print(f"  Loaded {len(corpus)} tokens")

    print(f"  Loading templates from {templates_path}...")
    with open(templates_path) as f:
        templates_data = json.load(f)
    templates = templates_data['templates']
    print(f"  Loaded templates for sections: {list(templates.keys())}")

    # ---------------------------------------------------------------
    # Step 0: Derive evaluation targets for all tokens
    # ---------------------------------------------------------------
    print("  Deriving evaluation targets...")
    for tok in corpus:
        tok['hazard_posture'] = derive_hazard_posture(tok)
        tok['closure_class'] = derive_closure_class(tok)
        tok['headless_subtype_derived'] = derive_headless_subtype(tok)

    # ---------------------------------------------------------------
    # Step 1: Pre-compute groupings
    # ---------------------------------------------------------------
    print("  Grouping tokens...")

    # By folio
    by_folio = defaultdict(list)
    # By folio -> paragraph -> line
    by_fol_para = defaultdict(lambda: defaultdict(list))
    by_fol_para_line = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    # Folio -> section mapping
    folio_section = {}

    for tok in corpus:
        fol = tok['folio']
        pi = tok['paragraph_idx']
        li = tok['line']
        by_folio[fol].append(tok)
        by_fol_para[fol][pi].append(tok)
        by_fol_para_line[fol][pi][li].append(tok)
        folio_section[fol] = tok['section']

    folios = sorted(by_folio.keys())
    print(f"  {len(folios)} folios")

    # ---------------------------------------------------------------
    # Step 2: Pre-compute section template inverse covariances
    # ---------------------------------------------------------------
    print("  Pre-computing section covariance inverses...")
    section_cov_inv = {}
    section_domain_fracs_vec = {}
    section_para_cloud_vectors = {}
    section_para_cloud_mean = {}
    section_para_cloud_cov = {}
    section_para_cloud_cov_inv = {}
    section_headless_ecology = {}
    section_hazard_prior = {}
    section_closure_prior = {}
    section_hl_subtype_prior = {}

    for sec, tmpl in templates.items():
        # Domain covariance inverse
        cov = tmpl['domain_priors']['covariance']
        section_cov_inv[sec] = _mat_inv_6(cov)
        # Domain fracs as ordered vector
        fracs = tmpl['domain_priors']['fracs']
        section_domain_fracs_vec[sec] = [fracs[d] for d in DOMAINS]

        # Paragraph cloud prior
        pcl = tmpl['paragraph_cloud_prior']
        section_para_cloud_vectors[sec] = pcl['vectors']
        section_para_cloud_mean[sec] = pcl['mean']
        section_para_cloud_cov[sec] = pcl['covariance']
        if pcl['n_qualifying_paragraphs'] >= 2:
            section_para_cloud_cov_inv[sec] = _mat_inv_6(pcl['covariance'])
        else:
            section_para_cloud_cov_inv[sec] = _mat_inv_6(
                [[0.0] * N_DOMAINS for _ in range(N_DOMAINS)])

        # Headless ecology
        section_headless_ecology[sec] = tmpl['headless_ecology']

        # Distribution priors
        section_hazard_prior[sec] = tmpl['hazard_posture_prior']
        section_closure_prior[sec] = tmpl['closure_class_prior']
        section_hl_subtype_prior[sec] = tmpl['headless_subtype_prior']

    # ---------------------------------------------------------------
    # Step 3: Build per-folio budgets
    # ---------------------------------------------------------------
    print("\n  Building per-folio budgets...")
    folio_budgets = {}

    for fol in folios:
        ftoks = by_folio[fol]
        sec = folio_section[fol]
        n_tokens = len(ftoks)

        # ===== A. Domain budget =====
        domain_vec = token_to_domain_vec(ftoks)
        domain_fracs = {d: domain_vec[i] for i, d in enumerate(DOMAINS)}

        # Deviation from section template
        sec_vec = section_domain_fracs_vec[sec]
        dev_vec = deviation_vector(domain_vec, sec_vec)
        domain_deviation = {d: round(dev_vec[i], 5) for i, d in enumerate(DOMAINS)}

        # Mahalanobis distance to section centroid
        m_dist = mahalanobis(domain_vec, sec_vec, section_cov_inv[sec])

        domain_budget = {
            'fracs': {d: round(v, 5) for d, v in domain_fracs.items()},
            'deviation_from_section': domain_deviation,
            'mahalanobis_to_section': round(m_dist, 4),
            'n_tokens': n_tokens,
            'section': sec,
        }

        # ===== B. Paragraph emphasis cloud =====
        para_vectors = []
        para_meta = []
        folio_paras = by_fol_para[fol]

        for pi in sorted(folio_paras.keys()):
            ptoks = folio_paras[pi]
            # Count body lines
            lines_in_para = by_fol_para_line[fol][pi]
            n_lines = len(lines_in_para)
            body_lines = max(0, n_lines - 2) if n_lines >= 3 else 0
            if body_lines < MIN_PARA_BODY_LINES:
                continue
            if len(ptoks) < MIN_PARA_TOKENS:
                continue
            vec = token_to_domain_vec(ptoks)
            para_vectors.append(vec)
            para_meta.append({
                'paragraph_idx': pi,
                'n_tokens': len(ptoks),
                'n_lines': n_lines,
                'body_lines': body_lines,
            })

        # Cloud centroid and dispersion
        if para_vectors:
            cloud_centroid = mean_6d(para_vectors)
            cloud_cov = covariance_6d(para_vectors) if len(para_vectors) >= 2 else (
                [[0.0] * N_DOMAINS for _ in range(N_DOMAINS)])
            cloud_cov_inv = _mat_inv_6(cloud_cov) if len(para_vectors) >= 2 else (
                _mat_inv_6([[0.0] * N_DOMAINS for _ in range(N_DOMAINS)]))

            # EMD to section-level paragraph cloud
            sec_cloud = section_para_cloud_vectors.get(sec, [])
            cloud_emd = emd_6d(para_vectors, sec_cloud)

            # Per-paragraph cloud-relative position
            para_distances_to_centroid = []
            for vec in para_vectors:
                d = mahalanobis(vec, cloud_centroid, cloud_cov_inv)
                para_distances_to_centroid.append(d)

            # Nearest-neighbor ranks
            for idx in range(len(para_vectors)):
                para_meta[idx]['mahalanobis_to_folio_centroid'] = round(
                    para_distances_to_centroid[idx], 4)
                para_meta[idx]['nn_rank'] = nn_rank(
                    idx, para_distances_to_centroid)
                para_meta[idx]['domain_vec'] = [round(v, 5) for v in para_vectors[idx]]

        else:
            cloud_centroid = [1.0 / N_DOMAINS] * N_DOMAINS
            cloud_cov = [[0.0] * N_DOMAINS for _ in range(N_DOMAINS)]
            cloud_emd = 0.0

        paragraph_cloud = {
            'n_qualifying_paragraphs': len(para_vectors),
            'centroid': [round(v, 5) for v in cloud_centroid],
            'dispersion': [[round(c, 6) for c in row] for row in cloud_cov],
            'emd_to_section_cloud': round(cloud_emd, 5),
            'paragraphs': para_meta,
        }

        # ===== C. Headless regime =====
        hl_tokens = [t for t in ftoks if t['domain'] == 'HEADLESS']
        n_hl = len(hl_tokens)
        hl_rate = n_hl / n_tokens if n_tokens > 0 else 0.0

        # Pseudo-head distribution
        pseudo_atoms = ['d', 'i', 'l', 'c', 'p', 'f']
        if n_hl > 0:
            ph_counter = Counter(
                t.get('pseudo_head_atom', 'unknown') for t in hl_tokens)
            pseudo_head_dist = {}
            for atom in pseudo_atoms:
                pseudo_head_dist[atom] = round(
                    ph_counter.get(atom, 0) / n_hl, 5)
            pseudo_head_dist['other'] = round(
                sum(v for k, v in ph_counter.items()
                    if k not in pseudo_atoms) / n_hl, 5)
        else:
            pseudo_head_dist = {a: 0.0 for a in pseudo_atoms}
            pseudo_head_dist['other'] = 0.0

        # Headless subtype distribution
        hl_subtype_counter = Counter(
            t['headless_subtype_derived'] for t in hl_tokens)
        subtype_dist = dist_from_counter(hl_subtype_counter, HEADLESS_SUBTYPES)
        subtype_dist = {k: round(v, 5) for k, v in subtype_dist.items()}

        # Displaced non-kt rate
        displaced = sum(1 for t in hl_tokens
                        if t.get('has_displaced_head_terminal'))
        displaced_nonkt_rate = displaced / max(n_hl, 1)

        # Suffix bifurcation
        hl_binary_sfx = sum(1 for t in hl_tokens
                            if t.get('suffix') and len(t['suffix']) == 1)
        parametric_hl = [t for t in hl_tokens
                         if t.get('pseudo_head_atom') in ('c', 'p', 'f')]
        parametric_sfx_rate = (
            sum(1 for t in parametric_hl
                if t.get('suffix') and len(t['suffix']) > 0) /
            max(len(parametric_hl), 1))

        # Deviation from section headless ecology
        sec_hl = section_headless_ecology.get(sec, {})
        hl_deviation = {}
        hl_deviation['hl_rate'] = round(
            hl_rate - sec_hl.get('hl_rate', 0), 5)
        sec_ph = sec_hl.get('pseudo_head_dist', {})
        hl_deviation['pseudo_head_dist'] = {
            k: round(pseudo_head_dist.get(k, 0) - sec_ph.get(k, 0), 5)
            for k in list(set(list(pseudo_head_dist.keys()) +
                              list(sec_ph.keys())))
        }
        hl_deviation['displaced_nonkt_rate'] = round(
            displaced_nonkt_rate - sec_hl.get('displaced_nonkt_rate', 0), 5)
        sec_sfx = sec_hl.get('suffix_bifurcation', {})
        hl_deviation['suffix_bifurcation'] = {
            'binary_sfx_rate': round(
                hl_binary_sfx / max(n_hl, 1) -
                sec_sfx.get('binary_sfx_rate', 0), 5),
            'parametric_sfx_rate': round(
                parametric_sfx_rate -
                sec_sfx.get('parametric_sfx_rate', 0), 5),
        }

        headless_regime = {
            'hl_rate': round(hl_rate, 5),
            'pseudo_head_dist': pseudo_head_dist,
            'subtype_dist': subtype_dist,
            'displaced_nonkt_rate': round(displaced_nonkt_rate, 5),
            'suffix_bifurcation': {
                'binary_sfx_rate': round(
                    hl_binary_sfx / max(n_hl, 1), 5),
                'parametric_sfx_rate': round(parametric_sfx_rate, 5),
            },
            'deviation_from_section': hl_deviation,
        }

        # ===== D. Per-folio distributions =====
        # Hazard posture distribution
        hazard_counter = Counter(t['hazard_posture'] for t in ftoks)
        hazard_dist = dist_from_counter(hazard_counter, HAZARD_POSTURES)
        hazard_dist = {k: round(v, 5) for k, v in hazard_dist.items()}

        # Closure class distribution
        closure_counter = Counter(t['closure_class'] for t in ftoks)
        closure_dist = dist_from_counter(closure_counter, CLOSURE_CLASSES)
        closure_dist = {k: round(v, 5) for k, v in closure_dist.items()}

        # Headless subtype distribution (already computed above as subtype_dist)
        # But D asks for ALL tokens' headless subtype, not just headless ones
        # The headless subtype for HEADED tokens is 'HEADED' which isn't in
        # HEADLESS_SUBTYPES. For T4 E2 mode, they need the distribution among
        # headless tokens only, which is already subtype_dist.

        # Terminal distribution
        term_counter = Counter(t.get('term', 'bare') for t in ftoks)
        term_dist = {}
        for term in TERMINALS:
            term_dist[term] = round(
                term_counter.get(term, 0) / max(n_tokens, 1), 5)

        # ===== Assemble folio budget =====
        folio_budgets[fol] = {
            'folio': fol,
            'section': sec,
            'n_tokens': n_tokens,
            'domain_budget': domain_budget,
            'paragraph_cloud': paragraph_cloud,
            'headless_regime': headless_regime,
            'hazard_posture_dist': hazard_dist,
            'closure_class_dist': closure_dist,
            'headless_subtype_dist': subtype_dist,
            'terminal_dist': term_dist,
        }

    # ---------------------------------------------------------------
    # Step 4: Validation
    # ---------------------------------------------------------------
    print("\n=== Validation ===")
    validations = {}
    all_pass = True

    # V1: All folios from corpus represented
    corpus_folios = set(t['folio'] for t in corpus)
    budget_folios = set(folio_budgets.keys())
    v1 = corpus_folios == budget_folios
    validations['all_folios_represented'] = {
        'pass': v1,
        'expected': len(corpus_folios),
        'actual': len(budget_folios),
    }
    print(f"  V1 All folios represented: {v1} "
          f"(expected={len(corpus_folios)}, actual={len(budget_folios)})")
    if not v1:
        all_pass = False
        missing = corpus_folios - budget_folios
        extra = budget_folios - corpus_folios
        if missing:
            print(f"    Missing: {sorted(missing)}")
        if extra:
            print(f"    Extra: {sorted(extra)}")

    # V2: Domain fracs sum to 1.0 for each folio
    frac_failures = []
    for fol, budget in folio_budgets.items():
        frac_sum = sum(budget['domain_budget']['fracs'].values())
        if abs(frac_sum - 1.0) > 0.001:
            frac_failures.append((fol, frac_sum))
    v2 = len(frac_failures) == 0
    validations['domain_fracs_sum_to_1'] = {
        'pass': v2,
        'n_failures': len(frac_failures),
    }
    print(f"  V2 Domain fracs sum to 1.0: {v2} "
          f"({len(frac_failures)} failures)")
    if not v2:
        all_pass = False
        for fol, s in frac_failures[:5]:
            print(f"    {fol}: {s:.5f}")

    # V3: At least 50 folios have qualifying paragraph clouds
    folios_with_clouds = sum(
        1 for b in folio_budgets.values()
        if b['paragraph_cloud']['n_qualifying_paragraphs'] > 0)
    v3 = folios_with_clouds >= 50
    validations['min_50_folios_with_clouds'] = {
        'pass': v3,
        'actual': folios_with_clouds,
    }
    print(f"  V3 Folios with qualifying clouds >= 50: {v3} "
          f"(actual={folios_with_clouds})")
    if not v3:
        all_pass = False

    # V4: Mahalanobis distances reasonable (mean ~1-3)
    all_m_dist = [b['domain_budget']['mahalanobis_to_section']
                  for b in folio_budgets.values()]
    mean_m = sum(all_m_dist) / len(all_m_dist)
    max_m = max(all_m_dist)
    min_m = min(all_m_dist)
    v4 = 0.5 <= mean_m <= 5.0
    validations['mahalanobis_reasonable'] = {
        'pass': v4,
        'mean': round(mean_m, 3),
        'min': round(min_m, 3),
        'max': round(max_m, 3),
    }
    print(f"  V4 Mahalanobis reasonable: {v4} "
          f"(mean={mean_m:.3f}, min={min_m:.3f}, max={max_m:.3f})")
    if not v4:
        all_pass = False

    # V5: Headless regime objects have all required fields
    required_hl_fields = ['hl_rate', 'pseudo_head_dist', 'subtype_dist',
                          'displaced_nonkt_rate', 'suffix_bifurcation',
                          'deviation_from_section']
    hl_field_failures = []
    for fol, budget in folio_budgets.items():
        hr = budget['headless_regime']
        missing = [f for f in required_hl_fields if f not in hr]
        if missing:
            hl_field_failures.append((fol, missing))
    v5 = len(hl_field_failures) == 0
    validations['headless_regime_complete'] = {
        'pass': v5,
        'n_failures': len(hl_field_failures),
    }
    print(f"  V5 Headless regime complete: {v5} "
          f"({len(hl_field_failures)} failures)")
    if not v5:
        all_pass = False
        for fol, missing in hl_field_failures[:3]:
            print(f"    {fol}: missing {missing}")

    # V6: Total qualifying paragraphs match T1 sum
    total_qualifying = sum(
        b['paragraph_cloud']['n_qualifying_paragraphs']
        for b in folio_budgets.values())
    t1_total_qualifying = sum(
        tmpl['paragraph_cloud_prior']['n_qualifying_paragraphs']
        for tmpl in templates.values())
    v6 = total_qualifying == t1_total_qualifying
    validations['qualifying_para_count_match'] = {
        'pass': v6,
        'folio_sum': total_qualifying,
        't1_sum': t1_total_qualifying,
    }
    print(f"  V6 Qualifying paragraph count: {v6} "
          f"(folio_sum={total_qualifying}, t1_sum={t1_total_qualifying})")
    if not v6:
        all_pass = False

    print(f"\n  Overall validation: {'PASS' if all_pass else 'FAIL'}")

    # ---------------------------------------------------------------
    # Step 5: Summary statistics
    # ---------------------------------------------------------------
    print("\n=== Summary ===")

    # Per-section stats
    section_budgets = defaultdict(list)
    for fol, budget in folio_budgets.items():
        section_budgets[budget['section']].append(budget)

    for sec in sorted(section_budgets.keys()):
        budgets = section_budgets[sec]
        n_folios = len(budgets)
        avg_tokens = sum(b['n_tokens'] for b in budgets) / n_folios
        avg_m_dist = sum(b['domain_budget']['mahalanobis_to_section']
                         for b in budgets) / n_folios
        n_with_cloud = sum(
            1 for b in budgets
            if b['paragraph_cloud']['n_qualifying_paragraphs'] > 0)
        total_paras = sum(b['paragraph_cloud']['n_qualifying_paragraphs']
                          for b in budgets)
        avg_hl_rate = sum(b['headless_regime']['hl_rate']
                          for b in budgets) / n_folios
        avg_emd = sum(b['paragraph_cloud']['emd_to_section_cloud']
                      for b in budgets if
                      b['paragraph_cloud']['n_qualifying_paragraphs'] > 0)
        n_cloud = max(n_with_cloud, 1)
        avg_emd /= n_cloud

        print(f"\n  Section {sec} ({n_folios} folios, "
              f"avg {avg_tokens:.0f} tokens/folio):")
        print(f"    Avg Mahalanobis to section: {avg_m_dist:.3f}")
        print(f"    Folios with cloud: {n_with_cloud}, "
              f"total qualifying paragraphs: {total_paras}")
        print(f"    Avg EMD to section cloud: {avg_emd:.4f}")
        print(f"    Avg HL rate: {avg_hl_rate:.4f}")

    # Top 5 most deviant folios
    print("\n  Top 5 most deviant folios (Mahalanobis):")
    ranked = sorted(folio_budgets.items(),
                    key=lambda x: x[1]['domain_budget']['mahalanobis_to_section'],
                    reverse=True)
    for fol, budget in ranked[:5]:
        m = budget['domain_budget']['mahalanobis_to_section']
        sec = budget['section']
        fracs = budget['domain_budget']['fracs']
        top_d = max(fracs, key=fracs.get)
        print(f"    {fol} ({sec}): M={m:.3f}, top domain={top_d} "
              f"({fracs[top_d]:.3f})")

    # ---------------------------------------------------------------
    # Step 6: Save output
    # ---------------------------------------------------------------
    output = {
        'metadata': {
            'phase': '562',
            'task': 'T2_folio_budget_paragraph_cloud',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'corpus_path': str(corpus_path),
            'templates_path': str(templates_path),
            'n_folios': len(folio_budgets),
            'n_total_tokens': len(corpus),
            'n_qualifying_paragraphs': total_qualifying,
        },
        'folio_budgets': folio_budgets,
        'validations': validations,
        'validation_pass': all_pass,
    }

    out_path = (Path(__file__).parent.parent / 'results' /
                't2_folio_budgets.json')
    print(f"\n  Writing to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    size_kb = os.path.getsize(out_path) / 1024
    elapsed = time.time() - t0
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== T2 Complete (validation: "
          f"{'PASS' if all_pass else 'FAIL'}) ===")


if __name__ == '__main__':
    main()
