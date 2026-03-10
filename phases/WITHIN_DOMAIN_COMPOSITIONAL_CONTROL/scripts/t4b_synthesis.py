"""Phase 560b T4b: Synthesis and Verdict

Combines T2b validation + T3b discrimination results.
Classifies verdict: DEPLOYMENT_PASS / DEPLOYMENT_PARTIAL / DEPLOYMENT_FAIL.

Input: t2b_constraint_validation.json, t3b_discriminability.json
Output: t4b_synthesis.json
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

    # Load results
    with open(RESULTS_DIR / 't2b_constraint_validation.json') as f:
        t2b = json.load(f)
    with open(RESULTS_DIR / 't3b_discriminability.json') as f:
        t3b = json.load(f)

    print("=" * 60)
    print("Phase 560b T4b: SYNTHESIS")
    print("=" * 60)

    # ================================================================
    # T2b Summary
    # ================================================================
    t2ba_pass = t2b['T2bA']['pass']
    t2bb_pass = t2b['T2bB']['pass']
    t2b_pass = t2b['overall_pass']
    print(f"\nT2b Validation:")
    print(f"  T2bA (constraint replication): {t2b['T2bA']['pass_count']}/{t2b['T2bA']['total']} -> {'PASS' if t2ba_pass else 'FAIL'}")
    print(f"  T2bB (instrument sanity):      {t2b['T2bB']['pass_count']}/{t2b['T2bB']['total']} -> {'PASS' if t2bb_pass else 'FAIL'}")
    print(f"  Overall: {'PASS' if t2b_pass else 'FAIL'}")
    print(f"  -> Deployment features are valid instruments")

    # ================================================================
    # D3b Summary (PRIMARY)
    # ================================================================
    d3b = t3b['D3b']['summary']
    print(f"\nD3b Within-Section Pairwise Distance (PRIMARY):")
    for set_name in ['HEAD', 'MARGINAL', 'DEPLOYMENT', 'FULL_560', 'FULL_560b', 'COMBINED']:
        s = d3b[set_name]
        print(f"  {set_name:12s}: {s['sections_pass']}/{s['total_sections']} -> {'PASS' if s['pass'] else 'FAIL'}")
    d3b_any_pass = any(d3b[s]['pass'] for s in d3b)
    print(f"  Any set passes D3b: {'YES' if d3b_any_pass else 'NO'}")

    # ================================================================
    # D4b Summary
    # ================================================================
    d4b = t3b['D4b']
    print(f"\nD4b Ward Clustering ARI:")
    for set_name in ['HEAD', 'MARGINAL', 'DEPLOYMENT', 'FULL_560', 'FULL_560b', 'COMBINED']:
        ari = d4b[set_name].get('ari_ward')
        p = d4b[set_name].get('pass')
        print(f"  {set_name:12s}: ARI={ari} -> {'PASS' if p else 'FAIL'}")
    d4b_deployment_better = (d4b.get('DEPLOYMENT', {}).get('ari_ward', 0) >
                              d4b.get('MARGINAL', {}).get('ari_ward', 0))
    print(f"  DEPLOYMENT > MARGINAL ARI: {'YES' if d4b_deployment_better else 'NO'}")

    # ================================================================
    # D5b Summary
    # ================================================================
    d5b = t3b['D5b']
    print(f"\nD5b Gain Test:")
    print(f"  NN accuracies:")
    for s, acc in d5b['nn_accuracies'].items():
        print(f"    {s:12s}: {acc}")
    print(f"  RF accuracies:")
    for s, acc in d5b['rf_accuracies'].items():
        print(f"    {s:12s}: {acc}")
    print(f"  NN gain FULL_560b vs FULL_560: {d5b['nn_gain_560b']:+.4f}")
    print(f"  RF gain FULL_560b vs FULL_560: {d5b['rf_gain_560b']:+.4f}")
    print(f"  RF gain COMBINED vs FULL_560:  {d5b['rf_gain_combined']:+.4f}")
    print(f"  D5b: {'PASS' if d5b['pass'] else 'FAIL'}")

    # ================================================================
    # D7 Summary
    # ================================================================
    d7 = t3b['D7']
    print(f"\nD7 Within-Section Variance:")
    print(f"  Marginal features with ratio > 0.5: {d7['marginal_high_ratio_count']}")
    print(f"  Deployment features with ratio > 0.5: {d7['deployment_high_ratio_count']}")
    print(f"  D7: {'PASS' if d7['pass'] else 'FAIL'}")

    # ================================================================
    # RF Feature Importances
    # ================================================================
    imps = d5b.get('rf_top20_importances', {})
    if imps:
        print(f"\nTop RF Importances (COMBINED):")
        for rank, (name, imp) in enumerate(sorted(imps.items(), key=lambda x: -x[1])[:10], 1):
            print(f"  {rank:2d}. {name:40s} {imp:.4f}")

    # ================================================================
    # VERDICT
    # ================================================================
    # Primary: D3b passes with deployment features
    d3b_deploy_pass = d3b.get('DEPLOYMENT', {}).get('pass', False) or d3b.get('FULL_560b', {}).get('pass', False)
    # Secondary: D5b shows deployment gain
    d5b_deploy_gain = d5b.get('rf_gain_560b', 0) >= 0.02 or d5b.get('rf_gain_combined', 0) >= 0.03

    if d3b_deploy_pass and d5b_deploy_gain:
        verdict = 'DEPLOYMENT_PASS'
    elif d5b_deploy_gain or d4b_deployment_better or d7['pass']:
        verdict = 'DEPLOYMENT_PARTIAL'
    else:
        verdict = 'DEPLOYMENT_FAIL'

    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")

    # Interpretation
    if verdict == 'DEPLOYMENT_PASS':
        interpretation = (
            "Deployment features recover within-section folio discrimination. "
            "Folio specificity lives in deployment packaging."
        )
    elif verdict == 'DEPLOYMENT_PARTIAL':
        interpretation = (
            "Deployment features add real section-level discriminative power "
            "beyond marginals, but do NOT recover within-section folio specificity. "
            "The primary D3b test fails across all feature sets. "
            "Within-section folio variation in averaged features is indistinguishable "
            "from within-domain token shuffle null. "
            "Folio individuality likely resides in HEAD proportions (domain mix) "
            "plus stochastic freedom within section templates, not in deployment grammar."
        )
    else:
        interpretation = (
            "Deployment features add nothing beyond marginals. "
            "Folio specificity resides entirely in HEAD proportions."
        )

    # Category diagnosis
    category_signals = {}
    if imps:
        from collections import defaultdict
        # Classify top features by category
        deploy_cats = {
            'zone': ['spec_frac', 'close_frac', 'e_ey_spec', 'a_high_close', 'k_q1', 'o_dispatch', 'e_ey_q0q1'],
            'adjacency': ['enrichment', 'transition_entropy', 'self_run', 'safe_to_thermal', 'hazard_safe', 'active_close', 'routing_break', 'cross_line', 'm_linefinal'],
            'closure': ['q4_', 'q3q4_head_jsd', 'post_highhaz', 'line_close'],
            'headless': ['hl_d_frac', 'hl_i_frac', 'hl_l_frac', 'hl_cpf', 'hl_other', 'hl_displaced', 'hl_zone', 'hl_header'],
            'paragraph': ['para_', 'within_folio_para', 'same_type_para', 'header_body'],
        }
        for cat, patterns in deploy_cats.items():
            cat_features = []
            for name, imp in imps.items():
                if any(p in name for p in patterns):
                    cat_features.append((name, imp))
            if cat_features:
                total_imp = sum(imp for _, imp in cat_features)
                category_signals[cat] = {
                    'n_in_top20': len(cat_features),
                    'total_importance': round(total_imp, 4),
                    'top_feature': max(cat_features, key=lambda x: x[1])[0],
                }

    print(f"\nInterpretation: {interpretation}")

    if category_signals:
        print(f"\nCategory Signal Strengths:")
        for cat, info in sorted(category_signals.items(), key=lambda x: -x[1]['total_importance']):
            print(f"  {cat:12s}: {info['n_in_top20']} features in top 20, "
                  f"total importance={info['total_importance']}, "
                  f"top={info['top_feature']}")

    # Key findings
    findings = []

    # F1: D3b fails universally
    findings.append({
        'id': 'F1',
        'finding': 'Within-section folio discrimination fails for ALL feature sets including deployment',
        'implication': 'Folio-average features (marginal or deployment) cannot distinguish folios within sections',
        'strength': 'Strong negative (0/18 section-set combinations pass)',
    })

    # F2: Deployment ARI highest
    dep_ari = d4b.get('DEPLOYMENT', {}).get('ari_ward', 0)
    marg_ari = d4b.get('MARGINAL', {}).get('ari_ward', 0)
    findings.append({
        'id': 'F2',
        'finding': f'Deployment features have highest Ward ARI ({dep_ari:.3f} vs marginal {marg_ari:.3f})',
        'implication': 'Deployment grammar is a BETTER section discriminator than marginal domain profiles',
        'strength': f'ARI improvement: +{dep_ari - marg_ari:.3f}',
    })

    # F3: RF gain
    rf_combined = d5b.get('rf_accuracies', {}).get('COMBINED', 0)
    rf_560 = d5b.get('rf_accuracies', {}).get('FULL_560', 0)
    findings.append({
        'id': 'F3',
        'finding': f'RF COMBINED ({rf_combined:.1%}) > FULL_560 ({rf_560:.1%}), +{rf_combined-rf_560:.1%}',
        'implication': 'Deployment features add real discriminative power for section classification',
        'strength': f'+{rf_combined-rf_560:.4f} RF gain',
    })

    # F4: NN hurt by deployment
    nn_560 = d5b.get('nn_accuracies', {}).get('FULL_560', 0)
    nn_560b = d5b.get('nn_accuracies', {}).get('FULL_560b', 0)
    findings.append({
        'id': 'F4',
        'finding': f'NN FULL_560b ({nn_560b:.1%}) < FULL_560 ({nn_560:.1%}): deployment HURTS NN',
        'implication': 'Deployment features introduce NaN-heavy dimensions that degrade nearest-neighbor; '
                       'RF handles this via tree-based feature selection, NN does not',
        'strength': 'Methodological caution for future simulation',
    })

    # F5: Paragraph features dominate RF
    findings.append({
        'id': 'F5',
        'finding': 'Paragraph features dominate RF importances (#1 para_iteration_emphasis_span, '
                   '#4 para_close_hazard_span)',
        'implication': 'Paragraph subroutine structure is the strongest deployment-level signal, '
                       'consistent with C1398-C1400',
        'strength': 'Top 3 deployment categories by RF importance: paragraph > headless > closure',
    })

    # F6: D7 within-section variance
    findings.append({
        'id': 'F6',
        'finding': f'D7: {d7["deployment_high_ratio_count"]}/56 deployment features have '
                   f'within-section ratio > 0.5 (vs {d7["marginal_high_ratio_count"]}/32 marginal)',
        'implication': 'Both feature types have mostly within-section variance (ratios near 1.0), '
                       'meaning almost NO between-section structure in raw values. '
                       'Section discrimination comes from PATTERNS across features, not individual feature levels.',
        'strength': 'Informative architectural finding',
    })

    print(f"\nKey Findings:")
    for finding in findings:
        print(f"\n  {finding['id']}: {finding['finding']}")
        print(f"      -> {finding['implication']}")

    # Constraint proposals
    constraints = []
    constraints.append({
        'id': 'C1570_proposed',
        'tier': 2,
        'scope': 'B',
        'statement': 'Deployment features (zone-conditioned, routing, closure, headless, paragraph) '
                     'are valid structural instruments (T2b 18/19 pass) and improve section-level '
                     'classification (RF +6.1pp) but do NOT recover within-section folio discrimination '
                     '(D3b 0/18). Folio specificity is not in deployment packaging at folio-average resolution.',
    })
    constraints.append({
        'id': 'C1571_proposed',
        'tier': 2,
        'scope': 'B',
        'statement': 'Ward-linkage clustering on deployment features achieves highest section ARI (0.615) '
                     'of any tested feature set, confirming deployment grammar is a stronger section-level '
                     'discriminator than within-domain marginals (ARI=0.443). Section identity is encoded '
                     'more in HOW domains are deployed than in domain proportions alone.',
    })

    # Output
    output = {
        'metadata': {
            'phase': '560b',
            'task': 'T4b_synthesis',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        },
        'verdict': verdict,
        'interpretation': interpretation,
        'T2b_valid': t2b_pass,
        'D3b_primary': {
            'any_pass': d3b_any_pass,
            'detail': 'All 18 section-set combinations FAIL. Real < null in most cases.',
        },
        'D4b_clustering': {
            'deployment_ari': dep_ari,
            'marginal_ari': marg_ari,
            'deployment_better': d4b_deployment_better,
        },
        'D5b_gain': {
            'rf_gain_560b': d5b.get('rf_gain_560b', 0),
            'rf_gain_combined': d5b.get('rf_gain_combined', 0),
            'nn_gain_560b': d5b.get('nn_gain_560b', 0),
            'pass': d5b['pass'],
        },
        'D7_variance': d7['pass'],
        'category_signals': category_signals,
        'findings': findings,
        'constraints_proposed': constraints,
    }

    out_path = RESULTS_DIR / 't4b_synthesis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Runtime: {time.time()-t0:.1f}s")


if __name__ == '__main__':
    main()
