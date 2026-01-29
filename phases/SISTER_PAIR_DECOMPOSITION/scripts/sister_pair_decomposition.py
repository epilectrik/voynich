"""
SISTER_PAIR_DECOMPOSITION Script 2: Decompose C412

Decompose the C412 anticorrelation (ch-preference ~ escape-density, rho=-0.326)
through sub-group variables: EN subfamily balance, CC trigger composition,
REGIME assignment, and FL hazard fraction.

Tests whether C412 is a direct effect or mediated by EN subfamily balance,
CC composition, or REGIME.

Data dependencies:
  - en_subfamily_selection.json (Script 1 output)
  - class_token_map.json (CLASS_COSURVIVAL_TEST)
  - regime_folio_mapping.json (REGIME_SEMANTIC_INTERPRETATION)
  - voynich.py (scripts/)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
SCRIPT1_RESULTS = BASE / 'phases/SISTER_PAIR_DECOMPOSITION/results/en_subfamily_selection.json'
RESULTS = BASE / 'phases/SISTER_PAIR_DECOMPOSITION/results'

# Sub-group definitions (from SUB_ROLE_INTERACTION)
EN_QO = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR = {41}
EN_CLASSES = EN_QO | EN_CHSH | EN_MINOR

CC_DAIIN = {10}
CC_OL = {11}
CC_OL_D = {17}

FL_HAZ = {7, 30}
FL_SAFE = {38, 40}

# Morphology for PREFIX extraction
morph = Morphology()
CORE_PREFIXES_CH = {'ch'}
CORE_PREFIXES_SH = {'sh'}
CORE_PREFIXES_QO = {'qo'}

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("SISTER_PAIR_DECOMPOSITION: C412 DECOMPOSITION")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Load Script 1 results for folio-level sub-group data
with open(SCRIPT1_RESULTS) as f:
    script1 = json.load(f)
folio_data_s1 = script1['folio_data']

results = {}

# ============================================================
# SECTION 1: REPLICATE C412
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: REPLICATE C412")
print("=" * 70)

# Per folio: ch_preference = ch/(ch+sh), escape_density = qo/total
# Requires >=10 tokens and >=5 ch+sh tokens
folio_prefix_counts = defaultdict(Counter)
folio_token_counts = Counter()

for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    folio_token_counts[token.folio] += 1
    m = morph.extract(word)
    if m.prefix in CORE_PREFIXES_CH:
        folio_prefix_counts[token.folio]['ch'] += 1
    elif m.prefix in CORE_PREFIXES_SH:
        folio_prefix_counts[token.folio]['sh'] += 1
    if m.prefix in CORE_PREFIXES_QO:
        folio_prefix_counts[token.folio]['qo'] += 1

# Build C412 vectors
MIN_TOKENS = 10
MIN_CHSH = 5

c412_folios = []
c412_ch_pref = []
c412_escape = []

for folio in sorted(folio_token_counts.keys()):
    total = folio_token_counts[folio]
    if total < MIN_TOKENS:
        continue
    ch = folio_prefix_counts[folio].get('ch', 0)
    sh = folio_prefix_counts[folio].get('sh', 0)
    qo = folio_prefix_counts[folio].get('qo', 0)
    if ch + sh < MIN_CHSH:
        continue
    ch_pref = ch / (ch + sh)
    escape_dens = qo / total
    c412_folios.append(folio)
    c412_ch_pref.append(ch_pref)
    c412_escape.append(escape_dens)

c412_ch_pref = np.array(c412_ch_pref)
c412_escape = np.array(c412_escape)

rho_c412, p_c412 = stats.spearmanr(c412_ch_pref, c412_escape)
print(f"\nC412 Replication:")
print(f"  N = {len(c412_folios)} folios")
print(f"  Spearman rho = {rho_c412:.4f} (expected ~-0.326)")
print(f"  p-value = {p_c412:.6f} (expected ~0.002)")
print(f"  Replication: {'SUCCESS' if abs(rho_c412 - (-0.326)) < 0.05 else 'CHECK'}")

results['c412_replication'] = {
    'rho': round(float(rho_c412), 4),
    'p_value': float(p_c412),
    'n': len(c412_folios),
    'expected_rho': -0.326,
    'replication_success': bool(abs(rho_c412 - (-0.326)) < 0.05),
}

# ============================================================
# SECTION 2: FOLIO-LEVEL VARIABLE BATTERY
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: FOLIO-LEVEL VARIABLE BATTERY")
print("=" * 70)

# Build comprehensive folio-level dataset
# Only for folios in the C412 valid set
folio_vars = {}
for i, folio in enumerate(c412_folios):
    row = {
        'ch_preference': float(c412_ch_pref[i]),
        'escape_density': float(c412_escape[i]),
        'regime': folio_regime.get(folio, 'UNKNOWN'),
    }

    # EN subfamily balance from Script 1
    if folio in folio_data_s1:
        s1 = folio_data_s1[folio]
        en_total = s1['en_total']
        if en_total > 0:
            row['en_chsh_proportion'] = s1['chsh_count'] / en_total
            row['en_qo_proportion'] = s1['qo_count'] / en_total
        else:
            row['en_chsh_proportion'] = None
            row['en_qo_proportion'] = None

        # CC composition
        if s1['cc_total'] > 0:
            row['cc_daiin_fraction'] = s1['cc_daiin'] / s1['cc_total']
            row['cc_old_fraction'] = s1['cc_old'] / s1['cc_total']
        else:
            row['cc_daiin_fraction'] = None
            row['cc_old_fraction'] = None

        # FL composition
        fl_total = s1['fl_haz'] + s1['fl_safe']
        if fl_total > 0:
            row['fl_haz_fraction'] = s1['fl_haz'] / fl_total
        else:
            row['fl_haz_fraction'] = None

        row['total_tokens'] = s1['b_total']
        row['section'] = s1.get('section', 'UNKNOWN')
    else:
        row['en_chsh_proportion'] = None
        row['en_qo_proportion'] = None
        row['cc_daiin_fraction'] = None
        row['cc_old_fraction'] = None
        row['fl_haz_fraction'] = None
        row['total_tokens'] = folio_token_counts[folio]
        row['section'] = 'UNKNOWN'

    folio_vars[folio] = row

n_complete = sum(1 for v in folio_vars.values()
                 if all(v.get(k) is not None for k in
                        ['en_chsh_proportion', 'cc_daiin_fraction', 'fl_haz_fraction']))
print(f"\nFolios in C412 set: {len(folio_vars)}")
print(f"Complete data (all variables): {n_complete}")

# Print summary stats for each variable
numeric_keys = ['ch_preference', 'escape_density', 'en_chsh_proportion',
                'en_qo_proportion', 'cc_daiin_fraction', 'cc_old_fraction',
                'fl_haz_fraction']

print(f"\n{'Variable':>22} {'N':>4} {'Mean':>7} {'Std':>7} {'Min':>7} {'Max':>7}")
print("-" * 60)
var_stats = {}
for key in numeric_keys:
    vals = [folio_vars[f][key] for f in c412_folios if folio_vars[f].get(key) is not None]
    if vals:
        arr = np.array(vals)
        print(f"{key:>22} {len(vals):>4} {np.mean(arr):>7.3f} {np.std(arr):>7.3f} "
              f"{np.min(arr):>7.3f} {np.max(arr):>7.3f}")
        var_stats[key] = {'n': len(vals), 'mean': round(float(np.mean(arr)), 4),
                          'std': round(float(np.std(arr)), 4)}

results['variable_stats'] = var_stats

# ============================================================
# SECTION 3: CORRELATION MATRIX
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: CORRELATION MATRIX")
print("=" * 70)

# Pairwise Spearman correlations for all numeric variables
# Only use folios with complete data for each pair
correlation_matrix = {}
print(f"\n{'Pair':>45} {'rho':>7} {'p':>10} {'n':>4} {'Sig?':>5}")
print("-" * 75)

key_pairs = [
    ('ch_preference', 'escape_density'),
    ('ch_preference', 'en_chsh_proportion'),
    ('escape_density', 'en_qo_proportion'),
    ('ch_preference', 'cc_daiin_fraction'),
    ('ch_preference', 'fl_haz_fraction'),
    ('en_chsh_proportion', 'escape_density'),
    ('en_chsh_proportion', 'en_qo_proportion'),
    ('cc_daiin_fraction', 'en_chsh_proportion'),
    ('cc_old_fraction', 'en_qo_proportion'),
    ('cc_daiin_fraction', 'cc_old_fraction'),
    ('fl_haz_fraction', 'en_chsh_proportion'),
]

# Full matrix for all pairs
all_pairs = []
for i, k1 in enumerate(numeric_keys):
    for k2 in numeric_keys[i+1:]:
        all_pairs.append((k1, k2))

for k1, k2 in all_pairs:
    valid = [(folio_vars[f][k1], folio_vars[f][k2])
             for f in c412_folios
             if folio_vars[f].get(k1) is not None and folio_vars[f].get(k2) is not None]
    if len(valid) < 10:
        continue
    v1, v2 = zip(*valid)
    rho, p = stats.spearmanr(v1, v2)
    is_key = (k1, k2) in key_pairs or (k2, k1) in key_pairs
    sig = '*' if p < 0.05 else ''
    bonf = '**' if p < 0.05 / len(all_pairs) else sig
    marker = '  <--' if is_key else ''
    print(f"{k1:>20} ~ {k2:<22} {rho:>7.3f} {p:>10.4f} {len(valid):>4} {bonf:>5}{marker}")
    correlation_matrix[f"{k1} ~ {k2}"] = {
        'rho': round(float(rho), 4),
        'p_value': float(p),
        'n': len(valid),
        'significant_raw': bool(p < 0.05),
        'significant_bonferroni': bool(p < 0.05 / len(all_pairs)),
    }

results['correlation_matrix'] = correlation_matrix

# ============================================================
# SECTION 4: MEDIATION ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: MEDIATION ANALYSIS")
print("=" * 70)

def rank_partial_correlation(x, y, z):
    """
    Compute rank-based partial correlation of x and y controlling for z.
    Method: rank all variables, regress out z from x and y, correlate residuals.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    z = np.array(z, dtype=float)

    # Rank transform
    x_rank = stats.rankdata(x)
    y_rank = stats.rankdata(y)
    z_rank = stats.rankdata(z)

    # Regress z out of x
    slope_xz, intercept_xz, _, _, _ = stats.linregress(z_rank, x_rank)
    x_resid = x_rank - (slope_xz * z_rank + intercept_xz)

    # Regress z out of y
    slope_yz, intercept_yz, _, _, _ = stats.linregress(z_rank, y_rank)
    y_resid = y_rank - (slope_yz * z_rank + intercept_yz)

    # Correlate residuals
    rho, p = stats.spearmanr(x_resid, y_resid)
    return rho, p

