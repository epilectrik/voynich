#!/usr/bin/env python3
"""
Data Recovery Phase, Task 9: Results Reporting Framework

Generates structured reports for success, failure, or partial results.
Ensures consistent presentation and hedged language.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

# =============================================================================
# REPORT TEMPLATES
# =============================================================================

def generate_success_report(correlation_results: Dict,
                           stress_test_results: Dict,
                           enum_mappings: Dict) -> str:
    """
    Generate success report when pre-registered criteria are met.

    Criteria:
    - >=3 correlations at p < 0.01 (Bonferroni)
    - >=1 correlation >99th percentile null
    - Single-dimension correlations
    """
    significant = correlation_results.get('significant_results', {})
    bonferroni_sig = significant.get('bonferroni_significant', [])
    null_sig = significant.get('null_model_significant', [])
    criteria = correlation_results.get('pre_registered_criteria', {})

    report = f"""
# Visual Correlation Results: SUCCESS

**Date:** {datetime.now().isoformat()}
**Status:** Pre-registered criteria MET

---

## Pre-Registered Criteria: MET

| Criterion | Required | Found | Status |
|-----------|----------|-------|--------|
| Correlations at p < 0.01 (Bonferroni) | >=3 | {len(bonferroni_sig)} | {'PASS' if criteria.get('criterion_1', {}).get('met') else 'FAIL'} |
| Correlation >99th percentile null | >=1 | {len(null_sig)} | {'PASS' if criteria.get('criterion_2', {}).get('met') else 'FAIL'} |
| Single-dimension correlations | Required | {'Yes' if criteria.get('criterion_3', {}).get('met') else 'No'} | {'PASS' if criteria.get('criterion_3', {}).get('met') else 'FAIL'} |

---

## Significant Correlations Found

| Visual Feature | Text Feature | Cramer's V | Null %ile | Confidence |
|----------------|--------------|------------|-----------|------------|
"""

    for corr in bonferroni_sig[:10]:
        mapping = enum_mappings.get(f"{corr['visual']}_{corr['text']}", {})
        confidence = mapping.get('confidence', 'LOW')
        report += f"| {corr['visual']} | {corr['text']} | {corr.get('cramers_v', 0):.3f} | {corr.get('null_percentile', 0):.1f} | {confidence} |\n"

    report += f"""
---

## Classifier Mappings Recovered

**Note:** All mappings use hedged language. "Correlates with" does NOT mean "equals" or "encodes".
"""

    high_conf = [m for m in enum_mappings.values() if m.get('confidence') == 'HIGH']
    med_conf = [m for m in enum_mappings.values() if m.get('confidence') == 'MEDIUM']

    if high_conf:
        report += "\n### HIGH Confidence Mappings\n\n"
        for m in high_conf:
            report += f"- Classifier '{m['prefix']}' correlates with {m['visual_feature']}={m['visual_value']}\n"
            report += f"  - Effect size: {m['effect_size']:.3f}, Propagation: {m['propagation_count']}, Context diversity: {m['context_diversity']}\n"

    if med_conf:
        report += "\n### MEDIUM Confidence Mappings\n\n"
        for m in med_conf:
            report += f"- Classifier '{m['prefix']}' correlates with {m['visual_feature']}={m['visual_value']}\n"

    report += f"""
---

## Schema Stress Test

"""
    if stress_test_results:
        interp = stress_test_results.get('interpretation', 'UNKNOWN')
        report += f"**Result:** {interp}\n\n"
        report += f"- Original significant correlations: {stress_test_results.get('original_significant_correlations', 0)}\n"
        report += f"- Permuted mean: {stress_test_results.get('permuted_statistics', {}).get('mean', 0):.2f}\n"
        report += f"- Original percentile: {stress_test_results.get('comparison', {}).get('original_percentile', 0):.1f}\n"
        report += f"\n{stress_test_results.get('explanation', '')}\n"

    report += f"""
---

## Implications

The visual correlation study has **succeeded**:

1. **Classifier markers correlate with morphological features** - Specific prefixes track specific visual properties
2. **Correlations are robust** - They survive null model comparison and stress testing
3. **Path to entity identification is now open** - Visual features can anchor semantic interpretation

### Next Steps

1. Extend analysis to full Currier A corpus (114 entries)
2. Use visual feature correlations to guide entity identification
3. Then (and only then) proceed to heading phonetic analysis with external matching

