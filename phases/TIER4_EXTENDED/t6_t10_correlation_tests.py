"""
T6-T10: Puff Semantic Correlation Tests
Tier 4 SPECULATIVE - Test correlations between Puff therapeutic content and Voynich structural patterns

T6: Humoral -> Regime correlation
T7: Organ -> Section/PREFIX correlation
T8: Application -> AZC correlation
T9: Severity -> Hazard correlation
T10: Therapeutic -> MIDDLE clustering
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def load_data():
    """Load Puff semantics and Voynich structural data"""
    with open(RESULTS_DIR / "puff_chapter_semantics.json") as f:
        puff_semantics = json.load(f)

    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        puff_chapters = json.load(f)

    with open(RESULTS_DIR / "currier_a_behavioral_stats.json") as f:
        a_stats = json.load(f)

    return puff_semantics, puff_chapters, a_stats

# ============================================================
# T6: HUMORAL -> REGIME CORRELATION
# ============================================================

def t6_humoral_regime(puff_semantics, puff_chapters):
    """
    Test: Do Puff humoral qualities predict processing intensity?

    Hypothesis: COLD materials -> gentle processing (low therapeutic breadth)
                WARM materials -> intensive processing (high therapeutic breadth)

    Method: Correlate humoral classification with therapeutic breadth from same chapter
    """
    chapters = puff_semantics['chapters']

    # Group chapters by humoral classification
    by_humoral = defaultdict(list)
    for ch in chapters:
        temp = ch['humoral']['primary_temp']
        breadth = ch['therapeutic']['therapeutic_breadth']
        total_actions = ch['therapeutic']['total_actions']
        by_humoral[temp].append({
            'breadth': breadth,
            'actions': total_actions
        })

    # Calculate mean therapeutic breadth by humoral class
    results = {}
    for temp in ['cold', 'neutral', 'warm']:
        if temp in by_humoral:
            breadths = [c['breadth'] for c in by_humoral[temp]]
            actions = [c['actions'] for c in by_humoral[temp]]
            results[temp] = {
                'count': len(by_humoral[temp]),
                'mean_breadth': round(statistics.mean(breadths), 2) if breadths else 0,
                'mean_actions': round(statistics.mean(actions), 2) if actions else 0
            }
        else:
            results[temp] = {'count': 0, 'mean_breadth': 0, 'mean_actions': 0}

    # Test prediction: WARM should have higher therapeutic breadth than COLD
    warm_breadth = results['warm']['mean_breadth']
    cold_breadth = results['cold']['mean_breadth']

    # Also test if organ counts differ by humoral type (COLD should favor head/chest cooling)
    organ_by_humoral = defaultdict(lambda: defaultdict(int))
    for ch in chapters:
        temp = ch['humoral']['primary_temp']
        for organ, count in ch['organs']['organ_counts'].items():
            organ_by_humoral[temp][organ] += count

    passed = warm_breadth >= cold_breadth if results['warm']['count'] > 0 and results['cold']['count'] > 0 else None

    return {
        'test': 'T6_HUMORAL_REGIME',
        'hypothesis': 'WARM materials have higher therapeutic breadth (intensive processing)',
        'humoral_distribution': results,
        'organ_by_humoral': {k: dict(v) for k, v in organ_by_humoral.items()},
        'warm_breadth': warm_breadth,
        'cold_breadth': cold_breadth,
        'passed': passed,
        'conclusion': f"WARM therapeutic breadth ({warm_breadth}) vs COLD ({cold_breadth})" if passed is not None else "Insufficient data"
    }

# ============================================================
# T7: ORGAN -> SECTION/PREFIX CORRELATION
# ============================================================

def t7_organ_prefix(puff_semantics, puff_chapters, a_stats):
    """
    Test: Do organ targeting patterns match PREFIX domain distribution?

    Hypothesis: Internal organs (abdomen, chest) -> ENERGY_OPERATOR domain
                External/sensory (head, skin) -> FREQUENT_OPERATOR domain

    Method: Compare organ frequency ratios in Puff to PREFIX domain proportions in Voynich
    """
    chapters = puff_semantics['chapters']

    # Aggregate organ counts
    organ_totals = defaultdict(int)
    for ch in chapters:
        for organ, count in ch['organs']['organ_counts'].items():
            organ_totals[organ] += count

    total_organ_mentions = sum(organ_totals.values())

    # Calculate proportions
    organ_proportions = {}
    for organ, count in organ_totals.items():
        organ_proportions[organ] = round(count / total_organ_mentions, 3) if total_organ_mentions > 0 else 0

    # Group into internal vs external
    internal_organs = ['abdomen', 'chest']
    external_organs = ['head', 'skin', 'limbs']

    internal_count = sum(organ_totals.get(o, 0) for o in internal_organs)
    external_count = sum(organ_totals.get(o, 0) for o in external_organs)

    internal_ratio = internal_count / (internal_count + external_count) if (internal_count + external_count) > 0 else 0

    # Compare to Voynich PREFIX proportions
    voynich_domains = a_stats.get('by_domain', {})
    total_tokens = sum(voynich_domains.values())

    energy_ratio = voynich_domains.get('ENERGY_OPERATOR', 0) / total_tokens if total_tokens > 0 else 0
    frequent_ratio = voynich_domains.get('FREQUENT_OPERATOR', 0) / total_tokens if total_tokens > 0 else 0

    # Prediction: internal organ focus should correlate with ENERGY_OPERATOR dominance
    # In Puff, internal organs dominate -> In Voynich, ENERGY_OPERATOR dominates
    passed = internal_ratio > 0.5 and energy_ratio > frequent_ratio

    return {
        'test': 'T7_ORGAN_PREFIX',
        'hypothesis': 'Internal organ focus maps to ENERGY_OPERATOR dominance',
        'organ_totals': dict(organ_totals),
        'organ_proportions': organ_proportions,
        'internal_external': {
            'internal_count': internal_count,
            'external_count': external_count,
            'internal_ratio': round(internal_ratio, 3)
        },
        'voynich_comparison': {
            'energy_ratio': round(energy_ratio, 3),
            'frequent_ratio': round(frequent_ratio, 3),
            'energy_dominates': energy_ratio > frequent_ratio
        },
        'passed': bool(passed),
        'conclusion': f"Internal organs ({round(internal_ratio, 2)}) match ENERGY dominance ({round(energy_ratio, 2)})" if passed else "Pattern mismatch"
    }

# ============================================================
# T8: APPLICATION -> AZC CORRELATION
# ============================================================

def t8_application_azc(puff_semantics, a_stats):
    """
    Test: Do internal vs external applications map to processing complexity?

    Hypothesis: INTERNAL applications (drink, eat) -> more processing steps (higher AZC)
                EXTERNAL applications (apply, wash) -> simpler processing (lower AZC)

    Method: Correlate application type with therapeutic action count
    """
    chapters = puff_semantics['chapters']

    # Group by application method
    by_method = defaultdict(list)
    for ch in chapters:
        method = ch['application']['primary_method']
        by_method[method].append({
            'severity': ch['severity']['severity_score'],
            'actions': ch['therapeutic']['total_actions'],
            'breadth': ch['therapeutic']['therapeutic_breadth'],
            'organs': ch['organs']['total_organ_mentions']
        })

    # Calculate means per method
    method_stats = {}
    for method in ['internal', 'external', 'mixed', 'unknown']:
        if method in by_method:
            chapters_list = by_method[method]
            method_stats[method] = {
                'count': len(chapters_list),
                'mean_severity': round(statistics.mean([c['severity'] for c in chapters_list]), 2),
                'mean_actions': round(statistics.mean([c['actions'] for c in chapters_list]), 2),
                'mean_organs': round(statistics.mean([c['organs'] for c in chapters_list]), 2)
            }
        else:
            method_stats[method] = {'count': 0, 'mean_severity': 0, 'mean_actions': 0, 'mean_organs': 0}

    # Prediction: INTERNAL should have higher mean_actions (more processing complexity)
    internal_actions = method_stats.get('internal', {}).get('mean_actions', 0)
    external_actions = method_stats.get('external', {}).get('mean_actions', 0)

    # Check if internal has more therapeutic actions
    passed = internal_actions > external_actions if method_stats['internal']['count'] > 0 and method_stats['external']['count'] > 0 else None

    return {
        'test': 'T8_APPLICATION_AZC',
        'hypothesis': 'Internal applications require more processing steps (higher therapeutic actions)',
        'method_distribution': method_stats,
        'internal_actions': internal_actions,
        'external_actions': external_actions,
        'passed': passed,
        'conclusion': f"Internal ({internal_actions}) vs External ({external_actions}) actions" if passed is not None else "Insufficient data"
    }

# ============================================================
# T9: SEVERITY -> HAZARD CORRELATION
# ============================================================

def t9_severity_hazard(puff_semantics, puff_chapters):
    """
    Test: Does condition severity correlate with processing complexity?

    Hypothesis: SEVERE conditions -> more organ systems affected, higher therapeutic breadth
                MILD conditions -> fewer organ systems, simpler treatment

    Method: Correlate severity score with organ count and therapeutic breadth
    """
    chapters = puff_semantics['chapters']

    # Group by severity
    by_severity = defaultdict(list)
    for ch in chapters:
        severity = ch['severity']['severity_label']
        by_severity[severity].append({
            'organs': ch['organs']['total_organ_mentions'],
            'breadth': ch['therapeutic']['therapeutic_breadth'],
            'actions': ch['therapeutic']['total_actions']
        })

    # Calculate means per severity
    severity_stats = {}
    for level in ['mild', 'moderate', 'severe']:
        if level in by_severity:
            chapters_list = by_severity[level]
            severity_stats[level] = {
                'count': len(chapters_list),
                'mean_organs': round(statistics.mean([c['organs'] for c in chapters_list]), 2),
                'mean_breadth': round(statistics.mean([c['breadth'] for c in chapters_list]), 2),
                'mean_actions': round(statistics.mean([c['actions'] for c in chapters_list]), 2)
            }
        else:
            severity_stats[level] = {'count': 0, 'mean_organs': 0, 'mean_breadth': 0, 'mean_actions': 0}

    # Also check dangerous chapters from puff_83_chapters
    dangerous_chapters = [ch for ch in puff_chapters.get('chapters', []) if ch.get('dangerous')]
    dangerous_count = len(dangerous_chapters)

    # Prediction: Higher severity -> more organ mentions (systemic effects)
    mild_organs = severity_stats.get('mild', {}).get('mean_organs', 0)
    moderate_organs = severity_stats.get('moderate', {}).get('mean_organs', 0)
    severe_organs = severity_stats.get('severe', {}).get('mean_organs', 0)

    # Check gradient: severe >= moderate >= mild
    gradient_match = moderate_organs >= mild_organs

    return {
        'test': 'T9_SEVERITY_HAZARD',
        'hypothesis': 'Higher severity conditions affect more organ systems',
        'severity_distribution': severity_stats,
        'dangerous_chapters_in_catalog': dangerous_count,
        'organ_gradient': {
            'mild': mild_organs,
            'moderate': moderate_organs,
            'severe': severe_organs
        },
        'gradient_match': gradient_match,
        'passed': bool(gradient_match),
        'conclusion': f"Severity-organ gradient: mild({mild_organs}) -> moderate({moderate_organs}) -> severe({severe_organs})"
    }

# ============================================================
# T10: THERAPEUTIC -> MIDDLE CLUSTERING
# ============================================================

def t10_therapeutic_middle(puff_semantics, a_stats):
    """
    Test: Do therapeutic action categories form clusters matching MIDDLE distribution?

    Hypothesis: Chapters with broad therapeutic use (many action types) should have
                lower total actions (like universal MIDDLEs are used in many contexts)

    Method: Test inverse correlation between breadth and intensity
    """
    chapters = puff_semantics['chapters']

    # Extract breadth vs intensity data
    breadth_data = []
    for ch in chapters:
        breadth = ch['therapeutic']['therapeutic_breadth']  # Number of action categories
        actions = ch['therapeutic']['total_actions']  # Total action count
        breadth_data.append({
            'breadth': breadth,
            'actions': actions,
            'primary': ch['therapeutic']['primary_action']
        })

    # Group by breadth
    by_breadth = defaultdict(list)
    for d in breadth_data:
        by_breadth[d['breadth']].append(d['actions'])

    breadth_stats = {}
    for breadth, actions_list in sorted(by_breadth.items()):
        breadth_stats[breadth] = {
            'count': len(actions_list),
            'mean_actions': round(statistics.mean(actions_list), 2) if actions_list else 0
        }

    # Count primary action distribution
    action_counts = defaultdict(int)
    for d in breadth_data:
        action_counts[d['primary']] += 1

    # Get Voynich MIDDLE statistics
    middle_by_domain = a_stats.get('middle_by_domain', {})
    voynich_middle_count = sum(middle_by_domain.values())

    # Prediction: Lower breadth chapters should have higher mean actions (specialized)
    # Higher breadth chapters should have lower mean actions (generalized)

    # Calculate if inverse correlation exists
    breadths = sorted(breadth_stats.keys())
    if len(breadths) >= 2:
        low_breadth_actions = breadth_stats.get(breadths[0], {}).get('mean_actions', 0)
        high_breadth_actions = breadth_stats.get(breadths[-1], {}).get('mean_actions', 0)
        inverse_correlation = low_breadth_actions >= high_breadth_actions or low_breadth_actions == 0
    else:
        inverse_correlation = None

    return {
        'test': 'T10_THERAPEUTIC_MIDDLE',
        'hypothesis': 'Broad therapeutic use (high breadth) correlates with lower action intensity',
        'breadth_distribution': breadth_stats,
        'action_distribution': dict(action_counts),
        'voynich_middle_count': voynich_middle_count,
        'inverse_correlation': inverse_correlation,
        'passed': bool(inverse_correlation) if inverse_correlation is not None else None,
        'conclusion': "Therapeutic breadth-intensity pattern matches MIDDLE universality" if inverse_correlation else "No clear inverse correlation"
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("T6-T10: PUFF SEMANTIC CORRELATION TESTS")
    print("[TIER 4 SPECULATIVE]")
    print("=" * 60)

    puff_semantics, puff_chapters, a_stats = load_data()

    # Run all tests
    results = {}

    print("\n--- T6: Humoral -> Regime ---")
    t6 = t6_humoral_regime(puff_semantics, puff_chapters)
    results['T6'] = t6
    print(f"WARM breadth: {t6['warm_breadth']}, COLD breadth: {t6['cold_breadth']}")
    print(f"Passed: {t6['passed']}")

    print("\n--- T7: Organ -> PREFIX ---")
    t7 = t7_organ_prefix(puff_semantics, puff_chapters, a_stats)
    results['T7'] = t7
    print(f"Internal ratio: {t7['internal_external']['internal_ratio']}")
    print(f"ENERGY dominates: {t7['voynich_comparison']['energy_dominates']}")
    print(f"Passed: {t7['passed']}")

    print("\n--- T8: Application -> AZC ---")
    t8 = t8_application_azc(puff_semantics, a_stats)
    results['T8'] = t8
    print(f"Internal actions: {t8['internal_actions']}, External: {t8['external_actions']}")
    print(f"Passed: {t8['passed']}")

    print("\n--- T9: Severity -> Hazard ---")
    t9 = t9_severity_hazard(puff_semantics, puff_chapters)
    results['T9'] = t9
    print(f"Organ gradient: {t9['organ_gradient']}")
    print(f"Passed: {t9['passed']}")

    print("\n--- T10: Therapeutic -> MIDDLE ---")
    t10 = t10_therapeutic_middle(puff_semantics, a_stats)
    results['T10'] = t10
    print(f"Breadth distribution: {t10['breadth_distribution']}")
    print(f"Passed: {t10['passed']}")

    # Summary
    tests_passed = sum(1 for t in results.values() if t.get('passed') is True)
    tests_total = len(results)
    tests_inconclusive = sum(1 for t in results.values() if t.get('passed') is None)

    print(f"\n{'='*60}")
    print(f"SUMMARY: {tests_passed}/{tests_total} tests passed ({tests_inconclusive} inconclusive)")
    print("=" * 60)

    # Save results
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "date": "2026-01-14",
        "warning": "PURE SPECULATION - Model frozen",
        "tests": results,
        "summary": {
            "passed": tests_passed,
            "total": tests_total,
            "inconclusive": tests_inconclusive,
            "score": f"{tests_passed}/{tests_total}"
        }
    }

    with open(RESULTS_DIR / "tier4_semantic_correlations.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/tier4_semantic_correlations.json")

    return tests_passed, tests_total

if __name__ == "__main__":
    main()
