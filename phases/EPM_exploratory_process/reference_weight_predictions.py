#!/usr/bin/env python3
"""
Data Recovery Phase, Task 2: Reference-Weighted Predictions

Stratifies A entries by B reference count and generates testable predictions.
Tests text-based predictions immediately; locks visual predictions for later.

Hypothesis: Highly-referenced A entries represent more foundational entities.
"""

import json
import csv
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Tuple
import statistics

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'pa', 'py', 'ky', 'ty', 'fa', 'fs', 'ks', 'r*'
]


# =============================================================================
# DATA LOADING
# =============================================================================

def load_reference_graph() -> Dict:
    """Load reference graph analysis results."""
    with open('reference_graph_analysis_report.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_folio_database() -> Dict:
    """Load folio feature database."""
    with open('folio_feature_database.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_heading_analysis() -> Dict:
    """Load heading phonetic analysis."""
    with open('heading_phonetic_analysis_report.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_corpus() -> List[Dict]:
    """Load the full corpus."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to H (PRIMARY) transcriber only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier
                })

    return words


# =============================================================================
# STRATIFICATION
# =============================================================================

def stratify_by_reference_count(graph_data: Dict, db: Dict) -> Dict[str, List[str]]:
    """
    Stratify A entries into reference count groups.

    Groups:
    - high_reference: top quartile by B in-degree
    - medium_reference: middle 50%
    - low_reference: bottom quartile + isolates
    """
    # Build in-degree mapping for all A entries
    a_folios = list(db.get('currier_a', {}).keys())

    # Get in-degrees from graph data
    in_degrees = {}
    most_referenced = graph_data.get('graph_statistics', {}).get('most_referenced_a', [])
    for entry in most_referenced:
        in_degrees[entry['folio']] = entry['in_degree']

    # All other A entries have 0 in-degree (isolated)
    for folio in a_folios:
        if folio not in in_degrees:
            in_degrees[folio] = 0

    # Sort by in-degree
    sorted_entries = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
    n = len(sorted_entries)

    # Quartile boundaries
    q1_idx = n // 4
    q3_idx = 3 * n // 4

    strata = {
        'high_reference': [],
        'medium_reference': [],
        'low_reference': []
    }

    for i, (folio, degree) in enumerate(sorted_entries):
        if i < q1_idx:
            strata['high_reference'].append(folio)
        elif i < q3_idx:
            strata['medium_reference'].append(folio)
        else:
            strata['low_reference'].append(folio)

    return strata, in_degrees


def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) >= length and word[:length] in KNOWN_PREFIXES:
            return word[:length]
    return word[:2] if len(word) >= 2 else word


# =============================================================================
# TEXT-BASED TESTS
# =============================================================================

def test_word_count_by_stratum(strata: Dict, db: Dict) -> Dict:
    """Test: Do high-reference entries have shorter word counts?"""
    results = {}

    for stratum, folios in strata.items():
        word_counts = []
        for folio in folios:
            entry = db.get('currier_a', {}).get(folio, {})
            text_features = entry.get('text_features', {})
            wc = text_features.get('word_count', 0)
            if wc > 0:
                word_counts.append(wc)

        if word_counts:
            results[stratum] = {
                'n': len(word_counts),
                'mean': round(statistics.mean(word_counts), 1),
                'std': round(statistics.stdev(word_counts), 1) if len(word_counts) > 1 else 0,
                'median': round(statistics.median(word_counts), 1),
                'min': min(word_counts),
                'max': max(word_counts)
            }

    # Calculate effect
    if results.get('high_reference') and results.get('low_reference'):
        high_mean = results['high_reference']['mean']
        low_mean = results['low_reference']['mean']
        effect = 'HIGH_SHORTER' if high_mean < low_mean else 'HIGH_LONGER'
        difference = round(high_mean - low_mean, 1)
    else:
        effect = 'INSUFFICIENT_DATA'
        difference = None

    return {
        'test': 'word_count_by_stratum',
        'hypothesis': 'High-reference entries have shorter word counts',
        'results_by_stratum': results,
        'effect': effect,
        'difference': difference,
        'prediction_supported': effect == 'HIGH_SHORTER'
    }


def test_prefix_commonality(strata: Dict, corpus: List[Dict], db: Dict) -> Dict:
    """Test: Do high-reference entries have more common prefixes?"""
    # Get overall prefix frequency from corpus
    a_words = [w for w in corpus if w['currier'] == 'A']
    all_prefixes = [get_prefix(w['word']) for w in a_words]
    prefix_freq = Counter(all_prefixes)
    total_words = len(all_prefixes)

    # Calculate commonality score for each stratum
    results = {}

    for stratum, folios in strata.items():
        stratum_prefixes = []
        for folio in folios:
            entry = db.get('currier_a', {}).get(folio, {})
            text_features = entry.get('text_features', {})
            opening_prefix = text_features.get('opening_prefix', '')
            if opening_prefix:
                stratum_prefixes.append(opening_prefix)

        if stratum_prefixes:
            # Calculate average frequency of prefixes used
            freq_scores = []
            for p in stratum_prefixes:
                freq_rate = prefix_freq.get(p, 0) / total_words if total_words > 0 else 0
                freq_scores.append(freq_rate)

            results[stratum] = {
                'n': len(stratum_prefixes),
                'mean_commonality': round(statistics.mean(freq_scores), 4),
                'top_prefixes': [p for p, _ in Counter(stratum_prefixes).most_common(5)]
            }

    # Calculate effect
    if results.get('high_reference') and results.get('low_reference'):
        high_comm = results['high_reference']['mean_commonality']
        low_comm = results['low_reference']['mean_commonality']
        effect = 'HIGH_MORE_COMMON' if high_comm > low_comm else 'HIGH_LESS_COMMON'
        ratio = round(high_comm / low_comm, 2) if low_comm > 0 else None
    else:
        effect = 'INSUFFICIENT_DATA'
        ratio = None

    return {
        'test': 'prefix_commonality_by_stratum',
        'hypothesis': 'High-reference entries have more common prefixes',
        'results_by_stratum': results,
        'effect': effect,
        'ratio': ratio,
        'prediction_supported': effect == 'HIGH_MORE_COMMON'
    }


def test_heading_length(strata: Dict, heading_data: Dict, db: Dict) -> Dict:
    """Test: Do high-reference headings differ in length?"""
    results = {}

    for stratum, folios in strata.items():
        heading_lengths = []
        for folio in folios:
            entry = db.get('currier_a', {}).get(folio, {})
            text_features = entry.get('text_features', {})
            opening_word = text_features.get('opening_word', '')
            if opening_word and len(opening_word) >= 2:
                heading_lengths.append(len(opening_word))

        if heading_lengths:
            results[stratum] = {
                'n': len(heading_lengths),
                'mean': round(statistics.mean(heading_lengths), 2),
                'std': round(statistics.stdev(heading_lengths), 2) if len(heading_lengths) > 1 else 0,
                'median': round(statistics.median(heading_lengths), 1)
            }

    # Compare high vs low
    if results.get('high_reference') and results.get('low_reference'):
        high_mean = results['high_reference']['mean']
        low_mean = results['low_reference']['mean']
        effect = 'HIGH_SHORTER_HEADINGS' if high_mean < low_mean else 'HIGH_LONGER_HEADINGS'
        difference = round(high_mean - low_mean, 2)
    else:
        effect = 'INSUFFICIENT_DATA'
        difference = None

    return {
        'test': 'heading_length_by_stratum',
        'hypothesis': 'High-reference entries may have different heading lengths',
        'results_by_stratum': results,
        'effect': effect,
        'difference': difference,
        'interpretation': 'Shorter headings might indicate simpler/foundational entities'
    }


def test_vocabulary_richness(strata: Dict, db: Dict) -> Dict:
    """Test: Do high-reference entries have simpler vocabulary (fewer unique words)?"""
    results = {}

    for stratum, folios in strata.items():
        richness_scores = []
        for folio in folios:
            entry = db.get('currier_a', {}).get(folio, {})
            text_features = entry.get('text_features', {})
            richness = text_features.get('vocabulary_richness', 0)
            if richness > 0:
                richness_scores.append(richness)

        if richness_scores:
            results[stratum] = {
                'n': len(richness_scores),
                'mean': round(statistics.mean(richness_scores), 4),
                'std': round(statistics.stdev(richness_scores), 4) if len(richness_scores) > 1 else 0
            }

    # Compare
    if results.get('high_reference') and results.get('low_reference'):
        high_mean = results['high_reference']['mean']
        low_mean = results['low_reference']['mean']
        effect = 'HIGH_LOWER_RICHNESS' if high_mean < low_mean else 'HIGH_HIGHER_RICHNESS'
        difference = round(high_mean - low_mean, 4)
    else:
        effect = 'INSUFFICIENT_DATA'
        difference = None

    return {
        'test': 'vocabulary_richness_by_stratum',
        'hypothesis': 'High-reference entries have simpler vocabulary (lower richness)',
        'results_by_stratum': results,
        'effect': effect,
        'difference': difference,
        'prediction_supported': effect == 'HIGH_LOWER_RICHNESS'
    }


def test_b_discussion_breadth(strata: Dict, in_degrees: Dict, graph_data: Dict) -> Dict:
    """Test: Are highly-referenced entities discussed in more B contexts?"""
    results = {}

    for stratum, folios in strata.items():
        degrees = [in_degrees.get(f, 0) for f in folios]
        nonzero_degrees = [d for d in degrees if d > 0]

        results[stratum] = {
            'n': len(folios),
            'referenced_count': len(nonzero_degrees),
            'isolation_rate': round(1 - len(nonzero_degrees)/len(degrees), 3) if degrees else 0,
            'mean_in_degree': round(statistics.mean(degrees), 2) if degrees else 0,
            'max_in_degree': max(degrees) if degrees else 0
        }

    return {
        'test': 'b_discussion_breadth',
        'hypothesis': 'Highly-referenced entries by definition have more B contexts',
        'results_by_stratum': results,
        'note': 'This is definitionally true for high-reference stratum'
    }


# =============================================================================
# VISUAL PREDICTIONS (LOCKED - DO NOT MODIFY AFTER CODING)
# =============================================================================

def generate_visual_predictions() -> Dict:
    """
    Generate and LOCK visual predictions before any visual coding.

    These predictions MUST NOT be modified after visual coding begins.
    """
    return {
        'prediction_status': 'LOCKED',
        'lock_date': datetime.now().isoformat(),
        'lock_note': 'These predictions were generated BEFORE visual coding. Do NOT modify.',

        'predictions': [
            {
                'id': 'VP1',
                'prediction': 'High-reference entries have lower visual complexity',
                'operationalization': 'complexity feature SIMPLE > MODERATE > COMPLEX',
                'expected_direction': 'high_reference mean complexity < low_reference mean',
                'rationale': 'Foundational entities may be depicted more simply'
            },
            {
                'id': 'VP2',
                'prediction': 'High-reference entries have more symmetric illustrations',
                'operationalization': 'symmetry feature SYMMETRIC vs ASYMMETRIC',
                'expected_direction': 'higher SYMMETRIC rate in high_reference',
                'rationale': 'Archetypal/canonical depictions may be more regularized'
            },
            {
                'id': 'VP3',
                'prediction': 'High-reference entries depict fewer distinct plant parts',
                'operationalization': 'Count of PRESENT plant features (root, stem, leaf, flower)',
                'expected_direction': 'high_reference mean part_count < low_reference mean',
                'rationale': 'Simpler entities may have fewer depicted components'
            },
            {
                'id': 'VP4',
                'prediction': 'High-reference entries have single stems more often',
                'operationalization': 'stem_count feature 1 vs 2 vs 3+',
                'expected_direction': 'higher stem_count=1 rate in high_reference',
                'rationale': 'Foundational plants may have simpler structure'
            },
            {
                'id': 'VP5',
                'prediction': 'High-reference entries have simpler root types',
                'operationalization': 'root_type SINGLE_TAPROOT vs BRANCHING/FIBROUS',
                'expected_direction': 'higher SINGLE_TAPROOT rate in high_reference',
                'rationale': 'Basic/archetypal plants often depicted with single root'
            }
        ],

        'success_criteria': {
            'minimum_predictions_supported': 2,
            'required_effect_size': 'Cramer V >= 0.2 or mean difference > 0.5 SD',
            'significance_level': 'p < 0.05 after Bonferroni correction (5 tests -> p < 0.01)'
        },

        'failure_interpretation': 'If fewer than 2 predictions supported, either: (1) reference count does not predict visual complexity, (2) illustrations are symbolic rather than morphological, or (3) our foundational-entity hypothesis is incorrect'
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 2: Reference-Weighted Predictions")
    print("=" * 70)

    # Load data
    print("\n[1/6] Loading data...")
    graph_data = load_reference_graph()
    db = load_folio_database()
    heading_data = load_heading_analysis()
    corpus = load_corpus()

    print(f"  Graph: {graph_data['graph_statistics']['basic_counts']['n_edges']} edges")
    print(f"  A entries: {len(db.get('currier_a', {}))}")
    print(f"  Corpus: {len(corpus)} word tokens")

    # Stratify
    print("\n[2/6] Stratifying A entries by reference count...")
    strata, in_degrees = stratify_by_reference_count(graph_data, db)

    for stratum, folios in strata.items():
        degrees = [in_degrees.get(f, 0) for f in folios]
        mean_deg = sum(degrees)/len(degrees) if degrees else 0
        print(f"  {stratum}: {len(folios)} entries (mean in-degree: {mean_deg:.2f})")

    # Run text-based tests
    print("\n[3/6] Running text-based tests...")

    test_results = []

    # Test 1: Word count
    wc_result = test_word_count_by_stratum(strata, db)
    test_results.append(wc_result)
    print(f"  Word count: {wc_result['effect']}")

    # Test 2: Prefix commonality
    prefix_result = test_prefix_commonality(strata, corpus, db)
    test_results.append(prefix_result)
    print(f"  Prefix commonality: {prefix_result['effect']}")

    # Test 3: Heading length
    heading_result = test_heading_length(strata, heading_data, db)
    test_results.append(heading_result)
    print(f"  Heading length: {heading_result['effect']}")

    # Test 4: Vocabulary richness
    vocab_result = test_vocabulary_richness(strata, db)
    test_results.append(vocab_result)
    print(f"  Vocabulary richness: {vocab_result['effect']}")

    # Test 5: B discussion breadth
    breadth_result = test_b_discussion_breadth(strata, in_degrees, graph_data)
    test_results.append(breadth_result)
    print(f"  B discussion breadth: calculated")

    # Generate visual predictions
    print("\n[4/6] Generating and LOCKING visual predictions...")
    visual_predictions = generate_visual_predictions()
    print(f"  Locked {len(visual_predictions['predictions'])} predictions")

    # Summarize text findings
    print("\n[5/6] Summarizing text-based findings...")

    predictions_supported = sum(1 for t in test_results if t.get('prediction_supported', False))

    text_summary = {
        'total_tests': len(test_results),
        'predictions_supported': predictions_supported,
        'key_findings': []
    }

    for t in test_results:
        finding = {
            'test': t['test'],
            'effect': t.get('effect', 'N/A'),
            'supported': t.get('prediction_supported', 'N/A')
        }
        text_summary['key_findings'].append(finding)

    print(f"  {predictions_supported}/{len(test_results)} text predictions supported")

    # Compile output
    print("\n[6/6] Saving results...")

    output = {
        'metadata': {
            'title': 'Reference-Weighted Predictions',
            'phase': 'Data Recovery Phase, Task 2',
            'date': datetime.now().isoformat(),
            'purpose': 'Test hypothesis that highly-referenced A entries are foundational'
        },

        'stratification': {
            'method': 'Quartile-based stratification by B in-degree',
            'strata': {
                stratum: {
                    'n_entries': len(folios),
                    'sample_folios': folios[:5],
                    'in_degree_stats': {
                        'mean': round(statistics.mean([in_degrees.get(f, 0) for f in folios]), 2),
                        'max': max([in_degrees.get(f, 0) for f in folios])
                    }
                }
                for stratum, folios in strata.items()
            }
        },

        'text_based_tests': test_results,

        'text_summary': text_summary,

        'visual_predictions': visual_predictions,

        'interpretation': {
            'text_findings': 'See text_based_tests for detailed results',
            'visual_status': 'PREDICTIONS LOCKED - awaiting visual coding',
            'next_step': 'Complete visual coding, then test visual predictions'
        }
    }

    output_file = 'reference_weight_predictions_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nStratification:")
    for stratum, data in output['stratification']['strata'].items():
        print(f"  {stratum}: {data['n_entries']} entries")

    print(f"\nText-based test results:")
    for finding in text_summary['key_findings']:
        status = "SUPPORTED" if finding['supported'] == True else "NOT SUPPORTED" if finding['supported'] == False else "N/A"
        print(f"  {finding['test']}: {finding['effect']} [{status}]")

    print(f"\nVisual predictions: {len(visual_predictions['predictions'])} LOCKED")
    for pred in visual_predictions['predictions']:
        print(f"  {pred['id']}: {pred['prediction'][:50]}...")

    return output


if __name__ == '__main__':
    main()
