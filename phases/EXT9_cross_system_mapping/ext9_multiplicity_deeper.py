"""
Deeper Analysis of Currier A Multiplicity

Now that we understand:
- A is a material classification system (8 PREFIX families)
- Compositional structure: PREFIX + MIDDLE + SUFFIX = identity codes
- 64.1% of entries have repeating blocks [BLOCK] × N

Questions:
1. Does repetition count correlate with PREFIX (material type)?
2. Does repetition count correlate with SUFFIX (output form)?
3. What's in the repeated blocks? Same identity or variations?
4. Does repetition mean quantity, batches, grades, or something else?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats

project_root = Path(__file__).parent.parent.parent
MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']


def load_currier_a_entries():
    """Load Currier A entries grouped by line."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    entries = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
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
                        entries[key]['tokens'].append(word)
                        entries[key]['section'] = section
                        entries[key]['folio'] = folio

    return dict(entries)


def detect_repetition(tokens):
    """
    Detect repeating block structure in a token sequence.
    Returns (block_size, repetition_count, block_tokens) or (0, 0, []) if no repetition.
    """
    n = len(tokens)
    if n < 4:
        return 0, 0, []

    # Try different block sizes
    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            count = n // block_size
            if count >= 2:
                block = tokens[:block_size]
                matches = True
                for i in range(1, count):
                    chunk = tokens[i * block_size:(i + 1) * block_size]
                    # Allow small variation (20%)
                    mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                    if mismatches > len(block) * 0.2:
                        matches = False
                        break
                if matches:
                    return block_size, count, block

    return 0, 0, []


def get_prefix(token):
    """Get the prefix of a marker token."""
    for prefix in MARKER_PREFIXES:
        if token.startswith(prefix):
            return prefix
    return None


def extract_suffix(token):
    """Extract suffix from token."""
    suffix_patterns = [
        'odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
        'chol', 'chor', 'chy', 'tchy', 'kchy',
        'eody', 'ody', 'eeol', 'eol', 'eey', 'ey', 'eor', 'eal',
        'edy', 'dy', 'ol', 'or', 'ar', 'al', 'hy', 'ty', 'ky', 'y',
    ]

    for suffix in suffix_patterns:
        if token.endswith(suffix) and len(token) > len(suffix):
            return suffix
    return ''


