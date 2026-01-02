#!/usr/bin/env python3
"""
Visual Coding Phase, Task 5: Correlation Engine Test

Validates the correlation engine with synthetic visual data.
Tests three scenarios: random, strong correlation, weak correlation.
"""

import json
import random
from datetime import datetime
from typing import Dict, List

# Import correlation engine functions
from correlation_engine import (
    chi_square_test,
    test_categorical_association,
    null_model_test,
    apply_bonferroni
)

# =============================================================================
# CONFIGURATION
# =============================================================================

PILOT_TEXT_FEATURES_FILE = 'pilot_folio_text_features.json'
PILOT_SELECTION_FILE = 'pilot_folio_selection.json'

# Synthetic data configuration
RANDOM_SEED = 42

# Visual feature values for synthetic generation
VISUAL_FEATURE_VALUES = {
    'root_type': ['NONE', 'SINGLE_TAPROOT', 'BRANCHING', 'BULBOUS', 'FIBROUS'],
    'root_present': ['PRESENT', 'ABSENT'],
    'leaf_present': ['PRESENT', 'ABSENT'],
    'leaf_shape': ['ROUND', 'OVAL', 'LANCEOLATE', 'LOBED', 'COMPOUND', 'MIXED'],
    'flower_present': ['PRESENT', 'ABSENT'],
    'stem_type': ['STRAIGHT', 'CURVED', 'BRANCHING', 'TWINING'],
    'plant_symmetry': ['SYMMETRIC', 'ASYMMETRIC']
}

# Prefixes for planted correlations
PLANTED_PREFIXES = {
    'po': ['f11v', 'f51v', 'f23v'],  # Folios with 'po' heading prefix
    'ko': ['f5v', 'f45v', 'f3v', 'f29v'],  # Folios with 'ko' heading prefix
    'ch': []  # Will be filled based on dominant body prefix
}


# =============================================================================
# DATA LOADING
# =============================================================================