# Get aligned data for mediation tests
def get_aligned(keys):
    """Get folios that have all specified keys non-None."""
    valid = [f for f in c412_folios
             if all(folio_vars[f].get(k) is not None for k in keys)]
    return valid

print("\n--- Mediation through EN subfamily balance ---")
med_folios = get_aligned(['ch_preference', 'escape_density', 'en_chsh_proportion'])
print(f"Folios with complete data: {len(med_folios)}")

if len(med_folios) >= 20:
    ch_p = [folio_vars[f]['ch_preference'] for f in med_folios]
    esc_d = [folio_vars[f]['escape_density'] for f in med_folios]
    en_chsh = [folio_vars[f]['en_chsh_proportion'] for f in med_folios]

    # Path a: ch_preference -> en_chsh_proportion
    rho_a, p_a = stats.spearmanr(ch_p, en_chsh)
    print(f"  Path a (ch_pref -> en_chsh): rho={rho_a:.4f}, p={p_a:.4f}")

    # Path b: en_chsh_proportion -> escape_density
    rho_b, p_b = stats.spearmanr(en_chsh, esc_d)
    print(f"  Path b (en_chsh -> escape): rho={rho_b:.4f}, p={p_b:.4f}")

    # Direct: ch_preference -> escape_density
    rho_direct, p_direct = stats.spearmanr(ch_p, esc_d)
    print(f"  Direct (ch_pref -> escape): rho={rho_direct:.4f}, p={p_direct:.4f}")

    # Partial: controlling for en_chsh
    rho_partial, p_partial = rank_partial_correlation(ch_p, esc_d, en_chsh)
    print(f"  Partial (ch_pref -> escape | en_chsh): rho={rho_partial:.4f}, p={p_partial:.4f}")

    reduction = abs(rho_direct) - abs(rho_partial)
    pct_reduction = reduction / abs(rho_direct) * 100 if rho_direct != 0 else 0
    print(f"  Reduction: {reduction:.4f} ({pct_reduction:.1f}%)")
    if pct_reduction > 50:
        print(f"  --> EN subfamily MEDIATES C412 (>{50}% reduction)")
    elif pct_reduction > 20:
        print(f"  --> EN subfamily PARTIALLY mediates C412 ({pct_reduction:.0f}% reduction)")
    else:
        print(f"  --> EN subfamily does NOT mediate C412 (<20% reduction)")

    results['mediation_en_chsh'] = {
        'n': len(med_folios),
        'path_a': {'rho': round(float(rho_a), 4), 'p': float(p_a)},
        'path_b': {'rho': round(float(rho_b), 4), 'p': float(p_b)},
        'direct': {'rho': round(float(rho_direct), 4), 'p': float(p_direct)},
        'partial': {'rho': round(float(rho_partial), 4), 'p': float(p_partial)},
        'reduction_pct': round(float(pct_reduction), 1),
    }

