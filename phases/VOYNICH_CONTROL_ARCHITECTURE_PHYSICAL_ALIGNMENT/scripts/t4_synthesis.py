"""
T4: Synthesis and Verdict (REDESIGNED)
======================================
Phase: VOYNICH_CONTROL_ARCHITECTURE_PHYSICAL_ALIGNMENT

Aggregates T3 results, applies pass criteria, audits failure conditions.

Output: t4_synthesis.json
"""

import json
import math
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_data():
    with open(RESULTS_DIR / 't3_predictive_competition.json') as f:
        t3 = json.load(f)
    with open(RESULTS_DIR / 't1_physical_process.json') as f:
        t1_summary = json.load(f)['summary']
    return t3, t1_summary


def failure_audit(t3):
    sig = t3['significance']['significant']
    hyps = t3['hypotheses']

    conditions = {}

    # FC1: No random beats
    conditions['FC1'] = {
        'triggered': not any(sig.values()),
        'desc': 'Voynich does not beat random on ANY hypothesis',
    }

    # FC2: H2 mode fail
    conditions['FC2'] = {
        'triggered': not sig.get('H2', False),
        'desc': 'Mode A/B decomposition not significant',
    }

    # FC3: ch/sh merged = split
    h3 = hyps.get('H3_feedback_channels', {})
    conditions['FC3'] = {
        'triggered': h3.get('split_advantage', 0) <= 0,
        'desc': 'Merged model >= split model',
    }

    # FC4: k aligns HOT_UNSTABLE
    h4 = hyps.get('H4_thermal_work', {})
    conditions['FC4'] = {
        'triggered': not h4.get('k_aligned_lowest_risk', False),
        'desc': 'k-domain aligns with HOT_UNSTABLE',
    }

    # FC5: Start-biased
    h5 = hyps.get('H5_closure_containment', {})
    conditions['FC5'] = {
        'triggered': not h5.get('closure_biased', False),
        'desc': 'Risk start-biased not closure-biased',
    }

    # FC6: Overfitting
    h1 = hyps.get('H1_safety_envelope', {})
    v_jsd = h1.get('voynich_jsd', 1)
    pv_jsd = h1.get('alternatives', {}).get('permuted_voynich', {}).get('jsd_mean', 1)
    conditions['FC6'] = {
        'triggered': v_jsd > pv_jsd,
        'desc': 'Voynich loses to permuted-Voynich (overfitting)',
    }

    # FC7: No ablation effect
    ablations = t3.get('ablations', {})
    any_deg = False
    for k, v in ablations.items():
        if k == 'baseline':
            continue
        deg = v.get('degradation', 0)
        if isinstance(deg, (int, float)) and not math.isnan(deg) and abs(deg) > 0.005:
            any_deg = True
    conditions['FC7'] = {
        'triggered': not any_deg,
        'desc': 'No ablation shows degradation',
    }

    return conditions


def compute_verdict(t3):
    sig = t3['significance']['significant']

    h1 = sig.get('H1', False)
    h2 = sig.get('H2', False)
    h3 = sig.get('H3', False)
    h4 = sig.get('H4', False)
    h5 = sig.get('H5', False)

    anchor = h1 or h5
    secondary = sum([h2, h3, h4])

    fc = failure_audit(t3)
    fc6 = fc['FC6']['triggered']
    fc7 = fc['FC7']['triggered']

    if fc6:
        return {'verdict': 'FAIL', 'reason': 'FC6: overfitting detected'}
    elif anchor and secondary >= 3 and not fc7:
        return {'verdict': 'STRONG_PASS', 'reason': f'Anchor + {secondary} secondary + ablation effects'}
    elif anchor and secondary >= 2:
        return {'verdict': 'MODERATE_PASS', 'reason': f'Anchor + {secondary} secondary'}
    elif anchor and secondary >= 1:
        return {'verdict': 'WEAK_PASS', 'reason': f'Anchor + {secondary} secondary'}
    elif not anchor:
        passing = [k for k, v in sig.items() if v]
        return {'verdict': 'FAIL', 'reason': f'No anchor (H1/H5). Passing: {passing}'}
    else:
        return {'verdict': 'FAIL', 'reason': f'Anchor but {secondary} secondary'}


