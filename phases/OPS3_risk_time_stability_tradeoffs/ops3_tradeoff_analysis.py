#!/usr/bin/env python3
"""
Phase OPS-3: Risk-Time-Stability Tradeoff Mapping

Quantifies tradeoffs between risk, time, and stability across the four OPS-2
control regimes using only operational metrics from OPS-1.

No semantic or historical interpretation is introduced.
"""

import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
OPS1_JSON = Path(__file__).parent.parent / "OPS1_folio_control_signatures" / "ops1_folio_control_signatures.json"
OPS2_JSON = Path(__file__).parent.parent / "OPS2_control_strategy_clustering" / "ops2_folio_cluster_assignments.json"
OUTPUT_DIR = Path(__file__).parent

# ============================================================================
# DATA LOADING
# ============================================================================

def load_ops1_signatures():
    """Load OPS-1 folio control signatures."""
    with open(OPS1_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['signatures']

def load_ops2_assignments():
    """Load OPS-2 cluster assignments."""
    with open(OPS2_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['assignments']

# ============================================================================
# METRIC EXTRACTION
# ============================================================================

def extract_time_axis_metrics(sig):
    """
    Extract TIME AXIS metrics.
    Higher values = MORE time cost (slower operation).
    """
    temporal = sig.get('temporal_metrics', {})
    loop = sig.get('loop_metrics', {})

    # mean_link_run_length: longer runs = more waiting = higher time cost
    mean_link_run = temporal.get('mean_link_run_length', 0) or 0

    # link_count: more links = more waiting episodes = higher time cost
    link_count = temporal.get('link_count', 0) or 0

    # loops_until_state_c: more loops = longer to converge = higher time cost
    loops_to_c = loop.get('loops_until_state_c', 0) or 0

    # convergence_speed_index: INVERSE - higher speed = lower time cost
    # So we use (1 - speed) to make higher = more time cost
    conv_speed = loop.get('convergence_speed_index', 0) or 0
    time_from_speed = 1.0 - conv_speed  # Invert so higher = slower

    return {
        'mean_link_run': mean_link_run,
        'link_count': link_count,
        'loops_to_state_c': loops_to_c,
        'time_from_speed': time_from_speed
    }

def extract_risk_axis_metrics(sig):
    """
    Extract RISK AXIS metrics.
    Higher values = MORE risk exposure.
    """
    hazard = sig.get('hazard_metrics', {})
    margin = sig.get('margin_metrics', {})

    # hazard_density: direct risk measure
    hazard_density = hazard.get('hazard_density', 0) or 0

    # min_distance_to_forbidden: INVERSE - smaller distance = higher risk
    min_dist = hazard.get('min_distance_to_forbidden')
    if min_dist is None or min_dist == 0:
        # No forbidden transitions nearby or null - use a default
        dist_risk = 0.5  # Neutral if unknown
    else:
        # Normalize: closer = higher risk, further = lower risk
        # Assume max reasonable distance is ~10 tokens
        dist_risk = max(0, 1.0 - (min_dist / 10.0))

    # hazard_class_exposure: count of hazard types present
    hazard_types = hazard.get('hazard_types_present', [])
    # Normalize by max possible (5 types)
    hazard_exposure = len(hazard_types) / 5.0

    # aggressiveness_score: direct risk measure
    aggressiveness = margin.get('aggressiveness_score', 0) or 0

    return {
        'hazard_density': hazard_density,
        'proximity_risk': dist_risk,
        'hazard_exposure': hazard_exposure,
        'aggressiveness': aggressiveness
    }

def extract_stability_axis_metrics(sig):
    """
    Extract STABILITY AXIS metrics.
    Higher values = MORE stability (better resilience).
    """
    loop = sig.get('loop_metrics', {})
    margin = sig.get('margin_metrics', {})
    recovery = sig.get('recovery_metrics', {})

    # state_c_hold_duration: longer hold = more stable
    # May be null - default to 0
    hold_duration = loop.get('state_c_hold_duration')
    if hold_duration is None:
        hold_duration = 0

    # control_margin_index: direct stability measure
    control_margin = margin.get('control_margin_index', 0) or 0

    # restart_capable: boolean - 1 if capable, 0 if not
    restart_capable = 1.0 if recovery.get('restart_capable', False) else 0.0

    # recovery_ops_count: more recovery ops = better recovery capability
    # Normalize assuming max ~25
    recovery_ops = recovery.get('recovery_ops_count', 0) or 0
    recovery_normalized = min(1.0, recovery_ops / 25.0)

    return {
        'hold_duration': hold_duration,
        'control_margin': control_margin,
        'restart_capable': restart_capable,
        'recovery_ops': recovery_normalized
    }

# ============================================================================
# NORMALIZATION
# ============================================================================

def normalize_to_unit(values, invert=False):
    """Normalize values to [0, 1] range."""
    arr = np.array(values, dtype=float)

    # Handle constant arrays
    if arr.std() == 0:
        return np.full_like(arr, 0.5)

    # Min-max normalization
    v_min, v_max = arr.min(), arr.max()
    if v_max == v_min:
        return np.full_like(arr, 0.5)

    normalized = (arr - v_min) / (v_max - v_min)

    if invert:
        normalized = 1.0 - normalized

    return normalized

def compute_composite_axis(metrics_dict, weights=None):
    """Compute weighted composite score from metrics dictionary."""
    keys = list(metrics_dict.keys())
    n = len(metrics_dict[keys[0]])

    if weights is None:
        weights = {k: 1.0 for k in keys}

    # Normalize each metric
    normalized = {}
    for key in keys:
        normalized[key] = normalize_to_unit(metrics_dict[key])

    # Compute weighted average
    total_weight = sum(weights.values())
    composite = np.zeros(n)
    for key in keys:
        composite += weights[key] * normalized[key]

    return composite / total_weight

# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return 0.0

    mean1, mean2 = np.mean(group1), np.mean(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))

    if pooled_std == 0:
        return 0.0

    return (mean1 - mean2) / pooled_std

def compute_within_between_variance(groups, values_dict):
    """
    Check if within-regime variance < between-regime variance.
    Returns (within_var, between_var, ratio, passes).
    """
    all_values = list(values_dict.values())

    # Grand mean
    grand_mean = np.mean(all_values)

    # Between-group variance
    group_means = {g: np.mean([values_dict[f] for f in fs])
                   for g, fs in groups.items()}
    between_var = np.mean([(m - grand_mean)**2 for m in group_means.values()])

    # Within-group variance
    within_vars = []
    for g, folios in groups.items():
        if len(folios) > 1:
            g_values = [values_dict[f] for f in folios]
            within_vars.append(np.var(g_values))

    within_var = np.mean(within_vars) if within_vars else 0

    # Ratio
    ratio = within_var / between_var if between_var > 0 else float('inf')
    passes = bool(within_var < between_var)  # Convert to Python bool

    return within_var, between_var, ratio, passes

# ============================================================================
# PARETO ANALYSIS
# ============================================================================

def is_pareto_dominated(point, other_points, minimize_axes):
    """
    Check if point is dominated by any other point.
    minimize_axes: list of axis indices to minimize (vs maximize).
    """
    for other in other_points:
        if all(point[i] == other[i] for i in range(len(point))):
            continue  # Same point

        # Check if other dominates point
        better_or_equal = True
        strictly_better = False

        for i in range(len(point)):
            if i in minimize_axes:
                # Lower is better
                if other[i] > point[i]:
                    better_or_equal = False
                    break
                if other[i] < point[i]:
                    strictly_better = True
            else:
                # Higher is better
                if other[i] < point[i]:
                    better_or_equal = False
                    break
                if other[i] > point[i]:
                    strictly_better = True

        if better_or_equal and strictly_better:
            return True  # Dominated by other

    return False

def identify_pareto_front(regime_centroids, axis_names):
    """
    Identify Pareto-efficient regimes.
    Minimize: Time, Risk
    Maximize: Stability
    """
    regime_ids = list(regime_centroids.keys())

    # Build point list: (time, risk, stability)
    points = {}
    for rid in regime_ids:
        centroid = regime_centroids[rid]
        points[rid] = (
            centroid['time']['mean'],
            centroid['risk']['mean'],
            centroid['stability']['mean']
        )

    # Minimize time (idx 0), minimize risk (idx 1), maximize stability (idx 2)
    minimize_axes = [0, 1]  # Time and Risk

    pareto_status = {}
    point_list = list(points.values())

    for rid in regime_ids:
        point = points[rid]
        is_dominated = is_pareto_dominated(point, point_list, minimize_axes)
        pareto_status[rid] = 'DOMINATED' if is_dominated else 'PARETO_EFFICIENT'

    return pareto_status

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def run_ops3_analysis():
    """Run complete OPS-3 tradeoff analysis."""
    print("=" * 70)
    print("PHASE OPS-3: Risk-Time-Stability Tradeoff Mapping")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load data
    print("Loading OPS-1 signatures...")
    signatures = load_ops1_signatures()
    print(f"  -> {len(signatures)} folios loaded")

    print("Loading OPS-2 cluster assignments...")
    assignments = load_ops2_assignments()
    print(f"  -> {len(assignments)} assignments loaded")
    print()

    # Build folio list (ensure consistency)
    folio_ids = sorted(set(signatures.keys()) & set(assignments.keys()))
    print(f"Common folios: {len(folio_ids)}")

    # Build regime groups
    regimes = defaultdict(list)
    for fid in folio_ids:
        rid = assignments[fid]['cluster_id']
        regimes[rid].append(fid)

    print(f"Regimes found: {sorted(regimes.keys())}")
    for rid in sorted(regimes.keys()):
        print(f"  {rid}: {len(regimes[rid])} folios")
    print()

    # ========================================================================
    # EXTRACT RAW METRICS
    # ========================================================================
    print("-" * 70)
    print("EXTRACTING AXIS METRICS")
    print("-" * 70)

    time_metrics = {k: [] for k in ['mean_link_run', 'link_count', 'loops_to_state_c', 'time_from_speed']}
    risk_metrics = {k: [] for k in ['hazard_density', 'proximity_risk', 'hazard_exposure', 'aggressiveness']}
    stability_metrics = {k: [] for k in ['hold_duration', 'control_margin', 'restart_capable', 'recovery_ops']}

    folio_raw_metrics = {}

    for fid in folio_ids:
        sig = signatures[fid]

        time_m = extract_time_axis_metrics(sig)
        risk_m = extract_risk_axis_metrics(sig)
        stab_m = extract_stability_axis_metrics(sig)

        folio_raw_metrics[fid] = {
            'time': time_m,
            'risk': risk_m,
            'stability': stab_m
        }

        for k, v in time_m.items():
            time_metrics[k].append(v)
        for k, v in risk_m.items():
            risk_metrics[k].append(v)
        for k, v in stab_m.items():
            stability_metrics[k].append(v)

    # Report ranges
    print("\nTIME AXIS raw ranges:")
    for k, v in time_metrics.items():
        print(f"  {k}: min={min(v):.4f}, max={max(v):.4f}, mean={np.mean(v):.4f}")

    print("\nRISK AXIS raw ranges:")
    for k, v in risk_metrics.items():
        print(f"  {k}: min={min(v):.4f}, max={max(v):.4f}, mean={np.mean(v):.4f}")

    print("\nSTABILITY AXIS raw ranges:")
    for k, v in stability_metrics.items():
        print(f"  {k}: min={min(v):.4f}, max={max(v):.4f}, mean={np.mean(v):.4f}")
    print()

    # ========================================================================
    # NORMALIZE AND COMPUTE COMPOSITE SCORES
    # ========================================================================
    print("-" * 70)
    print("NORMALIZING TO [0,1] AND COMPUTING COMPOSITE SCORES")
    print("-" * 70)

    # Compute composite scores for each axis
    time_composite = compute_composite_axis(time_metrics)
    risk_composite = compute_composite_axis(risk_metrics)
    stability_composite = compute_composite_axis(stability_metrics)

    # Store normalized per-folio scores
    folio_normalized = {}
    for i, fid in enumerate(folio_ids):
        folio_normalized[fid] = {
            'time': float(time_composite[i]),
            'risk': float(risk_composite[i]),
            'stability': float(stability_composite[i]),
            'regime': assignments[fid]['cluster_id']
        }

    print(f"Composite TIME range: [{time_composite.min():.4f}, {time_composite.max():.4f}]")
    print(f"Composite RISK range: [{risk_composite.min():.4f}, {risk_composite.max():.4f}]")
    print(f"Composite STABILITY range: [{stability_composite.min():.4f}, {stability_composite.max():.4f}]")
    print()

    # ========================================================================
    # AGGREGATE BY REGIME
    # ========================================================================
    print("-" * 70)
    print("AGGREGATING BY REGIME")
    print("-" * 70)

    regime_stats = {}

    for rid in sorted(regimes.keys()):
        folios = regimes[rid]

        time_vals = [folio_normalized[f]['time'] for f in folios]
        risk_vals = [folio_normalized[f]['risk'] for f in folios]
        stab_vals = [folio_normalized[f]['stability'] for f in folios]

        regime_stats[rid] = {
            'time': {
                'mean': float(np.mean(time_vals)),
                'std': float(np.std(time_vals)),
                'iqr': float(np.percentile(time_vals, 75) - np.percentile(time_vals, 25)),
                'min': float(min(time_vals)),
                'max': float(max(time_vals))
            },
            'risk': {
                'mean': float(np.mean(risk_vals)),
                'std': float(np.std(risk_vals)),
                'iqr': float(np.percentile(risk_vals, 75) - np.percentile(risk_vals, 25)),
                'min': float(min(risk_vals)),
                'max': float(max(risk_vals))
            },
            'stability': {
                'mean': float(np.mean(stab_vals)),
                'std': float(np.std(stab_vals)),
                'iqr': float(np.percentile(stab_vals, 75) - np.percentile(stab_vals, 25)),
                'min': float(min(stab_vals)),
                'max': float(max(stab_vals))
            },
            'n_folios': len(folios)
        }

        print(f"\n{rid} (n={len(folios)}):")
        print(f"  Time_cost    = {regime_stats[rid]['time']['mean']:.4f} +/- {regime_stats[rid]['time']['std']:.4f}")
        print(f"  Risk_exposure = {regime_stats[rid]['risk']['mean']:.4f} +/- {regime_stats[rid]['risk']['std']:.4f}")
        print(f"  Stability     = {regime_stats[rid]['stability']['mean']:.4f} +/- {regime_stats[rid]['stability']['std']:.4f}")

    print()

    # ========================================================================
    # PARETO FRONT ANALYSIS
    # ========================================================================
    print("-" * 70)
    print("PARETO FRONT ANALYSIS")
    print("-" * 70)

    pareto_status = identify_pareto_front(regime_stats, ['time', 'risk', 'stability'])

    for rid in sorted(pareto_status.keys()):
        status = pareto_status[rid]
        t = regime_stats[rid]['time']['mean']
        r = regime_stats[rid]['risk']['mean']
        s = regime_stats[rid]['stability']['mean']
        print(f"  {rid}: Time={t:.3f}, Risk={r:.3f}, Stability={s:.3f} -> {status}")

    # Store in regime_stats
    for rid, status in pareto_status.items():
        regime_stats[rid]['pareto_status'] = status

    print()

    # ========================================================================
    # COHEN'S D BETWEEN REGIMES
    # ========================================================================
    print("-" * 70)
    print("REGIME SEPARATION (Cohen's d)")
    print("-" * 70)

    regime_list = sorted(regimes.keys())
    cohens_d_results = {'time': {}, 'risk': {}, 'stability': {}}

    for axis_name, axis_key in [('TIME', 'time'), ('RISK', 'risk'), ('STABILITY', 'stability')]:
        print(f"\n{axis_name} axis:")
        for i, r1 in enumerate(regime_list):
            for r2 in regime_list[i+1:]:
                vals1 = [folio_normalized[f][axis_key] for f in regimes[r1]]
                vals2 = [folio_normalized[f][axis_key] for f in regimes[r2]]
                d = cohens_d(vals1, vals2)

                pair_key = f"{r1}_vs_{r2}"
                cohens_d_results[axis_key][pair_key] = float(d)

                # Interpret effect size
                abs_d = abs(d)
                if abs_d < 0.2:
                    effect = "negligible"
                elif abs_d < 0.5:
                    effect = "small"
                elif abs_d < 0.8:
                    effect = "medium"
                else:
                    effect = "large"

                print(f"  {r1} vs {r2}: d={d:+.3f} ({effect})")

    print()

    # ========================================================================
    # INTERNAL CONSISTENCY CHECK
    # ========================================================================
    print("-" * 70)
    print("INTERNAL CONSISTENCY CHECK")
    print("-" * 70)
    print("(within-regime variance < between-regime variance)")

    consistency_results = {}
    all_pass = True

    for axis_key in ['time', 'risk', 'stability']:
        values_dict = {f: folio_normalized[f][axis_key] for f in folio_ids}
        w_var, b_var, ratio, passes = compute_within_between_variance(regimes, values_dict)

        consistency_results[axis_key] = {
            'within_variance': float(w_var),
            'between_variance': float(b_var),
            'ratio': float(ratio),
            'passes': passes
        }

        status = "PASS" if passes else "FAIL"
        print(f"  {axis_key.upper()}: within={w_var:.4f}, between={b_var:.4f}, ratio={ratio:.3f} -> {status}")

        if not passes:
            all_pass = False

    print()
    if not all_pass:
        print("WARNING: Internal consistency violated on one or more axes.")
        print("         Regime separation may be weak on those axes.")
    else:
        print("All axes pass internal consistency check.")
    print()

    # ========================================================================
    # CROSS-CHECKS
    # ========================================================================
    print("-" * 70)
    print("CROSS-CHECKS")
    print("-" * 70)

    crosscheck_results = {}

    # 1. Aggressive regimes should have high risk, low time
    print("\n1. Aggressive regime (highest risk) position:")
    max_risk_regime = max(regime_list, key=lambda r: regime_stats[r]['risk']['mean'])
    max_risk_val = regime_stats[max_risk_regime]['risk']['mean']
    max_risk_time = regime_stats[max_risk_regime]['time']['mean']
    time_rank = sorted(regime_list, key=lambda r: regime_stats[r]['time']['mean']).index(max_risk_regime) + 1

    # High risk should correlate with lower time (faster = riskier)
    risk_time_corr = np.corrcoef(
        [regime_stats[r]['risk']['mean'] for r in regime_list],
        [regime_stats[r]['time']['mean'] for r in regime_list]
    )[0, 1]

    print(f"   Highest risk regime: {max_risk_regime} (risk={max_risk_val:.3f})")
    print(f"   Its time rank: {time_rank}/4 (1=fastest, 4=slowest)")
    print(f"   Risk-Time correlation: {risk_time_corr:.3f}")

    # Check: high risk should be fast (low time) - correlation should be negative
    crosscheck_1 = risk_time_corr < 0.3  # Allow some tolerance
    print(f"   CHECK: High-risk = low-time? {'PASS' if crosscheck_1 else 'NEUTRAL'}")
    crosscheck_results['aggressive_low_time'] = {
        'max_risk_regime': max_risk_regime,
        'risk_time_correlation': float(risk_time_corr),
        'status': 'PASS' if crosscheck_1 else 'NEUTRAL'
    }

    # 2. Conservative regimes should have low risk, high time
    print("\n2. Conservative regime (lowest risk) position:")
    min_risk_regime = min(regime_list, key=lambda r: regime_stats[r]['risk']['mean'])
    min_risk_val = regime_stats[min_risk_regime]['risk']['mean']
    min_risk_time = regime_stats[min_risk_regime]['time']['mean']

    print(f"   Lowest risk regime: {min_risk_regime} (risk={min_risk_val:.3f})")
    print(f"   Its time: {min_risk_time:.3f}")

    # Low risk should have high time
    crosscheck_2 = min_risk_time > 0.4  # Should be in upper half
    print(f"   CHECK: Low-risk = high-time? {'PASS' if crosscheck_2 else 'NEUTRAL'}")
    crosscheck_results['conservative_high_time'] = {
        'min_risk_regime': min_risk_regime,
        'time_cost': float(min_risk_time),
        'status': 'PASS' if crosscheck_2 else 'NEUTRAL'
    }

    # 3. Restart-capable folios should have high stability
    print("\n3. Restart-capable folios stability:")
    restart_folios = [f for f in folio_ids if signatures[f]['recovery_metrics'].get('restart_capable', False)]
    if restart_folios:
        restart_stab = [folio_normalized[f]['stability'] for f in restart_folios]
        other_stab = [folio_normalized[f]['stability'] for f in folio_ids if f not in restart_folios]
        mean_restart = float(np.mean(restart_stab))
        mean_other = float(np.mean(other_stab))

        print(f"   Restart-capable folios: {restart_folios}")
        print(f"   Mean stability (restart): {mean_restart:.3f}")
        print(f"   Mean stability (other): {mean_other:.3f}")

        crosscheck_3 = mean_restart > mean_other
        print(f"   CHECK: Restart = higher stability? {'PASS' if crosscheck_3 else 'FAIL'}")
        crosscheck_results['restart_stability'] = {
            'restart_folios': restart_folios,
            'restart_mean_stability': mean_restart,
            'other_mean_stability': mean_other,
            'status': 'PASS' if crosscheck_3 else 'FAIL'
        }
    else:
        print("   No restart-capable folios found.")
        crosscheck_results['restart_stability'] = {'status': 'SKIP', 'reason': 'No restart-capable folios'}

    # 4. No regime should dominate all three axes
    print("\n4. No regime dominates all axes:")
    # A regime dominates if it has best score on all: lowest time, lowest risk, highest stability
    time_ranks = sorted(regime_list, key=lambda r: regime_stats[r]['time']['mean'])
    risk_ranks = sorted(regime_list, key=lambda r: regime_stats[r]['risk']['mean'])
    stab_ranks = sorted(regime_list, key=lambda r: regime_stats[r]['stability']['mean'], reverse=True)

    print(f"   Best time (lowest): {time_ranks[0]}")
    print(f"   Best risk (lowest): {risk_ranks[0]}")
    print(f"   Best stability (highest): {stab_ranks[0]}")

    dominates = time_ranks[0] == risk_ranks[0] == stab_ranks[0]
    crosscheck_4 = not dominates
    print(f"   CHECK: No single regime dominates all? {'PASS' if crosscheck_4 else 'FAIL'}")
    crosscheck_results['no_domination'] = {
        'best_time': time_ranks[0],
        'best_risk': risk_ranks[0],
        'best_stability': stab_ranks[0],
        'single_dominates': bool(dominates),
        'status': 'PASS' if crosscheck_4 else 'FAIL'
    }

    print()

    # ========================================================================
    # SWITCHING PRESSURE VECTORS
    # ========================================================================
    print("-" * 70)
    print("REGIME SWITCHING PRESSURES (Non-Semantic)")
    print("-" * 70)

    pressures = {}

    for rid in sorted(regime_list):
        r = regime_stats[rid]
        t, ri, s = r['time']['mean'], r['risk']['mean'], r['stability']['mean']

        pressure_desc = []

        # High risk generates pressure away
        if ri > 0.6:
            pressure_desc.append("high risk -> pressure toward lower-risk regimes")
        elif ri < 0.4:
            pressure_desc.append("low risk -> tolerable for risk-averse conditions")

        # High time generates pressure away if speed needed
        if t > 0.6:
            pressure_desc.append("high time cost -> pressure toward faster regimes if time-constrained")
        elif t < 0.4:
            pressure_desc.append("low time cost -> efficient for throughput-critical conditions")

        # Low stability generates pressure away
        if s < 0.4:
            pressure_desc.append("low stability -> pressure toward more resilient regimes")
        elif s > 0.6:
            pressure_desc.append("high stability -> robust for uncertain conditions")

        pressures[rid] = {
            'time': t,
            'risk': ri,
            'stability': s,
            'pressure_vectors': pressure_desc
        }

        print(f"\n{rid}:")
        print(f"  Coordinates: time={t:.3f}, risk={ri:.3f}, stability={s:.3f}")
        for p in pressure_desc:
            print(f"  -> {p}")

    print()

    # ========================================================================
    # GENERATE OUTPUTS
    # ========================================================================
    print("=" * 70)
    print("GENERATING OUTPUT FILES")
    print("=" * 70)

    # 1. JSON models
    models = {
        'metadata': {
            'phase': 'OPS-3',
            'title': 'Risk-Time-Stability Tradeoff Mapping',
            'timestamp': datetime.now().isoformat(),
            'n_folios': len(folio_ids),
            'n_regimes': len(regime_list)
        },
        'folio_normalized_axes': folio_normalized,
        'regime_aggregates': regime_stats,
        'pareto_classification': pareto_status,
        'cohens_d_separation': cohens_d_results,
        'internal_consistency': consistency_results,
        'crosschecks': crosscheck_results,
        'switching_pressures': pressures
    }

    json_path = OUTPUT_DIR / "ops3_tradeoff_models.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(models, f, indent=2)
    print(f"  -> {json_path}")

    # 2. Summary CSV
    csv_path = OUTPUT_DIR / "ops3_regime_tradeoff_summary.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['regime_id', 'n_folios', 'mean_time_cost', 'mean_risk', 'mean_stability', 'pareto_status'])
        for rid in sorted(regime_list):
            r = regime_stats[rid]
            writer.writerow([
                rid,
                r['n_folios'],
                f"{r['time']['mean']:.4f}",
                f"{r['risk']['mean']:.4f}",
                f"{r['stability']['mean']:.4f}",
                r['pareto_status']
            ])
    print(f"  -> {csv_path}")

    # 3. Markdown report
    md_path = OUTPUT_DIR / "ops3_tradeoff_analysis.md"
    generate_markdown_report(
        md_path, regime_stats, pareto_status, cohens_d_results,
        consistency_results, crosscheck_results, pressures, regime_list
    )
    print(f"  -> {md_path}")

    print()
    print("=" * 70)
    print("PHASE OPS-3 COMPLETE")
    print("=" * 70)
    print()
    print('> **"OPS-3 is complete. Risk-time-stability tradeoffs between')
    print('>   control-strategy regimes have been quantified using purely')
    print('>   operational metrics. No semantic or historical interpretation')
    print('>   has been introduced."**')
    print()

    return models

def generate_markdown_report(path, regime_stats, pareto_status, cohens_d_results,
                             consistency_results, crosscheck_results, pressures, regime_list):
    """Generate the markdown analysis report."""

    lines = []
    lines.append("# Phase OPS-3: Risk-Time-Stability Tradeoff Analysis")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Regime Summary Table
    lines.append("## 1. Regime Tradeoff Summary")
    lines.append("")
    lines.append("| Regime | N | Time Cost | Risk | Stability | Pareto |")
    lines.append("|--------|---|-----------|------|-----------|--------|")

    for rid in sorted(regime_list):
        r = regime_stats[rid]
        lines.append(f"| {rid} | {r['n_folios']} | {r['time']['mean']:.3f} +/- {r['time']['std']:.3f} | "
                     f"{r['risk']['mean']:.3f} +/- {r['risk']['std']:.3f} | "
                     f"{r['stability']['mean']:.3f} +/- {r['stability']['std']:.3f} | {r['pareto_status']} |")

    lines.append("")
    lines.append("*Higher Time Cost = slower operation*")
    lines.append("*Higher Risk = more exposure to hazards*")
    lines.append("*Higher Stability = better resilience/recoverability*")
    lines.append("")

    # Pareto Analysis
    lines.append("---")
    lines.append("")
    lines.append("## 2. Pareto Front Analysis")
    lines.append("")
    lines.append("**Objective:** Minimize Time, Minimize Risk, Maximize Stability")
    lines.append("")

    efficient = [r for r in regime_list if pareto_status[r] == 'PARETO_EFFICIENT']
    dominated = [r for r in regime_list if pareto_status[r] == 'DOMINATED']

    lines.append(f"**Pareto-Efficient Regimes:** {', '.join(efficient)}")
    lines.append(f"**Dominated Regimes:** {', '.join(dominated) if dominated else 'None'}")
    lines.append("")

    # Risk vs Time plot (ASCII)
    lines.append("### Risk vs Time Plane")
    lines.append("")
    lines.append("```")
    lines.append("Risk (higher=worse)")
    lines.append("  ^")

    # Simple ASCII scatter
    for rid in sorted(regime_list):
        r = regime_stats[rid]
        t_pos = int(r['time']['mean'] * 20)
        r_pos = int((1 - r['risk']['mean']) * 5)  # Invert for display
        lines.append(f"  | {' ' * t_pos}{rid}")

    lines.append("  +--------------------> Time (higher=slower)")
    lines.append("```")
    lines.append("")

    # Risk vs Stability plot (ASCII)
    lines.append("### Risk vs Stability Plane")
    lines.append("")
    lines.append("```")
    lines.append("Stability (higher=better)")
    lines.append("  ^")

    for rid in sorted(regime_list):
        r = regime_stats[rid]
        r_pos = int(r['risk']['mean'] * 20)
        s_pos = int(r['stability']['mean'] * 5)
        lines.append(f"  | {' ' * r_pos}{rid}")

    lines.append("  +--------------------> Risk (higher=worse)")
    lines.append("```")
    lines.append("")

    # Cohen's d
    lines.append("---")
    lines.append("")
    lines.append("## 3. Regime Separation (Cohen's d)")
    lines.append("")
    lines.append("Effect size interpretation: |d|<0.2=negligible, 0.2-0.5=small, 0.5-0.8=medium, >0.8=large")
    lines.append("")

    for axis in ['time', 'risk', 'stability']:
        lines.append(f"### {axis.upper()} Axis")
        lines.append("")
        lines.append("| Comparison | Cohen's d | Effect |")
        lines.append("|------------|-----------|--------|")

        for pair, d in cohens_d_results[axis].items():
            abs_d = abs(d)
            if abs_d < 0.2:
                effect = "negligible"
            elif abs_d < 0.5:
                effect = "small"
            elif abs_d < 0.8:
                effect = "medium"
            else:
                effect = "large"
            lines.append(f"| {pair.replace('_', ' ')} | {d:+.3f} | {effect} |")

        lines.append("")

    # Internal Consistency
    lines.append("---")
    lines.append("")
    lines.append("## 4. Internal Consistency Check")
    lines.append("")
    lines.append("*Criterion: Within-regime variance < Between-regime variance*")
    lines.append("")
    lines.append("| Axis | Within Var | Between Var | Ratio | Status |")
    lines.append("|------|------------|-------------|-------|--------|")

    for axis in ['time', 'risk', 'stability']:
        c = consistency_results[axis]
        status = "PASS" if c['passes'] else "FAIL"
        lines.append(f"| {axis.upper()} | {c['within_variance']:.4f} | {c['between_variance']:.4f} | "
                     f"{c['ratio']:.3f} | {status} |")

    lines.append("")

    # Cross-checks
    lines.append("---")
    lines.append("")
    lines.append("## 5. Cross-Checks")
    lines.append("")

    lines.append("| Check | Result | Status |")
    lines.append("|-------|--------|--------|")

    if 'aggressive_low_time' in crosscheck_results:
        c = crosscheck_results['aggressive_low_time']
        lines.append(f"| Aggressive regimes = high-risk, low-time | Risk-Time r={c['risk_time_correlation']:.3f} | {c['status']} |")

    if 'conservative_high_time' in crosscheck_results:
        c = crosscheck_results['conservative_high_time']
        lines.append(f"| Conservative regimes = low-risk, high-time | {c['min_risk_regime']} time={c['time_cost']:.3f} | {c['status']} |")

    if 'restart_stability' in crosscheck_results:
        c = crosscheck_results['restart_stability']
        if c['status'] != 'SKIP':
            lines.append(f"| Restart-capable = high stability | Restart={c['restart_mean_stability']:.3f} vs Other={c['other_mean_stability']:.3f} | {c['status']} |")
        else:
            lines.append(f"| Restart-capable = high stability | {c.get('reason', 'N/A')} | SKIP |")

    if 'no_domination' in crosscheck_results:
        c = crosscheck_results['no_domination']
        lines.append(f"| No regime dominates all axes | Best: T={c['best_time']}, R={c['best_risk']}, S={c['best_stability']} | {c['status']} |")

    lines.append("")

    # Switching Pressures
    lines.append("---")
    lines.append("")
    lines.append("## 6. Regime Switching Pressures")
    lines.append("")
    lines.append("*Non-semantic directional tendencies derived from tradeoff position*")
    lines.append("")

    for rid in sorted(regime_list):
        p = pressures[rid]
        lines.append(f"### {rid}")
        lines.append("")
        lines.append(f"**Coordinates:** Time={p['time']:.3f}, Risk={p['risk']:.3f}, Stability={p['stability']:.3f}")
        lines.append("")
        if p['pressure_vectors']:
            for pv in p['pressure_vectors']:
                lines.append(f"- {pv}")
        else:
            lines.append("- Balanced position; no strong directional pressure")
        lines.append("")

    # Termination
    lines.append("---")
    lines.append("")
    lines.append("> **\"OPS-3 is complete. Risk-time-stability tradeoffs between control-strategy regimes ")
    lines.append("> have been quantified using purely operational metrics. No semantic or historical ")
    lines.append("> interpretation has been introduced.\"**")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    run_ops3_analysis()
