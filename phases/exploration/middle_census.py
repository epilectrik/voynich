#!/usr/bin/env python
"""
MIDDLE Census: Full inventory of middle components in Currier A.

Priority 2 investigation after DA punctuation (now C422).

Goals:
1. Full MIDDLE inventory (not just "common" ones)
2. PREFIX x MIDDLE incidence matrix
3. Frequency rank and entropy
4. DA-segmented block MIDDLE coherence

Related constraints:
- C267: Tokens are COMPOSITIONAL (PREFIX + MIDDLE + SUFFIX)
- C268: 897 observed combinations
- C269: 7 universal suffixes, 3 universal middles
- C276: MIDDLE is PREFIX-BOUND (V=0.674)
- C278: Three-axis hierarchy
- C346.a: MIDDLE drives 1.23x adjacent similarity
"""
import sys
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import entropy

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_currier_a_tokens():
    """Load all Currier A tokens."""

    tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''

                if language != 'A':
                    continue

                tokens.append(word)

    return tokens


def load_currier_a_entries():
    """Load Currier A entries with line structure."""

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
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


# =============================================================================
# TEST 1: FULL MIDDLE INVENTORY
# =============================================================================

def census_middle_inventory(tokens):
    """Build complete MIDDLE inventory with frequency."""

    print("=" * 70)
    print("TEST 1: FULL MIDDLE INVENTORY")
    print("=" * 70)

    middle_counts = Counter()
    prefix_to_middles = defaultdict(Counter)
    tokens_with_middle = 0
    tokens_without_middle = 0
    total_parsed = 0

    for token in tokens:
        result = parse_currier_a_token(token)

        if result.is_prefix_legal:
            total_parsed += 1

            if result.middle:
                middle_counts[result.middle] += 1
                prefix_to_middles[result.prefix][result.middle] += 1
                tokens_with_middle += 1
            else:
                tokens_without_middle += 1

    print(f"\nTokens parsed: {total_parsed}")
    print(f"With MIDDLE: {tokens_with_middle} ({100*tokens_with_middle/total_parsed:.1f}%)")
    print(f"Without MIDDLE: {tokens_without_middle} ({100*tokens_without_middle/total_parsed:.1f}%)")
    print(f"\nUnique MIDDLEs: {len(middle_counts)}")

    # Top 30 middles
    print(f"\nTop 30 MIDDLEs by frequency:")
    print(f"{'Rank':<6} {'MIDDLE':<15} {'Count':<10} {'%':<8} {'Cum%':<8}")
    print("-" * 47)

    cumulative = 0
    for i, (middle, count) in enumerate(middle_counts.most_common(30), 1):
        pct = 100 * count / tokens_with_middle
        cumulative += pct
        print(f"{i:<6} {middle:<15} {count:<10} {pct:>6.1f}% {cumulative:>6.1f}%")

    # Long tail analysis
    singletons = sum(1 for c in middle_counts.values() if c == 1)
    rare = sum(1 for c in middle_counts.values() if c <= 3)
    print(f"\nLong tail:")
    print(f"  Singletons (count=1): {singletons} ({100*singletons/len(middle_counts):.1f}%)")
    print(f"  Rare (count<=3): {rare} ({100*rare/len(middle_counts):.1f}%)")

    # Entropy calculation
    probs = np.array(list(middle_counts.values())) / sum(middle_counts.values())
    h = entropy(probs, base=2)
    print(f"\nMIDDLE entropy: {h:.2f} bits")
    print(f"Max entropy (uniform): {np.log2(len(middle_counts)):.2f} bits")
    print(f"Efficiency: {100*h/np.log2(len(middle_counts)):.1f}%")

    return middle_counts, prefix_to_middles


# =============================================================================
# TEST 2: PREFIX x MIDDLE MATRIX
# =============================================================================

