#!/usr/bin/env python3
"""
Anomalous Folio Investigation

P1 identified 4 folios that cluster by HT burden across system boundaries:
- f41r (B folio clustering with A)
- f65r (AZC folio clustering with A)
- f67r2 (AZC folio clustering with A)
- f86v5 (B folio clustering with A)

What makes these folios special?

Output: results/anomalous_folio_investigation.json
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

# Input
UNIFIED_PROFILES = RESULTS / "unified_folio_profiles.json"
B_FEATURES = RESULTS / "b_macro_scaffold_audit.json"
HT_FEATURES = RESULTS / "ht_folio_features.json"
AZC_FEATURES = RESULTS / "azc_folio_features.json"

# Output
OUTPUT = RESULTS / "anomalous_folio_investigation.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_percentile(value, all_values):
    """Get percentile of value in distribution."""
    return round(100 * sum(1 for v in all_values if v <= value) / len(all_values), 1)


def main():
    print("=" * 70)
    print("Anomalous Folio Investigation")
    print("=" * 70)

    # Target folios
    anomalous = ['f41r', 'f65r', 'f67r2', 'f86v5']

    # Load data
    print("\n[1] Loading data...")
    unified = load_json(UNIFIED_PROFILES)
    b_features = load_json(B_FEATURES)
    ht_features = load_json(HT_FEATURES)
    azc_features = load_json(AZC_FEATURES)

    # Get reference distributions
    all_ht = [p['ht_density'] for p in unified['profiles'].values() if p.get('ht_density')]
    a_ht = [p['ht_density'] for p in unified['profiles'].values() if p.get('system') == 'A' and p.get('ht_density')]
    b_ht = [p['ht_density'] for p in unified['profiles'].values() if p.get('system') == 'B' and p.get('ht_density')]
    azc_ht = [p['ht_density'] for p in unified['profiles'].values() if p.get('system') == 'AZC' and p.get('ht_density')]

    print(f"    Reference: A mean={np.mean(a_ht):.3f}, B mean={np.mean(b_ht):.3f}, AZC mean={np.mean(azc_ht):.3f}")

    # Analyze each anomalous folio
    print("\n[2] Analyzing anomalous folios...")
    results = {}

    for folio in anomalous:
        print(f"\n    === {folio} ===")
        profile = unified['profiles'].get(folio, {})
        system = profile.get('system')

        print(f"    System: {system}")

        # HT analysis
        ht = profile.get('ht_density', 0)
        ht_status = profile.get('ht_status')
        ht_pct_global = get_percentile(ht, all_ht)

        if system == 'A':
            ht_pct_system = get_percentile(ht, a_ht)
        elif system == 'B':
            ht_pct_system = get_percentile(ht, b_ht)
        else:
            ht_pct_system = get_percentile(ht, azc_ht)

        print(f"    HT density: {ht:.3f} ({ht_status})")
        print(f"    HT percentile (global): {ht_pct_global}%")
        print(f"    HT percentile (in {system}): {ht_pct_system}%")

        result = {
            'folio': folio,
            'system': system,
            'ht_density': round(ht, 4),
            'ht_status': ht_status,
            'ht_percentile_global': ht_pct_global,
            'ht_percentile_in_system': ht_pct_system
        }

        # System-specific analysis
        if system == 'B':
            b_data = profile.get('b_metrics', {})
            if b_data:
                tension = profile['burden_indices'].get('execution_tension')
                hazard = b_data.get('hazard_density', 0)
                escape = b_data.get('qo_density', 0)
                regime = b_data.get('regime')

                print(f"    Regime: {regime}")
                print(f"    Execution tension: {tension:.3f}" if tension else "    Execution tension: N/A")
                print(f"    Hazard density: {hazard:.4f}")
                print(f"    Escape density: {escape:.4f}")

                result['b_metrics'] = {
                    'regime': regime,
                    'execution_tension': round(tension, 3) if tension else None,
                    'hazard_density': round(hazard, 4),
                    'escape_density': round(escape, 4)
                }

        elif system == 'AZC':
            azc_data = azc_features.get('folios', {}).get(folio, {})
            if azc_data:
                ttr = azc_data.get('ttr', 0)
                coverage = azc_data.get('coverage', 0)
                section = azc_data.get('section', 'UNKNOWN')

                print(f"    Section: {section}")
                print(f"    TTR: {ttr:.3f}")
                print(f"    Coverage: {coverage:.3f}")

                result['azc_metrics'] = {
                    'section': section,
                    'ttr': round(ttr, 3),
                    'coverage': round(coverage, 3)
                }

        # Check if this folio is near system boundaries
        quire = profile.get('quire')
        print(f"    Quire: {quire}")
        result['quire'] = quire

        # Why does this cluster with A?
        # Compare to A mean
        a_mean = np.mean(a_ht)
        system_mean = np.mean(b_ht) if system == 'B' else np.mean(azc_ht)

        distance_to_a = abs(ht - a_mean)
        distance_to_own = abs(ht - system_mean)

        print(f"    Distance to A mean: {distance_to_a:.3f}")
        print(f"    Distance to {system} mean: {distance_to_own:.3f}")

        result['clustering_reason'] = {
            'distance_to_a_mean': round(distance_to_a, 4),
            'distance_to_own_system_mean': round(distance_to_own, 4),
            'closer_to': 'A' if distance_to_a < distance_to_own else system
        }

        results[folio] = result

    # Summary
    print("\n" + "=" * 70)
    print("[3] Summary")
    print("=" * 70)

    print("\n    Why do these folios cluster with A?")
    for folio, r in results.items():
        closer = r['clustering_reason']['closer_to']
        ht = r['ht_density']
        system = r['system']
        pct = r['ht_percentile_in_system']

        if r['ht_status'] == 'HOTSPOT':
            reason = "HT HOTSPOT - extreme high HT"
        elif pct > 90:
            reason = f"Top {100-pct:.0f}% HT in {system}"
        elif pct > 75:
            reason = f"High HT for {system} ({pct}th percentile)"
        else:
            reason = f"Moderate HT but clustering feature-driven"

        print(f"    {folio} ({system}): HT={ht:.3f}, {reason}")

    # Key findings
    print("\n[4] Key findings...")
    findings = []

    # Check if all are high HT
    high_ht = all(r['ht_percentile_in_system'] > 75 for r in results.values())
    if high_ht:
        findings.append({
            'finding': 'All anomalous folios have high HT for their system',
            'interpretation': 'Cross-system clustering driven by exceptional HT burden'
        })

    # Check for hotspots
    hotspots = [f for f, r in results.items() if r['ht_status'] == 'HOTSPOT']
    if hotspots:
        findings.append({
            'finding': f'{len(hotspots)} anomalous folios are HT hotspots',
            'folios': hotspots,
            'interpretation': 'Extreme HT drives cross-system affinity'
        })

    # Check B regime for B folios
    b_anomalous = [f for f, r in results.items() if r['system'] == 'B']
    if b_anomalous:
        regimes = [results[f]['b_metrics']['regime'] for f in b_anomalous if results[f].get('b_metrics')]
        if regimes:
            findings.append({
                'finding': f'B anomalous folios in regimes: {set(regimes)}',
                'interpretation': 'Check if specific regimes prone to high HT'
            })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[5] Saving output...")

    output = {
        'metadata': {
            'analysis': 'Anomalous Folio Investigation',
            'description': 'Why do these folios cluster across system boundaries?',
            'n_folios': len(anomalous)
        },
        'reference_distributions': {
            'a_mean_ht': round(np.mean(a_ht), 4),
            'b_mean_ht': round(np.mean(b_ht), 4),
            'azc_mean_ht': round(np.mean(azc_ht), 4)
        },
        'anomalous_folios': results,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
