"""
T2: Discretization Verdict
===========================
Phase: CATEGORICAL_DISCRETIZATION_TEST

Compares all 6 discretization strategies against the continuous baseline
(THERMAL_PLANT_SIMULATION) and random null. Renders verdict based on
direction-of-movement, not pass/fail thresholds (per expert adjustment A).

Output: t2_verdict.json
"""

import json
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'
THERMAL_RESULTS = Path(__file__).parent.parent.parent / 'THERMAL_PLANT_SIMULATION' / 'results'

# Continuous baseline from THERMAL_PLANT_SIMULATION T2/T3
BASELINE = {
    'spectral_gap': 0.000,
    'hub_mass': 0.558,
    'n_forbidden': 0,
    'alternation_rate': 0.462,
    'asymmetry': -0.002,
    'post_overshoot_cool_rate': 0.215,
    'heat_run_median': 2.0,
    'cool_run_median': 2.0,
    'buffer_rate': 0.000,
}

# Voynich targets (for reference — NOT used for scoring)
VOYNICH = {
    'spectral_gap': 0.894,
    'hub_mass': 0.68,
    'n_forbidden': 17,
    'alternation_rate': 0.549,
    'asymmetry': 0.043,
    'post_overshoot_cool_rate': 0.752,
    'heat_run_median': 1.0,
    'cool_run_median': 1.0,
    'buffer_rate': 0.0012,
}


def compute_movement(strategy_summary, baseline, voynich):
    """Compute direction-of-movement for each metric.

    Returns dict of {metric: {value, baseline, voynich, delta, toward_voynich}}.
    """
    movements = {}
    for metric in baseline:
        val = strategy_summary.get(metric, {}).get('median', 0)
        base = baseline[metric]
        target = voynich[metric]

        delta = val - base
        # "toward voynich" = delta moves value closer to target
        dist_base = abs(base - target)
        dist_val = abs(val - target)
        toward = dist_val < dist_base

        movements[metric] = {
            'value': float(val),
            'baseline': float(base),
            'voynich': float(target),
            'delta': float(delta),
            'toward_voynich': bool(toward),
            'pct_gap_closed': float((dist_base - dist_val) / dist_base * 100)
            if dist_base > 1e-10 else 0.0,
        }
    return movements


