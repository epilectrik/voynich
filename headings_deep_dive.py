#!/usr/bin/env python3
"""
Headings Deep Dive Analysis - Voynich Manuscript

Determines the semantic role and value type of Currier A heading words
without assigning meanings.

Produces 12 JSON output files covering phases H1-H7.
"""

import json
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from datetime import datetime
import math
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform

# ==============================================================================
# CONFIGURATION
# ==============================================================================

REFERENCE_GRAPH = 'reference_graph.graphml'
FOLIO_DATABASE = 'folio_feature_database.json'
VISUAL_CODING = 'visual_coding_complete.json'
HEADING_ANALYSIS = 'heading_word_analysis_report.json'

# Known prefix and suffix inventories
KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo'
]

KNOWN_SUFFIXES = [
    'aiin', 'ain', 'iin', 'in', 'eedy', 'edy', 'dy', 'eey', 'ey', 'hy', 'y',
    'ar', 'or', 'ir', 'er', 'al', 'ol', 'el', 'il', 'am', 'an', 'en', 'on',
    's', 'm', 'n', 'l', 'r', 'd'
]

# EVA character classification
CONSONANTS = set('ktpfcsdlrnmq')
VOWELS = set('aoiey')

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_cv_pattern(word):
    """Convert word to consonant-vowel pattern."""
    pattern = ''
    for char in word:
        if char in CONSONANTS:
            pattern += 'C'
        elif char in VOWELS:
            pattern += 'V'
        else:
            pattern += 'X'  # unknown
    return pattern

def get_prefix(word):
    """Extract prefix from word."""
    for length in [3, 2]:  # try longer prefixes first
        prefix = word[:length] if len(word) >= length else word
        if prefix in KNOWN_PREFIXES:
            return prefix
    # Try single character
    if len(word) >= 1 and word[0] in 'qchsdofpktylar':
        return word[:2] if len(word) >= 2 else word[0]
    return word[:2] if len(word) >= 2 else word

def get_suffix(word):
    """Extract suffix from word."""
    for suffix in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if word.endswith(suffix):
            return suffix
    return word[-2:] if len(word) >= 2 else word

def extract_ngrams(word, n):
    """Extract character n-grams from word."""
    if len(word) < n:
        return []
    return [word[i:i+n] for i in range(len(word) - n + 1)]

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def shannon_entropy(distribution):
    """Compute Shannon entropy of a distribution."""
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy

# ==============================================================================
# DATA LOADING
# ==============================================================================

def load_reference_graph():
    """Load and parse reference_graph.graphml."""
    tree = ET.parse(REFERENCE_GRAPH)
    root = tree.getroot()

    # Define namespace
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}

    # Parse key definitions
    keys = {}
    for key in root.findall('g:key', ns):
        keys[key.get('id')] = key.get('attr.name')

    # Parse nodes
    a_nodes = {}  # folio_id -> {type, word_count, heading, section}
    b_nodes = {}

    graph = root.find('g:graph', ns)
    for node in graph.findall('g:node', ns):
        node_id = node.get('id')
        attrs = {}
        for data in node.findall('g:data', ns):
            key_id = data.get('key')
            attrs[key_id] = data.text

        if attrs.get('type') == 'A':
            folio_id = node_id.replace('A_', '')
            a_nodes[folio_id] = {
                'type': 'A',
                'word_count': int(attrs.get('word_count', 0)),
                'heading': attrs.get('heading', ''),
                'section': attrs.get('section', '')
            }
        elif attrs.get('type') == 'B':
            folio_id = node_id.replace('B_', '')
            b_nodes[folio_id] = {
                'type': 'B',
                'word_count': int(attrs.get('word_count', 0)),
                'section': attrs.get('section', '')
            }

    # Parse edges (B -> A references)
    edges = []
    for edge in graph.findall('g:edge', ns):
        source = edge.get('source').replace('B_', '')
        target = edge.get('target').replace('A_', '')
        attrs = {}
        for data in edge.findall('g:data', ns):
            key_id = data.get('key')
            attrs[key_id] = data.text

        edges.append({
            'source': source,  # B folio
            'target': target,  # A folio
            'count': int(attrs.get('count', 1)),
            'heading_word': attrs.get('heading_word', '')
        })

    return a_nodes, b_nodes, edges

def load_folio_database():
    """Load folio feature database."""
    with open(FOLIO_DATABASE, 'r') as f:
        return json.load(f)

def load_visual_coding():
    """Load visual coding data."""
    try:
        with open(VISUAL_CODING, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'folios': {}}

