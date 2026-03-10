"""Phase 560 T4: Synthesis

Combines T2 + T3 results into phase verdict with domain execution dial cards.

Input: t2_within_domain_validation.json, t3_cross_folio_discriminability.json
Output: t4_synthesis.json
"""
import json
import sys
import time
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def main():
    t0 = time.time()
    print("=== Phase 560 T4: Synthesis ===")

    # Load results
    with open(RESULTS_DIR / 't2_within_domain_validation.json') as f:
        t2 = json.load(f)
    with open(RESULTS_DIR / 't3_cross_folio_discriminability.json') as f:
        t3 = json.load(f)

    # ═══════════════════════════════════════════════════════════
    # T2 summary
    # ═══════════════════════════════════════════════════════════
    t2a_pass = t2['verdict']['t2a_pass']
    t2a_failures = t2['verdict']['t2a_failures']
    t2b_pass_ct = t2['verdict']['t2b_pass_count']
    t2b_total = t2['verdict']['t2b_total']
    t2_pass = t2['verdict']['pass']

    print(f"  T2: {'PASS' if t2_pass else 'FAIL'}")
    print(f"    T2A: {17 - t2a_failures}/17 (spine)")
    print(f"    T2B: {t2b_pass_ct}/{t2b_total} (profile)")

    # ═══════════════════════════════════════════════════════════
    # T3 summary
    # ═══════════════════════════════════════════════════════════
    d1 = t3['verdict']['D1']
    d2 = t3['verdict']['D2']
    d3 = t3['verdict']['D3']
    d4 = t3['verdict']['D4']
    d5 = t3['verdict']['D5']
    d6a = t3['verdict']['D6a']
    d6b = t3['verdict']['D6b']
    t3_pass = t3['verdict']['t3_pass']

    # T3 detailed classification
    secondary_pass = sum([d2, d3, d4])
    if d1 and d5 and secondary_pass >= 2:
        t3_class = 'PASS'
    elif d1 and d5:
        t3_class = 'PARTIAL'  # D1+D5 pass but secondary insufficient
    elif d1:
        t3_class = 'WEAK'
    else:
        t3_class = 'FAIL'

    print(f"  T3: {t3_class}")
    print(f"    D1={d1}, D2={d2}, D3={d3}, D4={d4}, D5={d5}")
    print(f"    D6a={d6a}, D6b={d6b}")

    # ═══════════════════════════════════════════════════════════
    # Overall verdict
    # ═══════════════════════════════════════════════════════════
    if not t2_pass:
        verdict = 'FAIL'
        verdict_detail = 'Within-domain constraint predictions not confirmed (T2A failed)'
    elif t3_class == 'PASS' and d6a:
        verdict = 'FULL_PASS'
        verdict_detail = ('Hierarchical model validated. Within-domain folio+paragraph '
                         'specificity confirmed. Phase 561 must be paragraph-aware.')
    elif t3_class == 'PASS':
        verdict = 'PASS'
        verdict_detail = ('Hierarchical model validated. Within-domain folio specificity '
                         'confirmed. Phase 561 uses folio-averaged profiles.')
    elif t3_class == 'PARTIAL':
        if d6a:
            verdict = 'PARTIAL_PASS'
            verdict_detail = ('Hierarchical model validated. D5 confirms within-domain features '
                             'add discriminative power (+6-9pp). D6a shows paragraph differentiation. '
                             'But secondary cross-folio tests (D3, D4) indicate within-domain '
                             'variation is primarily between-section, not between-folio within-section.')
        else:
            verdict = 'PARTIAL_PASS'
            verdict_detail = ('Hierarchical model validated. D5 confirms within-domain features '
                             'add discriminative power (+6-9pp). But secondary cross-folio tests '
                             '(D3, D4) indicate within-domain variation is primarily between-section. '
                             'Paragraph differentiation at 28.8% (threshold 30%) — very close.')
    elif t3_class == 'WEAK':
        verdict = 'STRUCTURE_ONLY'
        verdict_detail = 'Within-domain structure validated but not folio-specific.'
    else:
        verdict = 'FAIL'
        verdict_detail = 'Within-domain structure validated (T2) but discriminability failed (T3).'

    print(f"\n  PHASE VERDICT: {verdict}")
    print(f"  {verdict_detail}")

    # ═══════════════════════════════════════════════════════════
    # D5 feature importance (from RF)
    # ═══════════════════════════════════════════════════════════
    d5b = t3['D5']['D5b']
    top_features = d5b.get('top_features', [])
    if top_features:
        print(f"\n  Top discriminative features (RF importance):")
        for name, imp in top_features[:10]:
            print(f"    {name}: {imp:.4f}")

    # ═══════════════════════════════════════════════════════════
    # Constraint implications
    # ═══════════════════════════════════════════════════════════
    constraints_proposed = []
    constraints_referenced = [
        'C1003', 'C1475', 'C1429', 'C1431', 'C1432', 'C1433',
        'C1446', 'C1448', 'C1457', 'C1461', 'C1476', 'C1477',
        'C1478', 'C1479', 'C1480', 'C1481', 'C1482', 'C1486',
        'C1487', 'C1488', 'C1489', 'C1492', 'C1494', 'C1497',
        'C1510', 'C1536', 'C1537', 'C1538', 'C1546', 'C1556',
        'C1557', 'C1558', 'C1561', 'C1563', 'C1564', 'C1566',
    ]

    if verdict in ('PASS', 'FULL_PASS', 'PARTIAL_PASS'):
        constraints_proposed.append({
            'id': 'C1567',
            'tier': 2,
            'text': ('Within-domain subordinate features validate constraint predictions '
                    'per domain: 16/17 structural spine tests pass (T2A). The single failure '
                    '(O3: bare-o OPERATION purity 42.6% vs 95%) reflects a '
                    'CategoryClassifier/C1556 tension, not a decomposition error.'),
        })
        constraints_proposed.append({
            'id': 'C1568',
            'tier': 2,
            'text': ('Cross-folio within-domain profiles add discriminative power beyond '
                    f'HEAD distribution alone: +{t3["D5"]["D5a"]["gain_pp"]:.1%} (NN), '
                    f'+{d5b.get("gain", 0):.1%} (RF) accuracy gain. Top features: '
                    'o_l_frac, xd_headless_frac, hl_frac, t_flow_purity, e_ey_frac.'),
        })
        constraints_proposed.append({
            'id': 'C1569',
            'tier': 2,
            'text': ('Folio specificity extends into within-domain parameterization at '
                    'section level (D1: 76.8% section classification from within-domain '
                    'features alone, D2: 15/32 features with significant section variance). '
                    'Within-section folio resolution is not established (D3, D4 fail).'),
        })

    if verdict == 'FULL_PASS' or d6a:
        constraints_proposed.append({
            'id': 'C1570',
            'tier': 2,
            'text': ('Paragraph subroutines within folios show differentiated within-domain '
                    f'tuning: {t3["D6"]["D6a"]["n_significant"]}/{t3["D6"]["D6a"]["n_qualifying"]} '
                    'qualifying folios show significant paragraph differentiation.'),
        })

    # ═══════════════════════════════════════════════════════════
    # Domain execution dial cards
    # ═══════════════════════════════════════════════════════════
    dial_cards = {
        'THERMAL': {
            'actuation': 'Thermal raise/hold',
            'safety': 'Intrinsically immune (K1: 0% hazard all frames)',
            'routing_inputs': 'y->k incoming (X2: 1.72x), qo PREFIX activation (K5: 4.66x)',
            'packaging': f'Bare-terminal {t2["t2b"]["tests"]["K2"]["value"]:.0%}, '
                        f'suffix rate {t2["t2b"]["tests"]["K4"]["value"]:.0%}',
            'folio_dials': 'k_suffix_entropy, k_bare_term_frac, k_thermal_purity',
            'category_purity': f'{t2["t2a"]["tests"]["K6"]["purity"]:.1%}',
        },
        'FLOW': {
            'actuation': 'Flow transition/routing',
            'safety': f'Modifier gate (T3: with-mod={t2["t2b"]["tests"]["T3"]["haz_with_mod"]}, '
                      f'without={t2["t2b"]["tests"]["T3"]["haz_without_mod"]})',
            'mirror': f'Terminal mirrors THERMAL (T1 JSD={t2["t2b"]["tests"]["T1"]["jsd"]:.4f}), '
                      f'category opposes (T2 JSD={t2["t2b"]["tests"]["T2"]["jsd"]:.4f})',
            'folio_dials': 't_mod_rate, t_flow_purity',
            'category_purity': f'{t2["t2b"]["tests"]["T5"]["value"]:.1%}',
        },
        'ACTIVE': {
            'actuation': 'Active transformation, risk-carrying iteration',
            'safety': f'i-modifier + terminal transformation: '
                      f'i-rate={t2["t2b"]["tests"]["A1"]["value"]:.1%}, '
                      f'double-ii safe (A5: {t2["t2a"]["tests"]["A5"]["safe_rate"]:.0%})',
            'hazard': f'Highest headed domain (A9). '
                      f'a->l: {t2["t2a"]["tests"]["A7"]["hazard_rate"]:.0%}, '
                      f'a->r: {t2["t2a"]["tests"]["A8"]["hazard_rate"]:.0%}, '
                      f'a->bare: {t2["t2b"]["tests"]["A6"]["hazard"]:.0%}',
            'controls': 'i-count -> terminal -> category mediation chain',
            'folio_dials': 'a_i_rate, a_ii_rate, a_n_term_rate, a_hazard_rate',
        },
        'STABILITY': {
            'actuation': 'Stabilization, preventive anchoring',
            'safety': f'e->y ambient safe substrate '
                      f'(E1: {t2["t2b"]["tests"]["E1"]["value"]:.1%} of e-HEAD, '
                      f'E2: {t2["t2a"]["tests"]["E2"]["hazard_rate"]:.0%} hazard)',
            'vocabulary': f'e->y uses {t2["t2b"]["tests"]["E3"]["count"]} unique MIDDLEs',
            'modifiers': f'd-mod enrichment: {t2["t2b"]["tests"]["E4"]["value"]:.1%}',
            'saturation': f'ee->THERMAL: {t2["t2b"]["tests"]["E5"]["value"]:.1%}',
            'folio_dials': 'e_ey_frac, e_d_mod_rate, e_ey_vocab, e_ey_zone_bias, e_edy_dominance',
        },
        'ARRANGEMENT': {
            'actuation': 'Configuration dispatch',
            'dispatch': f'o->l=STAGING ({t2["t2a"]["tests"]["O1"]["purity"]:.1%}), '
                        f'o->r=FLOW ({t2["t2a"]["tests"]["O2"]["purity"]:.1%})',
            'safety': f'Source immune, no hazard class assigned (O6: effective 0%)',
            'exclusion': f'y-terminal excluded ({t2["t2a"]["tests"]["O4"]["y_frac"]:.2%})',
            'tension': 'O3: bare-o OPERATION purity only 42.6% (CategoryClassifier tension)',
            'folio_dials': 'o_l_frac, o_r_frac, o_exec_mod_rate',
        },
        'HEADLESS': {
            'actuation': 'Infrastructure, containment, marking',
            'subtypes': f'PSEUDO_HEAD_CORE (d/i/l), PARAMETRIC (c/p/f), OTHER',
            'pseudo_head': f'Cramer V={t2["t2b"]["tests"]["H2"]["cramers_v"]:.3f}',
            'suffix_bifurcation': f'd/i sfx={t2["t2b"]["tests"]["HL6"]["di_suffix_rate"]:.1%}, '
                                  f'c/p/f sfx={t2["t2b"]["tests"]["HL6"]["cpf_suffix_rate"]:.1%}',
            'displaced': f'{t2["t2b"]["tests"]["HL7"]["count"]} tokens with displaced head terminal',
            'folio_dials': 'hl_pseudo_entropy, hl_mod_rate, hl_core_ratio, hl_suffix_bifurc',
        },
    }

    # ═══════════════════════════════════════════════════════════
    # Routing summary
    # ═══════════════════════════════════════════════════════════
    routing = {
        'within_line': {
            'r->a': t2['t2a']['tests']['X1']['enrichment'],
            'y->k': t2['t2a']['tests']['X2']['enrichment'],
            'h->t': t2['t2a']['tests']['X3']['enrichment'],
            'm->o': t2['t2a']['tests']['X4']['enrichment'],
        },
        'Q3_Q4_jump': t2['t2a']['tests']['X6']['ratio'],
        'suffix_forward_info': t2['t2b']['tests']['X5']['jsd'],
        'cross_line_collapse': t2['t2b']['tests']['X7']['ratio'],
        'cross_line_hazard_memory': t2['t2b']['tests']['X9']['ratio'],
    }

    # ═══════════════════════════════════════════════════════════
    # Assemble output
    # ═══════════════════════════════════════════════════════════
    output = {
        'metadata': {
            'phase': '560',
            'task': 'T4_synthesis',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        },
        'phase_verdict': verdict,
        'verdict_detail': verdict_detail,
        'summary': {
            'T2': {
                'pass': t2_pass,
                'T2A': f'{17 - t2a_failures}/17',
                'T2A_only_failure': 'O3 (bare-o OPERATION purity)',
                'T2B': f'{t2b_pass_ct}/{t2b_total}',
            },
            'T3': {
                'class': t3_class,
                'D1': {'pass': d1, 'accuracy': t3['D1']['accuracy']},
                'D2': {'pass': d2, 'n_significant': t3['D2']['n_significant']},
                'D3': {'pass': d3},
                'D4': {'pass': d4, 'ari': t3['D4']['ari']},
                'D5': {
                    'pass': d5,
                    'D5a_gain': t3['D5']['D5a']['gain_pp'],
                    'D5b_gain': d5b.get('gain', None),
                },
                'D6a': {'pass': d6a,
                        'fraction': t3['D6']['D6a']['fraction']},
                'D6b': {'pass': d6b},
            },
        },
        'constraints_proposed': constraints_proposed,
        'constraints_referenced': constraints_referenced,
        'domain_dial_cards': dial_cards,
        'routing_summary': routing,
        'interpretation': {
            'what_passed': (
                'T2A confirms the within-domain structural spine: 16/17 invariants hold. '
                'Domain decomposition is correct. D5 proves within-domain features carry '
                'folio-discriminative information beyond HEAD proportions (+6-9pp). '
                'D1 shows 76.8% section classification from within-domain features alone.'
            ),
            'what_failed': (
                'D3/D4: Within-section folio resolution absent. Folios within the same section '
                'have nearly identical within-domain profiles after domain-count adjustment. '
                'The discriminative power is section-level, not folio-level. '
                'D6a: Paragraph differentiation at 28.8%, just below 30% threshold.'
            ),
            'what_this_means': (
                'HEAD selects domain (confirmed). Within-domain features are real control dials '
                'that vary systematically across sections (confirmed). But the folio-to-folio '
                'variation WITHIN sections is indistinguishable from shuffled tokens within '
                'domains. This means either: (a) folio-level specificity lives in domain MIX '
                'not within-domain tuning, (b) within-domain variation exists but is too subtle '
                'for 32-feature profiles to capture, or (c) folios within sections really do '
                'share the same within-domain control settings.'
            ),
            'phase_561_guidance': (
                'Phase 561 can use: (1) domain dial cards as validated section-level control '
                'parameters, (2) HEAD proportions for folio-level specificity, (3) within-domain '
                'features for section-discriminative behavior. Paragraph-level emphasis differences '
                '(D6a at 28.8%, D6b shows gradient alignment) should be explored but not assumed. '
                'The simulator should be hierarchical: section -> folio (HEAD mix) -> domain dials.'
            ),
        },
        'non_circularity': {
            'HEAD_domain_assignment': 'DIRECT (structural partition, unavoidable)',
            'constraint_predictions': 'NONE (testing published predictions)',
            'CategoryClassifier': 'INDIRECT (MIDDLE property, independent of HEAD)',
            'headless_subtyping': 'DIRECT (first atom of MIDDLE, unavoidable)',
            'permutation_nulls': 'NONE (random shuffling)',
            'section_labels': 'NONE (illustration-based, external to text)',
            'folio_features': 'DIRECT (computed from token decomposition, unavoidable)',
            'random_forest': 'NONE (sklearn, no Voynich tuning)',
        },
    }

    out_path = RESULTS_DIR / 't4_synthesis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    elapsed = time.time() - t0
    print(f"\n  Output: {out_path}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== T4 Complete: {verdict} ===")


if __name__ == '__main__':
    main()
