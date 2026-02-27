#!/usr/bin/env python3
"""
Phase 481: ACCENT PC2/PC3 DECOMPOSITION
========================================
Characterizes the uncharacterized accent dimensions:
  PC2 (20.5%) = sequential complexity (bigram_entropy, class_entropy, class_concentration)
  PC3 (8.9%) = morphological texture (mean_word_length, category_entropy, suffix_rate)

PC1 was characterized in C1367 (THERMAL predicts it). This phase completes the accent
decomposition by identifying what predicts PC2 and PC3.

Pre-registered predictions (from expert):
  1. Section predicts PC2 but not PC3
  2. Paragraph density correlates with PC2
  3. Dark pipeline fraction predicts PC3
  4. No single predictor explains >30% of PC2 or PC3
  5. PC2 and PC3 are NOT archetype-structured

Tests:
  T1: Section → PC2 (ANOVA)
  T2: Section → PC3 (ANOVA)
  T3: Paragraph count → PC2 (partial correlation)
  T4: Dark pipeline fraction → PC3 (partial correlation)
  T5: Archetype → PC2 (ANOVA)
  T6: Archetype → PC3 (ANOVA)
  T7: Multivariate PC2 model (stepwise + LOO)
  T8: Multivariate PC3 model (stepwise + LOO)

Depends on: C1367, C1366, C1294, C1047, C1149, C821
"""

import json
import sys
import math
import re
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, f_oneway
from numpy.linalg import lstsq

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Constants ────────────────────────────────────────────────────────

CATEGORIES = ('THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING')


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


def folio_sort_key(folio_id):
    """Sort key for physical folio ordering."""
    m = re.match(r'f(\d+)([rv]?)(\d*)', folio_id)
    if m:
        num = int(m.group(1))
        side = 0 if m.group(2) == 'r' else 1
        sub = int(m.group(3)) if m.group(3) else 0
        return (num, side, sub)
    return (9999, 0, 0)


def folio_position(folio_id):
    """Extract numeric position from folio ID for manuscript ordering."""
    m = re.match(r'f(\d+)([rv]?)(\d*)', folio_id)
    if m:
        num = int(m.group(1))
        side = 0.0 if m.group(2) == 'r' else 0.5
        sub = int(m.group(3)) * 0.01 if m.group(3) else 0
        return num + side + sub
    return 9999.0


def compute_eta_squared(groups):
    """Compute ANOVA F-stat, p-value, and eta-squared."""
    if len(groups) < 2 or any(len(g) < 1 for g in groups):
        return None, None, None
    # Need at least 2 groups with 2+ members for valid ANOVA
    valid = [g for g in groups if len(g) >= 1]
    if len(valid) < 2:
        return None, None, None

    f_stat, p_val = f_oneway(*valid)
    grand_mean = np.mean([v for g in valid for v in g])
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in valid)
    ss_total = sum((v - grand_mean) ** 2 for g in valid for v in g)
    eta_sq = ss_between / max(ss_total, 1e-10)
    return float(f_stat), float(p_val), float(eta_sq)


