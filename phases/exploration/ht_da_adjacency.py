#!/usr/bin/env python3
"""
Check HT-DA adjacency patterns specifically.
"""

import sys
from collections import Counter

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token

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

    # Count patterns
    ht_before_da = 0  # HT immediately before DA
    ht_after_da = 0   # HT immediately after DA
    da_before_ht = 0  # DA immediately before HT (same as ht_after_da from DA perspective)
    da_after_ht = 0   # DA immediately after HT (same as ht_before_da)

    total_ht = 0
    total_da = 0

    # Also count what's between DA and HT
    between_da_ht = Counter()  # tokens between DA...HT
    between_ht_da = Counter()  # tokens between HT...DA

    for entry in entries:
        tokens = entry['tokens']
        n = len(tokens)

        for i, t in enumerate(tokens):
            if is_ht(t):
                total_ht += 1
                # Check if DA is immediately before
                if i > 0 and is_da(tokens[i-1]):
                    ht_after_da += 1
                # Check if DA is immediately after
                if i < n-1 and is_da(tokens[i+1]):
                    ht_before_da += 1

            if is_da(t):
                total_da += 1

    print("=" * 60)
    print("HT-DA ADJACENCY ANALYSIS")
    print("=" * 60)

    print(f"\nTotal HT tokens: {total_ht:,}")
    print(f"Total DA tokens: {total_da:,}")

    print(f"\n--- ADJACENCY ---")
    print(f"HT immediately AFTER DA: {ht_after_da:,} ({100*ht_after_da/total_ht:.1f}% of HT)")
    print(f"HT immediately BEFORE DA: {ht_before_da:,} ({100*ht_before_da/total_ht:.1f}% of HT)")
    print(f"HT adjacent to DA (either): {ht_after_da + ht_before_da:,} ({100*(ht_after_da+ht_before_da)/total_ht:.1f}% of HT)")

    # Expected if random
    # Average entry length
    total_tokens = sum(len(e['tokens']) for e in entries)
    avg_len = total_tokens / len(entries)
    da_rate = total_da / total_tokens

    print(f"\n--- BASELINE ---")
    print(f"DA rate in corpus: {100*da_rate:.1f}%")
    print(f"Expected adjacency if random: ~{100*2*da_rate:.1f}%")  # 2x for before+after
    print(f"Actual adjacency: {100*(ht_after_da+ht_before_da)/total_ht:.1f}%")
    print(f"Enrichment: {(ht_after_da+ht_before_da)/total_ht / (2*da_rate):.2f}x")

    # Check sequences
    print("\n--- SEQUENCE PATTERNS ---")

    # Look for DA-HT-DA sandwiches
    da_ht_da = 0
    ht_da_ht = 0

    for entry in entries:
        tokens = entry['tokens']
        n = len(tokens)
        for i in range(n-2):
            if is_da(tokens[i]) and is_ht(tokens[i+1]) and is_da(tokens[i+2]):
                da_ht_da += 1
            if is_ht(tokens[i]) and is_da(tokens[i+1]) and is_ht(tokens[i+2]):
                ht_da_ht += 1

    print(f"DA-HT-DA sandwiches: {da_ht_da}")
    print(f"HT-DA-HT sandwiches: {ht_da_ht}")

    # Look at what prefix families appear in HT-adjacent positions
    print("\n--- HT IN DA-SEGMENTED BLOCKS ---")

    # For entries with DA, count HT in each block
    ht_in_block_1 = 0
    ht_in_block_2plus = 0
    ht_in_single_block = 0

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

        if len(blocks) == 1:
            # Single block entry
            for t in blocks[0]:
                if is_ht(t):
                    ht_in_single_block += 1
        else:
            # Multi-block entry
            for i, block in enumerate(blocks):
                for t in block:
                    if is_ht(t):
                        if i == 0:
                            ht_in_block_1 += 1
                        else:
                            ht_in_block_2plus += 1

    print(f"HT in single-block entries: {ht_in_single_block:,}")
    print(f"HT in first block (multi-block): {ht_in_block_1:,}")
    print(f"HT in blocks 2+ (multi-block): {ht_in_block_2plus:,}")


if __name__ == "__main__":
    main()
