#!/usr/bin/env python3
"""
ts_02_judgment_zone_matrix.py - Vector A: Operator Interface Theory

Constructs judgment-zone availability matrix showing which of the 13 operator
judgments become IMPOSSIBLE vs UNAVOIDABLE in each zone.

Pre-registered hypotheses:
- H-A1: Judgment availability >70% non-uniform across zones
- H-A2: At least 3 judgments show significant zone restriction (chi-sq p<0.01)
- H-A3: HT density correlates with judgment count per zone (r>0.3)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# The 13 judgment types from OJLM-1 (grouped by category)
# Derived from constraint analysis of what operators must supply
JUDGMENT_TYPES = {
    # Watch Closely (6) - require active monitoring
    'TEMPERATURE': {
        'category': 'WATCH_CLOSELY',
        'description': 'Monitor heat level',
        'instruction_markers': ['k_ENERGY', 'HEATING', 'h_HAZARD'],
    },
    'PHASE_TRANSITION': {
        'category': 'WATCH_CLOSELY',
        'description': 'Observe state changes (liquid/vapor/solid)',
        'instruction_markers': ['h_HAZARD', 'MONITORING'],
    },
    'QUALITY_PURITY': {
        'category': 'WATCH_CLOSELY',
        'description': 'Assess product quality',
        'instruction_markers': ['MONITORING', 'COLLECTION'],
    },
    'TIMING': {
        'category': 'WATCH_CLOSELY',
        'description': 'Determine when to act',
        'instruction_markers': ['LINK', 'e_ESCAPE'],
    },
    'MATERIAL_STATE': {
        'category': 'WATCH_CLOSELY',
        'description': 'Assess current material condition',
        'instruction_markers': ['MONITORING', 'PREPARATION'],
    },
    'STABILITY': {
        'category': 'WATCH_CLOSELY',
        'description': 'Monitor process stability',
        'instruction_markers': ['h_HAZARD', 'LINK'],
    },

    # Forbidden Intervention (3) - must NOT intervene
    'EQUILIBRIUM_WAIT': {
        'category': 'FORBIDDEN_INTERVENTION',
        'description': 'Wait for system to stabilize (no touching)',
        'instruction_markers': ['FLOW', 'h_HAZARD'],
    },
    'CYCLE_COMPLETION': {
        'category': 'FORBIDDEN_INTERVENTION',
        'description': 'Let cycle complete without interruption',
        'instruction_markers': ['FLOW', 'RECOVERY'],
    },
    'PURIFICATION_PATIENCE': {
        'category': 'FORBIDDEN_INTERVENTION',
        'description': 'Allow purification to complete',
        'instruction_markers': ['COLLECTION', 'e_ESCAPE'],
    },

    # Recovery Decision (4) - decide whether to intervene
    'ABORT_DECISION': {
        'category': 'RECOVERY_DECISION',
        'description': 'Decide whether to abort current run',
        'instruction_markers': ['e_ESCAPE', 'RECOVERY'],
    },
    'CORRECTION_DECISION': {
        'category': 'RECOVERY_DECISION',
        'description': 'Decide whether to apply correction',
        'instruction_markers': ['LINK', 'AUX'],
    },
    'CONTINUATION_DECISION': {
        'category': 'RECOVERY_DECISION',
        'description': 'Decide whether to continue or pause',
        'instruction_markers': ['LINK', 'FLOW'],
    },
    'COLLECTION_DECISION': {
        'category': 'RECOVERY_DECISION',
        'description': 'Decide when to collect product',
        'instruction_markers': ['COLLECTION', 'e_ESCAPE'],
    },
}

# Instruction class to zone mapping (from ts_01)
INSTRUCTION_TO_ZONE = {
    'PREPARATION': 'C',
    'AUX': 'C',
    'MONITORING': 'P',
    'LINK': 'P',
    'FLOW': 'R',
    'k_ENERGY': 'R',
    'h_HAZARD': 'R',
    'e_ESCAPE': 'S',
    'RECOVERY': 'S',
    'COLLECTION': 'S',
    'HEATING': 'R',
    'OTHER': 'R',
    'UNKNOWN': 'R',
}

# Zone characteristics for judgment derivation
ZONE_SEMANTICS = {
    'C': {
        'name': 'Setup',
        'escape_rate': 0.014,  # 1.4% from C443
        'flexibility': 'HIGH',
        'intervention': 'PERMITTED',
    },
    'P': {
        'name': 'Observation',
        'escape_rate': 0.116,  # 11.6%
        'flexibility': 'MEDIUM',
        'intervention': 'REQUIRED',
    },
    'R': {
        'name': 'Progression',
        'escape_rate': 0.02,  # ~2% average
        'flexibility': 'LOW',
        'intervention': 'RESTRICTED',
    },
    'S': {
        'name': 'Locked',
        'escape_rate': 0.02,  # 0-3.8%
        'flexibility': 'NONE',
        'intervention': 'FORBIDDEN',
    },
}


def load_data():
    """Load Brunschwig data and compute zone distributions per recipe."""
    with open(DATA_DIR / "brunschwig_materials_master.json", encoding='utf-8') as f:
        master = json.load(f)

    # Load HT density by regime
    ht_by_regime = {
        'REGIME_1': 0.045,
        'REGIME_2': 0.062,
        'REGIME_3': 0.038,
        'REGIME_4': 0.051,
    }

    return master, ht_by_regime


def derive_judgment_zone_matrix():
    """
    Derive judgment availability for each zone based on zone semantics.

    Returns matrix where:
    - 2 = REQUIRED (zone demands this judgment)
    - 1 = PERMITTED (zone allows this judgment)
    - 0 = IMPOSSIBLE (zone forbids this judgment)
    """
    matrix = {}

    for judgment_name, judgment_info in JUDGMENT_TYPES.items():
        category = judgment_info['category']
        markers = judgment_info['instruction_markers']

        # Determine zone availability based on where markers appear
        marker_zones = [INSTRUCTION_TO_ZONE.get(m, 'R') for m in markers]
        zone_counts = defaultdict(int)
        for z in marker_zones:
            zone_counts[z] += 1

        row = {}
        for zone in ['C', 'P', 'R', 'S']:
            zone_sem = ZONE_SEMANTICS[zone]

            if category == 'WATCH_CLOSELY':
                # Watch closely judgments are REQUIRED where they appear, PERMITTED in flexible zones
                if zone_counts[zone] > 0:
                    row[zone] = 2  # REQUIRED
                elif zone_sem['flexibility'] == 'HIGH':
                    row[zone] = 1  # PERMITTED
                elif zone_sem['flexibility'] == 'NONE':
                    row[zone] = 0  # IMPOSSIBLE
                else:
                    row[zone] = 1  # PERMITTED

            elif category == 'FORBIDDEN_INTERVENTION':
                # Forbidden interventions: must NOT intervene - relevant in restricted zones
                if zone_sem['intervention'] == 'FORBIDDEN':
                    row[zone] = 2  # REQUIRED (must observe non-intervention)
                elif zone_sem['intervention'] == 'RESTRICTED':
                    row[zone] = 2  # REQUIRED
                else:
                    row[zone] = 0  # IMPOSSIBLE (intervention allowed, so no forbidden-wait)

            elif category == 'RECOVERY_DECISION':
                # Recovery decisions: relevant where escape is possible
                if zone_sem['escape_rate'] > 0.05:  # P-zone
                    row[zone] = 2  # REQUIRED
                elif zone_sem['intervention'] == 'PERMITTED':
                    row[zone] = 1  # PERMITTED
                elif zone_sem['intervention'] == 'FORBIDDEN':
                    row[zone] = 0  # IMPOSSIBLE
                else:
                    row[zone] = 1  # PERMITTED

        matrix[judgment_name] = row

    return matrix


def compute_empirical_distribution(master):
    """
    Compute empirical zone distribution for each judgment type
    based on where their instruction markers actually appear.
    """
    # Count instruction occurrences by zone across all recipes
    zone_instruction_counts = defaultdict(lambda: defaultdict(int))

    for recipe in master.get('materials', []):  # Key is 'materials' not 'recipes'
        sequence = recipe.get('instruction_sequence', [])
        for inst in sequence:
            zone = INSTRUCTION_TO_ZONE.get(inst, 'R')
            zone_instruction_counts[zone][inst] += 1

    # Compute judgment presence by zone
    judgment_zone_presence = {}

    for judgment_name, judgment_info in JUDGMENT_TYPES.items():
        markers = judgment_info['instruction_markers']
        zone_scores = defaultdict(float)

        for marker in markers:
            for zone in ['C', 'P', 'R', 'S']:
                zone_scores[zone] += zone_instruction_counts[zone][marker]

        total = sum(zone_scores.values())
        if total > 0:
            judgment_zone_presence[judgment_name] = {
                z: zone_scores[z] / total for z in ['C', 'P', 'R', 'S']
            }
        else:
            judgment_zone_presence[judgment_name] = {z: 0.25 for z in ['C', 'P', 'R', 'S']}

    return judgment_zone_presence


def test_uniformity(distribution):
    """Test if distribution is uniform using chi-squared."""
    observed = [distribution.get(z, 0) for z in ['C', 'P', 'R', 'S']]
    total = sum(observed)
    if total == 0:
        return {'chi2': 0, 'p': 1.0, 'non_uniform': False}

    # Normalize to counts (multiply by 100 for meaningful chi-sq)
    observed = [o * 100 for o in observed]
    expected = [25.0] * 4  # Uniform expectation

    chi2, p = stats.chisquare(observed, expected)

    return {
        'chi2': float(chi2),
        'p': float(p),
        'non_uniform': bool(p < 0.01),
    }


def compute_zone_judgment_counts(matrix):
    """Count how many judgments are REQUIRED/PERMITTED/IMPOSSIBLE per zone."""
    zone_counts = {z: {'required': 0, 'permitted': 0, 'impossible': 0} for z in ['C', 'P', 'R', 'S']}

    for judgment_name, row in matrix.items():
        for zone, value in row.items():
            if value == 2:
                zone_counts[zone]['required'] += 1
            elif value == 1:
                zone_counts[zone]['permitted'] += 1
            else:
                zone_counts[zone]['impossible'] += 1

    return zone_counts


def main():
    print("=" * 60)
    print("TRAJECTORY_SEMANTICS: Vector A - Interface Theory")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    master, ht_by_regime = load_data()

    # Derive theoretical matrix
    print("\nDeriving judgment-zone availability matrix...")
    matrix = derive_judgment_zone_matrix()

    # Compute empirical distribution
    print("Computing empirical zone distributions...")
    empirical = compute_empirical_distribution(master)

    # Display matrix
    print("\n" + "-" * 60)
    print("JUDGMENT-ZONE AVAILABILITY MATRIX")
    print("(2=REQUIRED, 1=PERMITTED, 0=IMPOSSIBLE)")
    print("-" * 60)

    print(f"\n{'Judgment':<25} {'C':>5} {'P':>5} {'R':>5} {'S':>5}  Category")
    print("-" * 60)

    for judgment_name, row in matrix.items():
        category = JUDGMENT_TYPES[judgment_name]['category']
        print(f"{judgment_name:<25} {row['C']:>5} {row['P']:>5} {row['R']:>5} {row['S']:>5}  {category}")

    # Zone judgment counts
    print("\n" + "-" * 40)
    print("ZONE JUDGMENT COUNTS")
    print("-" * 40)

    zone_counts = compute_zone_judgment_counts(matrix)
    for zone, counts in zone_counts.items():
        total_active = counts['required'] + counts['permitted']
        print(f"{zone}-zone: {counts['required']} required, {counts['permitted']} permitted, {counts['impossible']} impossible | Active: {total_active}")

    # Run hypothesis tests
    print("\n" + "=" * 60)
    print("HYPOTHESIS TESTS")
    print("=" * 60)

    results = {
        'phase': 'TRAJECTORY_SEMANTICS',
        'vector': 'A',
        'n_judgments': len(JUDGMENT_TYPES),
        'matrix': {j: {z: int(v) for z, v in row.items()} for j, row in matrix.items()},
        'zone_counts': zone_counts,
        'hypotheses': {},
    }

    # H-A1: Non-uniformity test
    print("\n[H-A1] Judgment availability non-uniformity")

    non_uniform_count = 0
    uniformity_results = {}

    for judgment_name, dist in empirical.items():
        result = test_uniformity(dist)
        uniformity_results[judgment_name] = result
        if result['non_uniform']:
            non_uniform_count += 1

    non_uniform_rate = non_uniform_count / len(empirical)
    print(f"  Non-uniform judgments: {non_uniform_count}/{len(empirical)} ({non_uniform_rate:.1%})")
    print(f"  PASS (>70% non-uniform): {non_uniform_rate > 0.70}")

    results['hypotheses']['H-A1'] = {
        'name': 'Judgment availability >70% non-uniform',
        'test': 'Chi-squared uniformity',
        'threshold': '>70% non-uniform (p<0.01)',
        'non_uniform_count': non_uniform_count,
        'total': len(empirical),
        'rate': float(non_uniform_rate),
        'significant': bool(non_uniform_rate > 0.70),
        'details': uniformity_results,
    }

    # H-A2: Significant zone restrictions
    print("\n[H-A2] Significant zone restrictions (chi-sq p<0.01)")

    significant_restrictions = []
    for judgment_name, result in uniformity_results.items():
        if result['p'] < 0.01:
            significant_restrictions.append({
                'judgment': judgment_name,
                'chi2': result['chi2'],
                'p': result['p'],
            })

    print(f"  Judgments with significant restriction: {len(significant_restrictions)}")
    print(f"  PASS (>=3 significant): {len(significant_restrictions) >= 3}")

    if significant_restrictions:
        print("  Top restrictions:")
        for sr in sorted(significant_restrictions, key=lambda x: x['p'])[:5]:
            print(f"    {sr['judgment']}: chi2={sr['chi2']:.2f}, p={sr['p']:.4f}")

    results['hypotheses']['H-A2'] = {
        'name': 'At least 3 judgments with significant zone restriction',
        'test': 'Chi-squared',
        'threshold': 'p<0.01 for each',
        'count': len(significant_restrictions),
        'significant': bool(len(significant_restrictions) >= 3),
        'details': significant_restrictions,
    }

    # H-A3: HT density correlation with judgment load
    print("\n[H-A3] HT density vs zone judgment count")

    # Use zone judgment load (required + permitted) and correlate with HT
    zone_load = {z: zone_counts[z]['required'] + zone_counts[z]['permitted'] for z in ['C', 'P', 'R', 'S']}

    # Map zones to typical REGIMEs and their HT
    # This is indirect but tests the hypothesis
    zone_to_ht = {
        'C': ht_by_regime['REGIME_2'],  # GENTLE = setup-heavy
        'P': ht_by_regime['REGIME_1'],  # STANDARD
        'R': ht_by_regime['REGIME_3'],  # OIL_RESIN = R-heavy
        'S': ht_by_regime['REGIME_4'],  # PRECISION = S-heavy
    }

    loads = [zone_load[z] for z in ['C', 'P', 'R', 'S']]
    hts = [zone_to_ht[z] for z in ['C', 'P', 'R', 'S']]

    if len(loads) >= 3:
        r, p = stats.pearsonr(loads, hts)
    else:
        r, p = np.nan, 1.0

    print(f"  Zone loads: C={zone_load['C']}, P={zone_load['P']}, R={zone_load['R']}, S={zone_load['S']}")
    print(f"  Correlation r={r:.3f}, p={p:.4f}")
    print(f"  PASS (r>0.3, p<0.05): {p < 0.05 and r > 0.3}")

    results['hypotheses']['H-A3'] = {
        'name': 'HT density correlates with judgment count per zone',
        'test': 'Pearson correlation',
        'threshold': 'r>0.3, p<0.05',
        'r': float(r) if not np.isnan(r) else None,
        'p': float(p),
        'zone_loads': zone_load,
        'significant': bool(p < 0.05 and r > 0.3) if not np.isnan(r) else False,
    }

    # Summary
    print("\n" + "=" * 60)
    print("VECTOR A SUMMARY")
    print("=" * 60)

    passed = sum(1 for h in ['H-A1', 'H-A2', 'H-A3']
                 if results['hypotheses'][h].get('significant', False))

    print(f"\nHypotheses passed: {passed}/3")

    if passed >= 2:
        verdict = "TIER_3_ENRICHMENT"
        print("VERDICT: TIER_3_ENRICHMENT - Operator interface theory supported")
    elif passed >= 1:
        verdict = "PARTIAL"
        print("VERDICT: PARTIAL - Some interface structure detected")
    else:
        verdict = "INCONCLUSIVE"
        print("VERDICT: INCONCLUSIVE - Weak interface signal")

    results['summary'] = {
        'hypotheses_passed': passed,
        'total_hypotheses': 3,
        'verdict': verdict,
    }

    # Save results
    output_path = RESULTS_DIR / "ts_judgment_zone_matrix.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
