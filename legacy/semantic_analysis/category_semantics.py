#!/usr/bin/env python3
"""
Category Semantics Reconstruction - Phase C

Builds on Phase 19 finding that headings are CATEGORY LABELS (HIGH confidence).
Recovers the semantic structure of the category system:
1. What defines membership in each category?
2. How do categories relate to each other?
3. How does Currier B apply rules over categories?
4. Where do entity-level distinctions live?

Produces 16 JSON output files (c1_1 through c6_3).
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform

# ============================================================================
# DATA LOADING
# ============================================================================

def load_json(filepath):
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved: {filepath}")

def load_reference_graph(filepath):
    """Parse reference_graph.graphml and extract nodes and edges."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    # GraphML namespace (note: graphdrawing not graphdml)
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}

    # Find key definitions
    keys = {}
    for key in root.findall('.//g:key', ns):
        keys[key.get('id')] = key.get('attr.name')

    # Parse nodes
    nodes = {}
    for node in root.findall('.//g:node', ns):
        node_id = node.get('id')
        node_data = {'id': node_id}
        for data in node.findall('g:data', ns):
            key_id = data.get('key')
            if key_id in keys:
                node_data[keys[key_id]] = data.text
        nodes[node_id] = node_data

    # Parse edges
    edges = []
    for edge in root.findall('.//g:edge', ns):
        edge_data = {
            'source': edge.get('source'),
            'target': edge.get('target')
        }
        for data in edge.findall('g:data', ns):
            key_id = data.get('key')
            if key_id in keys:
                value = data.text
                if keys[key_id] == 'count':
                    value = int(value) if value else 1
                edge_data[keys[key_id]] = value
        edges.append(edge_data)

    return nodes, edges

def load_transcription(filepath):
    """Load the interlinear transcription file."""
    import csv
    words_by_folio = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            word = row.get('word', '')
            folio = row.get('folio', '')
            lang = row.get('language', '')
            line_num = row.get('line_number', '0')

            if word and folio:
                words_by_folio[folio].append({
                    'word': word,
                    'language': lang,
                    'line': line_num
                })

    return words_by_folio

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def compute_mode(values):
    """Compute mode and agreement for a list of values."""
    if not values:
        return None, 0.0
    counter = Counter(values)
    mode, count = counter.most_common(1)[0]
    agreement = count / len(values)
    return mode, agreement

def get_heading_for_folio(folio_id, db):
    """Get the heading word for a folio from the database."""
    for section in ['currier_a', 'currier_b']:
        if section in db and folio_id in db[section]:
            text_features = db[section][folio_id].get('text_features', {})
            return text_features.get('opening_word', '')
    return ''

# ============================================================================
# PHASE C1: CATEGORY FEATURE PROFILES
# ============================================================================

def phase_c1_1_category_visual_profiles(visual_coding, folio_db):
    """C1.1 - Aggregate visual features by category."""
    print("\n=== Phase C1.1: Category Visual Profiles ===")

    results = {
        'metadata': {
            'phase': 'C1.1',
            'title': 'Category Visual Profiles',
            'timestamp': datetime.now().isoformat()
        },
        'categories': {},
        'summary': {}
    }

    # Get visual features list from first coded folio
    visual_features = []
    folios_data = visual_coding.get('folios', {})
    for folio_id, folio_data in folios_data.items():
        vf = folio_data.get('visual_features', {})
        visual_features = list(vf.keys())
        break

    # Group coded folios by heading
    categories = defaultdict(list)
    for folio_id, folio_data in folios_data.items():
        heading = folio_data.get('heading', '')
        if heading:
            categories[heading].append(folio_id)

    print(f"  Found {len(categories)} categories in visual coding data")

    # Compute profile for each category
    for heading, folios in categories.items():
        category_data = {
            'folios': folios,
            'folio_count': len(folios),
            'visual_profile': {},
            'internal_consistency': 0.0
        }

        # Compute mode and agreement for each visual feature
        for feature in visual_features:
            values = []
            for folio_id in folios:
                vf = folios_data[folio_id].get('visual_features', {})
                if feature in vf and vf[feature] is not None:
                    values.append(str(vf[feature]))

            if values:
                mode, agreement = compute_mode(values)
                category_data['visual_profile'][feature] = {
                    'mode': mode,
                    'agreement': round(agreement, 3),
                    'unique_values': len(set(values))
                }

        # Compute internal consistency (mean pairwise Jaccard)
        if len(folios) > 1:
            similarities = []
            for i, f1 in enumerate(folios):
                for f2 in folios[i+1:]:
                    vf1 = folios_data[f1].get('visual_features', {})
                    vf2 = folios_data[f2].get('visual_features', {})

                    # Compare as sets of feature-value pairs
                    set1 = {f"{k}:{v}" for k, v in vf1.items() if v is not None}
                    set2 = {f"{k}:{v}" for k, v in vf2.items() if v is not None}
                    similarities.append(jaccard_similarity(set1, set2))

            category_data['internal_consistency'] = round(np.mean(similarities), 3) if similarities else 0.0
        else:
            category_data['internal_consistency'] = 1.0  # Single folio = perfect consistency

        results['categories'][heading] = category_data

    # Summary statistics
    multi_folio_cats = [h for h, d in results['categories'].items() if d['folio_count'] > 1]
    single_folio_cats = [h for h, d in results['categories'].items() if d['folio_count'] == 1]

    consistencies = [d['internal_consistency'] for d in results['categories'].values() if d['folio_count'] > 1]

    results['summary'] = {
        'total_categories': len(categories),
        'multi_folio_categories': len(multi_folio_cats),
        'single_folio_categories': len(single_folio_cats),
        'multi_folio_list': multi_folio_cats,
        'mean_internal_consistency': round(np.mean(consistencies), 3) if consistencies else None,
        'visual_features_analyzed': len(visual_features)
    }

    print(f"  Multi-folio categories: {len(multi_folio_cats)}")
    print(f"  Single-folio categories: {len(single_folio_cats)}")
    if consistencies:
        print(f"  Mean internal consistency: {results['summary']['mean_internal_consistency']}")

    return results

