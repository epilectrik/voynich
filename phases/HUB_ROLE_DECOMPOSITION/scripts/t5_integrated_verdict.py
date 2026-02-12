"""
T5: Integrated Verdict
=======================
Phase: HUB_ROLE_DECOMPOSITION

Loads results from T1-T4, synthesizes into a verdict on HUB decomposability
and PREFIX interaction strength.

Verdict categories:
  HUB_DECOMPOSABLE   - 3+ dimensions show significant sub-structure
  PREFIX_IS_THE_KEY   - PREFIX differentiation is the strongest signal
  FREQUENCY_ARTIFACT  - HUB dominance is frequency-driven, no decomposition
  PARTIAL_STRUCTURE   - Some sub-structure exists but not clean decomposition

Output: t5_integrated_verdict.json
"""

import json
import functools
from pathlib import Path

print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def main():
    # ── Load all results ───────────────────────────────────
    with open(RESULTS_DIR / 't1_hub_sub_role_partition.json') as f:
        t1 = json.load(f)
    with open(RESULTS_DIR / 't2_prefix_bin_interaction.json') as f:
        t2 = json.load(f)
    with open(RESULTS_DIR / 't3_cross_bin_forbidden_anatomy.json') as f:
        t3 = json.load(f)
    with open(RESULTS_DIR / 't4_hub_compound_position_analysis.json') as f:
        t4 = json.load(f)

    # ── Score each dimension ───────────────────────────────
    scores = {}

    # Dimension 1: Sub-role decomposability (T1)
    t1_sig = t1['significant_dimensions']
    t1_total = len(t1['behavioral_comparison'])
    t1_verdict = t1['verdict']
    d1_score = min(1.0, t1_sig / 3.0)  # Normalized: 3 sig dims = 1.0
    scores['sub_role_decomposability'] = {
        'score': d1_score,
        'evidence': (f"{t1_sig}/{t1_total} dimensions significant "
                     f"(T1 verdict: {t1_verdict})"),
        'verdict': t1_verdict,
    }

    # Dimension 2: PREFIX differentiation (T2)
    t2_verdict = t2['verdict']
    t2a = t2['test_2a_prefix_lane']
    t2b = t2['test_2b_safety_buffer_prefix']
    t2c = t2['test_2c_mutual_information']
    prefix_signals = 0
    if t2a['p'] < 0.001:
        prefix_signals += 1
    if t2b['fishers_p'] < 0.05:
        prefix_signals += 1
    if t2c['MI_gain_pct'] > 10:
        prefix_signals += 1
    d2_score = min(1.0, prefix_signals / 3.0)
    scores['prefix_differentiation'] = {
        'score': d2_score,
        'evidence': (f"Lane chi2 p={t2a['p']:.2e}, "
                     f"Buffer Fisher p={t2b['fishers_p']:.4f}, "
                     f"MI gain={t2c['MI_gain_pct']:.1f}% "
                     f"(T2 verdict: {t2_verdict})"),
        'verdict': t2_verdict,
    }

    # Dimension 3: Forbidden concentration (T3)
    t3_perm = t3['permutation_test']
    t3_conc = t3['concentration_verdict']
    d3_score = 1.0 if t3_perm['p_value'] < 0.001 else (
        0.5 if t3_perm['p_value'] < 0.05 else 0.0)
    scores['forbidden_concentration'] = {
        'score': d3_score,
        'evidence': (f"Permutation p={t3_perm['p_value']:.4f}, "
                     f"observed={t3_perm['observed_hub_transitions']}/17 "
                     f"(verdict: {t3_conc})"),
        'verdict': t3_conc,
    }

    # Dimension 4: Internal structure (T4)
    t4_verdict = t4['verdict']
    t4_comp_sig = t4['compound_analysis']['significant_dimensions']
    t4_pos_p = t4['position_analysis']['position_p']
    t4_regime_sil = t4['regime_clustering']['best_silhouette']
    internal_signals = 0
    if t4_comp_sig >= 2:
        internal_signals += 1
    if t4_pos_p < 0.05:
        internal_signals += 1
    if t4_regime_sil > 0.25:
        internal_signals += 1
    d4_score = min(1.0, internal_signals / 2.0)
    scores['internal_structure'] = {
        'score': d4_score,
        'evidence': (f"Compound sig dims={t4_comp_sig}, "
                     f"Position p={t4_pos_p:.4f}, "
                     f"Regime sil={t4_regime_sil:.3f} "
                     f"(T4 verdict: {t4_verdict})"),
        'verdict': t4_verdict,
    }

    # ── Overall verdict ────────────────────────────────────
    total_score = sum(s['score'] for s in scores.values())
    high_dims = sum(1 for s in scores.values() if s['score'] >= 0.5)

    # Check which dimension is strongest
    max_dim = max(scores.items(), key=lambda x: x[1]['score'])

    if high_dims >= 3 and total_score >= 2.5:
        verdict = 'HUB_DECOMPOSABLE'
        detail = (f'{high_dims}/4 dimensions show significant sub-structure '
                  f'(total score {total_score:.1f}/4.0). HUB should be split '
                  f'in future analysis.')
    elif max_dim[0] == 'prefix_differentiation' and max_dim[1]['score'] >= 0.67:
        verdict = 'PREFIX_IS_THE_KEY'
        detail = ('PREFIX differentiation is the strongest signal. HUB MIDDLEs '
                  'are behaviorally homogeneous but PREFIX creates functional '
                  'sub-roles within the bin.')
    elif high_dims == 0 and total_score < 1.0:
        verdict = 'FREQUENCY_ARTIFACT'
        detail = ('HUB dominance is explained by frequency and compatibility, '
                  'not functional diversity. No decomposition is warranted.')
    else:
        verdict = 'PARTIAL_STRUCTURE'
        detail = (f'{high_dims}/4 dimensions show partial sub-structure '
                  f'(total score {total_score:.1f}/4.0). Sub-roles exist '
                  f'but boundaries are not clean enough for decomposition.')

    # ── Print ──────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"T5 HUB ROLE DECOMPOSITION VERDICT")
    print(f"{'='*70}")
    print(f"\nVERDICT: {verdict}")
    print(f"  {detail}")
    print(f"\nDIMENSION SCORES:")
    for dim, data in scores.items():
        bar = '#' * int(data['score'] * 10) + '.' * (10 - int(data['score'] * 10))
        print(f"  {dim:<28s}: [{bar}] {data['score']:.2f}")
        print(f"    {data['evidence']}")

    # Sub-role summary from T1
    print(f"\nHUB SUB-ROLE SUMMARY:")
    for role, members in t1.get('role_groups', {}).items():
        print(f"  {role:<16s}: {members}")

    # Key numbers
    print(f"\nKEY METRICS:")
    print(f"  T1 sig dimensions:  {t1_sig}/{t1_total}")
    print(f"  T2 lane chi2 p:     {t2a['p']:.2e}")
    print(f"  T2 buffer Fisher p: {t2b['fishers_p']:.4f}")
    print(f"  T2 MI gain:         {t2c['MI_gain_pct']:.1f}%")
    print(f"  T3 perm p:          {t3_perm['p_value']:.4f}")
    print(f"  T4 position p:      {t4_pos_p:.4f}")
    print(f"  T4 regime sil:      {t4_regime_sil:.3f}")

    # ── Output ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'HUB_ROLE_DECOMPOSITION',
            'test': 'T5_INTEGRATED_VERDICT',
        },
        'dimension_scores': scores,
        'total_score': total_score,
        'high_dimensions': high_dims,
        'verdict': verdict,
        'verdict_detail': detail,
        'sub_role_groups': t1.get('role_groups', {}),
    }

    out_path = RESULTS_DIR / 't5_integrated_verdict.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
