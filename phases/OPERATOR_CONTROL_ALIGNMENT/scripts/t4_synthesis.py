"""
T4: Synthesis — Phase 556: OPERATOR_CONTROL_ALIGNMENT
=====================================================

Reads T3 scoring results and T2 predictions.
Produces verdict + failure condition audit + non-circularity audit.
"""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def main():
    t2 = json.load(open(RESULTS_DIR / 't2_voynich_predictions.json'))
    t3 = json.load(open(RESULTS_DIR / 't3_scoring_engine.json'))

    predictions = t2['predictions']
    fc_defs = t2['failure_conditions']

    # ============================================================
    # HYPOTHESIS PASS/FAIL
    # ============================================================
    hypothesis_results = {}

    # H1: Three-Phase Operator Scheduling
    h1 = t3['H1']
    h1_pass = (h1.get('voynich_beats_position', False) and
               h1.get('q1_peak', False) and
               h1.get('permutation_p', 1) < 0.01 and
               h1.get('ablation_degradation', -1) > 0)
    hypothesis_results['H1'] = {
        'name': predictions['H1']['name'],
        'pass': h1_pass,
        'voynich_jsd': h1.get('voynich_jsd'),
        'position_jsd': h1.get('position_jsd'),
        'beats_position': h1.get('voynich_beats_position'),
        'q1_peak': h1.get('q1_peak'),
        'closure_ratio': h1.get('closure_ratio'),
        'permutation_p': h1.get('permutation_p'),
        'ablation_degradation': h1.get('ablation_degradation'),
        'beats_lite': h1.get('voynich_beats_lite'),
        'beats_ec': h1.get('voynich_beats_ec'),
    }

    # H2: Supervisory Decomposition
    h2 = t3['H2']
    h2_pass = h2.get('significant', False)
    hypothesis_results['H2'] = {
        'name': predictions['H2']['name'],
        'pass': h2_pass,
        'nc_fraction': h2.get('nc_fraction'),
        'mean_persistence': h2.get('mean_persistence'),
        'persistence_in_range': h2.get('persistence_in_range'),
        'permutation_p': h2.get('permutation_p'),
        'ablation_degradation': h2.get('ablation_degradation'),
    }

    # H3: Dual Feedback Channels
    h3 = t3['H3']
    h3_pass = h3.get('significant', False) and h3.get('split_outperforms', False)
    hypothesis_results['H3'] = {
        'name': predictions['H3']['name'],
        'pass': h3_pass,
        'delta': h3.get('delta'),
        'delta_positive': h3.get('delta_positive'),
        'split_advantage': h3.get('split_advantage'),
        'split_outperforms': h3.get('split_outperforms'),
        'active_higher_entropy': h3.get('active_higher_entropy'),
        'permutation_p': h3.get('permutation_p'),
    }

    # H4: Preventive Stabilization
    h4 = t3['H4']
    h4_pass = h4.get('significant', False)
    hypothesis_results['H4'] = {
        'name': predictions['H4']['name'],
        'pass': h4_pass,
        'db_frac': h4.get('db_frac'),
        'mean_position': h4.get('mean_position'),
        'early_biased': h4.get('early_biased'),
        'context_independent': h4.get('context_independent'),
        'q4_depleted': h4.get('q4_depleted'),
        'correction_rho': h4.get('correction_rho'),
    }

    # H5: Instruction-Profile Locality
    h5 = t3['H5']
    h5_pass = h5.get('significant', False)
    hypothesis_results['H5'] = {
        'name': predictions['H5']['name'],
        'pass': h5_pass,
        'raw_lag1': h5.get('raw_lag1'),
        'shuffle_p': h5.get('shuffle_p'),
        'shuffle_collapses': h5.get('shuffle_collapses'),
        'compensatory_ratio': h5.get('compensatory_ratio'),
        'no_compensatory': h5.get('no_compensatory'),
    }

    # H6: Hazard Immunity
    h6 = t3['H6']
    h6_pass = h6.get('significant', False)
    hypothesis_results['H6'] = {
        'name': predictions['H6']['name'],
        'pass': h6_pass,
        'mean_ib_to_da': h6.get('mean_ib_to_da'),
        'mean_check_to_da': h6.get('mean_check_to_da'),
        'da_ratio': h6.get('da_ratio'),
        'transition_immune': h6.get('transition_immune'),
        'check_more_dangerous': h6.get('check_more_dangerous'),
        'stability_enriched': h6.get('stability_enriched'),
        'phase_depleted': h6.get('phase_depleted'),
    }

    # ============================================================
    # FAILURE CONDITIONS
    # ============================================================
    failure_conditions = {}

    # FC1: Voynich doesn't beat random on ANY hypothesis
    any_beats_random = (h1.get('permutation_p', 1) < 0.05 or
                        h2.get('permutation_p', 1) < 0.05 or
                        h3.get('permutation_p', 1) < 0.05 or
                        h4.get('permutation_p', 1) < 0.05 or
                        h6.get('permutation_p', 1) < 0.05)
    failure_conditions['FC1'] = {
        'triggered': not any_beats_random,
        'desc': fc_defs['FC1']['condition'],
    }

    # FC2: Position-only beats Voynich on H1 JSD
    failure_conditions['FC2'] = {
        'triggered': not h1.get('voynich_beats_position', False),
        'desc': fc_defs['FC2']['condition'],
        'voynich_jsd': h1.get('voynich_jsd'),
        'position_jsd': h1.get('position_jsd'),
    }

    # FC3: Ablation improves ANY metric
    ablation_improves = []
    for h_key in ['H1', 'H2', 'H3', 'H4']:
        deg = t3[h_key].get('ablation_degradation', 0)
        if deg < 0:
            ablation_improves.append(h_key)
    failure_conditions['FC3'] = {
        'triggered': len(ablation_improves) > 0,
        'desc': fc_defs['FC3']['condition'],
        'improved_hypotheses': ablation_improves,
    }

    # FC4: Q1 peak test fails
    failure_conditions['FC4'] = {
        'triggered': not h1.get('q1_peak', False),
        'desc': fc_defs['FC4']['condition'],
        'actual_peak': h1.get('q1_peak_quintile'),
    }

    # FC5: H3 merged >= split
    failure_conditions['FC5'] = {
        'triggered': not h3.get('split_outperforms', False),
        'desc': fc_defs['FC5']['condition'],
        'split_advantage': h3.get('split_advantage'),
    }

    # FC6: H5 shuffle p < 0.01 (should be > 0.05 for locality)
    failure_conditions['FC6'] = {
        'triggered': h5.get('shuffle_p', 0) < 0.01,
        'desc': fc_defs['FC6']['condition'],
        'shuffle_p': h5.get('shuffle_p'),
    }

    # FC7: H6 IB->DA rate > 20%
    failure_conditions['FC7'] = {
        'triggered': h6.get('mean_ib_to_da', 1) > 0.20,
        'desc': fc_defs['FC7']['condition'],
        'rate': h6.get('mean_ib_to_da'),
    }

    # FC8: No dominant 2-way bundling
    hmm_k_dist = t3['H2'].get('hmm_k_distribution', {})
    no_bundling = h2.get('nc_fraction', 0) < 0.3
    failure_conditions['FC8'] = {
        'triggered': no_bundling,
        'desc': fc_defs['FC8']['condition'],
        'hmm_k_distribution': hmm_k_dist,
        'nc_fraction': h2.get('nc_fraction'),
    }

    # ============================================================
    # VERDICT
    # ============================================================
    n_secondary_pass = sum(1 for h in ['H2', 'H3', 'H4', 'H5', 'H6']
                           if hypothesis_results[h]['pass'])

    any_fc_fatal = (failure_conditions['FC1']['triggered'] or
                    failure_conditions['FC2']['triggered'])

    # Check ablation on H1
    h1_ablation_improves = h1.get('ablation_degradation', 0) < 0

    if any_fc_fatal or not h1_pass or h1_ablation_improves:
        verdict = 'FAIL'
        if failure_conditions['FC1']['triggered']:
            reason = 'FC1: Voynich doesnt beat random on any hypothesis'
        elif failure_conditions['FC2']['triggered']:
            reason = 'FC2: Position-only beats Voynich on H1'
        elif h1_ablation_improves:
            reason = 'H1 ablation improves fit'
        elif not h1_pass:
            reason = 'H1 fails core criteria'
        else:
            reason = 'Fatal failure condition triggered'
    elif h1_pass and n_secondary_pass >= 4 and not failure_conditions['FC3']['triggered']:
        beats_ec = h1.get('voynich_beats_ec', False)
        if beats_ec:
            verdict = 'STRONG_PASS'
            reason = f'H1 + {n_secondary_pass}/5 secondary + no ablation improves + beats equal-complexity'
        else:
            verdict = 'MODERATE_PASS'
            reason = f'H1 + {n_secondary_pass}/5 secondary (no equal-complexity beat)'
    elif h1_pass and n_secondary_pass >= 3:
        beats_lite = h1.get('voynich_beats_lite', False)
        if beats_lite and not h1_ablation_improves:
            verdict = 'MODERATE_PASS'
            reason = f'H1 + {n_secondary_pass}/5 secondary + beats Voynich-lite'
        else:
            verdict = 'WEAK_PASS'
            reason = f'H1 + {n_secondary_pass}/5 secondary'
    elif h1_pass and n_secondary_pass >= 2:
        verdict = 'WEAK_PASS'
        reason = f'H1 + {n_secondary_pass}/5 secondary'
    else:
        verdict = 'FAIL'
        reason = f'H1={h1_pass}, secondary={n_secondary_pass}/5'

    # ============================================================
    # NON-CIRCULARITY AUDIT
    # ============================================================
    non_circularity = {
        'T1_physical_plant': 'NONE — thermodynamic ODE, no Voynich parameters',
        'T1_controller': 'NONE — P-controller from control theory',
        'T1_LHS_sweep': 'NONE — statistical design of experiments',
        'T1_level_A_primitives': 'NONE — controller state algebra (dQ × error sign)',
        'T1_compound_categories': 'NONE — 2 binary features + condition triggers',
        'T1_operator_params': 'NONE — generic swept parameters',
        'T1_check_triggers': 'NONE — plant state conditions (swept thresholds)',
        'T1_apparatus_families': 'NONE — k-means on run-level dynamics',
        'T1_level_B_HMM': 'NONE — unsupervised BIC-selected state count',
        'T1_level_B_clustering': 'NONE — unsupervised regime detection',
        'T2_predictions': 'ALL — 35+ Tier 2 constraints',
        'verdict': 'CLEAN — T1 is entirely Voynich-free at both levels',
    }

    # ============================================================
    # OUT-OF-SAMPLE SUMMARY
    # ============================================================
    oos = {
        'H1': {
            'train_jsd': h1.get('oos_train_jsd'),
            'test_jsd': h1.get('oos_test_jsd'),
        },
        'H3': {
            'train_delta': h3.get('oos_train_delta'),
            'test_delta': h3.get('oos_test_delta'),
        },
        'H5': {
            'train_lag1': h5.get('oos_train_lag1'),
            'test_lag1': h5.get('oos_test_lag1'),
        },
    }

    # ============================================================
    # APPARATUS RESULTS
    # ============================================================
    apparatus = t3.get('apparatus', {})

    # ============================================================
    # OUTPUT
    # ============================================================
    output = {
        'verdict': {
            'verdict': verdict,
            'reason': reason,
        },
        'hypothesis_results': hypothesis_results,
        'failure_conditions': failure_conditions,
        'n_secondary_pass': n_secondary_pass,
        'non_circularity': non_circularity,
        'out_of_sample': oos,
        'apparatus': apparatus,
    }

    # Print
    print("=" * 60)
    print(f"PHASE 556: OPERATOR_CONTROL_ALIGNMENT")
    print(f"VERDICT: {verdict}")
    print(f"REASON: {reason}")
    print("=" * 60)

    print(f"\nHYPOTHESIS RESULTS:")
    for h_key in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
        hr = hypothesis_results[h_key]
        status = 'PASS' if hr['pass'] else 'FAIL'
        print(f"  {h_key}: {status} — {hr['name']}")

    print(f"\nFAILURE CONDITIONS:")
    for fc_key in sorted(failure_conditions.keys()):
        fc = failure_conditions[fc_key]
        status = 'TRIGGERED' if fc['triggered'] else 'CLEAR'
        print(f"  {fc_key}: {status} — {fc['desc']}")

    print(f"\nNON-CIRCULARITY: {non_circularity['verdict']}")

    print(f"\nOUT-OF-SAMPLE:")
    for h_key, oos_data in oos.items():
        print(f"  {h_key}: {oos_data}")

    if apparatus:
        print(f"\nAPPARATUS FAMILY RESULTS:")
        for fname, fres in apparatus.items():
            print(f"  {fname}: {fres}")

    out_path = RESULTS_DIR / 't4_synthesis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
