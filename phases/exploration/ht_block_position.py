#!/usr/bin/env python3
"""
Analyze HT distribution by block position in multi-block entries.
"""

import sys
from collections import Counter

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token, MARKER_FAMILIES

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'ta', 'do'}
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


def is_da(token):
    token_lower = token.lower()
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True
    if token_lower.startswith('daiin') or token_lower.startswith('dain'):
        return True
    return result.prefix and result.prefix.startswith('da')


def is_ht(token):
    token_lower = token.lower()
    result = parse_currier_a_token(token)
    if is_da(token):
        return False
    for ht_pf in HT_PREFIXES:
        if token_lower.startswith(ht_pf) and not result.is_prefix_legal:
            return True
    return False


def get_prefix(token):
    result = parse_currier_a_token(token)
    if result.prefix:
        pf = result.prefix
        if len(pf) == 3 and pf.endswith('ch'):
            return 'ch'
        elif len(pf) == 3 and pf.endswith('sh'):
            return 'sh'
        return pf
    return None


def load_entries():
    entries = []
    with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r') as f:
        header = f.readline()
        current = None
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                language = parts[6].strip('"').strip()
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''
                if language != 'A':
                    continue
                key = f"{folio}_{line_num}"
                if current is None or current['key'] != key:
                    if current and current['tokens']:
                        entries.append(current)
                    current = {'key': key, 'tokens': []}
                current['tokens'].append(word)
        if current and current['tokens']:
            entries.append(current)
    return entries


def main():
    entries = load_entries()

    # For multi-block entries, analyze HT rate by block index
    block_stats = {}  # block_index -> {'ht': count, 'total': count}

    # Also track dominant prefix of blocks with HT
    ht_block_prefix = Counter()
    all_block_prefix = Counter()

    for entry in entries:
        tokens = entry['tokens']

        # Segment by DA
        blocks = []
        current = []
        for t in tokens:
            if is_da(t):
                if current:
                    blocks.append(current)
                    current = []
            else:
                current.append(t)
        if current:
            blocks.append(current)

        if len(blocks) < 2:
            continue  # Skip single-block entries

        n_blocks = len(blocks)

        for i, block in enumerate(blocks):
            # Normalize block index
            if i == 0:
                idx = 'FIRST'
            elif i == n_blocks - 1:
                idx = 'LAST'
            else:
                idx = 'MIDDLE'

            if idx not in block_stats:
                block_stats[idx] = {'ht': 0, 'total': 0, 'blocks': 0}

            block_stats[idx]['blocks'] += 1

            # Count HT and total in this block
            ht_count = sum(1 for t in block if is_ht(t))
            block_stats[idx]['ht'] += ht_count
            block_stats[idx]['total'] += len(block)

            # Track dominant prefix
            prefix_counts = Counter()
            for t in block:
                if not is_ht(t):
                    pf = get_prefix(t)
                    if pf:
                        prefix_counts[pf] += 1

            if prefix_counts:
                dominant = prefix_counts.most_common(1)[0][0]
                all_block_prefix[dominant] += 1
                if ht_count > 0:
                    ht_block_prefix[dominant] += 1

    print("=" * 70)
    print("HT DISTRIBUTION BY BLOCK INDEX (Multi-block entries only)")
    print("=" * 70)

    print(f"\n{'Block Index':<12} {'Blocks':<10} {'Tokens':<10} {'HT':<10} {'HT Rate':<12}")
    print("-" * 55)

    for idx in ['FIRST', 'MIDDLE', 'LAST']:
        if idx in block_stats:
            s = block_stats[idx]
            ht_rate = 100 * s['ht'] / s['total'] if s['total'] > 0 else 0
            print(f"{idx:<12} {s['blocks']:<10} {s['total']:<10} {s['ht']:<10} {ht_rate:.1f}%")

    # Compare FIRST vs LAST
    first = block_stats.get('FIRST', {})
    last = block_stats.get('LAST', {})
    if first and last:
        first_rate = first['ht'] / first['total'] if first['total'] > 0 else 0
        last_rate = last['ht'] / last['total'] if last['total'] > 0 else 0
        ratio = last_rate / first_rate if first_rate > 0 else 0
        print(f"\nLAST/FIRST HT rate ratio: {ratio:.2f}x")

    # Block prefix analysis
    print("\n" + "-" * 70)
    print("BLOCKS WITH HT BY DOMINANT PREFIX")
    print("-" * 70)

    print(f"\n{'Prefix':<10} {'All Blocks':<12} {'HT Blocks':<12} {'HT Rate':<12}")
    print("-" * 50)

    for pf in ['ch', 'sh', 'qo', 'ok', 'ot', 'ol', 'ct']:
        all_count = all_block_prefix.get(pf, 0)
        ht_count = ht_block_prefix.get(pf, 0)
        rate = 100 * ht_count / all_count if all_count > 0 else 0
        print(f"{pf:<10} {all_count:<12} {ht_count:<12} {rate:.1f}%")

    # Summary
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if ratio > 1.3:
        print(f"\nHT is enriched in LAST blocks ({ratio:.2f}x vs FIRST)")
        print("-> HT appears more toward the END of multi-block entries")
    elif ratio < 0.7:
        print(f"\nHT is enriched in FIRST blocks ({1/ratio:.2f}x vs LAST)")
        print("-> HT appears more at the START of multi-block entries")
    else:
        print("\nHT is evenly distributed across block positions")


if __name__ == "__main__":
    main()
