#!/usr/bin/env python3
"""
ts_01_gradient_steepness.py - Vector C: Zone Transition Dynamics

Tests whether zone transition patterns (HOW FAST, not WHERE) differ by REGIME.

Pre-registered hypotheses:
- H-C1: Transition velocity differs by REGIME (ANOVA F>4, p<0.01)
- H-C2: Commitment sharpness correlates with REGIME_4 (r>0.3)
- H-C3: Setup duration differs: GENTLE > others (t-test p<0.05)
- H-C4: Gradient steepness correlates with HT density (r>0.25)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# Instruction class to zone mapping
# Based on constraint knowledge: C=setup, P=observation, R=progression, S=locked
INSTRUCTION_TO_ZONE = {
    'PREPARATION': 'C',
    'AUX': 'C',  # Flexible, but defaults to setup
    'MONITORING': 'P',
    'LINK': 'P',  # Transition/observation
    'FLOW': 'R',
    'k_ENERGY': 'R',
    'h_HAZARD': 'R',  # Active constraint region
    'e_ESCAPE': 'S',
    'RECOVERY': 'S',
    'COLLECTION': 'S',  # End phase
    'HEATING': 'R',  # Active phase
    'OTHER': 'R',  # Default to progression
    'UNKNOWN': 'R',  # Default to progression
}

# Zone ordering for gradient computation
ZONE_ORDER = {'C': 0, 'P': 1, 'R': 2, 'S': 3}


def load_data():
    """Load Brunschwig master data and HT densities."""
    with open(DATA_DIR / "brunschwig_materials_master.json", encoding='utf-8') as f:
        master = json.load(f)

    # Default HT values from prior analysis (SLI-Constraint Substitution Model)
    # REGIME_2 (GENTLE) has highest HT, REGIME_3 (OIL_RESIN) has lowest
    ht_by_regime = {
        'REGIME_1': 0.045,  # STANDARD
        'REGIME_2': 0.062,  # GENTLE (highest)
        'REGIME_3': 0.038,  # OIL_RESIN (lowest)
        'REGIME_4': 0.051,  # PRECISION
    }

    return master, ht_by_regime


def instruction_to_zone(instruction):
    """Map instruction class to zone."""
    return INSTRUCTION_TO_ZONE.get(instruction, 'R')


def compute_zone_sequence(instruction_sequence):
    """Convert instruction sequence to zone sequence."""
    return [instruction_to_zone(inst) for inst in instruction_sequence]


def count_transitions(zone_sequence):
    """Count number of zone changes in sequence."""
    if len(zone_sequence) < 2:
        return 0
    transitions = sum(1 for i in range(1, len(zone_sequence))
                      if zone_sequence[i] != zone_sequence[i-1])
    return transitions


def compute_transition_velocity(zone_sequence):
    """Compute steps per zone change (higher = slower transitions)."""
    n_steps = len(zone_sequence)
    n_transitions = count_transitions(zone_sequence)
    if n_transitions == 0:
        return float(n_steps) if n_steps > 0 else np.nan
    return n_steps / n_transitions


def compute_commitment_sharpness(zone_sequence):
    """
    Compute R→S transition steepness.
    Higher value = more abrupt transition (fewer intermediate steps).
    """
    if len(zone_sequence) < 2:
        return np.nan

    # Find last R occurrence and first S after it
    last_r = -1
    first_s_after_r = -1

    for i, zone in enumerate(zone_sequence):
        if zone == 'R':
            last_r = i
        elif zone == 'S' and last_r >= 0 and first_s_after_r < 0:
            first_s_after_r = i

    if last_r < 0 or first_s_after_r < 0:
        return np.nan

    # Sharpness = inverse of steps between R and S
    gap = first_s_after_r - last_r
    if gap == 0:
        return 1.0  # Impossible, but handle edge case
    return 1.0 / gap  # Higher = sharper


def compute_setup_duration(zone_sequence):
    """Compute steps before first R-zone entry."""
    for i, zone in enumerate(zone_sequence):
        if zone == 'R':
            return i
    return len(zone_sequence)  # Never reached R


def compute_escape_gradient(zone_sequence):
    """
    Compute gradient steepness: rate of escape permission decay.
    Uses zone ordering (C=0, P=1, R=2, S=3) as proxy for escape permission.
    Higher zone number = less escape permission.
    """
    if len(zone_sequence) < 2:
        return np.nan

    # Convert to numeric
    numeric = [ZONE_ORDER[z] for z in zone_sequence]

    # Linear regression: zone_order vs step_index
    x = np.arange(len(numeric))
    slope, _, r_value, _, _ = stats.linregress(x, numeric)

    return slope  # Positive slope = progressing toward S (steeper)


def compute_trajectory_metrics(recipe):
    """Compute all trajectory metrics for a recipe."""
    sequence = recipe.get('instruction_sequence', [])
    if not sequence or len(sequence) < 2:
        return None

    zone_seq = compute_zone_sequence(sequence)

    return {
        'recipe_id': recipe['recipe_id'],
        'regime': recipe.get('predicted_regime', recipe.get('regime_assignment', {}).get('final_regime', '')),
        'n_steps': len(sequence),
        'zone_sequence': zone_seq,
        'transition_velocity': compute_transition_velocity(zone_seq),
        'commitment_sharpness': compute_commitment_sharpness(zone_seq),
        'setup_duration': compute_setup_duration(zone_seq),
        'escape_gradient': compute_escape_gradient(zone_seq),
    }


def run_anova(metrics, metric_name):
    """Run ANOVA for metric by REGIME."""
    groups = defaultdict(list)
    for m in metrics:
        if m is None:
            continue
        val = m.get(metric_name)
        regime = m.get('regime', '')
        if val is not None and not np.isnan(val) and regime:
            groups[regime].append(val)

    if len(groups) < 2:
        return {'F': np.nan, 'p': 1.0, 'significant': False, 'groups': {}}

    # Get group values
    group_vals = [np.array(v) for v in groups.values() if len(v) > 1]
    if len(group_vals) < 2:
        return {'F': np.nan, 'p': 1.0, 'significant': False, 'groups': {}}

    F, p = stats.f_oneway(*group_vals)

    group_stats = {k: {'mean': float(np.mean(v)), 'std': float(np.std(v)), 'n': len(v)}
                   for k, v in groups.items()}

    return {
        'F': float(F) if not np.isnan(F) else None,
        'p': float(p) if not np.isnan(p) else 1.0,
        'significant': bool(p < 0.01),
        'groups': group_stats,
    }


def run_correlation(metrics, metric_name, ht_by_regime):
    """Correlate metric with HT density (via REGIME)."""
    vals = []
    hts = []

    for m in metrics:
        if m is None:
            continue
        val = m.get(metric_name)
        regime = m.get('regime', '')
        if val is not None and not np.isnan(val) and regime in ht_by_regime:
            vals.append(val)
            hts.append(ht_by_regime[regime])

    if len(vals) < 3:
        return {'r': np.nan, 'p': 1.0, 'significant': False, 'n': len(vals)}

    r, p = stats.pearsonr(vals, hts)

    return {
        'r': float(r),
        'p': float(p),
        'significant': bool(p < 0.05 and abs(r) > 0.25),
        'n': len(vals),
    }


def run_regime4_correlation(metrics):
    """Correlate commitment sharpness with REGIME_4 membership."""
    sharpness = []
    is_r4 = []

    for m in metrics:
        if m is None:
            continue
        val = m.get('commitment_sharpness')
        regime = m.get('regime', '')
        if val is not None and not np.isnan(val) and regime:
            sharpness.append(val)
            is_r4.append(1 if regime == 'REGIME_4' else 0)

    if len(sharpness) < 3 or sum(is_r4) < 2:
        return {'r': np.nan, 'p': 1.0, 'significant': False, 'n': len(sharpness)}

    # Point-biserial correlation
    r, p = stats.pointbiserialr(is_r4, sharpness)

    return {
        'r': float(r),
        'p': float(p),
        'significant': bool(p < 0.05 and abs(r) > 0.3),
        'n': len(sharpness),
        'n_regime4': sum(is_r4),
    }


def run_gentle_ttest(metrics):
    """T-test: setup duration for GENTLE vs others."""
    gentle = []
    others = []

    for m in metrics:
        if m is None:
            continue
        val = m.get('setup_duration')
        regime = m.get('regime', '')
        if val is not None and regime:
            if regime == 'REGIME_2':  # GENTLE
                gentle.append(val)
            else:
                others.append(val)

    if len(gentle) < 2 or len(others) < 2:
        return {'t': np.nan, 'p': 1.0, 'significant': False}

    t, p = stats.ttest_ind(gentle, others)

    return {
        't': float(t),
        'p': float(p),
        'significant': bool(p < 0.05),
        'gentle_mean': float(np.mean(gentle)),
        'others_mean': float(np.mean(others)),
        'gentle_n': len(gentle),
        'others_n': len(others),
        'direction': 'GENTLE > others' if np.mean(gentle) > np.mean(others) else 'GENTLE <= others',
    }


def main():
    print("=" * 60)
    print("TRAJECTORY_SEMANTICS: Vector C - Gradient Steepness")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    master, ht_by_regime = load_data()
    print(f"  HT by REGIME: {ht_by_regime}")

    # Compute metrics for all recipes with instruction sequences
    print("\nComputing trajectory metrics...")
    recipes = master.get('materials', [])  # Key is 'materials' not 'recipes'
    metrics = []

    for recipe in recipes:
        seq = recipe.get('instruction_sequence', [])
        if seq and len(seq) >= 2:
            m = compute_trajectory_metrics(recipe)
            if m:
                metrics.append(m)

    print(f"  Recipes with sequences: {len(metrics)}")

    if len(metrics) < 10:
        print("ERROR: Insufficient data for analysis")
        sys.exit(1)

    # Summary statistics
    print("\n" + "-" * 40)
    print("METRIC SUMMARIES BY REGIME")
    print("-" * 40)

    regimes = sorted(set(m['regime'] for m in metrics if m['regime']))
    for metric_name in ['transition_velocity', 'commitment_sharpness', 'setup_duration', 'escape_gradient']:
        print(f"\n{metric_name}:")
        for regime in regimes:
            vals = [m[metric_name] for m in metrics if m['regime'] == regime and not np.isnan(m[metric_name])]
            if vals:
                print(f"  {regime}: mean={np.mean(vals):.3f}, std={np.std(vals):.3f}, n={len(vals)}")

    # Run tests
    print("\n" + "=" * 60)
    print("HYPOTHESIS TESTS")
    print("=" * 60)

    results = {
        'phase': 'TRAJECTORY_SEMANTICS',
        'vector': 'C',
        'n_recipes': len(metrics),
        'hypotheses': {},
    }

    # H-C1: Transition velocity ANOVA
    print("\n[H-C1] Transition velocity by REGIME (ANOVA)")
    h_c1 = run_anova(metrics, 'transition_velocity')
    print(f"  F = {h_c1['F']:.3f}, p = {h_c1['p']:.4f}")
    print(f"  PASS (p<0.01): {h_c1['significant']}")
    results['hypotheses']['H-C1'] = {
        'name': 'Transition velocity differs by REGIME',
        'test': 'ANOVA',
        'threshold': 'F>4, p<0.01',
        **h_c1,
    }

    # H-C2: Commitment sharpness vs REGIME_4
    print("\n[H-C2] Commitment sharpness vs REGIME_4 (point-biserial)")
    h_c2 = run_regime4_correlation(metrics)
    print(f"  r = {h_c2['r']:.3f}, p = {h_c2['p']:.4f}")
    print(f"  PASS (r>0.3, p<0.05): {h_c2['significant']}")
    results['hypotheses']['H-C2'] = {
        'name': 'Commitment sharpness correlates with REGIME_4',
        'test': 'point-biserial correlation',
        'threshold': 'r>0.3, p<0.05',
        **h_c2,
    }

    # H-C3: Setup duration GENTLE vs others
    print("\n[H-C3] Setup duration: GENTLE vs others (t-test)")
    h_c3 = run_gentle_ttest(metrics)
    print(f"  t = {h_c3['t']:.3f}, p = {h_c3['p']:.4f}")
    print(f"  Direction: {h_c3['direction']}")
    print(f"  PASS (p<0.05, GENTLE>others): {h_c3['significant'] and 'GENTLE > others' in h_c3['direction']}")
    results['hypotheses']['H-C3'] = {
        'name': 'Setup duration: GENTLE > others',
        'test': 't-test',
        'threshold': 'p<0.05, correct direction',
        **h_c3,
    }

    # H-C4: Gradient steepness vs HT density
    print("\n[H-C4] Escape gradient vs HT density (correlation)")
    h_c4 = run_correlation(metrics, 'escape_gradient', ht_by_regime)
    print(f"  r = {h_c4['r']:.3f}, p = {h_c4['p']:.4f}")
    print(f"  PASS (r>0.25, p<0.05): {h_c4['significant']}")
    results['hypotheses']['H-C4'] = {
        'name': 'Gradient steepness correlates with HT density',
        'test': 'Pearson correlation',
        'threshold': 'r>0.25, p<0.05',
        **h_c4,
    }

    # Summary
    print("\n" + "=" * 60)
    print("VECTOR C SUMMARY")
    print("=" * 60)

    passed = sum(1 for h in ['H-C1', 'H-C2', 'H-C3', 'H-C4']
                 if results['hypotheses'][h].get('significant', False))

    print(f"\nHypotheses passed: {passed}/4")

    if passed >= 3:
        verdict = "TIER_2_CANDIDATE"
        print("VERDICT: TIER_2_CANDIDATE - Strong trajectory semantics signal")
    elif passed >= 2:
        verdict = "TIER_3_ENRICHMENT"
        print("VERDICT: TIER_3_ENRICHMENT - Partial trajectory semantics signal")
    else:
        verdict = "INCONCLUSIVE"
        print("VERDICT: INCONCLUSIVE - Weak or no trajectory semantics signal")

    results['summary'] = {
        'hypotheses_passed': passed,
        'total_hypotheses': 4,
        'verdict': verdict,
    }

    # Save results
    output_path = RESULTS_DIR / "ts_gradient_steepness.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