print("\n--- Mediation through CC composition ---")
med_cc_folios = get_aligned(['ch_preference', 'escape_density', 'cc_old_fraction'])
print(f"Folios with complete data: {len(med_cc_folios)}")

if len(med_cc_folios) >= 20:
    ch_p2 = [folio_vars[f]['ch_preference'] for f in med_cc_folios]
    esc_d2 = [folio_vars[f]['escape_density'] for f in med_cc_folios]
    cc_old2 = [folio_vars[f]['cc_old_fraction'] for f in med_cc_folios]

    rho_direct2, p_direct2 = stats.spearmanr(ch_p2, esc_d2)
    rho_partial2, p_partial2 = rank_partial_correlation(ch_p2, esc_d2, cc_old2)
    reduction2 = abs(rho_direct2) - abs(rho_partial2)
    pct_reduction2 = reduction2 / abs(rho_direct2) * 100 if rho_direct2 != 0 else 0

    print(f"  Direct: rho={rho_direct2:.4f}")
    print(f"  Partial (| cc_old_fraction): rho={rho_partial2:.4f}, p={p_partial2:.4f}")
    print(f"  Reduction: {reduction2:.4f} ({pct_reduction2:.1f}%)")

    results['mediation_cc'] = {
        'n': len(med_cc_folios),
        'direct': {'rho': round(float(rho_direct2), 4)},
        'partial': {'rho': round(float(rho_partial2), 4), 'p': float(p_partial2)},
        'reduction_pct': round(float(pct_reduction2), 1),
    }

