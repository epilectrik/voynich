#!/usr/bin/env python3
"""
Visual Coding Phase, Task 8: Post-Coding Analysis Pipeline

Automated analysis pipeline to run AFTER visual coding is complete.
Executes all pre-registered hypothesis tests and generates comprehensive report.
"""

import json
import csv
import random
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math

# =============================================================================
# CONFIGURATION
# =============================================================================

# Input files
VISUAL_DATA_FILE = 'blinded_visual_coding.json'
TEXT_FEATURES_FILE = 'pilot_folio_text_features.json'
HYPOTHESES_FILE = 'pre_coding_hypotheses.json'
PRE_ANALYSIS_FILE = 'pre_visual_analysis_report.json'

# Output file
OUTPUT_FILE = 'blinded_correlation_results.json'

# Analysis parameters
NULL_PERMUTATIONS = 1000
ALPHA = 0.05
CRAMERS_V_THRESHOLD = 0.3
NULL_PERCENTILE_THRESHOLD = 99


# =============================================================================
# DATA LOADING AND VALIDATION
# =============================================================================

def load_visual_data(filepath: str) -> Tuple[Dict[str, Dict], Dict]:
    """
    Load and validate visual coding data from JSON.
    Returns (visual_data_dict, quality_report).
    """
    visual_data = {}
    quality_issues = []
    feature_missing = defaultdict(int)
    feature_undetermined = defaultdict(int)
    all_features = set()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        folios = data.get('folios', {})

        if not folios:
            return {}, {'error': 'No folios found in JSON'}

        for folio_id, folio_data in folios.items():
            # Get visual_features from within each folio entry
            vf = folio_data.get('visual_features', {})

            visual_data[folio_id] = {}
            for key, value in vf.items():
                all_features.add(key)

                # Handle nested structure: {"value": "X", "confidence": "Y"}
                if isinstance(value, dict):
                    value = value.get('value', None)

                if value is None or value == '':
                    feature_missing[key] += 1
                    visual_data[folio_id][key] = None
                elif str(value).upper() == 'UNDETERMINED':
                    feature_undetermined[key] += 1
                    visual_data[folio_id][key] = 'UNDETERMINED'
                else:
                    visual_data[folio_id][key] = str(value).upper()

    except FileNotFoundError:
        return {}, {'error': f'File not found: {filepath}'}
    except Exception as e:
        return {}, {'error': str(e)}

    # Calculate quality metrics
    n_folios = len(visual_data)
    n_features = len(all_features)

    quality_report = {
        'n_folios': n_folios,
        'n_features': n_features,
        'issues': quality_issues,
        'missing_per_feature': dict(feature_missing),
        'undetermined_per_feature': dict(feature_undetermined),
        'features_with_high_missing': [
            f for f, c in feature_missing.items() if c > n_folios * 0.3
        ],
        'features_with_high_undetermined': [
            f for f, c in feature_undetermined.items() if c > n_folios * 0.3
        ],
        'data_quality': 'GOOD' if not quality_issues else 'ISSUES_FOUND'
    }

    return visual_data, quality_report


