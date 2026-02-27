#!/usr/bin/env python3
"""
Phase 485: THERMODYNAMIC ARC VALIDATION
========================================
Tests whether a first-principles thermodynamic ordering model (derived from
distillation process logic) predicts the observed 8-category quintile profiles
(C1371 "thermal arc") better than chance or a naive null model.

Tier 3 interpretive validation: tests whether the distillation interpretation
predicts observed Tier 2 structure.

Tests:
  T1: Thermodynamic rank correlation (predicted vs observed center-of-mass)
  T2: Gradient shape classification (8 categories x 5 shapes)
  T3: Superiority over uniform decay null
  T4: Cross-section stability
  T5: OPERATION lag behind THERMAL
  T6: MONITORING position-independence
  T7: Pairwise ordering accuracy (28 pairs)
  SUPPLEMENT: PREFIX confound control

Pre-registered predictions:
  P1: THERMAL peaks Q1 or Q2
  P2: FLOW monotonically increases (rho >= 0.8)
  P3: STAGING front-loaded (Q1 > Q5, ratio >= 1.1)
  P4: TRANSITION peaks at Q5
  P5: MONITORING position-flat (CV < 0.15)
  P6: CONTAINMENT concentrated Q1-Q2
  P7: OPERATION center-of-mass > THERMAL center-of-mass

Depends on: C1371, C1361, C1047, C1001, C1012, C1305, C1250
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
N_CATS = len(CATEGORIES)
N_QUINTILES = 5

# Pre-registered thermodynamic ordering (earliest to latest)
# Derived from distillation process logic BEFORE examining data
THERMO_RANK = {
    'STAGING': 1,      # apparatus setup first
    'MARKING': 2,      # identify what you're doing
    'CONTAINMENT': 3,  # seal vessel before heating
    'THERMAL': 4,      # apply heat
    'MONITORING': 5,   # interspersed checks
    'OPERATION': 6,    # active processing needs thermal state
    'FLOW': 7,         # fluid movement is consequence of heating
    'TRANSITION': 8,   # completion/state-change events at end
}

# Pre-registered gradient shape predictions
THERMO_SHAPES = {
    'THERMAL': 'DECLINING',
    'FLOW': 'RISING',
    'STAGING': 'DECLINING',
    'TRANSITION': 'RISING',
    'MONITORING': 'FLAT',
    'MARKING': 'DECLINING',
    'CONTAINMENT': 'PEAKED',
    'OPERATION': 'RISING',
}

SECTION_LABELS = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS', 'C': 'COSMO'}


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def quintile_index(pos, line_len):
    """Compute quintile (0-4) for position within line."""
    if line_len <= 1:
        return 2
    frac = pos / (line_len - 1)
    q = int(frac * N_QUINTILES)
    return min(q, N_QUINTILES - 1)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with category, quintile, prefix, section, folio."""
    print("Loading data...")

    morph = Morphology()
    cc = CategoryClassifier()

    # Section assignments from Phase 479
    with open(PROJECT / 'phases' / 'GENERATIVE_GAP_CHARACTERIZATION' / 'results' /
              'generative_gap_characterization.json', encoding='utf-8') as f:
        p479 = json.load(f)
    folio_section = {f: d.get('section', 'UNK') for f, d in p479['per_folio'].items()}

    # Collect per-line token data
    line_tokens = defaultdict(list)  # {(folio, line): [(cat, prefix, section, folio), ...]}

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        m = morph.extract(token.word)
        mid = m.middle if m else token.word
        cat = cc.classify(mid)
        if not cat:
            continue

        prefix = m.prefix if m else ''
        section = folio_section.get(token.folio, 'UNK')
        key = (token.folio, token.line)
        line_tokens[key].append((cat, prefix or '', section, token.folio))

    # Build global quintile-category matrix + per-token records
    global_cat_counts = np.zeros((N_QUINTILES, N_CATS), dtype=int)
    section_cat_counts = defaultdict(lambda: np.zeros((N_QUINTILES, N_CATS), dtype=int))
    folio_cat_counts = defaultdict(lambda: np.zeros((N_QUINTILES, N_CATS), dtype=int))

    # Per-prefix quintile distribution (for confound control)
    prefix_quintile_counts = defaultdict(lambda: np.zeros(N_QUINTILES, dtype=int))
    # Per-token records for confound control
    token_records = []  # [(cat_idx, quintile, prefix, section, folio)]

    n_lines = 0
    n_tokens = 0

    for key, tokens in line_tokens.items():
        line_len = len(tokens)
        if line_len < 2:
            continue

        n_lines += 1
        for pos, (cat, prefix, section, folio) in enumerate(tokens):
            q = quintile_index(pos, line_len)
            ci = CAT_IDX[cat]
            global_cat_counts[q, ci] += 1
            section_cat_counts[section][q, ci] += 1
            folio_cat_counts[folio][q, ci] += 1
            prefix_quintile_counts[prefix][q] += 1
            token_records.append((ci, q, prefix, section, folio))
            n_tokens += 1

    print(f"  Lines: {n_lines}, Tokens: {n_tokens}")
    print(f"  Tokens per quintile: {[int(global_cat_counts[q].sum()) for q in range(N_QUINTILES)]}")
    print(f"  Unique prefixes: {len(prefix_quintile_counts)}")

    return {
        'global_cat_counts': global_cat_counts,
        'section_cat_counts': dict(section_cat_counts),
        'folio_cat_counts': dict(folio_cat_counts),
        'prefix_quintile_counts': dict(prefix_quintile_counts),
        'token_records': token_records,
        'n_lines': n_lines,
        'n_tokens': n_tokens,
    }


