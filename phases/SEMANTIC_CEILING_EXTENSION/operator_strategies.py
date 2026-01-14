#!/usr/bin/env python3
"""
Test 4A: Operator Strategy Viability

Pre-Registered Question:
"Which B programs tolerate which operator strategies?"

EPISTEMIC SAFEGUARD:
This test remains Tier 3/4 exploratory. Results do NOT enable semantic decoding
or Tier 2 promotion without independent corroboration.
"""

import json
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
B_FEATURES = BASE_PATH / "results" / "b_macro_scaffold_audit.json"
HT_FEATURES = BASE_PATH / "results" / "ht_folio_features.json"
OUTPUT_FILE = BASE_PATH / "results" / "operator_strategies.json"

# Strategy definitions based on operational metrics
STRATEGIES = {
    'CAUTIOUS': {
        'description': 'High intervention, frequent stabilizing',
        'requires': {'link_density': 'high', 'intervention_frequency': 'high', 'qo_density': 'low'}
    },
    'AGGRESSIVE': {
        'description': 'Minimal intervention, fast throughput',
        'requires': {'link_density': 'low', 'intervention_frequency': 'low', 'hazard_density': 'high'}
    },
    'OPPORTUNISTIC': {
        'description': 'Escape-heavy, adaptive',
        'requires': {'qo_density': 'high', 'recovery_ops_count': 'high'}
    }
}


def load_b_features():
    """Load B folio behavior profiles."""
    with open(B_FEATURES) as f:
        data = json.load(f)
    return data['features']


def load_ht_features():
    """Load HT features per folio."""
    with open(HT_FEATURES) as f:
        data = json.load(f)
    return data['folios']


def categorize_folio_by_archetype(features):
    """Categorize each folio into operational archetype."""
    archetypes = {}

    for folio, f in features.items():
        # Determine dominant operational mode
        link = f.get('link_density', 0)
        hazard = f.get('hazard_density', 0)
        qo = f.get('qo_density', 0)
        intervention = f.get('intervention_frequency', 0)

        # Simple archetype classification
        if link > 0.35 and intervention > 6:
            archetype = 'CONSERVATIVE_WAITING'
        elif hazard > 0.65 and intervention > 6:
            archetype = 'AGGRESSIVE_INTERVENTION'
        elif qo > 0.22:
            archetype = 'ENERGY_INTENSIVE'
        elif link < 0.30 and hazard < 0.60:
            archetype = 'STANDARD_BALANCED'
        else:
            archetype = 'MIXED'

        archetypes[folio] = archetype

    return archetypes


def compute_strategy_compatibility(folio, features, strategy_name, thresholds):
    """Compute how compatible a folio is with a given strategy."""
    f = features.get(folio, {})
    strategy = STRATEGIES[strategy_name]

    compatibility_score = 0
    total_checks = 0

    for metric, requirement in strategy['requires'].items():
        if metric in f:
            value = f[metric]
            threshold = thresholds[metric]

            if requirement == 'high':
                compatible = value >= threshold['high']
            elif requirement == 'low':
                compatible = value <= threshold['low']
            else:
                compatible = True

            if compatible:
                compatibility_score += 1
            total_checks += 1

    return compatibility_score / total_checks if total_checks > 0 else 0


