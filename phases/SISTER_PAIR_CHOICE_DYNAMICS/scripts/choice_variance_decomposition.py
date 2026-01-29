#!/usr/bin/env python3
"""
choice_variance_decomposition.py - Hierarchical variance decomposition of ch_preference

Decomposes folio-level ch_preference variance into: section, REGIME, quire,
MIDDLE composition, and lane balance. Tests unique (semipartial) contribution
of each predictor group and analyzes residual structure.

Sections:
1. Predictor battery construction
2. Hierarchical regression (rank-based OLS)
3. Unique variance (semipartial)
4. Residual analysis
"""

import sys
import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# EN subfamily definitions (C603-C605 definitions, NOT canonical)
# These differ from hazard_circuit_token_mapping.py canonical definitions
# Must use these for lane_balance comparability with C605 (rho=-0.506)
EN_QO = {32, 33, 36, 44, 45, 46, 49}           # 7 classes
EN_CHSH = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}  # 10 classes
EN_MINOR = {41}                                  # 1 class
EN_CLASSES = EN_QO | EN_CHSH | EN_MINOR

CC_DAIIN = {10}
CC_OL = {11}
CC_OL_D = {17}
CC_CLASSES = CC_DAIIN | CC_OL | CC_OL_D


def rank_transform(arr):
    """Rank-transform an array (average ties, 1-based)."""
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    sorted_idx = np.argsort(arr)
    ranks = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j < n and arr[sorted_idx[j]] == arr[sorted_idx[i]]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[sorted_idx[k]] = avg_rank
        i = j
    return ranks


def ols_r_squared(X, y):
    """OLS R-squared using numpy.linalg.lstsq.
    X should include intercept column.
    Returns R2, adjusted R2, coefficients, residuals."""
    n = len(y)
    if X.shape[1] == 0:
        return 0.0, 0.0, np.array([]), y.copy()

    # Add intercept
    X_int = np.column_stack([np.ones(n), X])
    p = X_int.shape[1] - 1  # number of predictors (excluding intercept)

    coeffs, residuals_sum, rank, sv = np.linalg.lstsq(X_int, y, rcond=None)
    y_hat = X_int @ coeffs
    resid = y - y_hat

    SS_res = np.sum(resid ** 2)
    SS_tot = np.sum((y - np.mean(y)) ** 2)

    if SS_tot == 0:
        return 0.0, 0.0, coeffs, resid

    R2 = 1 - SS_res / SS_tot
    adj_R2 = 1 - (1 - R2) * (n - 1) / (n - p - 1) if n - p - 1 > 0 else R2

    return float(R2), float(adj_R2), coeffs, resid


def create_dummies(categories, min_count=0):
    """Create dummy variables (k-1 encoding) from categorical array.
    Returns: dummy matrix (n x k-1), category labels (length k)."""
    unique_cats = sorted(set(categories))
    # Filter by min_count
    if min_count > 0:
        cat_counts = Counter(categories)
        unique_cats = [c for c in unique_cats if cat_counts[c] >= min_count]

    if len(unique_cats) < 2:
        return np.zeros((len(categories), 0)), unique_cats

    # Reference category is the last one
    ref = unique_cats[-1]
    dummies = np.zeros((len(categories), len(unique_cats) - 1))
    for j, cat in enumerate(unique_cats[:-1]):
        dummies[:, j] = np.array([1 if c == cat else 0 for c in categories])

    return dummies, unique_cats