print("\n--- Mediation through REGIME ---")
# Encode REGIME as numeric (1-4)
regime_numeric = {'REGIME_1': 1, 'REGIME_2': 2, 'REGIME_3': 3, 'REGIME_4': 4}
med_reg_folios = [f for f in c412_folios if folio_vars[f]['regime'] in regime_numeric]
print(f"Folios with REGIME assignment: {len(med_reg_folios)}")

if len(med_reg_folios) >= 20:
    ch_p3 = [folio_vars[f]['ch_preference'] for f in med_reg_folios]
    esc_d3 = [folio_vars[f]['escape_density'] for f in med_reg_folios]
    reg3 = [regime_numeric[folio_vars[f]['regime']] for f in med_reg_folios]

    rho_direct3, p_direct3 = stats.spearmanr(ch_p3, esc_d3)
    rho_partial3, p_partial3 = rank_partial_correlation(ch_p3, esc_d3, reg3)
    reduction3 = abs(rho_direct3) - abs(rho_partial3)
    pct_reduction3 = reduction3 / abs(rho_direct3) * 100 if rho_direct3 != 0 else 0

    print(f"  Direct: rho={rho_direct3:.4f}")
    print(f"  Partial (| REGIME): rho={rho_partial3:.4f}, p={p_partial3:.4f}")
    print(f"  Reduction: {reduction3:.4f} ({pct_reduction3:.1f}%)")

    results['mediation_regime'] = {
        'n': len(med_reg_folios),
        'direct': {'rho': round(float(rho_direct3), 4)},
        'partial': {'rho': round(float(rho_partial3), 4), 'p': float(p_partial3)},
        'reduction_pct': round(float(pct_reduction3), 1),
    }