def phase_c1_2_category_classifier_profiles(classifier_signatures, hub_singleton, folio_db):
    """C1.2 - Aggregate classifier signatures by category."""
    print("\n=== Phase C1.2: Category Classifier Profiles ===")

    results = {
        'metadata': {
            'phase': 'C1.2',
            'title': 'Category Classifier Profiles',
            'timestamp': datetime.now().isoformat()
        },
        'categories': {},
        'summary': {}
    }

    # Get prefix order
    sig_data = classifier_signatures.get('heading_signatures', {})
    prefix_order = sig_data.get('prefix_order', [])
    signatures = sig_data.get('signatures', {})

    # Get hub/mid/isolate classification
    hub_members = set()
    isolate_members = set()
    for group_name, group in hub_singleton.get('group_statistics', {}).items():
        for member in group.get('members', []):
            folio_id = member.get('folio', '')  # Note: uses 'folio' not 'folio_id'
            if group_name == 'hub':
                hub_members.add(folio_id)
            elif group_name == 'isolate':
                isolate_members.add(folio_id)

    # Group folios by heading from folio_db
    categories = defaultdict(list)
    for folio_id, data in folio_db.get('currier_a', {}).items():
        heading = data.get('text_features', {}).get('opening_word', '')
        if heading:
            categories[heading].append(folio_id)

    print(f"  Found {len(categories)} categories in Currier A")

    # Compute profile for each category
    for heading, folios in categories.items():
        # Get prefix distributions for all folios in category
        prefix_vectors = []
        entropies = []

        for folio_id in folios:
            # Get from folio_db
            entry = folio_db.get('currier_a', {}).get(folio_id, {})
            prefix_dist = entry.get('text_features', {}).get('prefix_distribution', {})

            if prefix_dist:
                # Build vector in prefix_order
                vec = [prefix_dist.get(p, 0) for p in prefix_order]
                total = sum(vec)
                if total > 0:
                    vec = [v / total for v in vec]  # Normalize
                    prefix_vectors.append(vec)

            # Get entropy from classifier_signatures
            if folio_id in signatures:
                entropies.append(signatures[folio_id].get('entropy', 0))

        # Compute category-level mean vector
        if prefix_vectors:
            mean_vector = np.mean(prefix_vectors, axis=0).tolist()

            # Compute within-category variance
            if len(prefix_vectors) > 1:
                variances = np.var(prefix_vectors, axis=0)
                mean_variance = float(np.mean(variances))
            else:
                mean_variance = 0.0

            # Find dominant prefixes (top 5 by weight)
            prefix_weights = list(zip(prefix_order, mean_vector))
            dominant = sorted(prefix_weights, key=lambda x: -x[1])[:5]

            category_type = 'hub' if any(f in hub_members for f in folios) else \
                           'isolate' if all(f in isolate_members for f in folios) else 'mid'

            results['categories'][heading] = {
                'folios': folios,
                'folio_count': len(folios),
                'mean_prefix_vector': [round(v, 4) for v in mean_vector],
                'dominant_prefixes': [{'prefix': p, 'weight': round(w, 4)} for p, w in dominant if w > 0.01],
                'within_category_variance': round(mean_variance, 6),
                'mean_entropy': round(np.mean(entropies), 3) if entropies else None,
                'category_type': category_type
            }

    # Summary by category type
    hub_cats = [h for h, d in results['categories'].items() if d['category_type'] == 'hub']
    isolate_cats = [h for h, d in results['categories'].items() if d['category_type'] == 'isolate']

    hub_variances = [d['within_category_variance'] for d in results['categories'].values()
                    if d['category_type'] == 'hub' and d['folio_count'] > 1]
    isolate_variances = [d['within_category_variance'] for d in results['categories'].values()
                        if d['category_type'] == 'isolate' and d['folio_count'] > 1]

    results['summary'] = {
        'total_categories': len(categories),
        'prefix_dimensions': len(prefix_order),
        'hub_categories': len(hub_cats),
        'isolate_categories': len(isolate_cats),
        'hub_mean_variance': round(np.mean(hub_variances), 6) if hub_variances else None,
        'isolate_mean_variance': round(np.mean(isolate_variances), 6) if isolate_variances else None
    }

    print(f"  Hub categories: {len(hub_cats)}")
    print(f"  Isolate categories: {len(isolate_cats)}")

    return results

def phase_c1_3_category_defining_features(visual_profiles, classifier_profiles):
    """C1.3 - Identify category defining features."""
    print("\n=== Phase C1.3: Category Defining Features ===")

    results = {
        'metadata': {
            'phase': 'C1.3',
            'title': 'Category Defining Features',
            'timestamp': datetime.now().isoformat()
        },
        'categories': {},
        'summary': {}
    }

    # For categories with visual data
    visual_cats = visual_profiles.get('categories', {})
    classifier_cats = classifier_profiles.get('categories', {})

    for heading in set(visual_cats.keys()) | set(classifier_cats.keys()):
        cat_data = {
            'defining_visual_features': [],
            'defining_classifier_features': [],
            'confidence': 'LOW'
        }

        # Visual defining features (agreement >= 0.8)
        if heading in visual_cats:
            vp = visual_cats[heading].get('visual_profile', {})
            for feature, data in vp.items():
                if data.get('agreement', 0) >= 0.8:
                    cat_data['defining_visual_features'].append({
                        'feature': feature,
                        'value': data['mode'],
                        'agreement': data['agreement']
                    })

        # Classifier defining features (top 3 dominant prefixes with weight > 0.05)
        if heading in classifier_cats:
            dominant = classifier_cats[heading].get('dominant_prefixes', [])
            for item in dominant[:3]:
                if item['weight'] > 0.05:
                    cat_data['defining_classifier_features'].append({
                        'prefix': item['prefix'],
                        'weight': item['weight']
                    })

        # Confidence based on evidence
        visual_count = len(cat_data['defining_visual_features'])
        classifier_count = len(cat_data['defining_classifier_features'])

        if visual_count >= 3 and classifier_count >= 2:
            cat_data['confidence'] = 'HIGH'
        elif visual_count >= 1 or classifier_count >= 2:
            cat_data['confidence'] = 'MEDIUM'

        if cat_data['defining_visual_features'] or cat_data['defining_classifier_features']:
            results['categories'][heading] = cat_data

    # Summary
    high_conf = [h for h, d in results['categories'].items() if d['confidence'] == 'HIGH']
    med_conf = [h for h, d in results['categories'].items() if d['confidence'] == 'MEDIUM']

    results['summary'] = {
        'categories_with_defining_features': len(results['categories']),
        'high_confidence': len(high_conf),
        'medium_confidence': len(med_conf),
        'high_confidence_categories': high_conf
    }

    print(f"  Categories with defining features: {len(results['categories'])}")
    print(f"  High confidence: {len(high_conf)}")

    return results

# ============================================================================
# PHASE C2: CATEGORY HIERARCHY AND RELATIONSHIPS
# ============================================================================

def phase_c2_1_category_hierarchy(internal_reuse, hub_singleton, folio_db):
    """C2.1 - Build substring-based category hierarchy."""
    print("\n=== Phase C2.1: Category Hierarchy ===")

    results = {
        'metadata': {
            'phase': 'C2.1',
            'title': 'Category Hierarchy',
            'timestamp': datetime.now().isoformat()
        },
        'hierarchy': {},
        'relationships': [],
        'summary': {}
    }

    # Get shared substrings
    shared_substrings = internal_reuse.get('shared_substrings', {})

    # Get all headings and their hub/isolate status
    headings = {}
    hub_headings = set()

    for group_name, group in hub_singleton.get('group_statistics', {}).items():
        for member in group.get('members', []):
            folio_id = member.get('folio', '')  # Note: uses 'folio' not 'folio_id'
            heading = member.get('heading', '')
            if heading:
                headings[heading] = {
                    'folio_id': folio_id,
                    'type': group_name,
                    'in_degree': member.get('in_degree', 0)
                }
                if group_name == 'hub':
                    hub_headings.add(heading)

    print(f"  Total headings: {len(headings)}")
    print(f"  Hub headings: {len(hub_headings)}")

    # Build hierarchy: hub headings as potential parents
    for hub_heading in hub_headings:
        hub_data = {
            'type': 'hub',
            'in_degree': headings.get(hub_heading, {}).get('in_degree', 0),
            'possible_children': [],
            'shared_substrings': []
        }

        # Find headings that contain this hub heading as substring
        for other_heading, other_data in headings.items():
            if other_heading != hub_heading and hub_heading in other_heading:
                hub_data['possible_children'].append({
                    'heading': other_heading,
                    'type': other_data.get('type', 'unknown'),
                    'contains_hub_as': 'substring'
                })

        # Find shared substrings involving this heading
        for substring, data in shared_substrings.items():
            if hub_heading in data.get('headings', []):
                hub_data['shared_substrings'].append(substring)

        results['hierarchy'][hub_heading] = hub_data

    # Find parent-child relationships (longer heading contains shorter)
    for h1, d1 in headings.items():
        for h2, d2 in headings.items():
            if h1 != h2 and h1 in h2 and len(h1) < len(h2):
                results['relationships'].append({
                    'parent': h1,
                    'child': h2,
                    'parent_type': d1.get('type', 'unknown'),
                    'child_type': d2.get('type', 'unknown'),
                    'relationship': 'SUBSTRING_CONTAINMENT'
                })

    # Analyze hierarchy depth
    parents = set(r['parent'] for r in results['relationships'])
    children = set(r['child'] for r in results['relationships'])
    roots = parents - children
    leaves = children - parents

    results['summary'] = {
        'hub_headings_analyzed': len(hub_headings),
        'total_relationships': len(results['relationships']),
        'root_categories': list(roots),
        'leaf_categories_count': len(leaves),
        'max_hierarchy_depth': 2 if results['relationships'] else 1  # Simple estimate
    }

    print(f"  Parent-child relationships found: {len(results['relationships'])}")
    print(f"  Root categories: {len(roots)}")

    return results

