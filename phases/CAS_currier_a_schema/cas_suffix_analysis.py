"""
CAS Suffix Analysis

Analyze whether suffixes within marker classes encode a second classification axis.
If suffixes are meaningful, we have PREFIX × SUFFIX = potentially many more categories.
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


def extract_suffix(token, prefix):
    """Extract suffix from a marker token."""
    if token.startswith(prefix):
        remainder = token[len(prefix):]
        return remainder if remainder else None
    return None


def analyze_suffixes():
    """Analyze suffix patterns across marker classes."""
    catalog = load_marker_catalog()

    print("=" * 80)
    print("CAS SUFFIX ANALYSIS")
    print("=" * 80)

    # Collect all suffixes by prefix
    prefix_suffixes = {}
    all_suffixes = Counter()
    suffix_by_prefix = defaultdict(lambda: defaultdict(int))

    for prefix, data in catalog.items():
        suffixes = Counter()
        for token, count in data['all_tokens'].items():
            suffix = extract_suffix(token, prefix)
            if suffix:
                suffixes[suffix] += count
                all_suffixes[suffix] += count
                suffix_by_prefix[suffix][prefix] += count
        prefix_suffixes[prefix] = suffixes

    # Report unique suffixes
    print(f"\n## SUFFIX INVENTORY")
    print(f"Total unique suffixes: {len(all_suffixes)}")
    print(f"\nTop 30 suffixes by frequency:")
    for suffix, count in all_suffixes.most_common(30):
        prefixes_using = [p for p in catalog.keys() if suffix_by_prefix[suffix][p] > 0]
        print(f"  -{suffix:15s} {count:5d}  (used by: {', '.join(prefixes_using)})")

    # Check suffix universality
    print(f"\n## SUFFIX UNIVERSALITY")
    print("Do suffixes appear across multiple prefix classes?")

    universal_suffixes = []  # appear in 6+ prefixes
    common_suffixes = []     # appear in 3-5 prefixes
    rare_suffixes = []       # appear in 1-2 prefixes

    for suffix, count in all_suffixes.most_common():
        prefix_count = sum(1 for p in catalog.keys() if suffix_by_prefix[suffix][p] > 0)
        if prefix_count >= 6:
            universal_suffixes.append((suffix, count, prefix_count))
        elif prefix_count >= 3:
            common_suffixes.append((suffix, count, prefix_count))
        else:
            rare_suffixes.append((suffix, count, prefix_count))

    print(f"\nUniversal suffixes (6+ prefixes): {len(universal_suffixes)}")
    for suffix, count, pc in universal_suffixes[:15]:
        print(f"  -{suffix:15s} {count:5d}  ({pc} prefixes)")

    print(f"\nCommon suffixes (3-5 prefixes): {len(common_suffixes)}")
    for suffix, count, pc in common_suffixes[:15]:
        print(f"  -{suffix:15s} {count:5d}  ({pc} prefixes)")

    print(f"\nRare suffixes (1-2 prefixes): {len(rare_suffixes)}")

    # Analyze suffix structure
    print(f"\n## SUFFIX MORPHOLOGY")

    # Common suffix endings
    suffix_endings = Counter()
    for suffix in all_suffixes:
        if len(suffix) >= 2:
            suffix_endings[suffix[-2:]] += all_suffixes[suffix]
        if len(suffix) >= 3:
            suffix_endings[suffix[-3:]] += all_suffixes[suffix]

    print("\nCommon suffix endings:")
    for ending, count in suffix_endings.most_common(20):
        print(f"  ...{ending:10s} {count:5d}")

    # Check if suffixes form a consistent system
    print(f"\n## SUFFIX CONSISTENCY TEST")
    print("Do the same suffixes have similar frequency ratios across prefixes?")

    # For top 10 universal suffixes, check distribution
    test_suffixes = [s for s, c, p in universal_suffixes[:10]]

    print(f"\nDistribution of top universal suffixes by prefix:")
    print(f"{'Suffix':<12}", end="")
    for prefix in sorted(catalog.keys()):
        print(f"{prefix.upper():>8}", end="")
    print(f"{'TOTAL':>8}")
    print("-" * 80)

    for suffix in test_suffixes:
        print(f"-{suffix:<11}", end="")
        row_total = 0
        for prefix in sorted(catalog.keys()):
            count = suffix_by_prefix[suffix][prefix]
            row_total += count
            print(f"{count:>8}", end="")
        print(f"{row_total:>8}")

    # Calculate potential category count
    print(f"\n## CATEGORY COUNT ESTIMATION")

    # Method 1: Prefix × Suffix combinations actually observed
    observed_combinations = 0
    for prefix in catalog.keys():
        observed_combinations += len(prefix_suffixes[prefix])

    print(f"\nObserved PREFIX × SUFFIX combinations: {observed_combinations}")

    # Method 2: If suffixes are a separate axis
    print(f"If PREFIX (8) × UNIVERSAL_SUFFIX ({len(universal_suffixes)}) = {8 * len(universal_suffixes)} potential")
    print(f"If PREFIX (8) × COMMON_SUFFIX ({len(common_suffixes)}) = {8 * len(common_suffixes)} potential")

    # Check suffix exclusivity within entries
    print(f"\n## SUFFIX CO-OCCURRENCE IN ENTRIES")
    print("Do multiple suffixes appear in the same entry?")

    # Load entry data to check
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    entry_suffix_counts = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        lines = defaultdict(list)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                    if word:
                        key = f"{folio}_{line_num}"
                        lines[key].append(word)

    # For each entry, find all suffixes used
    for line_id, tokens in lines.items():
        suffixes_in_entry = set()
        for token in tokens:
            for prefix in marker_prefixes:
                if token.startswith(prefix):
                    suffix = extract_suffix(token, prefix)
                    if suffix and len(suffix) >= 2:  # Meaningful suffix
                        suffixes_in_entry.add(suffix)
                    break

        if suffixes_in_entry:
            entry_suffix_counts.append(len(suffixes_in_entry))

    if entry_suffix_counts:
        suffix_count_dist = Counter(entry_suffix_counts)

        print(f"\nSuffixes per entry distribution:")
        for count in sorted(suffix_count_dist.keys())[:10]:
            pct = 100 * suffix_count_dist[count] / len(entry_suffix_counts)
            print(f"  {count} suffixes: {suffix_count_dist[count]:5d} entries ({pct:.1f}%)")

        avg_suffixes = sum(entry_suffix_counts) / len(entry_suffix_counts)
        print(f"\nAverage suffixes per entry: {avg_suffixes:.2f}")

    # Semantic grouping attempt
    print(f"\n## SUFFIX SEMANTIC GROUPING (Speculative)")

    # Group by apparent structure
    suffix_groups = {
        'ol_type': [],      # -ol, -eol, -aol
        'or_type': [],      # -or, -eor, -aor
        'y_type': [],       # -y, -ey, -ody, -chy
        'aiin_type': [],    # -aiin, -daiin
        'al_type': [],      # -al, -eal
        'other': []
    }

    for suffix, count in all_suffixes.most_common():
        if suffix.endswith('ol'):
            suffix_groups['ol_type'].append((suffix, count))
        elif suffix.endswith('or'):
            suffix_groups['or_type'].append((suffix, count))
        elif suffix.endswith('aiin'):
            suffix_groups['aiin_type'].append((suffix, count))
        elif suffix.endswith('al'):
            suffix_groups['al_type'].append((suffix, count))
        elif suffix.endswith('y'):
            suffix_groups['y_type'].append((suffix, count))
        else:
            suffix_groups['other'].append((suffix, count))

    print("\nSuffix type groups:")
    for group_name, members in suffix_groups.items():
        total = sum(c for s, c in members)
        print(f"\n  {group_name}: {len(members)} suffixes, {total} occurrences")
        for suffix, count in members[:5]:
            print(f"    -{suffix}: {count}")
        if len(members) > 5:
            print(f"    ... (+{len(members)-5} more)")

    # Final assessment
    print(f"\n" + "=" * 80)
    print("SUFFIX ANALYSIS SUMMARY")
    print("=" * 80)

    print(f"""
