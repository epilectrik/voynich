"""
CAS-DEEP Validation Tests

Four additional tests to confirm and extend findings:
1. Permutation test - block order invariance
2. Block mutation tolerance - internal variation measurement
3. Upper-bound stability - section-specific ceilings
4. Marker entropy vs repetition - inverse-complexity per marker
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy.stats import spearmanr, entropy
import random

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


def get_marker(block):
    """Extract marker from block."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
    for token in block:
        if len(token) >= 2:
            prefix = token[:2]
            if prefix in marker_prefixes:
                return prefix
    return 'NONE'


def classify_entries(lines):
    """Classify entries with blocks, markers, and sections."""
    entries = []

    for line_id, info in lines.items():
        tokens = info['tokens']
        if len(tokens) >= 4:
            block, count = find_repeating_blocks(tokens)

            if count >= 2:
                marker = get_marker(block)
                entries.append({
                    'line_id': line_id,
                    'folio': info['folio'],
                    'section': info['section'],
                    'tokens': tokens,
                    'block': block,
                    'count': count,
                    'block_size': len(block),
                    'marker': marker
                })

    return entries


def test_1_permutation_invariance(entries, n_permutations=1000):
    """Test 1: Permutation test - block order invariance."""
    print("\n" + "=" * 70)
    print("TEST 1: PERMUTATION INVARIANCE")
    print("=" * 70)
    print("\nQuestion: Does block detection survive random token reordering?")

    original_markers = [e['marker'] for e in entries]
    original_counts = [e['count'] for e in entries]

    # For each entry, permute tokens and see if we still detect blocks
    marker_survival = []
    count_survival = []
    block_detection_rate = []

    random.seed(42)

    for entry in entries:
        tokens = entry['tokens'].copy()
        orig_marker = entry['marker']
        orig_count = entry['count']

        # Run permutation tests
        marker_matches = 0
        count_matches = 0
        blocks_found = 0

        for _ in range(100):  # 100 permutations per entry
            shuffled = tokens.copy()
            random.shuffle(shuffled)

            block, count = find_repeating_blocks(shuffled)
            if count >= 2:
                blocks_found += 1
                marker = get_marker(block)
                if marker == orig_marker:
                    marker_matches += 1
                if count == orig_count:
                    count_matches += 1

        marker_survival.append(marker_matches / 100)
        count_survival.append(count_matches / 100)
        block_detection_rate.append(blocks_found / 100)

    mean_marker_survival = np.mean(marker_survival)
    mean_count_survival = np.mean(count_survival)
    mean_block_detection = np.mean(block_detection_rate)

    print(f"\nResults (100 permutations per entry, {len(entries)} entries):")
    print(f"  Block detection after shuffle: {mean_block_detection:.1%}")
    print(f"  Marker preserved after shuffle: {mean_marker_survival:.1%}")
    print(f"  Count preserved after shuffle: {mean_count_survival:.1%}")

    # Original structure is NOT random
    if mean_block_detection < 0.3:
        verdict = "STRUCTURE_DESTROYED"
        print("\n  -> Shuffling DESTROYS block structure")
        print("  -> Original structure is NON-RANDOM")
    else:
        verdict = "STRUCTURE_ROBUST"
        print("\n  -> Shuffling PRESERVES some structure")

    # Key insight: if shuffling destroys blocks, original order is meaningful
    print(f"\nVerdict: {verdict}")

    return {
        'block_detection_rate': float(mean_block_detection),
        'marker_survival': float(mean_marker_survival),
        'count_survival': float(mean_count_survival),
        'verdict': verdict
    }


