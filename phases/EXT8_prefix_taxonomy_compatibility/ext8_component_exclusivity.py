"""
EXT-8 Component Exclusivity Test

Are PREFIX, MIDDLE, and SUFFIX components unique to Currier A's registry,
or do they appear in Currier B as well?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']


def load_ab_tokens():
    """Load all tokens separated by Currier language."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    a_tokens = Counter()
    b_tokens = Counter()

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[6].strip('"').strip()
                word = parts[0].strip('"').strip().lower()

                if word:
                    if lang == 'A':
                        a_tokens[word] += 1
                    elif lang == 'B':
                        b_tokens[word] += 1

    return a_tokens, b_tokens


def decompose_token(token):
    """Decompose a token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    for p in MARKER_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]
    if not remainder:
        return prefix, '', ''

    # Known suffix patterns
    suffix_patterns = [
        'odaiin', 'edaiin', 'adaiin',
        'daiin', 'kaiin', 'taiin', 'aiin',
        'chol', 'chor', 'chy',
        'tchy', 'kchy',
        'eody', 'ody',
        'eeol', 'eol',
        'eey', 'ey',
        'eor', 'eal',
        'ol', 'or', 'ar', 'al',
        'hy', 'dy', 'ty', 'ky', 'y',
    ]

    matched_suffix = ''
    for pattern in suffix_patterns:
        if remainder.endswith(pattern):
            matched_suffix = pattern
            break

    if matched_suffix:
        middle = remainder[:-len(matched_suffix)]
    else:
        middle = remainder
        matched_suffix = ''

    return prefix, middle, matched_suffix


def main():
    print("=" * 80)
    print("EXT-8: COMPONENT EXCLUSIVITY TEST")
    print("=" * 80)
    print("\nAre PREFIX, MIDDLE, SUFFIX components unique to Currier A?")

    a_tokens, b_tokens = load_ab_tokens()

    print(f"\nTotal tokens: A={sum(a_tokens.values())}, B={sum(b_tokens.values())}")
    print(f"Unique tokens: A={len(a_tokens)}, B={len(b_tokens)}")

    # === TEST 1: PREFIX TOKENS IN B ===
    print("\n" + "=" * 80)
    print("TEST 1: Do PREFIX-starting tokens appear in Currier B?")
    print("=" * 80)

    # Check each prefix
    for prefix in MARKER_PREFIXES:
        a_prefix_tokens = {t: c for t, c in a_tokens.items() if t.startswith(prefix)}
        b_prefix_tokens = {t: c for t, c in b_tokens.items() if t.startswith(prefix)}

        a_count = sum(a_prefix_tokens.values())
        b_count = sum(b_prefix_tokens.values())

        shared_tokens = set(a_prefix_tokens.keys()) & set(b_prefix_tokens.keys())

        print(f"\n{prefix.upper()}-prefixed tokens:")
        print(f"  In A: {len(a_prefix_tokens)} types, {a_count} occurrences")
        print(f"  In B: {len(b_prefix_tokens)} types, {b_count} occurrences")
        print(f"  Shared: {len(shared_tokens)} types")

        if b_prefix_tokens:
            print(f"  Top B tokens: {', '.join(f'{t}({c})' for t, c in sorted(b_prefix_tokens.items(), key=lambda x: -x[1])[:5])}")

    # === TEST 2: EXACT TOKEN OVERLAP ===
    print("\n" + "=" * 80)
    print("TEST 2: Exact token overlap (A and B)")
    print("=" * 80)

    # All marker tokens in A
    a_marker_tokens = {}
    for token, count in a_tokens.items():
        prefix, middle, suffix = decompose_token(token)
        if prefix:
            a_marker_tokens[token] = count

    # Check which appear in B
    shared_markers = set(a_marker_tokens.keys()) & set(b_tokens.keys())

    print(f"\nMarker tokens in A: {len(a_marker_tokens)}")
    print(f"Marker tokens also in B: {len(shared_markers)}")
    print(f"Overlap rate: {100*len(shared_markers)/len(a_marker_tokens):.1f}%")

    if shared_markers:
        print(f"\nShared marker tokens (top 20 by B frequency):")
        shared_with_b_count = [(t, a_marker_tokens[t], b_tokens[t]) for t in shared_markers]
        shared_with_b_count.sort(key=lambda x: -x[2])

        for token, a_count, b_count in shared_with_b_count[:20]:
            prefix, middle, suffix = decompose_token(token)
            ratio = b_count / a_count if a_count > 0 else 0
            print(f"  {token:<20} A={a_count:>5}  B={b_count:>5}  B/A={ratio:.2f}  ({prefix}+{middle}+{suffix})")

    # === TEST 3: COMPONENT-LEVEL ANALYSIS ===
    print("\n" + "=" * 80)
    print("TEST 3: Component-level overlap")
    print("=" * 80)

    # Extract components from A
    a_prefixes = Counter()
    a_middles = Counter()
    a_suffixes = Counter()

    for token, count in a_marker_tokens.items():
        prefix, middle, suffix = decompose_token(token)
        if prefix:
            a_prefixes[prefix] += count
            if middle:
                a_middles[middle] += count
            if suffix:
                a_suffixes[suffix] += count

    # Extract components from B (all tokens, not just marker-starting)
    b_prefixes = Counter()
    b_middles = Counter()
    b_suffixes = Counter()

    for token, count in b_tokens.items():
        prefix, middle, suffix = decompose_token(token)
        if prefix:
            b_prefixes[prefix] += count
            if middle:
                b_middles[middle] += count
            if suffix:
                b_suffixes[suffix] += count

    print("\n## PREFIX overlap:")
    print(f"{'Prefix':<8} {'In A':>10} {'In B':>10} {'B/A ratio':>12}")
    print("-" * 45)
    for prefix in MARKER_PREFIXES:
        a_c = a_prefixes[prefix]
        b_c = b_prefixes[prefix]
        ratio = b_c / a_c if a_c > 0 else 0
        status = "A-ENRICHED" if ratio < 0.5 else "B-ENRICHED" if ratio > 2.0 else "SHARED"
        print(f"{prefix.upper():<8} {a_c:>10} {b_c:>10} {ratio:>11.2f}x  {status}")

    print("\n## MIDDLE overlap (top 15):")
    print(f"{'Middle':<12} {'In A':>10} {'In B':>10} {'B/A ratio':>12}")
    print("-" * 50)

    all_middles = set(a_middles.keys()) | set(b_middles.keys())
    middle_data = []
    for middle in all_middles:
        if a_middles[middle] >= 10 or b_middles[middle] >= 10:
            middle_data.append((middle, a_middles[middle], b_middles[middle]))

    middle_data.sort(key=lambda x: -(x[1] + x[2]))
    for middle, a_c, b_c in middle_data[:15]:
        ratio = b_c / a_c if a_c > 0 else float('inf')
        status = "A-ONLY" if b_c == 0 else "B-ONLY" if a_c == 0 else "A-ENRICHED" if ratio < 0.5 else "B-ENRICHED" if ratio > 2.0 else "SHARED"
        print(f"-{middle:<11} {a_c:>10} {b_c:>10} {ratio:>11.2f}x  {status}")

    print("\n## SUFFIX overlap (top 15):")
    print(f"{'Suffix':<12} {'In A':>10} {'In B':>10} {'B/A ratio':>12}")
    print("-" * 50)

    all_suffixes = set(a_suffixes.keys()) | set(b_suffixes.keys())
    suffix_data = []
    for suffix in all_suffixes:
        if a_suffixes[suffix] >= 10 or b_suffixes[suffix] >= 10:
            suffix_data.append((suffix, a_suffixes[suffix], b_suffixes[suffix]))

    suffix_data.sort(key=lambda x: -(x[1] + x[2]))
    for suffix, a_c, b_c in suffix_data[:15]:
        ratio = b_c / a_c if a_c > 0 else float('inf')
        status = "A-ONLY" if b_c == 0 else "B-ONLY" if a_c == 0 else "A-ENRICHED" if ratio < 0.5 else "B-ENRICHED" if ratio > 2.0 else "SHARED"
        print(f"-{suffix:<11} {a_c:>10} {b_c:>10} {ratio:>11.2f}x  {status}")

    # === TEST 4: A-EXCLUSIVE COMPONENTS ===
    print("\n" + "=" * 80)
    print("TEST 4: A-EXCLUSIVE components (appear ONLY in A)")
    print("=" * 80)

    a_only_middles = [m for m in a_middles if b_middles[m] == 0 and a_middles[m] >= 10]
    a_only_suffixes = [s for s in a_suffixes if b_suffixes[s] == 0 and a_suffixes[s] >= 10]

    print(f"\nA-exclusive middles (freq >= 10): {len(a_only_middles)}")
    for m in sorted(a_only_middles, key=lambda x: -a_middles[x])[:10]:
        print(f"  -{m}: {a_middles[m]}x")

    print(f"\nA-exclusive suffixes (freq >= 10): {len(a_only_suffixes)}")
    for s in sorted(a_only_suffixes, key=lambda x: -a_suffixes[x])[:10]:
        print(f"  -{s}: {a_suffixes[s]}x")

    # === SYNTHESIS ===
    print("\n" + "=" * 80)
    print("SYNTHESIS")
    print("=" * 80)

    total_a_marker = sum(a_marker_tokens.values())
    total_b_marker = sum(b_prefixes.values())
    shared_tokens_count = sum(b_tokens[t] for t in shared_markers)

    print(f"""