FINDINGS:
- {len(all_suffixes)} unique suffixes observed
- {len(universal_suffixes)} suffixes appear across 6+ prefix classes (UNIVERSAL)
- {len(common_suffixes)} suffixes appear across 3-5 prefix classes (COMMON)
- {len(rare_suffixes)} suffixes appear in 1-2 prefix classes only (RARE)

INTERPRETATION:
- Universal suffixes suggest a SECOND CLASSIFICATION AXIS
- If suffixes encode attributes (e.g., state, quality, form), then:
  Category = PREFIX (type) × SUFFIX (attribute)

- Observed combinations: {observed_combinations} distinct marker tokens
- This is much richer than just 8 categories

SPECULATIVE SUFFIX MEANINGS:
- -ol/-eol: possibly "prepared" or "processed" form
- -or/-eor: possibly "raw" or "source" form
- -y/-ey: possibly "small" or "quantity" modifier
- -aiin/-daiin: possibly "dried" or "preserved" state
- -al/-eal: possibly alternate processing state
""")

    return {
        'total_suffixes': len(all_suffixes),
        'universal': len(universal_suffixes),
        'common': len(common_suffixes),
        'rare': len(rare_suffixes),
        'observed_combinations': observed_combinations,
        'suffix_groups': {k: len(v) for k, v in suffix_groups.items()}
    }


if __name__ == '__main__':
    results = analyze_suffixes()