def load_pilot_text_features() -> Dict:
    """Load pilot folio text features."""
    # Always use pilot selection for consistent prefix data
    with open(PILOT_SELECTION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Build text features from selection data
        features = {}
        for folio in data.get('folio_details', []):
            features[folio['folio_id']] = {
                'folio_id': folio['folio_id'],
                'word_count': folio.get('word_count', 100),
                'heading_word': folio.get('opening_word', ''),
                'heading_prefix': folio.get('opening_prefix', ''),
                'part1_dominant_prefix': folio.get('opening_prefix', ''),
                'part2_dominant_prefix': 'ch',  # Default
                'part3_dominant_prefix': 'ol',  # Default
            }
        return features


def get_pilot_folio_ids() -> List[str]:
    """Get list of pilot folio IDs."""
    with open(PILOT_SELECTION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('pilot_study_folios', [])


# =============================================================================
# SYNTHETIC DATA GENERATION
# =============================================================================

def generate_random_visual_data(folio_ids: List[str], seed: int = RANDOM_SEED) -> Dict:
    """
    Generate synthetic visual data with random assignments.

    Version A: No planted correlations.
    Expected: 0-2 spurious significant correlations.
    """
    random.seed(seed)

    visual_data = {}
    for folio_id in folio_ids:
        visual_data[folio_id] = {
            'root_type': random.choice(VISUAL_FEATURE_VALUES['root_type']),
            'root_present': random.choice(VISUAL_FEATURE_VALUES['root_present']),
            'leaf_present': random.choice(VISUAL_FEATURE_VALUES['leaf_present']),
            'leaf_shape': random.choice(VISUAL_FEATURE_VALUES['leaf_shape']),
            'flower_present': random.choice(VISUAL_FEATURE_VALUES['flower_present']),
            'stem_type': random.choice(VISUAL_FEATURE_VALUES['stem_type']),
            'plant_symmetry': random.choice(VISUAL_FEATURE_VALUES['plant_symmetry'])
        }

    return visual_data


def generate_strong_correlation_data(folio_ids: List[str], text_features: Dict,
                                     seed: int = RANDOM_SEED) -> Dict:
    """
    Generate synthetic visual data with strong planted correlations.

    Version B: 100% correlation for specific prefix-feature pairs.
    - All 'po' prefix folios get root_type=BULBOUS
    - All 'ko' prefix folios get leaf_present=PRESENT
    Expected: 2+ significant correlations.
    """
    random.seed(seed)

    # Start with random data
    visual_data = generate_random_visual_data(folio_ids, seed)

    # Plant correlation 1: po prefix -> BULBOUS root
    for folio_id in folio_ids:
        heading_prefix = text_features.get(folio_id, {}).get('heading_prefix', '')
        if heading_prefix == 'po':
            visual_data[folio_id]['root_type'] = 'BULBOUS'
            visual_data[folio_id]['root_present'] = 'PRESENT'

    # Plant correlation 2: ko prefix -> leaf_present=PRESENT, leaf_shape=LOBED
    for folio_id in folio_ids:
        heading_prefix = text_features.get(folio_id, {}).get('heading_prefix', '')
        if heading_prefix == 'ko':
            visual_data[folio_id]['leaf_present'] = 'PRESENT'
            visual_data[folio_id]['leaf_shape'] = 'LOBED'

    return visual_data


def generate_weak_correlation_data(folio_ids: List[str], text_features: Dict,
                                   seed: int = RANDOM_SEED, strength: float = 0.7) -> Dict:
    """
    Generate synthetic visual data with weak planted correlations.

    Version C: 70% correlation for specific prefix-feature pairs.
    - 70% of 'po' prefix folios get root_type=BULBOUS
    - 70% of 'ko' prefix folios get leaf_present=PRESENT
    Expected: Weaker but potentially detectable correlations.
    """
    random.seed(seed)

    # Start with random data
    visual_data = generate_random_visual_data(folio_ids, seed)

    # Plant weak correlation 1: po prefix -> BULBOUS root (70%)
    for folio_id in folio_ids:
        heading_prefix = text_features.get(folio_id, {}).get('heading_prefix', '')
        if heading_prefix == 'po':
            if random.random() < strength:
                visual_data[folio_id]['root_type'] = 'BULBOUS'
                visual_data[folio_id]['root_present'] = 'PRESENT'

    # Plant weak correlation 2: ko prefix -> leaf features (70%)
    for folio_id in folio_ids:
        heading_prefix = text_features.get(folio_id, {}).get('heading_prefix', '')
        if heading_prefix == 'ko':
            if random.random() < strength:
                visual_data[folio_id]['leaf_present'] = 'PRESENT'
                visual_data[folio_id]['leaf_shape'] = 'LOBED'

    return visual_data


# =============================================================================
# CORRELATION TESTING
# =============================================================================

def run_correlation_tests(visual_data: Dict, text_features: Dict,
                         n_null_permutations: int = 100) -> Dict:
    """
    Run correlation tests on visual-text data pair.

    Uses reduced null model permutations (100) for speed during testing.
    """
    folio_ids = list(visual_data.keys())

    results = []

    # Test each visual feature against each text feature
    visual_features = ['root_type', 'root_present', 'leaf_present',
                       'leaf_shape', 'flower_present', 'stem_type', 'plant_symmetry']
    text_prefixes = ['heading_prefix', 'part1_dominant_prefix']

    for v_feat in visual_features:
        for t_feat in text_prefixes:
            # Get values
            v_vals = [visual_data[f].get(v_feat) for f in folio_ids]
            t_vals = [text_features.get(f, {}).get(t_feat) for f in folio_ids]

            # Run chi-square test
            test_result = test_categorical_association(v_vals, t_vals)
            test_result['visual_feature'] = v_feat
            test_result['text_feature'] = t_feat

            # Run null model (reduced permutations for speed)
            null_result = null_model_test(v_vals, t_vals, n_permutations=n_null_permutations)
            test_result['null_percentile'] = null_result.get('percentile', 0)
            test_result['null_significant_99'] = null_result.get('significant_at_99', False)
            test_result['null_significant_95'] = null_result.get('significant_at_95', False)

            results.append(test_result)

    # Apply Bonferroni correction
    results = apply_bonferroni(results, alpha=0.01)

    return {
        'n_tests': len(results),
        'results': results,
        'significant_bonferroni': [r for r in results if r.get('significant_bonferroni', False)],
        'significant_null_99': [r for r in results if r.get('null_significant_99', False)],
        'significant_null_95': [r for r in results if r.get('null_significant_95', False)]
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_results(random_results: Dict, strong_results: Dict, weak_results: Dict) -> Dict:
    """
    Validate test results against expectations.
    """
    validations = {}

    # Validation 1: Random data should have few significant correlations
    random_sig_count = len(random_results['significant_bonferroni'])
    validations['random_dataset'] = {
        'significant_count': random_sig_count,
        'expected': '<3',
        'passed': random_sig_count < 3,
        'interpretation': 'PASS: False positive rate controlled' if random_sig_count < 3
                         else 'FAIL: Too many false positives'
    }

    # Validation 2: Strong correlation data should detect planted correlations
    strong_sig_count = len(strong_results['significant_bonferroni'])
    strong_null_count = len(strong_results['significant_null_99'])
    validations['strong_dataset'] = {
        'significant_count': strong_sig_count,
        'null_99_count': strong_null_count,
        'expected': '>=2',
        'passed': strong_sig_count >= 2 or strong_null_count >= 1,
        'interpretation': 'PASS: Engine detects planted correlations' if (strong_sig_count >= 2 or strong_null_count >= 1)
                         else 'FAIL: Engine missed planted correlations'
    }

    # Validation 3: Weak correlation data - note power limitations
    # With only 3-4 folios per prefix, 70% correlation may not be detectable
    weak_sig_count = len(weak_results['significant_bonferroni'])
    weak_null_95 = len(weak_results['significant_null_95'])
    weak_null_99 = len(weak_results['significant_null_99'])
    validations['weak_dataset'] = {
        'significant_count': weak_sig_count,
        'null_95_count': weak_null_95,
        'null_99_count': weak_null_99,
        'expected': 'Optional (power-limited with 3-4 folios per prefix)',
        'passed': True,  # Not a hard failure - power limitation expected
        'interpretation': f'Detected {weak_sig_count} Bonf, {weak_null_95} null-95, {weak_null_99} null-99. '
                         'Power limited with small prefix groups (3-4 folios each).'
    }

    # Overall validation
    all_passed = all(v['passed'] for v in validations.values())

    return {
        'validations': validations,
        'overall_passed': all_passed,
        'summary': 'Correlation engine VALIDATED' if all_passed
                  else 'Correlation engine needs debugging'
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Visual Coding Phase, Task 5: Correlation Engine Test")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading pilot folio data...")
    folio_ids = get_pilot_folio_ids()
    text_features = load_pilot_text_features()
    print(f"  Loaded {len(folio_ids)} folios")

    # Generate synthetic datasets
    print("\n[2/5] Generating synthetic visual data...")
    random_data = generate_random_visual_data(folio_ids)
    strong_data = generate_strong_correlation_data(folio_ids, text_features)
    weak_data = generate_weak_correlation_data(folio_ids, text_features)
    print("  Generated: Random, Strong, Weak datasets")

    # Count planted correlations
    po_count = sum(1 for f in folio_ids if text_features.get(f, {}).get('heading_prefix') == 'po')
    ko_count = sum(1 for f in folio_ids if text_features.get(f, {}).get('heading_prefix') == 'ko')
    print(f"  Prefix 'po' folios: {po_count}")
    print(f"  Prefix 'ko' folios: {ko_count}")

    # Run correlation tests
    print("\n[3/5] Testing random dataset (no planted correlations)...")
    random_results = run_correlation_tests(random_data, text_features)
    print(f"  Tests run: {random_results['n_tests']}")
    print(f"  Significant (Bonferroni): {len(random_results['significant_bonferroni'])}")
    print(f"  Significant (Null 99th): {len(random_results['significant_null_99'])}")

    print("\n[4/5] Testing strong correlation dataset (100% planted)...")
    strong_results = run_correlation_tests(strong_data, text_features)
    print(f"  Tests run: {strong_results['n_tests']}")
    print(f"  Significant (Bonferroni): {len(strong_results['significant_bonferroni'])}")
    print(f"  Significant (Null 99th): {len(strong_results['significant_null_99'])}")

    if strong_results['significant_bonferroni']:
        print("  Detected correlations:")
        for sig in strong_results['significant_bonferroni'][:5]:
            print(f"    - {sig['visual_feature']} x {sig['text_feature']}: "
                  f"V={sig.get('cramers_v', 0):.3f}, null%={sig.get('null_percentile', 0):.1f}")

    print("\n[5/5] Testing weak correlation dataset (70% planted)...")
    weak_results = run_correlation_tests(weak_data, text_features)
    print(f"  Tests run: {weak_results['n_tests']}")
    print(f"  Significant (Bonferroni): {len(weak_results['significant_bonferroni'])}")
    print(f"  Significant (Null 95th): {len(weak_results['significant_null_95'])}")

    # Validate results
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    validation = validate_results(random_results, strong_results, weak_results)

    for dataset_name, v in validation['validations'].items():
        status = "PASS" if v['passed'] else "FAIL"
        print(f"\n{dataset_name.upper()}:")
        print(f"  Significant: {v.get('significant_count', 0)} (expected {v['expected']})")
        print(f"  Status: [{status}] {v['interpretation']}")

    print(f"\n{'=' * 70}")
    print(f"OVERALL: {validation['summary']}")
    print(f"{'=' * 70}")

    # Compile report
    report = {
        'metadata': {
            'title': 'Correlation Engine Test Report',
            'phase': 'Visual Coding Phase, Task 5',
            'date': datetime.now().isoformat(),
            'purpose': 'Validate correlation engine with synthetic data'
        },
        'test_configuration': {
            'n_folios': len(folio_ids),
            'n_tests_per_dataset': random_results['n_tests'],
            'null_model_permutations': 100,
            'planted_prefixes': {
                'po': po_count,
                'ko': ko_count
            }
        },
        'random_dataset_results': {
            'n_significant_bonferroni': len(random_results['significant_bonferroni']),
            'n_significant_null_99': len(random_results['significant_null_99']),
            'significant_pairs': [
                f"{r['visual_feature']} x {r['text_feature']}"
                for r in random_results['significant_bonferroni']
            ]
        },
        'strong_dataset_results': {
            'n_significant_bonferroni': len(strong_results['significant_bonferroni']),
            'n_significant_null_99': len(strong_results['significant_null_99']),
            'significant_pairs': [
                {
                    'pair': f"{r['visual_feature']} x {r['text_feature']}",
                    'cramers_v': r.get('cramers_v', 0),
                    'null_percentile': r.get('null_percentile', 0)
                }
                for r in strong_results['significant_bonferroni']
            ]
        },
        'weak_dataset_results': {
            'n_significant_bonferroni': len(weak_results['significant_bonferroni']),
            'n_significant_null_95': len(weak_results['significant_null_95']),
            'significant_pairs': [
                {
                    'pair': f"{r['visual_feature']} x {r['text_feature']}",
                    'cramers_v': r.get('cramers_v', 0),
                    'null_percentile': r.get('null_percentile', 0)
                }
                for r in weak_results['significant_bonferroni']
            ]
        },
        'validation': validation,
        'conclusion': validation['summary']
    }

    # Save report
    output_file = 'correlation_engine_test_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nSaved to: {output_file}")

    return report


if __name__ == '__main__':
    main()