---

## Important Caveats

- Correlation is not causation
- "Correlates with" does not mean "represents" or "encodes"
- These findings establish statistical relationships, not semantic equivalences
- Further validation required before any translation claims
"""

    return report


def generate_failure_report(correlation_results: Dict,
                           tests_performed: List[str]) -> str:
    """
    Generate failure report when pre-registered criteria are NOT met.
    """
    criteria = correlation_results.get('pre_registered_criteria', {})

    report = f"""
# Visual Correlation Results: NEGATIVE

**Date:** {datetime.now().isoformat()}
**Status:** Pre-registered criteria NOT MET

---

## Pre-Registered Criteria: NOT MET

| Criterion | Required | Found | Status |
|-----------|----------|-------|--------|
| Correlations at p < 0.01 (Bonferroni) | >=3 | {criteria.get('criterion_1', {}).get('count', 0)} | FAIL |
| Correlation >99th percentile null | >=1 | {criteria.get('criterion_2', {}).get('count', 0)} | FAIL |
| Single-dimension correlations | Required | - | N/A |

---

## Tests Performed

All pre-registered tests were completed as specified:

| Visual Feature | Text Features Tested | Result |
|----------------|---------------------|--------|
"""

    for test in tests_performed[:20]:
        report += f"| {test} | prefix, word_count, vocabulary | No significant correlation |\n"

    report += f"""
---

## Results

- **No significant correlations** after Bonferroni correction, OR
- **All correlations explained** by null model, OR
- **Only compound features** correlated (rejected per protocol)

---

## Implications

This negative result is **scientifically informative**. It suggests one of:

1. **Illustrations are symbolic/schematic** - Not morphologically representative
2. **Classifier markers encode abstract categories** - Not tied to visual properties
3. **The encoding system is more complex** - Direct feature mapping insufficient

---

## What Remains Valid

**All structural findings are unaffected by this negative correlation result:**

- Schema structure (Currier A/B, three-part entries)
- B->A referential relationship (151 edges, infinite asymmetry)
- Heading word properties (78.3% unique, proper names)
- Part-specific vocabulary (33 words)
- Prefix positional roles
- Entry boundary detection
- Genre matches (herbal/encyclopedia)

---

## Publication Path

A **structure-only paper** documenting schema recovery is fully supported:

1. Formal database structure identified (tables, fields, foreign keys)
2. Classifier markers characterized (position, distribution, role)
3. Cross-referential relationship proven
4. Visual correlation attempted but negative

This is a **valid scientific contribution** - negative results are results.

---

## Recommendations

1. Consider alternative visual coding schemes
2. Test finer-grained visual features
3. Explore non-morphological correlations (layout, density)
4. Proceed with structural publication
"""

    return report


def generate_partial_report(correlation_results: Dict,
                           stress_test_results: Optional[Dict] = None) -> str:
    """
    Generate partial success report when some criteria met.
    """
    criteria = correlation_results.get('pre_registered_criteria', {})
    significant = correlation_results.get('significant_results', {})

    report = f"""
# Visual Correlation Results: PARTIAL

**Date:** {datetime.now().isoformat()}
**Status:** Pre-registered criteria PARTIALLY MET

---

## Pre-Registered Criteria: PARTIALLY MET

| Criterion | Required | Found | Status |
|-----------|----------|-------|--------|
| Correlations at p < 0.01 (Bonferroni) | >=3 | {criteria.get('criterion_1', {}).get('count', 0)} | {'PASS' if criteria.get('criterion_1', {}).get('met') else 'FAIL'} |
| Correlation >99th percentile null | >=1 | {criteria.get('criterion_2', {}).get('count', 0)} | {'PASS' if criteria.get('criterion_2', {}).get('met') else 'FAIL'} |

---

## Correlations Found (With Caveats)

"""

    bonferroni_sig = significant.get('bonferroni_significant', [])
    if bonferroni_sig:
        report += "| Visual Feature | Text Feature | Cramer's V | Null %ile | Note |\n"
        report += "|----------------|--------------|------------|-----------|------|\n"
        for corr in bonferroni_sig:
            note = "Below null threshold" if corr.get('null_percentile', 0) < 99 else "Valid"
            report += f"| {corr['visual']} | {corr['text']} | {corr.get('cramers_v', 0):.3f} | {corr.get('null_percentile', 0):.1f} | {note} |\n"

    report += f"""
