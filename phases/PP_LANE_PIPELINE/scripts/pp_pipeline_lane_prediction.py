"""
PP_LANE_PIPELINE Script 2: Pipeline Lane Prediction
Tests 4-6: Non-EN PP -> EN lane balance, A-record distribution matching,
incremental R-squared.

Tests whether PP vocabulary composition predicts B-folio lane balance,
whether A-record PP character distribution matches B-side observations,
and whether PP adds predictive power beyond section and REGIME.
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology
from scipy import stats as sp_stats

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================

print("=" * 70)
print("PP_LANE_PIPELINE Script 2: Pipeline Lane Prediction")
print("=" * 70)

# 1. PP/RI MIDDLE lists
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])

# 2. AZC-Med / B-Native split
with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json') as f:
    role_data = json.load(f)
azc_med_set = set(role_data['azc_split']['azc_mediated'])
b_native_set = set(role_data['azc_split']['b_native'])

# 3. EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

# 4. Class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)
token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'

# 5. REGIME mapping
with open(PROJECT_ROOT / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for f in folios:
        folio_to_regime[f] = regime

# 6. Transcript + Morphology
tx = Transcript()
morph = Morphology()

print(f"Loaded PP={len(pp_set)}, AZC-Med={len(azc_med_set)}, B-Native={len(b_native_set)}")


# ---- Lane prediction function (C649 rule) ----
def lane_prediction(middle):
    """C649 initial character rule: k/t/p -> QO, e/o -> CHSH, else neutral."""
    if not middle:
        return 'neutral'
    c = middle[0]
    if c in ('k', 't', 'p'):
        return 'QO'
    elif c in ('e', 'o'):
        return 'CHSH'
    return 'neutral'


def compute_qo_frac(middle_counter, pp_filter=None):
    """Compute QO fraction among lane-predicting PP MIDDLEs.
    pp_filter: optional set to restrict which PP MIDDLEs to count.
    Returns (qo_frac, n_qo, n_chsh, n_total_lane_pred).
    """
    n_qo = 0
    n_chsh = 0
    for mid, count in middle_counter.items():
        if mid not in pp_set:
            continue
        if pp_filter is not None and mid not in pp_filter:
            continue
        pred = lane_prediction(mid)
        if pred == 'QO':
            n_qo += count
        elif pred == 'CHSH':
            n_chsh += count
    total = n_qo + n_chsh
    frac = n_qo / total if total > 0 else float('nan')
    return frac, n_qo, n_chsh, total


# ---- Build per-folio B data ----
print("\nBuilding per-folio B data...")

folio_data = {}
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue

    folio = token.folio
    if folio not in folio_data:
        folio_data[folio] = {
            'n_qo_en': 0, 'n_chsh_en': 0,
            'all_pp_middles': Counter(),
            'non_en_pp_middles': Counter(),
            'section': token.section,
            'regime': folio_to_regime.get(folio, 'UNKNOWN'),
        }
    fd = folio_data[folio]

    cls = token_to_class.get(word)
    m = morph.extract(word)
    is_en = cls in all_en_classes if cls is not None else False

    # EN lane counts (DV)
    if is_en and m.prefix:
        if m.prefix == 'qo':
            fd['n_qo_en'] += 1
        elif m.prefix in ('ch', 'sh'):
            fd['n_chsh_en'] += 1

    # PP MIDDLE counts (predictor)
    if m.middle and m.middle in pp_set:
        fd['all_pp_middles'][m.middle] += 1
        if not is_en:
            fd['non_en_pp_middles'][m.middle] += 1

# Compute derived variables
for folio, fd in folio_data.items():
    n_en = fd['n_qo_en'] + fd['n_chsh_en']
    fd['n_en'] = n_en
    fd['lane_balance'] = fd['n_qo_en'] / n_en if n_en > 0 else float('nan')

    # Non-EN PP QO fractions
    fd['non_en_pp_qo_frac'], fd['non_en_qo'], fd['non_en_chsh'], fd['non_en_lane_pred'] = \
        compute_qo_frac(fd['non_en_pp_middles'])

    # All PP QO fractions (sensitivity)
    fd['all_pp_qo_frac'], fd['all_qo'], fd['all_chsh'], fd['all_lane_pred'] = \
        compute_qo_frac(fd['all_pp_middles'])

    # AZC-Med only
    fd['azc_med_qo_frac'], _, _, fd['azc_med_lane_pred'] = \
        compute_qo_frac(fd['non_en_pp_middles'], pp_filter=azc_med_set)

    # B-Native only
    fd['b_native_qo_frac'], _, _, fd['b_native_lane_pred'] = \
        compute_qo_frac(fd['non_en_pp_middles'], pp_filter=b_native_set)

print(f"  {len(folio_data)} B folios processed")

# ---- Helper: partial correlation ----
def partial_correlation(x, y, covariates):
    """Pearson partial correlation controlling for covariates.
    x, y: 1D arrays. covariates: list of 1D arrays (dummy variables).
    Returns (r, p).
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(covariates) == 0:
        r, p = sp_stats.pearsonr(x, y)
        return r, p

    # Build covariate matrix with intercept
    cov_matrix = np.column_stack([np.ones(len(x))] + [np.array(c, dtype=float) for c in covariates])

    # OLS residuals
    try:
        beta_x, _, _, _ = np.linalg.lstsq(cov_matrix, x, rcond=None)
        resid_x = x - cov_matrix @ beta_x
        beta_y, _, _, _ = np.linalg.lstsq(cov_matrix, y, rcond=None)
        resid_y = y - cov_matrix @ beta_y
    except np.linalg.LinAlgError:
        return float('nan'), float('nan')

    # Pearson on residuals
    if np.std(resid_x) < 1e-10 or np.std(resid_y) < 1e-10:
        return 0.0, 1.0

    r, p = sp_stats.pearsonr(resid_x, resid_y)
    return r, p


