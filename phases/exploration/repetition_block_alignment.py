#!/usr/bin/env python3
"""
Test: Do repetitions in Currier A align with DA-segmented block boundaries?

Critical question from expert:
> When an entry repeats [BLOCK] x N, does the repetition align with WHOLE blocks?

If confirmed: repetition operates at block level, not entry level.
This would be a refinement of CAS-MULT multiplicity encoding.
"""

import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import statistics

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA prefix detection
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


def is_da_token(token):
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True
    if token.lower().startswith('daiin') or token.lower().startswith('dain'):
        return True
    return result.prefix and result.prefix.startswith('da')


def load_currier_a_entries():
    """Load Currier A entries."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None and current_entry['tokens']:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def segment_by_da(tokens):
    """Segment tokens into blocks using DA as delimiter."""
    blocks = []
    current = []

    for token in tokens:
        if is_da_token(token):
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(token)

    if current:
        blocks.append(current)

    return blocks


def find_repetitions_in_tokens(tokens, min_length=2):
    """Find repeated subsequences in a token list."""
    n = len(tokens)
    repetitions = []

    # Check for consecutive repeated blocks
    for block_size in range(min_length, n // 2 + 1):
        for start in range(n - block_size):
            block = tokens[start:start + block_size]
            # Count how many times this exact block repeats consecutively
            count = 1
            pos = start + block_size
            while pos + block_size <= n:
                if tokens[pos:pos + block_size] == block:
                    count += 1
                    pos += block_size
                else:
                    break

            if count >= 2:
                repetitions.append({
                    'block': block,
                    'start': start,
                    'count': count,
                    'size': block_size
                })

    return repetitions


def block_similarity(block1, block2):
    """Compute Jaccard similarity between two blocks."""
    set1 = set(block1)
    set2 = set(block2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0


def find_similar_blocks(blocks, threshold=0.6):
    """Find blocks that are similar to each other (potential repetitions with variation)."""
    similar_pairs = []

    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            sim = block_similarity(blocks[i], blocks[j])
            if sim >= threshold:
                similar_pairs.append({
                    'block1_idx': i,
                    'block2_idx': j,
                    'similarity': sim,
                    'block1': blocks[i],
                    'block2': blocks[j]
                })

    return similar_pairs


def analyze_entry_repetition(entry):
    """Analyze repetition patterns in a single entry."""
    tokens = entry['tokens']
    blocks = segment_by_da(tokens)

    result = {
        'id': entry['key'],
        'num_tokens': len(tokens),
        'num_blocks': len(blocks),
        'block_sizes': [len(b) for b in blocks],
        'has_token_repetition': False,
        'has_block_similarity': False,
        'repetition_aligns_with_blocks': None,
        'similar_blocks': []
    }

    # Find exact token repetitions
    repetitions = find_repetitions_in_tokens(tokens)
    if repetitions:
        result['has_token_repetition'] = True
        result['repetitions'] = repetitions

        # Check if repetition boundaries align with DA boundaries
        # Find DA positions
        da_positions = set()
        pos = 0
        for block in blocks:
            pos += len(block)
            da_positions.add(pos)  # DA comes after each block

        # Check if any repetition starts/ends at DA boundary
        for rep in repetitions:
            start = rep['start']
            end = start + rep['size'] * rep['count']
            start_aligned = start == 0 or start in da_positions
            end_aligned = end == len(tokens) or end in da_positions
            rep['block_aligned'] = start_aligned and end_aligned

    # Find similar blocks (for variation-based repetition)
    if len(blocks) >= 2:
        similar = find_similar_blocks(blocks, threshold=0.5)
        if similar:
            result['has_block_similarity'] = True
            result['similar_blocks'] = similar

    return result


def main():
    print("=" * 70)
    print("REPETITION-BLOCK ALIGNMENT ANALYSIS")
    print("=" * 70)

    entries = load_currier_a_entries()
    print(f"\nLoaded {len(entries)} Currier A entries")

    # Analyze all entries
    multi_block_entries = []
    results = []

    for entry in entries:
        blocks = segment_by_da(entry['tokens'])
        if len(blocks) >= 2:
            multi_block_entries.append(entry)
            result = analyze_entry_repetition(entry)
            results.append(result)

    print(f"Multi-block entries: {len(multi_block_entries)}")

    # Statistics
    print("\n" + "-" * 60)
    print("BLOCK SIMILARITY ANALYSIS")
    print("-" * 60)

    entries_with_similar = [r for r in results if r['has_block_similarity']]
    print(f"\nEntries with similar block pairs (J >= 0.5): {len(entries_with_similar)} ({100*len(entries_with_similar)/len(results):.1f}%)")

    # Analyze similarity distribution
    all_similarities = []
    for r in results:
        for sim in r['similar_blocks']:
            all_similarities.append(sim['similarity'])

    if all_similarities:
        print(f"Total similar block pairs found: {len(all_similarities)}")
        print(f"Mean similarity: {statistics.mean(all_similarities):.3f}")
        print(f"Median similarity: {statistics.median(all_similarities):.3f}")

    # Check adjacency of similar blocks
    print("\n" + "-" * 60)
    print("ADJACENT vs NON-ADJACENT SIMILAR BLOCKS")
    print("-" * 60)

    adjacent_sim = []
    non_adjacent_sim = []

    for r in results:
        for sim in r['similar_blocks']:
            if sim['block2_idx'] - sim['block1_idx'] == 1:
                adjacent_sim.append(sim['similarity'])
            else:
                non_adjacent_sim.append(sim['similarity'])

    if adjacent_sim:
        print(f"\nAdjacent block pairs: {len(adjacent_sim)}")
        print(f"  Mean similarity: {statistics.mean(adjacent_sim):.3f}")
    if non_adjacent_sim:
        print(f"\nNon-adjacent block pairs: {len(non_adjacent_sim)}")
        print(f"  Mean similarity: {statistics.mean(non_adjacent_sim):.3f}")

    # Block size patterns in entries with similarity
    print("\n" + "-" * 60)
    print("BLOCK SIZE PATTERNS IN SIMILAR-BLOCK ENTRIES")
    print("-" * 60)

    balanced_count = 0
    unbalanced_count = 0

    for r in entries_with_similar:
        sizes = r['block_sizes']
        if len(sizes) >= 2:
            mean_size = statistics.mean(sizes)
            max_dev = max(abs(s - mean_size) / mean_size for s in sizes) if mean_size > 0 else 0
            if max_dev <= 0.3:
                balanced_count += 1
            else:
                unbalanced_count += 1

    print(f"\nIn entries with similar blocks:")
    print(f"  Balanced block sizes (within 30%): {balanced_count} ({100*balanced_count/(balanced_count+unbalanced_count):.1f}%)")
    print(f"  Unbalanced: {unbalanced_count} ({100*unbalanced_count/(balanced_count+unbalanced_count):.1f}%)")

    # Now check for exact block repetition
    print("\n" + "-" * 60)
    print("EXACT BLOCK REPETITION CHECK")
    print("-" * 60)

    exact_repeats = 0
    for entry in multi_block_entries:
        blocks = segment_by_da(entry['tokens'])
        block_strs = [' '.join(b) for b in blocks]
        # Check for any two identical blocks
        if len(block_strs) != len(set(block_strs)):
            exact_repeats += 1

    print(f"\nEntries with exact block repetition: {exact_repeats} ({100*exact_repeats/len(multi_block_entries):.1f}%)")

    # Highly similar blocks (J > 0.8)
    print("\n" + "-" * 60)
    print("HIGH SIMILARITY BLOCK PAIRS (J > 0.8)")
    print("-" * 60)

    high_sim = []
    for r in results:
        for sim in r['similar_blocks']:
            if sim['similarity'] > 0.8:
                high_sim.append({
                    'entry': r['id'],
                    'similarity': sim['similarity'],
                    'block1': sim['block1'],
                    'block2': sim['block2']
                })

    print(f"\nPairs with J > 0.8: {len(high_sim)}")

    if high_sim:
        print("\nTop 10 examples:")
        for i, hs in enumerate(sorted(high_sim, key=lambda x: -x['similarity'])[:10]):
            print(f"\n{i+1}. Entry {hs['entry']} (J={hs['similarity']:.2f})")
            print(f"   Block 1: {' '.join(hs['block1'][:8])}...")
            print(f"   Block 2: {' '.join(hs['block2'][:8])}...")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_with_similarity = len(entries_with_similar)
    pct_similar = 100 * total_with_similarity / len(results)

    print(f"""
Multi-block entries analyzed: {len(results)}

Key findings:
- {pct_similar:.1f}% show block-level similarity (J >= 0.5)
- {100*exact_repeats/len(multi_block_entries):.1f}% have exact block repetition
- {100*balanced_count/(balanced_count+unbalanced_count):.1f}% of similar-block entries have balanced sizes

Interpretation:
""")

    if pct_similar > 30:
        print("STRONG: Block-level repetition/similarity is common in DA-segmented entries.")
        print("Repetition appears to operate at BLOCK level, not token level.")
    elif pct_similar > 15:
        print("MODERATE: Block-level similarity exists but is not dominant.")
        print("Repetition may operate at multiple levels.")
    else:
        print("WEAK: Block-level similarity is rare.")
        print("Repetition (if any) operates at token level, not block level.")


if __name__ == "__main__":
    main()
