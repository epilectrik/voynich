#!/usr/bin/env python3
"""
F-AZC-007: Position-Conditioned Escape Suppression

Question: Is escape suppression uniform or position-conditioned?

Method:
- Measure qo/ct frequency by placement code
- Test if suppression is:
  - Uniform across all placements -> AZC = global safety lock
  - Concentrated at boundaries (S0, S3, start/end) -> AZC = transition stabilizer
- Chi-squared test for uniform distribution

Why This Matters:
Refines F-AZC-004's legality-sieve mechanism. Determines if AZC filters everywhere or only at edges.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

# AZC family assignments
ZODIAC_FAMILY = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

# Escape prefixes
ESCAPE_PREFIXES = {'qo', 'ct'}

# Position classifications
BOUNDARY_PLACEMENTS_ZODIAC = {'S0', 'S3', 'R4'}  # Start/end positions
INTERIOR_PLACEMENTS_ZODIAC = {'R1', 'R2', 'R3', 'S1', 'S2'}

BOUNDARY_PLACEMENTS_AC = {'C', 'S'}  # C=early, S=late
INTERIOR_PLACEMENTS_AC = {'P', 'R'}  # Middle positions


def load_azc_tokens():
    """Load all AZC tokens with morphological decomposition."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if token and placement:
                        result = decompose_token(token)
                        if result[0]:  # Successfully decomposed
                            prefix = result[0]

                            if folio in ZODIAC_FAMILY:
                                family = 'zodiac'
                            elif folio in AC_FAMILY:
                                family = 'ac'
                            else:
                                family = 'unknown'

                            is_escape = prefix in ESCAPE_PREFIXES

                            tokens.append({
                                'token': token,
                                'folio': folio,
                                'family': family,
                                'placement': placement,
                                'prefix': prefix,
                                'is_escape': is_escape
                            })
    return tokens


def analyze_escape_by_placement(tokens, family_filter=None):
    """Analyze escape prefix distribution by placement code."""

    if family_filter:
        tokens = [t for t in tokens if t['family'] == family_filter]

    # Count escape vs non-escape by placement
    placement_counts = defaultdict(lambda: {'escape': 0, 'non_escape': 0, 'total': 0})

    for t in tokens:
        p = t['placement']
        placement_counts[p]['total'] += 1
        if t['is_escape']:
            placement_counts[p]['escape'] += 1
        else:
            placement_counts[p]['non_escape'] += 1

    # Calculate rates
    placement_rates = {}
    for p, counts in placement_counts.items():
        if counts['total'] >= 10:  # Minimum sample size
            escape_rate = counts['escape'] / counts['total'] * 100
            placement_rates[p] = {
                'escape': counts['escape'],
                'non_escape': counts['non_escape'],
                'total': counts['total'],
                'escape_rate': escape_rate
            }

    return placement_rates


def test_uniform_distribution(placement_rates):
    """Test if escape rate is uniform across placements."""

    if len(placement_rates) < 2:
        return {'insufficient_data': True}

    # Overall escape rate
    total_escape = sum(r['escape'] for r in placement_rates.values())
    total_all = sum(r['total'] for r in placement_rates.values())
    overall_rate = total_escape / total_all

    # Expected counts under uniform distribution
    observed = []
    expected = []

    for p, r in placement_rates.items():
        observed.append(r['escape'])
        expected.append(r['total'] * overall_rate)

    # Chi-squared test
    chi2, p_value = stats.chisquare(observed, expected)

    return {
        'overall_rate': overall_rate * 100,
        'chi_squared': float(chi2),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05),
        'n_placements': len(placement_rates)
    }


def classify_position_type(placement, family):
    """Classify placement as boundary or interior."""

    if family == 'zodiac':
        if placement in BOUNDARY_PLACEMENTS_ZODIAC:
            return 'boundary'
        elif placement in INTERIOR_PLACEMENTS_ZODIAC:
            return 'interior'
    else:  # A/C
        if placement in BOUNDARY_PLACEMENTS_AC:
            return 'boundary'
        elif placement in INTERIOR_PLACEMENTS_AC:
            return 'interior'

    return 'other'