def analyze_prefix_middle_matrix(prefix_to_middles, middle_counts):
    """Analyze PREFIX x MIDDLE incidence matrix."""

    print("\n" + "=" * 70)
    print("TEST 2: PREFIX x MIDDLE MATRIX")
    print("=" * 70)

    # Which middles are PREFIX-EXCLUSIVE?
    exclusive_middles = []
    shared_middles = []
    prefix_coverage = defaultdict(set)

    for prefix, middles in prefix_to_middles.items():
        for middle in middles:
            prefix_coverage[middle].add(prefix)

    for middle, prefixes in prefix_coverage.items():
        if len(prefixes) == 1:
            exclusive_middles.append((middle, list(prefixes)[0], middle_counts[middle]))
        else:
            shared_middles.append((middle, len(prefixes), middle_counts[middle]))

    print(f"\nPREFIX-EXCLUSIVE middles: {len(exclusive_middles)}")
    print(f"SHARED middles: {len(shared_middles)}")

    # Top exclusive middles by count
    print(f"\nTop 15 PREFIX-EXCLUSIVE middles (high frequency):")
    print(f"{'MIDDLE':<15} {'PREFIX':<10} {'Count':<10}")
    print("-" * 35)
    for middle, prefix, count in sorted(exclusive_middles, key=lambda x: -x[2])[:15]:
        print(f"{middle:<15} {prefix:<10} {count:<10}")

    # Top shared middles by coverage
    print(f"\nTop 15 SHARED middles (by prefix coverage):")
    print(f"{'MIDDLE':<15} {'Prefixes':<10} {'Count':<10}")
    print("-" * 35)
    for middle, n_prefixes, count in sorted(shared_middles, key=lambda x: (-x[1], -x[2]))[:15]:
        prefixes_str = ','.join(sorted(prefix_coverage[middle]))
        print(f"{middle:<15} {n_prefixes:<10} {count:<10} ({prefixes_str})")

    # UNIVERSAL middles (appear in 6+ prefixes)
    universal = [m for m, n, c in shared_middles if n >= 6]
    print(f"\nUNIVERSAL middles (6+ prefixes): {len(universal)}")
    for m in universal:
        print(f"  {m}: appears in {len(prefix_coverage[m])} prefixes")

    # Prefix dominance for exclusive middles
    print(f"\nPREFIX-EXCLUSIVE distribution by prefix:")
    prefix_exclusive_counts = Counter()
    for middle, prefix, count in exclusive_middles:
        prefix_exclusive_counts[prefix] += 1

    for prefix in sorted(MARKER_FAMILIES):
        n = prefix_exclusive_counts.get(prefix, 0)
        print(f"  {prefix}: {n} exclusive middles")

    return exclusive_middles, shared_middles, prefix_coverage


# =============================================================================
# TEST 3: DA-SEGMENTED BLOCK COHERENCE
# =============================================================================

def analyze_da_segment_coherence(entries):
    """Check if DA-segmented blocks are MIDDLE-coherent."""

    print("\n" + "=" * 70)
    print("TEST 3: DA-SEGMENTED BLOCK MIDDLE COHERENCE")
    print("=" * 70)

    def is_da_token(token):
        return token.lower().startswith('da')

    segment_middle_diversity = []
    segment_middle_sets = []

    for entry in entries:
        tokens = entry['tokens']

        # Skip entries without DA
        if not any(is_da_token(t) for t in tokens):
            continue

        # Split on DA
        segments = []
        current = []

        for token in tokens:
            if is_da_token(token):
                if current:
                    segments.append(current)
                current = []
            else:
                current.append(token)

        if current:
            segments.append(current)

        # Analyze each segment
        for seg in segments:
            if len(seg) < 2:
                continue

            seg_middles = set()
            for token in seg:
                result = parse_currier_a_token(token)
                if result.middle:
                    seg_middles.add(result.middle)

            if seg_middles:
                segment_middle_diversity.append(len(seg_middles))
                segment_middle_sets.append(seg_middles)

    print(f"\nDA-segmented blocks analyzed: {len(segment_middle_diversity)}")
    print(f"Mean unique MIDDLEs per block: {np.mean(segment_middle_diversity):.2f}")
    print(f"Median: {np.median(segment_middle_diversity):.0f}")

    # Distribution
    div_dist = Counter(segment_middle_diversity)
    print(f"\nDistribution of unique MIDDLEs per block:")
    for n in sorted(div_dist.keys())[:10]:
        print(f"  {n} unique: {div_dist[n]} blocks ({100*div_dist[n]/len(segment_middle_diversity):.1f}%)")

    # Pure blocks (single MIDDLE)
    pure_blocks = sum(1 for d in segment_middle_diversity if d == 1)
    print(f"\nPure blocks (single MIDDLE): {pure_blocks} ({100*pure_blocks/len(segment_middle_diversity):.1f}%)")

    # Cross-segment MIDDLE similarity
    if len(segment_middle_sets) >= 2:
        same_entry_jaccards = []
        diff_entry_jaccards = []

        # Sample pairs
        import random
        random.seed(42)
        sample_size = min(1000, len(segment_middle_sets))
        sample_indices = random.sample(range(len(segment_middle_sets)), sample_size)

        for i in range(min(500, len(sample_indices)-1)):
            idx1 = sample_indices[i]
            idx2 = sample_indices[i+1]
            s1, s2 = segment_middle_sets[idx1], segment_middle_sets[idx2]
            if s1 and s2:
                j = len(s1 & s2) / len(s1 | s2)
                same_entry_jaccards.append(j)

        # Random non-adjacent pairs
        for i in range(500):
            idx1, idx2 = random.sample(range(len(segment_middle_sets)), 2)
            s1, s2 = segment_middle_sets[idx1], segment_middle_sets[idx2]
            if s1 and s2:
                j = len(s1 & s2) / len(s1 | s2)
                diff_entry_jaccards.append(j)

        print(f"\nCross-segment MIDDLE overlap:")
        print(f"  Adjacent segments: J={np.mean(same_entry_jaccards):.3f}")
        print(f"  Random segments: J={np.mean(diff_entry_jaccards):.3f}")
        if np.mean(diff_entry_jaccards) > 0:
            print(f"  Ratio: {np.mean(same_entry_jaccards)/np.mean(diff_entry_jaccards):.2f}x")