# ============================================================
# SECTION 5: REGIME STRATIFICATION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: REGIME STRATIFICATION")
print("=" * 70)

REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
regime_stratified = {}

print(f"\nC412 within each REGIME:")
for regime in REGIMES:
    reg_folios = [f for f in c412_folios if folio_vars[f]['regime'] == regime]
    if len(reg_folios) < 8:
        print(f"  {regime}: n={len(reg_folios)} (insufficient)")
        regime_stratified[regime] = {'n': len(reg_folios), 'verdict': 'insufficient'}
        continue

    ch_vals = [folio_vars[f]['ch_preference'] for f in reg_folios]
    esc_vals = [folio_vars[f]['escape_density'] for f in reg_folios]
    rho_r, p_r = stats.spearmanr(ch_vals, esc_vals)
    sig = '*' if p_r < 0.05 else ''
    print(f"  {regime}: rho={rho_r:.3f}, p={p_r:.4f}, n={len(reg_folios)} {sig}")

    regime_stratified[regime] = {
        'rho': round(float(rho_r), 4),
        'p_value': float(p_r),
        'n': len(reg_folios),
        'significant': bool(p_r < 0.05),
    }

# Check if C412 persists within all REGIMEs
persists_count = sum(1 for r in REGIMES
                     if regime_stratified[r].get('rho', 0) < -0.1
                     and regime_stratified[r].get('n', 0) >= 8)
print(f"\nREGIMEs where C412 persists (rho < -0.1): {persists_count}/{len(REGIMES)}")
if persists_count >= 3:
    print("  --> C412 is NOT a REGIME artifact (persists within REGIMEs)")
else:
    print("  --> C412 may be partially explained by REGIME confounding")

results['regime_stratification'] = regime_stratified

# ============================================================
# SECTION 6: MODEL COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: MODEL COMPARISON")
print("=" * 70)

# Rank predictors of ch_preference using Spearman correlations
predictors_of_ch = [
    ('escape_density', 'C412 baseline'),
    ('en_chsh_proportion', 'EN subfamily balance'),
    ('cc_daiin_fraction', 'CC DAIIN trigger fraction'),
    ('fl_haz_fraction', 'FL hazard fraction'),
]

print(f"\nPredictors of ch_preference:")
print(f"{'Variable':>25} {'rho':>7} {'p':>10} {'n':>4}")
print("-" * 55)

predictor_results = []
for key, label in predictors_of_ch:
    valid = [(folio_vars[f]['ch_preference'], folio_vars[f][key])
             for f in c412_folios
             if folio_vars[f].get(key) is not None]
    if len(valid) < 10:
        print(f"{label:>25} {'N/A':>7} {'N/A':>10} {len(valid):>4}")
        continue
    v1, v2 = zip(*valid)
    rho, p = stats.spearmanr(v1, v2)
    sig = '*' if p < 0.05 else ''
    print(f"{label:>25} {rho:>7.3f} {p:>10.4f} {len(valid):>4} {sig}")
    predictor_results.append({
        'variable': key,
        'label': label,
        'rho': round(float(rho), 4),
        'p_value': float(p),
        'n': len(valid),
        'abs_rho': round(abs(float(rho)), 4),
    })

# Rank by absolute rho
predictor_results.sort(key=lambda x: x['abs_rho'], reverse=True)
print(f"\nRanking by |rho|:")
for rank, pr in enumerate(predictor_results, 1):
    print(f"  {rank}. {pr['label']}: |rho|={pr['abs_rho']:.3f}")

results['predictors_of_ch'] = predictor_results

# REGIME Kruskal-Wallis for ch_preference
regime_ch_groups = defaultdict(list)
for f in c412_folios:
    r = folio_vars[f]['regime']
    if r in REGIMES:
        regime_ch_groups[r].append(folio_vars[f]['ch_preference'])

groups = [regime_ch_groups[r] for r in REGIMES if len(regime_ch_groups[r]) >= 3]
if len(groups) >= 2:
    h_kw, p_kw = stats.kruskal(*groups)
    print(f"\nKruskal-Wallis (REGIME -> ch_preference):")
    print(f"  H={h_kw:.3f}, p={p_kw:.6f}")
    for r in REGIMES:
        vals = regime_ch_groups[r]
        if vals:
            print(f"  {r}: mean={np.mean(vals):.3f}, n={len(vals)}")
    results['regime_ch_kw'] = {
        'H': round(float(h_kw), 4),
        'p_value': float(p_kw),
        'significant': bool(p_kw < 0.05),
    }