def main():
    # Load T1 results
    with open(RESULTS_DIR / 't1_discretization_scoring.json') as f:
        t1 = json.load(f)

    strategies = t1['strategies']
    physical = ['lane_temp', 'operational', 'gmm_bic', 't_bins', 'q_phase']
    null_name = 'random'

    # Compute direction-of-movement for each strategy
    movements = {}
    for name, data in strategies.items():
        movements[name] = compute_movement(data['summary'], BASELINE, VOYNICH)

    # Count metrics moving toward Voynich per strategy
    toward_counts = {}
    for name, mvmt in movements.items():
        toward_counts[name] = sum(
            1 for m in mvmt.values() if m['toward_voynich'])

    # Rank strategies
    ranking = sorted(toward_counts.items(), key=lambda x: -x[1])

    # Best physical strategy
    best_physical_name = max(
        physical, key=lambda n: toward_counts.get(n, 0))
    best_physical_toward = toward_counts[best_physical_name]
    null_toward = toward_counts[null_name]

    # Verdict
    n_metrics = len(BASELINE)
    if null_toward >= n_metrics - 1:
        verdict = 'DISCRETIZATION_TRIVIAL'
        detail = ('Random binning matches most metrics — discretization test '
                  'lacks discriminative power.')
    elif best_physical_toward >= 7 and best_physical_toward > null_toward + 2:
        verdict = 'DISCRETIZATION_SUFFICIENT'
        detail = ('Physical discretization moves most metrics toward Voynich. '
                  'Categorical encoding bridges the topology gap.')
    elif best_physical_toward >= 5 and best_physical_toward > null_toward:
        verdict = 'PARTIAL_BRIDGE'
        detail = ('Discretization improves some metrics but not enough. '
                  'Some Voynich features require additional structure.')
    else:
        verdict = 'DISCRETIZATION_INSUFFICIENT'
        detail = ('Categorical discretization does not significantly improve '
                  'over continuous baseline or random null. Voynich topology '
                  'requires engineered symbolic structure beyond categorization.')

    # Forbidden transition analysis
    forbidden_analysis = {}
    for name in strategies:
        s = strategies[name]['summary']
        forb_median = s['n_forbidden']['median']
        forbidden_analysis[name] = {
            'median_forbidden': float(forb_median),
            'above_random': float(forb_median - strategies[null_name][
                'summary']['n_forbidden']['median']),
        }
        if 'legality' in s:
            leg = s['legality']
            forbidden_analysis[name]['legality'] = {
                'defined_rules': leg['n_defined_forbidden'],
                'truly_absent': float(leg['median_truly_absent']),
                'violation_rate': float(leg['median_violation_rate']),
            }

    # Per-metric comparison table
    metric_table = {}
    for metric in BASELINE:
        row = {
            'baseline': BASELINE[metric],
            'voynich': VOYNICH[metric],
        }
        for name in strategies:
            val = strategies[name]['summary'].get(metric, {}).get('median', 0)
            row[name] = float(val)
        metric_table[metric] = row

    output = {
        'verdict': verdict,
        'verdict_detail': detail,
        'ranking': [{'strategy': name, 'metrics_toward_voynich': count}
                    for name, count in ranking],
        'best_physical': {
            'strategy': best_physical_name,
            'toward_count': best_physical_toward,
        },
        'null_toward_count': null_toward,
        'movements': movements,
        'forbidden_analysis': forbidden_analysis,
        'metric_table': metric_table,
    }

    out_path = RESULTS_DIR / 't2_verdict.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    # Print
    print(f"\n{'='*70}")
    print(f"T2 CATEGORICAL DISCRETIZATION VERDICT")
    print(f"{'='*70}")
    print(f"")
    print(f"VERDICT: {verdict}")
    print(f"  {detail}")
    print(f"")
    print(f"STRATEGY RANKING (metrics moving toward Voynich / {n_metrics}):")
    for name, count in ranking:
        marker = ' <-- best physical' if name == best_physical_name else ''
        marker = ' <-- null' if name == null_name else marker
        print(f"  {name:<16s}: {count}/{n_metrics}{marker}")
    print(f"")

    # Direction-of-movement table for best physical
    print(f"DIRECTION OF MOVEMENT ({best_physical_name} vs continuous baseline):")
    print(f"{'Metric':<28s} {'Baseline':>8s} {'Strategy':>8s} "
          f"{'Voynich':>8s} {'Delta':>8s} {'Toward?':>8s} {'%Gap':>7s}")
    print(f"{'-'*28} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*7}")
    for metric, mvmt in movements[best_physical_name].items():
        arrow = 'YES' if mvmt['toward_voynich'] else 'no'
        print(f"  {metric:<26s} {mvmt['baseline']:>8.3f} {mvmt['value']:>8.3f} "
              f"{mvmt['voynich']:>8.3f} {mvmt['delta']:>+8.3f} "
              f"{arrow:>8s} {mvmt['pct_gap_closed']:>6.1f}%")
    print(f"")

    # Forbidden transition analysis
    print(f"FORBIDDEN TRANSITION ANALYSIS:")
    print(f"  {'Strategy':<16s} {'Null-Cal':>8s} {'Legality':>10s} "
          f"{'Absent':>8s} {'ViolRate':>10s}")
    print(f"  {'-'*16} {'-'*8} {'-'*10} {'-'*8} {'-'*10}")
    for name in ['lane_temp', 'operational', 'q_phase', 'gmm_bic',
                  't_bins', 'random']:
        fa = forbidden_analysis[name]
        leg = fa.get('legality', {})
        defined = leg.get('defined_rules', '-')
        absent = leg.get('truly_absent', '-')
        viol = leg.get('violation_rate', '-')
        defined_str = f"{defined}" if isinstance(defined, int) else '-'
        absent_str = f"{absent:.0f}" if isinstance(absent, float) else '-'
        viol_str = f"{viol:.4f}" if isinstance(viol, float) else '-'
        print(f"  {name:<16s} {fa['median_forbidden']:>8.0f} "
              f"{defined_str:>10s} {absent_str:>8s} {viol_str:>10s}")
    print(f"  (Voynich: 17 forbidden transitions)")
    print(f"")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