def phase_c2_2_classifier_clusters(classifier_profiles, folio_db):
    """C2.2 - Cluster categories by classifier signature."""
    print("\n=== Phase C2.2: Classifier Clusters ===")

    results = {
        'metadata': {
            'phase': 'C2.2',
            'title': 'Classifier-Based Clusters',
            'timestamp': datetime.now().isoformat()
        },
        'clusters': {},
        'dendrogram_structure': {},
        'summary': {}
    }

    cats = classifier_profiles.get('categories', {})

    # Build matrix of category vectors
    headings = []
    vectors = []

    for heading, data in cats.items():
        vec = data.get('mean_prefix_vector', [])
        if vec and any(v > 0 for v in vec):
            headings.append(heading)
            vectors.append(vec)

    if len(vectors) < 3:
        print("  Not enough categories for clustering")
        results['summary']['error'] = 'Insufficient categories for clustering'
        return results

    print(f"  Clustering {len(headings)} categories")

    # Compute distance matrix (1 - cosine similarity)
    X = np.array(vectors)
    distances = pdist(X, metric='cosine')

    # Hierarchical clustering
    linkage_matrix = linkage(distances, method='ward')

    # Cut at different heights to get clusters
    for n_clusters in [3, 5, 7, 10]:
        if n_clusters > len(headings):
            continue

        cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')

        clusters = defaultdict(list)
        for heading, label in zip(headings, cluster_labels):
            clusters[int(label)].append(heading)

        results['clusters'][f'k={n_clusters}'] = {
            'cluster_count': n_clusters,
            'clusters': dict(clusters)
        }

    # Store dendrogram structure (simplified)
    results['dendrogram_structure'] = {
        'n_leaves': len(headings),
        'linkage_method': 'ward',
        'distance_metric': 'cosine'
    }

    # Summary
    results['summary'] = {
        'categories_clustered': len(headings),
        'cluster_counts_tested': [3, 5, 7, 10],
        'best_cluster_count': 5  # Arbitrary choice, could use silhouette
    }

    print(f"  Created cluster assignments for k=3,5,7,10")

    return results

def phase_c2_3_cocitation_clusters(cocitation_structure, hub_singleton):
    """C2.3 - Identify co-citation category groups."""
    print("\n=== Phase C2.3: Co-Citation Clusters ===")

    results = {
        'metadata': {
            'phase': 'C2.3',
            'title': 'Co-Citation Clusters',
            'timestamp': datetime.now().isoformat()
        },
        'clusters': [],
        'adjacency': {},
        'summary': {}
    }

    # Get co-citation matrix
    cocit_matrix = cocitation_structure.get('cocitation_matrix', {})
    strongly_cocited = cocitation_structure.get('strongly_cocited_pairs', [])

    # Build adjacency from strongly co-cited pairs
    adjacency = defaultdict(set)
    for pair in strongly_cocited:
        h1 = pair.get('heading1', '')
        h2 = pair.get('heading2', '')
        if h1 and h2:
            adjacency[h1].add(h2)
            adjacency[h2].add(h1)

    # Also build from cocitation_matrix if available
    for source, targets in cocit_matrix.items():
        for target, count in targets.items():
            if count >= 2:  # Threshold for strong co-citation
                adjacency[source].add(target)
                adjacency[target].add(source)

    results['adjacency'] = {k: list(v) for k, v in adjacency.items()}

    # Find connected components (simple BFS)
    visited = set()
    clusters = []

    for node in adjacency:
        if node not in visited:
            cluster = []
            queue = [node]
            while queue:
                current = queue.pop(0)
                if current not in visited:
                    visited.add(current)
                    cluster.append(current)
                    queue.extend(n for n in adjacency[current] if n not in visited)
            if len(cluster) > 1:
                clusters.append(sorted(cluster))

    # Store clusters with metadata
    for i, cluster in enumerate(clusters):
        results['clusters'].append({
            'cluster_id': i + 1,
            'size': len(cluster),
            'members': cluster,
            'interpretation': 'FUNCTIONAL_GROUP'
        })

    results['summary'] = {
        'nodes_in_adjacency': len(adjacency),
        'clusters_found': len(clusters),
        'largest_cluster_size': max(len(c) for c in clusters) if clusters else 0,
        'singleton_nodes': len(adjacency) - sum(len(c) for c in clusters)
    }

    print(f"  Co-citation clusters found: {len(clusters)}")

    return results

# ============================================================================
# PHASE C3: INTRA-CATEGORY ENTITY ANALYSIS
# ============================================================================

def phase_c3_1_intracategory_variation(folio_db):
    """C3.1 - Analyze body text variation within categories."""
    print("\n=== Phase C3.1: Intra-Category Variation ===")

    results = {
        'metadata': {
            'phase': 'C3.1',
            'title': 'Intra-Category Variation',
            'timestamp': datetime.now().isoformat()
        },
        'categories': {},
        'summary': {}
    }

    # Group folios by heading
    categories = defaultdict(list)
    for folio_id, data in folio_db.get('currier_a', {}).items():
        heading = data.get('text_features', {}).get('opening_word', '')
        if heading:
            categories[heading].append((folio_id, data))

    # Focus on multi-folio categories
    multi_folio = {h: f for h, f in categories.items() if len(f) > 1}
    print(f"  Multi-folio categories: {len(multi_folio)}")

    for heading, folios in multi_folio.items():
        # Collect vocabulary for each folio
        all_vocabs = []
        folio_vocabs = {}

        for folio_id, data in folios:
            tf = data.get('text_features', {})
            part1 = set(tf.get('part1_vocabulary', []))
            part2 = set(tf.get('part2_vocabulary', []))
            part3 = set(tf.get('part3_vocabulary', []))
            full_vocab = part1 | part2 | part3

            folio_vocabs[folio_id] = {
                'part1': part1,
                'part2': part2,
                'part3': part3,
                'full': full_vocab
            }
            all_vocabs.append(full_vocab)

        # Compute shared vs unique vocabulary
        shared_vocab = set.intersection(*all_vocabs) if all_vocabs else set()
        union_vocab = set.union(*all_vocabs) if all_vocabs else set()

        # Entry-specific words
        entry_specific = {}
        for folio_id, vocab_data in folio_vocabs.items():
            unique = vocab_data['full'] - shared_vocab
            entry_specific[folio_id] = list(unique)[:20]  # Limit for readability

        # Jaccard similarity between entries
        similarities = []
        folio_ids = list(folio_vocabs.keys())
        for i, f1 in enumerate(folio_ids):
            for f2 in folio_ids[i+1:]:
                sim = jaccard_similarity(folio_vocabs[f1]['full'], folio_vocabs[f2]['full'])
                similarities.append(sim)

        results['categories'][heading] = {
            'folios': list(folio_vocabs.keys()),
            'folio_count': len(folio_vocabs),
            'shared_vocabulary_count': len(shared_vocab),
            'union_vocabulary_count': len(union_vocab),
            'shared_vocabulary_sample': list(shared_vocab)[:20],
            'entry_specific': entry_specific,
            'mean_pairwise_jaccard': round(np.mean(similarities), 3) if similarities else None,
            'candidate_modifiers': list(union_vocab - shared_vocab)[:30]
        }

    # Summary
    jaccard_values = [d['mean_pairwise_jaccard'] for d in results['categories'].values()
                     if d['mean_pairwise_jaccard'] is not None]

    results['summary'] = {
        'multi_folio_categories': len(multi_folio),
        'mean_cross_entry_jaccard': round(np.mean(jaccard_values), 3) if jaccard_values else None,
        'categories_analyzed': list(multi_folio.keys())
    }

    print(f"  Mean cross-entry Jaccard: {results['summary']['mean_cross_entry_jaccard']}")

    return results