def load_text_features() -> Dict[str, Dict]:
    """Load text features for pilot folios."""
    with open(TEXT_FEATURES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('pilot_folios', {})


def load_hypotheses() -> Dict:
    """Load pre-registered hypotheses."""
    with open(HYPOTHESES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_pre_analysis() -> Dict:
    """Load pre-analysis report for null thresholds."""
    try:
        with open(PRE_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# =============================================================================
# DATA PREPARATION
# =============================================================================

def join_datasets(visual_data: Dict[str, Dict],
                  text_features: Dict[str, Dict]) -> Dict[str, Dict]:
    """Join visual and text features on folio_id."""
    merged = {}

    for folio_id in visual_data:
        if folio_id not in text_features:
            print(f"  WARNING: {folio_id} not in text features")
            continue

        merged[folio_id] = {
            'visual': visual_data[folio_id],
            'text': text_features[folio_id]
        }

    return merged


def extract_prefix_groups(merged_data: Dict[str, Dict],
                          prefix_key: str = 'heading_prefix') -> Dict[str, List[str]]:
    """Group folios by prefix value."""
    groups = defaultdict(list)

    for folio_id, data in merged_data.items():
        prefix = data['text'].get(prefix_key, '')
        if prefix:
            groups[prefix].append(folio_id)

    return dict(groups)


# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def calculate_chi_square(contingency_table: List[List[int]]) -> Tuple[float, int]:
    """Calculate chi-square statistic and degrees of freedom."""
    n = sum(sum(row) for row in contingency_table)
    if n == 0:
        return 0.0, 0

    row_totals = [sum(row) for row in contingency_table]
    col_totals = [sum(contingency_table[i][j] for i in range(len(contingency_table)))
                  for j in range(len(contingency_table[0]))]

    chi_sq = 0.0
    for i, row in enumerate(contingency_table):
        for j, observed in enumerate(row):
            expected = (row_totals[i] * col_totals[j]) / n if n > 0 else 0
            if expected > 0:
                chi_sq += (observed - expected) ** 2 / expected

    df = (len(contingency_table) - 1) * (len(contingency_table[0]) - 1)
    return chi_sq, df


def calculate_cramers_v(contingency_table: List[List[int]]) -> float:
    """Calculate Cramér's V for a contingency table."""
    chi_sq, df = calculate_chi_square(contingency_table)
    n = sum(sum(row) for row in contingency_table)

    r, k = len(contingency_table), len(contingency_table[0])
    min_dim = min(r - 1, k - 1)

    if min_dim == 0 or n == 0:
        return 0.0

    return (chi_sq / (n * min_dim)) ** 0.5


def run_correlation_test(merged_data: Dict[str, Dict],
                         prefix: str,
                         visual_feature: str) -> Dict:
    """Run correlation test between prefix and visual feature."""
    # Get folios with this prefix vs others
    with_prefix = []
    without_prefix = []

    for folio_id, data in merged_data.items():
        heading_prefix = data['text'].get('heading_prefix', '')
        visual_value = data['visual'].get(visual_feature)

        if visual_value is None or visual_value == 'UNDETERMINED':
            continue

        if heading_prefix == prefix:
            with_prefix.append(visual_value)
        else:
            without_prefix.append(visual_value)

    # Build contingency table
    all_values = sorted(set(with_prefix + without_prefix))
    if len(all_values) < 2:
        return {'error': 'Insufficient visual categories'}

    value_to_idx = {v: i for i, v in enumerate(all_values)}
    table = [[0] * len(all_values) for _ in range(2)]

    for v in with_prefix:
        table[0][value_to_idx[v]] += 1
    for v in without_prefix:
        table[1][value_to_idx[v]] += 1

    chi_sq, df = calculate_chi_square(table)
    cramers_v = calculate_cramers_v(table)

    return {
        'prefix': prefix,
        'visual_feature': visual_feature,
        'n_with_prefix': len(with_prefix),
        'n_without_prefix': len(without_prefix),
        'visual_categories': all_values,
        'contingency_table': table,
        'chi_square': round(chi_sq, 4),
        'df': df,
        'cramers_v': round(cramers_v, 4),
        'with_prefix_distribution': dict(Counter(with_prefix)),
        'without_prefix_distribution': dict(Counter(without_prefix))
    }


# =============================================================================
# NULL MODEL
# =============================================================================

def run_null_model(merged_data: Dict[str, Dict],
                   prefix: str,
                   visual_feature: str,
                   n_permutations: int = 1000) -> Dict:
    """Run null model permutation test."""
    # Get observed Cramér's V
    observed_result = run_correlation_test(merged_data, prefix, visual_feature)
    if 'error' in observed_result:
        return observed_result

    observed_v = observed_result['cramers_v']

    # Get visual values
    folio_ids = list(merged_data.keys())
    visual_values = []

    for folio_id in folio_ids:
        v = merged_data[folio_id]['visual'].get(visual_feature)
        if v and v != 'UNDETERMINED':
            visual_values.append(v)
        else:
            visual_values.append(None)

    # Run permutations
    null_vs = []
    for _ in range(n_permutations):
        # Shuffle visual values
        shuffled = visual_values.copy()
        random.shuffle(shuffled)

        # Create shuffled merged data
        shuffled_merged = {}
        for i, folio_id in enumerate(folio_ids):
            shuffled_merged[folio_id] = {
                'visual': {visual_feature: shuffled[i]},
                'text': merged_data[folio_id]['text']
            }

        # Calculate Cramér's V for shuffled data
        result = run_correlation_test(shuffled_merged, prefix, visual_feature)
        if 'error' not in result:
            null_vs.append(result['cramers_v'])

    if not null_vs:
        return {'error': 'No valid null permutations'}

    # Calculate percentile
    null_vs.sort()
    n_below = sum(1 for v in null_vs if v < observed_v)
    percentile = (n_below / len(null_vs)) * 100

    return {
        'observed_cramers_v': observed_v,
        'null_mean': round(sum(null_vs) / len(null_vs), 4),
        'null_std': round((sum((v - sum(null_vs)/len(null_vs))**2 for v in null_vs) / len(null_vs))**0.5, 4),
        'null_95th': round(null_vs[int(len(null_vs) * 0.95)], 4),
        'null_99th': round(null_vs[int(len(null_vs) * 0.99)], 4),
        'percentile': round(percentile, 1),
        'significant_at_95': percentile >= 95,
        'significant_at_99': percentile >= 99
    }


# =============================================================================
# HYPOTHESIS TESTING
# =============================================================================

def test_hypothesis(merged_data: Dict[str, Dict],
                    hypothesis: Dict,
                    n_permutations: int = 1000) -> Dict:
    """Test a single pre-registered hypothesis."""
    prefix = hypothesis.get('prefix_tested', hypothesis.get('prefix', ''))
    visual_features = hypothesis.get('visual_features_tested', [])

    if not prefix or not visual_features:
        return {'error': 'Missing prefix or visual features in hypothesis'}

    results = []
    for vf in visual_features:
        # Correlation test
        corr_result = run_correlation_test(merged_data, prefix, vf)
        if 'error' in corr_result:
            results.append({
                'visual_feature': vf,
                'error': corr_result['error']
            })
            continue

        # Null model test
        null_result = run_null_model(merged_data, prefix, vf, n_permutations)

        # Evaluate against success criteria
        success_criteria = hypothesis.get('success_criterion', {})
        v_threshold = success_criteria.get('cramers_v_minimum', CRAMERS_V_THRESHOLD)
        null_threshold = success_criteria.get('null_percentile_minimum', NULL_PERCENTILE_THRESHOLD)

        cramers_v = corr_result['cramers_v']
        percentile = null_result.get('percentile', 0)

        meets_v = cramers_v >= v_threshold
        meets_null = percentile >= null_threshold

        results.append({
            'visual_feature': vf,
            'correlation': corr_result,
            'null_model': null_result,
            'evaluation': {
                'cramers_v': cramers_v,
                'v_threshold': v_threshold,
                'meets_v_criterion': meets_v,
                'null_percentile': percentile,
                'null_threshold': null_threshold,
                'meets_null_criterion': meets_null,
                'both_criteria_met': meets_v and meets_null,
                'interpretation': 'STRONG' if (meets_v and meets_null) else
                                 'MODERATE' if meets_v or meets_null else 'WEAK'
            }
        })

    # Overall hypothesis result
    any_strong = any(r.get('evaluation', {}).get('interpretation') == 'STRONG'
                     for r in results if 'error' not in r)
    any_moderate = any(r.get('evaluation', {}).get('interpretation') in ['STRONG', 'MODERATE']
                       for r in results if 'error' not in r)

    return {
        'hypothesis_id': hypothesis.get('id', 'UNKNOWN'),
        'statement': hypothesis.get('statement', ''),
        'prefix': prefix,
        'feature_results': results,
        'overall_result': 'SUPPORTED' if any_strong else
                         'PARTIALLY_SUPPORTED' if any_moderate else 'NOT_SUPPORTED',
        'prediction': hypothesis.get('prediction', '')
    }


# =============================================================================
# FULL PIPELINE
# =============================================================================

def run_full_analysis(visual_data: Dict[str, Dict],
                      text_features: Dict[str, Dict],
                      hypotheses: Dict,
                      n_permutations: int = 1000) -> Dict:
    """Run the complete analysis pipeline."""
    # Join datasets
    merged_data = join_datasets(visual_data, text_features)

    if len(merged_data) < 10:
        return {'error': f'Only {len(merged_data)} folios with both visual and text data'}

    # Test primary hypotheses
    primary_results = {}
    primary_hyp = hypotheses.get('primary_hypotheses', {})
    for h_id, h_def in primary_hyp.items():
        print(f"    Testing {h_id}: {h_def.get('statement', '')[:50]}...")
        primary_results[h_id] = test_hypothesis(merged_data, h_def, n_permutations)

    # Test secondary hypotheses
    secondary_results = {}
    secondary_hyp = hypotheses.get('secondary_hypotheses', {})
    for h_id, h_def in secondary_hyp.items():
        print(f"    Testing {h_id}: {h_def.get('statement', '')[:50]}...")
        secondary_results[h_id] = test_hypothesis(merged_data, h_def, n_permutations)

    # Test structural hypotheses (if applicable)
    structural_results = {}
    # S1, S2, S3 require different analysis approach - placeholder for now

    # Count significant results
    all_results = list(primary_results.values()) + list(secondary_results.values())
    n_supported = sum(1 for r in all_results if r.get('overall_result') == 'SUPPORTED')
    n_partial = sum(1 for r in all_results if r.get('overall_result') == 'PARTIALLY_SUPPORTED')
    n_not_supported = sum(1 for r in all_results if r.get('overall_result') == 'NOT_SUPPORTED')

    # Evaluate against pre-registered success criteria
    success_criteria = hypotheses.get('pre_registration_commitment', {}).get('success_criteria', {})

    if n_supported >= 3:
        overall_outcome = 'SUCCESS'
    elif n_supported >= 1 or n_partial >= 2:
        overall_outcome = 'PARTIAL_SUCCESS'
    else:
        overall_outcome = 'FAILURE'

    return {
        'primary_hypotheses': primary_results,
        'secondary_hypotheses': secondary_results,
        'structural_hypotheses': structural_results,
        'summary': {
            'total_hypotheses_tested': len(all_results),
            'supported': n_supported,
            'partially_supported': n_partial,
            'not_supported': n_not_supported,
            'overall_outcome': overall_outcome
        }
    }


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_report(visual_quality: Dict,
                    analysis_results: Dict,
                    hypotheses: Dict) -> Dict:
    """Generate comprehensive results report."""
    report = {
        'metadata': {
            'title': 'Visual-Text Correlation Analysis Results',
            'phase': 'Visual Coding Phase - Post-Coding Analysis',
            'date': datetime.now().isoformat(),
            'analysis_parameters': {
                'null_permutations': NULL_PERMUTATIONS,
                'alpha': ALPHA,
                'cramers_v_threshold': CRAMERS_V_THRESHOLD,
                'null_percentile_threshold': NULL_PERCENTILE_THRESHOLD
            }
        },
        'data_quality': visual_quality,
        'hypothesis_tests': analysis_results,
        'conclusions': generate_conclusions(analysis_results, hypotheses)
    }

    return report


def generate_conclusions(analysis_results: Dict, hypotheses: Dict) -> Dict:
    """Generate conclusions based on analysis results."""
    summary = analysis_results.get('summary', {})
    outcome = summary.get('overall_outcome', 'UNKNOWN')

    if outcome == 'SUCCESS':
        interpretation = (
            "Multiple pre-registered hypotheses were supported. "
            "Visual features show statistically significant correlations with text prefixes. "
            "This supports the hypothesis that prefixes encode visual/semantic information."
        )
        next_steps = [
            "Extend analysis to full Currier A corpus",
            "Investigate semantic meanings of correlated prefixes",
            "Design validation study with independent coders"
        ]
    elif outcome == 'PARTIAL_SUCCESS':
        interpretation = (
            "Some pre-registered hypotheses showed partial support. "
            "Results are suggestive but not conclusive. "
            "Statistical power limitations may explain weak effects."
        )
        next_steps = [
            "Code additional folios to increase statistical power",
            "Refine visual coding categories based on observed distributions",
            "Consider alternative prefix groupings"
        ]
    else:
        interpretation = (
            "Pre-registered hypotheses were not supported. "
            "Visual features do not show expected correlations with text prefixes. "
            "This is consistent with null hypothesis (no visual-text correlation)."
        )
        next_steps = [
            "Consider alternative hypotheses about text structure",
            "Review visual coding reliability",
            "Explore other text features (suffixes, word patterns)"
        ]

    return {
        'overall_outcome': outcome,
        'interpretation': interpretation,
        'next_steps': next_steps,
        'null_predictions': hypotheses.get('null_predictions', {}),
        'limitations': [
            'Small sample size (30 folios)',
            'Power limited to large effects only',
            'Most heading prefixes appear only once',
            'Visual coding by single coder (reliability not verified)'
        ]
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Visual Coding Phase, Task 8: Post-Coding Analysis Pipeline")
    print("=" * 70)

    # Step 1: Load visual data
    print("\n[1/5] Loading visual coding data...")
    visual_data, quality_report = load_visual_data(VISUAL_DATA_FILE)

    if 'error' in quality_report:
        print(f"  ERROR: {quality_report['error']}")
        print("\n  NOTE: This pipeline runs AFTER visual coding is complete.")
        print("        Fill in visual_data_template.csv with coded features first.")
        print("\n  Generating TEMPLATE report with placeholder data...")

        # Generate template report showing what will be produced
        template_report = {
            'metadata': {
                'title': 'Visual-Text Correlation Analysis Results (TEMPLATE)',
                'phase': 'Visual Coding Phase - Post-Coding Analysis',
                'date': datetime.now().isoformat(),
                'status': 'AWAITING_VISUAL_CODING',
                'note': 'This is a template showing expected output format'
            },
            'instructions': {
                'step_1': 'Complete visual coding using coding_checklist.md',
                'step_2': 'Fill in visual_data_template.csv with coded values',
                'step_3': 'Re-run this script: python post_coding_pipeline.py',
                'expected_output': 'Full correlation analysis results'
            },
            'expected_sections': [
                'data_quality - Visual coding completeness and reliability',
                'hypothesis_tests - Results for all pre-registered hypotheses',
                'conclusions - Overall interpretation and next steps'
            ]
        }

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(template_report, f, indent=2, ensure_ascii=False)

        print(f"\n  Saved template to: {OUTPUT_FILE}")
        return template_report

    print(f"  Loaded {quality_report['n_folios']} folios, {quality_report['n_features']} features")
    print(f"  Data quality: {quality_report['data_quality']}")

    # Step 2: Load text features
    print("\n[2/5] Loading text features...")
    text_features = load_text_features()
    print(f"  Loaded {len(text_features)} folio text features")

    # Step 3: Load hypotheses
    print("\n[3/5] Loading pre-registered hypotheses...")
    hypotheses = load_hypotheses()
    n_primary = len(hypotheses.get('primary_hypotheses', {}))
    n_secondary = len(hypotheses.get('secondary_hypotheses', {}))
    print(f"  Loaded {n_primary} primary + {n_secondary} secondary hypotheses")

    # Step 4: Run analysis
    print("\n[4/5] Running correlation analysis...")
    print(f"  ({NULL_PERMUTATIONS} permutations per test - this may take a moment)")

    analysis_results = run_full_analysis(
        visual_data, text_features, hypotheses, NULL_PERMUTATIONS
    )

    if 'error' in analysis_results:
        print(f"  ERROR: {analysis_results['error']}")
        return None

    summary = analysis_results.get('summary', {})
    print(f"\n  Results:")
    print(f"    Supported: {summary.get('supported', 0)}")
    print(f"    Partially supported: {summary.get('partially_supported', 0)}")
    print(f"    Not supported: {summary.get('not_supported', 0)}")
    print(f"    Overall outcome: {summary.get('overall_outcome', 'UNKNOWN')}")

    # Step 5: Generate report
    print("\n[5/5] Generating report...")
    report = generate_report(quality_report, analysis_results, hypotheses)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  Saved to: {OUTPUT_FILE}")

    # Summary
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    conclusions = report.get('conclusions', {})
    print(f"\nOutcome: {conclusions.get('overall_outcome', 'UNKNOWN')}")
    print(f"\nInterpretation:")
    print(f"  {conclusions.get('interpretation', 'N/A')}")
    print(f"\nNext steps:")
    for step in conclusions.get('next_steps', []):
        print(f"  - {step}")

    return report


if __name__ == '__main__':
    main()
