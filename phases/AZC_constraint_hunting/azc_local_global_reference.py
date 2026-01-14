#!/usr/bin/env python3
"""
F-AZC-009: Local vs Global Reference Partition

Semantic Frame (Tier 3):
C and S partition AZC boundary legality into local (AZC-specific) vs
global (cross-system) reference spaces.

Structural Predictions (pre-registered):
1. AZC endemicity: C > S (C-types appear only in AZC more often)
2. Cross-system persistence: S > C (S-types appear in A and/or B more)
3. Global reusability: S-types span more systems than C-types
4. Family invariance: Same patterns in both Zodiac and A/C

Success criterion: >=3 of 4 predictions met
Failure criterion: No systematic difference -> discard frame

STOP CONDITION: After this test, AZC semantic exploration is COMPLETE.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Family assignments
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

# Position classifications for A/C
C_POSITIONS_AC = {'C', 'C1', 'C2'}
S_POSITIONS_AC = {'S', 'S1', 'S2', 'S3'}

# Position classifications for Zodiac (early vs late)
C_POSITIONS_ZODIAC = {'R1', 'S0'}  # Early positions
S_POSITIONS_ZODIAC = {'R3', 'R4', 'S2', 'S3'}  # Late positions


def load_all_tokens():
    """Load all tokens with system membership."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens_by_system = {
        'A': [],
        'B': [],
        'AZC': []
    }

    azc_tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 10:
                token = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()
                currier = parts[6].strip('"').strip()
                placement = parts[10].strip('"').strip()

                if not token:
                    continue

                if currier == 'A':
                    tokens_by_system['A'].append(token)
                elif currier == 'B':
                    tokens_by_system['B'].append(token)
                elif currier == 'NA':  # AZC
                    tokens_by_system['AZC'].append(token)

                    # Also track AZC details for position analysis
                    if folio in ZODIAC_FAMILY:
                        family = 'zodiac'
                    elif folio in AC_FAMILY:
                        family = 'ac'
                    else:
                        family = 'unknown'

                    azc_tokens.append({
                        'token': token,
                        'folio': folio,
                        'family': family,
                        'placement': placement
                    })

    return tokens_by_system, azc_tokens


def get_type_system_membership(tokens_by_system):
    """For each type, determine which systems it appears in."""
    type_systems = defaultdict(set)

    for system, tokens in tokens_by_system.items():
        for token in tokens:
            type_systems[token].add(system)

    return type_systems


def classify_azc_position(token_info):
    """Classify token as C-position or S-position based on family."""
    placement = token_info['placement']
    family = token_info['family']

    if family == 'ac':
        if placement in C_POSITIONS_AC:
            return 'C'
        elif placement in S_POSITIONS_AC:
            return 'S'
    elif family == 'zodiac':
        if placement in C_POSITIONS_ZODIAC:
            return 'C'
        elif placement in S_POSITIONS_ZODIAC:
            return 'S'

    return None  # Interior or unknown