def phase_c3_2_part_specific_vocabulary(folio_db):
    """C3.2 - Analyze part-specific vocabulary by category."""
    print("\n=== Phase C3.2: Part-Specific Vocabulary ===")

    results = {
        'metadata': {
            'phase': 'C3.2',
            'title': 'Part-Specific Vocabulary by Category',
            'timestamp': datetime.now().isoformat()
        },
        'categories': {},
        'global_analysis': {},
        'summary': {}
    }

    # Group folios by heading
    categories = defaultdict(list)
    for folio_id, data in folio_db.get('currier_a', {}).items():
        heading = data.get('text_features', {}).get('opening_word', '')
        if heading:
            categories[heading].append((folio_id, data))

    # Analyze vocabulary distribution across parts
    global_part1 = Counter()
    global_part2 = Counter()
    global_part3 = Counter()

    for heading, folios in categories.items():
        cat_part1 = Counter()
        cat_part2 = Counter()
        cat_part3 = Counter()

        for folio_id, data in folios:
            tf = data.get('text_features', {})
            for word in tf.get('part1_vocabulary', []):
                cat_part1[word] += 1
                global_part1[word] += 1
            for word in tf.get('part2_vocabulary', []):
                cat_part2[word] += 1
                global_part2[word] += 1
            for word in tf.get('part3_vocabulary', []):
                cat_part3[word] += 1
                global_part3[word] += 1

        # Find part-dominant words for this category
        all_words = set(cat_part1.keys()) | set(cat_part2.keys()) | set(cat_part3.keys())

        part_dominant = {'part1': [], 'part2': [], 'part3': []}
        for word in all_words:
            total = cat_part1[word] + cat_part2[word] + cat_part3[word]
            if total >= 2:  # Minimum frequency
                if cat_part1[word] / total > 0.7:
                    part_dominant['part1'].append(word)
                elif cat_part2[word] / total > 0.7:
                    part_dominant['part2'].append(word)
                elif cat_part3[word] / total > 0.7:
                    part_dominant['part3'].append(word)

        results['categories'][heading] = {
            'folio_count': len(folios),
            'part1_unique_words': len(cat_part1),
            'part2_unique_words': len(cat_part2),
            'part3_unique_words': len(cat_part3),
            'part1_dominant_words': part_dominant['part1'][:10],
            'part2_dominant_words': part_dominant['part2'][:10],
            'part3_dominant_words': part_dominant['part3'][:10]
        }

    # Global analysis: words that are part-specific across ALL categories
    all_words = set(global_part1.keys()) | set(global_part2.keys()) | set(global_part3.keys())
    global_part_dominant = {'part1': [], 'part2': [], 'part3': []}

    for word in all_words:
        total = global_part1[word] + global_part2[word] + global_part3[word]
        if total >= 5:  # Higher threshold for global
            p1_ratio = global_part1[word] / total
            p2_ratio = global_part2[word] / total
            p3_ratio = global_part3[word] / total

            if p1_ratio > 0.7:
                global_part_dominant['part1'].append({'word': word, 'ratio': round(p1_ratio, 2)})
            elif p2_ratio > 0.7:
                global_part_dominant['part2'].append({'word': word, 'ratio': round(p2_ratio, 2)})
            elif p3_ratio > 0.7:
                global_part_dominant['part3'].append({'word': word, 'ratio': round(p3_ratio, 2)})

    # Sort by ratio
    for part in global_part_dominant:
        global_part_dominant[part] = sorted(global_part_dominant[part], key=lambda x: -x['ratio'])[:20]

    results['global_analysis'] = {
        'part1_dominant_words': global_part_dominant['part1'],
        'part2_dominant_words': global_part_dominant['part2'],
        'part3_dominant_words': global_part_dominant['part3'],
        'interpretation': {
            'part1': 'IDENTIFICATION/NAMING' if global_part_dominant['part1'] else 'NO_DOMINANT_PATTERN',
            'part2': 'PROPERTIES/DESCRIPTION' if global_part_dominant['part2'] else 'NO_DOMINANT_PATTERN',
            'part3': 'APPLICATIONS/USES' if global_part_dominant['part3'] else 'NO_DOMINANT_PATTERN'
        }
    }

    results['summary'] = {
        'categories_analyzed': len(categories),
        'global_part1_dominant_count': len(global_part_dominant['part1']),
        'global_part2_dominant_count': len(global_part_dominant['part2']),
        'global_part3_dominant_count': len(global_part_dominant['part3'])
    }

    print(f"  Part 1 dominant words: {results['summary']['global_part1_dominant_count']}")
    print(f"  Part 2 dominant words: {results['summary']['global_part2_dominant_count']}")
    print(f"  Part 3 dominant words: {results['summary']['global_part3_dominant_count']}")

    return results

# ============================================================================
# PHASE C4: CURRIER B RULE ANALYSIS
# ============================================================================