def partial_correlation_via_residualization(x, y, controls):
    """Compute partial Spearman correlation between x and y, controlling for controls matrix."""
    n = len(x)
    if n < 5:
        return 0.0, 1.0

    X_ctrl = np.column_stack([controls, np.ones(n)])

    # Residualize x
    beta_x, _, _, _ = lstsq(X_ctrl, x, rcond=None)
    x_resid = x - X_ctrl @ beta_x

    # Residualize y
    beta_y, _, _, _ = lstsq(X_ctrl, y, rcond=None)
    y_resid = y - X_ctrl @ beta_y

    if np.std(x_resid) < 1e-10 or np.std(y_resid) < 1e-10:
        return 0.0, 1.0

    rho, p = spearmanr(x_resid, y_resid)
    return float(rho), float(p)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load Phase 480 PC scores, Phase 479 features, and all candidate predictors."""
    print("Loading data...")

    # Phase 480 results (for PC scores)
    with open(PROJECT / 'phases' / 'FOLIO_ACCENT_VECTOR' / 'results' /
              'folio_accent_vector.json', encoding='utf-8') as f:
        p480 = json.load(f)

    folio_scores = p480['T1_pca']['folio_scores']
    folios = sorted(folio_scores.keys())
    print(f"  {len(folios)} folios with PC scores from Phase 480")

    # Phase 479 results (for real_features, metadata)
    with open(PROJECT / 'phases' / 'GENERATIVE_GAP_CHARACTERIZATION' / 'results' /
              'generative_gap_characterization.json', encoding='utf-8') as f:
        p479 = json.load(f)
    per_folio_479 = p479['per_folio']

    # Unified folio profiles (for quire, ht_density)
    with open(PROJECT / 'results' / 'unified_folio_profiles.json', encoding='utf-8') as f:
        profiles = json.load(f)

    # AXM folio data (for paragraph_count, line_count, etc.)
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    axm_folio_data = axm_data['folio_data']

    # Sister pair ch_preference
    sister_path = (PROJECT / 'phases' / 'SISTER_PAIR_CHOICE_DYNAMICS' / 'results' /
                   'quire_sister_consistency.json')
    sister_data = {}
    if sister_path.exists():
        with open(sister_path, encoding='utf-8') as f:
            sp = json.load(f)
        sister_data = sp.get('per_folio_ch_preference', {})
        print(f"  Loaded sister pair data for {len(sister_data)} folios")
    else:
        print("  WARNING: Sister pair data not found")

    # Build per-folio predictor table
    data = {}
    for folio in folios:
        row = {
            'PC2': folio_scores[folio]['PC2'],
            'PC3': folio_scores[folio]['PC3'],
            'PC1': folio_scores[folio]['PC1'],
        }

        # Phase 479 metadata
        fp = per_folio_479.get(folio, {})
        row['section'] = fp.get('section', 'UNK')
        row['regime'] = fp.get('regime', 'UNK')
        row['archetype'] = fp.get('archetype')

        # Phase 479 real_features
        rf = fp.get('real_features', {})
        row['dark_middle_fraction'] = rf.get('dark_middle_fraction', 0)
        row['bridge_middle_fraction'] = rf.get('bridge_middle_fraction', 0)
        row['k_fraction'] = rf.get('k_fraction', 0)
        row['h_fraction'] = rf.get('h_fraction', 0)
        row['e_fraction'] = rf.get('e_fraction', 0)

        # AXM folio data
        axm = axm_folio_data.get(folio, {})
        row['paragraph_count'] = axm.get('paragraph_count', 0)
        row['line_count'] = axm.get('line_count', 0)

        # Unified profiles
        prof = profiles.get(folio, {})
        row['ht_density'] = prof.get('ht_density', 0) if isinstance(prof, dict) else 0

        # Sister pair
        sp_folio = sister_data.get(folio, {})
        row['ch_preference'] = sp_folio.get('ch_preference') if sp_folio else None

        # Folio position
        row['folio_position'] = folio_position(folio)

        data[folio] = row

    return folios, data


def compute_category_fractions(folios_set):
    """Compute per-folio 8-category fractions from transcript."""
    print("  Computing category fractions...")
    morph = Morphology()
    cc = CategoryClassifier()

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    folio_cat_counts = defaultdict(lambda: Counter())

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        if token_to_class.get(token.word) is None:
            continue
        if token.folio not in folios_set:
            continue

        m = morph.extract(token.word)
        mid = m.middle if m else token.word
        cat = cc.classify(mid)
        if cat:
            folio_cat_counts[token.folio][cat] += 1

    folio_cat_fractions = {}
    for folio in folios_set:
        total = sum(folio_cat_counts[folio].values())
        if total > 0:
            folio_cat_fractions[folio] = {
                cat: folio_cat_counts[folio].get(cat, 0) / total
                for cat in CATEGORIES
            }
        else:
            folio_cat_fractions[folio] = {cat: 0.0 for cat in CATEGORIES}

    return folio_cat_fractions


# ── Test Functions ───────────────────────────────────────────────────

def test1_section_pc2(folios, data):
    """T1: Section → PC2 (ANOVA). Prediction: eta-sq > 0.10."""
    print("\n=== T1: Section → PC2 (ANOVA) ===")

    section_groups = defaultdict(list)
    for f in folios:
        section_groups[data[f]['section']].append(data[f]['PC2'])

    groups = [section_groups[s] for s in sorted(section_groups.keys())]
    f_stat, p_val, eta_sq = compute_eta_squared(groups)

    for s in sorted(section_groups.keys()):
        vals = section_groups[s]
        print(f"  Section {s}: n={len(vals)}, mean={np.mean(vals):.3f}, std={np.std(vals):.3f}")

    if f_stat is not None:
        print(f"  ANOVA: F={f_stat:.2f}, p={p_val:.4f}, eta-sq={eta_sq:.3f}")
        prediction_confirmed = eta_sq > 0.10
        print(f"  Prediction (eta-sq > 0.10): {'CONFIRMED' if prediction_confirmed else 'FALSIFIED'}")
    else:
        prediction_confirmed = None
        print("  ANOVA not computable")

    return {
        'section_means': {s: float(np.mean(v)) for s, v in section_groups.items()},
        'section_n': {s: len(v) for s, v in section_groups.items()},
        'F': f_stat, 'p': p_val, 'eta_sq': eta_sq,
        'prediction_confirmed': prediction_confirmed,
    }


def test2_section_pc3(folios, data):
    """T2: Section → PC3 (ANOVA). Prediction: eta-sq < 0.10."""
    print("\n=== T2: Section → PC3 (ANOVA) ===")

    section_groups = defaultdict(list)
    for f in folios:
        section_groups[data[f]['section']].append(data[f]['PC3'])

    groups = [section_groups[s] for s in sorted(section_groups.keys())]
    f_stat, p_val, eta_sq = compute_eta_squared(groups)

    for s in sorted(section_groups.keys()):
        vals = section_groups[s]
        print(f"  Section {s}: n={len(vals)}, mean={np.mean(vals):.3f}, std={np.std(vals):.3f}")

    if f_stat is not None:
        print(f"  ANOVA: F={f_stat:.2f}, p={p_val:.4f}, eta-sq={eta_sq:.3f}")
        prediction_confirmed = eta_sq < 0.10
        print(f"  Prediction (eta-sq < 0.10): {'CONFIRMED' if prediction_confirmed else 'FALSIFIED'}")
    else:
        prediction_confirmed = None
        print("  ANOVA not computable")

    return {
        'section_means': {s: float(np.mean(v)) for s, v in section_groups.items()},
        'section_n': {s: len(v) for s, v in section_groups.items()},
        'F': f_stat, 'p': p_val, 'eta_sq': eta_sq,
        'prediction_confirmed': prediction_confirmed,
    }


def test3_para_pc2(folios, data):
    """T3: Paragraph count → PC2 (partial correlation controlling section)."""
    print("\n=== T3: Paragraph Count → PC2 (partial, section-controlled) ===")

    pc2 = np.array([data[f]['PC2'] for f in folios])
    para = np.array([data[f]['paragraph_count'] for f in folios])

    # Raw Spearman
    rho_raw, p_raw = spearmanr(para, pc2)
    print(f"  Raw: rho={rho_raw:.3f}, p={p_raw:.4f}")

    # Section dummies for control
    sections = sorted(set(data[f]['section'] for f in folios))
    section_dummies = np.zeros((len(folios), max(len(sections) - 1, 1)))
    section_map = {s: i for i, s in enumerate(sections)}
    for idx, f in enumerate(folios):
        s_idx = section_map[data[f]['section']]
        if s_idx > 0:
            section_dummies[idx, s_idx - 1] = 1.0

    rho_partial, p_partial = partial_correlation_via_residualization(para, pc2, section_dummies)
    print(f"  Partial (section ctrl): rho={rho_partial:.3f}, p={p_partial:.4f}")
    prediction_confirmed = p_partial < 0.05
    print(f"  Prediction (significant partial): {'CONFIRMED' if prediction_confirmed else 'FALSIFIED'}")

    return {
        'rho_raw': rho_raw, 'p_raw': p_raw,
        'rho_partial': rho_partial, 'p_partial': p_partial,
        'prediction_confirmed': prediction_confirmed,
    }


def test4_dark_pc3(folios, data):
    """T4: Dark pipeline fraction → PC3 (partial correlation controlling section)."""
    print("\n=== T4: Dark Pipeline Fraction → PC3 (partial, section-controlled) ===")

    pc3 = np.array([data[f]['PC3'] for f in folios])
    dark = np.array([data[f]['dark_middle_fraction'] for f in folios])

    # Raw Spearman
    rho_raw, p_raw = spearmanr(dark, pc3)
    print(f"  Raw: rho={rho_raw:.3f}, p={p_raw:.4f}")

    # Section dummies for control
    sections = sorted(set(data[f]['section'] for f in folios))
    section_dummies = np.zeros((len(folios), max(len(sections) - 1, 1)))
    section_map = {s: i for i, s in enumerate(sections)}
    for idx, f in enumerate(folios):
        s_idx = section_map[data[f]['section']]
        if s_idx > 0:
            section_dummies[idx, s_idx - 1] = 1.0

    rho_partial, p_partial = partial_correlation_via_residualization(dark, pc3, section_dummies)
    print(f"  Partial (section ctrl): rho={rho_partial:.3f}, p={p_partial:.4f}")
    prediction_confirmed = p_partial < 0.05
    print(f"  Prediction (significant partial): {'CONFIRMED' if prediction_confirmed else 'FALSIFIED'}")

    return {
        'rho_raw': rho_raw, 'p_raw': p_raw,
        'rho_partial': rho_partial, 'p_partial': p_partial,
        'prediction_confirmed': prediction_confirmed,
    }


def test5_archetype_pc2(folios, data):
    """T5: Archetype → PC2 (ANOVA). Prediction: eta-sq < 0.10."""
    print("\n=== T5: Archetype → PC2 (ANOVA) ===")

    arch_groups = defaultdict(list)
    for f in folios:
        arch = data[f]['archetype']
        if arch is not None:
            arch_groups[arch].append(data[f]['PC2'])

    groups = [arch_groups[k] for k in sorted(arch_groups.keys())]
    f_stat, p_val, eta_sq = compute_eta_squared(groups)

    for a in sorted(arch_groups.keys()):
        vals = arch_groups[a]
        print(f"  Archetype {a}: n={len(vals)}, mean={np.mean(vals):.3f}")

    if f_stat is not None:
        print(f"  ANOVA: F={f_stat:.2f}, p={p_val:.4f}, eta-sq={eta_sq:.3f}")
        prediction_confirmed = eta_sq < 0.10
        print(f"  Prediction (eta-sq < 0.10): {'CONFIRMED' if prediction_confirmed else 'FALSIFIED'}")
    else:
        prediction_confirmed = None

    return {
        'F': f_stat, 'p': p_val, 'eta_sq': eta_sq,
        'prediction_confirmed': prediction_confirmed,
    }


def test6_archetype_pc3(folios, data):
    """T6: Archetype → PC3 (ANOVA). Prediction: eta-sq < 0.10."""
    print("\n=== T6: Archetype → PC3 (ANOVA) ===")

    arch_groups = defaultdict(list)
    for f in folios:
        arch = data[f]['archetype']
        if arch is not None:
            arch_groups[arch].append(data[f]['PC3'])

    groups = [arch_groups[k] for k in sorted(arch_groups.keys())]
    f_stat, p_val, eta_sq = compute_eta_squared(groups)

    for a in sorted(arch_groups.keys()):
        vals = arch_groups[a]
        print(f"  Archetype {a}: n={len(vals)}, mean={np.mean(vals):.3f}")

    if f_stat is not None:
        print(f"  ANOVA: F={f_stat:.2f}, p={p_val:.4f}, eta-sq={eta_sq:.3f}")
        prediction_confirmed = eta_sq < 0.10
        print(f"  Prediction (eta-sq < 0.10): {'CONFIRMED' if prediction_confirmed else 'FALSIFIED'}")
    else:
        prediction_confirmed = None

    return {
        'F': f_stat, 'p': p_val, 'eta_sq': eta_sq,
        'prediction_confirmed': prediction_confirmed,
    }


def build_predictor_matrix(folios, data, folio_cat_fractions, target_pc):
    """Build candidate predictor matrix for stepwise regression.

    Returns: (predictor_matrix, predictor_names, target_vector)
    Category fractions are residualized against kernel (k, e) first.
    """
    n = len(folios)

    # Target
    y = np.array([data[f][target_pc] for f in folios])

    predictors = []
    names = []

    # Section dummies (H, S, C, B → 3 dummies, B as reference)
    sections = sorted(set(data[f]['section'] for f in folios))
    for s in sections[:-1]:  # Drop last as reference
        col = np.array([1.0 if data[f]['section'] == s else 0.0 for f in folios])
        predictors.append(col)
        names.append(f'section_{s}')

    # Continuous predictors
    continuous = [
        ('paragraph_count', [data[f]['paragraph_count'] for f in folios]),
        ('line_count', [data[f]['line_count'] for f in folios]),
        ('dark_middle_fraction', [data[f]['dark_middle_fraction'] for f in folios]),
        ('bridge_middle_fraction', [data[f]['bridge_middle_fraction'] for f in folios]),
        ('ht_density', [data[f]['ht_density'] for f in folios]),
        ('folio_position', [data[f]['folio_position'] for f in folios]),
    ]

    # Sister pair (may have missing values — use median imputation)
    ch_vals = [data[f].get('ch_preference') for f in folios]
    valid_ch = [v for v in ch_vals if v is not None]
    if valid_ch:
        median_ch = np.median(valid_ch)
        ch_filled = [v if v is not None else median_ch for v in ch_vals]
        continuous.append(('ch_preference', ch_filled))

    for name, vals in continuous:
        arr = np.array(vals, dtype=float)
        if np.std(arr) > 1e-10:
            predictors.append(arr)
            names.append(name)

    # Category fractions residualized against kernel (k, e)
    k_fracs = np.array([data[f]['k_fraction'] for f in folios])
    e_fracs = np.array([data[f]['e_fraction'] for f in folios])
    X_kernel = np.column_stack([k_fracs, e_fracs, np.ones(n)])

    for cat in CATEGORIES:
        cat_vals = np.array([folio_cat_fractions[f].get(cat, 0) for f in folios])
        if np.std(cat_vals) < 1e-10:
            continue
        beta, _, _, _ = lstsq(X_kernel, cat_vals, rcond=None)
        cat_resid = cat_vals - X_kernel @ beta
        if np.std(cat_resid) > 1e-10:
            predictors.append(cat_resid)
            names.append(f'cat_{cat}_resid')

    X = np.column_stack(predictors) if predictors else np.zeros((n, 0))
    return X, names, y


def forward_stepwise_aic(X, y, names, max_predictors=5):
    """Forward stepwise selection by AIC. Returns selected indices and AIC trace."""
    n = X.shape[0]
    p_total = X.shape[1]

    selected = []
    remaining = list(range(p_total))
    aic_trace = []

    # Null model AIC
    ss_null = np.sum((y - np.mean(y)) ** 2)
    aic_null = n * np.log(ss_null / n) + 2 * 1  # intercept only
    best_aic = aic_null
    aic_trace.append(('intercept_only', float(aic_null)))

    for step in range(min(max_predictors, p_total)):
        best_candidate = None
        best_candidate_aic = best_aic

        for j in remaining:
            trial = selected + [j]
            X_trial = np.column_stack([X[:, trial], np.ones(n)])
            try:
                beta, _, _, _ = lstsq(X_trial, y, rcond=None)
                residuals = y - X_trial @ beta
                ss_res = np.sum(residuals ** 2)
                k = len(trial) + 1  # predictors + intercept
                aic = n * np.log(ss_res / n) + 2 * k
            except Exception:
                continue

            if aic < best_candidate_aic:
                best_candidate_aic = aic
                best_candidate = j

        if best_candidate is not None and best_candidate_aic < best_aic - 2:
            # AIC must improve by at least 2 to be meaningful
            selected.append(best_candidate)
            remaining.remove(best_candidate)
            best_aic = best_candidate_aic
            aic_trace.append((names[best_candidate], float(best_aic)))
        else:
            break

    return selected, aic_trace


def loo_r_squared(X, y, selected):
    """Leave-one-out cross-validated R² for selected predictors."""
    n = len(y)
    if not selected:
        return 0.0

    predictions = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_train = np.column_stack([X[mask][:, selected], np.ones(n - 1)])
        y_train = y[mask]
        X_test = np.append(X[i, selected], 1.0).reshape(1, -1)

        try:
            beta, _, _, _ = lstsq(X_train, y_train, rcond=None)
            predictions[i] = float(X_test @ beta)
        except Exception:
            predictions[i] = np.mean(y_train)

    ss_res = np.sum((y - predictions) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return float(1 - ss_res / max(ss_tot, 1e-10))


def test7_multivariate_pc2(folios, data, folio_cat_fractions):
    """T7: Multivariate PC2 model (stepwise + LOO)."""
    print("\n=== T7: Multivariate PC2 Model ===")

    X, names, y = build_predictor_matrix(folios, data, folio_cat_fractions, 'PC2')
    print(f"  {len(names)} candidate predictors for {len(folios)} folios")

    # Forward stepwise
    selected, aic_trace = forward_stepwise_aic(X, y, names)
    selected_names = [names[i] for i in selected]

    print(f"  AIC trace:")
    for name, aic in aic_trace:
        print(f"    + {name}: AIC={aic:.2f}")

    if selected:
        # LOO R²
        loo_r2 = loo_r_squared(X, y, selected)
        print(f"  Selected: {selected_names}")
        print(f"  LOO R² = {loo_r2:.3f}")

        # In-sample R²
        X_sel = np.column_stack([X[:, selected], np.ones(len(folios))])
        beta, _, _, _ = lstsq(X_sel, y, rcond=None)
        predictions = X_sel @ beta
        ss_res = np.sum((y - predictions) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2_insample = 1 - ss_res / max(ss_tot, 1e-10)
        print(f"  In-sample R² = {r2_insample:.3f}")

        # Check prediction 4: no single predictor > 30%
        max_single_r2 = 0.0
        max_single_name = None
        for i in range(X.shape[1]):
            X_single = np.column_stack([X[:, [i]], np.ones(len(folios))])
            b, _, _, _ = lstsq(X_single, y, rcond=None)
            pred = X_single @ b
            sr = np.sum((pred - np.mean(y)) ** 2)
            st = np.sum((y - np.mean(y)) ** 2)
            r2_single = sr / max(st, 1e-10)
            if r2_single > max_single_r2:
                max_single_r2 = r2_single
                max_single_name = names[i]
        print(f"  Max single predictor R²: {max_single_name} = {max_single_r2:.3f}")
        pred4_confirmed = max_single_r2 < 0.30
        print(f"  Prediction 4 (no single >30%): {'CONFIRMED' if pred4_confirmed else 'FALSIFIED'}")
    else:
        loo_r2 = 0.0
        r2_insample = 0.0
        max_single_r2 = 0.0
        max_single_name = None
        pred4_confirmed = True
        print("  No predictors selected (null model)")

    return {
        'n_candidates': len(names),
        'candidate_names': names,
        'selected_names': selected_names if selected else [],
        'aic_trace': aic_trace,
        'loo_r2': loo_r2,
        'r2_insample': r2_insample,
        'max_single_predictor': max_single_name,
        'max_single_r2': max_single_r2,
        'prediction4_confirmed': pred4_confirmed,
    }


def test8_multivariate_pc3(folios, data, folio_cat_fractions):
    """T8: Multivariate PC3 model (stepwise + LOO)."""
    print("\n=== T8: Multivariate PC3 Model ===")

    X, names, y = build_predictor_matrix(folios, data, folio_cat_fractions, 'PC3')
    print(f"  {len(names)} candidate predictors for {len(folios)} folios")

    # Forward stepwise
    selected, aic_trace = forward_stepwise_aic(X, y, names)
    selected_names = [names[i] for i in selected]

    print(f"  AIC trace:")
    for name, aic in aic_trace:
        print(f"    + {name}: AIC={aic:.2f}")

    if selected:
        # LOO R²
        loo_r2 = loo_r_squared(X, y, selected)
        print(f"  Selected: {selected_names}")
        print(f"  LOO R² = {loo_r2:.3f}")

        # In-sample R²
        X_sel = np.column_stack([X[:, selected], np.ones(len(folios))])
        beta, _, _, _ = lstsq(X_sel, y, rcond=None)
        predictions = X_sel @ beta
        ss_res = np.sum((y - predictions) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2_insample = 1 - ss_res / max(ss_tot, 1e-10)
        print(f"  In-sample R² = {r2_insample:.3f}")

        # Check prediction 4: no single predictor > 30%
        max_single_r2 = 0.0
        max_single_name = None
        for i in range(X.shape[1]):
            X_single = np.column_stack([X[:, [i]], np.ones(len(folios))])
            b, _, _, _ = lstsq(X_single, y, rcond=None)
            pred = X_single @ b
            sr = np.sum((pred - np.mean(y)) ** 2)
            st = np.sum((y - np.mean(y)) ** 2)
            r2_single = sr / max(st, 1e-10)
            if r2_single > max_single_r2:
                max_single_r2 = r2_single
                max_single_name = names[i]
        print(f"  Max single predictor R²: {max_single_name} = {max_single_r2:.3f}")
        pred4_confirmed = max_single_r2 < 0.30
        print(f"  Prediction 4 (no single >30%): {'CONFIRMED' if pred4_confirmed else 'FALSIFIED'}")
    else:
        loo_r2 = 0.0
        r2_insample = 0.0
        max_single_r2 = 0.0
        max_single_name = None
        pred4_confirmed = True
        print("  No predictors selected (null model)")

    return {
        'n_candidates': len(names),
        'candidate_names': names,
        'selected_names': selected_names if selected else [],
        'aic_trace': aic_trace,
        'loo_r2': loo_r2,
        'r2_insample': r2_insample,
        'max_single_predictor': max_single_name,
        'max_single_r2': max_single_r2,
        'prediction4_confirmed': pred4_confirmed,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    folios, data = load_data()
    folio_cat_fractions = compute_category_fractions(set(folios))

    # T1-T2: Section ANOVA
    t1 = test1_section_pc2(folios, data)
    t2 = test2_section_pc3(folios, data)

    # T3-T4: Targeted partial correlations
    t3 = test3_para_pc2(folios, data)
    t4 = test4_dark_pc3(folios, data)

    # T5-T6: Archetype ANOVA
    t5 = test5_archetype_pc2(folios, data)
    t6 = test6_archetype_pc3(folios, data)

    # T7-T8: Multivariate models
    t7 = test7_multivariate_pc2(folios, data, folio_cat_fractions)
    t8 = test8_multivariate_pc3(folios, data, folio_cat_fractions)

    # ── Verdict ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRE-REGISTERED PREDICTION RESULTS:")

    # P1: Section predicts PC2 but not PC3
    p1_pc2 = t1.get('prediction_confirmed')
    p1_pc3 = t2.get('prediction_confirmed')
    p1 = p1_pc2 and p1_pc3 if p1_pc2 is not None and p1_pc3 is not None else None
    print(f"  P1 (section → PC2 yes, PC3 no): PC2 eta={t1['eta_sq']:.3f}, PC3 eta={t2['eta_sq']:.3f} → "
          f"{'CONFIRMED' if p1 else 'FALSIFIED' if p1 is not None else 'INCONCLUSIVE'}")

    # P2: Paragraph density → PC2
    p2 = t3.get('prediction_confirmed')
    print(f"  P2 (paragraph → PC2): partial rho={t3['rho_partial']:.3f}, p={t3['p_partial']:.4f} → "
          f"{'CONFIRMED' if p2 else 'FALSIFIED'}")

    # P3: Dark pipeline → PC3
    p3 = t4.get('prediction_confirmed')
    print(f"  P3 (dark pipeline → PC3): partial rho={t4['rho_partial']:.3f}, p={t4['p_partial']:.4f} → "
          f"{'CONFIRMED' if p3 else 'FALSIFIED'}")

    # P4: No single predictor > 30%
    p4_pc2 = t7.get('prediction4_confirmed')
    p4_pc3 = t8.get('prediction4_confirmed')
    p4 = p4_pc2 and p4_pc3
    print(f"  P4 (no single >30%): PC2 max={t7['max_single_r2']:.3f}, PC3 max={t8['max_single_r2']:.3f} → "
          f"{'CONFIRMED' if p4 else 'FALSIFIED'}")

    # P5: Not archetype-structured
    p5_pc2 = t5.get('prediction_confirmed')
    p5_pc3 = t6.get('prediction_confirmed')
    p5 = p5_pc2 and p5_pc3 if p5_pc2 is not None and p5_pc3 is not None else None
    print(f"  P5 (not archetype): PC2 eta={t5['eta_sq']:.3f}, PC3 eta={t6['eta_sq']:.3f} → "
          f"{'CONFIRMED' if p5 else 'FALSIFIED' if p5 is not None else 'INCONCLUSIVE'}")

    # Summary
    confirmed = sum(1 for p in [p1, p2, p3, p4, p5] if p is True)
    falsified = sum(1 for p in [p1, p2, p3, p4, p5] if p is False)
    print(f"\n  Score: {confirmed}/5 confirmed, {falsified}/5 falsified")
    print(f"\n  PC2 model: LOO R²={t7['loo_r2']:.3f}, selected={t7['selected_names']}")
    print(f"  PC3 model: LOO R²={t8['loo_r2']:.3f}, selected={t8['selected_names']}")

    verdict = (f"PC2 ({t7['loo_r2']:.1%} LOO) predicted by {t7['selected_names']}; "
               f"PC3 ({t8['loo_r2']:.1%} LOO) predicted by {t8['selected_names']}; "
               f"{confirmed}/5 predictions confirmed")
    print(f"\nVERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save results
    results = {
        'metadata': {
            'phase': 481,
            'name': 'ACCENT_PC23_DECOMPOSITION',
            'n_folios': len(folios),
            'elapsed_seconds': elapsed,
        },
        'T1_section_pc2': t1,
        'T2_section_pc3': t2,
        'T3_paragraph_pc2': t3,
        'T4_dark_pc3': t4,
        'T5_archetype_pc2': t5,
        'T6_archetype_pc3': t6,
        'T7_multivariate_pc2': t7,
        'T8_multivariate_pc3': t8,
        'predictions': {
            'P1_section_pc2_not_pc3': p1,
            'P2_paragraph_pc2': p2,
            'P3_dark_pc3': p3,
            'P4_no_single_above_30pct': p4,
            'P5_not_archetype_structured': p5,
            'confirmed_count': confirmed,
            'falsified_count': falsified,
        },
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'accent_pc23_decomposition.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
