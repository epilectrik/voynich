#!/usr/bin/env python3
"""
Phase 6: Semantic Reconstruction
Reconstruct semantic relationships without guessing meanings.

Phase 6A: Middle Semantics via Differential Context
Phase 6B: Affix Semantics as Operators
Phase 6C: Entry-Level Semantic Signatures
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
import math
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform

# Load corpus (same pattern as heading_word_analysis.py)
def load_corpus():
    """Load the interlinear corpus."""
    corpus_path = os.path.join('data', 'transcriptions', 'interlinear_full_words.txt')
    entries = defaultdict(list)
    currier_map = {}  # folio -> A or B

    with open(corpus_path, 'r', encoding='utf-8') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"')  # Column 0: word
                folio = parts[2].strip('"')  # Column 2: folio
                language = parts[6].strip('"')  # Column 6: language (A or B)

                if word and not word.startswith('[') and not word.startswith('<') and not word.startswith('*'):
                    entries[folio].append(word)
                    if folio not in currier_map:
                        currier_map[folio] = language

    return dict(entries), currier_map

# Known affixes from heading_word_analysis.py
KNOWN_PREFIXES = {
    'qo', 'ch', 'sh', 'da', 'ok', 'ot', 'ol', 'ar', 'al', 'or',
    'ct', 'yk', 'qe', 'qot', 'che', 'she', 'cho', 'sho', 'dai',
    'oko', 'ota', 'olo', 'ara', 'cha', 'sha', 'oke', 'ote', 'qok',
    'pc', 'po', 'ps', 'ts', 'cp', 'cf', 'op', 'of', 'fc', 'yp'
}

KNOWN_SUFFIXES = {
    'aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eedy', 'y',
    'ol', 'al', 'or', 'ar', 'am', 'om', 'an', 'hy', 'eey'
}

def get_prefix(word):
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) > length and word[:length] in KNOWN_PREFIXES:
            return word[:length]
    return None

def get_suffix(word):
    """Extract suffix from word."""
    for length in [4, 3, 2, 1]:
        if len(word) > length and word[-length:] in KNOWN_SUFFIXES:
            return word[-length:]
    return None

def extract_middle(word):
    """Extract middle using fixed_1_1 method (best from Phase 5)."""
    if len(word) <= 2:
        return word
    return word[1:-1]

def load_layer_assignments():
    """Load token layer assignments from Phase G."""
    with open('phase2a_layer_assignments.json', 'r') as f:
        data = json.load(f)
    return data['assignments'], data['layer_populations']

def load_hub_info():
    """Load hub folio information."""
    with open('h2_2_hub_singleton_contrast.json', 'r') as f:
        data = json.load(f)

    hub_folios = {}
    for member in data['group_statistics']['hub']['members']:
        hub_folios[member['folio']] = member['heading']

    return hub_folios

# ========== PHASE 6A: Middle Semantics ==========

def phase_6a_middle_semantics(entries, currier_map, hub_folios, layer_assignments):
    """Phase 6A: Map middle semantics via differential context."""
    print("\n=== Phase 6A: Middle Semantics via Differential Context ===")

    results = {
        "metadata": {
            "phase": "6A",
            "title": "Middle Semantics via Differential Context",
            "timestamp": datetime.now().isoformat()
        }
    }

    # 1. Middle-Hub Association Matrix
    print("  Building middle-hub association matrix...")
    middle_hub_counts = defaultdict(lambda: defaultdict(int))
    middle_total = Counter()
    hub_words = list(set(hub_folios.values()))

    for folio, words in entries.items():
        # Identify which hubs are referenced in this entry
        hubs_in_entry = set()
        for w in words:
            if w in hub_words:
                hubs_in_entry.add(w)

        # Count middle occurrences by hub association
        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:  # Skip single chars
                middle_total[middle] += 1
                for hub in hubs_in_entry:
                    middle_hub_counts[middle][hub] += 1

    # Compute association strengths (normalized)
    middle_hub_matrix = {}
    frequent_middles = [m for m, c in middle_total.items() if c >= 10]

    for middle in frequent_middles[:100]:  # Top 100 frequent middles
        hub_profile = {}
        for hub in hub_words:
            count = middle_hub_counts[middle][hub]
            rate = count / middle_total[middle] if middle_total[middle] > 0 else 0
            hub_profile[hub] = round(rate, 4)

        # Compute specificity (entropy)
        values = [v for v in hub_profile.values() if v > 0]
        entropy = -sum(p * math.log2(p) for p in values) if values else 0

        middle_hub_matrix[middle] = {
            "hub_profile": hub_profile,
            "total_count": middle_total[middle],
            "entropy": round(entropy, 3),
            "hub_specific": entropy < 1.5 and max(hub_profile.values()) > 0.3
        }

    results["middle_hub_matrix"] = {
        "hubs_analyzed": hub_words,
        "middles_analyzed": len(middle_hub_matrix),
        "hub_specific_middles": [m for m, v in middle_hub_matrix.items() if v["hub_specific"]],
        "sample": {k: v for k, v in list(middle_hub_matrix.items())[:20]}
    }

    # 2. Middle-Slot Distribution
    print("  Building middle-slot distribution...")
    middle_slot_counts = defaultdict(lambda: defaultdict(int))

    for folio, words in entries.items():
        entry_len = len(words)
        for i, w in enumerate(words):
            middle = extract_middle(w)
            if len(middle) >= 2 and entry_len > 0:
                # Normalize position to slot (0-9)
                slot = min(9, int(10 * i / entry_len))
                middle_slot_counts[middle][slot] += 1

    middle_slot_distribution = {}
    for middle in frequent_middles[:100]:
        slot_profile = {str(s): middle_slot_counts[middle].get(s, 0) for s in range(10)}
        total = sum(slot_profile.values())
        normalized = {s: round(c / total, 3) if total > 0 else 0 for s, c in slot_profile.items()}

        # Compute slot restriction (max deviation from uniform)
        expected = 0.1
        max_dev = max(abs(v - expected) for v in normalized.values())
        slot_restricted = max_dev > 0.15

        middle_slot_distribution[middle] = {
            "slot_profile": normalized,
            "total": total,
            "max_deviation": round(max_dev, 3),
            "slot_restricted": slot_restricted
        }

    results["middle_slot_distribution"] = {
        "middles_analyzed": len(middle_slot_distribution),
        "slot_restricted_middles": [m for m, v in middle_slot_distribution.items() if v["slot_restricted"]],
        "sample": {k: v for k, v in list(middle_slot_distribution.items())[:20]}
    }

    # 3. Middle-Modifier Compatibility
    print("  Building middle-affix compatibility matrix...")
    middle_prefix_counts = defaultdict(lambda: Counter())
    middle_suffix_counts = defaultdict(lambda: Counter())

    for folio, words in entries.items():
        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:
                prefix = get_prefix(w)
                suffix = get_suffix(w)
                if prefix:
                    middle_prefix_counts[middle][prefix] += 1
                if suffix:
                    middle_suffix_counts[middle][suffix] += 1

    middle_affix_compatibility = {}
    for middle in frequent_middles[:100]:
        prefix_profile = dict(middle_prefix_counts[middle].most_common(10))
        suffix_profile = dict(middle_suffix_counts[middle].most_common(10))

        # Compute affix diversity
        prefix_diversity = len(middle_prefix_counts[middle])
        suffix_diversity = len(middle_suffix_counts[middle])

        middle_affix_compatibility[middle] = {
            "top_prefixes": prefix_profile,
            "top_suffixes": suffix_profile,
            "prefix_diversity": prefix_diversity,
            "suffix_diversity": suffix_diversity,
            "constrained": prefix_diversity < 5 or suffix_diversity < 5
        }

    results["middle_affix_compatibility"] = {
        "middles_analyzed": len(middle_affix_compatibility),
        "constrained_middles": [m for m, v in middle_affix_compatibility.items() if v["constrained"]],
        "sample": {k: v for k, v in list(middle_affix_compatibility.items())[:20]}
    }

    # 4. Pairwise Differential Analysis
    print("  Performing pairwise differential analysis...")

    # Build feature vectors for clustering
    feature_vectors = {}
    all_prefixes = list(KNOWN_PREFIXES)[:20]
    all_suffixes = list(KNOWN_SUFFIXES)[:10]

    for middle in frequent_middles[:100]:
        vec = []
        # Prefix features
        prefix_total = sum(middle_prefix_counts[middle].values())
        for p in all_prefixes:
            rate = middle_prefix_counts[middle][p] / prefix_total if prefix_total > 0 else 0
            vec.append(rate)
        # Suffix features
        suffix_total = sum(middle_suffix_counts[middle].values())
        for s in all_suffixes:
            rate = middle_suffix_counts[middle][s] / suffix_total if suffix_total > 0 else 0
            vec.append(rate)
        # Slot features
        slot_total = sum(middle_slot_counts[middle].values())
        for s in range(10):
            rate = middle_slot_counts[middle][s] / slot_total if slot_total > 0 else 0
            vec.append(rate)

        feature_vectors[middle] = vec

    # Cluster middles
    if len(feature_vectors) >= 10:
        middle_list = list(feature_vectors.keys())
        vectors = np.array([feature_vectors[m] for m in middle_list])

        # Handle any NaN values
        vectors = np.nan_to_num(vectors, 0)

        if np.any(vectors):
            distances = pdist(vectors, 'cosine')
            distances = np.nan_to_num(distances, 1)  # Replace NaN distances with max
            linkage_matrix = linkage(distances, method='ward')
            clusters = fcluster(linkage_matrix, t=5, criterion='maxclust')

            middle_clusters = defaultdict(list)
            for i, middle in enumerate(middle_list):
                middle_clusters[int(clusters[i])].append(middle)

            results["pairwise_differential"] = {
                "clusters_found": len(middle_clusters),
                "cluster_membership": {f"cluster_{k}": v for k, v in middle_clusters.items()},
                "cluster_sizes": {f"cluster_{k}": len(v) for k, v in middle_clusters.items()}
            }
        else:
            results["pairwise_differential"] = {"status": "NO_VARIANCE", "message": "Vectors have no variance"}
    else:
        results["pairwise_differential"] = {"status": "INSUFFICIENT_DATA"}

    # Identify semantic axes
    hub_specific = results["middle_hub_matrix"]["hub_specific_middles"]
    slot_restricted = results["middle_slot_distribution"]["slot_restricted_middles"]
    constrained = results["middle_affix_compatibility"]["constrained_middles"]

    results["semantic_axes_detected"] = {
        "axis_hub_specificity": {
            "count": len(hub_specific),
            "examples": hub_specific[:10]
        },
        "axis_slot_restriction": {
            "count": len(slot_restricted),
            "examples": slot_restricted[:10]
        },
        "axis_affix_constraint": {
            "count": len(constrained),
            "examples": constrained[:10]
        }
    }

    with open('phase6a_middle_semantics.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  Hub-specific middles: {len(hub_specific)}")
    print(f"  Slot-restricted middles: {len(slot_restricted)}")
    print(f"  Affix-constrained middles: {len(constrained)}")

    return results

# ========== PHASE 6B: Affix Semantics ==========

def phase_6b_affix_operators(entries, currier_map, hub_folios, layer_assignments):
    """Phase 6B: Determine what affixes DO functionally."""
    print("\n=== Phase 6B: Affix Semantics as Operators ===")

    results = {
        "metadata": {
            "phase": "6B",
            "title": "Affix Semantics as Operators",
            "timestamp": datetime.now().isoformat()
        }
    }

    hub_words = list(set(hub_folios.values()))

    # 1. Affix Effect on Hub Association
    print("  Analyzing affix effect on hub association...")

    # For tokens with same middle but different prefix, how does hub distribution change?
    middle_to_tokens = defaultdict(list)
    token_hub_association = {}

    for folio, words in entries.items():
        hub_in_entry = None
        for w in words:
            if w in hub_words:
                hub_in_entry = w
                break

        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:
                middle_to_tokens[middle].append(w)
                if hub_in_entry:
                    if w not in token_hub_association:
                        token_hub_association[w] = Counter()
                    token_hub_association[w][hub_in_entry] += 1

    # Find middles with multiple token forms
    prefix_hub_effects = defaultdict(lambda: defaultdict(int))
    prefix_total = Counter()

    for middle, tokens in middle_to_tokens.items():
        unique_tokens = set(tokens)
        if len(unique_tokens) >= 3:
            for token in unique_tokens:
                prefix = get_prefix(token)
                if prefix and token in token_hub_association:
                    for hub, count in token_hub_association[token].items():
                        prefix_hub_effects[prefix][hub] += count
                        prefix_total[prefix] += count

    affix_hub_effects = {}
    for prefix in list(KNOWN_PREFIXES)[:30]:
        if prefix_total[prefix] >= 10:
            hub_profile = {}
            for hub in hub_words:
                rate = prefix_hub_effects[prefix][hub] / prefix_total[prefix]
                hub_profile[hub] = round(rate, 4)

            affix_hub_effects[prefix] = {
                "hub_profile": hub_profile,
                "total": prefix_total[prefix],
                "dominant_hub": max(hub_profile.items(), key=lambda x: x[1]) if hub_profile else None
            }

    results["affix_hub_effects"] = affix_hub_effects

    # 2. Affix Effect on Slot Position
    print("  Analyzing affix effect on slot position...")

    prefix_slot_counts = defaultdict(lambda: Counter())
    suffix_slot_counts = defaultdict(lambda: Counter())

    for folio, words in entries.items():
        entry_len = len(words)
        for i, w in enumerate(words):
            slot = min(9, int(10 * i / entry_len)) if entry_len > 0 else 0
            prefix = get_prefix(w)
            suffix = get_suffix(w)
            if prefix:
                prefix_slot_counts[prefix][slot] += 1
            if suffix:
                suffix_slot_counts[suffix][slot] += 1

    affix_slot_effects = {
        "prefixes": {},
        "suffixes": {}
    }

    for prefix in list(KNOWN_PREFIXES)[:30]:
        total = sum(prefix_slot_counts[prefix].values())
        if total >= 20:
            slot_profile = {str(s): round(prefix_slot_counts[prefix][s] / total, 3) for s in range(10)}
            mean_slot = sum(s * prefix_slot_counts[prefix][s] for s in range(10)) / total
            affix_slot_effects["prefixes"][prefix] = {
                "slot_profile": slot_profile,
                "mean_slot": round(mean_slot, 2),
                "early_bias": mean_slot < 4,
                "late_bias": mean_slot > 6
            }

    for suffix in list(KNOWN_SUFFIXES):
        total = sum(suffix_slot_counts[suffix].values())
        if total >= 20:
            slot_profile = {str(s): round(suffix_slot_counts[suffix][s] / total, 3) for s in range(10)}
            mean_slot = sum(s * suffix_slot_counts[suffix][s] for s in range(10)) / total
            affix_slot_effects["suffixes"][suffix] = {
                "slot_profile": slot_profile,
                "mean_slot": round(mean_slot, 2),
                "early_bias": mean_slot < 4,
                "late_bias": mean_slot > 6
            }

    results["affix_slot_effects"] = affix_slot_effects

    # 3. Affix Effect on Neighboring Tokens
    print("  Analyzing affix effect on neighboring tokens...")

    prefix_follower_counts = defaultdict(Counter)
    prefix_preceder_counts = defaultdict(Counter)

    for folio, words in entries.items():
        for i, w in enumerate(words):
            prefix = get_prefix(w)
            if prefix:
                if i > 0:
                    prev_prefix = get_prefix(words[i-1])
                    if prev_prefix:
                        prefix_preceder_counts[prefix][prev_prefix] += 1
                if i < len(words) - 1:
                    next_prefix = get_prefix(words[i+1])
                    if next_prefix:
                        prefix_follower_counts[prefix][next_prefix] += 1

    affix_context_effects = {}
    for prefix in list(KNOWN_PREFIXES)[:30]:
        if sum(prefix_follower_counts[prefix].values()) >= 20:
            affix_context_effects[prefix] = {
                "top_followers": dict(prefix_follower_counts[prefix].most_common(5)),
                "top_preceders": dict(prefix_preceder_counts[prefix].most_common(5)),
                "follower_diversity": len(prefix_follower_counts[prefix]),
                "preceder_diversity": len(prefix_preceder_counts[prefix])
            }

    results["affix_context_effects"] = affix_context_effects

    # 4. Affix Clustering by Function
    print("  Clustering affixes by behavioral profile...")

    # Build feature vectors for prefixes
    affix_features = {}
    for prefix in list(KNOWN_PREFIXES)[:30]:
        if prefix in affix_slot_effects["prefixes"]:
            slot_data = affix_slot_effects["prefixes"][prefix]
            hub_data = affix_hub_effects.get(prefix, {})

            features = []
            # Slot features
            for s in range(10):
                features.append(float(slot_data["slot_profile"].get(str(s), 0)))
            # Hub features
            for hub in hub_words:
                features.append(hub_data.get("hub_profile", {}).get(hub, 0))

            affix_features[prefix] = features

    # Cluster affixes
    if len(affix_features) >= 5:
        affix_list = list(affix_features.keys())
        vectors = np.array([affix_features[a] for a in affix_list])
        vectors = np.nan_to_num(vectors, 0)

        if np.any(vectors):
            distances = pdist(vectors, 'cosine')
            distances = np.nan_to_num(distances, 1)
            linkage_matrix = linkage(distances, method='ward')
            clusters = fcluster(linkage_matrix, t=4, criterion='maxclust')

            affix_clusters = defaultdict(list)
            for i, affix in enumerate(affix_list):
                affix_clusters[int(clusters[i])].append(affix)

            results["affix_functional_clusters"] = {
                "clusters_found": len(affix_clusters),
                "cluster_membership": {f"cluster_{k}": v for k, v in affix_clusters.items()}
            }
        else:
            results["affix_functional_clusters"] = {"status": "NO_VARIANCE"}
    else:
        results["affix_functional_clusters"] = {"status": "INSUFFICIENT_DATA"}

    # Identify operator candidates
    operator_candidates = []
    early_biased = [p for p, v in affix_slot_effects["prefixes"].items() if v["early_bias"]]
    late_biased = [p for p, v in affix_slot_effects["prefixes"].items() if v["late_bias"]]

    for prefix in early_biased:
        operator_candidates.append({
            "affix": prefix,
            "type": "POSITION_MARKER",
            "behavior": "early_bias",
            "evidence": f"mean_slot={affix_slot_effects['prefixes'][prefix]['mean_slot']}"
        })

    for prefix in late_biased:
        operator_candidates.append({
            "affix": prefix,
            "type": "POSITION_MARKER",
            "behavior": "late_bias",
            "evidence": f"mean_slot={affix_slot_effects['prefixes'][prefix]['mean_slot']}"
        })

    results["operator_candidates"] = operator_candidates

    with open('phase6b_affix_operators.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  Affixes with hub effects: {len(affix_hub_effects)}")
    print(f"  Early-biased prefixes: {len(early_biased)}")
    print(f"  Late-biased prefixes: {len(late_biased)}")
    print(f"  Operator candidates: {len(operator_candidates)}")

    return results

# ========== PHASE 6C: Entry-Level Signatures ==========

def phase_6c_entry_signatures(entries, currier_map, hub_folios, layer_assignments):
    """Phase 6C: Treat entries as composite semantic objects."""
    print("\n=== Phase 6C: Entry-Level Semantic Signatures ===")

    results = {
        "metadata": {
            "phase": "6C",
            "title": "Entry-Level Semantic Signatures",
            "timestamp": datetime.now().isoformat()
        }
    }

    gamma_tokens = set(layer_assignments.get('GAMMA', []))
    hub_words = set(hub_folios.values())

    # 1. Entry Vectorization
    print("  Vectorizing entries...")

    # Build vocabulary for bag-of-middles
    all_middles = Counter()
    all_prefixes_in_corpus = Counter()
    all_suffixes_in_corpus = Counter()

    for folio, words in entries.items():
        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:
                all_middles[middle] += 1
            prefix = get_prefix(w)
            if prefix:
                all_prefixes_in_corpus[prefix] += 1
            suffix = get_suffix(w)
            if suffix:
                all_suffixes_in_corpus[suffix] += 1

    top_middles = [m for m, c in all_middles.most_common(50)]
    top_prefixes = [p for p, c in all_prefixes_in_corpus.most_common(20)]
    top_suffixes = [s for s, c in all_suffixes_in_corpus.most_common(15)]

    entry_vectors = {}
    entry_features = {}

    for folio, words in entries.items():
        # Bag of middles
        middle_counts = Counter()
        prefix_counts = Counter()
        suffix_counts = Counter()

        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:
                middle_counts[middle] += 1
            prefix = get_prefix(w)
            if prefix:
                prefix_counts[prefix] += 1
            suffix = get_suffix(w)
            if suffix:
                suffix_counts[suffix] += 1

        # Build feature vector
        total_words = len(words) if words else 1

        vec = []
        # Middle features (normalized)
        for m in top_middles:
            vec.append(middle_counts[m] / total_words)
        # Prefix features
        for p in top_prefixes:
            vec.append(prefix_counts[p] / total_words)
        # Suffix features
        for s in top_suffixes:
            vec.append(suffix_counts[s] / total_words)

        entry_vectors[folio] = vec

        # Compute additional features
        gamma_count = sum(1 for w in words if w in gamma_tokens)
        hub_count = sum(1 for w in words if w in hub_words)

        entry_features[folio] = {
            "word_count": len(words),
            "gamma_density": round(gamma_count / total_words, 3),
            "hub_mentions": hub_count,
            "unique_middles": len(set(extract_middle(w) for w in words)),
            "prefix_diversity": len(prefix_counts),
            "suffix_diversity": len(suffix_counts),
            "currier": currier_map.get(folio, 'A')
        }

    results["entry_features_summary"] = {
        "total_entries": len(entry_features),
        "feature_dimensions": len(vec) if entry_vectors else 0,
        "sample": {k: v for k, v in list(entry_features.items())[:10]}
    }

    # 2. Entry Clustering
    print("  Clustering entries...")

    if len(entry_vectors) >= 10:
        folio_list = list(entry_vectors.keys())
        vectors = np.array([entry_vectors[f] for f in folio_list])
        vectors = np.nan_to_num(vectors, 0)

        if np.any(vectors):
            distances = pdist(vectors, 'cosine')
            distances = np.nan_to_num(distances, 1)
            linkage_matrix = linkage(distances, method='ward')
            clusters = fcluster(linkage_matrix, t=8, criterion='maxclust')

            entry_clusters = defaultdict(list)
            for i, folio in enumerate(folio_list):
                entry_clusters[int(clusters[i])].append(folio)

            # Analyze cluster composition
            cluster_analysis = {}
            for cluster_id, folios in entry_clusters.items():
                a_count = sum(1 for f in folios if currier_map.get(f, 'A') == 'A')
                b_count = len(folios) - a_count
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    "size": len(folios),
                    "currier_a": a_count,
                    "currier_b": b_count,
                    "a_ratio": round(a_count / len(folios), 3),
                    "members": folios[:10]  # Sample
                }

            results["entry_clusters"] = {
                "clusters_found": len(entry_clusters),
                "cluster_analysis": cluster_analysis
            }
        else:
            results["entry_clusters"] = {"status": "NO_VARIANCE"}
    else:
        results["entry_clusters"] = {"status": "INSUFFICIENT_DATA"}

    # 3. A-text vs B-text Semantic Comparison
    print("  Comparing A-text vs B-text...")

    a_entries = {f: w for f, w in entries.items() if currier_map.get(f, 'A') == 'A'}
    b_entries = {f: w for f, w in entries.items() if currier_map.get(f, 'A') == 'B'}

    # Aggregate statistics
    a_stats = {
        "count": len(a_entries),
        "mean_length": np.mean([len(w) for w in a_entries.values()]) if a_entries else 0,
        "middle_distribution": Counter(),
        "prefix_distribution": Counter(),
        "suffix_distribution": Counter()
    }

    b_stats = {
        "count": len(b_entries),
        "mean_length": np.mean([len(w) for w in b_entries.values()]) if b_entries else 0,
        "middle_distribution": Counter(),
        "prefix_distribution": Counter(),
        "suffix_distribution": Counter()
    }

    for words in a_entries.values():
        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:
                a_stats["middle_distribution"][middle] += 1
            prefix = get_prefix(w)
            if prefix:
                a_stats["prefix_distribution"][prefix] += 1
            suffix = get_suffix(w)
            if suffix:
                a_stats["suffix_distribution"][suffix] += 1

    for words in b_entries.values():
        for w in words:
            middle = extract_middle(w)
            if len(middle) >= 2:
                b_stats["middle_distribution"][middle] += 1
            prefix = get_prefix(w)
            if prefix:
                b_stats["prefix_distribution"][prefix] += 1
            suffix = get_suffix(w)
            if suffix:
                b_stats["suffix_distribution"][suffix] += 1

    # Compute enrichment ratios
    a_total_middles = sum(a_stats["middle_distribution"].values())
    b_total_middles = sum(b_stats["middle_distribution"].values())

    middle_enrichment = {}
    for middle in top_middles[:30]:
        a_rate = a_stats["middle_distribution"][middle] / a_total_middles if a_total_middles > 0 else 0
        b_rate = b_stats["middle_distribution"][middle] / b_total_middles if b_total_middles > 0 else 0

        if a_rate > 0 and b_rate > 0:
            enrichment = round(b_rate / a_rate, 3)
            middle_enrichment[middle] = {
                "a_rate": round(a_rate, 5),
                "b_rate": round(b_rate, 5),
                "b_enrichment": enrichment,
                "significant": enrichment > 2.0 or enrichment < 0.5
            }

    # Identify A-specific and B-specific middles
    a_specific = [m for m, v in middle_enrichment.items() if v.get("b_enrichment", 1) < 0.5]
    b_specific = [m for m, v in middle_enrichment.items() if v.get("b_enrichment", 1) > 2.0]

    results["a_vs_b_comparison"] = {
        "a_entries": len(a_entries),
        "b_entries": len(b_entries),
        "a_mean_length": round(a_stats["mean_length"], 1),
        "b_mean_length": round(b_stats["mean_length"], 1),
        "middle_enrichment": middle_enrichment,
        "a_specific_middles": a_specific,
        "b_specific_middles": b_specific,
        "differentiation_strength": "STRONG" if len(a_specific) + len(b_specific) > 10 else "MODERATE"
    }

    # 4. Entry Transition Patterns (cross-entry relationships)
    print("  Analyzing cross-entry patterns...")

    # For each pair of adjacent folios, compute vocabulary overlap
    folio_list_sorted = sorted(entries.keys())
    transitions = []

    for i in range(len(folio_list_sorted) - 1):
        f1, f2 = folio_list_sorted[i], folio_list_sorted[i+1]
        words1 = set(entries[f1])
        words2 = set(entries[f2])

        if words1 and words2:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            jaccard = intersection / union if union > 0 else 0

            transitions.append({
                "from": f1,
                "to": f2,
                "jaccard": round(jaccard, 4),
                "shared_words": intersection
            })

    # Compute statistics
    jaccard_values = [t["jaccard"] for t in transitions]

    results["cross_entry_patterns"] = {
        "transitions_analyzed": len(transitions),
        "mean_jaccard": round(np.mean(jaccard_values), 4) if jaccard_values else 0,
        "std_jaccard": round(np.std(jaccard_values), 4) if jaccard_values else 0,
        "high_overlap_transitions": [t for t in transitions if t["jaccard"] > 0.3][:10],
        "narrative_flow": "STRONG" if np.mean(jaccard_values) > 0.2 else "WEAK" if np.mean(jaccard_values) < 0.1 else "MODERATE"
    }

    with open('phase6c_entry_signatures.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"  Entry clusters found: {results.get('entry_clusters', {}).get('clusters_found', 0)}")
    print(f"  A-specific middles: {len(a_specific)}")
    print(f"  B-specific middles: {len(b_specific)}")
    print(f"  Cross-entry flow: {results['cross_entry_patterns']['narrative_flow']}")

    return results

# ========== SYNTHESIS ==========

def generate_synthesis(results_6a, results_6b, results_6c):
    """Generate Phase 6 synthesis."""
    print("\n=== Phase 6 Synthesis ===")

    synthesis = {
        "metadata": {
            "phase": "6",
            "title": "Semantic Reconstruction Synthesis",
            "timestamp": datetime.now().isoformat()
        },
        "findings": {},
        "semantic_model": {},
        "implications": []
    }

    # Middle semantics findings
    hub_specific_count = len(results_6a.get("semantic_axes_detected", {}).get("axis_hub_specificity", {}).get("examples", []))
    slot_restricted_count = len(results_6a.get("semantic_axes_detected", {}).get("axis_slot_restriction", {}).get("examples", []))
    affix_constrained_count = len(results_6a.get("semantic_axes_detected", {}).get("axis_affix_constraint", {}).get("examples", []))

    synthesis["findings"]["middle_semantics"] = {
        "hub_specific_middles": hub_specific_count,
        "slot_restricted_middles": slot_restricted_count,
        "affix_constrained_middles": affix_constrained_count,
        "resonance": "GREEN" if hub_specific_count > 5 else "YELLOW"
    }

    # Affix operator findings
    operator_count = len(results_6b.get("operator_candidates", []))
    affix_clusters = results_6b.get("affix_functional_clusters", {}).get("clusters_found", 0)

    synthesis["findings"]["affix_operators"] = {
        "operator_candidates": operator_count,
        "functional_clusters": affix_clusters,
        "resonance": "GREEN" if operator_count > 5 else "YELLOW"
    }

    # Entry signature findings
    entry_clusters = results_6c.get("entry_clusters", {}).get("clusters_found", 0)
    a_specific = len(results_6c.get("a_vs_b_comparison", {}).get("a_specific_middles", []))
    b_specific = len(results_6c.get("a_vs_b_comparison", {}).get("b_specific_middles", []))

    synthesis["findings"]["entry_signatures"] = {
        "entry_clusters": entry_clusters,
        "a_specific_middles": a_specific,
        "b_specific_middles": b_specific,
        "differentiation_strength": results_6c.get("a_vs_b_comparison", {}).get("differentiation_strength", "UNKNOWN"),
        "resonance": "GREEN" if a_specific + b_specific > 5 else "YELLOW"
    }

    # Build semantic model
    synthesis["semantic_model"] = {
        "structure": "MIDDLE-CENTRIC",
        "description": "Semantic meaning primarily carried by middles, with affixes as operators/modifiers",
        "axes": [
            {
                "name": "HUB_ASSOCIATION",
                "description": "Middles associate with specific hub categories",
                "evidence": f"{hub_specific_count} hub-specific middles identified"
            },
            {
                "name": "POSITIONAL_ROLE",
                "description": "Some middles/affixes are slot-restricted",
                "evidence": f"{slot_restricted_count} slot-restricted middles"
            },
            {
                "name": "A_VS_B_SEMANTIC_SPACE",
                "description": "Currier A and B have distinct vocabulary profiles",
                "evidence": f"{a_specific} A-specific, {b_specific} B-specific middles"
            }
        ],
        "affix_operators": results_6b.get("operator_candidates", [])[:5]
    }

    # Implications
    if hub_specific_count > 5:
        synthesis["implications"].append("Middles cluster by hub association -> categorical semantics recoverable")
    if operator_count > 3:
        synthesis["implications"].append("Affixes show systematic positional effects -> operator semantics recoverable")
    if a_specific + b_specific > 5:
        synthesis["implications"].append("A vs B show different semantic profiles -> confirms definitional vs applicational split")
    if entry_clusters >= 3:
        synthesis["implications"].append("Entry clusters exist -> content-structure alignment present")

    # Overall assessment
    green_count = sum(1 for v in synthesis["findings"].values() if v.get("resonance") == "GREEN")
    synthesis["overall_status"] = "GREEN" if green_count >= 2 else "YELLOW" if green_count >= 1 else "RED"
    synthesis["overall_status"] += f" - Semantic structure is mappable ({green_count}/3 GREEN findings)"

    with open('phase6_synthesis.json', 'w') as f:
        json.dump(synthesis, f, indent=2)

    print(f"\nOverall Status: {synthesis['overall_status']}")
    print(f"Implications: {len(synthesis['implications'])}")

    return synthesis

def main():
    print("=" * 60)
    print("Phase 6: Semantic Reconstruction")
    print("=" * 60)

    # Load data
    print("\nLoading corpus and previous phase data...")
    entries, currier_map = load_corpus()
    layer_assignments, layer_populations = load_layer_assignments()
    hub_folios = load_hub_info()

    print(f"  Loaded {len(entries)} entries")
    print(f"  Layer assignments: {len(layer_assignments)} tokens")
    print(f"  Hub folios: {len(hub_folios)}")

    # Run Phase 6A
    results_6a = phase_6a_middle_semantics(entries, currier_map, hub_folios, layer_assignments)

    # Run Phase 6B
    results_6b = phase_6b_affix_operators(entries, currier_map, hub_folios, layer_assignments)

    # Run Phase 6C
    results_6c = phase_6c_entry_signatures(entries, currier_map, hub_folios, layer_assignments)

    # Generate synthesis
    synthesis = generate_synthesis(results_6a, results_6b, results_6c)

    print("\n" + "=" * 60)
    print("Phase 6 Complete")
    print("=" * 60)
    print("\nOutput files:")
    print("  - phase6a_middle_semantics.json")
    print("  - phase6b_affix_operators.json")
    print("  - phase6c_entry_signatures.json")
    print("  - phase6_synthesis.json")

if __name__ == "__main__":
    main()
