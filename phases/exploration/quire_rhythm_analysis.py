#!/usr/bin/env python3
"""
E1: Quire Rhythm Alignment

Does HT oscillation align with quire boundaries, or is it independent?

Questions:
1. Are HT changepoints more likely at quire boundaries?
2. Do quires have characteristic HT profiles?
3. Is HT rhythm production-driven or content-driven?

Output: results/quire_rhythm_analysis.json
"""

import json
import re
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

# Input
UNIFIED_PROFILES = RESULTS / "unified_folio_profiles.json"
HT_TEMPORAL = RESULTS / "ht_temporal_dynamics.json"

# Output
OUTPUT = RESULTS / "quire_rhythm_analysis.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_folio_order(unified):
    """Get manuscript order of folios."""
    folios = list(unified['profiles'].keys())

    def folio_sort_key(f):
        match = re.match(r'f(\d+)([rv]?)(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1 if match.group(2) == 'v' else 0
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)

    return sorted(folios, key=folio_sort_key)


def get_quire_boundaries(unified, folio_order):
    """
    Find quire boundaries in manuscript order.
    Returns list of (boundary_position, quire_before, quire_after)
    """
    boundaries = []
    prev_quire = None

    for i, folio in enumerate(folio_order):
        quire = unified['profiles'].get(folio, {}).get('quire')
        if prev_quire is not None and quire != prev_quire:
            boundaries.append({
                'position': i,
                'folio_before': folio_order[i-1] if i > 0 else None,
                'folio_after': folio,
                'quire_before': prev_quire,
                'quire_after': quire
            })
        prev_quire = quire

    return boundaries


def build_quire_ht_profiles(unified, folio_order):
    """
    Build HT profile for each quire.
    """
    by_quire = defaultdict(list)

    for i, folio in enumerate(folio_order):
        profile = unified['profiles'].get(folio, {})
        quire = profile.get('quire')
        ht = profile.get('ht_density', 0)

        if quire and ht is not None:
            by_quire[quire].append({
                'folio': folio,
                'position': i,
                'ht': ht
            })

    profiles = {}
    for quire, folios in sorted(by_quire.items()):
        if len(folios) < 2:
            continue

        ht_values = [f['ht'] for f in folios]
        positions = list(range(len(folios)))

        # Compute profile statistics
        profiles[quire] = {
            'n_folios': len(folios),
            'first_folio': folios[0]['folio'],
            'last_folio': folios[-1]['folio'],
            'ht_mean': round(float(np.mean(ht_values)), 4),
            'ht_std': round(float(np.std(ht_values)), 4),
            'ht_first': round(float(ht_values[0]), 4),
            'ht_last': round(float(ht_values[-1]), 4),
            'ht_trend': round(float(ht_values[-1] - ht_values[0]), 4),
            'folios': folios
        }

        # Internal trend correlation
        if len(positions) >= 3:
            r, p = stats.spearmanr(positions, ht_values)
            profiles[quire]['internal_trend'] = {
                'spearman_r': round(float(r), 3),
                'p_value': round(float(p), 4),
                'direction': 'INCREASING' if r > 0.3 else 'DECREASING' if r < -0.3 else 'FLAT'
            }

    return profiles