def build_folio_quire_map():
    """Build folio -> quire mapping from raw transcript."""
    transcript_path = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    folio_quire = {}
    with open(transcript_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            language = row.get('language', '').strip().strip('"')
            if transcriber != 'H' or language != 'B':
                continue
            folio = row.get('folio', '').strip().strip('"')
            quire = row.get('quire', '').strip().strip('"')
            if folio and quire:
                folio_quire[folio] = quire
    return folio_quire


def main():
    print("=" * 70)
    print("CHOICE VARIANCE DECOMPOSITION")
    print("Phase: SISTER_PAIR_CHOICE_DYNAMICS | Script 3 of 3")
    print("=" * 70)

    results_dir = Path(__file__).parent.parent / 'results'

    # Load dependencies
    # Script 1 results (MIDDLE composition scores)
    s1_path = results_dir / 'middle_sister_preference.json'
    with open(s1_path, 'r', encoding='utf-8') as f:
        s1_data = json.load(f)

    # Build folio -> middle_comp_score from Script 1
    folio_comp_score = {}
    for entry in s1_data['folio_composition_score']['per_folio']:
        folio_comp_score[entry['folio']] = entry['predicted_ch_pref']

    # Script 2 results (quire mapping)
    s2_path = results_dir / 'quire_sister_consistency.json'
    with open(s2_path, 'r', encoding='utf-8') as f:
        s2_data = json.load(f)

    folio_quire = s2_data['folio_quire_map']

    # REGIME mapping
    regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_regime = {}
    for regime, folios in regime_data.items():
        for folio in folios:
            folio_regime[folio] = regime

    # Class token map
    ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = ctm_data['token_to_class']

    # ================================================================
    # SECTION 1: Predictor Battery Construction
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 1: Predictor Battery Construction")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()

    # Pre-compute per-folio counts in single pass
    folio_ch = defaultdict(int)
    folio_sh = defaultdict(int)
    folio_qo_prefix = defaultdict(int)
    folio_total = defaultdict(int)
    folio_section = {}
    folio_en_qo = defaultdict(int)
    folio_en_chsh = defaultdict(int)
    folio_en_total = defaultdict(int)
    folio_cc_daiin = defaultdict(int)
    folio_cc_old = defaultdict(int)
    folio_cc_total = defaultdict(int)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word:
            continue
        folio = token.folio
        folio_total[folio] += 1
        folio_section[folio] = token.section

        # Prefix counts
        m = morph.extract(word)
        if m.prefix == 'ch':
            folio_ch[folio] += 1
        elif m.prefix == 'sh':
            folio_sh[folio] += 1
        if m.prefix == 'qo':
            folio_qo_prefix[folio] += 1

        # Class-based counts
        cls_str = token_to_class.get(word)
        if cls_str is not None:
            cls = int(cls_str)
            if cls in EN_QO:
                folio_en_qo[folio] += 1
                folio_en_total[folio] += 1
            elif cls in EN_CHSH:
                folio_en_chsh[folio] += 1
                folio_en_total[folio] += 1
            elif cls in EN_MINOR:
                folio_en_total[folio] += 1

            if cls in CC_DAIIN:
                folio_cc_daiin[folio] += 1
                folio_cc_total[folio] += 1
            elif cls in CC_OL:
                folio_cc_total[folio] += 1
            elif cls in CC_OL_D:
                folio_cc_old[folio] += 1
                folio_cc_total[folio] += 1

    # Build folio dataset
    MIN_CHSH = 5
    folio_battery = {}

    for folio in sorted(folio_total.keys()):
        ch = folio_ch[folio]
        sh = folio_sh[folio]
        if ch + sh < MIN_CHSH:
            continue

        ch_pref = ch / (ch + sh)
        escape = folio_qo_prefix[folio] / folio_total[folio] if folio_total[folio] > 0 else 0

        # EN proportions
        en_tot = folio_en_total[folio]
        if en_tot > 0:
            en_chsh_prop = folio_en_chsh[folio] / en_tot
            en_qo_prop = folio_en_qo[folio] / en_tot
        else:
            en_chsh_prop = None
            en_qo_prop = None

        # CC fractions
        cc_tot = folio_cc_total[folio]
        if cc_tot > 0:
            cc_daiin_frac = folio_cc_daiin[folio] / cc_tot
            cc_old_frac = folio_cc_old[folio] / cc_tot
        else:
            cc_daiin_frac = None
            cc_old_frac = None

        # Lane balance: CHSH-lane / (CHSH-lane + QO-lane)
        if en_chsh_prop is not None and cc_daiin_frac is not None and en_qo_prop is not None and cc_old_frac is not None:
            chsh_lane = en_chsh_prop * cc_daiin_frac
            qo_lane = en_qo_prop * cc_old_frac
            total_lane = chsh_lane + qo_lane
            if total_lane > 0:
                lane_bal = chsh_lane / total_lane
            else:
                lane_bal = None
        else:
            lane_bal = None

        # MIDDLE composition score
        mid_score = folio_comp_score.get(folio)

        folio_battery[folio] = {
            'ch_preference': ch_pref,
            'section': folio_section.get(folio, 'UNK'),
            'regime': folio_regime.get(folio, 'UNKNOWN'),
            'quire': folio_quire.get(folio, 'UNK'),
            'middle_comp_score': mid_score,
            'lane_balance': lane_bal,
            'cc_daiin_fraction': cc_daiin_frac,
            'escape_density': escape,
            'total_tokens': folio_total[folio],
        }

    # Report completeness
    n_total = len(folio_battery)
    n_lane = sum(1 for v in folio_battery.values() if v['lane_balance'] is not None)
    n_mid = sum(1 for v in folio_battery.values() if v['middle_comp_score'] is not None)

    print(f"\nFolios with ch_preference (>=5 ch+sh): {n_total}")
    print(f"Folios with lane_balance: {n_lane}")
    print(f"Folios with middle_comp_score: {n_mid}")

    # Use folios with ALL predictors available
    complete_folios = sorted([
        f for f, v in folio_battery.items()
        if v['lane_balance'] is not None
        and v['middle_comp_score'] is not None
        and v['regime'] != 'UNKNOWN'
        and v['quire'] != 'UNK'
    ])
    n_complete = len(complete_folios)
    print(f"Folios with complete predictor battery: {n_complete}")

    # Extract vectors
    y_raw = np.array([folio_battery[f]['ch_preference'] for f in complete_folios])
    sections = [folio_battery[f]['section'] for f in complete_folios]
    regimes = [folio_battery[f]['regime'] for f in complete_folios]
    quires = [folio_battery[f]['quire'] for f in complete_folios]
    mid_scores = np.array([folio_battery[f]['middle_comp_score'] for f in complete_folios])
    lane_bals = np.array([folio_battery[f]['lane_balance'] for f in complete_folios])
    cc_daiin_fracs = np.array([folio_battery[f]['cc_daiin_fraction'] for f in complete_folios])
    escape_dens = np.array([folio_battery[f]['escape_density'] for f in complete_folios])
    total_tokens = np.array([folio_battery[f]['total_tokens'] for f in complete_folios])

    # Rank-transform continuous variables
    y = rank_transform(y_raw)
    mid_scores_r = rank_transform(mid_scores)
    lane_bals_r = rank_transform(lane_bals)

    # Create dummy variables
    section_dummies, section_cats = create_dummies(sections)
    regime_dummies, regime_cats = create_dummies(regimes)
    # For quire: only include quires with >=3 folios in complete set
    quire_counts = Counter(quires)
    quire_filtered = [q if quire_counts[q] >= 3 else '__OTHER__' for q in quires]
    quire_dummies, quire_cats = create_dummies(quire_filtered)

    print(f"\nSection categories: {section_cats}")
    print(f"REGIME categories: {regime_cats}")
    print(f"Quire categories (>=3 folios): {[c for c in quire_cats if c != '__OTHER__']}")

    print(f"\nPredictor dimensions:")
    print(f"  Section: {section_dummies.shape[1]} dummies")
    print(f"  REGIME: {regime_dummies.shape[1]} dummies")
    print(f"  Quire: {quire_dummies.shape[1]} dummies")
    print(f"  MIDDLE comp: 1 continuous (rank)")
    print(f"  Lane balance: 1 continuous (rank)")

    # Report EN definition discrepancy
    print(f"\nNOTE: EN definitions use C603-C605 (EN_CHSH=10 classes, EN_QO=7 classes)")
    print(f"      NOT canonical (EN_CHSH=2 classes, EN_QO=10 classes)")
    print(f"      This maintains comparability with C605 lane_balance (rho=-0.506)")

    # ================================================================
    # SECTION 2: Hierarchical Regression (Rank-Based OLS)
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 2: Hierarchical Regression (Rank-Based OLS)")
    print("=" * 70)

    n = len(y)
    steps = []

    # Step 1: Section alone
    X1 = section_dummies
    R2_1, adjR2_1, _, _ = ols_r_squared(X1, y)
    steps.append({
        'step': 1, 'predictors': 'Section',
        'R2': R2_1, 'adj_R2': adjR2_1, 'delta_R2': R2_1,
        'p_count': X1.shape[1],
    })
    print(f"\nStep 1: Section")
    print(f"  R2={R2_1:.4f}, adj_R2={adjR2_1:.4f}, delta_R2={R2_1:.4f}")
    print(f"  ({X1.shape[1]} dummies)")

    # Step 2: + REGIME
    X2 = np.column_stack([section_dummies, regime_dummies]) if regime_dummies.shape[1] > 0 else section_dummies
    R2_2, adjR2_2, _, _ = ols_r_squared(X2, y)
    delta_2 = R2_2 - R2_1
    steps.append({
        'step': 2, 'predictors': '+ REGIME',
        'R2': R2_2, 'adj_R2': adjR2_2, 'delta_R2': delta_2,
        'p_count': X2.shape[1],
    })
    print(f"\nStep 2: + REGIME")
    print(f"  R2={R2_2:.4f}, adj_R2={adjR2_2:.4f}, delta_R2={delta_2:.4f}")

    # Step 3: + Quire
    if quire_dummies.shape[1] > 0:
        X3 = np.column_stack([X2, quire_dummies])
    else:
        X3 = X2
    R2_3, adjR2_3, _, _ = ols_r_squared(X3, y)
    delta_3 = R2_3 - R2_2
    steps.append({
        'step': 3, 'predictors': '+ Quire',
        'R2': R2_3, 'adj_R2': adjR2_3, 'delta_R2': delta_3,
        'p_count': X3.shape[1],
    })
    print(f"\nStep 3: + Quire")
    print(f"  R2={R2_3:.4f}, adj_R2={adjR2_3:.4f}, delta_R2={delta_3:.4f}")

    # Step 4: + MIDDLE composition score
    X4 = np.column_stack([X3, mid_scores_r.reshape(-1, 1)])
    R2_4, adjR2_4, _, _ = ols_r_squared(X4, y)
    delta_4 = R2_4 - R2_3
    steps.append({
        'step': 4, 'predictors': '+ MIDDLE comp',
        'R2': R2_4, 'adj_R2': adjR2_4, 'delta_R2': delta_4,
        'p_count': X4.shape[1],
    })
    print(f"\nStep 4: + MIDDLE composition")
    print(f"  R2={R2_4:.4f}, adj_R2={adjR2_4:.4f}, delta_R2={delta_4:.4f}")

    # Step 5: + Lane balance
    X5 = np.column_stack([X4, lane_bals_r.reshape(-1, 1)])
    R2_5, adjR2_5, _, resid_full = ols_r_squared(X5, y)
    delta_5 = R2_5 - R2_4
    steps.append({
        'step': 5, 'predictors': '+ Lane balance',
        'R2': R2_5, 'adj_R2': adjR2_5, 'delta_R2': delta_5,
        'p_count': X5.shape[1],
    })
    print(f"\nStep 5: + Lane balance (full model)")
    print(f"  R2={R2_5:.4f}, adj_R2={adjR2_5:.4f}, delta_R2={delta_5:.4f}")

    # Summary table
    print(f"\n--- Hierarchical Regression Summary ---")
    print(f"{'Step':<5} {'Predictors':<20} {'R2':>8} {'adj_R2':>8} {'delta_R2':>9}")
    print("-" * 55)
    for s in steps:
        print(f"{s['step']:<5} {s['predictors']:<20} {s['R2']:>8.4f} {s['adj_R2']:>8.4f} {s['delta_R2']:>9.4f}")

    print(f"\nTotal R2: {R2_5:.4f} ({R2_5*100:.1f}% explained)")
    print(f"Total adj_R2: {adjR2_5:.4f}")
    print(f"Unexplained: {(1-R2_5)*100:.1f}%")
    print(f"N={n}, p={X5.shape[1]}")

    # ================================================================
    # SECTION 3: Unique Variance (Semipartial)
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 3: Unique Variance (Semipartial Correlations)")
    print("=" * 70)

    # Full model R2
    R2_full = R2_5

    # Define predictor groups by column indices
    # Group boundaries in X5:
    # section: 0 .. section_dummies.shape[1]-1
    # regime: section_dummies.shape[1] .. section_dummies.shape[1]+regime_dummies.shape[1]-1
    # quire: ... quire_dummies.shape[1]
    # middle_comp: 1 column
    # lane_balance: 1 column

    sec_end = section_dummies.shape[1]
    reg_end = sec_end + regime_dummies.shape[1]
    qui_end = reg_end + quire_dummies.shape[1]
    mid_end = qui_end + 1
    lan_end = mid_end + 1

    # Full model columns
    X_full = X5  # shape: (n, lan_end)

    def r2_without(exclude_start, exclude_end):
        """R2 of model excluding columns [exclude_start:exclude_end] from X_full."""
        cols_keep = list(range(0, exclude_start)) + list(range(exclude_end, X_full.shape[1]))
        if len(cols_keep) == 0:
            return 0.0
        X_reduced = X_full[:, cols_keep]
        r2, _, _, _ = ols_r_squared(X_reduced, y)
        return r2

    # Unique contributions
    unique_section = R2_full - r2_without(0, sec_end)
    unique_regime = R2_full - r2_without(sec_end, reg_end)
    unique_quire = R2_full - r2_without(reg_end, qui_end)
    unique_middle = R2_full - r2_without(qui_end, mid_end)
    unique_lane = R2_full - r2_without(mid_end, lan_end)

    sum_unique = unique_section + unique_regime + unique_quire + unique_middle + unique_lane
    shared = R2_full - sum_unique
    unexplained = 1 - R2_full

    print(f"\n{'Predictor':<20} {'Unique R2':>10} {'% of Total':>12}")
    print("-" * 45)
    components = [
        ('Section', unique_section),
        ('REGIME', unique_regime),
        ('Quire', unique_quire),
        ('MIDDLE comp', unique_middle),
        ('Lane balance', unique_lane),
        ('Shared', shared),
        ('UNEXPLAINED', unexplained),
    ]

    for name, val in components:
        pct = val * 100
        print(f"  {name:<18} {val:>10.4f} {pct:>10.1f}%")

    print(f"\nTotal explained: {R2_full:.4f} ({R2_full*100:.1f}%)")
    print(f"Sum of unique: {sum_unique:.4f} ({sum_unique*100:.1f}%)")
    print(f"Shared (overlap): {shared:.4f} ({shared*100:.1f}%)")

    # Rank of predictors by unique variance
    predictor_ranks = sorted(
        [(name, val) for name, val in components if name not in ('Shared', 'UNEXPLAINED')],
        key=lambda x: x[1], reverse=True
    )
    print(f"\nPredictor ranking by unique variance:")
    for i, (name, val) in enumerate(predictor_ranks, 1):
        print(f"  {i}. {name}: {val:.4f} ({val*100:.1f}%)")

    # ================================================================
    # SECTION 4: Residual Analysis
    # ================================================================
    print("\n" + "=" * 70)
    print("SECTION 4: Residual Analysis")
    print("=" * 70)

    # Sort folios by natural order for lag analysis
    # Use folio name as sorting key
    folio_order = list(range(n))  # already in sorted folio order from complete_folios

    residuals = resid_full

    # 4a. Lag-1 autocorrelation
    lag1_corr = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
    print(f"\n4a. Lag-1 autocorrelation (sequential folios):")
    print(f"    r = {lag1_corr:.4f}")
    print(f"    {'Significant sequential dependency' if abs(lag1_corr) > 2/np.sqrt(n) else 'No significant sequential dependency'}")

    # 4b. Durbin-Watson
    diff_resid = np.diff(residuals)
    DW = np.sum(diff_resid ** 2) / np.sum(residuals ** 2)
    print(f"\n4b. Durbin-Watson statistic:")
    print(f"    DW = {DW:.4f}")
    print(f"    (2.0 = no autocorrelation; <1.5 or >2.5 = concern)")

    # 4c. Residuals vs token count (size effect)
    rho_size = np.corrcoef(rank_transform(total_tokens), residuals)[0, 1]
    print(f"\n4c. Residuals vs folio token count:")
    print(f"    Pearson r = {rho_size:.4f}")
    print(f"    {'Size effect detected' if abs(rho_size) > 0.22 else 'No size effect'}")

    # 4d. Outlier identification (|residual| > 2 SD)
    resid_std = np.std(residuals)
    resid_mean = np.mean(residuals)
    outliers = []
    for i, f in enumerate(complete_folios):
        z = (residuals[i] - resid_mean) / resid_std if resid_std > 0 else 0
        if abs(z) > 2:
            outliers.append({
                'folio': f,
                'residual': float(residuals[i]),
                'z_score': float(z),
                'ch_preference': float(y_raw[i]),
                'predicted_rank': float(y[i] - residuals[i]),
                'section': folio_battery[f]['section'],
                'regime': folio_battery[f]['regime'],
            })

    print(f"\n4d. Outlier folios (|z| > 2 SD):")
    if outliers:
        for o in sorted(outliers, key=lambda x: abs(x['z_score']), reverse=True):
            direction = "OVER" if o['z_score'] > 0 else "UNDER"
            print(f"    {o['folio']}: z={o['z_score']:.2f} ({direction}-predicted), "
                  f"ch_pref={o['ch_preference']:.3f}, {o['section']}/{o['regime']}")
    else:
        print(f"    None found")
    print(f"    Expected ~{n*0.046:.0f} outliers by chance (4.6% of {n})")

    # 4e. Normality check (skewness and kurtosis of residuals)
    skew = np.mean(((residuals - resid_mean) / resid_std) ** 3) if resid_std > 0 else 0
    kurt = np.mean(((residuals - resid_mean) / resid_std) ** 4) - 3 if resid_std > 0 else 0
    print(f"\n4e. Residual distribution:")
    print(f"    Skewness: {skew:.3f} (0 = symmetric)")
    print(f"    Excess kurtosis: {kurt:.3f} (0 = normal)")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nTotal explained variance: {R2_full*100:.1f}% (adj: {adjR2_5*100:.1f}%)")
    print(f"Unexplained 'free choice': {unexplained*100:.1f}%")

    print(f"\nVariance budget:")
    for name, val in components:
        bar = "#" * int(val * 100)
        print(f"  {name:<18} {val*100:>5.1f}% {bar}")

    # Determine dominant predictor
    top_pred = predictor_ranks[0][0]
    top_val = predictor_ranks[0][1]
    print(f"\nDominant unique predictor: {top_pred} ({top_val*100:.1f}%)")

    # Interpretation
    if unexplained > 0.5:
        choice_verdict = "MAJORITY_FREE_CHOICE"
    elif unexplained > 0.3:
        choice_verdict = "SUBSTANTIALLY_FREE"
    else:
        choice_verdict = "LARGELY_DETERMINED"

    print(f"Verdict: {choice_verdict}")
    print(f"  {unexplained*100:.1f}% of ch_preference variance is unexplained")
    print(f"  by section, REGIME, quire, MIDDLE composition, and lane balance")

    # ================================================================
    # SAVE OUTPUT
    # ================================================================
    output = {
        'metadata': {
            'phase': 'SISTER_PAIR_CHOICE_DYNAMICS',
            'script': 'choice_variance_decomposition.py',
            'description': 'Hierarchical variance decomposition of ch_preference',
            'n_complete_folios': n_complete,
            'total_predictors': int(X5.shape[1]),
            'en_definition_note': 'Uses C603-C605 EN definitions (EN_CHSH=10 classes, EN_QO=7 classes) for lane_balance comparability with C605',
        },
        'predictor_battery': {
            'section': {
                'categories': section_cats,
                'n_dummies': int(section_dummies.shape[1]),
            },
            'regime': {
                'categories': regime_cats,
                'n_dummies': int(regime_dummies.shape[1]),
            },
            'quire': {
                'categories': quire_cats,
                'n_dummies': int(quire_dummies.shape[1]),
                'min_count': 3,
            },
            'middle_comp_score': {'type': 'continuous_rank'},
            'lane_balance': {'type': 'continuous_rank'},
        },
        'hierarchical_regression': {
            'steps': steps,
            'total_R2': R2_full,
            'total_adj_R2': float(adjR2_5),
            'unexplained': unexplained,
            'N': n,
            'p': int(X5.shape[1]),
        },
        'semipartial': {
            'unique_section': unique_section,
            'unique_regime': unique_regime,
            'unique_quire': unique_quire,
            'unique_middle': unique_middle,
            'unique_lane_balance': unique_lane,
            'shared': shared,
            'unexplained': unexplained,
            'total_explained': R2_full,
        },
        'residual_analysis': {
            'lag1_autocorrelation': float(lag1_corr),
            'durbin_watson': float(DW),
            'size_effect_r': float(rho_size),
            'n_outliers': len(outliers),
            'outliers': outliers,
            'skewness': float(skew),
            'excess_kurtosis': float(kurt),
        },
        'verdict': choice_verdict,
        'predictor_ranking': [
            {'predictor': name, 'unique_R2': val, 'pct': round(val * 100, 1)}
            for name, val in predictor_ranks
        ],
    }

    output_path = results_dir / 'choice_variance_decomposition.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nSaved: {output_path}")


if __name__ == '__main__':
    main()