def phase_c4_1_b_reference_contexts(reference_graph, transcription, folio_db):
    """C4.1 - Extract B reference contexts."""
    print("\n=== Phase C4.1: B Reference Contexts ===")

    results = {
        'metadata': {
            'phase': 'C4.1',
            'title': 'B Reference Context Extraction',
            'timestamp': datetime.now().isoformat()
        },
        'contexts': [],
        'summary': {}
    }

    nodes, edges = reference_graph

    # Get B folios and their A references
    b_to_a_refs = defaultdict(list)
    for edge in edges:
        source_raw = edge.get('source', '')
        target_raw = edge.get('target', '')
        # Strip A_ and B_ prefixes
        source = source_raw.replace('B_', '').replace('A_', '')
        target = target_raw.replace('B_', '').replace('A_', '')
        heading = edge.get('heading_word', '')
        count = edge.get('count', 1)

        # Only process B->A edges
        if source_raw.startswith('B_') and target_raw.startswith('A_'):
            b_to_a_refs[source].append({
                'a_folio': target,
                'heading': heading,
                'count': count
            })

    print(f"  B folios with A references: {len(b_to_a_refs)}")

    # For each B entry, find contexts where A headings appear
    contexts_extracted = 0

    for b_folio, refs in b_to_a_refs.items():
        # Get B entry text
        b_words = transcription.get(b_folio, [])
        if not b_words:
            continue

        word_list = [w['word'] for w in b_words]
        entry_length = len(word_list)

        # Get all A headings referenced
        a_headings = set(r['heading'] for r in refs if r.get('heading'))

        # Find positions of A headings in B text
        for heading in a_headings:
            positions = [i for i, w in enumerate(word_list) if w == heading]

            for pos in positions:
                # Extract context (±10 words)
                start = max(0, pos - 10)
                end = min(len(word_list), pos + 11)
                context_words = word_list[start:end]

                # Determine position in entry
                relative_pos = pos / entry_length if entry_length > 0 else 0
                if relative_pos < 0.33:
                    position_label = 'BEGINNING'
                elif relative_pos < 0.67:
                    position_label = 'MIDDLE'
                else:
                    position_label = 'END'

                results['contexts'].append({
                    'b_folio': b_folio,
                    'a_heading': heading,
                    'position_in_entry': pos,
                    'relative_position': round(relative_pos, 3),
                    'position_label': position_label,
                    'context': ' '.join(context_words),
                    'context_before': ' '.join(word_list[start:pos]),
                    'context_after': ' '.join(word_list[pos+1:end])
                })
                contexts_extracted += 1

    # Summary by position
    position_counts = Counter(c['position_label'] for c in results['contexts'])
    heading_counts = Counter(c['a_heading'] for c in results['contexts'])

    results['summary'] = {
        'b_folios_analyzed': len(b_to_a_refs),
        'contexts_extracted': contexts_extracted,
        'position_distribution': dict(position_counts),
        'most_referenced_headings': heading_counts.most_common(10),
        'mean_references_per_b_folio': round(contexts_extracted / len(b_to_a_refs), 2) if b_to_a_refs else 0
    }

    print(f"  Contexts extracted: {contexts_extracted}")
    print(f"  Position distribution: {dict(position_counts)}")

    return results

def phase_c4_2_category_usage_patterns(b_contexts, hub_singleton):
    """C4.2 - Analyze category usage patterns in B."""
    print("\n=== Phase C4.2: Category Usage Patterns ===")

    results = {
        'metadata': {
            'phase': 'C4.2',
            'title': 'Category Usage Patterns in B',
            'timestamp': datetime.now().isoformat()
        },
        'category_patterns': {},
        'position_analysis': {},
        'summary': {}
    }

    contexts = b_contexts.get('contexts', [])

    # Get hub/isolate classification
    hub_headings = set()
    isolate_headings = set()
    for group_name, group in hub_singleton.get('group_statistics', {}).items():
        for member in group.get('members', []):
            heading = member.get('heading', '')
            if group_name == 'hub':
                hub_headings.add(heading)
            elif group_name == 'isolate':
                isolate_headings.add(heading)

    # Analyze patterns per category
    category_data = defaultdict(lambda: {
        'total_occurrences': 0,
        'b_folios': set(),
        'positions': [],
        'co_occurring_headings': Counter()
    })

    # Group contexts by B folio for co-occurrence analysis
    b_folio_headings = defaultdict(set)
    for ctx in contexts:
        heading = ctx.get('a_heading', '')
        b_folio = ctx.get('b_folio', '')
        position = ctx.get('position_label', '')

        if heading:
            category_data[heading]['total_occurrences'] += 1
            category_data[heading]['b_folios'].add(b_folio)
            category_data[heading]['positions'].append(position)
            b_folio_headings[b_folio].add(heading)

    # Compute co-occurrences
    for headings in b_folio_headings.values():
        for h1 in headings:
            for h2 in headings:
                if h1 != h2:
                    category_data[h1]['co_occurring_headings'][h2] += 1

    # Build output
    for heading, data in category_data.items():
        position_counts = Counter(data['positions'])

        category_type = 'hub' if heading in hub_headings else \
                       'isolate' if heading in isolate_headings else 'mid'

        results['category_patterns'][heading] = {
            'category_type': category_type,
            'total_occurrences': data['total_occurrences'],
            'unique_b_folios': len(data['b_folios']),
            'position_distribution': dict(position_counts),
            'dominant_position': position_counts.most_common(1)[0][0] if position_counts else None,
            'top_co_occurring': data['co_occurring_headings'].most_common(5)
        }

    # Position analysis by category type
    hub_positions = []
    isolate_positions = []

    for heading, pattern in results['category_patterns'].items():
        if pattern['category_type'] == 'hub':
            hub_positions.extend([pattern.get('position_distribution', {})])
        elif pattern['category_type'] == 'isolate':
            isolate_positions.extend([pattern.get('position_distribution', {})])

    # Aggregate position distributions
    hub_pos_totals = Counter()
    isolate_pos_totals = Counter()

    for pos_dist in hub_positions:
        for pos, count in pos_dist.items():
            hub_pos_totals[pos] += count
    for pos_dist in isolate_positions:
        for pos, count in pos_dist.items():
            isolate_pos_totals[pos] += count

    results['position_analysis'] = {
        'hub_categories': dict(hub_pos_totals),
        'isolate_categories': dict(isolate_pos_totals),
        'interpretation': 'Hub categories may appear in different positions than isolates'
    }

    results['summary'] = {
        'categories_analyzed': len(category_data),
        'hub_categories_in_b': len([h for h, p in results['category_patterns'].items()
                                   if p['category_type'] == 'hub']),
        'isolate_categories_in_b': len([h for h, p in results['category_patterns'].items()
                                       if p['category_type'] == 'isolate']),
        'most_frequent_category': max(category_data.items(),
                                     key=lambda x: x[1]['total_occurrences'])[0] if category_data else None
    }

    print(f"  Categories appearing in B: {len(category_data)}")

    return results

