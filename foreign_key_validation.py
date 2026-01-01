#!/usr/bin/env python3
"""
Data Recovery Phase, Task 8: Foreign Key Validation

Validates the B->A reference structure for semantic consistency.
Includes co-citation analysis, semantic consistency testing, and outlier detection.
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set
import statistics

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


# =============================================================================
# CO-CITATION ANALYSIS
# =============================================================================

def analyze_co_citations(graph_data: Dict, db: Dict) -> Dict:
    """
    Analyze co-citation patterns in B->A references.

    When B entry references multiple A entries, are those A entries similar?
    """
    co_citations = graph_data.get('co_citation_analysis', {})
    top_pairs = co_citations.get('top_co_cited_pairs', [])

    # Analyze vocabulary similarity for co-cited pairs
    currier_a = db.get('currier_a', {})
    pair_similarities = []

    for pair in top_pairs[:20]:  # Top 20 pairs
        a1 = pair['a1']
        a2 = pair['a2']

        a1_data = currier_a.get(a1, {}).get('text_features', {})
        a2_data = currier_a.get(a2, {}).get('text_features', {})

        # Get vocabularies
        a1_vocab = set(a1_data.get('part1_vocabulary', []) +
                       a1_data.get('part2_vocabulary', []) +
                       a1_data.get('part3_vocabulary', []))
        a2_vocab = set(a2_data.get('part1_vocabulary', []) +
                       a2_data.get('part2_vocabulary', []) +
                       a2_data.get('part3_vocabulary', []))

        # Calculate Jaccard similarity
        intersection = len(a1_vocab & a2_vocab)
        union = len(a1_vocab | a2_vocab)
        jaccard = intersection / union if union > 0 else 0

        # Compare prefixes
        a1_prefix = a1_data.get('opening_prefix', '')
        a2_prefix = a2_data.get('opening_prefix', '')
        same_prefix = a1_prefix == a2_prefix and a1_prefix != ''

        pair_similarities.append({
            'a1': a1,
            'a2': a2,
            'a1_heading': pair.get('a1_heading', ''),
            'a2_heading': pair.get('a2_heading', ''),
            'co_citation_count': pair['co_citation_count'],
            'vocabulary_jaccard': round(jaccard, 4),
            'same_heading_prefix': same_prefix,
            'interpretation': 'SIMILAR' if jaccard > 0.1 or same_prefix else 'DISSIMILAR'
        })

    # Summary statistics
    jaccard_values = [p['vocabulary_jaccard'] for p in pair_similarities]
    same_prefix_count = sum(1 for p in pair_similarities if p['same_heading_prefix'])

    return {
        'n_pairs_analyzed': len(pair_similarities),
        'mean_vocabulary_jaccard': round(statistics.mean(jaccard_values), 4) if jaccard_values else 0,
        'max_vocabulary_jaccard': round(max(jaccard_values), 4) if jaccard_values else 0,
        'pairs_with_same_prefix': same_prefix_count,
        'similar_pairs': [p for p in pair_similarities if p['interpretation'] == 'SIMILAR'],
        'dissimilar_pairs': [p for p in pair_similarities if p['interpretation'] == 'DISSIMILAR'],
        'all_pairs': pair_similarities
    }


# =============================================================================
# SEMANTIC CONSISTENCY TEST
# =============================================================================

def test_semantic_consistency(graph_data: Dict, db: Dict) -> Dict:
    """
    Test if co-referenced A entries are related.

    If our schema is correct:
    - B entries discussing similar topics should reference similar A entries
    - A entries referenced together should have higher vocabulary overlap than random pairs
    """
    co_citations = graph_data.get('co_citation_analysis', {})
    most_co_cited = co_citations.get('most_co_cited_a', [])
    currier_a = db.get('currier_a', {})

    # Get vocabulary overlap for co-cited vs random pairs
    co_cited_folios = [entry['folio'] for entry in most_co_cited[:10]]

    # Calculate pairwise similarities for co-cited group
    co_cited_similarities = []
    for i, f1 in enumerate(co_cited_folios):
        for f2 in co_cited_folios[i+1:]:
            a1_data = currier_a.get(f1, {}).get('text_features', {})
            a2_data = currier_a.get(f2, {}).get('text_features', {})

            a1_vocab = set(a1_data.get('part1_vocabulary', []) +
                           a1_data.get('part2_vocabulary', []))
            a2_vocab = set(a2_data.get('part1_vocabulary', []) +
                           a2_data.get('part2_vocabulary', []))

            intersection = len(a1_vocab & a2_vocab)
            union = len(a1_vocab | a2_vocab)
            jaccard = intersection / union if union > 0 else 0
            co_cited_similarities.append(jaccard)

    # Calculate pairwise similarities for random pairs (from isolated A entries)
    isolated = graph_data.get('graph_statistics', {}).get('isolated_nodes', {})
    isolated_folios = isolated.get('a_isolated_folios', [])[:10]

    random_similarities = []
    for i, f1 in enumerate(isolated_folios):
        for f2 in isolated_folios[i+1:]:
            a1_data = currier_a.get(f1, {}).get('text_features', {})
            a2_data = currier_a.get(f2, {}).get('text_features', {})

            a1_vocab = set(a1_data.get('part1_vocabulary', []) +
                           a1_data.get('part2_vocabulary', []))
            a2_vocab = set(a2_data.get('part1_vocabulary', []) +
                           a2_data.get('part2_vocabulary', []))

            intersection = len(a1_vocab & a2_vocab)
            union = len(a1_vocab | a2_vocab)
            jaccard = intersection / union if union > 0 else 0
            random_similarities.append(jaccard)

    # Compare
    mean_co_cited = statistics.mean(co_cited_similarities) if co_cited_similarities else 0
    mean_random = statistics.mean(random_similarities) if random_similarities else 0

    ratio = mean_co_cited / mean_random if mean_random > 0 else float('inf') if mean_co_cited > 0 else 1

    if ratio > 1.5:
        interpretation = "CONSISTENT"
        explanation = "Co-cited A entries have higher vocabulary overlap than random pairs, suggesting thematic coherence."
    elif ratio > 1.1:
        interpretation = "MARGINALLY_CONSISTENT"
        explanation = "Co-cited A entries have slightly higher vocabulary overlap than random pairs."
    else:
        interpretation = "INCONSISTENT"
        explanation = "Co-cited A entries do not have higher vocabulary overlap than random pairs."

    return {
        'co_cited_pairs': len(co_cited_similarities),
        'random_pairs': len(random_similarities),
        'mean_co_cited_jaccard': round(mean_co_cited, 4),
        'mean_random_jaccard': round(mean_random, 4),
        'ratio': round(ratio, 2),
        'interpretation': interpretation,
        'explanation': explanation
    }


# =============================================================================
# PREFIX PROFILE COMPARISON
# =============================================================================

def compare_prefix_profiles(graph_data: Dict, db: Dict) -> Dict:
    """
    Compare prefix profiles of co-referenced A entries.

    Do A entries referenced together share prefix patterns?
    """
    co_citations = graph_data.get('co_citation_analysis', {})
    top_pairs = co_citations.get('top_co_cited_pairs', [])
    currier_a = db.get('currier_a', {})

    profile_comparisons = []

    for pair in top_pairs[:15]:
        a1 = pair['a1']
        a2 = pair['a2']

        a1_data = currier_a.get(a1, {}).get('text_features', {})
        a2_data = currier_a.get(a2, {}).get('text_features', {})

        a1_prefixes = a1_data.get('prefix_distribution', {})
        a2_prefixes = a2_data.get('prefix_distribution', {})

        # Get top 3 prefixes for each
        a1_top = sorted(a1_prefixes.items(), key=lambda x: x[1], reverse=True)[:3]
        a2_top = sorted(a2_prefixes.items(), key=lambda x: x[1], reverse=True)[:3]

        a1_top_set = set(p[0] for p in a1_top)
        a2_top_set = set(p[0] for p in a2_top)

        shared_top = a1_top_set & a2_top_set

        profile_comparisons.append({
            'a1': a1,
            'a2': a2,
            'a1_top_prefixes': [p[0] for p in a1_top],
            'a2_top_prefixes': [p[0] for p in a2_top],
            'shared_top_prefixes': list(shared_top),
            'n_shared': len(shared_top)
        })

    # Summary
    mean_shared = statistics.mean([p['n_shared'] for p in profile_comparisons]) if profile_comparisons else 0

    return {
        'n_pairs_analyzed': len(profile_comparisons),
        'mean_shared_top_prefixes': round(mean_shared, 2),
        'pairs_with_shared': sum(1 for p in profile_comparisons if p['n_shared'] > 0),
        'comparisons': profile_comparisons
    }


# =============================================================================
# OUTLIER DETECTION
# =============================================================================

def detect_outliers(graph_data: Dict, db: Dict) -> Dict:
    """
    Identify anomalous references for manual review.

    Outliers include:
    - B entries referencing seemingly unrelated A entries
    - A entries referenced in unexpected contexts
    - Very high or very low reference counts
    """
    most_referenced = graph_data.get('graph_statistics', {}).get('most_referenced_a', [])
    isolated_a = graph_data.get('graph_statistics', {}).get('isolated_nodes', {}).get('a_isolated_folios', [])
    currier_a = db.get('currier_a', {})

    outliers = []

    # High-reference outliers (unusually important entries)
    if most_referenced:
        max_degree = most_referenced[0]['in_degree']
        mean_degree = graph_data.get('graph_statistics', {}).get('a_node_in_degree', {}).get('mean', 0)

        for entry in most_referenced[:5]:
            if entry['in_degree'] > mean_degree * 5:
                outliers.append({
                    'type': 'HIGH_REFERENCE',
                    'folio': entry['folio'],
                    'heading': entry['heading'],
                    'in_degree': entry['in_degree'],
                    'note': f"Referenced {entry['in_degree']}x (mean: {mean_degree:.1f})",
                    'review_reason': 'Unusually central entity - may be foundational concept'
                })

    # Zero-reference outliers (isolated entries)
    for folio in isolated_a[:10]:
        entry = currier_a.get(folio, {})
        text_features = entry.get('text_features', {})
        word_count = text_features.get('word_count', 0)

        if word_count > 100:  # Substantial entry that's never referenced
            outliers.append({
                'type': 'ISOLATED_SUBSTANTIAL',
                'folio': folio,
                'word_count': word_count,
                'note': f"Large entry ({word_count} words) never referenced by B",
                'review_reason': 'May be self-contained or from different context'
            })

    # Heading similarity outliers (entries with very similar headings but different reference patterns)
    co_citations = graph_data.get('co_citation_analysis', {})
    top_pairs = co_citations.get('top_co_cited_pairs', [])

    for pair in top_pairs[:5]:
        if pair['a1_heading'] == pair['a2_heading']:
            outliers.append({
                'type': 'DUPLICATE_HEADING',
                'folio1': pair['a1'],
                'folio2': pair['a2'],
                'heading': pair['a1_heading'],
                'co_citation_count': pair['co_citation_count'],
                'note': f"Same heading '{pair['a1_heading']}' on different folios",
                'review_reason': 'May indicate encoding error or intentional duplicate'
            })

    return {
        'n_outliers': len(outliers),
        'outliers': outliers,
        'review_priority': [o for o in outliers if o['type'] in ['DUPLICATE_HEADING', 'HIGH_REFERENCE']]
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 8: Foreign Key Validation")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading data...")
    graph_data = load_reference_graph()
    db = load_folio_database()
    print(f"  Graph: {graph_data['graph_statistics']['basic_counts']['n_edges']} edges")
    print(f"  A entries: {len(db.get('currier_a', {}))}")

    # Co-citation analysis
    print("\n[2/5] Analyzing co-citations...")
    co_citation_results = analyze_co_citations(graph_data, db)
    print(f"  Pairs analyzed: {co_citation_results['n_pairs_analyzed']}")
    print(f"  Mean vocabulary Jaccard: {co_citation_results['mean_vocabulary_jaccard']}")
    print(f"  Similar pairs: {len(co_citation_results['similar_pairs'])}")

    # Semantic consistency
    print("\n[3/5] Testing semantic consistency...")
    consistency_results = test_semantic_consistency(graph_data, db)
    print(f"  Co-cited vs random ratio: {consistency_results['ratio']}")
    print(f"  Interpretation: {consistency_results['interpretation']}")

    # Prefix profile comparison
    print("\n[4/5] Comparing prefix profiles...")
    prefix_results = compare_prefix_profiles(graph_data, db)
    print(f"  Mean shared top prefixes: {prefix_results['mean_shared_top_prefixes']}")

    # Outlier detection
    print("\n[5/5] Detecting outliers...")
    outlier_results = detect_outliers(graph_data, db)
    print(f"  Outliers found: {outlier_results['n_outliers']}")
    print(f"  Priority reviews: {len(outlier_results['review_priority'])}")

    # Compile report
    report = {
        'metadata': {
            'title': 'Foreign Key Validation Report',
            'phase': 'Data Recovery Phase, Task 8',
            'date': datetime.now().isoformat(),
            'purpose': 'Validate B->A reference structure for semantic consistency'
        },
        'co_citation_analysis': co_citation_results,
        'semantic_consistency_test': consistency_results,
        'prefix_profile_comparison': prefix_results,
        'outlier_detection': outlier_results,
        'summary': {
            'co_citation_coherence': co_citation_results['mean_vocabulary_jaccard'] > 0.05,
            'semantic_consistency': consistency_results['interpretation'],
            'prefix_alignment': prefix_results['mean_shared_top_prefixes'] > 1,
            'outliers_to_review': len(outlier_results['review_priority'])
        }
    }

    # Save report
    with open('foreign_key_validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nCo-citation coherence: {'YES' if report['summary']['co_citation_coherence'] else 'NO'}")
    print(f"Semantic consistency: {report['summary']['semantic_consistency']}")
    print(f"Prefix alignment: {'YES' if report['summary']['prefix_alignment'] else 'NO'}")
    print(f"Outliers to review: {report['summary']['outliers_to_review']}")
    print(f"\nSaved to: foreign_key_validation_report.json")

    return report


if __name__ == '__main__':
    main()
