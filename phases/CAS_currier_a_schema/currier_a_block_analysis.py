"""
Currier A Block Repetition Analysis

Key finding: Entries appear to be REPEATING BLOCKS.
Question: What are the repetition counts? Is this a counting/tally system?
"""

from collections import defaultdict, Counter
from pathlib import Path
import re

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
    """Find the repeating block pattern in a sequence of tokens.

    Returns (block, count) if found, or (tokens, 1) if no repetition.
    """
    n = len(tokens)
    if n < 2:
        return tokens, 1

    # Try different block sizes
    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            # Check if this block size works
            block = tokens[:block_size]
            count = n // block_size

            # Verify all repetitions match (allowing for slight variations)
            matches = True
            for i in range(1, count):
                chunk = tokens[i * block_size:(i + 1) * block_size]
                # Allow up to 20% mismatch for scribal variation
                mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                if mismatches > len(block) * 0.2:
                    matches = False
                    break

            if matches and count >= 2:
                return block, count

    # Try with non-exact divisions (find longest repeating subsequence)
    for block_size in range(2, n // 2 + 1):
        block = tokens[:block_size]
        count = 1
        i = block_size

        while i + block_size <= n:
            chunk = tokens[i:i + block_size]
            mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
            if mismatches <= len(block) * 0.25:  # 25% tolerance
                count += 1
                i += block_size
            else:
                break

        if count >= 2:
            return block, count

    return tokens, 1


def analyze_block_patterns(lines):
    """Analyze repeating block patterns in all entries."""
    print("\n" + "=" * 70)
    print("BLOCK REPETITION ANALYSIS")
    print("=" * 70)

    block_counts = Counter()  # How many times blocks repeat
    block_sizes = Counter()   # Size of repeating blocks

    entries_with_blocks = []

    for line_id, info in lines.items():
        tokens = info['tokens']
        if len(tokens) >= 4:  # Need at least 4 tokens to have 2x repetition
            block, count = find_repeating_blocks(tokens)

            if count >= 2:
                block_counts[count] += 1
                block_sizes[len(block)] += 1
                entries_with_blocks.append({
                    'line_id': line_id,
                    'folio': info['folio'],
                    'tokens': tokens,
                    'block': block,
                    'count': count,
                    'block_size': len(block)
                })

    print(f"\nTotal entries analyzed: {len(lines)}")
    print(f"Entries with repeating blocks: {len(entries_with_blocks)} ({100*len(entries_with_blocks)/len(lines):.1f}%)")

    print(f"\nRepetition counts (how many times block repeats):")
    for count, freq in sorted(block_counts.items()):
        print(f"  {count}x: {freq} entries")

    print(f"\nBlock sizes (tokens per repeating unit):")
    for size, freq in sorted(block_sizes.items()):
        print(f"  {size} tokens: {freq} entries")

    return entries_with_blocks, block_counts, block_sizes


def show_block_examples(entries_with_blocks):
    """Show examples of repeating blocks."""
    print("\n" + "=" * 70)
    print("REPEATING BLOCK EXAMPLES")
    print("=" * 70)

    # Group by repetition count
    by_count = defaultdict(list)
    for entry in entries_with_blocks:
        by_count[entry['count']].append(entry)

    for count in sorted(by_count.keys(), reverse=True):
        print(f"\n--- {count}x REPETITIONS ---")
        for entry in by_count[count][:5]:
            block_str = ' '.join(entry['block'])
            print(f"  [{entry['folio']}] Block: [{block_str}] × {count}")


def analyze_count_distribution(entries_with_blocks):
    """Analyze if the counts follow any meaningful pattern."""
    print("\n" + "=" * 70)
    print("COUNT DISTRIBUTION ANALYSIS")
    print("=" * 70)

    counts = [e['count'] for e in entries_with_blocks]

    if not counts:
        print("No repeating blocks found.")
        return

    print(f"\nCount statistics:")
    print(f"  Min: {min(counts)}")
    print(f"  Max: {max(counts)}")
    print(f"  Mean: {sum(counts)/len(counts):.2f}")

    # Check if counts cluster around certain values
    count_dist = Counter(counts)
    print(f"\nCount frequency distribution:")
    for c in range(2, max(counts) + 1):
        freq = count_dist.get(c, 0)
        bar = '*' * freq
        print(f"  {c}x: {bar} ({freq})")

    # Check for special numbers (2, 3, 4, 5, 7, etc.)
    print(f"\nSpecial count analysis:")
    print(f"  2x (pairs): {count_dist.get(2, 0)}")
    print(f"  3x (triads): {count_dist.get(3, 0)}")
    print(f"  4x (quads): {count_dist.get(4, 0)}")
    print(f"  5x (quintets): {count_dist.get(5, 0)}")
    print(f"  6x: {count_dist.get(6, 0)}")
    print(f"  7x: {count_dist.get(7, 0)}")


def examine_block_content(entries_with_blocks):
    """Examine what the blocks contain - are they like labels/identifiers?"""
    print("\n" + "=" * 70)
    print("BLOCK CONTENT ANALYSIS")
    print("=" * 70)

    # Collect unique blocks
    unique_blocks = {}
    for entry in entries_with_blocks:
        block_key = ' '.join(entry['block'])
        if block_key not in unique_blocks:
            unique_blocks[block_key] = {
                'block': entry['block'],
                'count': entry['count'],
                'folio': entry['folio'],
                'entries': []
            }
        unique_blocks[block_key]['entries'].append(entry['folio'])

    print(f"\nUnique blocks: {len(unique_blocks)}")

    # Check if same block appears in multiple entries
    reused_blocks = {k: v for k, v in unique_blocks.items() if len(v['entries']) > 1}
    print(f"Blocks appearing in multiple entries: {len(reused_blocks)}")

    if reused_blocks:
        print("\nReused blocks:")
        for block_key, info in list(reused_blocks.items())[:10]:
            print(f"  [{block_key}] appears in: {info['entries']}")

    # Analyze block structure - what types of tokens are in blocks?
    print(f"\nBlock structure patterns:")

    # Count how many blocks start with marker prefixes
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
    starts_with_marker = 0
    contains_marker = 0
    contains_daiin = 0

    for block_key, info in unique_blocks.items():
        block = info['block']
        first_token = block[0] if block else ''

        if len(first_token) >= 2 and first_token[:2] in marker_prefixes:
            starts_with_marker += 1

        for token in block:
            if len(token) >= 2 and token[:2] in marker_prefixes:
                contains_marker += 1
                break

        if 'daiin' in block:
            contains_daiin += 1

    if len(unique_blocks) > 0:
        print(f"  Blocks starting with marker: {starts_with_marker} ({100*starts_with_marker/len(unique_blocks):.1f}%)")
        print(f"  Blocks containing any marker: {contains_marker} ({100*contains_marker/len(unique_blocks):.1f}%)")
        print(f"  Blocks containing 'daiin': {contains_daiin} ({100*contains_daiin/len(unique_blocks):.1f}%)")
    else:
        print("  No blocks to analyze.")


def main():
    print("=" * 70)
    print("CURRIER A BLOCK REPETITION ANALYSIS")
    print("=" * 70)
    print("\nHypothesis: Entries are REPEATING BLOCKS (possible counting/tally system)")

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    entries_with_blocks, block_counts, block_sizes = analyze_block_patterns(lines)
    show_block_examples(entries_with_blocks)
    analyze_count_distribution(entries_with_blocks)
    examine_block_content(entries_with_blocks)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if entries_with_blocks:
        pct = 100 * len(entries_with_blocks) / len(lines)
        avg_count = sum(e['count'] for e in entries_with_blocks) / len(entries_with_blocks)

        print(f"""
FINDING: {pct:.1f}% of Currier A entries show REPEATING BLOCK structure.

Average repetition: {avg_count:.1f}x
Most common repetition: {block_counts.most_common(1)[0][0]}x

INTERPRETATION OPTIONS:
1. TALLY SYSTEM: Each block = one instance of something being counted
2. RECIPE MULTIPLIER: "Do this N times" instructions
3. BATCH RECORDS: Multiple instances of same operation
4. INVENTORY COUNTS: Quantities of materials/products

The structure [BLOCK × N] suggests a COUNTING or RECORDING function,
not natural language or continuous prose.
        """)


if __name__ == '__main__':
    main()