# Multiple regression using rank-based approach
# Forward selection: add variables until no improvement
print(f"\n--- Forward Selection (rank-based regression) ---")
complete_folios = get_aligned(['ch_preference', 'escape_density',
                                'en_chsh_proportion', 'cc_daiin_fraction'])
print(f"Complete folios for regression: {len(complete_folios)}")

if len(complete_folios) >= 20:
    y = np.array([folio_vars[f]['ch_preference'] for f in complete_folios])
    y_rank = stats.rankdata(y)

    candidate_vars = {
        'escape_density': np.array([folio_vars[f]['escape_density'] for f in complete_folios]),
        'en_chsh_proportion': np.array([folio_vars[f]['en_chsh_proportion'] for f in complete_folios]),
        'cc_daiin_fraction': np.array([folio_vars[f]['cc_daiin_fraction'] for f in complete_folios]),
    }

    # Add fl_haz_fraction if available
    fl_complete = [f for f in complete_folios if folio_vars[f].get('fl_haz_fraction') is not None]
    if len(fl_complete) >= 20:
        # Use complete_folios subset that also has FL
        fl_available = True
    else:
        fl_available = False

    # Rank transform all
    for k in candidate_vars:
        candidate_vars[k] = stats.rankdata(candidate_vars[k])

    # Step 1: Best single predictor
    best_r2 = -1
    best_var = None
    for name, x in candidate_vars.items():
        slope, intercept, r, p, se = stats.linregress(x, y_rank)
        r2 = r ** 2
        if r2 > best_r2:
            best_r2 = r2
            best_var = name
    print(f"  Step 1: Best single = {best_var} (R2={best_r2:.4f})")

    # Step 2: Best pair
    selected = [best_var]
    remaining = [k for k in candidate_vars if k != best_var]
    X_selected = candidate_vars[best_var].reshape(-1, 1)

    best_r2_2 = best_r2
    best_add = None
    for name in remaining:
        X_test = np.column_stack([X_selected, candidate_vars[name].reshape(-1, 1)])
        # OLS regression
        X_aug = np.column_stack([np.ones(len(y_rank)), X_test])
        try:
            beta = np.linalg.lstsq(X_aug, y_rank, rcond=None)[0]
            y_pred = X_aug @ beta
            ss_res = np.sum((y_rank - y_pred) ** 2)
            ss_tot = np.sum((y_rank - np.mean(y_rank)) ** 2)
            r2 = 1 - ss_res / ss_tot
            if r2 > best_r2_2:
                best_r2_2 = r2
                best_add = name
        except np.linalg.LinAlgError:
            continue

    if best_add and best_r2_2 - best_r2 > 0.01:
        selected.append(best_add)
        print(f"  Step 2: Added {best_add} (R2={best_r2_2:.4f}, delta={best_r2_2-best_r2:.4f})")
    else:
        print(f"  Step 2: No improvement (best delta={best_r2_2-best_r2:.4f})")

    # Step 3: Best triple
    if len(selected) == 2:
        remaining2 = [k for k in candidate_vars if k not in selected]
        X_selected2 = np.column_stack([candidate_vars[s].reshape(-1, 1) for s in selected])
        best_r2_3 = best_r2_2
        best_add2 = None
        for name in remaining2:
            X_test = np.column_stack([X_selected2, candidate_vars[name].reshape(-1, 1)])
            X_aug = np.column_stack([np.ones(len(y_rank)), X_test])
            try:
                beta = np.linalg.lstsq(X_aug, y_rank, rcond=None)[0]
                y_pred = X_aug @ beta
                ss_res = np.sum((y_rank - y_pred) ** 2)
                ss_tot = np.sum((y_rank - np.mean(y_rank)) ** 2)
                r2 = 1 - ss_res / ss_tot
                if r2 > best_r2_3:
                    best_r2_3 = r2
                    best_add2 = name
            except np.linalg.LinAlgError:
                continue

        if best_add2 and best_r2_3 - best_r2_2 > 0.01:
            selected.append(best_add2)
            print(f"  Step 3: Added {best_add2} (R2={best_r2_3:.4f}, delta={best_r2_3-best_r2_2:.4f})")
        else:
            print(f"  Step 3: No improvement (best delta={best_r2_3-best_r2_2:.4f})")

    print(f"\n  Final model: {' + '.join(selected)}")

    results['forward_selection'] = {
        'n': len(complete_folios),
        'selected_vars': selected,
        'r2_values': {
            'step1': round(float(best_r2), 4),
            'step2': round(float(best_r2_2), 4) if best_add else None,
        },
    }

