#!/usr/bin/env python3
"""
Phase 412: PARAGRAPH_KERNEL_DYNAMICS
======================================
Tests whether within-folio paragraph kernel trajectory diversity mediates
the folio-level AXM residual (C1035, 57% irreducible).

Novel predictor: WITHIN-FOLIO PARAGRAPH KERNEL DIVERSITY — how different
a folio's paragraphs are from each other in kernel composition.

5-test battery:
  T1: PARAGRAPH_KERNEL_HETEROGENEITY (SD of per-paragraph kernel fracs vs AXM)
  T2: TRAJECTORY_SLOPE_DIVERSITY (variance of per-paragraph h_frac slopes vs AXM)
  T3: PARAGRAPH_TYPE_ENTROPY (Shannon entropy of HIGH_K/HIGH_H/BALANCED mix vs AXM)
  T4: INCREMENTAL_EXPLANATORY_POWER (add to C1035 baseline, dR² + LOO CV)
  T5: WITHIN_SECTION_VALIDATION (repeat T1 within each section)

Depends on: C965, C893, C944, C1022, C1035, C1152
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as scipy_stats

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

KERNEL_CHARS = {'k', 'h', 'e'}
MIN_PAR_TOKENS = 15      # Minimum tokens for paragraph kernel analysis
MIN_PAR_LINES = 4        # Minimum lines for trajectory slope
MIN_PARS_PER_FOLIO = 3   # Minimum qualifying paragraphs for heterogeneity
MIN_SECTION_FOLIOS = 8   # Minimum folios for within-section test


# ── Pure-Python Statistics ──────────────────────────────────────────

def round_floats(obj, digits=6):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def spearman_r(x, y):
    """Pure-Python Spearman rank correlation with two-tailed p-value."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    def _rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = avg_rank
            i = j + 1
        return ranks

    rx = _rank(list(x))
    ry = _rank(list(y))
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    sd_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    sd_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if sd_x == 0 or sd_y == 0:
        return 0.0, 1.0
    rho = cov / (sd_x * sd_y)
    rho = max(-1.0, min(1.0, rho))

    if n <= 2:
        return rho, 1.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-12))
    df = n - 2
    x_val = df / (df + t_stat ** 2)
    p = _betainc(df / 2.0, 0.5, x_val)
    return rho, p


def _betainc(a, b, x, n_iter=200):
    """Regularized incomplete beta function via continued fraction."""
    if x <= 0:
        return 1.0
    if x >= 1:
        return 0.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for m in range(n_iter):
        if m == 0:
            num = 1.0
        elif m % 2 == 0:
            k = m // 2
            num = (k * (b - k) * x) / ((a + 2*k - 1) * (a + 2*k))
        else:
            k = (m + 1) // 2
            num = -((a + k) * (a + b + k) * x) / ((a + 2*k) * (a + 2*k + 1))
        d = 1.0 + num * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < 1e-30:
            c = 1e-30
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-10:
            break
    return 1.0 - front * f


def shannon_entropy(counts_dict):
    """Shannon entropy in bits from a dict of counts."""
    total = sum(counts_dict.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts_dict.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


# ── OLS / LOO (from Phase 357, for Test 4) ─────────────────────────

def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-10)