def test_changepoint_alignment(ht_temporal, quire_boundaries, folio_order):
    """
    Test if HT changepoints align with quire boundaries.
    """
    changepoints = ht_temporal.get('changepoints', {}).get('changepoints', [])

    if not changepoints:
        return {'error': 'No changepoints in temporal data'}

    # Get changepoint positions
    cp_positions = set(cp['position'] for cp in changepoints)

    # Get quire boundary positions
    boundary_positions = set(b['position'] for b in quire_boundaries)

    # How many changepoints are at or near (±2) boundaries?
    near_boundary = 0
    for cp_pos in cp_positions:
        for b_pos in boundary_positions:
            if abs(cp_pos - b_pos) <= 2:
                near_boundary += 1
                break

    # Expected by chance
    n_total = len(folio_order)
    n_boundaries = len(boundary_positions)
    n_changepoints = len(cp_positions)

    # Probability of being within ±2 of a boundary by chance
    boundary_coverage = min(1.0, (n_boundaries * 5) / n_total)  # 5 positions per boundary (±2)
    expected = n_changepoints * boundary_coverage

    # Chi-squared test
    observed = [near_boundary, n_changepoints - near_boundary]
    expected_vals = [expected, n_changepoints - expected]

    if expected > 0 and n_changepoints - expected > 0:
        chi2, p_value = stats.chisquare(observed, expected_vals)
    else:
        chi2, p_value = 0, 1.0

    return {
        'n_changepoints': n_changepoints,
        'n_boundaries': n_boundaries,
        'near_boundary': near_boundary,
        'expected_by_chance': round(float(expected), 2),
        'enrichment': round(near_boundary / expected, 2) if expected > 0 else 0,
        'chi2': round(float(chi2), 2),
        'p_value': round(float(p_value), 4),
        'significant': bool(p_value < 0.05),
        'interpretation': 'ALIGNED' if near_boundary > expected * 1.5 and p_value < 0.05 else 'INDEPENDENT'
    }


def test_boundary_ht_discontinuity(unified, quire_boundaries):
    """
    Test if HT shows discontinuity at quire boundaries.
    """
    boundary_jumps = []
    internal_jumps = []

    folio_order = get_folio_order(unified)

    # Get HT values
    ht_by_pos = {}
    for i, folio in enumerate(folio_order):
        ht = unified['profiles'].get(folio, {}).get('ht_density', 0)
        ht_by_pos[i] = ht

    boundary_positions = set(b['position'] for b in quire_boundaries)

    # Compare consecutive folios
    for i in range(1, len(folio_order)):
        jump = abs(ht_by_pos.get(i, 0) - ht_by_pos.get(i-1, 0))
        if i in boundary_positions:
            boundary_jumps.append(jump)
        else:
            internal_jumps.append(jump)

    if not boundary_jumps or not internal_jumps:
        return {'error': 'Insufficient data'}

    # Compare distributions
    u_stat, p_value = stats.mannwhitneyu(boundary_jumps, internal_jumps, alternative='greater')

    return {
        'n_boundary_jumps': len(boundary_jumps),
        'n_internal_jumps': len(internal_jumps),
        'mean_boundary_jump': round(float(np.mean(boundary_jumps)), 4),
        'mean_internal_jump': round(float(np.mean(internal_jumps)), 4),
        'ratio': round(np.mean(boundary_jumps) / np.mean(internal_jumps), 2) if np.mean(internal_jumps) > 0 else 0,
        'u_statistic': round(float(u_stat), 2),
        'p_value': round(float(p_value), 4),
        'significant': bool(p_value < 0.05),
        'interpretation': 'DISCONTINUOUS' if p_value < 0.05 else 'CONTINUOUS'
    }


def analyze_quire_level_ht(quire_profiles):
    """
    Analyze HT variation at quire level.
    """
    quire_means = [(q, p['ht_mean']) for q, p in quire_profiles.items()]
    quire_means = sorted(quire_means, key=lambda x: x[1], reverse=True)

    # Variance analysis
    means = [p['ht_mean'] for p in quire_profiles.values()]
    stds = [p['ht_std'] for p in quire_profiles.values()]

    # Kruskal-Wallis: do quires differ in HT?
    quire_ht_lists = []
    for q, p in quire_profiles.items():
        if 'folios' in p:
            quire_ht_lists.append([f['ht'] for f in p['folios']])

    if len(quire_ht_lists) >= 3:
        h_stat, p_value = stats.kruskal(*quire_ht_lists)
        n_total = sum(len(g) for g in quire_ht_lists)
        eta_sq = (h_stat - len(quire_ht_lists) + 1) / (n_total - len(quire_ht_lists))
    else:
        h_stat, p_value, eta_sq = 0, 1.0, 0

    return {
        'n_quires': len(quire_profiles),
        'highest_ht_quire': quire_means[0] if quire_means else None,
        'lowest_ht_quire': quire_means[-1] if quire_means else None,
        'ht_mean_range': round(float(max(means) - min(means)), 4) if means else 0,
        'between_quire_variance': {
            'h_statistic': round(float(h_stat), 2),
            'p_value': round(float(p_value), 4),
            'eta_squared': round(float(max(0, eta_sq)), 3),
            'significant': bool(p_value < 0.05)
        },
        'ranking': [(q, round(m, 4)) for q, m in quire_means[:5]]
    }


