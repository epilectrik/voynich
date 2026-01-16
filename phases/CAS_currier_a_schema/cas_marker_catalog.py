"""
CAS Marker Token Catalog

Extract and document all category tokens (markers) used in Currier A.
These are the actual tokens that classify entries.
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


def extract_marker_tokens(lines):
    """Extract all marker tokens and their contexts."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Track marker tokens
    marker_tokens = {prefix: Counter() for prefix in marker_prefixes}
    marker_sections = {prefix: defaultdict(Counter) for prefix in marker_prefixes}
    marker_positions = {prefix: Counter() for prefix in marker_prefixes}  # first, middle, last
    marker_contexts = {prefix: [] for prefix in marker_prefixes}  # sample blocks

    entries_by_marker = {prefix: [] for prefix in marker_prefixes}

    for line_id, info in lines.items():
        tokens = info['tokens']
        section = info['section']

        if len(tokens) >= 4:
            block, count = find_repeating_blocks(tokens)

            if count >= 2:
                # Find all marker tokens in block
                for i, token in enumerate(block):
                    if len(token) >= 2:
                        prefix = token[:2]
                        if prefix in marker_prefixes:
                            marker_tokens[prefix][token] += 1
                            marker_sections[prefix][section][token] += 1

                            # Position in block
                            if i == 0:
                                marker_positions[prefix]['first'] += 1
                            elif i == len(block) - 1:
                                marker_positions[prefix]['last'] += 1
                            else:
                                marker_positions[prefix]['middle'] += 1

                            # Store sample context
                            if len(marker_contexts[prefix]) < 20:
                                marker_contexts[prefix].append({
                                    'token': token,
                                    'block': block,
                                    'section': section,
                                    'count': count
                                })

                            entries_by_marker[prefix].append({
                                'line_id': line_id,
                                'token': token,
                                'block': block,
                                'section': section,
                                'count': count,
                                'position': i,
                                'block_size': len(block)
                            })

    return marker_tokens, marker_sections, marker_positions, marker_contexts, entries_by_marker