# ── Helper: Category center-of-mass ─────────────────────────────────

def category_com(cat_counts):
    """Compute center-of-mass quintile for each category.
    cat_counts: (N_QUINTILES, N_CATS) array.
    Returns dict {category: float center-of-mass in [0, 4]}.
    """
    coms = {}
    quintiles = np.arange(N_QUINTILES, dtype=float)
    for ci, cat in enumerate(CATEGORIES):
        col = cat_counts[:, ci].astype(float)
        total = col.sum()
        if total > 0:
            coms[cat] = float(np.dot(quintiles, col) / total)
        else:
            coms[cat] = 2.0  # midpoint
    return coms


def classify_shape(quintile_fracs):
    """Classify a 5-element quintile profile as DECLINING/RISING/PEAKED/FLAT/U_SHAPED."""
    x = np.arange(N_QUINTILES, dtype=float)
    y = np.array(quintile_fracs, dtype=float)

    if y.sum() == 0:
        return 'FLAT'

    # Linear fit
    mean_x = x.mean()
    mean_y = y.mean()
    ss_xx = ((x - mean_x) ** 2).sum()
    ss_xy = ((x - mean_x) * (y - mean_y)).sum()

    if ss_xx > 0:
        slope = ss_xy / ss_xx
    else:
        slope = 0.0

    # Residuals from linear
    y_pred_linear = mean_y + slope * (x - mean_x)
    resid = y - y_pred_linear
    ss_resid_linear = (resid ** 2).sum()

    # Quadratic fit
    x2 = x ** 2
    X = np.column_stack([np.ones(5), x, x2])
    try:
        coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
        y_pred_quad = X @ coeffs
        ss_resid_quad = ((y - y_pred_quad) ** 2).sum()
        quad_coeff = coeffs[2]
    except np.linalg.LinAlgError:
        ss_resid_quad = ss_resid_linear
        quad_coeff = 0.0

    # CV of profile
    cv = float(np.std(y) / max(np.mean(y), 1e-10))

    # Classification logic
    # Flat if CV < 0.08
    if cv < 0.08:
        return 'FLAT'

    # Check quadratic improvement
    quad_improvement = 1.0 - (ss_resid_quad / max(ss_resid_linear, 1e-10))

    # If quadratic explains substantially more than linear, check shape
    if quad_improvement > 0.3 and abs(quad_coeff) > abs(slope) * 0.3:
        if quad_coeff < 0:
            return 'PEAKED'
        else:
            return 'U_SHAPED'

    # Linear classification
    # Normalize slope by mean to get relative effect
    rel_slope = slope / max(abs(mean_y), 1e-10)
    if rel_slope < -0.02:
        return 'DECLINING'
    elif rel_slope > 0.02:
        return 'RISING'
    else:
        return 'FLAT'


# ── Test Functions ───────────────────────────────────────────────────

