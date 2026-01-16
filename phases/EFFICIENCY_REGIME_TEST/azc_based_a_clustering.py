#!/usr/bin/env python3
"""
AZC-Based Currier A Entry Clustering

Uses AZC folio co-occurrence to cluster Currier A entries and reveal potential
material sub-families beyond what PREFIX morphology alone shows.

Logic:
- If two A entries appear in the same AZC folios, they may index related materials
- Clustering by co-occurrence may reveal sub-families within PREFIX classes
- This tests whether AZC provides additional grouping signal beyond morphology

Method:
1. Build token -> AZC folio mapping for all A entries
2. Compute pairwise Jaccard similarity (shared folios / union of folios)
3. Cluster entries by similarity
4. Analyze cluster composition vs PREFIX classes
5. Look for sub-families that morphology alone doesn't reveal
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "azc_based_a_clustering.json"

# AZC Family definitions (from C430)
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS

# Morphological components
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    original = token
    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix}


def load_a_entries_with_azc() -> Dict[str, Dict]:
    """
    Load Currier A entries and their AZC folio appearances.

    Logic:
    - First pass: identify all tokens that appear in Currier A (language='A')
    - Second pass: for those tokens, find which AZC folios they ALSO appear in

    Returns mapping: token -> {prefix, middle, suffix, azc_folios, family_counts}
    """
    # First pass: collect all Currier A tokens
    currier_a_tokens = set()

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            if language == 'A':
                currier_a_tokens.add(word)

    print(f"   Found {len(currier_a_tokens)} unique Currier A tokens")

    # Second pass: for A tokens, track their AZC folio appearances
    entries = defaultdict(lambda: {
        'prefix': '',
        'middle': '',
        'suffix': '',
        'azc_folios': set(),
        'zodiac_count': 0,
        'ac_count': 0,
        'a_count': 0  # Count in Currier A sections
    })

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            section = row.get('section', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Only process tokens that are also Currier A tokens
            if word not in currier_a_tokens:
                continue

            # Track morphology
            if not entries[word]['prefix']:
                decomp = decompose_token(word)
                entries[word]['prefix'] = decomp['prefix']
                entries[word]['middle'] = decomp['middle']
                entries[word]['suffix'] = decomp['suffix']

            # Track Currier A appearances
            if language == 'A':
                entries[word]['a_count'] += 1

            # Check if this is an AZC folio appearance
            # AZC folios have language=NA but folio in our list, OR section in Z/A/C
            is_azc = folio in ALL_AZC_FOLIOS
            if is_azc:
                entries[word]['azc_folios'].add(folio)
                if folio in ZODIAC_FOLIOS:
                    entries[word]['zodiac_count'] += 1
                elif folio in AC_FOLIOS:
                    entries[word]['ac_count'] += 1

    # Convert to result, keeping only tokens with AZC presence
    result = {}
    for token, data in entries.items():
        if data['azc_folios']:  # Only keep tokens that appear in at least one AZC folio
            result[token] = {
                'prefix': data['prefix'],
                'middle': data['middle'],
                'suffix': data['suffix'],
                'azc_folios': list(data['azc_folios']),
                'zodiac_count': data['zodiac_count'],
                'ac_count': data['ac_count'],
                'a_count': data['a_count'],
                'n_azc_folios': len(data['azc_folios'])
            }

    return result


def compute_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def build_similarity_matrix(entries: Dict[str, Dict], min_folios: int = 2) -> Dict[str, Dict]:
    """
    Build sparse similarity matrix for entries with sufficient AZC presence.
    Returns: {token1: {token2: similarity, ...}, ...}
    """
    # Filter to tokens with minimum folio presence
    eligible_tokens = [
        token for token, data in entries.items()
        if data['n_azc_folios'] >= min_folios
    ]

    print(f"   Eligible tokens (>={min_folios} AZC folios): {len(eligible_tokens)}")

    similarity = defaultdict(dict)
    comparisons = 0
    high_similarity_pairs = 0

    for i, token1 in enumerate(eligible_tokens):
        folios1 = set(entries[token1]['azc_folios'])

        for token2 in eligible_tokens[i+1:]:
            folios2 = set(entries[token2]['azc_folios'])
            sim = compute_jaccard_similarity(folios1, folios2)

            if sim > 0.3:  # Only store meaningful similarities
                similarity[token1][token2] = sim
                similarity[token2][token1] = sim
                high_similarity_pairs += 1

            comparisons += 1

    print(f"   Comparisons: {comparisons}, High similarity pairs: {high_similarity_pairs}")

    return dict(similarity), eligible_tokens


def simple_clustering(similarity: Dict[str, Dict], tokens: List[str],
                      threshold: float = 0.5) -> List[Set[str]]:
    """
    Simple single-linkage clustering based on similarity threshold.
    """
    # Initialize each token as its own cluster
    token_to_cluster = {token: i for i, token in enumerate(tokens)}
    clusters = [{token} for token in tokens]

    # Merge clusters based on similarity
    for token1, neighbors in similarity.items():
        for token2, sim in neighbors.items():
            if sim >= threshold:
                c1 = token_to_cluster[token1]
                c2 = token_to_cluster[token2]

                if c1 != c2:
                    # Merge smaller into larger
                    if len(clusters[c1]) < len(clusters[c2]):
                        c1, c2 = c2, c1

                    # Move all from c2 to c1
                    for token in clusters[c2]:
                        token_to_cluster[token] = c1
                        clusters[c1].add(token)
                    clusters[c2] = set()

    # Filter empty clusters
    return [c for c in clusters if len(c) > 0]


def analyze_cluster_composition(clusters: List[Set[str]], entries: Dict[str, Dict]) -> Dict:
    """
    Analyze PREFIX composition of each cluster.
    """
    cluster_analysis = []

    for i, cluster in enumerate(clusters):
        if len(cluster) < 2:
            continue

        # Prefix distribution
        prefix_counts = Counter(entries[t]['prefix'] for t in cluster if t in entries)

        # MIDDLE distribution (top 5)
        middle_counts = Counter(entries[t]['middle'] for t in cluster if t in entries)

        # Family distribution
        zodiac_sum = sum(entries[t]['zodiac_count'] for t in cluster if t in entries)
        ac_sum = sum(entries[t]['ac_count'] for t in cluster if t in entries)
        total = zodiac_sum + ac_sum

        if total > 0:
            zodiac_pct = zodiac_sum / total * 100
            ac_pct = ac_sum / total * 100
        else:
            zodiac_pct = 0
            ac_pct = 0

        # Get shared folios (intersection of all tokens in cluster)
        folio_sets = [set(entries[t]['azc_folios']) for t in cluster if t in entries]
        if folio_sets:
            shared_folios = folio_sets[0]
            for fs in folio_sets[1:]:
                shared_folios &= fs
        else:
            shared_folios = set()

        cluster_analysis.append({
            'cluster_id': i,
            'size': len(cluster),
            'tokens': list(cluster)[:20],  # Sample
            'prefix_distribution': dict(prefix_counts.most_common(5)),
            'middle_distribution': dict(middle_counts.most_common(5)),
            'zodiac_pct': round(zodiac_pct, 1),
            'ac_pct': round(ac_pct, 1),
            'shared_folios': list(shared_folios),
            'dominant_prefix': prefix_counts.most_common(1)[0][0] if prefix_counts else 'none'
        })

    return sorted(cluster_analysis, key=lambda x: x['size'], reverse=True)


def find_sub_families(cluster_analysis: List[Dict], entries: Dict[str, Dict]) -> Dict:
    """
    Look for sub-families within PREFIX classes.
    A sub-family exists when:
    - Multiple clusters share the same dominant PREFIX
    - But have different AZC family biases or different shared folios
    """
    # Group clusters by dominant prefix
    prefix_groups = defaultdict(list)
    for ca in cluster_analysis:
        if ca['size'] >= 3:  # Only consider meaningful clusters
            prefix_groups[ca['dominant_prefix']].append(ca)

    sub_families = {}

    for prefix, clusters in prefix_groups.items():
        if len(clusters) < 2:
            continue

        # Check if clusters have different family biases
        zodiac_biased = [c for c in clusters if c['zodiac_pct'] > 60]
        ac_biased = [c for c in clusters if c['ac_pct'] > 60]
        balanced = [c for c in clusters if 40 <= c['zodiac_pct'] <= 60]

        if len(zodiac_biased) > 0 and len(ac_biased) > 0:
            sub_families[prefix] = {
                'evidence': 'FAMILY_SPLIT',
                'n_clusters': len(clusters),
                'zodiac_biased_clusters': len(zodiac_biased),
                'ac_biased_clusters': len(ac_biased),
                'balanced_clusters': len(balanced),
                'interpretation': f'{prefix}- entries split by AZC family affinity'
            }
        elif len(clusters) >= 3:
            # Check for folio-based splits (different shared folios)
            folio_patterns = [tuple(sorted(c['shared_folios'])) for c in clusters]
            unique_patterns = len(set(folio_patterns))

            if unique_patterns >= 2:
                sub_families[prefix] = {
                    'evidence': 'FOLIO_SPLIT',
                    'n_clusters': len(clusters),
                    'unique_folio_patterns': unique_patterns,
                    'interpretation': f'{prefix}- entries cluster by specific AZC folio context'
                }

    return sub_families


def compute_prefix_azc_contingency(entries: Dict[str, Dict]) -> Dict:
    """
    For each PREFIX, compute how tokens distribute across AZC families.
    This provides baseline to compare against cluster-based analysis.
    """
    prefix_family = defaultdict(lambda: {'zodiac': 0, 'ac': 0, 'mixed': 0})

    for token, data in entries.items():
        prefix = data['prefix']
        zod = data['zodiac_count']
        ac = data['ac_count']

        if zod > 0 and ac == 0:
            prefix_family[prefix]['zodiac'] += 1
        elif ac > 0 and zod == 0:
            prefix_family[prefix]['ac'] += 1
        elif zod > 0 and ac > 0:
            prefix_family[prefix]['mixed'] += 1
        # If both are 0, token is in AZC but not in known family folios - skip

    result = {}
    for prefix, counts in prefix_family.items():
        total = counts['zodiac'] + counts['ac'] + counts['mixed']
        if total >= 3:  # Lower threshold since we're filtering more
            result[prefix] = {
                'zodiac_exclusive': counts['zodiac'],
                'ac_exclusive': counts['ac'],
                'mixed': counts['mixed'],
                'total': total,
                'zodiac_pct': round(counts['zodiac'] / total * 100, 1),
                'ac_pct': round(counts['ac'] / total * 100, 1)
            }

    return result


def main():
    print("=" * 70)
    print("AZC-BASED CURRIER A ENTRY CLUSTERING")
    print("=" * 70)
    print("\nGoal: Use AZC folio co-occurrence to reveal material sub-families")
    print()

    # Step 1: Load A entries with AZC presence
    print("1. Loading Currier A entries with AZC folio data...")
    entries = load_a_entries_with_azc()
    print(f"   Found {len(entries)} A tokens with AZC folio presence")

    if len(entries) == 0:
        print("\n   WARNING: No Currier A tokens found in AZC folios!")
        print("   This suggests minimal vocabulary overlap between Currier A sections and AZC sections.")
        print("   The probe cannot proceed - this is itself a meaningful finding.")

        output = {
            'probe_id': 'AZC_BASED_A_CLUSTERING',
            'question': 'Can AZC folio membership reveal material sub-families within Currier A?',
            'result': 'NO_OVERLAP',
            'interpretation': 'Currier A vocabulary does not appear in AZC folios - systems use disjoint vocabularies',
            'verdict': {
                'overall': 'DISJOINT_SYSTEMS',
                'interpretation': 'Currier A and AZC use largely disjoint vocabularies - clustering not possible'
            }
        }

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        print(f"\n\nResults saved to: {OUTPUT_FILE}")
        return output

    # Baseline: PREFIX distribution
    prefix_counts = Counter(e['prefix'] for e in entries.values())
    print(f"\n   PREFIX distribution (top 10):")
    for prefix, count in prefix_counts.most_common(10):
        print(f"      {prefix or '(none)'}: {count}")

    # Step 2: Compute baseline PREFIX -> AZC family contingency
    print("\n2. Computing PREFIX -> AZC family baseline...")
    prefix_contingency = compute_prefix_azc_contingency(entries)

    print(f"\n   PREFIX family bias (>= 5 tokens):")
    for prefix in sorted(prefix_contingency.keys()):
        data = prefix_contingency[prefix]
        bias = 'ZODIAC' if data['zodiac_pct'] > 60 else ('A/C' if data['ac_pct'] > 60 else 'BALANCED')
        print(f"      {prefix or '(none)'}: {data['total']} tokens, {bias} ({data['zodiac_pct']}% Zod, {data['ac_pct']}% A/C)")

    # Step 3: Build similarity matrix
    print("\n3. Building AZC folio co-occurrence similarity matrix...")
    similarity, eligible_tokens = build_similarity_matrix(entries, min_folios=2)

    # Step 4: Cluster at multiple thresholds
    print("\n4. Clustering at multiple similarity thresholds...")

    thresholds = [0.3, 0.5, 0.7]
    clustering_results = {}

    for thresh in thresholds:
        clusters = simple_clustering(similarity, eligible_tokens, threshold=thresh)
        non_singleton = [c for c in clusters if len(c) >= 2]
        total_in_clusters = sum(len(c) for c in non_singleton)
        largest = max(len(c) for c in clusters) if clusters else 0

        print(f"\n   Threshold {thresh}:")
        print(f"      Clusters (size >= 2): {len(non_singleton)}")
        print(f"      Tokens in clusters: {total_in_clusters}")
        print(f"      Largest cluster: {largest}")

        # Analyze composition
        analysis = analyze_cluster_composition(clusters, entries)
        sub_families = find_sub_families(analysis, entries)

        clustering_results[f"threshold_{thresh}"] = {
            'n_clusters': len(non_singleton),
            'tokens_clustered': total_in_clusters,
            'largest_cluster': max(len(c) for c in clusters),
            'top_clusters': analysis[:10],
            'sub_families_detected': sub_families
        }

        if sub_families:
            print(f"\n      SUB-FAMILIES DETECTED:")
            for prefix, sf in sub_families.items():
                print(f"         {prefix}: {sf['evidence']} - {sf['interpretation']}")

    # Step 5: Detailed analysis at optimal threshold
    print("\n" + "=" * 70)
    print("DETAILED ANALYSIS (threshold=0.5)")
    print("=" * 70)

    best_result = clustering_results['threshold_0.5']

    print(f"\nTop 10 clusters by size:")
    for i, cluster in enumerate(best_result['top_clusters'][:10]):
        print(f"\n   Cluster {cluster['cluster_id']} (n={cluster['size']}):")
        print(f"      Dominant PREFIX: {cluster['dominant_prefix']}")
        print(f"      PREFIX dist: {cluster['prefix_distribution']}")
        print(f"      Family: {cluster['zodiac_pct']}% Zodiac, {cluster['ac_pct']}% A/C")
        print(f"      Shared folios: {cluster['shared_folios'][:5]}")
        print(f"      Sample tokens: {cluster['tokens'][:5]}")

    # Step 6: Summary and interpretation
    print("\n" + "=" * 70)
    print("SUMMARY AND INTERPRETATION")
    print("=" * 70)

    # Count sub-families across thresholds
    all_sub_families = set()
    for thresh_key, result in clustering_results.items():
        for prefix in result['sub_families_detected'].keys():
            all_sub_families.add(prefix)

    if all_sub_families:
        verdict = 'SUB_FAMILIES_DETECTED'
        interpretation = f'AZC co-occurrence reveals sub-families within PREFIX classes: {", ".join(all_sub_families)}'
    else:
        # Check if clusters align with PREFIX or break across
        # Look at cluster composition diversity
        top_clusters = best_result['top_clusters'][:10]
        diverse_clusters = sum(1 for c in top_clusters if len(c['prefix_distribution']) >= 3)

        if diverse_clusters >= 3:
            verdict = 'CROSS_PREFIX_CLUSTERING'
            interpretation = 'AZC co-occurrence groups tokens across PREFIX boundaries - material context dominates morphology'
        else:
            verdict = 'PREFIX_ALIGNED'
            interpretation = 'Clusters largely align with PREFIX classes - AZC does not reveal additional structure beyond morphology'

    print(f"\n>>> {verdict} <<<")
    print(f"    {interpretation}")

    # Save results
    output = {
        'probe_id': 'AZC_BASED_A_CLUSTERING',
        'question': 'Can AZC folio membership reveal material sub-families within Currier A beyond PREFIX alone?',
        'method': 'Jaccard similarity clustering on AZC folio co-occurrence',
        'data': {
            'n_a_tokens_with_azc': len(entries),
            'n_eligible_for_clustering': len(eligible_tokens),
            'prefix_baseline': prefix_contingency
        },
        'clustering_results': clustering_results,
        'verdict': {
            'overall': verdict,
            'interpretation': interpretation,
            'sub_families_detected': list(all_sub_families)
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