def phase_c4_3_b_entry_structure(b_contexts, folio_db):
    """C4.3 - Analyze B entry structure."""
    print("\n=== Phase C4.3: B Entry Structure ===")

    results = {
        'metadata': {
            'phase': 'C4.3',
            'title': 'B Entry Structure Analysis',
            'timestamp': datetime.now().isoformat()
        },
        'entries': {},
        'patterns': {},
        'summary': {}
    }

    contexts = b_contexts.get('contexts', [])

    # Group contexts by B folio
    b_entries = defaultdict(list)
    for ctx in contexts:
        b_folio = ctx.get('b_folio', '')
        if b_folio:
            b_entries[b_folio].append(ctx)

    # Analyze each B entry
    for b_folio, entry_contexts in b_entries.items():
        # Sort by position
        entry_contexts.sort(key=lambda x: x.get('position_in_entry', 0))

        # Get entry metadata
        b_data = folio_db.get('currier_b', {}).get(b_folio, {})
        word_count = b_data.get('text_features', {}).get('word_count', 0)

        # Analyze reference pattern
        headings_referenced = [ctx['a_heading'] for ctx in entry_contexts]
        positions = [ctx['position_label'] for ctx in entry_contexts]

        # Check for patterns
        opening_refs = [h for ctx, h in zip(entry_contexts, headings_referenced)
                       if ctx['position_label'] == 'BEGINNING']
        closing_refs = [h for ctx, h in zip(entry_contexts, headings_referenced)
                       if ctx['position_label'] == 'END']

        results['entries'][b_folio] = {
            'word_count': word_count,
            'total_a_references': len(entry_contexts),
            'unique_a_headings': len(set(headings_referenced)),
            'headings_referenced': headings_referenced,
            'position_sequence': positions,
            'opening_references': opening_refs,
            'closing_references': closing_refs,
            'reference_density': round(len(entry_contexts) / word_count, 4) if word_count > 0 else 0
        }

    # Find structural patterns across entries
    # Pattern 1: Entries that start with A reference
    starts_with_ref = [e for e, d in results['entries'].items()
                      if d['opening_references']]

    # Pattern 2: Entries that end with A reference
    ends_with_ref = [e for e, d in results['entries'].items()
                    if d['closing_references']]

    # Pattern 3: Single-reference entries
    single_ref = [e for e, d in results['entries'].items()
                 if d['total_a_references'] == 1]

    # Pattern 4: Multi-reference entries
    multi_ref = [e for e, d in results['entries'].items()
                if d['total_a_references'] > 1]

    results['patterns'] = {
        'starts_with_reference': len(starts_with_ref),
        'ends_with_reference': len(ends_with_ref),
        'single_reference_entries': len(single_ref),
        'multi_reference_entries': len(multi_ref),
        'mean_references_per_entry': round(
            sum(d['total_a_references'] for d in results['entries'].values()) /
            len(results['entries']), 2) if results['entries'] else 0
    }

    results['summary'] = {
        'b_entries_analyzed': len(results['entries']),
        'total_a_references': sum(d['total_a_references'] for d in results['entries'].values()),
        'structural_pattern': 'MULTI_REFERENCE' if results['patterns']['multi_reference_entries'] >
                             results['patterns']['single_reference_entries'] else 'SINGLE_REFERENCE'
    }

    print(f"  B entries analyzed: {len(results['entries'])}")
    print(f"  Multi-reference entries: {results['patterns']['multi_reference_entries']}")

    return results

# ============================================================================
# PHASE C5: CROSS-VALIDATION
# ============================================================================

def phase_c5_1_cross_validation(visual_profiles, classifier_clusters, cocitation_clusters):
    """C5.1 - Cross-validate visual, classifier, and citation clusters."""
    print("\n=== Phase C5.1: Cross-Validation ===")

    results = {
        'metadata': {
            'phase': 'C5.1',
            'title': 'Visual-Classifier-Citation Alignment',
            'timestamp': datetime.now().isoformat()
        },
        'category_alignment': {},
        'global_alignment': {},
        'summary': {}
    }

    # Get visual profiles
    visual_cats = visual_profiles.get('categories', {})

    # Get classifier clusters (use k=5)
    classifier_cluster_data = classifier_clusters.get('clusters', {}).get('k=5', {})
    classifier_cat_clusters = classifier_cluster_data.get('clusters', {})

    # Invert classifier clusters to heading -> cluster
    heading_to_classifier_cluster = {}
    for cluster_id, headings in classifier_cat_clusters.items():
        for heading in headings:
            heading_to_classifier_cluster[heading] = cluster_id

    # Get co-citation clusters
    cocit_clusters_list = cocitation_clusters.get('clusters', [])
    heading_to_cocit_cluster = {}
    for cluster in cocit_clusters_list:
        cluster_id = cluster.get('cluster_id')
        for heading in cluster.get('members', []):
            heading_to_cocit_cluster[heading] = cluster_id

    # For each category with visual data, check alignment
    alignment_scores = []

    for heading in visual_cats:
        visual_consistency = visual_cats[heading].get('internal_consistency', 0)
        classifier_cluster = heading_to_classifier_cluster.get(heading)
        cocit_cluster = heading_to_cocit_cluster.get(heading)

        alignment = {
            'has_visual': True,
            'has_classifier_cluster': classifier_cluster is not None,
            'has_cocit_cluster': cocit_cluster is not None,
            'visual_consistency': visual_consistency,
            'classifier_cluster': classifier_cluster,
            'cocit_cluster': cocit_cluster
        }

        results['category_alignment'][heading] = alignment

    # Global alignment analysis
    # Check if categories in same classifier cluster have similar visual profiles
    cluster_visual_consistency = defaultdict(list)
    for heading, alignment in results['category_alignment'].items():
        if alignment['classifier_cluster']:
            cluster_visual_consistency[alignment['classifier_cluster']].append(
                alignment['visual_consistency']
            )

    cluster_consistency_means = {
        cluster: round(np.mean(consistencies), 3)
        for cluster, consistencies in cluster_visual_consistency.items()
        if consistencies
    }

    results['global_alignment'] = {
        'visual_classifier_correlation': cluster_consistency_means,
        'interpretation': 'PARTIAL_ALIGNMENT' if any(v > 0.5 for v in cluster_consistency_means.values())
                         else 'WEAK_ALIGNMENT'
    }

    results['summary'] = {
        'categories_with_all_data': len([h for h, a in results['category_alignment'].items()
                                        if a['has_visual'] and a['has_classifier_cluster']]),
        'mean_visual_consistency': round(
            np.mean([a['visual_consistency'] for a in results['category_alignment'].values()]), 3
        ),
        'alignment_assessment': results['global_alignment']['interpretation']
    }

    print(f"  Categories with full alignment data: {results['summary']['categories_with_all_data']}")

    return results

def phase_c5_2_correlation_reinterpretation(visual_profiles, classifier_profiles):
    """C5.2 - Reinterpret prior correlations at category level."""
    print("\n=== Phase C5.2: Correlation Reinterpretation ===")

    results = {
        'metadata': {
            'phase': 'C5.2',
            'title': 'Correlation Reinterpretation',
            'timestamp': datetime.now().isoformat()
        },
        'prefix_analyses': {},
        'category_level_correlations': {},
        'summary': {}
    }

    visual_cats = visual_profiles.get('categories', {})
    classifier_cats = classifier_profiles.get('categories', {})

    # Prior findings to reinterpret
    prior_correlations = {
        'ko': {'feature': 'leaf_shape', 'V': 0.61, 'percentile': 83.6},
        'po': {'feature': 'root_type', 'V': 0.20, 'percentile': 0}
    }

    for prefix, prior in prior_correlations.items():
        feature = prior['feature']

        # Find categories where this prefix is dominant
        prefix_categories = []
        for heading, cat_data in classifier_cats.items():
            dominant = cat_data.get('dominant_prefixes', [])
            if any(p['prefix'] == prefix and p['weight'] > 0.05 for p in dominant):
                prefix_categories.append(heading)

        # Get visual feature distribution for these categories
        feature_values = []
        for heading in prefix_categories:
            if heading in visual_cats:
                profile = visual_cats[heading].get('visual_profile', {})
                if feature in profile:
                    feature_values.append(profile[feature]['mode'])

        # Compute category-level agreement
        if feature_values:
            mode, agreement = compute_mode(feature_values)
        else:
            mode, agreement = None, 0.0

        results['prefix_analyses'][prefix] = {
            'prior_correlation': prior,
            'categories_with_prefix': prefix_categories,
            'categories_with_visual_data': len(feature_values),
            'category_level_feature_mode': mode,
            'category_level_agreement': round(agreement, 3) if agreement else None,
            'interpretation': 'STRONGER_AT_CATEGORY_LEVEL' if agreement > 0.5 else
                            'WEAKER_AT_CATEGORY_LEVEL' if feature_values else 'INSUFFICIENT_DATA'
        }

    # Summary
    results['summary'] = {
        'prior_correlations_analyzed': len(prior_correlations),
        'stronger_at_category_level': len([p for p, d in results['prefix_analyses'].items()
                                          if d['interpretation'] == 'STRONGER_AT_CATEGORY_LEVEL']),
        'conclusion': 'Category-level analysis may reveal different patterns than folio-level'
    }

    print(f"  Prefixes analyzed: {len(prior_correlations)}")

    return results