def analyze_position_types(azc_tokens, type_systems, family_filter=None):
    """Analyze C vs S position types for endemicity and cross-system persistence."""

    if family_filter:
        azc_tokens = [t for t in azc_tokens if t['family'] == family_filter]

    # Group types by position
    c_types = set()
    s_types = set()

    for t in azc_tokens:
        pos = classify_azc_position(t)
        if pos == 'C':
            c_types.add(t['token'])
        elif pos == 'S':
            s_types.add(t['token'])

    if not c_types or not s_types:
        return {'insufficient_data': True}

    # Metric 1: AZC endemicity (appears ONLY in AZC)
    c_endemic = sum(1 for t in c_types if type_systems[t] == {'AZC'})
    s_endemic = sum(1 for t in s_types if type_systems[t] == {'AZC'})

    c_endemic_rate = c_endemic / len(c_types) * 100
    s_endemic_rate = s_endemic / len(s_types) * 100

    # Metric 2: Cross-system persistence (appears in A or B)
    c_crosssystem = sum(1 for t in c_types if 'A' in type_systems[t] or 'B' in type_systems[t])
    s_crosssystem = sum(1 for t in s_types if 'A' in type_systems[t] or 'B' in type_systems[t])

    c_crosssystem_rate = c_crosssystem / len(c_types) * 100
    s_crosssystem_rate = s_crosssystem / len(s_types) * 100

    # Metric 3: Global reusability (average number of systems)
    c_avg_systems = np.mean([len(type_systems[t]) for t in c_types])
    s_avg_systems = np.mean([len(type_systems[t]) for t in s_types])

    # Statistical tests
    # Fisher's exact for endemicity
    endemic_contingency = [
        [c_endemic, len(c_types) - c_endemic],
        [s_endemic, len(s_types) - s_endemic]
    ]
    endemic_odds, endemic_p = stats.fisher_exact(endemic_contingency)

    # Fisher's exact for cross-system
    crosssystem_contingency = [
        [c_crosssystem, len(c_types) - c_crosssystem],
        [s_crosssystem, len(s_types) - s_crosssystem]
    ]
    crosssystem_odds, crosssystem_p = stats.fisher_exact(crosssystem_contingency)

    # Mann-Whitney for average systems
    c_system_counts = [len(type_systems[t]) for t in c_types]
    s_system_counts = [len(type_systems[t]) for t in s_types]
    mw_stat, mw_p = stats.mannwhitneyu(c_system_counts, s_system_counts, alternative='two-sided')

    return {
        'c_types': len(c_types),
        's_types': len(s_types),
        'endemicity': {
            'c_rate': round(c_endemic_rate, 1),
            's_rate': round(s_endemic_rate, 1),
            'c_higher': c_endemic_rate > s_endemic_rate,
            'fisher_p': round(float(endemic_p), 6),
            'significant': endemic_p < 0.05
        },
        'cross_system': {
            'c_rate': round(c_crosssystem_rate, 1),
            's_rate': round(s_crosssystem_rate, 1),
            's_higher': s_crosssystem_rate > c_crosssystem_rate,
            'fisher_p': round(float(crosssystem_p), 6),
            'significant': crosssystem_p < 0.05
        },
        'global_reusability': {
            'c_avg': round(c_avg_systems, 3),
            's_avg': round(s_avg_systems, 3),
            's_higher': s_avg_systems > c_avg_systems,
            'mann_whitney_p': round(float(mw_p), 6),
            'significant': mw_p < 0.05
        }
    }