def analyze_quire_internal_patterns(quire_profiles):
    """
    Look for consistent internal patterns within quires.
    """
    patterns = {
        'front_loaded': 0,  # HT higher at start
        'back_loaded': 0,   # HT higher at end
        'flat': 0,          # No clear pattern
        'increasing': 0,    # Trend up
        'decreasing': 0     # Trend down
    }

    for quire, profile in quire_profiles.items():
        if 'internal_trend' not in profile:
            continue

        direction = profile['internal_trend']['direction']
        if direction == 'INCREASING':
            patterns['increasing'] += 1
        elif direction == 'DECREASING':
            patterns['decreasing'] += 1
        else:
            patterns['flat'] += 1

        # Front vs back loaded
        if profile['ht_first'] > profile['ht_last'] + 0.02:
            patterns['front_loaded'] += 1
        elif profile['ht_last'] > profile['ht_first'] + 0.02:
            patterns['back_loaded'] += 1

    total = sum(patterns.values())
    if total > 0:
        dominant = max(patterns.items(), key=lambda x: x[1])
        consistency = dominant[1] / total
    else:
        dominant = ('unknown', 0)
        consistency = 0

    return {
        'patterns': patterns,
        'dominant_pattern': dominant[0],
        'consistency': round(float(consistency), 2),
        'interpretation': f'{dominant[0].upper()} is most common ({dominant[1]}/{total})' if total > 0 else 'No data'
    }


