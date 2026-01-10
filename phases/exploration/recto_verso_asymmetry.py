#!/usr/bin/env python3
"""
P2: Recto-Verso Asymmetry

Do bifolios systematically "load" stress on one side?

Questions:
1. Is HT density higher on recto or verso?
2. Is cognitive burden asymmetric across the spread?
3. Is there production ergonomics evidence?

Output: results/recto_verso_asymmetry.json
"""

import json
import re
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

# Output
OUTPUT = RESULTS / "recto_verso_asymmetry.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_folio_id(folio):
    """
    Parse folio ID to extract number and side.
    Returns: (number, side, subscript) or None
    """
    match = re.match(r'f(\d+)([rv])(\d*)', folio)
    if match:
        num = int(match.group(1))
        side = match.group(2)
        subscript = int(match.group(3)) if match.group(3) else 0
        return (num, side, subscript)
    return None


def find_recto_verso_pairs(unified):
    """
    Find all recto-verso pairs.
    A pair is (fNr, fNv) where N is the same.
    """
    by_number = defaultdict(dict)

    for folio, profile in unified['profiles'].items():
        parsed = parse_folio_id(folio)
        if parsed is None:
            continue

        num, side, subscript = parsed

        # Group by number and subscript
        key = (num, subscript)
        by_number[key][side] = folio

    # Find complete pairs
    pairs = []
    for key, sides in by_number.items():
        if 'r' in sides and 'v' in sides:
            pairs.append({
                'recto': sides['r'],
                'verso': sides['v'],
                'folio_number': key[0],
                'subscript': key[1]
            })

    return pairs


def compute_asymmetry_metrics(pairs, unified):
    """
    Compute asymmetry metrics for each pair.
    """
    results = []

    for pair in pairs:
        recto = pair['recto']
        verso = pair['verso']

        r_profile = unified['profiles'].get(recto)
        v_profile = unified['profiles'].get(verso)

        if not r_profile or not v_profile:
            continue

        # HT density
        r_ht = r_profile.get('ht_density', 0) or 0
        v_ht = v_profile.get('ht_density', 0) or 0
        ht_diff = r_ht - v_ht  # Positive = recto higher

        # Cognitive burden
        r_burden = r_profile.get('burden_indices', {}).get('cognitive_burden', 0) or 0
        v_burden = v_profile.get('burden_indices', {}).get('cognitive_burden', 0) or 0
        burden_diff = r_burden - v_burden

        # System match
        same_system = r_profile.get('system') == v_profile.get('system')

        # Execution tension (B only)
        r_tension = r_profile.get('burden_indices', {}).get('execution_tension')
        v_tension = v_profile.get('burden_indices', {}).get('execution_tension')
        tension_diff = None
        if r_tension is not None and v_tension is not None:
            tension_diff = r_tension - v_tension

        results.append({
            'pair': (recto, verso),
            'folio_number': pair['folio_number'],
            'same_system': same_system,
            'r_system': r_profile.get('system'),
            'v_system': v_profile.get('system'),
            'ht_diff': ht_diff,
            'r_ht': r_ht,
            'v_ht': v_ht,
            'burden_diff': burden_diff,
            'tension_diff': tension_diff
        })

    return results


