"""
CAS Non-Block Marker Scan

Scan the remaining 36% of Currier A (entries without repeating blocks)
to check for marker consistency with block-based findings.
"""

from collections import defaultdict, Counter
from pathlib import Path
import json

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


def classify_all_entries(lines):
    """Classify all entries as block or non-block."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    block_entries = []
    nonblock_entries = []

    for line_id, info in lines.items():
        tokens = info['tokens']

        # Check for repeating blocks
        has_block = False
        if len(tokens) >= 4:
            block, count = find_repeating_blocks(tokens)
            if count >= 2:
                has_block = True

        entry = {
            'line_id': line_id,
            'folio': info['folio'],
            'section': info['section'],
            'tokens': tokens,
            'token_count': len(tokens)
        }

        if has_block:
            block_entries.append(entry)
        else:
            nonblock_entries.append(entry)

    return block_entries, nonblock_entries


def extract_markers_from_entries(entries, label):
    """Extract marker tokens from a set of entries."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    marker_tokens = {prefix: Counter() for prefix in marker_prefixes}
    entries_with_markers = 0
    entries_without_markers = 0
    marker_counts_per_entry = []

    for entry in entries:
        tokens = entry['tokens']
        entry_markers = []

        for token in tokens:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in marker_prefixes:
                    marker_tokens[prefix][token] += 1
                    entry_markers.append(token)

        if entry_markers:
            entries_with_markers += 1
            marker_counts_per_entry.append(len(entry_markers))
        else:
            entries_without_markers += 1

    return marker_tokens, entries_with_markers, entries_without_markers, marker_counts_per_entry