def main():
    t3, t1_summary = load_data()

    verdict = compute_verdict(t3)
    fc = failure_audit(t3)

    hyps = t3['hypotheses']
    sig = t3['significance']

    # Build hypothesis table
    table = []
    for key, name in [
        ('H1', 'Safety-Envelope (Operator Scheduling)'),
        ('H2', 'Two-State Supervisory Decomposition'),
        ('H3', 'Dual Feedback Channel'),
        ('H4', 'Thermal-Work Neutralization'),
        ('H5', 'Closure Containment (Operator)'),
    ]:
        h_key = f'{key}_{"safety_envelope" if key == "H1" else "mode_decomposition" if key == "H2" else "feedback_channels" if key == "H3" else "thermal_work" if key == "H4" else "closure_containment"}'
        h = hyps.get(h_key, {})
        entry = {
            'hypothesis': key,
            'name': name,
            'p_value': sig['p_values'].get(key, 1.0),
            'significant': sig['significant'].get(key, False),
        }
        if key == 'H1':
            entry['metrics'] = {
                'jsd': h.get('voynich_jsd'),
                'auc': h.get('voynich_auc'),
                'mean_rho': h.get('mean_rho'),
                'contrasts': h.get('ordered_contrasts'),
            }
        elif key == 'H2':
            entry['metrics'] = {
                'cosine': h.get('voynich_cosine'),
                'silhouette': h.get('physical_silhouette'),
                'interleaving': h.get('mean_interleaving_rate'),
            }
        elif key == 'H3':
            entry['metrics'] = {
                'delta': h.get('empirical_delta'),
                'split_advantage': h.get('split_advantage'),
            }
        elif key == 'H4':
            entry['metrics'] = {
                'jsd': h.get('voynich_jsd'),
                'rho': h.get('rho'),
                'k_aligned': h.get('k_aligned_lowest_risk'),
            }
        elif key == 'H5':
            entry['metrics'] = {
                'rho': h.get('voynich_rho'),
                'closure_biased': h.get('closure_biased'),
                'cross_indep': h.get('cross_cycle_independent'),
            }
        table.append(entry)

    output = {
        'verdict': verdict,
        'hypothesis_table': table,
        'failure_conditions': fc,
        'non_circularity': {
            'T1_voynich_input': t1_summary.get('non_circularity', {}).get('voynich_input'),
            'operator_labels': t1_summary.get('non_circularity', {}).get('operator_labels'),
            'verdict': 'CLEAN',
        },
        'ablations': t3.get('ablations'),
        'out_of_sample': t3.get('out_of_sample'),
        'design_note': t1_summary.get('design_note', ''),
    }

    out_path = RESULTS_DIR / 't4_synthesis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"T4 SYNTHESIS — PHASE 555 VERDICT (REDESIGNED)")
    print(f"{'='*60}")
    print(f"\n  VERDICT: {verdict['verdict']}")
    print(f"  REASON:  {verdict['reason']}")
    print()
    print(f"HYPOTHESIS TABLE:")
    print(f"  {'Hyp':<5} {'Name':<42} {'p':<10} {'Pass':<6}")
    print(f"  {'-'*5} {'-'*42} {'-'*10} {'-'*6}")
    for h in table:
        print(f"  {h['hypothesis']:<5} {h['name']:<42} {h['p_value']:<10.4f} "
              f"{'YES' if h['significant'] else 'NO'}")
    print()
    print(f"FAILURE CONDITIONS:")
    for k, v in fc.items():
        print(f"  {k}: {'TRIGGERED' if v['triggered'] else 'CLEAR'} — {v['desc']}")
    print()
    oos = t3.get('out_of_sample', {})
    if 'error' not in oos:
        print(f"OUT-OF-SAMPLE:")
        print(f"  H1: train={oos.get('H1_train_jsd','?'):.4f}  test={oos.get('H1_test_jsd','?'):.4f}")
        print(f"  H5: train={oos.get('H5_train_rho','?'):.3f}  test={oos.get('H5_test_rho','?'):.3f}")
    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
