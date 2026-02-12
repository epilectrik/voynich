"""
T3: Voynich Fidelity Comparison
================================
Phase: THERMAL_PLANT_SIMULATION

Compares extracted automaton properties (from T2) against 10 Voynich
quantitative targets. Scores each of 100 parameterizations, reports
MEDIAN hit count and per-metric hit rates.

Output: t3_voynich_comparison.json
"""

import json
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ============================================================
# VOYNICH TARGETS (from validated constraints)
# ============================================================
TARGETS = {
    'state_count': {
        'description': 'Macro-state count 5-7 (C978: 6 states)',
        'test': lambda r: 5 <= r['optimal_k'] <= 7,
        'value': lambda r: r['optimal_k'],
        'voynich': '6 (range 5-7)',
    },
    'hub_mass': {
        'description': 'Hub state mass 60-70% (C978: S4=68%)',
        'test': lambda r: 0.60 <= r['hub_mass'] <= 0.70,
        'value': lambda r: r['hub_mass'],
        'voynich': '0.68 (range 0.60-0.70)',
    },
    'spectral_gap': {
        'description': 'Spectral gap > 0.80 (C978: 0.894)',
        'test': lambda r: r['spectral_gap'] > 0.80,
        'value': lambda r: r['spectral_gap'],
        'voynich': '0.894 (threshold >0.80)',
    },
    'alternation_rate': {
        'description': 'Lane alternation rate 50-60% (C643: 54.9%)',
        'test': lambda r: 0.50 <= r['lanes']['alternation_rate'] <= 0.60,
        'value': lambda r: r['lanes']['alternation_rate'],
        'voynich': '0.549 (range 0.50-0.60)',
    },
    'alternation_asymmetry': {
        'description': 'Heat->cool > cool->heat (C643: 57.8% vs 53.5%)',
        'test': lambda r: r['lanes']['heat_to_cool'] > r['lanes']['cool_to_heat'],
        'value': lambda r: r['lanes']['asymmetry'],
        'voynich': '+0.043 (heat_to_cool > cool_to_heat)',
    },
    'post_overshoot_cooling': {
        'description': 'Post-overshoot cooling bias > 70% (C645: 75.2%)',
        'test': lambda r: r['lanes']['post_overshoot_cool_rate'] > 0.70,
        'value': lambda r: r['lanes']['post_overshoot_cool_rate'],
        'voynich': '0.752 (threshold >0.70)',
    },
    'forbidden_count': {
        'description': 'Forbidden pair count 10-25 (C109/C783: 17)',
        'test': lambda r: 10 <= r['n_forbidden'] <= 25,
        'value': lambda r: r['n_forbidden'],
        'voynich': '17 (range 10-25)',
    },
    'buffer_rate': {
        'description': 'Safety buffer rate < 1% (C997: 0.12%)',
        'test': lambda r: r['safety_buffers']['buffer_rate'] < 0.01,
        'value': lambda r: r['safety_buffers']['buffer_rate'],
        'voynich': '0.0012 (threshold <0.01)',
    },
    'oscillation_variation': {
        'description': 'Oscillation rate variation > 20pp across params (C650: 33-61%)',
        # This is scored at aggregate level, not per-parameterization
        'test': None,  # handled separately
        'value': lambda r: r['lanes']['alternation_rate'],
        'voynich': '28pp spread (threshold >20pp)',
    },
    'run_length_median': {
        'description': 'Run-length median = 1 for both lanes (C643)',
        'test': lambda r: (r['lanes']['heat_run_median'] == 1.0
                          and r['lanes']['cool_run_median'] == 1.0),
        'value': lambda r: (r['lanes']['heat_run_median'],
                           r['lanes']['cool_run_median']),
        'voynich': '(1.0, 1.0)',
    },
}


def score_parameterization(result):
    """Score a single parameterization against per-param targets."""
    hits = {}
    for name, target in TARGETS.items():
        if target['test'] is None:
            continue  # aggregate-level target
        try:
            hit = bool(target['test'](result))
            val = target['value'](result)
        except (KeyError, ZeroDivisionError):
            hit = False
            val = None
        hits[name] = {'hit': hit, 'value': val}
    return hits