def ols_fit(X, y):
    """OLS regression. Returns beta, y_pred, ss_res, r2."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, y_pred, ss_res, r2


def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    """F-test for nested model comparison."""
    df_res = n_obs - k_full
    if df_res <= 0 or ss_res_full <= 0:
        return 0.0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - scipy_stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


def build_dummies(labels):
    """Build dummy variables from categorical labels (drop first)."""
    unique = sorted(set(labels))
    if len(unique) <= 1:
        return np.zeros((len(labels), 0))
    dummies = np.zeros((len(labels), len(unique) - 1))
    for i, label in enumerate(labels):
        idx = unique.index(label)
        if idx > 0:
            dummies[i, idx - 1] = 1
    return dummies


def loo_cv_r2(X, y):
    """Leave-one-out cross-validated R2."""
    n = len(y)
    y_pred_loo = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_train, y_train = X[mask], y[mask]
        X_test = X[i:i+1]
        beta = np.linalg.lstsq(X_train, y_train, rcond=None)[0]
        y_pred_loo[i] = float(X_test @ beta)
    ss_res = np.sum((y - y_pred_loo) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ── Data Loading ────────────────────────────────────────────────────

def load_data():
    """Load transcript, build per-paragraph kernel data, merge with AXM."""
    print("Loading data...")

    # Load AXM residual data (72 valid folios)
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']
    valid_folios = sorted(folio_data.keys())
    print(f"  AXM data: {len(valid_folios)} folios")

    morph = Morphology()

    # Single B-pass: group tokens by (folio, paragraph, line)
    # Use par_initial to detect paragraph boundaries
    folio_pars = defaultdict(list)  # folio -> list of paragraphs
    current_par_tokens = []
    current_par_lines = defaultdict(list)  # line_key -> [tokens]
    current_folio = None
    par_idx = 0

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue

        folio = t.folio

        # Detect paragraph boundary
        if t.par_initial and current_par_tokens:
            # Save current paragraph
            folio_pars[current_folio].append({
                'tokens': current_par_tokens,
                'lines': dict(current_par_lines),
                'par_idx': par_idx,
            })
            current_par_tokens = []
            current_par_lines = defaultdict(list)
            par_idx += 1

        if folio != current_folio and current_par_tokens:
            # New folio: save paragraph, reset
            folio_pars[current_folio].append({
                'tokens': current_par_tokens,
                'lines': dict(current_par_lines),
                'par_idx': par_idx,
            })
            current_par_tokens = []
            current_par_lines = defaultdict(list)
            par_idx = 0

        current_folio = folio

        # Extract kernel chars from MIDDLE
        m = morph.extract(w)
        middle = m.middle if m else w
        kernels = [ch for ch in middle if ch in KERNEL_CHARS]

        tok_data = {
            'word': w,
            'folio': folio,
            'line': t.line,
            'section': t.section,
            'middle': middle,
            'kernels': kernels,
        }
        current_par_tokens.append(tok_data)
        current_par_lines[t.line].append(tok_data)

    # Save last paragraph
    if current_par_tokens:
        folio_pars[current_folio].append({
            'tokens': current_par_tokens,
            'lines': dict(current_par_lines),
            'par_idx': par_idx,
        })

    # Compute per-paragraph kernel stats
    folio_paragraph_stats = {}
    total_pars = 0

    for folio in valid_folios:
        pars = folio_pars.get(folio, [])
        par_stats = []
        for par in pars:
            tokens = par['tokens']
            n_tokens = len(tokens)
            n_lines = len(par['lines'])

            # Count kernel characters
            k_count = sum(t['kernels'].count('k') for t in tokens)
            h_count = sum(t['kernels'].count('h') for t in tokens)
            e_count = sum(t['kernels'].count('e') for t in tokens)
            total_kernel = k_count + h_count + e_count

            if total_kernel == 0:
                k_frac, h_frac, e_frac = 0, 0, 0
            else:
                k_frac = k_count / total_kernel
                h_frac = h_count / total_kernel
                e_frac = e_count / total_kernel

            # Classify paragraph type (C893 thresholds)
            if k_frac > 0.35:
                kernel_type = 'HIGH_K'
            elif h_frac > 0.50:
                kernel_type = 'HIGH_H'
            else:
                kernel_type = 'BALANCED'

            # Per-line kernel fractions (for trajectory slope)
            line_kernels = []
            for line_key in sorted(par['lines'].keys()):
                line_toks = par['lines'][line_key]
                lk = sum(t['kernels'].count('k') for t in line_toks)
                lh = sum(t['kernels'].count('h') for t in line_toks)
                le = sum(t['kernels'].count('e') for t in line_toks)
                lt = lk + lh + le
                if lt >= 3:  # Minimum kernel chars for reliable fraction
                    line_kernels.append({
                        'k_frac': lk / lt,
                        'h_frac': lh / lt,
                        'e_frac': le / lt,
                    })

            par_stats.append({
                'n_tokens': n_tokens,
                'n_lines': n_lines,
                'k_frac': k_frac,
                'h_frac': h_frac,
                'e_frac': e_frac,
                'total_kernel': total_kernel,
                'kernel_type': kernel_type,
                'line_kernels': line_kernels,
            })
            total_pars += 1

        folio_paragraph_stats[folio] = par_stats

    print(f"  Total paragraphs across {len(valid_folios)} valid folios: {total_pars}")

    # Report type distribution (validate against C893)
    all_types = Counter()
    for folio, pars in folio_paragraph_stats.items():
        for p in pars:
            if p['n_tokens'] >= MIN_PAR_TOKENS:
                all_types[p['kernel_type']] += 1
    print(f"  Type distribution (>={MIN_PAR_TOKENS} tokens): "
          f"HIGH_K={all_types['HIGH_K']} HIGH_H={all_types['HIGH_H']} "
          f"BALANCED={all_types['BALANCED']}")

    return {
        'folio_data': folio_data,
        'valid_folios': valid_folios,
        'folio_paragraph_stats': folio_paragraph_stats,
    }


# ── Test 1: Paragraph Kernel Heterogeneity ─────────────────────────

def test1_paragraph_kernel_heterogeneity(data):
    """T1: SD of per-paragraph kernel fracs vs folio AXM self-transition."""
    print("\n── Test 1: PARAGRAPH_KERNEL_HETEROGENEITY ──")

    folio_data = data['folio_data']
    valid_folios = data['valid_folios']
    par_stats = data['folio_paragraph_stats']

    # Compute per-folio heterogeneity
    hetero_folios = []
    axm_vals = []
    section_labels = []
    hetero_k = []
    hetero_h = []
    hetero_e = []

    for folio in valid_folios:
        pars = par_stats[folio]
        qualifying = [p for p in pars if p['n_tokens'] >= MIN_PAR_TOKENS]

        if len(qualifying) < MIN_PARS_PER_FOLIO:
            continue

        k_fracs = [p['k_frac'] for p in qualifying]
        h_fracs = [p['h_frac'] for p in qualifying]
        e_fracs = [p['e_frac'] for p in qualifying]

        sd_k = float(np.std(k_fracs))
        sd_h = float(np.std(h_fracs))
        sd_e = float(np.std(e_fracs))
        composite = math.sqrt(sd_k**2 + sd_h**2 + sd_e**2)

        hetero_folios.append(folio)
        axm_vals.append(folio_data[folio]['axm_self'])
        section_labels.append(folio_data[folio]['section'])
        hetero_k.append(sd_k)
        hetero_h.append(sd_h)
        hetero_e.append(sd_e)

    n = len(hetero_folios)
    print(f"  {n} folios qualify (>={MIN_PARS_PER_FOLIO} paragraphs with >={MIN_PAR_TOKENS} tokens)")

    composites = [math.sqrt(hetero_k[i]**2 + hetero_h[i]**2 + hetero_e[i]**2)
                  for i in range(n)]

    # Raw Spearman
    rho_raw, p_raw = spearman_r(composites, axm_vals)
    print(f"  Composite heterogeneity vs AXM: rho={rho_raw:.3f}, p={p_raw:.4f}")

    # Per-kernel
    rho_k, p_k = spearman_r(hetero_k, axm_vals)
    rho_h, p_h = spearman_r(hetero_h, axm_vals)
    rho_e, p_e = spearman_r(hetero_e, axm_vals)
    print(f"  SD(k) vs AXM: rho={rho_k:.3f}, p={p_k:.4f}")
    print(f"  SD(h) vs AXM: rho={rho_h:.3f}, p={p_h:.4f}")
    print(f"  SD(e) vs AXM: rho={rho_e:.3f}, p={p_e:.4f}")

    # Section-controlled partial correlation (residualize both on section dummies)
    section_arr = np.array(section_labels)
    sec_dummies = build_dummies(section_labels)
    X_sec = np.column_stack([np.ones(n), sec_dummies])

    comp_arr = np.array(composites)
    axm_arr = np.array(axm_vals)

    # Residualize composite against section
    beta_comp = np.linalg.lstsq(X_sec, comp_arr, rcond=None)[0]
    comp_resid = comp_arr - X_sec @ beta_comp

    # Residualize AXM against section
    beta_axm = np.linalg.lstsq(X_sec, axm_arr, rcond=None)[0]
    axm_resid = axm_arr - X_sec @ beta_axm

    rho_partial, p_partial = spearman_r(comp_resid.tolist(), axm_resid.tolist())
    print(f"  Section-controlled partial: rho={rho_partial:.3f}, p={p_partial:.4f}")

    verdict = 'CORRELATED' if p_raw < 0.05 else 'UNCORRELATED'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'filter': f'>={MIN_PARS_PER_FOLIO} pars with >={MIN_PAR_TOKENS} tokens',
        'spearman_composite': {'rho': rho_raw, 'p': p_raw},
        'spearman_section_controlled': {'rho': rho_partial, 'p': p_partial},
        'per_kernel': {
            'sd_k': {'rho': rho_k, 'p': p_k},
            'sd_h': {'rho': rho_h, 'p': p_h},
            'sd_e': {'rho': rho_e, 'p': p_e},
        },
        'mean_composite': float(np.mean(composites)),
        'verdict': verdict,
        # Store for Test 4 and 5
        '_folios': hetero_folios,
        '_composites': composites,
        '_axm': axm_vals,
        '_sections': section_labels,
    }


# ── Test 2: Trajectory Slope Diversity ──────────────────────────────

def test2_trajectory_slope_diversity(data):
    """T2: Variance of per-paragraph h_frac trajectory slopes vs AXM."""
    print("\n── Test 2: TRAJECTORY_SLOPE_DIVERSITY ──")

    folio_data = data['folio_data']
    valid_folios = data['valid_folios']
    par_stats = data['folio_paragraph_stats']

    slope_folios = []
    slope_variances = []
    axm_vals = []
    total_qualifying_pars = 0

    for folio in valid_folios:
        pars = par_stats[folio]
        slopes = []

        for p in pars:
            if p['n_tokens'] < MIN_PAR_TOKENS:
                continue
            line_kernels = p['line_kernels']
            if len(line_kernels) < MIN_PAR_LINES:
                continue

            # Trajectory slope: Spearman rho of (line_position, h_frac)
            positions = list(range(len(line_kernels)))
            h_fracs = [lk['h_frac'] for lk in line_kernels]
            rho_slope, _ = spearman_r(positions, h_fracs)
            slopes.append(rho_slope)
            total_qualifying_pars += 1

        if len(slopes) >= 2:  # Need >=2 paragraphs for variance
            slope_var = float(np.var(slopes))
            slope_folios.append(folio)
            slope_variances.append(slope_var)
            axm_vals.append(folio_data[folio]['axm_self'])

    n = len(slope_folios)
    print(f"  {n} folios qualify (>=2 paragraphs with >={MIN_PAR_LINES} lines)")
    print(f"  {total_qualifying_pars} total qualifying paragraphs")

    if n < 5:
        print("  Insufficient data for trajectory analysis")
        return {
            'n_folios': n,
            'n_qualifying_pars': total_qualifying_pars,
            'verdict': 'INSUFFICIENT_DATA',
        }

    rho, p = spearman_r(slope_variances, axm_vals)
    print(f"  Slope variance vs AXM: rho={rho:.3f}, p={p:.4f}")

    verdict = 'DIVERSE_TRAJECTORIES_CORRELATE' if p < 0.05 else 'TRAJECTORY_NEUTRAL'
    print(f"  Mean slope variance: {float(np.mean(slope_variances)):.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'n_qualifying_pars': total_qualifying_pars,
        'spearman': {'rho': rho, 'p': p},
        'mean_slope_variance': float(np.mean(slope_variances)),
        'verdict': verdict,
        '_folios': slope_folios,
        '_variances': slope_variances,
        '_axm': axm_vals,
    }


# ── Test 3: Paragraph Type Entropy ─────────────────────────────────

def test3_paragraph_type_entropy(data):
    """T3: Shannon entropy of paragraph type distribution vs AXM."""
    print("\n── Test 3: PARAGRAPH_TYPE_ENTROPY ──")

    folio_data = data['folio_data']
    valid_folios = data['valid_folios']
    par_stats = data['folio_paragraph_stats']

    entropy_folios = []
    entropies = []
    axm_vals = []
    par_counts = []
    section_labels = []

    for folio in valid_folios:
        pars = par_stats[folio]
        qualifying = [p for p in pars if p['n_tokens'] >= MIN_PAR_TOKENS]

        if len(qualifying) < MIN_PARS_PER_FOLIO:
            continue

        type_counts = Counter(p['kernel_type'] for p in qualifying)
        h = shannon_entropy(type_counts)

        entropy_folios.append(folio)
        entropies.append(h)
        axm_vals.append(folio_data[folio]['axm_self'])
        par_counts.append(len(qualifying))
        section_labels.append(folio_data[folio]['section'])

    n = len(entropy_folios)
    print(f"  {n} folios qualify")

    rho_raw, p_raw = spearman_r(entropies, axm_vals)
    print(f"  Type entropy vs AXM: rho={rho_raw:.3f}, p={p_raw:.4f}")

    # Control for paragraph count
    rho_pc, p_pc = spearman_r(entropies, par_counts)
    print(f"  Type entropy vs paragraph count: rho={rho_pc:.3f}, p={p_pc:.4f}")

    # Section-controlled partial
    sec_dummies = build_dummies(section_labels)
    X_sec = np.column_stack([np.ones(n), sec_dummies])
    ent_arr = np.array(entropies)
    axm_arr = np.array(axm_vals)

    beta_ent = np.linalg.lstsq(X_sec, ent_arr, rcond=None)[0]
    ent_resid = ent_arr - X_sec @ beta_ent
    beta_axm = np.linalg.lstsq(X_sec, axm_arr, rcond=None)[0]
    axm_resid = axm_arr - X_sec @ beta_axm

    rho_partial, p_partial = spearman_r(ent_resid.tolist(), axm_resid.tolist())
    print(f"  Section-controlled partial: rho={rho_partial:.3f}, p={p_partial:.4f}")

    verdict = 'TYPE_ENTROPY_CORRELATES' if p_raw < 0.05 else 'TYPE_ENTROPY_NEUTRAL'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'spearman_raw': {'rho': rho_raw, 'p': p_raw},
        'spearman_section_controlled': {'rho': rho_partial, 'p': p_partial},
        'entropy_vs_par_count': {'rho': rho_pc, 'p': p_pc},
        'mean_entropy': float(np.mean(entropies)),
        'max_entropy': math.log2(3),
        'verdict': verdict,
        '_folios': entropy_folios,
        '_entropies': entropies,
        '_axm': axm_vals,
    }


# ── Test 4: Incremental Explanatory Power ───────────────────────────

def test4_incremental_explanatory_power(data, t1, t2, t3):
    """T4: Add paragraph kernel predictors to C1035 baseline. dR² + LOO CV."""
    print("\n── Test 4: INCREMENTAL_EXPLANATORY_POWER ──")

    folio_data = data['folio_data']
    valid_folios = data['valid_folios']
    par_stats = data['folio_paragraph_stats']

    # Compute paragraph kernel heterogeneity for ALL valid folios
    # (relaxed: use >=2 paragraphs, set 0 for single-paragraph folios)
    folio_heterogeneity = {}
    folio_slope_var = {}
    folio_type_entropy = {}

    for folio in valid_folios:
        pars = par_stats[folio]
        qualifying = [p for p in pars if p['n_tokens'] >= MIN_PAR_TOKENS]

        # Heterogeneity
        if len(qualifying) >= 2:
            k_fracs = [p['k_frac'] for p in qualifying]
            h_fracs = [p['h_frac'] for p in qualifying]
            e_fracs = [p['e_frac'] for p in qualifying]
            sd_k = float(np.std(k_fracs))
            sd_h = float(np.std(h_fracs))
            sd_e = float(np.std(e_fracs))
            folio_heterogeneity[folio] = math.sqrt(sd_k**2 + sd_h**2 + sd_e**2)
        else:
            folio_heterogeneity[folio] = 0.0

        # Type entropy
        if len(qualifying) >= 2:
            type_counts = Counter(p['kernel_type'] for p in qualifying)
            folio_type_entropy[folio] = shannon_entropy(type_counts)
        else:
            folio_type_entropy[folio] = 0.0

        # Trajectory slope variance
        slopes = []
        for p in pars:
            if p['n_tokens'] >= MIN_PAR_TOKENS and len(p['line_kernels']) >= MIN_PAR_LINES:
                positions = list(range(len(p['line_kernels'])))
                h_fracs_line = [lk['h_frac'] for lk in p['line_kernels']]
                rho_slope, _ = spearman_r(positions, h_fracs_line)
                slopes.append(rho_slope)
        folio_slope_var[folio] = float(np.var(slopes)) if len(slopes) >= 2 else 0.0

    # Build arrays matching C1035 baseline
    n = len(valid_folios)
    axm_self = np.array([folio_data[f]['axm_self'] for f in valid_folios])
    regime_labels = [folio_data[f]['regime'] for f in valid_folios]
    section_labels = [folio_data[f]['section'] for f in valid_folios]

    regime_dummies = build_dummies(regime_labels)
    section_dummies = build_dummies(section_labels)

    pfx_ent = np.array([folio_data[f]['prefix_entropy'] for f in valid_folios])
    haz_dens = np.array([folio_data[f]['hazard_density'] for f in valid_folios])
    bridge_pc1 = np.array([folio_data[f]['bridge_pc1'] for f in valid_folios])

    pfx_z = standardize(pfx_ent)
    haz_z = standardize(haz_dens)
    pc1_z = standardize(bridge_pc1)

    # C1035 baseline model
    X_base = np.column_stack([np.ones(n), regime_dummies, section_dummies, pfx_z, haz_z, pc1_z])
    _, _, ss_res_base, r2_base = ols_fit(X_base, axm_self)
    loo_base = loo_cv_r2(X_base, axm_self)
    k_base = X_base.shape[1]

    print(f"  C1035 baseline: R2={r2_base:.4f}, LOO R2={loo_base:.4f} (n={n})")

    # Test each novel predictor
    predictors = {
        'paragraph_kernel_heterogeneity': np.array([folio_heterogeneity[f] for f in valid_folios]),
        'trajectory_slope_variance': np.array([folio_slope_var[f] for f in valid_folios]),
        'paragraph_type_entropy': np.array([folio_type_entropy[f] for f in valid_folios]),
    }

    results = {}
    any_pass = False

    for pred_name, pred_arr in predictors.items():
        pred_z = standardize(pred_arr)
        X_ext = np.column_stack([X_base, pred_z])
        _, _, ss_res_ext, r2_ext = ols_fit(X_ext, axm_self)
        loo_ext = loo_cv_r2(X_ext, axm_self)

        delta_r2 = r2_ext - r2_base
        f_stat, f_p = f_test_increment(ss_res_base, ss_res_ext, 1, n, k_base + 1)
        loo_delta = loo_ext - loo_base

        passes = delta_r2 > 0.03 and f_p < 0.05

        results[pred_name] = {
            'r2_extended': float(r2_ext),
            'delta_r2': float(delta_r2),
            'f_stat': float(f_stat),
            'f_p': float(f_p),
            'loo_r2': float(loo_ext),
            'loo_delta_r2': float(loo_delta),
            'passes': passes,
        }

        if passes:
            any_pass = True

        tag = "PASS" if passes else "fail"
        print(f"  {pred_name}: dR2={delta_r2:.4f}, F={f_stat:.2f}, p={f_p:.4f}, "
              f"LOO dR2={loo_delta:.4f} [{tag}]")

    verdict = 'PARAGRAPH_DYNAMICS_EXPLAIN_RESIDUAL' if any_pass else 'RESIDUAL_IRREDUCIBLE_CONFIRMED'
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n,
        'c1035_baseline_r2': float(r2_base),
        'c1035_loo_r2': float(loo_base),
        'pass_criterion': 'dR2 > 0.03 AND p < 0.05',
        'predictors': results,
        'any_pass': any_pass,
        'verdict': verdict,
    }


# ── Test 5: Within-Section Validation ───────────────────────────────

def test5_within_section_validation(data, t1):
    """T5: Within-section Spearman of heterogeneity vs AXM."""
    print("\n── Test 5: WITHIN_SECTION_VALIDATION ──")

    if '_folios' not in t1:
        return {'verdict': 'INSUFFICIENT_DATA'}

    t1_folios = t1['_folios']
    t1_composites = t1['_composites']
    t1_axm = t1['_axm']
    t1_sections = t1['_sections']

    # Group by section
    section_data = defaultdict(lambda: {'composites': [], 'axm': []})
    for i in range(len(t1_folios)):
        sec = t1_sections[i]
        section_data[sec]['composites'].append(t1_composites[i])
        section_data[sec]['axm'].append(t1_axm[i])

    results = {}
    any_significant = False

    for sec in sorted(section_data.keys()):
        sd = section_data[sec]
        n_sec = len(sd['composites'])
        if n_sec < MIN_SECTION_FOLIOS:
            continue

        rho, p = spearman_r(sd['composites'], sd['axm'])
        sig = p < 0.05
        if sig:
            any_significant = True

        results[sec] = {
            'n': n_sec,
            'rho': rho,
            'p': p,
            'significant': sig,
            'mean_heterogeneity': float(np.mean(sd['composites'])),
            'mean_axm': float(np.mean(sd['axm'])),
        }
        print(f"  Section {sec}: n={n_sec}, rho={rho:.3f}, p={p:.4f} "
              f"{'*' if sig else ''}")

    verdict = 'WITHIN_SECTION_CONFIRMED' if any_significant else 'SECTION_CONFOUND_ONLY'
    print(f"  Verdict: {verdict}")

    return {
        'sections': results,
        'any_significant': any_significant,
        'verdict': verdict,
    }


# ── Synthesis ───────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5):
    """Combine all test results into overall verdict."""
    print("\n── SYNTHESIS ──")

    verdicts = {
        't1': t1['verdict'],
        't2': t2['verdict'],
        't3': t3['verdict'],
        't4': t4['verdict'],
        't5': t5['verdict'],
    }

    if t4['any_pass']:
        overall = 'PARAGRAPH_KERNEL_DYNAMICS_MEDIATES_RESIDUAL'
    else:
        supporting = 0
        if 'CORRELATED' in t1['verdict']:
            supporting += 1
        if 'CORRELATE' in t2['verdict']:
            supporting += 1
        if 'CORRELATE' in t3['verdict']:
            supporting += 1

        if supporting >= 2 and t5['verdict'] == 'WITHIN_SECTION_CONFIRMED':
            overall = 'PARAGRAPH_KERNEL_DYNAMICS_SIGNAL_WEAK'
        elif supporting >= 1:
            overall = 'PARAGRAPH_KERNEL_DYNAMICS_SIGNAL_MARGINAL'
        else:
            overall = 'RESIDUAL_IS_PROGRAM_SPECIFIC_DESIGN_FREEDOM'

    print(f"  T1={verdicts['t1']}")
    print(f"  T2={verdicts['t2']}")
    print(f"  T3={verdicts['t3']}")
    print(f"  T4={verdicts['t4']}")
    print(f"  T5={verdicts['t5']}")
    print(f"  Overall: {overall}")

    return {
        'verdicts': verdicts,
        'overall': overall,
    }


# ── Main ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 412: PARAGRAPH_KERNEL_DYNAMICS")
    print("=" * 60)

    data = load_data()

    t1 = test1_paragraph_kernel_heterogeneity(data)
    t2 = test2_trajectory_slope_diversity(data)
    t3 = test3_paragraph_type_entropy(data)
    t4 = test4_incremental_explanatory_power(data, t1, t2, t3)
    t5 = test5_within_section_validation(data, t1)

    synthesis = synthesize(t1, t2, t3, t4, t5)

    # Strip internal data from output
    for t in [t1, t2, t3]:
        for key in list(t.keys()):
            if key.startswith('_'):
                del t[key]

    output = round_floats({
        'phase': 'PARAGRAPH_KERNEL_DYNAMICS',
        'phase_number': 412,
        'depends_on': ['C965', 'C893', 'C944', 'C1022', 'C1035', 'C1152'],
        'test1_paragraph_kernel_heterogeneity': t1,
        'test2_trajectory_slope_diversity': t2,
        'test3_paragraph_type_entropy': t3,
        'test4_incremental_explanatory_power': t4,
        'test5_within_section_validation': t5,
        'synthesis': synthesis,
    })

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'paragraph_kernel_dynamics.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
