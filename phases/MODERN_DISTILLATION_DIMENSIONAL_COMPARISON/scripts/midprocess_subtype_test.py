"""
Phase 435 Extension: MIDPROCESS Sub-Type Split Test
=====================================================
Tests whether splitting MIDPROCESS into Voynich-aligned sub-types
(MONITORING, ENERGY, STABILITY, CLOSURE, STRUCTURAL) increases
dimensionality from 4 PCs to 5, closing the remaining gap to Voynich.
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
MODERN_PATH = ROOT / 'phases' / 'MODERN_DISTILLATION_DIMENSIONAL_COMPARISON' / 'data' / 'modern_procedures.json'
RESULTS_DIR = ROOT / 'phases' / 'MODERN_DISTILLATION_DIMENSIONAL_COMPARISON' / 'results'
RESULTS_PATH = RESULTS_DIR / 'midprocess_subtype_test.json'

# MIDPROCESS action → Voynich-aligned sub-type
MIDPROCESS_SUBTYPE = {
    'MONITOR_TEMP': 'MID_MONITORING',
    'MONITOR_VISUAL': 'MID_MONITORING',
    'MONITOR_RATE': 'MID_MONITORING',
    'DETECT_CHANNELING': 'MID_MONITORING',
    'ADJUST_HEAT': 'MID_ENERGY',
    'COOL_CONDENSER': 'MID_STABILITY',
    'REPLENISH_WATER': 'MID_STABILITY',
    'DETECT_ENDPOINT': 'MID_CLOSURE',
    'COLLECT_FRACTION': 'MID_CLOSURE',
    'COHOBATE': 'MID_CLOSURE',
    'AGITATE': 'MID_STRUCTURAL',
    'MANAGE_PRESSURE': 'MID_STRUCTURAL',
    'SEAL_JOINTS': 'MID_STRUCTURAL',
}

# Expanded feature order: 4 non-MIDPROCESS + 5 sub-types + 2 post = 11
EXPANDED_ORDER = [
    'COLLECTION', 'PREPARATION', 'PRETREATMENT', 'DISTILLATION',
    'MID_MONITORING', 'MID_ENERGY', 'MID_STABILITY', 'MID_CLOSURE', 'MID_STRUCTURAL',
    'POSTPROCESS', 'STORAGE',
]

# Original 7-phase order for comparison
PHASE_ORDER_7 = ['COLLECTION', 'PREPARATION', 'PRETREATMENT', 'DISTILLATION',
                 'MIDPROCESS', 'POSTPROCESS', 'STORAGE']


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


def variance_entropy(explained_ratios):
    ent = 0.0
    for r in explained_ratios:
        if r > 0:
            ent -= r * math.log2(r)
    return ent


def n_for_threshold(explained_ratios, threshold=0.80):
    cum = 0.0
    for i, r in enumerate(explained_ratios):
        cum += r
        if cum >= threshold:
            return i + 1
    return len(explained_ratios)


def build_expanded_matrix(procedures):
    """Build recipe x expanded_feature matrix, splitting MIDPROCESS by sub-type."""
    rows = []
    for proc in procedures:
        counts = Counter()
        total = 0
        for step in proc['steps']:
            phase = step['phase']
            action = step['action']
            if phase == 'MIDPROCESS':
                subtype = MIDPROCESS_SUBTYPE.get(action, 'MID_STRUCTURAL')
                counts[subtype] += 1
            else:
                counts[phase] += 1
            total += 1
        if total > 0:
            row = [counts.get(f, 0) / total for f in EXPANDED_ORDER]
            rows.append(row)
    return np.array(rows)


def build_7phase_matrix(procedures):
    """Build recipe x 7-phase matrix (original, for comparison)."""
    rows = []
    for proc in procedures:
        counts = Counter()
        total = 0
        for step in proc['steps']:
            counts[step['phase']] += 1
            total += 1
        if total > 0:
            row = [counts.get(p, 0) / total for p in PHASE_ORDER_7]
            rows.append(row)
    return np.array(rows)


def run_pca_generic(matrix, feature_names, label):
    """Run PCA and return summary."""
    n_samples, n_features = matrix.shape
    n_components = min(n_samples, n_features)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    pca = PCA(n_components=n_components)
    pca.fit(scaled)

    explained = pca.explained_variance_ratio_
    n80 = n_for_threshold(explained, 0.80)
    n90 = n_for_threshold(explained, 0.90)
    entropy = variance_entropy(explained)

    phase_variances = np.var(matrix, axis=0)
    active_dims = int(np.sum(phase_variances > 1e-10))

    return {
        'label': label,
        'n_recipes': n_samples,
        'n_features': n_features,
        'active_dimensions': active_dims,
        'n_for_80': n80,
        'n_for_90': n90,
        'entropy': round(entropy, 3),
        'explained_variance': [round(float(v), 4) for v in explained],
        'cumulative_variance': [round(float(v), 4) for v in np.cumsum(explained)],
        'pc_loadings': {
            f'PC{i+1}': {feature_names[j]: round(float(pca.components_[i][j]), 3)
                         for j in range(n_features)}
            for i in range(min(n80 + 2, len(pca.components_)))
        },
        'feature_means': {feature_names[j]: round(float(np.mean(matrix[:, j])), 4)
                          for j in range(n_features)},
        'feature_stds': {feature_names[j]: round(float(np.std(matrix[:, j])), 4)
                         for j in range(n_features)},
    }


# =====================================================================
# LOAD & BUILD
# =====================================================================
print("MIDPROCESS SUB-TYPE SPLIT TEST")
print("=" * 70)

with open(MODERN_PATH) as f:
    modern_data = json.load(f)
procs = modern_data['procedures']
print(f"Modern procedures: {len(procs)}")

# Build both matrices
matrix_7 = build_7phase_matrix(procs)
matrix_11 = build_expanded_matrix(procs)

print(f"\n7-phase matrix:    {matrix_7.shape}")
print(f"11-feature matrix: {matrix_11.shape}")

# =====================================================================
# SUB-TYPE DISTRIBUTION
# =====================================================================
print(f"\n{'=' * 70}")
print("MIDPROCESS SUB-TYPE DISTRIBUTION")
print(f"{'=' * 70}")

print(f"\n  {'Feature':<18} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
print(f"  {'-------':<18} {'----':>8} {'---':>8} {'---':>8} {'---':>8}")
for j, feat in enumerate(EXPANDED_ORDER):
    col = matrix_11[:, j]
    print(f"  {feat:<18} {np.mean(col):>7.1%} {np.std(col):>7.1%} {np.min(col):>7.1%} {np.max(col):>7.1%}")

# =====================================================================
# PCA COMPARISON: 7-phase vs 11-feature
# =====================================================================
print(f"\n{'=' * 70}")
print("PCA COMPARISON: 7-PHASE vs 11-FEATURE (MIDPROCESS SPLIT)")
print(f"{'=' * 70}")

pca_7 = run_pca_generic(matrix_7, PHASE_ORDER_7, 'Modern (7-phase)')
pca_11 = run_pca_generic(matrix_11, EXPANDED_ORDER, 'Modern (11-feature)')

voynich_ref = {
    'n_for_80': 5,
    'n_for_90': 6,
    'entropy': 2.660,
    'active_dimensions': 10,
}

print(f"\n  {'Metric':<25} {'7-phase':>12} {'11-feature':>12} {'Voynich':>12}")
print(f"  {'------':<25} {'-------':>12} {'----------':>12} {'-------':>12}")
print(f"  {'Features':<25} {pca_7['n_features']:>12} {pca_11['n_features']:>12} {'10':>12}")
print(f"  {'Active dimensions':<25} {pca_7['active_dimensions']:>12} {pca_11['active_dimensions']:>12} {voynich_ref['active_dimensions']:>12}")
print(f"  {'n_for_80%':<25} {pca_7['n_for_80']:>12} {pca_11['n_for_80']:>12} {voynich_ref['n_for_80']:>12}")
print(f"  {'n_for_90%':<25} {pca_7['n_for_90']:>12} {pca_11['n_for_90']:>12} {voynich_ref['n_for_90']:>12}")
print(f"  {'Entropy (bits)':<25} {pca_7['entropy']:>12.3f} {pca_11['entropy']:>12.3f} {voynich_ref['entropy']:>12.3f}")

# Entropy distances
dist_7 = abs(pca_7['entropy'] - voynich_ref['entropy'])
dist_11 = abs(pca_11['entropy'] - voynich_ref['entropy'])
print(f"\n  Entropy distance from Voynich:")
print(f"    7-phase:    |{pca_7['entropy']:.3f} - 2.660| = {dist_7:.3f}")
print(f"    11-feature: |{pca_11['entropy']:.3f} - 2.660| = {dist_11:.3f}")
if dist_11 < dist_7:
    print(f"    --> 11-feature is {dist_7/dist_11:.1f}x closer to Voynich")
elif dist_11 > dist_7:
    print(f"    --> 7-phase is closer (sub-type split did NOT help)")
else:
    print(f"    --> No change")

# =====================================================================
# PC LOADINGS: 11-FEATURE
# =====================================================================
print(f"\n{'=' * 70}")
print("PC LOADINGS: 11-FEATURE MODEL")
print(f"{'=' * 70}")

for pc_name, loadings in pca_11['pc_loadings'].items():
    pc_idx = int(pc_name[2:]) - 1
    var_pct = pca_11['explained_variance'][pc_idx] * 100
    print(f"\n  {pc_name} ({var_pct:.1f}% variance):")
    sorted_loads = sorted(loadings.items(), key=lambda x: -abs(x[1]))
    for feat, load in sorted_loads:
        bar = '+' * int(abs(load) * 20) if load > 0 else '-' * int(abs(load) * 20)
        print(f"    {feat:<18} {load:>+7.3f}  {bar}")

# =====================================================================
# VARIANCE EXPLAINED COMPARISON
# =====================================================================
print(f"\n{'=' * 70}")
print("VARIANCE EXPLAINED PER PC")
print(f"{'=' * 70}")

max_pcs = max(len(pca_7['explained_variance']), len(pca_11['explained_variance']))
print(f"\n  {'PC':<6} {'7-phase':>12} {'Cum':>8} {'11-feature':>12} {'Cum':>8}")
print(f"  {'--':<6} {'-------':>12} {'---':>8} {'----------':>12} {'---':>8}")
for i in range(min(max_pcs, 8)):
    v7 = pca_7['explained_variance'][i] if i < len(pca_7['explained_variance']) else 0
    c7 = pca_7['cumulative_variance'][i] if i < len(pca_7['cumulative_variance']) else 0
    v11 = pca_11['explained_variance'][i] if i < len(pca_11['explained_variance']) else 0
    c11 = pca_11['cumulative_variance'][i] if i < len(pca_11['cumulative_variance']) else 0
    marker_7 = ' <80%' if c7 >= 0.80 and (i == 0 or pca_7['cumulative_variance'][i-1] < 0.80) else ''
    marker_11 = ' <80%' if c11 >= 0.80 and (i == 0 or pca_11['cumulative_variance'][i-1] < 0.80) else ''
    print(f"  PC{i+1:<3} {v7:>11.1%} {c7:>7.1%}{marker_7:>6} {v11:>11.1%} {c11:>7.1%}{marker_11:>6}")

# =====================================================================
# VERDICT
# =====================================================================
print(f"\n{'=' * 70}")
print("VERDICT")
print(f"{'=' * 70}")

if pca_11['n_for_80'] > pca_7['n_for_80']:
    print(f"\n  CONFIRMED: Splitting MIDPROCESS into sub-types increases n_for_80%")
    print(f"    7-phase:    {pca_7['n_for_80']} PCs")
    print(f"    11-feature: {pca_11['n_for_80']} PCs")
    print(f"    Voynich:    {voynich_ref['n_for_80']} PCs")
    if pca_11['n_for_80'] == voynich_ref['n_for_80']:
        print(f"\n  MATCH: 11-feature modern distillation matches Voynich dimensionality exactly!")
        print(f"  The remaining gap was material-specific MIDPROCESS parameterization.")
elif pca_11['n_for_80'] == pca_7['n_for_80']:
    print(f"\n  NO CHANGE: Sub-type split did not increase n_for_80% (still {pca_7['n_for_80']} PCs)")
    print(f"  The remaining gap is NOT explained by MIDPROCESS sub-type differentiation.")
else:
    print(f"\n  UNEXPECTED: n_for_80% decreased ({pca_7['n_for_80']} -> {pca_11['n_for_80']})")

# =====================================================================
# SAVE
# =====================================================================
results = {
    'pca_7phase': pca_7,
    'pca_11feature': pca_11,
    'voynich_reference': voynich_ref,
    'midprocess_subtype_map': MIDPROCESS_SUBTYPE,
    'expanded_features': EXPANDED_ORDER,
    'comparison': {
        'n_for_80_7phase': pca_7['n_for_80'],
        'n_for_80_11feature': pca_11['n_for_80'],
        'n_for_80_voynich': voynich_ref['n_for_80'],
        'entropy_7phase': pca_7['entropy'],
        'entropy_11feature': pca_11['entropy'],
        'entropy_voynich': voynich_ref['entropy'],
        'entropy_distance_7phase': round(dist_7, 3),
        'entropy_distance_11feature': round(dist_11, 3),
        'split_increased_dimensionality': bool(pca_11['n_for_80'] > pca_7['n_for_80']),
        'matches_voynich': bool(pca_11['n_for_80'] == voynich_ref['n_for_80']),
    }
}

with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_PATH}")