def compare_marker_vocabularies(block_markers, nonblock_markers):
    """Compare marker vocabularies between block and non-block entries."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    print("\n" + "=" * 70)
    print("VOCABULARY COMPARISON: BLOCK vs NON-BLOCK")
    print("=" * 70)

    comparison = {}

    for prefix in marker_prefixes:
        block_vocab = set(block_markers[prefix].keys())
        nonblock_vocab = set(nonblock_markers[prefix].keys())

        shared = block_vocab & nonblock_vocab
        block_only = block_vocab - nonblock_vocab
        nonblock_only = nonblock_vocab - block_vocab

        print(f"\n{prefix.upper()} class:")
        print(f"  Block vocabulary: {len(block_vocab)} tokens")
        print(f"  Non-block vocabulary: {len(nonblock_vocab)} tokens")
        print(f"  Shared: {len(shared)} tokens")
        print(f"  Block-only: {len(block_only)} tokens")
        print(f"  Non-block-only: {len(nonblock_only)} tokens")

        if nonblock_only:
            # These are NEW tokens not seen in blocks
            print(f"  NEW tokens in non-block: {list(nonblock_only)[:10]}")
            if len(nonblock_only) > 10:
                print(f"    ... and {len(nonblock_only) - 10} more")

        comparison[prefix] = {
            'block_vocab': len(block_vocab),
            'nonblock_vocab': len(nonblock_vocab),
            'shared': len(shared),
            'block_only': len(block_only),
            'nonblock_only': len(nonblock_only),
            'new_tokens': list(nonblock_only)
        }

    return comparison


def analyze_nonblock_structure(nonblock_entries):
    """Analyze the structure of non-block entries."""
    print("\n" + "=" * 70)
    print("NON-BLOCK ENTRY STRUCTURE ANALYSIS")
    print("=" * 70)

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Length distribution
    lengths = [e['token_count'] for e in nonblock_entries]
    print(f"\nEntry length distribution:")
    print(f"  Min: {min(lengths)}")
    print(f"  Max: {max(lengths)}")
    print(f"  Mean: {sum(lengths)/len(lengths):.1f}")

    length_dist = Counter(lengths)
    print(f"\n  Length distribution:")
    for length in sorted(length_dist.keys())[:15]:
        count = length_dist[length]
        bar = '*' * min(count, 50)
        print(f"    {length:3d}: {count:4d} {bar}")

    # Why didn't they form blocks?
    print(f"\nWhy no blocks detected:")

    too_short = sum(1 for e in nonblock_entries if e['token_count'] < 4)
    print(f"  Too short (<4 tokens): {too_short} ({100*too_short/len(nonblock_entries):.1f}%)")

    # Check for near-blocks (almost repetition)
    near_blocks = 0
    unique_content = 0

    for entry in nonblock_entries:
        tokens = entry['tokens']
        if len(tokens) >= 4:
            # Check if there's any repetition pattern at all
            unique_ratio = len(set(tokens)) / len(tokens)
            if unique_ratio < 0.5:  # More than half are repeats
                near_blocks += 1
            else:
                unique_content += 1

    print(f"  High repetition but no block pattern: {near_blocks}")
    print(f"  Mostly unique content: {unique_content}")

    # Marker presence in non-block entries
    print(f"\nMarker presence:")
    entries_by_marker_count = Counter()

    for entry in nonblock_entries:
        markers_found = set()
        for token in entry['tokens']:
            if len(token) >= 2 and token[:2] in marker_prefixes:
                markers_found.add(token[:2])
        entries_by_marker_count[len(markers_found)] += 1

    print(f"  Entries by number of marker classes present:")
    for count in sorted(entries_by_marker_count.keys()):
        n = entries_by_marker_count[count]
        print(f"    {count} marker classes: {n} entries ({100*n/len(nonblock_entries):.1f}%)")

    return {
        'length_distribution': dict(length_dist),
        'too_short': too_short,
        'near_blocks': near_blocks,
        'unique_content': unique_content
    }


def check_for_inconsistencies(block_markers, nonblock_markers, block_entries, nonblock_entries):
    """Check for any inconsistencies between block and non-block marker usage."""
    print("\n" + "=" * 70)
    print("INCONSISTENCY CHECK")
    print("=" * 70)

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    inconsistencies = []

    # 1. Check for marker co-occurrence violations
    print("\n1. Marker Co-occurrence Check:")
    print("   (In blocks, markers are mutually exclusive per entry)")

    cooccurrence_violations = 0
    for entry in nonblock_entries:
        markers_found = set()
        for token in entry['tokens']:
            if len(token) >= 2 and token[:2] in marker_prefixes:
                markers_found.add(token[:2])
        if len(markers_found) > 1:
            cooccurrence_violations += 1

    print(f"   Non-block entries with multiple marker classes: {cooccurrence_violations}")
    if cooccurrence_violations > 0:
        # Show examples
        examples = []
        for entry in nonblock_entries:
            markers_found = set()
            for token in entry['tokens']:
                if len(token) >= 2 and token[:2] in marker_prefixes:
                    markers_found.add(token[:2])
            if len(markers_found) > 1:
                examples.append((entry['line_id'], markers_found, entry['tokens'][:10]))
                if len(examples) >= 5:
                    break

        print(f"   Examples:")
        for line_id, markers, tokens in examples:
            print(f"     {line_id}: markers={markers}")
            print(f"       tokens: {' '.join(tokens)}...")

        if cooccurrence_violations > 0:
            inconsistencies.append({
                'type': 'MARKER_COOCCURRENCE',
                'description': f'{cooccurrence_violations} entries have multiple marker classes',
                'severity': 'MODERATE' if cooccurrence_violations < 50 else 'HIGH'
            })

    # 2. Check for frequency distribution differences
    print("\n2. Frequency Distribution Check:")

    for prefix in marker_prefixes:
        block_total = sum(block_markers[prefix].values())
        nonblock_total = sum(nonblock_markers[prefix].values())

        if block_total > 0 and nonblock_total > 0:
            # Compare top token dominance
            block_top = block_markers[prefix].most_common(1)[0] if block_markers[prefix] else (None, 0)
            nonblock_top = nonblock_markers[prefix].most_common(1)[0] if nonblock_markers[prefix] else (None, 0)

            block_dominance = block_top[1] / block_total if block_total > 0 else 0
            nonblock_dominance = nonblock_top[1] / nonblock_total if nonblock_total > 0 else 0

            if abs(block_dominance - nonblock_dominance) > 0.2:
                print(f"   {prefix.upper()}: Block top={block_top[0]} ({block_dominance:.1%}), "
                      f"Non-block top={nonblock_top[0]} ({nonblock_dominance:.1%}) - DIFFERENT")
                inconsistencies.append({
                    'type': 'FREQUENCY_SHIFT',
                    'prefix': prefix,
                    'block_top': block_top,
                    'nonblock_top': nonblock_top,
                    'severity': 'LOW'
                })
            else:
                print(f"   {prefix.upper()}: Consistent (block={block_top[0]}, nonblock={nonblock_top[0]})")

    # 3. Check for novel tokens
    print("\n3. Novel Token Check:")
    total_novel = 0
    for prefix in marker_prefixes:
        block_vocab = set(block_markers[prefix].keys())
        nonblock_vocab = set(nonblock_markers[prefix].keys())
        novel = nonblock_vocab - block_vocab
        total_novel += len(novel)

    print(f"   Total novel tokens in non-block entries: {total_novel}")

    if total_novel > 0:
        inconsistencies.append({
            'type': 'NOVEL_TOKENS',
            'count': total_novel,
            'severity': 'LOW' if total_novel < 50 else 'MODERATE'
        })

    # 4. Check for missing expected tokens
    print("\n4. Missing Token Check:")
    print("   (Core tokens that appear in blocks but not in non-blocks)")

    missing_core = []
    for prefix in marker_prefixes:
        for token, count in block_markers[prefix].most_common(10):
            if count >= 20 and token not in nonblock_markers[prefix]:
                missing_core.append((prefix, token, count))

    if missing_core:
        print(f"   Missing core tokens: {len(missing_core)}")
        for prefix, token, count in missing_core[:10]:
            print(f"     {token} ({prefix}): {count} in blocks, 0 in non-blocks")
    else:
        print(f"   No missing core tokens - all appear in both")

    return inconsistencies


def main():
    print("=" * 70)
    print("CAS NON-BLOCK MARKER SCAN")
    print("=" * 70)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    # Classify entries
    block_entries, nonblock_entries = classify_all_entries(lines)
    print(f"\nBlock entries: {len(block_entries)} ({100*len(block_entries)/len(lines):.1f}%)")
    print(f"Non-block entries: {len(nonblock_entries)} ({100*len(nonblock_entries)/len(lines):.1f}%)")

    # Extract markers from both
    print("\n" + "=" * 70)
    print("MARKER EXTRACTION")
    print("=" * 70)

    block_markers, block_with, block_without, block_counts = extract_markers_from_entries(block_entries, "BLOCK")
    print(f"\nBlock entries:")
    if len(block_entries) > 0:
        print(f"  With markers: {block_with} ({100*block_with/len(block_entries):.1f}%)")
        print(f"  Without markers: {block_without} ({100*block_without/len(block_entries):.1f}%)")
        if block_counts:
            print(f"  Avg markers per entry: {sum(block_counts)/len(block_counts):.1f}")
    else:
        print("  No block entries found (0% block repetition with H-only data)")

    nonblock_markers, nonblock_with, nonblock_without, nonblock_counts = extract_markers_from_entries(nonblock_entries, "NON-BLOCK")
    print(f"\nNon-block entries:")
    print(f"  With markers: {nonblock_with} ({100*nonblock_with/len(nonblock_entries):.1f}%)")
    print(f"  Without markers: {nonblock_without} ({100*nonblock_without/len(nonblock_entries):.1f}%)")
    if nonblock_counts:
        print(f"  Avg markers per entry: {sum(nonblock_counts)/len(nonblock_counts):.1f}")

    # Compare vocabularies
    comparison = compare_marker_vocabularies(block_markers, nonblock_markers)

    # Analyze non-block structure
    structure = analyze_nonblock_structure(nonblock_entries)

    # Check for inconsistencies
    inconsistencies = check_for_inconsistencies(block_markers, nonblock_markers, block_entries, nonblock_entries)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_block_tokens = sum(sum(m.values()) for m in block_markers.values())
    total_nonblock_tokens = sum(sum(m.values()) for m in nonblock_markers.values())

    print(f"\nTotal marker tokens:")
    print(f"  Block entries: {total_block_tokens}")
    print(f"  Non-block entries: {total_nonblock_tokens}")

    print(f"\nInconsistencies found: {len(inconsistencies)}")
    for inc in inconsistencies:
        print(f"  - {inc['type']}: {inc.get('description', inc.get('count', ''))} [{inc['severity']}]")

    # Verdict
    if len(inconsistencies) == 0:
        verdict = "FULLY_CONSISTENT"
    elif all(i['severity'] == 'LOW' for i in inconsistencies):
        verdict = "MOSTLY_CONSISTENT"
    elif any(i['severity'] == 'HIGH' for i in inconsistencies):
        verdict = "INCONSISTENT"
    else:
        verdict = "MINOR_DIFFERENCES"

    print(f"\nVerdict: {verdict}")

    # Save results
    output_path = Path(__file__).parent / 'nonblock_marker_scan_results.json'

    results = {
        'block_entries': len(block_entries),
        'nonblock_entries': len(nonblock_entries),
        'block_with_markers': block_with,
        'nonblock_with_markers': nonblock_with,
        'vocabulary_comparison': comparison,
        'structure_analysis': structure,
        'inconsistencies': inconsistencies,
        'verdict': verdict
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