# ============================================================================
# PHASE C6: SYNTHESIS
# ============================================================================

def phase_c6_1_category_system_model(all_results):
    """C6.1 - Build comprehensive category system model."""
    print("\n=== Phase C6.1: Category System Model ===")

    results = {
        'metadata': {
            'phase': 'C6.1',
            'title': 'Category System Model',
            'timestamp': datetime.now().isoformat()
        },
        'model': {}
    }

    # Extract key findings from all phases
    hierarchy = all_results.get('c2_1', {}).get('hierarchy', {})
    classifier_clusters = all_results.get('c2_2', {}).get('clusters', {}).get('k=5', {})
    cocit_clusters = all_results.get('c2_3', {}).get('clusters', [])
    defining_features = all_results.get('c1_3', {}).get('categories', {})
    b_patterns = all_results.get('c4_2', {}).get('category_patterns', {})

    # Determine organizing principle
    visual_consistency = all_results.get('c1_1', {}).get('summary', {}).get('mean_internal_consistency')
    cross_validation = all_results.get('c5_1', {}).get('global_alignment', {}).get('interpretation', '')

    # Handle None values
    if visual_consistency is None:
        visual_consistency = 0.0

    if visual_consistency > 0.6 and 'PARTIAL' in cross_validation:
        organizing_principle = 'MORPHOLOGICAL'
    elif len(cocit_clusters) > 3:
        organizing_principle = 'FUNCTIONAL'
    else:
        organizing_principle = 'MIXED'

    # Build category definitions
    category_definitions = {}

    for heading in set(hierarchy.keys()) | set(defining_features.keys()) | set(b_patterns.keys()):
        cat_def = {
            'type': 'hub' if heading in hierarchy else 'isolate',
            'defining_features': [],
            'children': [],
            'functional_role_in_B': None,
            'confidence': 'LOW'
        }

        # From hierarchy
        if heading in hierarchy:
            cat_def['children'] = [c['heading'] for c in hierarchy[heading].get('possible_children', [])]

        # From defining features
        if heading in defining_features:
            df = defining_features[heading]
            cat_def['defining_features'] = df.get('defining_visual_features', []) + \
                                          df.get('defining_classifier_features', [])
            cat_def['confidence'] = df.get('confidence', 'LOW')

        # From B patterns
        if heading in b_patterns:
            bp = b_patterns[heading]
            cat_def['functional_role_in_B'] = bp.get('dominant_position')
            cat_def['b_occurrences'] = bp.get('total_occurrences', 0)

        category_definitions[heading] = cat_def

    # Count statistics
    hub_count = len([h for h, d in category_definitions.items() if d['type'] == 'hub'])
    high_conf = len([h for h, d in category_definitions.items() if d['confidence'] == 'HIGH'])

    results['model'] = {
        'total_categories': len(category_definitions),
        'hub_categories': hub_count,
        'hierarchy_depth': 2,  # From C2.1
        'primary_organizing_principle': organizing_principle,
        'high_confidence_definitions': high_conf,
        'category_definitions': category_definitions
    }

    print(f"  Total categories in model: {len(category_definitions)}")
    print(f"  Organizing principle: {organizing_principle}")

    return results

def phase_c6_2_semantic_recovery_assessment(model_results, all_results):
    """C6.2 - Assess semantic recovery feasibility."""
    print("\n=== Phase C6.2: Semantic Recovery Assessment ===")

    results = {
        'metadata': {
            'phase': 'C6.2',
            'title': 'Semantic Recovery Assessment',
            'timestamp': datetime.now().isoformat()
        },
        'assessment': {}
    }

    model = model_results.get('model', {})

    # Assess each level of semantic recovery
    levels = {
        'category_structure': {
            'description': 'Hierarchy and relationships between categories',
            'evidence': [
                f"Hierarchy depth: {model.get('hierarchy_depth', 0)}",
                f"Hub categories identified: {model.get('hub_categories', 0)}",
                f"Organizing principle: {model.get('primary_organizing_principle', 'UNKNOWN')}"
            ],
            'feasibility': 'ACHIEVED' if model.get('hub_categories', 0) > 0 else 'PARTIAL'
        },
        'category_features': {
            'description': 'Defining morphological/functional traits per category',
            'evidence': [
                f"High-confidence definitions: {model.get('high_confidence_definitions', 0)}",
                f"Categories with defining features: {len([c for c in model.get('category_definitions', {}).values() if c.get('defining_features')])}"
            ],
            'feasibility': 'PARTIAL' if model.get('high_confidence_definitions', 0) > 0 else 'BLOCKED'
        },
        'category_meaning': {
            'description': 'Natural language equivalents for categories',
            'evidence': [
                "No external word identification achieved",
                "No phonetic matching attempted (by design)"
            ],
            'feasibility': 'BLOCKED'
        },
        'entity_identification': {
            'description': 'Specific plants/entities within categories',
            'evidence': [
                f"Intra-category vocabulary variation analyzed",
                f"Candidate entity modifiers identified"
            ],
            'feasibility': 'PARTIAL'
        }
    }

    results['assessment'] = levels

    # Overall assessment
    achieved = len([l for l in levels.values() if l['feasibility'] == 'ACHIEVED'])
    partial = len([l for l in levels.values() if l['feasibility'] == 'PARTIAL'])
    blocked = len([l for l in levels.values() if l['feasibility'] == 'BLOCKED'])

    results['overall'] = {
        'achieved_levels': achieved,
        'partial_levels': partial,
        'blocked_levels': blocked,
        'conclusion': 'STRUCTURAL_RECOVERY_POSSIBLE' if achieved > 0 or partial >= 2 else 'LIMITED_RECOVERY'
    }

    print(f"  Achieved: {achieved}, Partial: {partial}, Blocked: {blocked}")

    return results