def test_systematic_asymmetry(metrics):
    """
    Test if asymmetry is systematic.
    """
    # Filter to same-system pairs only (cleaner signal)
    same_sys = [m for m in metrics if m['same_system']]

    tests = {}

    # Test 1: Is HT systematically higher on one side?
    ht_diffs = [m['ht_diff'] for m in same_sys]
    if len(ht_diffs) >= 10:
        # Sign test: Are there more positive or negative differences?
        n_pos = sum(1 for d in ht_diffs if d > 0)
        n_neg = sum(1 for d in ht_diffs if d < 0)
        n_zero = sum(1 for d in ht_diffs if d == 0)

        # Wilcoxon signed-rank test
        non_zero_diffs = [d for d in ht_diffs if d != 0]
        if len(non_zero_diffs) >= 5:
            w_stat, w_p = stats.wilcoxon(non_zero_diffs, alternative='two-sided')
        else:
            w_stat, w_p = 0, 1.0

        tests['ht_asymmetry'] = {
            'n_pairs': len(ht_diffs),
            'mean_diff': round(float(np.mean(ht_diffs)), 4),
            'std_diff': round(float(np.std(ht_diffs)), 4),
            'n_recto_higher': n_pos,
            'n_verso_higher': n_neg,
            'n_equal': n_zero,
            'wilcoxon_stat': round(float(w_stat), 2),
            'wilcoxon_p': round(float(w_p), 4),
            'significant': bool(w_p < 0.05),
            'direction': 'RECTO_HIGHER' if np.mean(ht_diffs) > 0.01 else 'VERSO_HIGHER' if np.mean(ht_diffs) < -0.01 else 'NO_BIAS'
        }

    # Test 2: Burden asymmetry
    burden_diffs = [m['burden_diff'] for m in same_sys]
    if len(burden_diffs) >= 10:
        n_pos = sum(1 for d in burden_diffs if d > 0)
        n_neg = sum(1 for d in burden_diffs if d < 0)

        non_zero = [d for d in burden_diffs if abs(d) > 0.001]
        if len(non_zero) >= 5:
            w_stat, w_p = stats.wilcoxon(non_zero, alternative='two-sided')
        else:
            w_stat, w_p = 0, 1.0

        tests['burden_asymmetry'] = {
            'n_pairs': len(burden_diffs),
            'mean_diff': round(float(np.mean(burden_diffs)), 4),
            'n_recto_higher': n_pos,
            'n_verso_higher': n_neg,
            'wilcoxon_stat': round(float(w_stat), 2),
            'wilcoxon_p': round(float(w_p), 4),
            'significant': bool(w_p < 0.05),
            'direction': 'RECTO_HIGHER' if np.mean(burden_diffs) > 0.1 else 'VERSO_HIGHER' if np.mean(burden_diffs) < -0.1 else 'NO_BIAS'
        }

    # Test 3: Tension asymmetry (B pairs only)
    tension_diffs = [m['tension_diff'] for m in same_sys if m['tension_diff'] is not None]
    if len(tension_diffs) >= 5:
        n_pos = sum(1 for d in tension_diffs if d > 0)
        n_neg = sum(1 for d in tension_diffs if d < 0)

        non_zero = [d for d in tension_diffs if abs(d) > 0.001]
        if len(non_zero) >= 5:
            w_stat, w_p = stats.wilcoxon(non_zero, alternative='two-sided')
        else:
            w_stat, w_p = 0, 1.0

        tests['tension_asymmetry'] = {
            'n_pairs': len(tension_diffs),
            'mean_diff': round(float(np.mean(tension_diffs)), 3),
            'n_recto_higher': n_pos,
            'n_verso_higher': n_neg,
            'wilcoxon_stat': round(float(w_stat), 2),
            'wilcoxon_p': round(float(w_p), 4),
            'significant': bool(w_p < 0.05),
            'direction': 'RECTO_HIGHER' if np.mean(tension_diffs) > 0.2 else 'VERSO_HIGHER' if np.mean(tension_diffs) < -0.2 else 'NO_BIAS'
        }

    return tests


def analyze_by_system(metrics):
    """
    Check if asymmetry differs by system.
    """
    by_system = defaultdict(list)

    for m in metrics:
        if m['same_system']:
            by_system[m['r_system']].append(m)

    results = {}
    for system, sys_metrics in by_system.items():
        if len(sys_metrics) >= 5:
            ht_diffs = [m['ht_diff'] for m in sys_metrics]
            results[system] = {
                'n_pairs': len(sys_metrics),
                'mean_ht_diff': round(float(np.mean(ht_diffs)), 4),
                'std_ht_diff': round(float(np.std(ht_diffs)), 4),
                'recto_higher_pct': round(100 * sum(1 for d in ht_diffs if d > 0) / len(ht_diffs), 1),
                'direction': 'RECTO' if np.mean(ht_diffs) > 0.01 else 'VERSO' if np.mean(ht_diffs) < -0.01 else 'NONE'
            }

    return results


def find_extreme_pairs(metrics, n=5):
    """
    Find pairs with most extreme asymmetry.
    """
    sorted_by_ht = sorted(metrics, key=lambda m: abs(m['ht_diff']), reverse=True)

    extremes = []
    for m in sorted_by_ht[:n]:
        extremes.append({
            'recto': m['pair'][0],
            'verso': m['pair'][1],
            'r_system': m['r_system'],
            'v_system': m['v_system'],
            'ht_diff': round(m['ht_diff'], 4),
            'higher_side': 'recto' if m['ht_diff'] > 0 else 'verso',
            'r_ht': round(m['r_ht'], 4),
            'v_ht': round(m['v_ht'], 4)
        })

    return extremes