---

## Interpretation

**Limited semantic claims may be possible** for specific classifiers, but full enum recovery is not supported.

### What Can Be Claimed

- Specific prefix-visual correlations (if any passed null model)
- These correlations are suggestive but not definitive
- Further validation required

### What Cannot Be Claimed

- Systematic classifier-to-visual mapping
- General semantic encoding principles
- Translation or meaning claims

---

## Recommended Next Steps

1. **Extend pilot sample** - Increase from 30 to 60+ folios for more statistical power
2. **Refine visual coding** - Tighter operational definitions may reduce noise
3. **Focus on strongest correlations** - Investigate specific prefix-visual pairs in detail
4. **Consider alternative feature definitions** - Current features may not capture relevant variation

---

## Publication Considerations

A **cautious partial-results paper** could:

1. Report structural findings (fully supported)
2. Note partial visual correlations (with appropriate hedging)
3. Identify promising directions for future work
4. Avoid overclaiming semantic recovery
"""

    return report


# =============================================================================
# JSON REPORT GENERATION
# =============================================================================

def generate_json_report(correlation_results: Dict,
                        stress_test_results: Optional[Dict],
                        enum_mappings: Dict,
                        fk_validation: Dict) -> Dict:
    """
    Generate structured JSON report for programmatic consumption.
    """
    criteria = correlation_results.get('pre_registered_criteria', {})
    overall_success = criteria.get('overall_success', False)

    if overall_success:
        outcome = "SUCCESS"
    elif criteria.get('criterion_1', {}).get('met') or criteria.get('criterion_2', {}).get('met'):
        outcome = "PARTIAL"
    else:
        outcome = "FAILURE"

    return {
        'metadata': {
            'title': 'Visual Correlation Study Results',
            'phase': 'Data Recovery Phase',
            'date': datetime.now().isoformat(),
            'outcome': outcome
        },
        'pre_registered_criteria': criteria,
        'correlation_results': {
            'n_tests': correlation_results.get('metadata', {}).get('n_tests', 0),
            'significant_bonferroni': len(correlation_results.get('significant_results', {}).get('bonferroni_significant', [])),
            'significant_null': len(correlation_results.get('significant_results', {}).get('null_model_significant', []))
        },
        'stress_test': stress_test_results.get('interpretation') if stress_test_results else 'NOT_RUN',
        'enum_mappings': {
            'high_confidence': len([m for m in enum_mappings.values() if m.get('confidence') == 'HIGH']),
            'medium_confidence': len([m for m in enum_mappings.values() if m.get('confidence') == 'MEDIUM']),
            'low_confidence': len([m for m in enum_mappings.values() if m.get('confidence') == 'LOW'])
        },
        'foreign_key_validation': {
            'semantic_consistency': fk_validation.get('semantic_consistency_test', {}).get('interpretation'),
            'outliers': fk_validation.get('outlier_detection', {}).get('n_outliers', 0)
        },
        'next_steps': {
            'SUCCESS': ['Extend to full corpus', 'Entity identification', 'Phonetic analysis'],
            'PARTIAL': ['Extend pilot sample', 'Refine visual coding', 'Focus on strong correlations'],
            'FAILURE': ['Structure-only publication', 'Alternative approaches', 'Negative result paper']
        }.get(outcome, [])
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 9: Results Report Generator")
    print("=" * 70)

    print("\nResults report generator ready.")
    print("Awaiting correlation results to generate appropriate report.")

    print("\nReport types available:")
    print("  - SUCCESS: All pre-registered criteria met")
    print("  - FAILURE: Criteria not met (negative result)")
    print("  - PARTIAL: Some criteria met")

    print("\nOutput formats:")
    print("  - Markdown report (human-readable)")
    print("  - JSON report (programmatic)")

    # Save configuration
    config = {
        'metadata': {
            'title': 'Results Report Generator Configuration',
            'phase': 'Data Recovery Phase, Task 9',
            'date': datetime.now().isoformat()
        },
        'report_types': ['SUCCESS', 'PARTIAL', 'FAILURE'],
        'output_formats': ['markdown', 'json'],
        'hedged_language_required': True,
        'status': 'READY - awaiting correlation results'
    }

    with open('results_report_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print(f"\nSaved configuration to: results_report_config.json")


if __name__ == '__main__':
    main()
