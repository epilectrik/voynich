#!/usr/bin/env python3
"""
MIDDLE A-B Overlap Analysis

Phase: MIDDLE-AB
Question: What percentage of Currier A's MIDDLEs also appear in Currier B?

This resolves the inconsistency between:
- C423/MODEL_CONTEXT: 1,184 distinct MIDDLEs
- EXT9_REPORT: 725 MIDDLEs (8 A-exclusive)

The answer determines whether MIDDLEs are:
- "Material identities" (many A-exclusive) → A catalogs things B doesn't operate on
- "Operational vocabulary" (mostly shared) → B uses what A defines
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
OUTPUT_PATH = PROJECT_ROOT / 'results' / 'middle_ab_overlap.json'

# Standard PREFIX list (8 marker classes from C235)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Extended prefixes (compound forms that should be recognized)
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',  # C+ch compounds
    'lch', 'lk', 'lsh', 'yk',  # L-compounds (B-specific per C298)
    'ke', 'te', 'se', 'de', 'pe',  # e-compounds
    'so', 'ko', 'to', 'do', 'po',  # o-compounds
    'sa', 'ka', 'ta',  # a-compounds
    'al', 'ar', 'or',  # vowel-initial
]

# All prefixes (try longest first for matching)
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

# Standard suffix list (comprehensive, try longest first)
SUFFIXES = [
    # Complex suffixes (longest first)
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]


def load_data():
    """Load H-only transcript data for both Currier A and B."""
    a_tokens = []
    b_tokens = []

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # H-only filter (CRITICAL)
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip().lower()
                lang = parts[6].strip('"').strip()

                if not word or '*' in word:
                    continue

                if lang == 'A':
                    a_tokens.append(word)
                elif lang == 'B':
                    b_tokens.append(word)

    return a_tokens, b_tokens


def extract_middle(token):
    """
    Extract MIDDLE from token using PREFIX + MIDDLE + SUFFIX decomposition.
    Returns (prefix, middle, suffix) or (None, None, None) if unparseable.
    """
    # Find prefix (try longest first)
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    # Find suffix (try longest first)
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    # Empty middle is valid (token is just PREFIX+SUFFIX)
    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix


def analyze_overlap(a_tokens, b_tokens):
    """Analyze MIDDLE overlap between Currier A and B."""

    # Extract MIDDLEs from each system
    a_middles = Counter()
    b_middles = Counter()
    a_parse_failures = 0
    b_parse_failures = 0
    a_prefix_counts = Counter()
    b_prefix_counts = Counter()

    for token in a_tokens:
        prefix, middle, suffix = extract_middle(token)
        if middle is not None:
            a_middles[middle] += 1
            a_prefix_counts[prefix] += 1
        else:
            a_parse_failures += 1

    for token in b_tokens:
        prefix, middle, suffix = extract_middle(token)
        if middle is not None:
            b_middles[middle] += 1
            b_prefix_counts[prefix] += 1
        else:
            b_parse_failures += 1

    # Calculate overlap
    a_middle_set = set(a_middles.keys())
    b_middle_set = set(b_middles.keys())

    shared = a_middle_set & b_middle_set
    a_only = a_middle_set - b_middle_set
    b_only = b_middle_set - a_middle_set

    # Characterize each set
    def get_top_examples(middle_set, counter, n=15):
        """Get top N examples from a set by frequency."""
        items = [(m, counter[m]) for m in middle_set]
        items.sort(key=lambda x: -x[1])
        return items[:n]

    return {
        'token_counts': {
            'a_total_tokens': len(a_tokens),
            'b_total_tokens': len(b_tokens),
            'a_parsed': len(a_tokens) - a_parse_failures,
            'b_parsed': len(b_tokens) - b_parse_failures,
            'a_parse_rate': (len(a_tokens) - a_parse_failures) / len(a_tokens) if a_tokens else 0,
            'b_parse_rate': (len(b_tokens) - b_parse_failures) / len(b_tokens) if b_tokens else 0,
        },
        'middle_counts': {
            'a_unique_middles': len(a_middle_set),
            'b_unique_middles': len(b_middle_set),
            'shared': len(shared),
            'a_only': len(a_only),
            'b_only': len(b_only),
            'total_union': len(a_middle_set | b_middle_set),
        },
        'percentages': {
            'a_exclusive_pct': 100 * len(a_only) / len(a_middle_set) if a_middle_set else 0,
            'b_exclusive_pct': 100 * len(b_only) / len(b_middle_set) if b_middle_set else 0,
            'shared_of_a_pct': 100 * len(shared) / len(a_middle_set) if a_middle_set else 0,
            'shared_of_b_pct': 100 * len(shared) / len(b_middle_set) if b_middle_set else 0,
            'jaccard': len(shared) / len(a_middle_set | b_middle_set) if (a_middle_set | b_middle_set) else 0,
        },
        'examples': {
            'a_only_top15': get_top_examples(a_only, a_middles),
            'b_only_top15': get_top_examples(b_only, b_middles),
            'shared_top15': get_top_examples(shared, Counter({m: a_middles[m] + b_middles[m] for m in shared})),
        },
        'prefix_distribution': {
            'a': dict(a_prefix_counts.most_common()),
            'b': dict(b_prefix_counts.most_common()),
        },
        'frequency_analysis': {
            'a_hapax': sum(1 for m, c in a_middles.items() if c == 1),
            'b_hapax': sum(1 for m, c in b_middles.items() if c == 1),
            'a_core_10plus': sum(1 for m, c in a_middles.items() if c >= 10),
            'b_core_10plus': sum(1 for m, c in b_middles.items() if c >= 10),
        }
    }


def main():
    print("=" * 70)
    print("MIDDLE A-B OVERLAP ANALYSIS")
    print("=" * 70)
    print()

    # Load data
    print("Loading H-only data...")
    a_tokens, b_tokens = load_data()
    print(f"  Currier A tokens: {len(a_tokens):,}")
    print(f"  Currier B tokens: {len(b_tokens):,}")
    print()

    # Analyze
    print("Analyzing MIDDLE overlap...")
    results = analyze_overlap(a_tokens, b_tokens)

    # Print results
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\n--- Token Parsing ---")
    tc = results['token_counts']
    print(f"  A: {tc['a_parsed']:,}/{tc['a_total_tokens']:,} parsed ({tc['a_parse_rate']:.1%})")
    print(f"  B: {tc['b_parsed']:,}/{tc['b_total_tokens']:,} parsed ({tc['b_parse_rate']:.1%})")

    print(f"\n--- MIDDLE Counts ---")
    mc = results['middle_counts']
    print(f"  Currier A unique MIDDLEs: {mc['a_unique_middles']:,}")
    print(f"  Currier B unique MIDDLEs: {mc['b_unique_middles']:,}")
    print(f"  Shared (A & B):           {mc['shared']:,}")
    print(f"  A-only (A - B):           {mc['a_only']:,}")
    print(f"  B-only (B - A):           {mc['b_only']:,}")
    print(f"  Total union (A | B):      {mc['total_union']:,}")

    print(f"\n--- Percentages ---")
    pct = results['percentages']
    print(f"  A MIDDLEs that are A-exclusive: {pct['a_exclusive_pct']:.1f}%")
    print(f"  A MIDDLEs that appear in B:     {pct['shared_of_a_pct']:.1f}%")
    print(f"  B MIDDLEs that are B-exclusive: {pct['b_exclusive_pct']:.1f}%")
    print(f"  B MIDDLEs that appear in A:     {pct['shared_of_b_pct']:.1f}%")
    print(f"  Jaccard similarity:             {pct['jaccard']:.3f}")

    print(f"\n--- Frequency Analysis ---")
    fa = results['frequency_analysis']
    print(f"  A hapax (freq=1):   {fa['a_hapax']:,} ({100*fa['a_hapax']/mc['a_unique_middles']:.1f}% of A MIDDLEs)")
    print(f"  B hapax (freq=1):   {fa['b_hapax']:,} ({100*fa['b_hapax']/mc['b_unique_middles']:.1f}% of B MIDDLEs)")
    print(f"  A core (freq>=10):  {fa['a_core_10plus']:,}")
    print(f"  B core (freq>=10):  {fa['b_core_10plus']:,}")

    print(f"\n--- Top A-Only MIDDLEs ---")
    for middle, count in results['examples']['a_only_top15'][:10]:
        print(f"  {middle}: {count}")

    print(f"\n--- Top B-Only MIDDLEs ---")
    for middle, count in results['examples']['b_only_top15'][:10]:
        print(f"  {middle}: {count}")

    print(f"\n--- Top Shared MIDDLEs ---")
    for middle, count in results['examples']['shared_top15'][:10]:
        print(f"  {middle}: {count}")

    # Interpretation
    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if pct['shared_of_a_pct'] > 80:
        print("""
FINDING: Most A MIDDLEs (>{:.0f}%) also appear in B.

This supports the "OPERATIONAL VOCABULARY" model:
- MIDDLEs carry configuration that B programs use
- A and B share a common discrimination vocabulary
- MIDDLEs are NOT just "material labels" catalogued only in A
""".format(pct['shared_of_a_pct']))
    elif pct['a_exclusive_pct'] > 30:
        print("""
FINDING: Many A MIDDLEs ({:.0f}%) are A-exclusive.

This supports the "MATERIAL CATALOG" model:
- A catalogues entities that B doesn't directly reference
- Some materials in the registry are never operated on
- A functions more as independent catalog than shared vocabulary
""".format(pct['a_exclusive_pct']))
    else:
        print("""
FINDING: Mixed result - moderate overlap.

Neither pure "operational vocabulary" nor "material catalog" model fits cleanly.
Further analysis needed to understand the relationship.
""")

    # Save results
    print()
    print(f"Saving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("\nDone.")

    return results


if __name__ == '__main__':
    main()