def analyze_boundary_vs_interior(tokens, family_filter=None):
    """Compare escape rates between boundary and interior positions."""

    if family_filter:
        tokens = [t for t in tokens if t['family'] == family_filter]

    boundary_escape = 0
    boundary_total = 0
    interior_escape = 0
    interior_total = 0

    for t in tokens:
        pos_type = classify_position_type(t['placement'], t['family'])

        if pos_type == 'boundary':
            boundary_total += 1
            if t['is_escape']:
                boundary_escape += 1
        elif pos_type == 'interior':
            interior_total += 1
            if t['is_escape']:
                interior_escape += 1

    if boundary_total < 10 or interior_total < 10:
        return {'insufficient_data': True}

    boundary_rate = boundary_escape / boundary_total * 100
    interior_rate = interior_escape / interior_total * 100

    # Fisher's exact test
    contingency = [[boundary_escape, boundary_total - boundary_escape],
                   [interior_escape, interior_total - interior_escape]]
    odds_ratio, fisher_p = stats.fisher_exact(contingency)

    return {
        'boundary': {
            'escape': boundary_escape,
            'total': boundary_total,
            'rate': boundary_rate
        },
        'interior': {
            'escape': interior_escape,
            'total': interior_total,
            'rate': interior_rate
        },
        'odds_ratio': float(odds_ratio),
        'fisher_p': float(fisher_p),
        'significant': bool(fisher_p < 0.05),
        'interpretation': 'boundary_suppressed' if boundary_rate < interior_rate else 'interior_suppressed' if interior_rate < boundary_rate else 'uniform'
    }