def test1_rank_correlation(data):
    """T1: Thermodynamic rank correlation."""
    print("\n=== T1: Thermodynamic Rank Correlation ===")

    coms = category_com(data['global_cat_counts'])

    # Sort by observed COM
    sorted_cats = sorted(coms.items(), key=lambda x: x[1])
    print("  Observed category ordering (earliest to latest):")
    for cat, com in sorted_cats:
        print(f"    {cat:15s} COM={com:.3f}  (predicted rank={THERMO_RANK[cat]})")

    # Spearman correlation between predicted rank and observed COM
    predicted = [THERMO_RANK[cat] for cat in CATEGORIES]
    observed_coms = [coms[cat] for cat in CATEGORIES]
    rho, p_val = spearmanr(predicted, observed_coms)
    print(f"\n  Spearman rho (predicted rank vs observed COM): {rho:.4f}, p={p_val:.6f}")

    # Permutation null: 10,000 random rank shuffles
    n_perm = 10000
    rng = np.random.default_rng(42)
    perm_rhos = []
    for _ in range(n_perm):
        shuffled = rng.permutation(predicted)
        r, _ = spearmanr(shuffled, observed_coms)
        perm_rhos.append(r)

    percentile = float(np.mean(np.array(perm_rhos) >= rho))
    perm_p = percentile
    print(f"  Permutation p-value (10K shuffles): {perm_p:.4f}")
    print(f"  Percentile of observed rho: {100*(1-percentile):.1f}th")

    passed = bool(rho >= 0.60 and p_val < 0.05)
    strong = bool(rho >= 0.75)
    print(f"  PASS (rho>=0.60, p<0.05): {passed}")
    print(f"  STRONG (rho>=0.75): {strong}")

    return {
        'category_coms': coms,
        'predicted_ranks': THERMO_RANK,
        'spearman_rho': float(rho),
        'spearman_p': float(p_val),
        'permutation_p': float(perm_p),
        'passed': passed,
        'strong': strong,
    }


def test2_gradient_shapes(data):
    """T2: Gradient shape classification."""
    print("\n=== T2: Gradient Shape Classification ===")

    counts = data['global_cat_counts']
    row_sums = counts.sum(axis=1, keepdims=True)
    fracs = counts / np.maximum(row_sums, 1)

    results = {}
    correct = 0

    print(f"  {'Category':15s} {'Q1':>6s} {'Q2':>6s} {'Q3':>6s} {'Q4':>6s} {'Q5':>6s}  "
          f"{'Observed':>10s} {'Predicted':>10s} {'Match':>6s}")

    for ci, cat in enumerate(CATEGORIES):
        vals = fracs[:, ci]
        observed_shape = classify_shape(vals)
        predicted_shape = THERMO_SHAPES[cat]

        # Match check (PEAKED matches PEAKED, etc.)
        match = observed_shape == predicted_shape
        if match:
            correct += 1

        marker = 'OK' if match else 'MISS'
        print(f"  {cat:15s} {vals[0]:6.3f} {vals[1]:6.3f} {vals[2]:6.3f} {vals[3]:6.3f} {vals[4]:6.3f}  "
              f"{observed_shape:>10s} {predicted_shape:>10s} {marker:>6s}")

        results[cat] = {
            'quintile_fracs': [float(v) for v in vals],
            'observed_shape': observed_shape,
            'predicted_shape': predicted_shape,
            'match': match,
        }

    passed = bool(correct >= 5)
    strong = bool(correct >= 7)
    print(f"\n  Correct: {correct}/8. PASS (>=5): {passed}. STRONG (>=7): {strong}")

    results['correct_count'] = correct
    results['passed'] = passed
    results['strong'] = strong

    return results


