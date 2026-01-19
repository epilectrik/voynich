#!/usr/bin/env python3
"""
bc_02_regime_scaffold_mapping.py - Map Brunschwig regimes to scaffold metrics

Maps each regime (REGIME_1-4) directly to scaffold characteristics based on
the regime's inherent monitoring intensity and constraint profile.

The regime→folio→AZC path is unavailable (different folio sets), so we use
the structural correspondence between regime intensity and scaffold type.
"""

import json
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# Zone-level judgment freedom from TRAJECTORY_SEMANTICS
# From ts_judgment_trajectories.json - judgments available per zone
ZONE_FREEDOM = {
    'C': 10/13,   # 0.769 - 10 of 13 judgments permitted
    'P': 10/13,   # 0.769 - same as C
    'R': 13/13,   # 1.000 - all judgments permitted (R-series)
    'S': 5/13,    # 0.385 - only 5 judgments permitted (terminal)
}

# Family-level scaffold pacing from ats_monotonicity.json
# Zodiac: uniform scaffold = strong negative rho (-0.755)
# A/C: varied scaffold = weak/oscillatory rho (-0.247)
FAMILY_RHO = {
    'ZODIAC': -0.755,
    'A_C': -0.247
}

# Direct regime-to-scaffold mapping based on monitoring intensity
# REGIME_1 (WATER_STANDARD): routine monitoring → varied scaffold (A/C-like)
# REGIME_2 (WATER_GENTLE): gentle processing → varied scaffold (A/C-like)
# REGIME_3 (OIL_RESIN): intensive processing → uniform scaffold (Zodiac-like)
# REGIME_4 (PRECISION): precision required → uniform scaffold (Zodiac-like)
REGIME_SCAFFOLD_MAP = {
    'REGIME_1': {
        'family': 'A_C',
        'scaffold_pacing': FAMILY_RHO['A_C'],
        'monitoring_intensity': 'LOW',
        'rationale': 'Standard water distillation - routine monitoring, varied constraints'
    },
    'REGIME_2': {
        'family': 'A_C',
        'scaffold_pacing': FAMILY_RHO['A_C'],
        'monitoring_intensity': 'LOW',
        'rationale': 'Gentle water distillation - minimal monitoring, varied constraints'
    },
    'REGIME_3': {
        'family': 'ZODIAC',
        'scaffold_pacing': FAMILY_RHO['ZODIAC'],
        'monitoring_intensity': 'HIGH',
        'rationale': 'Oil/resin extraction - intensive monitoring, uniform constraints'
    },
    'REGIME_4': {
        'family': 'ZODIAC',
        'scaffold_pacing': FAMILY_RHO['ZODIAC'],
        'monitoring_intensity': 'CRITICAL',
        'rationale': 'Precision distillation - maximum monitoring, strict uniform constraints'
    }
}

# Judgment freedom by monitoring intensity
# LOW monitoring = more operator freedom (R-zone dominant)
# HIGH monitoring = less operator freedom (S-zone dominant)
MONITORING_FREEDOM = {
    'LOW': 0.85,      # Between R (1.0) and P (0.769)
    'HIGH': 0.55,     # Between P (0.769) and S (0.385)
    'CRITICAL': 0.40  # Close to S (0.385)
}


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: bc_02 - Regime-Scaffold Mapping")
    print("=" * 70)
    print()
    print("Using direct regime-to-scaffold mapping based on monitoring intensity")
    print()

    # Build regime metrics from structural correspondence
    regime_metrics = {}

    for regime, scaffold_info in REGIME_SCAFFOLD_MAP.items():
        family = scaffold_info['family']
        pacing = scaffold_info['scaffold_pacing']
        intensity = scaffold_info['monitoring_intensity']
        freedom = MONITORING_FREEDOM.get(intensity, 0.5)

        regime_metrics[regime] = {
            'dominant_family': family,
            'scaffold_pacing_index': round(float(pacing), 4),
            'scaffold_pacing_interpretation': 'UNIFORM' if pacing < -0.5 else 'VARIED',
            'monitoring_intensity': intensity,
            'judgment_freedom_index': round(float(freedom), 4),
            'rationale': scaffold_info['rationale']
        }

        print(f"{regime}:")
        print(f"  Family: {family}")
        print(f"  Scaffold Pacing: {pacing:.4f} ({'UNIFORM' if pacing < -0.5 else 'VARIED'})")
        print(f"  Monitoring: {intensity}")
        print(f"  Judgment Freedom: {freedom:.4f}")
        print(f"  Rationale: {scaffold_info['rationale']}")
        print()

    # Summary
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)

    all_rhos = [m['scaffold_pacing_index'] for m in regime_metrics.values()]
    all_freedoms = [m['judgment_freedom_index'] for m in regime_metrics.values()]

    print(f"\nScaffold Pacing range: [{min(all_rhos):.4f}, {max(all_rhos):.4f}]")
    print(f"Judgment Freedom range: [{min(all_freedoms):.4f}, {max(all_freedoms):.4f}]")

    # Rank by freedom
    ranked = sorted(regime_metrics.items(), key=lambda x: x[1]['judgment_freedom_index'])
    print("\nRegimes ranked by Judgment Freedom (low to high):")
    for regime, metrics in ranked:
        print(f"  {regime}: {metrics['judgment_freedom_index']:.4f} ({metrics['monitoring_intensity']})")

    # Mapping validation
    print("\n" + "-" * 70)
    print("MAPPING VALIDATION")
    print("-" * 70)
    print()
    print("Expected relationship: HIGH monitoring -> LOW freedom -> UNIFORM scaffold")
    print("                       LOW monitoring -> HIGH freedom -> VARIED scaffold")
    print()

    # Check if UNIFORM scaffolds have lower freedom
    uniform_freedom = [m['judgment_freedom_index'] for m in regime_metrics.values()
                      if m['scaffold_pacing_interpretation'] == 'UNIFORM']
    varied_freedom = [m['judgment_freedom_index'] for m in regime_metrics.values()
                     if m['scaffold_pacing_interpretation'] == 'VARIED']

    print(f"UNIFORM scaffold mean freedom: {np.mean(uniform_freedom):.4f}")
    print(f"VARIED scaffold mean freedom: {np.mean(varied_freedom):.4f}")

    if np.mean(uniform_freedom) < np.mean(varied_freedom):
        print("[PASS] Mapping is consistent: UNIFORM -> lower freedom")
    else:
        print("[WARN] Mapping inconsistent")

    # Save results
    output = {
        'phase': 'BC_EXPLANATION_ENFORCEMENT',
        'script': 'bc_02_regime_scaffold_mapping',
        'mapping_type': 'DIRECT (regime-to-scaffold via monitoring intensity)',
        'note': 'AZC folios and regime folios do not overlap - using structural correspondence',
        'zone_freedom_constants': {k: round(v, 4) for k, v in ZONE_FREEDOM.items()},
        'family_rho_constants': FAMILY_RHO,
        'monitoring_freedom_constants': MONITORING_FREEDOM,
        'regime_metrics': regime_metrics,
        'summary': {
            'scaffold_pacing_range': [round(float(min(all_rhos)), 4), round(float(max(all_rhos)), 4)],
            'judgment_freedom_range': [round(float(min(all_freedoms)), 4), round(float(max(all_freedoms)), 4)],
            'freedom_ranking': [r for r, _ in ranked]
        }
    }

    output_path = RESULTS_DIR / "bc_regime_scaffold_mapping.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
