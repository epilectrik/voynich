"""
CAS-DEEP Track 1: Block Internal Structure Analysis

Question: What patterns exist WITHIN the repeating blocks?

Tests:
- T1.1: Token pair frequency within blocks
- T1.2: Block template clustering (do blocks cluster into types?)
- T1.3: First/last token patterns within blocks
- T1.4: Block vocabulary diversity by marker type
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

project_root = Path(__file__).parent.parent.parent


def load_currier_a_lines():
    """Load Currier A data grouped by line (PRIMARY transcriber H only)."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    lines = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                    if word:
                        key = f"{folio}_{line_num}"
                        lines[key]['tokens'].append(word)
                        lines[key]['section'] = section
                        lines[key]['folio'] = folio

    return dict(lines)


def find_repeating_blocks(tokens):
    """Find the repeating block pattern in a sequence of tokens."""
    n = len(tokens)
    if n < 2:
        return tokens, 1

    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            block = tokens[:block_size]
            count = n // block_size

            matches = True
            for i in range(1, count):
                chunk = tokens[i * block_size:(i + 1) * block_size]
                mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                if mismatches > len(block) * 0.2:
                    matches = False
                    break

            if matches and count >= 2:
                return block, count

    for block_size in range(2, n // 2 + 1):
        block = tokens[:block_size]
        count = 1
        i = block_size

        while i + block_size <= n:
            chunk = tokens[i:i + block_size]
            mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
            if mismatches <= len(block) * 0.25:
                count += 1
                i += block_size
            else:
                break

        if count >= 2:
            return block, count

    return tokens, 1


def classify_by_marker(lines):
    """Classify entries by marker and extract blocks."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    entries_with_blocks = []

    for line_id, info in lines.items():
        tokens = info['tokens']
        if len(tokens) >= 4:
            block, count = find_repeating_blocks(tokens)

            if count >= 2:
                # Find marker
                marker = None
                for token in block:
                    if len(token) >= 2:
                        prefix = token[:2]
                        if prefix in marker_prefixes:
                            marker = prefix
                            break

                entries_with_blocks.append({
                    'line_id': line_id,
                    'folio': info['folio'],
                    'section': info['section'],
                    'tokens': tokens,
                    'block': block,
                    'count': count,
                    'block_size': len(block),
                    'marker': marker or 'NONE'
                })

    return entries_with_blocks


def test_1_1_token_pair_frequency(entries):
    """T1.1: Token pair frequency within blocks."""
    print("\n" + "=" * 70)
    print("T1.1: TOKEN PAIR FREQUENCY WITHIN BLOCKS")
    print("=" * 70)

    # Count bigrams within blocks
    bigram_counts = Counter()
    total_bigrams = 0

    for entry in entries:
        block = entry['block']
        for i in range(len(block) - 1):
            bigram = (block[i], block[i + 1])
            bigram_counts[bigram] += 1
            total_bigrams += 1

    print(f"\nTotal bigrams in blocks: {total_bigrams}")
    print(f"Unique bigrams: {len(bigram_counts)}")

    if total_bigrams == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        return {
            'total_bigrams': 0,
            'unique_bigrams': 0,
            'top_10_pct': 0,
            'verdict': 'NO_BLOCKS',
            'top_bigrams': []
        }

    print(f"\nTop 20 most common bigrams:")
    for bigram, count in bigram_counts.most_common(20):
        pct = 100 * count / total_bigrams
        print(f"  {bigram[0]} -> {bigram[1]}: {count} ({pct:.2f}%)")

    # Check for dominant patterns
    top_5_pct = sum(c for _, c in bigram_counts.most_common(5)) / total_bigrams
    top_10_pct = sum(c for _, c in bigram_counts.most_common(10)) / total_bigrams

    print(f"\nConcentration:")
    print(f"  Top 5 bigrams: {top_5_pct:.1%}")
    print(f"  Top 10 bigrams: {top_10_pct:.1%}")

    verdict = "CONCENTRATED" if top_10_pct > 0.2 else "DIFFUSE"
    print(f"\nVerdict: {verdict}")

    return {
        'total_bigrams': total_bigrams,
        'unique_bigrams': len(bigram_counts),
        'top_10_pct': top_10_pct,
        'verdict': verdict,
        'top_bigrams': [(f"{b[0]}→{b[1]}", c) for b, c in bigram_counts.most_common(20)]
    }


def test_1_2_block_template_clustering(entries):
    """T1.2: Block template clustering - do blocks cluster into types?"""
    print("\n" + "=" * 70)
    print("T1.2: BLOCK TEMPLATE CLUSTERING")
    print("=" * 70)

    # Build vocabulary from all blocks
    all_tokens = set()
    for entry in entries:
        all_tokens.update(entry['block'])

    vocab = sorted(all_tokens)
    vocab_idx = {t: i for i, t in enumerate(vocab)}

    print(f"\nBlock vocabulary size: {len(vocab)}")

    # Create feature vectors (bag of words)
    vectors = []
    for entry in entries:
        vec = np.zeros(len(vocab))
        for token in entry['block']:
            if token in vocab_idx:
                vec[vocab_idx[token]] += 1
        vectors.append(vec)

    vectors = np.array(vectors)
    print(f"Feature matrix shape: {vectors.shape}")

    # Only cluster if we have enough entries
    if len(vectors) == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        return {'vocab_size': 0, 'n_entries': 0, 'verdict': 'NO_BLOCKS'}

    if len(vectors) < 10:
        print("Not enough entries for clustering")
        return {'vocab_size': len(vocab), 'n_entries': len(entries), 'verdict': 'INSUFFICIENT_DATA'}

    # Normalize vectors
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    vectors_norm = vectors / norms

    # Hierarchical clustering
    try:
        distances = pdist(vectors_norm, metric='cosine')
        Z = linkage(distances, method='ward')

        # Try different numbers of clusters
        for k in [2, 3, 4, 5]:
            labels = fcluster(Z, k, criterion='maxclust')
            cluster_sizes = Counter(labels)
            print(f"\n  k={k}: {dict(cluster_sizes)}")

        # Use k=3 for analysis
        labels = fcluster(Z, 3, criterion='maxclust')
        cluster_sizes = Counter(labels)

        # Analyze cluster characteristics
        print(f"\nCluster analysis (k=3):")
        for cluster_id in sorted(cluster_sizes.keys()):
            cluster_entries = [e for e, l in zip(entries, labels) if l == cluster_id]
            cluster_markers = Counter(e['marker'] for e in cluster_entries)
            cluster_sizes_dist = Counter(e['block_size'] for e in cluster_entries)

            print(f"\n  Cluster {cluster_id}: {len(cluster_entries)} entries")
            print(f"    Markers: {dict(cluster_markers.most_common(5))}")
            print(f"    Block sizes: {dict(cluster_sizes_dist.most_common(5))}")

            # Sample blocks
            print(f"    Sample blocks:")
            for entry in cluster_entries[:3]:
                print(f"      {' '.join(entry['block'][:8])}...")

        # Check if clusters are meaningful (not just by size)
        size_labels = [e['block_size'] for e in entries]
        from scipy.stats import chi2_contingency

        # Create contingency table: cluster × block_size_category
        size_cats = ['small' if s <= 5 else ('medium' if s <= 8 else 'large') for s in size_labels]
        contingency = defaultdict(lambda: defaultdict(int))
        for label, size_cat in zip(labels, size_cats):
            contingency[label][size_cat] += 1

        # Convert to numpy array
        table = np.array([[contingency[l][s] for s in ['small', 'medium', 'large']]
                         for l in sorted(contingency.keys())])

        if table.min() >= 5:
            chi2, p, dof, expected = chi2_contingency(table)
            print(f"\nCluster × Size independence: Chi²={chi2:.2f}, p={p:.4f}")
            if p < 0.05:
                print("  -> Clusters are NOT just size-based")
            else:
                print("  -> Clusters may be size-driven")

        verdict = "WEAK_CLUSTERING" if len(set(labels)) < 3 else "SOME_CLUSTERING"

    except Exception as e:
        print(f"Clustering failed: {e}")
        verdict = "FAILED"
        labels = None

    return {
        'vocab_size': len(vocab),
        'n_entries': len(entries),
        'verdict': verdict
    }


def test_1_3_first_last_patterns(entries):
    """T1.3: First/last token patterns within blocks."""
    print("\n" + "=" * 70)
    print("T1.3: FIRST/LAST TOKEN PATTERNS WITHIN BLOCKS")
    print("=" * 70)

    if len(entries) == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        return {
            'first_tokens_unique': 0,
            'last_tokens_unique': 0,
            'first_marker_pct': 0,
            'last_marker_pct': 0,
            'verdict': 'NO_BLOCKS'
        }

    first_tokens = Counter()
    last_tokens = Counter()
    first_prefixes = Counter()
    last_prefixes = Counter()

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    for entry in entries:
        block = entry['block']
        if block:
            first_tokens[block[0]] += 1
            last_tokens[block[-1]] += 1

            # Prefixes
            if len(block[0]) >= 2:
                first_prefixes[block[0][:2]] += 1
            if len(block[-1]) >= 2:
                last_prefixes[block[-1][:2]] += 1

    print(f"\nFirst token patterns:")
    print(f"  Unique first tokens: {len(first_tokens)}")
    print(f"  Top 10: {first_tokens.most_common(10)}")

    print(f"\nLast token patterns:")
    print(f"  Unique last tokens: {len(last_tokens)}")
    print(f"  Top 10: {last_tokens.most_common(10)}")

    print(f"\nFirst token prefixes:")
    for prefix, count in first_prefixes.most_common(10):
        is_marker = "MARKER" if prefix in marker_prefixes else ""
        print(f"  {prefix}: {count} {is_marker}")

    print(f"\nLast token prefixes:")
    for prefix, count in last_prefixes.most_common(10):
        is_marker = "MARKER" if prefix in marker_prefixes else ""
        print(f"  {prefix}: {count} {is_marker}")

    # Calculate marker presence
    first_marker_pct = sum(first_prefixes[p] for p in marker_prefixes) / len(entries)
    last_marker_pct = sum(last_prefixes[p] for p in marker_prefixes) / len(entries)

    print(f"\nMarker position analysis:")
    print(f"  First token is marker: {first_marker_pct:.1%}")
    print(f"  Last token is marker: {last_marker_pct:.1%}")

    if first_marker_pct > 0.5:
        position_verdict = "MARKER_FIRST"
    elif last_marker_pct > 0.5:
        position_verdict = "MARKER_LAST"
    else:
        position_verdict = "MARKER_MIXED"

    print(f"\nVerdict: {position_verdict}")

    return {
        'first_tokens_unique': len(first_tokens),
        'last_tokens_unique': len(last_tokens),
        'first_marker_pct': first_marker_pct,
        'last_marker_pct': last_marker_pct,
        'verdict': position_verdict
    }


def test_1_4_vocabulary_diversity(entries):
    """T1.4: Block vocabulary diversity by marker type."""
    print("\n" + "=" * 70)
    print("T1.4: BLOCK VOCABULARY DIVERSITY BY MARKER")
    print("=" * 70)

    if len(entries) == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        return {
            'total_tokens': 0,
            'unique_types': 0,
            'ttr': 0,
            'verdict': 'NO_BLOCKS',
            'marker_vocab_sizes': {}
        }

    marker_vocab = defaultdict(set)
    marker_counts = Counter()

    for entry in entries:
        marker = entry['marker']
        marker_counts[marker] += 1
        for token in entry['block']:
            marker_vocab[marker].add(token)

    print(f"\nVocabulary size by marker:")
    for marker in sorted(marker_vocab.keys()):
        vocab_size = len(marker_vocab[marker])
        count = marker_counts[marker]
        ratio = vocab_size / count if count > 0 else 0
        print(f"  {marker}: {vocab_size} types / {count} entries = {ratio:.2f} types/entry")

    # Overlap analysis
    print(f"\nVocabulary overlap (Jaccard index):")
    markers = sorted([m for m in marker_vocab.keys() if marker_counts[m] >= 10])

    if len(markers) >= 2:
        for i, m1 in enumerate(markers):
            for m2 in markers[i + 1:]:
                v1 = marker_vocab[m1]
                v2 = marker_vocab[m2]
                if v1 and v2:
                    jaccard = len(v1 & v2) / len(v1 | v2)
                    overlap = len(v1 & v2)
                    print(f"  {m1} & {m2}: {jaccard:.3f} ({overlap} shared tokens)")

    # Calculate overall diversity
    all_vocab = set()
    for v in marker_vocab.values():
        all_vocab.update(v)

    total_tokens = sum(len(e['block']) for e in entries)
    ttr = len(all_vocab) / total_tokens if total_tokens > 0 else 0

    print(f"\nOverall block vocabulary:")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Unique types: {len(all_vocab)}")
    print(f"  Type-Token Ratio: {ttr:.4f}")

    verdict = "HIGH_DIVERSITY" if ttr > 0.3 else ("MODERATE_DIVERSITY" if ttr > 0.15 else "LOW_DIVERSITY")
    print(f"\nVerdict: {verdict}")

    return {
        'total_tokens': total_tokens,
        'unique_types': len(all_vocab),
        'ttr': ttr,
        'verdict': verdict,
        'marker_vocab_sizes': {m: len(v) for m, v in marker_vocab.items()}
    }


def main():
    print("=" * 70)
    print("CAS-DEEP TRACK 1: BLOCK INTERNAL STRUCTURE")
    print("=" * 70)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    entries = classify_by_marker(lines)
    print(f"Entries with repeating blocks: {len(entries)}")

    # Run tests
    results = {}
    results['t1_1'] = test_1_1_token_pair_frequency(entries)
    results['t1_2'] = test_1_2_block_template_clustering(entries)
    results['t1_3'] = test_1_3_first_last_patterns(entries)
    results['t1_4'] = test_1_4_vocabulary_diversity(entries)

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 1 SUMMARY")
    print("=" * 70)

    print(f"\nT1.1 Token pairs: {results['t1_1']['verdict']}")
    print(f"T1.2 Clustering: {results['t1_2']['verdict']}")
    print(f"T1.3 First/last: {results['t1_3']['verdict']}")
    print(f"T1.4 Diversity: {results['t1_4']['verdict']}")

    # Save results
    output_path = Path(__file__).parent / 'cas_deep_track1_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
