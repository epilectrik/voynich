"""
Phase 435: Modern Distillation Dimensional Comparison
=====================================================
Tests whether modern distillation, formalized into the same 7-phase framework
as Brunschwig, has dimensionality closer to Voynich (5 PCs) than Brunschwig (3 PCs).

The critical prediction: modern procedures explicitly encode MIDPROCESS actions
(temperature monitoring, channeling detection, endpoint detection) that Brunschwig
leaves as tacit operator knowledge. This should produce higher PCA dimensionality.
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

CURATED_V3_PATH = ROOT / 'data' / 'brunschwig_curated_v3.json'
MODERN_PATH = ROOT / 'phases' / 'MODERN_DISTILLATION_DIMENSIONAL_COMPARISON' / 'data' / 'modern_procedures.json'
RESULTS_DIR = ROOT / 'phases' / 'MODERN_DISTILLATION_DIMENSIONAL_COMPARISON' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = RESULTS_DIR / 'dimensional_comparison.json'

PHASE_ORDER = ['COLLECTION', 'PREPARATION', 'PRETREATMENT', 'DISTILLATION',
               'MIDPROCESS', 'POSTPROCESS', 'STORAGE']

# Action-to-phase for Brunschwig (from BRSC)
BRUN_ACTION_TO_PHASE = {
    'GATHER': 'COLLECTION', 'SELECT': 'COLLECTION',
    'CHOP': 'PREPARATION', 'STRIP': 'PREPARATION', 'POUND': 'PREPARATION',
    'CRUSH': 'PREPARATION', 'BREAK': 'PREPARATION', 'PLUCK': 'PREPARATION',
    'BORE': 'PREPARATION', 'WASH': 'PREPARATION', 'KILL': 'PREPARATION',
    'CLEAN': 'PREPARATION', 'POWDER': 'PREPARATION', 'GRIND': 'PREPARATION',
    'MACERATE': 'PRETREATMENT', 'DRY': 'PRETREATMENT', 'FERMENT': 'PRETREATMENT',
    'DIGEST': 'PRETREATMENT', 'MIX': 'PRETREATMENT',
    'DISTILL': 'DISTILLATION', 'REDISTILL': 'DISTILLATION',
    'SEAL': 'MIDPROCESS', 'REGULATE': 'MIDPROCESS', 'MONITOR_DRIPS': 'MIDPROCESS',
    'MONITOR_TEMP': 'MIDPROCESS', 'REPLENISH': 'MIDPROCESS', 'COOL': 'MIDPROCESS',
    'STRAIN': 'POSTPROCESS', 'FILTER': 'POSTPROCESS', 'RECTIFY': 'POSTPROCESS',
    'SETTLE': 'POSTPROCESS', 'POUR': 'POSTPROCESS', 'COLLECT': 'POSTPROCESS',
    'MELT': 'POSTPROCESS',
    'SEAL_VESSEL': 'STORAGE', 'LABEL': 'STORAGE', 'STORE': 'STORAGE',
    'RENEW': 'STORAGE', 'STEEP': 'PRETREATMENT',
}


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
    """Shannon entropy of PCA variance distribution."""
    ent = 0.0
    for r in explained_ratios:
        if r > 0:
            ent -= r * math.log2(r)
    return ent


def n_for_threshold(explained_ratios, threshold=0.80):
    """Number of PCs needed to explain threshold of variance."""
    cum = 0.0
    for i, r in enumerate(explained_ratios):
        cum += r
        if cum >= threshold:
            return i + 1
    return len(explained_ratios)


def build_phase_matrix(recipes, action_map, phase_order):
    """Build recipe x phase_proportion matrix."""
    rows = []
    for recipe in recipes:
        phase_counts = Counter()
        total_steps = 0
        for step in recipe.get('procedural_steps', recipe.get('steps', [])):
            action = step.get('action', '')
            phase = step.get('phase', action_map.get(action, None))
            if phase and phase in phase_order:
                phase_counts[phase] += 1
                total_steps += 1
        if total_steps > 0:
            row = [phase_counts.get(p, 0) / total_steps for p in phase_order]
            rows.append(row)
    return np.array(rows)


def run_pca(matrix, label):
    """Run PCA on phase matrix and return summary dict."""
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

    # Active dimensions (phases with non-zero variance)
    phase_variances = np.var(matrix, axis=0)
    active_dims = int(np.sum(phase_variances > 1e-10))

    # MIDPROCESS loading analysis
    midprocess_idx = PHASE_ORDER.index('MIDPROCESS')
    midprocess_max_loading = 0.0
    midprocess_max_pc = -1
    for i in range(min(n80 + 1, len(pca.components_))):
        loading = abs(pca.components_[i][midprocess_idx])
        if loading > midprocess_max_loading:
            midprocess_max_loading = loading
            midprocess_max_pc = i + 1

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
            f'PC{i+1}': {PHASE_ORDER[j]: round(float(pca.components_[i][j]), 3)
                         for j in range(n_features)}
            for i in range(min(n80 + 2, len(pca.components_)))
        },
        'midprocess_stats': {
            'phase_mean': round(float(np.mean(matrix[:, midprocess_idx])), 4),
            'phase_std': round(float(np.std(matrix[:, midprocess_idx])), 4),
            'phase_max': round(float(np.max(matrix[:, midprocess_idx])), 4),
            'phase_min': round(float(np.min(matrix[:, midprocess_idx])), 4),
            'max_pc_loading': round(float(midprocess_max_loading), 3),
            'max_pc_loading_on': f'PC{midprocess_max_pc}' if midprocess_max_pc > 0 else 'none',
        },
        'phase_means': {PHASE_ORDER[j]: round(float(np.mean(matrix[:, j])), 4)
                        for j in range(n_features)},
    }


# =====================================================================
# LOAD DATA
# =====================================================================
print("MODERN DISTILLATION DIMENSIONAL COMPARISON")
print("=" * 70)

# Brunschwig
with open(CURATED_V3_PATH, encoding='utf-8') as f:
    brun_data = json.load(f)

brun_recipes = [r for r in brun_data['recipes'] if r.get('has_procedure', False)]
print(f"Brunschwig recipes with procedures: {len(brun_recipes)}")

# Modern
with open(MODERN_PATH) as f:
    modern_data = json.load(f)

modern_procs = modern_data['procedures']
print(f"Modern procedures: {len(modern_procs)}")

# =====================================================================
# BUILD PHASE MATRICES
# =====================================================================
print(f"\n{'=' * 70}")
print("PHASE PROPORTION ANALYSIS")
print(f"{'=' * 70}")

brun_matrix = build_phase_matrix(brun_recipes, BRUN_ACTION_TO_PHASE, PHASE_ORDER)
modern_matrix = build_phase_matrix(modern_procs, {}, PHASE_ORDER)  # phases already in data

print(f"\nBrunschwig matrix: {brun_matrix.shape}")
print(f"Modern matrix:     {modern_matrix.shape}")

# Phase mean proportions
print(f"\n{'Phase':<15} {'Brunschwig':>12} {'Modern':>12} {'Delta':>10}")
print(f"{'-----':<15} {'----------':>12} {'------':>12} {'-----':>10}")
for j, phase in enumerate(PHASE_ORDER):
    bm = np.mean(brun_matrix[:, j])
    mm = np.mean(modern_matrix[:, j])
    delta = mm - bm
    print(f"{phase:<15} {bm:>11.1%} {mm:>11.1%} {delta:>+9.1%}")

# =====================================================================
# PCA COMPARISON
# =====================================================================
print(f"\n{'=' * 70}")
print("PCA COMPARISON")
print(f"{'=' * 70}")

brun_pca = run_pca(brun_matrix, 'Brunschwig')
modern_pca = run_pca(modern_matrix, 'Modern')

# Voynich reference (from F-BRU-030)
voynich_ref = {
    'n_for_80': 5,
    'n_for_90': 6,
    'entropy': 2.660,
    'active_dimensions': 10,
}

print(f"\n{'Metric':<25} {'Brunschwig':>12} {'Modern':>12} {'Voynich':>12}")
print(f"{'------':<25} {'----------':>12} {'------':>12} {'-------':>12}")
print(f"{'Recipes/Folios':<25} {brun_pca['n_recipes']:>12} {modern_pca['n_recipes']:>12} {'69':>12}")
print(f"{'Active dimensions':<25} {brun_pca['active_dimensions']:>12} {modern_pca['active_dimensions']:>12} {voynich_ref['active_dimensions']:>12}")
print(f"{'n_for_80%':<25} {brun_pca['n_for_80']:>12} {modern_pca['n_for_80']:>12} {voynich_ref['n_for_80']:>12}")
print(f"{'n_for_90%':<25} {brun_pca['n_for_90']:>12} {modern_pca['n_for_90']:>12} {voynich_ref['n_for_90']:>12}")
print(f"{'Entropy (bits)':<25} {brun_pca['entropy']:>12.3f} {modern_pca['entropy']:>12.3f} {voynich_ref['entropy']:>12.3f}")
print(f"{'MIDPROCESS mean':<25} {brun_pca['midprocess_stats']['phase_mean']:>11.1%} {modern_pca['midprocess_stats']['phase_mean']:>11.1%} {'(present)':>12}")
print(f"{'MIDPROCESS max loading':<25} {brun_pca['midprocess_stats']['max_pc_loading']:>12.3f} {modern_pca['midprocess_stats']['max_pc_loading']:>12.3f} {'(present)':>12}")

# =====================================================================
# PC LOADINGS DETAIL
# =====================================================================
print(f"\n{'=' * 70}")
print("PC LOADINGS: BRUNSCHWIG")
print(f"{'=' * 70}")
for pc_name, loadings in brun_pca['pc_loadings'].items():
    var_pct = brun_pca['explained_variance'][int(pc_name[2:])-1] * 100
    print(f"\n  {pc_name} ({var_pct:.1f}% variance):")
    sorted_loads = sorted(loadings.items(), key=lambda x: -abs(x[1]))
    for phase, load in sorted_loads:
        bar = '+' * int(abs(load) * 20) if load > 0 else '-' * int(abs(load) * 20)
        print(f"    {phase:<15} {load:>+7.3f}  {bar}")

print(f"\n{'=' * 70}")
print("PC LOADINGS: MODERN DISTILLATION")
print(f"{'=' * 70}")
for pc_name, loadings in modern_pca['pc_loadings'].items():
    var_pct = modern_pca['explained_variance'][int(pc_name[2:])-1] * 100
    print(f"\n  {pc_name} ({var_pct:.1f}% variance):")
    sorted_loads = sorted(loadings.items(), key=lambda x: -abs(x[1]))
    for phase, load in sorted_loads:
        bar = '+' * int(abs(load) * 20) if load > 0 else '-' * int(abs(load) * 20)
        print(f"    {phase:<15} {load:>+7.3f}  {bar}")

# =====================================================================
# MIDPROCESS ENRICHMENT DETAIL
# =====================================================================
print(f"\n{'=' * 70}")
print("MIDPROCESS ENRICHMENT DETAIL")
print(f"{'=' * 70}")

# Per-recipe MIDPROCESS fraction
brun_mid = brun_matrix[:, PHASE_ORDER.index('MIDPROCESS')]
modern_mid = modern_matrix[:, PHASE_ORDER.index('MIDPROCESS')]

print(f"\n  Brunschwig MIDPROCESS fractions:")
print(f"    Mean: {np.mean(brun_mid):.3f}  Std: {np.std(brun_mid):.3f}")
print(f"    Zero-MIDPROCESS recipes: {np.sum(brun_mid == 0)}/{len(brun_mid)} ({np.mean(brun_mid == 0):.1%})")
print(f"    Non-zero recipes: {np.sum(brun_mid > 0)}/{len(brun_mid)}")

print(f"\n  Modern MIDPROCESS fractions:")
print(f"    Mean: {np.mean(modern_mid):.3f}  Std: {np.std(modern_mid):.3f}")
print(f"    Zero-MIDPROCESS procedures: {np.sum(modern_mid == 0)}/{len(modern_mid)} ({np.mean(modern_mid == 0):.1%})")
print(f"    Non-zero procedures: {np.sum(modern_mid > 0)}/{len(modern_mid)}")

# Per-procedure detail
print(f"\n  Per-procedure MIDPROCESS step count:")
for proc in modern_procs:
    mid_count = sum(1 for s in proc['steps'] if s.get('phase') == 'MIDPROCESS')
    total = len(proc['steps'])
    print(f"    {proc['id']:>2}. {proc['material']:<15} ({proc['method']:<25}) "
          f"MIDPROCESS: {mid_count}/{total} ({mid_count/total:.0%})")

# =====================================================================
# DISTANCE FROM VOYNICH
# =====================================================================
print(f"\n{'=' * 70}")
print("DISTANCE FROM VOYNICH")
print(f"{'=' * 70}")

brun_dist = abs(brun_pca['entropy'] - voynich_ref['entropy'])
modern_dist = abs(modern_pca['entropy'] - voynich_ref['entropy'])
brun_pc_dist = abs(brun_pca['n_for_80'] - voynich_ref['n_for_80'])
modern_pc_dist = abs(modern_pca['n_for_80'] - voynich_ref['n_for_80'])

print(f"\n  Entropy distance from Voynich (2.660 bits):")
print(f"    Brunschwig: |{brun_pca['entropy']:.3f} - 2.660| = {brun_dist:.3f}")
print(f"    Modern:     |{modern_pca['entropy']:.3f} - 2.660| = {modern_dist:.3f}")
if modern_dist < brun_dist:
    print(f"    --> Modern is {brun_dist/modern_dist:.1f}x closer to Voynich")
else:
    print(f"    --> Brunschwig is closer to Voynich")

print(f"\n  PC count distance from Voynich (5 PCs):")
print(f"    Brunschwig: |{brun_pca['n_for_80']} - 5| = {brun_pc_dist}")
print(f"    Modern:     |{modern_pca['n_for_80']} - 5| = {modern_pc_dist}")

# =====================================================================
# SAVE RESULTS
# =====================================================================
results = {
    'brunschwig': brun_pca,
    'modern': modern_pca,
    'voynich_reference': voynich_ref,
    'comparison': {
        'entropy_distance_brunschwig': brun_dist,
        'entropy_distance_modern': modern_dist,
        'modern_closer': modern_dist < brun_dist,
        'n_for_80_brunschwig': brun_pca['n_for_80'],
        'n_for_80_modern': modern_pca['n_for_80'],
        'n_for_80_voynich': voynich_ref['n_for_80'],
        'midprocess_mean_brunschwig': brun_pca['midprocess_stats']['phase_mean'],
        'midprocess_mean_modern': modern_pca['midprocess_stats']['phase_mean'],
    }
}

with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\n{'=' * 70}")
print(f"Results saved to {RESULTS_PATH}")
print(f"{'=' * 70}")
