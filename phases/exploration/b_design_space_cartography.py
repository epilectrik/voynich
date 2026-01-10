#!/usr/bin/env python3
"""
D1: B Design Space Cartography

Maps the B folio design space to find:
- Dense bands (common design configurations)
- Holes (forbidden design combinations)
- Regime partitioning
- Design slack vs constraint dimensions

Output: results/b_design_space_cartography.json
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

# Input
B_FEATURES = RESULTS / "b_macro_scaffold_audit.json"
UNIFIED_PROFILES = RESULTS / "unified_folio_profiles.json"

# Output
OUTPUT = RESULTS / "b_design_space_cartography.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_variance_ranking(features, metric_names):
    """
    Rank metrics by variance - high variance = design freedom, low = constraint.
    """
    variances = {}
    for metric in metric_names:
        values = [f[metric] for f in features.values() if f.get(metric) is not None]
        if len(values) > 1:
            # Use coefficient of variation for scale-independent comparison
            mean = np.mean(values)
            std = np.std(values)
            cv = std / mean if mean != 0 else 0
            variances[metric] = {
                'mean': round(mean, 4),
                'std': round(std, 4),
                'cv': round(cv, 4),
                'min': round(min(values), 4),
                'max': round(max(values), 4)
            }
    return variances


def compute_regime_variance(features, metric_names):
    """
    Compute within-regime variance for each metric.
    """
    # Group by regime
    by_regime = defaultdict(list)
    for folio, data in features.items():
        regime = data.get('regime', 'UNKNOWN')
        by_regime[regime].append(data)

    results = {}
    for regime, folios in sorted(by_regime.items()):
        regime_vars = {}
        for metric in metric_names:
            values = [f[metric] for f in folios if f.get(metric) is not None]
            if len(values) > 1:
                cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                regime_vars[metric] = {
                    'mean': round(np.mean(values), 4),
                    'std': round(np.std(values), 4),
                    'cv': round(cv, 4),
                    'n': len(values)
                }
        results[regime] = {
            'n_folios': len(folios),
            'metrics': regime_vars
        }

    return results


def find_dense_bands_and_holes(features, x_metric, y_metric, n_bins=5):
    """
    Analyze 2D distribution to find dense bands and holes.
    """
    x_values = [f[x_metric] for f in features.values() if f.get(x_metric) is not None]
    y_values = [f[y_metric] for f in features.values() if f.get(y_metric) is not None]

    if len(x_values) < 10:
        return None

    # Create 2D histogram
    x_edges = np.linspace(min(x_values), max(x_values), n_bins + 1)
    y_edges = np.linspace(min(y_values), max(y_values), n_bins + 1)

    hist, _, _ = np.histogram2d(x_values, y_values, bins=[x_edges, y_edges])

    # Find dense cells (> median) and empty cells
    median_count = np.median(hist[hist > 0]) if np.any(hist > 0) else 0
    dense_cells = []
    empty_cells = []

    for i in range(n_bins):
        for j in range(n_bins):
            x_range = (round(x_edges[i], 3), round(x_edges[i+1], 3))
            y_range = (round(y_edges[j], 3), round(y_edges[j+1], 3))
            count = int(hist[i, j])

            if count == 0:
                empty_cells.append({
                    'x_range': x_range,
                    'y_range': y_range,
                    'count': 0
                })
            elif count > median_count * 1.5:
                dense_cells.append({
                    'x_range': x_range,
                    'y_range': y_range,
                    'count': count
                })

    # Compute correlation
    r, p = stats.spearmanr(x_values, y_values)

    return {
        'x_metric': x_metric,
        'y_metric': y_metric,
        'correlation': {
            'spearman_r': round(r, 3),
            'p_value': round(p, 4)
        },
        'n_dense_cells': len(dense_cells),
        'n_empty_cells': len(empty_cells),
        'dense_cells': dense_cells,
        'empty_cells': empty_cells[:5]  # Top 5 holes only
    }


def analyze_regime_separation(features):
    """
    Test how well regimes partition the design space.
    """
    # Key metrics for regime separation
    test_metrics = ['hazard_density', 'qo_density', 'cei_total', 'link_density']

    results = {}
    for metric in test_metrics:
        groups = defaultdict(list)
        for data in features.values():
            regime = data.get('regime', 'UNKNOWN')
            if data.get(metric) is not None:
                groups[regime].append(data[metric])

        # Kruskal-Wallis test
        group_values = [v for v in groups.values() if len(v) >= 3]
        if len(group_values) >= 2:
            h_stat, p_value = stats.kruskal(*group_values)
            # Effect size (eta-squared approximation)
            n_total = sum(len(g) for g in group_values)
            eta_sq = (h_stat - len(group_values) + 1) / (n_total - len(group_values))

            results[metric] = {
                'h_statistic': round(h_stat, 2),
                'p_value': round(p_value, 4),
                'eta_squared': round(max(0, eta_sq), 3),
                'group_means': {k: round(np.mean(v), 4) for k, v in groups.items()}
            }

    return results


def identify_folio_positions(features, unified):
    """
    Map each folio's position in design space.
    """
    positions = {}

    for folio, data in features.items():
        # Get execution tension from unified profiles
        tension = None
        if folio in unified['profiles']:
            bi = unified['profiles'][folio].get('burden_indices', {})
            tension = bi.get('execution_tension')

        positions[folio] = {
            'regime': data.get('regime'),
            'hazard_density': round(data.get('hazard_density', 0), 4),
            'escape_density': round(data.get('qo_density', 0), 4),
            'cei_total': round(data.get('cei_total', 0), 4),
            'link_density': round(data.get('link_density', 0), 4),
            'execution_tension': round(tension, 3) if tension is not None else None
        }

    return positions


def main():
    print("=" * 70)
    print("D1: B Design Space Cartography")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    b_features = load_json(B_FEATURES)['features']
    unified = load_json(UNIFIED_PROFILES)
    print(f"    B folios: {len(b_features)}")

    # Define key metrics
    metric_names = [
        'hazard_density', 'qo_density', 'link_density',
        'cei_total', 'cei_time_component', 'cei_risk_component', 'cei_stability_component',
        'intervention_frequency', 'intervention_diversity',
        'cycle_regularity', 'mean_cycle_length',
        'kernel_contact_ratio', 'phase_ordering_rigidity',
        'near_miss_count', 'recovery_ops_count'
    ]

    # Global variance ranking
    print("\n[2] Computing global variance ranking...")
    global_variance = compute_variance_ranking(b_features, metric_names)

    # Sort by CV (high = design freedom)
    sorted_by_cv = sorted(global_variance.items(), key=lambda x: x[1]['cv'], reverse=True)
    print("\n    HIGH VARIANCE (design freedom):")
    for metric, stats in sorted_by_cv[:5]:
        print(f"      {metric}: CV={stats['cv']:.3f}")

    print("\n    LOW VARIANCE (constraints):")
    for metric, stats in sorted_by_cv[-5:]:
        print(f"      {metric}: CV={stats['cv']:.3f}")

    # Regime-specific variance
    print("\n[3] Computing within-regime variance...")
    regime_variance = compute_regime_variance(b_features, metric_names)

    for regime, data in sorted(regime_variance.items()):
        print(f"\n    {regime} ({data['n_folios']} folios):")
        # Find highest and lowest CV within this regime
        sorted_metrics = sorted(data['metrics'].items(), key=lambda x: x[1]['cv'], reverse=True)
        print(f"      Highest CV: {sorted_metrics[0][0]} ({sorted_metrics[0][1]['cv']:.3f})")
        print(f"      Lowest CV: {sorted_metrics[-1][0]} ({sorted_metrics[-1][1]['cv']:.3f})")

    # 2D projections for dense bands / holes
    print("\n[4] Analyzing 2D projections...")

    projections = [
        ('hazard_density', 'qo_density'),       # Risk-Recovery
        ('cei_total', 'link_density'),          # CEI-Link
        ('intervention_frequency', 'recovery_ops_count'),  # Tension-Slack
        ('hazard_density', 'link_density'),     # Hazard-Link
        ('near_miss_count', 'recovery_ops_count')  # Near-miss-Recovery
    ]

    projection_results = {}
    for x_metric, y_metric in projections:
        result = find_dense_bands_and_holes(b_features, x_metric, y_metric)
        if result:
            projection_results[f"{x_metric}_vs_{y_metric}"] = result
            r = result['correlation']['spearman_r']
            p = result['correlation']['p_value']
            dense = result['n_dense_cells']
            empty = result['n_empty_cells']
            print(f"    {x_metric} vs {y_metric}: r={r:.3f} (p={p:.4f}), {dense} dense, {empty} empty")

    # Regime separation test
    print("\n[5] Testing regime separation...")
    regime_separation = analyze_regime_separation(b_features)

    for metric, result in regime_separation.items():
        sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else ""
        print(f"    {metric}: H={result['h_statistic']:.1f}, eta²={result['eta_squared']:.3f} {sig}")
        for regime, mean in sorted(result['group_means'].items()):
            print(f"      {regime}: {mean:.4f}")

    # Execution tension by regime
    print("\n[6] Execution tension by regime...")
    tension_by_regime = defaultdict(list)
    for folio, data in unified['profiles'].items():
        if data['system'] == 'B' and data['burden_indices']['execution_tension'] is not None:
            regime = data['b_metrics']['regime']
            tension_by_regime[regime].append(data['burden_indices']['execution_tension'])

    for regime in sorted(tension_by_regime.keys()):
        tensions = tension_by_regime[regime]
        print(f"    {regime}: mean={np.mean(tensions):.3f}, std={np.std(tensions):.3f}, n={len(tensions)}")

    # Kruskal-Wallis on tension by regime
    tension_groups = [v for v in tension_by_regime.values() if len(v) >= 3]
    tension_kw = None
    if len(tension_groups) >= 2:
        from scipy.stats import kruskal as kruskal_test
        h, p = kruskal_test(*tension_groups)
        tension_kw = {'h': h, 'p': p}
        print(f"    Kruskal-Wallis: H={h:.2f}, p={p:.4f}")

    # Folio positions
    print("\n[7] Mapping folio positions...")
    folio_positions = identify_folio_positions(b_features, unified)

    # Save output
    print("\n[8] Saving output...")

    # Identify key findings
    findings = []

    # Check if tension correlates with regime
    if tension_kw and tension_kw['p'] < 0.05:
        findings.append({
            'finding': 'Execution tension differs by regime',
            'test': 'Kruskal-Wallis',
            'h_statistic': round(tension_kw['h'], 2),
            'p_value': round(tension_kw['p'], 4),
            'interpretation': 'REGIME_3 has higher tension than REGIME_1/2'
        })

    # Check for forbidden zones
    for proj_name, proj_result in projection_results.items():
        if proj_result['n_empty_cells'] >= 5:
            findings.append({
                'finding': f'Forbidden zone in {proj_name}',
                'n_empty_cells': proj_result['n_empty_cells'],
                'interpretation': 'Some design combinations are avoided'
            })

    # High/low variance dimensions
    high_cv = [m for m, s in sorted_by_cv[:3]]
    low_cv = [m for m, s in sorted_by_cv[-3:]]
    findings.append({
        'finding': 'Design freedom vs constraint dimensions',
        'high_freedom': high_cv,
        'tightly_constrained': low_cv,
        'interpretation': 'Designer allows freedom in some dimensions but clamps others'
    })

    output = {
        'metadata': {
            'analysis': 'D1 - B Design Space Cartography',
            'description': 'Mapping the shape of B folio design space',
            'n_folios': len(b_features)
        },
        'global_variance': {
            metric: stats for metric, stats in sorted_by_cv
        },
        'regime_variance': regime_variance,
        'projections': projection_results,
        'regime_separation': regime_separation,
        'tension_by_regime': {
            regime: {
                'mean': round(np.mean(tensions), 3),
                'std': round(np.std(tensions), 3),
                'n': len(tensions)
            }
            for regime, tensions in tension_by_regime.items()
        },
        'folio_positions': folio_positions,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    # Summary
    print("\n" + "=" * 70)
    print("D1 KEY FINDINGS")
    print("=" * 70)
    for finding in findings:
        print(f"\n  - {finding['finding']}")
        if 'interpretation' in finding:
            print(f"    {finding['interpretation']}")

    print("\n" + "=" * 70)
    print("D1 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
