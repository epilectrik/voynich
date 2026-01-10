#!/usr/bin/env python3
"""
E2: Zero-Escape Characterization

Are zero-escape B folios deliberate stress tests or accidents?

Questions:
1. How many B folios have zero or near-zero escape density?
2. Are they clustered or distributed?
3. What else characterizes them (regime, hazard, position)?
4. Are they intentional design choices?

Output: results/zero_escape_characterization.json
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
B_FEATURES = RESULTS / "b_macro_scaffold_audit.json"

# Output
OUTPUT = RESULTS / "zero_escape_characterization.json"


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


def identify_zero_escape_folios(unified, threshold=0.01):
    """
    Find all B folios with escape_density <= threshold.
    """
    zero_escape = []

    for folio, profile in unified['profiles'].items():
        if profile.get('system') != 'B':
            continue

        b_metrics = profile.get('b_metrics', {})
        if not b_metrics:
            continue

        escape = b_metrics.get('escape_density', 0)
        if escape <= threshold:
            zero_escape.append({
                'folio': folio,
                'escape_density': escape,
                'hazard_density': b_metrics.get('hazard_density', 0),
                'regime': b_metrics.get('regime'),
                'ht_density': profile.get('ht_density', 0),
                'ht_status': profile.get('ht_status'),
                'quire': profile.get('quire'),
                'tension': profile['burden_indices'].get('execution_tension')
            })

    return sorted(zero_escape, key=lambda x: x['escape_density'])


def analyze_distribution(zero_escape, unified, folio_order):
    """
    Analyze the distribution of zero-escape folios.
    """
    # Get positions
    positions = []
    for ze in zero_escape:
        try:
            pos = folio_order.index(ze['folio'])
            positions.append(pos)
        except ValueError:
            pass

    if not positions:
        return {'error': 'No positions found'}

    n_total = len(folio_order)

    # Position statistics
    early_third = [p for p in positions if p < n_total / 3]
    middle_third = [p for p in positions if n_total / 3 <= p < 2 * n_total / 3]
    late_third = [p for p in positions if p >= 2 * n_total / 3]

    # Clustering analysis - are they close together?
    gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)] if len(positions) > 1 else []
    mean_gap = np.mean(gaps) if gaps else 0
    expected_gap = n_total / (len(positions) + 1) if positions else 0

    return {
        'n_zero_escape': len(zero_escape),
        'positions': positions,
        'position_distribution': {
            'early_third': len(early_third),
            'middle_third': len(middle_third),
            'late_third': len(late_third)
        },
        'clustering': {
            'mean_gap': round(float(mean_gap), 1) if mean_gap else None,
            'expected_gap': round(float(expected_gap), 1),
            'clustering_ratio': round(expected_gap / mean_gap, 2) if mean_gap > 0 else 0,
            'interpretation': 'CLUSTERED' if mean_gap > 0 and expected_gap / mean_gap > 1.5 else 'DISTRIBUTED'
        }
    }


def analyze_regime_distribution(zero_escape, unified):
    """
    Check if zero-escape folios cluster in specific regimes.
    """
    # Get regime distribution for zero-escape
    ze_regimes = Counter(ze['regime'] for ze in zero_escape if ze['regime'])

    # Get regime distribution for all B folios
    all_regimes = Counter()
    for folio, profile in unified['profiles'].items():
        if profile.get('system') == 'B':
            b_metrics = profile.get('b_metrics', {})
            regime = b_metrics.get('regime')
            if regime:
                all_regimes[regime] += 1

    # Compute enrichment
    enrichment = {}
    for regime in all_regimes:
        ze_count = ze_regimes.get(regime, 0)
        all_count = all_regimes[regime]
        expected = len(zero_escape) * (all_count / sum(all_regimes.values())) if sum(all_regimes.values()) > 0 else 0

        enrichment[regime] = {
            'zero_escape_count': ze_count,
            'total_in_regime': all_count,
            'expected': round(float(expected), 1),
            'enrichment': round(ze_count / expected, 2) if expected > 0 else 0,
            'enriched': ze_count > expected * 1.5
        }

    return {
        'zero_escape_regimes': dict(ze_regimes),
        'all_b_regimes': dict(all_regimes),
        'enrichment_by_regime': enrichment
    }


def analyze_ht_relationship(zero_escape, unified):
    """
    Analyze relationship between zero-escape and HT.
    """
    # Compare HT in zero-escape vs other B folios
    ze_ht = [ze['ht_density'] for ze in zero_escape if ze['ht_density']]
    other_ht = []

    for folio, profile in unified['profiles'].items():
        if profile.get('system') != 'B':
            continue
        b_metrics = profile.get('b_metrics', {})
        escape = b_metrics.get('escape_density', 0)
        if escape > 0.01:  # Not zero-escape
            ht = profile.get('ht_density', 0)
            if ht:
                other_ht.append(ht)

    if not ze_ht or not other_ht:
        return {'error': 'Insufficient data'}

    # Mann-Whitney test
    u_stat, p_value = stats.mannwhitneyu(ze_ht, other_ht, alternative='greater')

    # Count hotspots
    ze_hotspots = sum(1 for ze in zero_escape if ze['ht_status'] == 'HOTSPOT')

    return {
        'zero_escape_mean_ht': round(float(np.mean(ze_ht)), 4),
        'other_b_mean_ht': round(float(np.mean(other_ht)), 4),
        'ratio': round(np.mean(ze_ht) / np.mean(other_ht), 2) if np.mean(other_ht) > 0 else 0,
        'u_statistic': round(float(u_stat), 2),
        'p_value': round(float(p_value), 4),
        'significant': bool(p_value < 0.05),
        'n_hotspots': ze_hotspots,
        'hotspot_rate': round(ze_hotspots / len(zero_escape), 2) if zero_escape else 0,
        'interpretation': 'ZERO-ESCAPE HAS HIGHER HT' if p_value < 0.05 else 'NO SIGNIFICANT DIFFERENCE'
    }


def analyze_hazard_relationship(zero_escape, unified):
    """
    Analyze relationship between zero-escape and hazard.
    """
    ze_hazard = [ze['hazard_density'] for ze in zero_escape if ze['hazard_density']]
    other_hazard = []

    for folio, profile in unified['profiles'].items():
        if profile.get('system') != 'B':
            continue
        b_metrics = profile.get('b_metrics', {})
        escape = b_metrics.get('escape_density', 0)
        if escape > 0.01:
            hazard = b_metrics.get('hazard_density', 0)
            if hazard:
                other_hazard.append(hazard)

    if not ze_hazard or not other_hazard:
        return {'error': 'Insufficient data'}

    # Mann-Whitney test
    u_stat, p_value = stats.mannwhitneyu(ze_hazard, other_hazard, alternative='two-sided')

    return {
        'zero_escape_mean_hazard': round(float(np.mean(ze_hazard)), 4),
        'other_b_mean_hazard': round(float(np.mean(other_hazard)), 4),
        'ratio': round(np.mean(ze_hazard) / np.mean(other_hazard), 2) if np.mean(other_hazard) > 0 else 0,
        'u_statistic': round(float(u_stat), 2),
        'p_value': round(float(p_value), 4),
        'significant': bool(p_value < 0.05),
        'interpretation': 'DIFFERENT HAZARD' if p_value < 0.05 else 'SIMILAR HAZARD'
    }


def analyze_neighbors(zero_escape, unified, folio_order):
    """
    Analyze what folios neighbor zero-escape pages.
    """
    neighbor_analysis = []

    for ze in zero_escape:
        folio = ze['folio']
        try:
            pos = folio_order.index(folio)
        except ValueError:
            continue

        # Get neighbors
        before = folio_order[pos-1] if pos > 0 else None
        after = folio_order[pos+1] if pos < len(folio_order)-1 else None

        before_profile = unified['profiles'].get(before, {}) if before else {}
        after_profile = unified['profiles'].get(after, {}) if after else {}

        neighbor_analysis.append({
            'folio': folio,
            'position': pos,
            'before': {
                'folio': before,
                'system': before_profile.get('system'),
                'ht': before_profile.get('ht_density')
            } if before else None,
            'after': {
                'folio': after,
                'system': after_profile.get('system'),
                'ht': after_profile.get('ht_density')
            } if after else None
        })

    # Summary statistics
    before_systems = Counter(n['before']['system'] for n in neighbor_analysis if n['before'])
    after_systems = Counter(n['after']['system'] for n in neighbor_analysis if n['after'])

    return {
        'n_analyzed': len(neighbor_analysis),
        'before_systems': dict(before_systems),
        'after_systems': dict(after_systems),
        'details': neighbor_analysis
    }


def main():
    print("=" * 70)
    print("E2: Zero-Escape Characterization")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    unified = load_json(UNIFIED_PROFILES)
    b_features = load_json(B_FEATURES)
    folio_order = get_folio_order(unified)

    b_folios = sum(1 for p in unified['profiles'].values() if p.get('system') == 'B')
    print(f"    B folios: {b_folios}")

    # Identify zero-escape folios
    print("\n[2] Identifying zero-escape folios...")
    zero_escape = identify_zero_escape_folios(unified, threshold=0.01)
    print(f"    Zero-escape folios (threshold 0.01): {len(zero_escape)}")

    print("\n    Zero-escape folios:")
    for ze in zero_escape:
        print(f"      {ze['folio']}: escape={ze['escape_density']:.4f}, hazard={ze['hazard_density']:.4f}, "
              f"regime={ze['regime']}, HT={ze['ht_density']:.3f} ({ze['ht_status']})")

    # Analyze distribution
    print("\n[3] Analyzing distribution...")
    distribution = analyze_distribution(zero_escape, unified, folio_order)

    if 'error' not in distribution:
        print(f"    Position distribution: {distribution['position_distribution']}")
        print(f"    Clustering: {distribution['clustering']['interpretation']}")
        print(f"      Mean gap: {distribution['clustering']['mean_gap']} (expected: {distribution['clustering']['expected_gap']})")

    # Analyze regime distribution
    print("\n[4] Analyzing regime distribution...")
    regime_analysis = analyze_regime_distribution(zero_escape, unified)

    print(f"    Zero-escape by regime: {regime_analysis['zero_escape_regimes']}")
    print(f"    All B by regime: {regime_analysis['all_b_regimes']}")
    print("    Enrichment:")
    for regime, data in regime_analysis['enrichment_by_regime'].items():
        marker = " **ENRICHED**" if data['enriched'] else ""
        print(f"      {regime}: {data['zero_escape_count']}/{data['total_in_regime']} ({data['enrichment']:.2f}x){marker}")

    # Analyze HT relationship
    print("\n[5] Analyzing HT relationship...")
    ht_analysis = analyze_ht_relationship(zero_escape, unified)

    if 'error' not in ht_analysis:
        print(f"    Zero-escape mean HT: {ht_analysis['zero_escape_mean_ht']:.4f}")
        print(f"    Other B mean HT: {ht_analysis['other_b_mean_ht']:.4f}")
        print(f"    Ratio: {ht_analysis['ratio']:.2f}x")
        print(f"    p-value: {ht_analysis['p_value']:.4f}")
        print(f"    Hotspots: {ht_analysis['n_hotspots']}/{len(zero_escape)} ({ht_analysis['hotspot_rate']:.0%})")
        print(f"    Result: {ht_analysis['interpretation']}")

    # Analyze hazard relationship
    print("\n[6] Analyzing hazard relationship...")
    hazard_analysis = analyze_hazard_relationship(zero_escape, unified)

    if 'error' not in hazard_analysis:
        print(f"    Zero-escape mean hazard: {hazard_analysis['zero_escape_mean_hazard']:.4f}")
        print(f"    Other B mean hazard: {hazard_analysis['other_b_mean_hazard']:.4f}")
        print(f"    Ratio: {hazard_analysis['ratio']:.2f}x")
        print(f"    Result: {hazard_analysis['interpretation']}")

    # Analyze neighbors
    print("\n[7] Analyzing neighbors...")
    neighbor_analysis = analyze_neighbors(zero_escape, unified, folio_order)

    print(f"    Before systems: {neighbor_analysis['before_systems']}")
    print(f"    After systems: {neighbor_analysis['after_systems']}")

    # Key findings
    print("\n[8] Key findings...")
    findings = []

    # How many zero-escape?
    if len(zero_escape) > 0:
        pct = 100 * len(zero_escape) / b_folios
        findings.append({
            'finding': f'{len(zero_escape)} B folios have zero escape ({pct:.1f}%)',
            'interpretation': 'Minority of B programs lack recovery routes'
        })

    # HT relationship
    if 'error' not in ht_analysis and ht_analysis['significant']:
        findings.append({
            'finding': 'Zero-escape folios have significantly higher HT',
            'ratio': ht_analysis['ratio'],
            'p_value': ht_analysis['p_value'],
            'interpretation': 'Confirms C459.b: recovery scarcity triggers human burden'
        })

    # Hotspot concentration
    if 'error' not in ht_analysis and ht_analysis['hotspot_rate'] > 0.3:
        findings.append({
            'finding': f'{ht_analysis["hotspot_rate"]:.0%} of zero-escape are HT hotspots',
            'interpretation': 'Zero-escape pages are attention-critical'
        })

    # Regime concentration
    enriched_regimes = [r for r, d in regime_analysis['enrichment_by_regime'].items() if d['enriched']]
    if enriched_regimes:
        findings.append({
            'finding': f'Zero-escape enriched in: {", ".join(enriched_regimes)}',
            'interpretation': 'Specific regimes prone to zero-escape design'
        })

    # Distribution pattern
    if 'error' not in distribution:
        if distribution['clustering']['interpretation'] == 'CLUSTERED':
            findings.append({
                'finding': 'Zero-escape folios are clustered',
                'ratio': distribution['clustering']['clustering_ratio'],
                'interpretation': 'Deliberately grouped, not random scatter'
            })
        else:
            findings.append({
                'finding': 'Zero-escape folios are distributed throughout',
                'interpretation': 'Spread across manuscript, not localized'
            })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[9] Saving output...")

    output = {
        'metadata': {
            'analysis': 'E2 - Zero-Escape Characterization',
            'description': 'Characterizing B folios with no recovery routes',
            'n_b_folios': b_folios,
            'n_zero_escape': len(zero_escape),
            'threshold': 0.01
        },
        'zero_escape_folios': zero_escape,
        'distribution': distribution,
        'regime_analysis': regime_analysis,
        'ht_analysis': ht_analysis,
        'hazard_analysis': hazard_analysis,
        'neighbor_analysis': {k: v for k, v in neighbor_analysis.items() if k != 'details'},
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("E2 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
