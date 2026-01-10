#!/usr/bin/env python3
"""
HT-THREAD Phase 2: Manuscript-Wide Distribution Analysis

Tests:
1. Is HT uniformly distributed or clustered?
2. Are there HT "hotspots" or "deserts"?
3. Does HT density correlate with manuscript position?
4. Autocorrelation: do adjacent folios have similar HT density?
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

def load_ht_features():
    """Load Phase 1 HT features."""
    path = RESULTS / "ht_folio_features.json"
    with open(path) as f:
        return json.load(f)

def get_folio_order():
    """Get folios in manuscript order (codicological sequence)."""
    # Standard folio ordering: f1r, f1v, f2r, f2v, ...
    # Some folios have special numbering (f85r1, f85r2, etc.)
    # We'll sort by extracting numeric parts

    def folio_sort_key(f):
        # Extract number and suffix
        import re
        match = re.match(r'f(\d+)([rv])(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)

    return folio_sort_key

def runs_test(sequence):
    """
    Wald-Wolfowitz runs test for randomness.

    Tests if values above/below median occur in random runs.
    """
    median = np.median(sequence)
    binary = [1 if x > median else 0 for x in sequence]

    # Count runs
    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i-1]:
            runs += 1

    # Expected runs and variance under null (random)
    n1 = sum(binary)
    n0 = len(binary) - n1

    if n0 == 0 or n1 == 0:
        return {'runs': runs, 'p_value': 1.0, 'verdict': 'INSUFFICIENT_DATA'}

    expected_runs = (2 * n0 * n1) / (n0 + n1) + 1
    variance = (2 * n0 * n1 * (2 * n0 * n1 - n0 - n1)) / ((n0 + n1)**2 * (n0 + n1 - 1))

    if variance <= 0:
        return {'runs': runs, 'p_value': 1.0, 'verdict': 'INSUFFICIENT_DATA'}

    z = (runs - expected_runs) / np.sqrt(variance)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Fewer runs than expected = clustering
    # More runs than expected = oscillation
    if p_value < 0.05:
        if runs < expected_runs:
            verdict = 'CLUSTERED'
        else:
            verdict = 'OSCILLATING'
    else:
        verdict = 'RANDOM'

    return {
        'runs': runs,
        'expected_runs': float(expected_runs),
        'z_score': float(z),
        'p_value': float(p_value),
        'verdict': verdict
    }

def autocorrelation(sequence, lag=1):
    """Compute autocorrelation at given lag."""
    n = len(sequence)
    if n < lag + 2:
        return 0.0

    mean = np.mean(sequence)
    var = np.var(sequence)

    if var == 0:
        return 0.0

    autocov = np.mean((sequence[:-lag] - mean) * (sequence[lag:] - mean))
    return autocov / var

def identify_hotspots_deserts(features, threshold_std=2):
    """Identify folios with extreme HT density."""
    densities = [f['ht_density'] for f in features.values()]
    mean_d = np.mean(densities)
    std_d = np.std(densities)

    hotspots = []
    deserts = []

    for folio, feat in features.items():
        d = feat['ht_density']
        z = (d - mean_d) / std_d if std_d > 0 else 0

        if z > threshold_std:
            hotspots.append({
                'folio': folio,
                'ht_density': d,
                'z_score': float(z),
                'system': feat['system'],
                'quire': feat.get('quire', 'UNKNOWN')
            })
        elif z < -threshold_std:
            deserts.append({
                'folio': folio,
                'ht_density': d,
                'z_score': float(z),
                'system': feat['system'],
                'quire': feat.get('quire', 'UNKNOWN')
            })

    return hotspots, deserts

def test_position_correlation(features):
    """Test if HT density correlates with manuscript position."""
    # Sort folios by manuscript order
    sort_key = get_folio_order()
    ordered_folios = sorted(features.keys(), key=sort_key)

    positions = list(range(len(ordered_folios)))
    densities = [features[f]['ht_density'] for f in ordered_folios]

    # Pearson correlation
    r, p = stats.pearsonr(positions, densities)

    # Spearman (rank) correlation
    rho, p_spearman = stats.spearmanr(positions, densities)

    return {
        'pearson_r': float(r),
        'pearson_p': float(p),
        'spearman_rho': float(rho),
        'spearman_p': float(p_spearman),
        'interpretation': (
            'GRADIENT_INCREASE' if r > 0.3 and p < 0.05 else
            'GRADIENT_DECREASE' if r < -0.3 and p < 0.05 else
            'NO_GRADIENT'
        )
    }

def test_quire_effects(features):
    """Test if HT density varies significantly by quire."""
    quire_densities = defaultdict(list)

    for folio, feat in features.items():
        quire = feat.get('quire', 'UNKNOWN')
        if quire and quire != 'UNKNOWN':
            quire_densities[quire].append(feat['ht_density'])

    # Filter quires with enough data
    valid_quires = {q: d for q, d in quire_densities.items() if len(d) >= 3}

    if len(valid_quires) < 2:
        return {'error': 'Insufficient quire data'}

    # Kruskal-Wallis test (non-parametric ANOVA)
    groups = list(valid_quires.values())
    h_stat, p_value = stats.kruskal(*groups)

    # Effect size (eta-squared approximation)
    n_total = sum(len(g) for g in groups)
    eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))

    # Quire summary
    quire_summary = {}
    for q, densities in valid_quires.items():
        quire_summary[q] = {
            'n': len(densities),
            'mean': float(np.mean(densities)),
            'std': float(np.std(densities))
        }

    return {
        'kruskal_h': float(h_stat),
        'p_value': float(p_value),
        'eta_squared': float(eta_sq),
        'n_quires': len(valid_quires),
        'significant': bool(p_value < 0.05),
        'quire_summary': quire_summary
    }

def test_system_differences(features):
    """Test if HT density differs significantly between A/B/AZC."""
    system_densities = defaultdict(list)

    for folio, feat in features.items():
        system = feat.get('system', 'UNKNOWN')
        if system in ['A', 'B', 'AZC']:
            system_densities[system].append(feat['ht_density'])

    # Kruskal-Wallis test
    groups = [system_densities['A'], system_densities['B'], system_densities['AZC']]
    h_stat, p_value = stats.kruskal(*groups)

    # Pairwise comparisons (Mann-Whitney U)
    pairwise = {}
    for s1, s2 in [('A', 'B'), ('A', 'AZC'), ('B', 'AZC')]:
        u_stat, p = stats.mannwhitneyu(system_densities[s1], system_densities[s2],
                                        alternative='two-sided')
        pairwise[f'{s1}_vs_{s2}'] = {
            'u_stat': float(u_stat),
            'p_value': float(p),
            'significant': bool(p < 0.05/3)  # Bonferroni correction
        }

    # Summary per system
    system_summary = {}
    for sys, densities in system_densities.items():
        system_summary[sys] = {
            'n': len(densities),
            'mean': float(np.mean(densities)),
            'std': float(np.std(densities)),
            'median': float(np.median(densities))
        }

    return {
        'kruskal_h': float(h_stat),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05),
        'pairwise_tests': pairwise,
        'system_summary': system_summary
    }

def main():
    print("=" * 70)
    print("HT-THREAD Phase 2: Distribution Analysis")
    print("=" * 70)

    # Load features
    print("\n[1] Loading HT features...")
    data = load_ht_features()
    features = data['folios']
    print(f"    Loaded {len(features)} folios")

    # Get ordered density sequence
    sort_key = get_folio_order()
    ordered_folios = sorted(features.keys(), key=sort_key)
    density_sequence = [features[f]['ht_density'] for f in ordered_folios]

    # Test 1: Runs test for randomness
    print("\n[2] Runs test for randomness...")
    runs_result = runs_test(density_sequence)
    print(f"    Observed runs: {runs_result['runs']}")
    print(f"    Expected runs: {runs_result.get('expected_runs', 'N/A'):.1f}")
    print(f"    P-value: {runs_result['p_value']:.4f}")
    print(f"    Verdict: {runs_result['verdict']}")

    # Test 2: Autocorrelation
    print("\n[3] Autocorrelation analysis...")
    autocorr_1 = autocorrelation(density_sequence, lag=1)
    autocorr_2 = autocorrelation(density_sequence, lag=2)
    autocorr_5 = autocorrelation(density_sequence, lag=5)
    print(f"    Lag-1 autocorrelation: {autocorr_1:.3f}")
    print(f"    Lag-2 autocorrelation: {autocorr_2:.3f}")
    print(f"    Lag-5 autocorrelation: {autocorr_5:.3f}")

    if autocorr_1 > 0.3:
        autocorr_verdict = 'STRONG_POSITIVE (adjacent folios similar)'
    elif autocorr_1 > 0.1:
        autocorr_verdict = 'WEAK_POSITIVE (some adjacency effect)'
    elif autocorr_1 < -0.3:
        autocorr_verdict = 'STRONG_NEGATIVE (adjacent folios differ)'
    else:
        autocorr_verdict = 'NEGLIGIBLE (no adjacency effect)'
    print(f"    Interpretation: {autocorr_verdict}")

    # Test 3: Hotspots and deserts
    print("\n[4] Identifying hotspots and deserts...")
    hotspots, deserts = identify_hotspots_deserts(features)
    print(f"    Hotspots (>2 std): {len(hotspots)}")
    for h in sorted(hotspots, key=lambda x: -x['ht_density'])[:5]:
        print(f"      {h['folio']}: {h['ht_density']:.3f} ({h['system']}, quire {h['quire']})")

    print(f"    Deserts (<2 std): {len(deserts)}")
    for d in sorted(deserts, key=lambda x: x['ht_density'])[:5]:
        print(f"      {d['folio']}: {d['ht_density']:.3f} ({d['system']}, quire {d['quire']})")

    # Test 4: Position correlation
    print("\n[5] Testing position correlation...")
    position_result = test_position_correlation(features)
    print(f"    Pearson r: {position_result['pearson_r']:.3f} (p={position_result['pearson_p']:.4f})")
    print(f"    Spearman rho: {position_result['spearman_rho']:.3f} (p={position_result['spearman_p']:.4f})")
    print(f"    Interpretation: {position_result['interpretation']}")

    # Test 5: Quire effects
    print("\n[6] Testing quire effects...")
    quire_result = test_quire_effects(features)
    if 'error' not in quire_result:
        print(f"    Kruskal-Wallis H: {quire_result['kruskal_h']:.2f}")
        print(f"    P-value: {quire_result['p_value']:.6f}")
        print(f"    Significant: {quire_result['significant']}")
        print(f"    Eta-squared: {quire_result['eta_squared']:.3f}")

        # Show quires with extreme HT
        sorted_quires = sorted(quire_result['quire_summary'].items(),
                               key=lambda x: x[1]['mean'], reverse=True)
        print("    Top 3 HT-dense quires:")
        for q, stats in sorted_quires[:3]:
            print(f"      Quire {q}: mean={stats['mean']:.3f}, n={stats['n']}")
        print("    Bottom 3 HT-dense quires:")
        for q, stats in sorted_quires[-3:]:
            print(f"      Quire {q}: mean={stats['mean']:.3f}, n={stats['n']}")

    # Test 6: System differences
    print("\n[7] Testing system differences...")
    system_result = test_system_differences(features)
    print(f"    Kruskal-Wallis H: {system_result['kruskal_h']:.2f}")
    print(f"    P-value: {system_result['p_value']:.6f}")
    print(f"    Significant: {system_result['significant']}")

    print("\n    System summary:")
    for sys in ['A', 'B', 'AZC']:
        s = system_result['system_summary'][sys]
        print(f"      {sys}: mean={s['mean']:.3f}, std={s['std']:.3f}, n={s['n']}")

    print("\n    Pairwise comparisons (Bonferroni-corrected):")
    for comp, result in system_result['pairwise_tests'].items():
        sig = "[SIGNIFICANT]" if result['significant'] else ""
        print(f"      {comp}: p={result['p_value']:.4f} {sig}")

    # Save results
    output = {
        'metadata': {
            'analysis': 'HT-THREAD Phase 2',
            'description': 'Manuscript-wide HT distribution analysis',
            'n_folios': len(features)
        },
        'runs_test': runs_result,
        'autocorrelation': {
            'lag_1': float(autocorr_1),
            'lag_2': float(autocorr_2),
            'lag_5': float(autocorr_5),
            'verdict': autocorr_verdict
        },
        'hotspots': hotspots,
        'deserts': deserts,
        'position_correlation': position_result,
        'quire_effects': quire_result,
        'system_differences': system_result,
        'summary': {
            'distribution_pattern': runs_result['verdict'],
            'adjacency_effect': autocorr_verdict,
            'position_gradient': position_result['interpretation'],
            'quire_significant': bool(quire_result.get('significant', False)),
            'system_significant': bool(system_result['significant'])
        }
    }

    output_path = RESULTS / "ht_distribution_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 2 SUMMARY")
    print("=" * 70)
    print(f"\nDistribution pattern: {runs_result['verdict']}")
    print(f"Adjacency effect: {autocorr_verdict}")
    print(f"Position gradient: {position_result['interpretation']}")
    print(f"Quire effect significant: {quire_result.get('significant', False)}")
    print(f"System differences significant: {system_result['significant']}")
    print("\n" + "=" * 70)

    return output

if __name__ == "__main__":
    main()
