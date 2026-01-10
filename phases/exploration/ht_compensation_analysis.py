#!/usr/bin/env python3
"""
D3: HT Compensation Hypothesis

Does HT spike where other systems are "stressful"?
Does HT anticipate or follow stress?

Questions:
1. Does B brittleness predict nearby HT density?
2. Do HT hotspots precede or follow brittle B sections?
3. Is HT correlated with B stress at quire level?

Output: results/ht_compensation_analysis.json
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
UNIFIED_PROFILES = RESULTS / "unified_folio_profiles.json"
B_FEATURES = RESULTS / "b_macro_scaffold_audit.json"
HT_FEATURES = RESULTS / "ht_folio_features.json"
HT_DIST = RESULTS / "ht_distribution_analysis.json"

# Output
OUTPUT = RESULTS / "ht_compensation_analysis.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_folio_order(unified):
    """Get manuscript order of folios."""
    # Extract folio numbers and sort
    folios = list(unified['profiles'].keys())

    def folio_sort_key(f):
        # Extract numeric part and suffix
        import re
        match = re.match(r'f(\d+)([rv]?)(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1 if match.group(2) == 'v' else 0
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)

    return sorted(folios, key=folio_sort_key)


def compute_b_stress_metrics(unified, b_features):
    """
    Compute stress metrics for B folios.
    Stress = high hazard, low escape (forgiveness).
    """
    stress = {}

    for folio, profile in unified['profiles'].items():
        if profile['system'] != 'B':
            continue

        b_metrics = profile.get('b_metrics')
        if not b_metrics:
            continue

        hazard = b_metrics.get('hazard_density', 0)
        escape = b_metrics.get('qo_density', 0)

        # Execution tension from unified profile
        tension = profile['burden_indices'].get('execution_tension')

        stress[folio] = {
            'hazard_density': hazard,
            'escape_density': escape,
            'execution_tension': tension,
            'regime': b_metrics.get('regime', 'UNKNOWN')
        }

    return stress


def compute_ht_at_windows(folio, folio_order, unified, window_sizes=[1, 2, 3]):
    """
    Compute HT density at various window sizes around a folio.
    """
    try:
        idx = folio_order.index(folio)
    except ValueError:
        return None

    windows = {}

    for w in window_sizes:
        # Get folios in window
        start = max(0, idx - w)
        end = min(len(folio_order), idx + w + 1)

        window_folios = folio_order[start:end]
        # Exclude the target folio itself
        window_folios = [f for f in window_folios if f != folio]

        if not window_folios:
            continue

        # Get HT densities
        ht_values = []
        for wf in window_folios:
            if wf in unified['profiles']:
                ht = unified['profiles'][wf].get('ht_density', 0)
                if ht is not None:
                    ht_values.append(ht)

        if ht_values:
            windows[f'window_{w}'] = {
                'mean_ht': round(float(np.mean(ht_values)), 4),
                'max_ht': round(float(max(ht_values)), 4),
                'n_folios': len(ht_values)
            }

    return windows


def compute_quire_ht(folio, unified):
    """
    Compute mean HT density in the same quire as folio.
    """
    target_quire = unified['profiles'].get(folio, {}).get('quire')
    if not target_quire:
        return None

    quire_ht = []
    for f, profile in unified['profiles'].items():
        if profile.get('quire') == target_quire and f != folio:
            ht = profile.get('ht_density', 0)
            if ht is not None:
                quire_ht.append(ht)

    if not quire_ht:
        return None

    return {
        'mean_ht': round(float(np.mean(quire_ht)), 4),
        'std_ht': round(float(np.std(quire_ht)), 4),
        'n_folios': len(quire_ht)
    }


def test_b_stress_ht_correlation(b_stress, unified, folio_order):
    """
    Test: Does B brittleness predict nearby HT?
    """
    results = {}

    # For each window size, correlate B stress with surrounding HT
    for window_name in ['window_1', 'window_2', 'window_3']:
        b_tensions = []
        ht_means = []

        for folio, stress in b_stress.items():
            if stress['execution_tension'] is None:
                continue

            windows = compute_ht_at_windows(folio, folio_order, unified)
            if windows and window_name in windows:
                b_tensions.append(stress['execution_tension'])
                ht_means.append(windows[window_name]['mean_ht'])

        if len(b_tensions) >= 5:
            r, p = stats.spearmanr(b_tensions, ht_means)
            results[window_name] = {
                'spearman_r': round(float(r), 3),
                'p_value': round(float(p), 4),
                'significant': bool(p < 0.05),
                'n_pairs': len(b_tensions),
                'interpretation': 'HT higher near stressed B' if r > 0 else 'HT lower near stressed B'
            }

    # Also test quire-level
    b_tensions = []
    quire_ht = []

    for folio, stress in b_stress.items():
        if stress['execution_tension'] is None:
            continue

        q_ht = compute_quire_ht(folio, unified)
        if q_ht:
            b_tensions.append(stress['execution_tension'])
            quire_ht.append(q_ht['mean_ht'])

    if len(b_tensions) >= 5:
        r, p = stats.spearmanr(b_tensions, quire_ht)
        results['quire_level'] = {
            'spearman_r': round(float(r), 3),
            'p_value': round(float(p), 4),
            'significant': bool(p < 0.05),
            'n_pairs': len(b_tensions),
            'interpretation': 'HT higher in quires with stressed B' if r > 0 else 'HT lower in quires with stressed B'
        }

    return results


def test_directional_relationship(b_stress, unified, folio_order):
    """
    Test: Does HT lead or lag B stress?
    Compare HT before vs HT after each B folio.
    """
    results = {'before': [], 'after': [], 'difference': []}

    for folio, stress in b_stress.items():
        if stress['execution_tension'] is None:
            continue

        try:
            idx = folio_order.index(folio)
        except ValueError:
            continue

        # Get HT before (up to 3 folios)
        before_folios = folio_order[max(0, idx-3):idx]
        after_folios = folio_order[idx+1:min(len(folio_order), idx+4)]

        before_ht = []
        for f in before_folios:
            if f in unified['profiles']:
                ht = unified['profiles'][f].get('ht_density')
                if ht is not None:
                    before_ht.append(ht)

        after_ht = []
        for f in after_folios:
            if f in unified['profiles']:
                ht = unified['profiles'][f].get('ht_density')
                if ht is not None:
                    after_ht.append(ht)

        if before_ht and after_ht:
            mean_before = np.mean(before_ht)
            mean_after = np.mean(after_ht)
            results['before'].append((stress['execution_tension'], mean_before))
            results['after'].append((stress['execution_tension'], mean_after))
            results['difference'].append((stress['execution_tension'], mean_after - mean_before))

    # Test correlations
    directional = {}

    if len(results['before']) >= 5:
        tensions = [x[0] for x in results['before']]
        ht_before = [x[1] for x in results['before']]
        ht_after = [x[1] for x in results['after']]
        ht_diff = [x[1] for x in results['difference']]

        r_before, p_before = stats.spearmanr(tensions, ht_before)
        r_after, p_after = stats.spearmanr(tensions, ht_after)
        r_diff, p_diff = stats.spearmanr(tensions, ht_diff)

        directional = {
            'ht_before_b': {
                'spearman_r': round(float(r_before), 3),
                'p_value': round(float(p_before), 4),
                'significant': bool(p_before < 0.05)
            },
            'ht_after_b': {
                'spearman_r': round(float(r_after), 3),
                'p_value': round(float(p_after), 4),
                'significant': bool(p_after < 0.05)
            },
            'ht_change_around_b': {
                'spearman_r': round(float(r_diff), 3),
                'p_value': round(float(p_diff), 4),
                'significant': bool(p_diff < 0.05),
                'interpretation': 'HT increases after stressed B' if r_diff > 0 else 'HT decreases after stressed B' if r_diff < 0 else 'No directional pattern'
            },
            'n_pairs': len(results['before'])
        }

        # Determine overall direction
        if directional['ht_before_b']['significant'] and not directional['ht_after_b']['significant']:
            directional['pattern'] = 'HT_ANTICIPATES_STRESS'
        elif directional['ht_after_b']['significant'] and not directional['ht_before_b']['significant']:
            directional['pattern'] = 'HT_FOLLOWS_STRESS'
        elif directional['ht_before_b']['significant'] and directional['ht_after_b']['significant']:
            directional['pattern'] = 'HT_SURROUNDS_STRESS'
        else:
            directional['pattern'] = 'NO_DIRECTIONAL_PATTERN'

    return directional


def analyze_hotspot_context(unified, folio_order):
    """
    For HT hotspots, analyze the surrounding B stress.
    """
    hotspots = []
    for folio, profile in unified['profiles'].items():
        if profile.get('ht_status') == 'HOTSPOT':
            hotspots.append(folio)

    results = {'hotspots': []}

    for hotspot in hotspots:
        try:
            idx = folio_order.index(hotspot)
        except ValueError:
            continue

        # Look for nearby B folios
        nearby = folio_order[max(0, idx-3):idx+4]
        nearby_b = []

        for f in nearby:
            if f == hotspot:
                continue
            profile = unified['profiles'].get(f)
            if profile and profile['system'] == 'B':
                tension = profile['burden_indices'].get('execution_tension')
                nearby_b.append({
                    'folio': f,
                    'position': 'before' if folio_order.index(f) < idx else 'after',
                    'distance': abs(folio_order.index(f) - idx),
                    'tension': tension
                })

        hotspot_data = {
            'hotspot': hotspot,
            'ht_density': unified['profiles'][hotspot].get('ht_density'),
            'system': unified['profiles'][hotspot].get('system'),
            'nearby_b_folios': nearby_b,
            'n_nearby_b': len(nearby_b)
        }

        # Compute mean tension of nearby B
        tensions = [b['tension'] for b in nearby_b if b['tension'] is not None]
        if tensions:
            hotspot_data['mean_nearby_b_tension'] = round(float(np.mean(tensions)), 3)

        results['hotspots'].append(hotspot_data)

    return results


def analyze_by_regime(b_stress, unified):
    """
    Does HT compensation differ by B regime?
    """
    by_regime = defaultdict(lambda: {'tensions': [], 'ht_local': []})

    for folio, stress in b_stress.items():
        if stress['execution_tension'] is None:
            continue

        regime = stress['regime']
        ht_local = unified['profiles'].get(folio, {}).get('ht_density', 0)

        by_regime[regime]['tensions'].append(stress['execution_tension'])
        by_regime[regime]['ht_local'].append(ht_local)

    results = {}
    for regime, data in sorted(by_regime.items()):
        if len(data['tensions']) >= 3:
            r, p = stats.spearmanr(data['tensions'], data['ht_local'])
            results[regime] = {
                'n_folios': len(data['tensions']),
                'mean_tension': round(float(np.mean(data['tensions'])), 3),
                'mean_ht': round(float(np.mean(data['ht_local'])), 4),
                'correlation': {
                    'spearman_r': round(float(r), 3),
                    'p_value': round(float(p), 4),
                    'significant': bool(p < 0.05)
                }
            }

    return results


def main():
    print("=" * 70)
    print("D3: HT Compensation Hypothesis")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    unified = load_json(UNIFIED_PROFILES)
    b_features = load_json(B_FEATURES)
    ht_features = load_json(HT_FEATURES)

    print(f"    Total folios: {len(unified['profiles'])}")

    # Get folio order
    folio_order = get_folio_order(unified)
    print(f"    Folio order established: {len(folio_order)} folios")

    # Compute B stress metrics
    print("\n[2] Computing B stress metrics...")
    b_stress = compute_b_stress_metrics(unified, b_features)
    print(f"    B folios with stress metrics: {len(b_stress)}")

    # Count by tension level
    high_tension = sum(1 for s in b_stress.values() if s['execution_tension'] and s['execution_tension'] > 0.5)
    low_tension = sum(1 for s in b_stress.values() if s['execution_tension'] and s['execution_tension'] < -0.5)
    print(f"    High tension (>0.5): {high_tension}")
    print(f"    Low tension (<-0.5): {low_tension}")

    # Test B stress -> HT correlation
    print("\n[3] Testing B stress -> HT correlation...")
    stress_ht_corr = test_b_stress_ht_correlation(b_stress, unified, folio_order)

    for window, result in stress_ht_corr.items():
        sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else ""
        print(f"    {window}: r={result['spearman_r']:.3f}, p={result['p_value']:.4f} {sig}")
        if result['significant']:
            print(f"      -> {result['interpretation']}")

    # Test directional relationship
    print("\n[4] Testing directional relationship (HT before vs after B)...")
    directional = test_directional_relationship(b_stress, unified, folio_order)

    if directional:
        print(f"    HT before B: r={directional['ht_before_b']['spearman_r']:.3f}, p={directional['ht_before_b']['p_value']:.4f}")
        print(f"    HT after B:  r={directional['ht_after_b']['spearman_r']:.3f}, p={directional['ht_after_b']['p_value']:.4f}")
        print(f"    Pattern: {directional['pattern']}")

    # Analyze hotspot context
    print("\n[5] Analyzing HT hotspot context...")
    hotspot_analysis = analyze_hotspot_context(unified, folio_order)

    print(f"    Hotspots analyzed: {len(hotspot_analysis['hotspots'])}")
    for hs in hotspot_analysis['hotspots'][:5]:  # Show first 5
        print(f"    {hs['hotspot']}: HT={hs['ht_density']:.3f}, system={hs['system']}, nearby_B={hs['n_nearby_b']}")
        if 'mean_nearby_b_tension' in hs:
            print(f"      Mean nearby B tension: {hs['mean_nearby_b_tension']:.3f}")

    # Analyze by regime
    print("\n[6] Analyzing by B regime...")
    regime_analysis = analyze_by_regime(b_stress, unified)

    for regime, data in sorted(regime_analysis.items()):
        sig = "*" if data['correlation']['significant'] else ""
        print(f"    {regime}: n={data['n_folios']}, tension={data['mean_tension']:.3f}, HT={data['mean_ht']:.4f}")
        print(f"      correlation: r={data['correlation']['spearman_r']:.3f} {sig}")

    # Key findings
    print("\n[7] Key findings...")
    findings = []

    # Check for significant window correlations
    sig_windows = [w for w, r in stress_ht_corr.items() if r['significant']]
    if sig_windows:
        findings.append({
            'finding': 'B stress correlates with nearby HT',
            'windows': sig_windows,
            'interpretation': 'HT density varies with B execution tension'
        })
    else:
        findings.append({
            'finding': 'No significant B stress -> HT correlation',
            'interpretation': 'HT and B stress appear independent at tested windows'
        })

    # Check directional pattern
    if directional and directional['pattern'] != 'NO_DIRECTIONAL_PATTERN':
        findings.append({
            'finding': f'Directional pattern: {directional["pattern"]}',
            'interpretation': 'HT shows temporal relationship with B stress'
        })

    # Check regime differences
    regime_corrs = [(r, d['correlation']['spearman_r']) for r, d in regime_analysis.items()]
    if len(regime_corrs) >= 2:
        corr_range = max(c for _, c in regime_corrs) - min(c for _, c in regime_corrs)
        if corr_range > 0.3:
            findings.append({
                'finding': 'Regime-dependent HT compensation',
                'corr_range': round(corr_range, 3),
                'interpretation': 'HT-stress relationship differs by B regime'
            })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[8] Saving output...")

    output = {
        'metadata': {
            'analysis': 'D3 - HT Compensation Hypothesis',
            'description': 'Testing if HT compensates for B stress',
            'n_b_folios': len(b_stress),
            'n_hotspots': len(hotspot_analysis['hotspots'])
        },
        'b_stress_summary': {
            'n_folios': len(b_stress),
            'high_tension': high_tension,
            'low_tension': low_tension
        },
        'stress_ht_correlation': stress_ht_corr,
        'directional_analysis': directional,
        'hotspot_context': hotspot_analysis,
        'regime_analysis': regime_analysis,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("D3 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