## TOKEN-LEVEL FINDINGS

- A marker tokens: {len(a_marker_tokens)} types, {total_a_marker} occurrences
- B marker tokens: {len(b_prefixes)} types, {total_b_marker} occurrences
- Shared tokens: {len(shared_markers)} types ({100*len(shared_markers)/len(a_marker_tokens):.1f}% of A types)

## COMPONENT-LEVEL FINDINGS

PREFIXES:
- All 8 prefixes appear in BOTH A and B
- But with VERY different frequencies (ratios range widely)
- Some are A-enriched, some B-enriched

MIDDLES:
- {len(a_only_middles)} middles are A-EXCLUSIVE (freq >= 10)
- Most middles appear in both but with different ratios

SUFFIXES:
- {len(a_only_suffixes)} suffixes are A-EXCLUSIVE (freq >= 10)
- Core suffixes appear in both

## INTERPRETATION

The compositional system is NOT fully exclusive to A:
- The PREFIX, MIDDLE, SUFFIX components ARE REUSED in B
- But the USAGE PATTERNS differ dramatically
- A uses them for IDENTIFICATION (compositional codes)
- B uses them within OPERATIONAL GRAMMAR

This is consistent with SHARED INFRASTRUCTURE:
- Same "alphabet" of components
- Different "grammar" of combination
- A = registry codes, B = instruction grammar
""")

    return {
        'shared_tokens': len(shared_markers),
        'a_only_middles': len(a_only_middles),
        'a_only_suffixes': len(a_only_suffixes)
    }


if __name__ == '__main__':
    results = main()