def phase_c6_3_new_constraints(all_results):
    """C6.3 - Document new validated constraints."""
    print("\n=== Phase C6.3: New Constraints ===")

    results = {
        'metadata': {
            'phase': 'C6.3',
            'title': 'New Constraints',
            'timestamp': datetime.now().isoformat()
        },
        'new_constraints': [],
        'summary': {}
    }

    # Extract validated findings as constraints

    # From C1: Category profiles
    c1_1_summary = all_results.get('c1_1', {}).get('summary', {})
    if c1_1_summary.get('mean_internal_consistency'):
        results['new_constraints'].append({
            'id': 27,
            'finding': 'Category visual consistency measurable',
            'evidence': f"Mean internal consistency: {c1_1_summary.get('mean_internal_consistency')}",
            'confidence': 'HIGH' if c1_1_summary.get('mean_internal_consistency', 0) > 0.3 else 'MEDIUM'
        })

    # From C2: Hierarchy
    c2_1_summary = all_results.get('c2_1', {}).get('summary', {})
    if c2_1_summary.get('total_relationships', 0) > 0:
        results['new_constraints'].append({
            'id': 28,
            'finding': 'Substring-based category hierarchy exists',
            'evidence': f"Parent-child relationships: {c2_1_summary.get('total_relationships')}",
            'confidence': 'MEDIUM'
        })

    # From C3: Intra-category variation
    c3_1_summary = all_results.get('c3_1', {}).get('summary', {})
    if c3_1_summary.get('mean_cross_entry_jaccard'):
        results['new_constraints'].append({
            'id': 29,
            'finding': 'Within-category vocabulary variation exists',
            'evidence': f"Mean cross-entry Jaccard: {c3_1_summary.get('mean_cross_entry_jaccard')}",
            'confidence': 'HIGH'
        })

    # From C4: B reference patterns
    c4_3_summary = all_results.get('c4_3', {}).get('summary', {})
    if c4_3_summary.get('structural_pattern'):
        results['new_constraints'].append({
            'id': 30,
            'finding': f"B entries use {c4_3_summary.get('structural_pattern')} structure",
            'evidence': f"B entries analyzed: {c4_3_summary.get('b_entries_analyzed')}",
            'confidence': 'MEDIUM'
        })

    # From C6.1: Organizing principle
    c6_1_model = all_results.get('c6_1', {}).get('model', {})
    if c6_1_model.get('primary_organizing_principle'):
        results['new_constraints'].append({
            'id': 31,
            'finding': f"Primary organizing principle: {c6_1_model.get('primary_organizing_principle')}",
            'evidence': f"Based on visual consistency, co-citation patterns, and hierarchy analysis",
            'confidence': 'MEDIUM'
        })

    results['summary'] = {
        'new_constraints_count': len(results['new_constraints']),
        'prior_constraint_count': 26,
        'total_constraints': 26 + len(results['new_constraints'])
    }

    print(f"  New constraints identified: {len(results['new_constraints'])}")

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all Category Semantics Reconstruction phases."""
    print("=" * 60)
    print("CATEGORY SEMANTICS RECONSTRUCTION - PHASE C")
    print("=" * 60)

    # Load data files
    print("\nLoading data files...")

    folio_db = load_json('folio_feature_database.json')
    visual_coding = load_json('visual_coding_complete.json')
    internal_reuse = load_json('h1_2_internal_reuse.json')
    classifier_signatures = load_json('h2_1_classifier_signatures.json')
    hub_singleton = load_json('h2_2_hub_singleton_contrast.json')
    cocitation = load_json('h4_1_cocitation_structure.json')

    reference_graph = load_reference_graph('reference_graph.graphml')
    transcription = load_transcription('data/transcriptions/interlinear_full_words.txt')

    print("  Data files loaded successfully")

    # Store all results for cross-referencing
    all_results = {}

    # Phase C1: Category Feature Profiles
    print("\n" + "=" * 60)
    print("PHASE C1: CATEGORY FEATURE PROFILES")
    print("=" * 60)

    c1_1 = phase_c1_1_category_visual_profiles(visual_coding, folio_db)
    save_json(c1_1, 'c1_1_category_visual_profiles.json')
    all_results['c1_1'] = c1_1

    c1_2 = phase_c1_2_category_classifier_profiles(classifier_signatures, hub_singleton, folio_db)
    save_json(c1_2, 'c1_2_category_classifier_profiles.json')
    all_results['c1_2'] = c1_2

    c1_3 = phase_c1_3_category_defining_features(c1_1, c1_2)
    save_json(c1_3, 'c1_3_category_defining_features.json')
    all_results['c1_3'] = c1_3

    # Phase C2: Category Hierarchy
    print("\n" + "=" * 60)
    print("PHASE C2: CATEGORY HIERARCHY")
    print("=" * 60)

    c2_1 = phase_c2_1_category_hierarchy(internal_reuse, hub_singleton, folio_db)
    save_json(c2_1, 'c2_1_category_hierarchy.json')
    all_results['c2_1'] = c2_1

    c2_2 = phase_c2_2_classifier_clusters(c1_2, folio_db)
    save_json(c2_2, 'c2_2_classifier_clusters.json')
    all_results['c2_2'] = c2_2

    c2_3 = phase_c2_3_cocitation_clusters(cocitation, hub_singleton)
    save_json(c2_3, 'c2_3_cocitation_clusters.json')
    all_results['c2_3'] = c2_3

    # Phase C3: Intra-Category Analysis
    print("\n" + "=" * 60)
    print("PHASE C3: INTRA-CATEGORY ANALYSIS")
    print("=" * 60)

    c3_1 = phase_c3_1_intracategory_variation(folio_db)
    save_json(c3_1, 'c3_1_intracategory_variation.json')
    all_results['c3_1'] = c3_1

    c3_2 = phase_c3_2_part_specific_vocabulary(folio_db)
    save_json(c3_2, 'c3_2_part_specific_vocabulary.json')
    all_results['c3_2'] = c3_2

    # Phase C4: Currier B Rule Analysis
    print("\n" + "=" * 60)
    print("PHASE C4: CURRIER B RULE ANALYSIS")
    print("=" * 60)

    c4_1 = phase_c4_1_b_reference_contexts(reference_graph, transcription, folio_db)
    save_json(c4_1, 'c4_1_b_reference_contexts.json')
    all_results['c4_1'] = c4_1

    c4_2 = phase_c4_2_category_usage_patterns(c4_1, hub_singleton)
    save_json(c4_2, 'c4_2_category_usage_patterns.json')
    all_results['c4_2'] = c4_2

    c4_3 = phase_c4_3_b_entry_structure(c4_1, folio_db)
    save_json(c4_3, 'c4_3_b_entry_structure.json')
    all_results['c4_3'] = c4_3

    # Phase C5: Cross-Validation
    print("\n" + "=" * 60)
    print("PHASE C5: CROSS-VALIDATION")
    print("=" * 60)

    c5_1 = phase_c5_1_cross_validation(c1_1, c2_2, c2_3)
    save_json(c5_1, 'c5_1_cross_validation.json')
    all_results['c5_1'] = c5_1

    c5_2 = phase_c5_2_correlation_reinterpretation(c1_1, c1_2)
    save_json(c5_2, 'c5_2_correlation_reinterpretation.json')
    all_results['c5_2'] = c5_2

    # Phase C6: Synthesis
    print("\n" + "=" * 60)
    print("PHASE C6: SYNTHESIS")
    print("=" * 60)

    c6_1 = phase_c6_1_category_system_model(all_results)
    save_json(c6_1, 'c6_1_category_system_model.json')
    all_results['c6_1'] = c6_1

    c6_2 = phase_c6_2_semantic_recovery_assessment(c6_1, all_results)
    save_json(c6_2, 'c6_2_semantic_recovery_assessment.json')
    all_results['c6_2'] = c6_2

    c6_3 = phase_c6_3_new_constraints(all_results)
    save_json(c6_3, 'c6_3_new_constraints.json')
    all_results['c6_3'] = c6_3

    # Final summary
    print("\n" + "=" * 60)
    print("CATEGORY SEMANTICS RECONSTRUCTION COMPLETE")
    print("=" * 60)
    print(f"\nOutput files generated: 16")
    print(f"Primary organizing principle: {c6_1.get('model', {}).get('primary_organizing_principle', 'UNKNOWN')}")
    print(f"New constraints identified: {len(c6_3.get('new_constraints', []))}")
    print(f"Semantic recovery assessment: {c6_2.get('overall', {}).get('conclusion', 'UNKNOWN')}")


if __name__ == '__main__':
    main()
