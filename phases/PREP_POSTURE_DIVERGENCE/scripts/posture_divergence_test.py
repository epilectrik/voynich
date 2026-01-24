"""
Statistical divergence test for prep verb → grammar posture correlation.

Tests whether recipes with different dominant prep verbs show
systematically different grammar posture metrics.
"""
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Posture metrics to analyze
METRICS = [
    'prefix_entropy',
    'auxiliary_density',
    'link_density',
    'escape_frequency',
    'hazard_frequency',
    'sli',
    'kernel_proximity',
]

# C458 baseline: hazard metrics clamped (CV~0.11), recovery free (CV~0.82)
HAZARD_METRICS = ['hazard_frequency', 'sli', 'kernel_proximity']
RECOVERY_METRICS = ['escape_frequency', 'link_density', 'auxiliary_density', 'prefix_entropy']

def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = math.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def main():
    print("=" * 60)
    print("PREP VERB -> GRAMMAR POSTURE DIVERGENCE TEST")
    print("=" * 60)

    # Load posture data
    with open(PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results' / 'recipe_grammar_postures.json', 'r') as f:
        data = json.load(f)

    postures = data['recipe_postures']
    print(f"\nLoaded {len(postures)} recipe postures")

    # Group by dominant verb
    by_verb = defaultdict(list)
    for p in postures:
        verb = p['dominant_verb']
        by_verb[verb].append(p)

    print("\nRecipe counts by dominant verb:")
    for verb, recipes in sorted(by_verb.items(), key=lambda x: -len(x[1])):
        print(f"  {verb}: {len(recipes)}")

    # Filter to verbs with sufficient samples (n >= 5)
    MIN_N = 5
    test_verbs = [v for v, recipes in by_verb.items() if len(recipes) >= MIN_N]
    print(f"\nVerbs with n >= {MIN_N}: {test_verbs}")

    # Compute metric distributions per verb
    print("\n" + "=" * 60)
    print("METRIC ANALYSIS BY VERB")
    print("=" * 60)

    results = {}
    for metric in METRICS:
        print(f"\n--- {metric} ---")
        metric_by_verb = {}
        for verb in test_verbs:
            values = [p[metric] for p in by_verb[verb] if p.get(metric) is not None]
            if values:
                metric_by_verb[verb] = values
                mean = np.mean(values)
                std = np.std(values)
                print(f"  {verb} (n={len(values)}): mean={mean:.4f}, std={std:.4f}")

        # ANOVA test across verbs
        groups = [metric_by_verb[v] for v in metric_by_verb.keys()]
        if len(groups) >= 2 and all(len(g) >= 2 for g in groups):
            f_stat, p_value = stats.f_oneway(*groups)
            print(f"  ANOVA: F={f_stat:.3f}, p={p_value:.4f}")

            # Pairwise comparisons for significant metrics
            if p_value < 0.10:
                print("  Pairwise Cohen's d:")
                verbs_list = list(metric_by_verb.keys())
                for i, v1 in enumerate(verbs_list):
                    for v2 in verbs_list[i+1:]:
                        d = cohens_d(metric_by_verb[v1], metric_by_verb[v2])
                        print(f"    {v1} vs {v2}: d={d:.3f}")

            results[metric] = {
                'f_stat': f_stat,
                'p_value': p_value,
                'verb_means': {v: float(np.mean(vals)) for v, vals in metric_by_verb.items()},
                'verb_stds': {v: float(np.std(vals)) for v, vals in metric_by_verb.items()},
                'verb_n': {v: len(vals) for v, vals in metric_by_verb.items()},
            }

    # Test by verb category (COLLECTION vs MECHANICAL)
    print("\n" + "=" * 60)
    print("CATEGORY-LEVEL ANALYSIS (COLLECTION vs MECHANICAL)")
    print("=" * 60)

    category_by_verb = {
        'GATHER': 'COLLECTION', 'COLLECT': 'COLLECTION', 'PLUCK': 'COLLECTION',
        'CHOP': 'MECHANICAL', 'STRIP': 'MECHANICAL', 'POUND': 'MECHANICAL',
        'CRUSH': 'MECHANICAL', 'BREAK': 'MECHANICAL',
    }

    by_category = defaultdict(list)
    for p in postures:
        verb = p['dominant_verb']
        cat = category_by_verb.get(verb)
        if cat:
            by_category[cat].append(p)

    print(f"\nCOLLECTION: {len(by_category['COLLECTION'])} recipes")
    print(f"MECHANICAL: {len(by_category['MECHANICAL'])} recipes")

    category_results = {}
    for metric in METRICS:
        coll_vals = [p[metric] for p in by_category['COLLECTION'] if p.get(metric) is not None]
        mech_vals = [p[metric] for p in by_category['MECHANICAL'] if p.get(metric) is not None]

        if len(coll_vals) >= 2 and len(mech_vals) >= 2:
            t_stat, p_value = stats.ttest_ind(coll_vals, mech_vals)
            d = cohens_d(coll_vals, mech_vals)

            coll_mean = np.mean(coll_vals)
            mech_mean = np.mean(mech_vals)

            sig = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""
            print(f"\n{metric}:")
            print(f"  COLLECTION: {coll_mean:.4f}")
            print(f"  MECHANICAL: {mech_mean:.4f}")
            print(f"  t={t_stat:.3f}, p={p_value:.4f}, d={d:.3f} {sig}")

            category_results[metric] = {
                't_stat': t_stat,
                'p_value': p_value,
                'cohens_d': d,
                'collection_mean': coll_mean,
                'mechanical_mean': mech_mean,
            }

    # Check C458 compliance (hazard effects < recovery effects)
    print("\n" + "=" * 60)
    print("C458 COMPLIANCE CHECK")
    print("=" * 60)
    print("Expected: Recovery metrics show larger effects than hazard metrics")
    print("  (Hazard clamped CV~0.11, Recovery free CV~0.82)")

    hazard_d = [abs(category_results[m]['cohens_d']) for m in HAZARD_METRICS if m in category_results]
    recovery_d = [abs(category_results[m]['cohens_d']) for m in RECOVERY_METRICS if m in category_results]

    avg_hazard_d = np.mean(hazard_d) if hazard_d else 0
    avg_recovery_d = np.mean(recovery_d) if recovery_d else 0

    print(f"\nAverage |d| for hazard metrics: {avg_hazard_d:.3f}")
    print(f"Average |d| for recovery metrics: {avg_recovery_d:.3f}")

    if avg_recovery_d > avg_hazard_d:
        print("CONSISTENT with C458: Recovery effects > Hazard effects")
        c458_compliant = True
    else:
        print("INCONSISTENT with C458: Hazard effects >= Recovery effects")
        c458_compliant = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    significant_metrics = [m for m, r in category_results.items() if r['p_value'] < 0.05]
    marginal_metrics = [m for m, r in category_results.items() if 0.05 <= r['p_value'] < 0.10]

    print(f"\nSignificant divergences (p < 0.05): {len(significant_metrics)}")
    for m in significant_metrics:
        d = category_results[m]['cohens_d']
        print(f"  {m}: d={d:.3f}")

    print(f"\nMarginal divergences (0.05 <= p < 0.10): {len(marginal_metrics)}")
    for m in marginal_metrics:
        d = category_results[m]['cohens_d']
        print(f"  {m}: d={d:.3f}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    success_criteria = {
        'significant_metrics': len(significant_metrics) >= 2,
        'c458_compliant': c458_compliant,
        'effect_size': any(abs(r['cohens_d']) > 0.3 for r in category_results.values()),
    }

    print("\nSuccess criteria:")
    for criterion, passed in success_criteria.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {criterion}: {status}")

    if all(success_criteria.values()):
        verdict = "H1 SUPPORTED: Verb profiles correlate with grammar postures"
    elif any(success_criteria.values()):
        verdict = "INCONCLUSIVE: Partial support for H1"
    else:
        verdict = "H0 NOT REJECTED: No significant verb-posture divergence"

    print(f"\n>>> {verdict}")

    # Save results
    output = {
        'verb_level_results': results,
        'category_level_results': category_results,
        'c458_compliance': {
            'avg_hazard_d': avg_hazard_d,
            'avg_recovery_d': avg_recovery_d,
            'compliant': c458_compliant,
        },
        'success_criteria': success_criteria,
        'verdict': verdict,
    }

    output_path = PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results' / 'divergence_statistics.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=float)

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