# ============================================================
# SECTION 7: TWO-LANE FOLIO PROFILE
# ============================================================
print("\n" + "=" * 70)
print("SECTION 7: TWO-LANE FOLIO PROFILE")
print("=" * 70)

# CHSH-lane intensity = en_chsh_proportion * cc_daiin_fraction
# QO-lane intensity = en_qo_proportion * cc_old_fraction
# Lane balance = CHSH-lane / (CHSH-lane + QO-lane)

lane_folios = get_aligned(['en_chsh_proportion', 'en_qo_proportion',
                            'cc_daiin_fraction', 'cc_old_fraction',
                            'escape_density', 'ch_preference'])
print(f"\nFolios with complete lane data: {len(lane_folios)}")

lane_data = {}
if len(lane_folios) >= 20:
    chsh_lane = []
    qo_lane = []
    lane_balance = []
    ch_pref_lane = []
    esc_lane = []

    for f in lane_folios:
        v = folio_vars[f]
        chsh_int = v['en_chsh_proportion'] * v['cc_daiin_fraction']
        qo_int = v['en_qo_proportion'] * v['cc_old_fraction']
        total_int = chsh_int + qo_int

        chsh_lane.append(chsh_int)
        qo_lane.append(qo_int)
        lane_balance.append(chsh_int / total_int if total_int > 0 else 0.5)
        ch_pref_lane.append(v['ch_preference'])
        esc_lane.append(v['escape_density'])

    lane_balance = np.array(lane_balance)
    ch_pref_lane = np.array(ch_pref_lane)
    esc_lane = np.array(esc_lane)

    print(f"\nLane balance distribution (0=all QO, 1=all CHSH):")
    print(f"  Mean: {np.mean(lane_balance):.3f}")
    print(f"  Std:  {np.std(lane_balance):.3f}")
    print(f"  Range: [{np.min(lane_balance):.3f}, {np.max(lane_balance):.3f}]")

    # Test 1: lane_balance -> ch_preference (expect positive)
    rho_lb_ch, p_lb_ch = stats.spearmanr(lane_balance, ch_pref_lane)
    print(f"\nLane balance vs ch_preference:")
    print(f"  rho={rho_lb_ch:.4f}, p={p_lb_ch:.4f}")
    print(f"  {'Positive (expected)' if rho_lb_ch > 0 else 'Negative (unexpected)'}")

    # Test 2: lane_balance -> escape_density (expect negative)
    rho_lb_esc, p_lb_esc = stats.spearmanr(lane_balance, esc_lane)
    print(f"\nLane balance vs escape_density:")
    print(f"  rho={rho_lb_esc:.4f}, p={p_lb_esc:.4f}")
    print(f"  {'Negative (expected)' if rho_lb_esc < 0 else 'Positive (unexpected)'}")

    # Test 3: is lane_balance a better predictor of escape_density than ch_preference?
    rho_ch_esc, p_ch_esc = stats.spearmanr(ch_pref_lane, esc_lane)
    print(f"\nComparison:")
    print(f"  ch_preference -> escape: |rho|={abs(rho_ch_esc):.4f}")
    print(f"  lane_balance  -> escape: |rho|={abs(rho_lb_esc):.4f}")
    if abs(rho_lb_esc) > abs(rho_ch_esc):
        print(f"  --> Lane balance is BETTER predictor (delta={abs(rho_lb_esc)-abs(rho_ch_esc):.4f})")
    else:
        print(f"  --> ch_preference is better predictor (delta={abs(rho_ch_esc)-abs(rho_lb_esc):.4f})")

    # Test 4: Partial correlation - escape ~ lane_balance | ch_preference
    rho_partial_lb, p_partial_lb = rank_partial_correlation(
        esc_lane, lane_balance, ch_pref_lane)
    print(f"\nPartial: escape ~ lane_balance | ch_preference:")
    print(f"  rho={rho_partial_lb:.4f}, p={p_partial_lb:.4f}")
    if abs(rho_partial_lb) > 0.1 and p_partial_lb < 0.05:
        print(f"  --> Lane balance adds INDEPENDENT information beyond ch_preference")
    else:
        print(f"  --> Lane balance does NOT add independent information")

    lane_data = {
        'n': len(lane_folios),
        'lane_balance_mean': round(float(np.mean(lane_balance)), 4),
        'lane_balance_std': round(float(np.std(lane_balance)), 4),
        'lb_vs_ch': {'rho': round(float(rho_lb_ch), 4), 'p': float(p_lb_ch)},
        'lb_vs_escape': {'rho': round(float(rho_lb_esc), 4), 'p': float(p_lb_esc)},
        'ch_vs_escape': {'rho': round(float(rho_ch_esc), 4), 'p': float(p_ch_esc)},
        'partial_escape_lb_given_ch': {'rho': round(float(rho_partial_lb), 4), 'p': float(p_partial_lb)},
        'lb_better_than_ch': bool(abs(rho_lb_esc) > abs(rho_ch_esc)),
    }