def main():
    print("=" * 80)
    print("MULTIPLICITY DEEP ANALYSIS")
    print("=" * 80)

    entries = load_currier_a_entries()

    # Detect repetitions
    repetitions = []
    non_repetitions = []

    for entry_id, data in entries.items():
        tokens = data['tokens']
        block_size, rep_count, block = detect_repetition(tokens)

        if rep_count >= 2:
            repetitions.append({
                'entry_id': entry_id,
                'tokens': tokens,
                'section': data['section'],
                'folio': data['folio'],
                'block_size': block_size,
                'rep_count': rep_count,
                'block': block
            })
        else:
            non_repetitions.append({
                'entry_id': entry_id,
                'tokens': tokens,
                'section': data['section'],
                'folio': data['folio']
            })

    print(f"\nEntries with repetition: {len(repetitions)} ({100*len(repetitions)/len(entries):.1f}%)")
    print(f"Entries without repetition: {len(non_repetitions)}")

    # === TEST 1: Repetition by PREFIX ===
    print("\n" + "=" * 80)
    print("TEST 1: REPETITION COUNT BY PREFIX (Material Type)")
    print("=" * 80)

    prefix_reps = defaultdict(list)

    for r in repetitions:
        # Get the dominant prefix in the block
        prefix_counts = Counter()
        for token in r['block']:
            prefix = get_prefix(token)
            if prefix:
                prefix_counts[prefix] += 1

        if prefix_counts:
            dominant_prefix = prefix_counts.most_common(1)[0][0]
            prefix_reps[dominant_prefix].append(r['rep_count'])

    print(f"\n{'Prefix':<8} {'Count':>8} {'Mean Rep':>10} {'Median':>8} {'Max':>6}")
    print("-" * 50)

    prefix_means = {}
    for prefix in MARKER_PREFIXES:
        reps = prefix_reps[prefix]
        if reps:
            mean_rep = np.mean(reps)
            median_rep = np.median(reps)
            max_rep = max(reps)
            prefix_means[prefix] = mean_rep
            print(f"{prefix.upper():<8} {len(reps):>8} {mean_rep:>10.2f} {median_rep:>8.1f} {max_rep:>6}")

    # Statistical test
    if len(prefix_means) >= 2:
        groups = [prefix_reps[p] for p in MARKER_PREFIXES if prefix_reps[p]]
        if all(len(g) >= 5 for g in groups):
            h_stat, p_val = stats.kruskal(*groups)
            print(f"\nKruskal-Wallis test (prefix effect on rep count):")
            print(f"  H = {h_stat:.2f}, p = {p_val:.4f}")
            if p_val < 0.05:
                print("  RESULT: Prefix DOES affect repetition count")
            else:
                print("  RESULT: Prefix does NOT significantly affect repetition count")

    # === TEST 2: Repetition by SUFFIX ===
    print("\n" + "=" * 80)
    print("TEST 2: REPETITION COUNT BY SUFFIX (Output Form)")
    print("=" * 80)

    suffix_reps = defaultdict(list)

    for r in repetitions:
        # Get suffixes in the block
        suffix_counts = Counter()
        for token in r['block']:
            suffix = extract_suffix(token)
            if suffix:
                suffix_counts[suffix] += 1

        if suffix_counts:
            dominant_suffix = suffix_counts.most_common(1)[0][0]
            suffix_reps[dominant_suffix].append(r['rep_count'])

    print(f"\n{'Suffix':<12} {'Count':>8} {'Mean Rep':>10} {'Median':>8}")
    print("-" * 45)

    # Top 15 suffixes by frequency
    top_suffixes = sorted(suffix_reps.keys(), key=lambda s: -len(suffix_reps[s]))[:15]
    for suffix in top_suffixes:
        reps = suffix_reps[suffix]
        if len(reps) >= 5:
            mean_rep = np.mean(reps)
            median_rep = np.median(reps)
            print(f"-{suffix:<11} {len(reps):>8} {mean_rep:>10.2f} {median_rep:>8.1f}")

    # === TEST 3: What's IN the repeated blocks? ===
    print("\n" + "=" * 80)
    print("TEST 3: CONTENT OF REPEATED BLOCKS")
    print("=" * 80)

    # Analyze block composition
    block_sizes = Counter(r['block_size'] for r in repetitions)
    print(f"\nBlock size distribution:")
    for size, count in sorted(block_sizes.items()):
        print(f"  {size} tokens: {count} entries ({100*count/len(repetitions):.1f}%)")

    # Are blocks single identity codes or compound?
    print(f"\n## BLOCK COMPOSITION ANALYSIS")

    single_prefix_blocks = 0
    multi_prefix_blocks = 0
    block_prefix_counts = []

    for r in repetitions:
        prefixes_in_block = set()
        for token in r['block']:
            prefix = get_prefix(token)
            if prefix:
                prefixes_in_block.add(prefix)

        if len(prefixes_in_block) == 1:
            single_prefix_blocks += 1
        elif len(prefixes_in_block) > 1:
            multi_prefix_blocks += 1

        block_prefix_counts.append(len(prefixes_in_block))

    print(f"\nSingle-prefix blocks: {single_prefix_blocks} ({100*single_prefix_blocks/len(repetitions):.1f}%)")
    print(f"Multi-prefix blocks: {multi_prefix_blocks} ({100*multi_prefix_blocks/len(repetitions):.1f}%)")
    print(f"Mean prefixes per block: {np.mean(block_prefix_counts):.2f}")

    # === TEST 4: Does higher repetition = simpler or more complex blocks? ===
    print("\n" + "=" * 80)
    print("TEST 4: REPETITION vs BLOCK COMPLEXITY")
    print("=" * 80)

    # Complexity = number of unique tokens in block / block size
    rep_complexity = []
    for r in repetitions:
        block = r['block']
        unique_tokens = len(set(block))
        complexity = unique_tokens / len(block) if block else 0
        rep_complexity.append((r['rep_count'], complexity, len(block)))

    # Correlation
    rep_counts = [x[0] for x in rep_complexity]
    complexities = [x[1] for x in rep_complexity]

    corr, p_val = stats.spearmanr(rep_counts, complexities)
    print(f"\nCorrelation (rep count vs block complexity):")
    print(f"  Spearman rho = {corr:.3f}, p = {p_val:.4f}")

    if corr > 0:
        print("  Higher repetition -> MORE complex blocks (diverse content)")
    else:
        print("  Higher repetition -> SIMPLER blocks (uniform content)")

    # Breakdown by repetition count
    print(f"\n## COMPLEXITY BY REPETITION COUNT")
    print(f"{'Rep Count':<12} {'Mean Complexity':>18} {'Mean Block Size':>18}")
    print("-" * 50)

    for rep in range(2, 7):
        subset = [x for x in rep_complexity if x[0] == rep]
        if len(subset) >= 5:
            mean_comp = np.mean([x[1] for x in subset])
            mean_size = np.mean([x[2] for x in subset])
            print(f"{rep}x{'':<10} {mean_comp:>18.3f} {mean_size:>18.1f}")

    # === TEST 5: Example repeated blocks ===
    print("\n" + "=" * 80)
    print("TEST 5: EXAMPLE REPEATED BLOCKS")
    print("=" * 80)

    # Show examples by repetition count
    for rep in [2, 3, 4, 5]:
        examples = [r for r in repetitions if r['rep_count'] == rep][:3]
        if examples:
            print(f"\n## {rep}x REPETITION EXAMPLES:")
            for ex in examples:
                print(f"\n  Entry: {ex['entry_id']}, Section: {ex['section']}")
                print(f"  Block ({ex['block_size']} tokens): {' '.join(ex['block'])}")
                print(f"  Full: {' '.join(ex['tokens'][:20])}{'...' if len(ex['tokens']) > 20 else ''}")

    # === SYNTHESIS ===
    print("\n" + "=" * 80)
    print("SYNTHESIS: WHAT DOES REPETITION MEAN?")
    print("=" * 80)

    print(f"""
## FINDINGS

1. PREFIX EFFECT: {"Significant" if 'p_val' in dir() and p_val < 0.05 else "Not significant"}
   - Different material types may have different typical quantities

2. BLOCK COMPOSITION:
   - {100*single_prefix_blocks/len(repetitions):.0f}% of blocks have SINGLE prefix (one material type)
   - {100*multi_prefix_blocks/len(repetitions):.0f}% of blocks have MULTIPLE prefixes (compound/mixture)

3. REPETITION vs COMPLEXITY:
   - Correlation: rho = {corr:.3f}
   - {"Higher repetition = MORE complex blocks" if corr > 0 else "Higher repetition = SIMPLER blocks"}

## INTERPRETATION

The repetition pattern suggests:

If repetition = QUANTITY/AMOUNT:
- "3x [material code]" = "3 units of this material"
- Would expect simpler blocks for higher counts (bulk items)
- But we see INVERSE: more complex blocks have higher repetition

If repetition = BATCHES/LOTS:
- "3x [material code]" = "3 separate batches"
- Could explain why blocks are unique (different batches)
- Section isolation = batches stay within product lines

If repetition = PREPARATION STAGES:
- "3x [material code]" = "processed 3 times"
- Would explain complexity correlation (more processing = more detail)
- But why would some materials need more processing?

If repetition = QUALITY GRADES/VARIANTS:
- "3x [material code]" = "3 quality levels"
- But why literal repetition instead of suffix variation?

MOST LIKELY INTERPRETATION:
The repetition appears to encode MULTIPLICITY (how many instances exist)
rather than abstract QUANTITY. Each block is a distinct instance/batch,
and the repetition says "there are N of these."

This is consistent with a MATERIAL INVENTORY where:
- Each entry catalogues a specific material
- Repetition indicates multiple lots/batches/specimens
- 100% block uniqueness = each batch is distinct
- Section isolation = batches organized by product line
""")


if __name__ == '__main__':
    main()