def build_dummy_variables(labels):
    """Build k-1 dummy variables from categorical labels.
    Returns list of 1D arrays.
    """
    unique = sorted(set(labels))
    if len(unique) <= 1:
        return []
    dummies = []
    for cat in unique[1:]:  # drop first as reference
        dummies.append([1.0 if l == cat else 0.0 for l in labels])
    return dummies


def manual_r_squared(X, y):
    """Compute R-squared from design matrix X (without intercept) and response y.
    Adds intercept internally.
    """
    y = np.array(y, dtype=float)
    if X is None or len(X) == 0:
        # Intercept-only model
        y_pred = np.mean(y) * np.ones(len(y))
    else:
        X = np.array(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        X_int = np.column_stack([np.ones(len(y)), X])
        try:
            beta, _, _, _ = np.linalg.lstsq(X_int, y, rcond=None)
            y_pred = X_int @ beta
        except np.linalg.LinAlgError:
            return float('nan')

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot < 1e-10:
        return 0.0
    return 1.0 - ss_res / ss_tot


def f_test_incremental(r2_full, r2_null, n, p_full, p_null):
    """F-test for incremental R-squared.
    p_full, p_null: number of predictors EXCLUDING intercept.
    """
    df1 = p_full - p_null
    df2 = n - p_full - 1
    if df2 <= 0 or df1 <= 0 or r2_full <= r2_null:
        return 0.0, 1.0, df1, df2
    f_stat = ((r2_full - r2_null) / df1) / ((1 - r2_full) / df2)
    p_val = 1.0 - sp_stats.f.cdf(f_stat, df1, df2)
    return f_stat, p_val, df1, df2


# ============================================================
# SECTION 2: Test 4 -- Non-EN PP Composition -> EN Lane Balance
# ============================================================

print("\n" + "=" * 70)
print("TEST 4: Non-EN PP Composition -> EN Lane Balance")
print("=" * 70)

MIN_EN = 10
MIN_NON_EN_PP = 5

# Filter folios
valid_folios = []
for folio, fd in folio_data.items():
    if fd['n_en'] >= MIN_EN and fd['non_en_lane_pred'] >= MIN_NON_EN_PP:
        valid_folios.append(folio)

excluded = len(folio_data) - len(valid_folios)
print(f"Folios: {len(valid_folios)} valid, {excluded} excluded (min EN={MIN_EN}, min non-EN PP lane-pred={MIN_NON_EN_PP})")

if len(valid_folios) >= 20:
    # Extract arrays
    x_vals = [folio_data[f]['non_en_pp_qo_frac'] for f in valid_folios]
    y_vals = [folio_data[f]['lane_balance'] for f in valid_folios]
    sections = [folio_data[f]['section'] for f in valid_folios]
    regimes = [folio_data[f]['regime'] for f in valid_folios]

    # Filter out NaN
    valid_mask = [(not (x != x) and not (y != y)) for x, y in zip(x_vals, y_vals)]
    x_clean = [x for x, v in zip(x_vals, valid_mask) if v]
    y_clean = [y for y, v in zip(y_vals, valid_mask) if v]
    sec_clean = [s for s, v in zip(sections, valid_mask) if v]
    reg_clean = [r for r, v in zip(regimes, valid_mask) if v]
    fol_clean = [f for f, v in zip(valid_folios, valid_mask) if v]

    n_valid = len(x_clean)
    print(f"After NaN filter: {n_valid} folios")

    # Bivariate Spearman
    rho, rho_p = sp_stats.spearmanr(x_clean, y_clean)
    print(f"\nBivariate Spearman: rho={rho:.4f}, p={rho_p:.4f}")

    # Partial correlation controlling section + REGIME
    sec_dummies = build_dummy_variables(sec_clean)
    reg_dummies = build_dummy_variables(reg_clean)
    all_covariates = sec_dummies + reg_dummies

    partial_r, partial_p = partial_correlation(x_clean, y_clean, all_covariates)
    print(f"Partial (section+REGIME): r={partial_r:.4f}, p={partial_p:.4f}")
    print(f"  Section levels: {len(set(sec_clean))}, REGIME levels: {len(set(reg_clean))}")

    # Sensitivity: all PP (tautological)
    x_all = [folio_data[f]['all_pp_qo_frac'] for f in fol_clean]
    valid_all = [not (x != x) for x in x_all]
    x_all_clean = [x for x, v in zip(x_all, valid_all) if v]
    y_all_clean = [y for y, v in zip(y_clean, valid_all) if v]

    if len(x_all_clean) >= 20:
        rho_all, rho_all_p = sp_stats.spearmanr(x_all_clean, y_all_clean)
        sec_all = [s for s, v in zip(sec_clean, valid_all) if v]
        reg_all = [r for r, v in zip(reg_clean, valid_all) if v]
        sd_all = build_dummy_variables(sec_all)
        rd_all = build_dummy_variables(reg_all)
        partial_r_all, partial_p_all = partial_correlation(x_all_clean, y_all_clean, sd_all + rd_all)
        print(f"\nSensitivity (all PP, includes EN -- tautological):")
        print(f"  Spearman: rho={rho_all:.4f}, p={rho_all_p:.4f}")
        print(f"  Partial: r={partial_r_all:.4f}, p={partial_p_all:.4f}")
    else:
        rho_all, rho_all_p = float('nan'), float('nan')
        partial_r_all, partial_p_all = float('nan'), float('nan')

    # Folio data for export
    folio_export = []
    for f in fol_clean:
        fd = folio_data[f]
        folio_export.append({
            'folio': f,
            'en_balance': round(fd['lane_balance'], 4),
            'non_en_pp_qo_frac': round(fd['non_en_pp_qo_frac'], 4) if not (fd['non_en_pp_qo_frac'] != fd['non_en_pp_qo_frac']) else None,
            'all_pp_qo_frac': round(fd['all_pp_qo_frac'], 4) if not (fd['all_pp_qo_frac'] != fd['all_pp_qo_frac']) else None,
            'section': fd['section'],
            'regime': fd['regime'],
            'n_en': fd['n_en'],
            'non_en_lane_pred': fd['non_en_lane_pred'],
        })

    test4_results = {
        'n_folios': n_valid,
        'guard': {'min_en': MIN_EN, 'min_non_en_pp': MIN_NON_EN_PP, 'excluded': excluded},
        'bivariate': {
            'spearman_rho': round(rho, 4),
            'p': round(rho_p, 6),
            'n': n_valid,
        },
        'partial': {
            'controlling': ['section', 'regime'],
            'partial_r': round(partial_r, 4),
            'p': round(partial_p, 6),
            'n_section_levels': len(set(sec_clean)),
            'n_regime_levels': len(set(reg_clean)),
        },
        'sensitivity_all_pp': {
            'bivariate_rho': round(rho_all, 4) if not (rho_all != rho_all) else None,
            'bivariate_p': round(rho_all_p, 6) if not (rho_all_p != rho_all_p) else None,
            'partial_r': round(partial_r_all, 4) if not (partial_r_all != partial_r_all) else None,
            'partial_p': round(partial_p_all, 6) if not (partial_p_all != partial_p_all) else None,
            'note': 'Includes EN MIDDLEs (tautological inflation expected)',
        },
        'folio_data': folio_export,
    }
else:
    print(f"INSUFFICIENT FOLIOS ({len(valid_folios)} < 20): descriptive only")
    test4_results = {
        'n_folios': len(valid_folios),
        'guard': {'min_en': MIN_EN, 'min_non_en_pp': MIN_NON_EN_PP, 'excluded': excluded},
        'status': 'INSUFFICIENT_DATA',
    }


# ============================================================
# SECTION 3: Test 5 -- A-Record Lane Prediction Distribution
# ============================================================

print("\n" + "=" * 70)
print("TEST 5: A-Record Lane Prediction Distribution")
print("=" * 70)

# Build A records
print("Building A records...")
record_groups = defaultdict(list)
for token in tx.currier_a():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    key = (token.folio, str(token.line))
    m = morph.extract(word)
    record_groups[key].append({
        'middle': m.middle,
        'section': token.section,
    })

# Compute per-record QO fraction
a_records = []
for (folio, line), tokens in record_groups.items():
    qo_count = 0
    chsh_count = 0
    section = tokens[0]['section']
    for t in tokens:
        mid = t['middle']
        if mid and mid in pp_set:
            pred = lane_prediction(mid)
            if pred == 'QO':
                qo_count += 1
            elif pred == 'CHSH':
                chsh_count += 1
    total_lane_pred = qo_count + chsh_count
    if total_lane_pred < 2:  # Guard: min 2 lane-predicting PP
        continue
    a_records.append({
        'folio': folio,
        'line': line,
        'section': section,
        'pp_qo_frac': qo_count / total_lane_pred,
        'n_lane_pred': total_lane_pred,
    })

print(f"  {len(a_records)} A records with >= 2 lane-predicting PP")

# B-folio lane balances (reuse from Test 4)
b_folios_for_test5 = []
for folio, fd in folio_data.items():
    if fd['n_en'] >= MIN_EN and not (fd['lane_balance'] != fd['lane_balance']):
        b_folios_for_test5.append({
            'folio': folio,
            'lane_balance': fd['lane_balance'],
            'section': fd['section'],
        })

print(f"  {len(b_folios_for_test5)} B folios with >= {MIN_EN} EN tokens")

# Distributions
a_fracs = [r['pp_qo_frac'] for r in a_records]
b_balances = [f['lane_balance'] for f in b_folios_for_test5]

# Descriptive stats
def describe(values, label):
    if not values:
        return {'n': 0}
    arr = np.array(values)
    desc = {
        'n': len(arr),
        'mean': round(float(np.mean(arr)), 4),
        'median': round(float(np.median(arr)), 4),
        'std': round(float(np.std(arr)), 4),
        'q25': round(float(np.percentile(arr, 25)), 4),
        'q75': round(float(np.percentile(arr, 75)), 4),
    }
    print(f"  {label}: n={desc['n']}, mean={desc['mean']:.3f}, median={desc['median']:.3f}, "
          f"std={desc['std']:.3f}, IQR=[{desc['q25']:.3f}, {desc['q75']:.3f}]")
    return desc

print("\nDistributions:")
a_desc = describe(a_fracs, "A-record PP QO frac")
b_desc = describe(b_balances, "B-folio EN lane balance")

# KS test
if len(a_fracs) >= 10 and len(b_balances) >= 10:
    ks_stat, ks_p = sp_stats.ks_2samp(a_fracs, b_balances)
    mw_u, mw_p = sp_stats.mannwhitneyu(a_fracs, b_balances, alternative='two-sided')
    print(f"\nAll sections:")
    print(f"  KS test: D={ks_stat:.4f}, p={ks_p:.4f}")
    print(f"  Mann-Whitney: U={mw_u:.1f}, p={mw_p:.4f}")

    all_section_results = {
        'ks_test': {'statistic': round(ks_stat, 4), 'p': round(ks_p, 6)},
        'mann_whitney': {'u_stat': round(float(mw_u), 1), 'p': round(mw_p, 6)},
    }
else:
    all_section_results = {'status': 'INSUFFICIENT_DATA'}

# Within-Herbal
a_herbal = [r['pp_qo_frac'] for r in a_records if r['section'] == 'H']
b_herbal = [f['lane_balance'] for f in b_folios_for_test5 if f['section'] == 'H']

print(f"\nWithin Herbal:")
a_herbal_desc = describe(a_herbal, "A-Herbal records")
b_herbal_desc = describe(b_herbal, "B-Herbal folios")

if len(a_herbal) >= 10 and len(b_herbal) >= 5:
    ks_h_stat, ks_h_p = sp_stats.ks_2samp(a_herbal, b_herbal)
    mw_h_u, mw_h_p = sp_stats.mannwhitneyu(a_herbal, b_herbal, alternative='two-sided')
    print(f"  KS test: D={ks_h_stat:.4f}, p={ks_h_p:.4f}")
    print(f"  Mann-Whitney: U={mw_h_u:.1f}, p={mw_h_p:.4f}")
    herbal_results = {
        'a_herbal': a_herbal_desc,
        'b_herbal': b_herbal_desc,
        'ks_test': {'statistic': round(ks_h_stat, 4), 'p': round(ks_h_p, 6)},
        'mann_whitney': {'u_stat': round(float(mw_h_u), 1), 'p': round(mw_h_p, 6)},
    }
else:
    herbal_results = {'a_herbal': a_herbal_desc, 'b_herbal': b_herbal_desc, 'status': 'INSUFFICIENT_DATA'}

# By section descriptive
a_by_section = defaultdict(list)
b_by_section = defaultdict(list)
for r in a_records:
    a_by_section[r['section']].append(r['pp_qo_frac'])
for f in b_folios_for_test5:
    b_by_section[f['section']].append(f['lane_balance'])

section_summary = {}
for sec in sorted(set(list(a_by_section.keys()) + list(b_by_section.keys()))):
    section_summary[sec] = {
        'a_records': len(a_by_section.get(sec, [])),
        'a_mean': round(float(np.mean(a_by_section[sec])), 4) if a_by_section.get(sec) else None,
        'b_folios': len(b_by_section.get(sec, [])),
        'b_mean': round(float(np.mean(b_by_section[sec])), 4) if b_by_section.get(sec) else None,
    }

print("\nBy section (descriptive):")
for sec, info in sorted(section_summary.items()):
    a_str = f"A: n={info['a_records']}, mean={info['a_mean']:.3f}" if info['a_mean'] is not None else "A: none"
    b_str = f"B: n={info['b_folios']}, mean={info['b_mean']:.3f}" if info['b_mean'] is not None else "B: none"
    print(f"  {sec}: {a_str} | {b_str}")

test5_results = {
    'a_records': {
        'n_total_records': len(record_groups),
        'n_with_predictions': len(a_records),
        'distribution': a_desc,
    },
    'b_folios': {
        'n': len(b_folios_for_test5),
        'distribution': b_desc,
    },
    'all_sections': all_section_results,
    'within_herbal': herbal_results,
    'by_section': section_summary,
    'granularity_warning': 'A=record-level (line), B=folio-level (program). Distributions are not paired.',
}


# ============================================================
# SECTION 4: Test 6 -- Pipeline Incremental Prediction
# ============================================================

print("\n" + "=" * 70)
print("TEST 6: Pipeline Incremental Prediction")
print("=" * 70)

# Use same valid folios as Test 4 (with additional NaN filter)
reg_folios = []
for folio in valid_folios:
    fd = folio_data[folio]
    if (not (fd['lane_balance'] != fd['lane_balance']) and
        not (fd['non_en_pp_qo_frac'] != fd['non_en_pp_qo_frac'])):
        reg_folios.append(folio)

n_reg = len(reg_folios)
print(f"Folios for regression: {n_reg}")

if n_reg >= 20:
    # Build arrays
    y_reg = np.array([folio_data[f]['lane_balance'] for f in reg_folios])
    sections_reg = [folio_data[f]['section'] for f in reg_folios]
    regimes_reg = [folio_data[f]['regime'] for f in reg_folios]

    # Dummy variables
    sec_dummies_reg = build_dummy_variables(sections_reg)
    reg_dummies_reg = build_dummy_variables(regimes_reg)
    n_sec_dummies = len(sec_dummies_reg)
    n_reg_dummies = len(reg_dummies_reg)
    n_null_predictors = n_sec_dummies + n_reg_dummies

    # Null model: section + REGIME
    if n_null_predictors > 0:
        X_null = np.column_stack([np.array(d) for d in sec_dummies_reg + reg_dummies_reg])
    else:
        X_null = None

    r2_null = manual_r_squared(X_null, y_reg)
    print(f"\nNull model (section + REGIME): R2={r2_null:.4f}")
    print(f"  Section dummies: {n_sec_dummies}, REGIME dummies: {n_reg_dummies}")

    # Combined PP model
    x_pp = np.array([folio_data[f]['non_en_pp_qo_frac'] for f in reg_folios])
    if X_null is not None:
        X_full = np.column_stack([X_null, x_pp])
    else:
        X_full = x_pp.reshape(-1, 1)

    r2_full = manual_r_squared(X_full, y_reg)
    incr_r2 = r2_full - r2_null
    n_full_predictors = n_null_predictors + 1
    f_stat, f_p, df1, df2 = f_test_incremental(r2_full, r2_null, n_reg, n_full_predictors, n_null_predictors)
    print(f"Full model (+PP QO frac): R2={r2_full:.4f}, incr_R2={incr_r2:.4f}")
    print(f"  F-test: F={f_stat:.3f}, p={f_p:.4f}, df=({df1},{df2})")

    combined_result = {
        'predictor': 'non_en_pp_qo_frac',
        'r_squared': round(r2_full, 4),
        'incremental_r2': round(incr_r2, 4),
        'f_test': {
            'f_stat': round(f_stat, 4),
            'p': round(f_p, 6),
            'df1': df1,
            'df2': df2,
        },
    }

    # AZC-Med only model
    azc_folios = [f for f in reg_folios if not (folio_data[f]['azc_med_qo_frac'] != folio_data[f]['azc_med_qo_frac'])]
    print(f"\nAZC-Med only: {len(azc_folios)} folios with data")

    if len(azc_folios) >= 10:
        y_azc = np.array([folio_data[f]['lane_balance'] for f in azc_folios])
        x_azc = np.array([folio_data[f]['azc_med_qo_frac'] for f in azc_folios])
        sec_azc = [folio_data[f]['section'] for f in azc_folios]
        reg_azc = [folio_data[f]['regime'] for f in azc_folios]
        sd_azc = build_dummy_variables(sec_azc)
        rd_azc = build_dummy_variables(reg_azc)
        n_null_azc = len(sd_azc) + len(rd_azc)

        if n_null_azc > 0:
            X_null_azc = np.column_stack([np.array(d) for d in sd_azc + rd_azc])
        else:
            X_null_azc = None

        r2_null_azc = manual_r_squared(X_null_azc, y_azc)

        if X_null_azc is not None:
            X_azc_full = np.column_stack([X_null_azc, x_azc])
        else:
            X_azc_full = x_azc.reshape(-1, 1)

        r2_azc = manual_r_squared(X_azc_full, y_azc)
        incr_azc = r2_azc - r2_null_azc
        f_azc, p_azc, df1_azc, df2_azc = f_test_incremental(r2_azc, r2_null_azc, len(azc_folios), n_null_azc + 1, n_null_azc)
        print(f"  R2={r2_azc:.4f}, incr_R2={incr_azc:.4f}, F={f_azc:.3f}, p={p_azc:.4f}")

        azc_result = {
            'predictor': 'azc_med_qo_frac',
            'n_folios_with_data': len(azc_folios),
            'r_squared': round(r2_azc, 4),
            'incremental_r2': round(incr_azc, 4),
            'f_test': {'f_stat': round(f_azc, 4), 'p': round(p_azc, 6), 'df1': df1_azc, 'df2': df2_azc},
        }
    else:
        azc_result = {'status': 'INSUFFICIENT_DATA', 'n_folios_with_data': len(azc_folios)}

    # B-Native only model
    native_folios = [f for f in reg_folios if not (folio_data[f]['b_native_qo_frac'] != folio_data[f]['b_native_qo_frac'])]
    print(f"\nB-Native only: {len(native_folios)} folios with data")

    if len(native_folios) >= 10:
        y_nat = np.array([folio_data[f]['lane_balance'] for f in native_folios])
        x_nat = np.array([folio_data[f]['b_native_qo_frac'] for f in native_folios])
        sec_nat = [folio_data[f]['section'] for f in native_folios]
        reg_nat = [folio_data[f]['regime'] for f in native_folios]
        sd_nat = build_dummy_variables(sec_nat)
        rd_nat = build_dummy_variables(reg_nat)
        n_null_nat = len(sd_nat) + len(rd_nat)

        if n_null_nat > 0:
            X_null_nat = np.column_stack([np.array(d) for d in sd_nat + rd_nat])
        else:
            X_null_nat = None

        r2_null_nat = manual_r_squared(X_null_nat, y_nat)

        if X_null_nat is not None:
            X_nat_full = np.column_stack([X_null_nat, x_nat])
        else:
            X_nat_full = x_nat.reshape(-1, 1)

        r2_nat = manual_r_squared(X_nat_full, y_nat)
        incr_nat = r2_nat - r2_null_nat
        f_nat, p_nat, df1_nat, df2_nat = f_test_incremental(r2_nat, r2_null_nat, len(native_folios), n_null_nat + 1, n_null_nat)
        print(f"  R2={r2_nat:.4f}, incr_R2={incr_nat:.4f}, F={f_nat:.3f}, p={p_nat:.4f}")

        native_result = {
            'predictor': 'b_native_qo_frac',
            'n_folios_with_data': len(native_folios),
            'r_squared': round(r2_nat, 4),
            'incremental_r2': round(incr_nat, 4),
            'f_test': {'f_stat': round(f_nat, 4), 'p': round(p_nat, 6), 'df1': df1_nat, 'df2': df2_nat},
        }
    else:
        native_result = {'status': 'INSUFFICIENT_DATA', 'n_folios_with_data': len(native_folios)}

    # Pathway comparison
    azc_incr = azc_result.get('incremental_r2', 0)
    nat_incr = native_result.get('incremental_r2', 0)
    if isinstance(azc_incr, (int, float)) and isinstance(nat_incr, (int, float)):
        if azc_incr > nat_incr + 0.02:
            pw_verdict = 'AZC_MED_STRONGER'
        elif nat_incr > azc_incr + 0.02:
            pw_verdict = 'B_NATIVE_STRONGER'
        else:
            pw_verdict = 'SIMILAR'
    else:
        pw_verdict = 'INSUFFICIENT_DATA'

    print(f"\nPathway comparison: {pw_verdict}")
    print(f"  AZC-Med incr R2: {azc_incr}")
    print(f"  B-Native incr R2: {nat_incr}")

    test6_results = {
        'n_folios': n_reg,
        'null_model': {
            'predictors': ['section_dummies', 'regime_dummies'],
            'n_predictors': n_null_predictors,
            'r_squared': round(r2_null, 4),
        },
        'combined_pp': combined_result,
        'azc_med_only': azc_result,
        'b_native_only': native_result,
        'pathway_comparison': {
            'azc_med_incremental_r2': azc_incr,
            'b_native_incremental_r2': nat_incr,
            'stronger_pathway': pw_verdict,
        },
    }
else:
    print(f"INSUFFICIENT FOLIOS ({n_reg} < 20): descriptive only")
    test6_results = {'n_folios': n_reg, 'status': 'INSUFFICIENT_DATA'}


# ============================================================
# SECTION 5: Summary & Save
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Verdicts
if 'bivariate' in test4_results:
    t4_verdict = 'SIGNAL' if test4_results['partial']['p'] < 0.05 else 'NULL'
    print(f"Test 4 (Non-EN PP -> Lane): {t4_verdict} (partial r={test4_results['partial']['partial_r']:.4f}, p={test4_results['partial']['p']:.4f})")
else:
    t4_verdict = 'INSUFFICIENT_DATA'
    print(f"Test 4: {t4_verdict}")

if 'ks_test' in test5_results.get('all_sections', {}):
    t5_verdict = 'MATCHED' if test5_results['all_sections']['ks_test']['p'] > 0.05 else 'DIVERGENT'
    print(f"Test 5 (Distribution Match): {t5_verdict} (KS p={test5_results['all_sections']['ks_test']['p']:.4f})")
else:
    t5_verdict = 'INSUFFICIENT_DATA'
    print(f"Test 5: {t5_verdict}")

if 'combined_pp' in test6_results:
    t6_verdict = 'PP_ADDS' if test6_results['combined_pp']['f_test']['p'] < 0.05 else 'PP_REDUNDANT'
    print(f"Test 6 (Incremental R2): {t6_verdict} (incr R2={test6_results['combined_pp']['incremental_r2']:.4f}, F p={test6_results['combined_pp']['f_test']['p']:.4f})")
else:
    t6_verdict = 'INSUFFICIENT_DATA'
    print(f"Test 6: {t6_verdict}")

results = {
    'metadata': {
        'phase': 'PP_LANE_PIPELINE',
        'script': 'pp_pipeline_lane_prediction',
        'description': 'Pipeline lane prediction: non-EN PP->lane, A-record distribution, incremental R-squared',
    },
    'non_en_pp_lane_prediction': test4_results,
    'a_record_lane_prediction': test5_results,
    'incremental_prediction': test6_results,
    'verdicts': {
        'non_en_prediction': t4_verdict,
        'distribution_match': t5_verdict,
        'incremental': t6_verdict,
    },
}

# JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

output_path = PROJECT_ROOT / 'phases/PP_LANE_PIPELINE/results/pp_pipeline_lane_prediction.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults saved to {output_path}")
