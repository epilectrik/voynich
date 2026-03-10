"""
T2: Voynich Predictions — Phase 557: PREDICTIVE_SUPERVISORY_CONTROL_ALIGNMENT
==============================================================================

All prediction values derived from Tier 2 constraints.
No simulation data used. Independent of T1.

Hypotheses:
  H1: Three-Phase Operator Scheduling + Closure Discontinuity
  H2: Inferred Supervisory Decomposition (Dominant Two-Way)
  H3: Dual Feedback Channels (Passive Before Active)
  H4: Preventive Stabilization Channel
  H5: Instruction-Profile Locality (Cross-Cycle Independence)
  H6: Hazard Immunity of Energy Operations

Identical to Phase 556 T2 — predictions are from Tier 2 constraints only.
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def build_predictions():
    """Build all hypothesis predictions from Tier 2 constraints."""

    predictions = {}

    # ==============================================================
    # H1: Three-Phase Operator Scheduling + Closure Discontinuity
    # Sources: C1463-C1466, C1464, C1428, C1434-C1445, C1566
    # ==============================================================
    predictions['H1'] = {
        'name': 'Three-Phase Operator Scheduling + Closure Discontinuity',
        'sources': ['C1463', 'C1464', 'C1466', 'C1428', 'C1434-C1445', 'C1566'],

        # Quintile enrichment profile for compound actions
        # ZERO enrichment 1.236x at Q0 (C1463): setup/preventive
        # k-HEAD 1.311x at Q1 (C1464): peak heating
        # Interior JSD < 0.003 (C1566): homogeneous
        # HIGH enrichment 1.134x at Q4 (C1463): correction/wind-down
        'quintile_dominant': {
            'Q0': ['HOLD_AT', 'DECREASE_BELOW'],
            'Q1': ['INCREASE_BELOW'],
            'Q2': ['INCREASE_BELOW', 'HOLD_AT'],
            'Q3': ['INCREASE_BELOW', 'HOLD_AT'],
            'Q4': ['DECREASE_ABOVE', 'HOLD_OFF'],
        },

        # Voynich-predicted enrichment profile (normalized)
        # Q0: setup/zero-enriched, Q1: peak energy, Q2-Q3: flat interior, Q4: closure
        'enrichment_profile': {
            'Q0': {'INCREASE_BELOW': 0.836, 'DECREASE_BELOW': 1.236,
                   'HOLD_AT': 1.1, 'CHECK': 1.0},
            'Q1': {'INCREASE_BELOW': 1.311, 'DECREASE_BELOW': 0.9,
                   'HOLD_AT': 0.9, 'CHECK': 1.0},
            'Q2': {'INCREASE_BELOW': 1.006, 'DECREASE_BELOW': 1.006,
                   'HOLD_AT': 1.006, 'CHECK': 1.0},
            'Q3': {'INCREASE_BELOW': 1.006, 'DECREASE_BELOW': 1.006,
                   'HOLD_AT': 1.006, 'CHECK': 1.0},
            'Q4': {'INCREASE_BELOW': 0.7, 'DECREASE_ABOVE': 1.134,
                   'HOLD_OFF': 1.2, 'CHECK': 1.0},
        },

        # Structural tests
        'tests': {
            # Q1 peak: INCREASE_BELOW must peak at Q1, not Q0 or elsewhere
            'q1_peak': {
                'action': 'INCREASE_BELOW',
                'peak_quintile': 1,
                'basis': 'C1464: k-HEAD enrichment 1.311x at Q1',
            },
            # Q3->Q4 closure discontinuity: abrupt, not gradual
            'closure_discontinuity': {
                'ratio_threshold': 5.0,
                'basis': 'C1566: 26x HEAD discontinuity at closure boundary',
            },
            # Opening-closure asymmetry in full symmetric cycles
            'asymmetry': {
                'increase_below_concentrate': [0, 1],  # Q0-Q1
                'decrease_above_concentrate': [3, 4],   # Q3-Q4
                'basis': 'Full trough-to-trough physics is symmetric; asymmetry = operator',
            },
            # Must beat position-only
            'beat_position_only': True,
        },

        # Pass criteria
        'pass_criteria': {
            'q1_peak_required': True,
            'closure_ratio_min': 5.0,
            'voynich_beats_position_only': True,
            'alpha': 0.01,
        },
    }

    # ==============================================================
    # H2: Inferred Supervisory Decomposition (Dominant Two-Way)
    # Sources: C1229-C1231, C1410, C1422, C1423, C1515
    # ==============================================================
    predictions['H2'] = {
        'name': 'Inferred Supervisory Decomposition (Dominant Two-Way)',
        'sources': ['C1229', 'C1230', 'C1231', 'C1410', 'C1422', 'C1423', 'C1515'],

        # BIC may select k>2; test dominant two-way bundling
        'dominant_two_way': True,

        # Bundle A (Mode A = specification): high intervention
        # Bundle B (Mode B = continuation): high hold/observation
        'bundle_signatures': {
            'A': {
                'high_intervention': True,
                'enriched_actions': ['INCREASE_BELOW', 'DECREASE_ABOVE', 'DECREASE_BELOW'],
                'basis': 'C1229-C1231: Mode A = specification, active intervention',
            },
            'B': {
                'high_observation': True,
                'enriched_actions': ['HOLD_AT', 'HOLD_OFF', 'CHECK'],
                'basis': 'C1229-C1231: Mode B = continuation, passive monitoring',
            },
        },

        # Interleaving: non-contiguous in >= 70% of cycles (C1229: 80%)
        'interleaving_threshold': 0.70,
        'interleaving_target': 0.80,

        # Persistence: ~60% within-cycle (C1423: switch rate 39.4%)
        'persistence_target': 0.606,
        'persistence_range': (0.45, 0.75),

        # Local determination: ~80% from action context (C1422)
        'local_determination_threshold': 0.60,
        'local_determination_target': 0.80,

        'pass_criteria': {
            'two_way_bundling_exists': True,
            'cosine_similarity_min': 0.5,
            'interleaving_min': 0.60,
            'persistence_in_range': True,
            'alpha': 0.01,
        },
    }

    # ==============================================================
    # H3: Dual Feedback Channels (Passive Before Active)
    # Sources: C929, C1243, C1299
    # ==============================================================
    predictions['H3'] = {
        'name': 'Dual Feedback Channels (Passive Before Active)',
        'sources': ['C929', 'C1243', 'C1299'],

        # Passive observation front-loads, active checking mid-to-late
        'passive_mean_position': 0.40,
        'active_mean_position': 0.52,
        'positional_delta_min': 0.06,

        # Routing difference after passive vs active observation
        'routing': {
            # After passive -> INCREASE_BELOW at higher rate (C1243: sh->heat = 32%)
            'passive_to_increase_below_rate': 0.32,
            # After CHECK -> higher entropy (diverse next actions)
            'active_higher_entropy': True,
            'basis': 'C1243: sh routes to heat 32%; ch branches diversely',
        },

        # Two-channel split must outperform merged single-observation
        'split_must_outperform_merged': True,

        'pass_criteria': {
            'delta_positive': True,
            'delta_min': 0.03,
            'split_advantage_positive': True,
            'alpha': 0.01,
        },
    }

    # ==============================================================
    # H4: Preventive Stabilization Channel
    # Sources: C1457-C1462
    # ==============================================================
    predictions['H4'] = {
        'name': 'Preventive Stabilization Channel',
        'sources': ['C1457', 'C1458', 'C1459', 'C1460', 'C1461', 'C1462'],

        # DECREASE_BELOW must exist at substantial rate
        'existence_min_fraction': 0.02,

        # Early-biased: mean position matching e->y at 0.463 (C1460)
        'mean_position_target': 0.463,
        'mean_position_max': 0.50,

        # Context-independent: rate doesn't depend on previous cycle's corrections
        # Post-correction-heavy rate ~ post-quiet rate (< 5pp, C1459: 0.3pp)
        'context_independence_max_diff': 0.05,
        'context_independence_target_diff': 0.003,

        # Correction-burden-reducing: rho(prevention, correction) negative
        # C1462: e->y rate predicts AXM stability, rho=+0.569
        'correction_reduction_rho_target': -0.30,

        # Q4 avoidance: depleted at Q4 (< 0.6x enrichment, C1460)
        'q4_depletion_max': 0.6,

        'pass_criteria': {
            'exists': True,
            'early_biased': True,
            'context_independent': True,
            'correction_reducing': True,
            'q4_depleted': True,
            'alpha': 0.01,
        },
    }

    # ==============================================================
    # H5: Instruction-Profile Locality (Cross-Cycle Independence)
    # Sources: C1470, C1471
    # ==============================================================
    predictions['H5'] = {
        'name': 'Instruction-Profile Locality (Cross-Cycle Independence)',
        'sources': ['C1470', 'C1471'],

        # Raw lag-1 correlation > 0.15 (real signal from shared parameterization)
        'raw_lag1_min': 0.15,
        'raw_lag1_target': 0.238,

        # Within-parameterization shuffle collapses correlation
        'shuffle_collapse_p_min': 0.05,

        # No compensatory pattern: after high-correction cycles,
        # next cycle does NOT show enriched prevention
        # C1471: e->y DEPLETED 0.82x after high-hazard lines
        'compensatory_ratio_max': 1.0,
        'compensatory_ratio_target': 0.82,

        # Inferred supervisory profile also resets
        'hmm_profile_independence': True,

        'pass_criteria': {
            'raw_correlation_positive': True,
            'shuffle_collapses': True,
            'no_compensatory': True,
            'alpha': 0.01,
        },
    }

    # ==============================================================
    # H6: Hazard Immunity of Energy Operations
    # Sources: C1446, C1464, C1475-C1477
    # ==============================================================
    predictions['H6'] = {
        'name': 'Hazard Immunity of Energy Operations',
        'sources': ['C1446', 'C1464', 'C1475', 'C1476', 'C1477'],

        # INCREASE_BELOW -> DECREASE_ABOVE transition rate < 5%
        # (C1446: k-HEAD 0/3100 in forbidden pairs)
        'ib_to_da_max': 0.05,

        # CHECK -> DECREASE_ABOVE substantially higher
        # (C1477: a-HEAD 66% forbidden rate)
        'check_to_da_ratio_min': 3.0,

        # INCREASE_BELOW concentrates in low-volatility windows
        # (C1475: THERMAL 90.3%)
        'ib_low_stability_enrichment_min': 1.2,

        # INCREASE_BELOW depleted during high phase_activity
        'ib_high_phase_depletion_max': 0.8,

        # Must outperform generic-heating and generic-low-risk baselines
        'beat_generic_heating': True,
        'beat_generic_low_risk': True,

        'pass_criteria': {
            'transition_immunity': True,
            'check_more_dangerous': True,
            'stability_enriched': True,
            'phase_depleted': True,
            'alpha': 0.01,
        },
    }

    return predictions


def build_alternatives():
    """Build alternative model specifications for competitive testing."""

    alternatives = {}

    # H1 alternatives
    alternatives['H1'] = {
        'position_only': {
            'desc': 'Linear gradient Q0->Q4',
            'profile': {f'Q{q}': q / 4.0 for q in range(5)},
        },
        'random': {
            'desc': 'Shuffled action distributions',
            'n_permutations': 1000,
        },
        'reversed': {
            'desc': 'Q4=safe, Q0=dangerous (opposite)',
            'profile': {f'Q{q}': (4 - q) / 4.0 for q in range(5)},
        },
        'flat': {
            'desc': 'Uniform distribution across quintiles',
            'profile': {f'Q{q}': 0.2 for q in range(5)},
        },
        'voynich_lite': {
            'desc': '3-phase (SETUP/RUN/CLOSE) without Q1 peak or Q3->Q4 step',
            'profile': {
                'Q0': {'HOLD_AT': 1.2, 'DECREASE_BELOW': 1.1},
                'Q1': {'INCREASE_BELOW': 1.0, 'HOLD_AT': 1.0},
                'Q2': {'INCREASE_BELOW': 1.0, 'HOLD_AT': 1.0},
                'Q3': {'INCREASE_BELOW': 0.9, 'HOLD_AT': 1.0},
                'Q4': {'DECREASE_ABOVE': 1.1, 'HOLD_OFF': 1.1},
            },
        },
        'equal_complexity': {
            'desc': 'Same dimensionality, DIFFERENT structural commitments',
            'profile': {
                'Q0': {'INCREASE_BELOW': 1.311},  # Q0 peak (not Q1)
                'Q1': {'INCREASE_BELOW': 1.0},
                'Q2': {'INCREASE_BELOW': 1.0},
                'Q3': {'DECREASE_ABOVE': 1.05},    # Gradual closure
                'Q4': {'DECREASE_ABOVE': 1.10},     # Not abrupt step
            },
        },
    }

    # H2 alternatives
    alternatives['H2'] = {
        'random_2state': {
            'desc': 'Random 2-state labels',
        },
        'no_mode': {
            'desc': 'Single state (no decomposition)',
        },
        'high_persistence': {
            'desc': 'Persistence > 0.85 (too sticky)',
            'persistence': 0.85,
        },
        'low_persistence': {
            'desc': 'Persistence < 0.40 (too chaotic)',
            'persistence': 0.40,
        },
        'generic_2state': {
            'desc': 'High/low intervention (no Voynich composition)',
            'split_by': 'intervention_density_only',
        },
    }

    # H3 alternatives
    alternatives['H3'] = {
        'reversed': {
            'desc': 'Active before passive',
            'passive_pos': 0.52,
            'active_pos': 0.40,
        },
        'zero_delta': {
            'desc': 'No positional separation',
            'delta': 0.0,
        },
        'position_only': {
            'desc': 'Position predicts observation type',
        },
        'merged': {
            'desc': 'Single observation type (no passive/active split)',
        },
    }

    # H4 alternatives
    alternatives['H4'] = {
        'reactive': {
            'desc': 'Prevention rate proportional to recent corrections',
        },
        'front_loaded': {
            'desc': 'All prevention at Q0 only',
        },
        'back_loaded': {
            'desc': 'All prevention at Q3-Q4',
        },
        'no_prevention': {
            'desc': 'DECREASE_BELOW is noise, not meaningful',
        },
    }

    # H5 alternatives
    alternatives['H5'] = {
        'full_correlation': {
            'desc': 'No shuffle collapse (cycle-to-cycle memory)',
        },
        'zero_correlation': {
            'desc': 'No raw lag-1 signal',
        },
        'anti_correlation': {
            'desc': 'Compensatory cross-cycle pattern',
        },
    }

    # H6 alternatives
    alternatives['H6'] = {
        'equal_rates': {
            'desc': 'INCREASE and CHECK equally likely before CORRECT',
        },
        'reversed': {
            'desc': 'INCREASE more likely to precede CORRECT',
        },
        'physical_delay': {
            'desc': 'Heating always leads to correction after delay',
        },
        'generic_heating': {
            'desc': 'Any dQ > 0 (no proactive/reactive distinction)',
        },
        'generic_low_risk': {
            'desc': 'Any action in low-stability windows',
        },
    }

    return alternatives


def build_ablations():
    """Build ablation specifications."""
    return {
        'H1': {
            'remove': 'Q1 peak + Q3->Q4 discontinuity',
            'replace_with': 'Linear gradient',
        },
        'H2': {
            'remove': 'Mode composition signature',
            'replace_with': 'Generic 2-state (high/low intervention)',
        },
        'H3': {
            'remove': 'Positional ordering',
            'replace_with': 'Separation magnitude only',
        },
        'H4': {
            'remove': 'Context independence + correction reduction',
            'replace_with': 'Q0-Q1 enrichment only',
        },
        'H5': {
            'remove': 'Parameterization conditioning',
            'replace_with': 'Raw independence test',
        },
        'H6': {
            'remove': 'Hazard class specificity',
            'replace_with': 'Overall correction rate',
        },
    }


def build_failure_conditions():
    """Build pre-registered failure conditions."""
    return {
        'FC1': {
            'condition': 'Voynich does not beat random on ANY hypothesis',
            'consequence': 'FAIL ALL',
        },
        'FC2': {
            'condition': 'Position-only beats Voynich on H1 JSD',
            'consequence': 'FAIL (repeats Phase 555 failure)',
        },
        'FC3': {
            'condition': 'Ablation improves ANY metric',
            'consequence': 'That hypothesis fails',
        },
        'FC4': {
            'condition': 'H1 Q1 peak test fails (INCREASE_BELOW doesnt peak at Q1)',
            'consequence': 'Core prediction failure',
        },
        'FC5': {
            'condition': 'H3 merged >= split',
            'consequence': 'Phase 555 FC3 repeated',
        },
        'FC6': {
            'condition': 'H5 shuffle p < 0.01 at operator level',
            'consequence': 'Instruction locality violated',
        },
        'FC7': {
            'condition': 'H6 INCREASE_BELOW -> DECREASE_ABOVE rate > 20%',
            'consequence': 'Hazard immunity fails',
        },
        'FC8': {
            'condition': 'BIC selects k=1 for HMM OR no dominant 2-way bundling exists',
            'consequence': 'H2 structurally impossible',
        },
    }


def main():
    predictions = build_predictions()
    alternatives = build_alternatives()
    ablations = build_ablations()
    failure_conditions = build_failure_conditions()

    output = {
        'predictions': predictions,
        'alternatives': alternatives,
        'ablations': ablations,
        'failure_conditions': failure_conditions,
        'verdict_criteria': {
            'STRONG_PASS': 'H1 + 4/5 H2-H6 + no ablation improves + OOS stable + beats equal-complexity',
            'MODERATE_PASS': 'H1 + 3/5 H2-H6 + ablation doesnt improve H1 + beats Voynich-lite',
            'WEAK_PASS': 'H1 + 2/5 H2-H6',
            'FAIL': 'H1 fails OR position-only beats Voynich on H1 OR ablation improves H1',
        },
        'non_circularity': {
            'T2_source': 'ALL values from Tier 2 constraints',
            'T1_input': 'NONE — T2 is independent of simulation',
            'constraint_files': [
                'C929', 'C1229-C1231', 'C1243', 'C1299',
                'C1410', 'C1422', 'C1423', 'C1428',
                'C1434-C1445', 'C1446', 'C1457-C1462',
                'C1463-C1466', 'C1470', 'C1471',
                'C1475-C1477', 'C1515', 'C1566',
            ],
        },
    }

    # Print summary
    print("T2: VOYNICH PREDICTIONS")
    print("=" * 50)
    for h_key in sorted(predictions.keys()):
        h = predictions[h_key]
        print(f"\n{h_key}: {h['name']}")
        print(f"  Sources: {', '.join(h['sources'])}")
        print(f"  Pass criteria: {list(h['pass_criteria'].keys())}")

    print(f"\nAlternatives per hypothesis:")
    for h_key in sorted(alternatives.keys()):
        print(f"  {h_key}: {list(alternatives[h_key].keys())}")

    print(f"\nFailure conditions: {list(failure_conditions.keys())}")

    out_path = RESULTS_DIR / 't2_voynich_predictions.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nOutput: {out_path}")
    print(f"Size: {out_path.stat().st_size / 1e3:.1f} KB")


if __name__ == '__main__':
    main()
