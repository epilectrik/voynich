#!/usr/bin/env python3
"""
Quick analysis: Where do HT tokens appear relative to DA-segmented record structure?

Question: Are HT tokens INSIDE or OUTSIDE the DA-delimited content blocks?
"""

import sys
from collections import Counter

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA family
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}

# HT prefixes (from C347 - disjoint from A/B)
HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'ta', 'do'}


def get_token_type(token):
    """Classify token as DA, HT, VALID_A, or OTHER."""
    token_lower = token.lower()
    result = parse_currier_a_token(token)

    # Check DA first
    if result.prefix in DA_PREFIXES:
        return 'DA'
    if token_lower.startswith('daiin') or token_lower.startswith('dain'):
        return 'DA'
    if result.prefix and result.prefix.startswith('da'):
        return 'DA'

    # Check HT prefixes (STRICT - only confirmed HT prefixes from C347)
    # Must match at word start with the exact HT prefix pattern
    for ht_pf in HT_PREFIXES:
        if token_lower.startswith(ht_pf):
            # Verify it's not a valid A prefix that happens to start with these letters
            if not result.is_prefix_legal:
                return 'HT'
            # If it has a valid A prefix, it's A not HT
            break

    # Check valid A (has valid C240 prefix)
    if result.is_prefix_legal:
        return 'VALID_A'

    # Everything else that fails A classification could be HT
    # But we'll be conservative and only count confirmed HT prefixes
    return 'OTHER'


def load_currier_a_entries():
    """Load Currier A entries as token sequences."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
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
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def analyze_ht_position_in_records(entries):
    """Analyze where HT tokens appear relative to DA-segmented blocks."""

    results = {
        'total_entries': 0,
        'entries_with_ht': 0,
        'total_tokens': 0,
        'total_ht': 0,
        'total_da': 0,
        'ht_positions': Counter(),  # 'BEFORE_FIRST_DA', 'BETWEEN_DA', 'AFTER_LAST_DA', 'NO_DA_IN_ENTRY'
        'ht_at_entry_boundary': 0,  # line-initial or line-final
        'ht_adjacent_to_da': 0,
        'ht_examples': []
    }

    for entry in entries:
        tokens = entry['tokens']
        results['total_entries'] += 1
        results['total_tokens'] += len(tokens)

        # Classify all tokens
        types = [get_token_type(t) for t in tokens]

        # Find DA positions
        da_positions = [i for i, t in enumerate(types) if t == 'DA']
        ht_positions = [i for i, t in enumerate(types) if t in ('HT', 'HT_CANDIDATE')]

        results['total_da'] += len(da_positions)
        results['total_ht'] += len(ht_positions)

        if ht_positions:
            results['entries_with_ht'] += 1

        # Analyze HT positions relative to DA structure
        for ht_pos in ht_positions:
            # Check entry boundaries
            if ht_pos == 0 or ht_pos == len(tokens) - 1:
                results['ht_at_entry_boundary'] += 1

            # Check adjacency to DA
            for da_pos in da_positions:
                if abs(ht_pos - da_pos) == 1:
                    results['ht_adjacent_to_da'] += 1
                    break

            # Determine position relative to DA blocks
            if not da_positions:
                results['ht_positions']['NO_DA_IN_ENTRY'] += 1
            elif ht_pos < min(da_positions):
                results['ht_positions']['BEFORE_FIRST_DA'] += 1
            elif ht_pos > max(da_positions):
                results['ht_positions']['AFTER_LAST_DA'] += 1
            else:
                results['ht_positions']['BETWEEN_DA'] += 1

            # Collect examples
            if len(results['ht_examples']) < 20:
                context_start = max(0, ht_pos - 2)
                context_end = min(len(tokens), ht_pos + 3)
                context = tokens[context_start:context_end]
                results['ht_examples'].append({
                    'entry': entry['key'],
                    'ht_token': tokens[ht_pos],
                    'position': ht_pos,
                    'entry_length': len(tokens),
                    'context': context,
                    'da_positions': da_positions
                })

    return results


def main():
    print("=" * 70)
    print("HT POSITION RELATIVE TO DA-SEGMENTED RECORD STRUCTURE")
    print("=" * 70)

    entries = load_currier_a_entries()
    print(f"\nLoaded {len(entries)} Currier A entries")

    results = analyze_ht_position_in_records(entries)

    print(f"\n--- SUMMARY ---")
    print(f"Total entries: {results['total_entries']:,}")
    print(f"Total tokens: {results['total_tokens']:,}")
    print(f"Total DA tokens: {results['total_da']:,}")
    print(f"Total HT tokens: {results['total_ht']:,}")
    print(f"Entries with HT: {results['entries_with_ht']:,} ({100*results['entries_with_ht']/results['total_entries']:.1f}%)")

    print(f"\n--- HT POSITION RELATIVE TO DA ---")
    total_ht = results['total_ht']
    for pos, count in results['ht_positions'].most_common():
        print(f"  {pos}: {count:,} ({100*count/total_ht:.1f}%)")

    print(f"\n--- HT AT ENTRY BOUNDARIES ---")
    print(f"  HT at entry start/end: {results['ht_at_entry_boundary']:,} ({100*results['ht_at_entry_boundary']/total_ht:.1f}%)")

    print(f"\n--- HT ADJACENT TO DA ---")
    print(f"  HT immediately before/after DA: {results['ht_adjacent_to_da']:,} ({100*results['ht_adjacent_to_da']/total_ht:.1f}%)")

    print(f"\n--- EXAMPLES ---")
    for ex in results['ht_examples'][:10]:
        print(f"\n  Entry: {ex['entry']} (len={ex['entry_length']}, DA at {ex['da_positions']})")
        print(f"  HT token '{ex['ht_token']}' at position {ex['position']}")
        print(f"  Context: {' '.join(ex['context'])}")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Determine pattern
    boundary_pct = 100 * results['ht_at_entry_boundary'] / total_ht if total_ht > 0 else 0
    between_pct = 100 * results['ht_positions'].get('BETWEEN_DA', 0) / total_ht if total_ht > 0 else 0
    no_da_pct = 100 * results['ht_positions'].get('NO_DA_IN_ENTRY', 0) / total_ht if total_ht > 0 else 0

    print(f"\n  HT at entry boundaries: {boundary_pct:.1f}%")
    print(f"  HT between DA tokens: {between_pct:.1f}%")
    print(f"  HT in entries without DA: {no_da_pct:.1f}%")

    if boundary_pct > 50:
        print("\n  => HT is primarily at ENTRY BOUNDARIES (outside record content)")
    elif between_pct > 50:
        print("\n  => HT is primarily INSIDE records (between DA blocks)")
    else:
        print("\n  => HT distribution is mixed")


if __name__ == "__main__":
    main()
