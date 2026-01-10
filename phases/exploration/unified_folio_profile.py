#!/usr/bin/env python3
"""
D0: Unified Folio Profile Generator

Creates a single integrated profile for all 227 folios, combining:
- HT features (density, prefix distribution)
- B features (CEI, hazard, escape, regime)
- AZC features (placement entropy, section)
- Outlier classifications
- Computed burden indices
- System pressure vectors

Output: results/unified_folio_profiles.json
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

# Input files
HT_FEATURES = RESULTS / "ht_folio_features.json"
HT_DIST = RESULTS / "ht_distribution_analysis.json"
B_FEATURES = RESULTS / "b_macro_scaffold_audit.json"
AZC_FEATURES = RESULTS / "azc_folio_features.json"
OUTLIER_REPORT = BASE / "phases" / "21-23_enumeration" / "outlier_report.json"

# Output
OUTPUT = RESULTS / "unified_folio_profiles.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_percentile(value, all_values):
    """Compute percentile rank (0-100)."""
    if not all_values or value is None:
        return None
    return float(stats.percentileofscore(all_values, value))


def compute_zscore(value, mean, std):
    """Compute z-score."""
    if std == 0 or value is None:
        return 0.0
    return (value - mean) / std


def classify_ht_status(ht_density, z_score, hotspot_folios, desert_threshold=-2.0):
    """Classify HT status as HOTSPOT, DESERT, or NORMAL."""
    if z_score >= 2.0:
        return "HOTSPOT"
    elif z_score <= desert_threshold:
        return "DESERT"
    else:
        return "NORMAL"


def main():
    print("=" * 70)
    print("D0: Unified Folio Profile Generator")
    print("=" * 70)

    # Load all data sources
    print("\n[1] Loading data sources...")

    ht_features = load_json(HT_FEATURES)
    print(f"    HT features: {len(ht_features['folios'])} folios")

    ht_dist = load_json(HT_DIST)
    hotspot_folios = {h['folio'] for h in ht_dist.get('hotspots', [])}
    print(f"    HT hotspots: {len(hotspot_folios)}")

    b_features = load_json(B_FEATURES)
    print(f"    B features: {len(b_features['features'])} folios")

    azc_features = load_json(AZC_FEATURES)
    print(f"    AZC features: {len(azc_features['folios'])} folios")

    try:
        outlier_report = load_json(OUTLIER_REPORT)
        outliers = {o['folio']: o for o in outlier_report.get('outliers', [])}
        print(f"    Outliers: {len(outliers)}")
    except FileNotFoundError:
        outliers = {}
        print("    Outliers: 0 (file not found)")

    # Compute global statistics for z-scores
    print("\n[2] Computing global statistics...")

    # HT densities
    all_ht_densities = [
        f['ht_density'] for f in ht_features['folios'].values()
    ]
    ht_mean = np.mean(all_ht_densities)
    ht_std = np.std(all_ht_densities)
    print(f"    HT density: mean={ht_mean:.4f}, std={ht_std:.4f}")

    # B metrics
    b_folios = b_features['features']
    b_hazard_densities = [f['hazard_density'] for f in b_folios.values()]
    b_escape_densities = [f['qo_density'] for f in b_folios.values()]  # qo = escape
    b_cei_totals = [f['cei_total'] for f in b_folios.values()]

    b_hazard_mean = np.mean(b_hazard_densities)
    b_hazard_std = np.std(b_hazard_densities)
    b_escape_mean = np.mean(b_escape_densities)
    b_escape_std = np.std(b_escape_densities)
    b_cei_mean = np.mean(b_cei_totals)
    b_cei_std = np.std(b_cei_totals)

    print(f"    B hazard: mean={b_hazard_mean:.4f}, std={b_hazard_std:.4f}")
    print(f"    B escape (qo): mean={b_escape_mean:.4f}, std={b_escape_std:.4f}")
    print(f"    B CEI: mean={b_cei_mean:.4f}, std={b_cei_std:.4f}")

    # Build unified profiles
    print("\n[3] Building unified profiles...")

    profiles = {}

    for folio, ht_data in ht_features['folios'].items():
        # Basic info
        system = ht_data.get('system', 'UNKNOWN')
        quire = ht_data.get('quire', 'UNKNOWN')
        ht_density = ht_data.get('ht_density', 0)

        # HT z-score and percentile
        ht_z = compute_zscore(ht_density, ht_mean, ht_std)
        ht_percentile = compute_percentile(ht_density, all_ht_densities)
        ht_status = classify_ht_status(ht_density, ht_z, hotspot_folios)

        # B metrics (if B folio)
        b_metrics = None
        execution_tension = None
        if folio in b_folios:
            b_data = b_folios[folio]
            b_metrics = {
                'cei_total': b_data['cei_total'],
                'regime': b_data['regime'],
                'hazard_density': b_data['hazard_density'],
                'escape_density': b_data['qo_density'],
                'link_density': b_data['link_density'],
                'near_miss_count': b_data['near_miss_count'],
                'recovery_ops_count': b_data['recovery_ops_count'],
                'intervention_frequency': b_data['intervention_frequency']
            }
            # Execution tension = z(hazard) - z(escape)
            z_hazard = compute_zscore(b_data['hazard_density'], b_hazard_mean, b_hazard_std)
            z_escape = compute_zscore(b_data['qo_density'], b_escape_mean, b_escape_std)
            execution_tension = z_hazard - z_escape

        # AZC metrics (if AZC folio)
        azc_metrics = None
        if folio in azc_features['folios']:
            azc_data = azc_features['folios'][folio]
            azc_metrics = {
                'section': azc_data.get('section'),
                'placement_entropy': azc_data.get('placement_entropy'),
                'ttr': azc_data.get('ttr'),
                'token_count': azc_data.get('token_count')
            }

        # Outlier flags
        outlier_flags = []
        if folio in outliers:
            outlier_data = outliers[folio]
            for dim in outlier_data.get('anomalous_dimensions', []):
                outlier_flags.append(f"{dim['dimension']}:{dim['z_score']:.1f}")
            if outlier_data.get('notes'):
                outlier_flags.extend(outlier_data['notes'])

        # Burden indices
        burden_indices = {
            'cognitive_burden': round(ht_z, 3),  # z(HT)
            'execution_tension': round(execution_tension, 3) if execution_tension is not None else None
        }

        # System pressure vector (normalized percentiles)
        system_pressure = {
            'A': None,
            'B': None,
            'AZC': None,
            'HT': round(ht_percentile / 100.0, 3) if ht_percentile else None
        }

        # Mark applicable systems
        if system == 'A':
            system_pressure['A'] = round(ht_percentile / 100.0, 3) if ht_percentile else None
        elif system == 'B':
            if folio in b_folios:
                # Use CEI as B pressure indicator
                cei_percentile = compute_percentile(b_folios[folio]['cei_total'], b_cei_totals)
                system_pressure['B'] = round(cei_percentile / 100.0, 3) if cei_percentile else None
        elif system == 'AZC':
            if azc_metrics and azc_metrics['placement_entropy'] is not None:
                all_entropies = [f.get('placement_entropy', 0) for f in azc_features['folios'].values()]
                entropy_percentile = compute_percentile(azc_metrics['placement_entropy'], all_entropies)
                system_pressure['AZC'] = round(entropy_percentile / 100.0, 3) if entropy_percentile else None

        # Distinctive features
        distinctive = []
        if ht_status == "HOTSPOT":
            distinctive.append("HT hotspot")
        if ht_status == "DESERT":
            distinctive.append("HT desert")
        if execution_tension is not None and execution_tension > 1.5:
            distinctive.append("high tension")
        if execution_tension is not None and execution_tension < -1.5:
            distinctive.append("high slack")
        if folio in outliers:
            distinctive.append("B outlier")
        if azc_metrics and azc_metrics.get('section') == 'Z':
            distinctive.append("Zodiac")

        # Determine dominant system
        dominant = system
        if ht_percentile and ht_percentile > 90:
            dominant = "HT-dominated"
        elif system == 'B' and execution_tension and execution_tension > 1.5:
            dominant = "B-stressed"
        elif system == 'AZC':
            dominant = "AZC"

        profiles[folio] = {
            'folio': folio,
            'system': system,
            'quire': quire,
            'ht_density': round(ht_density, 4),
            'ht_percentile': round(ht_percentile, 1) if ht_percentile else None,
            'ht_z_score': round(ht_z, 3),
            'ht_status': ht_status,
            'b_metrics': b_metrics,
            'azc_metrics': azc_metrics,
            'outlier_flags': outlier_flags,
            'burden_indices': burden_indices,
            'system_pressure': system_pressure,
            'distinctive_features': distinctive,
            'dominant': dominant
        }

    print(f"    Created {len(profiles)} unified profiles")

    # Summary statistics
    print("\n[4] Summary statistics...")

    # Count by system
    by_system = defaultdict(int)
    for p in profiles.values():
        by_system[p['system']] += 1
    print(f"    By system: {dict(by_system)}")

    # Count by status
    by_status = defaultdict(int)
    for p in profiles.values():
        by_status[p['ht_status']] += 1
    print(f"    By HT status: {dict(by_status)}")

    # Count by dominant
    by_dominant = defaultdict(int)
    for p in profiles.values():
        by_dominant[p['dominant']] += 1
    print(f"    By dominant: {dict(by_dominant)}")

    # Extreme folios
    print("\n[5] Extreme folios...")

    # Highest HT
    sorted_by_ht = sorted(profiles.values(), key=lambda x: x['ht_density'], reverse=True)
    print("\n    TOP 5 HT density:")
    for p in sorted_by_ht[:5]:
        print(f"      {p['folio']}: {p['ht_density']:.3f} ({p['system']}, {p['ht_status']})")

    # Lowest HT (non-zero)
    nonzero_ht = [p for p in profiles.values() if p['ht_density'] > 0]
    sorted_by_ht_low = sorted(nonzero_ht, key=lambda x: x['ht_density'])
    print("\n    BOTTOM 5 HT density (non-zero):")
    for p in sorted_by_ht_low[:5]:
        print(f"      {p['folio']}: {p['ht_density']:.3f} ({p['system']}, {p['ht_status']})")

    # Highest execution tension (B only)
    b_profiles = [p for p in profiles.values() if p['burden_indices']['execution_tension'] is not None]
    sorted_by_tension = sorted(b_profiles, key=lambda x: x['burden_indices']['execution_tension'], reverse=True)
    print("\n    TOP 5 execution tension (B folios):")
    for p in sorted_by_tension[:5]:
        print(f"      {p['folio']}: {p['burden_indices']['execution_tension']:.3f} (regime={p['b_metrics']['regime']})")

    # Lowest execution tension (most slack)
    print("\n    BOTTOM 5 execution tension (most slack, B folios):")
    for p in sorted_by_tension[-5:]:
        print(f"      {p['folio']}: {p['burden_indices']['execution_tension']:.3f} (regime={p['b_metrics']['regime']})")

    # Save output
    print("\n[6] Saving output...")

    output = {
        'metadata': {
            'analysis': 'D0 - Unified Folio Profiles',
            'description': 'Integrated multi-system profile for each folio',
            'n_folios': len(profiles),
            'n_b_folios': len(b_folios),
            'n_azc_folios': len(azc_features['folios']),
            'n_hotspots': by_status.get('HOTSPOT', 0),
            'n_deserts': by_status.get('DESERT', 0),
            'n_outliers': len(outliers)
        },
        'global_stats': {
            'ht_mean': round(ht_mean, 4),
            'ht_std': round(ht_std, 4),
            'b_hazard_mean': round(b_hazard_mean, 4),
            'b_hazard_std': round(b_hazard_std, 4),
            'b_escape_mean': round(b_escape_mean, 4),
            'b_escape_std': round(b_escape_std, 4),
            'b_cei_mean': round(b_cei_mean, 4),
            'b_cei_std': round(b_cei_std, 4)
        },
        'summary': {
            'by_system': dict(by_system),
            'by_ht_status': dict(by_status),
            'by_dominant': dict(by_dominant)
        },
        'extreme_folios': {
            'highest_ht': [p['folio'] for p in sorted_by_ht[:10]],
            'lowest_ht': [p['folio'] for p in sorted_by_ht_low[:10]],
            'highest_tension': [p['folio'] for p in sorted_by_tension[:10]],
            'most_slack': [p['folio'] for p in sorted_by_tension[-10:]]
        },
        'profiles': profiles
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    # Verification
    print("\n[7] Verification...")
    print(f"    All 227 folios covered: {len(profiles) == 227}")
    print(f"    B metrics only for B: {all(p['b_metrics'] is None or p['system'] == 'B' for p in profiles.values())}")
    print(f"    AZC metrics only for AZC: {all(p['azc_metrics'] is None or p['system'] == 'AZC' for p in profiles.values())}")

    print("\n" + "=" * 70)
    print("D0 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