def main():
    print("=" * 60)
    print("F-AZC-009: Local vs Global Reference Partition")
    print("=" * 60)
    print()
    print("Semantic Frame: C = local (AZC-specific), S = global (cross-system)")
    print()
    print("PRE-REGISTERED PREDICTIONS:")
    print("  1. AZC endemicity: C > S")
    print("  2. Cross-system persistence: S > C")
    print("  3. Global reusability: S-types span more systems")
    print("  4. Family invariance: Same pattern in Zodiac and A/C")
    print()
    print("SUCCESS: >= 3 of 4 predictions met")
    print("FAILURE: No systematic difference -> discard frame")
    print()

    # Load data
    tokens_by_system, azc_tokens = load_all_tokens()

    print(f"Currier A tokens: {len(tokens_by_system['A'])}")
    print(f"Currier B tokens: {len(tokens_by_system['B'])}")
    print(f"AZC tokens: {len(tokens_by_system['AZC'])}")
    print()

    # Get type-system membership
    type_systems = get_type_system_membership(tokens_by_system)
    print(f"Unique types across all systems: {len(type_systems)}")
    print()

    # ==========================================
    # Overall Analysis
    # ==========================================
    print("=" * 60)
    print("OVERALL AZC ANALYSIS")
    print("=" * 60)
    print()

    overall = analyze_position_types(azc_tokens, type_systems)

    if 'insufficient_data' in overall:
        print("INSUFFICIENT DATA")
    else:
        print(f"C-position unique types: {overall['c_types']}")
        print(f"S-position unique types: {overall['s_types']}")
        print()

        print("Prediction 1: AZC Endemicity (C > S)")
        print(f"  C endemic rate: {overall['endemicity']['c_rate']}%")
        print(f"  S endemic rate: {overall['endemicity']['s_rate']}%")
        print(f"  C > S: {'YES' if overall['endemicity']['c_higher'] else 'NO'}")
        print(f"  Fisher's p: {overall['endemicity']['fisher_p']}")
        print(f"  Significant: {'YES ***' if overall['endemicity']['significant'] else 'NO'}")
        print()

        print("Prediction 2: Cross-System Persistence (S > C)")
        print(f"  C cross-system rate: {overall['cross_system']['c_rate']}%")
        print(f"  S cross-system rate: {overall['cross_system']['s_rate']}%")
        print(f"  S > C: {'YES' if overall['cross_system']['s_higher'] else 'NO'}")
        print(f"  Fisher's p: {overall['cross_system']['fisher_p']}")
        print(f"  Significant: {'YES ***' if overall['cross_system']['significant'] else 'NO'}")
        print()

        print("Prediction 3: Global Reusability (S avg systems > C)")
        print(f"  C avg systems: {overall['global_reusability']['c_avg']}")
        print(f"  S avg systems: {overall['global_reusability']['s_avg']}")
        print(f"  S > C: {'YES' if overall['global_reusability']['s_higher'] else 'NO'}")
        print(f"  Mann-Whitney p: {overall['global_reusability']['mann_whitney_p']}")
        print(f"  Significant: {'YES ***' if overall['global_reusability']['significant'] else 'NO'}")
        print()

    # ==========================================
    # A/C Family Analysis
    # ==========================================
    print("=" * 60)
    print("A/C FAMILY ANALYSIS")
    print("=" * 60)
    print()

    ac_results = analyze_position_types(azc_tokens, type_systems, 'ac')

    if 'insufficient_data' in ac_results:
        print("INSUFFICIENT DATA")
    else:
        print(f"C-position types: {ac_results['c_types']}")
        print(f"S-position types: {ac_results['s_types']}")
        print(f"Endemicity - C: {ac_results['endemicity']['c_rate']}%, S: {ac_results['endemicity']['s_rate']}%")
        print(f"Cross-system - C: {ac_results['cross_system']['c_rate']}%, S: {ac_results['cross_system']['s_rate']}%")
        print(f"Avg systems - C: {ac_results['global_reusability']['c_avg']}, S: {ac_results['global_reusability']['s_avg']}")
        print()

    # ==========================================
    # Zodiac Family Analysis
    # ==========================================
    print("=" * 60)
    print("ZODIAC FAMILY ANALYSIS")
    print("=" * 60)
    print()

    zodiac_results = analyze_position_types(azc_tokens, type_systems, 'zodiac')

    if 'insufficient_data' in zodiac_results:
        print("INSUFFICIENT DATA")
    else:
        print(f"C-position types: {zodiac_results['c_types']}")
        print(f"S-position types: {zodiac_results['s_types']}")
        print(f"Endemicity - C: {zodiac_results['endemicity']['c_rate']}%, S: {zodiac_results['endemicity']['s_rate']}%")
        print(f"Cross-system - C: {zodiac_results['cross_system']['c_rate']}%, S: {zodiac_results['cross_system']['s_rate']}%")
        print(f"Avg systems - C: {zodiac_results['global_reusability']['c_avg']}, S: {zodiac_results['global_reusability']['s_avg']}")
        print()

    # ==========================================
    # Evaluation
    # ==========================================
    print("=" * 60)
    print("PRE-REGISTERED EVALUATION")
    print("=" * 60)
    print()

    predictions = {
        'p1_endemicity': False,
        'p2_cross_system': False,
        'p3_reusability': False,
        'p4_invariance': False
    }

    if 'insufficient_data' not in overall:
        # P1: AZC endemicity C > S
        predictions['p1_endemicity'] = overall['endemicity']['c_higher'] and overall['endemicity']['significant']

        # P2: Cross-system persistence S > C
        predictions['p2_cross_system'] = overall['cross_system']['s_higher'] and overall['cross_system']['significant']

        # P3: Global reusability S > C
        predictions['p3_reusability'] = overall['global_reusability']['s_higher'] and overall['global_reusability']['significant']

    # P4: Family invariance (same direction in both families)
    if 'insufficient_data' not in ac_results and 'insufficient_data' not in zodiac_results:
        ac_direction_endemic = ac_results['endemicity']['c_higher']
        zodiac_direction_endemic = zodiac_results['endemicity']['c_higher']

        ac_direction_cross = ac_results['cross_system']['s_higher']
        zodiac_direction_cross = zodiac_results['cross_system']['s_higher']

        # Invariance = same direction in both families for at least endemicity and cross-system
        predictions['p4_invariance'] = bool((ac_direction_endemic == zodiac_direction_endemic) and \
                                       (ac_direction_cross == zodiac_direction_cross))

    # Convert all to Python bool for JSON serialization
    predictions = {k: bool(v) for k, v in predictions.items()}
    predictions_met = sum(predictions.values())

    print(f"P1 (Endemicity C > S, significant): {'MET' if predictions['p1_endemicity'] else 'NOT MET'}")
    print(f"P2 (Cross-system S > C, significant): {'MET' if predictions['p2_cross_system'] else 'NOT MET'}")
    print(f"P3 (Reusability S > C, significant): {'MET' if predictions['p3_reusability'] else 'NOT MET'}")
    print(f"P4 (Family invariance): {'MET' if predictions['p4_invariance'] else 'NOT MET'}")
    print()
    print(f"PREDICTIONS MET: {predictions_met}/4")
    print()

    # Interpretation
    if predictions_met >= 3:
        conclusion = "LOCAL/GLOBAL REFERENCE PARTITION CONFIRMED"
        interpretation = "C = local (AZC-specific) reference space, S = global (cross-system) reference space"
        fit_tier = "F3"
        frame_status = "RETAINED as explanatory compression"
    elif predictions_met >= 1:
        conclusion = "WEAK SUPPORT for local/global partition"
        interpretation = "Partial asymmetry in reference scope"
        fit_tier = "F4"
        frame_status = "NOTED but not promoted"
    else:
        conclusion = "NO SYSTEMATIC DIFFERENCE"
        interpretation = "C and S do not partition reference scope"
        fit_tier = "F4"
        frame_status = "DISCARDED"

    print(f"CONCLUSION: {conclusion}")
    print(f"INTERPRETATION: {interpretation}")
    print(f"Fit tier: {fit_tier}")
    print(f"Frame status: {frame_status}")
    print()
    print("=" * 60)
    print("AZC SEMANTIC EXPLORATION IS NOW COMPLETE")
    print("=" * 60)

    # Prepare output
    output = {
        'fit_id': 'F-AZC-009',
        'semantic_frame': 'C = local (AZC-specific), S = global (cross-system)',
        'tier': 3,
        'pre_registered_predictions': [
            'P1: AZC endemicity C > S',
            'P2: Cross-system persistence S > C',
            'P3: Global reusability S-types > C-types',
            'P4: Family invariance (same pattern in both families)'
        ],
        'success_criterion': '>= 3 of 4 predictions met',
        'metadata': {
            'a_tokens': len(tokens_by_system['A']),
            'b_tokens': len(tokens_by_system['B']),
            'azc_tokens': len(tokens_by_system['AZC']),
            'unique_types': len(type_systems)
        },
        'overall': overall if 'insufficient_data' not in overall else {'insufficient_data': True},
        'ac_family': ac_results if 'insufficient_data' not in ac_results else {'insufficient_data': True},
        'zodiac_family': zodiac_results if 'insufficient_data' not in zodiac_results else {'insufficient_data': True},
        'predictions': predictions,
        'predictions_met': predictions_met,
        'interpretation': {
            'conclusion': conclusion,
            'interpretation': interpretation,
            'fit_tier': fit_tier,
            'frame_status': frame_status
        },
        'stop_condition': 'AZC semantic exploration is COMPLETE after this test'
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_local_global_reference.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
