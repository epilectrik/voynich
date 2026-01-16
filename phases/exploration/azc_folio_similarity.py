#!/usr/bin/env python3
"""
AZC-DEEP Phase 2: Folio Similarity Matrix
==========================================

Computes pairwise similarity between all 30 AZC folios using:
1. Vocabulary Jaccard similarity (token type overlap)
2. Feature cosine similarity (normalized feature vectors)
3. Jensen-Shannon divergence (for distribution features)

Output: results/azc_folio_similarity_matrix.json
"""

import json
import os
import math
from collections import defaultdict

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC-DEEP PHASE 2: FOLIO SIMILARITY MATRIX")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

print("\nLoading folio features...")

with open('results/azc_folio_features.json', 'r', encoding='utf-8') as f:
    feature_data = json.load(f)

folio_features = feature_data['folios']
folios = sorted(folio_features.keys())

print(f"Loaded {len(folios)} folios")

# Load raw transcription for vocabulary Jaccard
print("Loading transcription data for vocabulary comparison...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Build folio vocabulary sets
folio_vocab = defaultdict(set)
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip() != 'H':
            continue
        lang = row.get('language', '')
        if lang in ('NA', ''):  # AZC tokens
            folio = row.get('folio', '')
            word = row.get('word', '')
            if folio and word:
                folio_vocab[folio].add(word)

print(f"Vocabulary sets built for {len(folio_vocab)} folios")

# =============================================================================
# SIMILARITY FUNCTIONS
# =============================================================================

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors (as dicts)."""
    # Get all keys
    all_keys = set(vec1.keys()) | set(vec2.keys())

    # Compute dot product and magnitudes
    dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
    mag1 = math.sqrt(sum(vec1.get(k, 0) ** 2 for k in all_keys))
    mag2 = math.sqrt(sum(vec2.get(k, 0) ** 2 for k in all_keys))

    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def jensen_shannon_divergence(p, q):
    """Compute Jensen-Shannon divergence between two distributions."""
    # Normalize distributions
    all_keys = set(p.keys()) | set(q.keys())

    p_sum = sum(p.values())
    q_sum = sum(q.values())

    if p_sum == 0 or q_sum == 0:
        return 1.0  # Maximum divergence

    p_norm = {k: p.get(k, 0) / p_sum for k in all_keys}
    q_norm = {k: q.get(k, 0) / q_sum for k in all_keys}

    # Compute M = (P + Q) / 2
    m = {k: (p_norm[k] + q_norm[k]) / 2 for k in all_keys}

    # KL divergence
    def kl_div(a, b):
        total = 0
        for k in all_keys:
            if a[k] > 0 and b[k] > 0:
                total += a[k] * math.log2(a[k] / b[k])
        return total

    js_div = (kl_div(p_norm, m) + kl_div(q_norm, m)) / 2

    return js_div

def js_similarity(p, q):
    """Convert JS divergence to similarity (0-1 scale)."""
    js_div = jensen_shannon_divergence(p, q)
    # JS divergence is bounded [0, 1] for log2
    return 1.0 - js_div

# =============================================================================
# BUILD FEATURE VECTORS FOR COSINE SIMILARITY
# =============================================================================

def build_feature_vector(features):
    """Build a normalized feature vector from folio features."""
    vec = {}

    # Scalar features (normalized to 0-1 range based on observed ranges)
    scalar_ranges = {
        'ttr': (0.264, 1.0),
        'a_coverage': (0.506, 1.0),
        'b_coverage': (0.509, 1.0),
        'azc_unique_rate': (0.0, 0.468),
        'link_density': (0.0, 0.135),
        'mean_token_length': (2.77, 5.95),
        'placement_entropy': (0.0, 2.619),
        'ordered_subscript_depth': (0.0, 1.0)
    }

    for feat, (min_val, max_val) in scalar_ranges.items():
        val = features.get(feat, 0)
        if max_val > min_val:
            vec[feat] = (val - min_val) / (max_val - min_val)
        else:
            vec[feat] = 0.0

    # Distribution features (already normalized)
    for key in ['placement_vector', 'prefix_vector', 'suffix_vector']:
        if key in features:
            for k, v in features[key].items():
                vec[f"{key}_{k}"] = v

    return vec

# =============================================================================
# COMPUTE SIMILARITY MATRICES
# =============================================================================

print("\nComputing similarity matrices...")

n = len(folios)

# Initialize matrices
vocab_jaccard = [[0.0] * n for _ in range(n)]
feature_cosine = [[0.0] * n for _ in range(n)]
placement_js = [[0.0] * n for _ in range(n)]
combined = [[0.0] * n for _ in range(n)]

# Build feature vectors
feature_vectors = {f: build_feature_vector(folio_features[f]) for f in folios}

# Compute pairwise similarities
for i, folio_i in enumerate(folios):
    for j, folio_j in enumerate(folios):
        if i == j:
            vocab_jaccard[i][j] = 1.0
            feature_cosine[i][j] = 1.0
            placement_js[i][j] = 1.0
            combined[i][j] = 1.0
        else:
            # Vocabulary Jaccard
            vj = jaccard_similarity(folio_vocab[folio_i], folio_vocab[folio_j])
            vocab_jaccard[i][j] = round(vj, 4)

            # Feature cosine
            fc = cosine_similarity(feature_vectors[folio_i], feature_vectors[folio_j])
            feature_cosine[i][j] = round(fc, 4)

            # Placement JS similarity
            pjs = js_similarity(
                folio_features[folio_i]['placement_vector'],
                folio_features[folio_j]['placement_vector']
            )
            placement_js[i][j] = round(pjs, 4)

            # Combined similarity (equal weights)
            combined[i][j] = round((vj + fc + pjs) / 3, 4)

print("Similarity matrices computed")

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

print("\n" + "=" * 70)
print("SIMILARITY MATRIX SUMMARY")
print("=" * 70)

def matrix_stats(matrix, name):
    """Compute summary statistics for a similarity matrix."""
    n = len(matrix)
    # Get off-diagonal values
    off_diag = [matrix[i][j] for i in range(n) for j in range(n) if i != j]
    if not off_diag:
        return

    mean_sim = sum(off_diag) / len(off_diag)
    min_sim = min(off_diag)
    max_sim = max(off_diag)
    std_sim = math.sqrt(sum((x - mean_sim) ** 2 for x in off_diag) / len(off_diag))

    print(f"\n{name}:")
    print(f"  Mean similarity: {mean_sim:.4f}")
    print(f"  Std deviation:   {std_sim:.4f}")
    print(f"  Min similarity:  {min_sim:.4f}")
    print(f"  Max similarity:  {max_sim:.4f}")

matrix_stats(vocab_jaccard, "Vocabulary Jaccard")
matrix_stats(feature_cosine, "Feature Cosine")
matrix_stats(placement_js, "Placement JS Similarity")
matrix_stats(combined, "Combined Similarity")

# =============================================================================
# MOST/LEAST SIMILAR PAIRS
# =============================================================================

print("\n" + "=" * 70)
print("MOST AND LEAST SIMILAR FOLIO PAIRS")
print("=" * 70)

# Get all pairs with combined similarity
pairs = []
for i, folio_i in enumerate(folios):
    for j, folio_j in enumerate(folios):
        if i < j:  # Avoid duplicates
            pairs.append({
                'folio1': folio_i,
                'folio2': folio_j,
                'combined': combined[i][j],
                'vocab_jaccard': vocab_jaccard[i][j],
                'feature_cosine': feature_cosine[i][j],
                'placement_js': placement_js[i][j],
                'section1': folio_features[folio_i]['section'],
                'section2': folio_features[folio_j]['section']
            })

# Sort by combined similarity
pairs_sorted = sorted(pairs, key=lambda x: x['combined'], reverse=True)

print("\n--- TOP 10 MOST SIMILAR PAIRS ---")
print(f"{'Folio1':<12} {'Folio2':<12} {'Sect':<8} {'Combined':<10} {'Jaccard':<10} {'Cosine':<10} {'PlaceJS':<10}")
print("-" * 80)

for p in pairs_sorted[:10]:
    sect = f"{p['section1']}-{p['section2']}"
    print(f"{p['folio1']:<12} {p['folio2']:<12} {sect:<8} {p['combined']:.4f}     {p['vocab_jaccard']:.4f}     {p['feature_cosine']:.4f}     {p['placement_js']:.4f}")

print("\n--- TOP 10 LEAST SIMILAR PAIRS ---")
for p in pairs_sorted[-10:]:
    sect = f"{p['section1']}-{p['section2']}"
    print(f"{p['folio1']:<12} {p['folio2']:<12} {sect:<8} {p['combined']:.4f}     {p['vocab_jaccard']:.4f}     {p['feature_cosine']:.4f}     {p['placement_js']:.4f}")

# =============================================================================
# WITHIN-SECTION VS BETWEEN-SECTION SIMILARITY
# =============================================================================

print("\n" + "=" * 70)
print("WITHIN-SECTION VS BETWEEN-SECTION SIMILARITY")
print("=" * 70)

within_section = [p for p in pairs if p['section1'] == p['section2']]
between_section = [p for p in pairs if p['section1'] != p['section2']]

if within_section:
    within_mean = sum(p['combined'] for p in within_section) / len(within_section)
    print(f"\nWithin-section pairs: {len(within_section)}")
    print(f"  Mean combined similarity: {within_mean:.4f}")

if between_section:
    between_mean = sum(p['combined'] for p in between_section) / len(between_section)
    print(f"\nBetween-section pairs: {len(between_section)}")
    print(f"  Mean combined similarity: {between_mean:.4f}")

if within_section and between_section:
    ratio = within_mean / between_mean if between_mean > 0 else float('inf')
    print(f"\nWithin/Between ratio: {ratio:.2f}x")

# =============================================================================
# SAVE RESULTS
# =============================================================================

output_path = 'results/azc_folio_similarity_matrix.json'

output = {
    'metadata': {
        'num_folios': n,
        'folio_order': folios,
        'metrics': ['vocab_jaccard', 'feature_cosine', 'placement_js', 'combined']
    },
    'matrices': {
        'vocab_jaccard': vocab_jaccard,
        'feature_cosine': feature_cosine,
        'placement_js': placement_js,
        'combined': combined
    },
    'pair_summary': {
        'most_similar': pairs_sorted[:20],
        'least_similar': pairs_sorted[-20:]
    },
    'section_analysis': {
        'within_section_mean': sum(p['combined'] for p in within_section) / len(within_section) if within_section else 0,
        'between_section_mean': sum(p['combined'] for p in between_section) / len(between_section) if between_section else 0,
        'within_section_count': len(within_section),
        'between_section_count': len(between_section)
    }
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n[OK] Results saved to: {output_path}")
print("=" * 70)