def main():
    print("=" * 60)
    print("F-AZC-007: Position-Conditioned Escape Suppression")
    print("=" * 60)
    print()

    # Load data
    tokens = load_azc_tokens()

    escape_count = sum(1 for t in tokens if t['is_escape'])
    print(f"Total AZC tokens: {len(tokens)}")
    print(f"Escape tokens (qo, ct): {escape_count} ({escape_count/len(tokens)*100:.1f}%)")
    print()

    # Overall by family
    zodiac_tokens = [t for t in tokens if t['family'] == 'zodiac']
    ac_tokens = [t for t in tokens if t['family'] == 'ac']

    zodiac_escape = sum(1 for t in zodiac_tokens if t['is_escape'])
    ac_escape = sum(1 for t in ac_tokens if t['is_escape'])

    print(f"Zodiac: {zodiac_escape}/{len(zodiac_tokens)} escape ({zodiac_escape/len(zodiac_tokens)*100:.1f}%)")
    print(f"A/C: {ac_escape}/{len(ac_tokens)} escape ({ac_escape/len(ac_tokens)*100:.1f}%)")
    print()

    # ===========================================
    # Zodiac Analysis
    # ===========================================
    print("=" * 60)
    print("ZODIAC: Escape Rate by Placement")
    print("=" * 60)
    print()

    zodiac_rates = analyze_escape_by_placement(tokens, 'zodiac')

    print(f"{'Placement':<10} {'Escape':>8} {'Total':>8} {'Rate':>10}")
    print("-" * 40)
    for p in sorted(zodiac_rates.keys()):
        r = zodiac_rates[p]
        print(f"{p:<10} {r['escape']:>8} {r['total']:>8} {r['escape_rate']:>9.1f}%")
    print()

    zodiac_uniform = test_uniform_distribution(zodiac_rates)
    if 'insufficient_data' not in zodiac_uniform:
        print(f"Chi-squared test (uniform distribution):")
        print(f"  Overall rate: {zodiac_uniform['overall_rate']:.1f}%")
        print(f"  Chi-squared: {zodiac_uniform['chi_squared']:.2f}")
        print(f"  p-value: {zodiac_uniform['p_value']:.6f}")
        print(f"  Result: {'SIGNIFICANT - Non-uniform distribution ***' if zodiac_uniform['significant'] else 'NOT SIGNIFICANT - Uniform'}")
    print()

    zodiac_boundary = analyze_boundary_vs_interior(tokens, 'zodiac')
    if 'insufficient_data' not in zodiac_boundary:
        print(f"Boundary vs Interior comparison:")
        print(f"  Boundary rate: {zodiac_boundary['boundary']['rate']:.1f}% ({zodiac_boundary['boundary']['escape']}/{zodiac_boundary['boundary']['total']})")
        print(f"  Interior rate: {zodiac_boundary['interior']['rate']:.1f}% ({zodiac_boundary['interior']['escape']}/{zodiac_boundary['interior']['total']})")
        print(f"  Fisher's exact p: {zodiac_boundary['fisher_p']:.6f}")
        print(f"  Result: {'SIGNIFICANT ***' if zodiac_boundary['significant'] else 'NOT SIGNIFICANT'}")
    print()

    # ===========================================
    # A/C Analysis
    # ===========================================
    print("=" * 60)
    print("A/C: Escape Rate by Placement")
    print("=" * 60)
    print()

    ac_rates = analyze_escape_by_placement(tokens, 'ac')

    print(f"{'Placement':<10} {'Escape':>8} {'Total':>8} {'Rate':>10}")
    print("-" * 40)
    for p in sorted(ac_rates.keys()):
        r = ac_rates[p]
        print(f"{p:<10} {r['escape']:>8} {r['total']:>8} {r['escape_rate']:>9.1f}%")
    print()

    ac_uniform = test_uniform_distribution(ac_rates)
    if 'insufficient_data' not in ac_uniform:
        print(f"Chi-squared test (uniform distribution):")
        print(f"  Overall rate: {ac_uniform['overall_rate']:.1f}%")
        print(f"  Chi-squared: {ac_uniform['chi_squared']:.2f}")
        print(f"  p-value: {ac_uniform['p_value']:.6f}")
        print(f"  Result: {'SIGNIFICANT - Non-uniform distribution ***' if ac_uniform['significant'] else 'NOT SIGNIFICANT - Uniform'}")
    print()

    ac_boundary = analyze_boundary_vs_interior(tokens, 'ac')
    if 'insufficient_data' not in ac_boundary:
        print(f"Boundary vs Interior comparison:")
        print(f"  Boundary rate: {ac_boundary['boundary']['rate']:.1f}% ({ac_boundary['boundary']['escape']}/{ac_boundary['boundary']['total']})")
        print(f"  Interior rate: {ac_boundary['interior']['rate']:.1f}% ({ac_boundary['interior']['escape']}/{ac_boundary['interior']['total']})")
        print(f"  Fisher's exact p: {ac_boundary['fisher_p']:.6f}")
        print(f"  Result: {'SIGNIFICANT ***' if ac_boundary['significant'] else 'NOT SIGNIFICANT'}")
    print()

    # ===========================================
    # Overall Interpretation
    # ===========================================
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    # Determine pattern
    zodiac_nonuniform = zodiac_uniform.get('significant', False)
    ac_nonuniform = ac_uniform.get('significant', False)
    zodiac_boundary_diff = zodiac_boundary.get('significant', False) if 'insufficient_data' not in zodiac_boundary else False
    ac_boundary_diff = ac_boundary.get('significant', False) if 'insufficient_data' not in ac_boundary else False

    evidence_count = sum([zodiac_nonuniform, ac_nonuniform, zodiac_boundary_diff, ac_boundary_diff])

    print(f"Evidence for position-conditioned suppression: {evidence_count}/4")
    print(f"  - Zodiac non-uniform distribution: {'YES' if zodiac_nonuniform else 'NO'}")
    print(f"  - A/C non-uniform distribution: {'YES' if ac_nonuniform else 'NO'}")
    print(f"  - Zodiac boundary/interior difference: {'YES' if zodiac_boundary_diff else 'NO'}")
    print(f"  - A/C boundary/interior difference: {'YES' if ac_boundary_diff else 'NO'}")
    print()

    if evidence_count >= 2:
        conclusion = "Escape suppression is POSITION-CONDITIONED"
        mechanism = "AZC = TRANSITION STABILIZER (filters selectively by position)"
        fit_tier = "F2"
    elif evidence_count == 1:
        conclusion = "Escape suppression shows WEAK position conditioning"
        mechanism = "AZC = PARTIAL POSITION CONDITIONING"
        fit_tier = "F3"
    else:
        conclusion = "Escape suppression is UNIFORM across positions"
        mechanism = "AZC = GLOBAL SAFETY LOCK (filters everywhere equally)"
        fit_tier = "F2"  # Still informative

    print(f"CONCLUSION: {conclusion}")
    print(f"MECHANISM: {mechanism}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-007',
        'question': 'Is escape suppression uniform or position-conditioned?',
        'metadata': {
            'total_tokens': len(tokens),
            'escape_tokens': escape_count,
            'escape_rate': round(escape_count / len(tokens) * 100, 2)
        },
        'zodiac': {
            'placement_rates': {k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in zodiac_rates.items()},
            'uniform_test': {k: round(v, 4) if isinstance(v, float) else v for k, v in zodiac_uniform.items()} if 'insufficient_data' not in zodiac_uniform else zodiac_uniform,
            'boundary_test': {k: round(v, 4) if isinstance(v, float) else (
                {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} if isinstance(v, dict) else v
            ) for k, v in zodiac_boundary.items()} if 'insufficient_data' not in zodiac_boundary else zodiac_boundary
        },
        'ac': {
            'placement_rates': {k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in ac_rates.items()},
            'uniform_test': {k: round(v, 4) if isinstance(v, float) else v for k, v in ac_uniform.items()} if 'insufficient_data' not in ac_uniform else ac_uniform,
            'boundary_test': {k: round(v, 4) if isinstance(v, float) else (
                {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} if isinstance(v, dict) else v
            ) for k, v in ac_boundary.items()} if 'insufficient_data' not in ac_boundary else ac_boundary
        },
        'evidence': {
            'zodiac_nonuniform': zodiac_nonuniform,
            'ac_nonuniform': ac_nonuniform,
            'zodiac_boundary_diff': zodiac_boundary_diff,
            'ac_boundary_diff': ac_boundary_diff,
            'evidence_count': evidence_count
        },
        'interpretation': {
            'conclusion': conclusion,
            'mechanism': mechanism,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_escape_by_position.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