def main():
    # Load T2 results
    t2_path = RESULTS_DIR / 't2_automaton_extraction.json'
    with open(t2_path) as f:
        t2_data = json.load(f)

    results = t2_data['parameterizations']
    n = len(results)

    # Score each parameterization
    all_scores = []
    for r in results:
        scores = score_parameterization(r)
        hit_count = sum(1 for s in scores.values() if s['hit'])
        all_scores.append({
            'param_id': r['param_id'],
            'hits': scores,
            'hit_count': hit_count,
            'total_targets': len(scores),
        })

    # Aggregate: oscillation variation (across all parameterizations)
    alt_rates = [r['lanes']['alternation_rate'] for r in results]
    alt_spread = max(alt_rates) - min(alt_rates)
    oscillation_variation_hit = alt_spread > 0.20

    # Per-metric hit rates
    metric_hit_rates = {}
    for name in TARGETS:
        if TARGETS[name]['test'] is None:
            metric_hit_rates[name] = {
                'hit_rate': 1.0 if oscillation_variation_hit else 0.0,
                'hit': oscillation_variation_hit,
                'detail': f'spread = {alt_spread:.3f} (threshold > 0.20)',
            }
            continue

        hits = sum(1 for s in all_scores if s['hits'].get(name, {}).get('hit', False))
        vals = [s['hits'].get(name, {}).get('value') for s in all_scores
                if s['hits'].get(name, {}).get('value') is not None]

        # For tuple values (run_length_median), extract first element for stats
        if vals and isinstance(vals[0], (list, tuple)):
            val_summary = {
                'heat_median': float(np.median([v[0] for v in vals])),
                'cool_median': float(np.median([v[1] for v in vals])),
            }
        elif vals:
            val_summary = {
                'mean': float(np.mean(vals)),
                'median': float(np.median(vals)),
                'std': float(np.std(vals)),
            }
        else:
            val_summary = {}

        metric_hit_rates[name] = {
            'hit_rate': float(hits / n),
            'n_hits': hits,
            'n_total': n,
            'simulated_stats': val_summary,
            'voynich_target': TARGETS[name]['voynich'],
        }

    # Hit count distribution
    hit_counts = [s['hit_count'] for s in all_scores]
    # Add oscillation_variation hit to each score's count
    if oscillation_variation_hit:
        hit_counts = [h + 1 for h in hit_counts]

    median_hits = float(np.median(hit_counts))
    mean_hits = float(np.mean(hit_counts))
    max_possible = len([t for t in TARGETS.values() if t['test'] is not None]) + 1

    # Verdict
    if median_hits >= 8:
        verdict = 'STRUCTURAL_CONVERGENCE'
        verdict_detail = ('Reflux-class thermal control necessarily produces '
                         'Voynich-like macro-topology.')
    elif median_hits >= 5:
        verdict = 'PARTIAL_COMPATIBILITY'
        verdict_detail = ('Some features are physics-forced, others require '
                         'additional structure or convention.')
    else:
        verdict = 'STRUCTURAL_DIVERGENCE'
        verdict_detail = ('Minimal reflux model alone does not reproduce '
                         'Voynich grammar topology. See per-metric analysis '
                         'for diagnostic detail.')

    # Classify metrics by robustness
    robust = []     # >80% hit rate
    moderate = []   # 20-80%
    fragile = []    # <20%
    for name, info in metric_hit_rates.items():
        rate = info.get('hit_rate', 0)
        if rate > 0.80:
            robust.append(name)
        elif rate > 0.20:
            moderate.append(name)
        else:
            fragile.append(name)

    output = {
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'median_hits': median_hits,
        'mean_hits': mean_hits,
        'max_possible': max_possible,
        'hit_count_distribution': {
            str(i): int(hit_counts.count(i)) for i in range(max_possible + 1)
        },
        'metric_hit_rates': metric_hit_rates,
        'classification': {
            'robust': robust,
            'moderate': moderate,
            'fragile': fragile,
        },
        'oscillation_variation': {
            'spread': float(alt_spread),
            'min': float(min(alt_rates)),
            'max': float(max(alt_rates)),
            'hit': oscillation_variation_hit,
        },
        'per_parameterization': all_scores,
    }

    out_path = RESULTS_DIR / 't3_voynich_comparison.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    print(f"\n{'='*60}")
    print(f"T3 VOYNICH FIDELITY COMPARISON")
    print(f"{'='*60}")
    print(f"")
    print(f"VERDICT: {verdict}")
    print(f"  {verdict_detail}")
    print(f"")
    print(f"MEDIAN HITS: {median_hits:.0f} / {max_possible}")
    print(f"MEAN HITS:   {mean_hits:.1f} / {max_possible}")
    print(f"")
    print(f"HIT COUNT DISTRIBUTION:")
    for i in range(max_possible + 1):
        count = hit_counts.count(i)
        if count > 0:
            bar = '#' * count
            print(f"  {i:2d} hits: {count:3d} params  {bar}")
    print(f"")
    print(f"PER-METRIC HIT RATES:")
    print(f"{'Metric':<30s} {'Hit%':>6s} {'Simulated':>12s} {'Voynich':>12s}")
    print(f"{'-'*30} {'-'*6} {'-'*12} {'-'*12}")
    for name, info in sorted(metric_hit_rates.items()):
        rate = info.get('hit_rate', 0) * 100
        stats = info.get('simulated_stats', {})
        if 'median' in stats:
            sim_val = f"{stats['median']:.3f}"
        elif 'heat_median' in stats:
            sim_val = f"({stats['heat_median']:.0f},{stats['cool_median']:.0f})"
        else:
            sim_val = '-'
        voynich = TARGETS[name]['voynich'].split(' (')[0] if name in TARGETS else '-'
        print(f"  {name:<28s} {rate:5.1f}% {sim_val:>12s} {voynich:>12s}")
    print(f"")
    print(f"ROBUST (>80%):   {', '.join(robust) if robust else 'none'}")
    print(f"MODERATE (20-80%): {', '.join(moderate) if moderate else 'none'}")
    print(f"FRAGILE (<20%):  {', '.join(fragile) if fragile else 'none'}")
    print(f"")
    print(f"OSCILLATION VARIATION:")
    print(f"  Spread: {alt_spread:.3f} (threshold: >0.20)")
    print(f"  Range:  [{min(alt_rates):.3f}, {max(alt_rates):.3f}]")
    print(f"  Hit:    {oscillation_variation_hit}")
    print(f"")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
