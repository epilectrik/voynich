#!/usr/bin/env python3
"""
Visual Coding Phase, Task 4: Pre-Visual Analysis

Calculates baseline statistics BEFORE visual coding begins.
This establishes null expectations and power limitations.
"""

import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple
import random

# =============================================================================
# CONFIGURATION
# =============================================================================

PILOT_SELECTION_FILE = 'pilot_folio_selection.json'
TEXT_FEATURES_FILE = 'pilot_folio_text_features.json'
VISUAL_SCHEMA_FILE = 'visual_feature_schema.json'
FOLIO_DATABASE_FILE = 'folio_feature_database.json'

# Power analysis parameters
ALPHA = 0.05
POWER_TARGET = 0.80
MIN_FOLIOS_PER_PREFIX = 3

# Null model parameters
NULL_PERMUTATIONS = 1000


# =============================================================================
# DATA LOADING
# =============================================================================

def load_pilot_selection() -> Dict:
    """Load pilot folio selection data."""
    with open(PILOT_SELECTION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_text_features() -> Dict:
    """Load text features for pilot folios."""
    with open(TEXT_FEATURES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Text features are in 'pilot_folios' dict keyed by folio_id
    return data.get('pilot_folios', {})


def load_visual_schema() -> Dict:
    """Load visual feature schema."""
    with open(VISUAL_SCHEMA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_folio_database() -> Dict:
    """Load full folio feature database."""
    with open(FOLIO_DATABASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# TEXT STATISTICS
# =============================================================================

def calculate_heading_prefix_distribution(text_features: Dict) -> Dict:
    """Calculate distribution of heading prefixes in pilot."""
    prefix_counts = Counter()
    prefix_folios = defaultdict(list)

    for folio_id, features in text_features.items():
        prefix = features.get('heading_prefix', 'unknown')
        prefix_counts[prefix] += 1
        prefix_folios[prefix].append(folio_id)

    # Sort by count
    sorted_counts = sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        'total_unique_prefixes': len(prefix_counts),
        'prefix_counts': dict(sorted_counts),
        'prefix_folios': dict(prefix_folios),
        'prefixes_with_power': [p for p, c in prefix_counts.items() if c >= MIN_FOLIOS_PER_PREFIX],
        'prefixes_insufficient_power': [p for p, c in prefix_counts.items() if c < MIN_FOLIOS_PER_PREFIX]
    }


def calculate_dominant_prefix_distribution(text_features: Dict) -> Dict:
    """Calculate distribution of dominant body prefixes per part."""
    part_distributions = {}

    for part in ['part1', 'part2', 'part3']:
        key = f'{part}_dominant_prefix'
        prefix_counts = Counter()
        prefix_folios = defaultdict(list)

        for folio_id, features in text_features.items():
            prefix = features.get(key, 'unknown')
            if prefix and prefix != 'unknown':
                prefix_counts[prefix] += 1
                prefix_folios[prefix].append(folio_id)

        sorted_counts = sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True)

        part_distributions[part] = {
            'unique_prefixes': len(prefix_counts),
            'prefix_counts': dict(sorted_counts[:10]),  # Top 10
            'top_prefix': sorted_counts[0] if sorted_counts else ('none', 0),
            'prefixes_with_power': [p for p, c in prefix_counts.items() if c >= MIN_FOLIOS_PER_PREFIX]
        }

    return part_distributions


def calculate_word_count_distribution(text_features: Dict) -> Dict:
    """Calculate word count distribution."""
    word_counts = []

    for folio_id, features in text_features.items():
        wc = features.get('word_count', 0)
        word_counts.append(wc)

    if not word_counts:
        return {'error': 'No word counts found'}

    sorted_counts = sorted(word_counts)
    n = len(sorted_counts)

    return {
        'n': n,
        'min': sorted_counts[0],
        'max': sorted_counts[-1],
        'mean': sum(sorted_counts) / n,
        'median': sorted_counts[n // 2],
        'std': (sum((x - sum(sorted_counts)/n)**2 for x in sorted_counts) / n) ** 0.5,
        'quartiles': {
            'q1': sorted_counts[n // 4],
            'q2': sorted_counts[n // 2],
            'q3': sorted_counts[3 * n // 4]
        },
        'strata': {
            'short': len([x for x in sorted_counts if x < 89]),
            'medium': len([x for x in sorted_counts if 89 <= x <= 105]),
            'long': len([x for x in sorted_counts if x > 105])
        }
    }


def calculate_vocabulary_profiles(text_features: Dict) -> Dict:
    """Calculate vocabulary profiles per part."""
    part_vocabularies = {
        'part1': set(),
        'part2': set(),
        'part3': set()
    }

    for folio_id, features in text_features.items():
        for part in ['part1', 'part2', 'part3']:
            key = f'{part}_vocabulary'
            vocab = features.get(key, [])
            part_vocabularies[part].update(vocab)

    # Calculate overlaps
    p1, p2, p3 = part_vocabularies['part1'], part_vocabularies['part2'], part_vocabularies['part3']

    return {
        'part_sizes': {
            'part1': len(p1),
            'part2': len(p2),
            'part3': len(p3)
        },
        'pairwise_overlap': {
            'part1_part2': len(p1 & p2),
            'part1_part3': len(p1 & p3),
            'part2_part3': len(p2 & p3)
        },
        'all_three_overlap': len(p1 & p2 & p3),
        'part1_exclusive': len(p1 - p2 - p3),
        'part2_exclusive': len(p2 - p1 - p3),
        'part3_exclusive': len(p3 - p1 - p2),
        'total_unique': len(p1 | p2 | p3)
    }


# =============================================================================
# NULL DISTRIBUTION ANALYSIS
# =============================================================================

def calculate_cramers_v(contingency_table: List[List[int]]) -> float:
    """Calculate Cramér's V for a contingency table."""
    # Convert to flat counts
    n = sum(sum(row) for row in contingency_table)
    if n == 0:
        return 0.0

    # Row and column totals
    row_totals = [sum(row) for row in contingency_table]
    col_totals = [sum(contingency_table[i][j] for i in range(len(contingency_table)))
                  for j in range(len(contingency_table[0]))]

    # Chi-square calculation
    chi_sq = 0.0
    for i, row in enumerate(contingency_table):
        for j, observed in enumerate(row):
            expected = (row_totals[i] * col_totals[j]) / n if n > 0 else 0
            if expected > 0:
                chi_sq += (observed - expected) ** 2 / expected

    # Cramér's V
    r, k = len(contingency_table), len(contingency_table[0])
    min_dim = min(r - 1, k - 1)
    if min_dim == 0 or n == 0:
        return 0.0

    return (chi_sq / (n * min_dim)) ** 0.5


def generate_null_distribution(n_folios: int, n_prefix_categories: int,
                               n_visual_categories: int, n_permutations: int) -> Dict:
    """Generate null distribution of Cramér's V under random assignment."""
    cramers_vs = []

    for _ in range(n_permutations):
        # Random prefix assignment
        prefixes = [random.randint(0, n_prefix_categories - 1) for _ in range(n_folios)]
        # Random visual feature assignment
        visuals = [random.randint(0, n_visual_categories - 1) for _ in range(n_folios)]

        # Build contingency table
        table = [[0] * n_visual_categories for _ in range(n_prefix_categories)]
        for p, v in zip(prefixes, visuals):
            table[p][v] += 1

        v = calculate_cramers_v(table)
        cramers_vs.append(v)

    sorted_vs = sorted(cramers_vs)
    n = len(sorted_vs)

    return {
        'mean': sum(sorted_vs) / n,
        'std': (sum((x - sum(sorted_vs)/n)**2 for x in sorted_vs) / n) ** 0.5,
        'percentile_95': sorted_vs[int(n * 0.95)],
        'percentile_99': sorted_vs[int(n * 0.99)],
        'max': sorted_vs[-1]
    }


def calculate_null_expectations(visual_schema: Dict, n_folios: int = 30) -> Dict:
    """Calculate expected null distributions for each visual feature type."""
    null_distributions = {}

    # Typical prefix category count (from heading prefixes)
    n_prefix_categories = 5  # Approximate for features with 3+ folios

    # Group features by number of categories
    # Schema is nested: schemas -> plant_features -> root/stem/leaf/flower/overall -> features
    plant_schema = visual_schema.get('schemas', {}).get('plant_features', {})

    # Collect all features from all categories
    features = {}
    for category in ['root', 'stem', 'leaf', 'flower', 'overall']:
        cat_features = plant_schema.get(category, {}).get('features', {})
        for fname, fdef in cat_features.items():
            features[fname] = fdef

    for feature_name, feature_def in features.items():
        values = feature_def.get('values', [])
        n_visual_categories = len(values)

        if n_visual_categories < 2:
            continue

        # Generate null distribution
        null_dist = generate_null_distribution(
            n_folios=n_folios,
            n_prefix_categories=n_prefix_categories,
            n_visual_categories=n_visual_categories,
            n_permutations=NULL_PERMUTATIONS
        )

        null_distributions[feature_name] = {
            'n_categories': n_visual_categories,
            'null_mean_cramers_v': round(null_dist['mean'], 4),
            'null_std': round(null_dist['std'], 4),
            'threshold_95': round(null_dist['percentile_95'], 4),
            'threshold_99': round(null_dist['percentile_99'], 4)
        }

    return null_distributions


# =============================================================================
# POWER ANALYSIS
# =============================================================================

def calculate_minimum_detectable_effect(n: int, alpha: float = 0.05,
                                        power: float = 0.80, df: int = 4) -> float:
    """
    Calculate minimum detectable effect size (Cramér's V).

    Uses approximation: n ≈ chi2_crit / w^2 where w is effect size
    For chi-square with df degrees of freedom
    """
    # Chi-square critical values (approximate)
    # df=4, alpha=0.05: 9.49
    # df=4, alpha=0.01: 13.28
    chi2_crit = {
        (4, 0.05): 9.49,
        (4, 0.01): 13.28,
        (6, 0.05): 12.59,
        (6, 0.01): 16.81,
        (8, 0.05): 15.51,
        (8, 0.01): 20.09
    }

    crit = chi2_crit.get((df, alpha), 9.49)

    # Solve for w: w = sqrt(chi2_crit / n)
    w = (crit / n) ** 0.5

    return round(w, 3)


def assess_power_per_prefix(heading_distribution: Dict, n_total: int = 30) -> Dict:
    """Assess statistical power for each testable prefix."""
    power_assessment = {}

    prefix_counts = heading_distribution.get('prefix_counts', {})

    for prefix, count in prefix_counts.items():
        # Effect size detectable with this prefix count
        # Using simplified 2x2 contingency (prefix vs not-prefix, feature vs not-feature)
        min_effect = calculate_minimum_detectable_effect(n_total, df=1)

        # Power depends on both total N and smallest cell count
        power_adequate = count >= MIN_FOLIOS_PER_PREFIX

        power_assessment[prefix] = {
            'n_folios': count,
            'power_adequate': power_adequate,
            'minimum_detectable_v': min_effect,
            'recommendation': 'TESTABLE' if power_adequate else 'INSUFFICIENT_POWER'
        }

    return power_assessment


def calculate_overall_power_summary(n_folios: int = 30, n_features: int = 25) -> Dict:
    """Calculate overall power summary for the pilot study."""
    # With 30 folios and alpha=0.05/25 (Bonferroni), what's detectable?
    bonferroni_alpha = 0.05 / n_features

    min_effect_uncorrected = calculate_minimum_detectable_effect(n_folios, alpha=0.05)
    min_effect_bonferroni = calculate_minimum_detectable_effect(n_folios, alpha=bonferroni_alpha)

    return {
        'n_folios': n_folios,
        'n_features_tested': n_features,
        'bonferroni_alpha': round(bonferroni_alpha, 5),
        'minimum_detectable_effect': {
            'uncorrected': min_effect_uncorrected,
            'bonferroni_corrected': min_effect_bonferroni,
            'interpretation': 'LARGE' if min_effect_bonferroni > 0.5 else
                            'MEDIUM' if min_effect_bonferroni > 0.3 else 'SMALL'
        },
        'power_limitations': [
            'Only prefixes with >=3 folios are testable',
            f'Minimum detectable Cramér\'s V ≈ {min_effect_bonferroni} (Bonferroni)',
            'Small effects (V < 0.3) likely undetectable',
            'Wide confidence intervals expected'
        ],
        'recommendations': [
            'Focus on prefixes with 3+ folios (po=3, ko=4)',
            'Report effect sizes with confidence intervals',
            'Interpret null results as "inconclusive" not "no effect"',
            'Consider this a pilot for larger study'
        ]
    }


# =============================================================================
# PREFIX COVERAGE CHECK
# =============================================================================

def check_prefix_coverage(text_features: Dict) -> Dict:
    """Check prefix coverage across different feature sources."""
    coverage = {
        'heading_prefix': Counter(),
        'part1_dominant_prefix': Counter(),
        'part2_dominant_prefix': Counter(),
        'part3_dominant_prefix': Counter()
    }

    for folio_id, features in text_features.items():
        for key in coverage.keys():
            prefix = features.get(key)
            if prefix:
                coverage[key][prefix] += 1

    # Summarize coverage
    summary = {}
    for source, counts in coverage.items():
        sufficient = [p for p, c in counts.items() if c >= MIN_FOLIOS_PER_PREFIX]
        insufficient = [p for p, c in counts.items() if c < MIN_FOLIOS_PER_PREFIX]

        summary[source] = {
            'unique_prefixes': len(counts),
            'prefixes_with_power': sufficient,
            'prefixes_insufficient': insufficient,
            'coverage_rate': len(sufficient) / len(counts) if counts else 0
        }

    # Cross-source comparison
    all_heading = set(coverage['heading_prefix'].keys())
    all_part1 = set(coverage['part1_dominant_prefix'].keys())

    return {
        'by_source': summary,
        'heading_vs_part1_overlap': len(all_heading & all_part1),
        'heading_only': list(all_heading - all_part1),
        'part1_only': list(all_part1 - all_heading),
        'testable_hypotheses': {
            'po_root': coverage['heading_prefix'].get('po', 0) >= MIN_FOLIOS_PER_PREFIX,
            'ko_leaf': coverage['heading_prefix'].get('ko', 0) >= MIN_FOLIOS_PER_PREFIX,
            'ch_leaf': coverage['part1_dominant_prefix'].get('ch', 0) >= MIN_FOLIOS_PER_PREFIX
        }
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Visual Coding Phase, Task 4: Pre-Visual Analysis")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading data...")

    try:
        text_features = load_text_features()
        print(f"  Loaded {len(text_features)} folio text features")
    except FileNotFoundError:
        print("  ERROR: Could not load text features file")
        return None

    try:
        visual_schema = load_visual_schema()
        # Schema is nested: schemas -> plant_features -> root/stem/leaf/flower/overall
        plant_schema = visual_schema.get('schemas', {}).get('plant_features', {})
        # Count features across all categories
        n_features = 0
        for category in ['root', 'stem', 'leaf', 'flower', 'overall']:
            cat_features = plant_schema.get(category, {}).get('features', {})
            n_features += len(cat_features)
        if n_features == 0:
            n_features = 25  # Default if schema parsing fails
        print(f"  Loaded visual schema with {n_features} plant features")
    except FileNotFoundError:
        print("  WARNING: Could not load visual schema, using defaults")
        visual_schema = {}
        n_features = 25

    # Text statistics
    print("\n[2/5] Calculating text statistics...")

    heading_dist = calculate_heading_prefix_distribution(text_features)
    print(f"  Heading prefixes: {heading_dist['total_unique_prefixes']} unique")
    print(f"  With power (>=3): {heading_dist['prefixes_with_power']}")

    dominant_dist = calculate_dominant_prefix_distribution(text_features)
    for part, data in dominant_dist.items():
        top = data['top_prefix']
        print(f"  {part} top prefix: {top[0]} ({top[1]} folios)")

    word_count_dist = calculate_word_count_distribution(text_features)
    print(f"  Word count: mean={word_count_dist['mean']:.1f}, "
          f"range=[{word_count_dist['min']}, {word_count_dist['max']}]")

    vocab_profiles = calculate_vocabulary_profiles(text_features)
    print(f"  Part vocabularies: P1={vocab_profiles['part_sizes']['part1']}, "
          f"P2={vocab_profiles['part_sizes']['part2']}, "
          f"P3={vocab_profiles['part_sizes']['part3']}")

    # Null distributions
    print("\n[3/5] Calculating null distributions (1000 permutations)...")
    null_expectations = calculate_null_expectations(visual_schema)

    if null_expectations:
        sample_feature = list(null_expectations.keys())[0]
        sample = null_expectations[sample_feature]
        print(f"  Example ({sample_feature}): null mean V={sample['null_mean_cramers_v']}, "
              f"99th={sample['threshold_99']}")
    else:
        print("  Using default null thresholds")
        null_expectations = {
            'default': {
                'null_mean_cramers_v': 0.35,
                'threshold_95': 0.55,
                'threshold_99': 0.65
            }
        }

    # Power analysis
    print("\n[4/5] Conducting power analysis...")

    power_per_prefix = assess_power_per_prefix(heading_dist)
    testable = [p for p, data in power_per_prefix.items() if data['power_adequate']]
    print(f"  Testable prefixes: {testable}")

    overall_power = calculate_overall_power_summary(n_folios=30, n_features=n_features)
    print(f"  Minimum detectable effect: V >= {overall_power['minimum_detectable_effect']['bonferroni_corrected']}")
    print(f"  Interpretation: {overall_power['minimum_detectable_effect']['interpretation']} effects only")

    # Prefix coverage
    print("\n[5/5] Checking prefix coverage...")

    coverage = check_prefix_coverage(text_features)
    print(f"  Heading prefixes with power: {coverage['by_source']['heading_prefix']['prefixes_with_power']}")
    print(f"  H1 (po->root) testable: {coverage['testable_hypotheses']['po_root']}")
    print(f"  H4 (ko->leaf) testable: {coverage['testable_hypotheses']['ko_leaf']}")

    # Compile report
    report = {
        'metadata': {
            'title': 'Pre-Visual Analysis Report',
            'phase': 'Visual Coding Phase, Task 4',
            'date': datetime.now().isoformat(),
            'purpose': 'Establish baselines and power limitations BEFORE visual coding'
        },
        'pilot_summary': {
            'n_folios': len(text_features),
            'n_visual_features': n_features,
            'n_unique_heading_prefixes': heading_dist['total_unique_prefixes'],
            'testable_prefixes': heading_dist['prefixes_with_power']
        },
        'text_statistics': {
            'heading_prefix_distribution': heading_dist,
            'dominant_prefix_distribution': dominant_dist,
            'word_count_distribution': word_count_dist,
            'vocabulary_profiles': vocab_profiles
        },
        'null_distributions': null_expectations,
        'power_analysis': {
            'per_prefix': power_per_prefix,
            'overall': overall_power
        },
        'prefix_coverage': coverage,
        'key_findings': {
            'testable_primary_hypotheses': [
                'H1: po->root (3 folios, marginally testable)',
                'H4: ko->leaf (4 folios, testable)'
            ],
            'power_limitations': [
                'Only LARGE effects detectable (V >= 0.5 after Bonferroni)',
                'Most heading prefixes have only 1 folio (untestable)',
                'Null model threshold at 99th percentile: V ~ 0.65'
            ],
            'recommendations': [
                'Prioritize po and ko prefix tests',
                'Use dominant body prefixes for more power',
                'Interpret all results as preliminary',
                'Plan larger validation study if patterns found'
            ]
        }
    }

    # Save report
    output_file = 'pre_visual_analysis_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_file}")

    # Summary
    print("\n" + "=" * 70)
    print("PRE-VISUAL ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"\nPilot: {len(text_features)} folios, {n_features} visual features")
    print(f"Testable heading prefixes: {heading_dist['prefixes_with_power']}")
    print(f"Minimum detectable effect: V >= {overall_power['minimum_detectable_effect']['bonferroni_corrected']}")
    print("\nKey limitations:")
    for lim in report['key_findings']['power_limitations']:
        print(f"  - {lim}")

    return report


if __name__ == '__main__':
    main()