def analyze_marker_catalog(marker_tokens, marker_sections, marker_positions, entries_by_marker):
    """Analyze and print the marker catalog."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    print("=" * 80)
    print("CURRIER A MARKER TOKEN CATALOG")
    print("=" * 80)

    catalog = {}

    for prefix in marker_prefixes:
        tokens = marker_tokens[prefix]

        if not tokens:
            continue

        print(f"\n{'='*80}")
        print(f"MARKER CLASS: {prefix.upper()}")
        print(f"{'='*80}")

        total_occurrences = sum(tokens.values())
        unique_tokens = len(tokens)

        print(f"\nSummary:")
        print(f"  Total occurrences: {total_occurrences}")
        print(f"  Unique tokens: {unique_tokens}")
        print(f"  Entries using this marker: {len(entries_by_marker[prefix])}")

        # Position distribution
        positions = marker_positions[prefix]
        total_pos = sum(positions.values())
        if total_pos > 0:
            print(f"\nPosition in block:")
            print(f"  First: {positions['first']} ({100*positions['first']/total_pos:.1f}%)")
            print(f"  Middle: {positions['middle']} ({100*positions['middle']/total_pos:.1f}%)")
            print(f"  Last: {positions['last']} ({100*positions['last']/total_pos:.1f}%)")

        # Section distribution
        print(f"\nSection distribution:")
        for section in sorted(marker_sections[prefix].keys()):
            section_total = sum(marker_sections[prefix][section].values())
            print(f"  Section {section}: {section_total} occurrences")

        # Top tokens
        print(f"\nTop 20 tokens:")
        for token, count in tokens.most_common(20):
            pct = 100 * count / total_occurrences
            print(f"  {token:20s} {count:5d} ({pct:5.1f}%)")

        # Full token list
        print(f"\nComplete token list ({unique_tokens} tokens):")
        all_tokens_sorted = sorted(tokens.items(), key=lambda x: (-x[1], x[0]))

        # Group by frequency
        freq_groups = defaultdict(list)
        for token, count in all_tokens_sorted:
            if count >= 10:
                freq_groups['high (10+)'].append((token, count))
            elif count >= 5:
                freq_groups['medium (5-9)'].append((token, count))
            elif count >= 2:
                freq_groups['low (2-4)'].append((token, count))
            else:
                freq_groups['singleton (1)'].append((token, count))

        for group_name in ['high (10+)', 'medium (5-9)', 'low (2-4)', 'singleton (1)']:
            if freq_groups[group_name]:
                print(f"\n  {group_name}: {len(freq_groups[group_name])} tokens")
                tokens_str = ', '.join(f"{t}({c})" for t, c in freq_groups[group_name][:30])
                if len(freq_groups[group_name]) > 30:
                    tokens_str += f" ... (+{len(freq_groups[group_name])-30} more)"
                print(f"    {tokens_str}")

        # Store in catalog
        catalog[prefix] = {
            'total_occurrences': total_occurrences,
            'unique_tokens': unique_tokens,
            'entry_count': len(entries_by_marker[prefix]),
            'positions': dict(positions),
            'sections': {s: sum(marker_sections[prefix][s].values())
                        for s in marker_sections[prefix]},
            'top_tokens': [(t, c) for t, c in tokens.most_common(50)],
            'all_tokens': dict(tokens)
        }

    return catalog


def generate_reference_table(catalog):
    """Generate a reference table of marker tokens."""
    print("\n" + "=" * 80)
    print("MARKER TOKEN REFERENCE TABLE")
    print("=" * 80)

    # Core tokens (appear 10+ times)
    print("\n## CORE MARKER TOKENS (frequency >= 10)")
    print()

    all_core = []
    for prefix, data in catalog.items():
        for token, count in data['top_tokens']:
            if count >= 10:
                all_core.append((prefix, token, count))

    # Sort by prefix then frequency
    all_core.sort(key=lambda x: (x[0], -x[2]))

    current_prefix = None
    for prefix, token, count in all_core:
        if prefix != current_prefix:
            print(f"\n### {prefix.upper()} class:")
            current_prefix = prefix
        print(f"  {token:20s} ({count:4d} occurrences)")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total_tokens = sum(d['unique_tokens'] for d in catalog.values())
    total_occurrences = sum(d['total_occurrences'] for d in catalog.values())

    print(f"\nTotal unique marker tokens: {total_tokens}")
    print(f"Total marker occurrences: {total_occurrences}")

    print(f"\nBy marker class:")
    print(f"{'Prefix':<8} {'Unique':<10} {'Occurrences':<12} {'% of total':<10}")
    print("-" * 40)
    for prefix in sorted(catalog.keys()):
        data = catalog[prefix]
        pct = 100 * data['total_occurrences'] / total_occurrences
        print(f"{prefix:<8} {data['unique_tokens']:<10} {data['total_occurrences']:<12} {pct:.1f}%")

    # Core tokens count
    core_count = len([1 for p, t, c in all_core])
    print(f"\nCore tokens (freq >= 10): {core_count}")

    return all_core


def main():
    print("=" * 80)
    print("CAS MARKER TOKEN CATALOG EXTRACTION")
    print("=" * 80)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    # Extract marker data
    marker_tokens, marker_sections, marker_positions, marker_contexts, entries_by_marker = \
        extract_marker_tokens(lines)

    # Analyze and print catalog
    catalog = analyze_marker_catalog(marker_tokens, marker_sections, marker_positions, entries_by_marker)

    # Generate reference table
    core_tokens = generate_reference_table(catalog)

    # Save catalog
    output_path = Path(__file__).parent / 'marker_token_catalog.json'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\nCatalog saved to: {output_path}")

    # Save core tokens list
    core_path = Path(__file__).parent / 'core_marker_tokens.txt'
    with open(core_path, 'w', encoding='utf-8') as f:
        f.write("# CORE MARKER TOKENS (frequency >= 10)\n")
        f.write("# Format: PREFIX TOKEN COUNT\n\n")
        current_prefix = None
        for prefix, token, count in core_tokens:
            if prefix != current_prefix:
                f.write(f"\n## {prefix.upper()}\n")
                current_prefix = prefix
            f.write(f"{token}\t{count}\n")

    print(f"Core tokens saved to: {core_path}")

    return catalog, core_tokens


if __name__ == '__main__':
    main()