# =============================================================================
# TEST 4: MIDDLE SEMANTICS HINTS
# =============================================================================

def analyze_middle_patterns(prefix_to_middles):
    """Look for structural patterns in MIDDLEs."""

    print("\n" + "=" * 70)
    print("TEST 4: MIDDLE STRUCTURAL PATTERNS")
    print("=" * 70)

    # All middles
    all_middles = set()
    for middles in prefix_to_middles.values():
        all_middles.update(middles.keys())

    # Length distribution
    length_dist = Counter(len(m) for m in all_middles)
    print(f"\nMIDDLE length distribution:")
    for length in sorted(length_dist.keys()):
        print(f"  Length {length}: {length_dist[length]} ({100*length_dist[length]/len(all_middles):.1f}%)")

    # Character frequency in middles
    char_counts = Counter()
    for middle in all_middles:
        for c in middle:
            char_counts[c] += 1

    print(f"\nMost common characters in MIDDLEs:")
    total_chars = sum(char_counts.values())
    for char, count in char_counts.most_common(10):
        print(f"  '{char}': {count} ({100*count/total_chars:.1f}%)")

    # Starting characters
    start_chars = Counter(m[0] for m in all_middles if m)
    print(f"\nStarting characters:")
    for char, count in start_chars.most_common(10):
        print(f"  '{char}': {count} ({100*count/len(all_middles):.1f}%)")

    # Ending characters
    end_chars = Counter(m[-1] for m in all_middles if m)
    print(f"\nEnding characters:")
    for char, count in end_chars.most_common(10):
        print(f"  '{char}': {count} ({100*count/len(all_middles):.1f}%)")

    # Common substrings
    print(f"\nCommon 2-char substrings in MIDDLEs:")
    bigram_counts = Counter()
    for middle in all_middles:
        for i in range(len(middle) - 1):
            bigram_counts[middle[i:i+2]] += 1

    for bigram, count in bigram_counts.most_common(15):
        print(f"  '{bigram}': {count}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("Loading Currier A data...")
    tokens = load_currier_a_tokens()
    entries = load_currier_a_entries()
    print(f"Loaded {len(tokens)} tokens, {len(entries)} entries\n")

    middle_counts, prefix_to_middles = census_middle_inventory(tokens)
    exclusive, shared, coverage = analyze_prefix_middle_matrix(prefix_to_middles, middle_counts)
    analyze_da_segment_coherence(entries)
    analyze_middle_patterns(prefix_to_middles)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
Key findings:
- Total unique MIDDLEs: {len(middle_counts)}
- PREFIX-EXCLUSIVE: {len(exclusive)}
- SHARED across prefixes: {len(shared)}
- Universal (6+ prefixes): {sum(1 for m, n, c in shared if n >= 6)}

The MIDDLE component is the VOCABULARY of Currier A.
PREFIX provides FAMILY classification.
SUFFIX provides FORM variants.
MIDDLE provides TYPE-SPECIFIC content.
""")