def main():
    print("=" * 70)
    print("P2: Recto-Verso Asymmetry")
    print("=" * 70)

    # Load data
    print("\n[1] Loading unified profiles...")
    unified = load_json(UNIFIED_PROFILES)
    print(f"    Total folios: {len(unified['profiles'])}")

    # Find pairs
    print("\n[2] Finding recto-verso pairs...")
    pairs = find_recto_verso_pairs(unified)
    print(f"    Complete pairs found: {len(pairs)}")

    # Compute metrics
    print("\n[3] Computing asymmetry metrics...")
    metrics = compute_asymmetry_metrics(pairs, unified)
    print(f"    Pairs with metrics: {len(metrics)}")

    same_sys = sum(1 for m in metrics if m['same_system'])
    diff_sys = len(metrics) - same_sys
    print(f"    Same-system pairs: {same_sys}")
    print(f"    Different-system pairs: {diff_sys}")

    # Test systematic asymmetry
    print("\n[4] Testing systematic asymmetry...")
    tests = test_systematic_asymmetry(metrics)

    for test_name, result in tests.items():
        print(f"\n    {test_name}:")
        print(f"      n_pairs: {result['n_pairs']}")
        print(f"      mean_diff: {result['mean_diff']}")
        print(f"      recto higher: {result['n_recto_higher']}, verso higher: {result['n_verso_higher']}")
        print(f"      Wilcoxon p: {result['wilcoxon_p']}")
        if result['significant']:
            print(f"      *** SIGNIFICANT: {result['direction']}")
        else:
            print(f"      Not significant")

    # By-system analysis
    print("\n[5] Analyzing by system...")
    by_system = analyze_by_system(metrics)

    for system, data in sorted(by_system.items()):
        print(f"    {system}: {data['n_pairs']} pairs, mean_diff={data['mean_ht_diff']:.4f}")
        print(f"      Recto higher: {data['recto_higher_pct']}%")

    # Extreme pairs
    print("\n[6] Finding extreme pairs...")
    extremes = find_extreme_pairs(metrics)

    for e in extremes:
        print(f"    {e['recto']} vs {e['verso']}: diff={e['ht_diff']:.4f} ({e['higher_side']} higher)")

    # Key findings
    print("\n[7] Key findings...")
    findings = []

    # Check for significant asymmetry
    if 'ht_asymmetry' in tests and tests['ht_asymmetry']['significant']:
        findings.append({
            'finding': f"HT systematically {tests['ht_asymmetry']['direction'].replace('_', ' ').lower()}",
            'p_value': tests['ht_asymmetry']['wilcoxon_p'],
            'interpretation': 'Production ergonomics or design intent'
        })
    else:
        findings.append({
            'finding': 'No systematic HT asymmetry',
            'interpretation': 'HT load balanced across spreads'
        })

    if 'tension_asymmetry' in tests and tests['tension_asymmetry']['significant']:
        findings.append({
            'finding': f"Execution tension {tests['tension_asymmetry']['direction'].replace('_', ' ').lower()}",
            'p_value': tests['tension_asymmetry']['wilcoxon_p'],
            'interpretation': 'B programs may have side preference'
        })

    # Check for system differences
    if len(by_system) >= 2:
        directions = [d['direction'] for d in by_system.values()]
        if len(set(directions)) > 1:
            findings.append({
                'finding': 'Asymmetry direction varies by system',
                'systems': {s: d['direction'] for s, d in by_system.items()},
                'interpretation': 'Different production patterns per system'
            })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[8] Saving output...")

    output = {
        'metadata': {
            'analysis': 'P2 - Recto-Verso Asymmetry',
            'description': 'Testing if spreads load stress asymmetrically',
            'n_pairs': len(pairs),
            'n_same_system': same_sys
        },
        'pair_metrics': [
            {
                'recto': m['pair'][0],
                'verso': m['pair'][1],
                'same_system': m['same_system'],
                'ht_diff': round(m['ht_diff'], 4),
                'burden_diff': round(m['burden_diff'], 4)
            }
            for m in metrics
        ],
        'asymmetry_tests': tests,
        'by_system': by_system,
        'extreme_pairs': extremes,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("P2 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