def load_heading_analysis():
    """Load prior heading analysis."""
    try:
        with open(HEADING_ANALYSIS, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ==============================================================================
# PHASE H1: HEADING INTERNAL STRUCTURE ANALYSIS
# ==============================================================================

def phase_h1_1_length_shape(a_nodes, in_degrees):
    """H1.1 - Length and shape profiling."""
    print("Running Phase H1.1: Length and Shape Profiling...")

    results = {
        'metadata': {
            'phase': 'H1.1',
            'title': 'Length and Shape Profiling',
            'timestamp': datetime.now().isoformat(),
            'heading_count': len(a_nodes)
        },
        'individual_headings': [],
        'length_statistics': {},
        'cv_pattern_distribution': {},
        'prefix_distribution': {},
        'suffix_distribution': {},
        'hub_vs_singleton_comparison': {}
    }

    lengths = []
    cv_patterns = Counter()
    prefixes = Counter()
    suffixes = Counter()

    # Classify by in-degree
    hub_threshold = np.percentile(list(in_degrees.values()), 75) if in_degrees else 0
    isolate_threshold = np.percentile(list(in_degrees.values()), 25) if in_degrees else 0

    hub_lengths = []
    isolate_lengths = []

    for folio_id, attrs in a_nodes.items():
        heading = attrs['heading']
        if not heading or heading == 'r*':
            continue

        length = len(heading)
        cv_pattern = get_cv_pattern(heading)
        prefix = get_prefix(heading)
        suffix = get_suffix(heading)
        in_degree = in_degrees.get(folio_id, 0)

        # Determine category
        if in_degree >= hub_threshold:
            category = 'hub'
            hub_lengths.append(length)
        elif in_degree <= isolate_threshold:
            category = 'isolate'
            isolate_lengths.append(length)
        else:
            category = 'mid'

        lengths.append(length)
        cv_patterns[cv_pattern] += 1
        prefixes[prefix] += 1
        suffixes[suffix] += 1

        results['individual_headings'].append({
            'folio': folio_id,
            'heading': heading,
            'length': length,
            'cv_pattern': cv_pattern,
            'prefix': prefix,
            'suffix': suffix,
            'has_known_prefix': prefix in KNOWN_PREFIXES,
            'has_known_suffix': suffix in KNOWN_SUFFIXES,
            'in_degree': in_degree,
            'category': category
        })

    # Aggregate statistics
    if lengths:
        results['length_statistics'] = {
            'mean': np.mean(lengths),
            'median': np.median(lengths),
            'std': np.std(lengths),
            'min': min(lengths),
            'max': max(lengths),
            'mode': Counter(lengths).most_common(1)[0][0]
        }

        # Length histogram
        results['length_histogram'] = dict(Counter(lengths))

    # CV pattern distribution
    results['cv_pattern_distribution'] = dict(cv_patterns.most_common(20))

    # Prefix/suffix distributions
    results['prefix_distribution'] = dict(prefixes.most_common(20))
    results['suffix_distribution'] = dict(suffixes.most_common(20))

    # Hub vs singleton comparison
    if hub_lengths and isolate_lengths:
        results['hub_vs_singleton_comparison'] = {
            'hub': {
                'count': len(hub_lengths),
                'mean_length': np.mean(hub_lengths),
                'std_length': np.std(hub_lengths)
            },
            'isolate': {
                'count': len(isolate_lengths),
                'mean_length': np.mean(isolate_lengths),
                'std_length': np.std(isolate_lengths)
            },
            'interpretation': 'HUBS_SHORTER' if np.mean(hub_lengths) < np.mean(isolate_lengths) else 'HUBS_LONGER'
        }

    return results


def phase_h1_2_internal_reuse(a_nodes, folio_database):
    """H1.2 - Internal reuse patterns."""
    print("Running Phase H1.2: Internal Reuse Patterns...")

    results = {
        'metadata': {
            'phase': 'H1.2',
            'title': 'Internal Reuse Patterns',
            'timestamp': datetime.now().isoformat()
        },
        'shared_substrings': {},
        'heading_ngram_sets': {},
        'heading_clusters': [],
        'substring_heading_mapping': {}
    }

    # Extract n-grams for each heading
    heading_ngrams = {}
    all_ngrams = defaultdict(list)  # ngram -> list of headings

    for folio_id, attrs in a_nodes.items():
        heading = attrs['heading']
        if not heading or heading == 'r*':
            continue

        ngram_set = set()
        for n in [2, 3, 4]:
            ngrams = extract_ngrams(heading, n)
            ngram_set.update(ngrams)
            for ng in ngrams:
                all_ngrams[ng].append((folio_id, heading))

        heading_ngrams[folio_id] = {
            'heading': heading,
            'ngrams': list(ngram_set)
        }

    results['heading_ngram_sets'] = heading_ngrams

    # Find shared substrings (appearing in 3+ headings)
    shared = {}
    for ngram, occurrences in all_ngrams.items():
        unique_headings = set(h for _, h in occurrences)
        if len(unique_headings) >= 3:
            shared[ngram] = {
                'count': len(unique_headings),
                'headings': list(unique_headings)[:20],  # limit for readability
                'folios': list(set(f for f, _ in occurrences))[:20]
            }

    # Sort by frequency
    results['shared_substrings'] = dict(sorted(shared.items(), key=lambda x: -x[1]['count'])[:50])

    # Cluster headings by n-gram Jaccard similarity
    folios = list(heading_ngrams.keys())
    n = len(folios)

    if n > 2:
        # Build distance matrix
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                set_i = set(heading_ngrams[folios[i]]['ngrams'])
                set_j = set(heading_ngrams[folios[j]]['ngrams'])
                sim = jaccard_similarity(set_i, set_j)
                distances[i, j] = 1 - sim
                distances[j, i] = 1 - sim

        # Hierarchical clustering
        condensed = squareform(distances)
        if len(condensed) > 0:
            Z = linkage(condensed, method='average')

            # Cut at different thresholds
            for threshold in [0.5, 0.7, 0.9]:
                clusters = fcluster(Z, threshold, criterion='distance')
                cluster_groups = defaultdict(list)
                for idx, cluster_id in enumerate(clusters):
                    cluster_groups[int(cluster_id)].append({
                        'folio': folios[idx],
                        'heading': heading_ngrams[folios[idx]]['heading']
                    })

                results['heading_clusters'].append({
                    'threshold': threshold,
                    'num_clusters': len(cluster_groups),
                    'clusters': dict(cluster_groups)
                })

    # Build substring -> heading mapping for analysis
    for ngram, info in results['shared_substrings'].items():
        results['substring_heading_mapping'][ngram] = info['headings']

    return results

# ==============================================================================
# PHASE H2: HEADING VS CLASSIFIER RELATIONSHIP
# ==============================================================================

def phase_h2_1_classifier_signatures(a_nodes, folio_database, h1_2_results):
    """H2.1 - Classifier signatures per heading."""
    print("Running Phase H2.1: Classifier Signatures...")

    results = {
        'metadata': {
            'phase': 'H2.1',
            'title': 'Classifier Signatures per Heading',
            'timestamp': datetime.now().isoformat()
        },
        'heading_signatures': {},
        'entropy_distribution': {},
        'dendrogram_structure': {},
        'substring_cluster_overlap': {}
    }

    # Get prefix distribution for each folio
    currier_a = folio_database.get('currier_a', {})

    # Build signature vectors
    all_prefixes = sorted(KNOWN_PREFIXES)
    signatures = {}
    entropies = {}

    for folio_id, attrs in a_nodes.items():
        heading = attrs['heading']
        if not heading or heading == 'r*':
            continue

        folio_data = currier_a.get(folio_id, {})
        text_features = folio_data.get('text_features', {})
        prefix_dist = text_features.get('prefix_distribution', {})
        word_count = text_features.get('word_count', 1)

        # Build normalized vector
        vector = []
        for prefix in all_prefixes:
            count = prefix_dist.get(prefix, 0)
            vector.append(count / word_count if word_count > 0 else 0)

        signatures[folio_id] = {
            'heading': heading,
            'vector': vector,
            'word_count': word_count
        }

        # Compute entropy
        entropies[folio_id] = shannon_entropy(prefix_dist)

    results['heading_signatures'] = {
        'prefix_order': all_prefixes,
        'signatures': {f: {'heading': s['heading'], 'entropy': entropies.get(f, 0)}
                       for f, s in signatures.items()}
    }

    # Entropy distribution
    entropy_values = list(entropies.values())
    if entropy_values:
        results['entropy_distribution'] = {
            'mean': np.mean(entropy_values),
            'median': np.median(entropy_values),
            'std': np.std(entropy_values),
            'min': min(entropy_values),
            'max': max(entropy_values)
        }

    # Hierarchical clustering by classifier signature
    folios = list(signatures.keys())
    n = len(folios)

    if n > 2:
        # Build cosine distance matrix
        vectors = np.array([signatures[f]['vector'] for f in folios])

        # Normalize rows
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors_norm = vectors / norms

        # Cosine similarity -> distance
        sim_matrix = vectors_norm @ vectors_norm.T
        dist_matrix = 1 - sim_matrix
        np.fill_diagonal(dist_matrix, 0)

        # Clustering
        condensed = squareform(dist_matrix)
        if len(condensed) > 0:
            Z = linkage(condensed, method='average')

            # Store dendrogram structure
            results['dendrogram_structure'] = {
                'folios': folios,
                'headings': [signatures[f]['heading'] for f in folios],
                'linkage_matrix': Z.tolist()
            }

            # Cluster at threshold 0.5
            clusters = fcluster(Z, 0.5, criterion='distance')
            cluster_groups = defaultdict(list)
            for idx, cluster_id in enumerate(clusters):
                cluster_groups[int(cluster_id)].append({
                    'folio': folios[idx],
                    'heading': signatures[folios[idx]]['heading']
                })

            results['classifier_clusters'] = dict(cluster_groups)

    # Check if headings with shared substrings cluster together
    if h1_2_results and 'shared_substrings' in h1_2_results:
        substring_overlap = {}
        for ngram, info in h1_2_results['shared_substrings'].items():
            if info['count'] >= 3:
                # Find which classifier clusters these headings belong to
                if 'classifier_clusters' in results:
                    heading_clusters = {}
                    for cluster_id, members in results['classifier_clusters'].items():
                        for m in members:
                            if m['heading'] in info['headings']:
                                heading_clusters[m['heading']] = cluster_id

                    if heading_clusters:
                        cluster_ids = list(heading_clusters.values())
                        substring_overlap[ngram] = {
                            'headings': list(heading_clusters.keys()),
                            'clusters': cluster_ids,
                            'same_cluster': len(set(cluster_ids)) == 1
                        }

        results['substring_cluster_overlap'] = substring_overlap

    return results


def phase_h2_2_hub_singleton_contrast(a_nodes, folio_database, in_degrees, h2_1_results):
    """H2.2 - Hub vs singleton contrast."""
    print("Running Phase H2.2: Hub vs Singleton Contrast...")

    results = {
        'metadata': {
            'phase': 'H2.2',
            'title': 'Hub vs Singleton Contrast',
            'timestamp': datetime.now().isoformat()
        },
        'group_statistics': {},
        'comparison': {},
        'interpretation': ''
    }

    currier_a = folio_database.get('currier_a', {})

    # Partition by in-degree
    degree_values = list(in_degrees.values())
    if not degree_values:
        results['error'] = 'No in-degree data available'
        return results

    hub_threshold = np.percentile(degree_values, 75)
    isolate_threshold = np.percentile(degree_values, 25)

    groups = {'hub': [], 'mid': [], 'isolate': []}

    for folio_id, attrs in a_nodes.items():
        heading = attrs['heading']
        if not heading or heading == 'r*':
            continue

        in_degree = in_degrees.get(folio_id, 0)

        if in_degree >= hub_threshold:
            category = 'hub'
        elif in_degree <= isolate_threshold:
            category = 'isolate'
        else:
            category = 'mid'

        folio_data = currier_a.get(folio_id, {})
        text_features = folio_data.get('text_features', {})
        prefix_dist = text_features.get('prefix_distribution', {})

        groups[category].append({
            'folio': folio_id,
            'heading': heading,
            'heading_length': len(heading),
            'word_count': text_features.get('word_count', 0),
            'classifier_entropy': shannon_entropy(prefix_dist),
            'distinct_classifiers': len([k for k, v in prefix_dist.items() if v > 0]),
            'in_degree': in_degree
        })

    # Compute group statistics
    for group_name, members in groups.items():
        if not members:
            continue

        results['group_statistics'][group_name] = {
            'count': len(members),
            'mean_heading_length': np.mean([m['heading_length'] for m in members]),
            'mean_word_count': np.mean([m['word_count'] for m in members]),
            'mean_classifier_entropy': np.mean([m['classifier_entropy'] for m in members]),
            'mean_distinct_classifiers': np.mean([m['distinct_classifiers'] for m in members]),
            'mean_in_degree': np.mean([m['in_degree'] for m in members]),
            'members': members[:10]  # sample
        }

    # Comparison
    hub_stats = results['group_statistics'].get('hub', {})
    isolate_stats = results['group_statistics'].get('isolate', {})

    if hub_stats and isolate_stats:
        results['comparison'] = {
            'heading_length_diff': hub_stats.get('mean_heading_length', 0) - isolate_stats.get('mean_heading_length', 0),
            'entropy_diff': hub_stats.get('mean_classifier_entropy', 0) - isolate_stats.get('mean_classifier_entropy', 0),
            'word_count_diff': hub_stats.get('mean_word_count', 0) - isolate_stats.get('mean_word_count', 0)
        }

        # Interpretation
        if results['comparison']['heading_length_diff'] < -0.5:
            length_interp = 'Hubs have SHORTER headings'
        elif results['comparison']['heading_length_diff'] > 0.5:
            length_interp = 'Hubs have LONGER headings'
        else:
            length_interp = 'Heading lengths SIMILAR'

        if results['comparison']['entropy_diff'] < -0.2:
            entropy_interp = 'Hubs have MORE FOCUSED classifier profiles'
        elif results['comparison']['entropy_diff'] > 0.2:
            entropy_interp = 'Hubs have MORE DIVERSE classifier profiles'
        else:
            entropy_interp = 'Classifier entropy SIMILAR'

        results['interpretation'] = f'{length_interp}; {entropy_interp}'

    return results

# ==============================================================================
# PHASE H3: VISUAL COHERENCE TESTS
# ==============================================================================

def phase_h3_1_repeated_heading_visual(a_nodes, visual_data):
    """H3.1 - Visual consistency for repeated headings."""
    print("Running Phase H3.1: Repeated Heading Visual Consistency...")

    results = {
        'metadata': {
            'phase': 'H3.1',
            'title': 'Repeated Heading Visual Consistency',
            'timestamp': datetime.now().isoformat()
        },
        'repeated_headings': {},
        'visual_consistency_tests': [],
        'random_baseline': {},
        'blocked_headings': []
    }

    # Find repeated headings
    heading_to_folios = defaultdict(list)
    for folio_id, attrs in a_nodes.items():
        heading = attrs['heading']
        if heading and heading != 'r*':
            heading_to_folios[heading].append(folio_id)

    repeated = {h: folios for h, folios in heading_to_folios.items() if len(folios) > 1}
    results['repeated_headings'] = repeated

    # Get visual data
    coded_folios = set(visual_data.get('folios', {}).keys())

    # Compute random baseline similarity
    visual_vectors = {}
    for folio_id, folio_data in visual_data.get('folios', {}).items():
        vf = folio_data.get('visual_features', {})
        visual_vectors[folio_id] = vf

    if len(visual_vectors) >= 2:
        # Random pairwise similarities
        random_sims = []
        folio_list = list(visual_vectors.keys())
        for i in range(min(100, len(folio_list) * (len(folio_list) - 1) // 2)):
            import random
            f1, f2 = random.sample(folio_list, 2)
            sim = compute_visual_similarity(visual_vectors[f1], visual_vectors[f2])
            random_sims.append(sim)

        if random_sims:
            results['random_baseline'] = {
                'mean': np.mean(random_sims),
                'std': np.std(random_sims),
                'samples': len(random_sims)
            }

    # Test each repeated heading
    for heading, folios in repeated.items():
        coded = [f for f in folios if f in coded_folios]
        not_coded = [f for f in folios if f not in coded_folios]

        if len(coded) < 2:
            results['blocked_headings'].append({
                'heading': heading,
                'folios': folios,
                'coded': coded,
                'not_coded': not_coded,
                'reason': 'Insufficient visual data (need 2+ coded folios)'
            })
            continue

        # Compute pairwise visual similarity
        pairwise_sims = []
        for i in range(len(coded)):
            for j in range(i + 1, len(coded)):
                sim = compute_visual_similarity(
                    visual_vectors.get(coded[i], {}),
                    visual_vectors.get(coded[j], {})
                )
                pairwise_sims.append({
                    'folio1': coded[i],
                    'folio2': coded[j],
                    'similarity': sim
                })

        mean_sim = np.mean([p['similarity'] for p in pairwise_sims]) if pairwise_sims else 0

        # Compare to baseline
        baseline = results['random_baseline']
        if baseline:
            z_score = (mean_sim - baseline['mean']) / baseline['std'] if baseline['std'] > 0 else 0
            if z_score > 2:
                interpretation = 'HIGH_CONSISTENCY (entity identity)'
            elif z_score > 1:
                interpretation = 'MODERATE_CONSISTENCY (possible entity)'
            elif z_score > -1:
                interpretation = 'AVERAGE_CONSISTENCY (category label)'
            else:
                interpretation = 'LOW_CONSISTENCY (functional role or arbitrary)'
        else:
            z_score = 0
            interpretation = 'UNKNOWN (no baseline)'

        results['visual_consistency_tests'].append({
            'heading': heading,
            'folios': folios,
            'coded_folios': coded,
            'pairwise_similarities': pairwise_sims,
            'mean_similarity': mean_sim,
            'z_score': z_score,
            'interpretation': interpretation
        })

    return results


def compute_visual_similarity(vf1, vf2):
    """Compute similarity between two visual feature dictionaries."""
    if not vf1 or not vf2:
        return 0.0

    matching = 0
    total = 0

    for key in set(vf1.keys()) | set(vf2.keys()):
        val1 = vf1.get(key)
        val2 = vf2.get(key)

        if val1 is None or val2 is None:
            continue
        if val1 == 'NA' or val2 == 'NA':
            continue

        total += 1
        if val1 == val2:
            matching += 1

    return matching / total if total > 0 else 0.0


def phase_h3_2_visual_neighborhoods(a_nodes, visual_data, h2_1_results):
    """H3.2 - Visual neighborhoods."""
    print("Running Phase H3.2: Visual Neighborhoods...")

    results = {
        'metadata': {
            'phase': 'H3.2',
            'title': 'Visual Neighborhoods',
            'timestamp': datetime.now().isoformat()
        },
        'coded_folios': [],
        'visual_clusters': [],
        'heading_cluster_analysis': [],
        'status': ''
    }

    coded_folios = list(visual_data.get('folios', {}).keys())
    results['coded_folios'] = coded_folios

    if len(coded_folios) < 3:
        results['status'] = 'BLOCKED - insufficient visual data'
        return results

    # Build feature vectors for clustering
    feature_names = [
        'root_type', 'stem_type', 'leaf_shape', 'leaf_arrangement',
        'flower_shape', 'plant_symmetry', 'overall_complexity'
    ]

    # Encode features as numbers
    feature_encodings = defaultdict(dict)
    for folio_id in coded_folios:
        folio_data = visual_data['folios'].get(folio_id, {})
        vf = folio_data.get('visual_features', {})
        for feature in feature_names:
            val = vf.get(feature, 'UNKNOWN')
            if val not in feature_encodings[feature]:
                feature_encodings[feature][val] = len(feature_encodings[feature])

    # Build numeric matrix
    vectors = []
    for folio_id in coded_folios:
        folio_data = visual_data['folios'].get(folio_id, {})
        vf = folio_data.get('visual_features', {})
        vec = []
        for feature in feature_names:
            val = vf.get(feature, 'UNKNOWN')
            vec.append(feature_encodings[feature].get(val, 0))
        vectors.append(vec)

    vectors = np.array(vectors)

    # Compute distance matrix (Hamming-like)
    n = len(coded_folios)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sum(vectors[i] != vectors[j]) / len(feature_names)
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist

    # Hierarchical clustering
    condensed = squareform(dist_matrix)
    if len(condensed) > 0:
        Z = linkage(condensed, method='average')

        # Cut at 0.5 threshold
        clusters = fcluster(Z, 0.5, criterion='distance')
        cluster_groups = defaultdict(list)

        for idx, cluster_id in enumerate(clusters):
            folio_id = coded_folios[idx]
            heading = a_nodes.get(folio_id, {}).get('heading', '')
            cluster_groups[int(cluster_id)].append({
                'folio': folio_id,
                'heading': heading
            })

        results['visual_clusters'] = dict(cluster_groups)

        # Analyze headings within each cluster
        for cluster_id, members in cluster_groups.items():
            headings = [m['heading'] for m in members if m['heading']]

            # Check for shared n-grams
            shared_ngrams = set()
            if len(headings) >= 2:
                ngram_sets = [set(extract_ngrams(h, 2) + extract_ngrams(h, 3)) for h in headings]
                shared_ngrams = set.intersection(*ngram_sets) if ngram_sets else set()

            results['heading_cluster_analysis'].append({
                'cluster_id': cluster_id,
                'size': len(members),
                'headings': headings,
                'unique_headings': len(set(headings)),
                'shared_ngrams': list(shared_ngrams)[:10],
                'heading_diversity': len(set(headings)) / len(headings) if headings else 0
            })

    results['status'] = 'COMPLETE'
    return results

# ==============================================================================
# PHASE H4: CURRIER B REFERENCE SEMANTICS
# ==============================================================================

def phase_h4_1_cocitation(a_nodes, edges, visual_data, h2_1_results):
    """H4.1 - Co-citation structure."""
    print("Running Phase H4.1: Co-Citation Structure...")

    results = {
        'metadata': {
            'phase': 'H4.1',
            'title': 'Co-Citation Structure',
            'timestamp': datetime.now().isoformat()
        },
        'cocitation_matrix': {},
        'strongly_cocited_pairs': [],
        'cocitation_analysis': []
    }

    # Build B entry -> A references mapping
    b_to_a = defaultdict(list)
    for edge in edges:
        b_to_a[edge['source']].append(edge['target'])

    # Build co-citation matrix
    cocitation = defaultdict(lambda: defaultdict(int))
    for b_folio, a_refs in b_to_a.items():
        unique_a = list(set(a_refs))
        for i in range(len(unique_a)):
            for j in range(i + 1, len(unique_a)):
                a1, a2 = sorted([unique_a[i], unique_a[j]])
                cocitation[a1][a2] += 1

    # Convert to serializable format
    results['cocitation_matrix'] = {
        a1: dict(a2_counts) for a1, a2_counts in cocitation.items()
    }

    # Find strongly co-cited pairs (count >= 2)
    strong_pairs = []
    for a1, a2_counts in cocitation.items():
        for a2, count in a2_counts.items():
            if count >= 2:
                h1 = a_nodes.get(a1, {}).get('heading', '')
                h2 = a_nodes.get(a2, {}).get('heading', '')
                strong_pairs.append({
                    'folio1': a1,
                    'folio2': a2,
                    'heading1': h1,
                    'heading2': h2,
                    'cocitation_count': count
                })

    results['strongly_cocited_pairs'] = sorted(strong_pairs, key=lambda x: -x['cocitation_count'])

    # Analyze co-cited pairs
    coded_folios = set(visual_data.get('folios', {}).keys())

    for pair in results['strongly_cocited_pairs'][:20]:
        analysis = {
            'pair': f"{pair['heading1']} <-> {pair['heading2']}",
            'cocitation_count': pair['cocitation_count']
        }

        # Check visual similarity if both coded
        if pair['folio1'] in coded_folios and pair['folio2'] in coded_folios:
            vf1 = visual_data['folios'][pair['folio1']].get('visual_features', {})
            vf2 = visual_data['folios'][pair['folio2']].get('visual_features', {})
            analysis['visual_similarity'] = compute_visual_similarity(vf1, vf2)
            analysis['visual_data_available'] = True
        else:
            analysis['visual_data_available'] = False

        # Check n-gram overlap
        h1_ngrams = set(extract_ngrams(pair['heading1'], 2) + extract_ngrams(pair['heading1'], 3))
        h2_ngrams = set(extract_ngrams(pair['heading2'], 2) + extract_ngrams(pair['heading2'], 3))
        shared = h1_ngrams & h2_ngrams
        analysis['shared_ngrams'] = list(shared)[:10]
        analysis['ngram_overlap'] = len(shared) / len(h1_ngrams | h2_ngrams) if (h1_ngrams | h2_ngrams) else 0

        results['cocitation_analysis'].append(analysis)

    return results


def phase_h4_2_reference_context(a_nodes, b_nodes, edges, in_degrees):
    """H4.2 - Reference context analysis."""
    print("Running Phase H4.2: Reference Context Analysis...")

    results = {
        'metadata': {
            'phase': 'H4.2',
            'title': 'Reference Context Analysis',
            'timestamp': datetime.now().isoformat()
        },
        'b_entry_analysis': [],
        'a_heading_roles': {},
        'primary_secondary_correlation': {}
    }

    # Analyze each B entry
    b_to_refs = defaultdict(list)
    for edge in edges:
        b_to_refs[edge['source']].append({
            'target': edge['target'],
            'count': edge['count'],
            'heading_word': edge['heading_word']
        })

    for b_folio, refs in b_to_refs.items():
        if not refs:
            continue

        # Sort by count
        refs_sorted = sorted(refs, key=lambda x: -x['count'])
        primary = refs_sorted[0]
        secondary = refs_sorted[1:] if len(refs_sorted) > 1 else []

        results['b_entry_analysis'].append({
            'b_folio': b_folio,
            'word_count': b_nodes.get(b_folio, {}).get('word_count', 0),
            'distinct_a_refs': len(set(r['target'] for r in refs)),
            'primary_reference': {
                'a_folio': primary['target'],
                'heading': a_nodes.get(primary['target'], {}).get('heading', ''),
                'count': primary['count']
            },
            'secondary_references': [{
                'a_folio': r['target'],
                'heading': a_nodes.get(r['target'], {}).get('heading', ''),
                'count': r['count']
            } for r in secondary[:5]]
        })

    # Analyze A heading roles (primary vs secondary)
    primary_counts = defaultdict(int)
    secondary_counts = defaultdict(int)

    for analysis in results['b_entry_analysis']:
        primary_folio = analysis['primary_reference']['a_folio']
        primary_counts[primary_folio] += 1

        for sec in analysis['secondary_references']:
            secondary_counts[sec['a_folio']] += 1

    for folio_id, attrs in a_nodes.items():
        heading = attrs['heading']
        if not heading or heading == 'r*':
            continue

        p_count = primary_counts.get(folio_id, 0)
        s_count = secondary_counts.get(folio_id, 0)
        total = p_count + s_count

        results['a_heading_roles'][folio_id] = {
            'heading': heading,
            'primary_count': p_count,
            'secondary_count': s_count,
            'total_references': total,
            'primary_rate': p_count / total if total > 0 else 0,
            'in_degree': in_degrees.get(folio_id, 0)
        }

    # Correlation: in_degree vs primary_rate
    roles_with_refs = [r for r in results['a_heading_roles'].values() if r['total_references'] > 0]
    if len(roles_with_refs) >= 5:
        in_degs = [r['in_degree'] for r in roles_with_refs]
        primary_rates = [r['primary_rate'] for r in roles_with_refs]

        if np.std(in_degs) > 0 and np.std(primary_rates) > 0:
            correlation = np.corrcoef(in_degs, primary_rates)[0, 1]
            results['primary_secondary_correlation'] = {
                'pearson_r': correlation,
                'interpretation': 'Hubs more often PRIMARY' if correlation > 0.2 else
                                 'Hubs more often SECONDARY' if correlation < -0.2 else 'NO_CORRELATION'
            }

    return results

# ==============================================================================
# PHASE H5: ALIAS AND IDENTITY TESTS
# ==============================================================================

def phase_h5_1_mutual_exclusivity(a_nodes, edges, visual_data, h2_1_results, folio_database):
    """H5.1 - Mutual exclusivity test."""
    print("Running Phase H5.1: Mutual Exclusivity...")

    results = {
        'metadata': {
            'phase': 'H5.1',
            'title': 'Mutual Exclusivity',
            'timestamp': datetime.now().isoformat()
        },
        'candidate_aliases': [],
        'total_pairs_tested': 0
    }

    # Build co-occurrence matrix from B entries
    b_to_a = defaultdict(set)
    for edge in edges:
        b_to_a[edge['source']].add(edge['target'])

    # Get classifier signatures
    currier_a = folio_database.get('currier_a', {})
    signatures = {}
    for folio_id, attrs in a_nodes.items():
        folio_data = currier_a.get(folio_id, {})
        text_features = folio_data.get('text_features', {})
        prefix_dist = text_features.get('prefix_distribution', {})
        word_count = text_features.get('word_count', 1)

        vec = []
        for prefix in KNOWN_PREFIXES:
            count = prefix_dist.get(prefix, 0)
            vec.append(count / word_count if word_count > 0 else 0)
        signatures[folio_id] = vec

    # Visual data
    coded_folios = set(visual_data.get('folios', {}).keys())

    # Test all pairs
    folios = [f for f in a_nodes.keys() if a_nodes[f].get('heading') and a_nodes[f]['heading'] != 'r*']

    pairs_tested = 0
    candidates = []

    for i in range(len(folios)):
        for j in range(i + 1, len(folios)):
            f1, f2 = folios[i], folios[j]
            pairs_tested += 1

            # Check if they ever co-occur
            co_occur = False
            for b_refs in b_to_a.values():
                if f1 in b_refs and f2 in b_refs:
                    co_occur = True
                    break

            if co_occur:
                continue  # Not mutually exclusive

            # Check classifier similarity
            if f1 in signatures and f2 in signatures:
                sim = cosine_similarity(signatures[f1], signatures[f2])
                if sim < 0.8:
                    continue  # Not similar enough
            else:
                continue

            # Check visual similarity (if available)
            visual_sim = None
            if f1 in coded_folios and f2 in coded_folios:
                vf1 = visual_data['folios'][f1].get('visual_features', {})
                vf2 = visual_data['folios'][f2].get('visual_features', {})
                visual_sim = compute_visual_similarity(vf1, vf2)

            candidates.append({
                'folio1': f1,
                'folio2': f2,
                'heading1': a_nodes[f1]['heading'],
                'heading2': a_nodes[f2]['heading'],
                'classifier_similarity': sim,
                'visual_similarity': visual_sim,
                'mutually_exclusive': True
            })

    results['total_pairs_tested'] = pairs_tested
    results['candidate_aliases'] = sorted(candidates, key=lambda x: -x['classifier_similarity'])[:20]

    return results


def phase_h5_2_cardinality_patterns(a_nodes, visual_data, h3_2_results):
    """H5.2 - Cardinality patterns."""
    print("Running Phase H5.2: Cardinality Patterns...")

    results = {
        'metadata': {
            'phase': 'H5.2',
            'title': 'Cardinality Patterns',
            'timestamp': datetime.now().isoformat()
        },
        'one_heading_many_clusters': [],
        'many_headings_one_cluster': [],
        'interpretation': ''
    }

    if not h3_2_results or 'visual_clusters' not in h3_2_results:
        results['status'] = 'BLOCKED - no visual clusters available'
        return results

    visual_clusters = h3_2_results.get('visual_clusters', {})

    # Find repeated headings across clusters
    heading_to_clusters = defaultdict(list)
    cluster_headings = {}

    for cluster_id, members in visual_clusters.items():
        headings = [m['heading'] for m in members if m['heading']]
        cluster_headings[cluster_id] = headings

        for m in members:
            if m['heading']:
                heading_to_clusters[m['heading']].append(cluster_id)

    # One heading -> many clusters
    for heading, clusters in heading_to_clusters.items():
        unique_clusters = list(set(clusters))
        if len(unique_clusters) > 1:
            results['one_heading_many_clusters'].append({
                'heading': heading,
                'cluster_ids': unique_clusters,
                'num_clusters': len(unique_clusters),
                'interpretation': 'CATEGORY_LABEL (appears in visually diverse clusters)'
            })

    # Many headings -> one cluster
    for cluster_id, headings in cluster_headings.items():
        unique_headings = list(set(headings))
        if len(unique_headings) > 1 and len(headings) >= 2:
            results['many_headings_one_cluster'].append({
                'cluster_id': cluster_id,
                'headings': unique_headings,
                'num_headings': len(unique_headings),
                'interpretation': 'POSSIBLE_ALIASES or SUBTYPES'
            })

    # Overall interpretation
    one_many_count = len(results['one_heading_many_clusters'])
    many_one_count = len(results['many_headings_one_cluster'])

    if one_many_count > many_one_count:
        results['interpretation'] = 'CATEGORY_LABELS_DOMINANT'
    elif many_one_count > one_many_count:
        results['interpretation'] = 'ALIASES_OR_SUBTYPES_DOMINANT'
    else:
        results['interpretation'] = 'MIXED_PATTERNS'

    return results

# ==============================================================================
# PHASE H6: DECISION MATRIX
# ==============================================================================

def phase_h6_decision_matrix(h1_1, h1_2, h2_1, h2_2, h3_1, h3_2, h4_1, h4_2, h5_1, h5_2):
    """H6 - Decision matrix."""
    print("Running Phase H6: Decision Matrix...")

    results = {
        'metadata': {
            'phase': 'H6',
            'title': 'Decision Matrix',
            'timestamp': datetime.now().isoformat()
        },
        'evidence_summary': {},
        'model_scores': {},
        'classification': '',
        'confidence': '',
        'well_fitting_headings': [],
        'anomalous_headings': []
    }

    # Model definitions:
    # A: Literal entity names - high visual consistency, visual clusters predict headings
    # B: Category/class labels - visual diversity within repeated headings, classifier stability
    # C: Functional roles - no visual coherence, co-citation = substitutability
    # D: Arbitrary identifiers - no patterns

    scores = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    evidence = {'A': [], 'B': [], 'C': [], 'D': []}

    # H1: Structural diversity
    if h1_1:
        structural_diversity = h1_1.get('structural_patterns', {}).get('structural_diversity', {})
        if structural_diversity.get('is_diverse'):
            evidence['A'].append('Headings are structurally diverse (consistent with names)')
            scores['A'] += 1
        else:
            evidence['B'].append('Headings show structural patterns (consistent with codes)')
            scores['B'] += 1

    # H1.2: Shared substrings
    if h1_2:
        shared = h1_2.get('shared_substrings', {})
        if len(shared) > 10:
            evidence['B'].append(f'Many shared substrings ({len(shared)}) - morphological system')
            scores['B'] += 1
        else:
            evidence['A'].append('Few shared substrings - unique names')
            scores['A'] += 1

    # H2.2: Hub vs singleton
    if h2_2:
        interp = h2_2.get('interpretation', '')
        if 'SHORTER' in interp:
            evidence['B'].append('Hubs have shorter headings (generic categories)')
            scores['B'] += 1
        elif 'LONGER' in interp:
            evidence['A'].append('Hubs have longer headings (specific entities)')
            scores['A'] += 1

    # H3.1: Visual consistency for repeated headings
    if h3_1:
        tests = h3_1.get('visual_consistency_tests', [])
        high_consistency = sum(1 for t in tests if 'HIGH' in t.get('interpretation', ''))
        low_consistency = sum(1 for t in tests if 'LOW' in t.get('interpretation', '') or 'AVERAGE' in t.get('interpretation', ''))

        if high_consistency > low_consistency:
            evidence['A'].append(f'Repeated headings show HIGH visual consistency ({high_consistency} cases)')
            scores['A'] += 2
        elif low_consistency > high_consistency:
            evidence['B'].append(f'Repeated headings show LOW visual consistency ({low_consistency} cases)')
            scores['B'] += 2

    # H3.2: Visual neighborhoods
    if h3_2:
        cluster_analysis = h3_2.get('heading_cluster_analysis', [])
        diverse_clusters = sum(1 for c in cluster_analysis if c.get('heading_diversity', 0) > 0.5)

        if diverse_clusters > len(cluster_analysis) / 2:
            evidence['A'].append('Visual clusters have diverse headings (entity names)')
            scores['A'] += 1
        else:
            evidence['B'].append('Visual clusters have similar headings (categories)')
            scores['B'] += 1

    # H4.1: Co-citation
    if h4_1:
        strong_pairs = h4_1.get('strongly_cocited_pairs', [])
        if len(strong_pairs) > 5:
            evidence['B'].append(f'Many strongly co-cited pairs ({len(strong_pairs)}) - category system')
            scores['B'] += 1

        # Check if co-cited pairs are visually similar
        analysis = h4_1.get('cocitation_analysis', [])
        visual_similar_cocited = sum(1 for a in analysis if a.get('visual_similarity', 0) > 0.5)
        if visual_similar_cocited > len(analysis) / 2:
            evidence['B'].append('Co-cited pairs are visually similar (natural categories)')
            scores['B'] += 1
        else:
            evidence['C'].append('Co-cited pairs are visually dissimilar (functional grouping)')
            scores['C'] += 1

    # H5.1: Mutual exclusivity
    if h5_1:
        candidates = h5_1.get('candidate_aliases', [])
        if len(candidates) > 3:
            evidence['B'].append(f'{len(candidates)} candidate alias pairs found')
            scores['B'] += 1

    # H5.2: Cardinality patterns
    if h5_2:
        interp = h5_2.get('interpretation', '')
        if 'CATEGORY' in interp:
            evidence['B'].append('One-to-many cardinality dominant (category labels)')
            scores['B'] += 2
        elif 'ALIASES' in interp:
            evidence['A'].append('Many-to-one cardinality (possible aliases for entities)')
            scores['A'] += 1

    results['evidence_summary'] = evidence
    results['model_scores'] = scores

    # Determine classification
    max_score = max(scores.values())
    winners = [model for model, score in scores.items() if score == max_score]

    if len(winners) == 1:
        results['classification'] = winners[0]
        if max_score >= 5:
            results['confidence'] = 'HIGH'
        elif max_score >= 3:
            results['confidence'] = 'MEDIUM'
        else:
            results['confidence'] = 'LOW'
    else:
        results['classification'] = f"MIXED ({'/'.join(winners)})"
        results['confidence'] = 'LOW'

    # Model descriptions
    model_descriptions = {
        'A': 'Literal entity names (each heading identifies a unique entity)',
        'B': 'Category/class labels (headings identify categories or types)',
        'C': 'Functional roles (headings encode function, not identity)',
        'D': 'Arbitrary identifiers (no systematic pattern)'
    }
    results['classification_description'] = model_descriptions.get(results['classification'], 'Mixed model')

    return results

# ==============================================================================
# PHASE H7: RECONCILIATION WITH VISUAL CORRELATIONS
# ==============================================================================

def phase_h7_reconciliation(a_nodes, visual_data, folio_database, in_degrees, h6_results):
    """H7 - Reconciliation with visual correlations."""
    print("Running Phase H7: Reconciliation with Visual Correlations...")

    results = {
        'metadata': {
            'phase': 'H7',
            'title': 'Reconciliation with Visual Correlations',
            'timestamp': datetime.now().isoformat()
        },
        'prior_correlations': {
            'ko_leaf': {'V': 0.61, 'percentile': 83.6},
            'po_root': {'V': 0.20, 'percentile': 0}
        },
        'hub_vs_singleton_analysis': {},
        'interpretation': ''
    }

    coded_folios = set(visual_data.get('folios', {}).keys())
    currier_a = folio_database.get('currier_a', {})

    # Partition coded folios by hub/singleton status
    hub_threshold = np.percentile(list(in_degrees.values()), 75) if in_degrees else 0
    isolate_threshold = np.percentile(list(in_degrees.values()), 25) if in_degrees else 0

    hub_folios = []
    isolate_folios = []

    for folio_id in coded_folios:
        in_deg = in_degrees.get(folio_id, 0)
        if in_deg >= hub_threshold:
            hub_folios.append(folio_id)
        elif in_deg <= isolate_threshold:
            isolate_folios.append(folio_id)

    # Analyze ko prefix distribution
    ko_in_hubs = 0
    ko_in_isolates = 0
    po_in_hubs = 0
    po_in_isolates = 0

    for folio_id in hub_folios:
        folio_data = visual_data['folios'].get(folio_id, {})
        prefix = folio_data.get('heading_prefix', '')
        if prefix == 'ko':
            ko_in_hubs += 1
        if prefix == 'po':
            po_in_hubs += 1

    for folio_id in isolate_folios:
        folio_data = visual_data['folios'].get(folio_id, {})
        prefix = folio_data.get('heading_prefix', '')
        if prefix == 'ko':
            ko_in_isolates += 1
        if prefix == 'po':
            po_in_isolates += 1

    results['hub_vs_singleton_analysis'] = {
        'hub_folios_coded': len(hub_folios),
        'isolate_folios_coded': len(isolate_folios),
        'ko_prefix': {
            'in_hubs': ko_in_hubs,
            'in_isolates': ko_in_isolates,
            'distribution': 'HUB_CONCENTRATED' if ko_in_hubs > ko_in_isolates else
                          'ISOLATE_CONCENTRATED' if ko_in_isolates > ko_in_hubs else 'EVEN'
        },
        'po_prefix': {
            'in_hubs': po_in_hubs,
            'in_isolates': po_in_isolates,
            'distribution': 'HUB_CONCENTRATED' if po_in_hubs > po_in_isolates else
                          'ISOLATE_CONCENTRATED' if po_in_isolates > po_in_hubs else 'EVEN'
        }
    }

    # Interpretation based on H6 classification
    classification = h6_results.get('classification', '')

    if classification == 'B':
        results['interpretation'] = (
            'Heading system classified as CATEGORY LABELS. '
            'Visual correlations (ko-leaf, po-root) should be interpreted at category level, '
            'not entity level. Correlations may reflect morphological marking of plant categories.'
        )
    elif classification == 'A':
        results['interpretation'] = (
            'Heading system classified as ENTITY NAMES. '
            'Visual correlations may reflect consistent naming conventions for plant features.'
        )
    else:
        results['interpretation'] = (
            f'Heading system classification is {classification}. '
            'Visual correlation interpretation remains ambiguous.'
        )

    return results

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print("=" * 70)
    print("HEADINGS DEEP DIVE ANALYSIS")
    print("Voynich Manuscript - Phase H1-H7")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    a_nodes, b_nodes, edges = load_reference_graph()
    folio_database = load_folio_database()
    visual_data = load_visual_coding()

    print(f"  Loaded {len(a_nodes)} A nodes, {len(b_nodes)} B nodes, {len(edges)} edges")
    print(f"  Visual coding available for {len(visual_data.get('folios', {}))} folios")
    print()

    # Compute in-degrees
    in_degrees = defaultdict(int)
    for edge in edges:
        in_degrees[edge['target']] += edge['count']

    # Phase H1
    h1_1_results = phase_h1_1_length_shape(a_nodes, in_degrees)
    with open('h1_1_length_shape_profile.json', 'w') as f:
        json.dump(h1_1_results, f, indent=2)
    print(f"  Saved h1_1_length_shape_profile.json")

    h1_2_results = phase_h1_2_internal_reuse(a_nodes, folio_database)
    with open('h1_2_internal_reuse.json', 'w') as f:
        json.dump(h1_2_results, f, indent=2)
    print(f"  Saved h1_2_internal_reuse.json")

    # Phase H2
    h2_1_results = phase_h2_1_classifier_signatures(a_nodes, folio_database, h1_2_results)
    with open('h2_1_classifier_signatures.json', 'w') as f:
        json.dump(h2_1_results, f, indent=2)
    print(f"  Saved h2_1_classifier_signatures.json")

    h2_2_results = phase_h2_2_hub_singleton_contrast(a_nodes, folio_database, in_degrees, h2_1_results)
    with open('h2_2_hub_singleton_contrast.json', 'w') as f:
        json.dump(h2_2_results, f, indent=2)
    print(f"  Saved h2_2_hub_singleton_contrast.json")

    # Phase H3
    h3_1_results = phase_h3_1_repeated_heading_visual(a_nodes, visual_data)
    with open('h3_1_repeated_heading_visual_consistency.json', 'w') as f:
        json.dump(h3_1_results, f, indent=2)
    print(f"  Saved h3_1_repeated_heading_visual_consistency.json")

    h3_2_results = phase_h3_2_visual_neighborhoods(a_nodes, visual_data, h2_1_results)
    with open('h3_2_visual_neighborhoods.json', 'w') as f:
        json.dump(h3_2_results, f, indent=2)
    print(f"  Saved h3_2_visual_neighborhoods.json")

    # Phase H4
    h4_1_results = phase_h4_1_cocitation(a_nodes, edges, visual_data, h2_1_results)
    with open('h4_1_cocitation_structure.json', 'w') as f:
        json.dump(h4_1_results, f, indent=2)
    print(f"  Saved h4_1_cocitation_structure.json")

    h4_2_results = phase_h4_2_reference_context(a_nodes, b_nodes, edges, in_degrees)
    with open('h4_2_reference_context.json', 'w') as f:
        json.dump(h4_2_results, f, indent=2)
    print(f"  Saved h4_2_reference_context.json")

    # Phase H5
    h5_1_results = phase_h5_1_mutual_exclusivity(a_nodes, edges, visual_data, h2_1_results, folio_database)
    with open('h5_1_mutual_exclusivity.json', 'w') as f:
        json.dump(h5_1_results, f, indent=2)
    print(f"  Saved h5_1_mutual_exclusivity.json")

    h5_2_results = phase_h5_2_cardinality_patterns(a_nodes, visual_data, h3_2_results)
    with open('h5_2_cardinality_patterns.json', 'w') as f:
        json.dump(h5_2_results, f, indent=2)
    print(f"  Saved h5_2_cardinality_patterns.json")

    # Phase H6
    h6_results = phase_h6_decision_matrix(
        h1_1_results, h1_2_results, h2_1_results, h2_2_results,
        h3_1_results, h3_2_results, h4_1_results, h4_2_results,
        h5_1_results, h5_2_results
    )
    with open('h6_decision_matrix.json', 'w') as f:
        json.dump(h6_results, f, indent=2)
    print(f"  Saved h6_decision_matrix.json")

    # Phase H7
    h7_results = phase_h7_reconciliation(a_nodes, visual_data, folio_database, in_degrees, h6_results)
    with open('h7_reconciliation.json', 'w') as f:
        json.dump(h7_results, f, indent=2)
    print(f"  Saved h7_reconciliation.json")

    # Print summary
    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print()
    print(f"Classification: {h6_results.get('classification', 'UNKNOWN')}")
    print(f"Confidence: {h6_results.get('confidence', 'UNKNOWN')}")
    print()
    print("Model Scores:")
    for model, score in h6_results.get('model_scores', {}).items():
        print(f"  Model {model}: {score}")
    print()
    print("Key Evidence:")
    for model, evs in h6_results.get('evidence_summary', {}).items():
        if evs:
            print(f"  Model {model}:")
            for ev in evs[:3]:
                print(f"    - {ev}")
    print()


if __name__ == '__main__':
    main()