def test3_superiority_over_null(data):
    """T3: Thermodynamic model vs uniform decay null."""
    print("\n=== T3: Superiority Over Uniform Decay Null ===")

    counts = data['global_cat_counts']
    row_sums = counts.sum(axis=1, keepdims=True)
    observed = counts / np.maximum(row_sums, 1)  # (5, 8)

    # --- Thermodynamic model predictions ---
    # For each category, generate a predicted quintile profile based on shape
    thermo_predicted = np.zeros((N_QUINTILES, N_CATS))

    for ci, cat in enumerate(CATEGORIES):
        shape = THERMO_SHAPES[cat]
        obs_mean = observed[:, ci].mean()

        if shape == 'DECLINING':
            # Linear decline: high at Q1, low at Q5
            profile = np.array([1.4, 1.2, 1.0, 0.8, 0.6])
        elif shape == 'RISING':
            # Linear rise: low at Q1, high at Q5
            profile = np.array([0.6, 0.8, 1.0, 1.2, 1.4])
        elif shape == 'PEAKED':
            # Peak at Q1-Q2
            profile = np.array([1.3, 1.3, 1.0, 0.8, 0.6])
        elif shape == 'FLAT':
            profile = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        else:
            profile = np.array([1.0, 1.0, 1.0, 1.0, 1.0])

        # Scale to match observed mean
        profile = profile * obs_mean / profile.mean()
        thermo_predicted[:, ci] = profile

    # --- Uniform decay null ---
    # Every category has the same slight decline (entropy increases toward line end)
    uniform_predicted = np.zeros((N_QUINTILES, N_CATS))
    for ci, cat in enumerate(CATEGORIES):
        obs_mean = observed[:, ci].mean()
        # Slight uniform decline
        profile = np.array([1.1, 1.05, 1.0, 0.95, 0.9])
        profile = profile * obs_mean / profile.mean()
        uniform_predicted[:, ci] = profile

    # Compute MSE
    mse_thermo = float(((observed - thermo_predicted) ** 2).mean())
    mse_uniform = float(((observed - uniform_predicted) ** 2).mean())
    mse_ratio = mse_thermo / max(mse_uniform, 1e-15)

    print(f"  MSE (thermodynamic): {mse_thermo:.8f}")
    print(f"  MSE (uniform decay): {mse_uniform:.8f}")
    print(f"  MSE ratio (thermo/uniform): {mse_ratio:.4f}")

    passed = bool(mse_ratio < 0.80)
    strong = bool(mse_ratio < 0.60)
    print(f"  PASS (ratio<0.80): {passed}. STRONG (ratio<0.60): {strong}")

    return {
        'mse_thermodynamic': mse_thermo,
        'mse_uniform_decay': mse_uniform,
        'mse_ratio': float(mse_ratio),
        'passed': passed,
        'strong': strong,
    }


def test4_cross_section(data):
    """T4: Cross-section stability of thermodynamic ordering."""
    print("\n=== T4: Cross-Section Stability ===")

    section_coms = {}
    section_rhos = {}

    predicted = [THERMO_RANK[cat] for cat in CATEGORIES]

    for section in sorted(data['section_cat_counts'].keys()):
        if section not in SECTION_LABELS:
            continue

        s_counts = data['section_cat_counts'][section]
        total = s_counts.sum()
        if total < 200:
            print(f"  {SECTION_LABELS[section]}: insufficient data ({total} tokens)")
            continue

        coms = category_com(s_counts)
        observed_coms = [coms[cat] for cat in CATEGORIES]
        rho, p = spearmanr(predicted, observed_coms)

        label = SECTION_LABELS[section]
        section_coms[label] = coms
        section_rhos[label] = {'rho': float(rho), 'p': float(p)}
        print(f"  {label:10s}: rho={rho:.3f}, p={p:.4f}, n={total}")

    if section_rhos:
        rho_values = [v['rho'] for v in section_rhos.values()]
        min_rho = min(rho_values)
        max_rho = max(rho_values)
        median_rho = float(np.median(rho_values))
        print(f"\n  Min rho: {min_rho:.3f}, Max: {max_rho:.3f}, Median: {median_rho:.3f}")

        passed = bool(min_rho >= 0.40)
        strong = bool(min_rho >= 0.55)
    else:
        min_rho = max_rho = median_rho = None
        passed = False
        strong = False

    print(f"  PASS (min>=0.40): {passed}. STRONG (all>=0.55): {strong}")

    return {
        'section_rhos': section_rhos,
        'min_rho': min_rho,
        'max_rho': max_rho,
        'median_rho': median_rho,
        'passed': passed,
        'strong': strong,
    }


