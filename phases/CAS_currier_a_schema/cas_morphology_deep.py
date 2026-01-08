"""
CAS Deep Morphology Analysis

Analyze the full structure: PREFIX + MIDDLE + SUFFIX
Are there three classification axes?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import re

project_root = Path(__file__).parent.parent.parent


def load_marker_catalog():
    """Load the marker token catalog."""
    catalog_path = Path(__file__).parent / 'marker_token_catalog.json'
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def decompose_token(token, prefix):
    """Decompose a marker token into prefix + middle + suffix."""
    if not token.startswith(prefix):
        return None, None, None

    remainder = token[len(prefix):]
    if not remainder:
        return prefix, '', ''

    # Known suffix patterns (ordered by length, longest first)
    suffix_patterns = [
        'odaiin', 'edaiin', 'adaiin',  # compound -daiin
        'daiin', 'kaiin', 'taiin', 'aiin',  # -aiin family
        'chol', 'chor', 'chy',  # ch- combinations
        'tchy', 'kchy',  # -chy combinations
        'eody', 'ody',  # -ody
        'eey', 'ey',  # -ey
        'eol', 'eor', 'eal',  # -e + ending
        'ol', 'or', 'ar', 'al',  # simple endings
        'hy', 'dy', 'ty', 'ky', 'y',  # -y endings
        'o', 'r', 'l', 'm', 'n', 's'  # single char
    ]

    # Try to match suffix
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


def analyze_morphology():
    """Analyze token morphology deeply."""
    catalog = load_marker_catalog()

    print("=" * 80)
    print("CAS DEEP MORPHOLOGY ANALYSIS")
    print("=" * 80)

    # Collect all decompositions
    decompositions = []
    middle_counter = Counter()
    prefix_middle = defaultdict(Counter)
    middle_suffix = defaultdict(Counter)

    all_tokens = []
    for prefix, data in catalog.items():
        for token, count in data['all_tokens'].items():
            p, m, s = decompose_token(token, prefix)
            if p:
                decompositions.append((token, p, m, s, count))
                if m:
                    middle_counter[m] += count
                    prefix_middle[p][m] += count
                    middle_suffix[m][s] += count
                all_tokens.append((token, count))

    # Report middle components
    print(f"\n## MIDDLE COMPONENT ANALYSIS")
    print(f"Tokens with middle component: {sum(1 for _, p, m, s, c in decompositions if m)}")
    print(f"Unique middle components: {len(middle_counter)}")

    print(f"\nTop 30 middle components:")
    for middle, count in middle_counter.most_common(30):
        # Which prefixes use this middle?
        prefixes = [p for p in catalog.keys() if prefix_middle[p][middle] > 0]
        print(f"  -{middle}-  {count:5d}  (prefixes: {', '.join(prefixes)})")

    # Check if middle is universal or prefix-specific
    print(f"\n## MIDDLE UNIVERSALITY")

    universal_middle = []
    common_middle = []
    rare_middle = []

    for middle, count in middle_counter.most_common():
        prefix_count = sum(1 for p in catalog.keys() if prefix_middle[p][middle] > 0)
        if prefix_count >= 6:
            universal_middle.append((middle, count, prefix_count))
        elif prefix_count >= 3:
            common_middle.append((middle, count, prefix_count))
        else:
            rare_middle.append((middle, count, prefix_count))

    print(f"Universal middle (6+ prefixes): {len(universal_middle)}")
    for m, c, p in universal_middle[:10]:
        print(f"  -{m}-  {c:5d}  ({p} prefixes)")

    print(f"\nCommon middle (3-5 prefixes): {len(common_middle)}")
    for m, c, p in common_middle[:10]:
        print(f"  -{m}-  {c:5d}  ({p} prefixes)")

    print(f"\nRare middle (1-2 prefixes): {len(rare_middle)}")

    # Full decomposition table for top tokens
    print(f"\n## FULL DECOMPOSITION (Top 50 tokens)")
    print(f"{'Token':<20} {'PREFIX':<6} {'MIDDLE':<10} {'SUFFIX':<10} {'Count':>6}")
    print("-" * 60)

    # Sort by count
    sorted_tokens = sorted(decompositions, key=lambda x: -x[4])
    for token, p, m, s, count in sorted_tokens[:50]:
        middle_display = m if m else '—'
        suffix_display = s if s else '—'
        print(f"{token:<20} {p:<6} {middle_display:<10} {suffix_display:<10} {count:>6}")

    # Check three-axis hypothesis
    print(f"\n## THREE-AXIS HYPOTHESIS TEST")

    # If PREFIX × MIDDLE × SUFFIX, what's the space?
    unique_prefixes = len(catalog)
    unique_middles = len([m for m, c in middle_counter.items() if c >= 5])  # freq >= 5
    unique_suffixes_core = 7  # universal suffixes

    print(f"\nCore vocabulary:")
    print(f"  Prefixes: {unique_prefixes}")
    print(f"  Middles (freq>=5): {unique_middles}")
    print(f"  Suffixes (universal): {unique_suffixes_core}")
    print(f"  Theoretical max: {unique_prefixes} × {unique_middles} × {unique_suffixes_core} = {unique_prefixes * unique_middles * unique_suffixes_core}")

    # Actual observed combinations
    observed = len(set((p, m, s) for _, p, m, s, _ in decompositions if m and s))
    print(f"  Actually observed PREFIX×MIDDLE×SUFFIX: {observed}")

    # Check if middle correlates with prefix
    print(f"\n## MIDDLE-PREFIX CORRELATION")
    print("Are certain middles exclusive to certain prefixes?")

    exclusive_to_prefix = defaultdict(list)
    for middle, count in middle_counter.most_common():
        if count >= 5:
            prefixes_using = [p for p in catalog.keys() if prefix_middle[p][middle] > 0]
            if len(prefixes_using) == 1:
                exclusive_to_prefix[prefixes_using[0]].append((middle, count))

    for prefix in sorted(catalog.keys()):
        if exclusive_to_prefix[prefix]:
            print(f"\n  {prefix.upper()}-exclusive middles:")
            for m, c in exclusive_to_prefix[prefix][:5]:
                print(f"    -{m}-  ({c})")

    # Semantic grouping of middles
    print(f"\n## MIDDLE SEMANTIC PATTERNS")

    # Look for patterns in middles
    middle_patterns = {
        'e_initial': [],   # e-, ee-
        'o_initial': [],   # o-, ok-, od-
        'k_type': [],      # k-, ke-, ko-
        't_type': [],      # t-, te-, to-
        'ch_type': [],     # ch-
        'other': []
    }

    for middle, count in middle_counter.most_common():
        if count >= 3:
            if middle.startswith('e'):
                middle_patterns['e_initial'].append((middle, count))
            elif middle.startswith('o'):
                middle_patterns['o_initial'].append((middle, count))
            elif middle.startswith('k'):
                middle_patterns['k_type'].append((middle, count))
            elif middle.startswith('t'):
                middle_patterns['t_type'].append((middle, count))
            elif middle.startswith('ch'):
                middle_patterns['ch_type'].append((middle, count))
            else:
                middle_patterns['other'].append((middle, count))

    for pattern, members in middle_patterns.items():
        if members:
            total = sum(c for m, c in members)
            print(f"\n  {pattern}: {len(members)} middles, {total} occurrences")
            for m, c in members[:5]:
                print(f"    -{m}-  {c}")

    # Final assessment
    print(f"\n" + "=" * 80)
    print("MORPHOLOGY SUMMARY")
    print("=" * 80)

    total_tokens = sum(c for t, c in all_tokens)
    tokens_with_middle = sum(c for _, p, m, s, c in decompositions if m)
    pct_with_middle = 100 * tokens_with_middle / total_tokens

    print(f"""
STRUCTURE: PREFIX + [MIDDLE] + SUFFIX

FINDINGS:
- {len(middle_counter)} unique middle components observed
- {len(universal_middle)} middles appear across 6+ prefixes (UNIVERSAL)
- {len(common_middle)} middles appear across 3-5 prefixes (COMMON)
- {pct_with_middle:.1f}% of token occurrences have a middle component

POTENTIAL CLASSIFICATION AXES:
  1. PREFIX (8): Material TYPE (flower, herb, resin, etc.)
  2. MIDDLE (~{len(universal_middle)+len(common_middle)} common): Processing STATE or SOURCE?
  3. SUFFIX (7 universal): Material FORM or QUALITY?

CATEGORY COUNT:
  - Simple (PREFIX only): ~8
  - Two-axis (PREFIX × SUFFIX): ~56 (8 × 7)
  - Three-axis (observed): {observed}+ distinct combinations

The vocabulary is COMPOSITIONAL, not enumerated.
""")

    return {
        'unique_middles': len(middle_counter),
        'universal_middles': len(universal_middle),
        'common_middles': len(common_middle),
        'pct_with_middle': pct_with_middle,
        'observed_combinations': observed
    }


if __name__ == '__main__':
    results = analyze_morphology()
