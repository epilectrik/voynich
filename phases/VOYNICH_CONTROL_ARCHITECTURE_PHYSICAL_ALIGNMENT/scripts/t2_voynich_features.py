"""
T2: Voynich Structural Feature Extraction (REDESIGNED)
======================================================
Phase: VOYNICH_CONTROL_ARCHITECTURE_PHYSICAL_ALIGNMENT

Redesign: Reframes predictions around OPERATOR CONTROL SCHEDULING,
not raw physical risk. Maps Voynich hazard classes to operator action types:
  - ZERO → PROACTIVE (planned setup/heating toward target)
  - IMMUNE → NEUTRAL (stable work near setpoint)
  - HIGH → REACTIVE (correction/containment after overshoot)

All values from published, validated constraints (Tier 2).
NO physical simulation data enters this script.

Output: t2_voynich_features.json
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def build_h1_safety_envelope():
    """H1: Safety-envelope as OPERATOR SCHEDULING prediction.

    The Voynich zone-hazard profile predicts HOW THE OPERATOR ACTS
    at different points in the control cycle, not where physical danger peaks.

    Source: C1463, C1464, C1426-C1428, C1566
    """
    # Zone-hazard enrichment (C1463)
    zone_hazard_enrichment = {
        'Q0': {'HIGH': 0.836, 'LOW': 1.021, 'ZERO': 1.236, 'IMMUNE': 0.826, 'N': 5022},
        'Q1-Q3': {'HIGH': 1.006, 'LOW': 0.940, 'ZERO': 1.019, 'IMMUNE': 1.165, 'N': 12507},
        'Q4': {'HIGH': 1.134, 'LOW': 1.116, 'ZERO': 0.743, 'IMMUNE': 0.786, 'N': 5561},
    }

    # Per-quintile enrichment with k-HEAD peaks (C1464)
    quintile_hazard = {
        'Q0': {'HIGH': 0.836, 'ZERO': 1.236, 'IMMUNE': 0.826},
        'Q1': {'HIGH': 1.006, 'ZERO': 1.019, 'IMMUNE': 1.311},
        'Q2': {'HIGH': 1.006, 'ZERO': 1.019, 'IMMUNE': 1.113},
        'Q3': {'HIGH': 1.006, 'ZERO': 1.019, 'IMMUNE': 1.069},
        'Q4': {'HIGH': 1.134, 'ZERO': 0.743, 'IMMUNE': 0.786},
    }

    # OPERATOR-LAYER MAPPING (the redesign)
    # ZERO → PROACTIVE: operator is in planned setup mode (safe, controlled)
    # IMMUNE → NEUTRAL: operator near setpoint, stable work (immune to danger)
    # HIGH → REACTIVE: operator correcting overshoot (dangerous, reactive)
    operator_mapping = {
        'ZERO': 'PROACTIVE',
        'IMMUNE': 'NEUTRAL',
        'HIGH': 'REACTIVE',
    }

    # Predicted operator action profile per quintile
    # PROACTIVE should follow ZERO enrichment pattern (peaks at Q0)
    # NEUTRAL should follow IMMUNE enrichment pattern (peaks at Q1-Q3, esp Q1)
    # REACTIVE should follow HIGH enrichment pattern (peaks at Q4)
    predicted_operator_profile = {
        'Q0': {'PROACTIVE': 1.236, 'NEUTRAL': 0.826, 'REACTIVE': 0.836},
        'Q1': {'PROACTIVE': 1.019, 'NEUTRAL': 1.311, 'REACTIVE': 1.006},
        'Q2': {'PROACTIVE': 1.019, 'NEUTRAL': 1.113, 'REACTIVE': 1.006},
        'Q3': {'PROACTIVE': 1.019, 'NEUTRAL': 1.069, 'REACTIVE': 1.006},
        'Q4': {'PROACTIVE': 0.743, 'NEUTRAL': 0.786, 'REACTIVE': 1.134},
    }

    # Ordered contrast predictions
    ordered_contrasts = {
        'PROACTIVE_peaks_Q0': True,     # ZERO enrichment highest at Q0
        'NEUTRAL_peaks_Q1': True,       # IMMUNE (k-HEAD) peaks at Q1
        'REACTIVE_peaks_Q4': True,      # HIGH enrichment highest at Q4
        'PROACTIVE_Q0_gt_Q4': True,     # 1.236 > 0.743
        'REACTIVE_Q4_gt_Q0': True,      # 1.134 > 0.836
    }

    # Why this mapping works (control theory rationale):
    # Q0 = cycle start, T below target → operator PROACTIVELY heats (planned, safe)
    # Q1 = approaching setpoint → thermal work onset, NEUTRAL (near-equilibrium)
    # Q2-Q3 = at/past setpoint → overshoot zone, mixed
    # Q4 = returning from overshoot → operator REACTIVELY corrects (delayed response)
    #
    # The operator delay (0.3 time units) means the correction response to
    # Q2-Q3 overshoot arrives at Q4. This is WHY HIGH concentrates at closure:
    # not because danger peaks there, but because the operator's correction does.

    return {
        'zone_hazard_enrichment': zone_hazard_enrichment,
        'quintile_hazard': quintile_hazard,
        'operator_mapping': operator_mapping,
        'predicted_operator_profile': predicted_operator_profile,
        'ordered_contrasts': ordered_contrasts,
        'rationale': (
            'The Voynich zone-hazard profile predicts operator action scheduling, '
            'not raw physical risk. ZERO at Q0 = planned setup. IMMUNE at Q1 = stable '
            'work onset. HIGH at Q4 = reactive correction (delayed response to overshoot).'
        ),
        'sources': ['C1463', 'C1464', 'C1426', 'C1427', 'C1428', 'C1566'],
    }


def build_h2_mode_decomposition():
    """H2: Two-state supervisory decomposition.

    Sources: C1229, C1231, C1309, C1341, C1410, C1515
    """
    mode_centroids = {
        'A': [0.430, 0.019, 0.086, 0.466],
        'B': [0.155, 0.031, 0.072, 0.741],
    }

    clustering = {
        'k2_win_rate': 0.965,
        'mean_silhouette_k2': 0.459,
        'non_contiguous_interleaving': 0.800,
    }

    category_profile = {
        'A': {'THERMAL': 0.429, 'OPERATION': 0.148, 'MONITORING': 0.058,
              'CONTAINMENT': 0.055, 'STAGING': 0.053},
        'B': {'THERMAL': 0.358, 'FLOW': 0.227, 'STAGING': 0.114,
              'TRANSITION': 0.088, 'MONITORING': 0.011},
    }

    # Operator-level analogues
    # Mode A = specification: high intervention, active adjustment, parameter setting
    # Mode B = continuation: passive monitoring, flow accumulation, steady operation
    operator_analogues = {
        'A': {
            'intervention_density': 'HIGH',
            'active_frac': 'HIGH',
            'proactive_frac': 'HIGH',  # more planned actions
            'reactive_frac': 'HIGH',   # more corrections too
            'Q_var': 'HIGH',           # more actuator variation
            'dQ_var': 'HIGH',
            'boundary_frac': 'HIGH',
            'passive_frac': 'LOW',
        },
        'B': {
            'intervention_density': 'LOW',
            'active_frac': 'LOW',
            'proactive_frac': 'LOW',
            'reactive_frac': 'LOW',
            'Q_var': 'LOW',
            'dQ_var': 'LOW',
            'boundary_frac': 'LOW',
            'passive_frac': 'HIGH',
            'phi_accum': 'HIGH',       # more flow/accumulation
            'neutral_frac': 'HIGH',    # more stable-state time
        },
    }

    return {
        'centroids': mode_centroids,
        'clustering': clustering,
        'category_profile': category_profile,
        'operator_analogues': operator_analogues,
        'emergence': {'token_identity_prediction': 0.80, 'source': 'C1341'},
        'sources': ['C1229', 'C1231', 'C1309', 'C1341', 'C1410', 'C1515'],
    }


def build_h3_feedback_channels():
    """H3: Dual feedback channel (ch/sh).

    Sources: C929, C1203, C1243, C1299
    """
    positions = {
        'sh_mean_position': 0.396,
        'ch_mean_position': 0.515,
        'delta': 0.120,
    }

    sh_following = {'heat': 0.183, 'sustained_heat': 0.040, 'close': 0.043,
                    'check': 0.038, 'bare': 0.590}
    ch_following = {'heat': 0.106, 'close': 0.066, 'input': 0.042,
                    'iterate': 0.031, 'check': 0.058, 'bare': 0.469}

    # Operator-level mapping
    # sh (passive monitoring) → operator watches without acting
    # ch (active testing) → operator deliberately checks/adjusts
    # Passive events should be front-loaded, active events back-loaded
    operator_mapping = {
        'sh': {'role': 'PASSIVE_MONITORING', 'physical': 'low |dQ|, observation window'},
        'ch': {'role': 'ACTIVE_CHECKING', 'physical': 'high |dQ|, deliberate adjustment'},
    }

    return {
        'positions': positions,
        'sh_following': sh_following,
        'ch_following': ch_following,
        'operator_mapping': operator_mapping,
        'split_prediction': {
            'split_outperforms_merged': True,
            'positional_separation': 0.120,
        },
        'sources': ['C929', 'C1203', 'C1243', 'C1299'],
    }


def build_h4_thermal_work():
    """H4: Thermal-work neutralization (k-domain).

    Sources: C1446, C1464, C1475, C1476, C1477
    """
    k_hazard = {'any_hazard': 0.000, 'N': 3100}
    k_category = {'THERMAL': 0.903, 'THERMAL_enrichment': 3.80}
    k_quintile = {'Q0': 0.826, 'Q1': 1.311, 'Q2': 1.113, 'Q3': 1.069, 'Q4': 0.786}

    # Operator-level mapping
    # k = thermally active + structurally immune
    # Physical analogue: HOT_STABLE = near/above boiling, low |dT|, controlled
    # k peaks at Q1 = the operator's thermal work ENGAGEMENT point
    # After the initial ramp (Q0), the system reaches operating temperature (Q1)
    # The operator enters stable thermal management mode
    operator_mapping = {
        'target_state': 'HOT_STABLE',
        'Q1_peak_rationale': (
            'k-HEAD peaks at Q1 because that is where the operator ENTERS the stable '
            'thermal work zone. The system has just reached operating temperature. '
            'The operator transitions from PROACTIVE heating to NEUTRAL steady-state work.'
        ),
    }

    return {
        'k_hazard': k_hazard,
        'k_category': k_category,
        'k_quintile': k_quintile,
        'operator_mapping': operator_mapping,
        'sources': ['C1446', 'C1464', 'C1475', 'C1476', 'C1477'],
    }


def build_h5_closure_containment():
    """H5: Line-local closure containment.

    Sources: C1434-C1445, C1463-C1471
    """
    closure_risk = {
        'Q0_HIGH_enrichment': 0.836,
        'Q4_HIGH_enrichment': 1.134,
        'closure_danger_ratio': 1.134 / 0.836,
    }

    cross_line = {
        'shuffle_p_value': 0.212,
        'interpretation': 'No significant cross-line memory after folio control',
    }

    # Operator-level mapping
    # HIGH at Q4 doesn't mean physical danger peaks at Q4
    # It means the OPERATOR'S CORRECTION ACTIONS concentrate at Q4
    # The overshoot happens at Q2-Q3; the delayed response arrives at Q4
    # The "closure containment" is the operator packaging the correction response
    operator_mapping = {
        'prediction': (
            'REACTIVE operator actions (corrective, containment) concentrate at Q4. '
            'This is the delayed response to Q2-Q3 overshoot. The operator delay '
            'creates a natural lag: danger at Q3, correction at Q4.'
        ),
        'cross_cycle_independence': True,
        'test': 'REACTIVE fraction at Q4 > Q0, matching HIGH enrichment pattern',
    }

    return {
        'closure_risk': closure_risk,
        'cross_line': cross_line,
        'operator_mapping': operator_mapping,
        'sources': ['C1434', 'C1463', 'C1470', 'C1471'],
    }


def main():
    output = {
        'description': 'Voynich structural predictions — OPERATOR SCHEDULING LAYER',
        'tier_discipline': (
            'A positive result validates architecture-level alignment only; '
            'it does not validate lexical glosses.'
        ),
        'redesign_rationale': (
            'V1 tested raw physical risk against Voynich zones — wrong layer. '
            'The Voynich describes OPERATOR CONTROL SCHEDULING: where the operator '
            'places setup/work/containment actions within the control cycle. '
            'V2 maps Voynich hazard classes to operator action types: '
            'ZERO→PROACTIVE, IMMUNE→NEUTRAL, HIGH→REACTIVE.'
        ),
        'hypotheses': {
            'H1_safety_envelope': build_h1_safety_envelope(),
            'H2_mode_decomposition': build_h2_mode_decomposition(),
            'H3_feedback_channels': build_h3_feedback_channels(),
            'H4_thermal_work': build_h4_thermal_work(),
            'H5_closure_containment': build_h5_closure_containment(),
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't2_voynich_features.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"{'='*60}")
    print(f"T2 VOYNICH FEATURES (REDESIGNED) COMPLETE")
    print(f"{'='*60}")
    for name in output['hypotheses']:
        n_src = len(output['hypotheses'][name]['sources'])
        print(f"  {name}: {n_src} source constraints")
    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
