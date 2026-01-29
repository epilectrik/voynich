"""
RECOVERY_ARCHITECTURE_DECOMPOSITION - Script 3: Recovery-Regime Interaction

Folio-level recovery feature battery, raw KW tests of REGIME prediction,
partial correlation controlling for class composition, overall verdict.

Sections:
  1. Folio-level recovery feature battery (from Scripts 1+2 + raw class counts)
  2. Raw REGIME prediction (KW tests on each feature)
  3. Partial correlation (regress out class composition, KW on residuals)
  4. Overall verdict (UNCONDITIONALLY FREE / CLASS-MEDIATED / REGIME-STRATIFIED)

Output: results/recovery_regime_interaction.json
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import kruskal, rankdata

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

# =============================================================================
# JSON encoder
# =============================================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# =============================================================================
# Constants
# =============================================================================

KERNEL_CLASSES = {1, 2, 3}
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

CLASS_TO_SUBGROUP = {
    7: 'FL_HAZ', 8: 'EN_CHSH', 9: 'FQ_CONN', 10: 'CC_DAIIN',
    11: 'CC_OL', 12: 'CC_OL_D', 13: 'FQ_PAIR', 14: 'FQ_PAIR',
    17: 'CC_OL_D', 23: 'FQ_CLOSER', 30: 'FL_HAZ', 31: 'EN_CHSH',
    32: 'EN_QO', 33: 'EN_QO', 34: 'EN_QO', 35: 'EN_QO',
    36: 'EN_QO', 37: 'EN_MINOR', 38: 'FL_SAFE', 39: 'EN_MINOR',
    40: 'FL_SAFE', 41: 'EN_QO', 42: 'EN_MINOR', 43: 'EN_MINOR',
    44: 'EN_QO', 45: 'EN_QO', 46: 'EN_QO', 47: 'EN_MINOR',
    48: 'EN_MINOR', 49: 'EN_QO'
}

CLASS_TO_ROLE = {
    1: 'AX', 2: 'AX', 3: 'AX', 4: 'AX', 5: 'AX', 6: 'AX',
    7: 'FL', 8: 'EN', 9: 'FQ', 10: 'CC', 11: 'CC', 12: 'CC',
    13: 'FQ', 14: 'FQ', 15: 'AX', 16: 'AX', 17: 'AX', 18: 'AX',
    19: 'AX', 20: 'AX', 21: 'AX', 22: 'AX', 23: 'FQ', 24: 'AX',
    25: 'AX', 26: 'AX', 27: 'AX', 28: 'AX', 29: 'AX', 30: 'FL',
    31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN', 36: 'EN',
    37: 'EN', 38: 'FL', 39: 'EN', 40: 'FL', 41: 'EN', 42: 'EN',
    43: 'EN', 44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN',
    49: 'EN'
}

EN_SUBGROUPS = {'EN_QO', 'EN_CHSH', 'EN_MINOR'}
CC_SUBGROUPS = {'CC_DAIIN', 'CC_OL', 'CC_OL_D'}

# =============================================================================
# Load data
# =============================================================================

print("Loading data...")

# Class map
class_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path, 'r', encoding='utf-8') as f:
    token_to_class = json.load(f)['token_to_class']

# Regime map
regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)

folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Script 1 results
s1_path = Path(__file__).parent.parent / 'results' / 'recovery_pathway_profiling.json'
with open(s1_path, 'r', encoding='utf-8') as f:
    s1_data = json.load(f)

# Script 2 results
s2_path = Path(__file__).parent.parent / 'results' / 'escape_strategy_decomposition.json'
with open(s2_path, 'r', encoding='utf-8') as f:
    s2_data = json.load(f)

# Transcript for raw class composition
tx = Transcript()
b_tokens = list(tx.currier_b())
print(f"  Currier B tokens: {len(b_tokens)}")

# =============================================================================
# Section 1: Folio-Level Recovery Feature Battery
# =============================================================================

print("\n=== Section 1: Folio-Level Recovery Feature Battery ===")

# Compute per-folio class composition (raw token counts by subgroup)
folio_class_comp = defaultdict(Counter)
folio_token_counts = Counter()
for t in b_tokens:
    if not t.word.strip() or '*' in t.word:
        continue
    cls = token_to_class.get(t.word)
    if cls is None:
        continue
    sg = CLASS_TO_SUBGROUP.get(cls, 'OTHER')
    role = CLASS_TO_ROLE.get(cls, 'UNK')
    folio_class_comp[t.folio][sg] += 1
    folio_class_comp[t.folio][f'role_{role}'] += 1
    folio_token_counts[t.folio] += 1

# Build feature battery for each folio
all_folios = sorted(set(folio_token_counts.keys()))
print(f"  Folios: {len(all_folios)}")

feature_battery = {}

for folio in all_folios:
    features = {}
    total = folio_token_counts[folio]

    # --- Class composition features (covariates) ---
    comp = folio_class_comp[folio]
    features['en_qo_share'] = comp.get('EN_QO', 0) / total if total > 0 else 0
    features['en_chsh_share'] = comp.get('EN_CHSH', 0) / total if total > 0 else 0
    features['en_minor_share'] = comp.get('EN_MINOR', 0) / total if total > 0 else 0
    features['cc_share'] = (comp.get('CC_DAIIN', 0) + comp.get('CC_OL', 0) + comp.get('CC_OL_D', 0)) / total if total > 0 else 0
    features['total_en_share'] = comp.get('role_EN', 0) / total if total > 0 else 0

    # --- Recovery features from Script 1 ---
    s1_kernel = s1_data['per_folio']['kernel_stats'].get(folio, {})
    features['e_rate'] = s1_kernel.get('e_rate', 0)
    features['h_rate'] = s1_kernel.get('h_rate', 0)
    features['k_rate'] = s1_kernel.get('k_rate', 0)
    features['kernel_exit_rate'] = s1_kernel.get('exit_rate', 0)

    s1_recovery = s1_data['per_folio']['recovery_paths'].get(folio, {})
    features['mean_recovery_path_length'] = s1_recovery.get('mean_path_length', 0)
    features['n_recovery_paths'] = s1_recovery.get('n_recovery_paths', 0)

    s1_post = s1_data['per_folio']['post_kernel'].get(folio, {})
    pk_roles = s1_post.get('role_fractions', {})
    features['post_kernel_en_frac'] = pk_roles.get('EN', 0)
    features['post_kernel_ax_frac'] = pk_roles.get('AX', 0)

    # --- Escape features from Script 2 ---
    s2_en = s2_data['per_folio']['en_recovery'].get(folio, {})
    en_fracs = s2_en.get('fractions', {})
    features['en_qo_recovery_frac'] = en_fracs.get('EN_QO', 0)
    features['en_chsh_recovery_frac'] = en_fracs.get('EN_CHSH', 0)

    s2_first = s2_data['per_folio']['first_en'].get(folio, {})
    first_fracs = s2_first.get('fractions', {})
    features['first_en_qo_frac'] = first_fracs.get('EN_QO', 0)

    s2_cc = s2_data['per_folio']['cc_recovery'].get(folio, {})
    cc_fracs = s2_cc.get('fractions', {})
    features['cc_daiin_recovery_frac'] = cc_fracs.get('CC_DAIIN', 0)

    feature_battery[folio] = features

# Define which features are "recovery" (DV) vs "composition" (covariates)
COVARIATE_FEATURES = ['en_qo_share', 'en_chsh_share', 'en_minor_share', 'cc_share', 'total_en_share']
RECOVERY_FEATURES = [
    'e_rate', 'h_rate', 'k_rate', 'kernel_exit_rate',
    'mean_recovery_path_length', 'n_recovery_paths',
    'post_kernel_en_frac', 'post_kernel_ax_frac',
    'en_qo_recovery_frac', 'en_chsh_recovery_frac',
    'first_en_qo_frac', 'cc_daiin_recovery_frac'
]

print(f"  Recovery features: {len(RECOVERY_FEATURES)}")
print(f"  Composition covariates: {len(COVARIATE_FEATURES)}")

# =============================================================================
# Section 2: Raw REGIME Prediction (KW Tests)
# =============================================================================

print("\n=== Section 2: Raw REGIME Prediction ===")

# Build arrays: folio order must be consistent
regime_labels = []
folio_order = []
for folio in all_folios:
    regime = folio_to_regime.get(folio)
    if regime:
        regime_labels.append(regime)
        folio_order.append(folio)

n_folios = len(folio_order)
print(f"  Folios with REGIME: {n_folios}")

# Build feature arrays
feature_arrays = {}
for feat in RECOVERY_FEATURES + COVARIATE_FEATURES:
    feature_arrays[feat] = np.array([feature_battery[f][feat] for f in folio_order])

raw_kw_results = {}
for feat in RECOVERY_FEATURES:
    values = feature_arrays[feat]
    # Group by regime
    groups = defaultdict(list)
    for i, folio in enumerate(folio_order):
        groups[regime_labels[i]].append(values[i])

    group_list = [groups[r] for r in sorted(groups.keys())]
    group_list = [g for g in group_list if len(g) >= 2]

    # Check variance: if all values identical, skip
    all_vals = np.concatenate(group_list)
    if np.std(all_vals) < 1e-10:
        raw_kw_results[feat] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False, 'note': 'zero_variance'}
        continue

    if len(group_list) >= 2:
        try:
            h_stat, p_val = kruskal(*group_list)
            n_total = sum(len(g) for g in group_list)
            eta_sq = max(0, (h_stat - len(group_list) + 1) / (n_total - len(group_list)))
            raw_kw_results[feat] = {
                'H': round(float(h_stat), 4),
                'p': round(float(p_val), 6),
                'eta_sq': round(float(eta_sq), 4),
                'significant': bool(p_val < 0.05)
            }
        except ValueError:
            raw_kw_results[feat] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}
    else:
        raw_kw_results[feat] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

print("\nRaw KW results:")
n_raw_sig = 0
for feat in RECOVERY_FEATURES:
    res = raw_kw_results[feat]
    sig = "***" if res['significant'] else ""
    if res['significant']:
        n_raw_sig += 1
    note = f" [{res.get('note', '')}]" if res.get('note') else ""
    print(f"  {feat}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}{note}")

print(f"\nRaw significant: {n_raw_sig}/{len(RECOVERY_FEATURES)}")

# =============================================================================
# Section 3: Partial Correlation (Controlling for Class Composition)
# =============================================================================

print("\n=== Section 3: Partial Correlation (Controlling for Class Composition) ===")

def compute_residuals(y, covariates):
    """Regress y on covariates via OLS, return residuals.
    All inputs are rank-transformed."""
    y_rank = rankdata(y)
    cov_ranks = np.column_stack([rankdata(c) for c in covariates])
    X_design = np.column_stack([cov_ranks, np.ones(len(y_rank))])
    beta, _, _, _ = np.linalg.lstsq(X_design, y_rank, rcond=None)
    residuals = y_rank - X_design @ beta
    return residuals

# Build covariate matrix
covariate_arrays = [feature_arrays[c] for c in COVARIATE_FEATURES]

partial_kw_results = {}
for feat in RECOVERY_FEATURES:
    values = feature_arrays[feat]

    # Check variance
    if np.std(values) < 1e-10:
        partial_kw_results[feat] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False, 'note': 'zero_variance'}
        continue

    # Compute residuals after regressing out class composition
    residuals = compute_residuals(values, covariate_arrays)

    # KW test on residuals by REGIME
    groups = defaultdict(list)
    for i, folio in enumerate(folio_order):
        groups[regime_labels[i]].append(residuals[i])

    group_list = [groups[r] for r in sorted(groups.keys())]
    group_list = [g for g in group_list if len(g) >= 2]

    if len(group_list) >= 2 and np.std(np.concatenate(group_list)) > 1e-10:
        try:
            h_stat, p_val = kruskal(*group_list)
            n_total = sum(len(g) for g in group_list)
            eta_sq = max(0, (h_stat - len(group_list) + 1) / (n_total - len(group_list)))
            partial_kw_results[feat] = {
                'H': round(float(h_stat), 4),
                'p': round(float(p_val), 6),
                'eta_sq': round(float(eta_sq), 4),
                'significant': bool(p_val < 0.05)
            }
        except ValueError:
            partial_kw_results[feat] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}
    else:
        partial_kw_results[feat] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False, 'note': 'insufficient_variance'}

print("\nPartial KW results (controlling for class composition):")
n_partial_sig = 0
for feat in RECOVERY_FEATURES:
    res = partial_kw_results[feat]
    sig = "***" if res['significant'] else ""
    if res['significant']:
        n_partial_sig += 1
    note = f" [{res.get('note', '')}]" if res.get('note') else ""
    print(f"  {feat}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}{note}")

print(f"\nPartial significant: {n_partial_sig}/{len(RECOVERY_FEATURES)}")

# =============================================================================
# Section 4: Overall Verdict
# =============================================================================

print("\n=== Section 4: Overall Verdict ===")

# Summary table
print("\nFeature-level comparison:")
print(f"  {'Feature':<35} {'Raw_p':>8} {'Partial_p':>10} {'Interpretation'}")
print(f"  {'-'*35} {'-'*8} {'-'*10} {'-'*30}")

feature_verdicts = {}
for feat in RECOVERY_FEATURES:
    raw_p = raw_kw_results[feat]['p']
    partial_p = partial_kw_results[feat]['p']

    if raw_p >= 0.05 and partial_p >= 0.05:
        interpretation = "FREE"
    elif raw_p < 0.05 and partial_p >= 0.05:
        interpretation = "CLASS-MEDIATED"
    elif raw_p < 0.05 and partial_p < 0.05:
        interpretation = "REGIME-STRATIFIED"
    elif raw_p >= 0.05 and partial_p < 0.05:
        interpretation = "SUPPRESSOR"  # Composition suppresses REGIME effect
    else:
        interpretation = "INDETERMINATE"

    feature_verdicts[feat] = interpretation
    raw_sig = "*" if raw_p < 0.05 else " "
    partial_sig = "*" if partial_p < 0.05 else " "
    print(f"  {feat:<35} {raw_p:>7.4f}{raw_sig} {partial_p:>9.4f}{partial_sig} {interpretation}")

# Count verdicts
verdict_counts = Counter(feature_verdicts.values())
print(f"\nVerdict distribution:")
for v, c in verdict_counts.most_common():
    print(f"  {v}: {c}/{len(RECOVERY_FEATURES)}")

# Overall verdict
if verdict_counts.get('REGIME-STRATIFIED', 0) >= 3:
    overall_verdict = "REGIME-STRATIFIED"
    overall_detail = (f"{verdict_counts.get('REGIME-STRATIFIED', 0)}/{len(RECOVERY_FEATURES)} features "
                      "show REGIME effects beyond class composition")
elif verdict_counts.get('CLASS-MEDIATED', 0) >= 3:
    overall_verdict = "CLASS-MEDIATED"
    overall_detail = (f"{verdict_counts.get('CLASS-MEDIATED', 0)}/{len(RECOVERY_FEATURES)} features "
                      "lose significance after controlling for composition")
elif n_raw_sig == 0:
    overall_verdict = "UNCONDITIONALLY_FREE"
    overall_detail = ("No recovery feature shows significant REGIME dependence. "
                      "Recovery architecture varies freely across folios.")
else:
    overall_verdict = "MIXED"
    overall_detail = f"Raw sig: {n_raw_sig}, Partial sig: {n_partial_sig}, no clear dominant pattern"

print(f"\n=== OVERALL VERDICT: {overall_verdict} ===")
print(f"  {overall_detail}")
print(f"  Raw significant: {n_raw_sig}/{len(RECOVERY_FEATURES)}")
print(f"  Partial significant: {n_partial_sig}/{len(RECOVERY_FEATURES)}")

# =============================================================================
# Composition covariate summary (for reference)
# =============================================================================

print("\n--- Composition covariates by REGIME (for reference) ---")
for cov in COVARIATE_FEATURES:
    groups = defaultdict(list)
    for i, folio in enumerate(folio_order):
        groups[regime_labels[i]].append(feature_arrays[cov][i])

    group_list = [groups[r] for r in sorted(groups.keys())]
    group_list_valid = [g for g in group_list if len(g) >= 2]

    if len(group_list_valid) >= 2:
        try:
            h_stat, p_val = kruskal(*group_list_valid)
        except ValueError:
            h_stat, p_val = 0, 1.0
    else:
        h_stat, p_val = 0, 1.0

    sig = "***" if p_val < 0.05 else ""
    means = []
    for r in sorted(groups.keys()):
        means.append(f"{r}={np.mean(groups[r]):.3f}")
    print(f"  {cov}: {', '.join(means)} | KW p={p_val:.4f} {sig}")

# =============================================================================
# Output JSON
# =============================================================================

output = {
    'metadata': {
        'phase': 'RECOVERY_ARCHITECTURE_DECOMPOSITION',
        'script': 'recovery_regime_interaction.py',
        'description': 'Folio-level recovery feature battery with raw and partial KW tests',
        'n_folios': n_folios,
        'n_recovery_features': len(RECOVERY_FEATURES),
        'n_covariates': len(COVARIATE_FEATURES),
        'covariate_features': COVARIATE_FEATURES,
        'recovery_features': RECOVERY_FEATURES
    },
    'raw_kw_tests': raw_kw_results,
    'partial_kw_tests': partial_kw_results,
    'feature_verdicts': feature_verdicts,
    'verdict_counts': dict(verdict_counts),
    'overall': {
        'verdict': overall_verdict,
        'detail': overall_detail,
        'n_raw_significant': n_raw_sig,
        'n_partial_significant': n_partial_sig,
        'n_features': len(RECOVERY_FEATURES)
    },
    'per_folio_features': {f: {k: round(v, 6) if isinstance(v, float) else v
                               for k, v in features.items()}
                          for f, features in feature_battery.items()
                          if f in folio_order}
}

output_path = Path(__file__).parent.parent / 'results' / 'recovery_regime_interaction.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

print(f"\nOutput: {output_path}")
print("Done.")