def main():
    print("=" * 70)
    print("E1: Quire Rhythm Alignment")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    unified = load_json(UNIFIED_PROFILES)
    ht_temporal = load_json(HT_TEMPORAL)
    folio_order = get_folio_order(unified)

    print(f"    Total folios: {len(folio_order)}")

    # Get quire boundaries
    print("\n[2] Finding quire boundaries...")
    boundaries = get_quire_boundaries(unified, folio_order)
    print(f"    Quire boundaries found: {len(boundaries)}")

    for b in boundaries[:5]:
        print(f"      {b['quire_before']} -> {b['quire_after']} at {b['folio_after']}")

    # Build quire profiles
    print("\n[3] Building quire HT profiles...")
    quire_profiles = build_quire_ht_profiles(unified, folio_order)
    print(f"    Quires with profiles: {len(quire_profiles)}")

    for quire in sorted(quire_profiles.keys())[:5]:
        p = quire_profiles[quire]
        print(f"      {quire}: mean={p['ht_mean']:.3f}, n={p['n_folios']}, trend={p['ht_trend']:.3f}")

    # Test changepoint alignment
    print("\n[4] Testing changepoint alignment...")
    cp_alignment = test_changepoint_alignment(ht_temporal, boundaries, folio_order)

    if 'error' not in cp_alignment:
        print(f"    Changepoints: {cp_alignment['n_changepoints']}")
        print(f"    Near boundaries: {cp_alignment['near_boundary']} (expected: {cp_alignment['expected_by_chance']:.1f})")
        print(f"    Enrichment: {cp_alignment['enrichment']:.2f}x")
        print(f"    p-value: {cp_alignment['p_value']:.4f}")
        print(f"    Result: {cp_alignment['interpretation']}")

    # Test boundary discontinuity
    print("\n[5] Testing boundary HT discontinuity...")
    discontinuity = test_boundary_ht_discontinuity(unified, boundaries)

    if 'error' not in discontinuity:
        print(f"    Mean boundary jump: {discontinuity['mean_boundary_jump']:.4f}")
        print(f"    Mean internal jump: {discontinuity['mean_internal_jump']:.4f}")
        print(f"    Ratio: {discontinuity['ratio']:.2f}x")
        print(f"    p-value: {discontinuity['p_value']:.4f}")
        print(f"    Result: {discontinuity['interpretation']}")

    # Quire-level analysis
    print("\n[6] Analyzing quire-level HT variation...")
    quire_analysis = analyze_quire_level_ht(quire_profiles)

    print(f"    Highest HT quire: {quire_analysis['highest_ht_quire']}")
    print(f"    Lowest HT quire: {quire_analysis['lowest_ht_quire']}")
    print(f"    Between-quire variance: H={quire_analysis['between_quire_variance']['h_statistic']:.1f}, p={quire_analysis['between_quire_variance']['p_value']:.4f}")
    if quire_analysis['between_quire_variance']['significant']:
        print(f"    *** QUIRES DIFFER SIGNIFICANTLY IN HT ***")

    # Internal pattern analysis
    print("\n[7] Analyzing quire internal patterns...")
    internal_patterns = analyze_quire_internal_patterns(quire_profiles)

    print(f"    Patterns: {internal_patterns['patterns']}")
    print(f"    Dominant: {internal_patterns['dominant_pattern']} ({internal_patterns['consistency']:.0%} consistency)")

    # Key findings
    print("\n[8] Key findings...")
    findings = []

    # Changepoint alignment
    if 'error' not in cp_alignment:
        if cp_alignment['significant'] and cp_alignment['enrichment'] > 1.5:
            findings.append({
                'finding': 'HT changepoints align with quire boundaries',
                'enrichment': cp_alignment['enrichment'],
                'p_value': cp_alignment['p_value'],
                'interpretation': 'HT rhythm is PRODUCTION-DRIVEN (physical chunking)'
            })
        else:
            findings.append({
                'finding': 'HT changepoints do NOT align with quire boundaries',
                'enrichment': cp_alignment['enrichment'],
                'p_value': cp_alignment['p_value'],
                'interpretation': 'HT rhythm is CONTENT-DRIVEN (functional pacing)'
            })

    # Boundary discontinuity
    if 'error' not in discontinuity:
        if discontinuity['significant']:
            findings.append({
                'finding': 'HT shows discontinuity at quire boundaries',
                'ratio': discontinuity['ratio'],
                'interpretation': 'Quires are HT-distinct units'
            })

    # Quire-level variance
    if quire_analysis['between_quire_variance']['significant']:
        findings.append({
            'finding': 'Quires have distinct HT levels',
            'eta_squared': quire_analysis['between_quire_variance']['eta_squared'],
            'interpretation': 'Some quires are HT-heavy, others HT-light'
        })

    # Internal patterns
    if internal_patterns['consistency'] > 0.5:
        findings.append({
            'finding': f'{internal_patterns["dominant_pattern"].upper()} is dominant internal pattern',
            'consistency': internal_patterns['consistency'],
            'interpretation': f'Within quires, HT tends to be {internal_patterns["dominant_pattern"]}'
        })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[9] Saving output...")

    output = {
        'metadata': {
            'analysis': 'E1 - Quire Rhythm Alignment',
            'description': 'Testing if HT oscillation aligns with quire structure',
            'n_folios': len(folio_order),
            'n_boundaries': len(boundaries),
            'n_quires': len(quire_profiles)
        },
        'quire_boundaries': boundaries,
        'quire_profiles': {q: {k: v for k, v in p.items() if k != 'folios'} for q, p in quire_profiles.items()},
        'changepoint_alignment': cp_alignment,
        'boundary_discontinuity': discontinuity,
        'quire_level_analysis': quire_analysis,
        'internal_patterns': internal_patterns,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("E1 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
