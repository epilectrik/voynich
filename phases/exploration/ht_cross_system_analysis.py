#!/usr/bin/env python3
"""
HT-THREAD Phase 4: Cross-System Threading Analysis

Key questions:
1. Does HT density change abruptly at system boundaries?
2. Do HT vocabulary types cross system boundaries?
3. Is there HT continuity or discontinuity at A/B/AZC transitions?
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import re

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

def load_ht_features():
    """Load Phase 1 HT features."""
    path = RESULTS / "ht_folio_features.json"
    with open(path) as f:
        return json.load(f)

def get_folio_order():
    """Get folios in manuscript order."""
    def folio_sort_key(f):
        match = re.match(r'f(\d+)([rv])(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)
    return folio_sort_key

def identify_system_boundaries(features):
    """
    Find folios at system transitions (where system changes between adjacent folios).
    """
    sort_key = get_folio_order()
    ordered_folios = sorted(features.keys(), key=sort_key)

    boundaries = []
    for i in range(1, len(ordered_folios)):
        prev_folio = ordered_folios[i-1]
        curr_folio = ordered_folios[i]

        prev_sys = features[prev_folio]['system']
        curr_sys = features[curr_folio]['system']

        if prev_sys != curr_sys:
            boundaries.append({
                'index': i,
                'prev_folio': prev_folio,
                'curr_folio': curr_folio,
                'transition': f'{prev_sys}->{curr_sys}',
                'prev_ht_density': features[prev_folio]['ht_density'],
                'curr_ht_density': features[curr_folio]['ht_density'],
                'density_change': features[curr_folio]['ht_density'] - features[prev_folio]['ht_density']
            })

    return boundaries, ordered_folios

def test_boundary_discontinuity(features, boundaries, ordered_folios):
    """
    Test if HT density changes more at system boundaries than within systems.

    Compare:
    - Density change at boundaries
    - Density change between adjacent folios within same system
    """
    # Within-system adjacent changes
    within_changes = []
    for i in range(1, len(ordered_folios)):
        prev_folio = ordered_folios[i-1]
        curr_folio = ordered_folios[i]

        prev_sys = features[prev_folio]['system']
        curr_sys = features[curr_folio]['system']

        if prev_sys == curr_sys:
            change = abs(features[curr_folio]['ht_density'] - features[prev_folio]['ht_density'])
            within_changes.append(change)

    # Boundary changes
    boundary_changes = [abs(b['density_change']) for b in boundaries]

    if not within_changes or not boundary_changes:
        return {'error': 'Insufficient data'}

    # Mann-Whitney U test
    u_stat, p_value = stats.mannwhitneyu(boundary_changes, within_changes,
                                          alternative='greater')

    # Effect size (rank-biserial correlation)
    n1, n2 = len(boundary_changes), len(within_changes)
    r = 1 - (2 * u_stat) / (n1 * n2)

    return {
        'mean_boundary_change': float(np.mean(boundary_changes)),
        'mean_within_change': float(np.mean(within_changes)),
        'boundary_std': float(np.std(boundary_changes)),
        'within_std': float(np.std(within_changes)),
        'n_boundaries': len(boundary_changes),
        'n_within': len(within_changes),
        'u_stat': float(u_stat),
        'p_value': float(p_value),
        'effect_size_r': float(r),
        'verdict': 'DISCONTINUOUS' if p_value < 0.05 else 'CONTINUOUS',
        'interpretation': (
            'HT density changes MORE at system boundaries' if p_value < 0.05 else
            'HT density changes SIMILARLY at boundaries and within systems'
        )
    }

def analyze_transition_types(boundaries):
    """Analyze density changes by transition type."""
    transition_stats = defaultdict(list)

    for b in boundaries:
        trans_type = b['transition']
        transition_stats[trans_type].append(b['density_change'])

    results = {}
    for trans, changes in transition_stats.items():
        results[trans] = {
            'count': len(changes),
            'mean_change': float(np.mean(changes)),
            'std_change': float(np.std(changes)),
            'direction': 'INCREASE' if np.mean(changes) > 0 else 'DECREASE'
        }

    return results

def test_ht_vocabulary_crossing(features):
    """
    Test if HT vocabulary types cross system boundaries.

    If HT is a continuous layer, we expect vocabulary sharing across systems.
    If HT is system-specific, vocabulary should be localized.
    """
    # Collect HT types per system
    system_ht_types = defaultdict(set)

    for folio, feat in features.items():
        system = feat['system']
        # Get HT types from prefix distribution (types with non-zero count)
        for prefix, rate in feat['ht_prefix_dist'].items():
            if rate > 0:
                # Construct type proxy (we don't have actual types, use prefixes)
                system_ht_types[system].add(prefix)

    # Compute overlap between systems
    systems = ['A', 'B', 'AZC']
    overlap_matrix = {}

    for s1 in systems:
        for s2 in systems:
            if s1 == s2:
                continue
            overlap = len(system_ht_types[s1] & system_ht_types[s2])
            union = len(system_ht_types[s1] | system_ht_types[s2])
            jaccard = overlap / union if union > 0 else 0.0
            overlap_matrix[f'{s1}_{s2}'] = {
                'overlap_count': overlap,
                'jaccard': float(jaccard),
                's1_size': len(system_ht_types[s1]),
                's2_size': len(system_ht_types[s2])
            }

    return {
        'prefix_overlap': overlap_matrix,
        'system_prefix_counts': {s: len(types) for s, types in system_ht_types.items()},
        'interpretation': (
            'HIGH overlap suggests HT prefixes cross system boundaries' if
            all(v['jaccard'] > 0.7 for v in overlap_matrix.values()) else
            'MODERATE overlap - some system specificity in HT prefixes' if
            all(v['jaccard'] > 0.4 for v in overlap_matrix.values()) else
            'LOW overlap - HT prefixes are system-specific'
        )
    }

def analyze_ht_prefix_by_system(features):
    """Analyze which HT prefixes dominate in each system."""
    system_prefix_totals = defaultdict(lambda: defaultdict(float))

    for folio, feat in features.items():
        system = feat['system']
        n_ht = feat['n_ht']

        for prefix, rate in feat['ht_prefix_dist'].items():
            system_prefix_totals[system][prefix] += rate * n_ht

    # Normalize and find dominant prefixes
    results = {}
    for system in ['A', 'B', 'AZC']:
        totals = system_prefix_totals[system]
        total_count = sum(totals.values())

        if total_count == 0:
            continue

        prefix_rates = {p: c / total_count for p, c in totals.items()}
        sorted_prefixes = sorted(prefix_rates.items(), key=lambda x: -x[1])

        results[system] = {
            'top_prefixes': [{'prefix': p, 'rate': float(r)} for p, r in sorted_prefixes[:5]],
            'total_ht_tokens': int(total_count)
        }

    return results

def test_local_threading(features, ordered_folios, window=3):
    """
    Test if HT density shows local threading patterns.

    Look at windows of folios and test if HT density is more correlated
    within windows than across.
    """
    densities = [features[f]['ht_density'] for f in ordered_folios]
    n = len(densities)

    # Compute within-window correlations
    within_corrs = []
    for i in range(n - window + 1):
        window_dens = densities[i:i+window]
        if len(window_dens) >= 2:
            # Simple variance ratio as coherence measure
            var = np.var(window_dens)
            within_corrs.append(var)

    # Random baseline (shuffle and compute same measure)
    np.random.seed(42)
    n_shuffles = 1000
    shuffled_vars = []
    for _ in range(n_shuffles):
        shuffled = np.random.permutation(densities)
        for i in range(n - window + 1):
            shuffled_vars.append(np.var(shuffled[i:i+window]))

    # Compare observed to shuffled
    observed_mean_var = np.mean(within_corrs)
    shuffled_mean_var = np.mean(shuffled_vars)

    # P-value: proportion of shuffled <= observed (lower variance = tighter clustering)
    p_value = np.mean([s <= observed_mean_var for s in shuffled_vars])

    return {
        'window_size': window,
        'observed_mean_variance': float(observed_mean_var),
        'shuffled_mean_variance': float(shuffled_mean_var),
        'p_value': float(p_value),
        'verdict': 'LOCAL_THREADING' if p_value < 0.05 else 'NO_LOCAL_THREADING',
        'interpretation': (
            f'HT density shows tighter local clustering than random (p={p_value:.4f})' if p_value < 0.05 else
            f'HT density local clustering is similar to random (p={p_value:.4f})'
        )
    }

def main():
    print("=" * 70)
    print("HT-THREAD Phase 4: Cross-System Threading Analysis")
    print("=" * 70)

    # Load features
    print("\n[1] Loading HT features...")
    data = load_ht_features()
    features = data['folios']
    print(f"    Loaded {len(features)} folios")

    # Identify system boundaries
    print("\n[2] Identifying system boundaries...")
    boundaries, ordered_folios = identify_system_boundaries(features)
    print(f"    Found {len(boundaries)} system transitions")

    # Count by type
    trans_counts = Counter(b['transition'] for b in boundaries)
    print("\n    Transition types:")
    for trans, count in trans_counts.most_common():
        print(f"      {trans}: {count}")

    # Test boundary discontinuity
    print("\n[3] Testing boundary discontinuity...")
    discontinuity = test_boundary_discontinuity(features, boundaries, ordered_folios)
    if 'error' not in discontinuity:
        print(f"    Mean boundary change: {discontinuity['mean_boundary_change']:.4f}")
        print(f"    Mean within-system change: {discontinuity['mean_within_change']:.4f}")
        print(f"    P-value: {discontinuity['p_value']:.4f}")
        print(f"    Verdict: {discontinuity['verdict']}")
        print(f"    {discontinuity['interpretation']}")

    # Analyze transition types
    print("\n[4] Analyzing transition types...")
    trans_analysis = analyze_transition_types(boundaries)
    for trans, stats in trans_analysis.items():
        print(f"    {trans}: mean_change={stats['mean_change']:+.4f}, n={stats['count']}, direction={stats['direction']}")

    # Test vocabulary crossing
    print("\n[5] Testing HT vocabulary crossing...")
    vocab_crossing = test_ht_vocabulary_crossing(features)
    print(f"    {vocab_crossing['interpretation']}")
    for pair, stats in vocab_crossing['prefix_overlap'].items():
        print(f"      {pair}: Jaccard={stats['jaccard']:.3f}")

    # Prefix analysis by system
    print("\n[6] HT prefix usage by system...")
    prefix_by_system = analyze_ht_prefix_by_system(features)
    for system, stats in prefix_by_system.items():
        top3 = ', '.join(f"{p['prefix']}({p['rate']:.2f})" for p in stats['top_prefixes'][:3])
        print(f"    {system}: {top3}")

    # Local threading test
    print("\n[7] Testing local threading...")
    threading = test_local_threading(features, ordered_folios)
    print(f"    {threading['interpretation']}")

    # Save results
    output = {
        'metadata': {
            'analysis': 'HT-THREAD Phase 4',
            'description': 'Cross-system HT threading analysis',
            'n_folios': len(features),
            'n_boundaries': len(boundaries)
        },
        'boundaries': boundaries,
        'discontinuity_test': discontinuity,
        'transition_analysis': trans_analysis,
        'vocabulary_crossing': vocab_crossing,
        'prefix_by_system': prefix_by_system,
        'local_threading': threading,
        'summary': {
            'boundary_behavior': discontinuity.get('verdict', 'UNKNOWN'),
            'vocabulary_crossing': vocab_crossing['interpretation'],
            'local_threading': threading['verdict']
        }
    }

    output_path = RESULTS / "ht_cross_system_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 4 SUMMARY")
    print("=" * 70)
    print(f"\nBoundary behavior: {discontinuity.get('verdict', 'UNKNOWN')}")
    print(f"Vocabulary crossing: {vocab_crossing['interpretation']}")
    print(f"Local threading: {threading['verdict']}")
    print("\n" + "=" * 70)

    return output

if __name__ == "__main__":
    main()
