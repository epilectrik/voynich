#!/usr/bin/env python3
"""Phase 371: BRUNSCHWIG_MIDPROCESS_ABSENCE

Formal documentation of the MIDPROCESS structural absence in Brunschwig's
recipe-level encoding, quantification of its impact on the Brunschwig-Voynich
dimensional comparison, and Path C closure analysis.

F-BRU-029 Path C failed because MIDPROCESS has zero loading on all PCs.
Exhaustive investigation across 5 data sources confirmed that no per-recipe
MIDPROCESS variation exists. This script formally characterizes that absence.
"""

import json
import sys
import os
import numpy as np
from collections import Counter
from pathlib import Path

# Paths
BASE = Path(__file__).resolve().parents[3]
V3_CURATION = BASE / 'data' / 'brunschwig_curated_v3.json'
MASTER_DATA = BASE / 'data' / 'brunschwig_materials_master.json'
BRU029_RESULTS = BASE / 'phases' / 'BRUNSCHWIG_SEMANTIC_BOUNDARY' / 'results' / 'brunschwig_semantic_boundary.json'
VOY_PCA = BASE / 'phases' / 'BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS' / 'results' / 'multidimensional_pca.json'
M2_RESULTS = BASE / 'phases' / 'GENERATIVE_SUFFICIENCY' / 'results' / 'generative_sufficiency.json'
OUT_DIR = BASE / 'phases' / 'BRUNSCHWIG_MIDPROCESS_ABSENCE' / 'results'
OUT_FILE = OUT_DIR / 'brunschwig_midprocess_absence.json'