results['two_lane_validation'] = lane_data

# ============================================================
# SECTION 8: SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SECTION 8: OVERALL SUMMARY")
print("=" * 70)

print(f"\n1. C412 REPLICATION:")
print(f"   rho={results['c412_replication']['rho']:.4f}, p={results['c412_replication']['p_value']:.4f}")
print(f"   {'Replicated' if results['c412_replication']['replication_success'] else 'Not replicated'}")

print(f"\n2. MEDIATION ANALYSIS:")
if 'mediation_en_chsh' in results:
    r = results['mediation_en_chsh']
    print(f"   EN subfamily: {r['reduction_pct']:.1f}% reduction (partial rho={r['partial']['rho']:.4f})")
if 'mediation_cc' in results:
    r = results['mediation_cc']
    print(f"   CC composition: {r['reduction_pct']:.1f}% reduction (partial rho={r['partial']['rho']:.4f})")
if 'mediation_regime' in results:
    r = results['mediation_regime']
    print(f"   REGIME: {r['reduction_pct']:.1f}% reduction (partial rho={r['partial']['rho']:.4f})")

print(f"\n3. REGIME STRATIFICATION:")
for regime in REGIMES:
    if 'rho' in regime_stratified[regime]:
        print(f"   {regime}: rho={regime_stratified[regime]['rho']:.3f}, p={regime_stratified[regime]['p_value']:.4f}")

print(f"\n4. TWO-LANE MODEL:")
if lane_data:
    print(f"   Lane balance vs escape: rho={lane_data['lb_vs_escape']['rho']:.4f}")
    print(f"   Lane balance vs ch_pref: rho={lane_data['lb_vs_ch']['rho']:.4f}")
    print(f"   Better than ch_preference alone: {lane_data['lb_better_than_ch']}")

# Overall verdict
print(f"\n5. VERDICT:")
mediators = []
if 'mediation_en_chsh' in results and results['mediation_en_chsh']['reduction_pct'] > 20:
    mediators.append(f"EN subfamily ({results['mediation_en_chsh']['reduction_pct']:.0f}%)")
if 'mediation_cc' in results and results['mediation_cc']['reduction_pct'] > 20:
    mediators.append(f"CC composition ({results['mediation_cc']['reduction_pct']:.0f}%)")
if 'mediation_regime' in results and results['mediation_regime']['reduction_pct'] > 20:
    mediators.append(f"REGIME ({results['mediation_regime']['reduction_pct']:.0f}%)")

if mediators:
    print(f"   C412 partially decomposes through: {', '.join(mediators)}")
else:
    print(f"   C412 does NOT decompose through tested variables (direct effect)")

results['verdict'] = {
    'mediators': mediators,
    'c412_decomposes': bool(len(mediators) > 0),
}

# ============================================================
# SAVE
# ============================================================
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sister_pair_decomposition.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'sister_pair_decomposition.json'}")