def test_2_mutation_tolerance(entries):
    """Test 2: Block mutation tolerance - measure variation across repetitions."""
    print("\n" + "=" * 70)
    print("TEST 2: BLOCK MUTATION TOLERANCE")
    print("=" * 70)
    print("\nQuestion: How much variation exists across repetitions within entries?")

    mutation_rates = []
    position_mutations = defaultdict(list)  # Track which positions vary most

    for entry in entries:
        tokens = entry['tokens']
        block = entry['block']
        count = entry['count']
        block_size = len(block)

        if count < 2:
            continue

        # Compare each repetition to the first block
        total_positions = 0
        total_mutations = 0

        for rep in range(1, count):
            start = rep * block_size
            end = start + block_size
            if end <= len(tokens):
                rep_block = tokens[start:end]
                for pos, (orig, curr) in enumerate(zip(block, rep_block)):
                    total_positions += 1
                    if orig != curr:
                        total_mutations += 1
                        position_mutations[pos].append(1)
                    else:
                        position_mutations[pos].append(0)

        if total_positions > 0:
            mutation_rates.append(total_mutations / total_positions)

    mean_mutation = np.mean(mutation_rates)
    std_mutation = np.std(mutation_rates)

    print(f"\nMutation statistics:")
    print(f"  Mean mutation rate: {mean_mutation:.1%}")
    print(f"  Std mutation rate: {std_mutation:.1%}")
    print(f"  Max mutation rate: {max(mutation_rates):.1%}")
    print(f"  Min mutation rate: {min(mutation_rates):.1%}")

    # Analyze position-specific mutation rates
    print(f"\nMutation rate by position (first 10 positions):")
    for pos in sorted(position_mutations.keys())[:10]:
        pos_rate = np.mean(position_mutations[pos])
        print(f"  Position {pos}: {pos_rate:.1%}")

    # Classify mutation level
    if mean_mutation < 0.05:
        verdict = "NEAR_IDENTICAL"
    elif mean_mutation < 0.15:
        verdict = "LOW_MUTATION"
    elif mean_mutation < 0.25:
        verdict = "MODERATE_MUTATION"
    else:
        verdict = "HIGH_MUTATION"

    print(f"\nVerdict: {verdict}")
    print(f"  -> Blocks show {verdict.lower().replace('_', ' ')} across repetitions")

    return {
        'mean_mutation_rate': float(mean_mutation),
        'std_mutation_rate': float(std_mutation),
        'max_mutation_rate': float(max(mutation_rates)),
        'min_mutation_rate': float(min(mutation_rates)),
        'verdict': verdict
    }


def test_3_upper_bound_stability(entries):
    """Test 3: Upper-bound stability - section-specific ceilings."""
    print("\n" + "=" * 70)
    print("TEST 3: UPPER-BOUND STABILITY")
    print("=" * 70)
    print("\nQuestion: Does max repetition differ by section?")

    section_stats = defaultdict(lambda: {'counts': [], 'max': 0, 'n': 0})

    for entry in entries:
        section = entry['section']
        count = entry['count']
        if section:
            section_stats[section]['counts'].append(count)
            section_stats[section]['max'] = max(section_stats[section]['max'], count)
            section_stats[section]['n'] += 1

    print(f"\nSection-specific statistics:")
    print()

    sections = sorted(section_stats.keys())
    for section in sections:
        stats = section_stats[section]
        counts = stats['counts']
        print(f"  Section {section}:")
        print(f"    n = {len(counts)}")
        print(f"    max = {stats['max']}")
        print(f"    mean = {np.mean(counts):.2f}")
        print(f"    P95 = {np.percentile(counts, 95):.0f}")
        print(f"    P99 = {np.percentile(counts, 99):.0f}")

    # Compare maxes
    maxes = [section_stats[s]['max'] for s in sections]

    print(f"\nMax repetitions by section:")
    for section in sections:
        print(f"  {section}: {section_stats[section]['max']}x")

    # Check if maxes differ
    if len(set(maxes)) == 1:
        verdict = "UNIFORM_CEILING"
        print(f"\n  -> All sections have SAME max ({maxes[0]}x)")
    else:
        verdict = "SECTION_SPECIFIC_CEILINGS"
        print(f"\n  -> Sections have DIFFERENT maxes: {dict(zip(sections, maxes))}")

    print(f"\nVerdict: {verdict}")

    return {
        'section_maxes': {s: section_stats[s]['max'] for s in sections},
        'section_means': {s: float(np.mean(section_stats[s]['counts'])) for s in sections},
        'section_p95': {s: float(np.percentile(section_stats[s]['counts'], 95)) for s in sections},
        'verdict': verdict
    }