def test5_operation_lag(data):
    """T5: OPERATION center-of-mass lags THERMAL."""
    print("\n=== T5: OPERATION Lag Behind THERMAL ===")

    # Global COM comparison
    coms = category_com(data['global_cat_counts'])
    thermal_com = coms['THERMAL']
    operation_com = coms['OPERATION']
    global_lag = operation_com - thermal_com

    print(f"  Global THERMAL COM: {thermal_com:.4f}")
    print(f"  Global OPERATION COM: {operation_com:.4f}")
    print(f"  Global lag (OPERATION - THERMAL): {global_lag:.4f}")

    # Per-folio paired test
    folio_lags = []
    for folio, f_counts in data['folio_cat_counts'].items():
        total = f_counts.sum()
        if total < 20:
            continue
        f_coms = category_com(f_counts)
        lag = f_coms['OPERATION'] - f_coms['THERMAL']
        folio_lags.append(lag)

    if len(folio_lags) >= 10:
        folio_lags = np.array(folio_lags)
        mean_lag = float(folio_lags.mean())
        se_lag = float(folio_lags.std() / np.sqrt(len(folio_lags)))
        from scipy.stats import ttest_1samp
        t_stat, p_val = ttest_1samp(folio_lags, 0)
        # One-tailed: OPERATION > THERMAL
        p_one = float(p_val / 2) if t_stat > 0 else float(1 - p_val / 2)

        print(f"  Per-folio mean lag: {mean_lag:.4f} +/- {se_lag:.4f}")
        print(f"  t-test: t={t_stat:.3f}, p(one-tailed)={p_one:.6f}")
        print(f"  N folios: {len(folio_lags)}")

        passed = bool(mean_lag > 0 and p_one < 0.05 and abs(global_lag) >= 0.5)
        strong = bool(passed and abs(global_lag) >= 1.0)
    else:
        mean_lag = None
        p_one = None
        t_stat = None
        passed = False
        strong = False

    print(f"  PASS (lag>0, p<0.05, lag>=0.5): {passed}. STRONG (lag>=1.0): {strong}")

    return {
        'thermal_com': thermal_com,
        'operation_com': operation_com,
        'global_lag': global_lag,
        'folio_mean_lag': mean_lag,
        'folio_t_stat': float(t_stat) if t_stat is not None else None,
        'folio_p_one_tailed': p_one,
        'n_folios': len(folio_lags) if isinstance(folio_lags, np.ndarray) else 0,
        'passed': passed,
        'strong': strong,
    }


def test6_monitoring_flat(data):
    """T6: MONITORING position-independence."""
    print("\n=== T6: MONITORING Position-Independence ===")

    counts = data['global_cat_counts']
    row_sums = counts.sum(axis=1, keepdims=True)
    fracs = counts / np.maximum(row_sums, 1)

    # CV for each category
    cat_cvs = {}
    for ci, cat in enumerate(CATEGORIES):
        vals = fracs[:, ci]
        cv = float(np.std(vals) / max(np.mean(vals), 1e-10))
        cat_cvs[cat] = cv

    # Sort by CV
    sorted_cvs = sorted(cat_cvs.items(), key=lambda x: x[1])
    print("  Category CVs (flattest first):")
    for cat, cv in sorted_cvs:
        marker = ' <-- MONITORING' if cat == 'MONITORING' else ''
        print(f"    {cat:15s} CV={cv:.4f}{marker}")

    mon_cv = cat_cvs['MONITORING']
    mon_rank = [cat for cat, _ in sorted_cvs].index('MONITORING') + 1

    print(f"\n  MONITORING CV: {mon_cv:.4f}, rank: {mon_rank}/8 (1=flattest)")

    passed = bool(mon_cv < 0.15 and mon_rank <= 3)
    strong = bool(mon_cv < 0.10 and mon_rank == 1)
    print(f"  PASS (CV<0.15 AND bottom 3): {passed}. STRONG (CV<0.10 AND flattest): {strong}")

    return {
        'category_cvs': cat_cvs,
        'monitoring_cv': mon_cv,
        'monitoring_rank': mon_rank,
        'passed': passed,
        'strong': strong,
    }