def main():
    print("=" * 60)
    print("Test 4A: Operator Strategy Viability")
    print("Tier 3/4 Exploratory")
    print("=" * 60)
    print()

    # Load features
    print("Loading B folio features...")
    b_features = load_b_features()
    print(f"  B folios: {len(b_features)}")
    print()

    # Load HT features
    print("Loading HT features...")
    ht_features = load_ht_features()
    print()

    # Compute thresholds (median splits)
    metrics = ['link_density', 'intervention_frequency', 'qo_density', 'hazard_density', 'recovery_ops_count']
    thresholds = {}

    for metric in metrics:
        values = [f[metric] for f in b_features.values() if metric in f]
        if values:
            thresholds[metric] = {
                'low': np.percentile(values, 33),
                'high': np.percentile(values, 67)
            }
            print(f"  {metric}: low<{thresholds[metric]['low']:.3f}, high>{thresholds[metric]['high']:.3f}")
    print()

    # Categorize folios by archetype
    print("Categorizing folios by archetype...")
    archetypes = categorize_folio_by_archetype(b_features)
    archetype_counts = defaultdict(int)
    for a in archetypes.values():
        archetype_counts[a] += 1

    for arch, count in sorted(archetype_counts.items(), key=lambda x: -x[1]):
        print(f"  {arch}: {count}")
    print()

    # Compute strategy compatibility for each folio
    print("Computing strategy compatibility...")
    folio_compatibility = {}

    for folio in b_features:
        folio_compatibility[folio] = {}
        for strategy in STRATEGIES:
            score = compute_strategy_compatibility(folio, b_features, strategy, thresholds)
            folio_compatibility[folio][strategy] = score

    # Analyze strategy-archetype matrix
    print("\nStrategy-Archetype Viability Matrix:")
    print("-" * 60)

    archetype_strategy_scores = defaultdict(lambda: defaultdict(list))

    for folio, archetype in archetypes.items():
        if folio in folio_compatibility:
            for strategy, score in folio_compatibility[folio].items():
                archetype_strategy_scores[archetype][strategy].append(score)

    matrix = {}
    for archetype in sorted(archetype_counts.keys()):
        matrix[archetype] = {}
        print(f"\n  {archetype}:")
        for strategy in STRATEGIES:
            scores = archetype_strategy_scores[archetype][strategy]
            if scores:
                mean_score = np.mean(scores)
                matrix[archetype][strategy] = mean_score
                viable = "VIABLE" if mean_score > 0.5 else "POOR"
                print(f"    {strategy}: {mean_score:.2f} ({viable})")

    # Test HT-strategy correlation
    print("\n" + "=" * 60)
    print("Testing HT-Strategy Correlation")
    print("=" * 60)

    ht_strategy_correlations = {}
    for strategy in STRATEGIES:
        ht_values = []
        strat_values = []

        for folio in folio_compatibility:
            if folio in ht_features:
                ht_values.append(ht_features[folio]['ht_density'])
                strat_values.append(folio_compatibility[folio][strategy])

        if len(ht_values) >= 10:
            r, p = stats.pearsonr(ht_values, strat_values)
            ht_strategy_correlations[strategy] = {'r': r, 'p': p}
            sig = "*" if p < 0.05 else ""
            print(f"  HT vs {strategy}: r={r:.4f}, p={p:.4f}{sig}")

    # Verdict
    print("\n" + "=" * 60)

    # Check for non-uniform viability
    viable_counts = defaultdict(int)
    for archetype in matrix:
        for strategy in matrix[archetype]:
            if matrix[archetype][strategy] > 0.5:
                viable_counts[strategy] += 1

    uniform = all(c == len(matrix) or c == 0 for c in viable_counts.values())

    # Check HT correlations
    any_ht_sig = any(c['p'] < 0.05 for c in ht_strategy_correlations.values())

    if not uniform and any_ht_sig:
        verdict = "DIFFERENTIATED_STRATEGIES"
        print("VERDICT: STRATEGIES ARE DIFFERENTIATED")
        print("  Non-uniform viability across archetypes.")
        print("  HT predicts strategy compatibility.")
    elif not uniform:
        verdict = "PARTIAL_DIFFERENTIATION"
        print("VERDICT: PARTIAL DIFFERENTIATION")
        print("  Non-uniform viability, but HT not predictive.")
    else:
        verdict = "UNIFORM_VIABILITY"
        print("VERDICT: UNIFORM VIABILITY")
        print("  All strategies work in all archetypes.")
    print("=" * 60)

    # Save results
    results = {
        "test": "4A_OPERATOR_STRATEGIES",
        "tier": "3-4",
        "question": "Which B programs tolerate which operator strategies?",
        "thresholds": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in thresholds.items()},
        "archetype_counts": dict(archetype_counts),
        "viability_matrix": matrix,
        "ht_correlations": {k: {'r': float(v['r']), 'p': float(v['p'])} for k, v in ht_strategy_correlations.items()},
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
