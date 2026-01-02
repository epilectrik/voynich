#!/usr/bin/env python3
"""
Visual Coding Phase, Task 6: pchor Investigation

Deep dive into the duplicate heading anomaly where f19r, f21r, f52v
all share the identical heading "pchor" and are always co-cited.
"""

import json
from collections import Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple

# =============================================================================
# CONFIGURATION
# =============================================================================

FOLIO_DATABASE_FILE = 'folio_feature_database.json'
REFERENCE_GRAPH_FILE = 'reference_graph_analysis_report.json'

PCHOR_FOLIOS = ['f19r', 'f21r', 'f52v']


# =============================================================================
# DATA LOADING
# =============================================================================

def load_folio_database() -> Dict:
    """Load full folio feature database."""
    with open(FOLIO_DATABASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_reference_graph() -> Dict:
    """Load reference graph analysis."""
    with open(REFERENCE_GRAPH_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# TEXT COMPARISON
# =============================================================================

def get_vocabulary(text_features: Dict) -> Set[str]:
    """Extract full vocabulary from text features."""
    vocab = set()
    for part in ['part1_vocabulary', 'part2_vocabulary', 'part3_vocabulary']:
        vocab.update(text_features.get(part, []))
    return vocab


def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0


def compare_vocabularies(entries: Dict[str, Dict]) -> Dict:
    """Compare vocabularies between pchor entries."""
    comparisons = []

    folio_ids = list(entries.keys())
    vocabularies = {f: get_vocabulary(entries[f].get('text_features', {})) for f in folio_ids}

    for i, f1 in enumerate(folio_ids):
        for f2 in folio_ids[i+1:]:
            v1 = vocabularies[f1]
            v2 = vocabularies[f2]

            jaccard = jaccard_similarity(v1, v2)
            shared = v1 & v2
            unique_to_f1 = v1 - v2
            unique_to_f2 = v2 - v1

            comparisons.append({
                'pair': f'{f1} <-> {f2}',
                'jaccard': round(jaccard, 4),
                'shared_count': len(shared),
                'unique_to_first': len(unique_to_f1),
                'unique_to_second': len(unique_to_f2),
                'shared_words': sorted(list(shared))[:20],  # Top 20 for display
                'interpretation': 'SIMILAR' if jaccard > 0.1 else 'DISTINCT'
            })

    # Average similarity
    avg_jaccard = sum(c['jaccard'] for c in comparisons) / len(comparisons) if comparisons else 0

    return {
        'pairwise_comparisons': comparisons,
        'average_jaccard': round(avg_jaccard, 4),
        'interpretation': 'VOCABULARIES_SIMILAR' if avg_jaccard > 0.1 else 'VOCABULARIES_DISTINCT'
    }


def compare_parts(entries: Dict[str, Dict]) -> Dict:
    """Compare part-by-part vocabularies."""
    folio_ids = list(entries.keys())
    part_comparisons = {}

    for part in ['part1', 'part2', 'part3']:
        vocab_key = f'{part}_vocabulary'
        part_vocabs = {}

        for f in folio_ids:
            tf = entries[f].get('text_features', {})
            part_vocabs[f] = set(tf.get(vocab_key, []))

        # Compare all pairs
        similarities = []
        for i, f1 in enumerate(folio_ids):
            for f2 in folio_ids[i+1:]:
                jaccard = jaccard_similarity(part_vocabs[f1], part_vocabs[f2])
                similarities.append({
                    'pair': f'{f1} <-> {f2}',
                    'jaccard': round(jaccard, 4)
                })

        avg = sum(s['jaccard'] for s in similarities) / len(similarities) if similarities else 0
        part_comparisons[part] = {
            'pairwise': similarities,
            'average_jaccard': round(avg, 4)
        }

    return part_comparisons


# =============================================================================
# PREFIX PROFILE COMPARISON
# =============================================================================

def get_prefix_profile(text_features: Dict) -> Dict[str, int]:
    """Get prefix frequency distribution."""
    return text_features.get('prefix_distribution', text_features.get('prefix_counts', {}))


def compare_prefix_profiles(entries: Dict[str, Dict]) -> Dict:
    """Compare prefix profiles across pchor entries."""
    profiles = {}
    for folio_id, entry in entries.items():
        tf = entry.get('text_features', {})
        profiles[folio_id] = get_prefix_profile(tf)

    # Get top 5 prefixes for each
    top_prefixes = {}
    for folio_id, profile in profiles.items():
        sorted_prefixes = sorted(profile.items(), key=lambda x: x[1], reverse=True)
        top_prefixes[folio_id] = [p[0] for p in sorted_prefixes[:5]]

    # Find shared top prefixes
    all_top = [set(tp) for tp in top_prefixes.values()]
    if all_top:
        shared_top = all_top[0]
        for s in all_top[1:]:
            shared_top = shared_top & s
    else:
        shared_top = set()

    # Calculate profile similarity
    all_prefixes = set()
    for profile in profiles.values():
        all_prefixes.update(profile.keys())

    profile_vectors = {}
    for folio_id, profile in profiles.items():
        profile_vectors[folio_id] = {p: profile.get(p, 0) for p in all_prefixes}

    # Cosine similarity for prefix profiles
    def cosine_similarity(v1: Dict, v2: Dict) -> float:
        keys = set(v1.keys()) | set(v2.keys())
        dot = sum(v1.get(k, 0) * v2.get(k, 0) for k in keys)
        mag1 = sum(v1.get(k, 0) ** 2 for k in keys) ** 0.5
        mag2 = sum(v2.get(k, 0) ** 2 for k in keys) ** 0.5
        return dot / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0

    folio_ids = list(profiles.keys())
    profile_similarities = []
    for i, f1 in enumerate(folio_ids):
        for f2 in folio_ids[i+1:]:
            sim = cosine_similarity(profile_vectors[f1], profile_vectors[f2])
            profile_similarities.append({
                'pair': f'{f1} <-> {f2}',
                'cosine_similarity': round(sim, 4)
            })

    avg_sim = sum(s['cosine_similarity'] for s in profile_similarities) / len(profile_similarities) if profile_similarities else 0

    return {
        'top_prefixes_per_folio': top_prefixes,
        'shared_top_prefixes': list(shared_top),
        'profile_similarities': profile_similarities,
        'average_profile_similarity': round(avg_sim, 4),
        'interpretation': 'PROFILES_SIMILAR' if avg_sim > 0.7 else 'PROFILES_DISTINCT'
    }


# =============================================================================
# B REFERENCE ANALYSIS
# =============================================================================

def analyze_b_references(graph_data: Dict, pchor_folios: List[str]) -> Dict:
    """Analyze how B entries reference the pchor folios."""
    co_citations = graph_data.get('co_citation_analysis', {})
    top_pairs = co_citations.get('top_co_cited_pairs', [])

    # Find pchor-related pairs
    pchor_pairs = []
    for pair in top_pairs:
        a1, a2 = pair.get('a1'), pair.get('a2')
        if a1 in pchor_folios and a2 in pchor_folios:
            pchor_pairs.append({
                'a1': a1,
                'a2': a2,
                'co_citation_count': pair.get('co_citation_count', 0)
            })

    # Find which B entries reference all three
    # This would require access to the full reference edges, which we don't have
    # in the summary report. We can infer from co-citation counts.

    # From the data, we know each pchor folio has in-degree 7
    most_ref = graph_data.get('graph_statistics', {}).get('most_referenced_a', [])
    pchor_refs = {}
    for entry in most_ref:
        if entry['folio'] in pchor_folios:
            pchor_refs[entry['folio']] = {
                'in_degree': entry['in_degree'],
                'heading': entry['heading']
            }

    return {
        'pchor_reference_counts': pchor_refs,
        'pchor_co_citation_pairs': pchor_pairs,
        'always_co_cited': len(pchor_pairs) == 3 and all(p['co_citation_count'] == 7 for p in pchor_pairs),
        'interpretation': 'ALWAYS_CITED_TOGETHER' if len(pchor_pairs) == 3 else 'SOMETIMES_CITED_TOGETHER'
    }


# =============================================================================
# HYPOTHESIS GENERATION
# =============================================================================

def generate_hypotheses(vocab_comparison: Dict, prefix_comparison: Dict,
                       ref_analysis: Dict) -> Dict:
    """Generate hypotheses based on analysis results."""
    vocab_similar = vocab_comparison['interpretation'] == 'VOCABULARIES_SIMILAR'
    prefix_similar = prefix_comparison['interpretation'] == 'PROFILES_SIMILAR'
    always_cocited = ref_analysis.get('always_co_cited', False)

    hypotheses = []

    # Hypothesis 1: Same plant, multiple depictions
    h1_support = vocab_similar and prefix_similar
    hypotheses.append({
        'id': 'H1',
        'statement': 'pchor entries describe the SAME PLANT with different depictions',
        'support_level': 'STRONG' if h1_support else 'WEAK',
        'evidence': {
            'vocabulary_similar': vocab_similar,
            'prefix_profiles_similar': prefix_similar,
            'always_cocited': always_cocited
        },
        'prediction': 'Visual illustrations should show similar plant morphology'
    })

    # Hypothesis 2: Category label (not unique identifier)
    h2_support = not vocab_similar and always_cocited
    hypotheses.append({
        'id': 'H2',
        'statement': 'pchor is a CATEGORY LABEL, not a unique plant identifier',
        'support_level': 'STRONG' if h2_support else 'WEAK',
        'evidence': {
            'vocabulary_distinct': not vocab_similar,
            'always_cocited': always_cocited
        },
        'prediction': 'Visual illustrations may show different plants in same category'
    })

    # Hypothesis 3: Variants or subspecies
    h3_support = 0.05 < vocab_comparison['average_jaccard'] < 0.2
    hypotheses.append({
        'id': 'H3',
        'statement': 'pchor entries describe VARIANTS or SUBSPECIES of same plant',
        'support_level': 'MODERATE' if h3_support else 'WEAK',
        'evidence': {
            'partial_vocabulary_overlap': h3_support,
            'avg_jaccard': vocab_comparison['average_jaccard']
        },
        'prediction': 'Visual illustrations should show related but distinct plants'
    })

    # Hypothesis 4: Encoding error or scribal duplication
    h4_support = vocab_similar and prefix_similar and always_cocited
    hypotheses.append({
        'id': 'H4',
        'statement': 'pchor duplication is an ENCODING ERROR or intentional redundancy',
        'support_level': 'POSSIBLE' if h4_support else 'UNLIKELY',
        'evidence': {
            'highly_similar_content': h4_support
        },
        'prediction': 'Visual illustrations may be very similar or identical'
    })

    # Determine most likely hypothesis
    strong_hypotheses = [h for h in hypotheses if h['support_level'] == 'STRONG']
    if strong_hypotheses:
        most_likely = strong_hypotheses[0]['id']
    else:
        moderate = [h for h in hypotheses if h['support_level'] == 'MODERATE']
        most_likely = moderate[0]['id'] if moderate else 'UNCLEAR'

    return {
        'hypotheses': hypotheses,
        'most_likely': most_likely,
        'requires_visual_confirmation': True
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Visual Coding Phase, Task 6: pchor Investigation")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading data...")
    db = load_folio_database()
    graph_data = load_reference_graph()

    # Extract pchor entries
    pchor_entries = {}
    currier_a = db.get('currier_a', {})

    for folio_id in PCHOR_FOLIOS:
        if folio_id in currier_a:
            pchor_entries[folio_id] = currier_a[folio_id]
            tf = currier_a[folio_id].get('text_features', {})
            print(f"  {folio_id}: {tf.get('word_count', 'N/A')} words, "
                  f"heading '{tf.get('opening_word', 'N/A')}'")
        else:
            print(f"  {folio_id}: NOT FOUND in database")

    if len(pchor_entries) < 2:
        print("\nError: Need at least 2 pchor entries for comparison")
        return None

    # Vocabulary comparison
    print("\n[2/5] Comparing vocabularies...")
    vocab_comparison = compare_vocabularies(pchor_entries)
    print(f"  Average Jaccard similarity: {vocab_comparison['average_jaccard']}")
    print(f"  Interpretation: {vocab_comparison['interpretation']}")

    for comp in vocab_comparison['pairwise_comparisons']:
        print(f"    {comp['pair']}: Jaccard={comp['jaccard']}, "
              f"shared={comp['shared_count']}")

    # Part-by-part comparison
    print("\n[3/5] Comparing part-by-part vocabularies...")
    part_comparison = compare_parts(pchor_entries)
    for part, data in part_comparison.items():
        print(f"  {part}: avg Jaccard={data['average_jaccard']}")

    # Prefix profile comparison
    print("\n[4/5] Comparing prefix profiles...")
    prefix_comparison = compare_prefix_profiles(pchor_entries)
    print(f"  Shared top prefixes: {prefix_comparison['shared_top_prefixes']}")
    print(f"  Average profile similarity: {prefix_comparison['average_profile_similarity']}")
    print(f"  Top prefixes per folio:")
    for folio_id, top in prefix_comparison['top_prefixes_per_folio'].items():
        print(f"    {folio_id}: {top}")

    # B reference analysis
    print("\n[5/5] Analyzing B references...")
    ref_analysis = analyze_b_references(graph_data, PCHOR_FOLIOS)
    print(f"  Reference counts:")
    for folio_id, data in ref_analysis['pchor_reference_counts'].items():
        print(f"    {folio_id}: {data['in_degree']} references")
    print(f"  Always co-cited: {ref_analysis['always_co_cited']}")

    # Generate hypotheses
    print("\n" + "=" * 70)
    print("HYPOTHESIS GENERATION")
    print("=" * 70)

    hypotheses = generate_hypotheses(vocab_comparison, prefix_comparison, ref_analysis)

    for h in hypotheses['hypotheses']:
        print(f"\n{h['id']}: {h['statement']}")
        print(f"  Support: {h['support_level']}")
        print(f"  Prediction: {h['prediction']}")

    print(f"\nMost likely hypothesis: {hypotheses['most_likely']}")
    print(f"Requires visual confirmation: {hypotheses['requires_visual_confirmation']}")

    # Compile report
    report = {
        'metadata': {
            'title': 'pchor Investigation Report',
            'phase': 'Visual Coding Phase, Task 6',
            'date': datetime.now().isoformat(),
            'purpose': 'Investigate duplicate heading anomaly (f19r, f21r, f52v)'
        },
        'folios_analyzed': PCHOR_FOLIOS,
        'vocabulary_comparison': vocab_comparison,
        'part_by_part_comparison': part_comparison,
        'prefix_profile_comparison': prefix_comparison,
        'b_reference_analysis': ref_analysis,
        'hypothesis_analysis': hypotheses,
        'key_findings': {
            'average_vocabulary_overlap': vocab_comparison['average_jaccard'],
            'shared_top_prefixes': prefix_comparison['shared_top_prefixes'],
            'always_cocited': ref_analysis['always_co_cited'],
            'most_likely_explanation': hypotheses['most_likely']
        },
        'recommendations': {
            'visual_comparison_needed': True,
            'priority': 'HIGH',
            'specific_checks': [
                'Compare plant morphology across all three folios',
                'Check if illustrations show same, similar, or different plants',
                'Note any visual markers that might indicate category vs identity'
            ]
        }
    }

    # Save report
    output_file = 'pchor_investigation_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_file}")

    return report


if __name__ == '__main__':
    main()