def test7_pairwise_ordering(data):
    """T7: Pairwise ordering accuracy (28 pairs)."""
    print("\n=== T7: Pairwise Ordering Accuracy ===")

    coms = category_com(data['global_cat_counts'])

    correct = 0
    total_pairs = 0
    details = []

    for i in range(N_CATS):
        for j in range(i + 1, N_CATS):
            cat_i = CATEGORIES[i]
            cat_j = CATEGORIES[j]

            # Predicted: lower rank = earlier
            pred_earlier = cat_i if THERMO_RANK[cat_i] < THERMO_RANK[cat_j] else cat_j
            # Observed: lower COM = earlier
            obs_earlier = cat_i if coms[cat_i] < coms[cat_j] else cat_j

            match = pred_earlier == obs_earlier
            if match:
                correct += 1
            total_pairs += 1

            details.append({
                'pair': f"{cat_i} vs {cat_j}",
                'predicted_earlier': pred_earlier,
                'observed_earlier': obs_earlier,
                'match': match,
            })

    accuracy = correct / max(total_pairs, 1)
    print(f"  Correct: {correct}/{total_pairs} ({accuracy:.1%})")

    # Binomial test (vs 50% chance)
    from scipy.stats import binomtest
    binom_result = binomtest(correct, total_pairs, 0.5, alternative='greater')
    binom_p = float(binom_result.pvalue)
    print(f"  Binomial p (vs 50%): {binom_p:.6f}")

    # Show mismatches
    mismatches = [d for d in details if not d['match']]
    if mismatches:
        print(f"  Mismatches ({len(mismatches)}):")
        for m in mismatches:
            print(f"    {m['pair']}: predicted {m['predicted_earlier']}, observed {m['observed_earlier']}")

    passed = bool(correct >= 20)
    strong = bool(correct >= 24)
    print(f"  PASS (>=20/28): {passed}. STRONG (>=24/28): {strong}")

    return {
        'correct': correct,
        'total': total_pairs,
        'accuracy': accuracy,
        'binomial_p': binom_p,
        'mismatches': [d for d in details if not d['match']],
        'passed': passed,
        'strong': strong,
    }


# ── Supplementary: PREFIX Confound Control ───────────────────────────