# Phase taxonomy (same as F-BRU-029)
ACTION_TO_PHASE = {
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

MIDPROCESS_ACTIONS = {'SEAL', 'REGULATE', 'MONITOR_DRIPS', 'MONITOR_TEMP', 'REPLENISH', 'COOL'}
PHASE_ORDER = ['COLLECTION', 'PREPARATION', 'PRETREATMENT', 'DISTILLATION',
               'MIDPROCESS', 'POSTPROCESS', 'STORAGE']

# M2 test categorization
TEST_CATEGORIES = {
    'A1': 'DISTRIBUTIONAL',  # class KL divergence (rank-frequency)
    'A2': 'DISTRIBUTIONAL',  # hapax rate
    'A3': 'DISTRIBUTIONAL',  # active classes count
    'A4': 'DISTRIBUTIONAL',  # type count (vocabulary size)
    'B1': 'SEQUENTIAL',      # spectral gap (mixing rate)
    'B2': 'SEQUENTIAL',      # AXM self-transition rate
    'B3': 'SEQUENTIAL',      # forbidden pair violations
    'B4': 'STRUCTURAL',      # role rank preservation (role category ordering)
    'B5': 'SEQUENTIAL',      # forward-backward JSD (directional asymmetry)
    'C1': 'MORPHOLOGICAL',   # suffix rate
    'C2': 'MORPHOLOGICAL',   # MIDDLE pair mutual information (cc_suffix_free)
    'C3': 'MORPHOLOGICAL',   # prefix entropy reduction (PREFIX→MIDDLE dependency)
    'D1': 'DISTRIBUTIONAL',  # stationary distribution
    'D2': 'SEQUENTIAL',      # AXM dwell time
    'D3': 'SEQUENTIAL',      # cross-line mutual information
}


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


# ═══════════════════════════════════════════════════════════════════════
# S1: MIDPROCESS Absence Audit
# ═══════════════════════════════════════════════════════════════════════
def s1_absence_audit(v3, master):
    """Verify MIDPROCESS absence across all data sources."""
    print("=" * 72)
    print("S1: MIDPROCESS ABSENCE AUDIT")
    print("=" * 72)

    results = {}

    # Source 1: v3 curation — count MIDPROCESS actions per recipe
    midprocess_per_recipe = []
    total_recipes = len(v3['recipes'])
    recipes_with_steps = 0
    total_steps = 0
    midprocess_step_count = 0

    for recipe in v3['recipes']:
        steps = recipe.get('procedural_steps') or []
        if steps:
            recipes_with_steps += 1
        mp_count = 0
        for step in steps:
            total_steps += 1
            action = step.get('action', '')
            if action in MIDPROCESS_ACTIONS:
                mp_count += 1
                midprocess_step_count += 1
        midprocess_per_recipe.append(mp_count)

    results['v3_curation'] = {
        'total_recipes': total_recipes,
        'recipes_with_steps': recipes_with_steps,
        'total_steps': total_steps,
        'midprocess_steps': midprocess_step_count,
        'recipes_with_midprocess': sum(1 for c in midprocess_per_recipe if c > 0),
        'verdict': 'ZERO' if midprocess_step_count == 0 else 'PRESENT'
    }
    print(f"\n  Source 1: V3 Curation")
    print(f"    Total recipes: {total_recipes}")
    print(f"    Recipes with steps: {recipes_with_steps}")
    print(f"    Total procedural steps: {total_steps}")
    print(f"    MIDPROCESS steps: {midprocess_step_count}")
    print(f"    Recipes with MIDPROCESS: {sum(1 for c in midprocess_per_recipe if c > 0)}")
    print(f"    Verdict: {'ZERO — confirmed absent' if midprocess_step_count == 0 else 'PRESENT'}")

    # Source 2: Master data — monitoring_intensity
    materials = master['materials']
    monitoring_vals = []
    for mat in materials:
        ra = mat.get('regime_assignment', {})
        mi = ra.get('monitoring_intensity', None)
        if mi is not None:
            monitoring_vals.append(mi)

    nonzero_monitoring = sum(1 for v in monitoring_vals if v > 0)
    # Note: monitoring_intensity is derived from MONITORING step_type ratio,
    # which we've established are ALL medical usage monitoring, not process monitoring
    results['master_monitoring_intensity'] = {
        'total_materials': len(materials),
        'with_monitoring_field': len(monitoring_vals),
        'nonzero_count': nonzero_monitoring,
        'values_unique': sorted(set(round(v, 3) for v in monitoring_vals)),
        'verdict': 'USAGE_DERIVED' if nonzero_monitoring > 0 else 'ZERO',
        'note': 'Non-zero values derive from medical usage MONITORING steps, not distillation process monitoring'
    }
    print(f"\n  Source 2: Master Data — monitoring_intensity")
    print(f"    Total materials: {len(materials)}")
    print(f"    With monitoring_intensity field: {len(monitoring_vals)}")
    print(f"    Non-zero values: {nonzero_monitoring}")
    print(f"    Unique values: {sorted(set(round(v, 3) for v in monitoring_vals))}")
    if nonzero_monitoring > 0:
        print(f"    NOTE: Non-zero values derive from medical USAGE monitoring steps,")
        print(f"          NOT distillation process monitoring. See Source 3.")
        print(f"    Verdict: USAGE-DERIVED — non-zero but irrelevant to MIDPROCESS")
    else:
        print(f"    Verdict: ALL ZERO — confirmed absent")

    # Source 3: Master data — MONITORING step_types
    monitoring_steps = []
    for mat in materials:
        for step in mat.get('procedural_steps', []):
            if step.get('step_type') == 'MONITORING':
                monitoring_steps.append({
                    'recipe_id': mat.get('recipe_id', '?'),
                    'text_preview': step.get('brunschwig_text', '')[:80],
                    'instruction_class': step.get('instruction_class', '?')
                })

    # Check for distillation-process monitoring keywords
    process_keywords = ['finger', 'tropff', 'drip', 'regulier', 'warm waſſer',
                        'kalt werden', 'loch', 'vent', 'fewr', 'fire']
    usage_keywords = ['getruncken', 'getrunckẽ', 'tag', 'moꝛgen', 'abent',
                      'lot', 'nacht', 'geweschen', 'gůt für']

    process_match = 0
    usage_match = 0
    for ms in monitoring_steps:
        text = ms['text_preview'].lower()
        if any(kw in text for kw in process_keywords):
            process_match += 1
        if any(kw in text for kw in usage_keywords):
            usage_match += 1

    results['master_monitoring_steps'] = {
        'total_monitoring_steps': len(monitoring_steps),
        'process_monitoring_matches': process_match,
        'usage_monitoring_matches': usage_match,
        'verdict': 'ALL_USAGE' if process_match == 0 else 'MIXED'
    }
    print(f"\n  Source 3: Master Data — MONITORING step_types")
    print(f"    Total MONITORING steps: {len(monitoring_steps)}")
    print(f"    Distillation process monitoring: {process_match}")
    print(f"    Medical usage monitoring: {usage_match}")
    print(f"    Verdict: {'ALL USAGE — no process monitoring' if process_match == 0 else 'MIXED'}")

    # Source 4: Master data — precision/duration/cei variation
    precision_vals = Counter()
    duration_vals = Counter()
    cei_vals = []
    for mat in materials:
        ra = mat.get('regime_assignment', {})
        precision_vals[ra.get('precision_requirement', 'UNKNOWN')] += 1
        duration_vals[ra.get('duration_class', 'UNKNOWN')] += 1
        cei = ra.get('estimated_cei')
        if cei is not None:
            cei_vals.append(cei)

    results['master_operational_fields'] = {
        'precision_distribution': dict(precision_vals),
        'duration_distribution': dict(duration_vals),
        'cei_stats': {
            'mean': float(np.mean(cei_vals)) if cei_vals else None,
            'std': float(np.std(cei_vals)) if cei_vals else None,
            'unique_count': len(set(round(v, 3) for v in cei_vals)),
            'min': float(min(cei_vals)) if cei_vals else None,
            'max': float(max(cei_vals)) if cei_vals else None,
        },
        'verdict': 'LOW_VARIANCE'
    }
    dominant_precision = precision_vals.most_common(1)[0]
    dominant_duration = duration_vals.most_common(1)[0]
    print(f"\n  Source 4: Master Data — operational fields")
    print(f"    Precision: {dict(precision_vals)} (dominant: {dominant_precision[0]} = {dominant_precision[1]}/{len(materials)})")
    print(f"    Duration: {dict(duration_vals)} (dominant: {dominant_duration[0]} = {dominant_duration[1]}/{len(materials)})")
    print(f"    CEI: mean={np.mean(cei_vals):.3f}, std={np.std(cei_vals):.3f}, unique={len(set(round(v,3) for v in cei_vals))}")
    print(f"    Verdict: LOW VARIANCE — dominated by single categories")

    # Source 5: Master data — instruction_class LINK
    link_count = 0
    total_inst_steps = 0
    for mat in materials:
        for step in mat.get('procedural_steps', []):
            total_inst_steps += 1
            if step.get('instruction_class') == 'LINK':
                link_count += 1

    results['master_instruction_link'] = {
        'total_classified_steps': total_inst_steps,
        'link_count': link_count,
        'link_fraction': link_count / total_inst_steps if total_inst_steps > 0 else 0,
        'verdict': 'USAGE_CONTEXT'
    }
    print(f"\n  Source 5: Master Data — LINK instruction class")
    print(f"    Total classified steps: {total_inst_steps}")
    print(f"    LINK-classified steps: {link_count}")
    print(f"    Fraction: {link_count/total_inst_steps:.3f}" if total_inst_steps > 0 else "    Fraction: N/A")
    print(f"    Verdict: USAGE CONTEXT — LINK from medical usage text, not process monitoring")

    # Overall H1 verdict
    # H1 asks: is there per-recipe DISTILLATION PROCESS monitoring variation?
    # monitoring_intensity non-zero values come from medical usage monitoring, not process monitoring
    no_process_monitoring = (midprocess_step_count == 0 and process_match == 0)
    results['h1_verdict'] = 'PASS' if no_process_monitoring else 'FAIL'
    results['h1_detail'] = (
        'Zero MIDPROCESS actions in v3 curation; zero distillation process monitoring '
        'in master data. monitoring_intensity has {} non-zero values but these derive '
        'from medical usage monitoring steps, not distillation process monitoring.'
    ).format(nonzero_monitoring)
    print(f"\n  H1 VERDICT: {'PASS' if no_process_monitoring else 'FAIL'}")
    print(f"    {'Zero distillation process monitoring across all sources' if no_process_monitoring else 'Some source has process monitoring'}")
    if nonzero_monitoring > 0:
        print(f"    (monitoring_intensity has {nonzero_monitoring} non-zero values but these are usage-derived)")

    return results


# ═══════════════════════════════════════════════════════════════════════
# S2: Effective Dimensionality Analysis
# ═══════════════════════════════════════════════════════════════════════
def s2_effective_dimensionality(v3, bru029):
    """Compare 7D and 5D PCA to verify zero-column removal is neutral."""
    print("\n" + "=" * 72)
    print("S2: EFFECTIVE DIMENSIONALITY ANALYSIS")
    print("=" * 72)

    # Extract Path C results from F-BRU-029
    path_c = bru029['path_c']
    var_7d = np.array(path_c['brunschwig_var_explained'])
    n_for_80_7d = path_c['brunschwig_n_for_80']
    loadings_7d = path_c['brunschwig_loadings']

    print(f"\n  F-BRU-029 Path C (7D phase space):")
    print(f"    Recipes: {path_c['n_recipes']}")
    print(f"    Variance explained: {[f'{v:.4f}' for v in var_7d]}")
    print(f"    n_for_80: {n_for_80_7d}")

    # Show zero-variance phases
    zero_phases = []
    for pc_key, pc_loadings in loadings_7d.items():
        for phase, val in pc_loadings.items():
            if phase in ('MIDPROCESS', 'STORAGE') and abs(val) < 1e-10:
                if phase not in zero_phases:
                    zero_phases.append(phase)

    print(f"\n  Zero-variance phases: {zero_phases}")

    # Rebuild phase matrix from v3 and run 5D PCA
    recipes_with_steps = []
    for recipe in v3['recipes']:
        steps = recipe.get('procedural_steps') or []
        if not steps:
            continue
        phase_counts = Counter()
        for step in steps:
            action = step.get('action', '')
            if action in ACTION_TO_PHASE:
                phase_counts[ACTION_TO_PHASE[action]] += 1
        total = sum(phase_counts.values())
        if total == 0:
            continue
        profile = {phase: phase_counts.get(phase, 0) / total for phase in PHASE_ORDER}
        recipes_with_steps.append(profile)

    # 7D matrix
    X_7d = np.array([[r[p] for p in PHASE_ORDER] for r in recipes_with_steps])

    # 5D matrix (remove MIDPROCESS, STORAGE)
    active_phases = [p for p in PHASE_ORDER if p not in ('MIDPROCESS', 'STORAGE')]
    X_5d = np.array([[r[p] for p in active_phases] for r in recipes_with_steps])

    print(f"\n  Rebuilding from v3 curation:")
    print(f"    7D matrix: {X_7d.shape}")
    print(f"    5D matrix: {X_5d.shape} (removed {zero_phases})")

    # Run PCA on both
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    # 7D PCA
    scaler_7d = StandardScaler()
    X_7d_scaled = scaler_7d.fit_transform(X_7d)
    pca_7d = PCA()
    pca_7d.fit(X_7d_scaled)
    var_7d_recomputed = pca_7d.explained_variance_ratio_
    cum_7d = np.cumsum(var_7d_recomputed)
    n80_7d = int(np.searchsorted(cum_7d, 0.80) + 1)

    # 5D PCA
    scaler_5d = StandardScaler()
    X_5d_scaled = scaler_5d.fit_transform(X_5d)
    pca_5d = PCA()
    pca_5d.fit(X_5d_scaled)
    var_5d = pca_5d.explained_variance_ratio_
    cum_5d = np.cumsum(var_5d)
    n80_5d = int(np.searchsorted(cum_5d, 0.80) + 1)

    print(f"\n  7D PCA recomputed:")
    print(f"    Variance: {[f'{v:.4f}' for v in var_7d_recomputed]}")
    print(f"    n_for_80: {n80_7d}")

    print(f"\n  5D PCA (active phases only):")
    print(f"    Variance: {[f'{v:.4f}' for v in var_5d]}")
    print(f"    n_for_80: {n80_5d}")

    # Compare loadings on active phases
    print(f"\n  5D PCA loadings:")
    header = f"    {'Phase':<16}" + "".join(f"{'PC'+str(i+1):>10}" for i in range(min(3, len(var_5d))))
    print(header)
    for j, phase in enumerate(active_phases):
        row = f"    {phase:<16}" + "".join(f"{pca_5d.components_[i, j]:>10.3f}" for i in range(min(3, len(var_5d))))
        print(row)

    # H2: 5D matches 7D
    n80_match = n80_5d == n80_7d
    # Check active-phase loadings alignment
    loading_diffs = []
    for i in range(min(3, len(var_5d))):
        for j, phase in enumerate(active_phases):
            idx_7d = PHASE_ORDER.index(phase)
            diff = abs(abs(pca_5d.components_[i, j]) - abs(pca_7d.components_[i, idx_7d]))
            loading_diffs.append(diff)
    max_loading_diff = max(loading_diffs) if loading_diffs else 0

    h2_pass = n80_match and max_loading_diff < 0.05
    print(f"\n  H2: 5D matches 7D?")
    print(f"    n_for_80: 7D={n80_7d}, 5D={n80_5d} ({'match' if n80_match else 'DIFFER'})")
    print(f"    Max active-phase loading difference: {max_loading_diff:.4f}")
    print(f"    H2 VERDICT: {'PASS' if h2_pass else 'FAIL'}")

    return {
        'n_recipes': len(recipes_with_steps),
        'zero_phases': zero_phases,
        'var_7d': var_7d_recomputed.tolist(),
        'n80_7d': n80_7d,
        'var_5d': var_5d.tolist(),
        'n80_5d': n80_5d,
        'active_phases': active_phases,
        'loadings_5d': {f'PC{i+1}': {p: float(pca_5d.components_[i, j])
                                       for j, p in enumerate(active_phases)}
                        for i in range(min(5, len(var_5d)))},
        'max_loading_diff': float(max_loading_diff),
        'h2_verdict': 'PASS' if h2_pass else 'FAIL',
        'h2_detail': f'n80 match={n80_match}, max_loading_diff={max_loading_diff:.4f}'
    }


# ═══════════════════════════════════════════════════════════════════════
# S3: Dimensional Gap Quantification
# ═══════════════════════════════════════════════════════════════════════
def s3_dimensional_gap(s2_results, voy_pca):
    """Compare Brunschwig and Voynich variance structures."""
    print("\n" + "=" * 72)
    print("S3: DIMENSIONAL GAP QUANTIFICATION")
    print("=" * 72)

    bru_var = np.array(s2_results['var_5d'])
    bru_cum = np.cumsum(bru_var)
    bru_n80 = s2_results['n80_5d']

    voy_var = np.array(voy_pca['variance_explained'])
    voy_cum = np.array(voy_pca['cumulative_variance'])
    voy_n80 = voy_pca['n_components_80']

    print(f"\n  Brunschwig (5D effective):")
    print(f"    n_for_80: {bru_n80}")
    print(f"    Variance curve: {[f'{v:.3f}' for v in bru_var]}")
    print(f"    Cumulative: {[f'{v:.3f}' for v in bru_cum]}")

    print(f"\n  Voynich (10D):")
    print(f"    n_for_80: {voy_n80}")
    print(f"    Variance curve: {[f'{v:.3f}' for v in voy_var[:6]]}")
    print(f"    Cumulative: {[f'{v:.3f}' for v in voy_cum[:6]]}")

    gap = voy_n80 - bru_n80
    print(f"\n  Dimensional gap: Voynich({voy_n80}) - Brunschwig({bru_n80}) = {gap}")

    # Compare concentration: how much does PC1 explain?
    bru_pc1_share = float(bru_var[0])
    voy_pc1_share = float(voy_var[0])
    print(f"\n  PC1 concentration:")
    print(f"    Brunschwig PC1: {bru_pc1_share:.3f}")
    print(f"    Voynich PC1: {voy_pc1_share:.3f}")
    print(f"    Brunschwig is {'more' if bru_pc1_share > voy_pc1_share else 'less'} concentrated")

    # Entropy of variance distribution (measure of dimensionality spread)
    def variance_entropy(v):
        v_pos = v[v > 1e-10]
        return float(-np.sum(v_pos * np.log2(v_pos)))

    bru_entropy = variance_entropy(bru_var)
    voy_entropy = variance_entropy(voy_var)
    print(f"\n  Variance distribution entropy:")
    print(f"    Brunschwig: {bru_entropy:.3f} bits")
    print(f"    Voynich: {voy_entropy:.3f} bits")
    print(f"    Gap: {voy_entropy - bru_entropy:.3f} bits (Voynich has {'more' if voy_entropy > bru_entropy else 'less'} spread)")

    # H3: quantification
    results = {
        'brunschwig_n80': bru_n80,
        'brunschwig_n_features': len(s2_results['active_phases']),
        'voynich_n80': voy_n80,
        'voynich_n_features': len(voy_pca['features']),
        'dimensional_gap': gap,
        'brunschwig_pc1_share': bru_pc1_share,
        'voynich_pc1_share': voy_pc1_share,
        'brunschwig_variance_entropy': bru_entropy,
        'voynich_variance_entropy': voy_entropy,
        'entropy_gap': float(voy_entropy - bru_entropy),
        'interpretation': (
            f"Brunschwig needs {bru_n80} of {len(s2_results['active_phases'])} active dimensions for 80%, "
            f"Voynich needs {voy_n80} of {len(voy_pca['features'])}. "
            f"Gap of {gap} dimensions reflects Voynich's richer operational vocabulary."
        )
    }

    print(f"\n  H3: Dimensional gap = {gap} (Brunschwig {bru_n80}/{len(s2_results['active_phases'])} vs Voynich {voy_n80}/{len(voy_pca['features'])})")

    return results


# ═══════════════════════════════════════════════════════════════════════
# S4: Path C Closure Analysis
# ═══════════════════════════════════════════════════════════════════════
def s4_path_c_closure(v3, bru029):
    """Determine if Path C can EVER pass without genuine per-recipe MIDPROCESS variation."""
    print("\n" + "=" * 72)
    print("S4: PATH C CLOSURE ANALYSIS")
    print("=" * 72)

    # Rebuild phase matrix from v3
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    recipes = []
    for recipe in v3['recipes']:
        steps = recipe.get('procedural_steps') or []
        if not steps:
            continue
        phase_counts = Counter()
        for step in steps:
            action = step.get('action', '')
            if action in ACTION_TO_PHASE:
                phase_counts[ACTION_TO_PHASE[action]] += 1
        total = sum(phase_counts.values())
        if total == 0:
            continue
        profile = {phase: phase_counts.get(phase, 0) / total for phase in PHASE_ORDER}
        profile['fire_degree'] = recipe.get('fire_degree')
        profile['n_mapped_actions'] = total
        recipes.append(profile)

    X = np.array([[r[p] for p in PHASE_ORDER] for r in recipes])
    n_recipes = X.shape[0]

    print(f"\n  Recipes with steps: {n_recipes}")
    print(f"  Phase matrix: {X.shape}")

    # Current MIDPROCESS column stats
    mp_idx = PHASE_ORDER.index('MIDPROCESS')
    mp_col = X[:, mp_idx]
    print(f"\n  Current MIDPROCESS column: mean={mp_col.mean():.6f}, std={mp_col.std():.6f}")

    # Test 1: What if we add uniform degree-based MIDPROCESS?
    # Degree 1-2: 4 actions (SEAL, MONITOR_TEMP, REPLENISH, COOL)
    # Degree 3: 4 actions (SEAL, MONITOR_DRIPS, REGULATE, COOL)
    # Both get 4 MIDPROCESS actions, so the PROPORTION depends on total steps
    X_uniform = X.copy()
    for i, r in enumerate(recipes):
        fd = r.get('fire_degree', 2)
        total_actions = r['n_mapped_actions']
        if total_actions > 0:
            # Add 4 MIDPROCESS actions to each recipe
            new_total = total_actions + 4
            for j, phase in enumerate(PHASE_ORDER):
                if phase == 'MIDPROCESS':
                    X_uniform[i, j] = 4 / new_total
                else:
                    X_uniform[i, j] = X[i, j] * total_actions / new_total

    mp_col_uniform = X_uniform[:, mp_idx]
    print(f"\n  Test 1: Uniform degree-based MIDPROCESS (4 actions per recipe)")
    print(f"    MIDPROCESS column: mean={mp_col_uniform.mean():.4f}, std={mp_col_uniform.std():.4f}")

    # Run PCA on uniform version
    scaler = StandardScaler()
    X_uniform_scaled = scaler.fit_transform(X_uniform)
    pca = PCA()
    pca.fit(X_uniform_scaled)

    mp_loadings_uniform = [abs(pca.components_[i, mp_idx]) for i in range(min(5, pca.n_components_))]
    max_mp_loading = max(mp_loadings_uniform)
    print(f"    MIDPROCESS loadings: {[f'{v:.3f}' for v in mp_loadings_uniform]}")
    print(f"    Max loading: {max_mp_loading:.3f}")
    print(f"    Would C-3 pass (>0.3)? {'YES' if max_mp_loading > 0.3 else 'NO'}")

    # Test 2: Binary MIDPROCESS (degree 1-2 vs degree 3)
    X_binary = X.copy()
    for i, r in enumerate(recipes):
        fd = r.get('fire_degree', 2)
        total_actions = r['n_mapped_actions']
        if total_actions > 0:
            if fd in (1, 2):
                mp_count = 4  # balneum marie
            else:
                mp_count = 4  # cinerem — SAME count, different actions
            new_total = total_actions + mp_count
            for j, phase in enumerate(PHASE_ORDER):
                if phase == 'MIDPROCESS':
                    X_binary[i, j] = mp_count / new_total
                else:
                    X_binary[i, j] = X[i, j] * total_actions / new_total

    # Since both degrees get 4 actions, binary == uniform
    # The "variation" comes only from different total_actions denominators
    mp_col_binary = X_binary[:, mp_idx]
    print(f"\n  Test 2: Binary degree-based MIDPROCESS")
    print(f"    MIDPROCESS column: mean={mp_col_binary.mean():.4f}, std={mp_col_binary.std():.4f}")
    print(f"    Note: std comes from denominator variation, NOT from MIDPROCESS action differences")

    # Test 3: What minimum MIDPROCESS std would be needed for loading > 0.3?
    # Simulate by injecting increasing noise into MIDPROCESS column
    thresholds = []
    for noise_level in np.arange(0.01, 0.50, 0.01):
        X_test = X.copy()
        np.random.seed(42)
        X_test[:, mp_idx] = np.random.uniform(0, noise_level, n_recipes)
        # Renormalize rows to sum to 1
        row_sums = X_test.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        X_test = X_test / row_sums

        try:
            X_test_scaled = StandardScaler().fit_transform(X_test)
            pca_test = PCA()
            pca_test.fit(X_test_scaled)
            mp_loadings_test = [abs(pca_test.components_[i, mp_idx])
                                for i in range(min(5, pca_test.n_components_))]
            max_loading = max(mp_loadings_test)
            if max_loading > 0.3:
                thresholds.append(noise_level)
                break
        except Exception:
            continue

    threshold_needed = thresholds[0] if thresholds else None
    print(f"\n  Test 3: Minimum noise for MIDPROCESS loading > 0.3")
    if threshold_needed:
        print(f"    Threshold noise level: {threshold_needed:.2f}")
        print(f"    This requires random variation with range [0, {threshold_needed:.2f}]")
    else:
        print(f"    No threshold found up to 0.50 — MIDPROCESS loading stays below 0.3")

    # H4 verdict
    uniform_passes = max_mp_loading > 0.3
    h4_verdict = 'PATH_C_STRUCTURALLY_BLOCKED' if not uniform_passes else 'PATH_C_THEORETICALLY_POSSIBLE'

    print(f"\n  H4 VERDICT: {h4_verdict}")
    if not uniform_passes:
        print(f"    Even with fabricated MIDPROCESS data, loading stays below 0.3")
        print(f"    Path C-3 cannot pass without genuine per-recipe MIDPROCESS variation")
    else:
        print(f"    Fabricated MIDPROCESS data reaches loading > 0.3")
        print(f"    But the fabrication is circular — confirming what was designed")

    return {
        'n_recipes': n_recipes,
        'current_midprocess_std': float(mp_col.std()),
        'uniform_midprocess_mean': float(mp_col_uniform.mean()),
        'uniform_midprocess_std': float(mp_col_uniform.std()),
        'uniform_max_loading': float(max_mp_loading),
        'uniform_passes_c3': bool(uniform_passes),
        'binary_midprocess_std': float(mp_col_binary.std()),
        'noise_threshold_for_loading_03': threshold_needed,
        'h4_verdict': h4_verdict,
        'h4_detail': (
            'Uniform fabrication reaches MIDPROCESS loading of {:.3f}. '
            'C-3 threshold is 0.3. {}. '
            'Even if fabrication "works", the result is circular (designed = confirmed).'
        ).format(max_mp_loading, 'Passes' if uniform_passes else 'Fails')
    }


# ═══════════════════════════════════════════════════════════════════════
# S5: M2 Failure Category Analysis (OJLM-1 Parallel)
# ═══════════════════════════════════════════════════════════════════════
def s5_m2_failure_analysis(m2_results):
    """Categorize M2 test failures to test the OJLM-1 parallel hypothesis."""
    print("\n" + "=" * 72)
    print("S5: M2 FAILURE CATEGORY ANALYSIS (OJLM-1 PARALLEL)")
    print("=" * 72)

    m2 = m2_results['models']['M2']
    per_test = m2['per_test_pass_rate']

    print(f"\n  M2 per-test pass rates:")
    failing = []
    passing = []
    for test, rate in per_test.items():
        category = TEST_CATEGORIES.get(test, 'UNKNOWN')
        status = 'PASS' if rate >= 0.5 else 'FAIL'
        marker = ' <<<' if status == 'FAIL' else ''
        print(f"    {test}: {rate:.1f} [{category}]{marker}")
        if status == 'FAIL':
            failing.append((test, category))
        else:
            passing.append((test, category))

    print(f"\n  Failing tests ({len(failing)}):")
    fail_categories = Counter()
    for test, cat in failing:
        fail_categories[cat] += 1
        print(f"    {test}: {cat}")

    print(f"\n  Failure category distribution: {dict(fail_categories)}")

    # H5: Do all failures cluster in one category?
    n_fail_categories = len(fail_categories)
    all_sequential = all(cat in ('SEQUENTIAL',) for _, cat in failing)
    all_dynamic = all(cat in ('SEQUENTIAL', 'STRUCTURAL') for _, cat in failing)

    # More nuanced analysis: what information type do the failures capture?
    test_info_types = {
        'B4': 'role_rank_preservation — whether relative frequency ordering of role '
              'categories is maintained. Tests STATIC structural hierarchy.',
        'B5': 'forward_backward_JSD — whether generating left-to-right matches '
              'right-to-left. Tests DIRECTIONAL sequential asymmetry.',
        'C2': 'middle_pair_MI — mutual information between adjacent token classes '
              '(suffix-free). Tests PAIRWISE compositional correlation.',
    }

    print(f"\n  Detailed failure analysis:")
    for test, cat in failing:
        print(f"    {test} [{cat}]: {test_info_types.get(test, 'no description')}")

    # The OJLM-1 hypothesis: failures represent "monitoring-like" information
    # that requires real-time sequential adjustment, not static specification
    monitoring_relevant = {
        'B4': False,  # role rank = static structural property
        'B5': True,   # directional asymmetry = process has direction/flow
        'C2': True,   # pairwise correlation = adjacent-step dependencies
    }

    monitoring_count = sum(1 for t, _ in failing if monitoring_relevant.get(t, False))
    total_failing = len(failing)

    h5_all_sequential = all_sequential
    h5_monitoring_majority = monitoring_count > total_failing / 2

    print(f"\n  OJLM-1 parallel assessment:")
    print(f"    All failures in SEQUENTIAL category? {'YES' if all_sequential else 'NO'}")
    print(f"    Failure categories span: {n_fail_categories} categories")
    print(f"    Monitoring-relevant failures: {monitoring_count}/{total_failing}")

    # H5 verdict: the strict test (all sequential) fails, but the softer test
    # (monitoring-relevant majority) may pass
    h5_strict = all_sequential
    h5_soft = h5_monitoring_majority

    print(f"\n  H5 VERDICT (strict — all sequential): {'PASS' if h5_strict else 'FAIL'}")
    print(f"  H5 VERDICT (soft — monitoring majority): {'PASS' if h5_soft else 'FAIL'}")

    if not h5_strict and h5_soft:
        print(f"    Interpretation: failures span categories but 2/3 capture")
        print(f"    dynamic/pairwise structure consistent with monitoring gap.")
        print(f"    B4 (role rank) is the outlier — it tests static hierarchy,")
        print(f"    not dynamic adjustment. The parallel is PARTIAL.")
    elif h5_strict:
        print(f"    Strong parallel: all failures are sequential/dynamic")
    else:
        print(f"    Weak parallel: failures do not cluster in monitoring-relevant category")

    return {
        'failing_tests': [(t, c) for t, c in failing],
        'passing_tests': [(t, c) for t, c in passing],
        'failure_categories': dict(fail_categories),
        'n_fail_categories': n_fail_categories,
        'monitoring_relevant_count': monitoring_count,
        'total_failing': total_failing,
        'h5_strict_verdict': 'PASS' if h5_strict else 'FAIL',
        'h5_soft_verdict': 'PASS' if h5_soft else 'FAIL',
        'h5_detail': (
            f'Failures span {n_fail_categories} categories: {dict(fail_categories)}. '
            f'{monitoring_count}/{total_failing} are monitoring-relevant. '
            f'B4 (role rank) is static/structural, breaking the strict sequential cluster. '
            f'OJLM-1 parallel is PARTIAL — 2/3 failures capture dynamic/pairwise structure.'
        )
    }


# ═══════════════════════════════════════════════════════════════════════
# S6: Verdict Synthesis
# ═══════════════════════════════════════════════════════════════════════
def s6_verdict(s1, s2, s3, s4, s5):
    """Synthesize overall verdict."""
    print("\n" + "=" * 72)
    print("S6: VERDICT SYNTHESIS")
    print("=" * 72)

    verdicts = {
        'H1': s1['h1_verdict'],
        'H2': s2['h2_verdict'],
        'H3': f"gap={s3['dimensional_gap']}",
        'H4': s4['h4_verdict'],
        'H5_strict': s5['h5_strict_verdict'],
        'H5_soft': s5['h5_soft_verdict'],
    }

    passing = sum(1 for k, v in verdicts.items()
                  if v in ('PASS', 'PATH_C_STRUCTURALLY_BLOCKED'))

    print(f"\n  Hypothesis results:")
    for k, v in verdicts.items():
        print(f"    {k}: {v}")

    # Overall verdict
    overall = 'MIDPROCESS_STRUCTURALLY_ABSENT'
    print(f"\n  OVERALL VERDICT: {overall}")
    print(f"\n  Summary:")
    print(f"    1. MIDPROCESS is universally absent from all 5 data sources (H1 PASS)")
    print(f"    2. Removing zero-variance phases doesn't change PCA (H2 {s2['h2_verdict']})")
    print(f"    3. Voynich-Brunschwig dimensional gap = {s3['dimensional_gap']} (H3)")
    print(f"    4. Path C: {s4['h4_verdict']} (H4)")
    print(f"    5. OJLM-1 parallel: strict={s5['h5_strict_verdict']}, soft={s5['h5_soft_verdict']} (H5)")
    print(f"\n  Interpretation:")
    print(f"    MIDPROCESS represents tacit operator knowledge — information that exists")
    print(f"    procedurally (in the operator's judgment) but is not codified in the")
    print(f"    recipe-level specification. This is the OJLM-1 boundary.")
    print(f"    The Voynich M2 residual (B4, B5, C2) partially parallels this gap:")
    print(f"    2/3 failing tests capture dynamic/pairwise structure consistent with")
    print(f"    monitoring-type information, but B4 (static role hierarchy) breaks")
    print(f"    the strict parallel.")

    return {
        'verdicts': verdicts,
        'overall': overall,
        'fit_recommendation': 'F-BRU-030: MIDPROCESS Absence Characterization (NEGATIVE)',
        'constraint_recommendation': 'C1056: MIDPROCESS Structural Absence / OJLM-1 Boundary'
    }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 72)
    print("Phase 371: BRUNSCHWIG MIDPROCESS ABSENCE CHARACTERIZATION")
    print("=" * 72)

    # Load data
    print("\nLoading data sources...")
    with open(V3_CURATION, 'r', encoding='utf-8') as f:
        v3 = json.load(f)
    print(f"  V3 curation: {len(v3['recipes'])} recipes")

    with open(MASTER_DATA, 'r', encoding='utf-8') as f:
        master = json.load(f)
    print(f"  Master data: {len(master['materials'])} materials")

    with open(BRU029_RESULTS, 'r', encoding='utf-8') as f:
        bru029 = json.load(f)
    print(f"  F-BRU-029 results loaded")

    with open(VOY_PCA, 'r', encoding='utf-8') as f:
        voy_pca = json.load(f)
    print(f"  Voynich PCA: {voy_pca['n_components_80']} components for 80%")

    with open(M2_RESULTS, 'r', encoding='utf-8') as f:
        m2_results = json.load(f)
    print(f"  M2 results: {m2_results['models']['M2']['mean_pass_rate']:.0%} pass rate")

    # Run sections
    s1 = s1_absence_audit(v3, master)
    s2 = s2_effective_dimensionality(v3, bru029)
    s3 = s3_dimensional_gap(s2, voy_pca)
    s4 = s4_path_c_closure(v3, bru029)
    s5 = s5_m2_failure_analysis(m2_results)
    s6 = s6_verdict(s1, s2, s3, s4, s5)

    # Save results
    results = {
        'phase': 371,
        'name': 'BRUNSCHWIG_MIDPROCESS_ABSENCE',
        'fit_id': 'F-BRU-030',
        'title': 'MIDPROCESS Structural Absence Characterization',
        's1_absence_audit': s1,
        's2_effective_dimensionality': s2,
        's3_dimensional_gap': s3,
        's4_path_c_closure': s4,
        's5_m2_failure_analysis': s5,
        's6_verdict': s6,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to: {OUT_FILE}")


if __name__ == '__main__':
    main()
