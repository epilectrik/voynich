"""
CAS-DEEP Track 2: Marker-Block Correlation Analysis

Question: Do different markers have structurally different blocks?

Tests:
- T2.1: Chi-square test for marker x block_size independence
- T2.2: Vocabulary Jaccard distance between marker classes
- T2.3: Token frequency correlation between markers
- T2.4: Marker-exclusive tokens within blocks
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats

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


def test_2_1_marker_blocksize_independence(entries):
    """T2.1: Chi-square test for marker x block_size independence."""
    print("\n" + "=" * 70)
    print("T2.1: MARKER x BLOCK_SIZE INDEPENDENCE")
    print("=" * 70)

    # Create contingency table
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Bin block sizes
    def size_bin(s):
        if s <= 4:
            return 'small'
        elif s <= 7:
            return 'medium'
        else:
            return 'large'

    contingency = defaultdict(lambda: defaultdict(int))
    for entry in entries:
        if entry['marker'] in marker_prefixes:
            marker = entry['marker']
            size_cat = size_bin(entry['block_size'])
            contingency[marker][size_cat] += 1

    # Print contingency table
    print("\nContingency table (marker x block_size):")
    print(f"{'Marker':<8} {'small':>8} {'medium':>8} {'large':>8} {'Total':>8}")
    print("-" * 44)

    markers = sorted(contingency.keys())
    size_cats = ['small', 'medium', 'large']

    for marker in markers:
        row = [contingency[marker][s] for s in size_cats]
        total = sum(row)
        print(f"{marker:<8} {row[0]:>8} {row[1]:>8} {row[2]:>8} {total:>8}")

    # Column totals
    col_totals = [sum(contingency[m][s] for m in markers) for s in size_cats]
    print("-" * 44)
    print(f"{'Total':<8} {col_totals[0]:>8} {col_totals[1]:>8} {col_totals[2]:>8} {sum(col_totals):>8}")

    # Chi-square test
    table = np.array([[contingency[m][s] for s in size_cats] for m in markers])

    # Remove rows/cols with all zeros
    table = table[table.sum(axis=1) > 0]
    table = table[:, table.sum(axis=0) > 0]

    if table.min() < 5:
        print("\nWarning: Some cells have < 5 observations")

    chi2, p, dof, expected = stats.chi2_contingency(table)

    print(f"\nChi-square test:")
    print(f"  Chi2 = {chi2:.2f}")
    print(f"  df = {dof}")
    print(f"  p = {p:.6f}")

    if p < 0.01:
        verdict = "STRONG_DEPENDENCE"
        print("  -> STRONG dependence: markers and block size are NOT independent")
    elif p < 0.05:
        verdict = "MODERATE_DEPENDENCE"
        print("  -> MODERATE dependence")
    else:
        verdict = "INDEPENDENT"
        print("  -> Independent: marker does NOT predict block size")

    # Effect size (Cramer's V)
    n = table.sum()
    min_dim = min(table.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

    print(f"\nEffect size (Cramer's V): {cramers_v:.3f}")
    if cramers_v < 0.1:
        print("  -> Negligible effect")
    elif cramers_v < 0.3:
        print("  -> Small effect")
    elif cramers_v < 0.5:
        print("  -> Medium effect")
    else:
        print("  -> Large effect")

    return {
        'chi2': chi2,
        'p': p,
        'dof': dof,
        'cramers_v': cramers_v,
        'verdict': verdict
    }


def test_2_2_vocabulary_jaccard(entries):
    """T2.2: Vocabulary Jaccard distance between marker classes."""
    print("\n" + "=" * 70)
    print("T2.2: VOCABULARY JACCARD DISTANCE BETWEEN MARKERS")
    print("=" * 70)

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Collect vocabulary per marker
    marker_vocab = defaultdict(set)
    marker_counts = Counter()

    for entry in entries:
        if entry['marker'] in marker_prefixes:
            marker = entry['marker']
            marker_counts[marker] += 1
            for token in entry['block']:
                marker_vocab[marker].add(token)

    # Calculate pairwise Jaccard distances
    print("\nJaccard distance matrix (1 - similarity):")
    markers = sorted([m for m in marker_prefixes if marker_counts[m] >= 20])

    print(f"{'':>6}", end='')
    for m in markers:
        print(f"{m:>6}", end='')
    print()

    distances = {}
    for i, m1 in enumerate(markers):
        print(f"{m1:>6}", end='')
        for j, m2 in enumerate(markers):
            if i == j:
                print(f"{'--':>6}", end='')
            else:
                v1, v2 = marker_vocab[m1], marker_vocab[m2]
                jaccard_sim = len(v1 & v2) / len(v1 | v2) if v1 | v2 else 0
                jaccard_dist = 1 - jaccard_sim
                distances[(m1, m2)] = jaccard_dist
                print(f"{jaccard_dist:>6.2f}", end='')
        print()

    # Summary statistics
    dist_values = list(distances.values())
    mean_dist = np.mean(dist_values)
    min_dist = min(dist_values)
    max_dist = max(dist_values)

    print(f"\nDistance statistics:")
    print(f"  Mean: {mean_dist:.3f}")
    print(f"  Min: {min_dist:.3f}")
    print(f"  Max: {max_dist:.3f}")

    # Find most/least similar pairs
    sorted_pairs = sorted(distances.items(), key=lambda x: x[1])
    print(f"\nMost similar pairs (lowest distance):")
    for (m1, m2), d in sorted_pairs[:5]:
        print(f"  {m1}-{m2}: {d:.3f}")

    print(f"\nMost different pairs (highest distance):")
    for (m1, m2), d in sorted_pairs[-5:]:
        print(f"  {m1}-{m2}: {d:.3f}")

    if mean_dist > 0.8:
        verdict = "HIGHLY_DISTINCT"
    elif mean_dist > 0.6:
        verdict = "MODERATELY_DISTINCT"
    else:
        verdict = "OVERLAPPING"

    print(f"\nVerdict: {verdict}")

    return {
        'mean_distance': mean_dist,
        'min_distance': min_dist,
        'max_distance': max_dist,
        'verdict': verdict
    }


def test_2_3_token_frequency_correlation(entries):
    """T2.3: Token frequency correlation between markers."""
    print("\n" + "=" * 70)
    print("T2.3: TOKEN FREQUENCY CORRELATION BETWEEN MARKERS")
    print("=" * 70)

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Count tokens per marker
    marker_token_counts = defaultdict(Counter)
    marker_counts = Counter()

    for entry in entries:
        if entry['marker'] in marker_prefixes:
            marker = entry['marker']
            marker_counts[marker] += 1
            for token in entry['block']:
                marker_token_counts[marker][token] += 1

    # Build frequency vectors for markers with enough data
    markers = sorted([m for m in marker_prefixes if marker_counts[m] >= 20])

    # Get all tokens across all markers
    all_tokens = set()
    for counts in marker_token_counts.values():
        all_tokens.update(counts.keys())

    all_tokens = sorted(all_tokens)

    # Create frequency vectors
    vectors = {}
    for marker in markers:
        vec = np.array([marker_token_counts[marker].get(t, 0) for t in all_tokens])
        # Normalize
        vec = vec / vec.sum() if vec.sum() > 0 else vec
        vectors[marker] = vec

    # Calculate pairwise correlations
    print("\nSpearman correlation matrix:")
    print(f"{'':>6}", end='')
    for m in markers:
        print(f"{m:>6}", end='')
    print()

    correlations = {}
    for i, m1 in enumerate(markers):
        print(f"{m1:>6}", end='')
        for j, m2 in enumerate(markers):
            if i == j:
                print(f"{'1.00':>6}", end='')
            else:
                rho, p = stats.spearmanr(vectors[m1], vectors[m2])
                correlations[(m1, m2)] = rho
                print(f"{rho:>6.2f}", end='')
        print()

    # Summary
    corr_values = list(correlations.values())
    mean_corr = np.mean(corr_values)

    print(f"\nMean correlation: {mean_corr:.3f}")

    if mean_corr > 0.7:
        verdict = "HIGH_CORRELATION"
        print("  -> Markers use similar token distributions")
    elif mean_corr > 0.4:
        verdict = "MODERATE_CORRELATION"
        print("  -> Markers have moderately similar distributions")
    else:
        verdict = "LOW_CORRELATION"
        print("  -> Markers have distinct token distributions")

    return {
        'mean_correlation': mean_corr,
        'verdict': verdict
    }


def test_2_4_marker_exclusive_tokens(entries):
    """T2.4: Marker-exclusive tokens within blocks."""
    print("\n" + "=" * 70)
    print("T2.4: MARKER-EXCLUSIVE TOKENS")
    print("=" * 70)

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Collect vocabulary per marker
    marker_vocab = defaultdict(set)
    marker_counts = Counter()

    for entry in entries:
        if entry['marker'] in marker_prefixes:
            marker = entry['marker']
            marker_counts[marker] += 1
            for token in entry['block']:
                marker_vocab[marker].add(token)

    markers = sorted([m for m in marker_prefixes if marker_counts[m] >= 20])

    # Find exclusive tokens
    all_tokens = set()
    for v in marker_vocab.values():
        all_tokens.update(v)

    # Token to marker mapping
    token_markers = defaultdict(set)
    for marker in markers:
        for token in marker_vocab[marker]:
            token_markers[token].add(marker)

    # Count exclusive tokens per marker
    exclusive_by_marker = defaultdict(list)
    for token, markers_using in token_markers.items():
        if len(markers_using) == 1:
            marker = list(markers_using)[0]
            exclusive_by_marker[marker].append(token)

    print("\nExclusive tokens by marker:")
    total_exclusive = 0
    for marker in markers:
        exclusive = exclusive_by_marker[marker]
        total = len(marker_vocab[marker])
        pct = 100 * len(exclusive) / total if total > 0 else 0
        total_exclusive += len(exclusive)
        print(f"  {marker}: {len(exclusive)}/{total} ({pct:.1f}%) exclusive")

        if exclusive[:5]:
            print(f"       Examples: {exclusive[:5]}")

    # Overall exclusivity
    total_tokens = len(all_tokens)
    exclusivity_rate = total_exclusive / total_tokens if total_tokens > 0 else 0

    print(f"\nOverall exclusivity:")
    print(f"  Total unique tokens: {total_tokens}")
    print(f"  Marker-exclusive tokens: {total_exclusive} ({100*exclusivity_rate:.1f}%)")

    if exclusivity_rate > 0.5:
        verdict = "HIGH_EXCLUSIVITY"
        print("  -> Most tokens are marker-specific")
    elif exclusivity_rate > 0.3:
        verdict = "MODERATE_EXCLUSIVITY"
        print("  -> Many tokens are marker-specific")
    else:
        verdict = "LOW_EXCLUSIVITY"
        print("  -> Most tokens are shared across markers")

    return {
        'total_tokens': total_tokens,
        'total_exclusive': total_exclusive,
        'exclusivity_rate': exclusivity_rate,
        'verdict': verdict
    }


def main():
    print("=" * 70)
    print("CAS-DEEP TRACK 2: MARKER-BLOCK CORRELATION")
    print("=" * 70)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    entries = classify_by_marker(lines)
    print(f"Entries with repeating blocks: {len(entries)}")

    # Early return if no blocks (H-only data has 0% block repetition)
    if len(entries) == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        print("Block repetition (64.1%) was an artifact of transcriber interleaving.")

        results = {
            't2_1': {'verdict': 'NO_BLOCKS', 'cramers_v': 0},
            't2_2': {'verdict': 'NO_BLOCKS', 'mean_distance': 0},
            't2_3': {'verdict': 'NO_BLOCKS', 'mean_correlation': 0},
            't2_4': {'verdict': 'NO_BLOCKS', 'exclusivity_rate': 0},
            'note': 'Block repetition was artifact of transcriber interleaving; 0% with H-only'
        }

        output_path = Path(__file__).parent / 'cas_deep_track2_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")
        return results

    # Run tests
    results = {}
    results['t2_1'] = test_2_1_marker_blocksize_independence(entries)
    results['t2_2'] = test_2_2_vocabulary_jaccard(entries)
    results['t2_3'] = test_2_3_token_frequency_correlation(entries)
    results['t2_4'] = test_2_4_marker_exclusive_tokens(entries)

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 2 SUMMARY")
    print("=" * 70)

    print(f"\nT2.1 Marker x Size: {results['t2_1']['verdict']} (Cramer's V={results['t2_1']['cramers_v']:.3f})")
    print(f"T2.2 Vocabulary distance: {results['t2_2']['verdict']} (mean={results['t2_2']['mean_distance']:.3f})")
    print(f"T2.3 Frequency correlation: {results['t2_3']['verdict']} (mean={results['t2_3']['mean_correlation']:.3f})")
    print(f"T2.4 Exclusivity: {results['t2_4']['verdict']} (rate={results['t2_4']['exclusivity_rate']:.1%})")

    # Save results
    output_path = Path(__file__).parent / 'cas_deep_track2_results.json'

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