def test_4_marker_entropy_vs_repetition(entries):
    """Test 4: Marker entropy vs repetition - confirm inverse-complexity per marker."""
    print("\n" + "=" * 70)
    print("TEST 4: MARKER ENTROPY vs REPETITION")
    print("=" * 70)
    print("\nQuestion: Does inverse-complexity hold within each marker class?")

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    marker_results = {}

    for marker in marker_prefixes:
        marker_entries = [e for e in entries if e['marker'] == marker]

        if len(marker_entries) < 20:
            continue

        # Calculate entropy (diversity) for each block
        counts = []
        entropies = []

        for entry in marker_entries:
            block = entry['block']
            count = entry['count']

            # Calculate token entropy within block
            token_counts = Counter(block)
            probs = np.array(list(token_counts.values())) / len(block)
            block_entropy = entropy(probs)

            counts.append(count)
            entropies.append(block_entropy)

        # Spearman correlation
        if len(counts) >= 10:
            rho, p = spearmanr(counts, entropies)

            marker_results[marker] = {
                'n': len(marker_entries),
                'rho': float(rho),
                'p': float(p),
                'significant': p < 0.05,
                'direction': 'positive' if rho > 0 else 'negative'
            }

    print(f"\nCorrelation (count vs entropy) by marker:")
    print()

    positive_count = 0
    significant_positive = 0

    for marker in sorted(marker_results.keys()):
        r = marker_results[marker]
        sig = "*" if r['significant'] else ""
        print(f"  {marker}: rho={r['rho']:+.3f}, p={r['p']:.4f} {sig} (n={r['n']})")

        if r['rho'] > 0:
            positive_count += 1
            if r['significant']:
                significant_positive += 1

    total_markers = len(marker_results)

    print(f"\nSummary:")
    print(f"  Positive correlations: {positive_count}/{total_markers}")
    print(f"  Significant positive: {significant_positive}/{total_markers}")

    # Check if inverse-complexity is consistent
    if positive_count == total_markers:
        verdict = "INVERSE_COMPLEXITY_UNIVERSAL"
        print(f"\n  -> ALL markers show positive (inverse-complexity) trend")
    elif positive_count >= total_markers * 0.75:
        verdict = "INVERSE_COMPLEXITY_DOMINANT"
        print(f"\n  -> MOST markers show positive trend ({positive_count}/{total_markers})")
    else:
        verdict = "MIXED"
        print(f"\n  -> MIXED trends across markers")

    print(f"\nVerdict: {verdict}")

    return {
        'marker_correlations': marker_results,
        'positive_count': positive_count,
        'significant_positive': significant_positive,
        'total_markers': total_markers,
        'verdict': verdict
    }


def main():
    print("=" * 70)
    print("CAS-DEEP VALIDATION TESTS")
    print("=" * 70)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    entries = classify_entries(lines)
    print(f"Entries with repeating blocks: {len(entries)}")

    # Early return if no blocks (H-only data has 0% block repetition)
    if len(entries) == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        print("Block repetition (64.1%) was an artifact of transcriber interleaving.")

        results = {
            'test_1': {'verdict': 'NO_BLOCKS'},
            'test_2': {'verdict': 'NO_BLOCKS'},
            'test_3': {'verdict': 'NO_BLOCKS'},
            'test_4': {'verdict': 'NO_BLOCKS'},
            'note': 'Block repetition was artifact of transcriber interleaving; 0% with H-only'
        }

        output_path = Path(__file__).parent / 'cas_deep_validation_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")
        return results

    # Run all tests
    results = {}
    results['test_1'] = test_1_permutation_invariance(entries)
    results['test_2'] = test_2_mutation_tolerance(entries)
    results['test_3'] = test_3_upper_bound_stability(entries)
    results['test_4'] = test_4_marker_entropy_vs_repetition(entries)

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION TESTS SUMMARY")
    print("=" * 70)

    print(f"\nTest 1 (Permutation): {results['test_1']['verdict']}")
    print(f"Test 2 (Mutation): {results['test_2']['verdict']}")
    print(f"Test 3 (Upper-bound): {results['test_3']['verdict']}")
    print(f"Test 4 (Marker entropy): {results['test_4']['verdict']}")

    # Save results
    output_path = Path(__file__).parent / 'cas_deep_validation_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