def prefix_confound_control(data):
    """Test whether thermodynamic ordering survives after controlling for PREFIX position."""
    print("\n=== SUPPLEMENT: PREFIX Confound Control ===")

    token_records = data['token_records']
    prefix_quintile_counts = data['prefix_quintile_counts']

    # Step 1: Compute expected quintile for each PREFIX
    prefix_expected_q = {}
    for prefix, q_counts in prefix_quintile_counts.items():
        total = q_counts.sum()
        if total > 0:
            expected = float(np.dot(np.arange(N_QUINTILES), q_counts) / total)
        else:
            expected = 2.0
        prefix_expected_q[prefix] = expected

    # Step 2: Compute residual quintile for each token
    # residual = actual_quintile - expected_quintile_given_prefix
    cat_residual_sums = np.zeros(N_CATS)
    cat_residual_counts = np.zeros(N_CATS)

    for ci, q, prefix, section, folio in token_records:
        expected_q = prefix_expected_q.get(prefix, 2.0)
        residual = q - expected_q
        cat_residual_sums[ci] += residual
        cat_residual_counts[ci] += 1

    # Step 3: Residualized center-of-mass
    residual_coms = {}
    for ci, cat in enumerate(CATEGORIES):
        if cat_residual_counts[ci] > 0:
            residual_coms[cat] = float(cat_residual_sums[ci] / cat_residual_counts[ci])
        else:
            residual_coms[cat] = 0.0

    print("  PREFIX-residualized category COMs (positive = later than PREFIX predicts):")
    sorted_res = sorted(residual_coms.items(), key=lambda x: x[1])
    for cat, rcom in sorted_res:
        print(f"    {cat:15s} residual COM={rcom:+.4f}")

    # Step 4: Re-run T1 on residuals
    predicted = [THERMO_RANK[cat] for cat in CATEGORIES]
    residual_com_vals = [residual_coms[cat] for cat in CATEGORIES]
    rho_resid, p_resid = spearmanr(predicted, residual_com_vals)
    print(f"\n  Residualized Spearman rho: {rho_resid:.4f}, p={p_resid:.6f}")

    # Step 5: Re-run T2 (shape classification) on residualized quintile profiles
    # Build residualized quintile-category matrix
    resid_cat_counts = np.zeros((N_QUINTILES, N_CATS))
    for ci, q, prefix, section, folio in token_records:
        expected_q = prefix_expected_q.get(prefix, 2.0)
        residual = q - expected_q
        # Map residual to nearest quintile (centered at 0)
        # Shift so residual range maps back to [0, 4]
        shifted = residual + 2.0
        rq = int(np.clip(round(shifted), 0, 4))
        resid_cat_counts[rq, ci] += 1

    row_sums = resid_cat_counts.sum(axis=1, keepdims=True)
    resid_fracs = resid_cat_counts / np.maximum(row_sums, 1)

    resid_shapes = {}
    correct_resid = 0
    print("\n  Residualized gradient shapes:")
    for ci, cat in enumerate(CATEGORIES):
        vals = resid_fracs[:, ci]
        obs_shape = classify_shape(vals)
        pred_shape = THERMO_SHAPES[cat]
        match = obs_shape == pred_shape
        if match:
            correct_resid += 1
        marker = 'OK' if match else 'MISS'
        print(f"    {cat:15s} {obs_shape:>10s} (predicted {pred_shape:>10s}) {marker}")
        resid_shapes[cat] = {'observed': obs_shape, 'predicted': pred_shape, 'match': match}

    # Verdict
    survives_t1 = bool(rho_resid >= 0.40 and p_resid < 0.10)
    survives_t2 = bool(correct_resid >= 4)
    survives = survives_t1 or survives_t2

    print(f"\n  T1 survives PREFIX control (rho>=0.40, p<0.10): {survives_t1}")
    print(f"  T2 survives PREFIX control (>=4/8 shapes): {survives_t2}")
    print(f"  Overall: {'SURVIVES' if survives else 'COLLAPSES'}")

    return {
        'residual_coms': residual_coms,
        'residualized_rho': float(rho_resid),
        'residualized_p': float(p_resid),
        'residualized_shapes': resid_shapes,
        'resid_shape_correct': correct_resid,
        'survives_t1': survives_t1,
        'survives_t2': survives_t2,
        'survives': survives,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    data = load_data()

    t1 = test1_rank_correlation(data)
    t2 = test2_gradient_shapes(data)
    t3 = test3_superiority_over_null(data)
    t4 = test4_cross_section(data)
    t5 = test5_operation_lag(data)
    t6 = test6_monitoring_flat(data)
    t7 = test7_pairwise_ordering(data)
    supplement = prefix_confound_control(data)

    # ── Predictions ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRE-REGISTERED PREDICTION RESULTS:")

    counts = data['global_cat_counts']
    row_sums = counts.sum(axis=1, keepdims=True)
    fracs = counts / np.maximum(row_sums, 1)

    # P1: THERMAL peaks Q1 or Q2
    th = fracs[:, CAT_IDX['THERMAL']]
    p1 = bool(int(np.argmax(th)) in [0, 1])
    print(f"  P1 (THERMAL peaks Q1/Q2): {'CONFIRMED' if p1 else 'FALSIFIED'} "
          f"(peak=Q{np.argmax(th)+1})")

    # P2: FLOW monotonically increases (rho >= 0.8)
    fl = fracs[:, CAT_IDX['FLOW']]
    rho_fl, _ = spearmanr(np.arange(5), fl)
    p2 = bool(rho_fl >= 0.8)
    print(f"  P2 (FLOW rho>=0.8): {'CONFIRMED' if p2 else 'FALSIFIED'} (rho={rho_fl:.3f})")

    # P3: STAGING front-loaded (Q1/Q5 >= 1.1)
    st = fracs[:, CAT_IDX['STAGING']]
    st_ratio = float(st[0] / max(st[4], 1e-10))
    p3 = bool(st_ratio >= 1.1)
    print(f"  P3 (STAGING Q1/Q5>=1.1): {'CONFIRMED' if p3 else 'FALSIFIED'} (ratio={st_ratio:.3f})")

    # P4: TRANSITION peaks at Q5
    tr = fracs[:, CAT_IDX['TRANSITION']]
    p4 = bool(int(np.argmax(tr)) == 4)
    print(f"  P4 (TRANSITION peaks Q5): {'CONFIRMED' if p4 else 'FALSIFIED'} "
          f"(peak=Q{np.argmax(tr)+1})")

    # P5: MONITORING CV < 0.15
    mon = fracs[:, CAT_IDX['MONITORING']]
    mon_cv = float(np.std(mon) / max(np.mean(mon), 1e-10))
    p5 = bool(mon_cv < 0.15)
    print(f"  P5 (MONITORING CV<0.15): {'CONFIRMED' if p5 else 'FALSIFIED'} (CV={mon_cv:.4f})")

    # P6: CONTAINMENT concentrated Q1-Q2
    cn = fracs[:, CAT_IDX['CONTAINMENT']]
    cn_early = float(np.mean(cn[0:2]))
    cn_late = float(np.mean(cn[3:5]))
    p6 = bool(cn_early > cn_late)
    print(f"  P6 (CONTAINMENT early>late): {'CONFIRMED' if p6 else 'FALSIFIED'} "
          f"(early={cn_early:.4f}, late={cn_late:.4f})")

    # P7: OPERATION COM > THERMAL COM
    coms = t1['category_coms']
    p7 = bool(coms['OPERATION'] > coms['THERMAL'])
    print(f"  P7 (OPERATION after THERMAL): {'CONFIRMED' if p7 else 'FALSIFIED'} "
          f"(OPERATION COM={coms['OPERATION']:.3f}, THERMAL COM={coms['THERMAL']:.3f})")

    predictions = {
        'P1_thermal_peak': p1,
        'P2_flow_monotonic': p2,
        'P3_staging_front': p3,
        'P4_transition_final': p4,
        'P5_monitoring_flat': p5,
        'P6_containment_early': p6,
        'P7_operation_lag': p7,
    }

    confirmed = sum(1 for v in predictions.values() if v is True)
    falsified = sum(1 for v in predictions.values() if v is False)
    print(f"\n  Score: {confirmed}/7 confirmed, {falsified}/7 falsified")

    # ── Test Scorecard ───────────────────────────────────────────
    tests_passed = sum(1 for t in [t1, t2, t3, t4, t5, t6, t7] if t.get('passed'))
    tests_strong = sum(1 for t in [t1, t2, t3, t4, t5, t6, t7] if t.get('strong'))

    # Gate: T3 must pass for verdict > MIXED
    t3_gate = t3.get('passed', False)

    if not t3_gate and tests_passed > 4:
        effective_verdict_level = 'MIXED'
    elif tests_passed >= 6 and tests_strong >= 3:
        effective_verdict_level = 'STRONG_SUPPORT'
    elif tests_passed >= 5:
        effective_verdict_level = 'SUPPORT'
    elif tests_passed >= 3:
        effective_verdict_level = 'MIXED'
    else:
        effective_verdict_level = 'WEAK'

    # PREFIX confound qualifier
    prefix_qualifier = ''
    if supplement.get('survives'):
        prefix_qualifier = ' (PREFIX-independent)'
    else:
        prefix_qualifier = ' (PREFIX-confounded: category gradient may be PREFIX artifact)'
        if effective_verdict_level in ('STRONG_SUPPORT', 'SUPPORT'):
            effective_verdict_level = 'MIXED'

    verdict = (f"{effective_verdict_level}: {tests_passed}/7 tests pass, "
               f"{tests_strong}/7 strong, {confirmed}/7 predictions confirmed"
               f"{prefix_qualifier}")

    print(f"\n{'='*60}")
    print(f"TESTS: {tests_passed}/7 pass, {tests_strong}/7 strong")
    print(f"T3 GATE: {'OPEN' if t3_gate else 'CLOSED (caps verdict at MIXED)'}")
    print(f"PREFIX: {'SURVIVES' if supplement.get('survives') else 'COLLAPSES'}")
    print(f"\nVERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save
    results = {
        'metadata': {
            'phase': 485,
            'name': 'THERMODYNAMIC_ARC_VALIDATION',
            'n_tokens': data['n_tokens'],
            'n_lines': data['n_lines'],
            'elapsed_seconds': elapsed,
        },
        'T1_rank_correlation': t1,
        'T2_gradient_shapes': t2,
        'T3_superiority_over_null': t3,
        'T4_cross_section': t4,
        'T5_operation_lag': t5,
        'T6_monitoring_flat': t6,
        'T7_pairwise_ordering': t7,
        'supplement_prefix_control': supplement,
        'predictions': predictions,
        'test_scorecard': {
            'passed': tests_passed,
            'strong': tests_strong,
            't3_gate': t3_gate,
        },
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'thermodynamic_arc_validation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
